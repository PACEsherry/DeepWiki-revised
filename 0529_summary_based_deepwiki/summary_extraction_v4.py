#!/usr/bin/env python3
"""
Summary Extraction Script v4 - Multi-Language + Better Descriptions

Supports: Python, C++, Java, JavaScript, C, Go, Rust
Improvements:
  - Multi-language tree-sitter parsing
  - Better function descriptions (no title repetition)
  - Concise output for AI readers
"""

import argparse
import glob
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from tree_sitter import Language, Node, Parser
from openai import OpenAI

# ── Logging ────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────
DEFAULT_API_KEY = "tp-cbs3hu9i4xsldjtuyl82fj2l9uo2py2qe3ulrhc1zzhj8ij5"
DEFAULT_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"
DEFAULT_REPO_PATH = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_output_kit.md")

MAX_CODE_CHARS = 20000
API_CALL_DELAY = 1.0
MAX_RETRIES = 3

SKIP_PATTERNS = {"__pycache__", ".pyc", "node_modules", ".git", "build", "dist", "target"}
SKIP_FILES = {"__init__.py", "__main__.py", "setup.py", "conftest.py"}

# ── Language Registry ──────────────────────────────────────────────────

@dataclass
class LangConfig:
    name: str
    extensions: List[str]
    module_node: str  # Top-level container type
    class_node: str
    function_node: str
    method_node: str
    comment_prefix: str = "//"

# Supported languages
LANGUAGES: Dict[str, LangConfig] = {
    "python": LangConfig(
        name="python", extensions=[".py"],
        module_node="module", class_node="class_definition",
        function_node="function_definition", method_node="function_definition",
        comment_prefix="#"
    ),
    "cpp": LangConfig(
        name="cpp", extensions=[".cpp", ".cc", ".cxx", ".hpp", ".h"],
        module_node="translation_unit", class_node="class_specifier",
        function_node="function_definition", method_node="function_definition",
        comment_prefix="//"
    ),
    "c": LangConfig(
        name="c", extensions=[".c", ".h"],
        module_node="translation_unit", class_node="struct_specifier",
        function_node="function_definition", method_node="function_definition",
        comment_prefix="//"
    ),
    "java": LangConfig(
        name="java", extensions=[".java"],
        module_node="program", class_node="class_declaration",
        function_node="method_declaration", method_node="method_declaration",
        comment_prefix="//"
    ),
    "javascript": LangConfig(
        name="javascript", extensions=[".js", ".jsx", ".mjs"],
        module_node="program", class_node="class_declaration",
        function_node="function_declaration", method_node="method_definition",
        comment_prefix="//"
    ),
    "typescript": LangConfig(
        name="typescript", extensions=[".ts", ".tsx"],
        module_node="program", class_node="class_declaration",
        function_node="function_declaration", method_node="method_definition",
        comment_prefix="//"
    ),
    "go": LangConfig(
        name="go", extensions=[".go"],
        module_node="source_file", class_node="type_declaration",
        function_node="function_declaration", method_node="method_declaration",
        comment_prefix="//"
    ),
    "rust": LangConfig(
        name="rust", extensions=[".rs"],
        module_node="source_file", class_node="impl_item",
        function_node="function_item", method_node="function_item",
        comment_prefix="//"
    ),
}

# Extension -> Language mapping
EXT_TO_LANG: Dict[str, str] = {}
for lang_cfg in LANGUAGES.values():
    for ext in lang_cfg.extensions:
        EXT_TO_LANG[ext] = lang_cfg.name

# ── Tree-sitter Parser Pool ────────────────────────────────────────────

_parser_pool: Dict[str, Tuple[Parser, LangConfig]] = {}

def _get_parser(lang_name: str) -> Tuple[Parser, LangConfig]:
    if lang_name in _parser_pool:
        return _parser_pool[lang_name]

    cfg = LANGUAGES[lang_name]
    try:
        if lang_name == "python":
            import tree_sitter_python as ts_mod
        elif lang_name == "cpp":
            import tree_sitter_cpp as ts_mod
        elif lang_name == "c":
            import tree_sitter_c as ts_mod
        elif lang_name == "java":
            import tree_sitter_java as ts_mod
        elif lang_name in ("javascript", "typescript"):
            import tree_sitter_javascript as ts_mod
        elif lang_name == "go":
            import tree_sitter_go as ts_mod
        elif lang_name == "rust":
            import tree_sitter_rust as ts_mod
        else:
            raise ValueError(f"Unsupported language: {lang_name}")

        lang = Language(ts_mod.language())
        parser = Parser(lang)
        _parser_pool[lang_name] = (parser, cfg)
        return parser, cfg
    except ImportError as e:
        logger.warning(f"tree-sitter for {lang_name} not available: {e}")
        raise


# ── Data Structures ────────────────────────────────────────────────────

@dataclass
class SymbolInfo:
    name: str
    type: str  # "class", "function", "method", "interface", "struct"
    code: str
    start_line: int
    end_line: int
    parent_class: Optional[str] = None
    params: str = ""
    docstring: str = ""
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    abstract_methods: List[str] = field(default_factory=list)
    language: str = ""


@dataclass
class FileInfo:
    relative_path: str
    absolute_path: str
    content: str
    symbols: List[SymbolInfo] = field(default_factory=list)
    lines: int = 0
    language: str = ""
    imports: List[str] = field(default_factory=list)


# ── File Discovery ─────────────────────────────────────────────────────

def discover_files(repo_path: str, languages: List[str] = None) -> List[FileInfo]:
    if languages is None:
        languages = list(LANGUAGES.keys())

    # Collect all supported extensions
    extensions = set()
    for lang_name in languages:
        if lang_name in LANGUAGES:
            extensions.update(LANGUAGES[lang_name].extensions)

    files = []
    for ext in extensions:
        pattern = os.path.join(repo_path, "**", f"*{ext}")
        for file_path in sorted(glob.glob(pattern, recursive=True)):
            rel_path = os.path.relpath(file_path, repo_path)
            parts = Path(rel_path).parts

            # Skip patterns
            if any(skip in part for skip in SKIP_PATTERNS for part in parts):
                continue
            if os.path.basename(file_path) in SKIP_FILES:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if not content.strip() or len(content) < 50:
                    continue
                if len(content) > MAX_CODE_CHARS * 3:
                    logger.warning(f"Skipping large file {rel_path}: {len(content)} chars")
                    continue

                lang_name = EXT_TO_LANG.get(ext, "unknown")
                files.append(FileInfo(
                    relative_path=rel_path,
                    absolute_path=file_path,
                    content=content,
                    lines=len(content.splitlines()),
                    language=lang_name,
                ))
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

    logger.info(f"Discovered {len(files)} files across {len(set(f.language for f in files))} languages")
    return files


# ── Symbol Extraction (Multi-Language) ──────────────────────────────────

def _get_node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte:node.end_byte].decode("utf-8", errors="ignore")


def _extract_docstring(node: Node, source: bytes, lang_name: str) -> str:
    """Extract docstring/comment before or inside a function/class."""
    if lang_name == "python":
        # Python: check for string literal as first statement in body
        body = node.child_by_field_name("body")
        if body and body.children:
            first = body.children[0]
            if first.type == "expression_statement":
                expr = first.children[0] if first.children else None
                if expr and expr.type == "string":
                    return _get_node_text(expr, source).strip("'\"")
    else:
        # C-style languages: check for comment above
        parent = node.parent
        if parent:
            for child in parent.children:
                if child == node:
                    break
                if child.type == "comment":
                    text = _get_node_text(child, source)
                    # Clean comment markers
                    text = re.sub(r'^/\*\*?\s*', '', text)
                    text = re.sub(r'\s*\*/$', '', text)
                    text = re.sub(r'^//\s*', '', text)
                    text = re.sub(r'^\s*\*\s*', '', text, flags=re.MULTILINE)
                    return text.strip()
    return ""


def _extract_python_symbols(node: Node, source: bytes, parent_class: str = None) -> List[SymbolInfo]:
    """Extract symbols from Python AST."""
    symbols = []

    if node.type == "class_definition":
        name_node = node.child_by_field_name("name")
        body_node = node.child_by_field_name("body")
        class_name = _get_node_text(name_node, source) if name_node else "unknown"

        base_classes = []
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type in ("identifier", "attribute"):
                        base_classes.append(_get_node_text(arg, source))

        docstring = ""
        methods = []
        if body_node:
            for child in body_node.children:
                if child.type == "function_definition":
                    m_name = child.child_by_field_name("name")
                    if m_name:
                        methods.append(_get_node_text(m_name, source))
                    symbols.extend(_extract_python_symbols(child, source, parent_class=class_name))
                elif child.type == "expression_statement":
                    expr = child.children[0] if child.children else None
                    if expr and expr.type == "string" and not docstring:
                        docstring = _get_node_text(expr, source).strip("'\"")

        class_code = _get_node_text(node, source)
        if len(class_code) > MAX_CODE_CHARS:
            class_code = class_code[:MAX_CODE_CHARS] + "\n    ..."

        is_interface = any(bc in ("ABC", "Protocol") for bc in base_classes)
        symbol_type = "interface" if is_interface else "class"

        symbols.append(SymbolInfo(
            name=class_name, type=symbol_type, code=class_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            docstring=docstring, base_classes=base_classes, methods=methods,
            language="python",
        ))

    elif node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        func_name = _get_node_text(name_node, source) if name_node else "unknown"
        params_node = node.child_by_field_name("parameters")
        params = _get_node_text(params_node, source) if params_node else "()"

        body_node = node.child_by_field_name("body")
        docstring = ""
        if body_node and body_node.children:
            first = body_node.children[0]
            if first.type == "expression_statement":
                expr = first.children[0] if first.children else None
                if expr and expr.type == "string":
                    docstring = _get_node_text(expr, source).strip("'\"")

        func_code = _get_node_text(node, source)
        if len(func_code) > MAX_CODE_CHARS:
            func_code = func_code[:MAX_CODE_CHARS] + "\n    ..."

        symbol_type = "method" if parent_class else "function"
        symbols.append(SymbolInfo(
            name=func_name, type=symbol_type, code=func_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            parent_class=parent_class, params=params, docstring=docstring,
            language="python",
        ))
    else:
        for child in node.children:
            symbols.extend(_extract_python_symbols(child, source, parent_class))

    return symbols


def _extract_c_style_symbols(node: Node, source: bytes, lang_name: str, parent_class: str = None) -> List[SymbolInfo]:
    """Extract symbols from C-style language ASTs (C++, Java, JavaScript, Go, Rust)."""
    symbols = []
    cfg = LANGUAGES[lang_name]

    if node.type == cfg.class_node:
        name_node = node.child_by_field_name("name")
        class_name = _get_node_text(name_node, source) if name_node else "unknown"

        base_classes = []
        # Java: superclass, interfaces
        for child in node.children:
            if child.type in ("superclass", "super_interfaces"):
                for sub in child.children:
                    if sub.type in ("type_identifier", "generic_type"):
                        base_classes.append(_get_node_text(sub, source))

        docstring = _extract_docstring(node, source, lang_name)
        methods = []
        body_node = node.child_by_field_name("body")
        if body_node:
            for child in body_node.children:
                if child.type in (cfg.method_node, cfg.function_node):
                    m_name = child.child_by_field_name("name")
                    if m_name:
                        methods.append(_get_node_text(m_name, source))
                    symbols.extend(_extract_c_style_symbols(child, source, lang_name, parent_class=class_name))

        class_code = _get_node_text(node, source)
        if len(class_code) > MAX_CODE_CHARS:
            class_code = class_code[:MAX_CODE_CHARS] + "\n    ..."

        symbol_type = "class"
        symbols.append(SymbolInfo(
            name=class_name, type=symbol_type, code=class_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            docstring=docstring, base_classes=base_classes, methods=methods,
            language=lang_name,
        ))

    elif node.type in (cfg.function_node, cfg.method_node):
        name_node = node.child_by_field_name("name")
        func_name = _get_node_text(name_node, source) if name_node else "unknown"

        params_node = node.child_by_field_name("parameters")
        params = _get_node_text(params_node, source) if params_node else "()"

        docstring = _extract_docstring(node, source, lang_name)
        func_code = _get_node_text(node, source)
        if len(func_code) > MAX_CODE_CHARS:
            func_code = func_code[:MAX_CODE_CHARS] + "\n    ..."

        symbol_type = "method" if parent_class else "function"
        symbols.append(SymbolInfo(
            name=func_name, type=symbol_type, code=func_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            parent_class=parent_class, params=params, docstring=docstring,
            language=lang_name,
        ))
    else:
        for child in node.children:
            symbols.extend(_extract_c_style_symbols(child, source, lang_name, parent_class))

    return symbols


def _extract_go_symbols(node: Node, source: bytes, parent_type: str = None) -> List[SymbolInfo]:
    """Extract symbols from Go AST."""
    symbols = []

    if node.type == "type_declaration":
        # Go type declarations (struct, interface)
        type_spec = None
        for child in node.children:
            if child.type == "type_spec":
                type_spec = child
                break
        if type_spec:
            name_node = type_spec.child_by_field_name("name")
            type_name = _get_node_text(name_node, source) if name_node else "unknown"
            type_node = type_spec.child_by_field_name("type")

            is_interface = type_node and type_node.type == "interface_type"
            symbol_type = "interface" if is_interface else "class"

            methods = []
            docstring = _extract_docstring(node, source, "go")

            if type_node and type_node.type == "struct_type":
                # Extract fields
                for child in type_node.children:
                    if child.type == "field_declaration":
                        pass  # Fields are part of the struct
            elif is_interface:
                # Extract interface methods
                for child in type_node.children:
                    if child.type == "method_spec":
                        m_name = child.child_by_field_name("name")
                        if m_name:
                            methods.append(_get_node_text(m_name, source))

            class_code = _get_node_text(node, source)
            if len(class_code) > MAX_CODE_CHARS:
                class_code = class_code[:MAX_CODE_CHARS] + "\n    ..."

            symbols.append(SymbolInfo(
                name=type_name, type=symbol_type, code=class_code,
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                docstring=docstring, methods=methods, language="go",
            ))

    elif node.type == "function_declaration":
        name_node = node.child_by_field_name("name")
        func_name = _get_node_text(name_node, source) if name_node else "unknown"

        params_node = node.child_by_field_name("parameters")
        params = _get_node_text(params_node, source) if params_node else "()"

        docstring = _extract_docstring(node, source, "go")
        func_code = _get_node_text(node, source)
        if len(func_code) > MAX_CODE_CHARS:
            func_code = func_code[:MAX_CODE_CHARS] + "\n    ..."

        symbols.append(SymbolInfo(
            name=func_name, type="function", code=func_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            params=params, docstring=docstring, language="go",
        ))

    elif node.type == "method_declaration":
        name_node = node.child_by_field_name("name")
        func_name = _get_node_text(name_node, source) if name_node else "unknown"

        params_node = node.child_by_field_name("parameters")
        params = _get_node_text(params_node, source) if params_node else "()"

        # Get receiver type
        receiver = node.child_by_field_name("receiver")
        parent_class = None
        if receiver:
            for child in receiver.children:
                if child.type == "parameter_declaration":
                    type_node = child.child_by_field_name("type")
                    if type_node:
                        parent_class = _get_node_text(type_node, source).strip("*")

        docstring = _extract_docstring(node, source, "go")
        func_code = _get_node_text(node, source)
        if len(func_code) > MAX_CODE_CHARS:
            func_code = func_code[:MAX_CODE_CHARS] + "\n    ..."

        symbols.append(SymbolInfo(
            name=func_name, type="method", code=func_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            parent_class=parent_class, params=params, docstring=docstring,
            language="go",
        ))
    else:
        for child in node.children:
            symbols.extend(_extract_go_symbols(child, source, parent_type))

    return symbols


def extract_symbols(file_info: FileInfo) -> List[SymbolInfo]:
    """Extract symbols from a file using the appropriate language parser."""
    lang_name = file_info.language
    try:
        parser, cfg = _get_parser(lang_name)
        source = file_info.content.encode("utf-8")
        tree = parser.parse(source)
        root = tree.root_node

        if lang_name == "python":
            return _extract_python_symbols(root, source)
        elif lang_name == "go":
            return _extract_go_symbols(root, source)
        else:
            return _extract_c_style_symbols(root, source, lang_name)
    except Exception as e:
        logger.error(f"Error extracting symbols from {file_info.relative_path}: {e}")
        return []


# ── LLM Interaction ────────────────────────────────────────────────────

def _clean_response(text: str) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL)
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        end_idx = len(lines)
        for j in range(1, len(lines)):
            if lines[j].strip() == "```":
                end_idx = j
                break
        cleaned = "\n".join(lines[1:end_idx])
    cleaned = re.sub(r"```\w*\n```", "```", cleaned)
    cleaned = re.sub(r"```python\n(.*?)```python\n", r"```python\n", cleaned, flags=re.DOTALL)
    return cleaned.strip()


class LLMSummarizer:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.call_count = 0

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 800) -> str:
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3,
                )
                self.call_count += 1
                if API_CALL_DELAY > 0:
                    time.sleep(API_CALL_DELAY)
                return _clean_response(response.choices[0].message.content or "")
            except Exception as e:
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        return ""

    # ── Module ──────────────────────────────────────────────────────────
    def summarize_module(self, file_info: FileInfo) -> str:
        content = file_info.content[:MAX_CODE_CHARS]
        classes = [s.name for s in file_info.symbols if s.type in ("class", "interface")]
        functions = [s.name for s in file_info.symbols if s.type == "function"]

        sys_p = (
            "你是代码分析专家。用中文简洁描述模块职责，1-2句话，不超过80字。"
            "重点说明该模块的核心功能、解决的问题、或提供的能力。"
            "不要重复文件路径，不要包含代码围栏。"
        )
        usr_p = (
            f"语言: {file_info.language}\n"
            f"文件: {file_info.relative_path}\n"
            f"类: {', '.join(classes) or '无'}\n"
            f"函数: {', '.join(functions) or '无'}\n\n"
            f"代码片段:\n```\n{content[:3000]}\n```\n\n"
            f"请用中文简洁描述此模块的核心职责（1-2句）。"
        )

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 15:
            result = f"该模块提供 {len(classes)} 个类和 {len(functions)} 个函数，用于 {file_info.relative_path} 的核心功能实现。"
        return result

    def generate_module_usage(self, file_info: FileInfo) -> str:
        classes = [s.name for s in file_info.symbols if s.type in ("class", "interface")][:3]
        functions = [s.name for s in file_info.symbols if s.type == "function"][:3]
        lang = file_info.language

        sys_p = f"你是{lang}专家。生成3-5行简洁的使用示例代码。只输出代码，不要解释。"
        usr_p = f"模块: {file_info.relative_path}\n类: {', '.join(classes) or '无'}\n函数: {', '.join(functions) or '无'}\n\n生成3-5行简洁的使用示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 20:
            if classes:
                result = f"// 使用 {classes[0]}\nauto obj = new {classes[0]}();\nobj.someMethod();"
            elif functions:
                result = f"// 调用 {functions[0]}\nauto result = {functions[0]}();"
            else:
                result = f"// 导入并使用 {file_info.relative_path}"
        return result

    # ── Interface ───────────────────────────────────────────────────────
    def summarize_interface(self, file_path: str, symbol: SymbolInfo) -> str:
        abs_methods = ", ".join(symbol.abstract_methods[:6]) if symbol.abstract_methods else ", ".join(symbol.methods[:6])

        sys_p = (
            "你是代码分析专家。用中文简洁描述接口/抽象类的契约，1-2句话，不超过60字。"
            "重点说明该接口定义了什么能力契约、约束了哪些行为。不要重复接口名称。"
        )
        usr_p = (
            f"语言: {symbol.language}\n"
            f"接口: {symbol.name}\n"
            f"基类: {', '.join(symbol.base_classes) or '无'}\n"
            f"方法: {abs_methods}\n"
            f"文档: {symbol.docstring[:100] or '无'}\n\n"
            f"请用中文简洁描述此接口的职责（1-2句）。"
        )

        result = self._call_llm(sys_p, usr_p, max_tokens=150)
        if not result or len(result) < 15:
            result = f"定义了 {abs_methods} 等方法的能力契约，约束实现类必须提供这些行为。"
        return result

    def generate_interface_usage(self, file_path: str, symbol: SymbolInfo) -> str:
        abs_methods = symbol.abstract_methods[:4] if symbol.abstract_methods else symbol.methods[:4]

        sys_p = "你是代码专家。生成3-5行简洁的接口实现示例。只输出代码，不要解释。"
        usr_p = f"接口: {symbol.name}\n方法: {', '.join(abs_methods)}\n\n生成简洁的实现示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 20:
            methods_stub = "\n    ".join(f"def {m}(self, *args): ..." for m in abs_methods[:3])
            result = f"class MyImpl({symbol.name}):\n    {methods_stub}"
        return result

    # ── Class ───────────────────────────────────────────────────────────
    def summarize_class(self, file_path: str, symbol: SymbolInfo) -> str:
        sys_p = (
            "你是代码分析专家。用中文简洁描述类的职责，1-2句话，不超过60字。"
            "重点说明该类封装了什么数据/行为、在系统中扮演什么角色。不要重复类名。"
        )
        usr_p = (
            f"语言: {symbol.language}\n"
            f"类: {symbol.name}\n"
            f"基类: {', '.join(symbol.base_classes) or '无'}\n"
            f"方法: {', '.join(symbol.methods[:6]) or '无'}\n"
            f"文档: {symbol.docstring[:100] or '无'}\n\n"
            f"请用中文简洁描述此类的职责（1-2句）。"
        )

        result = self._call_llm(sys_p, usr_p, max_tokens=150)
        if not result or len(result) < 15:
            methods_str = ", ".join(symbol.methods[:4]) if symbol.methods else "无"
            result = f"封装相关功能，提供 {methods_str} 等方法。"
        return result

    def generate_class_usage(self, file_path: str, symbol: SymbolInfo) -> str:
        sys_p = "你是代码专家。生成3-5行简洁的类使用示例。只输出代码，不要解释。"
        usr_p = f"类: {symbol.name}\n方法: {', '.join(symbol.methods[:5]) or '无'}\n参数: {symbol.params}\n\n生成简洁的使用示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 20:
            if symbol.language == "python":
                result = f"obj = {symbol.name}()\nresult = obj.{symbol.methods[0]}()" if symbol.methods else f"obj = {symbol.name}()"
            else:
                result = f"auto obj = new {symbol.name}();\nobj->{symbol.methods[0]}();" if symbol.methods else f"auto obj = new {symbol.name}();"
        return result

    # ── Method / Function ───────────────────────────────────────────────
    def summarize_function(self, file_path: str, symbol: SymbolInfo) -> str:
        func_type = "方法" if symbol.type == "method" else "函数"
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name

        sys_p = (
            f"你是代码分析专家。用中文描述{func_type}的功能，1句话，不超过50字。"
            f"重点说明该{func_type}做了什么（处理逻辑、返回结果），而不是重复{func_type}名和参数。"
            f"例如：不要说'sanitize_url函数处理(url: str)参数'，而要说'去除URL中的凭据信息，返回安全的显示用字符串'。"
        )
        usr_p = (
            f"语言: {symbol.language}\n"
            f"{func_type}: {full_name}\n"
            f"参数: {symbol.params}\n"
            f"文档: {symbol.docstring[:100] or '无'}\n"
            f"代码片段:\n```\n{symbol.code[:1000]}\n```\n\n"
            f"请用中文简洁描述此{func_type}的核心功能（1句）。"
        )

        result = self._call_llm(sys_p, usr_p, max_tokens=100)
        if not result or len(result) < 10:
            doc_hint = f"，{symbol.docstring[:40]}" if symbol.docstring else ""
            result = f"执行特定处理逻辑并返回结果{doc_hint}。"
        return result

    def generate_function_usage(self, file_path: str, symbol: SymbolInfo) -> str:
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name

        sys_p = "你是代码专家。生成2-3行简洁的函数调用示例。只输出代码，不要解释。"
        usr_p = f"函数: {full_name}\n参数: {symbol.params}\n\n生成简洁的调用示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=150)
        if not result or len(result) < 15:
            if symbol.language == "python":
                result = f"result = {full_name}()\nprint(result)"
            else:
                result = f"auto result = {full_name}();"
        return result


# ── Output Formatting ──────────────────────────────────────────────────

class SummaryFormatter:
    @staticmethod
    def _wrap_usage(usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```{usage}\n```"
        return usage

    @staticmethod
    def format_module(file_info: FileInfo, summary: str, usage: str) -> str:
        usage = SummaryFormatter._wrap_usage(usage)
        return f"# module `{file_info.relative_path}`\n\n## function:\n\n{summary}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_interface(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = SummaryFormatter._wrap_usage(usage)
        extends = ", ".join(symbol.base_classes) if symbol.base_classes else "none"
        return f"# interface `{symbol.name}`\n\n## function:\n\n{summary}\n\n## extends:\n\n{extends}\n\n## implemented by:\n\nunknown\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_class(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = SummaryFormatter._wrap_usage(usage)
        extends = ", ".join(symbol.base_classes) if symbol.base_classes else "none"
        return f"# class `{symbol.name}`\n\n## function:\n\n{summary}\n\n## extends:\n\n{extends}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_method(file_path: str, symbol: SymbolInfo, summary: str, usage: str = "") -> str:
        if not usage:
            usage = f"obj.{symbol.name}()"
        usage = SummaryFormatter._wrap_usage(usage)
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name
        return f"# method `{full_name}{symbol.params}`\n\n## function:\n\n{summary}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_function(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = SummaryFormatter._wrap_usage(usage)
        return f"# func `{symbol.name}{symbol.params}`\n\n## function:\n\n{summary}\n\n## usage example:\n\n{usage}\n"


# ── Main Pipeline ──────────────────────────────────────────────────────

def run_extraction(
    repo_path: str = DEFAULT_REPO_PATH,
    output_path: str = OUTPUT_PATH,
    api_key: str = DEFAULT_API_KEY,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    max_files: int = 0,
    level: str = "all",
    batch_size: int = 0,
    resume_from: int = 0,
    languages: str = None,
) -> None:
    lang_list = [l.strip() for l in languages.split(",")] if languages else list(LANGUAGES.keys())

    logger.info("=" * 60)
    logger.info("Summary Extraction Pipeline v4 (Multi-Language)")
    logger.info("=" * 60)
    logger.info(f"Repository: {repo_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Model: {model}")
    logger.info(f"Level: {level}")
    logger.info(f"Languages: {', '.join(lang_list)}")

    logger.info("\n[Phase 1] Discovering files...")
    files = discover_files(repo_path, lang_list)
    if max_files > 0:
        files = files[:max_files]
    if resume_from > 0:
        files = files[resume_from:]
    if batch_size > 0:
        files = files[:batch_size]

    logger.info(f"\n[Phase 2] Extracting symbols from {len(files)} files...")
    for i, fi in enumerate(files):
        fi.symbols = extract_symbols(fi)
        types = {}
        for s in fi.symbols:
            types[s.type] = types.get(s.type, 0) + 1
        logger.info(f"  [{i+1}/{len(files)}] [{fi.language}] {fi.relative_path}: {types}")

    logger.info("\n[Phase 3] Generating summaries...")
    summarizer = LLMSummarizer(api_key=api_key, base_url=base_url, model=model)
    all_entries: List[str] = []
    formatter = SummaryFormatter()

    for i, fi in enumerate(files):
        logger.info(f"\n  [{i+1}/{len(files)}] [{fi.language}] {fi.relative_path}")

        # Module
        logger.info("    module...")
        m_sum = summarizer.summarize_module(fi)
        m_use = summarizer.generate_module_usage(fi)
        all_entries.append(formatter.format_module(fi, m_sum, m_use))

        if level in ("interface", "class", "all"):
            for s in [s for s in fi.symbols if s.type == "interface"]:
                logger.info(f"    interface {s.name}...")
                i_sum = summarizer.summarize_interface(fi.relative_path, s)
                i_use = summarizer.generate_interface_usage(fi.relative_path, s)
                all_entries.append(formatter.format_interface(fi.relative_path, s, i_sum, i_use))

        if level in ("class", "all"):
            for s in [s for s in fi.symbols if s.type == "class"]:
                logger.info(f"    class {s.name}...")
                c_sum = summarizer.summarize_class(fi.relative_path, s)
                c_use = summarizer.generate_class_usage(fi.relative_path, s)
                all_entries.append(formatter.format_class(fi.relative_path, s, c_sum, c_use))

        if level == "all":
            for cls in [s for s in fi.symbols if s.type in ("class", "interface")]:
                for method in [s for s in fi.symbols if s.type == "method" and s.parent_class == cls.name]:
                    logger.info(f"    method {cls.name}.{method.name}...")
                    mt_sum = summarizer.summarize_function(fi.relative_path, method)
                    all_entries.append(formatter.format_method(fi.relative_path, method, mt_sum))

            for func in [s for s in fi.symbols if s.type == "function"]:
                logger.info(f"    function {func.name}...")
                f_sum = summarizer.summarize_function(fi.relative_path, func)
                f_use = summarizer.generate_function_usage(fi.relative_path, func)
                all_entries.append(formatter.format_function(fi.relative_path, func, f_sum, f_use))

    # Write output
    logger.info(f"\n[Phase 4] Writing {len(all_entries)} entries to {output_path}...")
    file_exists = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    with open(output_path, "a" if file_exists else "w", encoding="utf-8") as f:
        if not file_exists:
            f.write(f"# Summary Output - Kit Repository\n\n> 由大模型 mimo-v2.5-pro 自动生成。\n> 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")
        else:
            f.write("\n\n")
        f.write("\n\n".join(all_entries))
        f.write("\n")

    logger.info(f"\n{'=' * 60}")
    logger.info(f"Done! {len(all_entries)} entries, {summarizer.call_count} API calls")
    logger.info(f"{'=' * 60}")


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract concise code summaries v4 (Multi-Language)")
    parser.add_argument("--repo-path", dest="repo_path", default=DEFAULT_REPO_PATH)
    parser.add_argument("--output", dest="output_path", default=OUTPUT_PATH)
    parser.add_argument("--api-key", dest="api_key", default=DEFAULT_API_KEY)
    parser.add_argument("--base-url", dest="base_url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-files", dest="max_files", type=int, default=0)
    parser.add_argument("--level", choices=["module", "interface", "class", "all"], default="all")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=0)
    parser.add_argument("--resume-from", dest="resume_from", type=int, default=0)
    parser.add_argument("--languages", default=None, help="Comma-separated language list (e.g., python,cpp,java)")
    args = parser.parse_args()
    run_extraction(**vars(args))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Summary Extraction Script v3 - Concise Version

Generates concise summaries following Summary_Output_Templet.md format.
Target audience: AI readers. Output ~4000 lines for 49 files.
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
from typing import List, Optional

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

DEFAULT_API_KEY = "tp-cbs3hu9i4xsldjtuyl82fj2l9uo2py2qe3ulrhc1zzhj8ij5"
DEFAULT_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"
KIT_REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kit", "src", "kit")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_output_kit.md")

MAX_CODE_CHARS = 20000
API_CALL_DELAY = 1.0
MAX_RETRIES = 3

SKIP_PATTERNS = {"__pycache__", ".pyc"}
SKIP_FILES = {"__init__.py", "__main__.py"}

_ts_language = Language(tspython.language())
_parser = Parser(_ts_language)


@dataclass
class SymbolInfo:
    name: str
    type: str  # "class", "function", "method", "interface"
    code: str
    start_line: int
    end_line: int
    parent_class: Optional[str] = None
    params: str = ""
    docstring: str = ""
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    abstract_methods: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)


@dataclass
class FileInfo:
    relative_path: str
    absolute_path: str
    content: str
    symbols: List[SymbolInfo] = field(default_factory=list)
    lines: int = 0
    imports: List[str] = field(default_factory=list)


def discover_files(repo_path: str) -> List[FileInfo]:
    files = []
    pattern = os.path.join(repo_path, "**", "*.py")
    for file_path in sorted(glob.glob(pattern, recursive=True)):
        rel_path = os.path.relpath(file_path, repo_path)
        parts = Path(rel_path).parts
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
            files.append(FileInfo(relative_path=rel_path, absolute_path=file_path, content=content, lines=len(content.splitlines())))
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
    logger.info(f"Discovered {len(files)} Python files")
    return files


def _extract_imports(node: Node, source: bytes) -> List[str]:
    imports = []
    if node.type in ("import_statement", "import_from_statement"):
        imports.append(node.text.decode())
    for child in node.children:
        imports.extend(_extract_imports(child, source))
    return imports


def _extract_symbols_from_node(node: Node, source: bytes, parent_class: str = None) -> List[SymbolInfo]:
    symbols = []

    if node.type == "class_definition":
        name_node = node.child_by_field_name("name")
        body_node = node.child_by_field_name("body")
        class_name = name_node.text.decode() if name_node else "unknown"

        base_classes = []
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type in ("identifier", "attribute"):
                        base_classes.append(arg.text.decode())

        docstring = ""
        methods = []
        abstract_methods = []
        attributes = []
        if body_node:
            for child in body_node.children:
                if child.type == "function_definition":
                    m_name = child.child_by_field_name("name")
                    if m_name:
                        methods.append(m_name.text.decode())
                    # Check for @abstractmethod
                    for prev in child.children:
                        if prev.type == "decorator" and "abstractmethod" in prev.text.decode():
                            if m_name:
                                abstract_methods.append(m_name.text.decode())
                    symbols.extend(_extract_symbols_from_node(child, source, parent_class=class_name))
                elif child.type == "expression_statement":
                    expr = child.children[0] if child.children else None
                    if expr and expr.type == "string" and not docstring:
                        docstring = expr.text.decode().strip("'\"")
                elif child.type == "assignment":
                    left = child.child_by_field_name("left")
                    if left and left.type == "identifier":
                        attributes.append(left.text.decode())

        class_code = node.text.decode()
        if len(class_code) > MAX_CODE_CHARS:
            class_code = class_code[:MAX_CODE_CHARS] + "\n    ..."

        # Determine if this is an interface (ABC or Protocol)
        is_interface = any(bc in ("ABC", "Protocol") for bc in base_classes)
        symbol_type = "interface" if is_interface else "class"

        symbols.append(SymbolInfo(
            name=class_name, type=symbol_type, code=class_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            docstring=docstring, base_classes=base_classes,
            methods=methods, abstract_methods=abstract_methods, attributes=attributes,
        ))

    elif node.type == "function_definition":
        name_node = node.child_by_field_name("name")
        func_name = name_node.text.decode() if name_node else "unknown"
        params_node = node.child_by_field_name("parameters")
        params = params_node.text.decode() if params_node else "()"

        docstring = ""
        body_node = node.child_by_field_name("body")
        if body_node and body_node.children:
            first = body_node.children[0]
            if first.type == "expression_statement":
                expr = first.children[0] if first.children else None
                if expr and expr.type == "string":
                    docstring = expr.text.decode().strip("'\"")

        func_code = node.text.decode()
        if len(func_code) > MAX_CODE_CHARS:
            func_code = func_code[:MAX_CODE_CHARS] + "\n    ..."

        symbol_type = "method" if parent_class else "function"
        symbols.append(SymbolInfo(
            name=func_name, type=symbol_type, code=func_code,
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            parent_class=parent_class, params=params, docstring=docstring,
        ))
    else:
        for child in node.children:
            symbols.extend(_extract_symbols_from_node(child, source, parent_class))
    return symbols


def extract_symbols(file_info: FileInfo) -> List[SymbolInfo]:
    try:
        source = file_info.content.encode("utf-8")
        tree = _parser.parse(source)
        root = tree.root_node
        file_info.imports = _extract_imports(root, source)
        return _extract_symbols_from_node(root, source)
    except Exception as e:
        logger.error(f"Error extracting symbols from {file_info.relative_path}: {e}")
        return []


def _clean_response(text: str) -> str:
    """Clean LLM response: remove code fences, nested fences, thinking tags."""
    if not text:
        return ""
    cleaned = text.strip()
    # Remove thinking tags
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL)
    # Remove outer code fences
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        end_idx = len(lines)
        for j in range(1, len(lines)):
            if lines[j].strip() == "```":
                end_idx = j
                break
        cleaned = "\n".join(lines[1:end_idx])
    # Remove nested code fences
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
        content = file_info.content[:MAX_CODE_CHARS] if len(file_info.content) > MAX_CODE_CHARS else file_info.content
        classes = [s.name for s in file_info.symbols if s.type in ("class", "interface")]
        functions = [s.name for s in file_info.symbols if s.type == "function"]

        sys_p = "你是代码分析专家。用中文简洁描述模块职责，1-2句话，不超过80字。不要包含代码围栏。"
        usr_p = f"文件: {file_info.relative_path}\n类: {', '.join(classes) or '无'}\n函数: {', '.join(functions) or '无'}\n\n代码片段:\n```python\n{content[:5000]}\n```\n\n请用中文简洁描述此模块的核心职责（1-2句）。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 15:
            result = f"该模块提供 {len(classes)} 个类和 {len(functions)} 个函数，用于 {file_info.relative_path.replace('/', '.').replace('.py', '')} 相关功能。"
        return result

    def generate_module_usage(self, file_info: FileInfo) -> str:
        classes = [s.name for s in file_info.symbols if s.type in ("class", "interface")][:3]
        functions = [s.name for s in file_info.symbols if s.type == "function"][:3]

        sys_p = "你是Python专家。生成3-5行简洁的使用示例代码，包含导入语句和基本调用。只输出代码，不要解释。"
        usr_p = f"模块路径: {file_info.relative_path}\n可用类: {', '.join(classes) or '无'}\n可用函数: {', '.join(functions) or '无'}\n\n生成3-5行简洁的使用示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 20:
            mod_name = file_info.relative_path.replace('/', '.').replace('.py', '')
            result = f"from src.kit.{mod_name} import {classes[0] if classes else functions[0] if functions else 'Module'}"
        return result

    # ── Interface ───────────────────────────────────────────────────────
    def summarize_interface(self, file_path: str, symbol: SymbolInfo) -> str:
        code = symbol.code[:5000] if len(symbol.code) > 5000 else symbol.code
        abs_methods = ", ".join(symbol.abstract_methods[:6]) if symbol.abstract_methods else ", ".join(symbol.methods[:6])

        sys_p = "你是代码分析专家。用中文简洁描述接口/抽象类的契约，1-2句话，不超过60字。不要包含代码围栏。"
        usr_p = f"文件: {file_path}\n接口名: {symbol.name}\n基类: {', '.join(symbol.base_classes)}\n抽象方法: {abs_methods}\n文档: {symbol.docstring[:100]}\n\n请用中文简洁描述此接口的职责（1-2句）。"

        result = self._call_llm(sys_p, usr_p, max_tokens=150)
        if not result or len(result) < 15:
            result = f"{symbol.name} 是抽象接口，定义了 {abs_methods} 等方法的契约。"
        return result

    def generate_interface_usage(self, file_path: str, symbol: SymbolInfo) -> str:
        abs_methods = symbol.abstract_methods[:4] if symbol.abstract_methods else symbol.methods[:4]

        sys_p = "你是Python专家。生成3-5行简洁的接口实现示例。只输出代码，不要解释。"
        usr_p = f"接口: {symbol.name}\n基类: {', '.join(symbol.base_classes)}\n需实现的方法: {', '.join(abs_methods)}\n\n生成3-5行简洁的实现示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 20:
            methods_stub = "\n    ".join(f"def {m}(self, *args): ..." for m in abs_methods[:3])
            result = f"class MyImpl({symbol.name}):\n    {methods_stub}"
        return result

    # ── Class ───────────────────────────────────────────────────────────
    def summarize_class(self, file_path: str, symbol: SymbolInfo) -> str:
        code = symbol.code[:5000] if len(symbol.code) > 5000 else symbol.code

        sys_p = "你是代码分析专家。用中文简洁描述类的职责，1-2句话，不超过60字。不要包含代码围栏。"
        usr_p = f"文件: {file_path}\n类名: {symbol.name}\n基类: {', '.join(symbol.base_classes) or '无'}\n方法: {', '.join(symbol.methods[:6]) or '无'}\n文档: {symbol.docstring[:100]}\n\n请用中文简洁描述此类的职责（1-2句）。"

        result = self._call_llm(sys_p, usr_p, max_tokens=150)
        if not result or len(result) < 15:
            methods_str = ", ".join(symbol.methods[:4]) if symbol.methods else "无"
            result = f"{symbol.name} 类封装相关功能，提供 {methods_str} 等方法。"
        return result

    def generate_class_usage(self, file_path: str, symbol: SymbolInfo) -> str:
        sys_p = "你是Python专家。生成3-5行简洁的类使用示例，展示实例化和方法调用。只输出代码，不要解释。"
        usr_p = f"类名: {symbol.name}\n基类: {', '.join(symbol.base_classes) or '无'}\n方法: {', '.join(symbol.methods[:5]) or '无'}\n参数: {symbol.params}\n\n生成3-5行简洁的使用示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=200)
        if not result or len(result) < 20:
            result = f"obj = {symbol.name}()\nresult = obj.{symbol.methods[0]}()" if symbol.methods else f"obj = {symbol.name}()"
        return result

    # ── Method / Function ───────────────────────────────────────────────
    def summarize_function(self, file_path: str, symbol: SymbolInfo) -> str:
        func_type = "方法" if symbol.type == "method" else "函数"
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name

        sys_p = f"你是代码分析专家。用中文简洁描述{func_type}的功能，1句话，不超过50字。不要包含代码围栏。"
        usr_p = f"文件: {file_path}\n{func_type}名: {full_name}\n参数: {symbol.params}\n文档: {symbol.docstring[:100]}\n\n请用中文简洁描述此{func_type}的功能（1句）。"

        result = self._call_llm(sys_p, usr_p, max_tokens=100)
        if not result or len(result) < 10:
            doc_hint = f"，{symbol.docstring[:40]}" if symbol.docstring else ""
            result = f"{full_name} {func_type}处理 {symbol.params} 参数{doc_hint}。"
        return result

    def generate_function_usage(self, file_path: str, symbol: SymbolInfo) -> str:
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name
        func_type = "方法" if symbol.type == "method" else "函数"

        sys_p = "你是Python专家。生成2-3行简洁的函数/方法调用示例。只输出代码，不要解释。"
        usr_p = f"{func_type}名: {full_name}\n参数: {symbol.params}\n\n生成2-3行简洁的调用示例。"

        result = self._call_llm(sys_p, usr_p, max_tokens=150)
        if not result or len(result) < 15:
            result = f"result = {full_name}()\nprint(result)"
        return result


class SummaryFormatter:
    @staticmethod
    def format_module(file_info: FileInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        return f"# module `{file_info.relative_path}`\n\n## function:\n\n{summary}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_interface(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        extends = ", ".join(symbol.base_classes) if symbol.base_classes else "none"
        # Find classes that implement this interface (from same file)
        implemented_by = "unknown"
        return f"# interface `{symbol.name}`\n\n## function:\n\n{summary}\n\n## extends:\n\n{extends}\n\n## implemented by:\n\n{implemented_by}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_class(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        extends = ", ".join(symbol.base_classes) if symbol.base_classes else "none"
        return f"# class `{symbol.name}`\n\n## function:\n\n{summary}\n\n## extends:\n\n{extends}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_method(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        if not usage:
            # Simple fallback for methods without usage examples
            full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name
            usage = f"```python\nobj.{symbol.name}()\n```"
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name
        return f"# method `{full_name}{symbol.params}`\n\n## function:\n\n{summary}\n\n## usage example:\n\n{usage}\n"

    @staticmethod
    def format_function(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        return f"# func `{symbol.name}{symbol.params}`\n\n## function:\n\n{summary}\n\n## usage example:\n\n{usage}\n"


def run_extraction(
    repo_path: str = KIT_REPO_PATH,
    output_path: str = OUTPUT_PATH,
    api_key: str = DEFAULT_API_KEY,
    base_url: str = DEFAULT_BASE_URL,
    model: str = DEFAULT_MODEL,
    max_files: int = 0,
    level: str = "all",
    batch_size: int = 0,
    resume_from: int = 0,
) -> None:
    logger.info("=" * 60)
    logger.info("Summary Extraction Pipeline v3 (Concise)")
    logger.info("=" * 60)
    logger.info(f"Repository: {repo_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Model: {model}")
    logger.info(f"Level: {level}")

    logger.info("\n[Phase 1] Discovering files...")
    files = discover_files(repo_path)
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
        logger.info(f"  [{i+1}/{len(files)}] {fi.relative_path}: {types}")

    logger.info("\n[Phase 3] Generating summaries...")
    summarizer = LLMSummarizer(api_key=api_key, base_url=base_url, model=model)
    all_entries: List[str] = []
    formatter = SummaryFormatter()

    for i, fi in enumerate(files):
        logger.info(f"\n  [{i+1}/{len(files)}] {fi.relative_path}")

        # Module
        logger.info("    module...")
        m_sum = summarizer.summarize_module(fi)
        m_use = summarizer.generate_module_usage(fi)
        all_entries.append(formatter.format_module(fi, m_sum, m_use))

        if level in ("interface", "class", "all"):
            # Interfaces (ABC / Protocol)
            for s in [s for s in fi.symbols if s.type == "interface"]:
                logger.info(f"    interface {s.name}...")
                i_sum = summarizer.summarize_interface(fi.relative_path, s)
                i_use = summarizer.generate_interface_usage(fi.relative_path, s)
                all_entries.append(formatter.format_interface(fi.relative_path, s, i_sum, i_use))

        if level in ("class", "all"):
            # Classes
            for s in [s for s in fi.symbols if s.type == "class"]:
                logger.info(f"    class {s.name}...")
                c_sum = summarizer.summarize_class(fi.relative_path, s)
                c_use = summarizer.generate_class_usage(fi.relative_path, s)
                all_entries.append(formatter.format_class(fi.relative_path, s, c_sum, c_use))

        if level == "all":
            # Methods (no usage example to save API calls)
            for cls in [s for s in fi.symbols if s.type in ("class", "interface")]:
                for method in [s for s in fi.symbols if s.type == "method" and s.parent_class == cls.name]:
                    logger.info(f"    method {cls.name}.{method.name}...")
                    mt_sum = summarizer.summarize_function(fi.relative_path, method)
                    all_entries.append(formatter.format_method(fi.relative_path, method, mt_sum, ""))

            # Functions
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


def main():
    parser = argparse.ArgumentParser(description="Extract concise code summaries (v3)")
    parser.add_argument("--repo-path", dest="repo_path", default=KIT_REPO_PATH)
    parser.add_argument("--output", dest="output_path", default=OUTPUT_PATH)
    parser.add_argument("--api-key", dest="api_key", default=DEFAULT_API_KEY)
    parser.add_argument("--base-url", dest="base_url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-files", dest="max_files", type=int, default=0)
    parser.add_argument("--level", choices=["module", "interface", "class", "all"], default="all")
    parser.add_argument("--batch-size", dest="batch_size", type=int, default=0)
    parser.add_argument("--resume-from", dest="resume_from", type=int, default=0)
    args = parser.parse_args()
    run_extraction(**vars(args))


if __name__ == "__main__":
    main()

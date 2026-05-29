#!/usr/bin/env python3
"""
Summary Extraction Script v2 - High Quality Version

Generates detailed summaries with real usage examples following 0528_summary_preview.md format.
"""

import argparse
import glob
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import tree_sitter_python as tspython
from tree_sitter import Language, Node, Parser
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

DEFAULT_API_KEY = "tp-cbs3hu9i4xsldjtuyl82fj2l9uo2py2qe3ulrhc1zzhj8ij5"
DEFAULT_BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"
KIT_REPO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kit", "src", "kit")
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "summary_output_kit.md")

MAX_CODE_CHARS = 25000
API_CALL_DELAY = 0.3
MAX_RETRIES = 3

SKIP_PATTERNS = {"__pycache__", ".pyc"}
SKIP_FILES = {"__init__.py", "__main__.py"}

_ts_language = Language(tspython.language())
_parser = Parser(_ts_language)


@dataclass
class SymbolInfo:
    name: str
    type: str
    code: str
    start_line: int
    end_line: int
    parent_class: Optional[str] = None
    params: str = ""
    docstring: str = ""
    base_classes: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
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
            
            file_info = FileInfo(
                relative_path=rel_path,
                absolute_path=file_path,
                content=content,
                lines=len(content.splitlines()),
            )
            files.append(file_info)
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
        attributes = []
        if body_node:
            for child in body_node.children:
                if child.type == "function_definition":
                    m_name = child.child_by_field_name("name")
                    if m_name:
                        methods.append(m_name.text.decode())
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
        
        symbols.append(SymbolInfo(
            name=class_name,
            type="class",
            code=class_code,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            docstring=docstring,
            base_classes=base_classes,
            methods=methods,
            attributes=attributes,
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
            name=func_name,
            type=symbol_type,
            code=func_code,
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            parent_class=parent_class,
            params=params,
            docstring=docstring,
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
        
        imports = _extract_imports(root, source)
        file_info.imports = imports
        
        symbols = _extract_symbols_from_node(root, source)
        return symbols
    except Exception as e:
        logger.error(f"Error extracting symbols from {file_info.relative_path}: {e}")
        return []


class LLMSummarizer:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.call_count = 0
    
    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=0.4,
                )
                self.call_count += 1
                result = response.choices[0].message.content or ""
                
                if API_CALL_DELAY > 0:
                    time.sleep(API_CALL_DELAY)
                
                cleaned = result.strip()
                # Remove outer code fences if present
                if cleaned.startswith("```"):
                    lines = cleaned.split("\n")
                    # Find the first end fence
                    end_idx = len(lines)
                    for j in range(1, len(lines)):
                        if lines[j].strip() == "```":
                            end_idx = j
                            break
                    cleaned = "\n".join(lines[1:end_idx])
                
                # Remove nested code fences - handle ```python\n```python pattern
                import re
                # Remove duplicate opening fences
                cleaned = re.sub(r'```\w*\n```', '```', cleaned)
                # Remove text between ```python and next ```python
                cleaned = re.sub(r'```python\n(.*?)```python\n', r'```python\n', cleaned, flags=re.DOTALL)
                # Clean up any remaining nested fences
                cleaned = cleaned.replace("```python\n```python", "```python")
                cleaned = cleaned.replace("```\n```", "```")
                
                return cleaned
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        return ""
    
    def summarize_module(self, file_info: FileInfo) -> str:
        content = file_info.content
        if len(content) > MAX_CODE_CHARS:
            content = content[:MAX_CODE_CHARS] + "\n# ... (truncated)"
        
        classes = [s.name for s in file_info.symbols if s.type == "class"]
        functions = [s.name for s in file_info.symbols if s.type == "function"]
        
        system_prompt = """你是代码分析专家。请用中文生成详细的模块摘要。

要求：
1. 用中文描述模块的整体用途和核心能力
2. 说明模块在项目中的主要作用
3. 描述关键实现细节（使用了什么技术/库）
4. 2-4句话，详细且具体
5. 不要包含代码围栏或标题前缀"""

        user_prompt = f"""分析以下 Python 模块并生成详细摘要。

文件路径: {file_info.relative_path}
导入的模块: {', '.join(file_info.imports[:10])}
包含的类: {', '.join(classes) if classes else '无'}
包含的函数: {', '.join(functions) if functions else '无'}

代码:
```python
{content}
```

请用中文详细描述此模块的用途、核心能力和关键实现（2-4句话）。"""

        result = self._call_llm(system_prompt, user_prompt, max_tokens=500)
        if not result or len(result) < 30:
            # Better fallback with more context
            imports_str = ", ".join(file_info.imports[:5]) if file_info.imports else "无"
            classes_str = ", ".join(classes[:5]) if classes else "无"
            funcs_str = ", ".join(functions[:5]) if functions else "无"
            result = f"该模块位于 {file_info.relative_path}，导入了 {imports_str}。它提供 {len(classes)} 个类（{classes_str}）和 {len(functions)} 个函数（{funcs_str}），用于实现特定的功能。"
        return result
    
    def generate_module_usage(self, file_info: FileInfo, summary: str) -> str:
        classes = [s for s in file_info.symbols if s.type == "class"][:3]
        functions = [s for s in file_info.symbols if s.type == "function"][:3]
        
        class_info = ""
        for cls in classes:
            methods_str = ", ".join(cls.methods[:5]) if cls.methods else "无方法"
            class_info += f"\n- {cls.name}: 方法={methods_str}"
        
        func_info = ""
        for func in functions:
            func_info += f"\n- {func.name}{func.params}"
        
        system_prompt = """你是 Python 专家。请生成详细的使用示例代码。

要求：
1. 生成可运行的 Python 代码
2. 包含导入语句
3. 展示主要类的实例化和方法调用
4. 添加中文注释说明每一步
5. 代码要真实可用，不要假设不存在的方法"""

        user_prompt = f"""为以下 Python 模块生成详细的使用示例。

模块路径: {file_info.relative_path}
模块摘要: {summary}

可用的类:{class_info}

可用的函数:{func_info}

导入语句: {', '.join(file_info.imports[:5])}

请生成一个完整的使用示例，包含导入、实例化、方法调用和结果处理。添加中文注释。"""

        result = self._call_llm(system_prompt, user_prompt, max_tokens=800)
        if not result or len(result) < 30:
            result = f"from src.kit import {file_info.relative_path.replace('/', '.').replace('.py', '')}\n# 使用示例"
        return result
    
    def summarize_class(self, file_path: str, symbol: SymbolInfo) -> str:
        code = symbol.code
        if len(code) > MAX_CODE_CHARS:
            code = code[:MAX_CODE_CHARS] + "\n    ..."
        
        system_prompt = """你是代码分析专家。请用中文生成详细的类摘要。

要求：
1. 描述类的核心职责和封装的数据/行为
2. 说明类在系统中的角色
3. 如果有继承，说明继承关系
4. 2-4句话，详细且具体
5. 不要包含代码围栏或标题前缀"""

        base_info = f"继承自: {', '.join(symbol.base_classes)}" if symbol.base_classes else "无继承"
        method_info = f"方法: {', '.join(symbol.methods[:10])}" if symbol.methods else "无方法"
        attr_info = f"属性: {', '.join(symbol.attributes[:5])}" if symbol.attributes else ""
        doc_info = f"文档字符串: {symbol.docstring[:200]}" if symbol.docstring else ""

        user_prompt = f"""分析以下 Python 类并生成详细摘要。

文件: {file_path}
类名: {symbol.name}
{base_info}
{method_info}
{attr_info}
{doc_info}

代码:
```python
{code}
```

请用中文详细描述此类的用途、职责和在系统中的角色（2-4句话）。"""

        result = self._call_llm(system_prompt, user_prompt, max_tokens=400)
        if not result or len(result) < 30:
            # Better fallback with more context
            methods_str = ", ".join(symbol.methods[:5]) if symbol.methods else "无"
            base_str = f"继承自 {', '.join(symbol.base_classes)}" if symbol.base_classes else "无继承"
            doc_hint = f"。{symbol.docstring[:80]}" if symbol.docstring else ""
            result = f"{symbol.name} 是一个 Python 类（{base_str}），提供以下方法：{methods_str}{doc_hint}。此类封装了相关数据和行为，在系统中扮演特定角色。"
        return result
    
    def generate_class_usage(self, file_path: str, symbol: SymbolInfo, summary: str) -> str:
        system_prompt = """你是 Python 专家。请生成详细的类使用示例。

要求：
1. 生成可运行的 Python 代码
2. 展示类的实例化
3. 展示主要方法的调用
4. 添加中文注释说明每一步
5. 代码要真实可用"""

        user_prompt = f"""为以下 Python 类生成详细的使用示例。

文件: {file_path}
类名: {symbol.name}
继承: {', '.join(symbol.base_classes) if symbol.base_classes else '无'}
方法: {', '.join(symbol.methods[:8]) if symbol.methods else '无'}
初始化参数: {symbol.params}

类摘要: {summary}

请生成一个完整的使用示例，展示如何实例化和使用此类。添加中文注释。"""

        result = self._call_llm(system_prompt, user_prompt, max_tokens=600)
        if not result or len(result) < 30:
            result = f"# 创建 {symbol.name} 实例\nobj = {symbol.name}()\n# 调用方法\nresult = obj.some_method()"
        return result
    
    def summarize_function(self, file_path: str, symbol: SymbolInfo) -> str:
        code = symbol.code
        if len(code) > MAX_CODE_CHARS:
            code = code[:MAX_CODE_CHARS] + "\n    ..."
        
        system_prompt = """你是代码分析专家。请用中文生成详细的函数/方法摘要。

要求：
1. 描述函数的核心任务
2. 说明主要输入参数和返回值
3. 描述处理逻辑
4. 2-3句话，详细且具体
5. 不要包含代码围栏或标题前缀"""

        doc_info = f"文档字符串: {symbol.docstring[:200]}" if symbol.docstring else ""
        func_type = "方法" if symbol.type == "method" else "函数"
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name

        user_prompt = f"""分析以下 Python {func_type}并生成详细摘要。

文件: {file_path}
{func_type}名: {full_name}
参数: {symbol.params}
{doc_info}

代码:
```python
{code}
```

请用中文详细描述此{func_type}的用途、输入输出和处理逻辑（2-3句话）。"""

        result = self._call_llm(system_prompt, user_prompt, max_tokens=350)
        if not result or len(result) < 30:
            # Better fallback with more context
            doc_hint = f"。{symbol.docstring[:50]}" if symbol.docstring else ""
            result = f"{full_name} 是一个 {func_type}，接受 {symbol.params} 参数{doc_hint}。该{func_type}执行特定的处理逻辑并返回结果。"
        return result
    
    def generate_function_usage(self, file_path: str, symbol: SymbolInfo, summary: str) -> str:
        system_prompt = """你是 Python 专家。请生成详细的函数使用示例。

要求：
1. 生成可运行的 Python 代码
2. 展示函数调用和参数传递
3. 展示返回值的处理
4. 添加中文注释说明每一步
5. 代码要真实可用"""

        func_type = "方法" if symbol.type == "method" else "函数"
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name

        user_prompt = f"""为以下 Python {func_type}生成详细的使用示例。

文件: {file_path}
{func_type}名: {full_name}
参数: {symbol.params}

{func_type}摘要: {summary}

请生成一个完整的使用示例，展示如何调用此{func_type}并处理返回值。添加中文注释。"""

        result = self._call_llm(system_prompt, user_prompt, max_tokens=400)
        if not result or len(result) < 30:
            result = f"# 调用 {full_name}\nresult = {full_name}()\nprint(result)"
        return result


class SummaryFormatter:
    @staticmethod
    def format_module(file_info: FileInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        return f"""# module `{file_info.relative_path}`

## function:

{summary}

## usage example:

{usage}
"""

    @staticmethod
    def format_class(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        extends = ", ".join(symbol.base_classes) if symbol.base_classes else "none"
        return f"""# class `{symbol.name}`

## function:

{summary}

## extends:

{extends}

## usage example:

{usage}
"""

    @staticmethod
    def format_method(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        full_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name
        return f"""# method `{full_name}{symbol.params}`

## function:

{summary}

## usage example:

{usage}
"""

    @staticmethod
    def format_function(file_path: str, symbol: SymbolInfo, summary: str, usage: str) -> str:
        usage = usage.strip()
        if usage and not usage.startswith("```"):
            usage = f"```python\n{usage}\n```"
        return f"""# func `{symbol.name}{symbol.params}`

## function:

{summary}

## usage example:

{usage}
"""


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
    valid_levels = ["module", "class", "all"]
    if level not in valid_levels:
        raise ValueError(f"Invalid level: {level}. Must be one of {valid_levels}")
    
    logger.info("=" * 60)
    logger.info("Summary Extraction Pipeline v2 (High Quality)")
    logger.info("=" * 60)
    logger.info(f"Repository: {repo_path}")
    logger.info(f"Output: {output_path}")
    logger.info(f"Model: {model}")
    logger.info(f"Level: {level}")
    
    logger.info("\n[Phase 1] Discovering files...")
    files = discover_files(repo_path)
    if max_files > 0:
        files = files[:max_files]
        logger.info(f"Limited to {max_files} files")
    
    if resume_from > 0:
        files = files[resume_from:]
        logger.info(f"Resuming from file index {resume_from}")
    
    if batch_size > 0:
        files = files[:batch_size]
        logger.info(f"Processing batch of {batch_size} files")
    
    logger.info("\n[Phase 2] Extracting symbols...")
    for i, file_info in enumerate(files):
        file_info.symbols = extract_symbols(file_info)
        classes = sum(1 for s in file_info.symbols if s.type == "class")
        funcs = sum(1 for s in file_info.symbols if s.type == "function")
        methods = sum(1 for s in file_info.symbols if s.type == "method")
        logger.info(f"  [{i+1}/{len(files)}] {file_info.relative_path}: {classes} classes, {funcs} functions, {methods} methods")
    
    logger.info("\n[Phase 3] Generating summaries with LLM...")
    summarizer = LLMSummarizer(api_key=api_key, base_url=base_url, model=model)
    
    all_entries: List[str] = []
    formatter = SummaryFormatter()
    
    for i, file_info in enumerate(files):
        logger.info(f"\n  [{i+1}/{len(files)}] Processing {file_info.relative_path}...")
        
        logger.info(f"    Generating module summary...")
        module_summary = summarizer.summarize_module(file_info)
        
        logger.info(f"    Generating module usage example...")
        module_usage = summarizer.generate_module_usage(file_info, module_summary)
        
        entry = formatter.format_module(file_info, module_summary, module_usage)
        all_entries.append(entry)
        
        if level in ["class", "all"]:
            classes = [s for s in file_info.symbols if s.type == "class"]
            for cls in classes:
                logger.info(f"    Generating class summary: {cls.name}...")
                cls_summary = summarizer.summarize_class(file_info.relative_path, cls)
                
                logger.info(f"    Generating class usage example...")
                cls_usage = summarizer.generate_class_usage(file_info.relative_path, cls, cls_summary)
                
                entry = formatter.format_class(file_info.relative_path, cls, cls_summary, cls_usage)
                all_entries.append(entry)
        
        if level == "all":
            for cls in [s for s in file_info.symbols if s.type == "class"]:
                methods = [s for s in file_info.symbols if s.type == "method" and s.parent_class == cls.name]
                for method in methods:
                    logger.info(f"    Generating method summary: {cls.name}.{method.name}...")
                    method_summary = summarizer.summarize_function(file_info.relative_path, method)
                    method_usage = summarizer.generate_function_usage(file_info.relative_path, method, method_summary)
                    entry = formatter.format_method(file_info.relative_path, method, method_summary, method_usage)
                    all_entries.append(entry)
            
            functions = [s for s in file_info.symbols if s.type == "function"]
            for func in functions:
                logger.info(f"    Generating function summary: {func.name}...")
                func_summary = summarizer.summarize_function(file_info.relative_path, func)
                func_usage = summarizer.generate_function_usage(file_info.relative_path, func, func_summary)
                entry = formatter.format_function(file_info.relative_path, func, func_summary, func_usage)
                all_entries.append(entry)
    
    logger.info(f"\n[Phase 4] Writing output to {output_path}...")
    
    file_exists = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    
    with open(output_path, "a" if file_exists else "w", encoding="utf-8") as f:
        if not file_exists:
            header = f"""# Summary Output - Kit Repository

> 由大模型 mimo-v2.5-pro 自动生成，展示 kit 代码仓的模块、类、方法、函数摘要 + 使用示例。
> 生成时间: {time.strftime("%Y-%m-%d %H:%M:%S")}

---

"""
            f.write(header)
        else:
            f.write("\n\n")
        f.write("\n\n".join(all_entries))
        f.write("\n")
    
    total_entries = len(all_entries)
    total_calls = summarizer.call_count
    logger.info("\n" + "=" * 60)
    logger.info("Extraction Complete!")
    logger.info(f"  Files processed: {len(files)}")
    logger.info(f"  Summary entries: {total_entries}")
    logger.info(f"  LLM API calls: {total_calls}")
    logger.info(f"  Output: {output_path}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Extract code summaries from kit repository using MiMo-v2.5-pro LLM (High Quality v2)"
    )
    parser.add_argument("--repo-path", default=KIT_REPO_PATH)
    parser.add_argument("--output", default=OUTPUT_PATH)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-files", type=int, default=0)
    parser.add_argument("--level", choices=["module", "class", "all"], default="class")
    parser.add_argument("--batch-size", type=int, default=0)
    parser.add_argument("--resume-from", type=int, default=0)
    
    args = parser.parse_args()
    
    run_extraction(
        repo_path=args.repo_path,
        output_path=args.output,
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        max_files=args.max_files,
        level=args.level,
        batch_size=args.batch_size,
        resume_from=args.resume_from,
    )


if __name__ == "__main__":
    main()

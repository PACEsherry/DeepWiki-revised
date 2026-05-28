#!/usr/bin/env python3
"""
Summary Extraction Script

基于 deepwiki-open 和 kit 的代码分析逻辑，使用 MiMo 大模型提取代码仓库摘要。
输出格式遵循 Summary_Output_Templet.md 模板。

Usage:
    python summary_extraction.py <repo_path_or_url> [--output summary_output.md] [--language zh]
"""

import argparse
import ast
import json
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

@dataclass
class MiMoConfig:
    """MiMo 大模型配置"""
    api_key: Optional[str] = field(default_factory=lambda: os.environ.get("MIMO_API_KEY"))
    base_url: str = field(default_factory=lambda: os.environ.get("MIMO_BASE_URL", "https://api.openai.com/v1"))
    model: str = field(default_factory=lambda: os.environ.get("MIMO_MODEL", "mimo-7b"))
    max_tokens: int = 4096
    temperature: float = 0.3

# File extensions to process
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".swift", ".cs", ".kt", ".scala", ".r",
    ".m", ".mm", ".vue", ".svelte"
}

DOC_EXTENSIONS = {".md", ".txt", ".rst", ".json", ".yaml", ".yml", ".toml"}

# Directories to exclude
EXCLUDED_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", ".nuxt", "coverage", ".idea", ".vscode",
    "vendor", "target", "bin", "obj", ".tox", ".mypy_cache", ".pytest_cache"
}

# ============================================================================
# File Reading (based on deepwiki-open data_pipeline.py)
# ============================================================================

@dataclass
class CodeDocument:
    """代码文档对象"""
    file_path: str
    content: str
    file_type: str
    is_code: bool
    token_count: int = 0

def count_tokens_approx(text: str) -> int:
    """近似计算 token 数量（4字符约等于1 token）"""
    return len(text) // 4

def should_process_file(file_path: str, excluded_dirs: Set[str]) -> bool:
    """判断文件是否应该被处理"""
    path_parts = Path(file_path).parts
    for part in path_parts:
        if part in excluded_dirs:
            return False
    return True

def read_repository_files(repo_path: str, excluded_dirs: Set[str] = None) -> List[CodeDocument]:
    """读取仓库中的所有代码文件"""
    if excluded_dirs is None:
        excluded_dirs = EXCLUDED_DIRS

    documents = []
    repo_path = Path(repo_path)

    if not repo_path.exists():
        logger.error(f"Repository path does not exist: {repo_path}")
        return documents

    logger.info(f"Reading files from: {repo_path}")

    # Process code files
    for ext in CODE_EXTENSIONS:
        for file_path in repo_path.rglob(f"*{ext}"):
            if not should_process_file(str(file_path), excluded_dirs):
                continue

            try:
                relative_path = file_path.relative_to(repo_path)
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                if not content.strip():
                    continue

                token_count = count_tokens_approx(content)
                if token_count > 50000:  # Skip very large files
                    logger.warning(f"Skipping large file {relative_path}: {token_count} tokens")
                    continue

                doc = CodeDocument(
                    file_path=str(relative_path),
                    content=content,
                    file_type=ext[1:],
                    is_code=True,
                    token_count=token_count
                )
                documents.append(doc)
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

    # Process documentation files
    for ext in DOC_EXTENSIONS:
        for file_path in repo_path.rglob(f"*{ext}"):
            if not should_process_file(str(file_path), excluded_dirs):
                continue

            try:
                relative_path = file_path.relative_to(repo_path)
                content = file_path.read_text(encoding="utf-8", errors="ignore")

                if not content.strip():
                    continue

                token_count = count_tokens_approx(content)
                if token_count > 20000:  # Skip large doc files
                    continue

                doc = CodeDocument(
                    file_path=str(relative_path),
                    content=content,
                    file_type=ext[1:],
                    is_code=False,
                    token_count=token_count
                )
                documents.append(doc)
            except Exception as e:
                logger.error(f"Error reading {file_path}: {e}")

    logger.info(f"Found {len(documents)} documents")
    return documents

# ============================================================================
# Symbol Extraction (based on kit tree_sitter_symbol_extractor.py)
# ============================================================================

@dataclass
class CodeSymbol:
    """代码符号对象"""
    name: str
    symbol_type: str  # function, class, method, interface, variable, constant
    file_path: str
    start_line: int
    end_line: int
    code: str
    docstring: Optional[str] = None
    parent_class: Optional[str] = None
    parameters: Optional[str] = None
    return_type: Optional[str] = None
    decorators: Optional[List[str]] = None

def extract_python_symbols(file_path: str, content: str) -> List[CodeSymbol]:
    """从 Python 文件中提取符号"""
    symbols = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return symbols

    lines = content.split('\n')

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Extract class
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            code = '\n'.join(lines[start_line-1:end_line])
            docstring = ast.get_docstring(node)

            # Get base classes
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
                elif isinstance(base, ast.Attribute):
                    bases.append(f"{ast.dump(base)}")

            symbols.append(CodeSymbol(
                name=node.name,
                symbol_type="class",
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                code=code,
                docstring=docstring
            ))

            # Extract methods within class
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_start = item.lineno
                    method_end = item.end_lineno or method_start
                    method_code = '\n'.join(lines[method_start-1:method_end])
                    method_docstring = ast.get_docstring(item)

                    # Get parameters
                    params = []
                    for arg in item.args.args:
                        if arg.arg != 'self':
                            param_str = arg.arg
                            if arg.annotation:
                                param_str += f": {ast.dump(arg.annotation)}"
                            params.append(param_str)

                    # Get return type
                    return_type = None
                    if item.returns:
                        return_type = ast.dump(item.returns)

                    # Get decorators
                    decorators = []
                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Name):
                            decorators.append(dec.id)
                        elif isinstance(dec, ast.Attribute):
                            decorators.append(dec.attr)

                    symbols.append(CodeSymbol(
                        name=item.name,
                        symbol_type="method",
                        file_path=file_path,
                        start_line=method_start,
                        end_line=method_end,
                        code=method_code,
                        docstring=method_docstring,
                        parent_class=node.name,
                        parameters=', '.join(params),
                        return_type=return_type,
                        decorators=decorators
                    ))

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not any(
            isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
            if node in ast.walk(parent)
        ):
            # Top-level function
            start_line = node.lineno
            end_line = node.end_lineno or start_line
            code = '\n'.join(lines[start_line-1:end_line])
            docstring = ast.get_docstring(node)

            # Get parameters
            params = []
            for arg in node.args.args:
                param_str = arg.arg
                if arg.annotation:
                    param_str += f": {ast.dump(arg.annotation)}"
                params.append(param_str)

            # Get return type
            return_type = None
            if node.returns:
                return_type = ast.dump(node.returns)

            # Get decorators
            decorators = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    decorators.append(dec.id)
                elif isinstance(dec, ast.Attribute):
                    decorators.append(dec.attr)

            symbols.append(CodeSymbol(
                name=node.name,
                symbol_type="function",
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                code=code,
                docstring=docstring,
                parameters=', '.join(params),
                return_type=return_type,
                decorators=decorators
            ))

    return symbols

def extract_symbols_from_file(file_path: str, content: str) -> List[CodeSymbol]:
    """根据文件类型提取符号"""
    ext = Path(file_path).suffix.lower()

    if ext == '.py':
        return extract_python_symbols(file_path, content)
    # TODO: Add support for other languages using tree-sitter
    # For now, return empty list for non-Python files
    return []

# ============================================================================
# LLM Client (based on kit summaries.py)
# ============================================================================

class MiMoClient:
    """MiMo 大模型客户端"""

    def __init__(self, config: MiMoConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        """延迟初始化 OpenAI 客户端"""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.config.api_key,
                    base_url=self.config.base_url
                )
            except ImportError:
                logger.error("openai package not installed. Install with: pip install openai")
                raise
        return self._client

    def generate_summary(self, prompt: str, system_prompt: str = None) -> str:
        """使用 MiMo 生成摘要"""
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling MiMo API: {e}")
            raise

# ============================================================================
# Summary Generation
# ============================================================================

SYSTEM_PROMPT = """你是一个专业的代码分析师，擅长分析代码仓库并生成结构化的摘要。
你需要分析代码中的库、模块、接口、类、方法、函数、配置、服务、变量、常量等，并按照指定格式生成摘要。

重要规则：
1. 使用中文生成摘要
2. 保持简洁但信息丰富
3. 按照模板格式输出
4. 每个条目必须包含 function 字段说明其用途
5. 提供 usage example 展示如何使用"""

def generate_library_summary(client: MiMoClient, repo_name: str, documents: List[CodeDocument]) -> str:
    """生成库级别的摘要"""
    # Get package.json, setup.py, pyproject.toml etc.
    config_files = [d for d in documents if d.file_path in [
        "package.json", "setup.py", "pyproject.toml", "Cargo.toml", "go.mod"
    ]]

    if not config_files:
        return ""

    config_content = "\n".join([f"=== {d.file_path} ===\n{d.content}" for d in config_files])

    prompt = f"""分析以下项目的配置文件，生成库级别的摘要。

项目名称: {repo_name}

配置文件内容:
{config_content}

请按照以下格式输出（只输出 library 部分）：

# library {repo_name}

## function:

[用简洁的中文说明该库的整体用途、核心能力]

## usage example:

```[语言]
[导入和使用示例]
```"""

    return client.generate_summary(prompt, SYSTEM_PROMPT)

def generate_module_summary(client: MiMoClient, module_path: str, documents: List[CodeDocument]) -> str:
    """生成模块级别的摘要"""
    # Get files in the module directory
    module_files = [d for d in documents if d.file_path.startswith(module_path) and d.is_code]

    if not module_files:
        return ""

    # Get the first few files to understand the module
    sample_files = module_files[:5]
    content = "\n".join([f"=== {d.file_path} ===\n{d.content[:2000]}" for d in sample_files])

    module_name = Path(module_path).name

    prompt = f"""分析以下模块的代码，生成模块级别的摘要。

模块路径: {module_path}
模块文件数: {len(module_files)}

代码内容:
{content}

请按照以下格式输出（只输出 module 部分）：

# module {module_name}

## function:

[说明该模块负责的业务范围或技术职责]

## usage example:

```[语言]
[导入和使用示例]
```"""

    return client.generate_summary(prompt, SYSTEM_PROMPT)

def generate_class_summary(client: MiMoClient, symbol: CodeSymbol) -> str:
    """生成类级别的摘要"""
    prompt = f"""分析以下类定义，生成类级别的摘要。

类名: {symbol.name}
文件路径: {symbol.file_path}

代码:
{symbol.code[:3000]}

{f"文档字符串: {symbol.docstring}" if symbol.docstring else ""}

请按照以下格式输出（只输出 class 部分）：

# class {symbol.name}

## function:

[说明该类的核心职责、封装的数据或行为]

## usage example:

```[语言]
[创建和使用该类的示例]
```"""

    return client.generate_summary(prompt, SYSTEM_PROMPT)

def generate_function_summary(client: MiMoClient, symbol: CodeSymbol) -> str:
    """生成函数级别的摘要"""
    func_type = "method" if symbol.symbol_type == "method" else "func"
    func_name = f"{symbol.parent_class}.{symbol.name}" if symbol.parent_class else symbol.name

    prompt = f"""分析以下函数/方法定义，生成函数级别的摘要。

函数名: {func_name}
类型: {symbol.symbol_type}
文件路径: {symbol.file_path}
参数: {symbol.parameters or '无'}

代码:
{symbol.code[:2000]}

{f"文档字符串: {symbol.docstring}" if symbol.docstring else ""}

请按照以下格式输出（只输出函数部分）：

# {func_type} {func_name}({symbol.parameters or ''})

## function:

[说明该函数完成的核心任务、主要输入、处理逻辑和输出结果]

## usage example:

```[语言]
[调用该函数的示例]
```"""

    return client.generate_summary(prompt, SYSTEM_PROMPT)

def generate_interface_summary(client: MiMoClient, symbol: CodeSymbol) -> str:
    """生成接口级别的摘要"""
    prompt = f"""分析以下接口定义，生成接口级别的摘要。

接口名: {symbol.name}
文件路径: {symbol.file_path}

代码:
{symbol.code[:2000]}

{f"文档字符串: {symbol.docstring}" if symbol.docstring else ""}

请按照以下格式输出（只输出 interface 部分）：

# interface {symbol.name}

## function:

[说明该接口描述的数据结构、对象职责或对外契约]

## extends:

[继承自哪些接口；如果没有则写 none]

## implemented by:

[被哪些类实现；如果没有则写 unknown]

## declaration:
```[语言]
[接口定义代码]
```

## usage example:

```[语言]
[实现和使用该接口的示例]
```"""

    return client.generate_summary(prompt, SYSTEM_PROMPT)

# ============================================================================
# Main Extraction Logic
# ============================================================================

def extract_repository_summary(
    repo_path: str,
    output_path: str = "summary_output.md",
    language: str = "zh",
    config: MiMoConfig = None
) -> str:
    """
    提取仓库摘要并生成输出文件

    Args:
        repo_path: 仓库路径或 URL
        output_path: 输出文件路径
        language: 输出语言
        config: MiMo 配置

    Returns:
        生成的摘要内容
    """
    if config is None:
        config = MiMoConfig()

    # Initialize MiMo client
    client = MiMoClient(config)

    # Read repository files
    logger.info(f"Reading repository: {repo_path}")
    documents = read_repository_files(repo_path)

    if not documents:
        logger.error("No documents found in repository")
        return ""

    # Get repository name
    repo_name = Path(repo_path).name if os.path.isdir(repo_path) else repo_path.split("/")[-1]

    # Collect all summaries
    summaries = []

    # 1. Generate library summary
    logger.info("Generating library summary...")
    library_summary = generate_library_summary(client, repo_name, documents)
    if library_summary:
        summaries.append(library_summary)

    # 2. Find and analyze modules (directories with __init__.py or index files)
    logger.info("Analyzing modules...")
    module_dirs = set()
    for doc in documents:
        if doc.file_path.endswith("__init__.py"):
            module_dir = str(Path(doc.file_path).parent)
            if module_dir and module_dir != ".":
                module_dirs.add(module_dir)

    for module_dir in list(module_dirs)[:10]:  # Limit to 10 modules
        logger.info(f"Generating module summary for: {module_dir}")
        module_summary = generate_module_summary(client, module_dir, documents)
        if module_summary:
            summaries.append(module_summary)

    # 3. Extract and analyze symbols
    logger.info("Extracting symbols...")
    all_symbols = []
    for doc in documents:
        if doc.is_code:
            symbols = extract_symbols_from_file(doc.file_path, doc.content)
            all_symbols.extend(symbols)

    logger.info(f"Found {len(all_symbols)} symbols")

    # Group symbols by type
    classes = [s for s in all_symbols if s.symbol_type == "class"]
    methods = [s for s in all_symbols if s.symbol_type == "method"]
    functions = [s for s in all_symbols if s.symbol_type == "function"]

    # 4. Generate class summaries
    logger.info("Generating class summaries...")
    for cls in classes[:20]:  # Limit to 20 classes
        logger.info(f"  Processing class: {cls.name}")
        class_summary = generate_class_summary(client, cls)
        if class_summary:
            summaries.append(class_summary)

    # 5. Generate method summaries
    logger.info("Generating method summaries...")
    for method in methods[:30]:  # Limit to 30 methods
        logger.info(f"  Processing method: {method.parent_class}.{method.name}")
        method_summary = generate_function_summary(client, method)
        if method_summary:
            summaries.append(method_summary)

    # 6. Generate function summaries
    logger.info("Generating function summaries...")
    for func in functions[:30]:  # Limit to 30 functions
        logger.info(f"  Processing function: {func.name}")
        func_summary = generate_function_summary(client, func)
        if func_summary:
            summaries.append(func_summary)

    # 7. Generate config summaries
    logger.info("Generating config summaries...")
    config_files = [d for d in documents if d.file_path.endswith((".json", ".yaml", ".yml", ".toml", ".env.example"))]
    for config_file in config_files[:5]:
        if config_file.file_path in ["package.json", "pyproject.toml", "Cargo.toml"]:
            continue  # Already handled in library summary

        prompt = f"""分析以下配置文件，生成配置级别的摘要。

文件路径: {config_file.file_path}

内容:
{config_file.content[:2000]}

请按照以下格式输出（只输出 config 部分）：

# config {Path(config_file.file_path).stem}

## function:

[说明该配置项或配置文件控制的功能范围]

## declaration:
```json
[关键配置项]
```

## usage example:

```[语言]
[如何使用该配置]
```"""

        config_summary = client.generate_summary(prompt, SYSTEM_PROMPT)
        if config_summary:
            summaries.append(config_summary)

    # Combine all summaries
    output_content = "\n\n---\n\n".join(summaries)

    # Add header
    header = f"""# {repo_name} - 代码仓库摘要

> 本文档由 summary_extraction.py 自动生成
> 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 使用模型: {config.model}

---

"""
    output_content = header + output_content

    # Write to file
    output_file = Path(output_path)
    output_file.write_text(output_content, encoding="utf-8")
    logger.info(f"Summary written to: {output_path}")

    return output_content

# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Extract code repository summary using MiMo LLM"
    )
    parser.add_argument(
        "repo_path",
        help="Path to local repository or repository URL"
    )
    parser.add_argument(
        "--output", "-o",
        default="summary_output.md",
        help="Output file path (default: summary_output.md)"
    )
    parser.add_argument(
        "--language", "-l",
        default="zh",
        help="Output language (default: zh)"
    )
    parser.add_argument(
        "--model",
        default=None,
        help="MiMo model name (default: from env MIMO_MODEL or mimo-7b)"
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="API base URL (default: from env MIMO_BASE_URL)"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (default: from env MIMO_API_KEY)"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Max tokens for generation (default: 4096)"
    )

    args = parser.parse_args()

    # Build config
    config = MiMoConfig()
    if args.model:
        config.model = args.model
    if args.base_url:
        config.base_url = args.base_url
    if args.api_key:
        config.api_key = args.api_key
    if args.max_tokens:
        config.max_tokens = args.max_tokens

    # Check API key
    if not config.api_key:
        logger.error("API key not set. Set MIMO_API_KEY environment variable or use --api-key")
        sys.exit(1)

    # Extract summary
    try:
        extract_repository_summary(
            repo_path=args.repo_path,
            output_path=args.output,
            language=args.language,
            config=config
        )
        logger.info("Summary extraction completed successfully!")
    except Exception as e:
        logger.error(f"Error during summary extraction: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

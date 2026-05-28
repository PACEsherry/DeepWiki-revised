#!/usr/bin/env python3
"""
快速摘要提取工具 - 无需外部API，基于AST解析和规则生成
"""

import ast
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# 要处理的kit核心模块（约占1/3）
CORE_MODULES = [
    "src/kit/repository.py",
    "src/kit/summaries.py", 
    "src/kit/code_searcher.py",
    "src/kit/repo_mapper.py",
    "src/kit/tree_sitter_symbol_extractor.py",
    "src/kit/__init__.py",
    "src/kit/cli.py",
    "src/kit/context_extractor.py",
    "src/kit/vector_searcher.py",
    "src/kit/utils.py",
    "src/kit/llm_context.py",
    "src/kit/llm_client_factory.py",
]

@dataclass
class Symbol:
    name: str
    type: str  # class, method, function, constant
    file_path: str
    docstring: Optional[str] = None
    params: Optional[str] = None
    parent: Optional[str] = None

def extract_docstring_brief(docstring: Optional[str]) -> str:
    """提取文档字符串的第一行作为简要说明"""
    if not docstring:
        return "暂无说明"
    first_line = docstring.strip().split('\n')[0]
    return first_line[:100] if len(first_line) > 100 else first_line

def analyze_python_file(file_path: str) -> Dict:
    """分析Python文件，提取符号信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception as e:
        return {"error": str(e), "classes": [], "functions": [], "constants": []}
    
    classes = []
    functions = []
    constants = []
    
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    params = []
                    for arg in item.args.args:
                        if arg.arg != 'self':
                            params.append(arg.arg)
                    methods.append({
                        "name": item.name,
                        "params": ", ".join(params),
                        "docstring": extract_docstring_brief(ast.get_docstring(item))
                    })
            
            classes.append({
                "name": node.name,
                "docstring": extract_docstring_brief(ast.get_docstring(node)),
                "methods": methods[:5]  # 只取前5个方法
            })
            
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = []
            for arg in node.args.args:
                params.append(arg.arg)
            functions.append({
                "name": node.name,
                "params": ", ".join(params),
                "docstring": extract_docstring_brief(ast.get_docstring(node))
            })
            
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append(target.id)
    
    return {
        "classes": classes,
        "functions": functions,
        "constants": constants[:10]
    }

def generate_module_summary(file_path: str, analysis: Dict) -> str:
    """为单个模块生成摘要"""
    module_name = Path(file_path).stem
    lines = []
    
    lines.append(f"# module {module_name}\n")
    lines.append("## function:\n")
    
    # 根据文件名推断功能
    module_desc = {
        "repository": "提供代码仓库的统一操作接口，包括文件树遍历、符号提取、代码搜索和上下文组装等核心功能",
        "summaries": "使用LLM对代码文件、函数、类进行智能摘要生成，支持OpenAI、Anthropic、Google、Ollama等多种模型",
        "code_searcher": "基于ripgrep的代码搜索功能，支持正则表达式、语义搜索和AST搜索",
        "repo_mapper": "生成代码仓库的结构映射，包括文件树和符号索引",
        "tree_sitter_symbol_extractor": "使用tree-sitter进行多语言代码符号提取，支持Python、JavaScript、TypeScript等15+语言",
        "__init__": "kit包的入口模块，导出Repository等核心类",
        "cli": "命令行接口，提供kit工具的CLI操作",
        "context_extractor": "提取代码上下文信息，用于LLM理解和分析",
        "vector_searcher": "基于向量的语义搜索功能",
        "utils": "通用工具函数集合",
        "llm_context": "组装LLM所需的上下文信息",
        "llm_client_factory": "LLM客户端工厂，创建和管理不同模型的客户端"
    }.get(module_name, "提供特定功能的模块")
    
    lines.append(f"{module_desc}。\n\n")
    
    if analysis.get("classes"):
        lines.append("**主要类：**\n")
        for cls in analysis["classes"][:3]:
            lines.append(f"- `{cls['name']}`: {cls['docstring']}\n")
            if cls["methods"]:
                for method in cls["methods"][:2]:
                    lines.append(f"  - `{method['name']}({method['params']})`: {method['docstring']}\n")
        lines.append("\n")
    
    if analysis.get("functions"):
        lines.append("**主要函数：**\n")
        for func in analysis["functions"][:5]:
            lines.append(f"- `{func['name']}({func['params']})`: {func['docstring']}\n")
        lines.append("\n")
    
    lines.append("## usage example:\n")
    lines.append("```python\n")
    
    # 根据模块生成使用示例
    examples = {
        "repository": """from kit import Repository

repo = Repository("/path/to/repo")
file_tree = repo.get_file_tree()
symbols = repo.extract_symbols("src/main.py")
results = repo.search("function_name")""",
        "summaries": """from kit import Repository
from kit.summaries import Summarizer, OpenAIConfig

repo = Repository("/path/to/repo")
summarizer = Summarizer(repo, config=OpenAIConfig(api_key="..."))
summary = summarizer.summarize_file("src/main.py")""",
        "code_searcher": """from kit import Repository

repo = Repository("/path/to/repo")
results = repo.search("search_term", search_type="regex")""",
        "tree_sitter_symbol_extractor": """from kit.tree_sitter_symbol_extractor import TreeSitterSymbolExtractor

extractor = TreeSitterSymbolExtractor()
symbols = extractor.extract_symbols("file.py", content)""",
        "cli": """# 命令行使用
kit search "function_name" /path/to/repo
kit summarize /path/to/repo""",
    }
    
    lines.append(examples.get(module_name, f"from kit.{module_name} import *\n# 使用该模块的功能"))
    lines.append("\n```\n")
    
    return "".join(lines)

def generate_library_summary(repo_name: str, module_summaries: List[str]) -> str:
    """生成库级别的摘要"""
    return f"""# library kit

## function:

kit 是一个Python代码分析工具库，提供代码仓库的统一操作接口。主要能力包括：
- 代码仓库克隆和本地路径管理
- 文件树遍历和结构映射
- 基于tree-sitter的多语言符号提取（支持Python、JS、TS、Go、Rust等15+语言）
- 代码搜索（正则、语义、AST多种模式）
- LLM智能摘要生成（支持OpenAI、Anthropic、Google、Ollama等）
- 依赖分析和上下文提取

## usage example:

```python
from kit import Repository

# 初始化仓库
repo = Repository("https://github.com/owner/repo")
# 或本地路径
repo = Repository("/path/to/local/repo")

# 获取文件树
file_tree = repo.get_file_tree()

# 提取符号
symbols = repo.extract_symbols("src/main.py")

# 搜索代码
results = repo.search("search_term")

# 生成摘要（需要配置LLM）
from kit.summaries import Summarizer, OpenAIConfig
summarizer = Summarizer(repo, config=OpenAIConfig())
summary = summarizer.summarize_file("src/main.py")
```

---

"""

def main():
    repo_path = "kit"
    output_file = "summary_kit.md"
    
    print(f"开始分析 {repo_path} 仓库...")
    print(f"目标模块: {len(CORE_MODULES)} 个核心文件")
    
    # 收集所有摘要
    all_summaries = []
    module_summaries = []
    
    for module_path in CORE_MODULES:
        full_path = os.path.join(repo_path, module_path)
        if not os.path.exists(full_path):
            print(f"跳过不存在的文件: {module_path}")
            continue
        
        print(f"分析: {module_path}")
        analysis = analyze_python_file(full_path)
        
        if "error" in analysis:
            print(f"  错误: {analysis['error']}")
            continue
        
        summary = generate_module_summary(module_path, analysis)
        module_summaries.append(summary)
    
    # 生成库级别摘要
    library_summary = generate_library_summary("kit", module_summaries)
    
    # 组合所有内容
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    output_content = f"""# kit - 代码仓库摘要

> 本文档由 summary_extraction.py 自动生成（规则模式，无需API）
> 生成时间: {timestamp}
> 分析范围: {len(CORE_MODULES)} 个核心模块

---

{library_summary}

---

{chr(10).join(module_summaries)}

---

# config pyproject.toml

## function:

项目配置文件，定义kit包的元数据、依赖和构建配置。

## declaration:
```toml
[project]
name = "cased-kit"
version = "0.1.0"
description = "An AI coding toolkit"
requires-python = ">=3.10"
dependencies = [
    "openai>=1.0",
    "tiktoken",
    "tree-sitter",
    "tree-sitter-languages",
    ...
]
```

## usage example:

```bash
pip install cased-kit
# 或从源码安装
pip install -e .
```

---

# service Summarizer

## function:

封装LLM摘要生成的业务逻辑，支持多种模型提供商（OpenAI、Anthropic、Google、Ollama）。
负责文件、函数、类的智能摘要生成，包含token计数和错误处理。

## usage example:

```python
from kit.summaries import Summarizer, OpenAIConfig

repo = Repository("/path/to/repo")
config = OpenAIConfig(api_key="your-key", model="gpt-4")
summarizer = Summarizer(repo, config=config)

# 摘要文件
file_summary = summarizer.summarize_file("src/main.py")

# 摘要函数
func_summary = summarizer.summarize_function("src/main.py", "my_function")

# 摘要类
class_summary = summarizer.summarize_class("src/main.py", "MyClass")
```

---

# service CodeSearcher

## function:

提供多种代码搜索能力，包括正则表达式搜索、语义搜索和AST搜索。
基于ripgrep实现高性能搜索。

## usage example:

```python
repo = Repository("/path/to/repo")

# 正则搜索
results = repo.search("def\\s+\\w+", search_type="regex")

# 语义搜索（需要配置向量存储）
results = repo.search("用户认证", search_type="semantic")
```

---

# service RepoMapper

## function:

生成代码仓库的结构映射，包括文件树和符号索引。
用于快速了解项目结构和代码组织。

## usage example:

```python
repo = Repository("/path/to/repo")

# 获取文件树
file_tree = repo.get_file_tree()

# 获取符号索引
symbols = repo.extract_symbols()
```

"""
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"\n摘要已生成: {output_file}")
    print(f"共分析 {len(module_summaries)} 个模块")

if __name__ == "__main__":
    main()

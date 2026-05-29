# kit - 代码仓库摘要

> 本文档由 summary_extraction.py 自动生成（规则模式，无需API）
> 生成时间: 2026-05-28 17:19:47
> 分析范围: 12 个核心模块

---

# library kit

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



---

# module repository
## function:
提供代码仓库的统一操作接口，包括文件树遍历、符号提取、代码搜索和上下文组装等核心功能。

**主要类：**
- `Repository`: Main interface for codebase operations: file tree, symbol extraction, search, and context.
  - `__init__(path_or_url, github_token, cache_dir, ref)`: 暂无说明
  - `_checkout_ref(ref)`: Checkout a specific ref (SHA, tag, or branch) in a local git repository.

## usage example:
```python
from kit import Repository

repo = Repository("/path/to/repo")
file_tree = repo.get_file_tree()
symbols = repo.extract_symbols("src/main.py")
results = repo.search("function_name")
```

# module summaries
## function:
使用LLM对代码文件、函数、类进行智能摘要生成，支持OpenAI、Anthropic、Google、Ollama等多种模型。

**主要类：**
- `LLMClientProtocol`: Protocol defining the interface for LLM clients.
- `LLMError`: Custom exception for LLM related errors.
- `SymbolNotFoundError`: Custom exception for when a symbol (function, class) is not found.

**主要函数：**
- `_strip_thinking_tokens(response)`: Strip thinking tokens from LLM responses.

## usage example:
```python
from kit import Repository
from kit.summaries import Summarizer, OpenAIConfig

repo = Repository("/path/to/repo")
summarizer = Summarizer(repo, config=OpenAIConfig(api_key="..."))
summary = summarizer.summarize_file("src/main.py")
```

# module code_searcher
## function:
基于ripgrep的代码搜索功能，支持正则表达式、语义搜索和AST搜索。

**主要类：**
- `SearchOptions`: Configuration options for text search.
- `CodeSearcher`: Provides text and regex search across the repository.
  - `__init__(repo_path)`: Initializes the CodeSearcher with the repository path.
  - `_load_gitignore()`: Loads .gitignore rules from the repository root.

## usage example:
```python
from kit import Repository

repo = Repository("/path/to/repo")
results = repo.search("search_term", search_type="regex")
```

# module repo_mapper
## function:
生成代码仓库的结构映射，包括文件树和符号索引。

**主要类：**
- `RepoMapper`: Maps the structure and symbols of a code repository.
  - `__init__(repo_path)`: 暂无说明
  - `_load_gitignore()`: 暂无说明

## usage example:
```python
from kit.repo_mapper import *
# 使用该模块的功能
```

# module tree_sitter_symbol_extractor
## function:
使用tree-sitter进行多语言代码符号提取，支持Python、JavaScript、TypeScript等15+语言。

**主要类：**
- `LanguagePlugin`: Represents a language plugin with query files and configuration.
  - `__init__(name, extensions, query_files, query_dirs)`: 暂无说明
- `TreeSitterSymbolExtractor`: Multi-language symbol extractor using tree-sitter queries with plugin support.
  - `register_language(cls, name, extensions, query_files, query_dirs)`: Register a completely new language.
  - `extend_language(cls, language, query_file)`: Extend an existing language with additional query patterns.

## usage example:
```python
from kit.tree_sitter_symbol_extractor import TreeSitterSymbolExtractor

extractor = TreeSitterSymbolExtractor()
symbols = extractor.extract_symbols("file.py", content)
```

# module __init__
## function:
kit包的入口模块，导出Repository等核心类。

## usage example:
```python
from kit.__init__ import *
# 使用该模块的功能
```

# module cli
## function:
命令行接口，提供kit工具的CLI操作。

**主要函数：**
- `_get_version()`: Get kit version without importing the entire package.
- `version_callback(value)`: 暂无说明
- `main(version)`: [bold blue]Kit[/] - A modular toolkit for LLM-powered codebase understanding.
- `cache_command(action, repo_path)`: 🗄️ Manage incremental analysis cache.
- `chunk_by_lines(path, file_path, max_lines, output)`: Chunk a file's content by line count.

## usage example:
```python
# 命令行使用
kit search "function_name" /path/to/repo
kit summarize /path/to/repo
```

# module context_extractor
## function:
提取代码上下文信息，用于LLM理解和分析。

**主要类：**
- `ContextExtractor`: Extracts context from source code files for chunking, search, and LLM workflows.
  - `__init__(repo_path)`: 暂无说明
  - `_read_file_cached(abs_path)`: Read file content with mtime-based caching.

## usage example:
```python
from kit.context_extractor import *
# 使用该模块的功能
```

# module vector_searcher
## function:
基于向量的语义搜索功能。

**主要类：**
- `VectorDBBackend`: Abstract vector DB interface for pluggable backends.
  - `add(embeddings, metadatas, ids)`: 暂无说明
  - `query(embedding, top_k)`: 暂无说明
- `ChromaDBBackend`: 暂无说明
  - `__init__(persist_dir, collection_name)`: 暂无说明
  - `add(embeddings, metadatas, ids)`: 暂无说明
- `ChromaCloudBackend`: ChromaDB Cloud backend for vector search using Chroma's managed cloud service.
  - `__init__(collection_name, api_key, tenant, database)`: 暂无说明
  - `add(embeddings, metadatas, ids)`: 暂无说明

**主要函数：**
- `_resolve_batch_size(collection, default)`: Derive a safe batch size for collection.add calls.
- `get_default_backend(persist_dir, collection_name)`: Factory function to create the appropriate backend based on environment configuration.

## usage example:
```python
from kit.vector_searcher import *
# 使用该模块的功能
```

# module utils
## function:
通用工具函数集合。

**主要函数：**
- `format_duration(seconds)`: Format duration in human-readable format.
- `format_size(bytes_size)`: Format size in human-readable format.
- `validate_relative_path(base_path, relative_path)`: Validate that relative_path stays within base_path bounds.
- `parse_git_url(url)`: Parse a git URL to extract owner and repo name.
- `truncate_text(text, max_length)`: Truncate text to max_length, adding ellipsis if needed.

## usage example:
```python
from kit.utils import *
# 使用该模块的功能
```

# module llm_context
## function:
组装LLM所需的上下文信息。

**主要类：**
- `ContextAssembler`: Collects pieces of context and spits out a prompt blob.
  - `__init__(repo)`: 暂无说明
  - `add_diff(diff)`: Add a raw git diff section.

## usage example:
```python
from kit.llm_context import *
# 使用该模块的功能
```

# module llm_client_factory
## function:
LLM客户端工厂，创建和管理不同模型的客户端。

**主要类：**
- `LLMClientError`: Error raised when LLM client creation fails.

**主要函数：**
- `create_openai_client(api_key, base_url)`: Create an OpenAI client.
- `create_anthropic_client(api_key)`: Create an Anthropic client.
- `create_google_client(api_key)`: Create a Google Generative AI client.
- `create_ollama_client(base_url, model, session)`: Create an Ollama client.
- `create_client_from_config(config)`: Create an LLM client from a summaries config object.

## usage example:
```python
from kit.llm_client_factory import *
# 使用该模块的功能
```


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
results = repo.search("def\s+\w+", search_type="regex")

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


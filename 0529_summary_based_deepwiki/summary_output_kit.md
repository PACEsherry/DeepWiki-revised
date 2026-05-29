# Summary Output - Kit Repository

> 由大模型 mimo-v2.5-pro 自动生成。
> 生成时间: 2026-05-29 13:26:57

---

# module `api/app.py`

## function:

该模块提供 2 个类和 16 个函数，用于 api.app 相关功能。

## usage example:

```python
from src.kit.api.app import RepoIn
```


# class `RepoIn`

## function:

RepoIn 类封装相关功能，提供 无 等方法。

## extends:

BaseModel

## usage example:

```python
obj = RepoIn()
```


# class `FilePathsIn`

## function:

FilePathsIn 类封装相关功能，提供 无 等方法。

## extends:

BaseModel

## usage example:

```python
class FilePathsIn(BaseModel):
    input_path: str
    output_path: str

# 创建实例
file_paths = FilePaths
```


# func `sanitize_url(url: str)`

## function:

sanitize_url 函数处理 (url: str) 参数，Remove credentials from URL for safe dis。

## usage example:

```python
result = sanitize_url()
print(result)
```


# func `matches_pattern(url: str, pattern: str)`

## function:

matches_pattern 函数处理 (url: str, pattern: str) 参数，Check if a URL matches a given pattern.
。

## usage example:

```python
result = matches_pattern()
print(result)
```


# func `validate_repo_url(url: str)`

## function:

validate_repo_url 函数处理 (url: str) 参数，Validate repository URL against allowlis。

## usage example:

```python
result = validate_repo_url()
print(result)
```


# func `open_repo(body: RepoIn)`

## function:

open_repo 函数处理 (body: RepoIn) 参数，Register a repository path/URL and retur。

## usage example:

```python
result = open_repo()
print(result)
```


# func `get_file_tree(repo_id: str)`

## function:

get_file_tree 函数处理 (repo_id: str) 参数，Get the file tree of the repository.。

## usage example:

```python
result = get_file_tree()
print(result)
```


# func `get_file_content(repo_id: str, file_path: str)`

## function:

get_file_content 函数处理 (repo_id: str, file_path: str) 参数，Get the content of a specific file in th。

## usage example:

```python
result = get_file_content()
print(result)
```


# func `search_text(repo_id: str, q: str, pattern: str = "*.py")`

## function:

search_text 函数处理 (repo_id: str, q: str, pattern: str = "*.py") 参数。

## usage example:

```python
result = search_text()
print(result)
```


# func `grep_text(
    repo_id: str,
    pattern: str,
    case_sensitive: bool = True,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    max_results: int = 1000,
    directory: str | None = None,
    include_hidden: bool = False,
)`

## function:

grep_text 函数处理 (
    repo_id: str,
    pattern: str,
    case_sensitive: bool = True,
    include_pattern: str | None = None,
    exclude_pattern: str | None = None,
    max_results: int = 1000,
    directory: str | None = None,
    include_hidden: bool = False,
) 参数，Perform literal grep search on repositor。

## usage example:

```python
result = grep_text()
print(result)
```


# func `delete_repo(repo_id: str)`

## function:

delete_repo 函数处理 (repo_id: str) 参数，Remove a repository from the registry an。

## usage example:

```python
result = delete_repo()
print(result)
```


# func `extract_symbols(repo_id: str, file_path: str | None = None, symbol_type: str | None = None)`

## function:

extract_symbols 函数处理 (repo_id: str, file_path: str | None = None, symbol_type: str | None = None) 参数，Extract symbols from a specific file or 。

## usage example:

```python
# 示例1：仅提供仓库ID，提取所有符号
symbols = extract_symbols("pytorch/pytorch")

# 示例2：指定文件路径和符号类型
func_symbols = extract_symbols("numpy/numpy", file_path="numpy/core
```


# func `find_symbol_usages(
    repo_id: str,
    symbol_name: str,
    file_path: str | None = None,
    symbol_type: str | None = None,
)`

## function:

find_symbol_usages 函数处理 (
    repo_id: str,
    symbol_name: str,
    file_path: str | None = None,
    symbol_type: str | None = None,
) 参数，Find all usages of a symbol across the r。

## usage example:

```python
result = find_symbol_usages()
print(result)
```


# func `get_full_index(repo_id: str)`

## function:

get_full_index 函数处理 (repo_id: str) 参数，Return combined file tree + symbols inde。

## usage example:

```python
result = get_full_index()
print(result)
```


# func `get_summary(repo_id: str, file_path: str, symbol_name: str | None = None)`

## function:

get_summary 函数处理 (repo_id: str, file_path: str, symbol_name: str | None = None) 参数，LLM-powered code summary.。

## usage example:

```python
result = get_summary()
print(result)
```


# func `analyze_dependencies(repo_id: str, file_path: str | None = None, depth: int = 1, language: str = "python")`

## function:

analyze_dependencies 函数处理 (repo_id: str, file_path: str | None = None, depth: int = 1, language: str = "python") 参数，Dependency analysis for Python or Terraf。

## usage example:

```python
result = analyze_dependencies()
print(result)
```


# func `get_git_info(repo_id: str)`

## function:

get_git_info 函数处理 (repo_id: str) 参数，Get git metadata for the repository (SHA。

## usage example:

```python
info = get_git_info("username/repo_name")
print(info)
```


# func `get_multiple_file_contents(repo_id: str, body: FilePathsIn)`

## function:

通过一个请求获取多个文件的内容。

## usage example:

```python
result = get_multiple_file_contents()
print(result)
```


# module `api/registry.py`

## function:

该模块提供 1 个类和 2 个函数，用于 api.registry 相关功能。

## usage example:

```python
from api.registry import PersistentRepoRegistry, _canonical, path_to_id

registry = PersistentRepoRegistry()
canonical_path = _canonical("some/repo/path")
repo_id = path_to_id(canonical_path)
registry.register(repo_id, canonical_path)
```


# class `PersistentRepoRegistry`

## function:

PersistentRepoRegistry 类封装相关功能，提供 __init__, _load, _save, add 等方法。

## extends:

none

## usage example:

```python
obj = PersistentRepoRegistry()
result = obj.__init__()
```


# method `PersistentRepoRegistry.__init__(self, max_cache_entries: int = 32)`

## function:

PersistentRepoRegistry.__init__ 方法处理 (self, max_cache_entries: int = 32) 参数。

## usage example:

```python
obj.__init__()
```


# method `PersistentRepoRegistry._load(self)`

## function:

PersistentRepoRegistry._load 方法处理 (self) 参数。

## usage example:

```python
obj._load()
```


# method `PersistentRepoRegistry._save(self)`

## function:

PersistentRepoRegistry._save 方法处理 (self) 参数。

## usage example:

```python
obj._save()
```


# method `PersistentRepoRegistry.add(self, path_or_url: str, ref: str | None = None)`

## function:

PersistentRepoRegistry.add 方法处理 (self, path_or_url: str, ref: str | None = None) 参数。

## usage example:

```python
obj.add()
```


# method `PersistentRepoRegistry.get_repo(self, repo_id: str)`

## function:

PersistentRepoRegistry.get_repo 方法处理 (self, repo_id: str) 参数。

## usage example:

```python
obj.get_repo()
```


# method `PersistentRepoRegistry.delete(self, repo_id: str)`

## function:

PersistentRepoRegistry.delete 方法处理 (self, repo_id: str) 参数。

## usage example:

```python
obj.delete()
```


# func `_canonical(value: str, ref: str | None = None)`

## function:

_canonical 函数处理 (value: str, ref: str | None = None) 参数，Return a stable representation including。

## usage example:

```python
result = _canonical()
print(result)
```


# func `path_to_id(canonical_path: str)`

## function:

path_to_id 函数处理 (canonical_path: str) 参数，Deterministically hash *canonical_path* 。

## usage example:

```python
result = path_to_id()
print(result)
```


# module `ast_search.py`

## function:

该模块提供 2 个类和 1 个函数，用于 ast_search 相关功能。

## usage example:

```python
from ast_search import ASTPattern, ASTSearcher, find_common_patterns

pattern = ASTPattern.from_string("def $name(): ...")
searcher = ASTSearcher(pattern)
common = find_common_patterns(searcher.find_nodes("example.py"))
```


# class `ASTPattern`

## function:

ASTPattern类负责构建和匹配抽象语法树中的特定模式，可用于搜索代码结构中的特定语法元素。

## extends:

none

## usage example:

```python
obj = ASTPattern()
result = obj.__init__()
```


# class `ASTSearcher`

## function:

ASTSearcher 类封装相关功能，提供 __init__, search_pattern, _get_matching_files, _search_file 等方法。

## extends:

none

## usage example:

```python
obj = ASTSearcher()
result = obj.__init__()
```


# method `ASTPattern.__init__(self, pattern: str, mode: str = "simple")`

## function:

ASTPattern.__init__ 方法处理 (self, pattern: str, mode: str = "simple") 参数。

## usage example:

```python
obj.__init__()
```


# method `ASTPattern._compile(self)`

## function:

ASTPattern._compile 方法处理 (self) 参数，Compile the pattern based on mode.。

## usage example:

```python
obj._compile()
```


# method `ASTPattern.matches(self, node: Node, source: bytes)`

## function:

ASTPattern.matches 方法处理 (self, node: Node, source: bytes) 参数，Check if a node matches this pattern.。

## usage example:

```python
obj.matches()
```


# method `ASTPattern._matches_simple(self, node: Node, source: bytes)`

## function:

ASTPattern._matches_simple 方法处理 (self, node: Node, source: bytes) 参数，Match using simple pattern syntax.。

## usage example:

```python
obj._matches_simple()
```


# method `ASTPattern._matches_pattern(self, node: Node, source: bytes)`

## function:

ASTPattern._matches_pattern 方法处理 (self, node: Node, source: bytes) 参数，Match using pattern criteria.。

## usage example:

```python
obj._matches_pattern()
```


# method `ASTSearcher.__init__(self, repo_path: str)`

## function:

初始化AST搜索器，设定要分析的代码仓库路径。

## usage example:

```python
obj.__init__()
```


# method `ASTSearcher.search_pattern(
        self, pattern: str, file_pattern: str = "*.py", mode: str = "simple", max_results: int = 100
    )`

## function:

ASTSearcher.search_pattern 方法处理 (
        self, pattern: str, file_pattern: str = "*.py", mode: str = "simple", max_results: int = 100
    ) 参数，Search for AST patterns in code.

      。

## usage example:

```python
obj.search_pattern()
```


# method `ASTSearcher._get_matching_files(self, pattern: str)`

## function:

ASTSearcher._get_matching_files 方法处理 (self, pattern: str) 参数，Get all files matching the given pattern。

## usage example:

```python
obj._get_matching_files()
```


# method `ASTSearcher._search_file(self, file_path: Path, pattern: ASTPattern)`

## function:

ASTSearcher._search_file 方法处理 (self, file_path: Path, pattern: ASTPattern) 参数，Search a single file for pattern matches。

## usage example:

```python
obj._search_file()
```


# method `ASTSearcher._search_node(
        self, node: Node, source: bytes, pattern: ASTPattern, file_path: Path, matches: List[Dict[str, Any]]
    )`

## function:

ASTSearcher._search_node 方法处理 (
        self, node: Node, source: bytes, pattern: ASTPattern, file_path: Path, matches: List[Dict[str, Any]]
    ) 参数，Recursively search a node and its childr。

## usage example:

```python
obj._search_node()
```


# method `ASTSearcher._get_context(self, node: Node, source: bytes)`

## function:

ASTSearcher._get_context 方法处理 (self, node: Node, source: bytes) 参数，Get context information for a match.。

## usage example:

```python
obj._get_context()
```


# func `find_common_patterns(repo_path: str)`

## function:

find_common_patterns 函数处理 (repo_path: str) 参数，Find common code patterns that might nee。

## usage example:

```python
result = find_common_patterns()
print(result)
```


# module `code_searcher.py`

## function:

该模块提供 2 个类和 0 个函数，用于 code_searcher 相关功能。

## usage example:

```python
from src.kit.code_searcher import SearchOptions
```


# class `SearchOptions`

## function:

SearchOptions 类封装相关功能，提供 无 等方法。

## extends:

none

## usage example:

```python
obj = SearchOptions()
```


# class `CodeSearcher`

## function:

CodeSearcher 类封装相关功能，提供 __init__, _load_gitignore, _should_ignore, _has_ripgrep 等方法。

## extends:

none

## usage example:

```python
obj = CodeSearcher()
result = obj.__init__()
```


# method `CodeSearcher.__init__(self, repo_path: str)`

## function:

CodeSearcher.__init__ 方法处理 (self, repo_path: str) 参数，
        Initializes the CodeSearcher wi。

## usage example:

```python
obj.__init__()
```


# method `CodeSearcher._load_gitignore(self)`

## function:

CodeSearcher._load_gitignore 方法处理 (self) 参数，Loads .gitignore rules from the reposito。

## usage example:

```python
obj._load_gitignore()
```


# method `CodeSearcher._should_ignore(self, file: Path)`

## function:

CodeSearcher._should_ignore 方法处理 (self, file: Path) 参数，Checks if a file should be ignored based。

## usage example:

```python
obj._should_ignore()
```


# method `CodeSearcher._has_ripgrep(self)`

## function:

CodeSearcher._has_ripgrep 方法处理 (self) 参数，Check if ripgrep (rg) is available on th。

## usage example:

```python
obj._has_ripgrep()
```


# method `CodeSearcher._is_git_repository(self)`

## function:

CodeSearcher._is_git_repository 方法处理 (self) 参数，Check if the repo_path is a git reposito。

## usage example:

```python
obj._is_git_repository()
```


# method `CodeSearcher._parse_ripgrep_json_messages(self, stdout: str)`

## function:

CodeSearcher._parse_ripgrep_json_messages 方法处理 (self, stdout: str) 参数，Parse ripgrep JSON output into message l。

## usage example:

```python
obj._parse_ripgrep_json_messages()
```


# method `CodeSearcher._extract_context_for_match(
        self,
        messages: List[Dict[str, Any]],
        match_index: int,
        file_path: str,
        match_line_number: int,
        options: SearchOptions,
    )`

## function:

CodeSearcher._extract_context_for_match 方法处理 (
        self,
        messages: List[Dict[str, Any]],
        match_index: int,
        file_path: str,
        match_line_number: int,
        options: SearchOptions,
    ) 参数，Extract context lines before and after a。

## usage example:

```python
obj._extract_context_for_match()
```


# method `CodeSearcher._search_with_ripgrep(
        self, query: str, file_pattern: str, options: SearchOptions
    )`

## function:

CodeSearcher._search_with_ripgrep 方法处理 (
        self, query: str, file_pattern: str, options: SearchOptions
    ) 参数，Search using ripgrep for better performa。

## usage example:

```python
obj._search_with_ripgrep()
```


# method `CodeSearcher.search_text(
        self, query: str, file_pattern: str = "*.py", options: Optional[SearchOptions] = None
    )`

## function:

CodeSearcher.search_text 方法处理 (
        self, query: str, file_pattern: str = "*.py", options: Optional[SearchOptions] = None
    ) 参数，
        Search for a text pattern (rege。

## usage example:

```python
obj.search_text()
```


# module `context_extractor.py`

## function:

该模块提供 1 个类和 0 个函数，用于 context_extractor 相关功能。

## usage example:

```python
from src.kit.context_extractor import ContextExtractor
```


# class `ContextExtractor`

## function:

ContextExtractor 类封装相关功能，提供 __init__, _read_file_cached, invalidate_cache, chunk_file_by_lines 等方法。

## extends:

none

## usage example:

```python
obj = ContextExtractor()
result = obj.__init__()
```


# method `ContextExtractor.__init__(self, repo_path: str)`

## function:

初始化上下文提取器，设置仓库路径。

## usage example:

```python
obj.__init__()
```


# method `ContextExtractor._read_file_cached(self, abs_path: Path)`

## function:

ContextExtractor._read_file_cached 方法处理 (self, abs_path: Path) 参数，Read file content with mtime-based cachi。

## usage example:

```python
obj._read_file_cached()
```


# method `ContextExtractor.invalidate_cache(self, file_path: Optional[str] = None)`

## function:

ContextExtractor.invalidate_cache 方法处理 (self, file_path: Optional[str] = None) 参数，Invalidate file cache.

        Args:
  。

## usage example:

```python
obj.invalidate_cache()
```


# method `ContextExtractor.chunk_file_by_lines(self, file_path: str, max_lines: int = 50)`

## function:

ContextExtractor.chunk_file_by_lines 方法处理 (self, file_path: str, max_lines: int = 50) 参数，
        Chunk file into blocks of at mo。

## usage example:

```python
obj.chunk_file_by_lines()
```


# method `ContextExtractor.chunk_file_by_symbols(self, file_path: str)`

## function:

ContextExtractor.chunk_file_by_symbols 方法处理 (self, file_path: str) 参数。

## usage example:

```python
obj.chunk_file_by_symbols()
```


# method `ContextExtractor.extract_context_around_line(self, file_path: str, line: int)`

## function:

ContextExtractor.extract_context_around_line 方法处理 (self, file_path: str, line: int) 参数，
        Extracts the function/class (or。

## usage example:

```python
obj.extract_context_around_line()
```


# module `deep_research.py`

## function:

该模块提供 2 个类和 0 个函数，用于 deep_research 相关功能。

## usage example:

```python
from src.kit.deep_research import ResearchResult
```


# class `ResearchResult`

## function:

该类作为数据容器，用于存储深度研究过程产生的结果数据。

## extends:

none

## usage example:

```python
obj = ResearchResult()
```


# class `DeepResearch`

## function:

DeepResearch 类封装相关功能，提供 __init__, _init_llm_client, research 等方法。

## extends:

none

## usage example:

```python
obj = DeepResearch()
result = obj.__init__()
```


# method `DeepResearch.__init__(self, config: Optional[Union[OpenAIConfig, AnthropicConfig, GoogleConfig, OllamaConfig]] = None)`

## function:

DeepResearch.__init__ 方法处理 (self, config: Optional[Union[OpenAIConfig, AnthropicConfig, GoogleConfig, OllamaConfig]] = None) 参数，Initialize with LLM config.。

## usage example:

```python
obj.__init__()
```


# method `DeepResearch._init_llm_client(self)`

## function:

根据配置初始化大语言模型客户端。

## usage example:

```python
obj._init_llm_client()
```


# method `DeepResearch.research(self, query: str)`

## function:

DeepResearch.research 方法处理 (self, query: str) 参数，
        Perform research by prompting a。

## usage example:

```python
obj.research()
```


# module `dependency_analyzer/dependency_analyzer.py`

## function:

定义依赖分析器的通用接口，提供

## usage example:

```python
from src.kit.dependency_analyzer.dependency_analyzer import DependencyAnalyzer
```


# interface `DependencyAnalyzer`

## function:

DependencyAnalyzer 是抽象接口，定义了 __init__, _build_reverse_deps, generate_llm_context, analyze 等方法的契约。

## extends:

ABC

## implemented by:

unknown

## usage example:

```python
class MyImpl(DependencyAnalyzer):
    def __init__(self, *args): ...
    def _build_reverse_deps(self, *args): ...
    def generate_llm_context(self, *args): ...
```


# method `DependencyAnalyzer.__init__(self, repository: "Repository")`

## function:

DependencyAnalyzer.__init__ 方法处理 (self, repository: "Repository") 参数，
        Initialize the analyzer with a 。

## usage example:

```python
obj.__init__()
```


# method `DependencyAnalyzer._build_reverse_deps(self)`

## function:

DependencyAnalyzer._build_reverse_deps 方法处理 (self) 参数，Build reverse dependency map for O(1) in。

## usage example:

```python
obj._build_reverse_deps()
```


# method `DependencyAnalyzer.generate_llm_context(
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    )`

## function:

DependencyAnalyzer.generate_llm_context 方法处理 (
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    ) 参数，
        Generate a concise, natural lan。

## usage example:

```python
obj.generate_llm_context()
```


# method `DependencyAnalyzer.analyze(self, file_path: Optional[str] = None, depth: int = 1)`

## function:

DependencyAnalyzer.analyze 方法处理 (self, file_path: Optional[str] = None, depth: int = 1) 参数，Return the dependency graph, optionally 。

## usage example:

```python
obj.analyze()
```


# module `dependency_analyzer/go_dependency_analyzer.py`

## function:

该模块提供 1 个类和 0 个函数，用于 dependency_analyzer.go_dependency_analyzer 相关功能。

## usage example:

```python
from src.kit.dependency_analyzer.go_dependency_analyzer import GoDependencyAnalyzer
```


# class `GoDependencyAnalyzer`

## function:

这是一个Go语言依赖分析器，用于解析Go项目中的模块依赖和

## extends:

DependencyAnalyzer

## usage example:

```python
obj = GoDependencyAnalyzer()
result = obj.__init__()
```


# method `GoDependencyAnalyzer.__init__(self, repository: "Repository")`

## function:

GoDependencyAnalyzer.__init__ 方法处理 (self, repository: "Repository") 参数，
        Initialize the analyzer with a 。

## usage example:

```python
obj.__init__()
```


# method `GoDependencyAnalyzer._parse_go_mod(self)`

## function:

GoDependencyAnalyzer._parse_go_mod 方法处理 (self) 参数，Parse go.mod to find the module path.。

## usage example:

```python
obj._parse_go_mod()
```


# method `GoDependencyAnalyzer._extract_imports_from_file(self, file_path: str)`

## function:

GoDependencyAnalyzer._extract_imports_from_file 方法处理 (self, file_path: str) 参数，
        Extract import statements from 。

## usage example:

```python
obj._extract_imports_from_file()
```


# method `GoDependencyAnalyzer._parse_import_spec(self, node, content: str)`

## function:

GoDependencyAnalyzer._parse_import_spec 方法处理 (self, node, content: str) 参数，Parse a single import_spec node.。

## usage example:

```python
obj._parse_import_spec()
```


# method `GoDependencyAnalyzer._extract_imports_regex(self, file_path: str)`

## function:

GoDependencyAnalyzer._extract_imports_regex 方法处理 (self, file_path: str) 参数，Fallback regex-based import extraction.。

## usage example:

```python
obj._extract_imports_regex()
```


# method `GoDependencyAnalyzer._get_package_name(self, file_path: str)`

## function:

GoDependencyAnalyzer._get_package_name 方法处理 (self, file_path: str) 参数，Extract the package name from a Go file.。

## usage example:

```python
obj._get_package_name()
```


# method `GoDependencyAnalyzer._classify_import(self, import_path: str)`

## function:

GoDependencyAnalyzer._classify_import 方法处理 (self, import_path: str) 参数，
        Classify an import as 'internal。

## usage example:

```python
obj._classify_import()
```


# method `GoDependencyAnalyzer._build_package_map(self)`

## function:

GoDependencyAnalyzer._build_package_map 方法处理 (self) 参数，Build a map of internal package paths to。

## usage example:

```python
obj._build_package_map()
```


# method `GoDependencyAnalyzer.build_dependency_graph(self)`

## function:

GoDependencyAnalyzer.build_dependency_graph 方法处理 (self) 参数，
        Analyzes the entire repository 。

## usage example:

```python
obj.build_dependency_graph()
```


# method `GoDependencyAnalyzer.export_dependency_graph(
        self, output_format: str = "json", output_path: Optional[str] = None
    )`

## function:

GoDependencyAnalyzer.export_dependency_graph 方法处理 (
        self, output_format: str = "json", output_path: Optional[str] = None
    ) 参数，
        Export the dependency graph in 。

## usage example:

```python
obj.export_dependency_graph()
```


# method `GoDependencyAnalyzer._generate_dot_file(self, graph: Dict[str, Dict[str, Any]])`

## function:

GoDependencyAnalyzer._generate_dot_file 方法处理 (self, graph: Dict[str, Dict[str, Any]]) 参数，Generate a DOT file for visualization wi。

## usage example:

```python
obj._generate_dot_file()
```


# method `GoDependencyAnalyzer._generate_graphml_file(self, graph: Dict[str, Dict[str, Any]])`

## function:

GoDependencyAnalyzer._generate_graphml_file 方法处理 (self, graph: Dict[str, Dict[str, Any]]) 参数，Generate a GraphML file for visualizatio。

## usage example:

```python
obj._generate_graphml_file()
```


# method `GoDependencyAnalyzer.find_cycles(self)`

## function:

GoDependencyAnalyzer.find_cycles 方法处理 (self) 参数，
        Find cycles in the dependency g。

## usage example:

```python
obj.find_cycles()
```


# method `GoDependencyAnalyzer.get_dependencies(self, item: str, include_indirect: bool = False)`

## function:

GoDependencyAnalyzer.get_dependencies 方法处理 (self, item: str, include_indirect: bool = False) 参数，
        Get dependencies for a specific。

## usage example:

```python
obj.get_dependencies()
```


# method `GoDependencyAnalyzer.get_package_dependencies(self, package_path: str, include_indirect: bool = False)`

## function:

GoDependencyAnalyzer.get_package_dependencies 方法处理 (self, package_path: str, include_indirect: bool = False) 参数，
        Get dependencies for a specific。

## usage example:

```python
obj.get_package_dependencies()
```


# method `GoDependencyAnalyzer.get_dependents(self, package_path: str, include_indirect: bool = False)`

## function:

GoDependencyAnalyzer.get_dependents 方法处理 (self, package_path: str, include_indirect: bool = False) 参数，
        Get packages that depend on the。

## usage example:

```python
obj.get_dependents()
```


# method `GoDependencyAnalyzer.visualize_dependencies(self, output_path: str, format: str = "png")`

## function:

GoDependencyAnalyzer.visualize_dependencies 方法处理 (self, output_path: str, format: str = "png") 参数，
        Generate a visualization of the。

## usage example:

```python
obj.visualize_dependencies()
```


# method `GoDependencyAnalyzer.generate_llm_context(
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    )`

## function:

GoDependencyAnalyzer.generate_llm_context 方法处理 (
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    ) 参数，
        Generate a Go-specific natural 。

## usage example:

```python
obj.generate_llm_context()
```


# module `dependency_analyzer/javascript_dependency_analyzer.py`

## function:

该模块提供 1 个类和 0 个函数，用于 dependency_analyzer.javascript_dependency_analyzer 相关功能。

## usage example:

```python
from src.kit.dependency_analyzer.javascript_dependency_analyzer import JavaScriptDependencyAnalyzer
```


# class `JavaScriptDependencyAnalyzer`

## function:

JavaScriptDependencyAnalyzer 类封装相关功能，提供 __init__, _parse_package_json, _extract_imports_from_file, _extract_imports_from_tree 等方法。

## extends:

DependencyAnalyzer

## usage example:

```python
obj = JavaScriptDependencyAnalyzer()
result = obj.__init__()
```


# method `JavaScriptDependencyAnalyzer.__init__(self, repository: "Repository")`

## function:

JavaScriptDependencyAnalyzer.__init__ 方法处理 (self, repository: "Repository") 参数，
        Initialize the analyzer with a 。

## usage example:

```python
obj.__init__()
```


# method `JavaScriptDependencyAnalyzer._parse_package_json(self)`

## function:

JavaScriptDependencyAnalyzer._parse_package_json 方法处理 (self) 参数，Parse package.json to get package info a。

## usage example:

```python
obj._parse_package_json()
```


# method `JavaScriptDependencyAnalyzer._extract_imports_from_file(self, file_path: str)`

## function:

JavaScriptDependencyAnalyzer._extract_imports_from_file 方法处理 (self, file_path: str) 参数，
        Extract import statements from 。

## usage example:

```python
obj._extract_imports_from_file()
```


# method `JavaScriptDependencyAnalyzer._extract_imports_from_tree(self, node, content: str)`

## function:

JavaScriptDependencyAnalyzer._extract_imports_from_tree 方法处理 (self, node, content: str) 参数，Extract imports by walking the tree-sitt。

## usage example:

```python
obj._extract_imports_from_tree()
```


# method `JavaScriptDependencyAnalyzer._extract_imports_regex(self, file_path: str)`

## function:

JavaScriptDependencyAnalyzer._extract_imports_regex 方法处理 (self, file_path: str) 参数，Fallback regex-based import extraction.。

## usage example:

```python
obj._extract_imports_regex()
```


# method `JavaScriptDependencyAnalyzer._resolve_import(self, import_source: str, from_file: str)`

## function:

JavaScriptDependencyAnalyzer._resolve_import 方法处理 (self, import_source: str, from_file: str) 参数，
        Resolve an import source to a m。

## usage example:

```python
obj._resolve_import()
```


# method `JavaScriptDependencyAnalyzer._build_file_map(self, js_ts_files: List[Dict[str, Any]])`

## function:

JavaScriptDependencyAnalyzer._build_file_map 方法处理 (self, js_ts_files: List[Dict[str, Any]]) 参数，Build a map of file paths for resolving 。

## usage example:

```python
obj._build_file_map()
```


# method `JavaScriptDependencyAnalyzer.build_dependency_graph(self)`

## function:

JavaScriptDependencyAnalyzer.build_dependency_graph 方法处理 (self) 参数，
        Analyzes the entire repository 。

## usage example:

```python
obj.build_dependency_graph()
```


# method `JavaScriptDependencyAnalyzer.export_dependency_graph(
        self, output_format: str = "json", output_path: Optional[str] = None
    )`

## function:

JavaScriptDependencyAnalyzer.export_dependency_graph 方法处理 (
        self, output_format: str = "json", output_path: Optional[str] = None
    ) 参数，
        Export the dependency graph in 。

## usage example:

```python
obj.export_dependency_graph()
```


# method `JavaScriptDependencyAnalyzer._generate_dot_file(self, graph: Dict[str, Dict[str, Any]])`

## function:

JavaScriptDependencyAnalyzer._generate_dot_file 方法处理 (self, graph: Dict[str, Dict[str, Any]]) 参数，Generate a DOT file for visualization wi。

## usage example:

```python
obj._generate_dot_file()
```


# method `JavaScriptDependencyAnalyzer._generate_graphml_file(self, graph: Dict[str, Dict[str, Any]])`

## function:

JavaScriptDependencyAnalyzer._generate_graphml_file 方法处理 (self, graph: Dict[str, Dict[str, Any]]) 参数，Generate a GraphML file for visualizatio。

## usage example:

```python
obj._generate_graphml_file()
```


# method `JavaScriptDependencyAnalyzer.find_cycles(self)`

## function:

JavaScriptDependencyAnalyzer.find_cycles 方法处理 (self) 参数，
        Find cycles in the dependency g。

## usage example:

```python
obj.find_cycles()
```


# method `JavaScriptDependencyAnalyzer.get_dependencies(self, item: str, include_indirect: bool = False)`

## function:

JavaScriptDependencyAnalyzer.get_dependencies 方法处理 (self, item: str, include_indirect: bool = False) 参数，
        Get dependencies for a specific。

## usage example:

```python
obj.get_dependencies()
```


# method `JavaScriptDependencyAnalyzer.get_module_dependencies(self, module_path: str, include_indirect: bool = False)`

## function:

JavaScriptDependencyAnalyzer.get_module_dependencies 方法处理 (self, module_path: str, include_indirect: bool = False) 参数，
        Get dependencies for a specific。

## usage example:

```python
obj.get_module_dependencies()
```


# method `JavaScriptDependencyAnalyzer.get_dependents(self, module_path: str, include_indirect: bool = False)`

## function:

JavaScriptDependencyAnalyzer.get_dependents 方法处理 (self, module_path: str, include_indirect: bool = False) 参数，
        Get modules that depend on the 。

## usage example:

```python
obj.get_dependents()
```


# method `JavaScriptDependencyAnalyzer.visualize_dependencies(self, output_path: str, format: str = "png")`

## function:

JavaScriptDependencyAnalyzer.visualize_dependencies 方法处理 (self, output_path: str, format: str = "png") 参数，
        Generate a visualization of the。

## usage example:

```python
obj.visualize_dependencies()
```


# method `JavaScriptDependencyAnalyzer.generate_llm_context(
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    )`

## function:

JavaScriptDependencyAnalyzer.generate_llm_context 方法处理 (
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    ) 参数，
        Generate a JavaScript/TypeScrip。

## usage example:

```python
obj.generate_llm_context()
```


# method `JavaScriptDependencyAnalyzer.generate_dependency_report(self, output_path: Optional[str] = None)`

## function:

JavaScriptDependencyAnalyzer.generate_dependency_report 方法处理 (self, output_path: Optional[str] = None) 参数，
        Generate a comprehensive depend。

## usage example:

```python
obj.generate_dependency_report()
```


# module `dependency_analyzer/python_dependency_analyzer.py`

## function:

该模块提供 1 个类和 0 个函数，用于 dependency_analyzerthon_dependency_analyzer 相关功能。

## usage example:

```python
from src.kit.dependency_analyzerthon_dependency_analyzer import PythonDependencyAnalyzer
```


# class `PythonDependencyAnalyzer`

## function:

PythonDependencyAnalyzer 类封装相关功能，提供 __init__, build_dependency_graph, _build_module_map, _process_file 等方法。

## extends:

DependencyAnalyzer

## usage example:

```python
obj = PythonDependencyAnalyzer()
result = obj.__init__()
```


# method `PythonDependencyAnalyzer.__init__(self, repository: "Repository")`

## function:

PythonDependencyAnalyzer.__init__ 方法处理 (self, repository: "Repository") 参数，
        Initialize the analyzer with a 。

## usage example:

```python
obj.__init__()
```


# method `PythonDependencyAnalyzer.build_dependency_graph(self)`

## function:

PythonDependencyAnalyzer.build_dependency_graph 方法处理 (self) 参数，
        Analyzes the entire repository 。

## usage example:

```python
obj.build_dependency_graph()
```


# method `PythonDependencyAnalyzer._build_module_map(self, python_files: List[Dict[str, Any]])`

## function:

PythonDependencyAnalyzer._build_module_map 方法处理 (self, python_files: List[Dict[str, Any]]) 参数，Maps module names to file paths for inte。

## usage example:

```python
obj._build_module_map()
```


# method `PythonDependencyAnalyzer._process_file(self, file_path: str)`

## function:

PythonDependencyAnalyzer._process_file 方法处理 (self, file_path: str) 参数，
        Process a single file to extrac。

## usage example:

```python
obj._process_file()
```


# method `PythonDependencyAnalyzer._add_dependency(self, source: str, target: str)`

## function:

PythonDependencyAnalyzer._add_dependency 方法处理 (self, source: str, target: str) 参数，
        Add a dependency from source to。

## usage example:

```python
obj._add_dependency()
```


# method `PythonDependencyAnalyzer.export_dependency_graph(
        self, output_format: str = "json", output_path: Optional[str] = None
    )`

## function:

PythonDependencyAnalyzer.export_dependency_graph 方法处理 (
        self, output_format: str = "json", output_path: Optional[str] = None
    ) 参数，
        Export the dependency graph in 。

## usage example:

```python
obj.export_dependency_graph()
```


# method `PythonDependencyAnalyzer._generate_dot_file(self, graph: Dict[str, Dict[str, Any]])`

## function:

PythonDependencyAnalyzer._generate_dot_file 方法处理 (self, graph: Dict[str, Dict[str, Any]]) 参数，Generate a DOT file for visualization wi。

## usage example:

```python
obj._generate_dot_file()
```


# method `PythonDependencyAnalyzer._generate_graphml_file(self, graph: Dict[str, Dict[str, Any]])`

## function:

PythonDependencyAnalyzer._generate_graphml_file 方法处理 (self, graph: Dict[str, Dict[str, Any]]) 参数，Generate a GraphML file for visualizatio。

## usage example:

```python
obj._generate_graphml_file()
```


# method `PythonDependencyAnalyzer.find_cycles(self)`

## function:

PythonDependencyAnalyzer.find_cycles 方法处理 (self) 参数，
        Find cycles in the dependency g。

## usage example:

```python
obj.find_cycles()
```


# method `PythonDependencyAnalyzer.get_dependencies(self, item: str, include_indirect: bool = False)`

## function:

PythonDependencyAnalyzer.get_dependencies 方法处理 (self, item: str, include_indirect: bool = False) 参数，
        Get dependencies for a specific。

## usage example:

```python
obj.get_dependencies()
```


# method `PythonDependencyAnalyzer.get_module_dependencies(self, module_name: str, include_indirect: bool = False)`

## function:

PythonDependencyAnalyzer.get_module_dependencies 方法处理 (self, module_name: str, include_indirect: bool = False) 参数，
        Get dependencies for a specific。

## usage example:

```python
obj.get_module_dependencies()
```


# method `PythonDependencyAnalyzer.get_dependents(self, module_name: str, include_indirect: bool = False)`

## function:

PythonDependencyAnalyzer.get_dependents 方法处理 (self, module_name: str, include_indirect: bool = False) 参数，
        Get modules that depend on the 。

## usage example:

```python
obj.get_dependents()
```


# method `PythonDependencyAnalyzer.get_file_dependencies(self, file_path: str)`

## function:

PythonDependencyAnalyzer.get_file_dependencies 方法处理 (self, file_path: str) 参数，
        Get detailed dependency informa。

## usage example:

```python
obj.get_file_dependencies()
```


# method `PythonDependencyAnalyzer.generate_dependency_report(self, output_path: Optional[str] = None)`

## function:

PythonDependencyAnalyzer.generate_dependency_report 方法处理 (self, output_path: Optional[str] = None) 参数，
        Generate a comprehensive depend。

## usage example:

```python
obj.generate_dependency_report()
```


# method `PythonDependencyAnalyzer.visualize_dependencies(self, output_path: str, format: str = "png")`

## function:

PythonDependencyAnalyzer.visualize_dependencies 方法处理 (self, output_path: str, format: str = "png") 参数，
        Generate a visualization of the。

## usage example:

```python
obj.visualize_dependencies()
```


# method `PythonDependencyAnalyzer.generate_llm_context(
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    )`

## function:

PythonDependencyAnalyzer.generate_llm_context 方法处理 (
        self, max_tokens: int = 4000, output_format: str = "markdown", output_path: Optional[str] = None
    ) 参数，
        Generate a Python-specific natu。

## usage example:

```python
obj.generate_llm_context()
```


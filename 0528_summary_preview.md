# Summary Preview

> 由大模型 mimo-v2.5-pro 自动生成，展示摘要 + 使用示例效果。


---

# module `src/kit/code_searcher.py`

## function:

该模块是代码仓库的文本搜索工具，支持基于正则表达式和文件模式的精确搜索。主要能力包括遵循 .gitignore 规则过滤文件、调用 ripgrep 提升搜索效率、解析搜索结果并提取匹配行的上下文信息。关键实现通过 subprocess 集成 ripgrep，使用 pathspec 库匹配忽略规则，并以结构化方式返回匹配详情。

## usage example:

```python
from src.kit.code_searcher import CodeSearcher, SearchOptions

# 初始化代码搜索器，指定仓库路径
searcher = CodeSearcher(repo_path="/path/to/your/repository")

# 配置搜索选项
options = SearchOptions(
    case_sensitive=False,          # 不区分大小写
    context_lines_before=3,        # 显示匹配行前3行上下文
    context_lines_after=3,         # 显示匹配行后3行上下文
    use_gitignore=True             # 遵守.gitignore规则
)

# 执行搜索：假设模块提供 search 方法（基于类描述）
# 示例：搜索正则表达式模式（如匹配函数定义）
results = searcher.search(pattern=r"def\s+\w+", options=options)

# 处理搜索结果
for match in results:
    print(f"文件: {match.get('file', '未知')}, 行号: {match.get('line', '?')}, 内容: {match.get('content', '')}")
```

# class `SearchOptions`

## function:

`SearchOptions` 类是一个配置类，用于集中管理文本搜索的各项参数设置。它封装了搜索行为的关键配置，如大小写敏感性、结果上下文行数显示规则以及是否遵循 .gitignore 规则。典型使用场景是在代码编辑器、IDE 或命令行工具中进行文件内容搜索时，通过实例化此类并设置属性来自定义搜索条件。

## extends:

none

## usage example:

```python
options = SearchOptions()
options.case_sensitive = False
options.context_lines_before = 3
options.context_lines_after = 2
options.use_gitignore = False
```

# class `CodeSearcher`

## function:

CodeSearcher 类的核心职责是在代码库中执行文本和正则表达式搜索，支持多语言和文件模式过滤并返回匹配详情。封装的数据包括代码库路径和 gitignore 规则，行为涵盖加载规则、检查文件忽略状态以及验证 ripgrep 工具的可用性。典型使用场景是开发者在代码仓库中快速查找特定代码片段、进行模式匹配，或集成到自动化工具中用于代码分析和审查。

## extends:

none

## usage example:

```python
from pathlib import Path

# 假设 CodeSearcher 类定义已导入
# from code_searcher import CodeSearcher

# 示例1: 基本使用
searcher = CodeSearcher("/path/to/your/repository")

# 示例2: 文本搜索
text_results = searcher.search_text("def main", file_pattern="*.py")
for result in text_results:
    print(f"文件: {result['file']}, 行号: {result['line']}, 内容: {result['content']}")

# 示例3: 正则搜索
regex_results = searcher.search_regex(r"class \w+:.*$", file_pattern="*.py")

# 示例4: 忽略 .gitignore 文件（自动处理）
searcher_with_gitignore = CodeSearcher("/project/with/gitignore")

# 示例5: 搜索特定语言文件
results_java = searcher.search_text("public static void main", file_pattern="*.java")

# 示例6: 检查 ripgrep 可用性
has_rg = searcher._has_ripgrep()
print(f"Ripgrep 可用: {has_rg}")
```

# method `CodeSearcher.search_text(query: str, file_pattern: str = '*.py', options: Optional[SearchOptions] = None) -> List[Dict[str, Any]]`

## function:

核心功能：使用正则表达式在指定文件模式（如 "*.py"）中搜索文本，优先调用高性能的 ripgrep 工具，不可用时回退到纯 Python 实现。
输入输出：输入为搜索模式 `query`、文件模式 `file_pattern` 和可选配置 `options`；输出为包含文件路径、行号、匹配行及上下文的字典列表。
典型使用场景：用于代码搜索、文本分析或开发工具中，在大量文件中快速定位特定模式（如函数定义、错误日志或关键词）。

## usage example:

```python
searcher = TextSearcher()
results = searcher.search_text("def function", "*.py")
for result in results:
    print(f"文件: {result['file']}, 行号: {result['line_number']}, 内容: {result['line']}")
```


---

# module `src/kit/repo_mapper.py`

## function:

RepoMapper 是一个代码仓库结构与符号的映射器，负责通过增量扫描高效遍历仓库文件树，提取各文件中的代码符号信息。它基于 Rust 实现的快速文件遍历器和 TreeSitter 符号提取器，支持多语言符号解析，并能智能忽略 `.gitignore` 规则匹配的文件。

## usage example:

```python
from src.kit.repo_mapper import RepoMapper

# 初始化 RepoMapper 实例
repo_path = "/path/to/your/repository"
mapper = RepoMapper(repo_path)

# 使用 RepoMapper 扫描仓库结构（假设存在公开方法 scan()）
# mapper.scan()

# 访问文件树（假设通过公开属性或方法获取）
file_tree = mapper._file_tree  # 或 mapper.get_file_tree()

# 访问符号映射
symbol_map = mapper._symbol_map  # 或 mapper.get_symbol_map()

# 检查文件是否应被忽略（使用私有方法示例）
test_file = Path(repo_path) / "some_file.py"
is_ignored = mapper._should_ignore(test_file)
print(f"File {test_file} is ignored: {is_ignored}")
```

# class `RepoMapper`

## function:

`RepoMapper` 类的核心职责是解析代码仓库的结构并提取符号（如函数、类名），通过增量扫描和 gitignore 过滤实现高效映射。它封装了仓库路径、文件树缓存、符号映射字典及 gitignore 规则，使用 pathspec 和字符串优化处理路径匹配。典型使用场景包括构建代码索引、IDE 项目视图或代码分析工具的基础数据获取。

## extends:

none

## usage example:

```python
from pathlib import Path
import json

# 假设仓库路径为当前目录下的一个项目
repo_path = Path("./my_python_project")

# 1. 实例化 RepoMapper
mapper = RepoMapper(repo_path)

# 2. 扫描仓库以构建文件树和符号映射
# 假设 scan() 是一个可能存在的方法来触发扫描过程
# 由于类定义中未明确给出，这里用一个假设的方法调用示意
# 如果类有 scan 方法：mapper.scan()

# 3. 获取仓库的文件树结构
file_tree = mapper.get_file_tree()  # 假设有此方法获取文件树
print("File Tree:")
print(json.dumps(file_tree, indent=2, ensure_ascii=False))

# 4. 获取特定文件的符号信息（例如，一个 Python 文件）
target_file = "src/utils.py"  # 假设仓库中的一个文件路径
symbols = mapper.get_symbols_for_file(target_file)  # 假设有此方法
print(f"\nSymbols in '{target_file}':")
print(json.dumps(symbols, indent=2, ensure_ascii=False))

# 5. 获取整个仓库的符号映射字典
symbol_map = mapper.get_symbol_map()  # 假设有此方法获取完整映射
print("\nFull Symbol Map Keys (files):")
for file_path in symbol_map:
    print(f"- {file_path}")
```

# method `RepoMapper.get_file_tree(subpath: Optional[str] = None) -> List[Dict[str, Any]]`

## function:

核心功能：递归遍历仓库目录，生成包含文件路径、大小、修改时间和类型信息的结构化数据，优先使用高性能Rust实现提升效率。
输入输出：输入可选子目录路径，输出字典列表，每个字典描述一个文件或目录的元数据。
典型使用场景：版本控制系统的文件浏览、代码仓库索引构建或需要快速获取目录结构的开发工具。

## usage example:

```python
# 假设已有一个 Repo 实例对象 repo
full_tree = repo.get_file_tree()

sub_tree = repo.get_file_tree("src/utils")
```

# method `RepoMapper.scan_repo() -> None`

## function:

该方法扫描指定代码仓库中所有支持的文件（基于文件扩展名），利用文件修改时间（mtime）避免重复解析，以增量更新符号映射表。输入是实例的仓库路径，输出为更新内部符号映射（返回空）。典型使用场景包括代码分析工具或集成开发环境（IDE），用于实时索引代码符号以支持代码导航和搜索。

## usage example:

```python
extractor = TreeSitterSymbolExtractor(repo_path="your_repo_path")
extractor.scan_repo()
```


---

# module `src/kit/utils.py`

## function:

这个模块是kit项目的共享工具库，负责提供通用实用函数。主要功能包括格式化持续时间和文件大小为人类可读格式、验证相对路径以防止目录遍历攻击、解析Git URL提取所有者和仓库名以及截断文本。关键实现通过条件逻辑处理格式化、使用路径部分检查确保安全性、解析字符串匹配GitHub URL格式以及基于长度进行文本切片来完成。

## usage example:

```python
from src.kit.utils import (
    format_duration,
    format_size,
    validate_relative_path,
    parse_git_url,
    truncate_text,
)
from pathlib import Path

# 1. 格式化持续时间
duration1 = format_duration(0.5)       # 返回 "500.0ms"
duration2 = format_duration(45.123)    # 返回 "45.12s"
duration3 = format_duration(125.5)     # 返回 "2m 5.5s"

# 2. 格式化文件大小
size1 = format_size(1023)              # 返回 "1023.0B"
size2 = format_size(1024 * 1024)       # 返回 "1.0MB"
size3 = format_size(1024**3)           # 返回 "1.0GB"

# 3. 验证相对路径
base = Path("/project/root")
valid_path = validate_relative_path(base, "subdir/file.txt")
# 返回 Path("/project/root/subdir/file.txt")

# 4. 解析 Git URL
github_url = "https://github.com/owner/repo.git"
ssh_url = "git@github.com:owner/repo.git"
result1 = parse_git_url(github_url)    # 返回 ("owner", "repo")
result2 = parse_git_url(ssh_url)       # 返回 ("owner", "repo")
invalid_url = "https://example.com"
result3 = parse_git_url(invalid_url)   # 返回 None

# 5. 截断文本
long_text = "这是一段很长的文本，需要被截断"
short_text = truncate_text(long_text, 10)   # 返回 "这是一段很长的文..."
```

# func `format_duration(seconds: float) -> str`

## function:

该函数将输入的秒数转换为人类可读的时间格式，根据秒数大小自动选择毫秒、秒或分钟作为输出单位。输入是一个浮点数类型的秒数，输出是一个格式化后的字符串。典型使用场景包括显示程序执行时间或视频长度，便于用户直观理解时间间隔。

## usage example:

```python
print(format_duration(0.5))
print(format_duration(30.5))
print(format_duration(125))
```

# func `format_size(bytes_size: int) -> str`

## function:

该函数的核心功能是将字节数自动转换为人类易读的单位格式，如KB、MB等。输入为整数字节数，输出为带一位小数和单位的字符串。典型使用场景包括文件大小显示或网络数据传输量报告。

## usage example:

```python
print(format_size(1024))    # 输出：1.0KB
print(format_size(500))     # 输出：500.0B
print(format_size(1048576)) # 输出：1.0MB
```


---

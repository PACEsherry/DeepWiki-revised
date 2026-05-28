# Summary Extraction Tool

基于 deepwiki-open 和 kit 的代码分析逻辑，使用 MiMo 大模型提取代码仓库摘要。

## 功能特性

- 自动扫描代码仓库，识别库、模块、接口、类、方法、函数、配置等
- 使用 MiMo 大模型生成中文摘要
- 按照 `Summary_Output_Templet.md` 模板格式输出
- 支持 Python、JavaScript、TypeScript 等多种语言

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量配置

```bash
export MIMO_API_KEY="your-api-key"
export MIMO_BASE_URL="https://api.openai.com/v1"  # 或其他兼容 OpenAI 的 API
export MIMO_MODEL="mimo-7b"  # 或其他模型名称
```

## 使用方法

```bash
# 分析本地仓库
python summary_extraction.py /path/to/repository

# 指定输出文件
python summary_extraction.py /path/to/repository --output my_summary.md

# 指定模型参数
python summary_extraction.py /path/to/repository --model mimo-7b --max-tokens 8192
```

## 输出格式

输出文件遵循 `Summary_Output_Templet.md` 模板格式，包含：

- **library**: 库级别摘要
- **module**: 模块级别摘要
- **class**: 类级别摘要
- **method**: 方法级别摘要
- **func**: 函数级别摘要
- **interface**: 接口级别摘要
- **config**: 配置级别摘要

## 核心算法

本工具结合了两个开源项目的优点：

1. **deepwiki-open**: 文件读取、文档处理、RAG 检索逻辑
2. **kit**: 符号提取（tree-sitter）、LLM 摘要生成逻辑

## 文件结构

```
DeepWiki-revised/
├── summary_extraction.py      # 主提取脚本
├── Summary_Output_Templet.md  # 输出模板
├── requirements.txt           # Python 依赖
├── deepwiki-open/             # deepwiki-open 仓库
└── kit/                       # kit 仓库
```

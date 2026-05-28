# Summary Output Template

> 本文档用于记录代码仓库中的广义接口摘要，包括库、模块、接口、类、方法、函数、配置、服务、变量、常量等。
> 每个条目应尽量保持结构统一，方便后续被 AI 检索、理解和定位源码，生成拓扑结构索引。

---

# library libraryName

## function:

用简洁的中文自然语言说明该库的整体用途、对外提供的核心能力，以及它在项目中的主要作用。

## usage example:

```ts
import { xxx } from "libraryName";
const result = xxx(input);
```

# module moduleName

## function:

说明该模块负责的业务范围或技术职责，例如用户认证、配置解析、文件扫描、摘要生成、索引构建、代码搜索等。

## usage example:

import { createSummaryIndex } from "./summary-indexer";
const index = await createSummaryIndex(repoPath);

# interface InterfaceName

## function:

说明该接口描述的数据结构、对象职责或对外契约。重点说明它约束了哪些字段，以及这些字段在业务逻辑中的作用。

## extends:

继承自哪些接口；如果没有则写 `none`。

## implemented by:

被哪些类实现；如果没有或暂未分析则写 `unknown`。

## declaration:
```ts
interface InterfaceName extends BaseInterface {
  methodName(param: Type): ReturnType;
}
```

## usage example:

class ClassName implements InterfaceName {
  methodName(param: Type): ReturnType {
    return result;
  }
}

# class ClassName

## function:

说明该类的核心职责、封装的数据或行为，以及它在系统中的角色。

## usage example:

const searcher = new InterfaceSummarySearcher(indexPath);
const results = await searcher.search("登录 session 是在哪里创建的");

# method ClassName.methodName(Type1: param1, Type2: param2, ...)

## function:

说明该方法在类中的具体职责，包括它读取或修改了哪些状态、调用了哪些核心流程。

## extends:

继承自哪个父类；如果没有则写 none。

## implements:

实现了哪些接口；如果没有则写 none。

## usage example:

const indexer = new InterfaceSummaryIndexer(config);
await indexer.build();

# func functionName(Type1: param1, Type2: param2, Type3: param3, ...)

## function:

用简洁的中文自然语言说明该函数完成的核心任务，包括主要输入、主要处理逻辑和主要输出结果。

## usage example:

const symbols = await extractSymbols(repoPath, {
  includePrivate: false,
});
console.log(symbols.length);

# config configName

## function:

说明该配置项或配置文件控制的功能范围，以及关键字段的含义。

## declaration:
{
  "repoPath": "./demo-project",
  "outputFormat": "markdown",
  "includePrivate": false,
  "language": "typescript"
}

## usage example:

const config = loadConfig("./summary.config.json");
await buildSummaryIndex(config);

# service ServiceName

## function:

说明该 service 封装的业务逻辑，以及它通常会调用哪些 repository、外部 API 或工具函数。

## usage example:

const session = await authService.createSession(userId);

# var variableName: Type

## function:

说明该变量的含义、保存的数据内容，以及它通常在哪些逻辑中被使用。

## usage example:

let currentRepoPath: string = "D:/ZSY/demo-project";
console.log(currentRepoPath);

# const CONSTANT_NAME: Type

## function:

说明该常量的用途、取值含义，以及是否用于配置、默认参数、路径、正则规则或枚举映射。

## usage example:

const DEFAULT_OUTPUT_FORMAT: string = "markdown";
generateSummary({
  format: DEFAULT_OUTPUT_FORMAT,
});

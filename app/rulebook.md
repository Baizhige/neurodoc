# EEG Dataset `analysis_minimax_v2.md` 文档生成与审核规则

状态：草案 v0.5

最近确认：2026-04-05

变更摘要（v0.4 → v0.5）：
- 新增 `## File Scan Result` 顶层节，包含 Kernel 指纹 blockquote 与三个子节。
- `## Event Structure` 和 `## MISC Label Summary` 降级为 `### Event Structure` / `### MISC Label Summary`，内容规则不变。
- 新增 `### Info` 子节（第57条之一～之五），记录受试者与设备元信息完整性。
- `Label Route` 重定义为监督信号来源，三值：`event / misc / info`（废止 `Annotation`/`STIM` 作为 Label Route 值）。
- 新增第77条之二：`Label Route = info` 时的 Target Definition 格式规则。

变更摘要（v0.3 → v0.4）：
- `## Kernel Responsibilities` 节移至 `## Data Quality Notes` 之后。
- `Event Structure` 下的 Event Type 图例行（`> **Event Type**: ...`）废止，不再要求在文档中声明枚举含义。
- 第53条之一（说明性 Note）改为非强制，并明确禁止重复解释 Type 枚举。

变更摘要（v0.2 → v0.3）：
- `Kernel Responsibilities Area` 大幅简化：废止 Type 1/2/3 模板文本、`Selected Mode`、`Why`、`Primary Label Routes`、`Web Reference Used for Decision`。
- blockquote 元字段仅保留 `Super Meta Required`（Yes/No）与 `Status` 两个字段。
- 新增 `Super Meta Required` 字段定义与判定规则（新第37条、第38条）。

变更摘要（v0.1 → v0.2）：
- `STIM Label Summary` 节废止；所有离散事件（含原 stim channel 来源）统一在 `Event Structure` 中登记。
- `Event Structure.Type` 枚举简化为 `event` / `admin` 两类，废止 `short`、`long`、`rest`。
- `target_events` 合法来源简化为唯一来源：`Event Structure` 中 `Type = event` 的条目。
- `Label Route` 明确为 kernel 输出格式，与原始存储来源解耦。

适用对象：LLM 审核脚本、人类审核员、维护者

适用范围：本仓库内各数据集目录下的 `analysis_minimax_v2.md` 及后续同结构版本文档

---

# 第一编 总则

## 第一章 目的与适用范围

### 第1条 目的

本规则用于统一 EEG 数据集 `analysis_minimax_v2.md` 文档的生成、审核、修订与复核行为，使相关文档能够同时服务于以下目标：

1. 为人工审核员提供一致、明确、可执行的审核标准。
2. 为 LLM 审核脚本提供稳定、可编程、可追溯的决策依据。
3. 为后续 kernel、EEGUnity 导出与 HDF5 生产提供结构化实现依据。

### 第2条 适用范围

本规则适用于以下行为：

1. 新建数据集文档。
2. 修订既有数据集文档。
3. 对 `Classical Task`、`Potential Task`、`Event Structure`、`Meta Area` 等核心栏目进行人工审核。
4. 为后续 LLM 审核脚本编写判定规则、提示词规则与降级规则。

### 第3条 基本原则

文档生成与审核应遵守以下原则：

1. 真实性优先。
2. 数据优先于网页描述。
3. 保守优于猜测。
4. 可追溯优于简洁表述。
5. 能落地实现优于理论上可想象的任务定义。


## 第二章 术语定义

### 第4条 数据集文档

本规则所称“数据集文档”，是指单个数据集目录下的 `analysis_minimax_v2.md` 或同结构后续版本文档。

### 第5条 Raw Meta

`raw meta` 是指原始数据中已经直接存在、无需额外推导即可读取的标签、事件、码值、注释、字段或标记。包括但不限于：

1. `events.tsv` 中的 `trial_type`、事件码、事件名称。
2. trigger/stim 通道中的原始码值。
3. 原始注释文件中的离散事件。
4. 原始表格中直接存在的可用行为字段。

### 第6条 Super Meta

`super meta` 是指原始数据中不存在，必须通过程序、规则或人工逻辑进一步生成、映射、折叠、配对、聚合或连接后才能获得的标签或目标。包括但不限于：

1. 反应事件。
2. 多个原始类折叠后的二分类标签。
3. 由文件名、受试者信息表、外部表格派生出的临床分组。
4. 由多个事件配对得到的正确/错误、目标/非目标、快/慢等标签。

### 第7条 Kernel

`kernel` 是指后续用于解析原始数据、构造标签、路由标签并生成 EEGUnity 兼容输出的数据处理代码或数据加载逻辑。

### 第8条 Label Route

`Label Route` 是指标签在 EEGUnity/MNE 兼容实现中的最终落地路径，而不等同于原始文件中天然存在的存储方式。包括：

1. `Annotation`：基于时间的标注对象，使用 `onset`、`duration`、`description` 描述事件或时间段；其本质不是 channel type。
2. `STIM`：trigger/stim channel 路由，适用于以码值或触发脉冲形式表达的事件标签。
3. `MISC`：misc channel 路由，适用于数值型辅助标签、连续量或不宜直接表示为事件名称的附属标签。

### 第9条 Task

`Task` 是指文档中可直接指导 EEG 数据切窗、标签构造与监督学习配置的任务定义。

### 第10条 Classical Task

`Classical Task` 是指同时得到外部证据支持且能够被当前公开数据实际落地实现的核心任务。

### 第11条 Potential Task

`Potential Task` 是指由数据本身支持、但外部证据不足以确认其为该数据集核心基准任务，或仅为推荐性、扩展性、派生性的任务。

### 第12条 Evidence

`Evidence` 是指支撑任务成立、参数选择或文档判断的外部依据，包括：

1. 数据集官方页面。
2. 官方说明文档。
3. 明确使用该数据集的论文。
4. 其他权威来源。


## 第三章 证据优先级与冲突处理

### 第13条 证据优先级

出现冲突时，证据优先级原则上按以下顺序排列：

1. 实际可验证的数据文件及其伴随标注文件。
2. 数据集官方页面、官方 README、官方说明文档。
3. 官方或明确使用该数据集的论文。
4. 第三方介绍页面、博客、非官方说明。

### 第14条 冲突处理总原则

当不同来源信息冲突时，应当优先采用高优先级证据，并在 `Data Quality Notes` 中记录冲突及裁定立场。

### 第15条 数据优先原则

当在线资料、论文描述与实际数据文件不一致时，应当以实际数据文件为准；但不得忽略这种不一致，而应在文档中显式指出。

### 第16条 保守原则

当现有证据不足以确认某个字段、某项任务或某个标签时：

1. 应当优先降级为 `Potential Task`。
2. 可以使用 `Needs verification`、`Variable`、`N/A`、`null` 等占位词。
3. 不得凭空补足缺失信息。

### 第17条 可实现性原则

即使某篇论文使用了该数据集，只要公开数据中不存在足以实现该任务的标签、事件或可验证的派生路径，该任务也不得直接认定为有效 `Classical Task`。


## 第四章 角色分工

### 第18条 管理员职责

管理员负责：

1. 决定数据集条目的命名。
2. 决定是否接受人工修订或 PR 中的规则更新。
3. 决定是否需要新增或重写 kernel。

### 第19条 人类审核员职责

人类审核员负责：

1. 审核 `Classical Task` 是否成立。
2. 审核字段是否与真实数据和官方资料一致。
3. 判断冲突信息的裁定方向。
4. 在需要时标记 `Manual Review`。

### 第20条 LLM 审核脚本职责

LLM 审核脚本负责：

1. 在既定规则下预生成或预修正文档。
2. 根据规则识别潜在冲突、缺漏和无效任务。
3. 输出保守、可追溯的建议，不得编造不存在的原始标签。


# 第二编 分则

## 第五章 Meta Area

### 第21条 字段总则

`Meta Area` 用于记录数据集的标识性元信息。除本规则另有规定外，字段应当优先简洁、稳定、便于程序读取。

### 第22条 `Dataset`

1. `Dataset` 字段为数据集标识符。
2. 该字段命名格式应为 `<source_name_id>`。
3. 该字段由管理员决定命名。
4. 审核员与 LLM 不得主动修改该字段。

### 第23条 `Year`

1. `Year` 字段用于记录与数据采集、处理或发布相关的关键年份集合。
2. 该字段不要求区分“采集年份”与“发布年份”。
3. 如同时涉及多个关键年份，可使用 `/` 连接，如 `2004/2021`。
4. 如涉及连续年份区间，可使用 `-` 连接，如 `2008-2015/2017`。
5. 该字段无需保证完全覆盖全部历史年份，应根据已有可信资料尽力更新。
6. 尽力避免因网页标题年份而忽略数据本身明确给出的关键年份。

### 第24条 `URL`

1. `URL` 应当优先指向可获取下载入口或数据说明的信息页面。
2. 如存在文件直链与信息页两种选择，应优先保留信息页。
3. 当链接失效且无法替换为有效信息页时，应删除或改写为可访问的权威页面。
4. 该字段不要求永久有效，但应保证在审核时具备实际访问价值。

### 第25条 `Category`

1. `Category` 必须且只能取以下六类之一：
   - `Complex Applied`
   - `High-level Mental`
   - `Action/Output`
   - `Sensory/Response`
   - `Biological State`
   - `Others`
2. 该字段原则上由程序或预处理 LLM 先行给出。
3. 人工审核员仅在分类明显错误时进行修正。
4. 不得创建上述六类之外的新分类值。

### 第26条 `Subjects`

1. `Subjects` 为数据集所涉及的有效被试数，取整数。
2. 如官方人数与实际可用人数不一致，应优先采用实际可用人数。
3. 该类冲突应在 `Data Quality Notes` 中说明。

### 第27条 `Files (Completed)`

1. `Files (Completed)` 指 EEGUnity 程序解析为 `Completed` 的文件数量。
2. 该字段原则上不由 LLM 与人工审核员手工修改。
3. 如程序解析结果明显异常，应提交“需重解析”或“需修正 kernel”的结论，而非直接手工篡改。

### 第28条 `Channels`

1. `Channels` 指文件所使用的通道数量，包含非 EEG 通道。
2. 若存在少量不同通道数量且可以清晰列举，可使用 `32/64`、`22-128` 等方式表示。
3. 若情况复杂且不宜完整枚举，可使用 `Variable`。
4. 允许采用 LLM 或审核员认为最清晰的表示方式，但应避免引起歧义。

### 第29条 `Sampling Rate`

1. `Sampling Rate` 应记录数据的主要采样率信息。
2. 当全数据集采样率一致时，应写明单一值。
3. 当不同文件、模态或阶段存在明显差异时，可以使用多值或说明性写法。
4. 当差异复杂且不宜完整枚举时，可以使用 `Variable`，并在 `Data Quality Notes` 中补充说明。

### 第30条 `Manual Review`

1. `Manual Review` 仅能由人类审核员填写。
2. 填写内容可以为姓名、笔名或审核员认可的标识符。
3. 多位人类审核员应按先后顺序使用 `/` 分隔。
4. LLM 不得伪造、补写或冒充 `Manual Review` 标记。

### 第30条之一 固定结构

1. 当前版本原则上只保留以下一级栏目，并按既有模板顺序组织：
   - `## Paradigm`
   - `## File Scan Result`
   - `## Tasks`
   - `## Data Quality Notes`
   - `## Kernel Responsibilities`
2. `## File Scan Result` 节下设以下三级子节，顺序固定：
   - `### Event Structure`（必须）
   - `### MISC Label Summary`（可选）
   - `### Info`（必须）
3. 除本规则明确列出的可选栏目外，不得擅自重命名固定栏目标题。
4. `STIM Label Summary` 已废止，不得在新文档中新增该栏目。原始数据中来自 trigger/stim channel 的离散事件，应统一在 `### Event Structure` 表格中登记。

### 第30条之二 禁止额外章节

1. 除维护者明确要求外，不得新增非模板一级栏目，例如 `## Meta`、独立 `## References`、自定义扩展说明区等。
2. 如确需补充说明，应优先写入现有栏目下的 `Kernel Notes`、`Data Quality Notes` 或审核记录，而不应新增一级章节。
3. 对既有历史文档进行实质性修订时，应同步删除不符合现行结构的额外章节，除非维护者另有明确要求。


## 第六章 Paradigm Area

### 第31条 范式描述总则

`Paradigm Area` 应描述数据集的实验范式、任务形式、被试行为与记录方式，并应与数据实际内容相一致。

### 第32条 一致性要求

范式描述应当同时对齐以下信息：

1. 数据目录与文件结构。
2. 事件文件。
3. 官方页面与官方说明。
4. 明确使用该数据集的权威论文。

### 第33条 数据优先

当在线资料与数据资料不一致时，应当以数据为准。

### 第34条 禁止过度推断

范式描述不得将论文中的实验目的、理论假设或作者常用分析方式，直接改写为当前公开数据已明确支持的标签任务，除非数据中确有可落地的事件或标签依据。

### 第35条 描述边界

范式描述可以写明实验原本意图，但应区分以下两层内容：

1. 实验设计层面的目标。
2. 当前公开数据层面实际可用的标签和任务。


## 第七章 Kernel Responsibilities Area

### 第36条 节的作用与结构

1. `Kernel Responsibilities Area` 用于记录当前数据集在 kernel 语义层面的核心判断。
2. 该节采用 blockquote 元字段形式，当前版本只保留两个字段：`Super Meta Required` 与 `Status`，按此顺序书写。
3. 不得在本节新增其他字段、自定义块或说明性文本。
4. 历史文档中遗留的 `Type 1/2/3` 模板文本、`Selected Mode`、`Why`、`Primary Label Routes`、`Web Reference Used for Decision` 等字段已废止，在实质性修订时应同步删除。

### 第37条 `Super Meta Required`

1. `Super Meta Required` 表示当前数据集是否存在需要额外派生、配对、折叠、映射或跨文件连接才能生成的目标标签。
2. 合法取值仅为以下两种：
   - `Yes` — `Tasks Area` 中至少一个任务的 `Meta Level = super`
   - `No` — 所有任务的 `Meta Level = raw`
3. 该字段不得使用其他同义词或大小写变体。

### 第38条 `Super Meta Required` 的判定规则

1. 凡 `Tasks Area` 中任一任务（含 `Classical Task` 与 `Potential Task`）的 `Meta Level = super`，则 `Super Meta Required` 必须为 `Yes`。
2. 所有任务的 `Meta Level = raw`，则 `Super Meta Required` 应为 `No`。
3. 若 `Super Meta Required` 字段与 `Tasks Area` 实际情况不一致，以 `Tasks Area` 为准，并应同步修正本字段。
4. LLM 审核脚本可根据 `Tasks Area` 自动推断并填写本字段。

### 第42条之一 `Status`

1. `Status` 用于标记“当前文档文本状态”是否已足以支撑后续 kernel 重构、EEGUnity 导出或事件/标签重建。
2. `Status` 为数据集级字段，不按单个 `Task` 分别填写。
3. 虽然 `Status` 在性质上属于元信息，但当前版本中应写在 `Kernel Responsibilities Area` 的 blockquote 元字段中，而非新增一级栏目。
4. `Status` 可以由 LLM 审核脚本、人类审核员或维护者根据最新判断进行修改。

### 第42条之二 `Status` 合法取值

`Status` 仅允许以下三种机器可读写法：

1. `wait_kernel_update`
2. `wait_manual_review`
3. `completed`

不得使用上述写法之外的同义词、自然语言短句或大小写变体替代。

### 第42条之二之一 `completed` 的权限边界

1. `completed` 仅能由管理员或人类审核员给出。
2. LLM 审核脚本当前阶段不得主动将任何数据集判为 `completed`。
3. 因此，LLM 审核脚本在当前阶段只应在 `wait_kernel_update` 与 `wait_manual_review` 之间作二选一判断。
4. 若当前文本已经足以支撑既有任务、且未暴露明确的 kernel 结构性缺口，LLM 审核脚本也应暂时保守地给出 `wait_manual_review`，等待管理员或人类审核员最终确认是否提升为 `completed`。

### 第42条之三 `Status` 判定规则

1. `wait_kernel_update` 表示：当前文档文本已经明确暴露出 kernel 语义层面的结构性缺口，即 `Event Structure`、`MISC Label Summary`、`Label Route`、companion files 接入、`super meta` 的整合路径等内容尚不足以支撑既有任务稳定成立。
2. `wait_manual_review` 表示：当前文档未明确暴露上述 kernel 结构性缺口，或虽然仍有疑点，但这些疑点主要属于人类审核确认、任务去留确认、最终放行确认，而不应被自动判定为”必须修改 kernel”。
3. `completed` 表示：当前文档已提供足够可信、可追溯、可实现的信息，能够支撑后续 kernel 重构或 EEGUnity 导出；后续工作即使尚未真正编码，也不影响该文本状态成立。
4. `Status` 反映的是”当前文本是否足够支撑 kernel 责任闭环”，而不是”代码是否已经写完”。
5. 下列事项原则上不得单独作为 `wait_kernel_update` 的判定理由：
   - 常规预处理、滤波、重参考、下采样
   - artifact rejection、坏段剔除、坏文件筛除
   - 一般性数据质量控制
   - 训练参数、epoch 长度、模型超参数等实现细节
   - 仅凭文档外推测 kernel 现实中也许尚未写完或尚未验证
6. 若文档语义上已经把相关事件、标签、companion files 或 metadata 接入路径说清楚，并以“当前方案已可成立”的口吻组织任务，则不应仅因实现层面的谨慎猜测而判为 `wait_kernel_update`。
7. 当同一数据集同时存在多类问题时，判定优先级应为：`wait_manual_review` 高于 `wait_kernel_update`，`wait_kernel_update` 高于 `completed`。

### 第42条之四 blockquote 书写位置与顺序

1. 当前版本中，`Kernel Responsibilities Area` 下的 blockquote 元字段应按以下顺序书写：
   - `Super Meta Required`
   - `Status`
2. 不得为上述字段单独新增一级章节或自定义块。
3. 若维护脚本批量改写 `Status`，应只修改该字段所在固定行，不得顺带重写其他正文内容。


## 第八章 File Scan Result Area

`## File Scan Result` 节汇总 kernel 对原始数据文件的扫描结果，包括 kernel 指纹、事件结构、MISC 标签与受试者信息。该节下设三个固定子节（`### Event Structure`、`### MISC Label Summary`、`### Info`），并在节开头提供 kernel 指纹 blockquote。

### 第42条之五 Kernel 指纹

1. `## File Scan Result` 节开头应以 blockquote 形式记录生成本扫描结果所用的 kernel 版本与哈希。
2. 格式为：
   ```
   > **Kernel**: EEGUnity vX.Y | `path/to/kernel1.py` | `path/to/kernel2.py`
   > **SHA256**: `<full_hash>`
   ```
3. `EEGUnity vX.Y` 为扫描时所用 EEGUnity 版本号。
4. `SHA256` 为所有参与哈希的 kernel 文件内容的联合摘要，由维护脚本自动计算，不应手工填写。
5. 若当前数据集尚无 kernel，`Kernel` 字段写 `N/A`，`SHA256` 字段写 `N/A`。
6. 该 blockquote 由自动化脚本维护，人类审核员与 LLM 不得手工修改哈希值。

### 第一节 Event Structure（子节）

### 第43条 表格形式

`### Event Structure` 应以表格形式呈现。表格可为空，但其为空本身应被视为具有规则后果的判断结果。

### 第44条 列要求

表格至少应包含以下列：

1. `Event ID`
2. `Count (total)`
3. `Type`
4. `Meta Level`
5. `Meaning`

### 第45条 空表格的后果

当 `Event Structure` 实际为空，或明确表示“无任何有效事件标签”时：

1. 不得保留 `epoch_by_event_hdf5` 任务。
2. 不得保留 `epoch_by_long_event_hdf5` 任务。
3. 原则上仅可考虑 `epoch_by_segmentation_hdf5`。

### 第46条 `Type` 的合法取值

`Type` 仅允许以下两个值：

1. `event` — 可用于任务的离散事件或时间段，包括刺激、反应、状态转换、睡眠分期等全部业务性事件。
2. `admin` — 系统性、边界性或应被排除的事件，如设备标记、文件边界、运动伪迹标记等。

> **说明**：原有的 `short`、`long`、`rest` 细分类型已废止。事件时长特征（瞬时 vs 持续）由 `Epoch Method` 在 `Tasks Area` 中决定，不在 `Event Structure` 中重复标注。

### 第47条 `admin` 事件

1. `admin` 事件应显式保留在 `Event Structure` 表格中，不得默认删除。
2. `admin` 事件默认不得作为监督学习任务的 `target_events`。
3. 如确有例外，应提供强证据并在 `Kernel Notes` 中写明理由。

### 第48条 `Meta Level` 的判定

1. 能直接从原始数据读取的事件，应标记为 `raw`。
2. 需经配对、折叠、推导、映射、连接或重构而成的事件，应标记为 `super`。

### 第49条 首次制作原则

首次制作文档时，`Event Structure` 原则上仅记录 `raw meta`。若 `super meta` 尚未由稳定 kernel 支持，不应伪装为已存在的原始事件。

### 第50条 与资料不符的处理

当 `Event Structure` 与数据集资料描述严重不符时，应作如下处理：

1. 若不影响 `Tasks Area` 的有效性，可在 `Data Quality Notes` 中注明警告。
2. 若影响任务有效性，应优先修正事件解释、降级任务、删除任务，或提交“需重解析”结论。
3. 不得在未说明冲突的情况下强行维持错误任务。

### 第51条 解析差异

当 `Event Structure` 与资料不符的原因疑似来自 kernel 解析差异时：

1. 若不影响任务成立，可暂不修正。
2. 若影响任务成立，应明确标记为“需重解析”或“需修正 kernel”。

### 第51条之一 与 `Status` 的联动

1. 若当前 `Event Structure`、`MISC Label Summary`（如有）与 `Tasks Area` 之间，已经在文档语义上形成足够一致的证据链，则不应仅因预处理、artifact rejection、质量控制或实现细节而判为 `wait_kernel_update`。
2. 若当前 `Event Structure` 的不足会直接导致 `Type 1/2/3` 责任无法闭环，例如原应进入文档的原始事件尚未登记、应进入 `MISC` 的连续目标尚无路由说明、companion files 或 `participants.tsv/events.tsv` 的接入方式尚未在文本中交代清楚，则 `Status` 原则上应为 `wait_kernel_update`。
3. 若当前文档已经足以组成既有 `Classical Task` 或 `Potential Task` 的文本依据，但是否最终放行为 `completed` 仍需管理员或人类审核员确认，则 LLM 审核脚本应暂时判为 `wait_manual_review`。
4. 若当前 `Event Structure` 不足以支撑现有任务，且问题主要来自任务定义本身是否成立、事件语义是否正确、证据是否冲突、标签映射是否应被删除或降级等人工裁定问题，则 `Status` 原则上应为 `wait_manual_review`。
5. 仅当当前 `Event Structure` 与相关任务、路由说明、`MISC Label Summary`（如有）之间已形成足够一致且可追溯的实现依据，并经管理员或人类审核员确认后，`Status` 方可为 `completed`。

### 第52条 上下文依赖事件

若同一事件码在不同文件、不同 task、或不同实验阶段中具有不同语义，应视为“上下文依赖事件”。

对此类事件：

1. 不得脱离文件级上下文独立解释其语义。
2. 应在 `Event Structure` 或 `Data Quality Notes` 中明确警告。
3. 如无稳定上下文判定规则，不得将其直接用于高置信度 `Classical Task`。

### 第53条 `super meta` 的后续更新

当 `Classical Task` 依赖 `super meta` 时，原则上不要求人工先手工改写 `Event Structure`。该类更新宜由后续 kernel 与 LLM 自动化流程完成。

### 第53条之一 `Event Structure` 下的说明性 Note

1. `Event Structure` 表格之后可以设置可选的说明性 `Note`，但不作强制要求。
2. 不得在该 `Note` 中重复解释 `Type` 枚举值的含义；`event` 与 `admin` 的语义由规则书统一定义，文档中无需重复声明。
3. 该 `Note` 仅用于以下情形：
   - 原始数据存在解析歧义（如同一事件码在不同文件中语义不同），需说明当前文档立场；
   - 事件来自多种来源（如 companion file、trigger channel）且合并方式需交代；
   - 其他对 kernel 实现有实质影响的说明。
4. 该 `Note` 不应用于凭空引入表格中不存在的新事件。
5. 若后续 kernel 更新导致事件表达方式发生变化，应优先修改该 `Note` 与相关任务路由，再决定是否需要改写 `Event Structure` 主表。

### 第53条之二 companion files 与外部表的使用

1. 若标签、事件区间或辅助字段直接存在于数据集随附的官方 companion files、`participants.tsv`、行为表、sleep stage 文件或其他正式 sidecar 中，原则上可以作为合法信息源使用。
2. 若上述信息本质上是离散事件或时间段，并将被用于 `target_events` 或事件型任务，必须先在 `Event Structure` 中登记后方可被任务引用。
3. 若上述信息本质上是每 epoch 一个类别、标量、计数、评分或连续量，不应强行写入 `Event Structure`；应根据其最终路由写入 `MISC Label Summary` 或 `Kernel Notes`。
4. 仅当这些字段可直接读取且无需额外推导时，方可视为 `raw`；若需要配对、映射、标准化、跨文件连接或规则重建，则应视为 `super`。


### 第二节 MISC Label Summary（子节）

### 第54条 一般规则

`### MISC Label Summary` 用于描述数值型或连续型辅助标签的来源、含义与实现方式。

> **说明**：`STIM Label Summary` 已废止。原始数据中来自 trigger/stim channel 的离散事件，应统一在 `### Event Structure` 表格中登记，不再单独设置 `STIM Label Summary` 节。

### 第55条 出现条件

1. 如某个任务使用 `misc` 作为 `Label Route`，则 `### MISC Label Summary` 必须存在。
2. 若 `misc` 路由未实际用于任何任务，该子节可以省略。

### 第56条 内容要求

`### MISC Label Summary` 至少应说明：

1. 字段名称。
2. 字段来源（原始表格、事件字段、companion file 等）。
3. 字段是 `raw` 还是 `super`。
4. 单位、对齐方式与必要的派生逻辑说明。

### 第57条 自动化原则

该部分原则上由 kernel 与 LLM 自动生成，人类审核员仅在明显错误、遗漏或任务依赖冲突时进行修正。


### 第三节 Info（子节）

### 第57条之一 一般规则

1. `### Info` 记录数据集文件级受试者与设备元信息的可用性，供 `Label Route = info` 类任务使用。
2. 该子节为必须节，不可省略；若信息完全缺失，仍需填写相应字段并标注 `missing`。

### 第57条之二 字段与完整性

1. `### Info` 以表格形式呈现，固定列为 `Field`、`Completeness`、`Notes`。
2. 以下字段为必填字段（可填 `missing`）：
   - `subject_age`
   - `subject_sex`
   - `device`
3. 以下字段为可选字段，仅在数据集存在受试者分组概念时填写：
   - `subject_group`

### 第57条之三 `Completeness` 合法取值

`Completeness` 仅允许以下四值：

1. `complete` — 数据集中每条 EEG 记录均存在该字段。
2. `partial` — 多数记录存在，但不保证全覆盖；具体比例可在 `Notes` 中说明。
3. `incomplete` — 明确存在较多缺失，缺失程度显著。
4. `missing` — 完全缺失。

### 第57条之四 `Notes` 列

1. `Notes` 列为可选补充说明，可填写数值范围、枚举值、缺失原因等。
2. 若无需补充，填写 `N/A`。

### 第57条之五 自动化原则

1. `subject_age` 与 `subject_sex` 的 `Completeness` 原则上由 kernel 扫描结果（`locator_meta`）自动推断。
2. `device` 与 `subject_group` 可由 LLM 从官方页面或 README 辅助填写。
3. 人类审核员仅在自动填写明显错误或缺失时进行修正。


## 第九章（原第九章已并入第八章）

> **说明**：原第九章 `MISC Label Summary` 已并入第八章 `File Scan Result Area` 的第二节，本章编号保留为空，不再另设内容。


## 第十章 Tasks Area

### 第一节 一般规则

### 第58条 任务区地位

`Tasks Area` 是文档中最关键的执行区，应能直接指导 EEG 数据切窗、标签生成与后续实现。

### 第59条 任务标题

任务标题应采用以下形式之一：

1. `### Classical Task N: ...`
2. `### Potential Task N: ...`

### 第60条 任务字段顺序

每个任务原则上应包含以下字段，并保持稳定顺序：

1. `Task Type`
2. `Epoch Method`
3. `Epoch Parameters`
4. `Label Route`
5. `Meta Level`
6. `Target Definition`
7. `Super Meta Notes`（如适用）
8. `Evidence`（`Classical Task` 必填）
9. `Kernel Notes`

### 第61条 历史遗留写法

当前仓库中可能存在将 `segmentation` 写入 `Task Type` 的历史写法。自本规则草案起，建议统一如下：

1. `Task Type` 只使用 `classification` 或 `regression`。
2. `epoch_by_segmentation_hdf5` 仅作为 `Epoch Method` 使用。
3. 历史遗留文档可暂不立即批量清理，但新文档与新修订应尽量遵循本条。


### 第二节 Classical Task 与 Potential Task

### 第62条 `Classical Task` 成立条件

`Classical Task` 同时满足下列两个条件时方可成立：

1. 存在证据表明外部文献或权威来源明确使用了本数据集或其可识别子集。
2. 该证据明确支持当前任务目标、标签定义或监督目标。

### 第62条之一 `Classical Task` 明确性要求

1. `Classical Task` 的关键字段不得使用模糊占位符。
2. 本条所称关键字段，至少包括：
   - `Task Type`
   - `Epoch Method`
   - `Epoch Parameters`
   - `Label Route`
   - `Meta Level`
   - `Target Definition`
   - `Evidence`
3. 下列内容均属于本条所称模糊占位符或模糊写法：
   - `Needs verification`
   - `TBD`
   - `task-dependent`
   - `see Target Definition`
   - `Variable`
   - `N/A`
   - `unknown`
   - 带 `*` 或其他未定义不确定标记的参数写法
   - 其他不能直接指导实现的空泛描述
4. 若缺乏足够依据填写明确值，则该任务不得保留为 `Classical Task`，应降级为 `Potential Task`、标记为需重审，或直接删除。
5. LLM 与人类审核员均可以运用认知判断，为 `Classical Task` 选择最合适的明确值。
6. 前款所称“最合适的明确值”，原则上按以下顺序优先选择：
   - 官方页面或官方说明中的推荐值
   - 明确使用该数据集的参考文献中的实际取值
   - 审核员或 LLM 基于专业知识给出的合理取值
7. 如所选取值并非直接由官方页面或文献逐字给出，应在 `Kernel Notes` 中简要说明判断依据。

### 第63条 `Potential Task` 适用情形

下列情形应写为 `Potential Task`：

1. 数据本身支持该任务，但外部证据不足。
2. 文献证明用了该数据集，但未能明确证明就是该任务。
3. 任务属于合理派生任务、推荐任务、工程任务，而非该数据集公认主任务。

### 第63条之一 `Potential Task` 的最低明确性要求

1. `Potential Task` 可以比 `Classical Task` 更保守，但仍应保持基本可读、可审、可落地。
2. 至少以下字段应给出明确合法值：`Task Type`、`Epoch Method`、`Label Route`、`Meta Level`。
3. 若某一 `Epoch Method` 的必需参数仍无法明确，不得使用 `or`、`task-dependent`、`see Target Definition` 等写法将多个方案揉成一个任务；应拆分为多个候选任务、降为审核备注，或直接删除。
4. 若任务仅代表“可能的研究方向”而尚不具备稳定标签来源或切窗定义，不应保留在 `Tasks Area`，应移至审核记录或 `Data Quality Notes`。

### 第64条 降级规则

当既有 `Classical Task` 不再满足第62条时，应当降级为 `Potential Task`，而非继续保留为 `Classical Task`。

### 第65条 删除规则

当任务所依赖的标签、事件或派生路径在数据中不存在，且无法通过可信规则稳定重建时，该任务应删除，不得保留。

### 第66条 并存规则

同一数据集可以同时存在多个 `Classical Task` 与多个 `Potential Task`，但每个任务都应有独立且自洽的成立依据。


### 第三节 Task Type、Epoch Method 与参数

### 第67条 `Task Type`

`Task Type` 仅允许取以下值：

1. `classification`
2. `regression`

### 第68条 `Epoch Method`

`Epoch Method` 仅允许取以下值：

1. `epoch_by_event_hdf5`
2. `epoch_by_long_event_hdf5`
3. `epoch_by_segmentation_hdf5`

### 第69条 `Epoch Parameters` 一般规则

`Epoch Parameters` 至少应提供当前 `Epoch Method` 所必需的参数。

### 第70条 `epoch_by_event_hdf5` 参数要求

使用 `epoch_by_event_hdf5` 时，应至少提供：

1. `tmin`
2. `tmax`
3. `target_events`

### 第71条 `epoch_by_long_event_hdf5` 参数要求

使用 `epoch_by_long_event_hdf5` 时，应至少提供：

1. `tmin`
2. `tmax`
3. `overlap`
4. `target_events`

### 第72条 `epoch_by_segmentation_hdf5` 参数要求

使用 `epoch_by_segmentation_hdf5` 时，应至少提供：

1. `segment_length`
2. `overlap`

### 第73条 参数来源

`Epoch Parameters` 应优先由 `Evidence` 支持；如证据未给出完整参数，人类审核员与 LLM 可以在保守原则下选择最合适的明确值。其优先顺序原则上为：

1. 官方页面或官方说明中的推荐值。
2. 明确使用该数据集的参考文献中的实际取值。
3. 审核员或 LLM 基于专业知识给出的合理取值。

所填写参数应为可直接实现的明确值，不得以模糊占位符替代。


### 第四节 Target Events、Label Route 与 Meta Level

### 第74条 `target_events` 合法来源

`Epoch Parameters` 中的 `target_events` 只能来自 `Event Structure` 中明确存在且 `Type = event` 的条目。

### 第75条 禁止虚构 `target_events`

若某个任务的 `target_events` 在 `Event Structure` 中不存在，或对应条目的 `Type = admin`，则该任务不得视为有效任务。

### 第76条 人工审核处置

人工审核时，如 `target_events` 与 `Event Structure` 不一致，应作以下处置之一：

1. 微调为真实存在的标签。
2. 在提交说明中标记”需重解析”。
3. 删除该任务。

### 第77条 `Label Route`

1. `Label Route` 描述该任务监督信号（supervision signal）的来源与存储形式，仅允许以下三个值：
   - `event` — 监督信号来自事件流（`### Event Structure` 中的离散事件，无论原始存储为 annotation 还是 stim channel）。
   - `misc` — 监督信号是数值型或连续型量，存储于 misc channel（对应 `### MISC Label Summary`）。
   - `info` — 监督信号来自文件级受试者或设备属性（对应 `### Info`，如性别、年龄、分组等）。
2. `Label Route` 与 `target_events`、`Target Definition` 应保持一致：
   - `Label Route = event` 时，`Target Definition` 使用 `Event → y` 映射表。
   - `Label Route = misc` 时，`Target Definition` 描述 MISC 字段到标量目标的对应关系。
   - `Label Route = info` 时，`Target Definition` 使用 `Info Field / Value → y` 映射表（见第77条之二）。
3. 离散分类标签不应仅因实现方便而改写为 `misc`。
4. 若任务属于例外情形，应在 `Kernel Notes` 中说明理由。

### 第77条之一 epoch-level scalar regression 与计数目标

1. 当任务目标是”每个 epoch 输出一个标量或计数”，如 `response_time`、评分、密度、持续时长或生理指标时，`Label Route` 应为 `misc`。
2. 切窗锚点事件（用于 epoch 边界定位的事件）与监督信号路由相互独立；`Label Route = misc` 不妨碍 `Epoch Method` 使用事件锚定方式。
3. 若该标量可由原始表格或 companion file 直接读取，标为 `raw`；若需配对、聚合或换算，标为 `super`。
4. 采用本条任务时，`### MISC Label Summary` 必须说明字段来源、单位、对齐方式与必要的派生逻辑。

### 第77条之二 `Label Route = info` 时的 `Target Definition` 格式

1. 当 `Label Route = info` 时，`Target Definition` 表格应采用以下格式：

   | Info Field | Value | y | Meaning |
   |---|---|---|---|
   | `subject_sex` | Male | 0 | Male subject |
   | `subject_sex` | Female | 1 | Female subject |

2. `Info Field` 列的取值必须与 `### Info` 表中已登记的字段名称一致。
3. 若该字段在 `### Info` 中的 `Completeness` 为 `missing` 或 `incomplete`，该任务不得成立为 `Classical Task`，至多为 `Potential Task`，并应在 `Kernel Notes` 中说明数据缺失情况。

### 第78条 `Meta Level`

1. `Meta Level = raw` 表示该任务依赖原始标签即可实现。
2. `Meta Level = super` 表示该任务依赖额外派生、连接或转换后的标签。
3. 若标签需进行事件配对、类别折叠、主体信息映射、标准体系映射或连续变量计算，应标为 `super`。


### 第五节 Evidence 与 Kernel Notes

### 第79条 `Evidence`

1. `Evidence` 展示支持任务成立或参数选择的外部依据。
2. `Classical Task` 必须提供 `Evidence`。
3. `Potential Task` 可以提供 `Evidence`，但非强制。
4. `Classical Task` 的 `Evidence` 应为可定位、可识别的具体来源，不得仅写空泛占位符。
5. 如 DOI 未识别但官方页面、比赛页面或正式文献页面可定位，应直接写该具体来源，而不应写“DOI 未知”等模糊表述。

### 第80条 证据审查重点

人类审核员与 LLM 应重点判断以下问题：

1. 证据是否明确使用了该数据集。
2. 证据是否明确支持当前任务，而非仅支持相近任务。
3. 证据中的标签定义是否与公开数据一致。

### 第81条 幻觉防范

由于 LLM 可能在论文理解中产生幻觉，凡无法确认“确实使用了该数据集且确实支持该任务”的，应降级或删除，而非强行保留 `Classical Task`。

### 第82条 `Kernel Notes`

`Kernel Notes` 用于说明代码实现时必须额外注意的事项，包括但不限于：

1. 标签映射细节。
2. 文件级上下文依赖。
3. 外部表格解析要求。
4. 事件配对与窗口生成规则。
5. 需排除的管理员事件或伪事件。


## 第十一章 Data Quality Notes Area

### 第83条 一般要求

`Data Quality Notes Area` 应采用分点形式，记录数据质量问题、资料冲突、解析风险与使用限制。

### 第84条 必写情形

下列情形应尽量在本区说明：

1. 官方资料与实际数据不一致。
2. 数据缺漏、排除、空文件、缺失事件、缺失字段。
3. 被试数、文件数、通道数、采样率与官方表述不一致。
4. 事件语义依赖文件级上下文。
5. 某些任务仅在子集文件中成立。

### 第85条 立场要求

若存在官方资料与真实数据不一致，应明确说明本文档的立场为“以真实数据为准”。

### 第86条 穷尽义务

本区不要求穷尽全部问题，但人类审核员与 LLM 应尽力记录对任务有效性有实质影响的质量问题。


## 第十二章 References Area（废止）

### 第87条 废止说明

1. `References Area` 属于早期文档版本的遗留栏目。
2. 现行版本的 `analysis_minimax_v2.md` 原则上不应保留独立的 `References Area`。
3. 与具体任务直接相关的来源，应写入对应 `Classical Task` 或 `Potential Task` 下的 `Evidence`。
4. 与数据冲突、质量问题或审核裁定相关的来源，应写入对应说明段落或审核记录，而不再单独汇总为 `References Area`。

### 第88条 过渡规则

1. 既有历史文档可暂时保留 `References Area`。
2. 一旦对文档进行实质性修订，应同步删除该栏目，除非维护者另有明确要求。
3. LLM 在生成新版本文档时，不应主动新增 `References Area`。


## 第十二章之一 STIM Label Summary 废止过渡规则

### 第88条之一 废止说明

1. `STIM Label Summary` 属于 v0.1 版本的遗留栏目，自 v0.2 起废止。
2. 所有来自 trigger/stim channel 的离散事件，应统一在 `Event Structure` 表格中登记，`Type` 字段按 `event` 或 `admin` 判定。
3. `Event Structure.Type` 中废止的 `short`、`long`、`rest` 三类也自 v0.2 起停止使用，对应信息由 `Tasks Area` 的 `Epoch Method` 字段承载。

### 第88条之二 存量文档过渡

1. 既有历史文档中已存在的 `STIM Label Summary` 暂不强制立即迁移。
2. 一旦对文档进行实质性修订，应将 `STIM Label Summary` 中的离散事件条目迁移至 `Event Structure`，并删除 `STIM Label Summary` 节。
3. `Event Structure` 中原有 `Type` 为 `short`、`long`、`rest` 的条目，在实质性修订时应统一改写为 `event`；`admin` 类型保持不变。
4. LLM 审核脚本在生成或修订新版本文档时，不应主动新增 `STIM Label Summary` 节，也不应在 `Event Structure.Type` 中使用废止的枚举值。


# 第三编 附则

## 第十三章 占位词、格式与文风

### 第90条 允许占位词

在无法确定具体信息时，可以使用以下占位词：

1. `Needs verification`
2. `Variable`
3. `N/A`
4. `null`

前款占位词原则上不得用于 `Classical Task` 的关键字段。

### 第91条 原样保留原则

原始事件名、原始码值、原始标签若可直接使用，应优先原样保留，不应为了语言美观而任意重命名。

### 第92条 文风要求

文档应尽量保持技术化、事实化、可执行化。避免使用宣传性、夸张性或无法验证的结论性表述。


## 第十四章 审核动作分类

### 第93条 审核动作类型

后续人工审核与 LLM 审核可采用以下动作类别：

1. `保留`
2. `修正`
3. `降级`
4. `删除`
5. `标注 Needs verification`
6. `标注需重解析`
7. `标注需修正 kernel`

### 第94条 动作适用原则

1. 能通过字段微调解决者，优先 `修正`。
2. 任务证据不足但数据支持者，优先 `降级`。
3. 标签来源不存在或无法稳定重建者，应 `删除`。
4. 解析链路存在明显程序性问题者，应标注 `需重解析` 或 `需修正 kernel`。

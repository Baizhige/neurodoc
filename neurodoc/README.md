# NeuroDoc

`neurodoc/` 是 EEG 数据集 kernel 文件与 `analysis.md` 文档的自动生成引擎。它通过 LLM 驱动的多阶段 pipeline 完成：分析参考文献 → 合成任务定义 → 生成/验证 kernel 代码 → 运行 EEGUnity 扫描 → 写出最终文档。

---

## 目录结构

```
neurodoc/
├── README.md                   # 本文件
├── api.py                      # NeuroAudit 对外稳定接口（唯一允许外部 import 的入口）
├── paths.py                    # 全局路径常量（NEURODOC_DIR、RUNTIME_DIR 等）
│
├── generate.py                 # CLI：并行生成多个数据集的 kernel + analysis.md
├── detect.py                   # CLI：对 analysis.md 和 kernel 执行语义规则校验
├── full_scan.py                # CLI：用已有 kernel 重新扫描并刷新 analysis.md
├── upgrade.py                  # CLI：通过 [to_agent:...] 标签增量更新 kernel/文档
│
├── llm_adapter.py              # LLM 配置规范化 + HTTP 重试适配器（Anthropic / OpenAI）
├── scan_engine.py              # EEGUnity 扫描核心：机器配置、locator 缓存、扫描执行、
│                               #   analysis.md merge 逻辑、采样计划
│
├── pipeline/                   # 生成 pipeline 各阶段实现
│   ├── runner.py               # Pipeline 类：主编排器，管理 10 个顺序阶段
│   ├── budget.py               # LLM 调用次数预算追踪（Budget / BudgetExhausted）
│   ├── context_builder.py      # 阶段 1：加载已有 kernel、参考文献、BIDS sidecar
│   ├── ref_analyzer.py         # 阶段 2：LLM 从论文/文档中提取关键信息
│   ├── task_synthesizer.py     # 阶段 3：LLM 可行性判断
│   ├── scan_bridge.py          # 阶段 3.5 / 6：调用 scan_engine 执行 EEGUnity 扫描
│   ├── event_annotator.py      # 阶段 3b：P3a+P3b 事件语义独立标注
│   ├── task_synthesizer_v2.py  # 阶段 4：aggregate → fill → gate → repair 任务合成
│   ├── kernel_builder.py       # 阶段 5：生成 kernel.py + 静态/运行时校验（最多 3 次）
│   ├── reconcile.py            # 阶段 6.5：剔除幻觉任务；最多 1 次 kernel patch + 重扫
│   ├── doc_writer.py           # 阶段 7：写出最终 analysis.md
│   └── file_scan_result_builder.py  # 从扫描结果构建 File Scan Result section
│
├── kernels/                    # 版本控制的 kernel 实现（400+ 个数据集）
│   ├── KERNEL_RULEBOOK.md      # Kernel 编写标准（中文，详细规范）
│   ├── bids.py                 # 通用 BIDS 解析器（fallback）
│   ├── openneuro.py            # OpenNeuro 通用解析器（fallback）
│   ├── openneuro_ds*.py        # OpenNeuro 数据集专用 kernel（200+ 个）
│   ├── openneuro_specific/     # 复杂情况的专用 kernel 子目录
│   ├── bcic_*.py               # BCI Competition 数据集
│   ├── physionet_*.py          # PhysioNet 数据集
│   ├── tuh_eeg_*.py            # TUH EEG 数据集
│   ├── figshare_*.py           # Figshare 数据集
│   ├── zenodo_*.py             # Zenodo 数据集
│   └── skills/                 # Kernel 合成用 LLM prompt 模板（SKILL_*.md）
│
├── rulebook/
│   └── semantic_rules.yaml     # detect.py 使用的语义校验规则
│
├── dataset_api/                # PyTorch Dataset 封装（读取 EEGUnity 生成的 HDF5）
│   ├── base.py                 # BaseHDF5Dataset：惰性文件句柄、epoch 截断/补齐
│   ├── factory.py              # build_dataset_from_task()：按 label_route 分发 Dataset
│   ├── event_dataset.py        # EventDataset（label_route = event）
│   ├── misc_dataset.py         # MISCDataset（label_route = misc）
│   ├── info_dataset.py         # InfoDataset（label_route = info）
│   └── tests/                  # Dataset 单元测试
│
└── tools/
    ├── migrate_to_v3.py        # 文档版本迁移工具（升级到 v3 格式）
    └── __init__.py
```

---

## 运行时目录（不受版本控制）

机器相关的运行时状态统一存放在 `Script/neurodoc_runtime/`（已 .gitignore）：

```
Script/neurodoc_runtime/
├── machine_config/     # 每台机器的 JSON 配置（LLM 密钥、数据集根目录、EEGUnity 路径）
├── locator_cache/      # EEGUnity locator CSV 缓存（按机器 ID 分目录）
├── progress/           # 每个数据集的 pipeline 进度 JSON（支持断点续跑）
├── evidence_cache/     # 事件标注的 LLM 缓存
├── logs/               # 每个数据集的运行日志
└── sandbox/            # kernel 代码运行时临时目录
```

---

## 输入与输出

| 类型 | 路径 |
|------|------|
| 原始 EEG 数据 | 在 `machine_config` 的 `dataset_roots` 中查找 |
| 参考文献 | `dataset_document/<dataset>/` 下的 PDF/TXT 文件 |
| 已有 analysis.md | `dataset_document/<dataset>/analysis.md` |
| **输出：kernel** | `neurodoc/kernels/<dataset>.py` |
| **输出：analysis.md** | `dataset_document/<dataset>/analysis.md` |

---

## CLI 入口点

### `generate.py` — 完整 pipeline（生成 kernel + analysis.md）

```bash
# 单个数据集
python -m neurodoc.generate --dataset openneuro_ds001784

# 多个数据集（并行，默认 4 workers）
python -m neurodoc.generate --dataset openneuro_ds001784 openneuro_ds002578 --workers 4

# 忽略已有进度，从头重跑
python -m neurodoc.generate --dataset openneuro_ds001784 --fresh

# 指定 machine_config
python -m neurodoc.generate --dataset openneuro_ds001784 --config path/to/config.json
```

完成后打印汇总表：`DATASET | STATUS | PHASE | BUDGET | KERNEL | TIME`。

支持 Ctrl-C 优雅暂停（进度已保存，下次可恢复）。

### `detect.py` — 语义规则校验

```bash
# 校验单个数据集
python -m neurodoc.detect --dataset openneuro_ds001784

# 校验所有数据集
python -m neurodoc.detect --all

# 只显示 error 级别
python -m neurodoc.detect --all --severity error

# 使用自定义 rulebook
python -m neurodoc.detect --dataset openneuro_ds001784 --rulebook custom.yaml
```

### `full_scan.py` — 用已有 kernel 重新扫描（不调用 LLM）

```bash
python -m neurodoc.full_scan --dataset openneuro_ds005505
python -m neurodoc.full_scan --dataset openneuro_ds005505 --workers 4
```

仅刷新 `File Scan Result` section 和 `Kernel Responsibilities` section，不改变任务定义。

### `upgrade.py` — 增量更新（通过 `[to_agent: ...]` 标签）

```bash
python -m neurodoc.upgrade --dataset openneuro_ds001784
```

读取 analysis.md 中的 `[to_agent: ...]` 指令，对 kernel 或文档执行局部 LLM 修改。

### `tools/migrate_to_v3.py` — 文档格式迁移

```bash
python -m neurodoc.tools.migrate_to_v3 --all --dry-run
python -m neurodoc.tools.migrate_to_v3 --dataset openneuro_ds001784
```

---

## Pipeline 阶段详解

`Pipeline.run()`（`pipeline/runner.py`）按序执行以下阶段，支持中途暂停后从断点恢复：

| # | 阶段名 | 模块 | 说明 |
|---|--------|------|------|
| 1 | `context` | `context_builder.py` | 加载已有 kernel、参考文献、BIDS sidecar、EEG header |
| 2 | `ref_analysis` | `ref_analyzer.py` | LLM 从论文/文档提取实验设计、事件、受试者信息 |
| 3 | `feasibility` | `task_synthesizer.py` | LLM 判断数据集是否可处理；不可行则写失败文档并退出 |
| 3.5 | `pre_scan` | `scan_bridge.py` | 用已有 kernel（或默认解析器）预扫描，获取事件 ID 预览 |
| 3b | `event_annotation` | `event_annotator.py` | LLM 独立标注每个事件 ID 的语义含义（P3a+P3b 模式）|
| 4 | `task_synthesis` | `task_synthesizer_v2.py` | LLM 合成任务：aggregate → fill → gate → repair |
| 5 | `kernel_loop` | `kernel_builder.py` | LLM 生成 kernel.py；静态检查 + 运行时校验；最多重试 3 次 |
| 6 | `scan` | `scan_bridge.py` | 用新 kernel 执行最终 EEGUnity 扫描；若事件为空则触发一次 patch |
| 6.5 | `reconcile` | `reconcile.py` | 剔除扫描结果中不存在的幻觉任务；最多 1 次 kernel patch + 重扫 |
| 7 | `doc_write` | `doc_writer.py` | 合成写出最终 analysis.md |
| — | `done` | — | 完成 |

**预算机制**：每次 LLM 调用消耗 1 个 budget 单位（默认总额 500）。budget 耗尽时触发 `BudgetExhausted`，尽力写出已有内容并保存进度。

---

## analysis.md 文档结构

每个数据集的 analysis.md 包含以下顶层 section（顺序固定，由 `detect.py` 的 `section_order` 规则校验）：

```markdown
## Paradigm           — 实验设计、受试者、事件语义描述
## File Scan Result   — 扫描结果：事件结构表、Info 表、MISC Label Summary
## Tasks              — 机器学习任务定义（可被 dataset_api 直接消费）
## Data Quality Notes — 数据质量问题备注（人工审核）
## Kernel Responsibilities — kernel 功能声明（自动维护）
```

文档头部元数据包含 `Status`（`wait_manual_review` / `completed` / 等）和 `Kernel SHA256`（用于检测 kernel 是否已更新）。

---

## dataset_api — PyTorch Dataset 封装

`dataset_api/` 提供从 HDF5（EEGUnity v2.0/v2.1 格式）直接构建 PyTorch Dataset 的接口。

```python
from neurodoc.dataset_api.factory import build_dataset_from_task

dataset = build_dataset_from_task(
    task=task_dict,     # 来自 analysis.md Tasks section 解析结果
    h5_path="data.h5",
    dry_run=False,
)
# dataset[i] -> (data: Tensor, label: Tensor, meta: dict)
```

**分发规则（`label_route` × `task_type`）：**

| label_route | task_type | 类 | 标签来源 |
|---|---|---|---|
| `event` | `classification` | `EventDataset` | `/epoch_meta/event_code` → `events_map` → int y |
| `event` | `regression` | `EventDataset` | `/epoch_meta/event_code` → float value |
| `misc` | `regression` | `MISCDataset` | `/misc_meta/<channel>` 单行 |
| `info` | `classification` | `InfoDataset` | `/source_meta/<group>/attrs[field]` → `info_map` → int y |
| `info` | `regression` | `InfoDataset` | `/source_meta/<group>/attrs[field]` → float |

---

## Kernel 规范

每个 kernel 是一个 Python 模块，暴露模块级 `KERNEL` 对象，兼容 EEGUnity 的 `UnifiedDataset.eeg_parser` 接口。核心职责：

1. **频道恢复**：将 `EEG-0` 形式的通用频道名还原为正确名称（如 `FC3`）
2. **元数据写入**：将年龄、性别、设备等写入 `raw.info["description"]`（JSON 格式）
3. **标签标准化**：
   - **raw meta**：原始事件码 → 可读标签的直接映射
   - **super meta**：语义派生标签（必须与 analysis.md 中的任务声明一致）
   - 多范式数据集：以范式 ID 前缀区分（如 `CLA: left hand MI`）

详见 [`kernels/KERNEL_RULEBOOK.md`](kernels/KERNEL_RULEBOOK.md)。

---

## 语义校验规则（detect.py）

`detect.py` 从 `rulebook/semantic_rules.yaml` 加载规则，支持四种规则类型：

- `pattern`：正则匹配
- `section_exists`：要求某个 section 存在
- `field_value`：提取字段值并验证合法值集合
- `cross_check`：自定义函数（20+ 个，用 `@_cc` 装饰器注册）

**关键 cross-check 示例：**

| 函数名 | 检查内容 |
|---|---|
| `section_order` | 顶层 section 是否按规定顺序出现 |
| `super_meta_consistency` | 任务的 Meta Level 是否与 Super Meta Required 一致 |
| `target_events_exist` | Target Definition 中的事件 ID 是否出现在 Event Structure 中 |
| `classification_y_zero_indexed_sequential` | 分类任务 y 值是否为 `{0, 1, …, N-1}` |
| `task_dataset_dispatchable` | 所有任务能否通过 `dataset_api.factory` 的 dry_run |
| `kernel_sha256_matches` | 文档内记录的 SHA256 是否与当前 kernel 文件一致 |
| `classical_task_evidence` | 每个 Classical Task 是否有非空 Evidence 字段 |

违规输出格式：
```python
{"dataset": str, "rule_id": str, "severity": "error|warning|info",
 "target": "analysis_md|kernel", "desc": str, "detail": str}
```

---

## scan_engine.py 职责

`scan_engine.py` 是一个职责较多的模块，目前承担：

- **机器身份**：`get_machine_id()` 基于主机名生成 12 位哈希
- **机器配置**：`load_machine_config()` / `save_machine_config()`（读写 `machine_config/<hash>.json`）
- **数据集路径查找**：`find_dataset_path()`（支持 `openneuro_` 前缀剥离）
- **Kernel 路径检测**：`detect_kernel_path()`（优先级：专用 kernel > 通用 fallback）
- **Kernel SHA256**：`get_kernel_sha256()`（跨平台 CRLF 规范化后哈希）
- **Locator 缓存**：CSV 格式，按机器 ID 和 kernel SHA256 分层存储
- **EEGUnity 扫描执行**：`run_full_scan()`，支持全量扫描和采样扫描
- **Subject 信息提取**：从 `raw.info["description"]` JSON 解析年龄、性别
- **MISC 频道检测**：`_extract_misc_channels()`，探测多文件后趋于稳定
- **analysis.md 合并**：`merge_scan_results()`，更新 Event Structure / Info / MISC 表
- **数据集列表**：`list_datasets()`，扫描 `dataset_document/` 并返回状态汇总
- **采样计划**：`prepare_sampling_plan()` / `build_sampling_prompt()`，为 LLM 辅助采样

---

## llm_adapter.py — LLM 适配器

支持 Anthropic 和 OpenAI 兼容接口，统一配置格式：

```python
from neurodoc.llm_adapter import resolve_llm_config, post_llm_json, call_llm_text

cfg = resolve_llm_config({
    "ANTHROPIC_BASE_URL": "https://...",  # 或 BASE_URL (OpenAI)
    "key": "sk-...",
    "model": "claude-opus-4-7",
})
# cfg["provider"] = "anthropic" | "openai"
# cfg["active_url"] = 最终请求 URL
```

**重试策略**：最多 5 次，遇 429/5xx 使用指数退避（5s × 2^n，最大 120s），遵守 `Retry-After` 头。

---

## NeuroAudit 集成接口

审计 UI（`neuroaudit/`）**只允许**从以下模块 import：

```python
import neurodoc.api      # check_analysis_text, load_rules, call_llm_text, ...
import neurodoc.paths    # NEURODOC_DIR, DATASET_DOCUMENT_DIR, RUNTIME_DIR, ...
import neurodoc.scan_engine  # list_datasets, run_full_scan, merge_scan_results, ...
```

不得直接 import `pipeline/` 内部模块。

`neurodoc.api` 当前暴露：

```python
check_analysis_text(text, dataset, kernel_text, severity_filter, rules)
load_rules(rulebook_path)
call_llm_text(config, messages)
post_llm_json(config, messages)
anthropic_to_openai_response(response)
resolve_llm_config(config)
```

---

## machine_config JSON 格式

```json
{
  "dataset_roots": ["/path/to/eeg_data"],
  "eegunity_path": "/path/to/eegunity",
  "python_env": "python3",
  "num_workers": 4,
  "budget": 500,
  "model": "claude-opus-4-7",
  "BASE_URL": "",
  "ANTHROPIC_BASE_URL": "https://...",
  "key": "sk-ant-..."
}
```

文件名格式：`<machine_id>.json`（machine_id = MD5(hostname + MAC)[:12]）。

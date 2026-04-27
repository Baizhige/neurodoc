# EEG Audit Tool

本地 Web 审查工具，用于编辑和验证 EEG 数据集的 `analysis.md` 文档，并通过多阶段 LLM 流水线自动生成任务定义（Tasks 章节）。

---

## 快速启动

```bash
cd /path/to/BIDS_description
pip install flask pymupdf beautifulsoup4 requests pyyaml
python app/server.py
# 浏览器打开 http://127.0.0.1:5000
```

依赖清单见 [requirements.txt](requirements.txt)。

---

## 文件说明

| 文件 | 说明 |
|---|---|
| [server.py](server.py) | Flask 后端，提供全部 REST API 和 LLM 调用逻辑 |
| [index.html](index.html) | 单页前端（SPA），包含所有 UI 和前端 JS 逻辑 |
| [template_checker.py](template_checker.py) | 文档结构检测器：校验 `analysis.md` 是否满足模板规范 |
| [template_spec.py](template_spec.py) | 机器可读的模板规范（章节名称、顺序、必须/禁止规则） |
| [rulebook.md](rulebook.md) | 文档撰写规则手册，在右侧面板展示供人工参考 |
| [config.json](config.json) | LLM 配置（首次保存时自动生成，不要手动提交 API key） |
| [skills/](skills/) | 每类数据集（Action/Output、Biological State 等）的专属提示词片段，在 Phase 2 时注入 LLM 上下文 |

| [detect.py](detect.py) | 语义规则检查器：对 analysis.md 运行跨字段一致性检查 |
| [llm_adapter.py](llm_adapter.py) | LLM HTTP 适配器：统一支持 OpenAI 协议和 Anthropic 协议 |
| [rulebook/semantic_rules.yaml](rulebook/semantic_rules.yaml) | 语义规则定义文件，由 detect.py 在启动时加载 |

---

## 界面用法

1. **左侧栏** — 列出所有含 `analysis.md` 的数据集目录，可按 Category 过滤。模板错误的数据集会标红。
2. **步骤条**（顶部）— 分 3 步浏览文档：
   - **Step 1: Meta / Paradigm** — 编辑 Category、Status 等元字段及 Paradigm 章节。
   - **Step 2: File Scan / Tasks** — 查看事件表（Event Structure）、MISC 标签、Info 表，并管理 Tasks。
   - **Step 3: DQN / Kernel** — 编辑 Data Quality Notes 和 Kernel Responsibilities。
3. **右侧面板** — 切换 Rulebook / LLM Chat / References 三个标签页。
4. **Save File** — 将当前编辑写回 `analysis.md`（保存前会重新运行模板检测，失败则拒绝保存）。
5. **Bulk LLM Fix**（顶部）— 对所有已加载的模板错误数据集批量调用 LLM 修复。

### References 标签页

在 File Scan / Tasks 步骤切换到 **References** 标签，可以：

- 查看 `<dataset>/references/` 目录下的参考文献列表（PDF / HTML / TXT / MD）。
- 点击 **Regenerate All Tasks** 启动完整的四阶段自动任务生成流程（详见下文）。
- 对单篇文献手动运行 Phase 0 / Phase 1 分析。

---

## LLM 配置

点击右上角 **Settings**，填写：

| 字段 | 说明 |
|---|---|
| `BASE_URL` | OpenAI 兼容端点，如 `https://api.openai.com/v1` |
| `ANTHROPIC_BASE_URL` | Anthropic 兼容端点，如 `https://api.anthropic.com` |
| `API Key` | 对应端点的 API 密钥 |
| `Model` | 模型名称，如 `gpt-4o`、`claude-opus-4-7` |

`BASE_URL` 和 `ANTHROPIC_BASE_URL` **只能配置其中一个**。配置保存至 `app/config.json`。

---

## 核心原理

### 一、文档结构检测原理

文档检测分两层，均在 `/api/template/check` 和 `/api/dataset/<name>` (PUT) 中触发：

**第一层：结构模板检测**（`template_checker.py` + `template_spec.py`）

`template_spec.py` 以 Python 列表形式声明规范：

```
必须章节（## 级，顺序固定）：
  Paradigm → File Scan Result → Tasks → Data Quality Notes → Kernel Responsibilities

File Scan Result 下必须的 ### 子章节（顺序固定）：
  Event Structure → MISC Label Summary（可选）→ Info

禁止章节：STIM Label Summary
```

`template_checker.py` 对 `analysis.md` 做如下检查：

1. **存在性** — 每个必须章节是否存在且不重复。
2. **顺序** — 章节出现顺序是否与规范一致。
3. **意外章节** — 是否有规范之外的 `##` 标题。
4. **子章节** — `## File Scan Result` 内的 `###` 子章节是否满足必须/可选/顺序要求。
5. **错位子章节** — 规范子章节是否出现在 `## File Scan Result` 之外。

检查结果为 `{"ok": bool, "errors": [...]}` 格式，直接反映在 UI 的红色警告徽章上。

**第二层：语义跨字段检查**（`eeg_kernel_agent/detect.py`）

服务器启动时加载 `eeg_kernel_agent/rulebook/semantic_rules.yaml`，注册一批以 `@_cc` 装饰的检查函数。`_run_semantic_checks()` 将 analysis.md 文本传入这些函数，返回违规列表。

Tasks 相关的语义规则示例：

| Rule ID | 说明 |
|---|---|
| `label_field_required_for_nonevent` | Route = misc/info 时必须有 Label Field |
| `label_field_absent_for_event` | Route = event 时禁止出现 Label Field |
| `misc_classification_forbidden` | misc 路由只能是 regression |
| `classification_task_has_multiple_classes` | 分类任务必须有 ≥2 个 y 值 |
| `segmentation_requires_empty_target_events` | segmentation 方法要求 target_events = [] |
| `target_def_schema_matches_route` | Target Definition 表头必须匹配 Route × Task Type |
| `epoch_parameters_complete` | Epoch Parameters 必须包含该方法的所有必填键 |

两层检查共同决定文档是否合规。任意一层有错误，UI 即标红并阻止保存。

---

### 二、参考文献识别原理（Phase 0 + Phase 1）

在 References 标签页，系统对每篇参考文献执行两阶段识别。

**Phase 0 — 文献标识符提取**（`/api/refs/phase0/<dataset>`）

目标是从一篇文献文件中提取 DOI / URL / arXiv ID，采用三级降级策略：

```
1. 文件名解码
   paper_10_1109_tnsre_2021_xxx.pdf  →  解析为 DOI 10.1109/tnsre.2021.xxx
   （命中即直接返回，无需读取文件内容）

2. 正则扫描（读取文件前 ~6000 字符）
   优先匹配 \b(10\.\d{4,}/...)  → DOI
   其次匹配 arXiv:\d{4}.\d{4,}  → arXiv
   再次匹配 https?://...        → URL
   （DOI 命中即返回）

3. LLM 兜底（仅当正则未找到 DOI 时）
   将前两页文本送入 LLM，要求返回 {"ref", "ref_type", "title"}
```

**Phase 1 — 相关性分类 + 任务提取**（`/api/refs/phase1/<dataset>`）

将完整文献文本（最多 100,000 字符）+ 数据集 analysis.md 摘要（最多 5,000 字符）+ Phase 0 得到的 ref 标识符一起发送给 LLM（`_P1_SYSTEM` 提示词），要求 LLM 同时完成两项判断：

- **Task A — 相关性分类**：`relevant` / `partial` / `irrelevant` / `uncertain` / `junk`
- **Task B — 任务字段提取**：`task_type`、`n_classes`、`paradigm`、`epoch_method_hint`、`epoch_params`、`target_events`、`label_mapping`、`meta_level` 等

LLM 返回 JSON，服务器解析后将 `ref`（LLM 提取 > Phase 0 > 文件名）写回响应。前端按 `classification` 过滤，保留 `relevant` 和 `partial` 的结果进入下一阶段。

---

### 三、Regenerate All Tasks 原理

点击 **Regenerate All Tasks** 触发前端函数 `regenTasksFromRefs()`，它串联调用后端接口，完整流程如下：

```
┌─────────────────────────────────────────────────────────┐
│  GET /api/refs/<dataset>                                 │
│  → 获取 references/ 目录下的所有文献文件列表             │
└───────────────────────┬─────────────────────────────────┘
                        │ files[]
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 0（并发 4 路）                                     │
│  POST /api/refs/phase0/<dataset>  × N files              │
│  → 为每篇文献提取 DOI/URL/arXiv（三级降级策略）          │
└───────────────────────┬─────────────────────────────────┘
                        │ p0Results{}
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 1（并发 4 路）                                     │
│  POST /api/refs/phase1/<dataset>  × N files              │
│  → 每篇文献：相关性分类 + 任务字段提取                   │
│  → 过滤保留 relevant + partial                           │
└───────────────────────┬─────────────────────────────────┘
                        │ extractions[] (relevant + partial)
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 2（服务器端串行执行两步）                          │
│  POST /api/tasks/phase2/<dataset>                        │
│                                                          │
│  ├─ Phase 2-1：Epoch 对齐分析                            │
│  │   LLM 接收：analysis.md + 技能指南 + Phase-1 提取结果  │
│  │   输出：alignment、cue_duration、每范式推荐参数        │
│  │   (tmin/tmax/overlap/segment_length/epoch_method)     │
│  │                                                        │
│  └─ Phase 2-2：Tasks 章节合成 + 自检                     │
│      LLM 接收：analysis.md + 原始 Event ID 列表 +         │
│               Phase-1 提取 + Phase-2-1 对齐结果 +        │
│               技能指南（按数据集 Category 注入）          │
│      输出：完整 "## Tasks" Markdown 文本                  │
│            + num_classical_tasks / num_potential_tasks    │
│            + self_check_notes（自检摘要）                 │
└───────────────────────┬─────────────────────────────────┘
                        │ tasks_section
                        ▼
        前端替换 rawContent 中的 ## Tasks 章节
        重新渲染 Task 卡片，标记文档为 dirty（未保存）
```

**Phase 2-1** 的核心任务是判断数据集事件标记代表刺激 onset 还是 offset，并为每个范式推荐 epoch 参数。其结果作为 Phase 2-2 的输入，确保生成的 Epoch Parameters 有据可依。

**Phase 2-2** 的 LLM 在写完 Tasks 后会立即执行内置自检（Self-Check A–F），验证：
- `target_events` 中的 ID 来自 Event Structure 表中的真实 ID
- 每个 Classical Task 至少有一条 Evidence（含 ref）
- Epoch Parameters 包含方法所要求的所有必填键
- 没有重复任务（相同 epoch + label 组合）
- H1–H7 硬性规则全部满足

服务器在将结果返回前还会调用 `_check_tasks_fragment()` 对生成的 Tasks 片段再次运行语义检查，将任何剩余违规以 `semantic_errors` 字段附在响应中供前端展示。

---

## API 参考

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/datasets` | 列出所有数据集及状态/模板校验结果 |
| GET | `/api/dataset/<name>` | 读取指定数据集的 analysis.md |
| PUT | `/api/dataset/<name>` | 保存 analysis.md（模板校验失败则拒绝） |
| POST | `/api/template/check` | 对任意文本执行结构 + 语义双层检测 |
| GET | `/api/rulebook` | 获取 rulebook.md 内容 |
| GET/POST | `/api/config` | 读取/保存 LLM 配置 |
| POST | `/api/llm` | 透传 LLM 请求（用于 UI 的 Chat 功能） |
| POST | `/api/template/fix_with_llm/<name>` | LLM 自动修复模板错误 |
| GET | `/api/refs/<name>` | 列出 references/ 目录下的文件 |
| POST | `/api/refs/phase0/<name>` | Phase 0：提取文献 DOI/URL |
| POST | `/api/refs/phase1/<name>` | Phase 1：相关性分类 + 任务提取 |
| POST | `/api/tasks/phase2/<name>` | Phase 2：epoch 对齐 + Tasks 章节合成 |

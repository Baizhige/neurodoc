# openneuro_ds001849 — Quality Review

**Source PR**: #5 (`analysis_minimax_v2.md`) — reviewer 旧版
**LLM pipeline result**: `wait_manual_review`, 16 rules OK, 17m39s
**Verdict**: ⚠️ **严重分歧 — 需要管理员介入；审核员描述与数据完全不符**

---

## 0. Ground truth from raw dataset

Files under `/home/public/eeg_dataset/openneuro_raw/ds001849/sub-*/eeg/`：

```
sub-XX_task-tmseegrest_acq-{dlpfc,m1,ppc}{active,sham}_eeg.{set,fdt}
```

- `dataset_description.json`: `"Name": "RS_TMSEEG_Data"`（Resting-State TMS-EEG）
- Task name 为 `tmseegrest` （TMS-EEG resting）
- Acquisition: 3 靶点（DLPFC / M1 / PPC）× 2 条件（active / sham），全部在受试者 **静息** 状态下记录

这是一个**静息态 TMS-EEG** 数据集（NIH, Wassermann lab），不是心理任务数据集。

---

## 1. Paradigm 对比

| 来源 | 描述 |
|---|---|
| **LLM** | ✅ "Resting-state EEG data recorded in conjunction with Transcranial Magnetic Stimulation (TMS). Subjects were at rest (no active task) while TMS pulses were delivered; the R128 marker … does not indicate a meaningful task event." |
| **Reviewer (PR#5)** | ❌ "Participants performed a variety of internal mental tasks across multiple runs. **Mental Arithmetic**, **Relaxation**, **Internalized Speech**, **Breath Sensing**." |

**结论**：Reviewer 描述完全错误 — 没有任何证据支持 4 类心理任务的存在（文件名、dataset_description、通道结构全部指向静息 TMS-EEG）。Reviewer 很可能把 ds001849 与另一个"internal mental states"数据集搞混了（例如 Kaggle Inria 或 ds002338 之类）。

---

## 2. Tasks 对比

| 来源 | Task 数 | 内容 |
|---|---|---|
| **LLM** | 0 | 正确：只有 R128 一种 trigger，无有效类别标签，**无法构造任务** |
| **Reviewer** | 1 | `Primary Task 1: Internal Mental State Classification`（4-class：Mental Arithmetic / Relaxation / Internalized Speech / Breath Sensing） |

**结论**：Reviewer 的任务定义基于错误的 paradigm 假设，无法在真实数据中落地。LLM 判断 "0 tasks" 是符合数据事实的。

---

## 3. LLM 可合理补充的任务建议

基于实际数据结构（3 靶点 × 2 条件），可以**合理地**推理出以下任务（若将来 epoch by TMS pulse）：

1. **Active vs Sham** 分类（2-class，label route = info 或 event-by-acquisition）
2. **Stimulation Site** 分类（3-class：DLPFC / M1 / PPC）
3. **TMS-evoked Potential (TEP) regression** on pulse-locked epochs

但当前 R128 是单一 trigger、无 meta 标签，所以 LLM 选择 "0 task" 也是正确的 — 要从 filename 的 `acq-*` 段反推条件，需要 kernel 层面支持 filename parsing。**这是链路的增强点，不是 bug**。

---

## 4. 最终判定

- **Paradigm**：LLM ✅ 正确；Reviewer ❌ 错误 → **管理员建议**：拒绝 PR#5 的 ds001849 部分，因为其 paradigm 与数据不符
- **Tasks**：LLM 0 task 是数据驱动的合理结果；Reviewer 的 1 task 基于错误 paradigm，不可采纳
- **可能的增强**：kernel 支持从 `acq-dlpfcactive/m1sham/...` 文件名派生 stimulation-site × condition 的 info label，但这是后续迭代，不影响当前判定

> **行动项**：建议核查 PR#5 的提交者——他们是否把 ds001849 误认为另一个心理任务数据集？

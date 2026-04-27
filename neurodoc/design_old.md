# auto_eeg V3 Pipeline Design

**Version**: 3.0 (draft)  
**Status**: Design phase — not yet implemented  
**Purpose**: Eliminate LLM hallucination through structural isolation, achieve rulebook compliance, and maximize per-prompt control via fine-grained decomposition.

---

## 1. Core Principles

### 1.1 Evidence Chain Hierarchy

Evidence is consumed in strict priority order. A lower-tier source never overrides a higher-tier one:

| Tier | Source | Examples |
|------|--------|---------|
| ① | BIDS sidecar files | `participants.tsv`, `events.tsv`, `events.json`, `eeg.json`, `README` |
| ② | Reference papers in `references/` | PDF, HTML, TXT extractions |
| ③ | EEGUnity scan output | Event counts, file count, channel count |
| ④ | LLM inference | Only for fields without tier ①–③ evidence |

### 1.2 Isolation Principle

The key anti-hallucination design decision: **Event Meaning inference is isolated from reference papers**.

- The prompt that assigns `Meaning` to event IDs sees **only** `events.tsv` and `events.json`.  
- It does **not** see paper content, paradigm descriptions, or prior BCI knowledge cues.
- This prevents the documented failure mode where strong LLM priors (e.g. "event codes 1-4 = left/right/feet/tongue in BCIC IV 2a") override the actual data evidence.

### 1.3 Granularity Principle

Each LLM request has exactly one focused job. No mega-prompts. A typical full run uses:

- 1 call per reference × 2 passes (classify + deep extract) = 2N calls
- 1 call for event Meaning (isolated)
- 1 call for epoch alignment per paradigm
- 1 call per candidate task for drafting
- 1 call for task cross-check
- 1 call per triggered Data Quality rule
- 1 call for Paradigm section

For 5 references and 2 tasks: approximately **20–25 LLM calls** total.

### 1.4 Programmatic Locking

Fields that can be determined programmatically are **never** delegated to LLM:

- Event IDs and counts: from EEGUnity scan (locked)
- File count, channel count, sampling rate: from locator cache (locked)  
- Kernel Responsibilities: always computed from Tasks section
- Manual Review: left blank — human only

---

## 2. Pipeline Phases

### Phase Overview

The pipeline runs in **two loops**. Loop 1 establishes a runnable base kernel and confirms event IDs. Loop 2 synthesizes documentation and closes with a full scan that produces the authoritative File Scan Result.

```
┌─ LOOP 1: Kernel Foundation ──────────────────────────────────────────┐
│  P0    Context + locator cache check (0 LLM)                         │
│  P1    Reference classification (N LLM)                              │
│  P2    Reference deep extraction (≤N LLM)                            │
│  P3a   Evidence collection agent — data_dir only (3–20 LLM)          │
│  P3b   Event annotation, isolated (1 LLM)                            │
│  P4    Provisional File Scan Result — from cache/evidence (0 LLM)    │
│  P5a   Kernel context flags (0 LLM)                                  │
│  P5b   Channel rename decision, conditional (0–1 LLM)                │
│  P5c   Annotation strategy, conditional non-BIDS (0–1 LLM)          │
│  P5d   Kernel assembly (1 LLM)                                       │
│  P5e   Kernel review (1 LLM)                                         │
│  P6    Quick scan — 3–5 sample files (0 LLM; +1 P5-fix if fail)      │
└──────────────────────────────────────────────────────────────────────┘
         ↓ event IDs confirmed; kernel runs
┌─ LOOP 2: Documentation + Full Scan ──────────────────────────────────┐
│  P7    Epoch alignment (1–3 LLM)                                     │
│  P8a   Per-task draft (M LLM)                                        │
│  P8b   Task cross-check (1 LLM)                                      │
│  P9    Paradigm section (1 LLM)                                      │
│  P10a  Data quality stat extraction (0 LLM)                          │
│  P10b  Data quality note generation (0–6 LLM)                        │
│  P11   Kernel responsibilities (0 LLM)                               │
│  P12   Provisional analysis.md assembly (0 LLM)                      │
│  P13   Super meta kernel update, conditional (0–1 LLM)               │
│  P14   Quick scan verify super meta, conditional (0 LLM; +1 if fail) │
│  P15   Full scan, max 3× (0 LLM; +1 P5-fix per fail)                 │
│  P16   Final File Scan Result — real counts + super meta events (0)  │
│  P17   Final analysis.md assembly (0 LLM)                            │
└──────────────────────────────────────────────────────────────────────┘
         ↓ OUTPUTS
         analysis.md  (File Scan Result = actual kernel scan)
         neurodoc/kernels/<dataset_name>.py  (tested, runnable)
```

**P5-fix** (Kernel Error Diagnosis): triggered on P6 or P15 failure — 1 LLM call to diagnose the traceback and produce a minimal patch. See §11 P5-fix prompt design.

**Locator cache check (pre-Loop 1)**:
- If `locator_cache/<sha256>/<dataset>.csv` exists → use directly, skip full scan
- If base locator exists (any prior scan) → use as base, only run kernel-specific scan for new SHA256
- If nothing exists → proceed with Phase 0 evidence; full scan required in Loop 2

**Full scan budget**: maximum 3 runs. Each run updates `locator_cache/<new_sha256>/<dataset>.csv`. Quick scans never write to locator cache.

**Final guarantee**: `analysis.md` File Scan Result is written only from the output of a full scan run with the dataset's kernel. The File Scan Result and Tasks section must be mutually consistent (event IDs in Target Definition must match Event Structure rows).

---

### Phase 0: Context Collection (Programmatic)

**Inputs**: dataset directory, optional `data_dir` path to raw EEG files  
**Outputs**: `context` dict  
**LLM calls**: 0

Steps:
1. Read existing `analysis.md` (may be empty or stale)
2. Extract trusted URLs from `analysis.md` (kept even if content is regenerated)
3. Build directory tree (max depth 3)
4. List `references/` files
5. Find existing kernel in `neurodoc/kernels/`
6. Load `KERNEL_RULEBOOK.md`, SKILL files, example kernels
7. Load `neuroaudit/rulebook.md` for compliance rules
8. Detect dataset category from `analysis.md` `**Category**` field; load category SKILL

If `data_dir` is provided:
- Detect format type (bids / mat / bdf / edf / other)
- Read BIDS sidecar files (tier-① evidence):
  - `participants.tsv` → parse N, age range, sex counts
  - `task-*_events.json` or first `*_events.json` found → column definitions
  - `task-*_events.tsv` or per-task sample → first 12 rows including header  
    *(one sample per unique task-* name, max 3 tasks)*
  - First `*_eeg.json` → device/amplifier metadata
  - `README` / `README.md` → up to 3000 chars
- Sample EEG file headers via MNE (no preload): channel names, sfreq, duration, annotations

---

### Phase 1: Reference Classification (N × 1 LLM calls)

**Inputs**: one reference file at a time, analysis.md excerpt  
**Outputs**: per-paper `classification` + `ref` (DOI/URL/arXiv)  
**LLM calls**: N (one per reference file)

For each file in `references/`:

**1a — Ref Extraction (sub-pass, may skip LLM if regex succeeds)**

1. Try to extract DOI/URL/arXiv from filename pattern (`paper_10_1109_...`)
2. If not found, try regex scan of first 6000 chars of text
3. If still not found, call LLM with first ~6000 chars (P0-style prompt: extract ref + title only)

**1b — Relevance Classification (1 LLM call per paper)**

Prompt sees:
- Dataset name and analysis.md excerpt (Paradigm section only, ≤3000 chars)
- Full reference text (≤100 000 chars)

Output JSON:
```json
{
  "classification": "relevant|partial|irrelevant|uncertain|junk",
  "cot_reasoning": "...",
  "ref": "10.xxxx/...",
  "ref_type": "doi|url|arxiv|none",
  "title": "..."
}
```

Cached to `auto_eeg/ref_cache/<dataset>/<filename>.json`.  
Skip LLM call if cache hit and `classification` is already set.

---

### Phase 2: Reference Deep Extraction (≤N LLM calls)

**Inputs**: one reference file per call, only for `relevant` or `partial` papers  
**Outputs**: per-paper task extraction struct  
**LLM calls**: ≤N (skips `irrelevant`/`junk`)

For each `relevant` or `partial` paper:

**2a — Task Extraction (1 LLM call per paper)**

Prompt sees:
- Dataset name + event structure from EEGUnity scan (IDs + counts only, no Meaning yet)
- Reference text
- Category SKILL guide

Output JSON (extends neuroaudit/server.py P1 schema):
```json
{
  "supports_task": true,
  "task_type": "classification|regression|segmentation|none",
  "n_classes": 0,
  "paradigm": "...",
  "epoch_method_hint": "event-based|long-event|segmentation|unclear",
  "epoch_params": "...",
  "target_events": [],
  "label_mapping": "...",
  "meta_level": "raw|super|unclear",
  "super_meta_note": "...",
  "evidence_desc": "..."
}
```

**IMPORTANT**: At this stage, `target_events` uses paper terminology (e.g. "left hand MI"), not raw IDs. Mapping to raw IDs happens in P8a.

System prompt includes: "Identify which sub-dataset in this paper matches dataset '{name}' by subject count, recording setup, or dataset ID. Extract only details for that sub-dataset. Do not apply paradigm details from one sub-dataset to another."

---

### Phase 3: Event Structure Annotation (Agent Loop — ISOLATED)

**Inputs**: `data_dir` only  
**Outputs**: `Meaning`, `Event Type`, `Meta Level` for each raw event ID  
**LLM calls**: Phase 3a evidence collection: min 3, max 20 turns; Phase 3b annotation: 1 turn  
**Path constraint**: `data_dir` only — NO access to `references/`, `analysis.md`, or any file outside the raw data directory

**Critical isolation**: This entire phase (3a + 3b) must NOT see:
- Reference paper content
- `analysis.md` or existing `## Paradigm` text
- Category SKILL guide or any BCI-related context

---

#### Phase 3a: Evidence Collection Agent (3–20 LLM turns)

The agent is given the `data_dir` directory tree and locator file list, then iteratively requests file reads until it declares sufficient coverage of all detected groupings.

**Turn 0 — Grouping Survey**

LLM receives:
- Raw event IDs and counts (from EEGUnity scan)
- Directory tree of `data_dir` (max depth 4)
- Locator CSV content: file list with sub/ses/task/run columns
- Programmatic summary: unique session names, unique task names, unique run labels
- Initial events.tsv samples already collected in Phase 0 (one per unique task name)

LLM outputs:
```json
{
  "turn_summary": "Detected 2 sessions (ses-01, ses-02) and 2 tasks (task-mi, task-nf). Initial sample only covers ses-01/task-mi.",
  "groups_identified": ["ses-01/task-mi", "ses-01/task-nf", "ses-02/task-mi", "ses-02/task-nf"],
  "groups_covered": ["ses-01/task-mi"],
  "groups_missing": ["ses-01/task-nf", "ses-02/task-mi", "ses-02/task-nf"],
  "coverage_sufficient": false,
  "next_reads": [
    {
      "tool": "read_tsv",
      "path": "sub-001/ses-01/eeg/sub-001_ses-01_task-nf_events.tsv",
      "params": {"nrows": 20}
    },
    {
      "tool": "read_json",
      "path": "task-nf_events.json",
      "params": {}
    }
  ]
}
```

**Turns 1–N — Read-Assess-Continue Loop**

Each turn:
1. Runner executes all `next_reads` instructions using the allowed tool set
2. Returns results (or error messages) to LLM
3. LLM assesses coverage and decides whether to continue

On error: LLM sees the error traceback and may adjust parameters or try a different path.  
On success: LLM updates coverage map and issues next reads if needed.

`coverage_sufficient: true` is only accepted after **turn ≥ 3**.  
Loop terminates at **turn 20** regardless (forced exit).

**Allowed Tool Set (structured JSON commands only):**

| Tool name | Operation | Key params |
|-----------|-----------|------------|
| `read_tsv` | `pandas.read_csv(sep='\t')` | `nrows`, `usecols` |
| `read_json` | `json.load()` | — |
| `read_eeg_header` | `mne.io.read_raw_*(preload=False)` | — (returns ch_names, sfreq, annotations sample) |
| `read_mat` | `scipy.io.loadmat()` | `variable_names` |
| `read_text` | `open().read()` for .txt/.md | `max_chars` |
| `read_pdf` | `fitz.open()` for .pdf within data_dir | `page_range`, `max_chars` |

All paths are resolved relative to `data_dir`. Any path traversal outside `data_dir` is rejected by the runner.

**Grouping detection heuristics** (programmatic pre-computation shown to LLM):
- Sessions: folder names matching `ses-*`
- Tasks: BIDS `task-*` part of filenames
- Runs: `run-*` part of filenames
- Non-BIDS formats: top-level subfolders, filename suffix patterns

**Evidence cache**: all read results persisted to `auto_eeg/evidence_cache/<dataset>/phase3_turn<N>.json`. Patch runs can replay from cache without re-reading files.

---

#### Phase 3b: Event Annotation (1 LLM call)

Triggered after 3a declares `coverage_sufficient: true` (or turn 20 forced exit).

LLM receives:
- All events.tsv samples and events.json files collected in 3a
- All other read results from 3a (EEG headers, README, etc.)
- Raw event IDs and counts from EEGUnity scan

System instruction:
```
You are an event annotation specialist. Your ONLY job is to assign Meaning,
Event Type, and Meta Level to each raw event ID based on the evidence collected.

Rules:
- Event Type: ONLY "event" or "admin"
  - "event": experimental stimulus, response, or imagery cue
  - "admin": system marker, session boundary, calibration, trigger sync
- Meta Level: "raw" if label is directly usable; "super" if derivation needed
- Meaning: describe what ACTUALLY happens at this trigger per the BIDS data.
  Do NOT apply BCI conventions or prior paradigm knowledge.
  If events.tsv shows value=3 → "task", Meaning = "Task phase onset"
  A marker mapping to "rest"/"ready"/"task"/"interval" is a TRIAL PHASE, not a class label.
- If the same event ID has different meanings across sessions/tasks, document both.
- confidence: "confirmed" (events.tsv direct mapping) / "inferred" / "unclear"

Output ONLY valid JSON:
{
  "annotations": [
    {
      "event_id": "event_1",
      "event_type": "event|admin",
      "meta_level": "raw|super",
      "meaning": "...",
      "confidence": "confirmed|inferred|unclear",
      "session_task_scope": "all | ses-01/task-mi only | ..."
    }
  ],
  "notes": "..."
}
```

Output stored as `event_annotations`. Used in Phase 4 (locked into Event Structure table) and P8a (constrains task synthesis).

---

### Phase 4: Provisional File Scan Result (Programmatic)

**Inputs**: locator cache (if available) or Phase 3 evidence; event annotations from Phase 3b  
**Outputs**: provisional `## File Scan Result` (event IDs confirmed; counts may be estimates)  
**LLM calls**: 0

Source priority for event IDs and counts:
1. `locator_cache/<sha256>/<dataset>.csv` — use directly if exists
2. Any base locator CSV — use for file paths and basic metadata
3. Phase 3a evidence (events.tsv samples) — derive event IDs; counts from Phase 0 EEGUnity scan

Event IDs are locked from Phase 3b annotations. Counts marked with `*` if not yet from full scan.  
This section is updated in Phase 4f after full scan completes.

The Event Structure table is assembled programmatically:

| Column | Source |
|--------|--------|
| Event ID | EEGUnity scan (locked) |
| Count (total) | EEGUnity scan (locked) |
| Type | Phase 3 LLM annotation (`event` or `admin` only) |
| Meta Level | Phase 3 LLM annotation |
| Meaning | Phase 3 LLM annotation |

The `### Info` table:

| Field | Source | Priority |
|-------|--------|----------|
| `subject_age` | `participants.tsv` age coverage | tier ① → EEGUnity fallback |
| `subject_sex` | `participants.tsv` sex/gender column | tier ① → EEGUnity fallback |
| `device` | `eeg.json` Manufacturer field | tier ① → EEGUnity fallback |

Kernel SHA256 and EEGUnity version: from scan result (programmatic, locked).

---

### Phase 5: Base Kernel Generation (2–4 LLM calls)

Generates the base kernel that handles reading and annotation building. Does NOT include super meta enhancement (added later in Phase 13 if tasks require it).

**Inputs**: Phase 3b event annotations, EEG header sample, locator CSV sample, KERNEL_RULEBOOK, 3 example kernels  
**LLM calls**: 2–4

**P5a — Context Flags (Programmatic)**

Compute flags from available evidence:
- `needs_channel_rename`: EEG header has non-standard channel names AND evidence contains a reliable mapping
- `needs_annotation_build`: format is non-BIDS (no events.tsv found) — kernel must build annotations from stim channel
- `large_N`: participants N > 50 → use dynamic loading instead of hardcoded dict

**P5b — Channel Rename Decision** (1 LLM call if `needs_channel_rename`, else skip → see §11 P5b)

**P5c — Annotation Strategy** (1 LLM call if `needs_annotation_build`, else skip → see §11 P5c)

**P5d — Kernel Assembly** (1 LLM call → see §11 P5d)
- Metadata injection always included
- Channel rename section: only if P5b confirmed it needed
- Annotation building section: only if P5c provided code
- Super meta section: **omitted** at this stage
- Misc channel section: **omitted** at this stage

**P5e — Kernel Review** (1 LLM call → see §11 P5e)

---

### Phase 6: Quick Scan (Programmatic + optional 1 LLM call)

**Goal**: Verify the base kernel runs correctly on representative files before committing to full scan.

**Steps**:
1. Select 3–5 sample files covering unique (task, session) combinations
2. Load each file header via MNE; apply kernel via `kernel.apply(udataset, raw, row)`
3. Check: `raw.info["description"]` parseable JSON with `eegunity_description` key
4. Check: annotations present (for non-BIDS); event IDs match Phase 3b annotations
5. Pass → proceed to Loop 2
6. Fail → call **P5-fix** (error diagnosis + patch → see §11 P5-fix) → retry; max 2 retries before flagging

Quick scan **never** writes to locator cache.

---

> **Loop 1 exits here.** Event IDs are confirmed. Base kernel is runnable.  
> Loop 2 begins: documentation synthesis and final full scan.

---

### Phase 7: Epoch Alignment Analysis (1 LLM call per paradigm)

**Inputs**: event structure table (with Meaning from Phase 3), BIDS sidecars, Phase 2 extractions, SKILL guide  
**Outputs**: epoch alignment and tmin/tmax/method recommendation per paradigm  
**LLM calls**: 1–3 (one per distinct paradigm detected in Phase 2)

Prompt sees:
- Full event structure table including Meaning column
- `events.json` column definitions
- `eeg.json` device info
- Phase 2 task extraction summaries (epoch hints, paradigm descriptions)
- Category SKILL guide

Paradigm count determined from Phase 2 unique paradigm descriptions. If all papers describe the same paradigm: 1 call. If multiple paradigms: one alignment call per paradigm.

Output per paradigm:
```json
{
  "paradigm_label": "...",
  "alignment": "onset|offset|mixed|unclear",
  "cue_duration_s": null,
  "epoch_method": "epoch_by_event_hdf5|epoch_by_long_event_hdf5|epoch_by_segmentation_hdf5",
  "tmin": 0.0,
  "tmax": 4.0,
  "overlap": null,
  "segment_length": null,
  "target_event_ids": ["event_1", "event_2"],
  "reasoning": "..."
}
```

---

### Phase 8: Task Synthesis (M + 1 LLM calls)

**M**: number of candidate tasks identified across all Phase 2 extractions  
**LLM calls**: M (one per candidate task) + 1 (cross-check and deduplication)

#### P8a — Per-Task Draft (1 LLM call per candidate task)

Each call focuses on ONE task. Prompt sees:
- Dataset name and full event structure table (IDs + counts + Type + Meta Level + Meaning)
- Epoch alignment recommendation for this task's paradigm (from Phase 5)
- Phase 2 extractions for the papers supporting this specific task only
- Category SKILL guide
- Rulebook task format rules

System prompt enforces:
- `target_events` MUST use exact IDs from the Event Structure table
- `Meaning` values come from Phase 3 annotation — task synthesis must not reinterpret them
- If Phase 3 Meaning says "rest phase onset", this is a trial phase marker, not a class label

Output: a single task block in analysis.md format (Classical/Potential/Normal, Target Definition table, Evidence, Kernel Notes).

#### P8b — Task Cross-Check (1 LLM call)

After all per-task drafts: one consolidation call that:
- Detects duplicate tasks (same epoch+label combination)
- Checks all Classical Tasks have Evidence with real refs
- Verifies all `target_events` exist in the Event Structure table
- Checks task tier is justified by evidence level
- Preserves existing Potential Tasks from prior analysis.md if no new evidence changes them

Output: final `## Tasks` section string.

---

### Phase 9: Paradigm Section (1 LLM call)

**Inputs**: dataset directory info, BIDS README, Phase 2 paper paradigm descriptions, participants summary  
**Outputs**: `## Paradigm` paragraph  
**LLM calls**: 1

Prompt sees:
- Dataset name, year, participants summary (N, age range, sex counts from `participants.tsv`)
- BIDS README
- Phase 2 paradigm descriptions from relevant/partial papers
- `eeg.json` device info

Explicitly does NOT write File Scan Result, Tasks, or any programmatic fields.

---

### Phase 10: Data Quality Notes (Programmatic stats + K LLM calls)

**K**: number of triggered rule categories  
**LLM calls**: 0–6 (one per triggered category)

#### P10a — Programmatic stat extraction

Computed from EEGUnity scan result and BIDS sidecars:

| Stat | Trigger condition |
|------|-----------------|
| Event imbalance | max_count / min_count > 5 among task-type events |
| Missing events per file | any task event absent from >20% of files |
| File-level event variability | task events present in only a known subset of files |
| participants.tsv vs scan N mismatch | absolute difference > 1 |
| Sampling rate inconsistency | multiple sfreq values across files |
| Channel count inconsistency | files with different channel counts |
| Missing subject info | age or sex = "missing" after tier-① lookup |

#### P10b — Rule-triggered LLM calls

For each triggered category, one LLM call produces a single bullet point (1–3 sentences):

| Category | LLM prompt focus |
|----------|-----------------|
| Event imbalance | Describe ratio, name scarce events, recommend file filtering in kernel |
| Subset events | Which events appear in which subset; scope of task validity |
| N mismatch | State both counts, which is authoritative (tier ① wins) |
| SR/channel inconsistency | Affected files, impact on batch processing |
| Missing info | Impact on Classical Task eligibility per rulebook §78c |
| Paradigm-task conflict | Describe conflict between paper claims and events.tsv evidence |

---

### Phase 11: Kernel Responsibilities (Fully Programmatic)

**Inputs**: synthesized `## Tasks` section  
**Outputs**: `## Kernel Responsibilities` blockquote  
**LLM calls**: 0

Rules:
- **Super Meta Required**: scan all tasks for `Meta Level: super` → "Yes" if any found, "No" otherwise
- **Status**: always `wait_manual_review` for new/regenerated documents

Output format (rulebook-compliant):
```markdown
## Kernel Responsibilities

> **Super Meta Required**: Yes/No
> **Status**: wait_manual_review
```

No other fields. Kernel team adds implementation notes during development.

---

### Phase 12: Provisional Analysis.md Assembly (Programmatic)

**Inputs**: all section strings from Phases 5–9; provisional File Scan Result from Phase 4  
**Outputs**: provisional `analysis.md` (File Scan Result counts may be estimates marked `*`)  
**LLM calls**: 0

Section order (per rulebook):
1. Header line (Dataset, Year, URL, Category, Subjects, Files, Channels, SR, Manual Review)
2. `## Paradigm`
3. `## File Scan Result` (from provisional Phase 4 — counts marked `*` if not from full scan)
4. `## Tasks`
5. `## Data Quality Notes`
6. `## Kernel Responsibilities`

Header field sources:
- **Subjects**: N from `participants.tsv` (tier ①)
- **Files (Completed)**: from locator cache if available; else from Phase 3a directory count
- **Channels**: from locator cache or EEG header sample; "Variable" if inconsistent
- **Sampling Rate**: from locator cache or EEG header; "Variable" if inconsistent
- **Manual Review**: left **blank** — never "Pending" or any LLM-generated value

This output is intermediate. The final `analysis.md` is produced by Phase 17 after full scan.

---

### Phase 13: Super Meta Kernel Update (Conditional, 0–1 LLM call)

**Triggered if**: any task has `Meta Level: super`  
**Inputs**: finalized tasks from P8b; base kernel from P5d  
**LLM calls**: 0–1

If triggered:
1. Extract from task JSONs: `super_meta_qualifier` (which participants column, which event IDs to prefix)
2. Add to kernel: participants loading logic + annotation prefix injection for `_SUPER_META_TARGET_EVENTS`
3. This is a small targeted addition to the existing kernel — uses the P5d prompt with `super_meta_only: true` flag
4. P5e review skipped for small additions; P5-fix available if quick scan fails

If not triggered: kernel unchanged from P5d output.

---

### Phase 14: Quick Scan Verify Super Meta (Conditional, Programmatic)

**Triggered if**: Phase 13 made changes  
**Steps**: apply updated kernel to 3–5 sample files; confirm super meta event IDs (e.g. `HC-event_1`) appear in annotations  
Fail → P5-fix → retry

---

### Phase 15: Full Scan (Programmatic, max 3×)

**Inputs**: finalized kernel; dataset files  
**Outputs**: `locator_cache/<sha256>/<dataset>.csv` updated  
**LLM calls**: 0 per scan; +1 (P5-fix) if scan exposes kernel errors

Runs EEGUnity full locator scan with the final kernel applied. Updates locator cache under the new kernel SHA256.

Full scan outputs per file:
- Event IDs and counts (including super meta events if kernel adds them)
- Channel count, sampling rate, file size
- Completeness check result

**Retry logic**:
- Scan #1: after P6 quick scan passes and Phase 12 provisional output is ready
- Scan #2: if scan #1 reveals kernel errors (P5-fix patches kernel, re-scan)
- Scan #3: final retry if scan #2 still has issues
- After scan #3 fails: write `Status: wait_kernel_update` in Kernel Responsibilities; stop

---

### Phase 16: Final File Scan Result (Programmatic)

**Inputs**: full scan output from Phase 15  
**Outputs**: final `## File Scan Result` with real counts and super meta events  
**LLM calls**: 0

Replaces provisional Phase 4 output with actual full scan data:
- Event counts are now accurate totals across all files
- Super meta events (if any) added as new rows in Event Structure table with `Meta Level: super`
- `*` markers removed from all count fields
- Header fields (Files Completed, Channels, SR) updated from full scan

---

### Phase 17: Final Analysis.md Assembly (Programmatic)

**Inputs**: final File Scan Result from Phase 16; all other sections unchanged from Phase 12  
**Outputs**: final `analysis.md`  
**LLM calls**: 0

Replaces the provisional File Scan Result section with the Phase 16 output. All other sections (Paradigm, Tasks, Data Quality Notes, Kernel Responsibilities) carry over unchanged from Phase 12.

**Final consistency check (programmatic)**:
- Every `target_events` entry in every task appears as an event ID row in File Scan Result
- Super meta events in Tasks also appear in Event Structure
- If mismatch found: flag in Data Quality Notes; set `Status: wait_manual_review` (already set)

> **Loop 2 exits here. Pipeline complete.**  
> Both outputs are now available: `analysis.md` + `neurodoc/kernels/<dataset_name>.py`

---

## 3. Run Modes

### Quick Run

For iterative testing and fast validation. Skips slow/expensive steps.

Phases executed: 0, 1 (classify only, no deep extract), 3a, 3b, 4, 9, 11, 12  
LLM calls: N + 2  
Output: Paradigm + File Scan Result (with annotated event Meanings) + Kernel Responsibilities  
No Tasks section generated.  
Use case: verify event annotation is correct and paradigm is coherent before committing to full run.

### Full Run

Complete pipeline including kernel generation and test.

Phases executed: 0–17  
LLM calls: ~2N + M + 10 + kernel (2–5)  
Output: complete `analysis.md` + `neurodoc/kernels/<dataset_name>.py`  
Use case: production document generation.

### Patch Run

For updating specific sections of an existing document without full regeneration.

Available patches:
- `--patch info`: P0 + P4 Info table only (participants.tsv fix, 0 LLM calls)
- `--patch events`: P0 + P3a (agent loop, 3–20 calls) + P3b (1 call) + P4 Event Structure; replays from evidence_cache if available (0 new reads, 1 annotation call)
- `--patch tasks`: P7 + P8 only, preserves Paradigm and File Scan (M+2 LLM calls)
- `--patch quality`: P10 only (K LLM calls)
- `--patch paradigm`: P9 only (1 LLM call)
- `--patch kernel`: P5a–P5e + P6 only, re-generates kernel from existing analysis.md (2–5 LLM calls)

---

## 4. LLM Call Summary Table

| Phase | Call | Job | Sees | Does NOT see |
|-------|------|-----|------|-------------|
| P1 (1a opt.) | 1 per ref | Extract DOI/ref | First 6000 chars of paper | — |
| P1 (1b) | 1 per ref | Classify relevance | Paradigm excerpt, full paper | events.tsv details |
| P2 | 1 per relevant/partial ref | Extract task struct | Paper text, event IDs (no Meaning), SKILL | Meaning annotations |
| **P3a** | **3–20 (agent loop)** | **Evidence collection** | **data_dir files only via tool calls** | **Papers, analysis.md, SKILL** |
| **P3b** | **1** | **Annotate event Meaning** | **All 3a evidence** | **Papers, analysis.md, SKILL** |
| P5b | 1 (conditional) | Channel rename decision | Header channel names, evidence cache | Papers, tasks |
| P5c | 1 (conditional) | Annotation building code | Format, event IDs, stim channel evidence | Papers, tasks |
| P5d | 1 (always) | Full kernel assembly | Tasks, event structure, participants, RULEBOOK, 3 examples | Raw paper text |
| P5e | 1 (always) | Kernel review | Generated kernel, tasks | Papers |
| P5-fix | 1 (conditional) | Error diagnosis + patch | Kernel code, traceback, sample row | Papers |
| P7 | 1 per paradigm | Epoch alignment | Event table with Meaning, P2 hints, SKILL | Raw paper text |
| P8a | 1 per candidate task | Draft task JSON struct | Event table + Meaning, this task's P2, alignment | Other tasks' P2 |
| P8b | 1 | Cross-check all tasks | All task JSONs | Raw paper text |
| P9 | 1 | Write Paradigm section | README, P2 paradigm descs, participants summary | Event structure |
| P10b | 1 per triggered rule | Write quality note bullet | Computed stats, specific context | All other phases |

**Example: 5 references, 2 tasks, 2 quality triggers, 5-turn evidence collection, simple BIDS kernel**  
- Ref work: 5 (classify) + 3 (deep extract) = 8  
- Event annotation: 5 (collection) + 1 (annotation) = 6  
- Epoch alignment: 1  
- Task drafts: 2 + 1 (cross-check) = 3  
- Paradigm: 1  
- Quality notes: 2  
- Kernel: 0 (channel) + 0 (annotation) + 1 (assembly) + 1 (review) = 2  
- **Total: ~23 calls**

**Worst case (20 refs, 20 collection turns, 5 tasks, 5 quality notes, non-BIDS + super meta kernel, 1 error)**:  
- ~70 (docs) + 5 (kernel) = ~75 calls — within 100-prompt budget

---

## 5. Task Construction Rules

### 5.1 Label Route Decision

Label Route describes **where the supervision signal (y) comes from**, not how the EEG is epoched.

| Label Route | Signal source | Typical epoch method |
|-------------|--------------|---------------------|
| `event` | Event ID in the event stream — y is determined by which trigger fired | `epoch_by_event_hdf5` or `epoch_by_long_event_hdf5` |
| `misc` | Auxiliary column in a file-level sidecar (condition flag, response column, discrete subject attribute embedded in a per-trial table) | Any |
| `info` | Subject-level attribute from `participants.tsv` or an external lookup table (age, sex, diagnosis, group) | Usually `epoch_by_segmentation_hdf5`; `epoch_by_event_hdf5` if epoching within a known event window |

Key distinction between `misc` and `info`:
- `misc`: the y value varies **trial-by-trial** within a single recording, sourced from a column in the file itself
- `info`: the y value is **constant per subject** across the whole recording, sourced from participants.tsv

### 5.2 Meta Level Decision

Meta Level describes whether the label can be read off directly (`raw`) or requires a derivation step (`super`).

| Meta Level | Meaning | Example |
|------------|---------|---------|
| `raw` | y is directly readable from the source (event ID → integer, participants.tsv column → integer) | MI left/right directly from event codes; sex M/F directly from participants.tsv |
| `super` | y requires joining, folding, mapping, or computing across sources | Healthy-MI vs Patient-MI requires joining event stream with participants.tsv diagnosis column; age regression requires reading a float from external table |

**Common combinations:**

| Label Route | Meta Level | Scenario |
|-------------|-----------|---------|
| `event` | `raw` | Standard ERP/MI: y comes directly from trigger value |
| `event` | `super` | Same task, but class label folds multiple event codes (e.g. left-hand + right-hand → "limb MI" vs "feet-tongue MI") |
| `info` | `raw` | Classify subjects by sex or diagnosis group — label read directly from participants.tsv column |
| `info` | `super` | Classify MI epochs by diagnosis, requiring event-based epoching then joining subject label from participants.tsv — derivation required at kernel level |
| `misc` | `raw` | Trial-level condition column in a sidecar CSV maps 1:1 to class label |
| `misc` | `super` | Trial-level scores that need thresholding or normalization to produce a discrete y |

If **Super Meta Required = Yes**, the kernel must implement the join/derivation logic, and `Kernel Notes` must document the derivation precisely.

### 5.3 Target Definition Table Formats

#### For `event` and `misc` Label Routes:

| Event | y | Meaning |
|-------|---|---------|
| `event_1` | 0 | Left-hand motor imagery cue |
| `event_2` | 1 | Right-hand motor imagery cue |

#### For `info` Label Route (uses Info Field column per rulebook §77):

| Info Field | y | Meaning |
|-----------|---|---------|
| `subject_sex = M` | 0 | Male subject |
| `subject_sex = F` | 1 | Female subject |

Or for segmentation + subject diagnosis:

| Info Field | y | Meaning |
|-----------|---|---------|
| `diagnosis = HC` | 0 | Healthy control |
| `diagnosis = MDD` | 1 | Major depressive disorder patient |

### 5.4 Task Construction Examples

The following examples show complete task blocks for the LLM to use as reference. Each example is a **distinct scenario** — the LLM must match the pattern that fits the evidence.

---

**Example A — Classical Task, event + raw, epoch_by_event**

```markdown
### Classical Task 1: Four-class Motor Imagery Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`event_1`, `event_2`, `event_3`, `event_4`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_1` | 0 | Left-hand motor imagery cue |
  | `event_2` | 1 | Right-hand motor imagery cue |
  | `event_3` | 2 | Feet motor imagery cue |
  | `event_4` | 3 | Tongue motor imagery cue |
- **Evidence**:
  - DOI: `10.xxxx/...` — 4-class MI paradigm (left/right/feet/tongue), epoch_by_event tmin=0s tmax=4s, cue onset alignment confirmed.
- **Kernel Notes**: Alignment = cue ONSET. Admin events (event_5 feedback, event_6 session) excluded from target_events.
```

---

**Example B — Potential Task, info + raw, epoch_by_segmentation (subject-level)**

```markdown
### Potential Task 1: Patient vs Healthy Control Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_segmentation_hdf5`
- **Epoch Parameters**: segment_length = 4.0 s, overlap = 2.0 s
- **Label Route**: `info`
- **Meta Level**: raw
- **Target Definition**:
  | Info Field | y | Meaning |
  |-----------|---|---------|
  | `diagnosis = HC` | 0 | Healthy control |
  | `diagnosis = MDD` | 1 | Major depressive disorder patient |
- **Evidence**:
  - (No direct reference — inferred from participants.tsv which contains `diagnosis` column with HC/MDD values)
- **Kernel Notes**: y is assigned per-subject from participants.tsv `diagnosis` column. Sliding window segmentation applied to full recording. No event alignment used.
```

---

**Example C — Classical Task, info + super, epoch_by_event (MI epochs labeled by diagnosis)**

```markdown
### Classical Task 2: Diagnosis Classification from Motor Imagery Epochs
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`event_1`, `event_2`]
- **Label Route**: `info`
- **Meta Level**: super
- **Target Definition**:
  | Info Field | y | Meaning |
  |-----------|---|---------|
  | `diagnosis = HC` | 0 | Healthy control (applies to all epochs of that subject) |
  | `diagnosis = MDD` | 1 | MDD patient (applies to all epochs of that subject) |
- **Evidence**:
  - DOI: `10.xxxx/...` — Used MI epochs to classify HC vs MDD; tmin=0s tmax=4s, event-based epoching, subject label from clinical diagnosis.
- **Kernel Notes**: Super Meta Required. Event-based epoching uses event_1/event_2 to locate MI windows; y is NOT from event IDs but from participants.tsv `diagnosis` joined by subject_id. Derivation: `y = participants_df.loc[subject_id, 'diagnosis'].map({'HC': 0, 'MDD': 1})`.
```

---

**Example D — Potential Task, event + raw, binary rest-vs-task (trial-phase paradigm)**

```markdown
### Potential Task 1: Binary Task-State vs Rest Classification
- **Task Type**: classification
- **Epoch Method**: `epoch_by_event_hdf5`
- **Epoch Parameters**: tmin = 0.0 s, tmax = 4.0 s, target_events = [`event_1`, `event_3`]
- **Label Route**: `event`
- **Meta Level**: raw
- **Target Definition**:
  | Event | y | Meaning |
  |-------|---|---------|
  | `event_1` | 0 | Rest/baseline period onset |
  | `event_3` | 1 | Task period onset |
- **Evidence**:
  - (Inferred from events.tsv: value=1→rest, value=3→task — no direct paper reference found)
- **Kernel Notes**: event_2 (ready cue) and event_4 (interval) are trial phase markers excluded from classification. Alignment = phase onset. Verify task duration is consistent across files before setting tmax.
```

---

### 5.5 Super Meta Event Naming Convention

When a kernel needs to synthesize subject-level or group-level labels into the event stream, it creates **super meta events** by augmenting base event IDs with a qualifier prefix. The naming convention is:

```
<qualifier>-<base_event_id>
```

The qualifier encodes the grouping dimension:

| Grouping dimension | Qualifier source | Example |
|-------------------|-----------------|---------|
| Subject attribute | participants.tsv column value | `HC-event_1`, `MDD-event_1` |
| Session identifier | BIDS `ses-*` label | `ses01-event_1`, `ses02-event_2` |
| Paradigm / experiment group | dataset-specific group label | `paradigm_A-event_1`, `exp1-event_2` |
| Sex / demographic | participants.tsv sex/age group | `male-event_1`, `female-event_1` |

Rules:
- Use lowercase with underscores for qualifier values
- Keep base_event_id exactly as it appears in the Event Structure table
- If multiple qualifiers apply, chain them: `HC-ses01-event_1`
- The kernel code comment must document the derivation and source (tier ①)

**Target Definition can fold super meta events into coarse or fine-grained tasks:**

Example — multi-group MI dataset (diagnosis × MI class):

| Event | y | Meaning |
|-------|---|---------|
| `HC-event_1` | 0 | Healthy control, left-hand MI |
| `HC-event_2` | 1 | Healthy control, right-hand MI |
| `MDD-event_1` | 2 | MDD patient, left-hand MI |
| `MDD-event_2` | 3 | MDD patient, right-hand MI |

Or folded into coarse group classification:

| Event | y | Meaning |
|-------|---|---------|
| `HC-event_1`, `HC-event_2` | 0 | Healthy control (all MI classes combined) |
| `MDD-event_1`, `MDD-event_2` | 1 | MDD patient (all MI classes combined) |

Example — multi-paradigm dataset (figshare_largemi, 5 paradigms):

| Event | y | Meaning |
|-------|---|---------|
| `paradigm_A-event_1` | 0 | Paradigm A, left-hand MI |
| `paradigm_A-event_2` | 1 | Paradigm A, right-hand MI |
| `paradigm_B-event_1` | 2 | Paradigm B, left-hand MI |
| ... | ... | ... |

Or collapsed to paradigm-level:

| Event | y | Meaning |
|-------|---|---------|
| `paradigm_A-event_*` | 0 | All events from Paradigm A |
| `paradigm_B-event_*` | 1 | All events from Paradigm B |

This design allows one kernel synthesis pass to support multiple Target Definition configurations, each becoming a separate task in the analysis.md.

**Continuous subject-level labels** (e.g. age regression, clinical scores) are NOT encoded as super meta events. Instead, the kernel encodes them as a `misc` channel value (constant per file, derived from participants.tsv). Label Route = `misc`, Meta Level = `super`.

**Info table stays fixed** at exactly 3 fields: `subject_age`, `subject_sex`, `device`. The `info` Label Route is reserved for tasks where y comes directly from these 3 standard fields without derivation.

### 5.6 Task Construction is Structured, Not Free-form

P8a LLM calls output a **structured JSON** that is assembled into the task block programmatically, not written as free text. This ensures format compliance.

P8a output schema:
```json
{
  "task_tier": "Classical|Normal|Potential",
  "task_name": "Four-class Motor Imagery Classification",
  "task_type": "classification|regression|segmentation",
  "epoch_method": "epoch_by_event_hdf5|epoch_by_long_event_hdf5|epoch_by_segmentation_hdf5",
  "tmin": 0.0,
  "tmax": 4.0,
  "overlap": null,
  "segment_length": null,
  "target_events": ["event_1", "event_2"],
  "label_route": "event|misc|info",
  "meta_level": "raw|super",
  "target_definition": [
    {"key": "event_1", "y": 0, "meaning": "Left-hand motor imagery cue"},
    {"key": "event_2", "y": 1, "meaning": "Right-hand motor imagery cue"}
  ],
  "evidence": [
    {"ref": "10.xxxx/...", "evidence_desc": "..."}
  ],
  "kernel_notes": "..."
}
```

The runner converts this JSON into the markdown task block using a fixed template. The LLM never writes raw markdown for the task section.

---

## 6. Kernel Code Comment Standard

When a kernel maps event IDs to labels, the remapping source must be annotated in a comment (Option B: kernel code comments):

```python
# Remapping source: events.tsv (tier-① BIDS sidecar)
# value=1 → "rest"     : rest/baseline period onset
# value=2 → "ready"    : readiness cue onset
# value=3 → "task"     : task period onset (classification target)
# value=4 → "interval" : inter-trial interval
EVENT_MAP = {1: "rest", 2: "ready", 3: "task", 4: "interval"}

# Remapping source: DOI 10.1038/s41597-023-02260-6 Table 1
# event_1 → left hand MI, event_2 → right hand MI
LABEL_MAP = {"event_1": 0, "event_2": 1}
```

Valid remapping source strings:
- `events.tsv (tier-① BIDS sidecar)` — highest priority
- `events.json (tier-① BIDS sidecar)`
- `README (tier-① BIDS sidecar)`
- `DOI 10.xxxx/... <section/table reference>`
- `Manual review — <reviewer initials> <date>`

---

## 7. Rulebook Compliance Checklist

All generated documents must satisfy:

| Rule | Field | Constraint |
|------|-------|------------|
| §61–62 | Event Type | Only `event` or `admin`; `short`/`long`/`rest` deprecated |
| §63–64 | Meta Level | `raw` or `super`; `super` requires derivation note in Kernel Notes |
| §65 | Label Route | `event` / `misc` / `info`; `Annotation`/`stim` deprecated |
| §66 | Epoch Method | Only the three `*_hdf5` variants |
| §78 | Task tier vs Info | subject_age/sex missing → max Potential Task (not Classical) |
| §79–81 | Evidence | Classical Task requires real ref; never fabricate DOI |
| §82 | Kernel Notes | Document label mapping details and excluded events |
| §83–86 | Data Quality Notes | Bullet form; imbalance, subset events, N mismatch |
| §87–88 | References Area | Do not create; references go in task Evidence only |
| §90 | Placeholders | Use `Needs verification`/`Variable`/`N/A`/`null` only |
| — | Manual Review | Leave **blank** in all LLM-generated documents |
| — | Kernel Responsibilities | Only `Super Meta Required` + `Status` fields |
| — | Status | LLM may only set `wait_kernel_update` or `wait_manual_review` |

---

## 8. Hallucination Prevention Architecture

### 7.1 Known Failure Mode: BCI Prior Knowledge Override

**Problem**: LLM associates event codes 1–4 with left/right/feet/tongue MI based on BCIC IV 2a training data. This prior overrides explicit events.tsv evidence (e.g. value=3→"task" reinterpreted as "feet MI"). Prompt rules adding "do not infer from BCI conventions" are insufficient — the LLM constructs rationalizations ("the BIDS sidecar captures a different event layer").

**V3 fix**: Phase 3 event annotation is structurally isolated from all paper content and paradigm context. Meaning is locked before any paper is read. P8a task synthesis receives the annotated Meaning and is explicitly told not to reinterpret it. The fix is architectural, not just prompt-level.

**Test case**: openneuro_ds004447 — events.tsv shows value=1→rest, value=2→ready, value=3→task, value=4→interval. V3 must produce a binary rest-vs-task paradigm, NOT 4-class MI.

### 7.2 Known Failure Mode: Multi-dataset Paper

**Problem**: A paper covers multiple datasets ("4 datasets"); LLM applies paradigm from dataset N to this dataset.

**V3 fix**: Phase 2a prompt explicitly requires: "Identify which sub-dataset matches '{name}' by subject count, recording setup, or dataset ID. Extract only details for that sub-dataset."

### 7.3 Known Failure Mode: Trial Phase vs Class Label

**Problem**: Trial phase markers (rest/cue/task/interval) are mistaken for class labels.

**V3 fix**: Phase 3 system prompt: "A marker that maps to 'rest', 'ready', 'task', 'interval' describes a trial phase — it is NOT a class label for classification. Report what it describes, not what class you think it represents."

### 7.4 Known Failure Mode: Prompt Rules Rationalized Away

**Problem**: Anti-hallucination prompt rules can be rationalized away if the LLM's prior is strong enough.

**V3 fix**: Structural isolation (7.1) is the load-bearing fix. Prompt rules are secondary defense. If the Meaning column already says "trial phase onset", a downstream prompt has no room to invent class labels — the upstream fact is already locked.

---

## 9. File Layout

```
auto_eeg/
  pipeline/
    context_builder.py     # Phase 0 — context collection (exists, V2)
    ref_analyzer.py        # Phases 1–2 — reference classify + extract (exists, needs split)
    event_annotator.py     # Phase 3 — ISOLATED event Meaning annotation (NEW)
    scan_assembler.py      # Phase 4 — File Scan Result assembly (NEW)
    epoch_analyzer.py      # Phase 5 — epoch alignment (exists as part of task_synthesizer)
    task_synthesizer.py    # Phases 6–7 — task drafting, cross-check, paradigm (refactor)
    quality_checker.py     # P10 — Data Quality Notes (NEW)
    doc_writer.py          # Phases 9–10 — assembly + kernel responsibilities (exists, V2)
    runner.py              # Orchestrator: quick/full/patch run modes (refactor)
  ref_cache/
    <dataset_name>/
      <filename>.json      # per-paper extraction cache (already used)
  evidence_cache/
    <dataset_name>/
      phase3_turn0.json    # initial grouping survey result
      phase3_turn1.json    # read results + coverage assessment
      ...
      phase3_annotation.json  # final Phase 3b annotation output
  progress/
    <dataset_name>.json    # pipeline progress tracker (already used)
  design.md                # this file
  patch_info_table.py      # batch patcher for pre-V2 Info tables (exists)
neurodoc/
  kernels/
    <dataset_name>.py      # generated kernel (P5d output)
```

---

---

## 10. Implementation Roadmap

Phase 3 (`event_annotator.py`) is the highest-priority change — it directly fixes the hallucination problem without requiring a full pipeline rewrite.

Recommended order:
1. **`event_annotator.py`** — isolated event annotation agent loop (P3a + P3b)
2. **`scan_assembler.py`** — programmatic Event Structure + Info table (P4)
3. **`quality_checker.py`** — programmatic stats + rule-triggered notes (P10a + P10b)
4. **`runner.py`** — quick/full/patch run modes + phase orchestration
5. **Refactor `task_synthesizer.py`** — per-task JSON drafts + cross-check (P8a + P8b)
6. **Update `doc_writer.py`** — programmatic Kernel Responsibilities (P11)
7. **`kernel_generator.py`** — P5a–P5e + P6: conditional decisions + assembly + scan test

Test dataset for each step: **openneuro_ds004447**  
Expected outcome after Phase 3 + 4: Event Structure shows "rest phase onset / readiness cue / task period onset / interval" — not MI class labels.  
Expected outcome after full V3: single binary paradigm (task vs rest), NOT 4-class MI.

---

## 11. Prompt Design Outlines

Each subsection below is the design specification for one LLM prompt. Sections cover: role, inputs, key rules, output schema, and anti-hallucination notes. These outlines are the authoritative reference for implementing the prompt strings in code.

---

### P1a — DOI / Reference Extraction

**Phase**: P1a (optional — only when filename and regex both fail)  
**Budget**: 1 call per paper that needs it  
**One-line job**: Extract the primary reference identifier and title from the first pages of a paper.

**System role**:
> You are a research paper metadata extractor. Extract the primary reference identifier and the paper title. Do nothing else.

**Input**:
- First ~6000 chars of the reference file (covers roughly 2 pages)

**Key rules**:
1. Prefer DOI (`10.XXXX/...`) over URL over arXiv ID
2. The DOI for THIS paper is usually in the header, footer, or abstract — not in the in-text citation list
3. arXiv format: `https://arxiv.org/abs/XXXX.XXXXX`
4. If nothing found, return empty strings — do not guess

**Output schema**:
```json
{
  "ref": "10.xxxx/... | https://... | arXiv:xxxx",
  "ref_type": "doi | url | arxiv | none",
  "title": "Full paper title as it appears on page 1"
}
```

---

### P1b — Reference Relevance Classification

**Phase**: P1b  
**Budget**: 1 call per reference file  
**One-line job**: Decide whether this paper uses this specific dataset and defines a concrete ML task.

**System role**:
> You are an EEG neuroscience analyst. Classify a single paper's relevance to a specific EEG dataset.

**Input**:
- Dataset name + Paradigm section from analysis.md (≤3000 chars)
- Full reference text (≤100 000 chars)

**Key rules**:
1. `relevant`: paper (a) explicitly uses THIS dataset AND (b) defines a concrete ML task with labels
2. `partial`: uses dataset but task definition vague/incomplete (no class count, no epoch params)
3. `irrelevant`: related topic but does NOT use this dataset
4. `uncertain`: insufficient text to judge
5. `junk`: clearly wrong domain
6. **Sub-dataset matching**: if paper covers multiple datasets, first identify which sub-dataset matches by N subjects, recording setup, or dataset ID. Only classify as `relevant` if the matching sub-dataset has a concrete task.
7. COT reasoning required (3–6 sentences) before classification

**Output schema**:
```json
{
  "classification": "relevant | partial | irrelevant | uncertain | junk",
  "cot_reasoning": "...",
  "ref": "DOI/URL/arXiv from P0 or extracted here",
  "ref_type": "doi | url | arxiv | none",
  "title": "..."
}
```

**Anti-hallucination**: Do not classify as `relevant` if the paper only mentions the dataset in passing without defining a task.

---

### P2 — Task Extraction from Reference

**Phase**: P2 (relevant and partial papers only)  
**Budget**: 1 call per relevant/partial paper  
**One-line job**: Extract structured task parameters from this paper for this specific dataset.

**System role**:
> You are an EEG task extraction specialist. Extract machine learning task parameters from a paper, strictly for the specified dataset.

**Input**:
- Dataset name + event IDs and counts (from EEGUnity scan — NO Meaning yet)
- Full reference text
- Category SKILL guide

**Key rules**:
1. Sub-dataset matching first: identify which sub-dataset in this paper is `{dataset_name}` and extract ONLY its parameters
2. `target_events`: use the paper's own terminology (e.g. "left hand MI"), not raw IDs — mapping happens later in P8a
3. `epoch_params`: quote exact values from paper if stated; "unclear" if not
4. `meta_level`: "super" only if the label requires derivation beyond reading the event ID
5. `super_meta_note`: for super, describe the derivation. For raw, leave empty.
6. `evidence_desc`: must cover — task type, class count, epoch window, any deviations

**Output schema**:
```json
{
  "supports_task": true,
  "task_type": "classification | regression | segmentation | none",
  "n_classes": 0,
  "paradigm": "brief description",
  "epoch_method_hint": "event-based | long-event | segmentation | unclear",
  "epoch_params": "tmin=0s tmax=4s (cue onset) | unclear",
  "target_events": ["left hand MI", "right hand MI"],
  "label_mapping": "left hand->0, right hand->1",
  "meta_level": "raw | super | unclear",
  "super_meta_note": "",
  "evidence_desc": "4-class MI (left/right/feet/tongue), epoch_by_event tmin=0s tmax=4s cue onset."
}
```

---

### P3a-0 — Evidence Collection: Grouping Survey (Turn 0)

**Phase**: P3a, first turn  
**Budget**: 1 call  
**One-line job**: Survey the dataset's file structure and identify all grouping dimensions that require separate event samples.

**System role**:
> You are a dataset structure analyst. Your job is to identify all grouping dimensions in this dataset and plan evidence collection to cover all groups. You only read files from the data directory.

**Input**:
- Raw event IDs and counts (from EEGUnity scan)
- Directory tree of `data_dir` (max depth 4)
- Locator CSV: file list with sub/ses/task/run columns
- Programmatic grouping summary: unique sessions, tasks, runs detected
- Initial events.tsv samples from Phase 0 (one per unique task name)

**Key rules**:
1. Identify grouping dimensions: sessions (`ses-*`), tasks (`task-*`), runs (`run-*`), or top-level subfolders for non-BIDS
2. Coverage goal: at least one events.tsv sample per unique (task, session) pair
3. Prioritize: root-level `task-*_events.tsv` > sub-level per task-session pair
4. Request `events.json` for any task not yet covered
5. `coverage_sufficient` MUST be false on turn 0 unless all groups are already covered by Phase 0 samples

**Output schema**:
```json
{
  "turn_summary": "Found 2 sessions × 2 tasks = 4 groups. Initial samples cover only ses-01/task-mi.",
  "groups_identified": ["ses-01/task-mi", "ses-01/task-nf", "ses-02/task-mi", "ses-02/task-nf"],
  "groups_covered": ["ses-01/task-mi"],
  "groups_missing": ["ses-01/task-nf", "ses-02/task-mi", "ses-02/task-nf"],
  "coverage_sufficient": false,
  "next_reads": [
    {"tool": "read_tsv", "path": "sub-001/ses-01/eeg/sub-001_ses-01_task-nf_events.tsv", "params": {"nrows": 20}},
    {"tool": "read_json", "path": "task-nf_events.json", "params": {}}
  ]
}
```

---

### P3a-N — Evidence Collection: Read-Assess-Continue (Turns 1–19)

**Phase**: P3a, turns 1 onward  
**Budget**: up to 19 additional calls  
**One-line job**: Assess new read results, update coverage map, decide whether to continue or declare sufficient.

**System role**:
> Same as P3a-0. You now receive the results of your previous read requests. Assess coverage and decide whether to continue collecting evidence or declare it sufficient.

**Input**:
- Full conversation history (all previous turns)
- New read results (tool outputs, including error messages)

**Key rules**:
1. On error: diagnose cause (wrong path, wrong parameters, unsupported format), adjust and retry in `next_reads`
2. `coverage_sufficient: true` is only valid after turn ≥ 3
3. Continue if: any identified group has no events.tsv sample yet; or read results reveal unexpected additional groupings
4. Stop if: all groups covered; or read results are consistent across all tested groups; or diminishing returns (last 2 turns produced no new information)
5. When stopping: write `assessment` explaining why coverage is sufficient
6. EEG header reads (`read_eeg_header`): useful to verify annotations when events.tsv is absent or sparse

**Output schema** (same as P3a-0):
```json
{
  "turn_summary": "ses-01/task-nf covered: value=10→'rest', value=20→'task'. Still missing ses-02.",
  "groups_identified": [...],
  "groups_covered": [...],
  "groups_missing": [...],
  "coverage_sufficient": false,
  "assessment": "",
  "next_reads": [...]
}
```

When `coverage_sufficient: true`:
```json
{
  "turn_summary": "All 4 groups covered. Trigger meanings are consistent across sessions.",
  "coverage_sufficient": true,
  "assessment": "events.tsv confirms value=1→rest, value=3→task across all ses/task combinations. No session-level differences found. EEG header annotations consistent with TSV values."
}
```

---

### P3b — Event Structure Annotation

**Phase**: P3b  
**Budget**: 1 call  
**One-line job**: Assign Meaning, Event Type, and Meta Level to each raw event ID using only the collected evidence.

**System role**:
> You are an event annotation specialist. Assign Meaning, Event Type, and Meta Level to each raw event ID based strictly on the BIDS evidence collected. No BCI prior knowledge. No inference from paradigm descriptions.

**Input**:
- All events.tsv samples and events.json files from Phase 3a
- All other read results (EEG headers, README, etc.) from Phase 3a
- Raw event IDs and counts from EEGUnity scan

**Key rules**:
1. Event Type: ONLY `event` (experimental cue/response) or `admin` (system/session marker)
2. Meaning: describe what actually happens at this trigger per the BIDS data. Do NOT apply BCI convention or paradigm prior.
3. Trial phase markers (`rest`/`ready`/`task`/`interval`) → Meaning = "Trial phase onset: [phase name]". NOT a class label.
4. If same event ID has different meanings across sessions/tasks → document both in `session_task_scope`
5. `confidence`: "confirmed" = events.tsv direct mapping; "inferred" = derived from context; "unclear"
6. Meta Level: "raw" if label is directly usable; "super" only if derivation from external source is needed

**Output schema**:
```json
{
  "annotations": [
    {
      "event_id": "event_1",
      "event_type": "event | admin",
      "meta_level": "raw | super",
      "meaning": "Rest/baseline period onset",
      "confidence": "confirmed | inferred | unclear",
      "session_task_scope": "all | ses-01/task-mi only | ..."
    }
  ],
  "notes": "events.tsv value=1→rest confirmed across all 4 session/task groups."
}
```

**Critical anti-hallucination**: If the collected evidence shows phase markers (rest/task/interval), the Meaning must reflect that. Never infer MI class labels from event count patterns or numbering conventions.

---

### P5b — Channel Rename Decision (conditional)

**Phase**: P5b  
**Budget**: 1 call (only if `needs_channel_rename = True`)  
**One-line job**: Decide whether channel renaming is needed and produce the rename map.

**System role**:
> You are an EEG channel naming specialist. Decide whether this dataset's channels need renaming and produce a precise rename map if so.

**Input**:
- Raw channel names from EEG header sample (Phase 0 `eeg_header_summary`)
- Locator CSV sample (first 10 rows + column list, compressed)
- Evidence collected in Phase 3a (any CSV/TSV/README in data_dir that lists channel names)
- `eeg.json` with `EEGChannelCount` and any channel description

**Key rules**:
1. Rename ONLY IF: channels have non-recoverable names (pure integers `1, 2, 3`, or opaque codes like `EEG-0`) AND there is a reliable mapping source in the evidence
2. Do NOT rename if channels already follow a recognizable standard (Fp1, Cz, O1, etc.) even if capitalisation differs slightly
3. Reliable mapping sources: a CSV/TSV in data_dir listing `channel_idx → channel_name`, a paper table, the README with explicit channel list
4. If no reliable source: set `rename_needed: false` and explain
5. Include `remapping_source` annotation string for each group of renames

**Output schema**:
```json
{
  "rename_needed": true,
  "remapping_source": "channel_info.csv in data_dir (tier-① evidence)",
  "rename_map": {
    "1": "Fp1", "2": "F7", "3": "F3"
  },
  "reasoning": "Channels named as integers 1–64; channel_info.csv in data_dir provides the standard 10-20 mapping explicitly."
}
```

---

### P5c — Annotation Strategy (conditional)

**Phase**: P5c  
**Budget**: 1 call (only if `needs_annotation_build = True`, i.e. non-BIDS format)  
**One-line job**: Write the annotation-building code for a non-BIDS format where EEGUnity cannot read events directly.

**System role**:
> You are an EEG signal processing specialist. Write the annotation building code for a dataset where events are not in BIDS format.

**Input**:
- Format type and sample file structure (from Phase 0 / evidence cache)
- Event structure table with event IDs and Meaning (from Phase 3b)
- EEG header sample: channel list, sfreq, any existing annotations
- Evidence from Phase 3a (e.g. .mat variable structure, STATUS channel pattern)

**Key rules**:
1. The goal is to produce `raw.set_annotations(mne.Annotations(onsets, durations, descriptions))` where descriptions match the event IDs in the Event Structure table (e.g. `"event_1"`, `"event_2"`)
2. Do NOT translate raw codes to semantic descriptions in the kernel — event IDs are enough; semantic meaning lives in analysis.md Meaning column
3. Admin events: set description to `"admin_<code>"` and they will be ignored by EEGUnity's epoch methods
4. Handle edge cases: empty stim channel, multiple stim channels, masked bits (BioSemi STATUS)
5. Output code only for the annotation-building helper function — not the full kernel

**Output schema**:
```json
{
  "helper_function": "def _build_annotations(raw):\n    ...\n    return raw",
  "remapping_source": "STATUS channel transitions (BioSemi 24-bit encoding, lower 16 bits)",
  "reasoning": "BioSemi STATUS channel stores event codes as integers; rising edges mark event onset."
}
```

---

### P5d — Kernel Assembly

**Phase**: P5d  
**Budget**: 1 call (always)  
**One-line job**: Write the complete kernel Python file for this dataset.

**System role**:
> You are an EEG kernel developer. Write a complete, correct, ready-to-run EEGUnity stage-1 kernel for this dataset. Follow the KERNEL_RULEBOOK and match the provided examples exactly in structure.

**Input**:
- Dataset name and analysis.md `## Tasks` section (finalized)
- Event Structure table with IDs, Type, Meta Level, Meaning (locked from Phase 3b)
- participants.tsv structure (column names, N, sample rows) — for metadata injection
- Locator CSV sample (first 10 rows, compressed)
- Channel rename decision from P5b (or `{}` if not needed)
- Annotation strategy code from P5c (or `None` if BIDS)
- KERNEL_RULEBOOK.md (full text)
- 3 example kernels (openneuro_ds001810.py, figshare_meng2019.py, openneuro_ds002158.py)
- Super meta qualifier details (from task JSONs: which events get prefixed, which column)
- Misc channel details (from task JSONs: which continuous value, which participants column)

**Key rules**:
1. Always write `raw.info["description"]` with `eegunity_description` containing age, sex, amplifier
2. For subject metadata: hardcode `_SUBJECT_DICT` if N ≤ 50; write dynamic `_load_participants(file_path)` function if N > 50
3. Channel rename: include `_CHANNEL_RENAME_MAP` and rename logic if P5b said needed; otherwise omit entirely
4. Annotation building: include P5c helper if non-BIDS; for BIDS, omit (EEGUnity handles it)
5. Super meta: add qualifier-prefix logic ONLY if any task has `Meta Level: super`. Use exact event IDs from Event Structure table as `_SUPER_META_TARGET_EVENTS`
6. Misc channels: add `add_channel(raw, ch_name, "misc", values)` ONLY if `needs_misc_channels`
7. All data-derived constants must have a `# Remapping source: ...` comment above them
8. Uncertain values (LLM-inferred, not confirmed by tier-① evidence): add `# LLM 推断，需人类复核` comment
9. `KERNEL_ID` format: `"<dataset-name>-stage1"`
10. Class name: `<DatasetName>Kernel` in PascalCase

**Output schema**:
```json
{
  "kernel_code": "\"\"\"OpenNeuro ds004447 stage1 kernel...\"\"\"\n\nfrom __future__ import annotations\n...\n\nKERNEL = OpenNeuroDs004447Kernel()",
  "sections_included": ["metadata_injection", "super_meta_enhancement"],
  "sections_omitted": ["channel_rename", "annotation_build", "misc_channels"],
  "notes": "N=30 subjects hardcoded from participants.tsv. Super meta adds HC-/MDD- prefix to event_1/event_3."
}
```

The runner extracts `kernel_code` and writes it to `neurodoc/kernels/<dataset_name>.py`.

---

### P5e — Kernel Review

**Phase**: P5e  
**Budget**: 1 call  
**One-line job**: Review the generated kernel for correctness, completeness, and style; produce a patch if issues are found.

**System role**:
> You are a code reviewer specializing in EEGUnity kernels. Review the generated kernel for correctness and completeness.

**Input**:
- Generated kernel code (full text)
- analysis.md `## Tasks` section
- Event Structure table

**Checks to perform**:
1. All imports are used; no missing imports (numpy, json, os, mne, etc.)
2. `KERNEL = ClassName()` at the end
3. `apply()` returns `raw`
4. `_SUBJECT_DICT` keys match expected subject ID format derived from file paths
5. `_SUPER_META_TARGET_EVENTS` contains exactly the event IDs that tasks require
6. Super meta prefix logic iterates `raw.annotations.description` correctly
7. Misc channel values have correct shape (`n_times` length)
8. No hardcoded absolute paths
9. All LLM-inferred values have `# LLM 推断，需人类复核` comments

**Output schema**:
```json
{
  "issues_found": ["Missing import: numpy", "_SUBJECT_DICT key format 'sub001' should be 'sub-001' per BIDS"],
  "patched_kernel_code": "...",
  "clean": false
}
```

If `clean: true`, `patched_kernel_code` is empty and the original is used as-is.

---

### P5-fix — Kernel Error Diagnosis (conditional)

**Phase**: triggered on P6 or P15 failure  
**Budget**: 1 call  
**One-line job**: Diagnose a kernel runtime error and produce a minimal patch.

**System role**:
> You are a debugging specialist. Fix the runtime error in this EEGUnity kernel.

**Input**:
- Full kernel code
- Error traceback from quick test
- Sample `row` data (locator row that triggered the error)
- Brief raw info (channel names, sfreq, n_times)

**Key rules**:
1. Fix the minimal amount needed to resolve the error
2. Do not restructure or rewrite working sections
3. Add `# Fixed: <brief description>` comment near the fix
4. If the error reveals a wrong assumption (e.g. wrong subject ID regex), fix the assumption and add `# LLM 推断，需人类复核` if still uncertain

**Output schema**:
```json
{
  "root_cause": "subject ID regex r'(sub-\\d+)' fails for filenames like 'S01_task.bdf'",
  "patched_lines": "        match = re.search(r'(S\\d+|sub-\\d+)', file_path)",
  "full_patched_kernel": "..."
}
```

---

### P7 — Epoch Alignment Analysis

**Phase**: P7  
**Budget**: 1 call per distinct paradigm  
**One-line job**: Determine epoch alignment (onset/offset) and recommend tmin/tmax/method for this paradigm.

**System role**:
> You are an EEG preprocessing expert. Determine the correct epoch alignment and parameters for a specific paradigm in this dataset.

**Input**:
- Full Event Structure table (IDs + counts + Type + Meta Level + Meaning locked from P3b)
- `events.json` column definitions
- `eeg.json` device info
- P2 task extraction summaries for this paradigm (epoch hints, `epoch_params` from paper)
- Category SKILL guide

**Key rules**:
1. Alignment = ONSET means marker fires at cue start; OFFSET means marker fires at cue end
2. Derive cue duration if stated in paper or inferable from event structure
3. `epoch_method` must be one of the three `*_hdf5` variants only
4. For segmentation paradigms (no natural events): `segment_length` and `overlap` required
5. If paper states different params than SKILL guide, use paper's values and note deviation
6. `target_event_ids`: must use exact IDs from Event Structure table

**Output schema**:
```json
{
  "paradigm_label": "Motor Imagery",
  "alignment": "onset | offset | mixed | unclear",
  "cue_duration_s": 4.0,
  "epoch_method": "epoch_by_event_hdf5",
  "tmin": 0.0,
  "tmax": 4.0,
  "overlap": null,
  "segment_length": null,
  "target_event_ids": ["event_1", "event_2"],
  "reasoning": "events.json states 'Onset of first frame of instruction'. Paper confirms 4s imagery window."
}
```

---

### P8a — Per-Task Draft

**Phase**: P8a  
**Budget**: 1 call per candidate task  
**One-line job**: Produce a structured JSON for one specific task, grounded in the locked event structure and a single paper's evidence.

**System role**:
> You are an EEG task documentation specialist. Document one machine learning task for this EEG dataset. Follow the Label Route decision rules and super meta naming convention strictly.

**Input**:
- Dataset name + full Event Structure table (IDs + Type + Meta Level + **Meaning locked**)
- Epoch alignment recommendation for this paradigm (from P7)
- P2 extraction for the paper(s) supporting this specific task only
- Category SKILL guide
- Label Route decision rules (§5.1–5.2)
- Super meta naming convention (§5.5)
- Task examples A–D (§5.4) — shown as few-shot examples

**Key rules**:
1. `target_events`: MUST use exact IDs from the Event Structure table. For super meta tasks: use `<qualifier>-<base_event_id>`
2. Meaning values from P3b are GROUND TRUTH — do not reinterpret them
3. If Meaning says "trial phase onset: rest", this event cannot be a classification class label in a raw task — it may only be used as a window anchor in a super task
4. Label Route decision: event (y from trigger), misc (y from file column/channel), info (y from standard Info fields)
5. Meta Level decision: raw (y readable directly), super (y requires join/derivation)
6. For super meta tasks: kernel_notes MUST describe the derivation formula explicitly
7. Task tier: Classical requires ref with real DOI/URL; Potential allowed without ref

**Output schema**:
```json
{
  "task_tier": "Classical | Normal | Potential",
  "task_name": "...",
  "task_type": "classification | regression | segmentation",
  "epoch_method": "epoch_by_event_hdf5 | epoch_by_long_event_hdf5 | epoch_by_segmentation_hdf5",
  "tmin": 0.0,
  "tmax": 4.0,
  "overlap": null,
  "segment_length": null,
  "target_events": ["event_1", "event_2"],
  "label_route": "event | misc | info",
  "meta_level": "raw | super",
  "super_meta_qualifier": "HC, MDD (from participants.tsv diagnosis column)",
  "target_definition": [
    {"key": "event_1", "y": 0, "meaning": "Rest/baseline period onset"},
    {"key": "event_3", "y": 1, "meaning": "Task period onset"}
  ],
  "evidence": [
    {"ref": "10.xxxx/...", "evidence_desc": "..."}
  ],
  "kernel_notes": "..."
}
```

---

### P8b — Task Cross-Check

**Phase**: P8b  
**Budget**: 1 call  
**One-line job**: Validate all task drafts for consistency, duplicates, and rulebook compliance; return the final approved task list.

**System role**:
> You are a task validation specialist. Review all drafted tasks for this dataset and fix any issues before final output.

**Input**:
- All task JSON structs from P8a
- Full Event Structure table
- List of valid event IDs (locked)
- Existing Potential Tasks from prior analysis.md (if any)

**Key rules**:
1. CHECK A: every `target_events` entry exists in the Event Structure table
2. CHECK B: every Classical Task has at least one `ref` with a real DOI/URL
3. CHECK C: no two tasks describe the same epoch+label combination (deduplicate)
4. CHECK D: task tier justified — Classical requires `relevant` paper; Potential allowed with partial or no ref
5. CHECK E: existing Potential Tasks from prior analysis.md are preserved verbatim if no new evidence changes them
6. CHECK F: no Meaning values were reinterpreted (trial phase ≠ class label)
7. If issues found: fix in place; document in `validation_notes`

**Output schema**:
```json
{
  "validated_tasks": [ ... ],
  "issues_found": ["task 2 duplicate of task 1 — merged", "task 3 ref missing — downgraded to Potential"],
  "validation_notes": "..."
}
```

The runner then assembles validated task JSONs into the `## Tasks` markdown section using the fixed template.

---

### P9 — Paradigm Section

**Phase**: P9  
**Budget**: 1 call  
**One-line job**: Write the `## Paradigm` paragraph summarizing the dataset's experimental design.

**System role**:
> You are an EEG dataset documentation writer. Write only the Paradigm section — one factual paragraph describing the experimental design, participants, and recording setup.

**Input**:
- Dataset name, year, URL (from analysis.md header)
- Participants summary (N, age range, sex counts from participants.tsv)
- BIDS README (up to 3000 chars)
- P2 paradigm descriptions from relevant/partial papers
- `eeg.json` device info (manufacturer, channel count, sfreq)

**Key rules**:
1. Write exactly one paragraph (3–6 sentences). No headers, no bullet points.
2. Cover: task design, participant details (N, age, sex), EEG device, key paradigm parameters
3. Do NOT mention event IDs, trigger codes, epoch parameters, or task names — those go in later sections
4. Do NOT write "Pending" or placeholder text. If information is unavailable, omit that detail.
5. Use information from participants.tsv over paper claims if they conflict (tier ① wins)
6. Technical, factual, no marketing language

**Output schema**:
```json
{
  "paradigm_text": "Participants (N=30, age 18–27, 5 female/25 male) performed motor imagery of four limb movements following visual cues, recorded with 130-channel high-density EEG (GES400/Hydrocel GSN) at 1000 Hz. ..."
}
```

---

### P10b — Data Quality Note (per triggered category)

**Phase**: P10b  
**Budget**: 1 call per triggered stat category  
**One-line job**: Write one bullet point describing a specific data quality issue and its practical implication.

**System role**:
> You are a data quality analyst. Write a single factual bullet point about a specific data quality issue in this EEG dataset.

**Input** (category-specific, one of):

| Category | Specific input |
|----------|---------------|
| Event imbalance | max_event/min_event ratio, event names and counts |
| Subset events | which events appear in which files, file count total |
| N mismatch | participants.tsv N vs scan N, both values |
| SR/channel inconsistency | list of (sfreq or n_channels) values with file counts |
| Missing Info field | which field, what tasks it affects |
| Paradigm-task conflict | paper claim vs events.tsv evidence |

**Key rules**:
1. One bullet point only (1–3 sentences)
2. Include specific numbers (ratios, counts)
3. State practical impact: which tasks are affected; what kernel must handle
4. Use "as per tier-① BIDS sidecar" or "as per scan result" to cite source
5. Never speculate beyond the provided stats

**Output schema**:
```json
{
  "bullet": "Significant class imbalance: event_2 (5090 trials) vs event_1 (327 trials), ratio ~15.5×. Kernels using both events should apply class-weighted loss or stratified sampling. Files without event_3/event_4 (327/418 files) must be filtered before feet/tongue MI tasks."
}
```

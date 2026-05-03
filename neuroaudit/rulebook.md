# NeuroAudit Rulebook for EEG Dataset `analysis.md`

Version: 1.0.0

Status: stable archive

Released: 2026-05-02

Baseline: draft v0.6, last confirmed 2026-04-18

Audience: LLM review scripts, human reviewers, and maintainers

Scope: `analysis.md` files, and same-structure successor documents, under this repository's dataset directories.

This v1.0.0 document preserves the design logic of draft v0.6, translates it into English, normalizes terminology, and removes draft-facing phrasing. Any future design change must be recorded as a new rulebook version.

---

## Legacy Version Archive

These entries are retained for auditability. They describe how the archived draft evolved before v1.0.0.

### v1.0.0

- Archives draft v0.6 as the stable English rulebook.
- Keeps the existing schema, status values, label routes, target-definition rules, and migration boundaries unchanged.
- Normalizes rule names, article labels, and reviewer-facing wording.

### v0.5 -> v0.6

- Clarified that epoch extraction and label extraction are independent axes. Each task must declare both.
- Removed `Label Field` from the `misc` and `info` task schema. Label source now lives in the first column of `Target Definition`.
- Allowed `misc` routes for both `classification` and `regression`, while still allowing only one misc channel per task.
- Added the single-target rule: one task may reference only one label source; multidimensional labels must be split into separate tasks.
- Added the rule that classification tasks must contain at least two classes.
- Added the derived-misc to super-meta rule: any kernel-created misc channel is super meta, and derivation steps should be recorded in task `Notes`.
- Expanded `### Info` from three fixed fields to all discovered `participants.tsv` columns, while keeping `subject_age`, `subject_sex`, and `device` as mandatory canonical fields.
- Bound `Target Definition` table schema strictly to `Label Route x Task Type`.
- Added the automation rule that `Manual Review` is human-only. LLMs must leave it blank, and generation pipelines must clear accidental non-empty values.

### v0.4 -> v0.5

- Added the top-level `## File Scan Result` section with a kernel fingerprint blockquote and three subsections.
- Demoted `## Event Structure` and `## MISC Label Summary` to `### Event Structure` and `### MISC Label Summary`.
- Added `### Info` for subject and device metadata completeness.
- Redefined `Label Route` as the source of supervision signal with three values: `event`, `misc`, and `info`.
- Deprecated `Annotation` and `STIM` as `Label Route` values.
- Added `Label Route = info` target-definition rules.

### v0.3 -> v0.4

- Moved `## Kernel Responsibilities` after `## Data Quality Notes` in the document template.
- Deprecated the event-type legend line under `Event Structure`.
- Made explanatory notes under `Event Structure` optional and forbade repeating the enum definition there.

### v0.2 -> v0.3

- Simplified the Kernel Responsibilities area.
- Deprecated Type 1/2/3 template text, `Selected Mode`, `Why`, `Primary Label Routes`, and `Web Reference Used for Decision`.
- Kept only `Super Meta Required` and `Status` in the blockquote metadata.
- Added rules for `Super Meta Required`.

### v0.1 -> v0.2

- Deprecated `STIM Label Summary`.
- Registered all discrete events, including events originally stored in stim channels, under `Event Structure`.
- Simplified `Event Structure.Type` to `event` and `admin`.
- Made `target_events` valid only when they come from `Event Structure` entries with `Type = event`.
- Clarified that `Label Route` is a kernel output route, not the raw storage location.

---

# Part I. General Provisions

## Chapter 1. Purpose and Scope

### Article 1. Purpose

This rulebook standardizes generation, review, revision, and re-review of EEG dataset `analysis.md` documents so that they can:

1. Provide human reviewers with consistent, explicit, actionable review standards.
2. Provide LLM review scripts with stable, programmable, traceable decision rules.
3. Provide structured implementation guidance for later kernels, EEGUnity exports, and HDF5 production.

### Article 2. Scope

This rulebook applies to:

1. Creating new dataset documents.
2. Revising existing dataset documents.
3. Reviewing core areas such as `Classical Task`, `Potential Task`, `Event Structure`, and metadata.
4. Writing later LLM review rules, prompt rules, and fallback rules.

### Article 3. Core Principles

Document generation and review must follow these principles:

1. Truthfulness first.
2. Actual data has priority over web descriptions.
3. Conservatism has priority over guessing.
4. Traceability has priority over brevity.
5. Implementable task definitions have priority over theoretically imaginable ones.

## Chapter 2. Terms

### Article 4. Dataset Document

A dataset document means the `analysis.md` file under a single dataset directory, or a same-structure successor version.

### Article 5. Raw Meta

`raw meta` means labels, events, codes, annotations, fields, or markers that already exist in the raw data and can be read without additional derivation. Examples include:

1. `trial_type`, event codes, and event names in `events.tsv`.
2. Raw codes in trigger or stim channels.
3. Discrete events in raw annotation files.
4. Directly available behavioral fields in raw tables.

### Article 6. Super Meta

`super meta` means labels or targets that do not directly exist in the raw data and must be generated, mapped, folded, paired, aggregated, joined, or otherwise derived by code, rules, or human logic. Examples include:

1. Response events.
2. Binary labels folded from multiple raw classes.
3. Clinical groups derived from filenames, participant tables, or external tables.
4. Correct or incorrect, target or non-target, fast or slow, and similar labels derived by pairing multiple events.

### Article 7. Kernel

`kernel` means the later data-processing code or data-loading logic used to parse raw data, construct labels, route labels, and generate EEGUnity-compatible output.

### Article 8. Label Route

Historically, `Label Route` meant the final EEGUnity or MNE-compatible path where labels landed, not necessarily the raw storage form. Earlier values were:

1. `Annotation`: time-based annotations with `onset`, `duration`, and `description`.
2. `STIM`: trigger or stim channel route for code values or trigger pulses.
3. `MISC`: misc channel route for numeric auxiliary labels, continuous quantities, or attached labels unsuitable as event names.

Deprecated: `Annotation`, `STIM`, and `MISC` as route values are not allowed in new documents. Current legal values are `event`, `misc`, and `info`; see Article 77.

### Article 9. Task

A `Task` is a definition that can directly guide EEG epoching, label construction, and supervised-learning configuration.

### Article 10. Classical Task

A `Classical Task` is a core task that is supported by external evidence and can be implemented from the currently public data.

### Article 11. Potential Task

A `Potential Task` is supported by the data itself but lacks enough external evidence to confirm it as a core benchmark task, or is only a recommended, extended, or derived task.

### Article 12. Evidence

`Evidence` means external material supporting a task, parameter choice, or document judgment. It includes:

1. The official dataset page.
2. Official documentation.
3. Papers that clearly use the dataset.
4. Other authoritative sources.

## Chapter 3. Evidence Priority and Conflict Handling

### Article 13. Evidence Priority

When sources conflict, use this priority order:

1. Verifiable data files and accompanying annotation files.
2. Official dataset page, official README, or official documentation.
3. Official papers or papers that clearly use the dataset.
4. Third-party pages, blogs, or unofficial descriptions.

### Article 14. General Conflict Rule

When sources conflict, use the higher-priority evidence and record the conflict and decision in `Data Quality Notes`.

### Article 15. Data Priority

When online material or paper descriptions conflict with actual data files, the actual data files prevail. The inconsistency must still be stated explicitly.

### Article 16. Conservative Handling

If existing evidence is insufficient to confirm a field, task, or label:

1. Prefer downgrading it to `Potential Task`.
2. Use placeholders such as `Needs verification`, `Variable`, `N/A`, or `null` when appropriate.
3. Do not fabricate missing information.

### Article 17. Implementability

Even if a paper used the dataset, a task must not be treated as a valid `Classical Task` unless the public data contains labels, events, or a verifiable derivation path sufficient to implement it.

## Chapter 4. Roles

### Article 18. Administrator Responsibilities

Administrators are responsible for:

1. Deciding dataset entry names.
2. Deciding whether to accept human revisions or rule updates in pull requests.
3. Deciding whether a kernel must be added or rewritten.

### Article 19. Human Reviewer Responsibilities

Human reviewers are responsible for:

1. Reviewing whether a `Classical Task` is valid.
2. Reviewing whether fields match actual data and official material.
3. Deciding how to resolve conflicting information.
4. Filling `Manual Review` when appropriate.

### Article 20. LLM Review Script Responsibilities

LLM review scripts are responsible for:

1. Pre-generating or pre-correcting documents under the rulebook.
2. Detecting likely conflicts, omissions, and invalid tasks.
3. Producing conservative, traceable suggestions without inventing raw labels.

# Part II. Specific Rules

## Chapter 5. Meta Area

### Article 21. General Field Rule

`Meta Area` records identifying dataset metadata. Unless otherwise specified, fields should be concise, stable, and easy for programs to read.

### Article 22. `Dataset`

1. `Dataset` is the dataset identifier.
2. It should follow `<source_name_id>`.
3. Administrators decide this name.
4. Reviewers and LLMs must not proactively modify it.

### Article 23. `Year`

1. `Year` records key years related to collection, processing, or release.
2. It does not need to distinguish collection year from release year.
3. Multiple key years may be joined with `/`, for example `2004/2021`.
4. Continuous ranges may use `-`, for example `2008-2015/2017`.
5. The field need not cover every historical year, but should be updated as well as trusted sources allow.
6. Do not ignore key years clearly present in the data because a web page title shows a different year.

### Article 24. `URL`

1. `URL` should preferably point to an information page that gives access to downloads or documentation.
2. If both a direct file link and an information page exist, keep the information page.
3. If a link is dead and cannot be replaced with an authoritative information page, delete it or replace it with an accessible authoritative page.
4. The field does not need to be permanently valid, but must have practical review value at the time of review.

### Article 25. `Category`

1. `Category` must be exactly one of:
   - `Complex Applied`
   - `High-level Mental`
   - `Action/Output`
   - `Sensory/Response`
   - `Biological State`
   - `Others`
2. The field is normally proposed by a program or preprocessing LLM.
3. Human reviewers should correct it only when the classification is clearly wrong.
4. Do not create category values outside the six listed values.

### Article 26. `Subjects`

1. `Subjects` is the integer number of valid subjects in the dataset.
2. If the official count differs from the actually usable count, prefer the actually usable count.
3. Record this conflict in `Data Quality Notes`.

### Article 27. `Files (Completed)`

1. `Files (Completed)` is the number of files parsed by EEGUnity as `Completed`.
2. LLMs and human reviewers normally must not edit this field manually.
3. If the parser result is clearly abnormal, report that the dataset needs a rescan or kernel correction instead of manually changing the count.

### Article 28. `Channels`

1. `Channels` is the number of channels used by files, including non-EEG channels.
2. If only a few channel counts exist and can be listed clearly, use forms such as `32/64` or `22-128`.
3. If the situation is complex and should not be fully enumerated, use `Variable`.
4. LLMs or reviewers may use the clearest representation, but must avoid ambiguity.

### Article 29. `Sampling Rate`

1. `Sampling Rate` records the main sampling-rate information.
2. If the whole dataset has one sampling rate, write a single value.
3. If files, modalities, or phases differ, use multiple values or explanatory wording.
4. If differences are complex, use `Variable` and explain in `Data Quality Notes`.

### Article 30. `Manual Review`

1. Only human reviewers may fill `Manual Review`.
2. The value may be a real name, alias, or reviewer-approved identifier.
3. Multiple reviewers should be separated by `/` in review order.
4. LLMs must not forge, add, or impersonate a `Manual Review` mark.
5. `Manual Review` must be inline at the end of the second meta line, after `Sampling Rate`, using `| **Manual Review**: ...`.
6. A separate third-line `Manual Review` field is no longer allowed.

### Article 30.1. Fixed Structure

1. The current template normally keeps only these top-level sections in this order:
   - `## Paradigm`
   - `## File Scan Result`
   - `## Tasks`
   - `## Data Quality Notes`
   - `## Kernel Responsibilities`
2. `## File Scan Result` contains these third-level subsections in fixed order:
   - `### Event Structure` (required)
   - `### MISC Label Summary` (optional)
   - `### Info` (required)
3. Do not rename fixed section headings except for explicitly optional sections listed in this rulebook.
4. `STIM Label Summary` is deprecated and must not be added to new documents. Discrete events from trigger or stim channels must be registered in `### Event Structure`.

### Article 30.2. No Extra Sections

1. Unless maintainers explicitly request it, do not add non-template top-level sections such as `## Meta`, standalone `## References`, or custom extension sections.
2. If extra explanation is necessary, prefer task `Notes`, `Data Quality Notes`, `### Kernel Notes` under `## Kernel Responsibilities`, or review records.
3. When substantially revising historical documents, remove extra sections that violate the current structure unless maintainers explicitly request otherwise.

### Article 30.3. Automated Behavior for `Manual Review`

1. LLM stages in generation pipelines must not fill `Manual Review`, including placeholders such as `Pending`, `TBD`, or `N/A`.
2. LLMs should output `| **Manual Review**:` at the end of the second meta line with nothing after the colon. If template reuse accidentally inserts a non-empty value, post-processing must clear it.
3. This field may be non-empty only when a human reviewer manually edits `analysis.md`; use Article 30 for formatting.

## Chapter 6. Paradigm Area

### Article 31. General Paradigm Rule

`Paradigm Area` should describe the dataset's experimental paradigm, task form, subject behavior, and recording method, and should match the actual data.

### Article 32. Consistency Requirements

Paradigm descriptions must align with:

1. Data directories and file structure.
2. Event files.
3. Official pages and official documentation.
4. Authoritative papers that clearly use the dataset.

### Article 33. Data Priority

When online material conflicts with data material, the data prevails.

### Article 34. No Over-Inference

Paradigm descriptions must not turn a paper's experimental goal, theoretical hypothesis, or common analysis style into a label task supposedly supported by the public data unless the data provides implementable events or labels.

### Article 35. Description Boundary

Paradigm descriptions may state the original experimental intent, but must distinguish:

1. The goal of the experimental design.
2. The labels and tasks actually available in the public data.

## Chapter 7. Kernel Responsibilities Area

### Article 36. Purpose and Structure

1. `Kernel Responsibilities Area` records the core semantic judgment for the dataset at the kernel level.
2. The section uses blockquote metadata fields. The current version keeps only `Super Meta Required` and `Status`, in that order.
3. Do not add other fields, custom blocks, or explanatory text in this section.
4. Historical fields such as Type 1/2/3 template text, `Selected Mode`, `Why`, `Primary Label Routes`, and `Web Reference Used for Decision` are deprecated and should be removed during substantial revisions.

### Article 37. `Super Meta Required`

1. `Super Meta Required` states whether the dataset has target labels that require extra derivation, pairing, folding, mapping, or cross-file joining.
2. Legal values are exactly:
   - `Yes`: at least one task in `Tasks Area` has `Meta Level = super`.
   - `No`: all tasks have `Meta Level = raw`.
3. Do not use synonyms or case variants.

### Article 38. Deciding `Super Meta Required`

1. If any task, including `Classical Task` or `Potential Task`, has `Meta Level = super`, `Super Meta Required` must be `Yes`.
2. If all tasks have `Meta Level = raw`, `Super Meta Required` should be `No`.
3. If this field conflicts with `Tasks Area`, `Tasks Area` prevails and this field must be corrected.
4. LLM review scripts may infer and fill this field from `Tasks Area`.

### Article 42.1. `Status`

1. `Status` marks whether the current document text is sufficient to support later kernel refactoring, EEGUnity export, or event and label reconstruction.
2. `Status` is a dataset-level field, not a per-task field.
3. Although `Status` is metadata, it must currently be written in the `Kernel Responsibilities Area` blockquote, not in a new top-level section.
4. LLM review scripts, human reviewers, or maintainers may update `Status` according to the latest judgment.

### Article 42.2. Legal `Status` Values

`Status` may use only these four machine-readable values:

1. `wait_kernel_update`
2. `wait_manual_review`
3. `completed`
4. `hallucination`

Do not replace them with synonyms, natural-language phrases, or case variants.

### Article 42.2.1. Authority Boundary for `completed` and `hallucination`

1. Only human reviewers may assign `completed` or `hallucination`. LLM review scripts must not proactively assign either value.
2. At the current stage, LLM review scripts should choose only between `wait_kernel_update` and `wait_manual_review`, and should default conservatively to `wait_manual_review`.
3. If the current text is already sufficient to support existing tasks and does not expose a clear structural kernel gap, LLM review scripts should output `wait_manual_review` and wait for final human confirmation.
4. After human review is complete, the final status must be `completed` or `hallucination`; it must not remain `wait_manual_review` or `wait_kernel_update`.

### Article 42.2.2. Boundary for `hallucination`

1. `hallucination` is a severe document-level defect flag for cases where the entire `analysis.md` cannot be trusted.
2. Triggering conditions include, but are not limited to:
   - The dataset URL is invalid and no key field can be verified.
   - The document describes a dataset that does not match the actual dataset.
   - Task definitions, `Event Structure`, and `Paradigm` have no credible basis and cannot be repaired by reasonable supplementation.
   - Dataset information is so incomplete that even experts cannot make a reliable judgment.
3. `hallucination` does not apply to local issues such as one incorrect task citation or partially inaccurate channel description. Local issues should be recorded in `Data Quality Notes`, and status should remain `completed` after human review.
4. For datasets marked `hallucination`, administrators will consider deleting the document or arranging a rescan. Reviewers are not required to keep repairing it.

### Article 42.3. Deciding `Status`

1. `wait_kernel_update` means the document clearly exposes a structural semantic kernel gap: `Event Structure`, `MISC Label Summary`, `Label Route`, companion-file ingestion, or `super meta` integration is not yet sufficient to support existing tasks stably. This is an intermediate state for LLM scripts or automatic scanning.
2. `wait_manual_review` means no clear structural kernel gap is exposed, or remaining doubts mainly require human confirmation of task validity, task retention, or final release. This is the default LLM output status.
3. `completed` means a human reviewer confirms that document review is finished. Known quality issues may still exist if they are recorded in `Data Quality Notes` and the overall document is trustworthy and ready to proceed. `completed` means the reviewer has done due diligence, not that the document is flawless.
4. `hallucination` means a human reviewer judges the whole document to have unrecoverable severe defects and that it should be handled by administrators.
5. The following must not, by themselves, justify `wait_kernel_update`:
   - Routine preprocessing, filtering, rereferencing, or downsampling.
   - Artifact rejection, bad-segment removal, or bad-file exclusion.
   - General data quality control.
   - Implementation details such as training parameters, epoch length, or model hyperparameters.
   - Guessing from outside the document that the kernel might be unfinished or unverified.
6. If the document semantically explains relevant events, labels, companion files, or metadata access paths and presents tasks as currently valid, do not mark `wait_kernel_update` only because of implementation caution.
7. When a dataset has multiple issue types, judgment priority is: `hallucination` above all other values; `wait_manual_review` above `wait_kernel_update`; `wait_kernel_update` above `completed`.

### Article 42.4. Blockquote Position and Order

1. In the current version, blockquote metadata under `Kernel Responsibilities Area` must appear in this order:
   - `Super Meta Required`
   - `Status`
2. Do not create separate top-level sections or custom blocks for these fields.
3. If a maintenance script batch-rewrites `Status`, it should modify only the fixed line for that field and should not rewrite unrelated body text.

## Chapter 8. File Scan Result Area

`## File Scan Result` summarizes the kernel scan over raw data files, including kernel fingerprint, event structure, MISC labels, and subject information. It always contains `### Event Structure` and `### Info`; `### MISC Label Summary` appears only when the dataset exposes misc-route labels or scanned native misc channels. The area begins with a kernel fingerprint blockquote.

### Article 42.5. Kernel Fingerprint

1. The start of `## File Scan Result` should record the kernel fingerprint used to generate the scan result as a blockquote.
2. The reference format is:
   ```markdown
   > **Kernel SHA256**: `<full_hash>`
   > **EEGUnity Version**: `X.Y.Z`
   > **Scan Type**: Full
   ```
3. `Kernel SHA256` is the hash of the kernel file content and is calculated by maintenance scripts; it should not be filled manually. `EEGUnity Version` is the version used during scanning.
4. `Scan Type` is `Full` or `Sampled (N/M files)`.
5. If the dataset has no kernel yet, write `N/A` for `Kernel SHA256`.
6. Neurodoc maintains this blockquote automatically. Human reviewers and LLMs must not manually edit the hash value.
7. The frontend display layer treats all consecutive `>` lines at the beginning of `## File Scan Result` as Kernel Fingerprint and renders them as one blockquote without parsing field names. This keeps the frontend independent of field changes.
8. Do not insert HTML comments such as `<!-- AUTO-KERNEL-... -->` inside `### Event Structure` or other subsections. All kernel-derived information must be written directly in standard Markdown.

### Article 43. Table Form

`### Event Structure` must be presented as a table. The table may be empty, but emptiness has rule consequences.

### Article 44. Required Columns

The table must contain at least:

1. `Event ID`
2. `Count (total)`
3. `Type`
4. `Meta Level`
5. `Meaning`

### Article 45. Consequences of an Empty Table

When `Event Structure` is empty or explicitly states that no valid event labels exist:

1. Do not keep `epoch_by_event_hdf5` tasks.
2. Do not keep `epoch_by_long_event_hdf5` tasks.
3. Normally only `epoch_by_segmentation_hdf5` may be considered.

### Article 46. Legal `Type` Values

`Type` may use only:

1. `event`: discrete events or time spans that can be used for tasks, including stimuli, responses, state transitions, sleep stages, and other domain events.
2. `admin`: system, boundary, or excluded events, such as device markers, file boundaries, or motion-artifact markers.

The historical `short`, `long`, and `rest` subdivisions are deprecated. Event duration behavior is determined by `Epoch Method` in `Tasks Area`, not repeated in `Event Structure`.

### Article 47. `admin` Events

1. `admin` events should remain explicitly listed in `Event Structure`; do not delete them by default.
2. `admin` events must not normally be used as `target_events` for supervised-learning tasks.
3. Any exception requires strong evidence and a reason in task `Notes`.

### Article 48. Deciding `Meta Level`

1. Events that can be read directly from raw data are `raw`.
2. Events that require pairing, folding, derivation, mapping, joining, or reconstruction are `super`.

### Article 49. First-Pass Documentation

On first document creation, `Event Structure` should normally record only `raw meta`. If `super meta` is not yet supported by a stable kernel, do not pretend it is a raw event.

### Article 50. Handling Mismatches with Source Material

When `Event Structure` seriously disagrees with dataset documentation:

1. If task validity is not affected, warn in `Data Quality Notes`.
2. If task validity is affected, correct event interpretation, downgrade tasks, delete tasks, or report that a rescan is needed.
3. Do not keep incorrect tasks without explaining the conflict.

### Article 51. Parser Differences

When mismatch is likely caused by kernel parser differences:

1. If task validity is not affected, correction may be postponed.
2. If task validity is affected, clearly mark that a rescan or kernel correction is needed.

### Article 51.1. Linkage with `Status`

1. If `Event Structure`, `MISC Label Summary` when present, and `Tasks Area` already form a sufficiently consistent evidence chain, do not mark `wait_kernel_update` only because of preprocessing, artifact rejection, quality control, or implementation details.
2. If the document is already sufficient as textual support for existing `Classical Task` or `Potential Task` entries, but final release still requires administrator or human-reviewer confirmation, LLM review scripts should temporarily mark `wait_manual_review`.
3. If `Event Structure` cannot support existing tasks and the issue mainly concerns human judgment about task validity, event semantics, evidence conflict, label mapping, deletion, or downgrading, `Status` should normally be `wait_manual_review`.
4. `Status` may be `completed` only when `Event Structure`, relevant tasks, route explanations, and `MISC Label Summary` when present form a sufficiently consistent and traceable implementation basis, and a human reviewer or administrator has confirmed it.

### Article 52. Context-Dependent Events

If the same event code has different meanings across files, tasks, or experimental phases, it is a context-dependent event. For such events:

1. Do not interpret their meaning without file-level context.
2. Warn explicitly in `Event Structure` or `Data Quality Notes`.
3. Without stable context rules, do not use them directly in high-confidence `Classical Task` entries.

### Article 53. Later Updates for `super meta`

When a `Classical Task` depends on `super meta`, human reviewers are normally not required to manually rewrite `Event Structure` first. Such updates should be handled by later kernel and LLM automation.

### Article 53.1. Optional Notes under `Event Structure`

1. An optional explanatory `Note` may appear after the `Event Structure` table, but is not required.
2. The note must not repeat the meanings of the `Type` enum values; `event` and `admin` are defined by this rulebook.
3. Use the note only when:
   - Raw data has parsing ambiguity, such as the same event code meaning different things in different files.
   - Events come from multiple sources, such as companion files and trigger channels, and their merge logic matters.
   - Other explanations materially affect kernel implementation.
4. Do not use the note to introduce new events that are absent from the table.
5. If a later kernel update changes event representation, first update this note and related task routes, then decide whether to rewrite the main `Event Structure` table.
6. When neurodoc writes new scan results, any change to the `Event Structure` table, including count changes or event additions or removals, clears this note automatically. If the table is unchanged, the note remains unchanged.

### Article 53.2. Companion Files and External Tables

1. Labels, event intervals, or auxiliary fields directly present in official companion files, `participants.tsv`, behavioral tables, sleep-stage files, or other formal sidecars may normally be used as valid information sources.
2. If such information is a discrete event or time span and will be used for `target_events` or event-route tasks, it must first be registered in `Event Structure`.
3. If such information is an epoch-level class, scalar, count, score, or continuous quantity, do not force it into `Event Structure`; route it through `MISC Label Summary` or task `Notes` as appropriate.
4. These fields are `raw` only when directly readable without extra derivation. If they require pairing, mapping, normalization, cross-file joining, or rule-based reconstruction, they are `super`.

### Article 54. General Rule

`### MISC Label Summary` describes the source, meaning, and implementation of numeric or continuous auxiliary labels.

`STIM Label Summary` is deprecated. Discrete events originally stored in trigger or stim channels must be registered in `### Event Structure` instead.

### Article 55. When It Appears

1. If any task uses `misc` as `Label Route`, `### MISC Label Summary` must exist.
2. If no task uses the `misc` route, this subsection may be omitted.
3. Native misc channels found during scanning may be registered here for future tasks even when no current task uses them.

### Article 56. Content Requirements

`### MISC Label Summary` is a table with fixed columns `Channel | Source | Meta | Notes`:

1. `Channel`: misc channel name, referenced by `Label Route = misc` tasks in the first column of `Target Definition`.
2. `Source`: field source, such as `native (raw misc in EEG file)`, `native (events.tsv column: response_time)`, or `derived from participants.tsv: p_factor`.
3. `Meta`: `raw` or `super`. Derived misc must be `super`; see Article 77.8.
4. `Notes`: units, alignment, derivation logic, fill rules, and other implementation notes.

### Article 57. Automation Principle

This section is normally generated by the kernel and LLM. Human reviewers should edit it only when it is clearly wrong, incomplete, or in conflict with task dependencies.

### Article 57.1. General Rule

1. `### Info` records availability of file-level metadata exported by the kernel for `Label Route = info` tasks, typically from `raw.info["description"]["eegunity_description"]`.
2. This subsection is required and must not be omitted. If information is entirely missing, still list the relevant fields and mark them `missing`.

### Article 57.2. Fields and Completeness

1. `### Info` is a table with fixed columns `Field`, `Completeness`, and `Notes`.
2. `Field` names come from the kernel-exported `eegunity_description` dictionary. The rulebook does not define a closed mandatory field list.
3. Common examples include `age`, `sex`, `device`, `handedness`, `group`, or other dataset-specific metadata keys. Any key exported by the kernel should be registered as-is and should appear only once.
4. If the kernel exports no usable info fields, the table may still contain placeholder rows such as `age`, `sex`, or `device`, marked `missing`, to make missingness explicit.
5. Any `Info Field` referenced by a `Label Route = info` task must be one of the fields registered in this table.

### Article 57.3. Legal `Completeness` Values

`Completeness` may use only:

1. `complete`: every EEG record in the dataset has this field.
2. `partial (x/n)`: the field exists for `x` out of `n` scanned records.
3. `incomplete`: many missing values are known, but a stable ratio is not recorded.
4. `missing`: the field is entirely absent.

### Article 57.4. `Notes` Column

1. `Notes` is optional supplementary explanation, such as numeric range, enum values, or missingness reasons.
2. If no supplement is needed, write `N/A`.

### Article 57.5. Automation Principle

1. Field discovery and `Completeness` should normally be inferred automatically from kernel scan results, based on the metadata the kernel actually writes into `eegunity_description`.
2. `Notes` may be assisted by the LLM during document generation, but the existence of fields and their completeness status should remain scan-derived.
3. Human reviewers should edit this subsection only when automatic filling is clearly wrong, stale, or semantically misleading.

## Chapter 9. Retired

The former Chapter 9, `MISC Label Summary`, has been merged into the `MISC Label Summary` articles under Chapter 8. This chapter number is retained as a placeholder and has no active content.

## Chapter 10. Tasks Area

### Article 58. Role of the Tasks Area

`Tasks Area` is the most important executable area in the document. It should directly guide EEG epoching, label generation, and later implementation.

### Article 59. Task Headings

Task headings must use one of:

1. `### Classical Task N: ...`
2. `### Potential Task N: ...`

### Article 60. Task Field Order

Each task should normally contain these fields in stable order:

1. `Task Type`
2. `Epoch Method`
3. `Epoch Parameters`
4. `Label Route`
5. `Meta Level`
6. `Target Definition`
7. `Super Meta Notes`, if applicable
8. `Evidence`, required for `Classical Task`
9. `Notes`, as free supplementary text with no forced format. It may be used for super-meta derivation steps, parameter inference, review notes, and similar content. The old field name `Kernel Notes` is unified as `Notes` from v3 onward.

### Article 61. Historical Legacy Syntax

Some historical documents may write `segmentation` as `Task Type`. From this rulebook onward:

1. `Task Type` should use only `classification` or `regression`.
2. `epoch_by_segmentation_hdf5` is only an `Epoch Method`.
3. Historical documents need not be batch-cleaned immediately, but new documents and new revisions should follow this rule.

### Article 62. Conditions for `Classical Task`

A `Classical Task` is valid only when both conditions hold:

1. Evidence shows that external literature or an authoritative source clearly used this dataset or an identifiable subset of it.
2. The evidence clearly supports the current task objective, label definition, or supervision target.

### Article 62.1. Explicitness Required for `Classical Task`

1. Key fields in a `Classical Task` must not use vague placeholders.
2. Key fields include at least:
   - `Task Type`
   - `Epoch Method`
   - `Epoch Parameters`
   - `Label Route`
   - `Meta Level`
   - `Target Definition`
   - `Evidence`
3. Vague placeholders or vague styles include:
   - `Needs verification`
   - `TBD`
   - `task-dependent`
   - `see Target Definition`
   - `Variable`
   - `N/A`
   - `unknown`
   - parameters marked with `*` or another undefined uncertainty marker
   - any broad description that cannot directly guide implementation
4. If there is not enough basis for explicit values, the task must not remain a `Classical Task`; downgrade it to `Potential Task`, mark it for review, or delete it.
5. LLMs and human reviewers may use judgment to choose the best explicit values for `Classical Task`.
6. The best explicit value should be chosen in this priority order:
   - official page or official documentation recommendation
   - actual values used in papers that clearly use the dataset
   - reasonable values chosen by a reviewer or LLM based on domain knowledge
7. If the chosen value is not quoted directly from the official page or paper, briefly explain the judgment in task `Notes`.

### Article 63. When to Use `Potential Task`

Use `Potential Task` when:

1. The data itself supports the task, but external evidence is insufficient.
2. Literature proves the dataset was used, but does not prove this exact task.
3. The task is a reasonable derived, recommended, or engineering task rather than the dataset's recognized main task.

### Article 63.1. Minimum Explicitness for `Potential Task`

1. A `Potential Task` may be more conservative than a `Classical Task`, but must remain readable, reviewable, and implementable.
2. At minimum, `Task Type`, `Epoch Method`, `Label Route`, and `Meta Level` must have explicit legal values.
3. If required parameters for an `Epoch Method` are unclear, do not merge alternatives into one task using `or`, `task-dependent`, or `see Target Definition`. Split into multiple candidates, move the uncertainty to review notes, or delete the task.
4. If a task is only a possible research direction without a stable label source or epoch definition, do not keep it in `Tasks Area`; move it to review records or `Data Quality Notes`.

### Article 64. Downgrading

When an existing `Classical Task` no longer satisfies Article 62, downgrade it to `Potential Task` rather than keeping it as `Classical Task`.

### Article 65. Deletion

When a task depends on labels, events, or derivation paths that do not exist in the data and cannot be reconstructed by trusted stable rules, delete it.

### Article 66. Coexistence

One dataset may contain multiple `Classical Task` and multiple `Potential Task` entries, but each task must have independent and self-consistent support.

### Article 67. `Task Type`

`Task Type` may use only:

1. `classification`
2. `regression`

### Article 68. `Epoch Method`

`Epoch Method` may use only:

1. `epoch_by_event_hdf5`
2. `epoch_by_long_event_hdf5`
3. `epoch_by_segmentation_hdf5`

### Article 69. General Rule for `Epoch Parameters`

`Epoch Parameters` must include at least the parameters required by the selected `Epoch Method`; see Articles 70-72. The semantic rule `epoch_parameters_complete` in `detect.py` enforces this minimum set with severity `error` for both `Classical Task` and `Potential Task`.

Additional optional parameters accepted by `MNE.Epoch`, such as `baseline`, `reject`, or `picks`, may be added as `key = value` pairs and are not constrained by `epoch_parameters_complete`.

### Article 70. Required Parameters for `epoch_by_event_hdf5`

When using `epoch_by_event_hdf5`, provide at least:

1. `tmin`
2. `tmax`
3. `target_events`

### Article 71. Required Parameters for `epoch_by_long_event_hdf5`

When using `epoch_by_long_event_hdf5`, provide at least:

1. `tmin`
2. `tmax`
3. `overlap`
4. `target_events`

### Article 72. Required Parameters for `epoch_by_segmentation_hdf5`

When using `epoch_by_segmentation_hdf5`, provide at least:

1. `segment_length`
2. `overlap`

### Article 73. Parameter Sources

`Epoch Parameters` should be supported by `Evidence` when possible. If evidence does not provide all parameters, human reviewers and LLMs may choose the best explicit values conservatively, using this priority:

1. Recommended values from official pages or official documentation.
2. Actual values used in references that clearly use the dataset.
3. Reasonable values chosen by a reviewer or LLM based on domain knowledge.

Filled parameters must be explicit and directly implementable; do not replace them with vague placeholders.

### Article 74. Valid Sources for `target_events`

`target_events` in `Epoch Parameters` may only come from entries in `Event Structure` that explicitly exist and have `Type = event`.

### Article 75. No Invented `target_events`

If a task's `target_events` do not exist in `Event Structure`, or the corresponding entries have `Type = admin`, the task must not be treated as valid.

### Article 76. Human Review Handling

When `target_events` and `Event Structure` are inconsistent, human reviewers should do one of:

1. Adjust them to real existing labels.
2. Mark in the submission notes that a rescan is needed.
3. Delete the task.

### Article 77. `Label Route`

1. `Label Route` describes the source and storage form of the task's supervision signal. Legal values are:
   - `event`: supervision comes from the event stream, namely discrete events in `### Event Structure`, regardless of whether raw storage was annotation or stim channel.
   - `misc`: supervision is numeric or continuous and stored in a misc channel registered in `### MISC Label Summary`.
   - `info`: supervision comes from file-level subject or device properties registered in `### Info`, such as sex, age, or group.
2. `Label Route`, `target_events`, and `Target Definition` must be consistent:
   - `Label Route = event`: `Target Definition` uses an `Event ID -> y` mapping table.
   - `Label Route = misc`: `Target Definition` uses two columns, `MISC Channel Name` and `Y Mapping Notes`.
   - `Label Route = info`: `Target Definition` uses two columns, `Info Field` and `Y Mapping Notes`; see Article 77.2.
3. For `misc` and `info` routes, the label source is uniquely specified by the first column of `Target Definition`; do not additionally declare `Label Field`.
4. If a task is an exception, explain the reason in task `Notes`.

### Article 77.1. `misc` Route Usage: Epoch-Level Scalars and Continuous Values

1. The `misc` route stores epoch-level numeric labels, continuous quantities, or categorical labels mapped from channel values, such as `response_time`, ratings, density, duration, physiological indicators, or derived factor scores such as `p_factor`.
2. Epoch anchor events, which define epoch boundaries, are independent from the supervision-signal route. `Label Route = misc` does not prevent `Epoch Method` from using event anchoring or segmentation.
3. `misc` sources are of two kinds:
   - Native misc: a misc channel already present in raw files, or a numeric `events.tsv` column such as `response_time` that can be directly read and filled per segmentation. `Meta Level = raw`.
   - Derived misc: a misc channel newly created by the kernel from external tables, such as `participants.tsv` or companion files, or from derivation logic. Values are filled per segmentation, with subject-level values constant across all segmentations for that subject. `Meta Level = super`; Article 77.8 applies.
4. One dataset may contain multiple misc channels, such as `misc:p_factor`, `misc:externalizing`, or `misc:response_time`. Each task may reference only one; that channel name must appear in the first column of `Target Definition`.
5. Tasks using this route require `### MISC Label Summary` to register source, unit, alignment, and necessary derivation logic.

### Article 77.2. `Target Definition` Format for `Label Route = info`

1. When `Label Route = info`, `Target Definition` uses this format:

   | Info Field | Y Mapping Notes |
   |---|---|
   | `sex` | Male -> 0; Female -> 1 |

2. Values in `Info Field` must match field names registered in `### Info`.
3. If that field has `Completeness = missing`, `partial (x/n)`, or `incomplete`, the task cannot be a `Classical Task`; it may be at most a `Potential Task`, and task `Notes` should describe missingness.
4. The `info` route applies only to raw file-level fields directly exported by the kernel into `### Info`, such as sex, age, device, or native group. If median split, normalization, pairing, cross-file joining, or derivation is needed, use derived misc instead; see Articles 77.1 and 77.8.
5. `Y Mapping Notes` may freely describe how original values map to `y`. If `y` directly follows the field value, write `no mapping`.
6. Each `info` route task may use only one source field; therefore `Target Definition` may contain only one row.

### Article 77.3. `Label Field` and the Single-Source Rule

1. `Label Route = event` tasks do not use `Label Field`.
2. `Label Route` in `{misc, info}` tasks also no longer declare `Label Field`; the label source is specified by the first column of `Target Definition`.
3. The first column of `Target Definition` must be locatable inside the document:
   - `Label Route = misc`: it appears in the `Channel` column of `### MISC Label Summary`.
   - `Label Route = info`: it appears in the `Field` column of `### Info`.
4. For `misc` and `info`, the first column of `Target Definition` may contain only one unique value, and the table may contain only one row. This restriction does not apply to `event` tasks.

### Article 77.4. `Target Definition` Format Matrix

`Target Definition` table columns are determined by `Label Route x Task Type`:

| Label Route | Task Type | Header columns |
|---|---|---|
| `event` | `classification` | `\| Event ID \| y \| Meaning \|` |
| `event` | `regression` | `\| Event ID \| Value \| Meaning \|` (rare) |
| `misc` | `classification` | `\| MISC Channel Name \| Y Mapping Notes \|` |
| `misc` | `regression` | `\| MISC Channel Name \| Y Mapping Notes \|` |
| `info` | `classification` | `\| Info Field \| Y Mapping Notes \|` |
| `info` | `regression` | `\| Info Field \| Y Mapping Notes \|` |

1. Headers and column order must exactly match this matrix. LLMs and human reviewers must not add or remove columns.
2. For event routes, every `Event ID` cell must come from `### Event Structure`; see Article 74.
3. For `misc` and `info` routes, `Y Mapping Notes` may be `no mapping` when `y` equals the raw field or channel value, or may freely describe a custom conversion.

### Article 77.5. Single-Target Task Rule

1. Each task encodes one learning target: one task equals one supervision route and one target schema.
2. Multidimensional labels, such as psychological four-factor scores `internalizing/externalizing/attention/p_factor`, must be split into separate tasks. Each `misc` or `info` task may use only one `MISC Channel Name` or one `Info Field`.
3. `event` tasks may contain multiple `Event ID` rows when those rows jointly define a valid classification or regression mapping.
4. If one external evidence item covers multiple dimensions, reuse the same evidence in each split task instead of merging tasks.
5. For `misc` and `info`, the first column of `Target Definition`, namely `MISC Channel Name` or `Info Field`, may contain only one unique value within the task.
6. More complex composite tasks, such as a joint label built from multiple sources, may conceptually be expressed through combinations of simpler tasks. For consistency and brevity, this document currently defines no dedicated schema for complex tasks.

### Article 77.6. Mapping Requirements for the `misc` Route

1. `Label Route = misc` tasks may be `classification` or `regression`.
2. When `Task Type = classification` and the label comes from a misc channel, `Y Mapping Notes` must clearly explain how channel values map to class labels.
3. Thresholding, binning, median split, taking the first value, aggregation, or any other conversion on `misc` must be described in `Y Mapping Notes` or `Notes`.
4. If the misc channel itself is kernel-derived, Article 77.8 still applies.

### Article 77.7. Multiple-Class Requirement for `classification`

1. For `Task Type = classification`, the `y` column in `Target Definition` must contain at least two distinct values.
2. If evidence or data supports only a single class, for example only a cue-onset marker with no contrast class, change the task to `regression` when applicable or downgrade/delete it. Do not keep a one-class classification task.

### Article 77.8. Derived Misc Implies Super Meta

1. Any misc channel newly created by a kernel is derived data. Any task carried by it must have `Meta Level = super`, and `Super Meta Required = Yes`; see Article 37.
2. Derived misc must be explicitly declared as derived in `### MISC Label Summary`. It is recommended to describe derivation steps in task `Notes`, including source column, fill method per segmentation, units, and outlier handling. This recommendation is not enforced by `detect.py`; it is review and implementation guidance.
3. If the source field for derivation does not exist in the dataset, including `events.tsv`, `participants.tsv`, or native misc channels, the task is invalid and must be deleted.

### Article 78. `Meta Level`

1. `Meta Level = raw` means the task can be implemented from raw labels.
2. `Meta Level = super` means the task depends on additional derived, joined, or transformed labels.
3. If the label requires event pairing, class folding, subject-info mapping, standard-system mapping, or continuous-variable calculation, mark it `super`.

### Article 79. `Evidence`

1. `Evidence` presents external support for task validity or parameter choice.
2. `Classical Task` must provide `Evidence`.
3. `Potential Task` may provide `Evidence`, but it is not mandatory.
4. `Evidence` for `Classical Task` must be a specific locatable and identifiable source, not a vague placeholder.
5. If a DOI is unknown but an official page, competition page, or formal literature page is locatable, write that specific source instead of a vague phrase such as `DOI unknown`.

### Article 80. Evidence Review Focus

Human reviewers and LLMs should focus on:

1. Whether the evidence clearly used this dataset.
2. Whether the evidence clearly supports this task rather than only a similar task.
3. Whether label definitions in the evidence match the public data.

### Article 81. Hallucination Prevention

Because LLMs may hallucinate paper interpretations, any case that cannot be confirmed as both using this dataset and supporting the task should be downgraded or deleted rather than forced to remain a `Classical Task`.

### Article 82. Task `Notes`

From v3 onward, `- **Notes**:` inside a task block, formerly `Kernel Notes`, is free supplementary explanation with no forced structure and no `detect.py` enforcement. Common uses include:

1. Label mapping details, file-level context dependencies, or external table parsing requirements.
2. Event pairing, window-generation rules, or admin and pseudo-events to exclude.
3. Super-meta derivation steps; see Article 77.8.
4. Rationale for inferred `Epoch Parameters`; see Article 73.
5. Human judgment when `Classical Task` parameters differ from official or reference values.

Task `Notes` and `### Kernel Notes` under `## Kernel Responsibilities` are different: the former is free annotation for a single task; the latter is implementation-level, cross-task kernel memo. They may both exist, but should not be conflated.

## Chapter 11. Data Quality Notes Area

### Article 83. General Requirement

`Data Quality Notes Area` should use bullet points to record data quality issues, source conflicts, parsing risks, and use limitations.

### Article 84. Cases to Record

Record these cases when possible:

1. Official material conflicts with actual data.
2. Data are missing, excluded, empty, or lack events or fields.
3. Subject count, file count, channel count, or sampling rate differs from official description.
4. Event semantics depend on file-level context.
5. Some tasks are valid only for a subset of files.

### Article 85. Stance Requirement

When official material conflicts with real data, explicitly state that this document follows the real data.

### Article 86. No Exhaustiveness Requirement

This area does not need to list every issue, but human reviewers and LLMs should try to record quality issues that materially affect task validity.

## Chapter 12. References Area, Deprecated

### Article 87. Deprecation

1. `References Area` is a legacy section from early document versions.
2. Current `analysis.md` documents should normally not keep a standalone `References Area`.
3. Sources directly related to a task should be written under `Evidence` in the corresponding `Classical Task` or `Potential Task`.
4. Sources related to data conflicts, quality issues, or review decisions should be written in the relevant note or review record, not separately summarized as `References Area`.

### Article 88. Transition Rule

1. Historical documents may temporarily keep `References Area`.
2. Once a document is substantially revised, remove that section unless maintainers explicitly request otherwise.
3. LLMs should not add `References Area` when generating new versions.

## Chapter 12.1. STIM Label Summary Transition Rule

### Article 88.1. Deprecation

1. `STIM Label Summary` is a v0.1 legacy section and is deprecated from v0.2 onward.
2. All discrete events from trigger or stim channels should be registered in `Event Structure`, with `Type` set to `event` or `admin`.
3. Deprecated `Event Structure.Type` values `short`, `long`, and `rest` are also no longer used from v0.2 onward. Their information is now represented by `Epoch Method` in `Tasks Area`.

### Article 88.2. Existing-Document Transition

1. Existing historical `STIM Label Summary` sections do not have to be migrated immediately.
2. Once a document is substantially revised, migrate discrete events from `STIM Label Summary` into `Event Structure` and delete `STIM Label Summary`.
3. Existing `Event Structure` rows with `Type` equal to `short`, `long`, or `rest` should be rewritten to `event` during substantial revision; `admin` remains unchanged.
4. LLM review scripts must not add `STIM Label Summary` or use deprecated `Event Structure.Type` enum values when generating or revising documents.

# Part III. Supplementary Rules

## Chapter 13. Placeholders, Format, and Style

### Article 90. Allowed Placeholders

When specific information cannot be determined, use:

1. `Needs verification`
2. `Variable`
3. `N/A`
4. `null`

These placeholders should normally not be used in key fields of `Classical Task`.

### Article 91. Preserve Raw Names

When raw event names, raw code values, or raw labels can be used directly, preserve them as-is. Do not rename them merely for language polish.

### Article 92. Style

Documents should be technical, factual, and executable. Avoid promotional, exaggerated, or unverifiable conclusions.

## Chapter 14. Review Action Types

### Article 93. Review Actions

Later human and LLM reviews may use these action categories:

1. `keep`
2. `correct`
3. `downgrade`
4. `delete`
5. `mark Needs verification`
6. `mark rescan required`
7. `mark kernel correction required`

### Article 94. Action Use

1. If a field adjustment can solve the problem, prefer `correct`.
2. If task evidence is insufficient but the data support the task, prefer `downgrade`.
3. If the label source does not exist or cannot be reconstructed stably, use `delete`.
4. If the parsing chain has an obvious programmatic issue, mark `rescan required` or `kernel correction required`.

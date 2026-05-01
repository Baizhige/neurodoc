# EEG Dataset Kernel Authoring and Maintenance Rules

Status: Draft v0.1

Last confirmed: 2026-04-08

Applies to: kernel authors (human, LLM), maintainers (human, LLM)

Scope: All kernel files under the `neurodoc/kernels/` directory

---

# Part I  General Provisions

## Chapter 1  Purpose and Scope

### Article 1  Purpose

These rules establish a unified standard for authoring, maintaining, and extending EEG dataset kernel files, ensuring that kernel files can:

1. Remain compatible with the current EEGUnity interface specification.
2. Restore, as accurately as possible, channel information that is missing or encoded inconsistently in the original data.
3. Provide EEGUnity with standardized subject and device metadata.
4. Output a normalized label structure that supports dynamic instantiation of raw meta and super meta.
5. Serve as a maintainable, augmented data container that records the source, addition date, and attribution for all information not derived from the original data.

### Article 2  Scope of Application

These rules apply to the following operations on all kernel files under `neurodoc/kernels/`:

1. Creation and initialization.
2. Manual extension or LLM-assisted extension.
3. Audit and review.

### Article 3  Basic Principles

1. **Interface compatibility first**: a kernel must remain compatible with the current version of EEGUnity / MNE interfaces and must not introduce custom wrappers that break standard interfaces.
2. **Source traceability**: all information in a kernel file that does not originate from the raw data must have its source, annotator, and date recorded in an immediately adjacent code comment.
3. **LLM honesty principle**: an LLM must not label any information as if it were a human. Unless explicitly instructed by a human, all content added by an LLM must be marked "inferred by LLM, needs human review".

---

# Part II  Interface Specification

## Chapter 2  EEGUnity Kernel Interface

### Article 4  Interface Reference Standard

Kernel files must comply with the current EEGUnity kernel interface specification. These rules do not redefine interface details; maintainers should consult EEGUnity's relevant functions and documentation (including but not limited to `UnifiedDataset.eeg_parser`, `EEGBatch`, and its kernel loading mechanism) to confirm the latest interface requirements.

### Article 5  Interface Consistency Requirements

1. A kernel file must expose a module-level `KERNEL` object for EEGUnity to load and call.
2. The core method signatures and return values of a kernel must remain consistent with the current version of EEGUnity; if an EEGUnity upgrade changes the interface, the kernel file must be updated in sync.
3. Helper functions and data structures internal to a kernel file are not constrained by the interface, but must not affect the standard behavior of the `KERNEL` object.

---

# Part III  Channel Information Restoration

## Chapter 3  Channel Information

### Article 6  Obligation to Restore Channel Information

1. A kernel should, wherever possible, restore channel names that are encoded inconsistently or missing in the original data to standard names (e.g., `EEG-0` -> `FC3`). The restoration basis should come from papers, dataset documentation, or official materials from the dataset provider.
2. Channel type resolution relies on EEGUnity's `format_channel_name()` function; a kernel is **not required** to explicitly set `type` for every channel. If a kernel does call `set_channel_types()`, its results must be consistent with the resolution results of `format_channel_name()` and must not contradict them.
3. If the original data uses a standard cap (e.g., standard_1020), the kernel should call `set_montage()` after channel renaming to set spatial position information.
4. If the original data uses a non-standard cap or the electrode layout cannot be confirmed, the montage setting may be skipped, but the reason must be stated in a comment at the top of the kernel file.

### Article 7  Channel Information from Non-Original Sources

1. Channel remapping information in a kernel file that does **not come from the raw data files themselves** (i.e., sourced from papers, dataset documentation, manual annotation, LLM inference, or other external sources) must be annotated at the corresponding code location with:
   - **Source**: paper (with citation or DOI), dataset README (with path), manual instruction, etc.
   - **Annotator**: human reviewer (with name or ID) or LLM (with model identifier).
   - **Date**: the date the information was added (ISO format, e.g., `2026-04-08`).
2. If filled in by an LLM, the annotation must additionally state "inferred by LLM, needs human review". After a human reviewer confirms, the mark may be removed and the annotator updated to the human.
3. An LLM must not label any channel information as if it were a human, unless an explicit written instruction from a human has been received.

---

# Part IV  Subject and Device Metadata

## Chapter 4  eegunity_description Format

### Article 8  Write Path

Subject and device metadata must be written as a JSON string into `raw.info["description"]` in the following format:

```json
{
  "original_description": "<original description field value, string>",
  "eegunity_description": {
    "age": "<str>",
    "sex": "<str>",
    "amplifier": "<str>",
    "cap": "<str>",
    "handedness": "<str>"
  }
}
```

`original_description` should retain the value of the original `raw.info["description"]` (if the original value is empty, write an empty string).

### Article 9  Required Fields

All of the following fields in `eegunity_description` are **required** and must not be omitted:

| Field | Meaning | Valid values |
|-------|---------|--------------|
| `age` | Subject age | Positive integer string (`"22"`); or range string (`"22-45"`); write `"unknown"` if unknown |
| `sex` | Subject sex | `"female"` or `"male"`; write `"unknown"` if unknown |
| `amplifier` | Recording device model | Device name string (e.g., `"BrainAmp"`); write `"unknown"` if unknown |
| `cap` | Electrode cap material or model | Material string (e.g., `"Ag/AgCl"`); write `"unknown"` if unknown |
| `handedness` | Handedness | `"right"`, `"left"`; write `"unknown"` if unknown |

All fields must **appear** regardless of whether the value is known. Unknown values must always be written as the string `"unknown"`; do not write `null`, an empty string, or Python `None`.

### Article 10  age Field Conventions

1. `age` is stored uniformly as a string (`str`); integer or float types must not be used.
2. If the exact age is known, write a positive integer string, e.g., `"22"`.
3. If only an age range is known (e.g., a paper states "22-45 years old"), write a range string in the format `"<lower>-<upper>"`, e.g., `"22-45"`; both ends are positive integers joined by an ASCII hyphen `-`.
4. Write `"unknown"` if the age is unknown; do not write `"0"` or a negative number string.

### Article 11  Source Annotation for Subject Information

1. If the value of any field in `eegunity_description` comes from external materials (papers, dataset documentation, manual entry), the source, annotator, and date must be stated in a comment adjacent to the corresponding subject dict or assignment code in the kernel file.
2. If filled in by an LLM, all field values must be set to `"unknown"` and annotated "inferred by LLM, needs human review", unless explicit human instructions providing specific values have been received.
3. An LLM must not fill in substantive values such as age and sex in a subject dict without human instruction.

---

# Part V  Label Standardization

## Chapter 5  Label Form and Responsibilities

### Article 12  Kernel Label Responsibilities

The kernel is responsible for normalizing label information from the raw data into a format that can be stably parsed by EEGUnity / MNE. Specific responsibilities include:

1. Mapping numerically encoded annotations from the original data to human-readable description strings.
2. Ensuring output labels can be stably parsed by `mne.events_from_annotations()`.
3. If a dataset's labels originate from a STIM channel or MISC channel, the kernel may choose to convert them to annotation form for output, or retain the original channel form, but must state the rationale in a comment in the kernel file.

### Article 13  raw meta

1. **raw meta** (corresponding to `Meta Level = raw` in `analysis.md`): labels output by the kernel correspond directly to event codes in the raw data, normalized in name but without introducing any semantic derivation.
2. raw meta is the foundational layer that all kernels **must implement**; it must not be absent.
3. The description strings of raw meta events should be consistent with the `Event ID` column of the `### Event Structure` table in the dataset's `analysis.md`; if there is an inconsistency, the kernel's actual output takes precedence and `analysis.md` should be corrected in sync.

### Article 13-1  Paradigm Prefix Convention for Multi-Paradigm Datasets

When a single dataset contains **multiple paradigms** and there are **overlapping event codes** between different paradigms (i.e., the same numeric code represents different semantics in different paradigms), the kernel should prepend a paradigm identifier prefix to all event description strings to eliminate ambiguity.

1. **Trigger condition**: the same dataset contains multiple paradigms and their event codes overlap (e.g., both CLA and HaLT use code 1 for left-hand MI, but NoMT uses code 1 for left-hand cue).
2. **Prefix format**: `<PARADIGM>: <event_label>`, where `<PARADIGM>` is the paradigm name (uppercase or the abbreviation defined by the dataset convention) and `<event_label>` is the semantic description of that code in that paradigm. Examples: `CLA: left hand MI`, `HaLT: right hand MI`, `NoMT: left hand cue`.
3. **Classification basis**: such labels are still classified as **raw meta**, because the paradigm identifier comes from the original filename or path prefix and introduces no semantic inference; prefix extraction is essentially filename parsing, not semantic derivation.
4. **Admin codes**: if a dataset contains administrative marker codes whose purpose is unclear (e.g., 91 / 92 / 99), until their specific meaning is confirmed, use the format `admin: marker-<code>` uniformly, **without a paradigm prefix**, to indicate their cross-paradigm shared nature, and document the known observed patterns in a comment at the top of the kernel file.
5. **Synchronization requirement**: the introduction of paradigm prefixes must be accompanied by an update to the `### Event Structure` table in the dataset's `analysis.md`, ensuring the `Event ID` column matches the kernel's actual output.
6. **Paradigm detection logic**: the kernel file should provide an independent paradigm detection function (e.g., `_detect_paradigm(file_name)`) that matches based on filename prefixes, and the detection order should be stated in a comment at the top of the kernel file (e.g., FREEFORM must be checked before FREE or CLA to avoid prefix ambiguity).

```python
# Example: paradigm prefix event mapping table
_PARADIGM_LABEL_MAP = {
    "CLA": {1: "CLA: left hand MI", 2: "CLA: right hand MI"},
    "HaLT": {1: "HaLT: left hand MI", 2: "HaLT: right hand MI",
             91: "admin: marker-91"},  # admin codes: no paradigm prefix
    "NoMT": {1: "NoMT: left hand cue"},  # passive cue, not MI
}
```

### Article 14  super meta

1. **super meta** (corresponding to `Meta Level = super` in `analysis.md`): the kernel may further construct semantically derived labels on top of raw meta, for example by combining multiple raw events into higher-level trial types, or by introducing external information to annotate events.
2. super meta and raw meta use the same storage form (both written into MNE Raw annotations or corresponding channels).
3. The introduction of super meta **must** be consistent with the `Meta Level` field of the corresponding task in the `Tasks Area` of the dataset's `analysis.md` (see the relevant articles of the main rulebook `neuroaudit/rulebook.md`). A kernel must not unilaterally introduce super meta labels not declared in `analysis.md`.
4. An LLM may infer and construct super meta based on the content of `analysis.md`, but must clearly annotate "constructed by LLM" in the kernel file and state the inference basis; only after a human reviewer confirms may the "needs human review" mark be removed.
5. The construction logic of super meta should be clearly annotated in the kernel file using an independent data structure or comment block, and must not be interleaved with raw meta logic without distinguishing comments.

---

# Part VI  Static Enhancement Data and External Resources

## Chapter 6  Enhancement Data in Kernel Files

### Article 15  Non-Original Data Allowed in Kernel Files

Kernel files are allowed to contain the following types of static enhancement data:

| Data type | Typical example | Recommended naming style |
|-----------|----------------|--------------------------|
| Subject information dictionary | `_SUBJECT_DICT` | Underscore-prefixed private variable |
| Channel remapping table | `_CHANNEL_RENAME_MAP`, `alias_groups` | Underscore-prefixed private variable |
| Event code mapping table | `_NUMERIC_EVENT_MAP` | Underscore-prefixed private variable |
| super meta construction rules | `_SUPER_META_RULES` | Underscore-prefixed private variable |
| Device / cap information | Hardcoded string constants | Uppercase constant or embedded in subject dict |

All of the above data are considered legitimate components of the kernel file. The presence of data implies that it has been (or is pending) review by a human or LLM, and must be accompanied by a source comment (see Article 16).

### Article 16  Reading External Files

1. Kernel files are allowed to read external files (e.g., `.json`, `.csv`, `.mat` files in the same directory or at a specified path) to supplement or replace hardcoded data.
2. When reading external files, a comment in the kernel file must state the purpose, format, and source of the external file.
3. The external file reading logic must not break the kernel's interface compatibility: even if an external file is missing, the kernel must have a reasonable fallback (e.g., fall back to built-in defaults, or raise an error with a clear explanation).

### Article 17  Source Comment Standards

For all information in kernel files that does not originate from the raw data, the following must be stated in an **immediately adjacent code comment**:

1. **Source**: paper (with citation or DOI), dataset documentation (with path or URL), manual entry, LLM inference, etc.
2. **Annotator**: human reviewer (with name or abbreviation) or LLM (with model identifier, e.g., `claude-sonnet-4-6`).
3. **Date**: the date the information was added or last confirmed (ISO format, e.g., `2026-04-08`).
4. When annotated by an LLM, "needs human review" must be additionally noted; after a human reviewer confirms, the human updates the annotator to themselves and removes the "needs human review" mark.

Example comment format (Python):

```python
# Source: BCI Competition IV Dataset 2a description, https://www.bbci.de/competition/iv/
# Annotator: [human-reviewer-id], 2026-04-08
_SUBJECT_DICT = { ... }

# Source: Inferred from channel naming convention in dataset README
# Annotator: claude-sonnet-4-6, 2026-04-08 — needs human review
_CHANNEL_RENAME_MAP = { ... }
```

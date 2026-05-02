# EEG Corpus, NeuroDoc, and NeuroAudit

This repository is an EEG dataset corpus with two companion tools:

- `dataset_document/` stores curated dataset documentation in `analysis.md` format.
- `neurodoc/` generates, scans, upgrades, and validates dataset kernels and documentation.
- `neuroaudit/` supports human review and lightweight editing of existing dataset documents.

The repository is designed for two main audiences:

1. People who want to use the corpus as a resource for understanding EEG datasets.
2. People who want to contribute documentation, review fixes, or new dataset kernels.

## If You Want to Use the Corpus

Start from `dataset_document/`.

Each dataset folder typically contains:

- `analysis.md`: a structured dataset description, including paradigm, scanned event structure, metadata fields, task definitions, and quality notes
- reference files such as papers, README exports, or official webpages when available

If a dataset has a dedicated kernel, it is stored in:

- `neurodoc/kernels/<dataset>.py`

These kernels are dataset-specific normalization and parsing resources used by the documentation workflow. If you want to export machine-learning tasks from these kernels, please refer to the EEGUnity repository for downstream task construction and data export workflows.

Suggested reading path for corpus users:

1. Open `dataset_document/<dataset>/analysis.md`
2. Check the `Paradigm` and `File Scan Result` sections first
3. Review the `Tasks` section if you want task-oriented summaries
4. Open `neurodoc/kernels/<dataset>.py` if you need to inspect how the dataset is normalized or annotated

## If You Want to Contribute

There are two common contribution paths.

### Light Document and Task Review

Use `neuroaudit/` if you want to:

- review existing dataset documents
- lightly edit wording or task definitions
- validate document structure and reviewer-facing rules
- regenerate task sections during review

Start here:

- [neuroaudit/README.md](neuroaudit/README.md)

### New Datasets, Kernel Work, or Re-Scanning

Use `neurodoc/` if you want to:

- add support for a new dataset
- write or fix a dataset kernel
- regenerate or re-scan `analysis.md`
- apply `[to_agent: ...]` upgrade instructions
- run semantic validation across the corpus

Start here:

- [neurodoc/README.md](neurodoc/README.md)

## Repository Map

- `dataset_document/`
  - the corpus itself; one folder per dataset
- `neurodoc/`
  - kernel generation, scanning, validation, and upgrade pipeline
- `neuroaudit/`
  - local review UI for existing dataset documents
- `Script/`
  - supporting and archived automation; not the main entry point for most users

## Recommended Reading Order

For corpus users:

1. `dataset_document/<dataset>/analysis.md`
2. `neurodoc/kernels/<dataset>.py`
3. `dataset_document/<dataset>/references/` when present

For light contributors:

1. [neuroaudit/README.md](neuroaudit/README.md)
2. `neuroaudit/rulebook.md`
3. the target `dataset_document/<dataset>/analysis.md`

For kernel contributors:

1. [neurodoc/README.md](neurodoc/README.md)
2. `neurodoc/kernels/KERNEL_RULEBOOK.md`
3. the target `neurodoc/kernels/<dataset>.py`
4. the target `dataset_document/<dataset>/analysis.md`

## Related Documentation

- [neurodoc/README.md](neurodoc/README.md)
- [neuroaudit/README.md](neuroaudit/README.md)
- [Script/README.md](Script/README.md)
- [AGENTS.md](AGENTS.md)


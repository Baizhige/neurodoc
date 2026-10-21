# Paper artifact supplement

This directory archives the supplement provided during peer review and retained in
the NeurIPS 2026 camera-ready artifact snapshot. It is intended to help readers inspect
the scripts, aggregate experiment records,
representative raw logs, and exported figures that support the paper.

The contents here were copied from the paper working directory and organized for audit.
They are not meant to replace the original full experiment workspace.

In particular, this supplement includes material for both:

- the experiment-result and figure-generation workflow used by the manuscript
- the NeuroDoc generation-quality experiment described in the appendix

## Curation Principle

The original paper workspace contains much more material, including many intermediate
artifacts, cache files, and large volumes of launcher or console logs. To keep the
review branch lightweight and easier to audit, this folder includes only:

- key plotting and export scripts used for paper-facing assets
- aggregate scheduler outputs used by those scripts
- representative run folders that expose raw training and evaluation logs
- exported figure snapshots for quick inspection

This folder is therefore a review-oriented package rather than a full archival dump.

## Directory Guide

### `pull_data_script/`

Selected scripts and appendix exports copied from the paper workspace:

- `plot_data_agent_main_figure.py`
- `stats_analysis_docs.py`
- `export_doc_latex.py`
- `export_rulebooks_latex.py`
- `appendix_documents.tex`
- `appendix_neuroaudit_rulebook.tex`
- `appendix_semantic_rules.tex`

These files are included because they directly support the summary tables, figures,
or appendix material discussed in the manuscript.

### `experiment_data/scheduler/`

This folder contains the main aggregate experiment bookkeeping files for the
execution-validation package reported in the manuscript. In the anonymous review
branch, it is organized around:

- 266 runs
- 18 datasets
- 37 benchmark tasks
- 4 backbone families: BENDR, CBraMod, CodeBrain, and LaBraM

The folder includes:

- `summary.json`
- `task_status.csv`
- `task_manifest.json`
- `state.json`
- `scheduler.log`

For review purposes, this is the most important summary-level evidence because it
records the reported task inventory and execution state consumed by the analysis
scripts. The `scheduler.log` file in this release is a short package note rather
than the original full scheduler runtime log.

### `experiment_data/representative_runs/`

This folder contains representative run directories so reviewers can inspect raw
per-run artifacts without requiring the entire large experiment directory.

The selected runs were chosen to cover multiple datasets, task types, and backbone
families. In addition, the examples align with the current selection logic used by
`plot_data_agent_main_figure.py`, especially the functions that choose:

- learning-curve examples
- gallery examples shown in the main figure pipeline

This keeps the review supplement tied to the actual plotting workflow rather than an
ad hoc manual sample.

To avoid Windows path-length failures, each checked-in directory uses a short
`run_<numeric-id>` name. [`manifest.csv`](experiment_data/representative_runs/manifest.csv)
maps those directory names to the original immutable run identifiers stored inside
the raw JSON records.

### `figures_snapshot/`

This folder contains exported figure files copied for quick visual inspection:

- `data_agent_main_figure.png`
- `data_agent_main_figure.svg`
- `doc_resource_overview_completed_only.png`

These snapshots are included so a reviewer can inspect the main outputs directly
without first rerunning the plotting scripts.

### `quality_test/`

This folder contains the raw batch outputs for the NeuroDoc generation-quality
experiment described in the appendix section
`NeuroDoc Generation Quality Characterization`.

The experiment was run with `Kimi-K2.6`. In the saved batch metadata, the model
name appears as `kimi-for-coding`; this was the runtime label used during the
experiment for the same Kimi-K2.6 setup.

The folder currently contains two experiment batches:

- `kimi-for-coding_20260505_0422` with 33 datasets
- `kimi-for-coding_20260506_1309` with 10 datasets

Together they cover 43 datasets, matching the appendix-level evaluation scale.

The included files are organized as raw experiment evidence:

- `run_generation_batch.py`: the batch runner used to regenerate completed datasets
  into an isolated experiment directory without overwriting `dataset_document/`
- `batch_info.json`: per-batch metadata, including dataset lists and run settings
- `generated_docs/`: generated NeuroDoc draft outputs for that batch
- `kernels/`: kernels produced during the generation run
- `logs/`: per-dataset runtime logs
- `cache/`: intermediate pipeline state used during generation

The `references/` subdirectories that originally appeared under some
`generated_docs/<dataset>/` folders were removed from this release because they
contained downloaded PDF papers and HTML pages that cannot be redistributed here.
See `quality_test/deleted_reference.md` for the removed-file record and examples.

### `reference_relevance_report.csv`

This CSV is a raw reference-screening record from one stage of the documentation
pipeline. It captures LLM-assisted relevance classification decisions for candidate
references at the dataset level.

The file includes columns such as:

- `dataset`
- `reference_file`
- `category`
- `reason`
- `text_length`
- `text_pages_read`
- `file_type`
- `cot_reasoning`
- `llm_reviewed`

It is included as process evidence rather than as a polished paper table. In other
words, this file reflects an intermediate classification stage that helped decide
whether a reference was considered relevant or irrelevant for dataset-specific
documentation and evidence gathering.

## Notes

- The materials here were copied into this repository for review and audit convenience.
- The original, larger paper workspace remains outside this repository.
- This supplement is intentionally lightweight and should be read together with the
  main repository code and manuscript.
- Absolute paths appearing inside raw logs or cache records are inert runtime
  provenance from the original compute environment; they are not required for use
  of the released corpus and do not imply that those local paths are publicly available.

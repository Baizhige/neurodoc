## NeuroDoc Croissant Package

This folder contains a submission-ready Croissant package for the NeurIPS 2026
Evaluations and Datasets Track.

### Scope

The Croissant file describes the review release of the NeuroDoc EEG benchmark
corpus used in the paper:

- `53` completed benchmark entries
- `245` task definitions
- benchmark metadata and task-interface summaries derived from the released
  `analysis.md` documents and paired kernels

This package describes the benchmark corpus as a derived documentation and task
resource. It does not redistribute raw EEG recordings.

### Files

- `neurodoc_eeg_benchmark_corpus_53.croissant.json`
  - main Croissant metadata file (conforms to Croissant 1.1 + RAI 1.0)
- `documents_53.csv`
  - one row per completed benchmark entry (53 rows)
- `tasks_245.csv`
  - one row per task definition belonging to the completed entries (245 rows)

### Important assumption

The dataset URL used in the Croissant file is:

- `https://anonymous.4open.science/r/anonymous_reviewe_neurodoc`

This package assumes that the anonymous review branch exposes the released
benchmark resources from the `BIDS_description` repository, including
`dataset_document/<dataset_name>/analysis.md` and the corresponding
dataset-specific kernels.

### Validation note

The Croissant file references `documents_53.csv` and `tasks_245.csv` via local
relative paths. Keep these three files together when running a validator or
when packaging them into a ZIP for OpenReview upload.

### Provenance

`documents_53.csv` and `tasks_245.csv` were generated from the local benchmark
summary tables in:

- `pull_data_script/docment_figures/tables/documents.csv`
- `pull_data_script/docment_figures/tables/tasks.csv`

They were filtered to the completed release subset and cleaned to remove local
absolute paths. SHA256 hashes in the Croissant JSON were computed after export.

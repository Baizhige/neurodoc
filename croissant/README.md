# NeuroDoc Croissant package

This directory contains the Croissant package for the NeurIPS 2026 camera-ready release of the NeuroDoc EEG Benchmark Corpus.

## Scope

- 53 human-reviewed `completed` benchmark entries
- 134 classical tasks
- 111 potential tasks
- 245 task definitions in total

The package describes derived benchmark documents, task interfaces, and provenance. It does not redistribute raw EEG recordings. Source-data access and use remain governed by the original providers and licenses.

## Files

- `neurodoc_eeg_benchmark_corpus_53.croissant.json`: Croissant 1.1 and RAI 1.0 metadata
- `documents_53.csv`: one row per released benchmark entry
- `tasks_245.csv`: one row per released task definition

The two CSV files are derived from the reviewed `analysis.md` documents in this snapshot. Their SHA256 values are recorded in the Croissant JSON.

## Public locations

- Repository: <https://github.com/Baizhige/neurodoc/>
- Camera-ready branch: <https://github.com/Baizhige/neurodoc/tree/camera-ready-snapshot>
- Project website: <https://neurodoc.eeg.fm>

## Validation

Keep the JSON and both CSV files together for local validation. Before uploading the Croissant file to OpenReview, validate this exact package with the current MLCommons Croissant validator and confirm that the public distribution URLs resolve without authentication.

## Provenance

This package is derived from the peer-review artifact at commit `eeede588ff2d3c0c07c20a58e150e5f6fd122573`. Camera-ready changes restore public attribution, public URLs, and release metadata without expanding the reviewed 53-entry/245-task scope.

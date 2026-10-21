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

The two CSV files are derived from the reviewed `analysis.md` documents in this snapshot. Their lowercase SHA-256 values are recorded in the Croissant JSON and match the exact bytes served by the public `raw.githubusercontent.com` URLs.

## Public locations

- Repository: <https://github.com/Baizhige/neurodoc/>
- Camera-ready branch: <https://github.com/Baizhige/neurodoc/tree/camera-ready-snapshot>
- Project website: <https://neurodoc.eeg.fm>

## Validation

The uploaded metadata file is `neurodoc_eeg_benchmark_corpus_53.croissant.json`. Its two distributions use branch-pinned public URLs, so OpenReview's validator can download and verify the release tables without authentication.

Validate the exact file with MLCommons `mlcroissant` 1.1.1 or newer:

```bash
mlcroissant validate --jsonld croissant/neurodoc_eeg_benchmark_corpus_53.croissant.json
mlcroissant load --jsonld croissant/neurodoc_eeg_benchmark_corpus_53.croissant.json --record_set documents-recordset --num_records 3
mlcroissant load --jsonld croissant/neurodoc_eeg_benchmark_corpus_53.croissant.json --record_set tasks-recordset --num_records 3
```

## Provenance

This package is derived from the peer-review artifact at commit `eeede588ff2d3c0c07c20a58e150e5f6fd122573`. Camera-ready changes restore public attribution, public URLs, and release metadata without expanding the reviewed 53-entry/245-task scope.

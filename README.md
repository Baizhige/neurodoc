<div align="center">

<img src="_docs/NeuroDoc_logo.png" width="88" alt="NeuroDoc"/>

# NeuroDoc EEG Benchmark Corpus

**Rulebook-guided candidate generation, executable task specifications, and structured human review for public EEG datasets**

[![NeurIPS 2026](https://img.shields.io/badge/NeurIPS%202026-camera--ready-7B2CBF?style=flat-square)](RELEASE.md)
[![Datasets](https://img.shields.io/badge/released%20entries-53-4CAF50?style=flat-square)](_docs/corpus_index.md)
[![Tasks](https://img.shields.io/badge/task%20definitions-245-1976D2?style=flat-square)](croissant/tasks_245.csv)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](neurodoc/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey?style=flat-square)](LICENSE)

</div>

This branch is the public, de-anonymized artifact snapshot accompanying the NeurIPS 2026 Evaluations and Datasets paper **“EEG Benchmarking Needs a Task Specification Layer: NeuroDoc for Rulebook-Guided, Executable Benchmark Construction.”**

- Project website: <https://neurodoc.eeg.fm>
- Code and dataset-metadata repository: <https://github.com/Baizhige/neurodoc/>
- Camera-ready snapshot: `camera-ready-snapshot`
- Review-snapshot provenance: `anonymous@eeede588ff2d3c0c07c20a58e150e5f6fd122573`

The scientific scope is intentionally frozen to the artifact evaluated during review. Ongoing community development may continue on `main`; later additions or corrections are not silently folded into this snapshot.

## Release scope

| Item | Camera-ready snapshot |
|---|---:|
| Attempted workspaces | 286 |
| Human-reviewed `completed` entries | 53 |
| Classical tasks | 134 |
| Potential tasks | 111 |
| Total task definitions | 245 |
| Awaiting manual review | 200 |
| Awaiting kernel update | 31 |
| Operational failures | 2 |
| `hallucination` terminal status | 0 |

The 53 released entries are the reviewed subset, not an autonomous-generation success rate. Potential tasks are data-supported candidate formulations whose scientific meaningfulness was not externally or empirically validated to the same degree as literature-established classical tasks.

## What the repository contains

Each corpus entry pairs:

1. a structured `dataset_document/<dataset>/analysis.md` document describing provenance, events, metadata, tasks, evidence, and known limitations; and
2. a dataset-specific normalization kernel under `neurodoc/kernels/`.

The repository does **not** redistribute raw EEG. Users obtain source data from the original providers and remain responsible for the provider's current license, data-use agreement, registration, or approval requirements.

Two tools support the workflow:

- **NeuroDoc** generates and repairs rulebook-constrained candidate documents and kernels. It reduces drafting effort but does not certify scientific validity or replace domain experts.
- **NeuroAudit** provides a browser-based interface for human inspection, correction, validation, and release decisions.

Execution demonstrates that an entry can be consumed by the supported pipeline. It is not, by itself, proof of semantic faithfulness, a protocol-identical reproduction of prior work, or a contamination-controlled universal ranking of EEG models.

## Browse and use the corpus

- [Corpus index: 53 released entries](_docs/corpus_index.md)
- [Corpus-user tutorial](_docs/tutorial_corpus_user.md)
- [Croissant metadata package](croissant/README.md)
- [NeuroDoc documentation](neurodoc/README.md)
- [NeuroAudit documentation](neuroaudit/README.md)
- [Release and provenance record](RELEASE.md)

```bash
git clone https://github.com/Baizhige/neurodoc.git
cd neurodoc
git switch camera-ready-snapshot
python -m pip install -r requirements.txt
python -m neurodoc.detect --completed-only --severity error
```

PyTorch is intentionally not pinned in `requirements.txt` because the correct wheel depends on the user's operating system and CPU/CUDA configuration. Install the appropriate PyTorch build before using `neurodoc.dataset_api`; install `requirements-dev.txt` to run the test suite.

For advanced EEGUnity setup and preprocessing, see <https://eegunity.readthedocs.io/>.

## Human review and governance

The initial release was reviewed by eight trained reviewers recruited through targeted invitations based on EEG-processing experience. Reviewers completed three 30-minute training sessions and used a 22-item checklist covering metadata and paradigm, file scans and task semantics, data-quality notes, and kernel responsibilities.

Each released entry received review by at least one human reviewer and one repository administrator. Human review was independent of automated drafting, but entries did not receive independent multiple ratings and no inter-rater agreement statistic was collected. Disagreements were discussed; unresolved cases were adjudicated by a repository administrator and documented in Data Quality Notes when applicable. A reviewer cannot override a blocking validation error.

A complete draft-to-`completed` cycle typically required approximately 2–3 person-hours. For one review round, the recorded median was 40 minutes, the mean was approximately 46 minutes, and the range was 30–85 minutes across seven respondents.

The release detector applies 46 rules and 23 cross-checks. Admission as `completed` requires zero blocking validation errors and final human approval.

For contribution procedures, see:

- [Reviewer and document-contributor guide](_docs/tutorial_reviewer.md)
- [Kernel and dataset-contributor guide](_docs/tutorial_contributor.md)
- [Contributor and reviewer attribution](CONTRIBUTORS.md)

## Repository map

```text
neurodoc/
├── dataset_document/       # Structured corpus documents
├── neurodoc/               # Candidate-generation, validation, and kernel code
│   └── kernels/            # Dataset-specific normalization kernels
├── neuroaudit/             # Human review interface and rulebook
├── croissant/              # Croissant JSON plus 53-entry and 245-task tables
├── other_data_for_review/  # Archived paper-facing audit evidence
├── _docs/                  # Corpus index and tutorials
├── CITATION.cff
├── CONTRIBUTORS.md
└── RELEASE.md
```

## Citation and license

Citation metadata are provided in [CITATION.cff](CITATION.cff). The repository's code, documentation, and derived metadata are released under [CC BY-NC 4.0](LICENSE). That license does not replace or modify the licenses and access conditions of upstream EEG datasets.

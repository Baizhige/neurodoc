<div align="center">

<img src="_docs/NeuroDoc_logo.png" width="88" alt="NeuroDoc"/>

# EEG Benchmark Skill

**An open EEG dataset corpus with automated documentation and community review tooling**

[![Datasets](https://img.shields.io/badge/datasets-55%20completed-4CAF50?style=flat-square)](dataset_document/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/EEG-BenchmarkSkill/EEGBenchmarkSKILL/pulls)
[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](neurodoc/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey?style=flat-square)](LICENSE)
[![NeurIPS 2026 Camera-ready Snapshot](https://img.shields.io/badge/NeurIPS%202026-camera--ready%20snapshot-4B44CE?style=flat-square)](https://github.com/Baizhige/neurodoc/tree/camera-ready-snapshot)

</div>

---

This repository is a curated corpus of EEG datasets, each paired with a structured `analysis.md` document and a dataset-specific normalization kernel. Two companion tools power the workflow:

- **NeuroDoc** — automated three-phase LLM pipeline that generates kernels and documentation from scratch
- **NeuroAudit** — browser-based review UI for human contributors to inspect, edit, and validate documents

---

## 🚀 Quick Navigation

<table>
<tr>
<td align="center" width="33%">

### 📚 Use the Corpus

Browse `analysis.md` files and kernels as a research reference. No setup required.

[**Get started ↓**](#-use-the-corpus)

</td>
<td align="center" width="33%">

### 🔍 Review & Contribute

Review documents, improve task definitions, and submit fixes via NeuroAudit.

[**Reviewer tutorial →**](_docs/tutorial_reviewer.md)

</td>
<td align="center" width="33%">

### 🔧 Build & Add Datasets

Add new datasets or fix kernels using the NeuroDoc generation pipeline.

[**Contributor tutorial →**](_docs/tutorial_contributor.md)

</td>
</tr>
</table>

---

## 📚 Use the Corpus

Start from the browsable index of all 55 completed datasets:

**[→ _docs/corpus_index.md](_docs/corpus_index.md)** — full table sorted by paradigm category, with links to each `analysis.md`

Each dataset document contains five sections: `Paradigm`, `File Scan Result`, `Tasks`, `Data Quality Notes`, and `Kernel Responsibilities`. The `Tasks` section defines ready-to-use ML task configurations (label route, target events, class mappings) that feed directly into the HDF5 export and PyTorch DataLoader pipeline.

**Full step-by-step guide** — browsing → dataset selection → EEGUnity HDF5 export → PyTorch DataLoader:

**[→ _docs/tutorial_corpus_user.md](_docs/tutorial_corpus_user.md)**

> [!NOTE]
> For advanced EEGUnity usage, preprocessing pipelines, and HDF5 format specification, refer to [eegunity.readthedocs.io](https://eegunity.readthedocs.io/).

---

## 🤝 Community Contributions

We welcome contributions from the EEG and BCI community. The standard contribution flow is:

```
Fork main branch  →  Make changes (NeuroAudit or NeuroDoc)  →  PR to dev branch
```

### Contribution Workflow

```
1.  Fork  EEG-BenchmarkSkill/EEGBenchmarkSKILL  on GitHub
        ↓
2.  Clone your fork  &  create a feature branch
    git checkout -b review/<dataset>   # for document review
    git checkout -b contrib/<dataset>  # for kernel / new dataset work
        ↓
3a. Document review  →  open NeuroAudit  →  edit  →  save
    python -m neuroaudit              # http://127.0.0.1:5000
        ↓
3b. Kernel / new dataset  →  run NeuroDoc pipeline  →  validate
    python -m neurodoc.generate --dataset <name>
    python -m neurodoc.detect   --dataset <name>
        ↓
4.  Commit the changed files  (analysis.md  and/or  kernel.py)
        ↓
5.  Open PR  →  base: EEG-BenchmarkSkill/EEGBenchmarkSKILL @ dev
```

> [!TIP]
> Not sure which path to take? If you are fixing wording, tasks, or quality notes on an existing dataset, use **NeuroAudit** (path 3a). If you are adding a new dataset or the kernel is broken, use **NeuroDoc** (path 3b).

**Detailed step-by-step tutorials:**

| Audience | Tutorial |
|---|---|
| Reviewers & document editors | [_docs/tutorial_reviewer.md](_docs/tutorial_reviewer.md) |
| Kernel & dataset contributors | [_docs/tutorial_contributor.md](_docs/tutorial_contributor.md) |

---

## 📁 Repository Map

```
EEGBenchmarkSKILL/
├── dataset_document/        # The corpus — one folder per dataset
│   └── <dataset>/
│       ├── analysis.md      # Structured documentation (paradigm, tasks, scan result)
│       └── *.pdf / *.txt    # Reference materials
│
├── neurodoc/                # NeuroDoc: automated generation pipeline
│   ├── generate.py          # CLI: full 3-phase pipeline
│   ├── detect.py            # CLI: semantic rule validation
│   ├── full_scan.py         # CLI: re-scan with existing kernel
│   ├── kernels/             # Dataset-specific normalization kernels (400+)
│   └── README.md            # NeuroDoc full documentation
│
├── neuroaudit/              # NeuroAudit: browser-based review UI
│   ├── server.py            # Flask backend
│   ├── index.html           # Single-page review interface
│   └── README.md            # NeuroAudit documentation
│
├── Script/                  # Supporting automation and experiment scripts
│   └── neurodoc_runtime/    # Runtime state: logs, progress, machine config (gitignored)
│
├── _docs/                   # Guides and assets
│   ├── tutorial_reviewer.md
│   └── tutorial_contributor.md
│
└── AGENTS.md                # Codex / OpenAI Agents skill definition
```

---

## 📖 Related Documentation

| Document | Description |
|---|---|
| [neurodoc/README.md](neurodoc/README.md) | NeuroDoc pipeline architecture, CLI reference, kernel specification |
| [neuroaudit/README.md](neuroaudit/README.md) | NeuroAudit UI, review workflow, rulebook |
| [neurodoc/kernels/KERNEL_RULEBOOK.md](neurodoc/kernels/KERNEL_RULEBOOK.md) | Kernel writing standards |
| [AGENTS.md](AGENTS.md) | Codex / OpenAI Agents skill definition |
| [_docs/corpus_index.md](_docs/corpus_index.md) | Browsable index of all 55 completed datasets |
| [_docs/tutorial_corpus_user.md](_docs/tutorial_corpus_user.md) | Corpus user guide: browse → select → export HDF5 → PyTorch |
| [_docs/tutorial_reviewer.md](_docs/tutorial_reviewer.md) | Reviewer & document contributor guide |
| [_docs/tutorial_contributor.md](_docs/tutorial_contributor.md) | Kernel & dataset contributor guide |

---

## ⚖️ License

This repository is released under **[CC BY-NC 4.0](LICENSE)**.
Free to use and adapt for academic and research purposes.
Commercial use is not permitted.

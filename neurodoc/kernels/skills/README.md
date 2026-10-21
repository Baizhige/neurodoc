# Kernel SKILL File Index

This directory contains SKILL prompt templates for AI-assisted generation of EEGUnity kernels.

Usage: Select the appropriate SKILL file based on the dataset's file format and label storage method,  
provide its full content to the AI (Claude Code / Codex / other LLM),  
along with the dataset path. The AI will inspect the dataset and draft a candidate kernel, which must then pass the applicable validation rules and human review before release.

---

## Selecting a SKILL File

| Dataset Characteristics | Use SKILL File |
|-------------------------|----------------|
| GDF / BDF / EDF, events in MNE Annotations | [SKILL_gdf_annotation_remap.md](SKILL_gdf_annotation_remap.md) |
| `.mat` files (main file or sidecar), events in `.mat` fields | [SKILL_mat_sidecar.md](SKILL_mat_sidecar.md) |
| Proprietary format that EEGUnity cannot parse | [SKILL_custom_format.md](SKILL_custom_format.md) |
| BIDS standard dataset (with participants.tsv / events.tsv) | [SKILL_bids_standard.md](SKILL_bids_standard.md) |

## Decision Tree

```
Can the dataset files be read directly by MNE?
├── No → SKILL_custom_format.md
└── Yes → Dataset follows BIDS structure (has participants.tsv)?
          ├── Yes → SKILL_bids_standard.md
          └── No → Where are the event labels?
                    ├── MNE Annotations (GDF/BDF/EDF header) → SKILL_gdf_annotation_remap.md
                    └── Separate .mat file fields → SKILL_mat_sidecar.md
```

## Specification Reference

The validation checklists in all SKILL files are aligned with [KERNEL_RULEBOOK.md](../KERNEL_RULEBOOK.md).  
Generated kernels should be placed in the `neurodoc/kernels/` directory.

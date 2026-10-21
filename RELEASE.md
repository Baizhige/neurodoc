# NeurIPS 2026 camera-ready artifact snapshot

## Identity

- Branch: `camera-ready-snapshot`
- Snapshot prepared: 21 October 2026
- Public repository: <https://github.com/Baizhige/neurodoc/>
- Project website: <https://neurodoc.eeg.fm>
- Source review commit: `anonymous@eeede588ff2d3c0c07c20a58e150e5f6fd122573`

## Frozen scientific scope

This release preserves the scientific scope evaluated during peer review:

- 53 human-reviewed `completed` entries
- 134 classical tasks
- 111 potential tasks
- 245 task definitions in total

The two entries subsequently marked completed on the development branch, `openneuro_ds001849` and `openneuro_ds001971`, are not part of the 53-entry paper release. Post-review document and kernel rewrites on `main` are likewise not silently incorporated here.

## Camera-ready changes

The camera-ready snapshot makes release and compliance changes without expanding the reviewed scientific scope:

- restores public author, contributor, and reviewer attribution;
- replaces anonymous and obsolete repository URLs;
- adds citation, governance, licensing-scope, and provenance documentation;
- reframes NeuroDoc as candidate generation under human release authority;
- preserves and republishes the 53-entry/245-task Croissant tables with updated metadata and hashes;
- removes machine-specific examples from user-facing corpus documents;
- strengthens secret and local-configuration exclusions; and
- makes archived representative-run paths usable on Windows while preserving original run identifiers in a manifest.

## Relationship to `main`

`main` is a living community-development branch and may contain newer entries, task revisions, kernels, and utilities. Those changes can be scientifically useful, but they should not be interpreted as the exact artifact reviewed for the NeurIPS 2026 paper. Cite or reproduce this snapshot when correspondence with the paper's 53 entries and 245 tasks matters.

## Raw-data boundary

This repository contains documents, task metadata, kernels, review tooling, and selected audit evidence. It does not redistribute raw EEG. The original data providers retain control of their datasets, licenses, access procedures, and data-use terms.

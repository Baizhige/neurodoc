# NeuroDoc

`neurodoc/` is the generation engine for EEG dataset kernels and `analysis.md` documents.

## Repository Role

- Generates or updates `dataset_document/<dataset>/analysis.md`
- Maintains version-controlled kernels in `neurodoc/kernels/`
- Exposes stable NeuroAudit-facing APIs via `neurodoc.api`
- Provides the `dataset_api/` torch dataset loaders for generated HDF5 outputs

## Runtime Layout

Tracked source lives in `neurodoc/`.

Machine-specific runtime state now lives in ignored local paths under:

```text
Script/neurodoc_runtime/
├─ machine_config/
├─ locator_cache/
├─ progress/
├─ evidence_cache/
├─ logs/
└─ sandbox/
```

## Main Entry Points

```bash
python -m neurodoc.generate --dataset openneuro_ds001784
python -m neurodoc.detect --dataset openneuro_ds001784
python -m neurodoc.tools.migrate_to_v3 --all --dry-run
```

Direct script execution still works for local use:

```bash
python neurodoc/generate.py --dataset openneuro_ds001784
python neurodoc/detect.py --all
```

## Data And Outputs

- Documentation root: `dataset_document/`
- Final kernel location: `neurodoc/kernels/<dataset>.py`
- Final document location: `dataset_document/<dataset>/analysis.md`

## App Integration

The audit UI should import only from:

- `neurodoc.api`
- `neurodoc.paths`

It should not reach into internal pipeline modules directly.

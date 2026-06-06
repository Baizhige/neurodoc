# neurodoc.utils — task-ready HDF5 exporter

Export the EEGUnity v2 HDF5 file for a specific **dataset + task**, driven by the
task definitions already written in `dataset_document/<dataset>/analysis.md`.
The output is directly consumable by `neurodoc.dataset_api.build_dataset_from_task`.

**One command, one file:**

```bash
python -m neurodoc.utils.export_task_h5 --config export_jobs.yaml
```

Everything (which datasets/tasks, preprocessing, channel space, output location)
lives in the YAML config. See [`export_jobs.example.yaml`](export_jobs.example.yaml).

## What it does per job

1. Resolve the raw data path (`dataset_roots` / `raw_path`) and the kernel
   (`neurodoc/kernels/`), exactly as the NeuroDoc scan pipeline does.
2. Parse the `task`-th Task block (1-based, document order) from `analysis.md`:
   `Epoch Method`, `Epoch Parameters`, `Label Route`, `Target Definition`.
3. Compute a `config_key` (epoch method + epoch params + pipeline + channel
   signature) and check the cache at
   `<cache_dir>/<dataset>/task<N>/<config_key>.hdf5`.
4. On a miss: build a kernel-applied `UnifiedDataset` and call the matching
   `epoch_by_{event,segmentation,long_event}_hdf5` with
   `pipeline = <your pipeline> → <common-channel alignment>`.
5. Read the HDF5 back and print a summary (epoch count, shape, class
   distribution for event tasks).

The base locator scan is cached once per dataset
(`<cache_dir>/<dataset>/locator.csv`) and reused across tasks and configs.
Builds are guarded by a POSIX file lock so concurrent runs on a shared
filesystem (NFS/GPFS) are safe.

## Config scopes (finest wins)

Processing params — `pipeline`, `pipeline_param`, `common_channels`,
`min_matched_channels`, `epoch_param` — resolve through three scopes:

```
default  (broadest)  <  datasets.<name>  <  job (per task)
```

Resolution is **per parameter, whole-value** (option A): the most specific scope
that sets a parameter wins outright — no deep merge across scopes. `epoch_param`
is then layered over the values parsed from the document.

## Channel space (`common_channels`)

* **omitted / `null`** — no alignment. The kernel must already yield a uniform
  channel count; if not, EEGUnity raises and that job is reported as `failed`
  (it is a kernel/doc issue, not the exporter's job to paper over).
* **a list** — every recording is aligned to exactly that set (missing channels
  interpolated, extras dropped), producing a uniform flat HDF5. The channel
  signature is part of `config_key`, so different sets cache separately.
  A task whose recordings have **no overlap** with the requested set is
  **skipped** with a detailed log (the dataset's channels vs the requested set);
  individual recordings below `min_matched_channels` are dropped and logged.

## Preprocessing pipelines

`--pipeline` / config `pipeline` points at a `.py` file exporting either
`pipeline(raw) -> raw` or `make_pipeline(**kwargs) -> (raw -> raw)`. Built-ins
live in [`pipelines/`](pipelines): `default.py` (resample + band-pass + notch),
`raw_only.py` (identity).

## Fault tolerance & exit code

Every job is isolated: a missing doc, empty channel intersection, or build error
is logged and recorded, then the batch continues. A summary table is printed at
the end and (when `log_dir` is set) written to `export_<timestamp>.log`. The
process exits non-zero if **any** job was skipped or failed.

## Supported routes

| Label Route | Supported | Notes |
|-------------|-----------|-------|
| `event`     | ✅ | `/epoch_meta/event_code` + `label_map` → `EventDataset` |
| `info`      | ✅ | subject attrs in `/source_meta/<group>` → `InfoDataset` |
| `misc`      | ✅ | NeuroDoc writes per-epoch labels to EEGUnity v2.1 `/misc_meta/<channel>` and removes misc/stim label channels from `/data` |

## EEGUnity location

`eegunity_path` (config or `--eegunity_path`) is prepended to `sys.path`.
During development it defaults to the in-repo `Script/` directory. For a release
that ships EEGUnity as an installed package, leave it empty to use the
environment's `eegunity`.

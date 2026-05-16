# Kernel invariants — K1 through K6

These are *do-no-harm* rules layered on top of `semantic_rules.yaml`. They are
enforced statically by `pipeline/kernel_gate.py` BEFORE the kernel test
subprocess runs. Failing any one drops the kernel into the v3 build_kernel
retry queue.

The motivating incident: dataset `sleepdata_shhs` accumulated three failure
modes that K1–K6 are designed to prevent.

---

## K1 — Preserve channel names

**Rule.** Kernel may call `rename_channels()` only when every key appears in
`LocatorReport.rename_evidence`. Default is no rename.

**Why.** A v2 kernel rewrote `EOG(L)` → `EOG-L` and `Heart Rate` → `HR`,
silently breaking the static check that compared the kernel's declared
`required_native_misc=['EOG(L)','EOG(R)','H.R.']` against the actually-present
post-rename names.

**How.** Static regex match on `rename_channels` invocations. v3 keeps
`rename_map` empty unless `LocatorReport.rename_evidence` has explicit
documentation justifying the rename (e.g. bcic_iv_2a's numeric→10-20 mapping
cited from a SKILL doc).

---

## K2 — Preserve event IDs

**Rule.** Kernel must NOT call `mne.rename_events()` or pass an
`event_id_map=` dict. Pass-through is mandatory. The single exception is
prefix-only enrichment when `kernel_requirements.event_prefix_groups` is
non-empty (cross-group label collision detected by Phase 4 v3).

**Why.** Multiple v2 kernels invented synthetic IDs like `Stage 1|1, Stage 2|2`
that didn't exist in the source data, then dropped event tasks because the
"required" IDs weren't found.

**How.** Static regex matches on `rename_events`, `event_id_map=`, or
`mapping={...}` arguments to `mne.events_from_annotations`.

---

## K3 — Native MISC honesty

**Rule.** `kernel_requirements.required_native_misc` must be a subset of
`ProbeReport.misc_channel_names`. If the probe found no native MISC, the
kernel may not synthesize MISC channels with overlapping names.

**Why.** A v2 SHHS kernel declared `H.R.` as native misc but the channel was
actually called `Heart Rate` in the EDF; the rename pollution then broke the
declaration.

**How.** Set membership check: `set(kr.required_native_misc) ⊆ probe.misc`.

---

## K4 — Derived MISC must be groundable

**Rule.** Each entry in `derived_misc_channels[*].source_field` must cite a
column from `LocatorReport.sidecars` (events.tsv:col or participants.tsv:col).
No fallback substitution — if grounding fails, Phase 4 v3 *drops* the task
rather than substituting a bogus column.

**Why.** A v2 SHHS reconcile pass substituted `nsrrid` (subject ID) for SaO2 /
HR / EMG / EOG when the original sources weren't grounded — turning every
regression task into a constant-per-subject prediction.

**How.** Set membership check inside the kernel_gate: each `source_field`
appears in a deterministically-built sidecar columns set.

---

## K5 — Annotation source from locator

**Rule.** Every kernel sidecar-read path (xml/tsv/json/csv) must match a path
or path-fragment listed in `kernel_requirements.annotation_paths`.

**Why.** The original SHHS kernel hard-coded sibling-of-EDF paths for NSRR
XMLs, but the actual layout was `polysomnography/annotations-events-nsrr/shhs1/...`
The kernel walked 8571 files and produced 0 events.

**How.** Extract sidecar-looking string literals from the kernel; reject any
that share zero path fragments with `LocatorReport.annotation_files` entries.
The fragment match is loose (allows the kernel to compose paths via os.path.join)
but blocks the "imagine a sibling" failure mode.

---

## K6 — Test honesty

**Rule.** The kernel test harness reports ERROR (not silent PASS) when zero
files succeeded — even if every file SKIPPED due to ImportError. Skipped
files now increment a counter and the harness exits with code 2 if `n_ok == 0`.

**Why.** A scipy ImportError silently caused every SHHS test file to SKIP, and
the harness still printed `[PASS] All N files passed`.

**How.** `_build_test_script()` in `kernel_builder.py` now tracks
`n_ok` / `n_skipped` and emits explicit `[FAIL] K6: 0 / N files succeeded`
when nothing parsed cleanly.

---

## Severity & retry behaviour

All six rules are `error` severity. A K-gate violation drops the kernel into
the v3 build retry queue (`max_versions = 2`). On the second failure, the
pipeline ends with `wait_kernel_update` status and writes the failed kernel
under `sandbox/<dataset>/kernel_v{N}_KGATE.py` for offline inspection.

If aggressive false-positives appear during dogfood (most likely K1 / K3),
they can be downgraded to `warning` by editing `kernel_invariants.yaml` —
the kernel_gate.py implementation reads severity dynamically from the YAML.

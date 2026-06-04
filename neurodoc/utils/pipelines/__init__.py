"""Built-in preprocessing pipelines for the HDF5 exporter.

Each file exports either:
    pipeline(raw) -> raw                         (no-param)
    make_pipeline(**kwargs) -> (raw -> raw)      (parameterised factory)

A pipeline receives an mne Raw (kernel-applied) and returns a processed Raw.
It runs after loading and before epoching; channel-space alignment (if any)
is applied after the pipeline by the exporter.
"""

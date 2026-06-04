"""default — a generic resample + band-pass + notch preprocessing pipeline.

Parameterised factory. All steps are optional (pass None to skip a step).
Resampling runs last so the exported sampling rate is exactly ``resample`` Hz.

    make_pipeline(resample=200, lower_bound=0.1, upper_bound=75.0, notch=50.0)
"""
from typing import Optional


def make_pipeline(resample: Optional[float] = 200.0,
                  lower_bound: Optional[float] = 0.1,
                  upper_bound: Optional[float] = 75.0,
                  notch: Optional[float] = 50.0):
    """Return a callable ``pipeline(raw) -> raw`` applying the configured steps."""

    def pipeline(raw):
        raw.load_data()
        if lower_bound is not None or upper_bound is not None:
            raw.filter(l_freq=lower_bound, h_freq=upper_bound, verbose="ERROR")
        if notch is not None:
            sfreq = float(raw.info["sfreq"])
            freqs = list(range(int(notch), int(sfreq // 2) + 1, int(notch)))
            if freqs:
                raw.notch_filter(freqs=freqs, verbose="ERROR")
        if resample is not None and abs(float(raw.info["sfreq"]) - float(resample)) > 1e-6:
            raw.resample(float(resample), verbose="ERROR")
        return raw

    return pipeline

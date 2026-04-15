"""OpenNeuro ds004784 stage1 kernel for EEGUnity.

Dataset: Phantom EEG Dataset with Motion, Muscle, and Eye Artifacts.
264‑channel phantom EEG recorded at 512 Hz.
Event codes: 65471 (artifact‑on) and 65343 (artifact‑off/clean).

Source: https://openneuro.org/datasets/ds004784
"""

from __future__ import annotations

import json

import mne


class OpenNeuroDS004784Kernel:
    """Stage1 kernel for OpenNeuro ds004784 (Phantom EEG)."""

    KERNEL_ID = "openneuro-ds004784-stage1"

    def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
        # --- Metadata (eegunity_description) ---
        original_desc = raw.info.get("description", "")
        description_dict = {
            "original_description": original_desc,
            "eegunity_description": {
                "age": "unknown",
                "sex": "unknown",
                "amplifier": "unknown",
                "cap": "unknown",
                "handedness": "unknown",
            },
        }
        # LLM 推断，需人类复核
        raw.info["description"] = json.dumps(description_dict)

        # --- Ensure events are present as annotations ---
        # Try to use existing annotations; if none, try to read from a stim channel.
        try:
            events, event_id = mne.events_from_annotations(raw, verbose=False)
        except Exception:
            # No annotations found – look for a stimulation channel.
            stim_ch = None
            for ch in raw.ch_names:
                if "stim" in ch.lower() or "stimulation" in ch.lower():
                    stim_ch = ch
                    break
            # Common stimulator channel names in BrainVision / BIDS files.
            if stim_ch is None:
                for candidate in ["STI 014", "STI 013", "STI"]:
                    if candidate in raw.ch_names:
                        stim_ch = candidate
                        break
            if stim_ch:
                events = mne.find_events(raw, stim_channel=stim_ch, verbose=False)
                # Convert to annotations using the numeric code as description.
                onsets = events[:, 0] / raw.info["sfreq"]
                durations = [0.0] * len(events)
                descriptions = events[:, 2].astype(str)
                raw.set_annotations(mne.Annotations(onsets, durations, descriptions))
            # If no stim channel, do nothing – raw may already contain events.

        # At this point raw.annotations holds the event markers.
        # The dataset uses numeric codes 65471 and 65343; they should appear as
        # description strings "65471" and "65343". No further remapping is needed
        # for raw meta.

        return raw


KERNEL = OpenNeuroDS004784Kernel()
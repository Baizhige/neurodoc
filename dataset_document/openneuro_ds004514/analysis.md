# Simultaneous EEG and fNIRS recordings for semantic decoding of imagined animals and tools

**Dataset**: `openneuro_ds004514` | **Year**: 2023 | **URL**: https://openneuro.org/datasets/ds004514
**Category**: High-level Mental | **Subjects**: 12 | **Files (Completed)**: 12 | **Channels**: 32 | **Sampling Rate**: 500 Hz | **Manual Review**:

## Paradigm

Participants performed mental imagery tasks involving semantic categories of animals and tools while simultaneous EEG and fNIRS were recorded. The study employed multiple task modalities including visual imagery, silent naming, auditory imagery, and drawing imagery, with each mental task epoch lasting approximately 3 seconds. Visual cues (images, audio, written words, drawings) preceded imagery periods to prompt the semantic category and modality type.

## File Scan Result

> **Kernel SHA256**: `9e4ac72eeeba2ae337cb2c3972d72c87bb4555866153c72ca91f780f565a3567`
> **EEGUnity Version**: `0.8.1`
> **Scan Type**: Full

### Event Structure

| Event ID | Count (total) | Type | Meta Level | Meaning |
|----------|---------------|------|------------|---------|
| `127.0` | 13 | admin | raw | System trigger code (not present in curated events.tsv) |
| `255.0` | 28184 | admin | raw | System trigger code (not present in curated events.tsv) |
| `animal_visual_imagery_task` | 13 | event | raw | Trial phase onset: animal visual imagery task |
| `audio_tool` | 14 | event | raw | Trial phase onset: audio tool |
| `rest` | 28184 | event | raw | Trial phase onset: rest |
| `written_animal` | 3 | event | raw | Trial phase onset: written animal |


### Info
| Field | Completeness | Notes |
|---|---|---|
| `age` | complete | N/A |
| `sex` | complete | N/A |
| `device` | missing | N/A |

## Tasks



## Data Quality Notes

- Event structure shows severe imbalance: `rest` events dominate with 28,184 occurrences while task-related events (`animal_visual_imagery_task`: 13, `audio_tool`: 14, `written_animal`: 3) are extremely rare.
- Only 3 semantic task event types are present out of the expected 8 combinations (2 categories × 4 modalities), indicating substantial missing event labels in the available data.
- The `written_animal` event has only 3 occurrences, limiting any statistical analysis for this condition.
- System trigger codes `127.0` and `255.0` are marked as "not present in curated events.tsv" suggesting a mismatch between raw trigger channels and curated event annotations.
- `device` field is completely missing from metadata, preventing equipment identification and noise characterization.
- Subject count discrepancy: original draft referenced 22 subjects but File Scan Result and Tasks sections confirm 12 subjects with complete age/sex data.
- The `participant_id` field name contains a leading zero-width no-break space character (`\ufeff`), which may cause parsing issues in automated workflows.
- No event labels exist for expected conditions: visual tool, silent naming animal, silent naming tool, auditory animal, drawing animal, drawing tool — preventing the originally intended animal vs. tool semantic decoding task.

## Kernel Responsibilities

> **Super Meta Required**: No
> **Status**: wait_kernel_update

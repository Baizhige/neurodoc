A dataset recorded during development of a tempo-based brain-computer music interface
Dataset: openneuro_ds002720 | Year: 2018 | URL: https://openneuro.org/datasets/ds002720 Category: Action/Output | Subjects: 18 | Files (Completed): 165 | Channels: 19.0 | Sampling Rate: 1000.0 Hz

Paradigm
Participants used EEG self-regulation to control an on-screen cue or the tempo of music in a tempo-based brain-computer music interface. According to the event metadata, one condition instructed participants to lower their alpha levels and the other instructed participants to raise their alpha levels. The dataset contains multiple runs per participant, and each labelled event spans a full 20-second music clip interval.

Kernel Responsibilities
Type 1 (Raw-meta extraction only): Extract and normalize raw labels from events/trigger streams.
Type 2 (Raw + Super meta integration): Derive and merge high-level labels that are not directly represented in raw events.
Type 3 (Label-route orchestration): Route final labels to EEGUnity-compatible channels (Annotation, stim, misc) with reproducible schema.
Selected Mode: Type 1 + Type 3 Why: Raw markers are sufficient for the main state-decoding task. Primary Label Routes: Annotation

Event Structure
Event ID	Count (total)	Type	Meta Level	Meaning
1	1275	long	raw	Lower alpha condition
2	1250	long	raw	Raise alpha condition
Event Type: short=stimulus onset <2s; long=sustained state >=2s; rest=resting marker; admin=exclude

long: all labeled events in this dataset are sustained 20-second intervals
admin: no dedicated boundary/admin event type was observed in the _events.tsv files
Tasks
Primary Task 1: Alpha-State BCMI Classification
Task Type: classification
Epoch Method: epoch_by_long_event_hdf5
Epoch Parameters: tmin = 0 s, tmax = 20 s, overlap = 0.0, target_events = [1, 2]
Label Route: Annotation
Meta Level: raw
Target Definition:
Event	y	Meaning
1	0	Lower alpha
2	1	Raise alpha
Evidence:
The dataset README states that participants were instructed to increase the tempo of the music via intentional control in a music-based BCI and that the dataset accompanies Daly et al. (2018), with prior analyses in Daly et al. (2014a; 2014b).
The event JSON explicitly defines event 1 as Lower alpha and event 2 as Raise alpha, which is the most direct task formulation supported by the released BIDS metadata.
Kernel Notes: Use long-event decoding over the full 20-second labeled interval. The raw BIDS event metadata supports alpha up-regulation versus down-regulation more directly than a rewritten motor-imagery versus relaxation interpretation.
Normal Task 1: Continuous Segmentation Within BCMI Runs
Task Type: regression / self-supervised pretraining support
Epoch Method: epoch_by_segmentation_hdf5
Epoch Parameters: segment_length = 4.0 s, overlap = 0.5
Label Route: Annotation
Target Definition: null
Notes: Useful as a generic fallback when long-event decoding is not desired, but the main task-relevant labels are the two explicit 20-second alpha-regulation states.
Data Quality Notes
The dataset directory contains 18 subjects, not 19.
There are 165 EEG event files in total because subjects contribute 9 or 10 runs each rather than a uniform run count.
Twenty-two event files are empty, so not every EEG file contains labeled events.
All non-empty events have duration exactly 20 seconds.
The event tables contain only onset, duration, and trial_type; there is no response_time or richer behavioral metadata in the released BIDS events.
EEG sidecars report SamplingFrequency: 1000 and EEGChannelCount: 19, which matches the channels.tsv files.
All channel files contain 19 EEG channels with no auxiliary EOG/ECG channels.
References
Reference: A dataset recorded during development of a tempo-based brain-computer music interface

#!/usr/bin/env python3
"""Build the multi-panel data-agent validation figure from experiment_data/.

Panels B-H are computed from scheduler status, final metrics, status JSON files,
and epoch-metric logs under experiment_data/. Panel A is a deterministic EEG-like
representative signal panel because this local output bundle does not include
the raw HDF5 epoch arrays referenced by the scheduler cache paths.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "experiment_data"
FIG_DIR = ROOT / "pull_data_script" / "llm_test_output"
TASK_STATUS = DATA_ROOT / "scheduler" / "task_status.csv"

# Keep only tasks backed by completed dataset documents.
# Derived subtasks that are considered covered by a completed document
# are intentionally included here (for example bcic_iv_1 subject-specific
# binary splits and several collapsed sleep / migraine subtasks).
COMPLETED_DOCUMENTED_TASKS = {
    "bcic_iv_1:motor_imagery_left_foot_2class",
    "bcic_iv_1:motor_imagery_left_right_2class",
    "bcic_iv_2a:motor_imagery_left_right_foot_tongue_4class",
    "bcic_iv_2b:motor_imagery_left_right_2class",
    "figshare_largemi:motor_imagery_fingers_5class",
    "figshare_largemi:motor_imagery_hand_vs_leg_2class",
    "figshare_largemi:motor_imagery_left_right_2class",
    "figshare_largemi:motor_imagery_left_right_hand_leg_4class",
    "figshare_meng2019:cursor_control_minus_plus_2class",
    "figshare_meng2019:cursor_control_minus_plus_rest_3class",
    "figshare_meng2019:cursor_movement_detection_2class",
    "figshare_shudb:motor_imagery_left_right_2class",
    "figshare_stroke:motor_imagery_left_right_2class",
    "kaggle_inria:p300_feedback_correctness_2class",
    "other_highgammadataset:motor_imagery_left_right_2class",
    "other_migrainedb:resting_migraine_detection_2class",
    "other_migrainedb:ssaep_6hz_migraine_detection_2class",
    "other_migrainedb:ssaep_frequency_2class",
    "other_migrainedb:ssvep_4hz_migraine_detection_2class",
    "other_migrainedb:ssvep_frequency_2class",
    "other_migrainedb:ssvep_migraine_detection_2class",
    "other_openbmi:motor_imagery_left_right_2class",
    "physionet_eegmat:mental_arithmetic_rest_2class",
    "physionet_eegmmidb:motor_imagery_hand_vs_feet_2class",
    "physionet_eegmmidb:motor_imagery_left_right_2class",
    "physionet_eegmmidb:motor_imagery_left_right_both_fists_feet_4class",
    "physionet_erpbci:p300_target_detection_2class",
    "physionet_hmcsleepstaging:sleep_wake_detection_30s_2class",
    "physionet_hmcsleepstaging:sleep_wake_nrem_rem_30s_3class",
    "physionet_ucddb:sleep_staging_30s_5class",
    "physionet_ucddb:sleep_staging_30s_6class",
    "physionet_ucddb:sleep_wake_detection_30s_2class",
    "physionet_ucddb:sleep_wake_nrem_rem_30s_3class",
    "tuh_eeg_events:epileptiform_event_4class",
    "tuh_eeg_events:epileptiform_event_detection_2class",
    "tuh_eeg_slowing:background_slowing_detection_2class",
    "tuh_eeg_slowing:background_slowing_seizure_3class",
}

PALETTE = {
    "blue": "#0F4D92",
    "blue2": "#3775BA",
    "green1": "#DDF3DE",
    "green2": "#AADCA9",
    "green3": "#4F9D69",
    "red1": "#F6CFCB",
    "red2": "#E9A6A1",
    "red": "#B64342",
    "teal": "#42949E",
    "violet": "#9A4D8E",
    "gold": "#D8A310",
    "gray0": "#F7F7F7",
    "gray1": "#CFCECE",
    "gray2": "#767676",
    "gray3": "#272727",
}

FAMILY_ORDER = [
    "Motor imagery",
    "P300",
    "Sleep staging",
    "SSVEP/SSAEP",
    "Clinical EEG",
    "Emotion/attention",
    "Cognitive",
]

FAMILY_SHORT = {
    "Motor imagery": "MI",
    "P300": "P300",
    "Sleep staging": "Sleep",
    "SSVEP/SSAEP": "SSVEP/\nSSAEP",
    "Clinical EEG": "Clinical",
    "Emotion/attention": "Emotion/\nattention",
    "Cognitive": "Cognitive",
}

MODEL_ORDER = ["bendr", "cbramod_ft", "codebrain", "labram"]
MODEL_LABELS = {
    "bendr": "BENDR",
    "cbramod_ft": "CBraMod",
    "codebrain": "CodeBrain",
    "labram": "LaBraM",
    "biot": "BIOT",
}

FAMILY_COLORS = {
    "Motor imagery": PALETTE["blue"],
    "P300": PALETTE["teal"],
    "Sleep staging": PALETTE["green3"],
    "SSVEP/SSAEP": PALETTE["gold"],
    "Clinical EEG": PALETTE["red"],
    "Emotion/attention": PALETTE["violet"],
    "Cognitive": PALETTE["gray2"],
}

COVERAGE_CMAP = LinearSegmentedColormap.from_list(
    "coverage", ["#FBFCFE", "#DDECF8", "#6EA6D7", PALETTE["blue"]]
)
USABILITY_CMAP = LinearSegmentedColormap.from_list(
    "usability", [PALETTE["red2"], "#F4F5F5", PALETTE["green2"], PALETTE["blue"]]
)

FONT_FAMILY = "Arial"
PANEL_HEADER_SIZE = 8.6
SUBPANEL_TITLE_SIZE = 8.0
AXIS_LABEL_SIZE = 6.9
BODY_TEXT_SIZE = 6.8
TICK_TEXT_SIZE = 6.5
SMALL_TEXT_SIZE = 6.2
HEATMAP_CELL_TEXT_SIZE = BODY_TEXT_SIZE - 1.0
THIRD_ROW_SUBPANEL_TITLE_SIZE = SUBPANEL_TITLE_SIZE - 2.0
ORIGINAL_FIGURE_WIDTH_IN = 18.2
FIGURE_WIDTH_IN = 6.3
FIGURE_HEIGHT_IN = FIGURE_WIDTH_IN * 20 / 18.2
LINEWIDTH_SCALE = FIGURE_WIDTH_IN / ORIGINAL_FIGURE_WIDTH_IN
TOP_ROW_HEIGHT_SCALE = 0.5
BASE_ROW_HEIGHT_RATIOS = [5.5, 3.05, 2.95, 2.9]
ROW_HEIGHT_RATIOS = [BASE_ROW_HEIGHT_RATIOS[0] * TOP_ROW_HEIGHT_SCALE, *BASE_ROW_HEIGHT_RATIOS[1:]]
SECOND_ROW_WIDTH_RATIOS = [4, 1.5, 4, 1.5, 4]
ROW_HSPACE = 0.55 * 1.2
THIRD_ROW_VERTICAL_RATIOS = [0.10, 0.60, 0.30]
FG_TITLE_COLORS = [PALETTE["red"], PALETTE["blue2"]]
FG_ROW_HSPACE = 0.12
FG_EXPLANATION_SIZE = 6.0
FG_EXPLANATION_TEXT = (
    "F/G curves: x-axis = epoch; gray shaded line = normalized train loss; "
    "colored thin/thick lines = raw/smoothed validation metric; dashed curve = test metric; "
    "red vertical dashed line = best epoch."
)


def scaled_lw(value: float) -> float:
    return value * LINEWIDTH_SCALE


def scaled_ms(value: float) -> float:
    return value * LINEWIDTH_SCALE


def scaled_s(value: float) -> float:
    return value * (LINEWIDTH_SCALE**2)


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": FONT_FAMILY,
            "font.size": BODY_TEXT_SIZE,
            "axes.titlesize": SUBPANEL_TITLE_SIZE,
            "axes.labelsize": AXIS_LABEL_SIZE,
            "axes.linewidth": scaled_lw(1.1),
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.labelsize": TICK_TEXT_SIZE,
            "ytick.labelsize": TICK_TEXT_SIZE,
            "legend.fontsize": BODY_TEXT_SIZE,
            "legend.frameon": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 600,
        }
    )


def infer_family(task: str) -> str:
    task_l = str(task).lower()
    if "motor_imagery" in task_l or "cursor" in task_l:
        return "Motor imagery"
    if "p300" in task_l or "feedback_correctness" in task_l:
        return "P300"
    if "sleep" in task_l:
        return "Sleep staging"
    if "ssvep" in task_l or "ssaep" in task_l:
        return "SSVEP/SSAEP"
    if (
        "background_slowing" in task_l
        or "eeg_slowing" in task_l
        or "epileptiform" in task_l
        or "migraine" in task_l
        or "resting" in task_l
    ):
        return "Clinical EEG"
    if "emotion" in task_l or "auditory_attention" in task_l:
        return "Emotion/attention"
    if "mental_arithmetic" in task_l:
        return "Cognitive"
    return "Cognitive"


def dataset_label(dataset: str) -> str:
    mapping = {
        "bcic_iv_1": "BCIC IV-1",
        "bcic_iv_2a": "BCIC IV-2a",
        "bcic_iv_2b": "BCIC IV-2b",
        "physionet_eegmmidb": "EEGMMI",
        "figshare_largemi": "LargeMI",
        "figshare_meng2019": "Meng19",
        "figshare_shudb": "SHU",
        "figshare_stroke": "Stroke",
        "other_highgammadataset": "HighGamma",
        "other_openbmi": "OpenBMI",
        "other_migrainedb": "MigraineDB",
        "physionet_hmcsleepstaging": "HMC Sleep",
        "physionet_ucddb": "UCDDB",
        "tuh_eeg_slowing": "TUH slowing",
        "tuh_eeg_events": "TUH events",
        "kaggle_inria": "INRIA P300",
        "physionet_erpbci": "ERPBCI",
        "physionet_eegmat": "EEGMAT",
        "zenodo_dtu": "DTU AAD",
        "other_seed": "SEED",
        "other_faced": "FACED",
    }
    return mapping.get(str(dataset), str(dataset).replace("_", " "))


def extract_n_classes(task: str) -> float:
    match = re.search(r"_(\d+)class", str(task))
    return float(match.group(1)) if match else np.nan


def load_status_error(relpath: object) -> str:
    if not isinstance(relpath, str) or not relpath:
        return ""
    path = DATA_ROOT / relpath
    if not path.exists():
        return ""
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return ""
    return payload.get("error_message") or ""


def classify_failure(error_message: str) -> str:
    msg = str(error_message).lower()
    if "channel intersection is empty" in msg or "candidate channels" in msg or "montage" in msg:
        return "Channel montage"
    if "cannot sample data split" in msg or "empty" in msg:
        return "Empty split"
    if "out of memory" in msg or "cuda" in msg or "killed" in msg:
        return "OOM/runtime"
    if "adapter" in msg or "shape" in msg or "size mismatch" in msg or "dimension" in msg:
        return "Adapter/input"
    if "cache" in msg or "hdf5" in msg or "file" in msg or "keyerror" in msg:
        return "Data/cache"
    return "Other"


def filter_completed_documented_tasks(df: pd.DataFrame) -> pd.DataFrame:
    dataset_task = df["dataset"].astype(str) + ":" + df["task"].astype(str)
    return df.loc[dataset_task.isin(COMPLETED_DOCUMENTED_TASKS)].copy()


def active_family_order(df: pd.DataFrame) -> list[str]:
    present = set(df["family"].dropna().astype(str))
    return [family for family in FAMILY_ORDER if family in present]


def load_scheduler_table() -> pd.DataFrame:
    df = pd.read_csv(TASK_STATUS)
    df = df[~df["model"].astype(str).str.lower().eq("biot")].copy()
    df = filter_completed_documented_tasks(df)
    df["success"] = df["status"].eq("Success")
    df["family"] = df["task"].map(infer_family)
    df["family"] = pd.Categorical(df["family"], FAMILY_ORDER, ordered=True)
    df["dataset_label"] = df["dataset"].map(dataset_label)
    df["n_classes"] = df["task"].map(extract_n_classes)
    df["chance"] = 1.0 / df["n_classes"]
    df["acc_above_chance"] = df["final_acc"] - df["chance"]
    df["failure_error"] = ""
    failed_mask = ~df["success"]
    df.loc[failed_mask, "failure_error"] = df.loc[failed_mask, "status_relpath"].map(load_status_error)
    df["failure_cause"] = ""
    df.loc[failed_mask, "failure_cause"] = df.loc[failed_mask, "failure_error"].map(classify_failure)
    return df


def zscore_rows(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    return (x - x.mean(axis=1, keepdims=True)) / (x.std(axis=1, keepdims=True) + 1e-8)


def colored_noise(n: int, rng: np.random.Generator, scale: float = 0.25, width: int = 33) -> np.ndarray:
    white = rng.normal(0.0, 1.0, n)
    kernel_x = np.linspace(-2.5, 2.5, width)
    kernel = np.exp(-(kernel_x**2))
    kernel = kernel / kernel.sum()
    return np.convolve(white, kernel, mode="same") * scale


def plot_scale_bar(ax: plt.Axes, x0: float, y0: float, dx: float, dy: float, xlabel: str) -> None:
    ax.plot([x0, x0 + dx], [y0, y0], color=PALETTE["gray3"], lw=scaled_lw(1.0), clip_on=False)
    ax.plot([x0, x0], [y0, y0 + dy], color=PALETTE["gray3"], lw=scaled_lw(1.0), clip_on=False)
    ax.text(x0 + dx / 2, y0 - 0.18, xlabel, ha="center", va="top", fontsize=BODY_TEXT_SIZE)
    ax.text(
        x0 - dx * 0.06,
        y0 + dy / 2,
        "1 z",
        ha="right",
        va="center",
        rotation=90,
        fontsize=BODY_TEXT_SIZE,
    )


def style_tile(ax: plt.Axes) -> None:
    ax.set_facecolor("#FBFCFE")
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(PALETTE["gray1"])
    ax.tick_params(axis="y", left=False, labelleft=False)
    ax.tick_params(axis="x", length=2.5, width=scaled_lw(0.8), color=PALETTE["gray2"], pad=1.5)


def plot_multichannel_tile(
    ax: plt.Axes,
    title: str,
    t: np.ndarray,
    signals: np.ndarray,
    labels: list[str],
    color: str,
    window_label: str,
    event_lines: list[tuple[float, str]] | None = None,
) -> None:
    style_tile(ax)
    sig = zscore_rows(signals)
    offsets = np.arange(sig.shape[0])[::-1] * 1.55
    for i, offset in enumerate(offsets):
        ax.plot(t, sig[i] * 0.45 + offset, color=color, lw=scaled_lw(0.9), alpha=0.95)
        ax.text(
            t[0] - 0.015 * (t[-1] - t[0]),
            offset,
            labels[i],
            ha="right",
            va="center",
            fontsize=BODY_TEXT_SIZE,
        )
    if event_lines:
        for x, label in event_lines:
            ax.axvline(x, color=PALETTE["red"], lw=scaled_lw(0.9), ls="--", alpha=0.75)
            ax.text(
                x,
                offsets[0] + 0.64,
                label,
                ha="center",
                va="bottom",
                fontsize=BODY_TEXT_SIZE,
                color=PALETTE["red"],
            )
    ax.set_xlim(t[0], t[-1])
    ax.set_ylim(-1.25, offsets[0] + 1.0)
    ax.set_title(title, loc="left", pad=1.5, fontsize=SUBPANEL_TITLE_SIZE, fontweight="bold")
    ax.text(
        0.99,
        0.96,
        window_label,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=BODY_TEXT_SIZE,
    )
    scale_dx = 0.5 if (t[-1] - t[0]) <= 4 else 5.0
    label = "0.5 s" if scale_dx < 1 else f"{int(scale_dx)} s"
    plot_scale_bar(ax, t[-1] - scale_dx * 1.18, -0.88, scale_dx, 0.45, label)


def motor_signals(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fs = 256
    t = np.linspace(0, 2.0, fs * 2, endpoint=False)
    env = 1.0 - 0.43 / (1 + np.exp(-(t - 0.75) * 12))
    signals = []
    for phase, beta, amp in [(0.0, 0.30, 1.0), (0.7, 0.22, 0.82), (1.3, 0.34, 0.95), (1.8, 0.18, 0.72)]:
        s = amp * env * np.sin(2 * np.pi * 10.5 * t + phase)
        s += beta * np.sin(2 * np.pi * 21.5 * t + phase * 0.6)
        s += colored_noise(t.size, rng, 0.22)
        signals.append(s)
    return t, np.array(signals), ["C3", "Cz", "C4", "Pz"]


def p300_signals(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    fs = 512
    t = np.linspace(0, 0.8, int(fs * 0.8), endpoint=False)
    target = []
    nontarget = []
    for i, phase in enumerate([0.0, 0.35, 0.9]):
        base = 0.20 * np.sin(2 * np.pi * 7 * t + phase) + colored_noise(t.size, rng, 0.08)
        p3 = (1.15 - 0.12 * i) * np.exp(-0.5 * ((t - 0.31) / 0.065) ** 2)
        n2 = -0.28 * np.exp(-0.5 * ((t - 0.18) / 0.035) ** 2)
        target.append(base + p3 + n2)
        nontarget.append(base * 0.8 + 0.22 * np.exp(-0.5 * ((t - 0.28) / 0.075) ** 2))
    return t, np.array(target), np.array(nontarget), ["Pz", "Cz", "Fz"]


def sleep_signals(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fs = 64
    t = np.linspace(0, 30.0, fs * 30, endpoint=False)
    wake = 0.42 * np.sin(2 * np.pi * 10.5 * t) + 0.18 * np.sin(2 * np.pi * 18 * t) + colored_noise(t.size, rng, 0.20, 81)
    nrem = 1.05 * np.sin(2 * np.pi * 1.2 * t) + 0.22 * np.sin(2 * np.pi * 13.0 * t) * np.exp(
        -0.5 * ((t - 15.0) / 1.0) ** 2
    )
    nrem += -1.4 * np.exp(-0.5 * ((t - 8.4) / 0.18) ** 2) + colored_noise(t.size, rng, 0.18, 101)
    rem = 0.25 * np.sin(2 * np.pi * 6.0 * t + 0.7) + 0.18 * np.sin(2 * np.pi * 3.3 * t) + colored_noise(t.size, rng, 0.24, 61)
    return t, np.array([wake, nrem, rem]), ["Wake", "NREM", "REM"]


def ssvep_signals(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, list[str], float]:
    fs = 256
    t = np.linspace(0, 2.0, fs * 2, endpoint=False)
    freq = 12.0
    signals = []
    for amp, phase in [(1.05, 0.0), (0.92, 0.45), (0.86, 0.9), (0.62, 1.2)]:
        s = amp * np.sin(2 * np.pi * freq * t + phase)
        s += 0.32 * np.sin(2 * np.pi * (freq * 2) * t + phase * 0.5)
        s += 0.22 * np.sin(2 * np.pi * 8.0 * t)
        s += colored_noise(t.size, rng, 0.16)
        signals.append(s)
    return t, np.array(signals), ["Oz", "O1", "O2", "POz"], fs


def clinical_signals(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fs = 256
    t = np.linspace(0, 4.0, fs * 4, endpoint=False)
    event = np.exp(-0.5 * ((t - 2.05) / 0.018) ** 2) - 0.48 * np.exp(-0.5 * ((t - 2.12) / 0.06) ** 2)
    signals = []
    for amp, phase in [(0.95, 0.0), (0.75, 0.35), (0.55, 0.9), (0.45, 1.3)]:
        s = amp * np.sin(2 * np.pi * 2.5 * t + phase) + 0.35 * np.sin(2 * np.pi * 4.5 * t)
        s += (1.0 + 0.25 * amp) * event
        s += colored_noise(t.size, rng, 0.20, 55)
        signals.append(s)
    return t, np.array(signals), ["Fp1", "F7", "T7", "P7"]


def attention_signals(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, list[str]]:
    fs = 256
    t = np.linspace(0, 3.0, fs * 3, endpoint=False)
    envelope = 0.55 * np.sin(2 * np.pi * 4.0 * t) + 0.25 * np.sin(2 * np.pi * 8.0 * t + 0.6)
    signals = []
    for amp, phase in [(0.9, 0.1), (0.75, 0.7), (0.58, 1.1), (0.50, 1.8)]:
        s = amp * envelope + 0.32 * np.sin(2 * np.pi * 10.0 * t + phase)
        s += colored_noise(t.size, rng, 0.18)
        signals.append(s)
    return t, np.array(signals), ["T7", "T8", "Cz", "Pz"]


def draw_panel_header(ax: plt.Axes, label: str, title: str) -> None:
    ax.annotate(
        label,
        xy=(0, 1),
        xycoords="axes fraction",
        xytext=(-4, 8),
        textcoords="offset points",
        fontsize=PANEL_HEADER_SIZE,
        fontweight="bold",
        va="bottom",
        ha="right",
    )
    ax.annotate(
        title,
        xy=(0, 1),
        xycoords="axes fraction",
        xytext=(0, 8),
        textcoords="offset points",
        fontsize=PANEL_HEADER_SIZE,
        fontweight="bold",
        va="bottom",
        ha="left",
    )


def draw_panel_a(fig: plt.Figure, spec) -> None:
    frame = fig.add_subplot(spec)
    frame.axis("off")
    draw_panel_header(frame, "A", "EEG Signal Examples")
    gs = spec.subgridspec(2, 3, hspace=0.42, wspace=0.25)
    rng = np.random.default_rng(2026)

    ax = fig.add_subplot(gs[0, 0])
    t, sig, labels = motor_signals(rng)
    plot_multichannel_tile(ax, "MI epoch", t, sig, labels, PALETTE["blue"], "0-2 s", [(0.50, "cue")])
    ax.set_xticks([0, 1, 2])

    ax = fig.add_subplot(gs[0, 1])
    style_tile(ax)
    t, target, nontarget, labels = p300_signals(rng)
    offsets = np.arange(target.shape[0])[::-1] * 1.45
    target_z = zscore_rows(target)
    nontarget_z = zscore_rows(nontarget)
    for i, off in enumerate(offsets):
        ax.plot(t, target_z[i] * 0.45 + off, color=PALETTE["blue"], lw=scaled_lw(1.0), label="target" if i == 0 else None)
        ax.plot(
            t,
            nontarget_z[i] * 0.45 + off,
            color=PALETTE["red2"],
            lw=scaled_lw(0.9),
            alpha=0.95,
            label="non-target" if i == 0 else None,
        )
        ax.text(-0.012, off, labels[i], ha="right", va="center", fontsize=BODY_TEXT_SIZE)
    ax.axvline(0, color=PALETTE["gray3"], lw=scaled_lw(0.8))
    ax.text(0.30, offsets[0] + 0.58, "P300", ha="center", va="bottom", fontsize=BODY_TEXT_SIZE, color=PALETTE["blue"])
    ax.set_xlim(0, 0.8)
    ax.set_ylim(-1.15, offsets[0] + 0.95)
    ax.set_title("P300 target/non-target ERP", loc="left", pad=1.5, fontsize=SUBPANEL_TITLE_SIZE, fontweight="bold")
    ax.text(0.99, 0.96, "0-800 ms", transform=ax.transAxes, ha="right", va="top", fontsize=BODY_TEXT_SIZE)
    ax.set_xticks([0, 0.4, 0.8])
    ax.set_xticklabels(["0", "400", "800"])
    ax.legend(loc="lower right", handlelength=1.4, borderpad=0.1, labelspacing=0.2)
    plot_scale_bar(ax, 0.58, -0.82, 0.18, 0.45, "180 ms")

    ax = fig.add_subplot(gs[0, 2])
    t, sig, labels = sleep_signals(rng)
    plot_multichannel_tile(ax, "Sleep staging epoch", t, sig, labels, PALETTE["green3"], "30 s", None)
    ax.set_xticks([0, 10, 20, 30])

    ax = fig.add_subplot(gs[1, 0])
    t, sig, labels, fs = ssvep_signals(rng)
    plot_multichannel_tile(ax, "SSVEP/SSAEP frequency response", t, sig, labels, PALETTE["gold"], "0-2 s", None)
    ax.set_xticks([0, 1, 2])
    inset = ax.inset_axes([0.63, 0.18, 0.31, 0.36])
    y = zscore_rows(sig)[0]
    freqs = np.fft.rfftfreq(y.size, d=1 / fs)
    psd = np.abs(np.fft.rfft(y)) ** 2
    psd = psd / psd.max()
    inset.plot(freqs, psd, color=PALETTE["gold"], lw=scaled_lw(0.9))
    inset.axvline(12, color=PALETTE["red"], lw=scaled_lw(0.7), ls="--")
    inset.set_xlim(0, 32)
    inset.set_ylim(0, 1.04)
    inset.set_xticks([0, 12, 24])
    inset.set_yticks([])
    inset.set_title("PSD", fontsize=BODY_TEXT_SIZE, pad=0.5)
    inset.tick_params(axis="x", labelsize=TICK_TEXT_SIZE, length=2, width=scaled_lw(0.8))

    ax = fig.add_subplot(gs[1, 1])
    t, sig, labels = clinical_signals(rng)
    plot_multichannel_tile(
        ax,
        "Clinical EEG pattern",
        t,
        sig,
        labels,
        PALETTE["red"],
        "0-4 s",
        [(2.05, "event")],
    )
    ax.set_xticks([0, 2, 4])

    ax = fig.add_subplot(gs[1, 2])
    t, sig, labels = attention_signals(rng)
    plot_multichannel_tile(
        ax,
        "Emotion/auditory attention",
        t,
        sig,
        labels,
        PALETTE["violet"],
        "0-3 s",
        [(1.0, "stim")],
    )
    ax.set_xticks([0, 1.5, 3])


def panel_title(ax: plt.Axes, label: str, title: str) -> None:
    draw_panel_header(ax, label, title)


def draw_panel_b(ax: plt.Axes, df: pd.DataFrame) -> None:
    families = active_family_order(df)
    coverage = (
        df.groupby(["dataset_label", "family"], observed=False)["task"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=families, fill_value=0)
    )
    row_order = coverage.sum(axis=1).sort_values(ascending=False).index.tolist()
    coverage = coverage.loc[row_order]
    coverage_t = coverage.T
    mat = coverage_t.values.astype(float)
    im = ax.imshow(mat, aspect="auto", cmap=COVERAGE_CMAP, vmin=0, vmax=max(1, mat.max()))
    for y in range(mat.shape[0]):
        for x in range(mat.shape[1]):
            if mat[y, x] > 0:
                text_color = "white" if mat[y, x] >= 4 else PALETTE["gray3"]
                ax.text(x, y, str(int(mat[y, x])), ha="center", va="center", fontsize=BODY_TEXT_SIZE, color=text_color)
    ax.set_xticks(range(len(row_order)))
    ax.set_xticklabels(row_order, rotation=45, ha="right", rotation_mode="anchor", fontsize=TICK_TEXT_SIZE)
    ax.set_yticks(range(len(families)))
    ax.set_yticklabels([FAMILY_SHORT[f] for f in families], fontsize=BODY_TEXT_SIZE)
    ax.tick_params(length=0)
    ax.set_xlabel("")
    ax.set_ylabel("")
    for spine in ax.spines.values():
        spine.set_visible(False)
    panel_title(ax, "A", "Coverage Map")
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.025, pad=0.012)
    cbar.set_label("unique task settings", fontsize=AXIS_LABEL_SIZE)
    cbar.ax.tick_params(labelsize=TICK_TEXT_SIZE, length=2, width=scaled_lw(0.8))


def draw_panel_c(ax: plt.Axes, df: pd.DataFrame) -> None:
    families = active_family_order(df)
    success = df[df["success"]].copy()
    mean_f1 = (
        success.groupby(["model", "family"], observed=False)["final_f1_macro"]
        .mean()
        .unstack()
        .reindex(index=MODEL_ORDER, columns=families)
    )
    counts = (
        success.groupby(["model", "family"], observed=False)["final_f1_macro"]
        .count()
        .unstack()
        .reindex(index=MODEL_ORDER, columns=families)
        .fillna(0)
        .astype(int)
    )
    matrix = np.ma.masked_invalid(mean_f1.values.astype(float))
    cmap = USABILITY_CMAP.copy()
    cmap.set_bad("#EEEEEE")
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for y, model in enumerate(MODEL_ORDER):
        for x, family in enumerate(families):
            value = mean_f1.loc[model, family]
            n = int(counts.loc[model, family])
            if pd.isna(value) or n == 0:
                ax.text(x, y, "NA", ha="center", va="center", fontsize=HEATMAP_CELL_TEXT_SIZE, color=PALETTE["gray2"])
                continue
            color = "white" if value >= 0.62 else PALETTE["gray3"]
            ax.text(x, y, f"F1={value:.2f}\nn={n}", ha="center", va="center", fontsize=HEATMAP_CELL_TEXT_SIZE, color=color)
    ax.set_xticks(range(len(families)))
    ax.set_xticklabels(
        [FAMILY_SHORT[f] for f in families],
        rotation=45,
        ha="right",
        rotation_mode="anchor",
        fontsize=TICK_TEXT_SIZE,
    )
    ax.set_yticks(range(len(MODEL_ORDER)))
    ax.set_yticklabels([MODEL_LABELS[m] for m in MODEL_ORDER], fontsize=TICK_TEXT_SIZE)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    panel_title(ax, "B", "Model F1 Heatmap")
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.035, pad=0.016)
    cbar.set_label("mean macro-F1", fontsize=AXIS_LABEL_SIZE)
    cbar.ax.tick_params(labelsize=TICK_TEXT_SIZE, length=2, width=scaled_lw(0.8))


def jittered_points(x_center: float, n: int, width: float, rng: np.random.Generator) -> np.ndarray:
    if n <= 1:
        return np.array([x_center])
    return x_center + rng.uniform(-width, width, n)


def draw_panel_d(ax: plt.Axes, df: pd.DataFrame) -> None:
    rng = np.random.default_rng(7)
    success = df[df["success"]].copy()
    families = active_family_order(success)
    data = [success.loc[success["family"].astype(str).eq(f), "acc_above_chance"].dropna().to_numpy() * 100 for f in families]
    positions = np.arange(len(families))
    nonempty_positions = [pos for pos, vals in zip(positions, data) if vals.size > 0]
    nonempty_data = [vals for vals in data if vals.size > 0]
    if nonempty_data:
        viol = ax.violinplot(
            nonempty_data,
            positions=nonempty_positions,
            widths=0.78,
            showextrema=False,
            showmeans=False,
        )
        for body in viol["bodies"]:
            body.set_facecolor(PALETTE["blue2"])
            body.set_edgecolor(PALETTE["blue"])
            body.set_alpha(0.16)
            body.set_linewidth(scaled_lw(0.8))
    for i, vals in enumerate(data):
        if vals.size == 0:
            continue
        x = jittered_points(i, vals.size, 0.18, rng)
        ax.scatter(x, vals, s=scaled_s(7), color=FAMILY_COLORS[families[i]], alpha=0.42, linewidths=0)
        q1, med, q3 = np.percentile(vals, [25, 50, 75])
        ax.plot([i - 0.24, i + 0.24], [med, med], color=PALETTE["gray3"], lw=scaled_lw(1.2))
        ax.plot([i, i], [q1, q3], color=PALETTE["gray3"], lw=scaled_lw(1.0))
    ax.axhline(0, color=PALETTE["gray2"], lw=scaled_lw(0.9), ls="--")
    ax.set_xticks(positions)
    ax.set_xticklabels([FAMILY_SHORT[f].replace("\n", " ") for f in families], rotation=35, ha="right")
    ax.set_ylabel("Test accuracy above chance (pp)")
    ax.grid(axis="y", color="#E8E8E8", lw=scaled_lw(0.6))
    panel_title(ax, "C", "Accuracy Above Chance")


def draw_panel_e(ax: plt.Axes, df: pd.DataFrame) -> None:
    success = df[df["success"]].copy()
    pair = (
        success.pivot_table(
            index=["model", "dataset", "task"],
            columns="split_mode",
            values="final_f1_macro",
            aggfunc="mean",
        )
        .dropna(subset=["cs", "ws"])
        .reset_index()
    )
    pair["family"] = pair["task"].map(infer_family)
    families = active_family_order(pair)
    means = pair.groupby("family")[["cs", "ws"]].mean().reindex(families)
    counts = pair.groupby("family").size().reindex(families).fillna(0).astype(int)
    x = np.arange(len(families))
    for i, fam in enumerate(families):
        if pd.isna(means.loc[fam, "cs"]):
            continue
        ax.plot([i - 0.17, i + 0.17], [means.loc[fam, "cs"], means.loc[fam, "ws"]], color=PALETTE["gray1"], lw=scaled_lw(2.0))
        ax.scatter(
            i - 0.17,
            means.loc[fam, "cs"],
            s=scaled_s(42),
            color=PALETTE["red2"],
            edgecolor=PALETTE["gray3"],
            lw=scaled_lw(0.5),
            zorder=3,
        )
        ax.scatter(
            i + 0.17,
            means.loc[fam, "ws"],
            s=scaled_s(42),
            color=PALETTE["blue2"],
            edgecolor=PALETTE["gray3"],
            lw=scaled_lw(0.5),
            zorder=3,
        )
        gap = (means.loc[fam, "ws"] - means.loc[fam, "cs"]) * 100
        ax.text(i, max(means.loc[fam, "cs"], means.loc[fam, "ws"]) + 0.04, f"{gap:+.0f}", ha="center", va="bottom", fontsize=BODY_TEXT_SIZE)
        ax.text(i, 0.03, f"n={counts.loc[fam]}", ha="center", va="bottom", fontsize=BODY_TEXT_SIZE, color=PALETTE["gray2"])
    overall_gap = (pair["ws"] - pair["cs"]).mean() * 100
    ax.text(0.02, 0.93, f"mean WS-CS gap: {overall_gap:+.1f} pp", transform=ax.transAxes, fontsize=BODY_TEXT_SIZE, color=PALETTE["gray2"])
    ax.scatter([], [], s=scaled_s(38), color=PALETTE["red2"], edgecolor=PALETTE["gray3"], lw=scaled_lw(0.5), label="CS")
    ax.scatter([], [], s=scaled_s(38), color=PALETTE["blue2"], edgecolor=PALETTE["gray3"], lw=scaled_lw(0.5), label="WS")
    ax.legend(loc="upper right", handletextpad=0.3, borderaxespad=0.1)
    ax.set_ylim(0.0, 1.3)
    ax.set_xticks(x)
    ax.set_xticklabels([FAMILY_SHORT[f].replace("\n", " ") for f in families], rotation=35, ha="right")
    ax.set_ylabel("Macro-F1")
    ax.grid(axis="y", color="#E8E8E8", lw=scaled_lw(0.6))
    panel_title(ax, "D", "CS vs WS Generalization")


def draw_panel_f(ax: plt.Axes, df: pd.DataFrame) -> None:
    rng = np.random.default_rng(12)
    success = df[df["success"]].dropna(subset=["n_classes", "final_f1_macro"]).copy()
    levels = sorted(int(x) for x in success["n_classes"].dropna().unique())
    positions = np.arange(len(levels))
    medians = []
    for i, cls in enumerate(levels):
        vals = success.loc[success["n_classes"].eq(cls), "final_f1_macro"].to_numpy()
        medians.append(np.median(vals))
        ax.scatter(
            jittered_points(i, vals.size, 0.18, rng),
            vals,
            s=scaled_s(7),
            color=PALETTE["blue2"],
            alpha=0.38,
            linewidths=0,
        )
        q1, med, q3 = np.percentile(vals, [25, 50, 75])
        ax.plot([i - 0.24, i + 0.24], [med, med], color=PALETTE["gray3"], lw=scaled_lw(1.2))
        ax.plot([i, i], [q1, q3], color=PALETTE["gray3"], lw=scaled_lw(1.0))
        label_y = 0.09 if cls in {3, 9, 11} else 0.03
        ax.text(i, label_y, f"n={vals.size}", ha="center", va="bottom", fontsize=BODY_TEXT_SIZE, color=PALETTE["gray2"])
    ax.plot(positions, medians, color=PALETTE["red"], lw=scaled_lw(1.4), marker="o", ms=scaled_ms(3.5), label="median")
    xlog = np.log2(success["n_classes"].to_numpy())
    slope, intercept = np.polyfit(xlog, success["final_f1_macro"].to_numpy(), deg=1)
    ax.text(
        0.04,
        0.93,
        f"log2-class slope: {slope:+.2f}",
        transform=ax.transAxes,
        fontsize=BODY_TEXT_SIZE,
        color=PALETTE["gray2"],
    )
    ax.set_ylim(0, 1.05)
    ax.set_xticks(positions)
    ax.set_xticklabels([str(c) for c in levels])
    ax.set_xlabel("Number of classes")
    ax.set_ylabel("Macro-F1")
    ax.grid(axis="y", color="#E8E8E8", lw=scaled_lw(0.6))
    panel_title(ax, "E", "Difficulty Gradient")


def load_epoch_metrics(run_relpath: str) -> pd.DataFrame:
    path = DATA_ROOT / run_relpath / "metrics" / "epoch_metrics.jsonl"
    rows = []
    if not path.exists():
        return pd.DataFrame()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        val = payload.get("val_metrics") or {}
        test = payload.get("test_metrics") or {}
        metric_name = payload.get("selection_metric_name") or "f1_macro"
        rows.append(
            {
                "epoch": payload.get("epoch"),
                "train_loss": payload.get("train_loss"),
                "is_best": bool(payload.get("is_best")),
                "val_f1_macro": val.get("f1_macro"),
                "val_acc": val.get("acc"),
                "val_kappa": val.get("kappa"),
                "test_f1_macro": test.get("f1_macro"),
                "metric_name": metric_name,
            }
        )
    return pd.DataFrame(rows).sort_values("epoch")


def select_learning_examples(df: pd.DataFrame) -> list[pd.Series]:
    success = df[df["success"]].copy()
    choices = []
    for fam in active_family_order(success):
        sub = success[success["family"].astype(str).eq(fam)].copy()
        if sub.empty:
            continue
        sub["has_epochs"] = sub["run_relpath"].map(
            lambda p: (DATA_ROOT / str(p) / "metrics" / "epoch_metrics.jsonl").exists()
        )
        sub = sub[sub["has_epochs"]].copy()
        if sub.empty:
            continue
        sub = sub.sort_values(["final_f1_macro", "final_acc"], ascending=False)
        if not sub.empty:
            choices.append(sub.iloc[0])
    return choices


def normalize_loss(loss: np.ndarray) -> np.ndarray:
    loss = np.asarray(loss, dtype=float)
    loss = np.log1p(np.maximum(loss, 0))
    if np.nanmax(loss) - np.nanmin(loss) < 1e-8:
        return np.zeros_like(loss) + 0.5
    return (loss - np.nanmin(loss)) / (np.nanmax(loss) - np.nanmin(loss))


def normalize_metric(metric: np.ndarray) -> np.ndarray:
    metric = np.asarray(metric, dtype=float)
    if np.nanmax(metric) - np.nanmin(metric) < 1e-8:
        return np.zeros_like(metric) + np.nanmean(metric)
    return metric


def metric_series(hist: pd.DataFrame) -> tuple[np.ndarray, str]:
    candidates = [
        ("val_f1_macro", "Val. macro-F1"),
        ("val_acc", "Val. accuracy"),
        ("val_kappa", "Val. kappa"),
    ]
    for col, label in candidates:
        if col in hist and hist[col].notna().any():
            return hist[col].to_numpy(dtype=float), label
    return np.zeros(len(hist)), "Val. metric"


def smooth_curve(values: np.ndarray, window: int = 3) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.size < window:
        return values
    padded = np.pad(values, (window // 2, window // 2), mode="edge")
    kernel = np.ones(window) / window
    return np.convolve(padded, kernel, mode="valid")


def compact_family_title(family: str) -> str:
    labels = {
        "Motor imagery": "MI",
        "P300": "P300",
        "Sleep staging": "Sleep",
        "SSVEP/SSAEP": "SSVEP/SSAEP",
        "Clinical EEG": "Clinical",
        "Emotion/attention": "Emotion/Attn",
        "Cognitive": "Cognitive",
    }
    return labels.get(str(family), str(family))


def draw_panel_g(fig: plt.Figure, spec, df: pd.DataFrame) -> None:
    frame = fig.add_subplot(spec)
    frame.axis("off")
    draw_panel_header(frame, "F", "Learning Dynamics")
    examples = select_learning_examples(df)
    if not examples:
        frame.text(0.02, 0.5, "No retained runs with epoch metrics.", fontsize=BODY_TEXT_SIZE, color=PALETTE["gray2"])
        return
    gs = spec.subgridspec(1, len(examples), wspace=0.32)
    for i, run in enumerate(examples):
        ax = fig.add_subplot(gs[0, i])
        hist = load_epoch_metrics(str(run["run_relpath"]))
        if hist.empty:
            ax.axis("off")
            continue
        epochs = hist["epoch"].to_numpy(dtype=float)
        loss = normalize_loss(hist["train_loss"].to_numpy(dtype=float))
        val, _ = metric_series(hist)
        test = hist["test_f1_macro"].to_numpy(dtype=float) if hist["test_f1_macro"].notna().any() else None
        best_epoch = run.get("best_epoch")
        color = FAMILY_COLORS[str(run["family"])]
        loss_ax = ax.twinx()
        loss_ax.plot(epochs, loss, color=PALETTE["gray2"], lw=scaled_lw(1.15), alpha=0.72)
        loss_ax.fill_between(epochs, 0, loss, color=PALETTE["gray1"], alpha=0.10, linewidth=0)
        loss_ax.set_ylim(-0.02, 1.05)
        loss_ax.set_yticks([])
        loss_ax.spines["right"].set_visible(False)
        if test is not None:
            ax.plot(epochs, smooth_curve(test, 3), color=color, lw=scaled_lw(0.9), ls="--", alpha=0.55)
        ax.plot(epochs, val, color=color, lw=scaled_lw(0.75), alpha=0.25)
        ax.plot(epochs, smooth_curve(val, 3), color=color, lw=scaled_lw(1.8))
        if not pd.isna(best_epoch):
            ax.axvline(float(best_epoch), color=PALETTE["red"], lw=scaled_lw(0.8), ls="--", alpha=0.8)
            idx = int(np.argmin(np.abs(epochs - float(best_epoch))))
            if 0 <= idx < len(val):
                ax.scatter([epochs[idx]], [val[idx]], s=20, color="white", edgecolor=color, lw=scaled_lw(1.0), zorder=5)
                ax.text(
                    epochs[idx],
                    min(1.0, val[idx] + 0.09),
                    f"best {int(best_epoch)}",
                    ha="center",
                    va="bottom",
                    fontsize=BODY_TEXT_SIZE,
                    color=PALETTE["red"],
                )
        title = f"{compact_family_title(str(run['family']))} | {MODEL_LABELS.get(run['model'], run['model'])} {str(run['split_mode']).upper()}"
        ax.set_title(
            title,
            fontsize=THIRD_ROW_SUBPANEL_TITLE_SIZE,
            pad=2.5,
            fontweight="normal",
            color=FG_TITLE_COLORS[i % 2],
        )
        ax.set_ylim(0, 1.3)
        ax.set_xlim(1, max(epochs) if len(epochs) else 50)
        ax.set_facecolor("#FBFCFE")
        ax.grid(axis="y", color="#E8E8E8", lw=scaled_lw(0.55))
        if i == 0:
            ax.set_ylabel("Macro-F1 / val. metric")
        else:
            ax.set_yticklabels([])
        ax.text(
            0.03,
            0.06,
            f"F1={run['final_f1_macro']:.2f}",
            transform=ax.transAxes,
            fontsize=BODY_TEXT_SIZE,
            color=PALETTE["gray2"],
        )


def draw_panel_h(ax: plt.Axes, df: pd.DataFrame) -> None:
    failed = df[~df["success"]].copy()
    causes = ["Channel montage", "Empty split", "OOM/runtime", "Adapter/input", "Data/cache", "Other"]
    counts = failed["failure_cause"].value_counts().reindex(causes, fill_value=0)
    colors = [PALETTE["red"], PALETTE["red2"], PALETTE["gold"], PALETTE["violet"], PALETTE["blue2"], PALETTE["gray1"]]
    y = np.arange(len(causes))
    bars = ax.barh(y, counts.values, color=colors, edgecolor=PALETTE["gray3"], linewidth=scaled_lw(0.5))
    total_failed = max(1, int(len(failed)))
    for bar, val in zip(bars, counts.values):
        ax.text(
            bar.get_width() + max(counts.max(), 1) * 0.025,
            bar.get_y() + bar.get_height() / 2,
            f"{int(val)} ({val / total_failed * 100:.0f}%)",
            va="center",
            fontsize=SMALL_TEXT_SIZE,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(causes, fontsize=TICK_TEXT_SIZE)
    ax.invert_yaxis()
    ax.set_xlabel("Failed runs")
    ax.set_xlim(0, max(counts.max() * 1.22, 1))
    ax.grid(axis="x", color="#E8E8E8", lw=scaled_lw(0.6))
    panel_title(ax, "H", "Failure Diagnostics")
    ax.text(
        0.02,
        -0.18,
        f"{len(failed)} failed / {len(df)} scheduled; failure labels parsed from status.json",
        transform=ax.transAxes,
        fontsize=SMALL_TEXT_SIZE,
        color=PALETTE["gray2"],
    )


def select_curve_gallery(df: pd.DataFrame, exclude_run_ids: set[str], max_count: int = 12) -> list[pd.Series]:
    success = df[df["success"]].copy()
    success["has_epochs"] = success["run_relpath"].map(
        lambda p: (DATA_ROOT / str(p) / "metrics" / "epoch_metrics.jsonl").exists()
    )
    success = success[success["has_epochs"] & ~success["run_id"].isin(exclude_run_ids)]
    success = success.dropna(subset=["final_f1_macro"])

    choices: list[pd.Series] = []
    used: set[str] = set()
    families = active_family_order(success)

    for fam in families:
        sub = success[success["family"].astype(str).eq(fam)].sort_values("final_f1_macro", ascending=False)
        if not sub.empty:
            row = sub.iloc[0]
            choices.append(row)
            used.add(str(row["run_id"]))

    while len(choices) < max_count:
        added = False
        for fam in families:
            sub = success[
                success["family"].astype(str).eq(fam) & ~success["run_id"].astype(str).isin(used)
            ].copy()
            if sub.empty:
                continue
            median_f1 = sub["final_f1_macro"].median()
            sub["median_distance"] = (sub["final_f1_macro"] - median_f1).abs()
            row = sub.sort_values(["median_distance", "final_f1_macro"], ascending=[True, False]).iloc[0]
            choices.append(row)
            used.add(str(row["run_id"]))
            added = True
            if len(choices) >= max_count:
                break
        if not added:
            break
    return choices[:max_count]


def draw_panel_i(fig: plt.Figure, spec, df: pd.DataFrame) -> None:
    frame = fig.add_subplot(spec)
    frame.axis("off")
    draw_panel_header(frame, "G", "Learning Curve Gallery")
    frame.text(
        -0.1,
        -0.16,
        FG_EXPLANATION_TEXT,
        transform=frame.transAxes,
        fontsize=FG_EXPLANATION_SIZE,
        color=PALETTE["gray2"],
        ha="left",
        va="top",
    )
    excluded = {str(row["run_id"]) for row in select_learning_examples(df)}
    examples = select_curve_gallery(df, excluded, max_count=12)
    gs = spec.subgridspec(2, 6, hspace=0.55, wspace=0.32)
    for i, run in enumerate(examples):
        ax = fig.add_subplot(gs[i // 6, i % 6])
        hist = load_epoch_metrics(str(run["run_relpath"]))
        if hist.empty:
            ax.axis("off")
            continue
        epochs = hist["epoch"].to_numpy(dtype=float)
        loss = normalize_loss(hist["train_loss"].to_numpy(dtype=float))
        val, _ = metric_series(hist)
        color = FAMILY_COLORS[str(run["family"])]
        loss_ax = ax.twinx()
        loss_ax.plot(epochs, loss, color=PALETTE["gray2"], lw=scaled_lw(1.15), alpha=0.72)
        loss_ax.fill_between(epochs, 0, loss, color=PALETTE["gray1"], alpha=0.10, linewidth=0)
        loss_ax.set_ylim(-0.02, 1.05)
        loss_ax.set_yticks([])
        loss_ax.spines["right"].set_visible(False)
        ax.plot(epochs, val, color=color, lw=scaled_lw(0.75), alpha=0.22)
        ax.plot(epochs, smooth_curve(val, 3), color=color, lw=scaled_lw(1.45))
        if hist["test_f1_macro"].notna().any():
            ax.plot(
                epochs,
                smooth_curve(hist["test_f1_macro"].to_numpy(dtype=float), 3),
                color=PALETTE["gray2"],
                lw=scaled_lw(0.8),
                ls="--",
                alpha=0.60,
            )
        best_epoch = run.get("best_epoch")
        if not pd.isna(best_epoch):
            ax.axvline(float(best_epoch), color=PALETTE["red"], lw=scaled_lw(0.65), ls="--", alpha=0.55)
        ax.set_ylim(0, 1.03)
        ax.set_xlim(1, max(epochs) if len(epochs) else 50)
        ax.set_facecolor("#FBFCFE")
        ax.grid(axis="y", color="#ECECEC", lw=scaled_lw(0.45))
        family_label = FAMILY_SHORT[str(run["family"])].replace("\n", " ")
        model_label = MODEL_LABELS.get(str(run["model"]), str(run["model"]))
        split = str(run["split_mode"]).upper()
        dataset_text = dataset_label(str(run["dataset"]))
        ax.set_title(
            f"{family_label} | {model_label} {split}",
            fontsize=THIRD_ROW_SUBPANEL_TITLE_SIZE,
            pad=1.8,
            fontweight="normal",
            color=FG_TITLE_COLORS[(i % 6) % 2],
        )
        note_x = 0.03
        note_y = 0.08
        note_ha = "left"
        note_va = "bottom"
        if family_label == "MI" and model_label == "LaBraM" and split == "WS" and dataset_text == "BCIC IV-1":
            note_x, note_y, note_ha, note_va = 0.03, 0.97, "left", "top"
        elif family_label == "P300" and model_label == "LaBraM" and split == "CS" and dataset_text == "INRIA P300":
            note_x, note_y, note_ha, note_va = 0.03, 0.97, "left", "top"
        elif family_label == "SSVEP/SSAEP" and model_label == "CBraMod" and split == "CS" and dataset_text == "MigraineDB":
            note_x, note_y, note_ha, note_va = 0.97, 0.97, "right", "top"
        ax.text(
            note_x,
            note_y,
            f"{dataset_text}\nF1={run['final_f1_macro']:.2f}",
            transform=ax.transAxes,
            ha=note_ha,
            va=note_va,
            fontsize=BODY_TEXT_SIZE,
            color=PALETTE["gray2"],
        )
        if i // 6 != 1:
            ax.set_xticklabels([])
        if i % 6 == 0:
            ax.set_ylabel("Val. metric", fontsize=AXIS_LABEL_SIZE)
        else:
            ax.set_yticklabels([])
        ax.tick_params(labelsize=TICK_TEXT_SIZE, length=2, width=scaled_lw(0.8))


def save_summary(df: pd.DataFrame, paths: dict[str, str]) -> None:
    success = df[df["success"]]
    pair = (
        success.pivot_table(index=["model", "dataset", "task"], columns="split_mode", values="final_f1_macro", aggfunc="mean")
        .dropna(subset=["cs", "ws"])
    )
    summary = {
        "total_runs": int(len(df)),
        "success_runs": int(df["success"].sum()),
        "failed_runs": int((~df["success"]).sum()),
        "datasets": int(df["dataset"].nunique()),
        "task_definitions": int(df["task"].nunique()),
        "dataset_task_pairs": int((df["dataset"].astype(str) + ":" + df["task"].astype(str)).nunique()),
        "models": sorted(df["model"].dropna().unique().tolist()),
        "split_modes": sorted(df["split_mode"].dropna().unique().tolist()),
        "completed_documented_tasks": sorted(COMPLETED_DOCUMENTED_TASKS),
        "mean_ws_minus_cs_macro_f1_pp": float((pair["ws"] - pair["cs"]).mean() * 100) if not pair.empty else None,
        "failure_causes": df.loc[~df["success"], "failure_cause"].value_counts().to_dict(),
        "outputs": paths,
    }
    (FIG_DIR / "data_agent_main_figure_summary.json").write_text(json.dumps(summary, indent=2))


def build_figure(df: pd.DataFrame) -> plt.Figure:
    fig = plt.figure(figsize=(FIGURE_WIDTH_IN, FIGURE_HEIGHT_IN), constrained_layout=False)
    outer = fig.add_gridspec(
        4,
        12,
        height_ratios=ROW_HEIGHT_RATIOS,
        left=0.045,
        right=0.985,
        top=0.965,
        bottom=0.055,
        hspace=ROW_HSPACE,
        wspace=0.62,
    )

    ax_b = fig.add_subplot(outer[0, 0:6])
    draw_panel_b(ax_b, df)

    ax_c = fig.add_subplot(outer[0, 7:12])
    draw_panel_c(ax_c, df)

    second_row = outer[1, :].subgridspec(1, 5, width_ratios=SECOND_ROW_WIDTH_RATIOS, wspace=0.0)

    ax_d = fig.add_subplot(second_row[0, 0])
    draw_panel_d(ax_d, df)

    ax_e = fig.add_subplot(second_row[0, 2])
    draw_panel_e(ax_e, df)

    ax_f = fig.add_subplot(second_row[0, 4])
    draw_panel_f(ax_f, df)

    lower_rows = outer[2:, :].subgridspec(
        2,
        1,
        height_ratios=BASE_ROW_HEIGHT_RATIOS[2:],
        hspace=FG_ROW_HSPACE,
    )

    third_row = lower_rows[0, 0].subgridspec(3, 1, height_ratios=THIRD_ROW_VERTICAL_RATIOS, hspace=0.0)
    draw_panel_g(fig, third_row[1, 0], df)

    draw_panel_i(fig, lower_rows[1, 0], df)

    return fig


def main() -> None:
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load_scheduler_table()
    fig = build_figure(df)
    paths = {
        "pdf": str(FIG_DIR / "data_agent_main_figure.pdf"),
        "svg": str(FIG_DIR / "data_agent_main_figure.svg"),
        "png": str(FIG_DIR / "data_agent_main_figure.png"),
    }
    fig.savefig(paths["pdf"], bbox_inches="tight", pad_inches=0.08)
    fig.savefig(paths["svg"], bbox_inches="tight", pad_inches=0.08)
    fig.savefig(paths["png"], bbox_inches="tight", pad_inches=0.08, dpi=600)
    plt.close(fig)
    save_summary(df, paths)
    print(json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()

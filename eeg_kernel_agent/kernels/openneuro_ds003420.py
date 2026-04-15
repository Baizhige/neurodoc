"""openneuro_ds003420 stage1 kernel for EEGUnity.

HD-EEG visual naming and spelling task (Dataset 1 of the conneXion project).
Participants name/spell visually presented objects while 256-channel EEG is recorded.

Source: https://openneuro.org/datasets/ds003420 (ds003420)
Paper DOI: 10.1088/1741-2552.aad7b1
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

import mne
import numpy as np
import pandas as pd


# =============================================================================
# 被试者信息（来源：conneXion 项目数据集说明 / 论文补充材料）
# Annotator: LLM, 2026-06-02
# 注意：以下 age/sex/handedness 为 LLM 根据论文推断，需人类复核
# =============================================================================
_SUBJECT_DICT: Dict[str, Dict[str, Any]] = {
    "sub-01": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-02": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-03": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-04": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-05": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-06": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-07": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-08": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-09": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-10": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-11": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-12": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-13": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-14": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-15": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-16": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-17": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-18": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-19": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-20": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-21": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-22": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
    "sub-23": {"age": "unknown", "sex": "unknown", "handedness": "unknown"},
}
# Source: LLM 推断，需人类复核

# =============================================================================
# 通道重命名映射
# 来源：conneXion 数据集原始 EEG 文件；BrainVision 系统 256-channel 系统命名
# Annotator: LLM, 2026-06-02
# =============================================================================
# BrainVision 256-channel 系统通道列表（标准顺序）
_BRAINVISION_256_CHANNELS = [
    "Fp1", "Fp2", "Fpz", "AF7", "AF3", "AFz", "AF4", "AF8",
    "F7", "F5", "F3", "F1", "Fz", "F2", "F4", "F6", "F8",
    "FT7", "FT8", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "T7", "T8", "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
    "TP7", "TP8", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6",
    "P7", "P5", "P3", "P1", "Pz", "P2", "P4", "P6", "P8",
    "PO7", "PO5", "PO3", "POz", "PO4", "PO6", "PO8",
    "O1", "Oz", "O2",
    # 扩展通道（256 系统额外行）
    "VEOa", "VEOb", "HEOl", "HEOr",
    # 以下为占位符，实际 256-channel 有完整列表
]

# 常见非标准名称别名（从实际数据观察或论文推断）
_ALIAS_GROUPS = [
    # 标准 10-5 名称常见变体
    ("Fp1", ["Fp1", "EEG-Fp1"]),
    ("Fp2", ["Fp2", "EEG-Fp2"]),
    ("Fpz", ["Fpz", "EEG-Fpz"]),
    ("AF7", ["AF7", "EEG-AF7"]),
    ("AF3", ["AF3", "EEG-AF3"]),
    ("AFz", ["AFz", "EEG-AFz"]),
    ("AF4", ["AF4", "EEG-AF4"]),
    ("AF8", ["AF8", "EEG-AF8"]),
    ("F7", ["F7", "EEG-F7"]),
    ("F3", ["F3", "EEG-F3"]),
    ("Fz", ["Fz", "EEG-Fz"]),
    ("F4", ["F4", "EEG-F4"]),
    ("F8", ["F8", "EEG-F8"]),
    ("FC5", ["FC5", "EEG-FC5"]),
    ("FC3", ["FC3", "EEG-FC3"]),
    ("FC1", ["FC1", "EEG-FC1"]),
    ("FCz", ["FCz", "EEG-FCz"]),
    ("FC2", ["FC2", "EEG-FC2"]),
    ("FC4", ["FC4", "EEG-FC4"]),
    ("FC6", ["FC6", "EEG-FC6"]),
    ("T7", ["T7", "EEG-T7"]),
    ("T8", ["T8", "EEG-T8"]),
    ("C5", ["C5", "EEG-C5"]),
    ("C3", ["C3", "EEG-C3"]),
    ("C1", ["C1", "EEG-C1"]),
    ("Cz", ["Cz", "EEG-Cz"]),
    ("C2", ["C2", "EEG-C2"]),
    ("C4", ["C4", "EEG-C4"]),
    ("C6", ["C6", "EEG-C6"]),
    ("TP7", ["TP7", "EEG-TP7"]),
    ("TP8", ["TP8", "EEG-TP8"]),
    ("CP5", ["CP5", "EEG-CP5"]),
    ("CP3", ["CP3", "EEG-CP3"]),
    ("CP1", ["CP1", "EEG-CP1"]),
    ("CPz", ["CPz", "EEG-CPz"]),
    ("CP2", ["CP2", "EEG-CP2"]),
    ("CP4", ["CP4", "EEG-CP4"]),
    ("CP6", ["CP6", "EEG-CP6"]),
    ("P7", ["P7", "EEG-P7"]),
    ("P5", ["P5", "EEG-P5"]),
    ("P3", ["P3", "EEG-P3"]),
    ("P1", ["P1", "EEG-P1"]),
    ("Pz", ["Pz", "EEG-Pz"]),
    ("P2", ["P2", "EEG-P2"]),
    ("P4", ["P4", "EEG-P4"]),
    ("P6", ["P6", "EEG-P6"]),
    ("P8", ["P8", "EEG-P8"]),
    ("PO7", ["PO7", "EEG-PO7"]),
    ("PO5", ["PO5", "EEG-PO5"]),
    ("PO3", ["PO3", "EEG-PO3"]),
    ("POz", ["POz", "EEG-POz"]),
    ("PO4", ["PO4", "EEG-PO4"]),
    ("PO6", ["PO6", "EEG-PO6"]),
    ("PO8", ["PO8", "EEG-PO8"]),
    ("O1", ["O1", "EEG-O1"]),
    ("Oz", ["Oz", "EEG-Oz"]),
    ("O2", ["O2", "EEG-O2"]),
    # 眼动通道
    ("VEOa", ["VEOa", "HEOGL", "VEO"]),
    ("VEOb", ["VEOb", "HEOGR"]),
    ("HEOl", ["HEOl", "EOGleft"]),
    ("HEOr", ["HEOr", "EOGright"]),
    # 数字化通道编号（常见于部分文件）
    ("Fz", ["31", "32"]),   # 需确认具体映射
]

# 通用数字索引 → 标准名映射（fallback）
_DIGIT_CHANNEL_MAP: Dict[str, str] = {}


def _build_channel_rename_map(raw: mne.io.BaseRaw) -> Dict[str, str]:
    """根据原始数据中的通道名为 EEGUnity 构建重命名映射."""
    rename_map: Dict[str, str] = {}
    existing_names = set(raw.ch_names)

    for target_name, aliases in _ALIAS_GROUPS:
        for source_name in aliases:
            if source_name in existing_names and source_name != target_name:
                rename_map[source_name] = target_name
                break

    # fallback: 纯数字名称（EEG-0 格式）
    for ch in existing_names:
        if re.match(r"^(EEG[-_])?(\d+)$", ch):
            # 尝试映射为标准名，若无映射则跳过
            mapped = _DIGIT_CHANNEL_MAP.get(ch)
            if mapped:
                rename_map[ch] = mapped

    return rename_map


def _detect_paradigm(file_path: str) -> Optional[str]:
    """基于文件路径检测范式类型.

    路径示例: sub-01/ses-S1/eeg/sub-01_ses-S1_task-pictureNaming_run-01_ieeg.fif
    """
    basename = os.path.basename(file_path).lower()
    if "pictureNaming" in basename or "naming" in basename:
        return "pictureNaming"
    elif "spelling" in basename or "spell" in basename:
        return "spelling"
    elif "control" in basename:
        return "control"
    return None


def _remap_events_from_tsv(
    raw: mne.io.BaseRaw,
    row,
    file_path: str,
) -> mne.io.BaseRaw:
    """从 events.tsv 读取事件并构建 MNE annotations.

    events.tsv 列：onset, duration, trial_type, value, stimuli, response_time
    value: 0 = stimulus onset (meaningful), 1 = response
    额外 trial_type 含: D249/D250 用于区分 meaningful/meaningless
    """
    # 查找 events.tsv
    events_tsv = None
    base_dir = os.path.dirname(file_path)
    for fname in os.listdir(base_dir):
        if fname.endswith("_events.tsv"):
            events_tsv = os.path.join(base_dir, fname)
            break

    if events_tsv is None or not os.path.exists(events_tsv):
        # 无 events.tsv 时使用 raw 内置 annotations
        return raw

    events_df = pd.read_csv(events_tsv, sep="\t")
    paradigm = _detect_paradigm(file_path)

    onsets = []
    durations = []
    descriptions = []

    for _, ev in events_df.iterrows():
        onset = float(ev.get("onset", 0))
        duration = float(ev.get("duration", 0))
        value = str(ev.get("value", "")).strip()
        trial_type = str(ev.get("trial_type", "")).strip()
        stimuli = str(ev.get("stimuli", "")).strip()

        # 事件映射（raw meta）
        if value == "0":
            desc = f"stimulus_onset"
            if trial_type in ("D249", "pictureNaming"):
                desc = f"trigger/D249"
            elif trial_type in ("D250", "meaningless"):
                desc = f"trigger/D250"
        elif value == "1":
            desc = "response"
        else:
            desc = f"event_{value}"

        # super meta: 添加 stimuli 标签
        if stimuli and stimuli not in ("n/a", "nan"):
            desc = f"{desc}/{stimuli}"

        onsets.append(onset)
        durations.append(duration)
        descriptions.append(desc)

    if onsets:
        annotations = mne.Annotations(
            onset=np.array(onsets),
            duration=np.array(durations),
            description=descriptions,
        )
        raw.set_annotations(annotations)

    return raw


def _inject_reaction_time_misc(raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
    """将 reaction_time 从 events.tsv 注入为 misc 通道或 annotations.

    reaction_time 单位为秒（从 stimulus onset 到 vocalization）。
    """
    file_path = row.get("File Path", "")
    if not file_path:
        return raw

    base_dir = os.path.dirname(file_path)
    events_tsv = None
    for fname in os.listdir(base_dir):
        if fname.endswith("_events.tsv"):
            events_tsv = os.path.join(base_dir, fname)
            break

    if events_tsv is None or not os.path.exists(events_tsv):
        return raw

    try:
        events_df = pd.read_csv(events_tsv, sep="\t")
    except Exception:
        return raw

    if "response_time" not in events_df.columns and "response_time" not in events_df.columns:
        return raw

    # response_time 列
    rt_col = "response_time" if "response_time" in events_df.columns else "response_time"
    if rt_col not in events_df.columns:
        for c in events_df.columns:
            if "response" in c.lower() or "reaction" in c.lower():
                rt_col = c
                break

    if rt_col not in events_df.columns:
        return raw

    # 已有 annotations 中添加 rt 信息（作为 annotation description 扩展）
    annotations = raw.annotations.copy()
    if len(annotations) > 0:
        new_descriptions = []
        for idx, desc in enumerate(annotations.description):
            if idx < len(events_df):
                ev_row = events_df.iloc[idx]
                rt_val = ev_row.get(rt_col)
                if pd.notna(rt_val) and rt_val != "n/a":
                    try:
                        rt_ms = float(rt_val) * 1000  # s → ms
                        desc = f"{desc}/rt={rt_ms:.0f}ms"
                    except (ValueError, TypeError):
                        pass
            new_descriptions.append(desc)
        annotations.description = new_descriptions
        raw.set_annotations(annotations)

    return raw


def _apply_montage(raw: mne.io.BaseRaw) -> mne.io.BaseRaw:
    """设置标准 10-5 系统 montage.

    仅对已重命名且在 standard_1020 系统中存在的通道设置 montage。
    """
    try:
        standard_montage = mne.channels.make_standard_montage("standard_1020")
        # 保留 raw 中实际存在的通道
        common_chs = set(raw.ch_names) & set(standard_montage.ch_names)
        if len(common_chs) >= 20:  # 至少 20 个通道才设置
            raw.set_montage(standard_montage, on_missing="warn")
    except Exception as e:
        # 若 montage 设置失败，记录但不中断
        print(f"[openneuro_ds003420] Montage setup warning: {e}")

    return raw


class OpenNeuroDS003420Kernel:
    """Stage1 kernel for openneuro_ds003420 — HD-EEG Visual Naming dataset."""

    KERNEL_ID: str = "openneuro-ds003420-stage1"

    def apply(self, udataset, raw: mne.io.BaseRaw, row) -> mne.io.BaseRaw:
        file_path = str(row.get("File Path", ""))

        # -------------------------------------------------------------------------
        # 1. 通道重命名（channel rename BEFORE set_montage）
        # -------------------------------------------------------------------------
        rename_map = _build_channel_rename_map(raw)
        if rename_map:
            renaming = {k: v for k, v in rename_map.items() if k in raw.ch_names}
            if renaming:
                raw.rename_channels(renaming)

        # -------------------------------------------------------------------------
        # 2. 设置 montage（通道重命名后调用）
        # -------------------------------------------------------------------------
        raw = _apply_montage(raw)

        # -------------------------------------------------------------------------
        # 3. 事件处理：从 events.tsv 构建 annotations
        # -------------------------------------------------------------------------
        raw = _remap_events_from_tsv(raw, row, file_path)

        # -------------------------------------------------------------------------
        # 4. 反应时间注入（super meta）
        # -------------------------------------------------------------------------
        raw = _inject_reaction_time_misc(raw, row)

        # -------------------------------------------------------------------------
        # 5. eegunity_description 元信息
        # -------------------------------------------------------------------------
        # 提取 subject ID
        subject_id = ""
        if "sub-" in file_path:
            match = re.search(r"(sub-\d+)", file_path)
            if match:
                subject_id = match.group(1)

        sub_info = _SUBJECT_DICT.get(subject_id, {})
        original_desc = raw.info.get("description", "")

        description_dict = {
            "original_description": original_desc if original_desc else "",
            "eegunity_description": {
                "age": sub_info.get("age", "unknown"),   # LLM 推断，需人类复核
                "sex": sub_info.get("sex", "unknown"),    # LLM 推断，需人类复核
                "amplifier": "BrainAmp",                  # LLM 推断，需人类复核（基于 conneXion 项目惯例）
                "cap": "Ag/AgCl",                          # LLM 推断，需人类复核
                "handedness": sub_info.get("handedness", "unknown"),  # LLM 推断，需人类复核
            },
        }
        raw.info["description"] = json.dumps(description_dict)

        return raw


KERNEL = OpenNeuroDS003420Kernel()
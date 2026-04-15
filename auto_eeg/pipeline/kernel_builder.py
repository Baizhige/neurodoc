"""Phase 5: Iterative kernel generation + subprocess testing loop."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple  # noqa: F401

from .budget import BudgetExhausted
from .ref_analyzer import _parse_json

BIDS_ROOT = Path(__file__).parent.parent.parent
KERNELS_DIR = BIDS_ROOT / "app_kernel" / "kernels"


_KERNEL_SYSTEM = """\
You are an EEG kernel engineer. Write a complete Python kernel file for EEGUnity.

Output your response as a Python code block ONLY — no explanation, no JSON:
```python
<full kernel source code here>
```

MANDATORY requirements — violating any will cause rejection:
1. Last line of file: KERNEL = <ClassName>()
2. Method signature MUST be EXACTLY: def apply(self, udataset, raw, row) -> mne.io.BaseRaw:
   — DO NOT split across lines, DO NOT add type annotations to parameters, DO NOT rename udataset/raw/row
3. raw.info["description"] = json.dumps({
       "original_description": <original>,
       "eegunity_description": {"age": str, "sex": str, "amplifier": str, "cap": str, "handedness": str}
   })
4. age is always a STRING (e.g. "22", not 22)
5. sex is always lowercase: "male" / "female" / "unknown"
6. Inferred values: add comment  # LLM 推断，需人类复核
7. Channel rename BEFORE set_montage()
"""

_KERNEL_FIX_SYSTEM = """\
You are an EEG kernel engineer fixing a broken Python kernel for EEGUnity.
Fix ONLY what is broken. Output your fix as a Python code block ONLY:
```python
<full corrected kernel source code here>
```

MANDATORY: def apply(self, udataset, raw, row) -> mne.io.BaseRaw:  — exact signature, one line, no type hints on params."""

_RULEBOOK_VALIDATION_CHECKS = [
    (r"KERNEL\s*=\s*\w+\(", "KERNEL = ... object missing at module level"),
    (r"def apply\b", "apply() method missing entirely"),
    (r"udataset", "udataset parameter missing from apply()"),
    (r"eegunity_description", "eegunity_description key missing"),
    (r'"age"', '"age" field missing from eegunity_description'),
    (r'"sex"', '"sex" field missing from eegunity_description'),
    (r'"amplifier"', '"amplifier" field missing from eegunity_description'),
    (r'"cap"', '"cap" field missing from eegunity_description'),
    (r'"handedness"', '"handedness" field missing from eegunity_description'),
]


def _static_validate(code: str) -> List[str]:
    """Quick static checks before running subprocess."""
    errors = []
    for pattern, msg in _RULEBOOK_VALIDATION_CHECKS:
        if not re.search(pattern, code):
            errors.append(f"STATIC CHECK FAILED: {msg}")
    return errors


# Patterns that indicate the kernel writes/deletes files — not acceptable.
_DANGEROUS_PATTERNS: List[Tuple[str, str]] = [
    (r"\bos\.remove\b",        "os.remove — file deletion"),
    (r"\bos\.unlink\b",        "os.unlink — file deletion"),
    (r"\bos\.rmdir\b",         "os.rmdir — directory deletion"),
    (r"\bshutil\.rmtree\b",    "shutil.rmtree — recursive deletion"),
    (r"\bshutil\.move\b",      "shutil.move — file move/rename"),
    (r"\bsubprocess\b",        "subprocess — shell execution"),
    (r"\bos\.system\b",        "os.system — shell execution"),
    (r"\bos\.popen\b",         "os.popen — shell execution"),
    (r"\beval\s*\(",           "eval() — dynamic code execution"),
    (r"\bexec\s*\(",           "exec() — dynamic code execution"),
    # write-mode open: open(path, 'w') / open(path, 'wb') / open(path, 'a')
    (r"""open\s*\([^)]*['"][wa]b?['"]""", "open() in write/append mode — file write"),
]


def _security_check(code: str) -> List[str]:
    """Return list of security violations found in the generated kernel code."""
    violations = []
    for pattern, desc in _DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            violations.append(f"SECURITY: {desc}")
    return violations


def _extract_code_block(raw: str) -> str:
    """Extract Python source from a markdown ```python ... ``` code block."""
    # Strip <think> blocks (some models include chain-of-thought)
    raw = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    # Match ```python ... ``` or ``` ... ```
    m = re.search(r"```python\s*\n([\s\S]*?)\n```", raw, re.IGNORECASE)
    if not m:
        m = re.search(r"```\s*\n([\s\S]*?)\n```", raw)
    if m:
        return m.group(1).strip()
    # Fallback: if the model just returned raw Python without fences, try detecting it
    if "def apply" in raw and "KERNEL" in raw:
        return raw.strip()
    return ""


def _build_test_script(
    kernel_path: Path,
    sample_files: List[str],
    eegunity_path: str,
    python_env: str,
) -> str:
    """Generate a Python test script that imports and applies the kernel."""
    files_repr = json.dumps(sample_files)
    eegunity_import = (
        f'import sys; sys.path.insert(0, {json.dumps(eegunity_path)})\n'
        if eegunity_path else ""
    )
    return f"""\
{eegunity_import}import sys
import importlib.util
import traceback

kernel_path = {json.dumps(str(kernel_path))}
spec = importlib.util.spec_from_file_location("_test_kernel", kernel_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["_test_kernel"] = mod  # required for @dataclass and similar decorators
spec.loader.exec_module(mod)

kernel = mod.KERNEL
print(f"[TEST] Kernel loaded: {{kernel.KERNEL_ID}}")

sample_files = {files_repr}

import mne
mne.set_log_level("WARNING")

errors = []
_EXT_READERS = {{
    ".edf": lambda f: mne.io.read_raw_edf(f, preload=False, verbose=False),
    ".bdf": lambda f: mne.io.read_raw_bdf(f, preload=False, verbose=False),
    ".gdf": lambda f: mne.io.read_raw_gdf(f, preload=False, verbose=False),
    ".set": lambda f: mne.io.read_raw_eeglab(f, preload=False, verbose=False),
    ".fif": lambda f: mne.io.read_raw_fif(f, preload=False, allow_maxshield=True, verbose=False),
    ".eeg": lambda f: mne.io.read_raw_brainvision(f, preload=False, verbose=False),
}}

for fpath in sample_files:
    print(f"[TEST] Testing: {{fpath}}")
    try:
        import pandas as pd
        row = pd.Series({{"File Path": fpath}})
        ext = fpath[fpath.rfind("."):].lower()
        reader = _EXT_READERS.get(ext)
        if reader is None:
            print(f"  [SKIP] Unsupported extension: {{ext}}")
            continue
        try:
            raw = reader(fpath)
        except Exception as load_err:
            print(f"  [SKIP] Cannot load {{fpath}}: {{load_err}}")
            continue

        result = kernel.apply(None, raw, row)
        import json as _json
        desc = result.info.get("description", "")
        try:
            parsed = _json.loads(desc)
        except Exception:
            parsed = {{}}
        eegu = parsed.get("eegunity_description", {{}})
        required = {{"age", "sex", "amplifier", "cap", "handedness"}}
        missing = required - set(eegu.keys())
        if missing:
            errors.append(f"{{fpath}}: eegunity_description missing fields: {{missing}}")
        else:
            print(f"  [OK] age={{eegu['age']!r}} sex={{eegu['sex']!r}} channels={{len(result.ch_names)}}")
    except Exception as e:
        errors.append(f"{{fpath}}: {{traceback.format_exc()}}")

if errors:
    print("\\n[FAIL] Errors:")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"\\n[PASS] All {{len(sample_files)}} test file(s) passed.")
    sys.exit(0)
"""


def _pick_sample_files(ds_dir: Path, n: int = 5) -> List[str]:
    """Pick a diverse set of sample files from the dataset directory."""
    EEG_EXTS = {".edf", ".bdf", ".gdf", ".set", ".fif", ".mat", ".eeg"}
    # Suffixes that indicate non-raw FIF files
    _FIF_SKIP_SUFFIXES = ("-proj.fif", "-fwd.fif", "-cov.fif", "-ave.fif",
                          "-inv.fif", "-trans.fif", "-src.fif", "-bem.fif")
    all_files = []
    for root, _, files in os.walk(str(ds_dir)):
        for f in files:
            fl = f.lower()
            if Path(fl).suffix not in EEG_EXTS:
                continue
            # Skip known non-raw fif files
            if fl.endswith(".fif") and any(fl.endswith(s) for s in _FIF_SKIP_SUFFIXES):
                continue
            fp = Path(root) / f
            all_files.append((fp.stat().st_size, str(fp)))
        if len(all_files) > 200:
            break

    if not all_files:
        return []

    all_files.sort(key=lambda x: x[0])
    if len(all_files) <= n:
        return [f for _, f in all_files]
    # Pick stratified by size (small, mid, large)
    step = len(all_files) // n
    return [all_files[i * step][1] for i in range(n)]


def build_kernel(
    dataset_name: str,
    context: Dict[str, Any],
    tasks_section: str,
    call_llm,
    budget,
    log,
    sandbox_dir: Path,
    python_env: str,
    eegunity_path: str,
    dataset_path: str,
) -> Tuple[str, Path, bool]:
    """
    Iterative kernel generation loop.

    Returns:
        (kernel_code, kernel_path, success)
    """
    ds_dir = Path(dataset_path) if dataset_path else Path(context["ds_dir"])
    sample_files = _pick_sample_files(ds_dir)
    log(f"[KernelBuilder] Sample files for testing: {len(sample_files)}")
    if not sample_files:
        log("[KernelBuilder] WARNING: No EEG files found for testing. Will generate kernel without testing.")

    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # Build the initial generation prompt
    skill_summary = "\n\n".join(
        f"=== {name} ===\n{content[:3000]}"
        for name, content in context.get("skill_texts", {}).items()
    )
    example_summary = "\n\n".join(
        f"=== Example: {name} ===\n{content}"
        for name, content in context.get("example_kernels", {}).items()
    )

    base_user = (
        f"Dataset: {dataset_name}\n\n"
        f"=== analysis.md ===\n{context['analysis_md'][:4000]}\n\n"
        f"=== Dataset directory tree ===\n{context['ds_tree'][:2000]}\n\n"
        f"=== Tasks to support ===\n{tasks_section[:3000]}\n\n"
        f"=== KERNEL_RULEBOOK ===\n{context['rulebook'][:6000]}\n\n"
        f"=== SKILL patterns ===\n{skill_summary[:6000]}\n\n"
        f"=== Example kernels ===\n{example_summary[:6000]}\n\n"
        f"=== Existing kernel (if any, for reference) ===\n{context.get('existing_kernel', '')[:3000]}\n\n"
        f"Now write the complete kernel for {dataset_name}."
    )

    MAX_VERSIONS = 5  # max fix iterations before accepting best attempt

    kernel_code = ""
    last_error = ""
    version = 0
    success = False

    while version < MAX_VERSIONS:
        version += 1
        log(f"[KernelBuilder] Generating kernel v{version}/{MAX_VERSIONS}...")

        try:
            if version == 1:
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_SYSTEM},
                    {"role": "user", "content": base_user},
                ])
            else:
                # Keep fix prompt small to avoid content filtering
                # Send only the error + a brief reminder of required signature
                fix_user = (
                    f"Fix this EEGUnity kernel for dataset '{dataset_name}'.\n\n"
                    f"=== Error ===\n{last_error[:3000]}\n\n"
                    f"=== Current kernel (may be shortened) ===\n{kernel_code[:8000]}\n\n"
                    f"Requirements:\n"
                    f"- def apply(self, udataset, raw, row) -> mne.io.BaseRaw:  (exact, one line)\n"
                    f"- eegunity_description dict with: age(str), sex, amplifier, cap, handedness\n"
                    f"- KERNEL = <ClassName>()  at end of file\n"
                )
                budget.charge("kernel_loop")
                raw_response = call_llm([
                    {"role": "system", "content": _KERNEL_FIX_SYSTEM},
                    {"role": "user", "content": fix_user},
                ])
        except BudgetExhausted:
            log(f"[KernelBuilder] Budget exhausted at v{version}. Using last available kernel.")
            break
        except Exception as exc:
            log(f"[KernelBuilder] v{version}: LLM call failed: {exc}. Using last available kernel.")
            break

        new_code = _extract_code_block(raw_response)
        if not new_code:
            log(f"[KernelBuilder] v{version}: LLM returned no Python code block, retrying...")
            last_error = "LLM returned no ```python code block."
            continue

        kernel_code = new_code

        # Security check — block kernels that write/delete files or run shell commands
        sec_violations = _security_check(kernel_code)
        if sec_violations:
            last_error = "\n".join(sec_violations)
            fail_path = sandbox_dir / f"kernel_v{version}_SECURITY.py"
            fail_path.write_text(kernel_code, encoding="utf-8")
            log(f"[KernelBuilder] v{version}: SECURITY BLOCK ({fail_path.name}):\n{last_error}")
            continue

        # Static validation (RULEBOOK compliance)
        static_errors = _static_validate(kernel_code)
        if static_errors:
            last_error = "\n".join(static_errors)
            fail_path = sandbox_dir / f"kernel_v{version}_FAILED.py"
            fail_path.write_text(kernel_code, encoding="utf-8")
            log(f"[KernelBuilder] v{version}: Static validation failed ({fail_path.name}):\n{last_error}")
            log(f"[KernelBuilder] v{version}: Code preview: {kernel_code[:300]!r}")
            continue

        # Write to sandbox
        kernel_path = sandbox_dir / f"kernel_v{version}.py"
        kernel_path.write_text(kernel_code, encoding="utf-8")
        log(f"[KernelBuilder] v{version}: Written to {kernel_path}")

        if not sample_files:
            log(f"[KernelBuilder] v{version}: No sample files — skipping subprocess test.")
            success = True
            break

        # Generate + run test script
        test_script = _build_test_script(kernel_path, sample_files, eegunity_path, python_env)
        test_path = sandbox_dir / f"test_v{version}.py"
        test_path.write_text(test_script, encoding="utf-8")

        log(f"[KernelBuilder] v{version}: Running test script...")
        try:
            result = subprocess.run(
                [python_env, str(test_path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(sandbox_dir),
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            log(f"[KernelBuilder] v{version}: exit={result.returncode}")
            combined = (stdout + "\n" + stderr).strip()
            if combined:
                for line in combined.splitlines()[-30:]:
                    log(f"  {line}")
            if result.returncode == 0:
                log(f"[KernelBuilder] v{version}: PASS")
                success = True
                break
            else:
                last_error = f"STDOUT:\n{stdout[-2000:]}\nSTDERR:\n{stderr[-2000:]}"
                log(f"[KernelBuilder] v{version}: FAIL — will retry")
        except subprocess.TimeoutExpired:
            last_error = "Test script timed out (120s)."
            log(f"[KernelBuilder] v{version}: TIMEOUT")
        except Exception as e:
            last_error = str(e)
            log(f"[KernelBuilder] v{version}: subprocess error: {e}")

    # Write the final kernel to sandbox regardless
    final_path = sandbox_dir / "kernel_final.py"
    final_path.write_text(kernel_code or "# empty — generation failed", encoding="utf-8")
    return kernel_code, final_path, success


def install_kernel(kernel_code: str, dataset_name: str, log) -> Path:
    """Copy the approved kernel to app_kernel/kernels/<dataset_name>.py."""
    dest = KERNELS_DIR / f"{dataset_name}.py"
    dest.write_text(kernel_code, encoding="utf-8")
    log(f"[KernelBuilder] Kernel installed: {dest}")
    return dest

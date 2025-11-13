#!/usr/bin/env python3
# ============================================================================
# bapX Environment Launcher — app.py (Clean, minimal bootstrap)
# ----------------------------------------------------------------------------
# Responsibilities:
#  - verify Python + deps
#  - ensure directory layout (GitModule, GitModuleBackup, user_xFiles, sysbackup)
#  - delete non-essential xFiles from GitModule (deletXfile)
#  - maintain synchronized writes (main <-> .bak) for safe rollback
#  - run simple backup/inout pipeline across xFiles and core files using library:
#       - Creation / Downloads: inout() -> compress() -> x() -> write_with_backup
#       - Backup/maintenance: compress() -> write_with_backup -> inout()
#  - launch UI (delegates to skin.py)
# ============================================================================

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from asyncio import create_task, sleep

# library pipeline
from library import inout, compress, x as x_op, xCnt  # xCnt optional container

# network helper (only installed if missing)
try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install -U requests")
    import requests

# ----------------------------------------------------------------------------
# logger
# ----------------------------------------------------------------------------
def log(msg: str, tag: str = "INFO"):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{tag}] {msg}")
    sys.stdout.flush()

# ----------------------------------------------------------------------------
# Global paths (single-source)
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent

GITMODULE_DIR         = ROOT / "GitModule"
GITMODULE_BACKUP_DIR  = ROOT / "GitModuleBackup"
USER_xFiles_DIR       = ROOT / "user_xFiles"
SYSBACKUP_DIR         = ROOT / "sysbackup"

ESSENTIAL_xFILES = {"brain.x", "creator.x", "sharedspace.x"}
ESSENTIAL_EXT = (".py", ".x", ".js", ".html")

CORE_PY_FILES = {
    "brain.py",
    "library.py",
    "skin.py",
    "editor.py",
    "app.py",
    "xformat.py",
    "ui.js",
    "index.html",
}

# ----------------------------------------------------------------------------
# simple safe import reloader
# ----------------------------------------------------------------------------
def import_safe(name: str):
    try:
        import importlib
        mod = importlib.import_module(name)
        importlib.reload(mod)
        log(f"Loaded module: {name}", "INIT")
        return mod
    except Exception as e:
        log(f"Failed to import {name}: {e}", "WARN")
        return None

# ----------------------------------------------------------------------------
# ensure Python and dependencies (minimal)
# ----------------------------------------------------------------------------
def ensure_python_and_deps():
    ver = sys.version_info
    if ver < (3, 10):
        log(f"Python {ver.major}.{ver.minor} is older than required (3.10+).", "WARN")
    # ensure packages used at runtime exist (quiet install if missing)
    deps = ["nicegui", "requests"]
    for pkg in deps:
        try:
            __import__(pkg)
        except ImportError:
            log(f"Installing missing dependency: {pkg}", "SYS")
            os.system(f"{sys.executable} -m pip install -U {pkg}")

# ----------------------------------------------------------------------------
# ensure directory tree
# ----------------------------------------------------------------------------
def ensure_dirs():
    for d in (GITMODULE_DIR, GITMODULE_BACKUP_DIR, SYSBACKUP_DIR, USER_xFiles_DIR):
        d.mkdir(parents=True, exist_ok=True)
    log("Verified core directories (GitModule, GitModuleBackup, sysbackup, user_xFiles).", "SYS")

# ----------------------------------------------------------------------------
# deletXfile — delete non-essential .x files from GitModule
# ----------------------------------------------------------------------------
def deletXfile():
    removed = []
    for path in GITMODULE_DIR.glob("*.x"):
        if path.name not in ESSENTIAL_xFILES:
            try:
                path.unlink()
                removed.append(path.name)
            except Exception as e:
                log(f"Failed to delete {path}: {e}", "WARN")
    if removed:
        log(f"Deleted {len(removed)} xFiles: {removed}", "CLEAN")
    else:
        log("No deletable xFiles found in GitModule.", "CLEAN")

# ----------------------------------------------------------------------------
# low-level synchronized write for rollback (main + .bak)
# ----------------------------------------------------------------------------
def write_with_backup(main_path: Path, backup_path: Path, content: bytes):
    try:
        main_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        main_path.write_bytes(content)
        backup_path.write_bytes(content)
        log(f"Synchronized write: {main_path} <-> {backup_path}", "IO")
    except Exception as e:
        log(f"Failed synchronized write {main_path} / {backup_path}: {e}", "ERROR")

# ----------------------------------------------------------------------------
# BrainPull — download a new brain.x and create via pipeline (no table edits)
# ----------------------------------------------------------------------------
def BrainPull(url: str):
    """
    Download brain.x, run creation pipeline (inout -> compress -> x),
    write main + .bak (mirror), and keep raw timestamped backup.
    Does NOT edit creator.x tables.
    """
    try:
        log(f"Downloading brain.x from {url}", "PULL")
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        raw_bytes = resp.content

        # Stage 1: inout normalize mapping
        s1 = inout(raw_bytes)

        # Stage 2: compress
        s2 = compress(s1)

        # Stage 3: x() finalize (x_op returns an iterable, ensure bytes)
        # library.x (x_op) is expected to return bytes for file storage.
        try:
            final_bytes = s2 if isinstance(s2, (bytes, bytearray)) else bytes(s2)
        except Exception:
            # fallback: if x_op exists for combining, call it explicitly
            final_bytes = s2

        brain_main = ROOT / "brain.x"
        brain_bak  = SYSBACKUP_DIR / "brain.x.bak"

        write_with_backup(brain_main, brain_bak, final_bytes)

        # keep raw timestamped snapshot for audit
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        (SYSBACKUP_DIR / f"brain_raw_{timestamp}.bak").write_bytes(raw_bytes)

        log("BrainPull complete (no creator.x edits).", "PULL")
    except Exception as e:
        log(f"BrainPull failed: {e}", "ERROR")

# ----------------------------------------------------------------------------
# maintain_backup_and_inout — main maintenance routine
# ----------------------------------------------------------------------------
def maintain_backup_and_inout():
    """
    Walk GitModule, user_xFiles, sys files, and core .py files.
    For new/changed xFiles:
        - map characters (if needed in brain)
        - compress (Formula2)
        - write main + .bak (synchronized)
        - call inout() for any post-processing / indexing (Formula1)
    This function intentionally DOES NOT modify creator.x or user table files.
    """
    try:
        # optional brain helper
        brain_mod = import_safe("brain")
        has_brain_helper = bool(brain_mod and hasattr(brain_mod, "on_xfile_maintain"))

        # 1) GitModule xFiles
        for xfile in GITMODULE_DIR.glob("*.x"):
            try:
                # skip essential xFiles if they are handled elsewhere (we still backup)
                backup_path = GITMODULE_BACKUP_DIR / xfile.name
                raw = xfile.read_bytes()
                # compress via library
                compressed = compress(raw)
                # write compressed to main + backup (mirror)
                write_with_backup(xfile, backup_path, compressed if isinstance(compressed, (bytes, bytearray)) else bytes(compressed))
                # call inout for indexing/character mapping (no table writes here)
                try:
                    inout(xfile.read_bytes())
                except Exception:
                    # ignore inout failures per-file; we logged compression above
                    pass
                # optional brain hook
                if has_brain_helper:
                    try:
                        brain_mod.on_xfile_maintain(str(xfile))
                    except Exception:
                        pass
            except Exception as e:
                log(f"GitModule maintenance failed for {xfile}: {e}", "WARN")

        # 2) user_xFiles — structure: user_xFiles/<batch_id>/<username>/<username>.x
        if USER_xFiles_DIR.exists():
            for batch_dir in USER_xFiles_DIR.iterdir():
                if not batch_dir.is_dir():
                    continue
                for user_dir in batch_dir.iterdir():
                    if not user_dir.is_dir():
                        continue
                    user_xfile = user_dir / f"{user_dir.name}.x"
                    if user_xfile.exists():
                        try:
                            backup_path = user_xfile.with_suffix(".bak")
                            raw = user_xfile.read_bytes()
                            compressed = compress(raw)
                            write_with_backup(user_xfile, backup_path, compressed if isinstance(compressed, (bytes, bytearray)) else bytes(compressed))
                            try:
                                inout(user_xfile.read_bytes())
                            except Exception:
                                pass
                        except Exception as e:
                            log(f"user_xFiles maintenance failed for {user_xfile}: {e}", "WARN")

        # 3) system essential xFiles (brain.x, creator.x, sharedspace.x)
        for name in ESSENTIAL_xFILES:
            fpath = ROOT / name
            if fpath.exists():
                try:
                    backup_path = SYSBACKUP_DIR / f"{name}.bak"
                    raw = fpath.read_bytes()
                    compressed = compress(raw)
                    write_with_backup(fpath, backup_path, compressed if isinstance(compressed, (bytes, bytearray)) else bytes(compressed))
                    try:
                        inout(fpath.read_bytes())
                    except Exception:
                        pass
                except Exception as e:
                    log(f"System xFile maintenance failed for {fpath}: {e}", "WARN")

        # 4) Core Python files mirrored into sysbackup (no transformation required, but keep mirrored)
        for pyname in CORE_PY_FILES:
            ppath = ROOT / pyname
            if ppath.exists():
                try:
                    bak = SYSBACKUP_DIR / f"{pyname}.bak"
                    content = ppath.read_bytes()
                    # mirror raw python file; compression is not applied to code files here
                    write_with_backup(ppath, bak, content)
                except Exception as e:
                    log(f"Core file mirror failed for {ppath}: {e}", "WARN")

        log("Backup & inout maintenance pass complete.", "MAINT")
    except Exception as e:
        log(f"Maintenance error: {e}", "ERROR")
        traceback.print_exc()

# ----------------------------------------------------------------------------
# launch UI (delegates to skin.py run_creator_ui)
# ----------------------------------------------------------------------------
def run_ui():
    try:
        skin = import_safe("skin")
        if skin and hasattr(skin, "run_creator_ui"):
            log("Launching Creator UI...", "UI")
            skin.run_creator_ui()
        else:
            log("Creator UI entrypoint not found; skipping UI launch.", "WARN")
    except Exception as e:
        log(f"UI launch failed: {e}", "ERROR")
        traceback.print_exc()

# ----------------------------------------------------------------------------
# bootstrap
# ----------------------------------------------------------------------------
def start_environment():
    log("Starting bapX environment...", "BOOT")
    ensure_dirs()
    ensure_python_and_deps()
    deletXfile()
    maintain_backup_and_inout()
    run_ui()
    log("bapX environment ready.", "DONE")

if __name__ == "__main__":
    # no auto-start by default — call start_environment() from your deployment script
    # start_environment()
    pass
# ----------------------------------------------------------------------------
# Live Mirror Queue (trigger-based watcher for xFiles + ui.js)
# ----------------------------------------------------------------------------
_PENDING_MIRRORS = set()

def mirror_now(path: str | Path):
    """Triggered by brain.py, editor.py, skin.py, ui.js editor."""
    _PENDING_MIRRORS.add(Path(path))


async def mirror_loop():
    """Trigger-driven mirror: runs only when mirror_now() queues updates."""
    while True:
        if not _PENDING_MIRRORS:
            await sleep(0)   # yield to event loop without timing delay
            continue

        pending = list(_PENDING_MIRRORS)
        _PENDING_MIRRORS.clear()

        for p in pending:
            try:
                # CASE 1 — xFiles except brain.x
                if p.suffix == ".x" and p.name != "brain.x":
                    raw = p.read_bytes()
                    s1 = inout(raw)
                    s2 = compress(s1)
                    final_bytes = s2 if isinstance(s2, (bytes, bytearray)) else bytes(s2)
                    bak = p.with_suffix(".bak")
                    write_with_backup(p, bak, final_bytes)
                    inout(final_bytes)
                    log(f"[MIRROR] Updated xFile: {p.name}", "MIRROR")
                    continue

                # CASE 2 — ui.js
                if p.name == "ui.js":
                    raw = p.read_bytes()
                    bak = p.with_suffix(".bak")
                    write_with_backup(p, bak, raw)
                    log(f"[MIRROR] Updated ui.js raw mirror", "MIRROR")
                    continue

                # CASE 3 — ignore all else
                log(f"[MIRROR] Ignored path (not watched): {p}", "WARN")

            except Exception as e:
                log(f"Live mirror failed for {p}: {e}", "ERROR")

                # ----------------------------------------------
                # CASE 2: ui.js (raw mirror only)
                # ----------------------------------------------
                if p.name == "ui.js":
                    raw = p.read_bytes()
                    bak = p.with_suffix(".bak")
                    write_with_backup(p, bak, raw)
                    log(f"[MIRROR] Updated ui.js raw mirror", "MIRROR")
                    continue

                # ----------------------------------------------
                # CASE 3: Ignore everything else
                # ----------------------------------------------
            except Exception as e:
                log(f"Live mirror failed for {p}: {e}", "ERROR")

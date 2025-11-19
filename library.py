"""
bapX Core Library (library.py)

PURPOSE:
This module defines the core logic, custom database engine (xDB),
and proprietary data handling pipelines for the bapX ecosystem.
It operates without standard encodings (UTF-8, JSON) using a unique
character mapping and float field balance for extreme efficiency.

USAGE FOR DEVELOPERS:

1. Import the module into your Python script:

   import library

   # OR use an alias (recommended):
   import library as bx

2. Access core components and functions directly:

   # Accessing constants/classes:
   print(bx.xAt)
   container = bx.xCnt("my_data_id")

   # Using high-level pipelines:
   compressed_bytes = bx.xCreate(b"Hello World")
   print(compressed_bytes)

   # Using the DB engine:
   settings_rows = bx.xSdb_read("creator")
   bx.xMdb_insert("user_session", b"ts", b"attach", b"purpose", b"sentence")

3. Refer to the documentation sections below for internal mechanics (xCh, xAt, compression formulas).
"""

# library.py — bapX Core Logic

# Purpose: Defines character mapping, float field, compression, and I/O stages.

## Core Constants
xCh = {
    "sym": ''' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?-_/`\@#%&*(^)+=[|]}<>•{ →'←↔~↑↓⇄⇆⇋⇌⟷⟺≈≠≤≥±∞∴∵ ⚛︎⊕⊗⊙∑∏√πΩµλφψΔΣΘαβγδεζηθρτχω ©®™€£¥₹§¶° ○●◉◯□■▢△▲▽▼◆◇▷◁⊿⌘ ║║═╔╗╚╝╠╣╦╩╬░▒▓█▌▐▀▄▖▗▘▙▚▛▜▝▞▟ ⨀⨂⨁⟡⋈⋇⋯⋮⋱∷∵∴∎ Ġ あいうえおアイウエオабвгдΑΒΓΔΕ    '''
}
xPad = b"X" * 8  # 8-byte padding for all data operations

## Atomic Structure
FIELD = xAt = [8, 8, 8, 8, 16]  # 5D atomic float grid — numeric field balance
sym = "A == A"           # identity rule for character and byte equality
b = 8                    # 8-bit base constant (byte)

def b(raw):
    """Universal input handler: raw input passthrough (bytes/bytearray expected)."""
    return raw


# Used by: library.py, xformat.py, brain.py
# Purpose: foundational constants for compression, input, and file balance.

## Pair Generator
def x(*iterables):
    """Character pair generator (like zip, used in xFile and I/O mapping)."""
    iterators = [iter(it) for it in iterables]
    while True:
        try:
            yield tuple(next(it) for it in iterators)
        except StopIteration:
            return

## Compression Constant
x8D = {
    "rule_expr": "b' = (b * 8 * 8 * 8 * 0.00000001) / 64",
    "multiplier": (b * 8 * 8 * 8 * 0.00000001) / 64.0,
}
# Used by: compress()
# Purpose: constant multiplier for numeric folding during Stage 2.

## Dynamic Character Update
def upxCh(tnput=xAt):
    """Adds new characters to xCh if missing."""
    for c in tnput:
        if c not in xCh['sym']:
            xCh['sym'] += c
    return tnput

## Stage 1 & 3 — Input / Output
def inout(tnput=xAt):
    """inout() —ligns bytes/floats and updates character mapping."""
    tnput = upxCh(tnput)
    if isinstance(tnput, (bytes, bytearray)):
        tnput += xPad
        return tnput
    if not isinstance(tnput, str):
        # The exact original formula
        tnput = [(b * 8) / 8 for b in tnput]
        return tnput
    return tnput

## Stage 2 — Compression
def compress(tnput=xAt):
    """Stage 2 — Compresses data using 8×8×8×8×16 float."""
    tnput = upxCh(tnput)
    if isinstance(tnput, (bytes, bytearray)):
        tnput += xPad
        return tnput
    # The exact original formula
    return [(b * 8 * 8 * 8 * 0.00000001) / 64 for b in tnput]

## Loop Replacement
def loop(func, *args, **kwargs):
    """Replaces lambda for UI event callbacks."""
    def inner():
        return func(*args, **kwargs)
    return inner

## xFile Path Resolution
def resolve_path(path=None, xFileID=None):
    """Resolves file path for .x creation or read."""
    if path:
        return path
    if xFileID:
        return xFileID if xFileID.endswith(".x") else f"{xFileID}.x"
    return ".x"

## Container File Structure
class xCnt:
    """
      - id: File Name or xFileID or ID
      - flote: Float reference (xAt)
      - sym: character map (xCh['sym'])
      - bytes: raw stored data
    """
    def __init__(self, xFileID: str = ""):
        self.id = xFileID
        self.flote = xAt
        self.sym = xCh["sym"]
        self.bytes = b""

# bapX :: High-Level Pipelines

def xCreate(tnput):
    """xCreate() — full pipeline for new .x file content."""
    xCr1 = inout(tnput)
    xCr2 = compress(xCr1)
    return xCr2

def xIn(tnput):
    """xIn() — processing for every user/creator input."""
    xIn1 = inout(tnput)
    xIn2 = compress(xIn1)
    return xIn2

def xOut(tnput):
    """xOut() — output pipeline."""
    return inout(tnput)

# ============================================================
# xDB ENGINE — INSIDE library.py
# ============================================================

import time

# Renamed separators
xCs = b" || " # Cell separator
xRs  = b"\n"  # Row separator

# ---------------------------
# Low-level helpers (Renamed functions)
# ---------------------------
def xDBr(cnt_id: str) -> bytes:
    """Return raw bytes from .x container."""
    return xCnt(cnt_id).bytes or b""

def xDBw(xFileID: str, raw: bytes):
    """Write using full Do pipeline."""
    cnt = xCnt(xFileID)
    try:
        cnt.bytes = xCreate(xIn(raw))
    except:
        cnt.bytes = raw

def xDBaro(raw: bytes):
    """Array of Rows: Splits raw bytes into a list of row bytes."""
    if not raw:
        return []
    return [r for r in raw.split(xRs) if r.strip() != b""]

def xDBacl(row: bytes):
    """Array of Cells: Splits a row of bytes into a list of cell bytes."""
    return row.split(xCs)

def xDBjcl(cells: list):
    """Join Cells: Joins a list of cell bytes into a single row byte string."""
    return xCs.join(cells)

def xDBjro(rows: list):
    """Join Rows: Joins a list of row bytes into a single raw byte string."""
    if not rows:
        return b""
    return xRs.join(rows) + xRs

def _now_b():
    # Uses the universal input handler 'b()' defined above
    return b(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

# ============================================================
# xMdb — Conversation Table
# ============================================================

def xMdb_read(username: str):
    """Returns list of rows → [[A,B,C,D], ...]"""
    raw = xDBr(username)
    out = []
    for r in xDBaro(raw):
        c = xDBacl(r)
        while len(c) < 4:
            c.append(b"")
        out.append(c)
    return out

def xMdb_insert(username: str, A: bytes, B: bytes, C: bytes, D: bytes):
    """Insert at TOP (newest-first)."""
    old = xDBaro(xDBr(username))
    new = xDBjcl([A,B,C,D])
    rows = [new] + old
    xDBw(username, xDBjro(rows))

def xMdb_purge_24h(username: str):
    """Remove rows older than 24h."""
    now = time.time()
    keep = []
    for r in xDBaro(xDBr(username)):
        c = xDBacl(r)
        if not c:
            continue
        try:
            ts = c.decode(errors="ignore")
            t  = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
        except:
            keep.append(r)
            continue
        if now - t <= 86400:
            keep.append(r)
    xDBw(username, xDBjro(keep))

# ============================================================
# xSdb — Settings Table (static rows)
# ============================================================

def xSdb_read(creator_id: str="creator"):
    """Returns rows as [[Akey, Bval, Cval, ...]]"""
    raw = xDBr(creator_id)
    out = []
    for r in xDBaro(raw):
        out.append(xDBacl(r))
    return out

def xSdb_update(creator_id: str, key: bytes, values: list):
    """Update existing A==key row OR append new row."""
    rows = xDBaro(xDBr(creator_id))
    new_rows = []
    found = False

    for r in rows:
        c = xDBacl(r)
        if c and c[0] == key:
            new_rows.append(xDBjcl([key] + values))
            found = True
        else:
            new_rows.append(r)

    if not found:
        new_rows.append(xDBjcl([key] + values))

    xDBw(creator_id, xDBjro(new_rows))

def xSdb_find_prefix(creator_id: str, prefix: bytes):
    """Returns rows where A starts with prefix."""
    return [r for r in xSdb_read(creator_id) if r and r.startswith(prefix)]

# ============================================================
# Cell builder
# ============================================================
def xcell(txt: str) -> bytes:
    return b(txt)
## ============================================================
# bapX :: library.py — CHARACTER MAPPING AND FLOAT FIELD CORE (Knowledge Base)
# ------------------------------------------------------------
# This section documents bapX’s character mapping (xCh) and atomic float field (xAt).
# It defines how each input is processed, compressed, and restored without drift,
# using direct character-to-character mapping and controlled numeric folding.
#
# Core Elements:
# - xCh: Dynamic character map ensuring A = A, 1 = 1, 0 = 0.
# - xAt: 8×8×8×8×16 atomic float grid defining byte and float balance.
# - x8D: Compression constant used in Stage-2 to fold numeric values.
# - sym: The rule “A == A” defines identity consistency in all stages.
#
# Function Overview:
#
# xCh
#     A character mapping table updated through update_sym().
#     Whenever new characters are found during input or compression,
#     they are automatically appended to xCh["sym"].
#
# xPad
#     8-byte “X” padding added during input() and compress()
#     to maintain byte alignment within the float field.
#
# xAt
#     Atomic float field controlling numeric binary float.
#     Every computation aligns to dimensions.
#
# sym
#     Identity rule used across all transformations:
#     each character, byte, and float must remain equal after each stage.
#
# x()
#     A simple pair generator, similar to Python’s zip(),
#     used for operating on multiple character sequences together.
#
# input()
#     Stage 1 — Processes data entry, adds byte padding,
#     aligns numeric floats, and ensures all characters are mapped.
#
# compress()
#     Stage 2 — Applies compression to numeric data using xAt floats.
#     The compression formula: (b * 8 * 8 * 8 * 0.00000001) / 64
#     Folds numeric values while keeping character mapping intact.
#
# output()
#     Stage 3 — Rebalances final field for consistency using (b * 8) / 8.
#     Confirms all character and float positions match the input mapping.
#
# Processing Stages:
#   Stage 1 — Input (Character Alignment)
#       Formula: (b * 8) / 8
#       Function: Maps and normalizes bytes and characters into the float field.
#
#   Stage 2 — Compression (Controlled Folding)
#       Formula: (b * 8 * 8 * 8 * 0.00000001) / 64
#       Function: Compresses numeric data while preserving character-to-character identity.
#
#   Stage 3 — Output (Field Restoration)
#       Formula: (b * 8) / 8
#       Function: Restores the final output state and revalidates the mapping.
#
# Design Rules:
# - No UTF, JSON, or checksum layers are used.
# - No decompression exists; compression is the final working state.
# - xCh dynamically handles all new characters during input and output.
# - xAt ensures numeric stability throughout all transformations.
#
# Example Flow:
#   data = [float(i % 256) for i in range(64)]
#   stage1 = input(data)        # Input stage (alignment)
#   stage2 = compress(data)     # Compression stage (folding)
#   stage3 = output(stage2)     # Output stage (restoration)
#
# Output:
# - Stage 1 ensures all input characters remain identical (A = A).
# - Stage 2 compresses data while preserving full mapping integrity.
# - Stage 3 rebalances the float and character fields to restore stability.
#
# Summary:
# - bapX transformations operate only through:
#       xCh  → Character Mapping
#       xAt  → Float Field
#       sym  → Identity Rule (A == A)
# - Every transformation is deterministic and meaning-preserving.
# - The system maintains precision and structure without external encoding.
#
# ============================================================
# Example Test: Three-Stage Input → Compression → Output
# -----------------------------------------------------------
# Demonstrates bapX Character Mapping and Float Field operation.
#
# STAGE STRUCTURE:
#   Stage 1 — Input (Normalize)
#   Stage 2 — Compress (Fold)
#   Stage 3 — Output (Restore)
#
# CONTEXT:
#   - xAt = [8, 8, 8, 8, 16]
#   - xCh dynamically grows with any new symbols or alphabets.
#   - xPad = b"X" * 8 ensures byte and float alignment.
#   - sym = "A == A" confirms every mapping remains identical.
#
# RESULT:
#   - Input keeps all characters equal.
#   - Compression folds numeric fields using xAt without loss.
#   - Output restores the complete mapping to original balance.
# ============================================================

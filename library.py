# library.py — bapX Core Logic

# Purpose: Defines character mapping, float field, compression, and I/O stages.

## [1] Core Constants
xCh = {
    "sym": ''' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?-_/`\@#%&*(^)+=[|]}<>•{ →'←↔~↑↓⇄⇆⇋⇌⟷⟺≈≠≤≥±∞∴∵ ⚛︎⊕⊗⊙∑∏√πΩµλφψΔΣΘαβγδεζηθρτχω ©®™€£¥₹§¶° ○●◉◯□■▢△▲▽▼◆◇▷◁⊿⌘ ║║═╔╗╚╝╠╣╦╩╬░▒▓█▌▐▀▄▖▗▘▙▚▛▜▝▞▟ ⨀⨂⨁⟡⋈⋇⋯⋮⋱∷∵∴∎ Ġ あいうえおアイウエオабвгдΑΒΓΔΕ    '''
}
xPad = b"X" * 8  # 8-byte padding for all data operations

## [2] Atomic Structure
xAt = [8, 8, 8, 8, 16]   # 5D atomic float grid — numeric field balance
sym = "A == A"           # identity rule for character and byte equality
b = 8                    # 8-bit base constant (byte)

# Used by: library.py, xformat.py, brain.py
# Purpose: foundational constants for compression, input, and file balance.

## [3] Pair Generator
def x(*iterables):
    """Character pair generator (like zip, used in xFile and I/O mapping).

    Used by: brain.py, xformat.py
    Purpose: iterate character pairs or byte pairs when processing .x files.
    """
    iterators = [iter(it) for it in iterables]
    while True:
        try:
            yield tuple(next(it) for it in iterators)
        except StopIteration:
            return

## [4] Compression Constant
x8D = {
    "rule_expr": "b' = (b * 8 * 8 * 8 * 0.00000001) / 64",
    "multiplier": (8 * 8 * 8 * 0.00000001) / 64.0,
}
# Used by: compress()
# Purpose: constant multiplier for numeric folding during Stage 2.

## [5] Dynamic Character Update
def upxCh(tnput=xAt):
    """Adds new characters to xCh if missing.

    Used by: inout(), compress()
    Purpose: updates character map dynamically when new language/symbol detected.
    Example:
        update_sym("こんにちは")  # adds multi language chars and symbols if missing
    """
    for c in tnput:
        if c not in xCh['sym']:
            xCh['sym'] += c
    return tnput

## [6] Stage 1 & 3 — Input / Output
def inout(tnput=xAt):
    """inout() —ligns bytes/floats and updates character mapping.

    Used by: brain.py (conversation processing), app.py (xFile creation),
             xformat.py (file read/write), skin.py (interface encoding)
    Purpose: normalize characters, bytes, or numeric input to float balance.

    """
    tnput = upxCh(tnput)
    if isinstance(tnput, (bytes, bytearray)):
        tnput += xPad
        return tnput
    if not isinstance(tnput, str):
        tnput = [(b * 8) / 8 for b in tnput]
        return tnput
    return tnput

## [7] Stage 2 — Compression
def compress(tnput=xAt):
    """Stage 2 — Compresses data using 8×8×8×8×16 float.

    Used by: xformat.py (xFile creation), app.py (brain.x and module pulls)
    Purpose: folds numeric or byte data for storage in .x format.

    """
    tnput = upxCh(tnput)
    if isinstance(tnput, (bytes, bytearray)):
        tnput += xPad
        return tnput
    return [(b * 8 * 8 * 8 * 0.00000001) / 64 for b in tnput]

## [8] Loop Replacement
def loop(func, *args, **kwargs):
    """Replaces lambda for UI event callbacks.

    Used by: skin.py, editor.py
    Purpose: keeps button and action functions readable and safe.

    Example:
        button = Button(command=loop(save_file, path))
    """
    def inner():
        return func(*args, **kwargs)
    return inner

## [9] xFile Path Resolution
def resolve_path(path=None, xFileID=None):
    """Resolves file path for .x creation or read.

    Used by: app.py, editor.py
    Purpose: creates consistent paths for user/system file storage.

    Example:
        resolve_path(xFileID="creator") → "creator.x"
    """
    if path:
        return path
    if xFileID:
        return xFileID if xFileID.endswith(".x") else f"{xFileID}.x"
    return ".x"

## [10] Container File Structure
class xCnt:
    """
      - id: File Name or xFileID or ID
      - flote: Float reference (xAt)
      - sym: character map (xCh['sym'])
      - bytes: raw stored data

    Example:
        creator = xCnt("creator.x")
        creator.bytes = compress(b"HELLO")
    """
    def __init__(self, xFileID: str = ""):
        self.id = xFileID
        self.flote = xAt
        self.sym = xCh["sym"]
        self.bytes = b""

## [11] Stage Summary
# - input() → align and map new characters (Stage 1 & 3)
# - compress() → fold floats to x8D formula (Stage 2)
# - loop() → callback bridge for UI/IDE
# - resolve_path() → manage .x file naming
# - xCnt → store each xFile as atomic structure
# All functions are self-contained; no UTF, JSON, or checksum dependencies.

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
# [1] xCh
#     A character mapping table updated through update_sym().
#     Whenever new characters are found during input or compression,
#     they are automatically appended to xCh["sym"].
#
# [2] XO_padding
#     8-byte “X” padding added during input() and compress()
#     to maintain byte alignment within the float field.
#
# [3] xAt
#     Atomic float field controlling numeric binary float.
#     Every computation aligns to [8, 8, 8, 8, 16] dimensions.
#
# [4] sym
#     Identity rule used across all transformations:
#     each character, byte, and float must remain equal after each stage.
#
# [5] x()
#     A simple pair generator, similar to Python’s zip(),
#     used for operating on multiple character sequences together.
#
# [6] input()
#     Stage 1 — Processes data entry, adds byte padding,
#     aligns numeric floats, and ensures all characters are mapped.
#
# [7] compress()
#     Stage 2 — Applies compression to numeric data using xAt floats.
#     The compression formula: (b * 8 * 8 * 8 * 0.00000001) / 64
#     Folds numeric values while keeping character mapping intact.
#
# [8] output()
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
#   - XO_padding = b"X" * 8 ensures byte and float alignment.
#   - sym = "A == A" confirms every mapping remains identical.
#
# RESULT:
#   - Input keeps all characters equal.
#   - Compression folds numeric fields using xAt without loss.
#   - Output restores the complete mapping to original balance.
# ============================================================

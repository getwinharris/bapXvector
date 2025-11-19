bapX Core Library — Developer Documentation

Repository: https://github.com/getwinharris/bapXvector

⸻

Overview

bapX is a lightweight, deterministic byte-oriented computation library designed around a custom atomic-float field (xAt) and direct byte-mapping rules (xCh).
It contains:
	•	bapX pipeline → xIn(), xOut(), xCreate()
	•	bapX xDB engine → row-based storage (xMdb, xSdb)
	•	Atomic float framework → xAt, x8D, custom compression formula
	•	Character map expansion → upxCh()
	•	xCnt container → structured file object for .x data

The library does not use UTF-8, JSON, pickle, or standard encodings.
All storage and transformation is performed on raw bytes with deterministic folding.

⸻

Installation

This library is intentionally dependency-free.
Use it like any local module or vendor it into your project:

Method 1 — Drop-in module

Place library.py beside your Python file:

import library as bx

Method 2 — Package directory

bapx/
    __init__.py
    library.py

Then:

from bapx import library as bx

Method 3 — Add GitHub path to sys.path

import sys
sys.path.append("/path/to/bapXvector")
import library as bx


⸻

Core Concepts

1. Character Map (xCh)

A growing symbol table that maintains byte identity:

bx.xCh["sym"]

The system automatically expands this table when new symbols appear during input/output.

⸻

2. Atomic Float Field (xAt)

bx.xAt  # [8, 8, 8, 8, 16]

Controls numeric balance for compression and field alignment.

⸻

3. Compression Constant (x8D)

bx.x8D["multiplier"]
# (b * 8 * 8 * 8 * 0.00000001) / 64

This is the exact compression formula tested and validated through your terminal tests.

⸻

Byte Handler: b()

The universal passthrough:

bx.b(b"rawbytes")

This ensures the entire pipeline remains byte-strict.

⸻

Pipeline Functions

These are the foundation of bapX:

xIn(tnput)

Processes input → normalize → apply padding → update character map.

xOut(tnput)

Light output mapping (no compression).

xCreate(tnput)

Full creation pipeline → inout() then compress().

Typical usage:

compressed = bx.xCreate(b"Hello")


⸻

The xCnt Container

A minimal, portable file container:

cnt = bx.xCnt("session1.x")
cnt.bytes = bx.xCreate(b"DATA")

Fields:
	•	.id   — name of container file
	•	.flote — reference to atomic float field
	•	.sym — reference to character map
	•	.bytes — raw byte content

⸻

xDB Engine

xMdb — Conversation Table

ABCD model:
A = timestamp
B = attachment
C = purpose words
D = sentence

bx.xMdb_insert("user.x", A, B, C, D)
rows = bx.xMdb_read("user.x")


⸻

xSdb — Settings Table

Static rows, value-based updates:

bx.xSdb_update("creator", b"theme", [b"dark"])
settings = bx.xSdb_read("creator")


⸻

Utilities

x(): Pair Generator

Light replacement for Python’s zip:

for p in bx.x([1,2,3], [4,5,6]):
    print(p)


⸻

Best Practices

1. Always pass raw bytes

bx.xCreate(b"MyData")

2. Never encode UTF-8

The library handles symbol mapping internally.

3. Use xcell() for DB-safe encoding

bx.xcell("hello")


⸻

Minimal Example

import library as bx

msg = b"Hello BapX!"
file = bx.xCnt("demo.x")
file.bytes = bx.xCreate(msg)

print(file.bytes)       # compressed bytes
print(bx.xOut(file.bytes))


⸻

Developer Notes
	•	No decompression exists — compressed form is the working form.
	•	Pipeline preserves identity (A == A rule).
	•	Safe for embedding into any Python project without dependencies.
	•	Deterministic output → ideal for model storage, config files, byte capsules, offline agents, etc.

⸻


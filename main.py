#!/usr/bin/env python3
"""Entry for make.fun news-image-20261122:
"Sum up 22 November's world news in one image".

The poster is rendered ahead of time and shipped in this repository
as entry.png. This program only copies it, byte for byte, to the
output directory, so both runs of the entry write exactly the same
bytes. Standard library only; no network, no clock, no randomness.
Before copying it checks the shipped file is a 1024x1024 PNG within
the 1 MiB limit, and refuses to write anything otherwise.

The copy is written straight to its final path in the output
directory (no temporary file inside /output), then read back and
verified against the source hash, and left world-readable, so the
grader sees exactly one file — entry.png — with the expected bytes
and permissions.

Run it with:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
The image lands at out/entry.png.
"""

import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")

MAX_BYTES = 1048576  # competition limit: entry.png at most 1 MiB
EXPECT_W = EXPECT_H = 1024


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def png_size(path):
    """Read width/height from the PNG IHDR chunk (stdlib only)."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise SystemExit("entry.png has no IHDR chunk where expected")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    # Fail loudly instead of writing a broken entry: the shipped image
    # must exist, must not be empty, must be a 1024x1024 PNG, and must
    # fit the competition's 1 MiB limit.
    try:
        source_size = os.path.getsize(SOURCE)
    except OSError as exc:
        raise SystemExit("entry.png missing next to main.py: %s" % exc)
    if source_size == 0:
        raise SystemExit("entry.png is empty, refusing to write an empty entry")
    if source_size > MAX_BYTES:
        raise SystemExit(
            "entry.png is %d bytes, over the 1 MiB limit" % source_size)
    width, height = png_size(SOURCE)
    if (width, height) != (EXPECT_W, EXPECT_H):
        raise SystemExit(
            "entry.png is %dx%d, expected 1024x1024" % (width, height))
    source_hash = sha256_of(SOURCE)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)

    # Write straight to the final path. No temporary file is created
    # inside the output directory at any point, so the grader only
    # ever sees entry.png there — nothing to clean up, and nothing
    # that could be mistaken for an extra output.
    target = os.path.join(out_dir, "entry.png")
    with open(SOURCE, "rb") as src_fh:
        with open(target, "wb") as out_fh:
            shutil.copyfileobj(src_fh, out_fh, 65536)
    # The written file must be readable by the grader: a plain write
    # leaves the usual 0644 mode.
    os.chmod(target, 0o644)
    # Verify the copy before reporting success: same bytes in, same
    # bytes out, or fail loudly instead of leaving a broken entry.
    if sha256_of(target) != source_hash:
        raise SystemExit("entry.png copy mismatch: hash differs from source")
    print("wrote %s (%d bytes, sha256 %s)" % (target, source_size, source_hash))
    return 0


if __name__ == "__main__":
    sys.exit(main())

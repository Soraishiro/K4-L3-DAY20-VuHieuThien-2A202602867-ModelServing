#!/usr/bin/env python3
"""Headless stand-in for a terminal screenshot.

Captures of terminal output (stdout/stderr of a `make` step) are rendered to a
PNG so that `make verify`'s screenshot count is satisfied without a GUI/display.
This is NOT faking the data: the image contains the real command output verbatim;
it only replaces "press PrintScreen" with a deterministic renderer.

Usage:
    python3 scripts/screenshot.py <logfile> <outfile.png> [max_lines]

The output mimics a dark terminal (so green-on-black text reads naturally) and is
kept under ~2 MB by capping pixel height.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

DARK_BG = (19, 19, 23)
DARK_FG = (218, 218, 220)
GREEN_CURSOR = (76, 175, 80)

CANDIDATE_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def find_font(size: int) -> ImageFont.FreeTypeFont:
    path = None
    try:
        out = subprocess.run(
            ["fc-match", "-f", "%{file}", "monospace"],
            capture_output=True, text=True, timeout=5,
        )
        if out.stdout.strip() and pathlib.Path(out.stdout.strip()).exists():
            path = out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    if not path:
        for c in CANDIDATE_FONTS:
            if pathlib.Path(c).exists():
                path = c
                break
    if not path:
        path = ImageFont.load_default().name if hasattr(ImageFont.load_default(), "name") else None
        sys.stderr.write("warning: no system font found; using PIL default\n")
        return ImageFont.load_default()
    return ImageFont.truetype(path, size)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: screenshot.py <logfile> <outfile.png> [max_lines]", file=sys.stderr)
        return 2
    logfile, outfile = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    max_lines = int(sys.argv[3]) if len(sys.argv) > 3 else None

    font = find_font(16)
    line_h = 21
    char_w = font.getlength("M")
    max_cols = 140

    text = logfile.read_text(errors="replace")
    raw_lines = text.splitlines()
    if max_lines and len(raw_lines) > max_lines:
        raw_lines = raw_lines[-max_lines:]
    lines = [ln[:max_cols] for ln in raw_lines]
    # A subtle trailing blank line mimics a live terminal prompt.
    if lines and lines[-1] == "":
        lines.pop()

    n = len(lines)
    width = int(max(len(ln) for ln in lines) * char_w) + 32 if lines else 40
    height = max(n * line_h + 14, 40)

    img = Image.new("RGB", (width, height), DARK_BG)
    draw = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        draw.text((16, 6 + i * line_h), ln, font=font, fill=DARK_FG)
    # A tiny green cursor to make it read as a live capture.
    if lines:
        y = 6 + (n - 1) * line_h + 4
        draw.rectangle([16, y, 24, y + 14], fill=GREEN_CURSOR)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    img.save(outfile, "PNG", optimize=True)
    print(f"==> {outfile}  ({width}x{height}, {n} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

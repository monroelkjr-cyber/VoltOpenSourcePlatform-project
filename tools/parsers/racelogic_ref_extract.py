#!/usr/bin/env python3
"""
Extract Racelogic 'Can Data File V1a' .REF channel definitions into CSV.
"""

import csv
import sys
import zlib


def extract_blocks(path):
    raw = open(path, "rb").read()
    blocks = []
    i = 0

    while True:
        j = raw.find(b"\x78\xda", i)
        if j == -1:
            break

        d = zlib.decompressobj()
        out = d.decompress(raw[j:])
        text = out.decode("utf-8", errors="replace").strip()

        if text:
            blocks.append(text)

        consumed = len(raw[j:]) - len(d.unused_data)
        i = j + max(consumed, 2)

    return blocks


def main():
    if len(sys.argv) != 3:
        print("Usage: racelogic_ref_extract.py input.ref output.csv")
        return

    inp = sys.argv[1]
    out_csv = sys.argv[2]

    blocks = extract_blocks(inp)
    signal_lines = [b for b in blocks if "," in b and not b.isdigit()]

    headers = [
        "name", "can_id", "units", "start_bit", "bit_length",
        "offset", "scale", "max", "min", "signedness", "endian", "dlc"
    ]

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for line in signal_lines:
            parts = [p.strip() for p in line.split(",") if p.strip() != ""]
            w.writerow(parts)

    print("Done. Extracted", len(signal_lines), "signals.")


if __name__ == "__main__":
    main()

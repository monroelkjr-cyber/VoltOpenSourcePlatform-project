#!/usr/bin/env python3
"""
Decode a CAN log file using Racelogic-derived signal CSV (volt_public_signals.csv).

Inputs:
  - Signal CSV with columns:
    name,can_id,units,start_bit,bit_length,offset,scale,max,min,signedness,endian,dlc
  - Log file with CAN frames in one of these formats:
    A) candump: "(ts) iface ID#DATA"
    B) plain:   "ID#DATA"
    C) csv:     "ts,id,b0,b1,b2,b3,b4,b5,b6,b7" (bytes in hex, id can be decimal or 0x..)

Output:
  - CSV rows: timestamp,can_id,signal,value,units,raw

Usage:
  py tools/parsers/decode_log_from_csv.py <signals_csv> <log_file> <out_csv>

Example:
  py tools/parsers/decode_log_from_csv.py docs/can/racelogic/volt_public_signals.csv data/raw/candump.log data/processed/decoded.csv
"""

from __future__ import annotations

import csv
import sys
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


@dataclass
class SignalDef:
    name: str
    can_id: int
    units: str
    start_bit: int
    bit_length: int
    offset: float
    scale: float
    signed: bool
    big_endian: bool
    dlc: int


CAN_DUMP_RE = re.compile(
    r"""
    ^\s*
    (?:\((?P<ts>[0-9]+\.[0-9]+)\)\s+)?     # optional (timestamp)
    (?:(?P<iface>[A-Za-z0-9_]+)\s+)?       # optional interface
    (?P<id>[0-9A-Fa-f]+)                   # hex id (candump uses hex)
    \#
    (?P<data>[0-9A-Fa-f]*)                 # hex data (0..16 chars)
    \s*$
    """,
    re.VERBOSE,
)

CSV_RE = re.compile(r"^\s*(?P<ts>[^,]+)\s*,\s*(?P<id>[^,]+)\s*,\s*(?P<rest>.+)\s*$")


def parse_can_id(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    # if it's purely hex without 0x (e.g., 4D1), treat as hex in log contexts
    if re.fullmatch(r"[0-9A-Fa-f]+", s) and any(c.isalpha() for c in s):
        return int(s, 16)
    # fallback decimal
    return int(float(s))


def parse_bytes_from_hex_data(hexdata: str) -> bytes:
    hexdata = hexdata.strip()
    if hexdata == "":
        return b""
    if len(hexdata) % 2 != 0:
        # odd length -> pad right (rare, but keep moving)
        hexdata += "0"
    b = bytes.fromhex(hexdata)
    return b


def parse_bytes_from_csv_parts(rest: str) -> bytes:
    parts = [p.strip() for p in rest.split(",")]
    # allow "00 11 22 ..." in a single field too
    if len(parts) == 1 and " " in parts[0]:
        parts = [p.strip() for p in parts[0].split()]
    if len(parts) < 8:
        raise ValueError("CSV frame line must contain 8 data bytes after id.")
    return bytes(int(p, 16) for p in parts[:8])


def get_little_endian(data8: bytes, start_bit: int, bit_len: int) -> int:
    val = int.from_bytes(data8, byteorder="little", signed=False)
    mask = (1 << bit_len) - 1
    return (val >> start_bit) & mask


def get_big_endian(data8: bytes, start_bit: int, bit_len: int) -> int:
    # Motorola: bit 0 is MSB of byte 0
    result = 0
    for i in range(bit_len):
        bit_index = start_bit + i
        byte_index = bit_index // 8
        bit_in_byte = 7 - (bit_index % 8)
        bit = (data8[byte_index] >> bit_in_byte) & 1
        result = (result << 1) | bit
    return result


def to_signed(value: int, bit_len: int) -> int:
    sign_bit = 1 << (bit_len - 1)
    if value & sign_bit:
        return value - (1 << bit_len)
    return value


def load_signals(signals_csv_path: str) -> Dict[int, List[SignalDef]]:
    by_id: Dict[int, List[SignalDef]] = {}
    with open(signals_csv_path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not row.get("name") or not row.get("can_id"):
                continue
            can_id = parse_can_id(row["can_id"])
            sd = SignalDef(
                name=row.get("name", "").strip(),
                can_id=can_id,
                units=row.get("units", "").strip(),
                start_bit=int(float(row.get("start_bit", "0") or 0)),
                bit_length=int(float(row.get("bit_length", "1") or 1)),
                offset=float(row.get("offset", "0") or 0),
                scale=float(row.get("scale", "1") or 1),
                signed=(row.get("signedness", "").strip().lower() in ("signed", "s", "1", "true", "yes")),
                big_endian=(row.get("endian", "").strip().lower() in ("motorola", "big", "be", "msb", "0", "true", "yes")),
                dlc=int(float(row.get("dlc", "8") or 8)),
            )
            by_id.setdefault(can_id, []).append(sd)
    return by_id


def parse_frame_line(line: str) -> Optional[Tuple[Optional[str], int, bytes]]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    # CSV-ish
    m = CSV_RE.match(line)
    if m:
        ts = m.group("ts").strip()
        cid = parse_can_id(m.group("id"))
        data = parse_bytes_from_csv_parts(m.group("rest"))
        return (ts, cid, data)

    # candump / ID#DATA
    m = CAN_DUMP_RE.match(line)
    if m:
        ts = m.group("ts")
        cid_hex = m.group("id")
        data_hex = m.group("data") or ""
        cid = int(cid_hex, 16)  # candump IDs are hex
        data = parse_bytes_from_hex_data(data_hex)
        return (ts, cid, data)

    return None


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2

    signals_csv = sys.argv[1]
    log_path = sys.argv[2]
    out_csv = sys.argv[3]

    signals_by_id = load_signals(signals_csv)

    total_frames = 0
    decoded_rows = 0
    skipped_frames = 0

    with open(out_csv, "w", newline="", encoding="utf-8") as f_out:
        w = csv.writer(f_out)
        w.writerow(["timestamp", "can_id", "signal", "value", "units", "raw"])

        with open(log_path, "r", encoding="utf-8", errors="replace") as f_in:
            for line in f_in:
                parsed = parse_frame_line(line)
                if parsed is None:
                    continue

                ts, cid, data = parsed
                total_frames += 1

                # normalize to 8 bytes for bit extraction
                if len(data) < 8:
                    data8 = data + b"\x00" * (8 - len(data))
                else:
                    data8 = data[:8]

                sigs = signals_by_id.get(cid)
                if not sigs:
                    skipped_frames += 1
                    continue

                for sd in sigs:
                    raw = get_big_endian(data8, sd.start_bit, sd.bit_length) if sd.big_endian else get_little_endian(data8, sd.start_bit, sd.bit_length)
                    if sd.signed:
                        raw = to_signed(raw, sd.bit_length)
                    value = raw * sd.scale + sd.offset
                    w.writerow([ts or "", f"0x{cid:X}", sd.name, value, sd.units, raw])
                    decoded_rows += 1

    print(f"Frames read: {total_frames}")
    print(f"Frames with matching CAN IDs: {total_frames - skipped_frames}")
    print(f"Decoded signal rows written: {decoded_rows}")
    print(f"Output: {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

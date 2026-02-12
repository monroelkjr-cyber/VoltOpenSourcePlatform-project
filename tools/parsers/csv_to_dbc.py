#!/usr/bin/env python3
"""
Convert Racelogic-exported signal CSV -> minimal DBC.

Input CSV headers (expected):
name,can_id,units,start_bit,bit_length,offset,scale,max,min,signedness,endian,dlc

Output:
docs/can/racelogic/volt_public.dbc

Notes:
- This is a *minimal* but usable DBC.
- We create one message per unique CAN ID.
- If DLC is missing/blank, we default to 8.
- If endian field is unknown, we default to little-endian (Intel).
- If signedness is unknown, we default to unsigned.
"""

import csv
import re
import sys
from collections import defaultdict

DEFAULT_DLC = 8
DEFAULT_SENDER = "VOSP"
DEFAULT_RECEIVER = "Vector__XXX"

def sanitize_name(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[^A-Za-z0-9_]", "_", s)
    if not s:
        s = "SIG"
    if s[0].isdigit():
        s = "_" + s
    return s

def parse_can_id(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(float(s))

def parse_int(s: str, default: int) -> int:
    s = (s or "").strip()
    if s == "":
        return default
    return int(float(s))

def parse_float(s: str, default: float) -> float:
    s = (s or "").strip()
    if s == "":
        return default
    return float(s)

def is_signed(s: str) -> bool:
    t = (s or "").strip().lower()
    return t in ("signed", "s", "1", "true", "yes")

def is_big_endian(s: str) -> bool:
    t = (s or "").strip().lower()
    # Common variants we might see:
    # "motorola", "big", "be", "msb", "1"
    return t in ("motorola", "big", "be", "msb", "1", "true", "yes")

def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: csv_to_dbc.py input.csv output.dbc")
        return 2

    input_csv = sys.argv[1]
    output_dbc = sys.argv[2]

    rows = []
    with open(input_csv, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not row.get("name"):
                continue
            rows.append(row)

    # Group signals by CAN ID
    by_id = defaultdict(list)
    for row in rows:
        can_id = parse_can_id(row["can_id"])
        by_id[can_id].append(row)

    # Build DBC
    lines = []
    lines.append('VERSION ""')
    lines.append("")
    lines.append("NS_ :")
    lines.append("\tNS_DESC_")
    lines.append("\tCM_")
    lines.append("\tBA_DEF_")
    lines.append("\tBA_")
    lines.append("\tVAL_")
    lines.append("\tCAT_DEF_")
    lines.append("\tCAT_")
    lines.append("\tFILTER")
    lines.append("\tBA_DEF_DEF_")
    lines.append("\tEV_DATA_")
    lines.append("\tENVVAR_DATA_")
    lines.append("\tSGTYPE_")
    lines.append("\tSGTYPE_VAL_")
    lines.append("\tBA_DEF_SGTYPE_")
    lines.append("\tBA_SGTYPE_")
    lines.append("\tSIG_TYPE_REF_")
    lines.append("\tVAL_TABLE_")
    lines.append("\tSIG_GROUP_")
    lines.append("\tSIG_VALTYPE_")
    lines.append("\tSIGTYPE_VALTYPE_")
    lines.append("\tBO_TX_BU_")
    lines.append("\tBA_DEF_REL_")
    lines.append("\tBA_REL_")
    lines.append("\tBA_DEF_DEF_REL_")
    lines.append("\tBU_SG_REL_")
    lines.append("\tBU_EV_REL_")
    lines.append("\tBU_BO_REL_")
    lines.append("\tSG_MUL_VAL_")
    lines.append("")
    lines.append("BS_:")
    lines.append("")
    lines.append(f"BU_: {DEFAULT_SENDER}")
    lines.append("")

    # Deterministic ordering
    for can_id in sorted(by_id.keys()):
        sigs = by_id[can_id]

        # message name: MSG_<ID>
        msg_name = f"MSG_{can_id}"
        dlc = DEFAULT_DLC
        for s in sigs:
            dlc = parse_int(s.get("dlc", ""), dlc)

        lines.append(f"BO_ {can_id} {msg_name}: {dlc} {DEFAULT_SENDER}")

        for s in sigs:
            name = sanitize_name(s["name"])
            start_bit = parse_int(s.get("start_bit", ""), 0)
            bit_len = parse_int(s.get("bit_length", ""), 1)
            offset = parse_float(s.get("offset", ""), 0.0)
            scale = parse_float(s.get("scale", ""), 1.0)
            vmin = parse_float(s.get("min", ""), 0.0)
            vmax = parse_float(s.get("max", ""), 0.0)
            units = (s.get("units", "") or "").strip()

            signed = is_signed(s.get("signedness", ""))
            big_end = is_big_endian(s.get("endian", ""))

            # DBC signal format:
            # SG_ <name> : <start>|<len>@<endian><sign> (<factor>,<offset>) [min|max] "<unit>" <receiver>
            # endian: 0 = Motorola (big), 1 = Intel (little)
            endian_num = 0 if big_end else 1
            sign_char = "-" if signed else "+"

            lines.append(
                f' SG_ {name} : {start_bit}|{bit_len}@{endian_num}{sign_char} '
                f'({scale},{offset}) [{vmin}|{vmax}] "{units}" {DEFAULT_RECEIVER}'
            )

        lines.append("")

    with open(output_dbc, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip() + "\n")

    print(f"DBC written: {output_dbc} (messages: {len(by_id)}, signals: {len(rows)})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

import csv
import sys


def parse_can_id(s: str) -> int:
    s = s.strip()
    if s.lower().startswith("0x"):
        return int(s, 16)
    return int(float(s))


def parse_bytes(hex_str: str) -> bytes:
    parts = hex_str.replace(",", " ").split()
    if len(parts) != 8:
        raise ValueError("Expected exactly 8 bytes.")
    return bytes(int(p, 16) for p in parts)


def get_little_endian(data: bytes, start_bit: int, bit_len: int) -> int:
    val = int.from_bytes(data, byteorder="little", signed=False)
    mask = (1 << bit_len) - 1
    return (val >> start_bit) & mask


def get_big_endian(data: bytes, start_bit: int, bit_len: int) -> int:
    # Motorola bit numbering:
    # Bit 0 = MSB of byte 0
    result = 0
    for i in range(bit_len):
        bit_index = start_bit + i
        byte_index = bit_index // 8
        bit_in_byte = 7 - (bit_index % 8)
        bit = (data[byte_index] >> bit_in_byte) & 1
        result = (result << 1) | bit
    return result


def to_signed(value: int, bit_len: int) -> int:
    sign_bit = 1 << (bit_len - 1)
    if value & sign_bit:
        return value - (1 << bit_len)
    return value


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: decode_frame_from_csv.py <csv> <can_id> <8 bytes hex>")
        return 2

    csv_path = sys.argv[1]
    can_id = parse_can_id(sys.argv[2])
    data = parse_bytes(sys.argv[3])

    rows = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not row.get("can_id"):
                continue
            if parse_can_id(row["can_id"]) == can_id:
                rows.append(row)

    if not rows:
        print("No signals for that CAN ID.")
        return 0

    print(f"CAN ID {hex(can_id)}  DATA {data.hex(' ')}")
    print("-" * 60)

    for row in rows:
        name = row["name"]
        units = row["units"]
        start_bit = int(float(row["start_bit"]))
        bit_len = int(float(row["bit_length"]))
        offset = float(row["offset"])
        scale = float(row["scale"])
        signedness = row["signedness"].lower()
        endian = row["endian"].lower()

        if "motorola" in endian or "big" in endian:
            raw = get_big_endian(data, start_bit, bit_len)
        else:
            raw = get_little_endian(data, start_bit, bit_len)

        if "signed" in signedness:
            raw = to_signed(raw, bit_len)

        value = raw * scale + offset

        print(f"{name}: {value} {units} (raw={raw})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

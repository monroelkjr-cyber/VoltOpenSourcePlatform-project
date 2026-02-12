# Racelogic Volt CAN Definitions

This folder contains a public Racelogic CAN channel definition file and derived artifacts for the Chevy Volt.

## Files
- `volt_public.ref`
  - Racelogic CAN channel definition container (V1a). This is the source artifact.
- `volt_public_signals.csv`
  - Extracted signal table (human-readable).
- `volt_public.dbc`
  - Minimal DBC generated from the CSV for use with standard CAN tooling.

## Tools
- `tools/parsers/racelogic_ref_extract.py`
  - Extracts signal definitions from `.ref` into CSV.
  - Example:
    - `py tools/parsers/racelogic_ref_extract.py docs/can/racelogic/volt_public.ref docs/can/racelogic/volt_public_signals.csv`
- `tools/parsers/csv_to_dbc.py`
  - Generates a minimal `.dbc` from the CSV.
  - Example:
    - `py tools/parsers/csv_to_dbc.py docs/can/racelogic/volt_public_signals.csv docs/can/racelogic/volt_public.dbc`
- `tools/parsers/decode_frame_from_csv.py`
  - Demo decoder for a single 8-byte CAN frame using the CSV (supports Intel + Motorola endian).
  - Example:
    - `py tools/parsers/decode_frame_from_csv.py docs/can/racelogic/volt_public_signals.csv 1233 "00 00 00 00 00 0A 00 00"`

## Notes
- The DBC is intentionally minimal and may not include advanced attributes/value tables.
- Signal definitions are based on the public Racelogic channel set; validate against real vehicle logs before relying on it for control logic.

"""Inspect the proposed Honda 0xE4 angle field with offline test vectors.

The field is big-endian. Bits 15:2 carry a signed angle in the existing CAN
sign convention, with one count per 0.1 degree. Bits 1:0 carry the mode.
This prototype covers the two-byte field. Authority, request, checksum and the
firmware compatibility handshake belong to the full protocol.
"""

import argparse
from typing import Tuple


MIN_COUNTS = -(1 << 13)
MAX_COUNTS = (1 << 13) - 1
MODE_BITS = 2
MODE_MASK = (1 << MODE_BITS) - 1
MODES = (0, 1)


def encode(angle_counts: int, mode: int) -> bytes:
    if not MIN_COUNTS <= angle_counts <= MAX_COUNTS:
        raise ValueError(f"angle must be {MIN_COUNTS} through {MAX_COUNTS} counts")
    if mode not in MODES:
        raise ValueError(f"reserved mode {mode}")
    return ((angle_counts << MODE_BITS) | mode).to_bytes(2, "big", signed=True)


def decode(field: bytes) -> Tuple[int, int]:
    if len(field) != 2:
        raise ValueError("expected a two-byte steering field")
    word = int.from_bytes(field, "big", signed=True)
    mode = word & MODE_MASK
    if mode not in MODES:
        raise ValueError(f"reserved mode {mode}")
    return word >> MODE_BITS, mode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("encode", help="encode a two-byte test vector")
    pack.add_argument("angle_counts", type=int, help="signed angle in tenths of a degree, in CAN units")
    pack.add_argument("mode", type=int, choices=MODES, help="0 for stock, 1 for angle")
    unpack = commands.add_parser("decode", help="decode a two-byte test vector")
    unpack.add_argument("field", help="four hexadecimal digits")

    args = parser.parse_args()
    try:
        if args.command == "encode":
            print(encode(args.angle_counts, args.mode).hex())
        else:
            angle_counts, mode = decode(bytes.fromhex(args.field))
            print(f"angle_counts={angle_counts} mode={mode}")
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

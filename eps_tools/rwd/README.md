# Local EPS firmware

This folder is intentionally retained. No `.rwd` firmware files are
distributed by eps-tools. Supply your own image for the exact EPS ECU,
retain a validated stock recovery image, and follow [the main README](../README.md).
Firmware files are ignored by Git. Do not commit them.

## Honda CR-V TLA-A220 Angle Mode

The November 25, 2026 Angle-ATM reference for this EPS is
`39990+TLA+A220-Angle-ATM-20261125-0E.rwd`. The supplied RWD is 442,493 bytes,
passes the container checksum, and lists `39990+TLA+A220` in its header.
Its SHA-256 is `3b351bc9e8d60240d66167314cae36593f3cf1df28a42f5ef959c6842a6f86a7`.

`pbm-star-angle` supports protocol v3 from
[Biscuit Labs `57dea2d`](https://github.com/Biscuit-Labs/openpilot/commit/57dea2df3afad4dfc06006effe8168116bbea180).
Angle Mode selects the protocol from live EPS status. For this image, confirm
the EPS reports software ID `39990+TLA+A220` and build `0x0E`. Verify engagement
with the matching EPS and radar on a bench before evaluating it in a vehicle.

## Recommended flashing

Add the tools to your openpilot fork root and commit them. Once the fork is
installed on the comma, run the guided flasher from `/data/openpilot/eps_tools/`.
A standalone device copy under `/data/media/0/eps_tools/` is an alternative,
not the fork integration location. See the main README for both installations.
From the installed tools folder:

```sh
python3 flash.py
```

It handles selection, validation, power prompts, bus detection, and a recommended
dry run before explicit flash confirmation. Its optional EPS communication check
is a sanity check, not an indication that the flash failed. `eps-diag.py --recovery`
adds troubleshooting guidance when investigating an unsuccessful flash.
`eps-update.py` remains the older manual alternative and the guided tool's backend.

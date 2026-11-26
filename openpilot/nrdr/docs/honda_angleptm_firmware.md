# Honda CR-V TLA-A220 Angle Mode firmware

The November 25, 2026 Angle-ATM reference for the CR-V TLA-A220 EPS is
`39990+TLA+A220-Angle-ATM-20261125-0E.rwd`. The supplied RWD is 442,493 bytes,
passes the container checksum, and lists `39990+TLA+A220` in its header.
Its SHA-256 is `3b351bc9e8d60240d66167314cae36593f3cf1df28a42f5ef959c6842a6f86a7`.

The `pbm-sunny-angle` branch supports protocol v3 for build `0x0E` from
[Biscuit Labs `57dea2d`](https://github.com/Biscuit-Labs/openpilot/commit/57dea2df3afad4dfc06006effe8168116bbea180).
The device selects the protocol from live EPS status when **Honda Angle Mode**
is on. Confirm the flashed EPS reports software ID `39990+TLA+A220` and build
`0x0E`. Older supported builds select their own protocol.

Protocol v3 carries the angle command in a field the factory Bosch radar
preserves according to the upstream implementation. The branch still requires
fresh aligned rack feedback and enforces Panda's angle and rate limits.
Verify the exact EPS and radar combination on a bench before vehicle testing.

# Continuing this project

Start with `docs/HANDOFF.md`, then the files it links for the subsystem being
changed. Read `engine/AGENTS.md` before changing engine code. Preserve existing
local changes; neither framework submodule may be edited.

Backgrounds require per-scene layer/scroll/initialization evidence. See
`docs/background-audit.md`. Decoded assets are not proof of a complete renderer;
keep capability reporting and native fallbacks accurate. Do not assume SNES/MD
planes correspond one-to-one or that all scenes repeat at their edges.

Do not commit ROMs, extracted assets, generated game code or recordings. Research
artifacts go under ignored `build/`. Verify presentation through real window
captures as well as guest-state hashes.

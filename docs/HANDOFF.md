# Shared source handoff

Start with ../SOURCE-NOTES.md and ../README.md. The Windows Widescreen Performance release includes faster expanded Genesis scenery rendering, complete Hakuna SNES forest coordinates and finite Pride Lands background framing. Previously released custom colours, presets and screen effects are retained. Per-scene evidence and targeted validation are in background-audit.md.

Expanded800x450 Genesis Pride Lands measured55.23 to78.54 updates/sec unpaced and54.65 to60.10 in the paced Windows check. Old/new native frame, WRAM and displayed pictures match. This is focused validation, not a new full walkthrough or a universal performance guarantee. The binary remains an incremental build; a byte-identical clean rebuild is not certified.

Keep frameworks unmodified at ../dependencies.json revisions. Do not commit ROMs, extracted assets, generated game code, settings, saves or recordings. Background changes require per-scene evidence in background-audit.md.

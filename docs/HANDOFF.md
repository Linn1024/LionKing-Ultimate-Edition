# Shared source handoff

Start with ../SOURCE-NOTES.md and ../README.md. Scenery colour selection now follows the original shade instead of a temporary palette index. Optional Genesis scrolling on SNES artwork uses SNES source rows and artwork boundaries; Pride Lands retains the correct positive horizontal background wrap. Per-scene evidence and validation are in background-audit.md. Existing custom colours and presets are preserved.

The Windows Scenery Fixes download contains the tested player with these fixes and the Custom Colours features. A clean rebuild reproducing the incremental local player is not certified.

Keep frameworks unmodified at ../dependencies.json revisions. Do not commit ROMs, extracted assets, generated game code, settings, saves or recordings. Background changes require per-scene evidence in background-audit.md.

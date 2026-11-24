# Shared source handoff

Start with ../SOURCE-NOTES.md and ../README.md. Scenery colour selection now follows the original shade instead of a temporary palette index. Optional Genesis scrolling on SNES artwork uses SNES source rows and artwork boundaries; Pride Lands retains the correct positive horizontal background wrap. Per-scene evidence and validation are in background-audit.md. Existing custom colours and presets are preserved.

The Windows Custom Colours download remains the previously published build. These source fixes have been checked in the newer local player; this commit does not replace the Windows ZIP. A clean rebuild reproducing the incremental local player is not certified.

Keep frameworks unmodified at ../dependencies.json revisions. Do not commit ROMs, extracted assets, generated game code, settings, saves or recordings. Background changes require per-scene evidence in background-audit.md.

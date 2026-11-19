# Lion King: Your Edition — Windows preview

Mix SNES artwork with Genesis music and gameplay, or choose resources individually.
This is a development preview: visual and performance issues remain, especially
at very large window sizes. It is an unofficial, noncommercial fan project.

## Install and play

1. Download the Windows ZIP from Releases and extract the **whole ZIP** to a
   writable folder, for example `C:\Games\LionKing`. Do not run inside the ZIP.
2. Open **Setup.cmd**. Browse to your two original ROM dumps and click
   **Prepare game data**. No Python, compiler or administrator account is needed
   for installation or play.
3. Open **Play.cmd** for **The best** preset: SNES artwork and colours, Genesis
   music/sounds/gameplay, SNES Stampede damage and the longer Bug Hunt timer.
   Alternatively use **Play Full Genesis.cmd** or
   **Play SNES Visuals with Genesis Gameplay.cmd**.
4. Press **F12** to mix individual resources and save your own named presets.
   Each choice explains whether it applies when you resume or restarts the level.
   The game is paused while you customize it.

Setup needs these exact **uncompressed, unmodified 3 MiB** dumps. Renaming a
different ROM does not make it compatible. Headered SNES ROMs are not supported.

| ROM | SHA-256 |
| --- | --- |
| SNES USA, unheadered | `457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712` |
| Mega Drive / Genesis World | `e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5` |

ROMs are not included or downloaded. Setup prepares assets locally in
`game-data`. This build also retains imported ROM payloads there for its hybrid
runtime; do not delete that folder after installing. The port uses native game
code with emulated console components; it is not a wholly native replacement.

Use the in-game settings for controls, display and practice-level selection.
Start with a normal window before trying an expanded view. Settings and saves
are kept under `settings`; named presets are also kept in your Windows app-data
folder. A reinstall must not require deleting them.

If Windows blocks the downloaded ZIP, inspect its origin and SHA-256 first.
The preview is unsigned. Report the launcher, level, window size, selected
preset and a short clip/timecode when reporting a problem. Do not upload ROMs,
prepared `game-data`, or save states to the public repository.

## Recording

**Record Video.cmd** records a three-minute gameplay clip with sound. It needs
Python 3 and FFmpeg on PATH (these are optional, only for recording). Close the
game window to finish early. Output is under `build/video-recordings`, and the
script prints the complete MP4 path. Keep the window visible and at the same
size while recording.

Examples from a terminal:

```powershell
python tools/record_video.py --preset best --seconds 180
python tools/record_video.py --preset genesis --level 1 --seconds 60 --fps-counter
python tools/record_video.py --preset best --desktop --seconds 120
```

Levels are numbered from 0 (Pride Lands). `--desktop` records the primary
desktop, including the separate F12 customization window; close unrelated
windows first. The default records only the game-window rectangle. Audio comes
from the game's mixed output and is aligned to capture start; it does not
record your microphone or system sounds. The capture shows real-time stalls.

See [VIDEO-SCRIPT.md](VIDEO-SCRIPT.md) for the proposed short presentation.

## For developers and distributors

`tools/package_share.py` builds an allowlisted Windows ZIP from the current
installed player, its preparers, runtime dependencies, licenses and launchers.
It never copies ROMs, prepared assets, settings, saves or recordings. Keep the
licenses and the matching Genesis Plus GX source archive with the binary.
Release binaries belong in **GitHub Releases**, not Git commits.

The maintained source snapshot excludes generated game code and both framework
working trees. Their pinned upstream revisions and URLs are recorded separately.
The current preview was linked incrementally against reviewed local objects;
the source snapshot is not yet a certified byte-for-byte clean rebuild of that
preview. The local `build/` history is research evidence, not a release input
for players.

The Lion King belongs to its original rights holders. This project is not
affiliated with Disney, Virgin Interactive, Nintendo or Sega. Preserve upstream
credits and component licenses. The included runtime/backend restrict this
distribution to noncommercial use.

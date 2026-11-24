# Source snapshot and credits

This is the maintained source snapshot for The Lion King: Ultimate Edition.
The working Windows binary has been built incrementally from reviewed local
objects. A byte-for-byte clean rebuild from this snapshot is not yet certified;
use the Windows ZIP in Releases to play. Some development tools reference local
ignored research history; those tools are not required by the installer.

Ultimate Edition by [Linn1024](https://github.com/Linn1024).
Based on [TLKRecomp by Alejandro AR (kinduff) and contributors](https://github.com/kinduff/TLKRecomp).
See [CREDITS.md](CREDITS.md) for edition and upstream credits.
Port source license: engine/LICENSE. Framework URLs/revisions: dependencies.json.
Fetch those frameworks into engine/snesrecomp and engine/recomp-ui before trying
scripts/Build.ps1. Frameworks must be kept unmodified. The generator takes your
local original ROM and produces ignored engine/generated files.

No ROM, extracted game assets, generated game source, saves, recordings or
personal settings are committed. The binary includes translated program code;
it and the matching backend source/licenses are distributed as release assets.

The Lion King is an original Disney/Virgin Interactive game. This is an unofficial
fan project. The combined runtime is noncommercial; see the packaged licenses.

Optional external screen effects include a GLSL adaptation of the installed BizHawk 3xBRZ Linear recipe, HQ2x, scanlines and bicubic. Original shader source and notices are under engine/runner/shaders. GPL text accompanies 3xBRZ; shader resources retain their original licenses.

The current source includes optional scenery effects, independent custom sprite colours and a stable palette editor with separate SNES/Genesis edits, pose previews, resets and preset saving. The Best enables the optional scenery effects. The Windows Custom Colours release includes these features.

The source now also fixes scenery shade-selection stability, adapts optional Genesis scrolling to the SNES artwork boundaries, and corrects Pride Lands background wrapping. These fixes are tested locally; the published Windows Custom Colours ZIP is unchanged.

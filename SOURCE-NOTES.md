# Source snapshot and credits

This is the maintained project source snapshot accompanying preview7004.
The working Windows binary has been built incrementally from reviewed local
objects. A byte-for-byte clean rebuild from this snapshot is not yet certified;
use the Windows ZIP in Releases to play. Some development tools reference local
ignored research history; those tools are not required by the installer.

Based on [TLKRecomp by kinduff and contributors](https://github.com/kinduff/TLKRecomp).
Port source license: engine/LICENSE. Framework URLs/revisions: dependencies.json.
Fetch those frameworks into engine/snesrecomp and engine/recomp-ui before trying
scripts/Build.ps1. Frameworks must be kept unmodified. The generator takes your
local original ROM and produces ignored engine/generated files.

No ROM, extracted game assets, generated game source, saves, recordings or
personal settings are committed. The binary includes translated program code;
it and the matching backend source/licenses are distributed as release assets.

The Lion King is an original Disney/Virgin Interactive game. This is an unofficial
fan project. The combined runtime is noncommercial; see the packaged licenses.

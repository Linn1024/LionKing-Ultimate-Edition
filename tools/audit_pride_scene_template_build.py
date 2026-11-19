"""Bind all fresh candidate objects and the changed decoder-template header."""
from pathlib import Path

original=Path(__file__).with_name('audit_pride_player_build.py')
source=original.read_text()
changes={
    "base = ROOT / 'build/pride-player'":"base = ROOT / 'build/pride-scene-template-work/player'",
    "assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base)), source":
        "assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base) and not source.is_relative_to(ROOT/'build/pride-bounce-owner-work/game-program')), source",
    "ROOT / 'build/pride-player-configure2.log', ROOT / 'build/pride-player-build.log'":
        "ROOT/'build/pride-scene-template-work/configure.log',ROOT/'build/pride-scene-template-work/build.log',original,ROOT/'build/pride-scene-template-work/commands.json',ROOT/'build/pride-bounce-owner-work/game-program/generation-report.json',ROOT/'build/pride-scene-template-baseline/report.json',ROOT/'engine/runner/pride/pride_scene_template.h'",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))

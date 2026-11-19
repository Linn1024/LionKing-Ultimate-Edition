"""Audit the separate lizard-launch sound player and its freshly generated program."""
from pathlib import Path

original=Path(__file__).with_name('audit_pride_player_build.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-lizard-launch-work/player'")
source=source.replace("assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base)), source",
    "assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base) and not source.is_relative_to(ROOT/'build/pride-lizard-launch-work/game-program')), source")
source=source.replace("ROOT / 'build/pride-player-configure2.log', ROOT / 'build/pride-player-build.log'",
    "ROOT/'build/pride-lizard-launch-work/configure.log', ROOT/'build/pride-lizard-launch-work/build.log', original, ROOT/'build/pride-lizard-launch-work/game-program/generation-report.json', ROOT/'build/pride-lizard-launch-baseline/report.json', ROOT/'engine/runner/tlk_lizard_audio.c', ROOT/'engine/runner/tlk_lizard_audio.h', ROOT/'engine/runner/tlk_audio.c', ROOT/'engine/runner/tlk_audio.h', ROOT/'engine/runner/tlk_resources.c', ROOT/'engine/cmake/native_adapters.h.in'")
exec(compile(source,str(original),'exec'))

"""Audit fresh pickup-flight player objects with reviewed immutable generation inputs."""
from pathlib import Path

original=Path(__file__).with_name('audit_pride_player_build.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'", "base = ROOT / 'build/pride-flight-player'")
source=source.replace("assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base)), source",
    "assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base) and not source.is_relative_to(ROOT/'build/pride-player/game-program')), source")
source=source.replace("ROOT / 'build/pride-player-configure2.log', ROOT / 'build/pride-player-build.log'",
    "base/'CMakeCache.txt', base/'build.log', base/'placement-build.log', original, ROOT/'build/pride-player/game-program/generation-report.json', ROOT/'build/pride-flight-baseline/report.json', ROOT/'engine/runner/tlk_pickup_flight_role.h', ROOT/'engine/runner/tlk_wide.c', ROOT/'engine/runner/tlk_resources.c'")
source=source.replace("every_object_and_archive_in_new_build=True,", "every_object_and_archive_in_new_build=True, reviewed_guest_generation_reused=True,")
exec(compile(source,str(original),'exec'))

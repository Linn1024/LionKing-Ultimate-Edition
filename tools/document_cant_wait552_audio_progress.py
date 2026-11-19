"""Bind restored second-level scope and the first scoped sound implementation without claiming completion."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
proof=ROOT/'build/cant-wait551-roar/report.json';assert bound(proof)['result']=='PASS'
build=ROOT/'build/cant-wait550/build-report.json';bound(build)
paths=[Path(__file__),proof,build,ROOT/'build/cant-wait547-audio/report.json',ROOT/'build/cant-wait549-md-actors/report.json',*[ROOT/x for x in ('docs/HANDOFF.md','docs/second-level-goal.md','docs/cant-wait-sound-gameplay-goal.md','engine/runner/tlk_audio.c','engine/runner/tlk_resources.c','tools/pride_arena_history.py','tools/build_cant_wait550.py')]]
out=ROOT/'build/cant-wait552-audio-progress';out.mkdir(exist_ok=True)
(out/'report.json').write_text(json.dumps(dict(result='SECOND_LEVEL_AUDIO_PROGRESS',full_requested_scope_complete=False,published=False,first_roar_qualified=True,remaining='Animal/interaction/running/pickup effects, audio lifecycle/native-music checks and observable gameplay assessment; do not substitute earlier graphics/route completion.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('SECOND_LEVEL_AUDIO_PROGRESS; candidate550 only; full goal active',flush=True)

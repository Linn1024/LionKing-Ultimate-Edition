"""Qualify the final resource-only correction and preserve the prior publication."""
import json,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/graveyard722-qualified';out.mkdir(exist_ok=True)
paths=[ROOT/'build'/p/'report.json' for p in ('graveyard714-qualified','graveyard721-independent','graveyard721-window')]
reports=[bound(p) for p in paths];build=ROOT/'build/graveyard720/build-report.json';bound(build)
archive=ROOT/'build/graveyard722-publication-baseline';archive.mkdir();rows={}
for name in ('scripts/RunInstalledPreview.ps1','game-data/install.json'):
 p=ROOT/name;q=archive/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);rows[name]=dict(sha256=digest(p),archive=q.relative_to(ROOT).as_posix())
(archive/'report.json').write_text(json.dumps(dict(historical_sources=rows),indent=2)+'\n')
h=ROOT/'tools/pride_arena_history.py';s=h.read_text();a="    folders.append('graveyard719-resource-baseline')";assert a in s;h.write_text(s.replace(a,a+"\n    folders.append('graveyard722-publication-baseline')"))
checks=dict(prior_four_fixes=reports[0]['result']=='PASS',death_only_native_art_viewport=reports[1]['result']=='PASS',actual_death_only_window=reports[2]['result']=='PASS')
paths += [Path(__file__),build]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope='720 changes only resource presentation eligibility and installed-data validation; prior714 scoped combat/audio/retry qualification retained.721 exercises MD death movement alone with native artwork/palette/256 viewport and current save.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks)

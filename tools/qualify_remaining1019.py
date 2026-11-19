"""Qualify reviewed Scar contacts and the visible final-level HUD correction."""
import csv,json
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1019-qualified';out.mkdir(exist_ok=True)
names=['remaining1004-bounds','remaining1005-bounds','remaining1008-data','remaining1009-scar','remaining1010-combat','remaining1011-md-preset','remaining1012-client','remaining1016-client','remaining1017-setup']
paths=[ROOT/'build'/n/'report.json' for n in names];r={n:bound(p) for n,p in zip(names,paths)}
checks={n:r[n]['result']=='PASS' for n in ('remaining1008-data','remaining1010-combat','remaining1011-md-preset','remaining1016-client','remaining1017-setup')}
checks['all_scar_pose_bounds_unambiguous']=r['remaining1004-bounds']['safe']==r['remaining1004-bounds']['total']==56
checks['original_prior_records_preserved']=all(r['remaining1005-bounds']['checks'].values())
checks['native_control_preserved']=r['remaining1009-scar']['checks']['native_control_unchanged']
checks['old_snes_tape_failure_retained']=r['remaining1009-scar']['result']=='INCOMPLETE' and not r['remaining1009-scar']['checks']['healthy']
a=r['remaining1012-client']['cases']['direct'];b=r['remaining1016-client']['cases']['direct'];checks['hud_correction_visible_guest_preserved']=a['guest']==b['guest'] and a['picture']!=b['picture'] and b['gameplay']['lives']==8 and b['gameplay']['health']>0
ref=ROOT/'build/remaining1001-reference/report.json';bound(ref);rows=list(csv.DictReader((ref.parent/'frames.csv').open()));checks['original_tas_reaches_ending']=int(rows[-1]['field'])==60000 and len(rows)==60000-int(rows[0]['field'])+1 and int(rows[-1]['ending'])==1553
build=ROOT/'build/remaining1014-player/build-report.json';bb=bound(build);checks['binary_identity']=digest(build.parent/'player.exe')==bb['binary_sha256']
scope='Scar has independent original MD collision rectangles for56 unambiguous reviewed poses (47 differ, up22px) under exact three-encounter ownership. Native AI/timing retained. Ordinary attacks damage Scar with Simba surviving; current save/restore and real full-available-MD Windows combat checked. The old SNES recording dies under selected MD Scar bounds and is retained as incomplete, not claimed as a selected full-route pass. Pride Rock MD HUD now updates health/roar/lives: old <=8 guard excluded9 and showed0/empty meters; actual corrected8-life client inspected, guest unchanged.1466 image bytes, preceding924 bounds and all other five gameplay sections preserved;980 total bounds, sprite-v2 policy10; scene-v3/helper787 unchanged. Most AI, Stampede perspective, bonus gameplay/FX/counters and post-fight/ending presentation remain native. Genesis TAS verification on the final installed all-available-MD build is separate and must not be inferred from the original or SNES walkthrough.'
paths += [Path(__file__),ref,ROOT/'build/remaining1018-ending/report.json',build,ROOT/'build/remaining1007-helper/build-report.json',ROOT/'scripts/Setup.ps1',ROOT/'Play Available MD.cmd',ROOT/'profiles/available-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope=scope,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,flush=True)

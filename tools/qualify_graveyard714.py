"""Qualify the four concrete Graveyard audit fixes from focused evidence."""
import json,re,csv
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
out=ROOT/'build/graveyard714-qualified';out.mkdir(exist_ok=True)
paths=[ROOT/'build'/p/'report.json' for p in ('graveyard709-scripted','graveyard710-behavior','graveyard711-death','graveyard712-death-window','graveyard713-setup')]
reports=[bound(p) for p in paths];visual,behavior,death,window,setup=reports
b=behavior['cases'];voices=b['scripted-voice']['voices'];actors=list(csv.DictReader((ROOT/'build/graveyard710-behavior/scripted-voice/actors.csv').open()))
def wram(name):return re.search(r'wram_sha256=([a-f0-9]+)',(ROOT/'build/graveyard711-death'/name/'run.log').read_text()).group(1)
checks=dict(scripted_artwork_colors=visual['result']=='PASS',scripted_voice=any(v['emitted']=='1' and any(a['actor']==v['actor'] and a['field']==v['field'] and a['descriptor']=='c58c80' for a in actors) for v in voices),hyena_contact_gameplay=b['bounds-md']['scene']['health']<b['bounds-snes']['scene']['health'] and len(b['bounds-md']['hitboxes'])>0 and not b['bounds-snes']['hitboxes'],roar_delay=any(r['event']=='activation_delay' and r['value']=='14' for r in b['roar-md']['roar']) and not b['roar-snes']['roar'],death_presentation_save_retry=death['result']=='PASS',death_guest_unchanged=wram('middle')==wram('native')==wram('restored'),real_death_window=window['result']=='PASS',native_setup=setup['result']=='PASS')
paths += [Path(__file__),ROOT/'build/graveyard708/build-report.json',ROOT/'build/graveyard707-helper/build-report.json']
bound(paths[-2]);bound(paths[-1])
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope='Focused scripted hyena art/palette/reaction voice, independent contact boxes and roar delay, nonfinal health-death movement/current save/retry. Real Windows captures. No universal MD AI or new full-MD walkthrough claim.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks)

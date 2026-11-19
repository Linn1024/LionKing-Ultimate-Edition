"""Qualify a natural idle-roar entry with both attack-timing sources and saves."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    out=ROOT/'build/pride-porcupine-idle-runtime';out.mkdir()
    base=ROOT/'build/pride-porcupine38';observer=ROOT/'build/pride-porcupine-roar-observer'
    search_path=ROOT/'build/pride-porcupine-idle-roar2/report.json';search=bound(search_path)
    tape=ROOT/search['cases']['idle-roar2-16']['full_tape']
    profile=ROOT/'build/pride-porcupine-roar-qualification/resources.ini'
    checks={};commands={};reports={}
    def capture(player,label,frames=3408,source='md',extra=()):
        cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',player.relative_to(ROOT).as_posix(),
            '--output',label,'--frames',str(frames),'--source',source,'--tape',tape.relative_to(ROOT).as_posix(),
            '--profile',profile.relative_to(ROOT).as_posix(),*map(str,extra)]
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        p=player/label/'report.json';reports[p]=bound(p);checks[label+'_capture']=reports[p]['result']=='PASS'
    capture(observer,'idle-roar-full-aot')
    capture(observer,'idle-roar-full-lle',extra=['--lle'])
    capture(base,'idle-roar-full')
    capture(base,'idle-roar-native',source='snes')
    capture(base,'idle-roar-entry',frames=3240,extra=['--save-at',3240])
    seed=base/'idle-roar-entry';tree=json.loads((seed/'tree.jsonl').read_text().splitlines()[-1])
    assert tree['field']==3240
    for label,extra in [('idle-roar-cold',[]),('idle-roar-cold-lle',['--lle'])]:
        capture(base,label,extra=['--load',(seed/'saved.state').relative_to(ROOT),'--poll-offset',tree['poll_index'],*extra])
    def equal(label,a,b,names=('window.png','scene.json','audio.wav')):
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        for name in names:checks[label+'_'+name]=digest(a/name)==digest(b/name)
    equal('idle_modes',observer/'idle-roar-full-aot',observer/'idle-roar-full-lle',('window.png','scene.json','audio.wav','attack.csv','events.csv'))
    equal('observer_neutral',observer/'idle-roar-full-aot',base/'idle-roar-full',('window.png','scene.json','audio.wav','events.csv'))
    equal('cold_modes',base/'idle-roar-cold',base/'idle-roar-cold-lle',('window.png','scene.json','audio.wav','attack.csv','events.csv'))
    equal('cold_warm',base/'idle-roar-cold',base/'idle-roar-full',('window.png','scene.json'))
    checks['cold_remaining_pcm']=pcm(base/'idle-roar-cold/audio.wav')==pcm(base/'idle-roar-full/audio.wav')[len(pcm(seed/'audio.wav')):]
    rows=list(csv.DictReader((observer/'idle-roar-full-aot/attack.csv').open()))
    new=[r for r in rows if r['actor']=='b913' and r['pc']=='c15c64']
    checks['natural_late_entry']=bool(new) and new[0]['field']=='3241' and new[0]['timer']=='28' and new[0]['wait']=='0' and new[0]['persistent']=='1'
    checks['entry_player_roaring']=bool(new) and new[0]['player_action']=='c3589c'
    def cues(label):
        return [int(r['frame']) for r in csv.DictReader((base/label/'events.csv').open()) if r['event']=='0015' and int(r['frame'])>=3208]
    checks['md_immediate_phase_cue']=cues('idle-roar-full')==[3240]
    checks['native_eight_update_later_cue']=cues('idle-roar-native')==[3248]
    previous=bound(ROOT/'build/pride-porcupine-roar-saves/report.json')
    offset=previous['actual_saved_wram_offset'];raw=(seed/'saved.state').read_bytes();ram=raw[offset:offset+0x20000]
    expected=re.search(r'wram_sha256=([0-9a-f]{64})',(seed/'run.log').read_text())[1]
    assert hashlib.sha256(ram).hexdigest()==expected
    (out/'entry-wram.bin').write_bytes(ram)
    word=lambda at:int.from_bytes(ram[at:at+2],'little')
    pointer=lambda at:int.from_bytes(ram[at:at+3],'little')
    checks['actual_saved_roar_strength24']=word(0xa698)==24
    checks['original_late_constructor_fields']=pointer(0xb943)==0xc15b87 and pointer(0xb921)==0xc288ac and word(0xb93f)==28 and word(0xb92f)==0 and word(0xb935)==1
    actor=0xb913;distance=max(abs(word(0xb21b)-word(actor+8)),abs(word(0xb21d)-word(actor+10)))
    effective=word(0xa698)-max(0,distance-50)//8
    checks['live_original_rule_exceeds10']=effective>10
    checks['field_layout_does_not_reuse_md_wait']=word(actor+0x1c)==0
    paths=[Path(__file__),search_path,ROOT/'build/pride-porcupine-idle/report.json',
           ROOT/'build/md-porcupine-idle-roar2/report.json',base/'build-report.json',observer/'build-report.json',tape,profile,*reports]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        live_entry_distance=distance,live_entry_effective_strength=effective,entry_poll_index=tree['poll_index'],
        ordinary_controls_only=True,guest_rom_or_rng_edits=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),distance,effective,[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

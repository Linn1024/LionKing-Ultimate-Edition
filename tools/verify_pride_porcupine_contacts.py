"""Qualify real attributed attack hits, avoidance and pending-damage cold saves."""
import csv
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes
from verify_pride_final_scene_runtime import pcm


def main():
    observer=ROOT/'build/pride-porcupine-contact-observer';player=ROOT/'build/pride-porcupine38'
    out=ROOT/'build/pride-porcupine-contact-verification';out.mkdir()
    search_path=ROOT/'build/pride-porcupine-contact-search/report.json';search=bound(search_path)
    original_tape=ROOT/'engine/tapes/allbugsF.read.tape'
    neutral_tape=ROOT/'build/pride-porcupine-contact-search/neutral/poweron.polled.tape'
    pending=player/'contact-pending';pending_report=bound(pending/'report.json')
    raw=(pending/'saved.state').read_bytes()
    expected=re.search(r'wram_sha256=([0-9a-f]{64})',(pending/'run.log').read_text())[1]
    # Locate the actual contiguous WRAM by a live actor signature, then require
    # its full128KiB hash to equal the independently emitted runtime hash.
    signature=bytes.fromhex('5c8cc500f401a303');offsets=[];at=raw.find(signature)
    while at>=0:
        start=at-0xb717
        if start>=0 and hashlib.sha256(raw[start:start+0x20000]).hexdigest()==expected:offsets.append(start)
        at=raw.find(signature,at+1)
    assert len(offsets)==1,offsets
    ram=raw[offsets[0]:offsets[0]+0x20000];(out/'pending-wram.bin').write_bytes(ram)
    w=lambda at:struct.unpack_from('<H',ram,at)[0]
    ptr=lambda at:int.from_bytes(ram[at:at+3],'little')
    tree=[json.loads(line) for line in (pending/'tree.jsonl').read_text().splitlines()]
    used=tree[-1]['poll_index'];assert tree[-1]['field']==1471
    prefix=original_tape.read_bytes()[:search['anchor_poll_offset']*2]
    avoid=out/'avoid.polled.tape';avoid.write_bytes(prefix+(ROOT/'build/pride-porcupine-contact-search/left32/tail.polled.tape').read_bytes())
    jump=out/'pending-jump.polled.tape'
    jump.write_bytes(neutral_tape.read_bytes()[:used*2]+struct.pack('<H',0x8000)+bytes(398))
    commands={};reports={};checks={}
    def capture(base,label,source='md',tape=neutral_tape,extra=()):
        cmd=['python',str(ROOT/'tools/capture_pride_porcupine2.py'),'--player',base.relative_to(ROOT).as_posix(),
             '--output',label,'--source',source,'--frames','1600','--tape',tape.relative_to(ROOT).as_posix(),*map(str,extra)]
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        report_path=base/label/'report.json';reports[report_path]=bound(report_path)
        checks[label+'_capture']=reports[report_path]['result']=='PASS'
    capture(observer,'avoid-aot',tape=avoid)
    capture(observer,'avoid-lle',tape=avoid,extra=['--lle'])
    capture(player,'contact-neutral-native-lle',source='snes',extra=['--lle'])
    for label,mode in [('contact-pending-cold',[]),('contact-pending-cold-lle',['--lle'])]:
        capture(player,label,extra=['--load',(pending/'saved.state').relative_to(ROOT),'--poll-offset',used,*mode])
    capture(player,'contact-pending-jump',tape=jump)
    capture(player,'contact-pending-jump-lle',tape=jump,extra=['--lle'])
    for base,label in [(observer,'neutral-aot'),(observer,'neutral-lle'),(player,'contact-neutral-native'),(player,'contact-neutral-md')]:
        p=base/label/'report.json';reports[p]=bound(p)
    def equal(label,a,b,names=('window.png','scene.json','audio.wav')):
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        for name in names:checks[label+'_'+name]=digest(a/name)==digest(b/name)
    equal('hit_modes',observer/'neutral-aot',observer/'neutral-lle',('window.png','scene.json','audio.wav','attack.csv','events.csv'))
    equal('observer_neutral',observer/'neutral-aot',player/'contact-neutral-md',('window.png','scene.json','audio.wav','events.csv'))
    equal('avoid_modes',observer/'avoid-aot',observer/'avoid-lle',('window.png','scene.json','audio.wav','attack.csv','events.csv'))
    equal('native_modes',player/'contact-neutral-native',player/'contact-neutral-native-lle')
    equal('pending_cold_modes',player/'contact-pending-cold',player/'contact-pending-cold-lle',('window.png','scene.json','audio.wav','attack.csv','events.csv'))
    equal('pending_cold_warm',player/'contact-pending-cold',player/'contact-neutral-md',('window.png','scene.json'))
    equal('pending_jump_modes',player/'contact-pending-jump',player/'contact-pending-jump-lle')
    rows=list(csv.DictReader((observer/'neutral-aot/attack.csv').open()))
    hits=[r for r in rows if r['pc']=='c15c8f' and r['phase_before']=='1' and r['contact_result']=='ffff']
    first=hits[0];checks['real_initial_late_contact']=first['field']=='1471' and first['timer']=='28' and first['contact_flag']=='0'
    checks['original_reaction_attributed']=first['actor']=='b713' and first['victim']=='b213' and int(first['player_flags'],16)&4 and first['attacker']=='7eb713'
    checks['health_still4_when_reaction_queued']=first['health']=='4'
    avoided=list(csv.DictReader((observer/'avoid-aot/attack.csv').open()))
    checks['avoid_executes_late_checks']=any(r['pc']=='c15c8f' and r['phase_before']=='1' for r in avoided)
    checks['avoid_has_no_contact']=not any(r['pc']=='c15c8f' and r['phase_before']=='1' and r['contact_result']=='ffff' for r in avoided)
    def health_drops(base,label):
        data=[json.loads(line) for line in (base/label/'tree.jsonl').read_text().splitlines() if json.loads(line)['field']>=1400]
        return [(b['field'],a['health'],b['health']) for a,b in zip(data,data[1:]) if b['health']<a['health']]
    checks['md_one_damage1472']=health_drops(player,'contact-neutral-md')==[(1472,4,3)]
    checks['native_one_damage1486']=health_drops(player,'contact-neutral-native')==[(1486,4,3)]
    checks['avoid_no_damage']=health_drops(observer,'avoid-aot')==[]
    checks['pending_snapshot_exact_ram']=hashlib.sha256(ram).hexdigest()==expected
    checks['pending_snapshot_real_flag_link']=w(0x2004)==4 and ram[0xb256]&4 and ptr(0xb237)==0x7eb713
    checks['pending_snapshot_live_attack']=ptr(0xb743)==0xc15b87 and w(0xb713+0x2c)==27
    checks['pending_cold_one_damage']=health_drops(player,'contact-pending-cold')==[(1472,4,3)]
    checks['pending_jump_does_not_erase_damage']=health_drops(player,'contact-pending-jump')==[(1472,4,3)]
    checks['pending_cold_remaining_pcm']=pcm(player/'contact-pending-cold/audio.wav')==pcm(player/'contact-neutral-md/audio.wav')[len(pcm(pending/'audio.wav')):]
    original=bound(player/'build-report.json');instrumented=bound(observer/'build-report.json')
    a=original['link_inputs_sha256'];b=instrumented['link_inputs_sha256']
    checks['observer_only_one_object_changes']=len(set(a)-set(b))==len(set(b)-set(a))==1 and all(a[p]==b[p] for p in set(a)&set(b))
    checks['observer_binary_inputs_bound']=digest(observer/'player.exe')==instrumented['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in b.items())
    paths=[Path(__file__),search_path,pending/'report.json',player/'build-report.json',observer/'build-report.json',*reports]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                first_original_contact=first,pending_wram_state_offset=offsets[0],pending_poll_index=used,
                ordinary_inputs_only=True,guest_rom_or_rng_edits=False,original_md_whole_damage_equivalence_proven=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

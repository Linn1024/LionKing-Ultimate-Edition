"""Natural lizard cues, early audible output, native preservation and full win."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-lizard-voice74';bp=base/'build-report.json';bound(bp)
    op=base/'allbugs-observer/build-report.json';observer=bound(op)
    reference_path=ROOT/'build/pride-hyena-voice72/voice-fight/report.json';reference=bound(reference_path)
    out=base/'voice-fight';out.mkdir();checks={};commands={};folders={};observations={}
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    for name in ('native','md-aot','md-lle'):
        folder=out/name;folder.mkdir();cmd=reference['commands']['native'].copy();cmd[0]=str(base/'allbugs-observer/player.exe')
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        if name!='native':profile+='\naudio.effects.world.lizard = md\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name.endswith('lle'):cmd+=['--lle']
        env=dict(clean,TLK_TRACKED_RAM_LOG=str(folder/'route.ram'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),
                 TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_LIZARD_ATTACK_TRACE=str(folder/'entries.csv'))
        with (folder/'run.log').open('wb') as log:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        commands[name]=cmd;folders[name]=folder
        scene=json.loads((folder/'scene.json').read_text());guest=scene['latched_gameplay']
        entries=list(csv.DictReader((folder/'entries.csv').open())) if (folder/'entries.csv').exists() else []
        driver=list(csv.DictReader((folder/'driver.csv').open()));voices=[r for r in driver if r['selector']=='2' and r['value']=='124']
        checks[name+'_exit']=rc==0
        checks[name+'_alive_owned_boss_victory']=guest['health']>0 and any(p['actor_descriptor']==0xc58c68 and p['actor_owner']==p['object'] and p['actor_action']==0xc147f7 for p in scene['pieces'])
        checks[name+'_natural_counter32_entries']=bool(entries) and all(r['counter']=='32' for r in entries)
        checks[name+'_entry_source_and_command_count']=all(int(r['emitted'])==(name!='native') for r in entries) and len(voices)==(len(entries) if name!='native' else 0)
        checks[name+'_only_selected_voice_commands']=len(driver)==len(voices)
        observations[name]=dict(entries=entries,voice_commands=voices,health=guest['health'],lives=guest['lives'])
        print(name,rc,len(entries),'counter32 entries',len(voices),'voices',flush=True)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    def hashes(folder):return re.findall(pattern,(folder/'run.log').read_text())
    old=reference_path.parent/'native';native=folders['native'];a=folders['md-aot'];b=folders['md-lle']
    checks['all4600_native_guest_fields_preserved']=len(hashes(native))==4600 and hashes(native)==hashes(old)
    checks['native_whole_pcm_preserved']=digest(native/'audio.wav')==digest(old/'audio.wav')
    for name,folder in (('aot',a),('lle',b)):
        checks[name+'_all4600_canonical_pictures_native']=len(hashes(folder))==4600 and [r[:2] for r in hashes(folder)]==[r[:2] for r in hashes(native)]
        checks[name+'_all4600_tracked_gameplay_native']=len((folder/'route.ram').read_bytes().splitlines())==4600 and (folder/'route.ram').read_bytes()==(native/'route.ram').read_bytes()
    for name in ('audio.wav','driver.csv','entries.csv','scene.json','window.png','route.ram'):checks[name+'_mode_parity']=digest(a/name)==digest(b/name)
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:
            assert stream.getframerate()==48000 and stream.getnchannels()==2 and stream.getsampwidth()==2
            return stream.readframes(stream.getnframes())
    totals={0:0};counts={};acc=0.0
    for field in range(1,4601):
        acc+=48000/(21477272.0/357366.0);n=int(acc);acc-=n;counts[field]=n;totals[field]=totals[field-1]+n
    allpcm={name:pcm(folder) for name,folder in folders.items()}
    checks['all_exact_host_sample_totals']=all(len(p)==totals[4600]*4 for p in allpcm.values())
    checks['active_sample_blocks_match_timeline']=all(int(r['samples'])==counts[int(r['frame'])] for folder in folders.values() for r in csv.DictReader((folder/'stems.csv').open()))
    entries=observations['md-aot']['entries'];events=list(csv.DictReader((native/'events.csv').open()))
    native_calls=[int(r['frame'])+1 for r in events if r['event']=='0014' and int.from_bytes(bytes.fromhex(r['stack'])[5:8],'little')+1==0xc16527]
    checks['native_eight_attack_cues_retained']=len(native_calls)==8
    if entries and native_calls:
        first=int(entries[0]['field']);late=min(f for f in native_calls if f>=first)
        begin=totals[first-1]*4;end=totals[late-1]*4;x=allpcm['native'];y=allpcm['md-aot']
        checks['pcm_exact_before_first_counter32_cue']=begin>0 and x[:begin]==y[:begin]
        checks['md_voice_audible_before_native_counter51_cue']=end>begin and x[begin:end]!=y[begin:end]
        observations['early_audio_window']=dict(first_md_cue=first,first_native_cue=late,begin_byte=begin,end_byte=end)
    else:checks['md_voice_audible_before_native_counter51_cue']=False
    checks['observer_bound']=digest(base/'allbugs-observer/player.exe')==observer['binary_sha256']
    paths=[Path(__file__),bp,op,reference_path,base/'frontend/sdl_main.c']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                ordinary_poweron_win=True,whole_enemy_ai_or_all_interruptions_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

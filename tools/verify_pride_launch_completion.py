"""Verify current supported mixtures finish Pride from ordinary power-on input."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-launch3';bp=base/'build-report.json';build=bound(bp)
    out=base/'completion';out.mkdir();checks={};commands={};sources=[Path(__file__),bp];total=0
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for width in (320,256):
        root=out/str(width);root.mkdir();name='media' if width==320 else 'media256'
        parent=ROOT/'build/pride-checkpoint-player/completion3'/name
        previous=json.loads((parent/'report.json').read_text());assert previous['result']=='PASS'
        original=parent/'resources.ini';assert digest(original)==previous['profile_sha256']
        tape=ROOT/previous['tape'];assert digest(tape)==previous['tape_sha256']
        sources.extend([original,parent/'report.json',tape])
        profile=root/'resources.ini';profile.write_text(original.read_text()+'\ngameplay.levels.pride_lands.health_death = md\n')
        for mode in ('aot','lle'):
            folder=root/mode;folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
            env=dict(clean,TLK_SPRITE_REPORT=str(folder/'coverage.json'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'))
            cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',previous['frames'],
                 '--no-audio','--no-pace','--no-record','--hash-at',','.join(map(str,range(1,previous['frames']+1))),
                 '--wav',folder/'route.wav','--wav-seconds',120,'--dump-scene',folder/'scene.json',
                 '--dump-window',folder/'window.png','--dump-png',folder/'guest.png']
            if mode=='lle':cmd+=['--lle']
            commands[f'{width}/{mode}']=list(map(str,cmd))
            with (folder/'run.log').open('wb') as log:r=subprocess.run(commands[f'{width}/{mode}'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
            checks[f'{width}/{mode}/exit']=not r.returncode
            scene=json.loads((folder/'scene.json').read_text());coverage=json.loads((folder/'coverage.json').read_text())
            checks[f'{width}/{mode}/next_main_level']=scene['level']==1
            checks[f'{width}/{mode}/no_missing_observed_poses']=not coverage['missing_poses'] and not coverage['missing_npc_poses']
            tracks={int(row['value']) for row in csv.DictReader((folder/'driver.csv').open()) if row['selector']=='1'}
            checks[f'{width}/{mode}/level_and_boss_music']={137,134}<=tracks
            stems=list(csv.DictReader((folder/'stems.csv').open()))
            checks[f'{width}/{mode}/md_audio_rendered']=len(stems)>1000 and max(int(row['md_peak']) for row in stems)>500
            print(width,mode,'final level',scene['level'],[k for k,v in checks.items() if not v],flush=True)
        a,b=root/'aot',root/'lle';rows=lambda p:re.findall(pattern,(p/'run.log').read_text());total+=len(rows(a))
        checks[f'{width}/every_aot_lle_field']=len(rows(a))==previous['frames'] and rows(a)==rows(b)
        checks[f'{width}/entire_pcm']=wav_data(a/'route.wav')==wav_data(b/'route.wav')
        for name in ('guest','window'):checks[f'{width}/{name}']=pixels(a/(name+'.png'))==pixels(b/(name+'.png'))
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,commands=commands,native_fields_compared=total,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
                ordinary_poweron_controller_inputs_only=True,loaded_states=False,practice_or_guest_edits=False,
                full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

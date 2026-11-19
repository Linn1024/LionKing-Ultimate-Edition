"""Observe original SNES contact-helper entries and every sound event on input routes."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-arrival-work/player';observer=base/'contact-audio-observer2'
    bp=observer/'build-report.json';build=bound(bp)
    assert digest(observer/'player.exe')==build['binary_sha256']
    out=ROOT/'build/native-ledge-audio';out.mkdir()
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
    ordinary=ROOT/'engine/tapes/allbugsF.read.tape'
    converted=ROOT/'build/pride-streaming-verification/aot/derived.polled.tape'
    random=ROOT/'engine/build/playtapes/l00_random.tape'
    cases=[('control',base/'player.exe',ordinary,2000,True),
           ('allbugs',observer/'player.exe',ordinary,4500,True),
           ('converted',observer/'player.exe',converted,6000,True),
           ('random',observer/'player.exe',random,5000,False)]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={};observations={}
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for name,binary,tape,frames,polled in cases:
        folder=out/name;folder.mkdir()
        child=dict(env,TLK_NATIVE_CONTACT_AUDIO_TRACE=str(folder/'entries.csv'),TLK_AUDIO_EVENTS=str(folder/'audio.csv'))
        command=list(map(str,[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',out/'missing.md',
            '--config',config,'--resource-profile',profile,'--input-polled' if polled else '--input',tape,
            '--frames',frames,'--lle','--no-pace','--no-audio','--no-record',
            '--hash-at',','.join(map(str,range(1,frames+1))),'--dump-window',folder/'window.png']))
        commands[name]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=child,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360)
        entries=list(csv.DictReader((folder/'entries.csv').open())) if (folder/'entries.csv').exists() else []
        audio=list(csv.DictReader((folder/'audio.csv').open()))
        relevant=[]
        for entry in entries:
            if entry['level']!='0' or entry['scene'] not in ('c00387','c0080d'):continue
            field=int(entry['field']);actor=entry['actor']
            nearby=[r for r in audio if r['actor']==actor and field-2<=int(r['frame'])<=field+2]
            relevant.append(dict(entry=entry,native_audio_within_two_fields=nearby))
        observations[name]=relevant
        print(name,'entries',len(entries),'Pride contacts',len(relevant),
              'directions',sorted({r['entry']['entry'] for r in relevant}),flush=True)
    rows=lambda name:re.findall(pattern,(out/name/'run.log').read_text())
    assert len(rows('control'))==2000 and rows('allbugs')[:2000]==rows('control')
    paths=[Path(__file__),bp,base/'build-report.json',ordinary,converted,random]
    report=dict(result='ORIGINAL_CONTACT_HELPERS_OBSERVED',observations=observations,commands=commands,
        observer_neutral_all_2000_picture_full_wram_fields=True,
        original_guest_or_input_mutations=False,random_route_uses_original_level_select=True,
        sound_windows_are_local_not_complete_lifetime=True,
        production_mapping_enabled=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],flush=True)


if __name__=='__main__':main()

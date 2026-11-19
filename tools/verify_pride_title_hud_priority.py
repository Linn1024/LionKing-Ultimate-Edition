"""Verify the native wide HUD keeps original OAM order at caption overlap."""
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_windows import pixels,hashes


def main():
    base=ROOT/'build/pride-title-work';out=base/'hud-priority';out.mkdir()
    parent=base/'player-check3';previous=ROOT/'build/pride-popup-work/player/native-engine/tlk_pride_player.exe'
    checks={};commands=[];observations=[]
    for width in (256,320):
        folder=out/str(width);folder.mkdir()
        cmd=[previous,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--config',parent/'host.ini','--resource-profile',parent/f'{width}-950-native/resources.ini',
             '--load',parent/'before-caption.state','--input-polled',parent/'after930.polled.tape',
             '--frames',950,'--no-pace','--no-audio','--no-record','--dump-window',folder/'previous.png']
        commands.append(list(map(str,cmd)))
        with (folder/'run.log').open('wb') as log:
            subprocess.run(commands[-1],cwd=ROOT,env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))},
                           stdout=log,stderr=subprocess.STDOUT,timeout=120,check=True)
        current=parent/f'{width}-950-native';pw,ph,old=pixels(folder/'previous.png');_,_,new=pixels(current/'window.png')
        checks[f'{width}/guest_unchanged']=hashes(folder/'run.log')==hashes(current/'run.log')
        changed={(i%pw//3,i//pw//3) for i,(a,b) in enumerate(zip(old,new)) if a!=b}
        if width==256:checks['native_snes_view_exact']=not changed
        else:
            expected={(22,14),(23,14),(21,16),(23,16),(21,17)}
            checks['only_five_overlap_pixels_corrected']=changed==expected
            scene=json.loads((current/'scene.json').read_text())
            font=next(p for p in scene['pieces'] if p['title_owner'] and p['local'][0]==0)
            meter=next(p for p in scene['pieces'] if p['fixed'] and p['screen']==[16,14])
            checks['caption_precedes_meter_in_original_oam']=font['slot']==5 and meter['slot']==13
            # Duration-only uses reconstructed native letter pixels and the
            # same priority rules, so its entire view must remain identical.
            checks['independent_duration_does_not_change_entrance']=pixels(base/'entrance3/320-950-duration/window.png')==pixels(current/'window.png')
        observations.append(dict(width=width,changed_physical_pixels=sorted(changed)))
    paths=[Path(__file__),base/'final-build3.json',base/'entrance3/report.json',previous]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'HUD priority checks',flush=True)
    assert all(checks.values()),checks


if __name__=='__main__':main()

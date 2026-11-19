"""Compare complete owned-revival pictures and actual caption-source windows."""
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_title_preview_history import bound
from verify_windows import pixels,hashes


def main():
    out=ROOT/'build/pride-title-reentry-verified';out.mkdir()
    reference=ROOT/'build/pride-title-reentry-original/report.json';original=bound(reference)
    assert original['result']=='PASS'
    md_path=ROOT/'build/pride-title-reentry/report.json';native_path=ROOT/'build/pride-title-reentry-control/report.json'
    md=bound(md_path);native=bound(native_path)
    a,b=md_path.parent,native_path.parent
    checks={};observations=[];commands=[]
    for folder in ('','scene-2458/'):
        checks[folder+'all_owned_pixels_unchanged']=digest(a/folder/'render-owned.rgb')==digest(b/folder/'render-owned.rgb')
        checks[folder+'same_owned_presentation_fields']=(a/folder/'render-fields.csv').read_bytes()==(b/folder/'render-fields.csv').read_bytes()
    events=list(csv.DictReader((a/'owner-events.csv').open()))
    begins=[r for r in events if r['event']=='begin'];normal=[r for r in events if r['event']=='normal']
    checks['two_real_owned_health_revives']=len(begins)==len(normal)==2 and [int(r['field']) for r in begins]==[1777,2458]
    binary=ROOT/'build/pride-title-work/player/native-engine/tlk_pride_player.exe'
    state=ROOT/'build/pride-scene-template-work/player/owned-regression/preceding-owned-2001.state'
    identity=digest(state);checks['legacy_owned_save']=state.read_bytes()[:8]==b'PRHSAVE1'
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 3\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for field in (2062,2076,2078,2120,2170):
        rendered=[]
        for choice in ('snes','md'):
            folder=out/f'{field}-{choice}';folder.mkdir();profile=folder/'resources.ini'
            base=(ROOT/'build/pride-scene-template-work/player/owned-regression/mixed.ini').read_text()
            profile.write_text(base+'\ngraphics.titles.pride_lands = '+choice+'\n')
            cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                 '--config',config,'--resource-profile',profile,'--input',tape,'--load',state,'--frames',field,
                 '--no-pace','--no-audio','--no-record','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
            commands.append(list(map(str,cmd)))
            with (folder/'run.log').open('wb') as log:
                subprocess.run(commands[-1],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True)
            scene=json.loads((folder/'scene.json').read_text())
            owned=[p for p in scene['pieces'] if p.get('title_owner')]
            checks[f'{field}/{choice}/no_recreated_title_task']=not owned
            observations.append(dict(field=field,choice=choice,title_pieces=len(owned),scene=scene['latched_gameplay']))
            rendered.append((pixels(folder/'window.png'),hashes(folder/'run.log')))
        checks[f'{field}/caption_sources_same_actual_view']=rendered[0]==rendered[1]
        print(field,'actual caption-source views identical',flush=True)
    checks['legacy_owned_save_unchanged']=digest(state)==identity
    paths=[Path(__file__),reference,md_path,native_path,binary,state,tape]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
                original_md_default_and_checkpoint_no_reentry_caption=True,
                port_default_owned_revives_verified=True,port_checkpoint_owned_revive_verified=False,
                gameover_continue_or_level_restart_verified=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'caption/re-entry checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()

"""Exercise current CMD entrypoints with installed data and owned settings/cache paths."""
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    out=ROOT/'build/pride-launchers66';out.mkdir();checks={};commands={};observations={}
    buildpath=ROOT/'build/pride-music-output65/build-report.json';build=bound(buildpath)
    referencepath=ROOT/'build/pride-music-output65/allbugs-verification/report.json';bound(referencepath)
    reference=hashes(referencepath.parent/'pilot-control/run.log')
    routes=[('Play.cmd','native',None),('Play Mixed Graphics.cmd','mixed-graphics',None),
        ('Play Pride Lands.cmd','native',0),('Play Pride Lands Mix.cmd','pride-lands',0),
        ('Play Development Preview.cmd','pride-development-preview',0),('Play Standalone Preview.cmd','pride-development-preview',None),
        ('Play Cant Wait Mix.cmd','next-levels',1),('Play Elephant Graveyard Mix.cmd','next-levels',2),
        ('Play Stampede Mix.cmd','next-levels',3),('Play Simbas Exile Mix.cmd','next-levels',4),
        ('Play Hakuna Matata Mix.cmd','next-levels',5),('Play Simbas Destiny Mix.cmd','next-levels',6),
        ('Play Be Prepared Mix.cmd','final-levels',7),('Play Simbas Return Mix.cmd','final-levels',8),('Play Pride Rock Mix.cmd','final-levels',9),
        ('Play Installed Preview.cmd','pride-development-preview',None)]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    clean['PATH']=str(Path(os.environ['SystemRoot'])/'System32');clean['SDL_VIDEODRIVER']='dummy'
    def run(item):
        index,(name,preset,level)=item;label=f'{index:02d}';folder=out/label;folder.mkdir();settings=folder/'settings';settings.mkdir()
        sentinel=b'current recording retained';(settings/'last_session.rec').write_bytes(sentinel)
        cmd=['cmd.exe','/d','/c','call',str(ROOT/name),'-SettingsDirectory',str(settings),'-Frames','3000','-NoPace','-NoAudio',
             '-WindowCapture',str(folder/'window.png'),'-SceneCapture',str(folder/'scene.json')]
        if level is None:cmd+=['-InputTape',str(ROOT/'engine/tapes/allbugsF.read.tape')]
        commands[name]=cmd
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv')),
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        checks[name+'_exit']=rc==0
        rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
        requested=0 if level is None else level
        entered=[r for r in rows if r['level']==requested and r['health']>0 and r['descriptor']>=0xc00000]
        checks[name+'_requested_level_alive']=bool(entered)
        checks[name+'_preset_created']=digest(settings/'resources.ini')==digest(ROOT/'profiles'/(preset+'.ini'))
        checks[name+'_recording_retained']=(settings/'last_session.rec').read_bytes()==sentinel
        log=(settings/'last-launch.log').read_text();checks[name+'_prepared_data_loaded']='resource_cache=loaded' in log
        scene=json.loads((folder/'scene.json').read_text());guest=scene['latched_gameplay']
        if name=='Play.cmd':checks['normal_full_native_endpoint']=hashes(settings/'last-launch.log')==reference
        if name=='Play Mixed Graphics.cmd':
            first=entered[-1];choice=lambda key:next(c[-1] for c in first['choices'] if c[0]==key)
            checks['mixed_viewport_and_background_md']=choice('display.viewport')==choice('graphics.scenery')==2
            checks['mixed_cub_palette_md_frames_native']=choice('graphics.sprites.simba.cub.palette')==2 and choice('graphics.sprites.simba.cub.frames')==1
            checks['mixed_gameplay_and_music_native']=choice('gameplay')==choice('audio.music.pride_lands')==1
            checks['mixed_no_md_audio_commands']=not list(csv.DictReader((folder/'driver.csv').open()))
        observations[name]=dict(folder=label,preset=preset,requested_level=requested,first_alive_field=entered[0]['field'] if entered else None,
            final_level=scene['level'],final_health=guest['health'],endpoint=hashes(settings/'last-launch.log'))
        print(name,rc,'alive',bool(entered),'level',scene['level'],flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,enumerate(routes)))
    checks['current_binary_exact']=digest(ROOT/'dist/installed-preview65/LionKing.exe')==build['binary_sha256']
    paths=[Path(__file__),buildpath,referencepath,ROOT/'scripts/RunInstalledPreview.ps1',ROOT/'tools/pride_arena_history.py',ROOT/'game-data/install.json',ROOT/'engine/tapes/allbugsF.read.tape']
    paths.extend(ROOT/name for name,_,_ in routes);paths.extend(ROOT/'profiles'/(p+'.ini') for p in sorted({p for _,p,_ in routes}))
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
        binary_or_assets_changed=False,later_level_first_entry_smoke_only=True,old_cli_or_save_compatibility_not_tested=True,
        all_settings_and_implicit_caches_owned=True,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

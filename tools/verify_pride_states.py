"""Broaden first-level artwork coverage through idle, random, run and death inputs."""
import concurrent.futures
import json
import os
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes

def main():
    dest=ROOT/'build/pride-state-verification';dest.mkdir(parents=True,exist_ok=True)
    mixed='\n'.join(line for line in (ROOT/'profiles/pride-lands.ini').read_text().splitlines()
                    if not line.startswith(('audio.','gameplay.')))+'\n'
    def run(item):
        case,mode=item;folder=dest/(case+'-'+mode);folder.mkdir(exist_ok=True)
        profile=folder/'resources.ini'
        profile.write_text(mixed if mode=='md' else 'schema = 1\ngame = snes\ndisplay.viewport = md\n')
        config=folder/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
        env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(folder/'coverage.json')
        command=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
                 '--config',str(config),'--frames','7000','--input',str(ROOT/f'engine/build/playtapes/{case}.tape'),
                 '--no-pace','--no-audio','--no-record','--dump-window',str(folder/'window.png'),
                 '--dump-scene',str(folder/'scene.json')]
        with (folder/'game.log').open('wb') as output:
            subprocess.run(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=180)
        data={'hashes':hashes(folder/'game.log'),'coverage':json.loads((folder/'coverage.json').read_text())}
        if mode=='snes':
            cmd=[str(ROOT/'engine/build-win/tlk_headless.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--frames','7000','--input',str(ROOT/f'engine/build/playtapes/{case}.tape'),
                 '--ram-log',str(folder/'native.ram')]
            with (folder/'native.log').open('wb') as output:
                subprocess.run(cmd,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=180)
            assert hashes(folder/'native.log')==data['hashes'],case+' SDL/headless baseline differs'
            previous=None;deaths=[]
            for line in (folder/'native.ram').read_text().splitlines():
                row=line.split();level=int(row[6],16);lives=int(row[7],16)
                if previous and level==previous[0]==0 and lives<previous[1]:deaths.append(int(row[0]))
                previous=level,lives
            data['life_loss_frames']=deaths
        return case,mode,data
    results={}
    cases=['l00_idle','l00_right','l00_random','d_00_r7007']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(run,(case,mode)) for case in cases for mode in ('snes','md')]
        for future in concurrent.futures.as_completed(futures):
            case,mode,data=future.result();results.setdefault(case,{})[mode]=data
    failures=[]
    for case,runs in results.items():
        assert len(runs['md']['hashes'])==2 and runs['snes']['hashes']==runs['md']['hashes'],case+' artwork changed gameplay'
        # Native stage entry consumes the initial life at frame 591. Require a
        # later loss too, rather than mistaking that initialization for a death.
        if case=='d_00_r7007':assert len(runs['snes']['life_loss_frames'])>1,'death route did not exercise a later life loss'
        coverage=runs['md']['coverage']
        missing=coverage['missing_poses'] or coverage['missing_npc_poses']
        if missing:failures.append(case)
        print(case,'guest state identical; missing art:',coverage['missing_poses'],coverage['missing_npc_poses'],flush=True)
    (dest/'report.json').write_text(json.dumps({'result':'FAIL' if failures else 'PASS','runs':results},indent=2)+'\n')
    assert not failures,'broader first-level inputs encountered unmapped art: '+', '.join(failures)

if __name__=='__main__':main()

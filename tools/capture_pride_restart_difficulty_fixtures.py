"""Create genuine difficulty settings through ordinary Options/new-game inputs."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_soft_tree import latest
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-restart-difficulty24');args=parser.parse_args()
    base=ROOT/args.player;bound(base/'build-report.json')
    source=ROOT/'build/pride-title-navigation23/verification/report.json';old=bound(source)
    out=ROOT/'build/pride-restart-difficulty-fixtures';out.mkdir();checks={};commands={};observations={}
    sys.path.insert(0,str(ROOT/'engine/tools/re'));import make_level_tape as mlt
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(nav,difficulty,presses,expected,lle=False):
        label=nav+'-'+difficulty+('-lle' if lle else '');folder=out/label;folder.mkdir()
        steps=mlt.BOOT_TO_OPTIONS+['A','wait 30']*presses+['Start','wait 60',('wait 6' if nav=='md' else 'Up'),'wait 20','Start']
        tape=folder/'ordinary.tape';data=mlt.build(steps);data+= [0]*max(0,2200-len(data))
        tape.write_bytes(struct.pack('<'+'H'*len(data),*data))
        profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\ngameplay.levels.pride_lands.final_life = md\ngameplay.menus.title_navigation = '+nav+'\n')
        cmd=old['commands']['256-idle'].copy();cmd[0]=str(base/'player.exe')
        if '--load' in cmd:i=cmd.index('--load');del cmd[i:i+2]
        if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--input',tape),('--frames',2000),('--config',out/'host.ini'),('--resource-profile',profile),
                           ('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--save-at','2000',str(folder/'saved.state')]
        if lle:cmd.append('--lle')
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl')),
            stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        row=latest(folder/'tree.jsonl');commands[label]=cmd;observations[label]=row
        checks[label+'_exit']=r.returncode==0
        checks[label+'_pride']=row['level']==0 and row['descriptor']==0xc00387
        checks[label+'_difficulty']=row['difficulty']==expected
        checks[label+'_starting_budget']=row['lives']=={0:8,1:2,2:0}[expected] and row['health']==4
        checks[label+'_save_exists']=(folder/'saved.state').exists()
        print(label,r.returncode,{k:row[k] for k in ('difficulty','lives','health','descriptor')},flush=True)
        return folder
    for nav in ('snes','md'):
        for name,presses,value in [('easy',2,0),('normal',0,1),('difficult',1,2)]:
            normal=run(nav,name,presses,value)
            if nav=='md' and name=='difficult':
                other=run(nav,name,presses,value,lle=True)
                checks['difficult_lle_guest']=hashes(other/'run.log')==hashes(normal/'run.log')
                checks['difficult_lle_client']=pixels(other/'window.png')==pixels(normal/'window.png')
                checks['difficult_lle_pcm']=pcm(other/'audio.wav')==pcm(normal/'audio.wav')
    paths=[Path(__file__),base/'build-report.json',source,ROOT/'engine/tools/re/make_level_tape.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                ordinary_inputs=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()

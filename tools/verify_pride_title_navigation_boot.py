"""Verify independent MD navigation on ordinary boot with native final-life rules."""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--player',default='build/pride-title-navigation21');args=parser.parse_args()
    base=ROOT/args.player;bound(base/'build-report.json')
    source=ROOT/'build/pride-title-ready18/verification/report.json';old=bound(source)
    out=base/'boot';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.menus.title_navigation = md\n')
    tape=out/'input.tape';data=bytearray(2401*2)
    for at,pad in [(2001,0x400),(2010,0x1000),(2200,0x1000),(2250,0x800),(2260,0x1000)]:struct.pack_into('<H',data,(at-1)*2,pad)
    tape.write_bytes(data)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(label,end,lle=False,load=None):
        folder=out/label;folder.mkdir();cmd=old['commands']['256-neutral'].copy();cmd[0]=str(base/'player.exe')
        for flag in ('--load','--input'):
            i=cmd.index(flag);del cmd[i:i+2]
        if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--frames',end),('--resource-profile',profile),('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--input',str(tape),'--save-at',str(end),str(folder/'saved.state')]
        if lle:cmd.append('--lle')
        if load:cmd+=['--load',str(load)]
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[label]=cmd;checks[label+'_exit']=r.returncode==0;print(label,r.returncode,flush=True);return folder
    def same(label,a,b,skip=0):
        checks[label+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    first=run('ordinary2000',2000);raw=(first/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
    checks['ordinary_v4']=struct.unpack_from('<I',raw,at+8)[0]==4
    checks['ordinary_no_final_episode']=struct.unpack_from('<I',raw,at+100)[0]==0
    checks['ordinary_native_final_choice']='gameplay.levels.pride_lands.final_life' not in profile.read_text()
    normal=run('options2300',2300);lle=run('options2300-lle',2300,lle=True);same('ordinary_lle',lle,normal)
    cold=run('cold2000to2300',2300,load=first/'saved.state');same('ordinary_cold',cold,normal,len(pcm(first/'audio.wav')))
    raw=(normal/'saved.state').read_bytes();at=96+struct.unpack_from('<I',raw,20)[0]
    checks['options_navigation_owner_retired']=raw[at+180:at+192]==bytes(12)
    paths=[Path(__file__),source,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()

"""Verify maintained title readiness in compiled/LLE execution and cold processes."""
import hashlib
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
    base=ROOT/'build/pride-title-ready18';build=bound(base/'build-report.json')
    original=ROOT/'build/pride-title-readiness-probe3';probe=bound(original/'report.json')
    previous=ROOT/'build/pride-title-upload16';old=bound(previous/'verification/report.json')
    out=base/'verification';out.mkdir();checks={};commands={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    def run(width,label,end,template=None,lle=False,save=False,load=None,native_art=False):
        folder=out/f'{width}-{label}';folder.mkdir()
        cmd=(template or probe['commands'][f'{width}-neutral']).copy();cmd[0]=str(base/'player.exe')
        if '--lle' in cmd:cmd.remove('--lle')
        if lle:cmd.append('--lle')
        for flag,value in [('--frames',4444+end),('--config',out/'host.ini'),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if save:cmd+=['--save-at',str(4444+end),str(folder/'saved.state')]
        if load:cmd[cmd.index('--load')+1]=str(load)
        env=dict(clean)
        if not native_art:env['TLK_FINAL_MD_ART']='1'
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[folder.name]=cmd;checks[folder.name+'_exit']=r.returncode==0
        print(folder.name,r.returncode,flush=True);return folder,r.returncode
    def same(label,a,b,skip=0):
        checks[label+'_client']=(a/'window.png').exists() and pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_pcm']=(a/'audio.wav').exists() and pcm(a/'audio.wav')==pcm(b/'audio.wav')[skip:]
    def inner(path):
        raw=path.read_bytes();n,size=struct.unpack_from('<II',raw,20);return raw,96+n,size
    for width in (256,320):
        live={}
        for label,end in [('neutral',700),('start514',700),('start515',700),('held512to515',700),('released512to514',700),('menu515',515),('newgame1115',1115)]:
            template=probe['commands'][f'{width}-{label}']
            folder,code=run(width,label,end,template=template,save=label in ('neutral','newgame1115'));live[label]=folder
            same(f'{width}_{label}_prototype',folder,original/f'{width}-{label}')
            other,code=run(width,label+'-lle',end,template=template,lle=True)
            same(f'{width}_{label}_lle',other,folder)
        checkpoints={}
        for age in (367,511,512,513,514):
            folder,code=run(width,f'saved{age}',age,save=True);checkpoints[age]=folder
            if (folder/'saved.state').exists():
                raw,at,size=inner(folder/'saved.state')
                checks[f'{width}_{age}_record_v3']=struct.unpack_from('<I',raw,at+8)[0]==3
                checks[f'{width}_{age}_record_ready']=struct.unpack_from('<I',raw,at+172)[0]==4444+515
            for target in (515,700):
                cold,code=run(width,f'cold{age}to{target}',target,load=folder/'saved.state')
                same(f'{width}_cold{age}to{target}',cold,live['menu515' if target==515 else 'neutral'],len(pcm(folder/'audio.wav')))
        # The held edge survives a process boundary during constructor execution.
        held_before,code=run(width,'held-saved512',512,template=probe['commands'][f'{width}-held512to515'],save=True)
        held_cold,code=run(width,'held-cold512to700',700,template=probe['commands'][f'{width}-held512to515'],load=held_before/'saved.state')
        same(f'{width}_held_cold',held_cold,live['held512to515'],len(pcm(held_before/'audio.wav')))
        for label in ('neutral','newgame1115'):
            raw,at,size=inner(live[label]/'saved.state')
            checks[f'{width}_{label}_retired']=struct.unpack_from('<I',raw,at+100)[0]==0 and raw[at+172:at+180]==bytes(8)
        control,code=run(width,'native-control2600',2600,template=old['commands'][f'{width}-native-control2600'],native_art=True)
        same(f'{width}_native_control',control,previous/f'verification/{width}-native-control2600')
        alternate,code=run(width,'native-art',700,native_art=True)
        same(f'{width}_native_art',alternate,live['neutral'])
        # Source-policy changes reject old combined saves before any guest load.
        rejected,code=run(width,'old-save',700,load=previous/f'verification/{width}-367/saved.state')
        checks[f'{width}_old_save_rejects']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
        checks[rejected.name+'_exit']=code==8
        # Reseal both layers, so malformed intent is rejected semantically.
        raw,at,size=inner(checkpoints[512]/'saved.state');bad=bytearray(raw)
        struct.pack_into('<I',bad,at+176,65536);bad[at+48:at+80]=bytes(32)
        bad[at+48:at+80]=hashlib.sha256(bad[at:at+size]).digest()
        bad[64:96]=bytes(32);bad[64:96]=hashlib.sha256(bad).digest()
        malformed=out/f'{width}-malformed.state';malformed.write_bytes(bad)
        rejected,code=run(width,'malformed-save',700,load=malformed)
        checks[f'{width}_malformed_rejects']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
        checks[rejected.name+'_exit']=code==8
    paths=[Path(__file__),base/'build-report.json',original/'report.json',previous/'verification/report.json',
           ROOT/'engine/runner/tlk_final_scene_state.c',ROOT/'engine/runner/tlk_final_scene_state.h',
           ROOT/'engine/runner/pride/final/pride_final_title_ready.inc',ROOT/'engine/runner/pride/final/pride_final_save.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,binary_sha256=digest(base/'player.exe'),
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

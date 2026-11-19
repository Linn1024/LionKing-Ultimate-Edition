"""Verify continued gameplay, mode parity and missing-preparation rejection."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-final-menu-player9';source=base/'yes/report.json';data=bound(source)
    build=base/'build-report.json';bound(build)
    out=base/'handoff2';out.mkdir();commands={};checks={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    bank=ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'
    env=dict(clean,TLK_FINAL_MD_ART='1',TLK_CONTINUE_BANK_RECORD=str(bank))
    def run(width,label,age=600,load=None,enabled=True,lle=False,prepared=True,save=False):
        folder=out/f'{width}-{label}';folder.mkdir()
        cmd=data['commands'][f'{width}-124-197'].copy()
        for flag,value in [('--config',out/'host.ini'),('--frames',3894+age),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if load:cmd[cmd.index('--load')+1]=str(load)
        if lle:cmd+=['--lle']
        if save:cmd+=['--save-at',str(3894+age),str(folder/'saved.state')]
        actual=env.copy()
        if not enabled:actual.pop('TLK_FINAL_MD_ART')
        if not prepared:actual.pop('TLK_CONTINUE_BANK_RECORD')
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[f'{width}-{label}']=cmd;print(width,label,'exit',result.returncode,flush=True)
        return folder,result.returncode
    for width in (256,320):
        frames={}
        for age in (408,426,433,600):
            frames[age],code=run(width,str(age),age);checks[f'{width}-{age}_exit']=code==0
        native,code=run(width,'native',enabled=False,save=True);checks[f'{width}_native_exit']=code==0
        lle,code=run(width,'lle',lle=True);checks[f'{width}_lle_exit']=code==0
        saved=source.parent/f'{width}-124-333/saved.state'
        cold,code=run(width,'cold600',load=saved);checks[f'{width}_cold_exit']=code==0
        for label,folder in [('native',native),('lle',lle),('cold',cold)]:
            checks[f'{width}_{label}_guest']=hashes(folder/'run.log')==hashes(frames[600]/'run.log')
            checks[f'{width}_{label}_client']=pixels(folder/'window.png')==pixels(frames[600]/'window.png')
            expected=pcm(frames[600]/'audio.wav')
            if label=='cold':expected=expected[len(pcm(saved.parent/'audio.wav')):]
            checks[f'{width}_{label}_pcm']=pcm(folder/'audio.wav')==expected
        # A structurally valid native-style confirmed record cannot omit the
        # installed-art counter and silently derive it from changed guest RAM.
        raw=bytearray(saved.read_bytes());native_size,private_size=struct.unpack_from('<II',raw,20)
        start=96+native_size;record=bytearray(raw[start:start+private_size])
        struct.pack_into('<I',record,8,1);struct.pack_into('<I',record,168,0)
        record[48:80]=bytes(32);record[48:80]=hashlib.sha256(record).digest();raw[start:start+private_size]=record
        raw[64:96]=bytes(32);raw[64:96]=hashlib.sha256(raw).digest()
        bad=out/f'{width}-missing-credit.state';bad.write_bytes(raw)
        rejected,code=run(width,'missing-credit',load=bad)
        checks[f'{width}_missing_credit_rejects_before_guest']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
    missing,code=run(320,'missing-preparation',age=124,prepared=False)
    checks['missing_bank_no_fallback']=code==114 and b'no fallback is available' in (missing/'run.log').read_bytes()
    paths=[Path(__file__),source,build,bank,ROOT/'engine/runner/pride/final/pride_final_save.inc',ROOT/'engine/runner/pride/final/pride_final_runtime.inc']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()

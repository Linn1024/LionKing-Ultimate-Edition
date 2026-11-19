"""Check held and fresh jump presses at Continue's gameplay handoff."""
import csv
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-transition-edge-probe';out=base/'jump-edges';out.mkdir()
    reference=base/'capture/report.json';report=bound(reference)
    origin=ROOT/'build/pride-final-input-reference/prefatal.state';raw=origin.read_bytes();state=C.create_string_buffer(raw)
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    observations={};commands=[]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    try:
        for name,start,end in [('held',380,460),('fresh',433,436)]:
            folder=out/name;folder.mkdir();assert game.core.retro_unserialize(state,len(raw));md_first=None
            for age in range(461):
                game.step(128 if age==0 else (256 if age==124 or start<=age<=end else 0));game.samples.clear()
                word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                camera=word(0xcd36);player=word(camera+0x24) if 0x8000<=camera<0xffc8 else 0
                if age>=433 and word(0xccf6)==6 and 0x8000<=player<0xffc0 and word(player+10)<1255 and md_first is None:md_first=age
            png(folder/'md.png',*game.image)
            cmd=report['commands'][0].copy();cmd[cmd.index('--frames')+1]=str(3894+460)
            for flag,filename in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/filename)
            data=bytearray(Path(cmd[cmd.index('--input')+1]).read_bytes())
            for age in range(start,end+1):struct.pack_into('<H',data,(3894+age-1)*2,0x8000)
            tape=folder/'input.tape';tape.write_bytes(data);cmd[cmd.index('--input')+1]=str(tape)
            env=dict(clean,TLK_FINAL_SKIP='0',TLK_FINAL_LATE_SKIP='1',TLK_FINAL_FAST_ASSETS='1',
                TLK_FINAL_SCENE_PRESENT='1',TLK_CONTINUE_FAST_RELOAD='1',TLK_CONTINUE_BANK_APPLY='1',
                TLK_CONTINUE_BANK_DIR=str(folder),TLK_CONTINUE_BANK_RECORD=str(ROOT/'build/pride-continue-bank-ready-probe/capture/boot/bank.record'),
                TLK_FINAL_SKIP_LOG=str(folder/'points.csv'),TLK_CONTINUE_TRANSITION='1',
                TLK_CONTINUE_TRANSITION_LOG=str(folder/'transition.csv'))
            with (folder/'run.log').open('wb') as log:
                subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,
                    creationflags=subprocess.CREATE_NO_WINDOW)
            rows=list(csv.DictReader((folder/'transition.csv').open()))
            native_first=next((int(r['field'])-3894 for r in rows if int(r['field'])-3894>=433 and int(r['y'])<1255),None)
            observations[name]=dict(original_first_jump=md_first,prototype_first_jump=native_first)
            commands.append(cmd);print(name,observations[name],flush=True)
    finally:game.close()
    checks={name+'/jump_onset':r['original_first_jump']==r['prototype_first_jump'] for name,r in observations.items()}
    paths=[Path(__file__),reference,origin]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,flush=True);assert all(checks.values()),checks


if __name__=='__main__':main()

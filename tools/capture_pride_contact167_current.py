"""Fresh current139 rolling/contact captures; no historical checkpoints or headless substitution."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from pride_movement_audit import ROLL_CONTACT_VARIANTS,raw_slots
base=ROOT/'build/pride-hyena-entrance139';bp=base/'build-report.json';b=bound(bp)
observer=ROOT/'build/pride-contact166-observer';op=observer/'build-report.json';bound(op)
reference=base/'boundary159/report.json';ref=bound(reference);assert ref['result']=='PASS'
out=ROOT/'build/pride-contact167-current';out.mkdir();checks={};commands={}
profile_source=ROOT/'build/pride-hitbox-verification/both/native.ini'
profile=out/'resources.ini';profile.write_bytes(profile_source.read_bytes())
normal=ROOT/'engine/tapes/allbugsF.read.tape';raw=normal.read_bytes();words=struct.unpack('<'+'H'*(len(raw)//2),raw)
prefix=out/'ordinary-boot.polled.tape';prefix.write_bytes(raw[:words.index(0x100)*2])
pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
def run(name,exe,frames,tape,polled=False,load=None,save=None,first=2457):
    folder=out/name;folder.mkdir();cmd=ref['commands']['native'].copy();cmd[0]=str(exe)
    for flag in ('--input-polled','--lle'):
        if flag in cmd:
            i=cmd.index(flag);del cmd[i:i+(2 if flag=='--input-polled' else 1)]
    cmd+=['--input-polled' if polled else '--input',str(tape)]
    cmd[cmd.index('--frames')+1]=str(frames);cmd[cmd.index('--hash-at')+1]=','.join(map(str,range(1,frames+1)))
    (folder/'host.ini').write_text('opengl = 0\nscale = 2\n');(folder/'resources.ini').write_bytes(profile.read_bytes())
    for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
    if load:cmd+=['--load',str(load)]
    if save:cmd+=['--save-at',str(frames),str(save)]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['SDL_VIDEODRIVER']='dummy'
    if exe.parent==observer:env.update(TLK_CONTACT_RAM166=str(folder/'samples.bin'),TLK_CONTACT_FIRST166=str(first))
    with (folder/'run.log').open('wb') as f:rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    assert rc==0,(name,rc)
    commands[name]=cmd;print(name,'exit0',flush=True);return folder
seed=out/'current.state'
control=run('seed-production',base/'player.exe',2456,prefix,True,save=seed)
pilot=run('seed-observer',observer/'player.exe',2456,prefix,True,first=2456)
checks['seed_all2456_guest_fields_neutral']=len(hashes(control))==2456 and hashes(control)==hashes(pilot)
checks['seed_whole_pcm_neutral']=digest(control/'audio.wav')==digest(pilot/'audio.wav')
assert all(checks.values()),checks
def samples(path):
    with path.open('rb') as f:
        while header:=f.read(16):
            magic,field,pad,size=struct.unpack('<4I',header);assert magic==0x4b4c5443 and size==0x20000
            ram=f.read(size);assert len(ram)==size
            yield field,pad,ram
cases={}
for name,pads in ROLL_CONTACT_VARIANTS.items():
    tape=out/(name+'.tape');tape.write_bytes(struct.pack('<'+'H'*(2456+len(pads)),*([0]*2456+pads)))
    folder=run(name,observer/'player.exe',2456+len(pads),tape,load=seed)
    rows=[]
    for n,(field,pad,ram) in enumerate(samples(folder/'samples.bin')):
        assert field==2457+n and pad==pads[n],(name,n,field,pad,pads[n])
        w=lambda at:struct.unpack_from('<H',ram,at)[0];assert w(0x1ff9e)==0
        draw=w(0xb21f);assert 0x8000<=draw<0xffe8
        rows.append(dict(frame=n,pad=pad,x=w(0xb21b),y=w(0xb21d),health=w(0x2004),roar=w(0x2002),roar_active=w(0xa698),words=list(struct.unpack_from('<64H',ram,0xb213)),pose=int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff,draw_words=list(struct.unpack_from('<11H',ram,draw)),raw_slots=raw_slots(w,'snes'),camera_words=[w(0xb293+i*2) for i in range(64)],spawn_bounds=[w(at) for at in (0xb1ff,0xb201,0xb203,0xb205)]))
    assert len(rows)==len(pads);cases[name]=rows
    print(name,'captured',len(rows),'first',rows[0]['x'],rows[0]['y'],flush=True)
(out/'snes.json').write_text(json.dumps(dict(cases=cases,settle_frames=256,ordinary_native_input_boot=True,md_start_selected=True,md_camera_selected=True,md_activation_selected=True,md_reactivation_selected=True,md_body_bounds_selected='both',player_sha256=b['binary_sha256'],current_build_seed_sha256=digest(seed),scope='Current139 SDL path with fresh2456 checkpoint and ordinary boot, historical protocol inputs, exact pads/frame observations. Raw actor slots are not active-list proof; original MD and selected mode/production per-branch neutrality still separate.'),indent=2)+'\n')
checks['all1238_fields_captured']=sum(map(len,cases.values()))==1238
paths=[Path(__file__),bp,op,reference,profile_source,normal,ROOT/'tools/pride_movement_audit.py']
(out/'report.json').write_text(json.dumps(dict(result='CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,current_build_saves_only=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('CAPTURED',checks,flush=True)

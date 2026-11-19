"""Check Game Over input-mode parity, policy identity and the next new game."""
import json
import hashlib
import os
import re
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
    base=ROOT/'build/pride-game-over13';source=base/'verification2/report.json';data=bound(source)
    older=ROOT/'build/pride-final-native-player11/game-over/report.json';bound(older)
    out=base/'lifecycle2';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    def run(width,label,age,template,load=None,tape=None,lle=False,save=False,native_control=False):
        folder=out/f'{width}-{label}';folder.mkdir();cmd=data['commands'][template].copy()
        for flag,value in [('--config',out/'host.ini'),('--frames',4444+age),('--dump-window',folder/'window.png'),
            ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        if '--save-at' in cmd:
            at=cmd.index('--save-at');del cmd[at:at+3]
        if load:cmd[cmd.index('--load')+1]=str(load)
        if tape:cmd[cmd.index('--input')+1]=str(tape)
        if native_control:
            profile=out/f'{width}-native.ini';profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.health_death = md\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n')
            cmd[cmd.index('--resource-profile')+1]=str(profile)
        if lle:cmd+=['--lle']
        if save:cmd+=['--save-at',str(4444+age),str(folder/'saved.state')]
        actual={k:v for k,v in env.items() if k!='TLK_FINAL_MD_ART'} if native_control else env
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=actual,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        commands[f'{width}-{label}']=cmd;print(width,label,'exit',r.returncode,flush=True);return folder,r.returncode
    for width in (256,320):
        lle,code=run(width,'input-lle130',130,f'{width}-a124-130',lle=True)
        original=source.parent/f'{width}-a124-130'
        checks[f'{width}_input_lle_exit']=code==0
        checks[f'{width}_input_lle_client']=pixels(lle/'window.png')==pixels(original/'window.png')
        checks[f'{width}_input_lle_guest']=hashes(lle/'run.log')==hashes(original/'run.log')
        checks[f'{width}_input_lle_pcm']=pcm(lle/'audio.wav')==pcm(original/'audio.wav')
        raw=bytearray((source.parent/'none.tape').read_bytes())
        raw.extend(bytes(8200*2-len(raw)))
        for age in range(1400,1404):struct.pack_into('<H',raw,(4444+age-1)*2,0x1000)
        tape=out/f'{width}-start1400.tape';tape.write_bytes(raw)
        live,code=run(width,'new-game2000',2000,f'{width}-none-title700',tape=tape,save=True)
        checks[f'{width}_next_game_exit']=code==0
        scene=json.loads((live/'scene.json').read_text());guest=scene['latched_gameplay']
        checks[f'{width}_next_game_is_pride']=scene['level']==0 and guest['descriptor']==0x387 and guest['health']>0
        saved=(live/'saved.state').read_bytes();at=96+struct.unpack_from('<I',saved,20)[0]
        checks[f'{width}_next_game_owner_retired']=struct.unpack_from('<I',saved,at+100)[0]==0 and struct.unpack_from('<I',saved,at+112)[0]==0
        previous=source.parent/f'{width}-none-330'
        cold,code=run(width,'cold-new-game2000',2000,f'{width}-none-title700',load=previous/'saved.state',tape=tape)
        checks[f'{width}_cold_next_game_exit']=code==0
        checks[f'{width}_cold_next_game_client']=pixels(cold/'window.png')==pixels(live/'window.png')
        checks[f'{width}_cold_next_game_guest']=hashes(cold/'run.log')==hashes(live/'run.log')
        checks[f'{width}_cold_next_game_pcm']=pcm(cold/'audio.wav')==pcm(live/'audio.wav')[len(pcm(previous/'audio.wav')):]
        # Run the unchanged native title path with its later Start as a control.
        raw=bytearray((source.parent/'none.tape').read_bytes());raw.extend(bytes(8200*2-len(raw)))
        for age in range(2000,2004):struct.pack_into('<H',raw,(4444+age-1)*2,0x1000)
        control_tape=out/f'{width}-native-start2000.tape';control_tape.write_bytes(raw)
        control,code=run(width,'native-control2600',2600,f'{width}-none-title700',tape=control_tape,save=True,native_control=True)
        checks[f'{width}_native_control_exit']=code==0
        reference=json.loads((control/'scene.json').read_text())['latched_gameplay']
        checks[f'{width}_new_game_counters_match_native']=all(guest[key]==reference[key] for key in ('health','lives','checkpoint','player'))
        # Locate this pinned32-bit backend's WRAM and verify its hash before
        # reading difficulty/mode. Never infer a new game from a screenshot.
        def backend_ram(folder):
            record=(folder/'saved.state').read_bytes();at=record.find(b'TLKSTAT1');assert at>=0
            length=struct.unpack_from('<Q',record,at+24)[0];blob=record[at+36:at+36+length]
            assert blob[:8]==b'SLTR\x0a\x00\x00\x00'
            residue=blob.find(b'RBRS');assert residue>=0
            end=residue-4-struct.unpack_from('<I',blob,residue-4)[0]
            ram=blob[end-70-0x20000:end-70]
            expected=re.search(r'wram_sha256=([0-9a-f]+)',(folder/'run.log').read_text()).group(1)
            assert hashlib.sha256(ram).hexdigest()==expected
            return ram
        live_ram=backend_ram(live);control_ram=backend_ram(control)
        checks[f'{width}_ordinary_mode_retained']=struct.unpack_from('<H',live_ram,0x1ff9c)[0]==struct.unpack_from('<H',control_ram,0x1ff9c)[0]==0
        checks[f'{width}_hard_difficulty_retained']=struct.unpack_from('<H',live_ram,0x1ff92)[0]==struct.unpack_from('<H',control_ram,0x1ff92)[0]==2
        checks[f'{width}_hard_spares_retained']=guest['lives']==reference['lives']==0
        observations[str(width)]=dict(gameplay=guest,native_control=reference,difficulty=2,mode=0,
            early_start700_unmet_report='build/pride-game-over13/lifecycle/report.json')
        old=older.parent/f'{width}-140/saved.state'
        rejected,code=run(width,'old-policy-save',180,f'{width}-none-title700',load=old)
        checks[f'{width}_old_policy_rejects_before_guest']=code==8 and b'loaded_state=' not in (rejected/'run.log').read_bytes()
    paths=[Path(__file__),source,older]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()

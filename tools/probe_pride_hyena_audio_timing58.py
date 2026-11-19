"""Isolate audio selections that change the captured Difficult encounter state."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    source=ROOT/'build/pride-hyena-mixtures58/report.json';prior=bound(source)
    out=ROOT/'build/pride-hyena-audio-timing58';out.mkdir();commands={};observations={};checks={}
    template=prior['commands']['hard-art-aot'].copy();i=template.index('--hash-at');del template[i:i+2]
    for flag in ('--dump-window','--dump-scene'):
        i=template.index(flag);del template[i:i+2]
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};clean['SDL_VIDEODRIVER']='dummy'
    referencepath=ROOT/'build/pride-hyena-recovery/snes/hard/hl_wram_4000.bin';reference=referencepath.read_bytes()
    def info(r):
        word=lambda p:struct.unpack_from('<H',r,p)[0]
        ptr=lambda p:word(p)|r[p+2]<<16
        return dict(player_x=word(0xb21b),player_y=word(0xb21d),player_health=word(0x2004),player_action=ptr(0xb243),
            player_vy=struct.unpack_from('<i',r,0xb213+0x3c)[0],boss_x=word(0xba13+8),boss_y=word(0xba13+10),
            boss_health=word(0xba13+0x2a),boss_action=ptr(0xba13+0x30),boss_timer=word(0xba13+0x2c))
    definitions={
        'music':['audio.music.pride_lands'],
        'bounce':['audio.effects.simba.bounce'],
        'simba-hurt':['audio.effects.simba.hurt'],
        'hyena-hurt':['audio.effects.world.hyena_hurt'],
        'hyena-other':['audio.effects.world.hyena_'+part for part in ('pant','jump','taunt')]}
    def run(name):
        folder=out/name;folder.mkdir();cmd=template.copy();cmd[cmd.index('--frames')+1]='4000'
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()+''.join('\n'+key+' = md' for key in definitions[name])+'\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        cmd+=['--save-at','4000',str(folder/'current.state')];commands[name]=cmd
        with (folder/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=360,creationflags=subprocess.CREATE_NO_WINDOW)
        expected=re.findall(r'^wram_sha256=([a-f0-9]+)',(folder/'run.log').read_text(),re.M)[-1]
        state=(folder/'current.state').read_bytes();assert state[:8]==b'TLKSTAT1' and struct.unpack_from('<I',state,8)[0]==4
        size=struct.unpack_from('<Q',state,24)[0];blob=state[36:36+size];ram=blob[166265:166265+0x20000]
        assert hashlib.sha256(ram).hexdigest()==expected
        (folder/'verified-wram.bin').write_bytes(ram)
        observed=info(ram);baseline=info(reference)
        observations[name]=dict(selected_audio=definitions[name],observed=observed,
            gameplay_differences={k:dict(reference=baseline[k],observed=v) for k,v in observed.items() if v!=baseline[k]},
            player_record_changed_bytes=[i for i in range(128) if ram[0xb213+i]!=reference[0xb213+i]],
            boss_record_changed_bytes=[i for i in range(128) if ram[0xba13+i]!=reference[0xba13+i]],
            entire_wram_equals_original=ram==reference)
        checks[name+'_hash_verified_current_snapshot']=True
        print(name,observations[name]['gameplay_differences'],flush=True)
    with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(run,definitions))
    paths=[Path(__file__),source,referencepath]
    report=dict(result='OBSERVED',checks=checks,commands=commands,observations=observations,
                original_reference=info(reference),exact_timing_cause_or_runtime_fix_established=False,
                guest_or_rom_edits=False,public_preview_unchanged=True,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()

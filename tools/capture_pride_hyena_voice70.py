"""Observe natural hyena voice timing; no game code or actor state changes."""
import argparse
import csv
import ctypes as C
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',choices=('snes','md'),required=True)
    ap.add_argument('--out',required=True);args=ap.parse_args();out=ROOT/args.out;out.mkdir()
    shutil.copy2(__file__,out/Path(__file__).name)
    paths=[Path(__file__)];checks={};commands=[]
    if args.source=='md':
        from md_lab import MdLab
        source=ROOT/'tools/md_hyena_voice_trace70.c';library=out/'trace.dll'
        cmd=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc',str(source),'-o',str(library)]
        subprocess.run(cmd,check=True);commands.append(cmd)
        origin=ROOT/'build/pride-md-hyena-hard-repeat-plan/report.json';bound(origin)
        inputs=origin.parent/'selected-inputs.json';pads=json.loads(inputs.read_text())
        game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513)
        trace=C.CDLL(str(library));trace.hyena_voice_init.argtypes=[C.c_void_p,C.c_char_p]
        assert trace.hyena_voice_init(game.core._handle,str(out/'calls.csv').encode())
        reference_report=ROOT/'build/pride-hyena-recovery/md/report.json';bound(reference_report)
        reference=reference_report.parent/'hard/frames.json'
        expected={r['field']:r for r in json.loads(reference.read_text())};matches=[]
        try:
            for field,pad in enumerate(pads,1):
                trace.hyena_voice_field(field);game.step(pad);game.samples.clear()
                if field in expected:
                    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                    actor=0x9a4e;draw=word(actor+12)
                    row=dict(field=field,health=word(actor+0x2a),cycle=word(actor+0x28),timer=word(actor+0x2c),
                        tag=word(actor+0x2e),action=word(actor+0x30)<<16|word(actor+0x32),
                        pose=(word(draw+10)<<16|word(draw+12))&0xffffff,x=word(actor+8),y=word(actor+10),
                        facing=word(actor+0x20),player_health=word(0xccf6),lives=word(0xccee))
                    matches.append((field,row==expected[field]))
        finally:trace.hyena_voice_close();game.close()
        rows=list(csv.DictReader((out/'calls.csv').open()))
        entries=[r for r in rows if r['pc']=='19b6d6' and r['action']!='19b6d6']
        voices=[r for r in rows if r['pc']=='002210']
        checks['ordinary_action_entries_observed']=bool(entries)
        checks['one_pcm4_per_entry_same_field']=len(voices)==len(entries) and all(a['field']==b['field'] and a['actor']==b['actor'] and b['argument']=='4' for a,b in zip(entries,voices))
        checks['all_original_captured_actor_fields_preserved']=len(matches)==len(expected) and all(v for _,v in matches)
        observations=dict(entries=entries,voices=voices,reference_samples=len(matches),reference_mismatches=[f for f,v in matches if not v])
        paths.extend([source,ROOT/'tools/md_lab.py',origin,inputs,reference_report,reference,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md'])
    else:
        prior_path=ROOT/'build/pride-music-output65/hyena-effects/report.json';prior=bound(prior_path)
        cmd=prior['commands']['native'].copy();cmd[0]=str(ROOT/'dist/installed-preview65/LionKing.exe')
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini')]:
            old=Path(cmd[cmd.index(flag)+1]);shutil.copy2(old,out/file);cmd[cmd.index(flag)+1]=str(out/file)
        for flag,file in [('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(out/file)
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(out/'events.csv'))
        with (out/'run.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        commands.append(cmd);reference=prior_path.parent/'native'
        pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
        actual=re.findall(pattern,(out/'run.log').read_text());expected=re.findall(pattern,(reference/'run.log').read_text())
        rows=list(csv.DictReader((out/'events.csv').open()))
        voices=[r for r in rows if r['event']=='0020']
        checks['all4600_native_picture_and_full_wram_fields_preserved']=len(actual)==4600 and actual==expected
        checks['whole_native_pcm_preserved']=digest(out/'audio.wav')==digest(reference/'audio.wav')
        checks['native_voice_events_observed']=bool(voices)
        observations=dict(voices=voices,fields=len(actual))
        paths.extend([prior_path,Path(cmd[0]),reference/'run.log',reference/'audio.wav',ROOT/'build/pride-hyena-recovery/snes/hard/frames.json',ROOT/'engine/runner/tlk_audio.c'])
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',source=args.source,checks=checks,observations=observations,commands=commands,
                read_only_observation=True,production_modified=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],args.source,checks,flush=True)


if __name__=='__main__':main()

"""Capture ordinary Normal/Difficult repeated-hit fights through owned boss death.

Every retained row belongs to Pride and the known hyena slot. Record reuse after
the death is excluded. Planning checkpoints are not loaded in these captures.
"""
import argparse
import ctypes as C
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT, MdLab, png
from capture_pride_difficulty_start import digest
from summarize_pride_practice import bound


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=('snes','md'),required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    paths=[Path(__file__),ROOT/'tools/md_lab.py'];cases={}
    for name in ('normal','hard'):
        folder=out/name;folder.mkdir();rows=[]
        if args.source=='snes':
            plan=ROOT/('build/pride-hyena-normal-repeat-plan' if name=='normal' else 'build/pride-native-hyena-hard-repeat-plan')
            report_path=plan/'report.json';plan_report=json.loads(report_path.read_text())
            if name=='normal':
                tape=plan/'best.polled.tape';end=4320
                assert digest(tape)==plan_report['selected_tape_sha256']
            else:
                bound(report_path);tape=plan/'selected.polled.tape';end=plan_report['frames']
            exe=ROOT/'engine/build-win/tlk_headless.exe';profile=ROOT/f'build/pride-hyena-hits/snes/{name}/resources.ini'
            paths.extend([report_path,tape,exe,profile,ROOT/'Lion King, The (USA).sfc'])
            env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
            env.update(TLK_WRAM_DUMP=','.join(map(str,range(3950,end+1))),TLK_WRAM_DIR=str(folder))
            cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,
                '--input-polled',tape,'--frames',end,'--dump-png',folder/'end.png']
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
            for field in range(3950,end+1):
                ram=(folder/f'hl_wram_{field}.bin').read_bytes();word=lambda a:struct.unpack_from('<H',ram,a)[0]
                actor=0xba13;draw=word(actor+12)
                assert word(0x1ff9e)==0 and word(0xdf)==0x80d
                rows.append(dict(field=field,health=word(actor+0x2a),cycle=word(actor+0x28),timer=word(actor+0x2c),
                    tag=word(actor+0x2e),action=word(actor+0x30)|word(actor+0x32)<<16,
                    pose=int.from_bytes(ram[draw+10:draw+13],'little'),x=word(actor+8),y=word(actor+10),
                    facing=word(actor+0x20),player_health=word(0x2004),lives=word(0x1ffaa)))
        else:
            plan=ROOT/f'build/pride-md-hyena-{name}-repeat-plan';report_path=plan/'report.json';bound(report_path)
            tape=plan/'selected-inputs.json';pads=json.loads(tape.read_text())
            paths.extend([report_path,tape,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md'])
            game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
            for port in (0,1):game.core.retro_set_controller_port_device(port,513)
            previous=None
            try:
                for field,pad in enumerate(pads,1):
                    game.step(pad);game.samples.clear()
                    if field<3950:continue
                    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                    actor=0x9a4e;draw=word(actor+12)
                    assert word(0xccce)==1
                    row=dict(field=field,health=word(actor+0x2a),cycle=word(actor+0x28),timer=word(actor+0x2c),
                        tag=word(actor+0x2e),action=word(actor+0x30)<<16|word(actor+0x32),
                        pose=(word(draw+10)<<16|word(draw+12))&0xffffff,x=word(actor+8),y=word(actor+10),
                        facing=word(actor+0x20),player_health=word(0xccf6),lives=word(0xccee))
                    rows.append(row)
                    if previous and row['action']!=previous['action']:
                        png(folder/f'action-{field}.png',*game.image)
                    previous=row
                png(folder/'end.png',*game.image)
            finally:game.close()
        changes=[r for i,r in enumerate(rows) if i==0 or r['health']!=rows[i-1]['health']]
        (folder/'frames.json').write_text(json.dumps(rows,indent=2)+'\n')
        cases[name]=dict(changes=changes,first=rows[0],final=rows[-1],samples=len(rows))
        print(args.source,name,[(r['field'],r['health'],hex(r['action'])) for r in changes],flush=True)
    result=dict(result='CAPTURED',scope=__doc__,source=args.source,cases=cases,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()

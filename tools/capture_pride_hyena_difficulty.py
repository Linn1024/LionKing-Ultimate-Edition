"""Observe Pride hyena records on ordinary three-difficulty routes.

Only Options button presses change, plus one native Difficult neutral poll before
movement to retain the route's jump phase. Each source retains its own gameplay
route, releasing controls after native source poll3528/MD field3900. Raw records
are not independent active-list proof; reviewed hyena poses identify samples.
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


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',choices=('snes','md'),required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--fight',action='store_true',help='Continue the original gameplay inputs through4500 instead of stopping before the fight')
    args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    catalog=ROOT/'tools/pride_npc_pairs.json'
    pairs=json.loads(catalog.read_text())['pairs']
    poses={int(r[args.source],16) for r in pairs if r['role']=='hyena'}
    paths=[Path(__file__),ROOT/'tools/md_lab.py',catalog]
    cases={}
    for name in ('easy','normal','hard'):
        folder=out/name;folder.mkdir();rows=[]
        if args.source=='snes':
            source=ROOT/'engine/tapes/allbugsF.read.tape';exe=ROOT/'engine/build-win/tlk_headless.exe'
            raw=source.read_bytes();words=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
            # Removing menu B/A presses preserves every subsequent gameplay pad.
            for index in range(466,502):
                if name!='easy' and words[index] in (0x80,0x8000) and not (name=='hard' and index==479):
                    words[index]=0
            # The recorded easy3850 boundary consumed3528 controller polls.
            prefix=words if args.fight else words[:3528]
            if name=='hard':prefix=prefix[:638]+[0]+prefix[638:]
            tape=folder/'ordinary.polled.tape'
            tape.write_bytes(struct.pack('<'+'H'*len(prefix),*prefix)+bytes(5000))
            profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\n')
            env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
            fields=list(range(3000,4501,8))
            env.update(TLK_WATCH='0xba3d',TLK_WRAM_DUMP=','.join(map(str,fields)),TLK_WRAM_DIR=str(folder))
            cmd=[exe,'--rom',ROOT/'Lion King, The (USA).sfc','--resource-profile',profile,
                 '--input-polled',tape,'--frames',4500,'--ram-log',folder/'ram.log']
            with (folder/'run.log').open('wb') as log:
                subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
            for field in fields:
                ram=(folder/f'hl_wram_{field}.bin').read_bytes()
                word=lambda a:struct.unpack_from('<H',ram,a)[0]
                actor=0xba13;draw=word(actor+12)
                pose=int.from_bytes(ram[draw+10:draw+13],'little') if 0x8000<=draw<=0xffe8 else 0
                if pose not in poses:continue
                rows.append(dict(field=field,actor=actor,pose=pose,action=word(actor+0x30)|word(actor+0x32)<<16,
                    candidate_health=word(actor+0x2a),cycle=word(actor+0x28),x=word(actor+8),y=word(actor+10),
                    player_health=word(0x2004),difficulty=word(0x1ff92),level=word(0x1ff9e),descriptor=word(0xdf)))
            paths.extend([source,exe,ROOT/'Lion King, The (USA).sfc'])
        else:
            source=ROOT/'build/md-next-levels-replay/frames.json';inputs=json.loads(source.read_text())
            game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
            for port in (0,1):game.core.retro_set_controller_port_device(port,513)
            pads=[]
            try:
                for field in range(1,4501):
                    pad=inputs[field-1]['pad'] if field<=(4500 if args.fight else 3900) else 0
                    if field==1000:pad={'easy':64,'normal':0,'hard':128}[name]
                    pads.append(pad);game.step(pad);game.samples.clear()
                    if field<3000:continue
                    word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
                    for actor in range(0x944e,0xa3ce,0x80):
                        draw=word(actor+12)
                        pose=(word(draw+10)<<16|word(draw+12))&0xffffff if 0x8000<=draw<=0xffe8 else 0
                        if pose not in poses:continue
                        rows.append(dict(field=field,actor=actor,pose=pose,action=word(actor+0x30)<<16|word(actor+0x32),
                            candidate_health=word(actor+0x2a),cycle=word(actor+0x28),x=word(actor+8),y=word(actor+10),
                            player_health=word(0xccf6),level=word(0xccce)))
                    if field in (3800,4100):
                        png(folder/f'{field}.png',*game.image)
                        (folder/f'{field}-wram.bin').write_bytes(bytes(game.work_ram))
            finally:game.close()
            (folder/'inputs.json').write_text(json.dumps(pads)+'\n')
            paths.extend([source,ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md'])
        (folder/'frames.json').write_text(json.dumps(rows,indent=2)+'\n')
        changes=[r for i,r in enumerate(rows) if i==0 or r['candidate_health']!=rows[i-1]['candidate_health']]
        cases[name]=dict(first=rows[0] if rows else None,changes=changes,samples=len(rows))
        print(args.source,name,[(r['field'],r['candidate_health']) for r in changes],flush=True)
    result=dict(result='CAPTURED',scope=__doc__,source=args.source,continued_original_fight=args.fight,cases=cases,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()

"""Observe original checkpoint revival artwork at completed video fields.

Use the same ordinary controller route as the retained nine-death reference.
No loaded states or guest writes. Raw ROM/WRAM-derived output remains in build/.
Run with the pinned embedded32 Python and original MD core.
"""
import hashlib
import json
import ctypes as C
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-revival-art';out.mkdir(exist_ok=True)
    report=out/'reference.json';report.write_text('{"result":"RUNNING"}\n')
    source=ROOT/'build/md-next-levels-replay'
    inputs=json.loads((source/'frames.json').read_text())
    previous_path=ROOT/'build/pride-revival-reference/report.json'
    previous=json.loads(previous_path.read_text());assert previous['result']=='PASS'
    core=ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'
    assert previous['source_sha256']['core']==digest(core)
    cases=[r for r in previous['cases'] if not r.get('final_life_skips_revival')]
    frames={f:(i,f-r['death']) for i,r in enumerate(cases) for f in range(r['death']+254,r['normal_play_jump']+1)}
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    rows=[];checks=0;pictures=[]
    word=lambda at:game.work_ram[at&65535]|game.work_ram[(at+1)&65535]<<8
    longword=lambda at:((word(at)<<16)|word(at+2))&0xffffff
    try:
        for frame in range(1,15301):
            game.step(inputs[frame-1]['pad'] if frame<=4000 else 128 if frame>5400 else 0)
            if frame<=4000 and frame%100==1:
                file=source/f'{frame:05d}-wram.bin'
                if file.exists():assert bytes(game.work_ram)==file.read_bytes();checks+=1
            if frame in (4800,5400):
                assert bytes(game.work_ram)==(ROOT/f'build/pride-health-death-original/{frame}-wram.bin').read_bytes()
                path=out/f'{frame}.png';png(path,*game.image)
                assert path.read_bytes()==(ROOT/f'build/pride-health-death-original/{frame}.png').read_bytes()
            if frame in frames:
                number,age=frames[frame];actor=word(0xcd48);draw=word(actor+12)
                rows.append({'case':number,'frame':frame,'age':age,'actor':actor,'draw':draw,
                    'pose':longword(draw+10),'animation':longword(actor+14),'cursor':longword(actor+18),
                    'timer_word':word(actor+26),'x':word(actor+8),'y':word(actor+10),
                    'health':word(0xccf6),'lives':word(0xccee),'cram':bytes(game.cram).hex()})
                if number==0 and age in (271,273,295,296,299,300,340,343,344,345):
                    path=out/f'age-{age}.png';png(path,*game.image)
                    pictures.append({'age':age,'sha256':digest(path)})
            if frame==14948:
                path=out/'game-over.png';png(path,*game.image)
                assert path.read_bytes()==(ROOT/'build/pride-game-over-original/game-over.png').read_bytes()
            game.samples.clear()
    finally:game.close()
    assert len(rows)==8*92
    # Ignore physical allocator addresses and absolute frame IDs when checking
    # repeated revival. The original art, timer and position must be identical.
    signatures=[]
    for number in range(8):
        signatures.append([{k:r[k] for k in ('age','pose','animation','cursor','timer_word','x','y','health','cram')}
                           for r in rows if r['case']==number and r['age']>=271])
    assert all(s==signatures[0] for s in signatures)
    fields=out/'fields.json';fields.write_text(json.dumps(rows,indent=2)+'\n')
    result={'result':'PASS','scope':__doc__,'checkpoint_revivals':8,'completed_video_fields':len(rows),
            'all_revivals_same_art_clock':True,'unchanged_prefix_wram_checks':checks,
            'unchanged_original_pictures':[4800,5400,14948],'pictures':pictures,
            'loaded_states':False,'guest_edits':False,'source_sha256':{'script':digest(Path(__file__)),
                'core':digest(core),'inputs':digest(source/'frames.json'),'revival_reference':digest(previous_path),
                'fields':digest(fields),'rom':digest(ROOT/'Lion King, The (World).md')}}
    report.write_text(json.dumps(result,indent=2)+'\n')
    print('Original checkpoint revival artwork:',len(rows),'completed fields, eight matching clocks PASS',flush=True)


if __name__=='__main__':main()

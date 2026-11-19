"""Capture original death fade/reload video fields without modifying the game.

Embedded32 Python; all input comes from the existing ordinary original route.
The earlier timeline and exact original checkpoint captures are the controls.
"""
import ctypes as C
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-death-presentation-md';out.mkdir(exist_ok=True)
    path=out/'report.json';path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    timeline=ROOT/'build/pride-death-timeline'
    contract=json.loads((timeline/'report.json').read_text())
    assert contract['result']=='STREAMS_EQUAL_STAGING_DIFFERENT_ADAPTER_OPEN'
    first=contract['md_deaths'][0];final=contract['md_deaths'][-1]
    source=ROOT/'build/md-next-levels-replay'
    inputs=json.loads((source/'frames.json').read_text())
    expected={r['frame']:r for r in json.loads((timeline/'md/samples.json').read_text())}
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    word=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
    rows=[];snapshots=[];checks=0
    pictures=set(range(first['death']-1,first['loop_start']+7))
    pictures.update((first['loop_end']-1,first['loop_end'],first['health_restored']-1,
                     first['health_restored'],first['health_restored']+1,5060))
    pictures.update(range(final['death']-1,final['death']+33,4))
    try:
        for frame in range(1,15301):
            game.step(inputs[frame-1]['pad'] if frame<=4000 else 128 if frame>5400 else 0)
            if frame<=4000 and frame%100==1:
                control=source/f'{frame:05d}-wram.bin'
                if control.exists():assert bytes(game.work_ram)==control.read_bytes();checks+=1
            if (first['death']-1<=frame<=5060) or (final['death']-1<=frame<=final['death']+100):
                # The camera's actor link changes during game-over setup;
                # the old global hero pointer is then no longer its owner.
                camera=word(0xcd36);actor=word(camera+36);draw=word(actor+12)
                row={'frame':frame,'health':word(0xccf6),'lives':word(0xccee),
                     'pose':(word(draw+10)<<16|word(draw+12))&0xffffff,
                     'xy':[word(actor+8),word(actor+10)],'camera':[word(0x880c),word(0x880e)],
                     'words':[word(actor+i*2) for i in range(64)]}
                assert all(row[k]==expected[frame][k] for k in row if k!='frame'),frame
                hero=word(0xcd48);hero_draw=word(hero+12)
                row.update({'camera_pointer':camera,'camera_actor':actor,'global_hero_pointer':word(0xcd48),
                            'global_hero':{'xy':[word(hero+8),word(hero+10)],
                                           'pose':(word(hero_draw+10)<<16|word(hero_draw+12))&0xffffff,
                                           'words':[word(hero+i*2) for i in range(64)]},
                            'cram':bytes(game.cram).hex(),'vdp_registers':bytes(game.reg).hex(),
                            'video_sha256':hashlib.sha256(game.image[0]).hexdigest(),
                            'video_geometry':list(game.image[1:])})
                rows.append(row)
            if frame in pictures:
                file=out/f'{frame}.png';png(file,*game.image)
                snapshots.append({'frame':frame,'sha256':digest(file)})
            if frame in (4800,5400):
                assert bytes(game.work_ram)==(ROOT/f'build/pride-health-death-original/{frame}-wram.bin').read_bytes()
                png(out/f'control-{frame}.png',*game.image)
                assert (out/f'control-{frame}.png').read_bytes()==(ROOT/f'build/pride-health-death-original/{frame}.png').read_bytes()
            if frame==14948:
                png(out/'game-over-control.png',*game.image)
                assert (out/'game-over-control.png').read_bytes()==(ROOT/'build/pride-game-over-original/game-over.png').read_bytes()
            game.samples.clear()
    finally:game.close()
    (out/'fields.json').write_text(json.dumps(rows,indent=2)+'\n')
    report={'result':'PASS','scope':__doc__,'sampled_video_fields':len(rows),'pictures':snapshots,
            'prefix_full_wram_checks':checks,'unchanged_lifecycle_actor_fields':True,
            'exact_control_wram_and_pictures':[4800,5400,14948],
            'loaded_states':False,'guest_edits':False,
            'source_sha256':{'script':digest(Path(__file__)),'timeline':digest(timeline/'report.json'),
                             'original_samples':digest(timeline/'md/samples.json'),'input':digest(source/'frames.json'),
                             'core':digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
                             'rom':digest(ROOT/'Lion King, The (World).md'),'fields':digest(out/'fields.json')}}
    path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD death fade/reload video and final-life skip captured; original controls unchanged PASS',flush=True)


if __name__=='__main__':main()

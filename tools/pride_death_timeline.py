"""Observe original Pride death animation/staging, separate from music choice.

Both references run from power-on with ordinary controller inputs and neutral
tails. No states or actor/ROM/RNG edits. MD uses embedded32 Python; native uses
the original LLE and compiled hosts with no MD ROM/choices. Art and timings are
reported separately; identical stream bytes are not a timing-equivalence claim.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from verify_windows import hashes


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def native(continuing=False,reuse=False):
    out=ROOT/('build/pride-death-timeline/native-continue' if continuing else 'build/pride-death-timeline/native');out.mkdir(parents=True,exist_ok=True)
    old=json.loads((out/'report.json').read_text()) if reuse else None
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/('build/pride-game-over-music/normal.tape' if continuing else 'build/pride-health-death-native/neutral-tail.polled.tape')
    if reuse:
        assert old['headless_sha256']==digest(ROOT/'engine/build-win/tlk_headless.exe') and old['input_sha256']==digest(tape)
    (out/'report.json').write_text(json.dumps({'result':'RUNNING','scope':__doc__})+'\n')
    frames=list(range(4400,4901)) if not continuing else [*range(1668,2045),*range(2816,3193),*range(3878,4351)]
    modes={};records={}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env['TLK_WRAM_DIR']=str(folder)
        command=[ROOT/'engine/build-win/tlk_headless.exe','--rom',ROOT/'Lion King, The (USA).sfc',
                 '--resource-profile',profile,'--input' if continuing else '--input-polled',tape,
                 '--frames','5300' if continuing else '5400','--ram-log',folder/'route.ram']
        if mode=='lle':command.append('--lle')
        if not reuse:
            previous=None
            # The existing diagnostic accepts a4096-byte frame list. Capture
            # bounded batches; every power-on replay must retain identical
            # tracked RAM/final guest hashes before combining its snapshots.
            for batch,start in enumerate(range(0,len(frames),700)):
                env['TLK_WRAM_DUMP']=','.join(map(str,frames[start:start+700]))
                log_path=folder/f'run-{batch}.log'
                with log_path.open('wb') as log:
                    subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
                current=(hashes(log_path),digest(folder/'route.ram'))
                if previous is not None:assert current==previous,'Original capture batches diverged'
                previous=current
                (folder/'run.log').write_bytes(log_path.read_bytes())
        sample_hash=hashlib.sha256();rows=[]
        for frame in frames:
            data=(folder/f'hl_wram_{frame}.bin').read_bytes();assert len(data)==131072;sample_hash.update(data)
            word=lambda a:struct.unpack_from('<H',data,a)[0]
            actor=0xb213;draw=word(actor+12)
            rows.append({'frame':frame,'level':word(0x1ff9e),'descriptor':word(0xdf),'health':word(0x2004),
                         'skip_display_flag':word(0xa6ba),'brightness_control':data[0x56],
                         'lives':word(0x1ffaa),'xy':[word(actor+8),word(actor+10)],'camera':[word(0x4a),word(0x4c)],
                         'words':list(struct.unpack_from('<64H',data,actor)),
                         'pose':int.from_bytes(data[draw+10:draw+13],'little')&0x3fffff if 0x2000<=draw<0xffe0 else 0,
                         'draw_words':list(struct.unpack_from('<11H',data,draw)) if 0x2000<=draw<0xffe0 else []})
        records[mode]=rows
        modes[mode]={'hashes':hashes(folder/'run.log'),'sampled_wram_sha256':sample_hash.hexdigest(),
                     'tracked_sha256':digest(folder/'route.ram')}
        print(mode,len(rows),'native original death samples',flush=True)
    assert modes['aot']==modes['lle'],'Original native modes differ'
    if reuse:assert modes==old['modes'],'Retained capture changed'
    if not continuing:
        assert (out/'lle/route.ram').read_bytes()==(ROOT/'build/pride-health-death-native/game.ram').read_bytes()
    else:
        assert modes['aot']['hashes']==hashes(ROOT/'build/pride-game-over-music/normal-native-aot/run.log')
    (out/'samples.json').write_text(json.dumps(records['lle'],indent=2)+'\n')
    report={'result':'PASS','scope':__doc__,'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),
            'input_sha256':digest(tape),'samples':len(records['lle']),'modes':modes,
            'route':'continue' if continuing else 'checkpoint',
            'capture_source_sha256':old.get('capture_source_sha256',old['source_sha256']) if reuse else digest(Path(__file__)),
            'loaded_states':False,'guest_edits':False,'source_sha256':digest(Path(__file__))}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


def md():
    import ctypes as C
    from md_lab import MdLab,png
    out=ROOT/'build/pride-death-timeline/md';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'build/md-next-levels-replay';inputs=json.loads((source/'frames.json').read_text())
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();trace=C.CDLL(str(ROOT/'build/md_death_trace.dll'))
    trace.md_death_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_death_trace_init(game.core._handle,str(out/'callbacks.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    rows=[];checks=0;pictures=[]
    word=lambda a:game.work_ram[a&65535]|game.work_ram[(a+1)&65535]<<8
    try:
        for frame in range(1,15301):
            trace.md_death_trace_frame(frame);game.step(inputs[frame-1]['pad'] if frame<=4000 else (128 if frame>5400 else 0))
            if frame<=4000 and frame%100==1:
                path=source/f'{frame:05d}-wram.bin'
                if path.exists():assert bytes(game.work_ram)==path.read_bytes();checks+=1
            if frame>=4400:
                camera=word(0xcd36);actor=word(camera+36);draw=word(actor+12)
                rows.append({'frame':frame,'level':word(0xccce),'health':word(0xccf6),'lives':word(0xccee),
                             'xy':[word(actor+8),word(actor+10)],'camera':[word(0x880c),word(0x880e)],
                             'words':[word(actor+i*2) for i in range(64)],
                             'pose':(word(draw+10)<<16|word(draw+12))&0xffffff,
                             'draw_words':[word(draw+i*2) for i in range(11)]})
            if frame in (4800,5400):
                assert bytes(game.work_ram)==(ROOT/f'build/pride-health-death-original/{frame}-wram.bin').read_bytes()
                png(out/f'{frame}.png',*game.image)
                assert (out/f'{frame}.png').read_bytes()==(ROOT/f'build/pride-health-death-original/{frame}.png').read_bytes()
                pictures.append(frame)
            if frame==14948:
                png(out/'game-over.png',*game.image)
                assert (out/'game-over.png').read_bytes()==(ROOT/'build/pride-game-over-original/game-over.png').read_bytes()
                pictures.append(frame)
            game.samples.clear()
    finally:trace.md_death_trace_close();game.close()
    (out/'samples.json').write_text(json.dumps(rows,indent=2)+'\n')
    report={'result':'PASS','scope':__doc__,'samples':len(rows),'unchanged_prefix_wram':checks,
            'unchanged_death_revival_pictures':pictures,'loaded_states':False,'guest_edits':False,
            'source_sha256':{'input':digest(source/'frames.json'),'core':digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
                             'trace_dll':digest(ROOT/'build/md_death_trace.dll'),'trace_source':digest(ROOT/'tools/md_death_trace.c'),
                             'samples':digest(out/'samples.json'),'callbacks':digest(out/'callbacks.csv'),'script':digest(Path(__file__))}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD death timeline;',checks,'prefix snapshots and death/revival outputs unchanged',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',choices=('native','md'))
    parser.add_argument('--continue-route',action='store_true');parser.add_argument('--reuse-native',action='store_true')
    args=parser.parse_args();native(args.continue_route,args.reuse_native) if args.source=='native' else md()


if __name__=='__main__':main()

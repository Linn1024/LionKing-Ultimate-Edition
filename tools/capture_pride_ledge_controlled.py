"""Reusable natural ledge fixtures; no ROM, RAM, register or clock edits."""
import argparse
import csv
import ctypes as C
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from capture_pride_ledge_physics import CASES, PATTERN
from pride_bounce_owner_preview_history import bound

FIXTURES = {
    'first': (1472,1874,'c33d1f','194b94',543,785),
    'opposite': (4032,4191,'c33f11','194da6',1536,256),
}
PUBLIC = ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
OBSERVER = ROOT/'build/pride-bounce-owner-work/player/actor-observer'


def actor_row(words, source, field, polls, health, roar):
    at=lambda offset:words[offset//2]
    long=lambda offset:(at(offset)|at(offset+2)<<16 if source=='snes' else at(offset)<<16|at(offset+2))
    return dict(field=field,polls=polls,health=health,roar=roar,words=words,
        action=f'{long(0x30)&0xffffff:06x}',x=at(8),y=at(10),
        frac_x=at(0x34),frac_y=at(0x36),vx=long(0x38),vy=long(0x3c),
        timer=at(0x2c),flags=at(0x4c))


def native(out,fixture):
    point,_,action,_,x,y=fixture
    bp=OBSERVER/'build-report.json';build=bound(bp)
    assert digest(OBSERVER/'player.exe')==build['binary_sha256']
    assert digest(PUBLIC)=='f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    config=out/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
    profile=out/'native.ini';profile.write_text('schema = 1\ngame = snes\n')
    tape=ROOT/'engine/tapes/allbugsF.read.tape';state=out/'ledge.state'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    commands={}
    def run(label,exe,end,inputs,load=False,observe=False,mode='lle'):
        folder=out/label;folder.mkdir();env=dict(clean)
        if observe:env['TLK_ACTOR_FIELDS']=str(folder/'actor.csv')
        command=list(map(str,[exe,'--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',out/'absent.md','--config',config,'--resource-profile',profile,
            '--frames',end,'--no-pace','--no-audio','--no-record',
            '--input' if load else '--input-polled',inputs,
            '--hash-at',','.join(map(str,range(1,end+1))),
            '--dump-window',folder/'window.png']))
        if mode=='lle':command+=['--lle']
        if load:command+=['--load',str(state)]
        else:command+=['--save-at',str(end),str(folder/'checkpoint.state')]
        commands[label]=command
        with (folder/'run.log').open('wb') as log:
            subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)
        return folder,re.findall(PATTERN,(folder/'run.log').read_text())
    def rows(folder):
        result=[]
        with (folder/'actor.csv').open() as stream:
            for row in csv.DictReader(stream):
                words=[int(row['actor_words'][at:at+4],16) for at in range(0,256,4)]
                assert len(words)==64
                assert row['scene'] in ('c00387','c0080d') and row['level']=='0'
                result.append(actor_row(words,'snes',int(row['field']),int(row['polls']),int(row['health']),int(row['roar'])))
        return result
    prefix,hashes=run('checkpoint-observer',OBSERVER/'player.exe',point,tape,observe=True)
    state.write_bytes((prefix/'checkpoint.state').read_bytes())
    _,control=run('checkpoint-public',PUBLIC,point,tape)
    assert hashes==control and len(control)==point
    # Earlier boot rows are outside Pride and do not need actor interpretation.
    with (prefix/'actor.csv').open() as stream:last=list(csv.DictReader(stream))[-1]
    words=[int(last['actor_words'][at:at+4],16) for at in range(0,256,4)]
    initial=actor_row(words,'snes',point,int(last['polls']),int(last['health']),int(last['roar']))
    assert (initial['action'],initial['x'],initial['y'],initial['timer'])==(action,x,y,42),initial
    results={}
    for name,pads in CASES.items():
        inputs=out/(name+'.tape');inputs.write_bytes(struct.pack('<'+'H'*(point+len(pads)),*([0]*point+pads)))
        folder,observed=run(name+'-observer',OBSERVER/'player.exe',point+len(pads),inputs,True,True)
        for mode in ('lle','aot'):
            _,control=run(name+'-public-'+mode,PUBLIC,point+len(pads),inputs,True,mode=mode)
            assert observed==control and len(control)==len(pads),(name,mode)
        results[name]=rows(folder)
        print('SNES',name,len(pads),'observer/public AOT/LLE fields exact',flush=True)
    return dict(initial=initial,cases=results,commands=commands,
        every_observed_field_matches_public_aot_lle=True,checkpoint_field=point),[bp,tape,PUBLIC,OBSERVER/'player.exe']


def megadrive(out,fixture):
    from md_lab import MdLab,png
    from md_replay_movie import movie_inputs
    _,point,_,action,x,y=fixture
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv';pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();trace_path=ROOT/'build/pride-cub-contact-audio/trace.dll'
    trace=C.CDLL(str(trace_path));trace.md_contact_audio_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_contact_audio_init(game.core._handle,str(out/'boot-entries.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    def row(field):
        word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
        assert word(0xccce)==1,'Left Pride Lands'
        return actor_row([word(0x93ce+at) for at in range(0,128,2)],'md',field,
            int(bool(trace.md_contact_audio_polled())),word(0xccf6),word(0xccf2))
    index=0
    try:
        for field in range(1,point+1):
            trace.md_contact_audio_field(field);game.step(polled[index]);game.samples.clear()
            if trace.md_contact_audio_polled():index+=1
        initial=row(point)
        assert (initial['action'],initial['x'],initial['y'],initial['timer'])==(action,x,y,42),initial
        (out/'checkpoint-wram.bin').write_bytes(bytes(game.work_ram));png(out/'checkpoint.png',*game.image)
        game.core.retro_serialize_size.restype=C.c_size_t;size=game.core.retro_serialize_size();state=C.create_string_buffer(size)
        game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
        game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
        assert game.core.retro_serialize(state,size) and b'TLKAE001' in state.raw
        (out/'ledge.state').write_bytes(state.raw);trace.md_contact_audio_close();results={}
        for name,inputs in CASES.items():
            assert game.core.retro_unserialize(state,size)
            assert trace.md_contact_audio_init(game.core._handle,str(out/(name+'-entries.csv')).encode())
            records=[]
            for n,pad in enumerate(inputs):
                mapped=0
                for native,button in [(0x100,7),(0x200,6),(0x400,5),(0x800,4),(0x8000,8),(0x80,1),(0x4000,0),(0x1000,3)]:
                    if pad&native:mapped|=1<<button
                trace.md_contact_audio_field(point+n+1);game.step(mapped);game.samples.clear();records.append(row(point+n+1))
                if n in (0,20,44,119):png(out/f'{name}-{n+1}.png',*game.image)
            trace.md_contact_audio_close();results[name]=records
            print('MD',name,len(records),'original fields',flush=True)
    finally:game.close()
    return dict(initial=initial,cases=results,checkpoint_field=point,
        complete_reference_core_snapshot=True),[movie,reference,trace_path,
        ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',choices=('snes','md'),required=True)
    parser.add_argument('--fixture',choices=FIXTURES,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();out=args.out.resolve();out.mkdir(parents=True)
    data,paths=(native if args.source=='snes' else megadrive)(out,FIXTURES[args.fixture])
    paths += [Path(__file__),ROOT/'tools/capture_pride_ledge_physics.py',ROOT/'tools/build_pride_actor_observer.py',ROOT/'tools/native_pride_actor_observer.c']
    report=dict(result='CAPTURED',source=args.source,fixture=args.fixture,**data,
        guest_mutations=False,finite_protocols_only=True,full_first_level_fidelity_complete=False,
        protocols=CASES,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()

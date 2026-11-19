"""Input-only ledge continuations from naturally reached original checkpoints.

Research only. Run MD with the local 32-bit Python; SNES uses the previously
verified read-only observer and checks every continued guest field against the
current public player. Outputs are exclusive and never replace older evidence.
"""
import argparse
import csv
import ctypes as C
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT, read_rom
from build_pride_compiled_hooks import digest
from pride_bounce_owner_preview_history import bound

CASES = {
    'neutral': [0]*120,
    'right': [0x100]*60+[0]*60,
    'left': [0x200]*60+[0]*60,
    'up': [0x800]*60+[0]*60,
    'down': [0x400]*60+[0]*60,
    'jump': [0x8000]*4+[0]*116,
    'right-jump': [0x8100]*4+[0]*116,
    'left-jump': [0x8200]*4+[0]*116,
    'roar': [0x80]*20+[0]*100,
    'roll': [0x500]*20+[0]*100,
    'reverse': [0x100]*8+[0x200]*52+[0]*60,
    'late-jump': [0]*20+[0x8000]*4+[0]*96,
}
PATTERN = r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'


def snes(out):
    observer = ROOT/'build/pride-arrival-work/player/contact-audio-lifetime'
    bp = observer/'build-report.json'
    assert digest(observer/'player.exe') == bound(bp)['binary_sha256']
    public = ROOT/'build/pride-bounce-owner-work/player/native-engine/tlk_pride_player.exe'
    assert digest(public) == 'f0165236ff540101d53b642b5b9f0464ec9ba0b4f565a442615ad2fe87b6293d'
    config = out/'host.ini'; config.write_text('opengl = 0\nscale = 2\n')
    profile = out/'native.ini'; profile.write_text('schema = 1\ngame = snes\n')
    tape = ROOT/'engine/tapes/allbugsF.read.tape'
    checkpoint = out/'ledge.state'
    clean = {k:v for k,v in os.environ.items() if not k.startswith(('TLK_', 'SDL_'))}
    commands = {}

    def run(label, exe, end, inputs, load=False, observe=False):
        folder = out/label; folder.mkdir()
        env = dict(clean)
        if observe: env['TLK_NATIVE_CONTACT_LIFETIME'] = str(folder/'lifetime.csv')
        cmd = list(map(str, [exe, '--rom', ROOT/'Lion King, The (USA).sfc',
            '--md-rom', out/'absent.md', '--config', config, '--resource-profile', profile,
            '--frames', end, '--lle', '--no-pace', '--no-audio', '--no-record',
            '--input' if load else '--input-polled', inputs,
            '--hash-at', ','.join(map(str, range(1,end+1))), '--dump-window', folder/'window.png']))
        if load: cmd += ['--load', str(checkpoint)]
        else: cmd += ['--save-at', str(end), str(folder/'checkpoint.state')]
        commands[label] = cmd
        with (folder/'run.log').open('wb') as stream:
            subprocess.run(cmd, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=240)
        return folder, re.findall(PATTERN, (folder/'run.log').read_text())

    base, hashes = run('checkpoint-observer', observer/'player.exe',1472,tape,observe=True)
    checkpoint.write_bytes((base/'checkpoint.state').read_bytes())
    _, public_hashes = run('checkpoint-public',public,1472,tape)
    assert hashes == public_hashes and len(hashes)==1472
    initial = list(csv.DictReader((base/'lifetime.csv').open()))[-1]
    assert (initial['action'],initial['x'],initial['y'],initial['timer']) == ('c33d1f','543','785','42'), initial
    results = {}
    for name, pads in CASES.items():
        inputs = out/(name+'.tape')
        inputs.write_bytes(struct.pack('<'+'H'*(1472+len(pads)), *([0]*1472+pads)))
        folder, observed = run(name+'-observer',observer/'player.exe',1592,inputs,True,True)
        _, control = run(name+'-public',public,1592,inputs,True)
        assert observed == control and len(control)==120, name
        rows = list(csv.DictReader((folder/'lifetime.csv').open()))
        assert len(rows)==120
        results[name] = rows
        print('SNES',name,'120 public guest fields exact',flush=True)
    return dict(initial=initial,cases=results,commands=commands,
        every_observed_field_matches_public=True,checkpoint_field=1472), [bp,tape,public,observer/'player.exe']


def md(out):
    from md_lab import MdLab,png
    from md_replay_movie import movie_inputs
    read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();trace_path=ROOT/'build/pride-cub-contact-audio/trace.dll'
    trace=C.CDLL(str(trace_path));trace.md_contact_audio_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_contact_audio_init(game.core._handle,str(out/'entries.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    def row(field):
        word=lambda a:game.work_ram[a]|game.work_ram[a+1]<<8
        long=lambda a:word(a)<<16|word(a+2)
        a=0x93ce
        return dict(field=str(field),action=f'{long(a+0x30):06x}',x=str(word(a+8)),y=str(word(a+10)),
            timer=str(word(a+0x2c)),vx=f'{long(a+0x38):08x}',vy=f'{long(a+0x3c):08x}',
            flags=f'{word(a+0x4c):04x}',level=str(word(0xccce)))
    index=0
    try:
        for field in range(1,1875):
            trace.md_contact_audio_field(field);game.step(polled[index]);game.samples.clear()
            if trace.md_contact_audio_polled():index+=1
        initial=row(1874)
        assert (initial['action'],initial['x'],initial['y'],initial['timer'])==('194b94','543','785','42'),initial
        png(out/'checkpoint.png',*game.image)
        game.core.retro_serialize_size.restype=C.c_size_t
        size=game.core.retro_serialize_size();state=C.create_string_buffer(size)
        game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
        game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
        assert game.core.retro_serialize(state,size)
        assert b'TLKAE001' in state.raw
        (out/'ledge.state').write_bytes(state.raw)
        trace.md_contact_audio_close()
        results={}
        for name,inputs in CASES.items():
            assert game.core.retro_unserialize(state,size)
            rows=[]
            for n,pad in enumerate(inputs):
                mapped=0
                for native,button in [(0x100,7),(0x200,6),(0x400,5),(0x800,4),(0x8000,8),(0x80,1),(0x4000,0),(0x1000,3)]:
                    if pad&native:mapped|=1<<button
                game.step(mapped);game.samples.clear();rows.append(row(1875+n))
                if n in (0,20,44,119):png(out/f'{name}-{n+1}.png',*game.image)
            results[name]=rows
            print('MD',name,'120 original fields',flush=True)
    finally:game.close()
    return dict(initial=initial,cases=results,checkpoint_field=1874,complete_reference_core_snapshot=True),[
        movie,reference,trace_path,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',
        ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',choices=('snes','md'),required=True)
    args=parser.parse_args()
    out=ROOT/'build/pride-ledge-physics'/args.source;out.mkdir(parents=True)
    data,paths=(snes if args.source=='snes' else md)(out)
    report=dict(result='CAPTURED',source=args.source,**data,guest_mutations=False,
        finite_protocols_only=True,full_ledge_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),*paths]},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()

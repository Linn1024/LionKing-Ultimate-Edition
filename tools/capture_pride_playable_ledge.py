"""Compare the playable opposite ledge, retaining its natural input provenance."""
import argparse
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from capture_pride_ledge_controlled import native,actor_row,CASES
from pride_bounce_owner_preview_history import bound

FIXTURE=(2165,2542,'c33f11','194da6',1232,481)


def md(out):
    from md_lab import MdLab,png
    from md_replay_movie import movie_inputs
    found_path=ROOT/'build/pride-ledge-controlled/find-playable/report.json'
    found=bound(found_path);assert found['result']=='FOUND'
    origin=found_path.parent/'ledge.state';raw=origin.read_bytes()
    assert found['found']['entry']['field']==2542
    game=MdLab();library=ROOT/'build/pride-cub-contact-audio/trace.dll';trace=C.CDLL(str(library))
    trace.md_contact_audio_init.argtypes=[C.c_void_p,C.c_char_p]
    _,_,settings=movie_inputs(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2')
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    state=C.create_string_buffer(raw)
    def row(field):
        word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
        assert word(0xccce)==1 and word(word(0xcd36)+0x24)==0x93ce,'Player ownership/level changed'
        return actor_row([word(0x93ce+at) for at in range(0,128,2)],'md',field,
            int(bool(trace.md_contact_audio_polled())),word(0xccf6),word(0xccf2))
    results={}
    try:
        assert game.core.retro_unserialize(state,len(raw))
        assert trace.md_contact_audio_init(game.core._handle,str(out/'initial-entries.csv').encode())
        trace.md_contact_audio_field(2542);initial=row(2542)
        assert (initial['action'],initial['x'],initial['y'],initial['timer'])==('194da6',1232,481,42)
        trace.md_contact_audio_close()
        (out/'ledge.state').write_bytes(raw)
        for name,inputs in CASES.items():
            assert game.core.retro_unserialize(state,len(raw))
            assert trace.md_contact_audio_init(game.core._handle,str(out/(name+'-entries.csv')).encode())
            records=[]
            for n,pad in enumerate(inputs):
                mapped=0
                for native_pad,button in [(0x100,7),(0x200,6),(0x400,5),(0x800,4),(0x8000,8),(0x80,1),(0x4000,0),(0x1000,3)]:
                    if pad&native_pad:mapped|=1<<button
                field=2543+n;trace.md_contact_audio_field(field);game.step(mapped);game.samples.clear();records.append(row(field))
                if n in (0,20,44,119):png(out/f'{name}-{n+1}.png',*game.image)
            trace.md_contact_audio_close();results[name]=records
            print('MD playable opposite',name,len(records),'original fields',flush=True)
    finally:game.close()
    return dict(initial=initial,cases=results,checkpoint_field=2542,
        complete_reference_core_snapshot=True,natural_checkpoint_report=found_path.relative_to(ROOT).as_posix()),[
        found_path,origin,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',choices=('snes','md'),required=True)
    args=parser.parse_args();out=ROOT/'build/pride-ledge-controlled/playable-opposite'/args.source;out.mkdir(parents=True)
    data,paths=native(out,FIXTURE) if args.source=='snes' else md(out)
    paths += [Path(__file__),ROOT/'tools/capture_pride_ledge_controlled.py',ROOT/'tools/capture_pride_ledge_physics.py']
    report=dict(result='CAPTURED',fixture='playable-opposite',source=args.source,**data,
        guest_mutations=False,full_first_level_fidelity_complete=False,protocols=CASES,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()

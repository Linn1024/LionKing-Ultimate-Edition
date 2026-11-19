"""Read-only MD title sound census: ordinary movie prefix and neutral power-on."""
import csv
import ctypes as C
import hashlib
import json
from pathlib import Path
import sys
import wave
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from pride_arena_history import bound


def main():
    origin=ROOT/'build/pride-audio-inventory/report.json';prior=bound(origin)
    assert prior['result']=='ORIGINAL_PRIDE_CENSUS_CAPTURED'
    out=ROOT/'build/pride-title-audio77';out.mkdir()
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    library=origin.parent/'trace.dll';trace=C.CDLL(str(library))
    trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    observations={};checks={}
    expected=list(csv.DictReader((origin.parent/'commands.csv').open()))
    for name in ('route','neutral'):
        folder=out/name;folder.mkdir();game=MdLab();index=0;frames=[]
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
        assert trace.md_commands_init(game.core._handle,str(folder/'commands.csv').encode())
        try:
            with wave.open(str(folder/'audio.wav'),'wb') as wav:
                wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(round(game.av.timing.sample_rate))
                for field in range(1,1401):
                    trace.md_commands_frame(field);game.step(polled[index] if name=='route' else 0)
                    if trace.md_commands_polled():index+=1
                    wav.writeframesraw(game.samples);game.samples.clear()
                    if field in (300,600,820,830,950,1287,1400):
                        png(folder/f'{field}.png',*game.image)
                        frames.append(dict(field=field,ram_sha256=hashlib.sha256(bytes(game.work_ram)).hexdigest(),
                                           image_sha256=hashlib.sha256(game.image[0]).hexdigest(),
                                           level=game.work_ram[0xccce]|game.work_ram[0xcccf]<<8))
        finally:trace.md_commands_close();game.close()
        calls=list(csv.DictReader((folder/'commands.csv').open()))
        observations[name]=dict(calls=calls,frames=frames,consumed_polls=index)
        checks[name+'_1400_fields_captured']=frames[-1]['field']==1400
        checks[name+'_title_music73_observed']=any(r['selector']=='1' and r['value']=='73' for r in calls)
        if name=='route':
            checks['all_original_prefix_commands_exact']=calls==[r for r in expected if int(r['frame'])<=1400]
            checks['original_ready_picture_exact']=digest(folder/'1287.png')==digest(origin.parent/'ready.png')
        print(name,'calls',len(calls),'sound_commands',[(r['frame'],r['selector'],r['value']) for r in calls if r['selector'] in ('1','2','19')],flush=True)
    paths=[Path(__file__),origin,origin.parent/'commands.csv',origin.parent/'ready.png',library,movie,reference,
           ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll',ROOT/'Lion King, The (World).md']
    report=dict(result='ORIGINAL_TITLE_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,
                guest_or_rom_edits=False,production_changed=False,whole_title_equivalence_proven=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()

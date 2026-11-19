"""Observe original MD title/Options audio under widely spaced ordinary controls."""
import csv
import ctypes as C
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from md_lab import MdLab,png
from md_replay_movie import movie_inputs
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-title-audio77/report.json';p=bound(prior)
    assert p['result']=='ORIGINAL_TITLE_CAPTURED'
    out=ROOT/'build/pride-menu-protocol79';out.mkdir()
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    library=ROOT/'build/pride-audio-inventory/trace.dll';trace=C.CDLL(str(library))
    trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    plans={'options':{990:32,1010:8,1080:128,1110:64,1140:32,1170:16,1200:8},
           'start':{990:256}}
    observations={};checks={}
    for name,plan in plans.items():
        folder=out/name;folder.mkdir();game=MdLab();index=0;rows=[]
        game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
        for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
        assert trace.md_commands_init(game.core._handle,str(folder/'commands.csv').encode())
        try:
            for field in range(1,1351):
                pad=polled[index] if field<=985 else next((v for at,v in plan.items() if at<=field<at+4),0)
                trace.md_commands_frame(field);game.step(pad);game.samples.clear()
                if trace.md_commands_polled():index+=1
                if field>=985:
                    word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
                    rows.append(dict(field=field,pad=pad,level=word(0xccce),cursor_y=word(0xfe12),difficulty=word(0xccdc)))
                if field==950 or field in (1000,1030,1070,1100,1130,1160,1190,1220,1250,1350):png(folder/f'{field}.png',*game.image)
        finally:trace.md_commands_close();game.close()
        calls=list(csv.DictReader((folder/'commands.csv').open()))
        checks[name+'_same_original_title_prefix']=digest(folder/'950.png')==digest(prior.parent/'route/950.png')
        checks[name+'_1350_fields_captured']=rows[-1]['field']==1350
        observations[name]=dict(rows=rows,calls=[r for r in calls if int(r['frame'])>=985])
        print(name,[(r['frame'],r['selector'],r['value'],r['outer_caller']) for r in observations[name]['calls']],flush=True)
    paths=[Path(__file__),prior,movie,reference,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py']
    report=dict(result='ORIGINAL_MENU_PROTOCOL_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,plans=plans,
                observations=observations,ordinary_inputs=True,guest_or_rom_edits=False,production_changed=False,
                source_mapping_or_whole_menu_equivalence_proven=False,
                source_sha256={path.relative_to(ROOT).as_posix():digest(path) for path in paths},
                artifacts_sha256={path.relative_to(out).as_posix():digest(path) for path in out.rglob('*') if path.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    assert all(checks.values())


if __name__=='__main__':main()

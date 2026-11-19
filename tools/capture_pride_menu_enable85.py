"""Original MD sound-effects Off/On from Options using ordinary controls only."""
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
    previous=ROOT/'build/pride-menu-protocol79/report.json';bound(previous)
    out=ROOT/'build/pride-menu-enable85-md';out.mkdir()
    movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
    reference=ROOT/'build/md-next-levels-reference/ram.csv'
    pads,_,settings=movie_inputs(movie)
    with reference.open() as stream:
        polled=[pads[int(r['frame'])-1] for r in csv.DictReader(stream) if r['lag']=='0' and int(r['frame'])<=len(pads)]
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513 if settings['o']['UseSixButton'] else 257)
    library=ROOT/'build/pride-audio-inventory/trace.dll';trace=C.CDLL(str(library));trace.md_commands_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_commands_init(game.core._handle,str(out/'commands.csv').encode())
    plan={990:32,1010:8,1080:32,1110:32,1140:128,1170:128};rows=[];index=0
    try:
        for field in range(1,1251):
            pad=polled[index] if field<=985 else next((v for at,v in plan.items() if at<=field<at+4),0)
            trace.md_commands_frame(field);game.step(pad);game.samples.clear()
            if trace.md_commands_polled():index+=1
            if field>=985:rows.append(dict(field=field,pad=pad,effects=game.work_ram[0xf284],music=game.work_ram[0xf283],cursor_y=game.work_ram[0xfe12]|game.work_ram[0xfe13]<<8))
            if field in (1130,1160,1190,1250):png(out/f'{field}.png',*game.image)
    finally:trace.md_commands_close();game.close()
    calls=list(csv.DictReader((out/'commands.csv').open()));states={r['field']:r for r in rows}
    fx=[(int(r['frame']),int(r['selector']),int(r['value'])) for r in calls if r['selector'] in ('2','19') and int(r['frame'])>=985]
    checks=dict(initial_effects_enabled=states[1130]['effects']==1,ordinary_off=states[1160]['effects']==0,
                ordinary_on=states[1190]['effects']==1,
                off_action_plays101=(1140,2,101) in fx,on_action_has_no_effect=not any(1170<=f<=1174 for f,s,v in fx))
    paths=[Path(__file__),previous,movie,reference,library,ROOT/'tools/md_lab.py',ROOT/'tools/md_replay_movie.py']
    report=dict(result='ORIGINAL_EFFECTS_ENABLE_CAPTURED' if all(checks.values()) else 'FAIL',checks=checks,plan=plan,frames=rows,effect_calls=fx,
                ordinary_inputs=True,guest_or_rom_edits=False,whole_options_equivalence_proven=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,fx,flush=True)


if __name__=='__main__':main()

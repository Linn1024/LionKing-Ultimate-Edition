"""Compare ordinary original Up/Down sequences with equal event timing."""
import ctypes as C
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,MdLab,png
from capture_pride_title_readiness_contexts import picture
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-title-wrap-original2';out.mkdir()
    prior=ROOT/'build/pride-title-readiness-original/report.json';bound(prior)
    state=prior.parent/'game-over-timeout/before-input.state';raw=state.read_bytes()
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    results={};checks={}
    try:
        for label,events in [('neutral',{}),('up',{515:16}),('down',{515:32}),('up-up',{515:16,525:16}),
                             ('down-down',{515:32,525:32}),('down-up',{515:32,525:16}),('up-down',{515:16,525:32}),
                             ('up-up524',{515:16,524:16}),('down-down524',{515:32,524:32})]:
            blob=C.create_string_buffer(raw);assert game.core.retro_unserialize(blob,len(raw))
            for age in range(484,651):game.step(events.get(age,0));game.samples.clear()
            png(out/(label+'.png'),*game.image);results[label]=dict(events=events,picture_sha256=picture(game))
        same=lambda a,b:results[a]['picture_sha256']==results[b]['picture_sha256']
        checks['one_up_down_equal']=same('up','down')
        checks['two_equal_up_down']=same('up-up','down-down')
        checks['mixed_equal_two']=same('down-up','up-up') and same('up-down','up-up')
        checks['one_and_two_distinct']=not same('up','up-up')
        checks['same_button_at_first_poll_suppressed']=same('up','up-up524') and same('down','down-down524')
        checks['two_returns_start']=same('neutral','up-up')
    finally:game.close()
    paths=[Path(__file__),prior,state,ROOT/'tools/md_lab.py',ROOT/'tools/capture_pride_title_readiness_contexts.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=results,ordinary_inputs=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()

"""Original MD held/directional/confirmation priority from a genuine title state."""
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
    out=ROOT/'build/pride-title-navigation-edges2';out.mkdir()
    prior=ROOT/'build/pride-title-readiness-original/report.json';bound(prior)
    state=prior.parent/'game-over-timeout/before-input.state';raw=state.read_bytes()
    game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    plans={'idle':{},'selected':{515:32},'open':{515:32,524:8},'start515':{515:8},'start524':{524:8},
           'held-down':{i:32 for i in range(515,601)},'held-up':{i:16 for i in range(515,601)},
           'both-directions':{515:48},'start-down':{515:40},'start-up':{515:24},
           'both-then-up524':{515:48,524:16},'both-then-down524':{515:48,524:32},
           'both-then-down525':{515:48,525:32},
           'selected-start-up':{515:32,524:24},'selected-start-down':{515:32,524:40},
           'selected-repeat524':{515:32,524:32},'selected-repeat525':{515:32,525:32},
           'held-start-into-ready':{515:32,**{i:8 for i in range(516,525)}}}
    observations={}
    try:
        for label,events in plans.items():
            blob=C.create_string_buffer(raw);assert game.core.retro_unserialize(blob,len(raw))
            for age in range(484,651):game.step(events.get(age,0));game.samples.clear()
            png(out/(label+'.png'),*game.image);observations[label]=dict(events=events,picture_sha256=picture(game))
        baselines={observations[label]['picture_sha256']:label for label in ('idle','selected','open','start515','start524')}
        for label,row in observations.items():row['outcome']=baselines.get(row['picture_sha256']);print(label,row['outcome'],flush=True)
    finally:game.close()
    checks={label+'_classified':r['outcome'] is not None for label,r in observations.items()}
    paths=[Path(__file__),prior,state,ROOT/'tools/md_lab.py',ROOT/'tools/capture_pride_title_readiness_contexts.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,ordinary_inputs=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()

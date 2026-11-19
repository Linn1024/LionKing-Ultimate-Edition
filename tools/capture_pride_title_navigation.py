"""Measure original MD title navigation/confirmation after the first ready field."""
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
    out=ROOT/'build/pride-title-navigation-original';out.mkdir()
    prior=ROOT/'build/pride-title-readiness-original/report.json';bound(prior)
    path=prior.parent/'game-over-timeout/before-input.state'
    raw=path.read_bytes();game=MdLab();game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_unserialize.restype=C.c_bool
    game.core.retro_serialize_size.restype=C.c_size_t
    game.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t];game.core.retro_serialize.restype=C.c_bool
    checks={};observations={};neutral={};plans={}
    try:
        blob=C.create_string_buffer(raw);assert game.core.retro_unserialize(blob,len(raw))
        for age in range(484,516):game.step(32 if age==515 else 0);game.samples.clear()
        n=game.core.retro_serialize_size();state=C.create_string_buffer(n);assert game.core.retro_serialize(state,n)
        (out/'after-down515.state').write_bytes(state.raw)
        for age in range(516,651):
            game.step();game.samples.clear();neutral[age]=picture(game)
        png(out/'neutral650.png',*game.image)
        for button,label in [(8,'start'),(16,'up')]:
            rows=[]
            for at in range(516,556):
                assert game.core.retro_unserialize(state,n);changed=None
                for age in range(516,651):
                    game.step(button if age==at else 0);game.samples.clear()
                    if changed is None and picture(game)!=neutral[age]:changed=age
                rows.append(dict(pressed=at,first_picture_change=changed,endpoint=picture(game)))
                if changed is not None and not any(r['first_picture_change'] is not None for r in rows[:-1]):
                    png(out/f'{label}-first-accepted650.png',*game.image)
            accepted=[r['pressed'] for r in rows if r['first_picture_change'] is not None]
            first=min(accepted) if accepted else None;observations[label]=dict(first_accepted=first,after_down=first-515 if first else None,rows=rows)
            checks[label+'_contiguous_boundary']=first is not None and all((r['first_picture_change'] is not None)==(r['pressed']>=first) for r in rows)
            print(label,'first accepted',first,flush=True)
        ready=observations['start']['first_accepted']
        for label,release in [('held',ready),('released',ready-1)]:
            assert game.core.retro_unserialize(state,n);changed=None
            for age in range(516,651):
                game.step(8 if 516<=age<=release else 0);game.samples.clear()
                if changed is None and picture(game)!=neutral[age]:changed=age
            observations[label]=dict(first_picture_change=changed,released=release);png(out/f'{label}650.png',*game.image)
            checks[label+'_outcome']=(changed is not None)==(label=='held')
        # A widely spaced genuine Options -> title -> new-game route for later timing work.
        blob=C.create_string_buffer(raw);assert game.core.retro_unserialize(blob,len(raw))
        events={515:32,550:8,700:8,750:16,800:8};frames=[]
        for age in range(484,1801):
            game.step(events.get(age,0));game.samples.clear()
            word=lambda p:game.work_ram[p]|game.work_ram[p+1]<<8
            frames.append(dict(age=age,level=word(0xccce),health=word(0xccf6),lives=word(0xccee),picture_sha256=picture(game)))
            if age in (550,600,700,730,750,800,850,900,950,1000,1100,1200,1400,1800):png(out/f'route{age}.png',*game.image)
        observations['route']=dict(events=events,frames=frames,first_level1=next((r['age'] for r in frames if r['level']==1),None))
        plans['route']=events
    finally:game.close()
    paths=[Path(__file__),prior,path,ROOT/'tools/md_lab.py',ROOT/'tools/capture_pride_title_readiness_contexts.py']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,plans=plans,
                ordinary_inputs=True,guest_or_rom_edits=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),flush=True)


if __name__=='__main__':main()

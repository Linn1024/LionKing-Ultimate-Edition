"""Observe the original MD post-fade respawn hold before normal play resumes."""
import csv
import ctypes as C
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT,png


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-revival-reference';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    source=ROOT/'build/md-next-levels-replay';inputs=json.loads((source/'frames.json').read_text())
    timeline_path=ROOT/'build/pride-death-timeline/report.json';timeline=json.loads(timeline_path.read_text())
    assert timeline['result']=='STREAMS_EQUAL_STAGING_DIFFERENT_ADAPTER_OPEN'
    game=MdLab();trace=C.CDLL(str(ROOT/'build/md_revival_trace.dll'))
    trace.md_revival_trace_init.argtypes=[C.c_void_p,C.c_char_p]
    assert trace.md_revival_trace_init(game.core._handle,str(out/'callbacks.csv').encode())
    game.core.retro_set_controller_port_device.argtypes=[C.c_uint,C.c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    checks=0;palettes=[]
    try:
        for frame in range(1,15301):
            trace.md_revival_trace_frame(frame);game.step(inputs[frame-1]['pad'] if frame<=4000 else 128 if frame>5400 else 0)
            if frame<=4000 and frame%100==1:
                file=source/f'{frame:05d}-wram.bin'
                if file.exists():assert bytes(game.work_ram)==file.read_bytes();checks+=1
            if frame in (4800,5400):
                assert bytes(game.work_ram)==(ROOT/f'build/pride-health-death-original/{frame}-wram.bin').read_bytes()
                png(out/f'{frame}.png',*game.image)
                assert (out/f'{frame}.png').read_bytes()==(ROOT/f'build/pride-health-death-original/{frame}.png').read_bytes()
            if frame==14948:
                png(out/'game-over.png',*game.image)
                assert (out/'game-over.png').read_bytes()==(ROOT/'build/pride-game-over-original/game-over.png').read_bytes()
            if any(not d['display_skipped'] and d['death']<=frame<=d['death']+345 for d in timeline['md_deaths']):
                palettes.append({'frame':frame,'cram':bytes(game.cram).hex()})
            game.samples.clear()
    finally:trace.md_revival_trace_close();game.close()
    rows=list(csv.DictReader((out/'callbacks.csv').open()));cases=[]
    for number,death in enumerate(timeline['md_deaths']):
        start=death['death'];stop=timeline['md_deaths'][number+1]['death'] if number+1<len(timeline['md_deaths']) else 15301
        events=[r for r in rows if start<=int(r['frame'])<stop]
        assert len([r for r in events if r['pc']=='1d6cb2'])==1
        by_pc=lambda pc:[r for r in events if r['pc']==pc]
        if death['display_skipped']:
            assert not by_pc('1d70f6') and not by_pc('1d7158')
            cases.append({'death':start,'final_life_skips_revival':True});continue
        unique=lambda pc:int(by_pc(pc)[0]['frame']) if len(by_pc(pc))==1 else None
        hold=by_pc('1d7158');assert [int(r['d7']) for r in hold]==list(range(48,-1,-1))
        cases.append({'death':start,'checkpoint':events[0]['checkpoint'],
                      'main_loop_start':unique('1d6d9c'),'main_loop_end':unique('1d6e00'),
                      'complete_fade_end':unique('1d6e22'),'new_actor_owner':unique('1d6e4c'),
                      'health_restore_write':unique('1d7046'),
                      'fade_in_call':unique('1d70f6'),'fade_in_return':unique('1d70fc'),
                      'respawn_hold_start':int(hold[0]['frame']),'respawn_hold_iterations':len(hold),
                      'after_hold':unique('1d717e'),'normal_play_jump':unique('1d71ce')})
    (out/'palettes.json').write_text(json.dumps(palettes,indent=2)+'\n')
    report={'result':'PASS','scope':__doc__,'cases':cases,'unchanged_prefix_wram_checks':checks,
            'loaded_states':False,'guest_edits':False,'source_sha256':{'script':digest(Path(__file__)),
            'trace_source':digest(ROOT/'tools/md_revival_trace.c'),'trace_dll':digest(ROOT/'build/md_revival_trace.dll'),
            'core':digest(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'),
            'timeline':digest(timeline_path),'callbacks':digest(out/'callbacks.csv'),'input':digest(source/'frames.json'),
            'palettes':digest(out/'palettes.json')}}
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print('Original MD revival fade return,49-step checkpoint hold and normal-play jump observed PASS',flush=True)
    print(json.dumps(cases[0]),flush=True)


if __name__=='__main__':main()

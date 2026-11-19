"""Qualify captured mixtures without repeating completed gameplay runs.

The initial runner requested per-field hashes only through3280 and then tried
to read such a row after loading3280. Its IndexError was a verifier error; the
ordinary final guest hashes and successful game termination remain available.
"""
import json
from pathlib import Path
import re
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes


def main():
    base=ROOT/'build/pride-checkpoint-animation52';out=base/'source-mixtures-qualification';out.mkdir()
    playpath=base/'animation-play/report.json';play=bound(playpath)
    runner=ROOT/'tools/verify_pride_checkpoint_sources52.py'
    captures=base/'source-mixtures';checks={};cases={};paths=[Path(__file__),runner,playpath,base/'build-report.json']
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    fields=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for frames,palette in [('snes','snes'),('snes','md'),('md','snes'),('md','md')]:
        name=frames+'-'+palette
        # Already-qualified MD/MD baseline supplies the fourth source pair;
        # the runner's remaining queued copy was canceled on its IndexError.
        locations=dict(seed=playpath.parent/'md-contact',blink=playpath.parent/'display-3293') if name=='md-md' else {
            stage:captures/name/stage for stage in ('seed','blink')}
        checks[name+'_all3280_seed_guest_fields']=fields(locations['seed'])==fields(playpath.parent/'md-contact') and len(fields(locations['seed']))==3280
        scene=json.loads((locations['blink']/'scene.json').read_text())
        choices=json.loads((locations['blink']/'tree.jsonl').read_text().splitlines()[-1])['choices']
        selected=lambda key:next(c for c in choices if c[0]==key)[-1]
        checks[name+'_timing_md']=selected('gameplay.levels.pride_lands.checkpoint_animation')==2
        checks[name+'_frames_independent']=selected('graphics.sprites.checkpoints.frames')==(2 if frames=='md' else 1)
        checks[name+'_palette_independent']=selected('graphics.sprites.checkpoints.palette')==(2 if palette=='md' else 1)
        checks[name+'_same_blink_pose']=any(p['pose']==0xc2fe18 for p in scene['pieces'])
        for stage,reference in [('seed',playpath.parent/'md-contact'),('blink',playpath.parent/'display-3293')]:
            folder=locations[stage];log=(folder/'run.log').read_text()
            checks[name+'_'+stage+'_completed']=('frames='+('3280' if stage=='seed' else '3293')+' wall_s=') in log and 'runtime failure' not in log
            checks[name+'_'+stage+'_guest_endpoint']=hashes(folder/'run.log')==hashes(reference/'run.log')
            for file in ('audio.wav','timing.csv'):
                checks[name+'_'+stage+'_'+file]=digest(folder/file)==digest(reference/file)
            paths.extend(p for p in folder.iterdir() if p.is_file())
        cases[name]=dict(locations={k:p.relative_to(ROOT).as_posix() for k,p in locations.items()},
                         window_sha256=digest(locations['blink']/'window.png'),checkpoint_adapter=scene.get('checkpoint_adapter'))
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,cases=cases,
                initial_verifier_index_error_retained=True,guest_execution_repeated=False,
                original_decoded_pixel_correctness_retested=False,full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

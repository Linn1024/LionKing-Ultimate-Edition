"""Verify the new partial-font plumbing preserves default full-roar behavior."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from audit_scenes import ROOT


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-empty-roar-controls';out.mkdir(exist_ok=True)
    player=ROOT/'engine/build-win/tlk_scene_prepared_probe.exe';identity=digest(player)
    cases={}
    for width in (320,256):
        old=ROOT/f'build/pride-scene-render-prepared-headless-{width}-5400-checkpoint-both'
        previous=json.loads((old/'report.json').read_text())
        assert previous['result']=='OWNED_SCENERY_CUB_PIXELS_VERIFIED_OTHER_OBJECTS_OPEN'
        old_case=previous['runs']['native-owned']
        for name in ('render-owned.rgb','route.ram','picture.png'):
            assert digest(old/'native-owned'/name)==old_case['artifacts_sha256'][name],name
        folder=out/f'headless-{width}'
        cmd=[sys.executable,str(ROOT/'tools/probe_pride_scene_render.py'),'--prepared','--checkpoint','both',
             '--profiles','native','--width',str(width),'--output-root',str(folder)]
        with (out/f'{width}.log').open('wb') as log:
            subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        report=json.loads((folder/'report.json').read_text())
        assert report['probe_sha256']==identity and report['revival_roar_source']=='snes'
        for name in ('render-owned.rgb','route.ram','picture.png'):
            assert digest(folder/'native-owned'/name)==digest(old/'native-owned'/name),(width,name)
        cases[str(width)]=dict(default_full_roar_trace_and_full_tracked_ram_and_picture_exact=True,
            previous_report_sha256=digest(old/'report.json'),current_report_sha256=digest(folder/'report.json'))
    assert digest(player)==identity
    result=dict(result='PASS',scope=__doc__,probe_sha256=identity,cases=cases,
        production_behavior_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in
            (Path(__file__),ROOT/'tools/probe_pride_scene_render.py',ROOT/'tools/pride_scene_prepared_objects.c',
             ROOT/'tools/pride_scene_restore_probe.c',ROOT/'engine/runner/tlk_native_hud.c',ROOT/'engine/runner/tlk_native_hud.h')})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Default full-roar pixels, final pictures and full tracked RAM match prior private release at320/256',flush=True)


if __name__=='__main__':main()

"""Bind title-readiness research, including the two retained held-input failures."""
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_final_scene_runtime import pcm


def main():
    out=ROOT/'build/pride-title-readiness-bindings';out.mkdir();checks={}
    reports=['pride-title-readiness-original/report.json','pride-title-readiness-native/report.json',
             'pride-title-readiness-probe/report.json','pride-title-readiness-probe2/report.json',
             'pride-title-readiness-probe3/report.json','pride-title-readiness-probe3/contexts/report.json',
             'pride-title-upload16/build-report.json']
    data={}
    for name in reports:
        data[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for folder in ('pride-title-readiness-native','pride-title-readiness-probe','pride-title-readiness-probe2','pride-title-readiness-probe3'):
        report=data[folder+'/report.json'];base=ROOT/'build'/folder
        checks[folder+'_binary']=digest(base/'player.exe')==report['binary_sha256']
        inputs=report['link_inputs_sha256']
        checks[folder+'_316_link_inputs']=len(inputs)==316 and all(digest(ROOT/p)==sha for p,sha in inputs.items())
    checks['original12_pass']=data[reports[0]]['result']=='PASS' and len(data[reports[0]]['checks'])==12
    checks['native_observer8_neutral']=data[reports[1]]['result']=='NEUTRAL' and all(data[reports[1]]['checks'].values())
    for index in (2,3):
        report=data[reports[index]]
        failed=[k for k,v in report['checks'].items() if not v]
        checks[f'retained_probe{index-1}_held_failure']=report['result']=='FAIL' and bool(failed) and all('held_accepted' in k for k in failed)
    checks['probe3_pass34']=data[reports[4]]['result']=='PASS' and len(data[reports[4]]['checks'])==34 and all(data[reports[4]]['checks'].values())
    contexts=data[reports[5]]
    checks['five_contexts_match_original']=contexts['result']=='PASS' and len(contexts['observations'])==5 and all(contexts['checks'].values())
    for width in (256,320):
        base=ROOT/'build/pride-title-readiness-probe3'
        for label,reference in [('held512to515','start515'),('start514','neutral'),('released512to514','neutral')]:
            checks[f'{width}_{label}_pcm']=pcm(base/f'{width}-{label}/audio.wav')==pcm(base/f'{width}-{reference}/audio.wav')
    checks['private16_unchanged']=digest(ROOT/'build/pride-title-upload16/player.exe')==data[reports[-1]]['binary_sha256']
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),ROOT/'tools/pride_arena_history.py',*[ROOT/'build'/p for p in reports]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                research_only=True,compiled_or_cold_qualification_claimed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

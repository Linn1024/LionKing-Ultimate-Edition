"""Qualify flight arithmetic, viewport presentation, cold replay and full routes."""
import csv
import json
import os
from pathlib import Path
import subprocess

from PIL import Image,ImageChops
from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-pickup-flight34';out=base/'integration';out.mkdir();checks={}
    labels=['capture','narrow-lle','wide-flight-view','wide-warm','wide-lle','wide-md-art','wide-cold','wide-cold2',
            'wide-full','wide-full-lle','complete-wide','complete-wide-lle','wide-camera','narrow-md-camera','flight-ui','flight-tree-view']
    reports={label:bound(base/label/'report.json') for label in labels}
    build=base/'build-report.json';bound(build)
    def equal(label,a,b,audio=True):
        a=base/a;b=base/b
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        if audio:checks[label+'_full_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
        checks[label+'_motion']=(a/'flight.csv').read_bytes()==(b/'flight.csv').read_bytes()
    equal('narrow_lle','capture','narrow-lle');equal('wide_native_camera_lle','wide-warm','wide-lle')
    equal('wide_md_camera_lle','wide-full','wide-full-lle');equal('full_wide_lle','complete-wide','complete-wide-lle')
    for label in ['capture','wide-warm']:
        arrivals=reports[label]['observations']['arrivals']
        checks[label+'_both_flights_arrive']={r['right'] for r in arrivals}=={'0','1'}
        checks[label+'_md_height']=all(r['y']=='20' for r in arrivals)
    for label in ['complete-wide','complete-wide-lle']:
        checks[label+'_next_level']=json.loads((base/label/'scene.json').read_text())['level']==1
        checks[label+'_active_movement']=reports[label]['observations']['calls']>0
    seed=base/'wide-flight-view';cold=base/'wide-cold2';warm=base/'wide-warm'
    checks['cold_guest']=hashes(cold/'run.log')==hashes(warm/'run.log')
    checks['cold_client']=pixels(cold/'window.png')==pixels(warm/'window.png')
    checks['cold_remaining_pcm']=pcm(cold/'audio.wav')==pcm(warm/'audio.wav')[len(pcm(seed/'audio.wav')):]
    def rows(folder):return list(csv.DictReader((folder/'flight.csv').open()))
    checks['cold_motion_suffix']=rows(cold)==rows(warm)[len(rows(seed)):]
    checks['wrong_unsliced_cold_retained']=hashes(base/'wide-cold/run.log')!=hashes(warm/'run.log')
    for label in ['wide-camera','narrow-md-camera']:
        checks[label+'_inapplicable_tape_retained']=reports[label]['result']=='FAIL' and reports[label]['checks']['exit'] and reports[label]['observations']['calls']==0
    checks['art_independent_guest']=hashes(seed/'run.log')==hashes(base/'wide-md-art/run.log')
    checks['art_independent_pcm']=pcm(seed/'audio.wav')==pcm(base/'wide-md-art/audio.wav')
    checks['art_independent_motion']=(seed/'flight.csv').read_bytes()==(base/'wide-md-art/flight.csv').read_bytes()
    box=ImageChops.difference(Image.open(seed/'window.png').convert('RGB'),Image.open(base/'wide-md-art/window.png').convert('RGB')).getbbox()
    checks['art_visible_difference']=box==(462,170,500,208)
    ui=reports['flight-ui'];checks['real_f12_both_sources']=ui['result']=='PASS' and len(ui['checks'])==13 and all(ui['checks'].values())
    tree=reports['flight-tree-view'];checks['actual_tree_view']=tree['result']=='PASS' and (base/'flight-tree-view/md-easy/node.png').is_file()
    aborted=base/'routes/aborted.json';partial=bound(aborted)
    previous=ROOT/'build/pride-audio-prime30/routes/report.json';old=bound(previous)
    checks['route_verifier_abort_retained']=partial['result']=='ABORTED'
    for label in ['256-snes','256-snes-lle','256-md','256-md-lle']:
        folder=base/'routes'/label;checks[label+'_complete']=json.loads((folder/'scene.json').read_text())['level']==1
        if label.startswith('256-snes'):
            ref=Path(old['commands'][label][old['commands'][label].index('--dump-window')+1]).parent
            checks[label+'_native_guest']=hashes(folder/'run.log')==hashes(ref/'run.log')
            checks[label+'_native_client']=pixels(folder/'window.png')==pixels(ref/'window.png')
            checks[label+'_native_pcm']=pcm(folder/'audio.wav')==pcm(ref/'audio.wav')
    # A genuine moving save must not enter another flight source's coordinate system.
    reject=out/'source-mismatch';reject.mkdir();profile=reject/'resources.ini'
    profile.write_text((seed/'resources.ini').read_text().replace('pickup_flight = md','pickup_flight = snes'))
    cmd=reports['wide-flight-view']['command'].copy()
    if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
    for flag,value in [('--resource-profile',profile),('--frames',1601),('--dump-window',reject/'window.png'),
                       ('--dump-scene',reject/'scene.json'),('--wav',reject/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
    cmd+=['--load',str(seed/'saved.state')]
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    with (reject/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    checks['moving_save_rejects_wrong_source']=r.returncode==8 and 'loaded_state=' not in (reject/'run.log').read_text()
    paths=[Path(__file__),build,previous,aborted,*[base/label/'report.json' for label in labels]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=dict(art_difference_box=box),rejection_command=cmd,
                full_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

"""Verify pristine level-select and cold restores before/during/after revival."""
import argparse
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import hashes,pixels

BASE=ROOT/'build/pride-restart'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--case',choices=('native-aot','md-lle'),default='native-aot');args=p.parse_args()
    native=args.case=='native-aot';start,width,graphics,mode=('snes',256,'native','aot') if native else ('md',320,'all','lle')
    out=BASE/'final/windows'/args.case;out.mkdir(parents=True,exist_ok=True)
    assert not (out/'report.json').exists(),'Use fresh proof directory'
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text());binary=BASE/'restart-sdl.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs']['sdl']['binary_sha256']
    reference=ROOT/'build/pride-repeat/scoped-windows'/f'{start}-{width}-{graphics}-{mode}'
    profile=out/'resources.ini';profile.write_bytes((reference/'resources.ini').read_bytes())
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape'
    common=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
        '--resource-profile',profile,'--config',config,'--no-pace','--no-audio','--no-record']
    if mode=='lle':common+=['--lle']
    commands={};exits={}
    def run(name,extra,frames=3000):
        folder=out/name;folder.mkdir(exist_ok=True)
        command=common+['--frames',frames,'--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
            '--wav',folder/'audio.wav','--wav-seconds','200']+extra
        commands[name]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(commands[name],cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=240)
        exits[name]=result.returncode;assert not result.returncode,(name,result.returncode)
        return folder
    selection=run('selection',['--practice-level',0],2)
    boot=out/'tlk_practice_boot.state';data=boot.read_bytes()
    assert data[:8]==b'PRHBOOT1' and len(data)>128
    assert read_rows(selection/'live-load.csv')==[dict(attempt_field='1',loaded_field='0',success='1')]
    baseline=run('baseline',['--input',tape])
    direct=run('direct',['--input',tape,'--load',boot])
    entry=1776 if native else 1777;second=2459 if native else 2458
    runs={'direct':direct}
    for name,at in (('before',1500),('owned',entry+269),('released',second+303)):
        runs[name]=run(name,['--input',tape,'--load-at',at,boot])
    expected=hashes(baseline/'run.log');baseline_audio=wav_data(baseline/'audio.wav')
    checks=dict(selection_boot=True,selection_load=True,baseline_guest=expected==hashes(reference/'run.log'),
        baseline_client=pixels(baseline/'window.png')==pixels(reference/'window.png'),
        baseline_pcm=baseline_audio==wav_data(reference/'audio.wav'))
    def scene_checks(a,b,label):
        for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','ground-entry.bin','ground-return.bin'):
            checks[label+'/'+name]=digest(a/name)==digest(b/name)
    scene_checks(baseline,reference,'baseline-first')
    scene_checks(baseline/f'scene-{second}',reference/f'scene-{second}','baseline-second')
    for name,folder in runs.items():
        checks[name+'/guest']=hashes(folder/'run.log')==expected
        checks[name+'/client']=pixels(folder/'window.png')==pixels(baseline/'window.png')
        loads=read_rows(folder/'live-load.csv')
        checks[name+'/load']=len(loads)==1 and loads[0]['success']=='1' and loads[0]['loaded_field']=='0'
        fresh=folder/'restart-1'
        scene_checks(fresh,baseline,name+'/first')
        scene_checks(fresh/f'scene-{second}',baseline/f'scene-{second}',name+'/second')
        pcm=wav_data(folder/'audio.wav')
        if name=='direct':checks[name+'/pcm']=pcm==baseline_audio
        else:
            prefix=len(pcm)-len(baseline_audio)
            checks[name+'/pcm']=prefix>0 and pcm[:prefix]==baseline_audio[:prefix] and pcm[prefix:]==baseline_audio
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,reference/'report.json',tape,ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',case=args.case,checks=checks,
        source_sha256=sources,binary_sha256=digest(binary),exits=exits,commands=commands,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.case,report['result'],'failed:',[n for n,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

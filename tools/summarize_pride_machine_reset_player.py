"""Bind owned mixed-player reset, source caches and native regression evidence."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-machine-player4';old=ROOT/'build/pride-machine-player'
    paths=[Path(__file__)];checks={};reports={}
    def read(path,result='PASS'):
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r.get('checks',{}).values()),path
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    read(ROOT/'build/pride-reset-cache-latest.json','PARTIAL')
    read(ROOT/'build/pride-cli-practice-latest.json','PARTIAL')
    original=read(old/'build-report.json','BUILT')
    build=read(base/'build-report.json','BUILT');native_path=ROOT/'build/pride-reset/fixed4/build-report.json';native=read(native_path,'BUILT')
    for report,folder in ((build,base),(original,old)):
        assert digest(folder/'machine.exe')==report['binary_sha256']
        for name,sha in report['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in native['production_sha256'].items():assert digest(ROOT/name)==sha,name
    for host,run in native['runs'].items():
        assert digest(native_path.parent/('native-'+host+'.exe'))==run['binary_sha256']
        for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    # The private executable reuses byte-identical game/audio/bridge/reset
    # objects and the exact new common runtime, not a different untested core.
    for unit in ('tlk_game','tlk_audio','tlk_reset','interp_bridge'):
        a=ROOT/'build/pride-reset/fixed3'/('sdl-'+unit+'.obj');b=native_path.parent/('sdl-'+unit+'.obj')
        checks['core/'+unit]=digest(a)==digest(b)==build['link_inputs_sha256'][str(a.relative_to(ROOT)).replace('\\','/')];paths.extend((a,b))
    common=native_path.parent/'sdl-common_rtl.obj'
    checks['core/common_runtime']=digest(common)==build['link_inputs_sha256'][str(common.relative_to(ROOT)).replace('\\','/')]
    for diagnostic in ('diagnostic','diagnostic-bus','diagnostic-bridge','diagnostic-hardware','diagnostic-field'):
        r=read(old/diagnostic/'report.json','OBSERVED')
        expected=[] if diagnostic=='diagnostic-field' else [dict(address='0x1f08',cold=130,reset=128)]
        checks[diagnostic+'/soft']=r['differences']['soft']==expected
        checks[diagnostic+'/init']=r['differences']['init']==expected
    a=(old/'diagnostic-hardware/cold/hardware.csv').read_text().splitlines()
    b=(old/'diagnostic-hardware/soft/hardware.csv').read_text().splitlines()
    first=next(i for i,(x,y) in enumerate(zip(a,b)) if x!=y)
    ca,cb=a[first].split(','),b[first].split(',')
    checks['hardware/first_refresh_difference']=first>1000 and ca[0]==cb[0]=='5' and int(cb[1])-int(ca[1])==40
    paths.extend((old/'diagnostic-hardware/cold/hardware.csv',old/'diagnostic-hardware/soft/hardware.csv'))
    # Preserve the original failed full replay as evidence even though the MD
    # verifier subsequently stopped on a duplicated CSV header at SnesInit.
    failed_stdout=ROOT/'build/pride-machine-player-md.log';raw=failed_stdout.read_bytes()
    text=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8');paths.append(failed_stdout)
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for kind in ('soft-aot','soft-lle','init-aot'):
        assert 'md '+kind+' exit0' in text
        folder=old/'md'/kind;control=old/'md'/('cold-lle' if kind.endswith('lle') else 'cold-aot')
        boundary_path=folder/'machine-boundary.json';boundary=json.loads(boundary_path.read_text());cut=boundary['audio_samples_before']*4
        controls=re.findall(pattern,(control/'run.log').read_text());observed=re.findall(pattern,(folder/'run.log').read_text())[2002:]
        checks['reproduced/'+kind+'/native_ram']=observed!=controls and len(observed)==len(controls)==3000
        checks['reproduced/'+kind+'/native_video_unchanged']=[r[1] for r in observed]==[r[1] for r in controls]
        checks['reproduced/'+kind+'/pcm']=wav_data(folder/'audio.wav')[cut:]!=wav_data(control/'audio.wav')
        paths.extend((boundary_path,control/'run.log',folder/'run.log',control/'audio.wav',folder/'audio.wav'))
    old_native=read(old/'native/report.json');assert old_native['binary_sha256']==original['binary_sha256']
    for case in ('native','md'):
        r=read(base/case/'report.json');assert r['binary_sha256']==build['binary_sha256']
        checks.update({case+'/'+k:v for k,v in r['checks'].items()})
        mode='lle' if case=='md' else 'aot';control=base/case/('cold-'+mode);prior=ROOT/'build/pride-cli-practice'/case/'after/author'
        checks[case+'/prior_cold_guest']=re.findall(pattern,(control/'run.log').read_text())==re.findall(pattern,(prior/'run.log').read_text())
        checks[case+'/prior_cold_pcm']=wav_data(control/'audio.wav')==wav_data(prior/'audio.wav')
        checks[case+'/prior_cold_client']=pixels(control/'window.png')==pixels(prior/'window.png')
        paths.extend((control/'run.log',prior/'run.log',control/'audio.wav',prior/'audio.wav',control/'window.png',prior/'window.png'))
    os_window=read(base/'os-window/report.json');assert os_window['binary_sha256']==build['binary_sha256']
    checks.update({'os-window/'+k:v for k,v in os_window['checks'].items()})
    profile=read(native_path.parent/'profile-noop/report.json');checks.update({'profile/'+k:v for k,v in profile['checks'].items()})
    for relative,host in (('early-state/report.json','headless'),('windows/report.json','sdl')):
        r=read(native_path.parent/relative);identity=r['binary_sha256'] if host=='headless' else r['after_binary_sha256']
        assert identity==native['runs'][host]['binary_sha256'];checks.update({relative+'/'+k:v for k,v in r['checks'].items()})
    for filename in ('play-report.json','allbugs-report.json'):
        path=native_path.parent/'native/gates'/filename;r=read(path);prior_path=ROOT/'build/pride-reset/fixed3/native/gates'/filename;prior=read(prior_path)
        assert r['binary_sha256']==native['runs']['headless']['binary_sha256'] and r['verifier_sha256']==digest(ROOT/'tools/verify_native_routes.py')
        checks[filename+'/prior_endpoints']=r['routes']==prior['routes']
        if filename=='allbugs-report.json':
            ram=[path.parent/'allbugs-aot.ram',path.parent/'allbugs-lle.ram',prior_path.parent/'allbugs-aot.ram']
            checks['allbugs/prior_every_field_ram']=len({digest(p) for p in ram})==1;paths.extend(ram)
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    result=dict(result='PARTIAL',checks=checks,checks_passed=len(checks),reports_sha256=reports,
        source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
        private_owned_machine_reset_cases=8,post_reset_native_fields=24000,complete_pcm_and_md_stems_exact=True,
        complete_clients_and_scene_evidence_exact=True,actual_user_reset_control_verified=False,
        os_client_after_reset_captured_and_inspected=True,
        hardware_audio_device_queue_reset_verified=False,legacy_save_migration_verified=False,
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-machine-reset-player-latest.json').write_text(json.dumps(result,indent=2)+'\n');print('PARTIAL owned machine reset:',len(checks),'checks; 24000 restarted fields',flush=True)


if __name__=='__main__':main()

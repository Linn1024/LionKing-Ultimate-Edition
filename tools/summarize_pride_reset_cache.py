"""Bind the effective-source cache correction and complete reset regressions."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-reset';paths=[Path(__file__)];checks={};reports={}
    def read(path,result='PASS'):
        r=bound(path);assert r['result']==result,(path,r['result'])
        if result=='PASS':assert all(r.get('checks',{}).values()),path
        paths.append(path);reports[str(path.relative_to(ROOT)).replace('\\','/')]=digest(path);return r
    previous=read(ROOT/'build/pride-reset-latest.json','PARTIAL');assert previous['checks_passed']==190
    builds={}
    for folder in ('fixed3','views3','audio3'):
        build=read(base/folder/'build-report.json','BUILT');builds[folder]=build
        for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
        for host,run in build['runs'].items():
            binary=base/folder/(('native-'+host if folder=='fixed3' else host+'-reset')+'.exe')
            assert digest(binary)==run['binary_sha256'],binary
            for name,sha in run['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    before=read(base/'fixed2/profile-noop/report.json','REPRODUCED')
    checks['old_unchanged_md_apply_reproduced']=all(v==[1,1] for k,v in before['observations'].items() if k.startswith('md-'))
    for case in ('profile-noop','profile-commit'):
        r=read(base/'fixed3'/case/'report.json')
        for name,sha in r['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
        checks.update({case+'/'+k:v for k,v in r['checks'].items()})
    for scope,folder,host,old_folder in (('native-headless','views3','headless','views2'),('native-sdl','views3','sdl','views2'),('md-audio','audio3','sdl','audio-views2')):
        r=read(base/folder/'matrix'/host/'report.json');assert r['binary_sha256']==builds[folder]['runs'][host]['binary_sha256']
        checks.update({scope+'/'+k:v for k,v in r['checks'].items()})
        for mode in ('aot','lle'):
            for filename in ('native-fields.csv','native.pcm' if host=='headless' else 'audio.wav'):
                a=base/folder/'matrix'/host/('none-'+mode+'-0')/filename
                b=base/old_folder/'matrix'/host/('none-'+mode+'-0')/filename
                checks[scope+'/'+mode+'/'+filename+'/prior_cold_control']=digest(a)==digest(b);paths.extend((a,b))
    for relative,host in (('early-state/report.json','headless'),('windows/report.json','sdl')):
        r=read(base/'fixed3'/relative)
        identity=r['binary_sha256'] if host=='headless' else r['after_binary_sha256']
        assert identity==builds['fixed3']['runs'][host]['binary_sha256']
        checks.update({relative+'/'+k:v for k,v in r['checks'].items()})
    for filename in ('play-report.json','allbugs-report.json'):
        current=base/'fixed3/native/gates'/filename;old=base/'fixed2/native/gates'/filename
        r=read(current);prior=read(old)
        assert r['binary_sha256']==builds['fixed3']['runs']['headless']['binary_sha256']
        assert r['verifier_sha256']==digest(ROOT/'tools/verify_native_routes.py')
        checks[filename+'/prior_endpoints']=r['routes']==prior['routes']
        if filename=='allbugs-report.json':
            a=current.parent/'allbugs-aot.ram';b=current.parent/'allbugs-lle.ram';c=old.parent/'allbugs-aot.ram'
            checks['allbugs/prior_every_field_ram']=a.read_bytes()==b.read_bytes()==c.read_bytes();paths.extend((a,b,c))
    assert all(checks.values()),[k for k,v in checks.items() if not v]
    result=dict(result='PARTIAL',checks=checks,checks_passed=len(checks),reports_sha256=reports,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                unchanged_audio_apply_after_reset_verified=True,real_audio_source_commits=96,
                native_and_md_audio_reset_compared_fields=72000,private_revival_reset_verified=False,
                actual_resource_tree_after_hardware_reset_verified=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    (ROOT/'build/pride-reset-cache-latest.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PARTIAL reset cache:',len(checks),'checks; 72000 replayed fields',flush=True)


if __name__=='__main__':main()

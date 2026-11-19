"""Bind installed title data, genuine decoder evidence and final candidate graphs."""
import json
import hashlib
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-title-native-bindings';out.mkdir();checks={}
    names=['pride-title-native-payloads/report.json','pride-title-native-installed/verification/report.json',
           'pride-title-native-installed/setup-verification/report.json','pride-title-native-installed/window/report.json',
           'pride-title-native14/build-report.json','pride-title-native14/continue-regressions/report.json',
           'pride-title-native14/verification/report.json','pride-title-native15/build-report.json',
           'pride-title-native15/verification/report.json','pride-title-native15/contexts/report.json',
           'pride-game-over-title-evidence2/report.json','pride-game-over-bindings/report.json']
    reports={}
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for candidate in ('pride-title-native14','pride-title-native15'):
        build=reports[candidate+'/build-report.json']
        checks[candidate+'_binary']=digest(ROOT/'build'/candidate/'player.exe')==build['binary_sha256']
        checks[candidate+'_315_link_inputs']=len(build['link_inputs_sha256'])==315 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    checks['retained_handoff_save_failure']=reports['pride-title-native14/verification/report.json']['result']=='FAIL'
    for name in ['pride-title-native-installed/verification/report.json','pride-title-native-installed/setup-verification/report.json',
                 'pride-title-native-installed/window/report.json','pride-title-native14/continue-regressions/report.json',
                 'pride-title-native15/verification/report.json','pride-title-native15/contexts/report.json']:
        r=reports[name];checks[name+'_passes']=r['result']=='PASS' and all(r['checks'].values())
    data=ROOT/'build/pride-title-native-installed/setup-verification/Game data & native loads';manifest=data/'install.json';info=json.loads(manifest.read_text())
    checks['installed_v2_twenty_payloads']=info['native_final_assets']['version']==2 and info['native_final_assets']['payloads']==20
    checks['installed_native_package']=digest(data/info['native_final_assets']['file'])==info['native_final_assets']['sha256']=='74364047aecdcb16cd10bead0bcf8538b845e5881f7bb54920c3a03fd7ef80ce'
    checks['md_package_unchanged']=digest(data/info['menu_assets']['file'])=='f1e4e1f4fed4f19642b545e402c359d3fa6d1b457d2205f2470cbea1fc0bd075'
    helper=ROOT/'build/pride-title-native-installed/cmake/tlk_prepare_final_assets.exe'
    checks['published_helper_matches_fresh_graph']=digest(ROOT/'dist/PrepareFinalAssets.exe')==digest(helper)=='29cd5b80913a6011ec3828f5a2e90cf686dfaf79da8b94c324cf8faf41b8c693'
    checks['old_helper_archived']=digest(ROOT/'build/pride-title-native-baseline/dist/PrepareFinalAssets.exe')=='4dfa39a2d902f820dab445470ea97d7e611b2187d62afefb569c51bb9658072b'
    graph=ROOT/'build/pride-title-native-installed/cmake'
    compdb=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb'],cwd=graph))
    entries=[r for r in compdb if r.get('file','').endswith('.c')]
    checks['fresh_helper_eight_objects']=len(entries)==8 and all((graph/r['output']).is_file() for r in entries)
    input_hashes={str((graph/r['file']).resolve().relative_to(ROOT)).replace('\\','/'):digest(graph/r['file']) for r in entries}
    object_hashes={str((graph/r['output']).resolve().relative_to(ROOT)).replace('\\','/'):digest(graph/r['output']) for r in entries}
    old=(ROOT/'build/pride-title-native14/verification/320-434/saved.state').read_bytes()
    new=(ROOT/'build/pride-title-native15/verification/320-434/saved.state').read_bytes()
    side=64*224*4
    checks['old_absent_outgoing_margins_nonzero']=any(old[-2*side:-side])
    checks['new_absent_outgoing_margins_canonical']=not any(new[-2*side:-side])
    checks['strict_absent_canvas_validation_retained']='if(!present[slot])' in (ROOT/'engine/runner/pride/final/pride_final_save.inc').read_text()
    malformed=bytearray(new);malformed[-2*side]=1;malformed[64:96]=bytes(32);malformed[64:96]=hashlib.sha256(malformed).digest()
    bad=out/'absent-side.state';bad.write_bytes(malformed)
    command=reports['pride-title-native15/verification/report.json']['commands']['320-cold434to435'].copy()
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    for flag,value in [('--config',out/'host.ini'),('--load',bad),('--dump-window',out/'unexpected.png'),
                       ('--dump-scene',out/'unexpected.json'),('--wav',out/'unexpected.wav')]:command[command.index(flag)+1]=str(value)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env['TLK_FINAL_MD_ART']='1'
    with (out/'rejection.log').open('wb') as log:
        result=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    checks['resealed_absent_side_rejects_before_guest']=result.returncode==8 and b'loaded_state=' not in (out/'rejection.log').read_bytes()
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['framework_submodules_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine',text=True).strip()
    paths=[Path(__file__),manifest,helper,ROOT/'dist/PrepareFinalAssets.exe',ROOT/'scripts/Setup.ps1',*[ROOT/'build'/n for n in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,helper_compile_commands=entries,malformed_command=command,
                helper_source_sha256=input_hashes,helper_object_sha256=object_hashes,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True);assert all(checks.values())

if __name__=='__main__':main()

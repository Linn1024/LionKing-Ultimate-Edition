"""Final release identities; run after public OS inspection and documentation."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';out=base/'bindings';out.mkdir();checks={};paths=[Path(__file__)]
for name in ('parent-verification','windows-ui','fights144-qualification','boundary159','routes156-qualification','native75','allbugs-verification','package-play','publication','cmd-play','game-window-verification','mixed-window'):
    p=base/name/'report.json';r=bound(p);paths.append(p);checks[name]=r['result']=='PASS' and all(r['checks'].values())
for name in ('pride-hyena-entrance132','pride-hyena-countdown133','pride-hyena-entrance153-live-decision'):
    p=ROOT/'build'/name/'report.json';r=bound(p);paths.append(p);checks[name]=r['result']=='PASS' and all(r['checks'].values())
for name in ('pride-hyena-entrance149-observer/build-report.json','pride-hyena-entrance150-boundary/report.json','pride-hyena-entrance157-drop/report.json','pride-hyena-entrance158-reapproach/report.json'):
    p=ROOT/'build'/name;r=bound(p);paths.append(p);checks[name]=r['result'] in ('BUILT','CAPTURED') and all(r.get('checks',{}).values())
for name in ('routes148/attempt-report.json','routes154-qualification/report.json'):
    p=base/name;r=bound(p);paths.append(p);checks[name+'_failed_evidence_retained']=r['result']=='FAIL'
bp=base/'build-report.json';b=bound(bp);paths.append(bp)
checks['all324_link_inputs_exact']=len(b['link_inputs_sha256'])==324 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
checks['320_prior_inputs_retained']=b['unchanged_public118_inputs']==320
checks['public_binary_exact']=digest(base/'player.exe')==digest(ROOT/'dist/installed-preview139/LionKing.exe')==b['binary_sha256']
checks['public_launcher_selects139']='dist/installed-preview139' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
generation=ROOT/'build/pride-hyena-entrance138-generation';gp=generation/'generation-report.json';g=bound(gp);paths.append(gp)
checks['compiled_hook_emitted_once']=(generation/'hooks/bankc0_part17_v2.c').read_text().count('PrideSceneCompiledPreOpcode(cpu,0xC03BDBu)')==1
checks['hook_declared_in_maintained_manifest']='0xc03bdb' in json.loads((ROOT/'engine/recomp/pride_hooks.json').read_text())['hook_pcs']
package=ROOT/'dist/installed-preview139/package-report.json';bound(package);paths.append(package)
paths += [ROOT/p for p in b['link_inputs_sha256']]
paths += [ROOT/p for p in ('README.md','docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-hyena-entrance.md','docs/pride-hyena-probe.md','docs/resource-tree-inheritance.md','docs/launchers.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1','engine/runner/tlk_hyena_entrance.c','engine/runner/tlk_hyena_entrance.h','engine/runner/tlk_hyena_entrance_policy.h','engine/runner/tlk_resources.c','engine/runner/tlk_resource_parent.h','engine/recomp/pride_hooks.json','engine/recomp/pride_program_contract.json','engine/cmake/TlkPrideFinalPlayer.cmake','engine/cmake/final-frontend-patches/hyena-entrance-window.hunks','tools/pride_arena_history.py')]
paths += list((ROOT/'tools').glob('*pride_hyena_entrance*.py'))
paths += [ROOT/'tools'/p for p in ('verify_pride_checkpoint_cmd53.py','verify_pride_checkpoint_public_window53.py','capture_pride_mixed_launcher66.py','verify_pride_checkpoint_package53.py','verify_pride_menu_output83_package.py','verify_pride_hyena_probe99_routes.py','verify_pride_installed_native75.py','build_pride_checkpoint52_allbugs.py','verify_pride_checkpoint52_allbugs.py','verify_pride_music_ui65.py')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published_sha256=b['binary_sha256'],full_first_level_complete=False,current_build_saves_only=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)

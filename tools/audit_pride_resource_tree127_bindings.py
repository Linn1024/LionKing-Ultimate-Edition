"""Final corrected resource-tree publication bindings; run after public docs/OS checks."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-resource-tree118';out=base/'bindings';out.mkdir();checks={};paths=[Path(__file__)]
for name in ['parent-verification','windows-ui119','routes99','native75','allbugs-verification','package-play','publication','cmd-play','game-window-verification','mixed-window']:
    p=base/name/'report.json';r=bound(p);paths.append(p);checks[name]=r['result']=='PASS' and all(r['checks'].values())
for name in ['pride-hyena-probe103-original','pride-hyena-probe103-component','pride-hyena-probe103/fights104','pride-hyena-probe103/windows-ui-qualification104']:
    p=ROOT/'build'/name/'report.json';r=bound(p);paths.append(p);checks[name]=r['result']=='PASS' and all(r['checks'].values())
p=ROOT/'build/pride-resource-parents117/report.json';r=bound(p);paths.append(p)
checks['original_parent_bug_retained']=r['result']=='RESOURCE_PARENT_MISMATCHES_OBSERVED' and any(x['id']=='graphics.sprites.pickups.continue_token.frames' and x['parent_id']=='audio.effects.options_adjustment' for x in r['mismatches'])
bp=base/'build-report.json';b=bound(bp);paths.append(bp)
checks['all323_link_inputs_bound']=len(b['link_inputs_sha256'])==323 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
checks['only_resources_object_replaced']=b['unchanged_candidate103_inputs']==322
checks['public_binary_exact']=digest(ROOT/'dist/installed-preview118/LionKing.exe')==digest(base/'player.exe')==b['binary_sha256']
checks['public_launcher_selects118']='dist/installed-preview118' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
p=ROOT/'dist/installed-preview118/package-report.json';bound(p);paths.append(p)
paths += [ROOT/p for p in b['link_inputs_sha256']]
paths += [ROOT/p for p in ['engine/runner/tlk_resources.c','engine/runner/tlk_resource_parent.h','engine/tests/resource_parent_test.c','engine/runner/tlk_hyena_probe.c','engine/runner/tlk_hyena_probe.h','engine/runner/tlk_hyena_probe_policy.h','engine/cmake/final-frontend-patches/hyena-walking-probe.hunks','engine/cmake/TlkPrideFinalPlayer.cmake','README.md','docs/HANDOFF.md','docs/pride-lands-status.md','docs/resource-tree-inheritance.md','docs/pride-hyena-probe.md','docs/launchers.md','engine/docs/devlog.md','scripts/RunInstalledPreview.ps1']]
paths += [p for p in (ROOT/'tools').glob('*pride_resource*.py')]
paths += [ROOT/'tools'/p for p in ['verify_pride_checkpoint_cmd53.py','verify_pride_checkpoint_public_window53.py','capture_pride_mixed_launcher66.py','verify_pride_checkpoint_package53.py','verify_pride_menu_output83_package.py','package_pride_hyena_probe107.py','build_pride_checkpoint52_allbugs.py','verify_pride_checkpoint52_allbugs.py','verify_pride_hyena_probe99_routes.py','verify_pride_hyena_probe103_native75.py','verify_pride_hyena_probe97_native75.py','verify_pride_menu_enable86_native75.py','verify_pride_menu_output83_native75.py','verify_pride_hyena_voice72_native75.py','verify_pride_installed_native75.py']]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,published_sha256=b['binary_sha256'],full_first_level_complete=False,current_build_saves_only=True,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)

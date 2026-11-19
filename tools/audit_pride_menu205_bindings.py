"""Bind private native-menu progress without promoting incomplete capability."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

out=ROOT/'build/pride-menu205-bindings'
out.mkdir()
checks={}
paths=[Path(__file__)]
for name,expected in (
    ('pride-menu197-observer/build-report.json','BUILT'),
    ('pride-menu198-clocks/report.json','PASS'),
    ('pride-menu199-windows/report.json','PASS'),
    ('pride-menu200-native-art/build-report.json','BUILT'),
    ('pride-menu201-native-art/report.json','PASS'),
    ('pride-menu202-art-windows/report.json','PASS'),
    ('pride-menu203-art-pixels/report.json','PASS'),
    ('pride-porcupine196-bindings/report.json','PASS'),
    ('pride-contact176-bindings/report.json','PASS'),
    ('pride-hyena-entrance139/bindings/report.json','PASS')):
    p=ROOT/'build'/name;r=bound(p);paths.append(p)
    checks[name]=r['result']==expected and all(r.get('checks',{}).values())
    if expected=='BUILT':
        checks[name+'_binary_exact']=digest(p.parent/'player.exe')==r['binary_sha256']
        checks[name+'_all324_inputs_exact']=len(r['link_inputs_sha256'])==324 and all(digest(ROOT/q)==sha for q,sha in r['link_inputs_sha256'].items())
bp=ROOT/'build/pride-hyena-entrance139/build-report.json'
b=bound(bp);paths.append(bp)
checks['published139_binary_exact']=digest(ROOT/'dist/installed-preview139/LionKing.exe')==digest(bp.parent/'player.exe')==b['binary_sha256']
checks['all324_public_link_inputs_unchanged']=len(b['link_inputs_sha256'])==324 and all(digest(ROOT/p)==sha for p,sha in b['link_inputs_sha256'].items())
launcher=ROOT/'scripts/RunInstalledPreview.ps1'
checks['public_launcher_still139']='dist/installed-preview139' in launcher.read_text() and 'TLK_NATIVE_MENU200' not in launcher.read_text()
checks['capability_still_reports_native_menu_art']='native menu artwork' in (ROOT/'engine/runner/tlk_resources.c').read_text()
checks['framework_submodules_clean']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
paths += [ROOT/p for p in b['link_inputs_sha256']]
paths += [ROOT/p for p in (
    'docs/HANDOFF.md','docs/pride-lands-status.md','docs/pride-final-menu-native-timing.md',
    'docs/pride-final-menu-drawing.md','docs/pride-final-menu-layout.md','docs/pride-final-menu-yes.md',
    'docs/background-audit.md','engine/docs/devlog.md','tools/pride_arena_history.py',
    'scripts/RunInstalledPreview.ps1','engine/runner/tlk_resources.c')]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',
    checks=checks,current_player_sha256=b['binary_sha256'],full_first_level_complete=False,
    public_capability_or_gameplay_changed=False,
    scope='Private installed MD Game Over on native timing, bounded256 loop/fade/retirement proof. '
          'Native Continue,320 bridge and source-change/current-save lifecycle still required. '
          'Published139 and existing immediate report identities preserved; no new full release-gate claim.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)

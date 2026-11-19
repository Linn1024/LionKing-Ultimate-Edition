"""Bind the private Continue-token candidate; do not imply release qualification."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-continue-token47';out=base/'candidate-audit';out.mkdir()
    checks={};paths=[Path(__file__)];counts={}
    scopes={
        'effect_inventory':ROOT/'build/pride-effect-coverage/report.json',
        'dynamic_packets':ROOT/'build/pride-effect-coverage/dynamic-packets2/qualification/report.json',
        'sun_owners':ROOT/'build/pride-effect-coverage/sun-owners2/report.json',
        'map':ROOT/'build/pride-continue-token-map/report.json',
        'component':ROOT/'build/pride-continue-token46/component/report.json',
        'setup':ROOT/'build/pride-continue-token-assets/setup-verification/report.json',
        'runtime':base/'artwork-verification/report.json',
        'guards':base/'guards/report.json',
        'full_route':base/'full-route/qualification/report.json',
        'window':base/'presentation/report.json',
        'visible_window':base/'presentation2/report.json',
        'live_ui':base/'live-ui/report.json'}
    for name,path in scopes.items():
        report=bound(path);paths.append(path);checks[name]=report['result']=='PASS' and all(report['checks'].values());counts[name]=len(report['checks'])
    gates={}
    for name in ('native75','allbugs-verification'):
        path=base/name/'report.json'
        if path.exists():
            report=bound(path);paths.append(path);checks[name]=report['result']=='PASS' and all(report['checks'].values());gates[name]=report['result']
        else:gates[name]='RUNNING; no pass claimed'
    build_path=base/'build-report.json';build=bound(build_path);paths.append(build_path)
    checks['all322_inputs_bound']=len(build['link_inputs_sha256'])==322 and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    checks['private_binary_exact']=digest(base/'player.exe')==build['binary_sha256']
    checks['public44_binary_preserved']=digest(ROOT/'dist/installed-preview44/LionKing.exe')=='6f98ebffdca1415e95bdc275e81b50e7531510d157976f4f1919279d6583b7be'
    checks['distributed44_helper_preserved']=digest(ROOT/'dist/PrepareSpriteAssets.exe')=='2193f1f56af19fe990aabec1375eeef8f8aa066481244a71135b5c854475c63f'
    manifest=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
    checks['default44_sprite_data_preserved']=digest(ROOT/'game-data'/manifest['sprite_assets']['file'])==manifest['sprite_assets']['sha256']=='54f09308890314a40e20871b67937843ce842f872c7592dbabb472ad72a8050a'
    checks['public_launcher_still44']='dist/installed-preview44' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    failure=ROOT/'build/pride-continue-token46/artwork-verification/failure.json';checks['old_save_failure_retained']=bound(failure)['result']=='FAIL';paths.append(failure)
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,report_check_counts=counts,broad_gates=gates,
                private_candidate_only=True,published=False,full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,gates,flush=True)


if __name__=='__main__':main()

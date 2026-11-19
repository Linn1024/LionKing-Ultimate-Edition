"""Bind pristine-menu saving and the current complete first-level route checks."""
import json
from pathlib import Path
import re

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_save_identity_owned import contract_identity
from summarize_pride_practice import bound
from verify_pride_audio_state import wav_data
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-launch4';bp=base/'build-report.json';build=bound(bp);checks={};paths=[Path(__file__),bp]
    checks['binary_bound']=digest(base/'player.exe')==build['binary_sha256']
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    checks['all_link_inputs_bound']=True
    contract=json.loads((base/'save-compatibility.json').read_text())
    checks['identity_bound']=contract_identity(contract)==build['save_compatibility_sha256']
    for name in ('engine/runner/tlk_pride_save_cold.inc','engine/runner/tlk_pride_save_dispatch.inc'):
        checks[name+'/bound']=contract['private_context_sources_sha256'][name]==digest(ROOT/name)
    total=0
    for name in ('menu-save/report.json','menu-slots/report.json','menu-source/report.json','preview-slots/report.json','native-slots/report.json','completion2/report.json'):
        path=base/name;r=bound(path);paths.append(path);assert r['result']=='PASS',name
        for key,value in r['checks'].items():checks[name+'/'+key]=value
        total+=r.get('native_fields_compared',0)
    old_path=ROOT/'build/pride-launch3/completion/report.json';old=bound(old_path);paths.append(old_path);assert old['result']=='PASS'
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    for width in (256,320):
        for mode in ('aot','lle'):
            a=old_path.parent/str(width)/mode;b=base/'completion2'/str(width)/mode
            checks[f'{width}/{mode}/preceding_complete_fields']=re.findall(pattern,(a/'run.log').read_text())==re.findall(pattern,(b/'run.log').read_text())
            checks[f'{width}/{mode}/preceding_complete_pcm']=wav_data(a/'route.wav')==wav_data(b/'route.wav')
            for what in ('guest','window'):checks[f'{width}/{mode}/preceding_{what}']=pixels(a/(what+'.png'))==pixels(b/(what+'.png'))
    preview_path=ROOT/'build/pride-launch2/build-report.json';preview=bound(preview_path);paths.append(preview_path)
    checks['published_preview_unchanged']=digest(ROOT/'dist/development-preview/LionKing.exe')==preview['binary_sha256']
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    checks['installed_players_unchanged']=True
    report=dict(result='PARTIAL' if all(checks.values()) else 'INCOMPLETE',checks=checks,check_count=len(checks),native_fields_compared=total,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                normal_first_level_completion_verified=True,production_cmake_integration_complete=False,public_player_enabled=False,
                full_first_level_fidelity_complete=False,
                limitations=['Native menu save fallback is limited to before the first Pride bank/decoder capture; partial capture/loading is not serialized.',
                             'No full native75/All Bugs rerun on this candidate; no package update.',
                             'Final/fall lifecycle and full original movement/combat/enemy/particle/voice fidelity remain open.'])
    (ROOT/'build/pride-cold-saves-latest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',total,'compared fields',flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

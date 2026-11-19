"""Bind the scene-aware save change and its deliberately limited evidence."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_save_identity_owned import contract_identity
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-launch3';bp=base/'build-report.json';build=bound(bp);checks={};sources=[Path(__file__),bp]
    checks['candidate_binary_bound']=digest(base/'player.exe')==build['binary_sha256']
    for name,sha in build['link_inputs_sha256'].items():assert digest(ROOT/name)==sha,name
    checks['every_link_input_bound']=True
    contract=json.loads((base/'save-compatibility.json').read_text())
    checks['owned_dispatch_bound']=contract['private_context_sources_sha256']['engine/runner/tlk_pride_save_dispatch.inc']==digest(ROOT/'engine/runner/tlk_pride_save_dispatch.inc')
    checks['contract_identity_bound']=contract_identity(contract)==build['save_compatibility_sha256']
    total=0
    for name in ('scene-saves/audit.json','regression/report.json','preview-slots/report.json','native-slots/report.json','save-sources/report.json','owned-exit/report.json'):
        path=base/name;r=bound(path);sources.append(path);assert r['result']=='PASS',name
        for key,value in r['checks'].items():checks[name+'/'+key]=value
        total+=r.get('native_fields_compared',0)
    old=bound(ROOT/'build/pride-launch2/build-report.json');sources.append(ROOT/'build/pride-launch2/build-report.json')
    checks['published_preview_unchanged']=digest(ROOT/'dist/development-preview/LionKing.exe')==old['binary_sha256']
    for name,sha in build['production_sha256'].items():assert digest(ROOT/name)==sha,name
    checks['installed_players_unchanged']=True
    report=dict(result='PARTIAL' if all(checks.values()) else 'INCOMPLETE',checks=checks,check_count=len(checks),native_fields_compared=total,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
                limitations=['Native fallback on save added for nonzero level IDs only; title/Pride transitions remain unaudited.',
                             'No full native75 route or All Bugs rerun on this candidate; four cold paths retain12000 every-field hashes/PCM/clients.',
                             'No public package update or production CMake integration.',
                             'Full original first-level fidelity and final/fall lifecycle audit remain open.'],
                production_cmake_integration_complete=False,public_player_enabled=False,full_first_level_fidelity_complete=False)
    path=ROOT/'build/pride-scene-saves-latest.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'checks',total,'compared fields',flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

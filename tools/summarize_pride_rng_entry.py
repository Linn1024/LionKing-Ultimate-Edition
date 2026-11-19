"""Retain lifecycle findings while selecting the simpler normal-entry component."""
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    base=ROOT/'build/pride-rng-lifecycle';old_path=base/'audit.json';old=bound(old_path);assert old['result']=='PARTIAL' and all(old['checks'].values())
    component_path=base/'entry-component/report.json';component=bound(component_path);assert component['result']=='PASS'
    reloads=[r for case in old['native_clear_milestones'] for r in case['clears'] if r['descriptor'] in (0xc00387,0xc0080d)]
    checks=dict(all_observed_pride_reloads_skip_low_clear=bool(reloads) and all(r['x']==0x1fff for r in reloads),
                original_instruction_component_cases=component['original_instruction_cases']==192,
                no_component_installed=not component['component_installed'])
    test=base/'rng_entry_test.exe';result=subprocess.run([str(test),str(ROOT/'Lion King, The (USA).sfc'),str(ROOT/'Lion King, The (World).md')],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True,timeout=30)
    log=base/'entry-component/unit.log';log.write_bytes(result.stdout);checks['guard_cpu_immutability_idempotence']=b'PASS 1570' in result.stdout
    paths=[Path(__file__),old_path,component_path,ROOT/'engine/runner/tlk_rng_entry.c',ROOT/'engine/runner/tlk_rng_entry.h',ROOT/'engine/tests/rng_entry_test.c',test]
    report=dict(result='PARTIAL' if all(checks.values()) else 'INCOMPLETE',checks=checks,original_md_reseed_fields=old['original_md_reseed_fields'],
        native_pride_reload_clear_milestones=reloads,canonical_component='engine/runner/tlk_rng_entry.c',
        superseded_component='engine/runner/tlk_rng_scene.c',reason='Observed native revival reloads skip the low-byte clear already; no temporary CPU state is needed for the normal-entry-only choice.',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={'entry-component/unit.log':digest(log)},
        component_installed=False,resource_capability_enabled=False,full_first_level_fidelity_complete=False)
    (base/'entry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'build/pride-rng-entry-latest.json').write_text(json.dumps(dict(result=report['result'],component_installed=False,
        full_first_level_fidelity_complete=False,source_sha256={(base/'entry-audit.json').relative_to(ROOT).as_posix():digest(base/'entry-audit.json')}),indent=2)+'\n')
    print(report['result'],'canonical normal-entry component;1570 guard checks/192 original cases; native reloads retain seed',flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

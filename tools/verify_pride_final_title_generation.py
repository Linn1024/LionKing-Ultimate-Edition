"""Check optional extra hook units while preserving ordinary generation."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out = ROOT/'build/pride-final-title-generation-checks'
    out.mkdir()
    normal = ROOT/'build/pride-final-title-normal-generation'
    final = ROOT/'build/pride-final-title-hooks2'
    prior = ROOT/'build/pride-final-maintained-generation2/normal'
    reports = [folder/'generation-report.json' for folder in (normal, final, prior)]
    rows = [bound(path) for path in reports]
    validator = ROOT/'engine/scripts/validate_pride_generation.py'
    for folder in (normal, final):
        with (out/(folder.name+'.log')).open('wb') as log:
            subprocess.run([sys.executable, str(validator), '--rom', str(ROOT/'Lion King, The (USA).sfc'),
                            '--generation', str(folder)], stdout=log, stderr=subprocess.STDOUT, check=True)
    names = sorted(path.name for path in (normal/'hooks').glob('bank*.c'))
    checks = dict(default_137_units_unchanged=len(names) == 137 and all(
                      digest(normal/'hooks'/name) == digest(prior/'hooks'/name) for name in names),
                  default_15_instrumented=len(rows[0]['instrumented_units']) == 15 and rows[0]['final_scene_hooks'] is False,
                  final_16_instrumented=len(rows[1]['instrumented_units']) == 16 and rows[1]['final_scene_hooks'] is True,
                  explicit_extra_title_unit='bankc4_part1c_v2.c' in rows[1]['instrumented_units'],
                  rng_137_units_unchanged=len(list((normal/'rng').glob('bank*.c'))) == 137 and all(
                      digest(normal/'rng'/name) == digest(prior/'rng'/name) for name in names),
                  configured_program_unchanged=rows[0]['program_contract_sha256'] == rows[1]['program_contract_sha256'] == rows[2]['program_contract_sha256'])
    paths = [Path(__file__), validator, *reports, ROOT/'engine/scripts/generate_pride_final_player.py']
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], checks, flush=True)
    assert all(checks.values()), checks


if __name__ == '__main__':
    main()

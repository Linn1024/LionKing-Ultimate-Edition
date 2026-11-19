"""Check fresh patch application preserves candidate41's final-target C tokens."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base = ROOT/'build/pride-installed-cache41'
    build_path = base/'build-report.json'
    build = bound(build_path)
    out = base/'scope-verification'
    out.mkdir()
    patches = ROOT/'engine/cmake/game-patches'
    subprocess.run(['python', str(ROOT/'engine/scripts/apply_runtime_patches.py'), '--patches', str(patches),
                    '--snesrecomp', str(ROOT/'engine'), '--out', str(out/'game')], cwd=ROOT, check=True)
    commands = {}
    for label, source, extra in [('candidate-final', base/'game/tlk_resources.c', []),
                                  ('fresh-final', out/'game/tlk_resources.c', []),
                                  ('ordinary-target', out/'game/tlk_resources.c', ['-UTLK_PRIDE_FINAL_AVAILABLE'])]:
        cmd = build['compiles']['resources'].copy()
        cmd[cmd.index('-c')] = '-E'
        for flag, value in [('-E', source), ('-o', out/(label+'.i')),
                            ('-MF', out/(label+'.d')), ('-MT', out/(label+'.obj'))]:
            cmd[cmd.index(flag)+1] = str(value)
        cmd += ['-P', *extra]
        commands[label] = cmd
        with (out/(label+'.log')).open('wb') as log:
            subprocess.run(cmd, cwd=ROOT/'build/pride-final-standalone', stdout=log,
                           stderr=subprocess.STDOUT, check=True, timeout=120)
    checks = dict(final_preprocessed_source_exact=(out/'candidate-final.i').read_bytes() == (out/'fresh-final.i').read_bytes(),
                  ordinary_target_does_not_reject_into_a_legacy_frontend='Installed scene data is missing or invalid.' not in (out/'ordinary-target.i').read_text(),
                  final_target_strict_guard_present='Installed scene data is missing or invalid.' in (out/'fresh-final.i').read_text())
    paths = [Path(__file__), build_path, *sorted(patches.glob('*.hunks'))]
    report = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, commands=commands,
                  no_relink_required_for_equal_final_target_tokens=True,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.relative_to(out).as_posix(): digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(report['result'], sum(checks.values()), '/', len(checks), [k for k, v in checks.items() if not v], flush=True)


if __name__ == '__main__':
    main()

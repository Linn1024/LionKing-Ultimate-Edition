"""Compare freshly built CMake runtime/helper sections with their reviewed predecessors."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=ROOT / 'build/pride-owned-core')
    base = parser.parse_args().base.resolve()
    bp = base / 'build-report.json'
    build = bound(bp)
    out = base / 'code-equivalence'
    out.mkdir()
    checks = {}
    commands = []
    def run(cmd):
        commands.append(list(map(str, cmd)))
        return subprocess.check_output(commands[-1], text=True, timeout=30)
    def sections(path):
        text = run(['C:/mingw32/bin/objdump.exe', '-h', path])
        return {name: int(size, 16) for name, size in re.findall(r'^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s', text, re.M)
                if name != '.rdata$zzz'}
    def relocations(path):
        text = run(['C:/mingw32/bin/objdump.exe', '-r', path])
        return '\n'.join(line for line in text.splitlines() if 'file format pe-i386' not in line).strip()
    details = {}
    for index, (old, new) in enumerate(build['replacements'].items()):
        old, new = ROOT / old, ROOT / new
        a, b = sections(old), sections(new)
        checks[str(index) + '/section_sizes'] = a == b
        differences = []
        for section in sorted(set(a) | set(b)):
            if section == '.bss':
                continue
            content = []
            for label, obj in (('old', old), ('new', new)):
                path = out / (str(index) + '-' + label + section.replace('$', '_') + '.bin')
                cmd = ['C:/mingw32/bin/objcopy.exe', '-O', 'binary', '--only-section=' + section, str(obj), str(path)]
                subprocess.run(cmd, check=True, timeout=30)
                content.append(path.read_bytes())
            if content[0] != content[1]:
                differences.append(section)
        checks[str(index) + '/all_section_bytes'] = not differences
        checks[str(index) + '/all_relocations'] = relocations(old) == relocations(new)
        details[str(index)] = dict(old=old.relative_to(ROOT).as_posix(), new=new.relative_to(ROOT).as_posix(),
                                   old_sections=a, new_sections=b, differing_sections=differences)
        print(old.name, [key for key in checks if key.startswith(str(index) + '/') and not checks[key]], flush=True)
    paths = [Path(__file__), bp]
    result = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks, objects=details,
                  ignored_compiler_metadata_section='.rdata$zzz', commands=commands,
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()},
                  full_first_level_fidelity_complete=False)
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['result'], len(checks), 'checks', flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()

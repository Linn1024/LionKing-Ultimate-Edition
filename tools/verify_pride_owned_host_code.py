"""Prove the clean-source host retains reviewed machine code/data and relocations."""
import json
from pathlib import Path
import re
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound


def main():
    old = ROOT / 'build/pride-rng-player7'
    new = ROOT / 'build/pride-owned-host3'
    paths = [Path(__file__)]
    for folder in (old, new):
        p = folder / 'build-report.json'
        r = bound(p)
        assert digest(folder / 'player.exe') == r['binary_sha256']
        paths.append(p)
    out = new / 'code-equivalence'
    out.mkdir()
    checks = {}
    for section in ('.text', '.data', '.rdata', '.text.unlikely', '.text.startup'):
        files = []
        for label, folder in (('old', old), ('new', new)):
            path = out / (label + section + '.bin')
            subprocess.run(['C:/mingw32/bin/objcopy.exe', '-O', 'binary', '--only-section=' + section,
                            str(folder / 'host.obj'), str(path)], check=True, timeout=30)
            files.append(path.read_bytes())
        checks[section + '/all_bytes'] = bool(files[0]) and files[0] == files[1]
    relocations = []
    for label, folder in (('old', old), ('new', new)):
        data = subprocess.check_output(['C:/mingw32/bin/objdump.exe', '-r', str(folder / 'host.obj')], text=True, timeout=30)
        data = '\n'.join(line for line in data.splitlines() if 'file format pe-i386' not in line).strip()
        (out / (label + '-relocations.txt')).write_text(data + '\n')
        relocations.append(data)
    checks['all_relocation_records'] = bool(relocations[0]) and relocations[0] == relocations[1]
    a = (old / 'host.i').read_text()
    b = (new / 'host.i').read_text()
    marker = 'static unsigned restore_installed,restore_enabled,restore_pending,restore_committed;'
    a = a[a.index(marker):]
    b = b[b.index(marker):]
    # The two declarations now come from the maintained headers before marker.
    a = re.sub(r'extern int TlkTemporaryPath\([^;]+;', '', a)
    start = a.index('typedef struct TlkPrideSaveContext {')
    end = a.index('static int practice_context_ready(void) {', start)
    a = a[:start] + a[end:]
    # A source-time inline binding protects the original frame call from the
    # coordinator's macro aliases. Compiled bytes/relocations are checked above.
    assert b.count('return PrideNativeFrame(inputs);') == 1
    b = b.replace('return PrideNativeFrame(inputs);', 'return RtlRunFrame(inputs);')
    def tokens(text):
        text = re.sub(r'^# .*$', '', text, flags=re.M)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
        return re.findall(r'"(?:[^"\\]|\\.)*"|\w+|[^\s]', text)
    left, right = tokens(a), tokens(b)
    checks['all_host_tail_tokens'] = len(left) == 386078 and left == right
    for folder in (old, new):
        paths.extend([folder / 'host.obj', folder / 'host.i'])
    result = dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
                  compared_host_tail_tokens=len(left),
                  source_sha256={p.relative_to(ROOT).as_posix(): digest(p) for p in paths},
                  artifacts_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()},
                  full_first_level_fidelity_complete=False)
    (out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['result'], checks, flush=True)
    assert all(checks.values())


if __name__ == '__main__':
    main()

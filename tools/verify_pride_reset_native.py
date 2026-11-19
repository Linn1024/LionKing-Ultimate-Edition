"""Run ordinary-host early-save and captured-window regression gates."""
import argparse
from pathlib import Path
from audit_scenes import ROOT

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=('early', 'windows'), required=True)
    args = parser.parse_args()
    tool = 'verify_pride_clock_early_state.py' if args.kind == 'early' else 'verify_pride_clock_native_windows.py'
    original = ROOT / 'tools' / tool
    source = original.read_text()
    for old, new in {
        "base=ROOT/'build/pride-restart-clock/native'": "base=ROOT/'build/pride-reset/fixed2'",
        'Path(__file__),build_path': 'Path(__file__),original,build_path',
    }.items():
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    exec(compile(source, str(original), 'exec'))

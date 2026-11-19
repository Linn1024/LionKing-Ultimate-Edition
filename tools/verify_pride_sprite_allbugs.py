"""Verify the fresh graph's neutral observer and complete native All Bugs route."""
from pathlib import Path

original = Path(__file__).with_name('verify_pride_installed_allbugs.py')
source = original.read_text().replace("ROOT/'build/pride-installed-cache41'", "ROOT/'build/pride-sprite-fresh44'")
source = source.replace("source = base/'verification/report.json'", "source = base/'runtime-verification/report.json'")
source = source.replace('paths = [Path(__file__), build_path,', 'paths = [Path(__file__), original, build_path,')
exec(compile(source, str(original), 'exec'))

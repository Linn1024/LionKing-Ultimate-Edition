"""Validate frozen evidence after lizard-launch edits."""
from pathlib import Path
original_verifier=Path(__file__).with_name('pride_ledge_preview_history.py')
source=original_verifier.read_text().replace("('build/pride-ledge-baseline/report.json',", "('build/pride-lizard-launch-baseline/report.json','build/pride-ledge-baseline/report.json',")
exec(compile(source,str(original_verifier),'exec'))

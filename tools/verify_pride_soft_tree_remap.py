"""Run unchanged input regressions against both new tree frontends."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_singlepass_remap.py')
source=original_verifier.read_text().replace("ROOT/'build/pride-singlepass'","ROOT/'build/pride-soft-tree'")
source=source.replace('paths=[Path(__file__)]','paths=[Path(__file__),original_verifier]')
exec(compile(source,str(original_verifier),'exec'))

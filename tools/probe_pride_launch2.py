"""Verify normal configuration after fixing the outermost native dispatch."""
from pathlib import Path

first_probe=Path(__file__).with_name('probe_pride_launch.py')
source=first_probe.read_text().replace("ROOT/'build/pride-launch'","ROOT/'build/pride-launch2'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),first_probe,')
exec(compile(source,str(first_probe),'exec'))

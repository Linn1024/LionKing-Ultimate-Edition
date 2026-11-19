"""Measure the original FM94 tail independently of the leaf/ledge source choice."""
from pathlib import Path

original=Path(__file__).with_name('audit_pride_arrival_tail.py')
source=original.read_text().replace('build/pride-arrival-tail','build/pride-ledge-tail').replace('FM112','FM94')
source=source.replace('None,112)','None,94)').replace('original_command=[2,112]','original_command=[2,94]')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))

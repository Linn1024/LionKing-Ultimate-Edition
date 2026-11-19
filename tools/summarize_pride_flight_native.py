"""Extend the immutable renderer review with predecessor completion comparisons."""
from pathlib import Path
original=Path(__file__).with_name('summarize_pride_flight_art.py')
source=original.read_text().replace('paths=[Path(__file__),bp,',
    "paths=[Path(__file__),original,base/'completion-baseline/report.json',bp,")
source=source.replace('    checks=fields=0',
    "    baseline=bound(base/'completion-baseline/report.json')\n    assert baseline['result']=='PASS' and len(baseline['checks'])==6 and all(baseline['checks'].values())\n    checks=6;fields=0")
source=source.replace('semantic_predicate_checks=480,original_fixed_flight_snapshots=24,',
    'semantic_predicate_checks=480,original_fixed_flight_snapshots=24,predecessor_completion_fields=4500,')
exec(compile(source,str(original),'exec'))

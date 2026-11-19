"""Actual published118 CMD using default data and the qualified selected route."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_cmd53.py')
source=verifier_source.read_text().replace('pride-checkpoint-capability53','pride-resource-tree118').replace('installed-preview53','installed-preview118')
source=source.replace("base/'completion/report.json'","base/'routes99/report.json'").replace("source.parent/'aot'","source.parent/'probe-aot'").replace("prior['commands']['aot']","prior['commands']['probe-aot']")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

"""Actual public CMD/default imported data and selected completed route."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_cmd53.py')
source=verifier_source.read_text().replace('pride-checkpoint-capability53','pride-hyena-entrance139').replace('installed-preview53','installed-preview139')
source=source.replace("base/'completion/report.json'","base/'routes156-qualification/report.json'").replace("source.parent/'aot'","base/'routes148/probe-aot'").replace("prior['commands']['aot']","prior['commands']['probe-aot']")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

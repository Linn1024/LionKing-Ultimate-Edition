"""Public139 OS game/menu windows; run only after terminal161 CMD."""
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
cmd_report=bound(ROOT/'build/pride-hyena-entrance139/cmd-play/report.json')
assert cmd_report['result']=='PASS' and all(cmd_report['checks'].values())
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_public_window53.py')
source=verifier_source.read_text().replace('pride-checkpoint-capability53','pride-hyena-entrance139').replace('installed-preview53','installed-preview139')
source=source.replace("base/'completion/aot'/before","base/'routes148/probe-aot'/before")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

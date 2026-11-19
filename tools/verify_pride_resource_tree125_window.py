"""Published OS window, after terminal124 CMD check; use actual current route files."""
from pathlib import Path
verifier_source=Path(__file__).with_name('verify_pride_checkpoint_public_window53.py')
source=verifier_source.read_text().replace('pride-checkpoint-capability53','pride-resource-tree118').replace('installed-preview53','installed-preview118')
source=source.replace("base/'completion/aot'/before","base/'routes99/probe-aot'/before")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

"""Capture Continue edge handling with the original pad service kept live."""
from pathlib import Path
import sys

original=Path(__file__).with_name('capture_pride_final_continue_inputs.py')
source=original.read_text()
for before,after in [
    ('build/pride-final-input-probe2','build/pride-final-input-refresh-probe2'),
    ('paths=[Path(__file__),base/', 'paths=[Path(__file__),Path(__file__).with_name("capture_pride_final_continue_inputs.py"),base/')]:
    assert source.count(before)==1,before
    source=source.replace(before,after)
if '--resume' in sys.argv:
    source=source.replace("out=base/'continue';out.mkdir()", "out=base/'continue';out.mkdir(exist_ok=True);assert not (out/'report.json').exists()")
    source=source.replace('folder=out/name;folder.mkdir();','folder=out/name;folder.mkdir(exist_ok=True);')
    before="        with (folder/'run.log').open('wb') as log:\n            subprocess.run(commands[-1],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240)"
    after="        if not ((folder/'scene.json').exists() and 'wram_sha256=' in (folder/'run.log').read_text()):\n    "+before.replace('\n','\n    ')
    assert source.count(before)==1
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))

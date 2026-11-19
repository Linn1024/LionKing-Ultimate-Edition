"""Check the actual extended compiled table using the maintained parent tests."""
from pathlib import Path
import json
import subprocess
from audit_scenes import ROOT
from pride_arena_history import bound
base=ROOT/'build/pride-hyena-entrance139';b=bound(base/'build-report.json')
cmd=b['compiles']['resources'].copy();cmd[cmd.index('-c')]='-E';cmd[cmd.index('-o')+1]=str(base/'resources.i')
subprocess.run(cmd,cwd=ROOT/'build/pride-sprite-fresh44',check=True)
verifier_source=Path(__file__).with_name('verify_pride_resource_tree118.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-resource-tree118'","ROOT/'build/pride-hyena-entrance139'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

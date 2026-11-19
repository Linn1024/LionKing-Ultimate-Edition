"""Run the75 native route endpoints through the normal-configuration SDL host."""
from pathlib import Path
import os

original_verifier=Path(__file__).with_name('verify_native_routes.py')
source=original_verifier.read_text()
source=source.replace("ROOT/'engine/build-win/tlk_headless.exe'","ROOT/'build/pride-launch2/player.exe'")
source=source.replace("ROOT/'build/native-route-verification'","ROOT/'build/pride-launch2/native-gates'")
needle="    identity=hashlib.sha256(binary.read_bytes()).hexdigest()"
assert source.count(needle)==1
source=source.replace(needle,"""    assert not args.allbugs,'Use a separate supported observer for every-field All Bugs evidence'
    profile=dest/'resources.ini';profile.write_text('schema = 1\\ngame = snes\\n')
    config=dest/'host.ini';config.write_text('opengl = 0\\nscale = 1\\n')
    child_env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    child_env['SDL_VIDEODRIVER']='dummy'
"""+needle)
needle="        if tape:command+="
assert source.count(needle)==1
source=source.replace(needle,"        command+=['--config',str(config),'--resource-profile',str(profile),'--md-rom',str(dest/'missing.md'),'--no-pace','--no-audio','--no-record']\n"+needle)
source=source.replace('subprocess.run(command,cwd=ROOT,stdout=output,','subprocess.run(command,cwd=ROOT,env=child_env,stdout=output,')
source=source.replace("    print(len(routes),'native AOT/LLE routes PASS',flush=True)","""    baseline_path=ROOT/'build/pride-reset/fixed4/native/gates/play-report.json'
    baseline=json.loads(baseline_path.read_text())
    assert baseline['result']=='PASS' and baseline['route_count']==75 and baseline['routes']==modes,'Native endpoint regression'
    print(len(routes),'native AOT/LLE routes PASS; previous endpoints exact',flush=True)""")
exec(compile(source,str(original_verifier),'exec'))

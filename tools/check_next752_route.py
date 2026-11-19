"""Combined two-level route after removing the costly per-pixel setting searches."""
from pathlib import Path
template=Path(__file__).with_name('check_next748_route.py')
s=template.read_text().replace('build/next748-route','build/next752-route').replace('build/next747/player.exe','build/next751/player.exe')
s=s.replace("exec(compile(s,str(template),'exec'))", "s=s.replace('time.monotonic()+100','time.monotonic()+180')\nexec(compile(s,str(template),'exec'))")
exec(compile(s,str(template),'exec'))

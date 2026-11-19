"""Final actual-window matte check after the source-slot correction."""
from pathlib import Path
template=Path(__file__).with_name('check_next767_backdrop.py')
s=template.read_text().replace('build/next767-backdrop','build/next772-matte').replace('build/next766/player.exe','build/next771/player.exe')
exec(compile(s,str(template),'exec'))

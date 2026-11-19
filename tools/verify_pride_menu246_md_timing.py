"""Retry the retained MD timing/art test with local storage and real headroom."""
from pathlib import Path

template246 = Path(__file__).with_name('verify_pride_menu240_md_timing.py')
source = template246.read_text().replace('pride-menu240-md-timing', 'pride-menu246-md-timing')
start = source.index('assert shutil.disk_usage(ROOT).free>')
end = source.index('clean={', start)
source = source[:start] + """assert shutil.disk_usage(ROOT).free > 5*1024**3, 'Need 5 GiB headroom'
out=ROOT/'build/pride-menu246-md-timing';out.mkdir();checks={};observations={};commands={}
link=out/'control';link.mkdir()
""" + source[end:]
source = source.replace('paths=[Path(__file__),reference,', 'paths=[Path(__file__),template246,reference,')
exec(compile(source, str(template246), 'exec'))

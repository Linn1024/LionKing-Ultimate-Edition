"""Bounded local output for240 after G root proved unusable for creation."""
from pathlib import Path
template241=Path(__file__).with_name('verify_pride_menu240_md_timing.py')
source=template241.read_text().replace('pride-menu240-md-timing','pride-menu241-md-timing-local')
start=source.index("assert shutil.disk_usage(ROOT).free>")
end=source.index("out=ROOT/",start)
source=source[:start]+"assert shutil.disk_usage(ROOT).free>44*1024*1024,'Need44MiB for bounded control/live WAVs'\n"+source[end:]
start=source.index("target=Path('G:/")
end=source.index("clean={",start)
source=source[:start]+"(out/'control').mkdir()\nlink=out/'control'\n"+source[end:]
source=source.replace('paths=[Path(__file__),reference,','paths=[Path(__file__),template241,reference,')
exec(compile(source,str(template241),'exec'))

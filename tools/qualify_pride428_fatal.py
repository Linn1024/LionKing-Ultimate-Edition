"""The recorded end-of-field MD counter already includes the lost life."""
from pathlib import Path
template=Path(__file__).with_name('qualify_pride427_fatal.py')
s=template.read_text().replace('build/pride427-fatal-qualified','build/pride428-fatal-qualified').replace("r['lives']>1","r['lives']>0").replace("e['remaining_total_lives']>1","e['remaining_total_lives']>0")
s=s.replace('paths=[Path(__file__),capture,','paths=[Path(__file__),template,capture,')
exec(compile(s,str(template),'exec'))

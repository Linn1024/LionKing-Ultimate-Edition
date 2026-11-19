"""Use the saved late entry to capture the active final fight, without replaying the level."""
from pathlib import Path
template=Path(__file__).with_name('check_graveyard542_late.py')
s=template.read_text().replace("reference=ROOT/'build/graveyard523-vultures/report.json'", "reference=ROOT/'build/graveyard542-late/report.json'")
s=s.replace("'build/graveyard542-late')", "'build/graveyard544-fight')").replace("\"'17800'\"", "\"'18000'\"")
exec(compile(s,str(template),'exec'))

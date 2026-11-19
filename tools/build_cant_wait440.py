"""Build the second-level monkey palette adapter with the published418 frontend."""
from pathlib import Path
template=Path(__file__).with_name('build_pride418.py')
s=template.read_text().replace("base=ROOT/'build/pride398'","base=ROOT/'build/pride418'").replace("out=ROOT/'build/pride418'","out=ROOT/'build/cant-wait440'")
# These replacements occur inside the wrapper's own source transformation.
s=s.replace("'build_pride398.py'","'build_pride398.py'")
s=s.replace("'engine/runner/tlk_wide.c',\")","'engine/runner/tlk_wide.c','engine/runner/tlk_cw_monkey_metadata.h',\")")
exec(compile(s,str(template),'exec'))

"""Ordinary reapproach from below, with the camera crossing the extra right band."""
from pathlib import Path
verifier_source=Path(__file__).with_name('capture_pride_hyena_entrance157_drop.py')
source=verifier_source.read_text().replace("ROOT/'build/pride-hyena-entrance157-drop'","ROOT/'build/pride-hyena-entrance158-reapproach'")
old="[('down80',[0x400]*80+[0]*420),('leftdown40',[0x600]*40+[0]*460)]"
new="[('reapproach',[0x600]*40+[0]*120+[0x100]*8+[0x200]+[0]*331)]"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

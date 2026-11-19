"""Add separate later-level MD defaults and direct launchers; preserve user settings."""
from audit_scenes import ROOT
profile=(ROOT/'profiles/exile-md.ini').read_text().replace('graphics.sprites.simba.adult.frames = snes','graphics.sprites.simba.adult.frames = inherit')
for name,title,level in [('hakuna-md','Play Hakuna Matata MD.cmd',5),('destiny-md','Play Simbas Destiny MD.cmd',6)]:
 p=ROOT/f'profiles/{name}.ini';assert not p.exists(),p;p.write_text(profile)
 q=ROOT/title;assert not q.exists(),q
 q.write_text((ROOT/'Play Simbas Exile MD.cmd').read_text().replace('exile-md',name).replace('-PracticeLevel 4',f'-PracticeLevel {level}'))
print('Prepared separate Hakuna/Destiny MD defaults')

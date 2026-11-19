"""Add separate Be Prepared/Return MD defaults without modifying saved user choices."""
from audit_scenes import ROOT
profile=(ROOT/'profiles/destiny-md.ini').read_text()
for name,title,level in [('be-prepared-md','Play Be Prepared MD.cmd',7),('return-md','Play Simbas Return MD.cmd',8)]:
 p=ROOT/f'profiles/{name}.ini';assert not p.exists(),p;p.write_text(profile)
 p=ROOT/title;assert not p.exists(),p;p.write_text((ROOT/'Play Simbas Destiny MD.cmd').read_text().replace('destiny-md',name).replace('-PracticeLevel 6',f'-PracticeLevel {level}'))
print('Prepared independent7/8 defaults')

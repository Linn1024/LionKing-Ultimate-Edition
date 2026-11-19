"""Default MD profiles have separate settings; never overwrite user choices."""
from audit_scenes import ROOT
for name in ('stampede-md','exile-md'):
 p=ROOT/f'profiles/{name}.ini';assert not p.exists(),p
 p.write_text((ROOT/'profiles/graveyard-md.ini').read_text())
print('Created independent Stampede/Exile MD defaults')

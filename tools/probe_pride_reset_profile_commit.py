"""Prove that corrected reset caches retain actual music, cue and trigger changes."""
from pathlib import Path

original_verifier=Path(__file__).with_name('probe_pride_reset_profile.py')
source=original_verifier.read_text().replace("'profile-noop'","'profile-commit'").replace('tools/pride_reset_profile_probe.c','tools/pride_reset_profile_commit_probe.c')
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
source=source.replace("values=list(map(int,re.findall", "commits=re.findall(r'reset_profile_commit,[^,\\n]+,1,1,1,0,1,1,1,0',log);checks[name+'/six_real_source_commits']=len(commits)==6\n                values=list(map(int,re.findall")
exec(compile(source,str(original_verifier),'exec'))

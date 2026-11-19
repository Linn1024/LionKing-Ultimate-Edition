"""Observe both original levels once; retain small local checkpoints for follow-up."""
import json,os,subprocess,shutil
from audit_scenes import ROOT
out=ROOT/'build/next726-reference';out.mkdir(exist_ok=True)
shutil.copyfile(ROOT/'build/md-exile-art-reference/config.ini',out/'config.ini')
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(ROOT/'tools/bizhawk/next726_reference.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,NEXT726_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=240,creationflags=subprocess.CREATE_NO_WINDOW)
error=(out/'lua-error.txt').read_text();assert not error,error
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',command=cmd),indent=2)+'\n');print('ORIGINAL reference complete')

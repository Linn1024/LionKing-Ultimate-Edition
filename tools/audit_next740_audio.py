"""Original sound ownership at nearby saved levels, without an earlier-level replay."""
import os,subprocess,shutil
from audit_scenes import ROOT
out=ROOT/'build/next740-audio';out.mkdir(exist_ok=True);shutil.copyfile(ROOT/'build/md-exile-art-reference/config.ini',out/'config.ini')
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(ROOT/'tools/bizhawk/next740_audio.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,NEXT740_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=80,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text();print('ORIGINAL audio checkpoints complete')

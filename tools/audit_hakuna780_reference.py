"""Original Hakuna/Destiny initialization and actors, resumed from the nearby MD save."""
import os,json,subprocess,shutil
from audit_scenes import ROOT
out=ROOT/'build/hakuna780-reference';out.mkdir(exist_ok=True)
lua=(ROOT/'tools/bizhawk/next726_reference.lua').read_text().replace("assert(movie.isloaded() and emu.framecount()<=1)","assert(movie.isloaded())\n  savestate.load(out..'/../next726-reference/24500.State')")
lua=lua.replace('NEXT726_OUT','HAKUNA780_OUT').replace('level==3 or level==4','level==5 or level==6').replace('26300','40100')
a=lua.index('local seen={};local fields=');b=lua.index('\n  local scroll=',a)
lua=lua[:a]+"local seen={};local fields={[27000]=true,[28000]=true,[29000]=true,[30000]=true,[31000]=true,[32000]=true,[33000]=true,[34000]=true,[34500]=true,[36000]=true,[38000]=true,[40000]=true}"+lua[b:]
lua=lua.replace('frame==20500 or frame==24500','frame==27000 or frame==31000 or frame==34000 or frame==36000')
(out/'observe.lua').write_text(lua);shutil.copyfile(ROOT/'build/md-exile-art-reference/config.ini',out/'config.ini')
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(out/'observe.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,HAKUNA780_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=160,creationflags=subprocess.CREATE_NO_WINDOW)
error=(out/'lua-error.txt').read_text();assert not error,error
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',command=cmd),indent=2)+'\n');print('Original Hakuna/Destiny observation complete')

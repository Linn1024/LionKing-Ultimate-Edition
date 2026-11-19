"""Original late Destiny/Be Prepared reference from the existing nearby MD save."""
import os,json,subprocess,shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/next824-reference';out.mkdir(exist_ok=True)
assert (ROOT/'build/hakuna780-reference/36000.State').is_file()
lua=(ROOT/'build/hakuna780-reference/observe.lua').read_text().replace('HAKUNA780_OUT','NEXT824_OUT').replace("/../next726-reference/24500.State","/../hakuna780-reference/36000.State").replace('level==5 or level==6','level==6 or level==7 or level==8').replace('40100','49000')
lua=lua.replace('  client.speedmode(6400)','  assert(emu.framecount()==36000, "Expected nearby original36000 checkpoint")\n  client.speedmode(6400)')
a=lua.index('local seen={};local fields=');b=lua.index('\n  local scroll=',a)
lua=lua[:a]+"local seen={};local fields={[41000]=true,[42000]=true,[43000]=true,[44000]=true,[45000]=true,[46000]=true,[47000]=true,[48000]=true}"+lua[b:]
lua=lua.replace('frame==27000 or frame==31000 or frame==34000 or frame==36000','frame==41000 or frame==43000 or frame==46000')
(out/'observe.lua').write_text(lua);shutil.copyfile(ROOT/'build/hakuna780-reference/config.ini',out/'config.ini')
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(out/'observe.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,NEXT824_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=160,creationflags=subprocess.CREATE_NO_WINDOW)
error=(out/'lua-error.txt').read_text();assert not error,error
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',command=cmd,scope=__doc__,source_sha256={'tools/observe_next824_reference.py':digest(ROOT/'tools/observe_next824_reference.py')}),indent=2)+'\n');print('Next-level original reference captured',flush=True)

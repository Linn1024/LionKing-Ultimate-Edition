"""Observe original adult death at nearby Destiny with research-only health1."""
import os,json,subprocess,shutil
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/hakuna834-death';out.mkdir(exist_ok=True)
lua=r'''local out=assert(os.getenv('HAKUNA834_OUT'))
local errors=assert(io.open(out..'/lua-error.txt','w'))
local function run()
 client.speedmode(6400)
 local function w(a)return memory.read_u16_be(a&0xffff,'68K RAM')end
 local function l(a)return memory.read_u32_be(a&0xffff,'68K RAM')&0xffffff end
 local log=assert(io.open(out..'/commands.csv','w'));log:write('field,level,selector,value,caller,health,lives,simba,action\n')
 event.onmemoryexecute(function()
  local sel=emu.getregister('M68K D7')&0xffffffff
  if sel==1 or sel==19 or sel==2 then
   local p=w(w(0xcd36)+0x24)
   log:write(string.format('%d,%d,%d,%d,%06x,%d,%d,%04x,%06x\n',emu.framecount()+1,w(0xccce)-1,sel,emu.getregister('M68K D0')&0xffff,l(emu.getregister('M68K A7')),w(0xccf6),w(0xccee),p,l(p+0x30)))
  end
 end,0x2d0000,'hakuna834 death driver')
 local state=assert(io.open(out..'/states.csv','w'));state:write('field,level,health,lives,simba,action,x,y\n')
 for _,part in ipairs({{36000,40000}})do
  savestate.load(out..'/../hakuna780-reference/'..part[1]..'.State')
  -- Research-only input branch; no health, actor, game-code or driver changes.
  movie.stop()
  memory.write_u16_be(0xccf6,1,'68K RAM')
  while emu.framecount()<part[2] do
   joypad.set({Right=true});emu.frameadvance();local p=w(w(0xcd36)+0x24)
   if emu.framecount()%5==0 then state:write(string.format('%d,%d,%d,%d,%04x,%06x,%d,%d\n',emu.framecount(),w(0xccce)-1,w(0xccf6),w(0xccee),p,l(p+0x30),w(p+8),w(p+10)))end
  end
 end
 log:close();state:close()
end
local ok,message=xpcall(run,debug.traceback);if not ok then errors:write(message)end
errors:close();client.exit()
'''
(out/'observe.lua').write_text(lua);shutil.copyfile(ROOT/'build/hakuna780-reference/config.ini',out/'config.ini')
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(out/'observe.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,HAKUNA834_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text()
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,source_sha256={'tools/audit_hakuna834_death.py':digest(Path(__file__))}),indent=2)+'\n');print('OBSERVED',flush=True)

"""Observe original Pride Rock summit and ending without broad opcode callbacks."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride924-reference';out.mkdir(exist_ok=True);state=ROOT/'build/pride921-reference/57000.State';assert state.exists()
lua=r'''local out=os.getenv('PRIDE924_OUT'):gsub('\\','/');local err=assert(io.open(out..'/lua-error.txt','w'))
local function run()
 savestate.load(out..'/../pride921-reference/57000.State');assert(emu.framecount()==57000);client.speedmode(6400);client.SetSoundOn(false)
 local function w(a)return memory.read_u16_be(a,'68K RAM')end
 local function l(a)return memory.read_u32_be(a,'68K RAM')end
 local poses=assert(io.open(out..'/poses.csv','w'));poses:write('field,level,actor,descriptor,action,pose,palette,x,y\n');local seen={}
 local frames={[58000]=true,[59000]=true,[60000]=true,[61000]=true,[62000]=true,[65000]=true}
 local status=assert(io.open(out..'/scenes.csv','w'));status:write('field,level,camera_x,camera_y,e9ce\n')
 while emu.framecount()<65000 do
  emu.frameadvance();local f=emu.framecount();local level=w(0xccce)-1
  if f%4==0 and level==9 then
   for a=0x804e,0xff00,128 do local d=w(a+12)
    if d>=0x8000 and d<=0xffe8 and w(d+4)==a+8 then
     local desc=l(a+4);local p=l(d+10);local pal=(w(d+8)>>13)&3;local key=string.format('%x:%x:%d',desc,p,pal)
     if not seen[key] then seen[key]=true;poses:write(string.format('%d,%d,%04x,%06x,%06x,%06x,%d,%d,%d\n',f,level,a,desc,l(a+0x30),p,pal,w(a+8),w(a+10)))end
    end
   end
  end
  if frames[f] then
   local cam=w(0xcd36);status:write(string.format('%d,%d,%d,%d,%d\n',f,level,w(cam+8),w(cam+10),w(0xe9ce)));status:flush();poses:flush()
   for _,domain in ipairs({'68K RAM','VRAM','CRAM','VSRAM'})do local file=assert(io.open(out..'/'..f..'-'..domain..'.bin','wb'));for _,v in ipairs(memory.read_bytes_as_array(0,memory.getmemorydomainsize(domain),domain))do file:write(string.char(v))end;file:close()end
   client.screenshot(out..'/'..f..'.png');if f==60000 or f==65000 then savestate.save(out..'/'..f..'.State')end
  end
 end
 poses:close();status:close()
end
local ok,message=xpcall(run,debug.traceback);if not ok then err:write(message)end;err:close();client.exit()
''';(out/'observe.lua').write_text(lua);shutil.copy2(ROOT/'build/later873-reference/config.ini',out/'config.ini');cmd=json.loads((ROOT/'build/later873-reference/report.json').read_text())['command'];cmd=[x.replace('later873-reference','pride924-reference') for x in cmd]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,PRIDE924_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=170,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text();(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,source_sha256={Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__))}),indent=2)+'\n');print('OBSERVED',flush=True)

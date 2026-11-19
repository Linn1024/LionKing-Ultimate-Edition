"""Continue original MD summit/ending with movie-end Finish instead of Pause."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride958-reference';out.mkdir(exist_ok=True);cfg=json.loads((ROOT/'build/pride921-reference/config.ini').read_text(encoding='utf-8-sig'));assert cfg['Movies']['MovieEndAction']==1;cfg['Movies']['MovieEndAction']=3;(out/'config.ini').write_text(json.dumps(cfg,indent=2))
lua=r'''local out=assert(os.getenv('PRIDE958_OUT'));local errors=assert(io.open(out..'/lua-error.txt','w'))
local function run()
 assert(movie.isloaded());savestate.load(out..'/../pride921-reference/57000.State');assert(emu.framecount()==57000 and memory.read_u16_be(0xccce,'68K RAM')==10);client.speedmode(6400)
 local function w(a)return memory.read_u16_be(a&0xffff,'68K RAM')end
 local function l(a)return memory.read_u32_be(a&0xffff,'68K RAM')&0xffffff end
 local status=assert(io.open(out..'/scenes.csv','w'));status:write('field,level,camera_x,camera_y,e9ce\n')
 local commands=assert(io.open(out..'/commands.csv','w'));commands:write('field,level,selector,value,caller\n')
 event.onmemoryexecute(function()local s=emu.getregister('M68K D7')&0xffffffff;if s==1 or s==2 or s==19 then commands:write(string.format('%d,%d,%d,%d,%06x\n',emu.framecount()+1,w(0xccce)-1,s,emu.getregister('M68K D0')&0xffff,l(emu.getregister('M68K A7'))))end end,0x2d0000,'pride958 audio')
 local frames={[57050]=true,[57100]=true,[57200]=true,[57300]=true,[57400]=true,[58000]=true,[60000]=true}
 while emu.framecount()<60000 do
  emu.frameadvance();local f=emu.framecount()
  if frames[f] then
   local cam=w(0xcd36);status:write(string.format('%d,%d,%d,%d,%d\n',f,w(0xccce)-1,w(cam+8),w(cam+10),w(0xe9ce)));status:flush();commands:flush()
   for _,domain in ipairs({'68K RAM','VRAM','CRAM','VSRAM'})do local file=assert(io.open(out..'/'..f..'-'..domain..'.bin','wb'));for _,v in ipairs(memory.read_bytes_as_array(0,memory.getmemorydomainsize(domain),domain))do file:write(string.char(v))end;file:close()end
   client.screenshot(out..'/'..f..'.png');if f==57200 or f==58000 then savestate.save(out..'/'..f..'.State')end
  end
 end
 status:close();commands:close()
end
local ok,message=xpcall(run,debug.traceback);if not ok then errors:write(message)end;errors:close();client.exit()
''';(out/'observe.lua').write_text(lua);cmd=json.loads((ROOT/'build/later873-reference/report.json').read_text())['command'];cmd=[x.replace('later873-reference','pride958-reference') for x in cmd]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,PRIDE958_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=75,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text();paths=[Path(__file__),out/'config.ini'];(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,movie_input_fields=57325,movie_end_action=dict(previous='Pause=1',current='Finish=3',source='installed BizHawk.Client.Common.MovieEndAction enum via reflection'),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('OBSERVED',flush=True)

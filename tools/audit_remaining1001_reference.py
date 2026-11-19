"""One unmodified original Genesis TAS reference; no recordings or guest edits."""
import csv,json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1001-reference';out.mkdir(exist_ok=True)
cfg=json.loads((ROOT/'build/pride958-reference/config.ini').read_text());cfg['Movies']['MovieEndAction']=3;(out/'config.ini').write_text(json.dumps(cfg,indent=2))
lua=r'''local out=assert(os.getenv('REMAINING1001_OUT'));local errors=assert(io.open(out..'/lua-error.txt','w'))
local function run()
 assert(movie.isloaded() and emu.framecount()<=1);client.speedmode(6400)
 local function w(a)return memory.read_u16_be(a&0xffff,'68K RAM')end
 local function l(a)return memory.read_u32_be(a&0xffff,'68K RAM')&0xffffff end
 local log=assert(io.open(out..'/frames.csv','w'));log:write('field,lag,level,player_x,player_y,health,roar,ending\n')
 local sound=assert(io.open(out..'/commands.csv','w'));sound:write('field,level,selector,value,caller\n')
 event.onmemoryexecute(function()local s=emu.getregister('M68K D7')&0xffffffff;if s==1 or s==2 or s==19 then sound:write(string.format('%d,%d,%d,%d,%06x\n',emu.framecount()+1,w(0xccce)-1,s,emu.getregister('M68K D0')&0xffff,l(emu.getregister('M68K A7'))))end end,0x2d0000,'remaining1001 sound')
 local old=-1;local capture=-1;local samples={[19900]=true,[57325]=true,[60000]=true}
 while emu.framecount()<60000 do
  emu.frameadvance();local f=emu.framecount();local level=w(0xccce)-1;local cam=w(0xcd36);local player=cam>=0x8000 and cam<=0xff80 and w(cam+0x24) or 0;local valid=player>=0x8000 and player<=0xff80
  log:write(string.format('%d,%d,%d,%d,%d,%d,%d,%d\n',f,emu.islagged() and 1 or 0,level,valid and w(player+8) or 0,valid and w(player+10) or 0,w(0xccf6),w(0xccf2),w(0xe9ce)))
  if level~=old then capture=f+120;old=level;log:flush();sound:flush()end
  if f==capture then client.screenshot(out..'/level-'..level..'-'..f..'.png')end
  if samples[f] then
   for _,domain in ipairs({'68K RAM','VRAM','CRAM','VSRAM'})do local file=assert(io.open(out..'/'..f..'-'..domain..'.bin','wb'));for _,v in ipairs(memory.read_bytes_as_array(0,memory.getmemorydomainsize(domain),domain))do file:write(string.char(v))end;file:close()end
   client.screenshot(out..'/'..f..'.png')
  end
 end
 log:close();sound:close()
end
local ok,message=xpcall(run,debug.traceback);if not ok then errors:write(message)end;errors:close();client.exit()
'''
(out/'observe.lua').write_text(lua);movie=ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(movie),'--lua='+str(out/'observe.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,REMAINING1001_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=210,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text();rows=list(csv.DictReader((out/'frames.csv').open()));transitions=[]
for r in rows:
 n=int(r['level'])
 if not transitions or transitions[-1]['level']!=n:transitions.append(dict(field=int(r['field']),level=n))
checks=dict(completed_input=len(rows)==60000,all_main_levels=set(range(10))<=set(int(r['level']) for r in rows),actual_rainy_ending=int(rows[-1]['ending'])==1553)
paths=[Path(__file__),out/'config.ini',out/'observe.lua',movie]
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,author='ShgofcTAS',source='https://tasvideos.org/10612S',movie_fields=57325,transitions=transitions,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks,transitions,flush=True)

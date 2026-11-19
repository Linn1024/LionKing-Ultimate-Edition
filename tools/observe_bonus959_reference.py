"""Observe original bonus backgrounds, initialized actors and sound from nearby movie routes."""
import json,os,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/bonus959-reference';out.mkdir(exist_ok=True);cfg=json.loads((ROOT/'build/pride958-reference/config.ini').read_text());cfg['Movies']['MovieEndAction']=3;cases={}
for name,start,end,state,frames in [('early',0,13200,None,[4400,4500,4600,13130,13160]),('late',36000,41450,'hakuna780-reference/36000.State',[41400,41440])]:
 folder=out/name;folder.mkdir(exist_ok=True);(folder/'config.ini').write_text(json.dumps(cfg,indent=2));lua=r'''local out=assert(os.getenv('BONUS959_OUT'));local err=assert(io.open(out..'/lua-error.txt','w'))
local function run()
 assert(movie.isloaded());__LOAD__;assert(emu.framecount()==__START__);client.speedmode(6400)
 local function w(a)return memory.read_u16_be(a&0xffff,'68K RAM')end
 local function l(a)return memory.read_u32_be(a&0xffff,'68K RAM')&0xffffff end
 local poses=assert(io.open(out..'/poses.csv','w'));poses:write('field,level,actor,descriptor,action,pose,palette,x,y\n');local seen={}
 local status=assert(io.open(out..'/scenes.csv','w'));status:write('field,level,camera_x,camera_y\n');local prev=-1
 local audio=assert(io.open(out..'/commands.csv','w'));audio:write('field,level,selector,value,caller\n')
 event.onmemoryexecute(function()local s=emu.getregister('M68K D7')&0xffffffff;if w(0xccce)>=11 and (s==1 or s==2 or s==19) then audio:write(string.format('%d,%d,%d,%d,%06x\n',emu.framecount()+1,w(0xccce)-1,s,emu.getregister('M68K D0')&0xffff,l(emu.getregister('M68K A7'))))end end,0x2d0000,'bonus959 audio')
 local frames=__FRAMES__
 while emu.framecount()<__END__ do
  emu.frameadvance();local f=emu.framecount();local level=w(0xccce)-1
  if level~=prev then status:write(string.format('%d,%d,%d,%d\n',f,level,w(w(0xcd36)+8),w(w(0xcd36)+10)));status:flush();prev=level end
  if level>=10 and level<=13 then
   for a=0x804e,0xff00,128 do local d=w(a+12)
    if d>=0x8000 and d<=0xffe8 and w(d+4)==a+8 then
     local desc=l(a+4);local p=l(d+10);local pal=(w(d+8)>>13)&3;local key=string.format('%d:%x:%x:%d',level,desc,p,pal)
     if not seen[key] then seen[key]=true;poses:write(string.format('%d,%d,%04x,%06x,%06x,%06x,%d,%d,%d\n',f,level,a,desc,l(a+0x30),p,pal,w(a+8),w(a+10)))end
    end
   end
  end
  if frames[f] then
   assert(level>=10 and level<=13,'Expected actual bonus');poses:flush();audio:flush()
   for _,domain in ipairs({'68K RAM','VRAM','CRAM','VSRAM'})do local file=assert(io.open(out..'/'..f..'-'..domain..'.bin','wb'));for _,v in ipairs(memory.read_bytes_as_array(0,memory.getmemorydomainsize(domain),domain))do file:write(string.char(v))end;file:close()end
   client.screenshot(out..'/'..f..'.png');if f==4500 or f==13160 or f==41400 then savestate.save(out..'/'..f..'.State')end
  end
 end
 poses:close();status:close();audio:close()
end
local ok,message=xpcall(run,debug.traceback);if not ok then err:write(message)end;err:close();client.exit()
''';lua=lua.replace('__LOAD__',"savestate.load(out..'/../../"+state+"')" if state else '').replace('emu.framecount()==__START__','emu.framecount()<=1' if start==0 else 'emu.framecount()==__START__').replace('__START__',str(start)).replace('__END__',str(end)).replace('__FRAMES__','{'+','.join(f'[{f}]=true' for f in frames)+'}');(folder/'observe.lua').write_text(lua)
 cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(folder/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(folder/'observe.lua'),str(ROOT/'Lion King, The (World).md')]
 with (folder/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,BONUS959_OUT=str(folder)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
 assert not (folder/'lua-error.txt').read_text(),(folder/'lua-error.txt').read_text();cases[name]=dict(start=start,end=end,command=cmd);print('OBSERVED',name,flush=True)
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,cases=cases,source_sha256={'tools/observe_bonus959_reference.py':digest(Path(__file__))}),indent=2)+'\n')

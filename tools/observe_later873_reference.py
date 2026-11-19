"""Original7-9 actor/audio/VDP reference from the verified43000 MD save."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/later873-reference';out.mkdir(exist_ok=True);state=ROOT/'build/next824-reference/43000.State';assert state.is_file()
lua=(ROOT/'build/hakuna780-reference/observe.lua').read_text().replace('HAKUNA780_OUT','LATER873_OUT').replace('/../next726-reference/24500.State','/../next824-reference/43000.State').replace('level==5 or level==6','level==7 or level==8 or level==9').replace('40100','55000')
lua=lua.replace('  client.speedmode(6400)',"  assert(emu.framecount()==43000 and memory.read_u16_be(0xccce,'68K RAM')==8, 'Expected original7 checkpoint43000')\n  client.speedmode(6400)")
a=lua.index('local seen={};local fields=');b=lua.index('\n  local scroll=',a);lua=lua[:a]+"local seen={};local fields={[45000]=true,[48000]=true,[49000]=true,[50000]=true,[51000]=true,[52000]=true,[53000]=true,[54000]=true,[54500]=true}"+lua[b:]
lua=lua.replace('frame==27000 or frame==31000 or frame==34000 or frame==36000','frame==49000 or frame==52000 or frame==54000')
lua=lua.replace('  local seen={}',r'''  local calls=assert(io.open(out..'/calls.csv','w'));calls:write('field,level,kind,value,caller,registers\n')
  for _,entry in ipairs({{0x22a2,'fm'},{0x2244,'pcm'}})do
    event.onmemoryexecute(function()
      local fields={}
      for n=0,6 do local actor=emu.getregister('M68K A'..n)&0xffff;fields[#fields+1]=string.format('%04x:%06x:%06x',actor,l(actor+4),l(actor+0x30))end
      calls:write(string.format('%d,%d,%s,%d,%06x,%s\n',emu.framecount()+1,w(0xccce)-1,entry[2],emu.getregister('M68K D0')&0xffff,l(emu.getregister('M68K A7')),table.concat(fields,';')))
    end,entry[1],'later873 '..entry[2])
  end
  local seen={}''')
lua=lua.replace('poses:close();audio:close();scroll:close()','poses:close();audio:close();scroll:close();calls:close()')
(out/'observe.lua').write_text(lua);shutil.copyfile(ROOT/'build/next824-reference/config.ini',out/'config.ini')
cmd=[str(ROOT/'.tools/BizHawk-2.11/EmuHawk.exe'),'--config='+str(out/'config.ini'),'--movie='+str(ROOT/'build/md-tas/ShgofcTAS-Genesis-LionKing-allbugs-10612S.bk2'),'--lua='+str(out/'observe.lua'),str(ROOT/'Lion King, The (World).md')]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,LATER873_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=130,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text()
(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,source_sha256={'tools/observe_later873_reference.py':digest(Path(__file__))}),indent=2)+'\n');print('OBSERVED',flush=True)

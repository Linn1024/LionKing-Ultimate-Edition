"""Bounded original final-level and ending observation from verified54000; no earlier replay."""
import json,os,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
out=ROOT/'build/pride921-reference';out.mkdir(exist_ok=True)
lua=(ROOT/'build/later873-reference/observe.lua').read_text().replace('LATER873_OUT','PRIDE921_OUT').replace('/../next824-reference/43000.State','/../later873-reference/54000.State').replace('emu.framecount()==43000','emu.framecount()==54000').replace("memory.read_u16_be(0xccce,'68K RAM')==8","memory.read_u16_be(0xccce,'68K RAM')==10").replace('checkpoint43000','checkpoint54000').replace('while emu.framecount()<55000','while emu.framecount()<65000')
a=lua.index('local seen={};local fields=');b=lua.index('\n  local scroll=',a);lua=lua[:a]+"local seen={};local fields={[55000]=true,[57000]=true,[59000]=true,[61000]=true,[63000]=true,[65000]=true}"+lua[b:];lua=lua.replace('frame==49000 or frame==52000 or frame==54000','frame==57000 or frame==61000 or frame==65000');(out/'observe.lua').write_text(lua);shutil.copy2(ROOT/'build/later873-reference/config.ini',out/'config.ini');cmd=json.loads((ROOT/'build/later873-reference/report.json').read_text())['command'];cmd=[x.replace('later873-reference','pride921-reference') for x in cmd]
with (out/'host.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT/'.tools/BizHawk-2.11',env=dict(os.environ,PRIDE921_OUT=str(out)),stdout=log,stderr=subprocess.STDOUT,check=True,timeout=140,creationflags=subprocess.CREATE_NO_WINDOW)
assert not (out/'lua-error.txt').read_text(),(out/'lua-error.txt').read_text();(out/'report.json').write_text(json.dumps(dict(result='OBSERVED',scope=__doc__,command=cmd,source_sha256={Path(__file__).relative_to(ROOT).as_posix():digest(Path(__file__))}),indent=2)+'\n');print('OBSERVED',flush=True)

"""Actual compiled table and maintained resolver: group inheritance survives insertions."""
import json
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

base=ROOT/'build/pride-resource-tree118';bp=base/'build-report.json';b=bound(bp)
out=base/'parent-verification';out.mkdir();pre=(base/'resources.i').read_text()
start=pre.index('static TlkResourceNode nodes[]');end=pre.index('};',start)+2
table=pre[start:end];source=(ROOT/'engine/runner/tlk_resources.c').read_text()
def function(name):
    start=source.index(name);a=source.index('{',start);depth=1;end=a+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
text=table+'\nenum {COUNT=sizeof nodes/sizeof nodes[0]};\nstatic int parents_ready;\nstatic unsigned char active[COUNT],draft[COUNT];\n'
text+=function('static void BindResourceParents')+'\n'+function('int TlkResourcesResolved')+'\n'
(out/'resource_table118.h').write_text(text)
test=ROOT/'engine/tests/resource_parent_test.c';cmd=['C:/mingw32/bin/gcc.exe','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(out),str(test),'-o',str(out/'test.exe')]
subprocess.run(cmd,check=True);result=subprocess.run([str(out/'test.exe')],capture_output=True,text=True)
checks=dict(actual_table_and_production_resolver=result.returncode==0 and bool(re.fullmatch(r'PASS \d+ checks\s*',result.stdout)))
paths=[Path(__file__),bp,test,ROOT/'engine/runner/tlk_resource_parent.h',ROOT/'engine/runner/tlk_resources.c',base/'resources.i',out/'resource_table118.h',out/'test.exe']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,output=result.stdout,stderr=result.stderr,
    scope='Exact current compiled table plus maintained binding/resolution functions; checks Continue-token group/leaf inheritance, isolation from Options source, two intentional ceiling aliases and stability after three inserted nodes. Runtime UI/pictures separate.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(result.stdout,result.stderr,flush=True)

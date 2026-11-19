"""Actual compiled226 table and resolver, including independent menu inheritance."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

build_path=ROOT/'build/pride-menu226-integrated/build-report.json'; build=bound(build_path)
out=ROOT/'build/pride-menu250-parents/verified';out.mkdir()
cmd=build['compiles']['resources'].copy();cmd[cmd.index('-c')]='-E';cmd[cmd.index('-o')+1]=str(out/'resources.i')
subprocess.run(cmd,cwd=ROOT/'build/pride-sprite-fresh44',check=True)
source=(out/'resources.i').read_text();start=source.index('static TlkResourceNode nodes[]');end=source.index('};',start)+2
table=source[start:end]
maintained=ROOT/'engine/runner/tlk_resources.c';source=maintained.read_text()
def function(name):
    start=source.index(name);a=source.index('{',start);depth=1;end=a+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
(out/'resource_table118.h').write_text(table+'\nenum {COUNT=sizeof nodes/sizeof nodes[0]};\nstatic int parents_ready;\nstatic unsigned char active[COUNT],draft[COUNT];\n'+function('static void BindResourceParents')+'\n'+function('int TlkResourcesResolved')+'\n')
test=ROOT/'engine/tests/resource_parent_test.c';text=test.read_text()
anchor='    TlkResourceNode shifted[COUNT+3];'
assert anchor in text
text=text.replace(anchor,'''    int menu=find("graphics.pride_final_menu"),graphics=find("graphics"),timing=find("gameplay.levels.pride_lands.final_life");
    CHECK(menu>=0 && graphics>=0 && timing>=0);
    CHECK(nodes[menu].leaf && nodes[menu].md_supported && nodes[menu].parent==graphics);
    memset(draft,0,sizeof draft);draft[0]=TLK_SOURCE_SNES;
    draft[timing]=TLK_SOURCE_MD;CHECK(TlkResourcesResolved(menu,1)==TLK_SOURCE_SNES);
    draft[graphics]=TLK_SOURCE_MD;CHECK(TlkResourcesResolved(menu,1)==TLK_SOURCE_MD);
    draft[menu]=TLK_SOURCE_SNES;CHECK(TlkResourcesResolved(menu,1)==TLK_SOURCE_SNES);
    CHECK(TlkResourcesResolved(timing,1)==TLK_SOURCE_MD);
    draft[menu]=TLK_SOURCE_MD;draft[timing]=TLK_SOURCE_SNES;
    CHECK(TlkResourcesResolved(menu,1)==TLK_SOURCE_MD);
    CHECK(TlkResourcesResolved(timing,1)==TLK_SOURCE_SNES);
'''+anchor)
generated=out/'parent_test.c';generated.write_text(text)
cmd=['C:/mingw32/bin/gcc.exe','-O2','-I'+str(ROOT/'engine/runner'),'-I'+str(out),str(generated),'-o',str(out/'test.exe')]
subprocess.run(cmd,check=True)
result=subprocess.run([str(out/'test.exe')],capture_output=True,text=True)
checks=dict(actual_compiled_table_and_resolver=result.returncode==0 and result.stdout.startswith('PASS '))
paths=[Path(__file__),build_path,maintained,test,ROOT/'engine/runner/tlk_resource_parent.h']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,command=cmd,stdout=result.stdout,stderr=result.stderr,
    scope='Current compiled table and maintained resolver: inherited artwork follows Graphics, leaf overrides work, final-life timing independent both ways, implemented availability plus existing full parent/insertion suite.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()}),indent=2)+'\n')
print(result.returncode,result.stdout,result.stderr,flush=True)

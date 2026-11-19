"""Private read-only native death/controller and gorilla-token observer."""
import json,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
bp=ROOT/'build/hakuna829/build-report.json';b=bound(bp);out=ROOT/'build/hakuna835-observer';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
src=out/'tlk_audio.c';s=(ROOT/'build/next771/game/tlk_audio.c').read_text() if False else (ROOT/'engine/runner/tlk_audio.c').read_text()
# This translation unit normally includes patched ownership history. Use the
# actual staged source from the qualified build rather than dropping patches.
stage=Path(b['compiles']['audio'][b['compiles']['audio'].index('-c')+1]);assert stage.is_file();s=stage.read_text()
s=s.replace('void TlkAudioFrame(unsigned value) {',r'''void TlkAudioFrame(unsigned value) {
    static FILE *audit;static unsigned last_health=~0u,last_action=~0u,last_level=~0u;
    if(getenv("TLK_LATER_CONTROLLER_TRACE")) {
        if(!audit){audit=fopen(getenv("TLK_LATER_CONTROLLER_TRACE"),"w");fprintf(audit,"frame,level,health,lives,age,action,x,y\n");}
        unsigned action=address(0xb243),level=word(0x1ff9e),health=word(0x2004);
        if(last_health!=health || last_action!=action || last_level!=level){fprintf(audit,"%u,%u,%u,%u,%u,%06x,%u,%u\n",value,level,health,word(0x1ffaa),word(0x2000),action,word(0xb21b),word(0xb21d));fflush(audit);last_health=health;last_action=action;last_level=level;}
    }
''')
anchor='void TlkAudioAnimationToken(CpuState *cpu,uint32_t pc) {';assert anchor in s
s=s.replace(anchor,anchor+r'''
    if((pc&65535)==0xad50 && word(0x1ff9e)==5 && address(word(0x68)+4)==0xc58a7f && getenv("TLK_LATER_GORILLA_TOKENS")) {
        static FILE *tokens;if(!tokens){tokens=fopen(getenv("TLK_LATER_GORILLA_TOKENS"),"w");fputs("frame,actor,cursor,value\n",tokens);}
        fprintf(tokens,"%u,%04x,%06x,%u\n",frame,word(0x68),address(0x14),cpu->A&255);fflush(tokens);
    }
''');src.write_text(s)
inputs=argv('link '+(bp.parent/'link.rsp').read_text())[1:];cmd=b['compiles']['audio'].copy();old=(cwd/cmd[cmd.index('-o')+1]).resolve();obj=out/'audio.obj'
for flag,value in (('-o',obj),('-MT',obj),('-MF',out/'audio.d'),('-c',src)):cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
ix=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(ix)==1;inputs[ix[0]]=obj.as_posix();rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(bp.parent/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
(out/'report.json').write_text(json.dumps(dict(result='BUILT',scope=__doc__,binary_sha256=digest(out/'player.exe'),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in [Path(__file__),bp,src]}),indent=2)+'\n');print('BUILT',flush=True)

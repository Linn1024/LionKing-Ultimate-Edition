"""Check ownership continuation and transactional rejection against real headers."""
import json
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_semantic_owner_component import SOURCE

EXTRA=r'''
    uint8_t saved[800],again[800],invalid[800];
    /* Queue -> ring -> software/physical -> pending KON -> sounding voice. */
    for(unsigned stage=0;stage<5;stage++) {
        PrideSemanticReset();flow(&cpu,0xc36686);
        if(stage>=1)allocate(7);
        if(stage>=2)PrideSemanticLatchKon(128);
        if(stage>=3)PrideSemanticCommit(7);
        if(stage==4) { flow(&cpu,0xc36686);allocate(5); }
        CHECK(PrideSemanticStateSave(saved,sizeof saved));
        PrideSemanticReset();CHECK(PrideSemanticStateLoad(saved,sizeof saved));
        CHECK(PrideSemanticStateSave(again,sizeof again));CHECK(!memcmp(saved,again,sizeof saved));
        for(unsigned length=0;length<800;length++)CHECK(!PrideSemanticStateLoad(saved,length));
        memcpy(invalid,saved,800);SemPut32(invalid+8,2);
        CHECK(!PrideSemanticStateLoad(invalid,800));
        memcpy(invalid,saved,800);SemPut32(invalid+24,SemGet32(saved+16)+1);
        CHECK(!PrideSemanticStateLoad(invalid,800));
        CHECK(PrideSemanticStateSave(again,800));CHECK(!memcmp(saved,again,800));
    }
'''


def main():
    out=ROOT/'build/pride-lizard-launch-work/semantic-state-component2';out.mkdir()
    stub=out/'snes';stub.mkdir()
    (stub/'interp_bridge.h').write_text('''#include <stdint.h>
typedef struct { unsigned D,DB,m_flag,x_flag,X,Y,S; } CpuState;
static int interp_bridge_add_pre_opcode_hook(unsigned pc,void (*fn)(CpuState *,uint32_t)) { return 1; }
''')
    source=out/'component.c'
    text=SOURCE.replace('#include "native_bounce_semantic_owner2.h"',
        '#include "native_bounce_semantic_owner2.h"\n#include "native_bounce_semantic_save.h"')
    additional='\n    /* Save accepted CPU work and an SPC request before software allocation. */\n    for(unsigned pending=0;pending<2;pending++) {\n        PrideSemanticReset();cpu.D=0x1f00;cpu.DB=0x7e;cpu.m_flag=1;cpu.x_flag=0;\n        cpu.X=0;cpu.S=0x2ce;address(cpu.S+17,0xc36685);cpu_call(SemAccepted,&cpu);\n        uint8_t aram[65536]={0};\n        memcpy(aram+0x1bcb,"\\xf6\\x04\\x02\\x1c\\x5d",5);\n        memcpy(aram+0x1be3,"\\xeb\\xeb\\xf6\\x05\\x02",5);\n        memcpy(aram+0xfd1,"\\xd5\\x51\\x03\\xd5\\xa9\\x03",6);\n        memcpy(aram+0xd34,"\\xd5\\x27\\x05",3);\n        aram[8]=17;aram[0x230]=2;aram[0x231]=17;\n        aram[0x294]=0x15;aram[0x295]=0x3d;aram[0x3d08]=17;aram[0x3d09]=1;\n        if(pending) {\n            cpu.m_flag=0;cpu.Y=0x230;cpu_call(SemTransfer,&cpu);\n            PrideSemanticSpc(0x1bcb,0,0,0x2c,aram);PrideSemanticSpc(0x1be3,4,4,0x2c,aram);\n        }\n        CHECK(PrideSemanticStateSave(saved,800));PrideSemanticReset();\n        CHECK(PrideSemanticStateLoad(saved,800));\n        if(!pending) {\n            cpu.m_flag=0;cpu.Y=0x230;cpu_call(SemTransfer,&cpu);\n            PrideSemanticSpc(0x1bcb,0,0,0x2c,aram);PrideSemanticSpc(0x1be3,4,4,0x2c,aram);\n        }\n        PrideSemanticSpc(0xfd1,0x3d,8,0,aram);PrideSemanticSpc(0xd34,8,7,0,aram);\n        PrideSemanticLatchKon(128);PrideSemanticCommit(7);CHECK(PrideSemanticVoice(7));\n    }\n'
    text=text.replace('    printf("PASS %u semantic ownership checks',EXTRA+additional+'    printf("PASS %u semantic ownership checks')
    source.write_text(text);exe=out/'component.exe'
    command=['C:/mingw32/bin/gcc.exe','-std=c11','-O2','-I',str(out),'-I',str(ROOT/'tools'),str(source),'-o',str(exe)]
    subprocess.run(command,check=True,capture_output=True)
    output=subprocess.check_output([str(exe)],text=True);print(output,end='')
    (out/'run.log').write_text(output)
    paths=[Path(__file__),ROOT/'tools/verify_pride_semantic_owner_component.py',
        ROOT/'tools/native_bounce_semantic_owner2.h',ROOT/'tools/native_bounce_semantic_save.h',source,stub/'interp_bridge.h']
    report=dict(result='PASS',output=output,command=command,
        scope='synthetic ownership serialization and rejected-load neutrality',
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()

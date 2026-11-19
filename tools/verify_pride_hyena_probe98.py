"""Execute the maintained probe adapter inside the complete original walking slice."""
import ctypes as C
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    reference=ROOT/'build/pride-hyena-walk-gate94/report.json';prior=bound(reference);assert prior['result']=='FAIL'
    out=ROOT/'build/pride-hyena-probe98';out.mkdir()
    original=ROOT/'tools/pride_hyena_walk_gate94.c';text=original.read_text()
    text=text.replace('int hyena_walk_gate94(','int hyena_probe_native98(')
    anchor='__declspec(dllexport) int hyena_probe_native98('
    text=text.replace(anchor,'''#include "tlk_hyena_probe.h"
#include "tlk_resources.h"
uint8_t g_ram[0x20000];int snes_frame_counter;
static unsigned selected98=1,hits98;
int TlkResourcesUseMd(const char *id){return selected98 && !strcmp(id,"gameplay.levels.pride_lands.hyena_probe_height");}
__declspec(dllexport) void hyena_probe_source98(unsigned v){selected98=v;hits98=0;}
__declspec(dllexport) unsigned hyena_probe_hits98(void){return hits98;}
'''+anchor)
    anchor='    Interp816 *cpu=interp816_init(NULL,read_bus,write_bus);';assert text.count(anchor)==1
    text=text.replace(anchor,'''    word(0xdf,0x387);ram[0xe1]=0xc0;
    word(actor+4,0x8c68);ram[actor+6]=0xc5;
    word(actor+0x30,0x3c83);ram[actor+0x32]=0xc1;
'''+anchor)
    anchor='        interp816_runOpcode(cpu);';assert text.count(anchor)==1
    text=text.replace(anchor,'''        if(pc==0xc0c5fe || pc==0xc0c6e3) {
            CpuState host={0};host.PB=cpu->k;host.DB=cpu->db;host.D=cpu->dp;
            host.S=cpu->sp;host.A=cpu->a;host.m_flag=cpu->mf;host.x_flag=cpu->xf;host._flag_D=cpu->d;
            memcpy(g_ram,ram,sizeof ram);unsigned before=host.A;
            TlkHyenaWalkingProbe(&host,pc);
            if(host.A!=before)hits98++;
            if(memcmp(g_ram,ram,sizeof ram))invalid_accesses++;
            cpu->a=host.A;
        }
'''+anchor)
    source=out/'oracle.c';source.write_text(text)
    module=ROOT/'engine/runner/tlk_hyena_probe.c';runtime=ROOT/'engine/build-win/tlk-runtime/interp816.c'
    command=['C:/mingw32/bin/gcc.exe','-O2','-shared','-static-libgcc','-I'+str(ROOT/'tools'),'-I'+str(ROOT/'engine/runner'),
             '-I'+str(ROOT/'engine/snesrecomp/runner/src'),'-I'+str(ROOT/'engine/snesrecomp/runner/src/snes'),str(source),str(module),str(runtime),'-o',str(out/'oracle.dll')]
    subprocess.run(command,check=True)
    snespath=ROOT/'Lion King, The (USA).sfc';snes=read_rom(snespath.name,'457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    native=C.CDLL(str(out/'oracle.dll'));native.terrain_native_init.argtypes=[C.c_void_p,C.c_uint]
    native.hyena_probe_native98.argtypes=[C.POINTER(C.c_uint),C.POINTER(C.c_uint)]
    assert native.terrain_native_init(C.create_string_buffer(snes),len(snes))
    count=hits=changed=0;failures=[]
    with (reference.parent/'cases.jsonl').open() as rows,(out/'cases.jsonl').open('w') as log:
        for line in rows:
            row=json.loads(line);args=(C.c_uint*7)(row['dx']&65535,row['terrain'],row['tag'],row['facing'],row['ground'],row['rng'],row['y'])
            actual=[]
            for selected in (0,1):
                native.hyena_probe_source98(selected);raw=(C.c_uint*7)();assert native.hyena_probe_native98(args,raw)
                actual.append(list(raw));hits+=native.hyena_probe_hits98()
            control=actual[0]==row['snes']
            selected=actual[1][:5]+actual[1][6:]==row['md'][:5]+row['md'][6:]
            changed+=actual[0][:5]!=actual[1][:5];count+=1
            result=dict(inputs={k:row[k] for k in ('dx','terrain','tag','facing','ground','rng','y')},native_control=control,selected_md_semantics=selected,actual=actual,md=row['md'])
            log.write(json.dumps(result,separators=(',',':'))+'\n')
            if not(control and selected):failures.append(result)
    checks=dict(all67328_cases=count==67328,native_original_records_unchanged=not any(not r['native_control'] for r in failures),
                selected_decisions_match_original_md=not any(not r['selected_md_semantics'] for r in failures),
                all1284_original_slope_turn_differences_reproduced=changed==1284,actual_original_seams_adjusted=hits>0)
    paths=[Path(__file__),reference,original,module,ROOT/'engine/runner/tlk_hyena_probe.h',ROOT/'tools/pride_enemy_motion_oracle88.c',ROOT/'tools/pride_terrain_native_oracle.c',runtime,snespath]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,fixtures=count,selected_probe_hits=hits,changed_turn_cases=changed,failures=failures,command=command,
                scope='Maintained adapter called at actual original interpreter seams/stack frames during full walking decision slice; native preserved and MD semantic outputs matched to frozen94 original MD ledger. Synthetic uniform maps, no full-game/window claim.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,'hits',hits,'changed',changed,flush=True)


if __name__=='__main__':main()

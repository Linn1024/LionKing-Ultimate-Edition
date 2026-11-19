"""Trace the first hardware-clock divergence without changing guest execution."""
from pathlib import Path

wrapped_diagnostic=Path(__file__).with_name('diagnose_pride_machine_reset.py')
source=wrapped_diagnostic.read_text().replace("out=base/'diagnostic'","out=base/'diagnostic-hardware'")
trace='''static FILE *machine_hw_file;
static uint64_t machine_hw_origin;
static void machine_hw_trace(uint16_t address) {
    if(getenv("TLK_MACHINE_RESET_AT") && !machine_injected)return;
    if(!machine_hw_file) {
        char path[4096];snprintf(path,sizeof path,"%s/hardware.csv",getenv("TLK_SCENE_OWNER_PROBE"));
        machine_hw_file=fopen(path,"w");if(!machine_hw_file)exit(95);
    }
    fprintf(machine_hw_file,"%u,%llu,%04x,%llu\\n",(unsigned)snes_frame_counter,
        (unsigned long long)(g_cpu.master_cycles-machine_hw_origin),address,
        (unsigned long long)g_snes->apu->portClock);
}
'''
extra="    extern void (*g_aot_pace_hw_log)(uint16_t);g_aot_pace_hw_log=machine_hw_trace;\n    if(!snes_frame_counter)machine_hw_origin=g_cpu.master_cycles;\n"
injection="    source=source.replace('void __wrap_TlkResetMachine(void) {',"+repr(trace)+"+'void __wrap_TlkResetMachine(void) {')\n    injected=injected.replace('    _Bool result=',"+repr(extra)+"+'    _Bool result=')\n"
source=source.replace("    generated=out/",injection+"    generated=out/")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),wrapped_diagnostic,')
exec(compile(source,str(wrapped_diagnostic),'exec'))

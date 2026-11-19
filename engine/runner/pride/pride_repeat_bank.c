/* Isolated component integration. Never linked to either distributed host. */
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include "snes/snes.h"
#include "snes/apu.h"
#include "snes/saveload.h"
#include "tlk_native_bank.h"
#include "sha256.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static const char *probe_dir;
static FILE *probe_log;
static uint8_t build_digest[32];
static TlkNativeBankProgram *program;
static TlkNativeBank *prepared;
static unsigned installed,apply_bank,active,applied,candidate_dumped;
static unsigned return_a,return_x,return_y,have_return,record_loaded;
#ifdef TLK_PRIVATE_COMPILED_HOOKS
/* Snapshot/apply must observe the APU at the actual guest instruction boundary,
 * not at the preceding tier-dependent batching flush. This is research-only
 * until both execution modes, PCM and scene lifecycle are verified. */
extern void tlk_bridge_apu_flush(CpuState *cpu);
extern uint64_t s_apu_pending_master;
static void bank_sync_boundary(CpuState *cpu,uint32_t pc) {
    static FILE *log;
    if(!log) {
        char path[2048];snprintf(path,sizeof path,"%s/bank-clock.csv",probe_dir);
        log=TlkPrideFileOpen(path,"w");if(!log)exit(30);
        fprintf(log,"field,pc,master,pending_before,port_before,port_after\n");
    }
    uint64_t pending=s_apu_pending_master,port=g_snes->apu->portClock;
    tlk_bridge_apu_flush(cpu);
    fprintf(log,"%u,%06x,%llu,%llu,%llu,%llu\n",(unsigned)snes_frame_counter+1,pc,
        (unsigned long long)cpu->master_cycles,(unsigned long long)pending,
        (unsigned long long)port,(unsigned long long)g_snes->apu->portClock);fflush(log);
}
#endif
static unsigned word_at(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned address_at(unsigned at) { return word_at(at)|(unsigned)g_ram[at+2]<<16; }
typedef struct ProbeIo { SaveLoadInfo base;FILE *file; } ProbeIo;
static void probe_write(SaveLoadInfo *base,void *data,size_t size) {
    ProbeIo *io=(ProbeIo*)base;if(fwrite(data,1,size,io->file)!=size)exit(30);
}
static void dump(const char *name) {
    char path[2048];snprintf(path,sizeof path,"%s/%s-apu.bin",probe_dir,name);
    FILE *f=TlkPrideFileOpen(path,"wb");if(!f)exit(30);
    ProbeIo io={.base={.func=probe_write},.file=f};apu_saveload(g_snes->apu,&io.base);fclose(f);
    snprintf(path,sizeof path,"%s/%s-wram.bin",probe_dir,name);f=TlkPrideFileOpen(path,"wb");
    if(!f || fwrite(g_ram,1,0x20000,f)!=0x20000)exit(30);fclose(f);
}
static void save_record(void) {
    size_t n=TlkNativeBankRecordSize(prepared);uint8_t *bytes=malloc(n);if(!bytes || !TlkNativeBankSave(prepared,program,bytes,n))exit(30);
    char path[2048];snprintf(path,sizeof path,"%s/bank.record",probe_dir);FILE *f=TlkPrideFileOpen(path,"wb");
    if(!f || fwrite(bytes,1,n,f)!=n)exit(30);fclose(f);free(bytes);
}
static void hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    unsigned field=(unsigned)snes_frame_counter+1;
    if(!active && !word_at(0x1ff9e) && address_at(0xdf)==0xc00387 && !word_at(0x2000)) {
#ifdef TLK_PRIVATE_COMPILED_HOOKS
        if(pc==0xc082bb || pc==0xc082fa)bank_sync_boundary(cpu,pc);
#endif
        if(pc==0xc082bb && !have_return) { return_a=cpu->A;return_x=cpu->X;return_y=cpu->Y;have_return=1; }
        if(pc==0xc082fa && !candidate_dumped) { dump("candidate");candidate_dumped=1; }
        if(!TlkNativeBankReady(prepared,program) && (pc==0xc082bb || pc==0xc082fa) &&
           TlkNativeBankCapture(prepared,program,g_snes->apu,g_ram,0x20000,pc,field)) {
            dump("capture");save_record();fprintf(probe_log,"capture,%u,%06x,0,0,0,0\n",field,pc);fflush(probe_log);
        }
    }
    if(pc==0xc089b7)active=PrideRepeatEligible();
    if(!active)return;
    if(pc==0xc082a5) {
        dump("before");
        if(apply_bank) {
#ifdef TLK_PRIVATE_COMPILED_HOOKS
            bank_sync_boundary(cpu,pc);
#endif
            if(applied || cpu->D || cpu->DB || cpu->m_flag || cpu->x_flag || !TlkNativeBankReady(prepared,program))exit(31);
            uint64_t clock=g_snes->apu->portClock;uint32_t cycles=g_snes->apu->cycles;
            size_t ds=sizeof(Dsp)-offsetof(Dsp,ram);uint8_t *dsp=malloc(ds);if(!dsp)exit(30);
            memcpy(dsp,&g_snes->apu->dsp->ram,ds);
            if(!TlkNativeBankApply(prepared,program,g_snes->apu,g_ram,0x20000,pc)) {
                fprintf(stderr,"native bank apply rejected: ready=%d echo=%04x/%u gains=",TlkNativeBankReady(prepared,program),
                    g_snes->apu->dsp->echoBufferAdr,g_snes->apu->dsp->echoDelay);
                for(unsigned i=0;i<8;i++)fprintf(stderr,"%u,",g_snes->apu->dsp->channel[i].gain);
                fprintf(stderr,"\n");exit(31);
            }
            unsigned same=!memcmp(dsp,&g_snes->apu->dsp->ram,ds);free(dsp);
            if(!same || g_snes->apu->portClock!=clock || g_snes->apu->cycles!=cycles)exit(32);
            dump("applied");applied=1;
            /* These observed original return registers belong to the reload
             * coordinator, independently from the audio-bank component. */
            if(!have_return && !record_loaded)exit(31);
            if(record_loaded) { return_a=0;return_x=0;return_y=16; }
            cpu->A=(uint16_t)return_a;cpu->X=(uint16_t)return_x;cpu->Y=(uint16_t)return_y;
            interp_bridge_pre_opcode_redirect(0xc082b9);
            fprintf(probe_log,"apply,%u,%06x,%u,%u,%u,%llu\n",field,pc,same,g_snes->apu->dsp->sampleRead,
                g_snes->apu->dsp->sampleWrite,(unsigned long long)clock);fflush(probe_log);
        }
    }
    if(pc==0xc082bb)dump("after");
    fprintf(probe_log,"point,%u,%06x,%u,%u,%u,%u\n",field,pc,word_at(0x2004),word_at(0x1ffaa),cpu->S,applied);fflush(probe_log);
    if(pc==0xc32b24) { dump("normal");active=0; }
}
static bool component_frame(uint32 inputs) {
    if(!TlkPrideHealthDeathSelected())return PrideNativeFrame(inputs);
    if(!installed) {
        installed=1;probe_dir=TlkPrideSetting("TLK_NATIVE_BANK_PROBE");if(!probe_dir)exit(30);
        const char *mode=TlkPrideSetting("TLK_NATIVE_BANK_APPLY");apply_bank=mode && !strcmp(mode,"1");
        char path[2048];snprintf(path,sizeof path,"%s/events.csv",probe_dir);probe_log=TlkPrideFileOpen(path,"w");if(!probe_log)exit(30);
        fprintf(probe_log,"event,field,pc,value1,value2,value3,value4\n");
        program=TlkNativeBankProgramCreate(g_rom,0x300000,build_digest);prepared=TlkNativeBankCreate();
        if(!program || !prepared) { fprintf(stderr,"native bank program creation failed\n");exit(30); }
        const char *record=TlkPrideSetting("TLK_NATIVE_BANK_RECORD");
        if(record && *record) {
            FILE *f=TlkPrideFileOpen(record,"rb");if(!f)exit(30);fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);
            if(n<=0 || n>262144)exit(30);uint8_t *bytes=malloc((size_t)n);if(!bytes || fread(bytes,1,(size_t)n,f)!=(size_t)n)exit(30);fclose(f);
            if(!TlkNativeBankLoad(prepared,program,bytes,(size_t)n))exit(30);free(bytes);record_loaded=1;
            fprintf(probe_log,"load,%u,000000,1,0,0,0\n",(unsigned)snes_frame_counter);fflush(probe_log);
        }
        static const uint32_t points[]={0xc082bb,0xc082fa,0xc089b7,0xc082a5,0xc08650,0xc08859,0xc32b24};
        for(unsigned i=0;i<sizeof points/sizeof *points;i++)interp_bridge_add_pre_opcode_hook(points[i],hook);
    }
    return RtlRunFrame(inputs);
}
#undef RtlRunFrame
#define RtlRunFrame component_frame
#ifdef TLK_NATIVE_BANK_SDL
#define main component_headless_main
#define getenv TlkPrideSetting
#include TLK_PRIDE_FRONTEND_SOURCE
#undef getenv
#else
#define main component_headless_main
#include "../headless_main.c"
#endif
#undef main
#include "tlk_pride_save_identity.h"
static const unsigned char kPrideSaveCompatibility[32]={TLK_PRIDE_SAVE_COMPATIBILITY_BYTES};
_Static_assert(sizeof(void *)==4,"save compatibility requires reviewed 32-bit ABI");
int main(int argc,char **argv) {
    memcpy(build_digest,kPrideSaveCompatibility,32);
    int result=component_headless_main(argc,argv);if(probe_log)fclose(probe_log);
    TlkNativeBankFree(prepared);TlkNativeBankProgramFree(program);return result;
}

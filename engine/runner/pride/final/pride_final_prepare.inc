/* Isolated final-life preparation experiment, never selected by resources. */
#include "snes/interp_bridge.h"
static FILE *final_log;
static unsigned final_mode,final_once,final_prepare_installed;
static unsigned FinalWord(unsigned at) {return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned FinalAddress(unsigned at) {return FinalWord(at)|(unsigned)g_ram[at+2]<<16;}
static void FinalPoint(CpuState *cpu,uint32_t pc) {
    if(FinalWord(0x1ff9e) || FinalWord(0x2000))return;
    if(final_log) {fprintf(final_log,"%u,%06x,%u,%u,%06x,%06x,%04x,%04x,%02x,%02x,%u\n",
        (unsigned)snes_frame_counter+1,pc,FinalWord(0x2004),FinalWord(0x1ffaa),
        FinalAddress(0xdf),FinalAddress(0xb243),cpu->S,cpu->D,cpu->DB,cpu->P,final_once);fflush(final_log);}
    if(final_mode && pc==0xc089b9 && !final_once && !FinalWord(0x2004) && !FinalWord(0x1ffaa) &&
       FinalAddress(0xdf)==0xc00387 && FinalAddress(0xb243)==0xc35a82 && FinalWord(0x1ff9c)!=2) {
        if(cpu->D)exit(96);
        final_once=1;interp_bridge_pre_opcode_redirect(0xc08ad9);
    }
}
_Bool __wrap_RtlRunFrame(uint32 inputs) {
    if(!final_prepare_installed) {
        const char *path=getenv("TLK_FINAL_SKIP_LOG"),*mode=ContinueModeSetting("TLK_FINAL_SKIP");
        if(path && !(final_log=fopen(path,"w")))exit(96);
        final_mode=mode && !strcmp(mode,"1");
        if(final_log)fputs("field,pc,health,spares,descriptor,action,stack,direct_page,db,p,redirected\n",final_log);
        static const uint32_t points[]={0xc089b9,0xc08ad9,0xc08b22,0xc08c06,0xc08dc8};
        for(unsigned i=0;i<sizeof points/sizeof *points;i++)
            if(!interp_bridge_add_pre_opcode_hook(points[i],FinalPoint))exit(96);
        final_prepare_installed=1;
    }
    return PrideObservedRunFrame(inputs);
}

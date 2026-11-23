/* Reviewed semantic asset substitution. Installation prepares the native menu
 * bank; preserve the real native caller frame and original RTL handoff. */
#include "snes/snes.h"
#include "snes/dma.h"
/* A complete reviewed mode is selected by the resource leaf. Explicit private
 * flags remain available to replay the frozen pre-integration evidence. */
static const char *ContinueModeSetting(const char *name) {
    if(TlkPrideFinalLifeSelected())return !strcmp(name,"TLK_FINAL_SKIP")?"0":"1";
    return getenv(name);
}
#define __wrap_RtlRunFrame PrideFinalEarlyProbe
#include "pride_final_prepare.inc"
#undef __wrap_RtlRunFrame
static unsigned final_fast_installed,final_fast_mode,final_fast_applied,final_fast_late_mode;
static const uint8_t *final_fast_payload;
static void FinalFastLatePoint(CpuState *cpu,uint32_t pc) {
    FinalPoint(cpu,pc);
    if(!final_fast_late_mode || final_once || FinalWord(0x1ff9e) || FinalWord(0x2000) ||
       FinalWord(0x2004) || FinalWord(0x1ffaa) || FinalWord(0x1ff9c)==2 ||
       (FinalAddress(0xdf)!=0xc00387 && FinalAddress(0xdf)!=0xc0080d) || FinalAddress(0xb243)!=0xc35a82)return;
    if(cpu->D || cpu->DB!=0x7e)exit(96);
    final_once=1;interp_bridge_pre_opcode_redirect(0xc08ad9);
}
static void FinalFastDecodePoint(CpuState *cpu,uint32_t pc) {
    if(!final_fast_mode || !final_once || final_fast_applied || FinalWord(0x1ff9e) ||
       FinalAddress(0xdf)!=0xc0057b || FinalAddress(13)!=0xd545ec || FinalAddress(10)!=0x7f0000)return;
    if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag || cpu->S!=0x2f4 ||
       g_snes->dma->dmaBusy || g_snes->dma->dmaTimer)exit(99);
    for(unsigned i=0;i<8;i++)if(g_snes->dma->channel[i].dmaActive)exit(99);
    FinalPoint(cpu,pc);
    memcpy(g_ram+0x10000,final_fast_payload,TlkFinalNativeRecipeAt(0)->size);
    g_snes->ramAdr=0x18b80;final_fast_applied=1;
    /* No prologue executed, so no DB/P locals were pushed. The native caller
     * replaces its scratch/register inputs before the next asset load. */
    interp_bridge_pre_opcode_redirect(0xc1cd85);
}
_Bool FinalSceneRunNative(uint32 inputs) {
    if(!final_fast_installed) {
        const char *mode=ContinueModeSetting("TLK_FINAL_LATE_SKIP");final_fast_late_mode=mode && !strcmp(mode,"1");
        mode=ContinueModeSetting("TLK_FINAL_FAST_ASSETS");final_fast_mode=mode && !strcmp(mode,"1");
        size_t size=0;
        final_fast_payload=TlkFinalNativePayload(final_native_assets,0,&size);
        if(!final_fast_payload || size!=35712)exit(99);
        if(!interp_bridge_add_pre_opcode_hook(0xc08a59,FinalFastLatePoint) ||
           !interp_bridge_add_pre_opcode_hook(0xc1ccfe,FinalFastDecodePoint) ||
           !interp_bridge_add_pre_opcode_hook(0xc08d83,FinalPoint))exit(99);
        final_fast_installed=1;
    }
    return PrideFinalEarlyProbe(inputs);
}

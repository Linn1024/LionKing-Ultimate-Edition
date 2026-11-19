/* Isolated observer of the remaining native reload decoder ABI/write set.
 * The two wrappers compose deliberately: bank component -> scene observer ->
 * original frame driver. Neither observer changes a decompressor instruction. */
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include "snes/snes.h"
#include "snes/dma.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char *scene_folder;
static FILE *scene_events;
static unsigned scene_installed,scene_calls,scene_active,scene_started,scene_death;
static unsigned scene_source,scene_dest,scene_return,scene_number;
static unsigned scene_word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned scene_long(unsigned at) { return scene_word(at)|(unsigned)g_ram[at+2]<<16; }
static void scene_dump(const char *label) {
    char path[2048];snprintf(path,sizeof path,"%s/%03u-%s-wram.bin",scene_folder,scene_number,label);
    FILE *f=TlkPrideFileOpen(path,"wb");if(!f || fwrite(g_ram,1,0x20000,f)!=0x20000)exit(40);fclose(f);
    snprintf(path,sizeof path,"%s/%03u-%s-dma1.bin",scene_folder,scene_number,label);
    f=TlkPrideFileOpen(path,"wb");if(!f || fwrite(&g_snes->dma->channel[1],1,sizeof(DmaChannel),f)!=sizeof(DmaChannel))exit(40);fclose(f);
}
static void scene_log(CpuState *cpu,const char *event,uint32_t pc) {
    fprintf(scene_events,"%u,%s,%u,%u,%06x,%06x,%06x,%06x,%04x,%02x,%04x,%u,%u,%04x,%04x,%04x,%02x,%u,%u,%u,%06x\n",
        scene_number,event,(unsigned)snes_frame_counter+1,scene_death,pc,scene_source,scene_dest,scene_return,
        cpu->S,cpu->DB,cpu->D,cpu->m_flag,cpu->x_flag,cpu->A,cpu->X,cpu->Y,cpu->P,
        g_snes->nmiEnabled,g_snes->dma->dmaBusy,g_snes->dma->dmaTimer,g_snes->ramAdr);
    fflush(scene_events);
}
#include "pride_scene_template.h"
static void scene_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(pc==0xc1ccfe && !scene_word(0x1ff9e) && scene_long(0xdf)==0xc00387 && !scene_word(0x2000)) {
        if(scene_active)exit(41);
        scene_number=++scene_calls;scene_active=1;scene_started=0;
        scene_source=scene_long(cpu->D+0x0d);scene_dest=scene_long(cpu->D+0x0a);
        /* Only the active owned reload may substitute cached decoder bodies.
         * Ordinary/demo loading after a completed scene remains native. */
        scene_death=owner_scene.started && !owner_ended;
        scene_return=(scene_long(cpu->S+1)&0xff0000)|((scene_long(cpu->S+1)+1)&0xffff);
        scene_log(cpu,"entry",pc);scene_dump("entry");
        interp_bridge_add_pre_opcode_hook(scene_return,scene_hook);
    }
    if(!scene_active)return;
    if(pc==0xc1cd75 && !scene_started) {
        scene_started=1;scene_log(cpu,"loop",pc);scene_dump("loop");
        scene_template_loop(cpu);
    }
    if(pc==0xc1cd83) { scene_template_exit(cpu);scene_log(cpu,"exit",pc);scene_dump("exit"); }
    if(pc==scene_return) {
        scene_log(cpu,"return",pc);scene_dump("return");scene_active=0;
    }
}
static bool scene_frame(uint32 inputs) {
    if(!scene_installed) {
        scene_installed=1;scene_folder=TlkPrideSetting("TLK_SCENE_PREPARE_PROBE");if(!scene_folder || !*scene_folder)exit(40);
        char path[2048];snprintf(path,sizeof path,"%s/decompress.csv",scene_folder);scene_events=TlkPrideFileOpen(path,"w");if(!scene_events)exit(40);
        fprintf(scene_events,"call,event,field,death,pc,source,destination,return_pc,stack,db,direct_page,m,x,a,rx,ry,p,nmi,dma_busy,dma_timer,wram_port\n");
        scene_template_init();
        static const uint32_t points[]={0xc1ccfe,0xc1cd75,0xc1cd83};
        for(unsigned i=0;i<sizeof points/sizeof *points;i++)interp_bridge_add_pre_opcode_hook(points[i],scene_hook);
    }
    return RtlRunFrame(inputs);
}
/* The included component replaces this macro for its host main after its
 * component_frame has bound this wrapper. The redefinition is intentional. */
#undef RtlRunFrame
#define RtlRunFrame scene_frame
#include "pride_repeat_bank.c"

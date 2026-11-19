#include "tlk_terrain.h"
#include "tlk_contact_map.h"
#include "tlk_guest.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>

static int previous_source;
void (*g_tlk_cw_rhino_pc_hook)(CpuState *,uint32_t);
void (*g_tlk_cw_hippo_pc_hook)(CpuState *,uint32_t);
void (*g_tlk_cw_terrain_pc_hook)(CpuState *,uint32_t);
static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
/* Observe immediately after original attribute loads. The following AND/CMP,
 * or PLP followed by AND, establishes the original flags. Nothing is written
 * to the map, collision dictionary, artwork, markers or actor state here. */
static const struct { unsigned pc,below; } loads[]={
    {0xc512,0},{0xc55b,1}, /* floor: current and next row */
    {0xc64a,1},{0xc6b7,0}, /* right wall and left neighbor */
    {0xc734,1},{0xc797,0}, /* left wall and right neighbor */
    {0xc7d0,0},           /* generic wall classifier */
    {0xc8bb,0},{0xc934,0},{0xc9b6,0}, /* ledge probe and neighbors */
    {0xca5e,1},{0xca82,0},{0xcac3,0}, /* ceiling probe */
};
static void pre(CpuState *cpu,uint32_t pc) {
    if (!TlkResourcesUseMd("gameplay.levels.pride_lands.contacts") || !TlkContactMapReady() ||
        word(0x1ff9e) || (word(0xdf)!=0x387 && word(0xdf)!=0x80d) ||
        cpu->D || cpu->DB!=0x7e || word(0xd0)!=TlkContactMapRowBytes()) return;
    unsigned i;
    for (i=0;i<sizeof loads/sizeof loads[0];i++) if ((pc&65535)==loads[i].pc) break;
    if (i==sizeof loads/sizeof loads[0]) return;
    unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16;
    unsigned at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)+(loads[i].below?word(0xd0):0);
    if (base<0x7e0000 || base>0x800000-16000 || at<base || at-base>=16000 || ((at-base)&1)) return;
    unsigned cell=(at-base)/2,live=word(at-0x7e0000),attribute;
    if (!TlkContactMapAttribute(cell,live,cpu->A&255,&attribute)) return;
    static FILE *trace;
    const char *path=getenv("TLK_TERRAIN_TRACE");
    if (path && !trace) { trace=fopen(path,"w");if(trace) fprintf(trace,"pc,cell,map_address,live_word,native,md\n"); }
    if (trace) { fprintf(trace,"%06x,%u,%06x,%04x,%u,%u\n",pc,cell,at,live,cpu->A&255,attribute);fflush(trace); }
    cpu->A=(cpu->A&0xff00)|attribute;
}
void TlkTerrainInstall(void) {
    for (unsigned i=0;i<sizeof loads/sizeof loads[0];i++) {
        interp_bridge_add_pre_opcode_hook(0xc00000|loads[i].pc,pre);
        interp_bridge_add_pre_opcode_hook(loads[i].pc,pre);
    }
}
int TlkTerrainProfileChanged(void) {
    int source=TlkResourcesUseMd("gameplay.levels.pride_lands.contacts") |
        (TlkResourcesUseMd("gameplay.levels.cant_wait.terrain")<<1) |
        (TlkResourcesUseMd("gameplay.levels.cant_wait.hippo_height")<<2) |
        (TlkResourcesUseMd("gameplay.levels.cant_wait.rhino_bounds")<<3) |
        (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.ceiling_rows")<<4) |
        (TlkResourcesUseMd("gameplay.levels.simbas_exile.ceiling_rows")<<5) |
        (TlkResourcesUseMd("gameplay.levels.simbas_exile.ceiling_clearance")<<6) |
        (TlkResourcesUseMd("gameplay.levels.simbas_exile.terrain")<<7) |
        (TlkResourcesUseMd("gameplay.levels.hakuna_matata.terrain")<<8);
    int changed=source!=previous_source;previous_source=source;return changed;
}
RecompReturn TlkTerrainFloorDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc4a7,2); }
RecompReturn TlkTerrainRightDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc5fa,2); }
RecompReturn TlkTerrainRightActorDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc602,2); }
RecompReturn TlkTerrainLeftDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc6df,2); }
RecompReturn TlkTerrainLeftActorDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc6e7,2); }
RecompReturn TlkTerrainWallDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc7c2,2); }
RecompReturn TlkTerrainLedgeDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc855,3); }
RecompReturn TlkTerrainCeilingDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xca1e,3); }

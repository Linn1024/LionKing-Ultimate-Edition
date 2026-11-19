#include "tlk_porcupine_attack_runtime.h"
#include "tlk_porcupine_attack.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned at) {return g_ram[at]|(unsigned)g_ram[at+1]<<8;}
static unsigned address(unsigned at) {return word(at)|(unsigned)g_ram[at+2]<<16;}
static void put(unsigned at,unsigned value) {g_ram[at]=value;g_ram[at+1]=value>>8;}
int TlkPorcupineAttackSelected(void) {return TlkResourcesUseMd("gameplay.levels.pride_lands.porcupine_attack");}
int TlkPorcupineAttackProfileChanged(void) {
    static int previous;int next=TlkPorcupineAttackSelected(),changed=previous!=next;previous=next;return changed;
}
uint32_t TlkPorcupineAttackOpcode(CpuState *cpu,uint32_t pc) {
    if(!TlkPorcupineAttackSelected())return 0;
    unsigned actor=word(0x68),descriptor=address(0xdf);
    if(word(0x1ff9e) || word(0x2000) || (descriptor!=0xc00387 && descriptor!=0xc0080d) ||
       actor<0xb213 || actor>0xc193 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58c5c || address(actor+0x30)!=0xc15b87 ||
       cpu->m_flag || cpu->x_flag || cpu->DB!=0x7e || cpu->D<0x600 || cpu->D>0x1f00 ||
       word(cpu->D)!=actor || word(0xa68c)!=cpu->D+0x22)return 0;
    /* Original C15B87 reserves22 bytes. Its own locals use00/08/0C/10;
     * 14 is unused, inside that allocation, and survives original callees. */
    uint16_t phase=(uint16_t)word(cpu->D+0x14),before=phase;
    uint32_t next=TlkPorcupineAttackBoundary(pc,(uint16_t)word(actor+0x2c),&phase);
    if(phase!=before)put(cpu->D+0x14,phase);
    const char *path=getenv("TLK_PORCUPINE_ATTACK_TRACE");
    if(path && *path) {
        static FILE *log;
        if(!log){log=fopen(path,"w");if(log)fputs("pc,actor,timer,wait,persistent,contact_flag,phase_before,phase_after,next\n",log);}
        if(log){fprintf(log,"%06x,%04x,%u,%u,%u,%u,%u,%u,%06x\n",pc,actor,word(actor+0x2c),word(actor+0x1c),word(actor+0x22),word(actor+0x2e),before,phase,next);fflush(log);}
    }
    return next;
}

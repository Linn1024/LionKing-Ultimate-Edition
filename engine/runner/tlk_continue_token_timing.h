#ifndef TLK_CONTINUE_TOKEN_TIMING_H
#define TLK_CONTINUE_TOKEN_TIMING_H
#include "tlk_continue_token_role.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include <stdio.h>
#include <stdlib.h>

static int TlkContinueTokenTimingSelected(void) {
    return TlkResourcesUseMd("gameplay.levels.pride_lands.continue_token_animation");
}
static int TlkContinueTokenTimingChanged(void) {
    static int previous;int next=TlkContinueTokenTimingSelected(),changed=next!=previous;
    previous=next;return changed;
}
static void TlkContinueTokenTimingPoint(CpuState *cpu,uint32_t pc) {
    /* Shared animation parser's ordinary positive-duration store. Replace the
     * reviewed Sun stream's duration4 with MD5, then let the original STA and
     * countdown run. No host clock, guest code patch or extra saved state. */
    if(pc!=0xc0ad54 || !TlkContinueTokenTimingSelected() || cpu->D || cpu->DB!=0x7e ||
       !cpu->m_flag || !cpu->x_flag || (cpu->A&255)!=4 || (cpu->Y&255)!=0x1a)return;
    unsigned cursor=TlkContinueTokenPointer(g_ram,0x14);
    if(cursor<0xc23e4b || cursor>0xc23e57 || ((cursor-0xc23e4b)&3))return;
    unsigned level=TlkContinueTokenWord(g_ram,0x1ff9e),scene=TlkContinueTokenPointer(g_ram,0xdf);
    if(level>9 || (scene!=0xc00387+level*50 && !(level==0 && scene==0xc0080d)) ||
       TlkContinueTokenWord(g_ram,0x2000)!=(level<6?0:0xffff))return;
    unsigned actor=TlkContinueTokenWord(g_ram,0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127))return;
    unsigned draw=TlkContinueTokenWord(g_ram,actor+12);
    if(draw<0x8000 || draw>0xffe8 ||
       !TlkContinueTokenCommonDrawRole(g_ram,0x20000,draw,
           TlkContinueTokenPointer(g_ram,draw+10),g_ram[draw+9]&0x40))return;
    cpu->A=(cpu->A&0xff00)|5;
    const char *path=getenv("TLK_CONTINUE_TOKEN_TIMING_TRACE");
    if(path && *path) {
        static FILE *log;
        if(!log){log=fopen(path,"w");if(log)fputs("actor,cursor,before,after\n",log);}
        if(log){fprintf(log,"%04x,%06x,4,5\n",actor,cursor);fflush(log);}
    }
}
#endif

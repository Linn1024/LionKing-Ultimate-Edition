#ifndef TLK_CHECKPOINT_TIMING_H
#define TLK_CHECKPOINT_TIMING_H
#include "tlk_checkpoint_role.h"
#include "tlk_resources.h"
#include "common_rtl.h"
#include <stdio.h>
#include <stdlib.h>

static unsigned CheckpointTimingWord(unsigned at) {
    return g_ram[at]|(unsigned)g_ram[at+1]<<8;
}
static unsigned CheckpointTimingPointer(unsigned at) {
    return CheckpointTimingWord(at)|(unsigned)g_ram[at+2]<<16;
}
static void CheckpointTimingPut(unsigned at,unsigned value) {
    g_ram[at]=value;g_ram[at+1]=value>>8;
}
static int TlkCheckpointTimingSelected(void) {
    return TlkResourcesUseMd("gameplay.levels.pride_lands.checkpoint_animation");
}
static int TlkCheckpointTimingChanged(void) {
    static int previous;int next=TlkCheckpointTimingSelected(),changed=next!=previous;
    previous=next;return changed;
}
static unsigned CheckpointTimingActor(void) {
    unsigned actor=CheckpointTimingWord(0x68);
    if(actor<0xb293 || actor>0xc193 || ((actor-0xb213)&127) ||
       CheckpointTimingPointer(actor+4)!=0xc5889a ||
       CheckpointTimingWord(actor+0x2c)!=0xffff || CheckpointTimingWord(0x2000))return 0;
    unsigned draw=CheckpointTimingWord(actor+12);
    if(draw<0x8000 || draw>0xffe8 ||
       !TlkCheckpointDrawRole(g_ram,0x20000,g_rom,0x300000,draw,
         CheckpointTimingPointer(draw+10),g_ram[draw+9]&0x40))return 0;
    return actor;
}
static void CheckpointTimingTrace(unsigned pc,unsigned actor,unsigned phase,unsigned value) {
    const char *path=getenv("TLK_CHECKPOINT_TIMING_TRACE");
    if(path && *path) {
        static FILE *log;
        if(!log){log=fopen(path,"w");if(log)fputs("field,pc,actor,phase,value,cursor,pose\n",log);}
        if(log){unsigned draw=CheckpointTimingWord(actor+12);
            fprintf(log,"%d,%06x,%04x,%u,%u,%06x,%06x\n",snes_frame_counter,pc,actor,phase,value,
                CheckpointTimingPointer(actor+0x12),CheckpointTimingPointer(draw+10));fflush(log);}
    }
}
static unsigned TlkCheckpointTimingOpcode(CpuState *cpu,unsigned pc) {
    if(!TlkCheckpointTimingSelected() || cpu->DB!=0x7e)return 0;
    unsigned actor=CheckpointTimingActor();if(!actor)return 0;
    unsigned phase=CheckpointTimingWord(actor+0x2e);
    if(pc==0xc55750 || pc==0xc557d8) {
        if(cpu->m_flag || cpu->x_flag || cpu->D<0x600 || cpu->D>0x1f00 ||
           CheckpointTimingWord(0xa68c)!=cpu->D+0x22)return 0;
        if(pc==0xc557d8 && CheckpointTimingPointer(actor+0xe)==0xc255d3 && phase==19) {
            /* Native first pose takes two fields to reach the presenter; MD
             * takes one. Four initial waits reproduce MD's first visible blink
             * seven completed fields after contact. Subsequent waits use MD. */
            CheckpointTimingPut(actor+0xe,0x8959);g_ram[actor+0x10]=0xc2;
            CheckpointTimingPut(actor+0x12,0x55f3);g_ram[actor+0x14]=0xc2;
            g_ram[actor+0x1a]=4;CheckpointTimingPut(actor+0x2e,0);
            CheckpointTimingTrace(pc,actor,0,4);
        } else if(pc==0xc55750 && phase<=5 && CheckpointTimingPointer(actor+0xe)==0xc28959 &&
                  CheckpointTimingWord(cpu->D)==actor) {
            /* Keep the original flags gate and one-time contact work; bypass
             * only its finite native animation timer. No host clock/state. */
            CheckpointTimingTrace(pc,actor,phase,g_ram[actor+0x1a]);
            return 0xc5575a;
        }
        return 0;
    }
    if(cpu->D || !cpu->x_flag || phase>5 || CheckpointTimingPointer(actor+0xe)!=0xc28959)return 0;
    unsigned cursor=CheckpointTimingPointer(0x14);
    if(pc==0xc0ad54 && cpu->m_flag && (cpu->A&255)==4 && (cpu->Y&255)==0x1a) {
        unsigned duration=0,next=phase+1;
        if(cursor==0xc255f3 && phase==0)duration=5;
        if(cursor==0xc255f7 && phase==1)duration=20;
        if(cursor==0xc255fb && phase==2)duration=5;
        if(cursor==0xc255ff && (phase==3 || phase==4))duration=90;
        if(cursor==0xc255ff && phase==5){duration=5;next=0;}
        if(duration) {
            cpu->A=(cpu->A&0xff00)|duration;
            /* C28952/C28955 copy one byte into task+2E. The adjacent AA/AB
             * word is the live camera pointer, not animation scratch. */
            g_ram[0xa9]=(uint8_t)next;
            CheckpointTimingTrace(pc,actor,phase,duration);
        }
    } else if(pc==0xc0ad68 && !cpu->m_flag && (cpu->Y&255)==0x0a &&
              cursor==0xc255ff && phase==5 && !g_ram[0xa9]) {
        /* Pose was already read/written from the real base entry. The next
         * original LDA/ADC#4 publishes the beginning of the reviewed stream. */
        CheckpointTimingPut(0x14,0x55ef);
    }
    return 0;
}
#endif

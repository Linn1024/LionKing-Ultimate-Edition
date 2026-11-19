#include "tlk_graveyard_gameplay.h"
#include "tlk_resources.h"
#include "tlk_graveyard_data.h"
#include "tlk_graveyard_hyena_owner.h"
#include "tlk_rng_runtime.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
extern void (*g_tlk_graveyard_gameplay_pc_hook)(CpuState *,uint32_t);
static int known,previous;
static unsigned word(unsigned a){return g_ram[a]|(unsigned)g_ram[a+1]<<8;}
static unsigned pointer(unsigned a){return word(a)|(unsigned)g_ram[a+2]<<16;}
static const char *sources[]={"gameplay.levels.elephant_graveyard.vulture_health",
    "gameplay.levels.elephant_graveyard.vulture_bounds",
    "gameplay.levels.elephant_graveyard.hyena_ground_tags",
    "gameplay.levels.elephant_graveyard.hyena_bounds",
    "gameplay.levels.elephant_graveyard.falling_bone_shake",
    "gameplay.levels.elephant_graveyard.hyena_wall_probes",
    "gameplay.levels.elephant_graveyard.falling_bone_support",
    "gameplay.levels.elephant_graveyard.vulture_turn_point",
    "gameplay.levels.elephant_graveyard.vulture_launch_timing"};
static int mask(void){int value=0;for(unsigned i=0;i<sizeof sources/sizeof *sources;i++)if(TlkResourcesUseMd(sources[i]))value|=1<<i;return value;}
static void shake(CpuState *cpu){
    const uint16_t *r=TlkGraveyardShakeRules();unsigned a=word(0x68);
    if(!r || !TlkResourcesUseMd(sources[4]) || cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e)!=2 || pointer(0xdf)!=0xc003eb || a<0xb293 || a>=0xc213 || ((a-0xb213)&127) ||
       pointer(a+48)!=0xc199f9)return;
    unsigned d=pointer(a+4);
    if(d!=0xc58d90 && d!=0xc58da2 && d!=0xc58db4 && d!=0xc58dce && d!=0xc58de8 && d!=0xc58e02)return;
    /* Linked bones start with34,38,42... updates, not just the initial30.
     * MD shakes on every countdown update, including the delayed portion.
     * The C19ACD continuation already excludes initialization and falling;
     * do not suppress real movement/RNG while a neighbor's count exceeds30. */
    unsigned draw=TlkRngRuntimeNextValue(),x=word(a+r[2]),y=(word(a+r[3])+(draw&r[1]))&65535;
    /* Replace fixed horizontal animation with original MD vertical movement.
     * Keep ordinary animation/pose initialization, countdown and drop logic. */
    g_ram[a+8]=(uint8_t)x;g_ram[a+9]=(uint8_t)(x>>8);g_ram[a+10]=(uint8_t)y;g_ram[a+11]=(uint8_t)(y>>8);
    static FILE *f;static int checked;if(!checked){checked=1;const char *p=getenv("TLK_MD_SHAKE_TRACE");if(p){f=fopen(p,"w");if(f)fputs("field,actor,count,x,y,draw\n",f);}}
    if(f){fprintf(f,"%u,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,a,word(a+44),x,y,draw);fflush(f);}
}
static void wall_point(CpuState *cpu,uint32_t pc){
    const uint16_t *r=TlkGraveyardWallRules();unsigned left=pc==0xc0c6e3,a=word(0x68);
    if(!r || !TlkResourcesUseMd(sources[5]) || word(0x1ff9e)!=2 || pointer(0xdf)!=0xc003eb ||
       cpu->D || cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag || cpu->_flag_D || cpu->Y!=10 ||
       a<0xb293 || a>=0xc213 || ((a-0xb213)&127) || !TlkGraveyardHyenaDescriptor(pointer(a+4)) ||
       pointer(a+48)!=0xc13c83 || cpu->A!=word(a+10)+r[0] ||
       word(cpu->S+1)!=(left?0xc816:0xc840) || word(cpu->S+6)!=(left?0x4070:0x408b) ||
       g_ram[cpu->S+8]!=0xc1 || word(cpu->S+9)!=r[left?2:3])return;
    unsigned before=cpu->A;cpu->A=(uint16_t)(before-r[1]);cpu->_flag_Z=!cpu->A;cpu->_flag_N=!!(cpu->A&32768);
    cpu->P=(cpu->P&~0x82)|(cpu->_flag_Z?2:0)|(cpu->_flag_N?0x80:0);
    static FILE *f;static int checked;if(!checked){checked=1;const char*p=getenv("TLK_GRAVEYARD_WALL_TRACE");
        if(p){f=fopen(p,"w");if(f)fputs("field,actor,left,x,native_y,md_y\n",f);}}
    if(f){fprintf(f,"%u,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,a,left,word(a+8),before,cpu->A);fflush(f);}
}
static void observe(CpuState *cpu,uint32_t pc){
    if(pc==0xc17157){
        unsigned actor=word(0x68),native,external;
        if(word(0x1ff9e)!=2 || pointer(0xdf)!=0xc003eb || cpu->PB!=0xc1 || cpu->DB!=0x7e ||
           cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>0x1fc0 ||
           actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) || pointer(actor+48)==0xc17104 ||
           (pointer(actor+4)!=0xc58cd8 && pointer(actor+4)!=0xc58cf2) || cpu->A || word(cpu->D+14) ||
           !TlkResourcesUseMd(sources[8]) || !TlkGraveyardVultureLaunch(&native,&external) || native)return;
        /* MD's VBlank counter runs across level loading; native A0A is cleared
         * with each scene's work RAM. Use completed guest video fields, whose
         * clock survives scene changes and ordinary save/load. No wall time,
         * route offset or RNG adjustment. Only the original parity branch is
         * selected; constructor, launch count and real RNG calls stay native. */
        unsigned parity=((unsigned)snes_frame_counter+word(0xa6e0))&external;
        cpu->_flag_Z=!parity;cpu->P=(cpu->P&~2)|(cpu->_flag_Z?2:0);
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_GRAVEYARD_LAUNCH_TRACE");opened=1;if(p){trace=fopen(p,"w");
            if(trace)fputs("field,actor,clock,count,mask,wait\n",trace);}}
        if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,actor,
            (unsigned)snes_frame_counter,word(0xa6e0),external,parity);fflush(trace);}
        return;
    }
    if(pc==0xc175d0 || pc==0xc17638){
        unsigned actor=word(0x68),native,external;
        if(word(0x1ff9e)!=2 || pointer(0xdf)!=0xc003eb || cpu->PB!=0xc1 || cpu->DB!=0x7e ||
           cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>0x1fc0 ||
           actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) || pointer(actor+48)!=0xc173e7 ||
           !TlkResourcesUseMd(sources[7]) || !TlkGraveyardVultureTurn(pc==0xc17638,&native,&external) || cpu->A!=native)return;
        unsigned descriptor=pointer(actor+4);
        if(descriptor!=0xc58cca && descriptor!=0xc58cd8 && descriptor!=0xc58ce6 && descriptor!=0xc58cf2 && descriptor!=0xc58d00)return;
        /* Select the original operand; native wing-phase gates, direction,
         * acceleration, contact and movement stores remain in control. */
        cpu->A=(uint16_t)external;cpu->_flag_N=!!(external&32768);cpu->_flag_Z=!external;
        cpu->P=(cpu->P&~0x82)|(cpu->_flag_N?0x80:0)|(cpu->_flag_Z?2:0);
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_GRAVEYARD_VULTURE_TURN_TRACE");opened=1;
            if(p){trace=fopen(p,"w");if(trace)fputs("field,pc,actor,x,y,native,md\n",trace);}}
        if(trace){fprintf(trace,"%u,%06x,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,word(actor+8),word(actor+10),native,external);fflush(trace);}
        return;
    }
    if(pc==0xc19af0){
        unsigned actor=word(0x68),delay;
        if(word(0x1ff9e)!=2 || pointer(0xdf)!=0xc003eb || cpu->PB!=0xc1 || cpu->DB!=0x7e ||
           !cpu->m_flag || cpu->x_flag || cpu->_flag_D || (cpu->A&255)!=120 ||
           actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) || pointer(actor+48)!=0xc199f9 ||
           !TlkResourcesUseMd(sources[6]) || !TlkGraveyardBoneContactDelay(&delay))return;
        const unsigned heads[]={0xc58d90,0xc58da2,0xc58db4,0xc58dce,0xc58de8,0xc58e02};
        for(unsigned i=0;i<sizeof heads/sizeof *heads;i++)if(pointer(actor+4)==heads[i]){
            /* Original MD1A1B58 arms ten updates after each falling update,
             * where native loads120. Its existing byte store owns the timer. */
            cpu->A=(cpu->A&0xff00)|(uint16_t)delay;cpu->_flag_N=!!(delay&128);cpu->_flag_Z=!delay;
            cpu->P=(cpu->P&~0x82)|(cpu->_flag_N?0x80:0)|(cpu->_flag_Z?2:0);
            return;
        }
        return;
    }
    if(pc==0xc0c6e3 || pc==0xc0c5fe){wall_point(cpu,pc);return;}
    if(pc==0xc19acd){shake(cpu);return;}
    if(word(0x1ff9e)!=2 || pointer(0xdf)!=0xc003eb || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>0x1fdb)return;
    unsigned actor=word(0x68);if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127))return;
    unsigned descriptor=pointer(actor+4),draw=word(actor+12),old=cpu->A;const char *event=NULL;
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return;
    if(TlkGraveyardHyenaDescriptor(descriptor) && pointer(actor+0x30)==0xc13c83 && TlkResourcesUseMd(sources[2]) &&
       (pc==0xc140a8 || pc==0xc140ab || pc==0xc140c6 || pc==0xc140c9 ||
        pc==0xc13ed9 || pc==0xc13edc || pc==0xc13f5c || pc==0xc13f5f)) {
        unsigned tag;
        if(TlkGraveyardGroundTag(word(actor+8),word(actor+10),g_ram[actor+0x40],g_ram,&tag)) {
            int left=pc==0xc140a8 || pc==0xc140ab || pc==0xc13f5c || pc==0xc13f5f;
            unsigned result=left?(tag==0x11 || tag==0xfa || tag==0xee || tag==0xec || tag==0x8d || tag==0x8f):
                (tag==0x10 || tag==0xf9 || tag==0xed || tag==0xeb || tag==0x8c || tag==0x8e);
            /* Original classifiers agree; only their installed cell tags differ.
             * Replace the completed result, including LDA's flags. Original
             * stores, turn animation, jump velocity and physics stay in control. */
            cpu->A=result?0xffff:0;cpu->_flag_Z=!result;cpu->_flag_N=result;
            cpu->P=(cpu->P&~0x82)|(result?0x80:0x02);event="hyena_ground_tag";
        }
    }
    if((pc==0xc16d9f || pc==0xc16da0) && descriptor==0xc58cca && !pointer(actor+0x30) &&
       word(0x1ff92)<=2 && cpu->A==word(0x1ff92)+2 && TlkResourcesUseMd(sources[0])){
        /* Both originals decrement health once per successful hit. Only this
         * native initializer adds2; original MD adds1. Original store owns HP. */
        cpu->A--;event="vulture_health";
    }
    static FILE *trace;const char *path=getenv("TLK_GRAVEYARD_GAMEPLAY_TRACE");
    if(event && path){if(!trace){trace=fopen(path,"w");if(trace)fputs("field,event,actor,before,after\n",trace);}
        if(trace){fprintf(trace,"%u,%s,%04x,%u,%u\n",(unsigned)snes_frame_counter+1,event,actor,old,cpu->A);fflush(trace);}}
}
void TlkGraveyardGameplayPrepareSource(void){
    if(!known){previous=mask();known=1;}
    /* Explicit read-only diagnosis also covers stretches without a hyena.
     * Field numbers join the ordinary input-cursor telemetry; no new replay
     * inputs, actor updates or random calls are introduced. */
    static FILE *player;static int player_checked;
    if(!player_checked){const char *path=getenv("TLK_GRAVEYARD_PLAYER_TRACE");player_checked=1;
        if(path){player=fopen(path,"w");if(player)fputs("field,x,y,health,lives,action,words\n",player);}}
    if(player && word(0x1ff9e)==2 && pointer(0xdf)==0xc003eb){
        fprintf(player,"%u,%u,%u,%u,%u,%06x,",(unsigned)snes_frame_counter,
            word(0xb21b),word(0xb21d),word(0x2004),word(0x1ffaa),pointer(0xb243));
        for(unsigned i=0;i<128;i++)fprintf(player,"%02x",g_ram[0xb213+i]);
        fputc('\n',player);fflush(player);
    }
    /* Optional bounded encounter observation. Never changes actor state. */
    static FILE *actors;static int trace_checked;
    if(!trace_checked){const char *path=getenv("TLK_GRAVEYARD_ACTOR_TRACE");trace_checked=1;
        if(path){actors=fopen(path,"w");if(actors)fputs("field,player_x,player_y,actor,descriptor,x,y,action,pose,phase,health\n",actors);}}
    if(actors && word(0x1ff9e)==2 && pointer(0xdf)==0xc003eb){
        for(unsigned actor=0xb293;actor<0xc213;actor+=128){
            if(!TlkGraveyardHyenaDescriptor(pointer(actor+4)))continue;
            unsigned draw=word(actor+12);if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)continue;
            fprintf(actors,"%u,%u,%u,%04x,%06x,%u,%u,%06x,%06x,%u,%u\n",(unsigned)snes_frame_counter,
                word(0xb21b),word(0xb21d),actor,pointer(actor+4),word(actor+8),word(actor+10),
                pointer(actor+0x30),pointer(draw+10),word(actor+0x2e),word(0x2004));
        }fflush(actors);
    }
    g_tlk_graveyard_gameplay_pc_hook=observe;
    interp_bridge_add_pre_opcode_hook(0xc17157,observe);
    interp_bridge_add_pre_opcode_hook(0xc175d0,observe);
    interp_bridge_add_pre_opcode_hook(0xc17638,observe);
    interp_bridge_add_pre_opcode_hook(0xc19acd,observe);
    interp_bridge_add_pre_opcode_hook(0xc19af0,observe);
    interp_bridge_add_pre_opcode_hook(0xc0c6e3,observe);
    interp_bridge_add_pre_opcode_hook(0xc0c5fe,observe);
    interp_bridge_add_pre_opcode_hook(0xc16da0,observe);
    interp_bridge_add_pre_opcode_hook(0xc140ab,observe);
    interp_bridge_add_pre_opcode_hook(0xc140c9,observe);
    interp_bridge_add_pre_opcode_hook(0xc13edc,observe);
    interp_bridge_add_pre_opcode_hook(0xc13f5f,observe);
}
int TlkGraveyardGameplayProfileChanged(void){int selected=mask(),changed=known && selected!=previous;previous=selected;known=1;return changed;}

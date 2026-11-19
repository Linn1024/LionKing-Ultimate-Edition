#include "tlk_roar.h"
#include "tlk_roar_data.h"
#include "tlk_next_scene_data.h"
#include "tlk_graveyard_data.h"
#include "tlk_guest.h"
#include "tlk_resources.h"
#include "tlk_audio.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>

static int previous_source;
static int previous_outro_source;
void (*g_tlk_roar_pc_hook)(CpuState *cpu,uint32_t pc);
static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
static void put(unsigned a,unsigned v) { g_ram[a]=v;g_ram[a+1]=v>>8; }
static int active(void) {
    return TlkRoarDataReady() && TlkResourcesUseMd("gameplay.simba.roar") &&
        ((!word(0x1ff9e) && (word(0xdf)==0x387 || word(0xdf)==0x80d)) ||
         (word(0x1ff9e)==2 && word(0xdf)==0x3eb && g_ram[0xe1]==0xc0) ||
         (word(0x1ff9e)==5 && word(0xdf)==0x481 && g_ram[0xe1]==0xc0) ||
         (word(0x1ff9e)==4 && word(0xdf)==0x44f && g_ram[0xe1]==0xc0)) &&
        !word(0x2000) && word(0x68)==0xb213 && word(0xb243)==0x589c && word(0xb245)==0xc3;
}
static void load(CpuState *cpu,unsigned value) {
    if (cpu->m_flag) {
        cpu->A=(cpu->A&0xff00)|(value&255);
        cpu->_flag_N=!!(value&128);cpu->_flag_Z=!(value&255);
    } else {
        cpu->A=value;cpu->_flag_N=!!(value&32768);cpu->_flag_Z=!(value&65535);
    }
    cpu_mirrors_to_p(cpu);
}
/* Source MD10DFD4..10DFE9 holds the shared last drawing30/80/100
 * updates before phase1, looping at the second hold. Express those native
 * semantic operands in C; no cartridge instruction stream is read here. */
static unsigned exile_outro_byte(unsigned offset) {
    if(offset<12){
        unsigned part=offset&3;
        if(!part)return offset<4?30:offset<8?80:100;
        return (0xc5fa10u>>((part-1)*8))&255;
    }
    if(offset==12)return 0xfa;
    if(offset==13)return 1;
    if(offset==14)return 0xff;
    return (0xc25481u>>((offset-15)*8))&255;
}
static int exile_outro_hold(CpuState *cpu,uint32_t pc) {
    unsigned bank=(pc>>16)&127,at=pc&65535;
    if((bank!=0x40 && bank!=0) || cpu->DB!=0x7e || cpu->D || !cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e)!=4 || word(0xdf)!=0x44f || g_ram[0xe1]!=0xc0 || word(0x68)!=0xb213 ||
       word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
       word(0xb243)!=0xa4c8 || g_ram[0xb245]!=0xc1 ||
       !TlkResourcesUseMd("gameplay.levels.simbas_exile.outro_holds"))return 0;
    unsigned cursor=word(0x14)|(unsigned)g_ram[0x16]<<16,address=cursor,width=1;
    if(at==0xad50 && cpu->m_flag){}
    else if(at==0xad5a && cpu->m_flag)address+=3;
    else if(at==0xad64 && !cpu->m_flag){address++;width=2;}
    else if(at==0xadd2 && cpu->m_flag)address+=2;
    else if(at==0xadd7 && !cpu->m_flag)width=2;
    else if(at==0xae3b && cpu->m_flag){}
    else return 0;
    if(address<0xc2547d || address+width>0xc2548f)return 0;
    unsigned value=0;
    for(unsigned i=0;i<width;i++)value|=exile_outro_byte(address+i-0xc2547d)<<(i*8);
    load(cpu,value);return 1;
}
static int farewell(CpuState *cpu,uint32_t pc) {
    unsigned bank=(pc>>16)&127,at=pc&65535,actor=word(0x68);
    unsigned cursor=word(0x14)|(unsigned)g_ram[0x16]<<16,value,address=cursor,width=1;
    if((bank!=0x40 && bank!=0) || cpu->DB!=0x7e || cpu->D || !cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e)!=2 || word(0xdf)!=0x3eb || g_ram[0xe1]!=0xc0 ||
       actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       word(actor+4)!=0x882c || g_ram[actor+6]!=0xc5 ||
       word(actor+48)!=0x8452 || g_ram[actor+50]!=0xc4 ||
       !TlkResourcesUseMd("gameplay.levels.elephant_graveyard.mufasa_farewell"))return 0;
    if(at==0xad50 && cpu->m_flag) { /* duration or command */ }
    else if(at==0xad5a && cpu->m_flag)address+=3;
    else if(at==0xad64 && !cpu->m_flag){address++;width=2;}
    else if(at==0xadd2 && cpu->m_flag)address+=2;
    else if(at==0xadd7 && !cpu->m_flag)width=2;
    else if(at==0xae3b && cpu->m_flag && cursor==0xc25678) { /* phase2 operand */ }
    else return 0;
    if(!TlkGraveyardFarewellValue(address,width,&value))return 0;
    /* The installed MD program uses native semantic pose identities. Keep
     * both repeated-pose token boundaries, the real phase2 and ordinary loop;
     * the parser owns every cursor advance, wait, event and completion. */
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_FAREWELL_TRACE");if(p){trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,cursor,old,value\n",trace);}}
    if(trace){fprintf(trace,"%u,%06x,%04x,%06x,%u,%u\n",snes_frame_counter+1,pc,actor,cursor,cpu->A,value);fflush(trace);}
    load(cpu,value);return 1;
}
static void pre(CpuState *cpu,uint32_t pc) {
    if(exile_outro_hold(cpu,pc))return;
    if(farewell(cpu,pc))return;
    TlkAudioAnimationToken(cpu,pc);
    TlkAudioAdultRoarPulse(cpu,pc);
    /* MD holds one pose for99 updates where SNES splits the identical pose
     * into119 and35; its next hold is89 instead of34. Fold the adjacent native
     * pose tokens through the original parser cursor, then use its normal
     * wait/store/phase-flag behavior. Timing remains independent of artwork. */
    if((pc&65535)==0xad50 && ((pc>>16)&127)==0x40 && cpu->DB==0x7e && !cpu->D &&
       cpu->m_flag && cpu->x_flag && word(0x1ff9e)==5 && word(0xdf)==0x481 && g_ram[0xe1]==0xc0 &&
       TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_defeat_pauses")){
        unsigned actor=word(0x68),cursor=word(0x14);const uint16_t *r=TlkNextSceneHakunaDefeat();
        if(r && actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           word(actor+4)==0x8a7f && g_ram[actor+6]==0xc5 &&
           word(actor+48)==0x4880 && g_ram[actor+50]==0xc0 && g_ram[0x16]==0xc2){
            unsigned before=cpu->A&255,selected=0;
            if(cursor==0x7da9 && before==r[0] && r[1]==35){put(0x14,cursor+4);selected=r[2];}
            else if(cursor==0x7db3 && before==r[3])selected=r[4];
            if(selected){
                load(cpu,selected);
                static FILE *trace;static int opened;
                if(!opened){const char *p=getenv("TLK_GORILLA_DEFEAT_TRACE");opened=1;if(p)trace=fopen(p,"w");
                    if(trace)fputs("field,actor,cursor,native,selected,next_cursor\n",trace);}
                if(trace){fprintf(trace,"%u,%04x,%04x,%u,%u,%04x\n",snes_frame_counter+1,actor,cursor,before,selected,word(0x14));fflush(trace);}
            }
        }
    }
    /* Original normal gorilla landing: native C27D43 waits59 updates;
     * MD E94D4 waits11. Alternate/final landing C27D9D keeps59 in both.
     * The scoped loaded token is already decoded by the original parser.
     * No cartridge-code reader, host timer or animation/art coupling. */
    if((pc&65535)==0xad50 && ((pc>>16)&127)==0x40 && cpu->DB==0x7e && !cpu->D &&
       cpu->m_flag && cpu->x_flag && (cpu->A&255)==59 &&
       word(0x1ff9e)==5 && word(0xdf)==0x481 && g_ram[0xe1]==0xc0 &&
       word(0x68)>=0xb293 && word(0x68)<0xc213 &&
       word(word(0x68)+4)==0x8a7f && g_ram[word(0x68)+6]==0xc5 &&
       word(0x14)==0x7d43 && g_ram[0x16]==0xc2 &&
       TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_recovery")) {
        load(cpu,11);
        static FILE *trace;const char *path=getenv("TLK_GORILLA_TIMING");
        if(path) {
            if(!trace){trace=fopen(path,"w");if(trace)fputs("field,actor,native,selected\n",trace);}
            if(trace){fprintf(trace,"%u,%04x,59,11\n",(unsigned)snes_frame_counter+1,word(0x68));fflush(trace);}
        }
    }
    /* Original adult action uses the same age-selected pulse comparison twice,
     * for activation and clearing. Keep the native comparison, strength stores,
     * counters, animation, voice source and enemy reactions in control. */
    unsigned level=word(0x1ff9e),native_delay,md_delay;
    if((pc==0xc35955 || pc==0xc35997) && level>=6 && level<=9 &&
       word(0xdf)==0x4b3+(level-6)*50 && g_ram[0xe1]==0xc0 && word(0x2000)==65535 &&
       word(0x68)==0xb213 && word(0xb217)==0x858a && g_ram[0xb219]==0xc5 &&
       word(0xb243)==0x589c && g_ram[0xb245]==0xc3 && cpu->PB==0xc3 && cpu->DB==0x7e &&
       !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D && cpu->D>=0x600 && cpu->D<0x1f00 &&
       word(0xa68c)==cpu->D+0x24 && TlkResourcesUseMd("gameplay.simba.adult_roar") &&
       TlkNextSceneAdultRoar(&native_delay,&md_delay) && word(0xa68e)==native_delay){
        put(0xa68e,md_delay);
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_ADULT_ROAR_TRACE");opened=1;if(p)trace=fopen(p,"w");
            if(trace)fputs("field,pc,counter,native,selected\n",trace);}
        if(trace){fprintf(trace,"%u,%06x,%u,%u,%u\n",snes_frame_counter+1,pc,g_ram[0xb255],native_delay,md_delay);fflush(trace);}
        return;
    }
    if (!active() || cpu->DB!=0x7e) return;
    unsigned at=pc&65535,bank=(pc>>16)&127,value=0;
    const char *event=NULL;
    if (bank==0x43 && !cpu->m_flag && !cpu->x_flag) {
        unsigned marker=(cpu->D+0x22)&65535;
        if (at==0x5955 || at==0x5997) {
            if (word(0xa68e)!=20) return;
            put(0xa68e,TlkRoarFireDelay());value=TlkRoarFireDelay();event="activation_delay";
        } else if (at==0x5971) {
            /* Fire branch has finished setting the roar's active strength.
             * Its duration-result local is dead here. Keep the extra original
             * voice-call continuation in this serialized guest local. */
            put(marker,0x4d52);interp_bridge_pre_opcode_redirect((pc&0xff0000)|0x5a62);event="voice_at_activation";
        } else if (at==0x5a62) {
            if (word(marker)!=0x4d52) {
                /* MD 07DA7A is RTS: no separate update-16 auxiliary cue. */
                interp_bridge_pre_opcode_redirect((pc&0xff0000)|0x5a66);event="skip_auxiliary_voice";
            }
        } else if (at==0x5a66 && word(marker)==0x4d52) {
            put(marker,0);interp_bridge_pre_opcode_redirect((pc&0xff0000)|0x5a7b);event="voice_return";
        }
    } else if ((bank==0x40 || bank==0) && !cpu->D && cpu->x_flag) {
        unsigned cursor=word(0x14)|(unsigned)g_ram[0x16]<<16;
        if (cursor<TLK_ROAR_STREAM) return;
        unsigned offset=cursor-TLK_ROAR_STREAM,index=offset/4,duration,pose;
        if (!TlkRoarToken(index,&duration,&pose)) return;
        if (!(offset&3) && at==0xad50 && cpu->m_flag) value=duration;
        else if (!(offset&3) && duration!=255 && at==0xad5a && cpu->m_flag) value=pose>>16;
        else if (!(offset&3) && duration!=255 && at==0xad64 && !cpu->m_flag) value=pose&65535;
        else if ((offset&3)==1 && duration==255 && at==0xadd2 && cpu->m_flag) value=pose>>16;
        else if ((offset&3)==1 && duration==255 && at==0xadd7 && !cpu->m_flag) value=pose&65535;
        else return;
        /* The original parser still advances/waits/loops. Its immutable ROM
         * cursor is a logical index into the translated MD stream only while
         * this scoped action/source is active; no ROM or scratch script write. */
        load(cpu,value);event="animation_token";
    }
    static FILE *trace;
    const char *path=getenv("TLK_ROAR_TRACE");
    if (event && path) {
        if (!trace) { trace=fopen(path,"w");if(trace) fprintf(trace,"event,pc,counter,cursor,value\n"); }
        if (trace) { fprintf(trace,"%s,%06x,%u,%06x,%u\n",event,pc,g_ram[0xb255],word(0x14)|(unsigned)g_ram[0x16]<<16,value);fflush(trace); }
    }
}
static void after(CpuState *cpu,uint32_t pc) {
    /* The same five original post-load boundaries as the interpreter hooks.
     * Keep the shared parser compiled, including its native callback exits. */
    pre(cpu,pc+2);
}
void TlkRoarInstall(void) {
    g_tlk_roar_pc_hook=after;
    static const unsigned handler[]={0x5955,0x5997,0x5971,0x5a62,0x5a66};
    static const unsigned animation[]={0xad50,0xad5a,0xad64,0xadd2,0xadd7,0xae3b};
    for (unsigned i=0;i<sizeof handler/sizeof handler[0];i++) interp_bridge_add_pre_opcode_hook(0xc30000|handler[i],pre);
    for (unsigned i=0;i<sizeof animation/sizeof animation[0];i++) {
        interp_bridge_add_pre_opcode_hook(0xc00000|animation[i],pre);
        interp_bridge_add_pre_opcode_hook(animation[i],pre);
    }
}
int TlkRoarProfileChanged(void) {
    int source=TlkResourcesUseMd("gameplay.simba.roar"),changed=source!=previous_source;
    int outro=TlkResourcesUseMd("gameplay.levels.simbas_exile.outro_holds");
    changed|=outro!=previous_outro_source;previous_outro_source=outro;
    previous_source=source;return changed;
}
RecompReturn TlkRoarHandlerDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xc3589c,3); }

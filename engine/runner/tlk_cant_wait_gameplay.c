#include "tlk_hitboxes.h"
#include "tlk_cant_wait_gameplay.h"
#include "tlk_cant_wait_data.h"
#include "tlk_cw_terrain.h"
#include "tlk_resources.h"
#include "tlk_guest.h"
#include "tlk_wide.h"
#include "tlk_md_assets.h"
#include "tlk_cw_audio_metadata.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned p){return g_ram[p]|g_ram[p+1]<<8;}
static unsigned pointer(unsigned p){return word(p)|g_ram[p+2]<<16;}
static void exit_pre(CpuState *cpu,uint32_t pc){
    if(pc!=0xc0d1c6 || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       cpu->Y!=8 || pointer(0x6e)!=0x7eb213 || cpu->A!=word(0xb21b) ||
       !TlkResourcesUseMd("gameplay.levels.cant_wait.exit_boundary"))return;
    unsigned native,external;if(!TlkCantWaitExitBoundary(&native,&external))return;
    /* Re-evaluate the original CMP; its BCC and normal level-completion
     * stores/fade/loading keep ownership. No player or input adjustments. */
    unsigned result=(cpu->A-external)&65535;
    cpu->_flag_C=cpu->A>=external;cpu->_flag_Z=!result;cpu->_flag_N=!!(result&32768);cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_KING_EXIT_TRACE");opened=1;
        if(p)trace=fopen(p,"w");if(trace)fputs("field,x,native_boundary,md_boundary,complete\n",trace);}
    if(trace){fprintf(trace,"%u,%u,%u,%u,%u\n",snes_frame_counter+1,cpu->A,native,external,cpu->_flag_C);fflush(trace);}
}
void (*g_tlk_cw_exit_pc_hook)(CpuState *,uint32_t);
static void exit_after(CpuState *cpu,uint32_t pc){exit_pre(cpu,pc+3);}
void TlkCantWaitRidePostOpcode(CpuState *cpu,uint32_t pc){
    if(pc==0xc4c6)pc=0xc0c4c6;
    if(word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 || cpu->DB!=0x7e || cpu->m_flag || cpu->_flag_D)return;
    unsigned native=0,external=0,before=cpu->A,selected=0;
    if(pc==0xc0c4c6){
        /* Original floor query wraps X below loop_base+viewport_width.
         * Pair MD's320 width with its selected loop base (birdX-320),
         * retaining the original lookup, floor shape and actor movement. */
        if((cpu->PB!=0xc0 && cpu->PB) || cpu->D || cpu->x_flag || !word(0xa56) ||
           !TlkCantWaitRideValue(0,&native,&external))return;
        unsigned input=word(0xa56);
        if(before!=((input+native)&65535))return;
        selected=TlkResourcesUseMd("gameplay.camera");
        if(selected){unsigned sum=input+external,result=sum&65535;cpu->A=result;
            cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);
            cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);}
    }else if(pc==0xc4326d){
        unsigned actor=word(0x68);
        if(cpu->PB!=0xc4 || cpu->x_flag || cpu->Y!=0x20 || actor<0xb293 || actor>=0xc213 ||
           ((actor-0xb213)&127) || (pointer(actor+4)!=0xc58c20 && pointer(actor+4)!=0xc58c2c) || pointer(actor+48)!=0xc4317d ||
           !TlkCantWaitRideValue(0,&native,&external))return;
        unsigned input=word(actor+0x20);
        if(before!=((input-native)&65535))return;
        selected=TlkResourcesUseMd("gameplay.camera");
        if(selected){unsigned result=(input-external)&65535;cpu->A=result;
            cpu->_flag_C=input>=external;cpu->_flag_V=!!(((input^external)&(input^result))&32768);
            cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);}
    }else{
        if((cpu->PB!=0xc0 && cpu->PB) || cpu->D || !cpu->x_flag || !word(0xa56))return;
        selected=TlkResourcesUseMd("gameplay.levels.cant_wait.ostrich_obstacles");
        if(pc==0xc0b625 || pc==0xc0b62b){
            unsigned distance,flags;
            if(!TlkCantWaitRideEvent(pointer(0xba),&distance,&flags))return;
            external=pc==0xc0b625?distance:flags;
            if(selected){
                if(pc==0xc0b625){
                    /* Spawn farther ahead for the wide view, but unlock and
                     * finish the ride at the original actual travel distance.
                     * CMP changes only flags; original A and stores remain. */
                    unsigned travel=before;
                    if(flags==16 || flags==65535)travel=(travel-TlkWideRideScriptLead())&65535;
                    unsigned result=(travel-distance)&65535;
                    cpu->_flag_C=travel>=distance;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;
                }else{cpu->A=flags;cpu->_flag_N=!!(flags&32768);cpu->_flag_Z=!flags;}
                cpu_mirrors_to_p(cpu);
            }
        }else if(pc==0xc0bb96){
            unsigned descriptor=pointer(0x8e);
            if((descriptor!=0xc4e18d && descriptor!=0xc4e198 && descriptor!=0xc4e1a3 && descriptor!=0xc4e1ae) ||
               word(0xaa)!=0xb293 || !TlkCantWaitRideValue(1,&native,&external))return;
            unsigned input=word(0xb29b)&0xfff0;
            if(before!=((input+native)&65535))return;
            if(selected){unsigned sum=input+external,result=sum&65535;cpu->A=result;
                cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);
                cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);}
        }else return;
    }
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_RIDE_SCRIPT_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,cursor,travel,camera_x,before,after,md,source_md\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%06x,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,pointer(0xba),word(0xa40),word(0xb29b),before,cpu->A,external,selected);fflush(trace);}
}
void TlkCantWaitOstrichDelayPostOpcode(CpuState *cpu,uint32_t pc){
    if(pc!=0xc439d3 || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->PB!=0xc4 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x22)return;
    unsigned actor=word(0x68),native,external;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(actor+4)!=0xc58690 || pointer(actor+48)!=0xc43979 ||
       !TlkCantWaitOstrichDelay(&native,&external) || cpu->A!=native)return;
    unsigned selected=TlkResourcesUseMd("gameplay.levels.cant_wait.ostrich_obstacles");
    if(selected){cpu->A=external;cpu->_flag_N=!!(external&32768);cpu->_flag_Z=!external;cpu_mirrors_to_p(cpu);}
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_OSTRICH_DELAY_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,actor,native,md,selected,source_md\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,actor,native,external,cpu->A,selected);fflush(trace);}
}
void TlkCantWaitHippoPostOpcode(CpuState *cpu,uint32_t pc){
    if(pc!=0xc49326 || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->PB!=0xc4 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x22 || cpu->Y!=10)return;
    unsigned actor=word(0x68),native,external;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(actor+4)!=0xc58ac7 || !TlkCantWaitHippoOffset(&native,&external))return;
    unsigned input=word(actor+10),before=cpu->A;
    if(before!=((input+native)&65535))return;
    /* The original map marker owns this actor's birth position. Cancel the
     * three co-located hippos; the remaining prepared MD marker is one cell
     * left. Apply that spawn parameter before any motion/contact updates,
     * independently of the platform-height and artwork selections. */
    int mx,my;unsigned x=word(actor+8);
    if(TlkResourcesUseMd("gameplay.levels.cant_wait.hippo_positions") &&
       TlkMdSceneMarkerMove(1,0x2c,(int)x,(int)input,&mx,&my) && my==(int)input) {
        g_ram[actor+8]=(uint8_t)mx;g_ram[actor+9]=(uint8_t)(mx>>8);
        static FILE *positions;static int positions_opened;
        if(!positions_opened){positions_opened=1;const char *path=getenv("TLK_HIPPO_POSITION_TRACE");
            if(path)positions=fopen(path,"w");
            if(positions)fputs("marker,native_x,native_y,md_x,md_y\n",positions);}
        if(positions){fprintf(positions,"44,%u,%u,%d,%d\n",x,input,mx,my);fflush(positions);}
    }
    unsigned selected=TlkResourcesUseMd("gameplay.levels.cant_wait.hippo_height");
    if(selected){unsigned sum=input+external,result=sum&65535;
        cpu->A=result;cpu->_flag_C=sum>65535;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;
        cpu->_flag_V=!!((~(input^external)&(input^result))&32768);cpu_mirrors_to_p(cpu);}
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_HIPPO_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,actor,x,marker_y,native_offset,md_offset,before,after,source_md\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,word(actor+8),input,native,external,before,cpu->A,selected);fflush(trace);}
}
void TlkCantWaitGiraffePostOpcode(CpuState *cpu,uint32_t pc){
    if(pc!=0xc18f74 || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x22 || cpu->Y!=8)return;
    unsigned actor=word(0x68),native,external;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       pointer(actor+4)!=0xc58d80 || pointer(actor+48)!=0xc18f39 || word(actor+52) ||
       !TlkCantWaitGiraffeOffset(&native,&external))return;
    unsigned input=word(actor+8),before=cpu->A;
    if(before!=((input+native)&65535))return;
    unsigned selected=TlkResourcesUseMd("gameplay.levels.cant_wait.giraffe_platforms");
    if(selected){unsigned sum=input+external,result=sum&65535;
        cpu->A=result;cpu->_flag_C=sum>65535;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;
        cpu->_flag_V=!!((~(input^external)&(input^result))&32768);cpu_mirrors_to_p(cpu);}
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_GIRAFFE_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,actor,marker_x,y,native_offset,md_offset,before,after,source_md\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,input,word(actor+10),native,external,before,cpu->A,selected);fflush(trace);}
}
void TlkCantWaitMonkeyGripPostOpcode(CpuState *cpu,uint32_t pc){
    TlkAdultPointsPostOpcode(cpu,pc);
    if((pc!=0xc0cb46 && pc!=0xc0cb54 && pc!=0xc0cb82) || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       (cpu->PB!=0xc0 && cpu->PB) || cpu->DB!=0x7e || cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x1f),draw=word(0x93),pose=pointer(0x99),axis=pc==0xc0cb82;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) || draw<0x8000 || draw>0xffe8 ||
       word(actor+12)!=draw || word(draw+4)!=actor+8 || pointer(draw+10)!=pose || cpu->Y!=20+axis*2)return;
    unsigned descriptor=pointer(actor+4),owner=0,native,external;
    for(unsigned i=0;i<sizeof cw_audio_monkey_descriptors/sizeof *cw_audio_monkey_descriptors;i++)
        owner|=descriptor==cw_audio_monkey_descriptors[i];
    if(!owner || !TlkCantWaitMonkeyGrip(pose,axis,&native,&external))return;
    unsigned selected=TlkResourcesUseMd("gameplay.levels.cant_wait.monkey_grips"),before=cpu->A,result=before;
    if(selected) {
        if(pc==0xc0cb54) {
            unsigned input=(before+native)&65535;result=(input-external)&65535;
            cpu->_flag_C=input>=external;cpu->_flag_V=!!(((input^external)&(input^result))&32768);
        } else {
            unsigned input=(before-native)&65535,sum=input+external;result=sum&65535;
            cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);
        }
        cpu->A=(uint16_t)result;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
    }
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_MONKEY_GRIP_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,pose,axis,native,md,before,after,source_md\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%06x,%u,%04x,%04x,%u,%u,%u\n",snes_frame_counter+1,pc,actor,pose,axis,native,external,before,result,selected);fflush(trace);}
}
void TlkCantWaitRoarPostOpcode(CpuState *cpu,uint32_t pc){
    if((pc!=0xc45687 && pc!=0xc4569c) || word(0x1ff9e)!=1 || pointer(0xdf)!=0xc003b9 ||
       cpu->PB!=0xc4 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x22)return;
    unsigned actor=word(0x68),descriptor,native,external;
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127))return;
    descriptor=pointer(actor+4);unsigned owner=0;
    for(unsigned i=0;i<sizeof cw_audio_monkey_descriptors/sizeof *cw_audio_monkey_descriptors;i++)
        owner|=descriptor==cw_audio_monkey_descriptors[i];
    if(!owner || !TlkCantWaitRoarRange(&native,&external))return;
    unsigned selected=TlkResourcesUseMd("gameplay.levels.cant_wait.monkey_roar_range");
    unsigned distance=cpu->A,bound=selected?external:native,result=(distance-bound)&65535;
    static FILE *trace;static int initialized;
    if(!initialized){const char *p=getenv("TLK_MONKEY_ROAR_TRACE");initialized=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,descriptor,x,y,distance,native,md,source_md\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%06x,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,descriptor,word(actor+8),word(actor+10),distance,native,external,selected);fflush(trace);}
    if(!selected)return;
    /* Re-evaluate the completed original 16-bit CMP. CMP leaves V unchanged;
     * the original BPL and the rest of the actual reaction keep running. */
    cpu->_flag_C=distance>=bound;cpu->_flag_Z=!result;cpu->_flag_N=!!(result&32768);
    cpu_mirrors_to_p(cpu);
}
extern void (*g_tlk_cw_hippo_pc_hook)(CpuState *,uint32_t);
static void hippo_after(CpuState *cpu,uint32_t pc){TlkCantWaitHippoPostOpcode(cpu,pc+3);}
void (*g_tlk_cw_grip_pc_hook)(CpuState *,uint32_t);
static void grip_after(CpuState *cpu,uint32_t pc){TlkCantWaitMonkeyGripPostOpcode(cpu,pc+2);}
void TlkCantWaitGameplayInstall(void){
    g_tlk_cw_exit_pc_hook=exit_after;
    interp_bridge_add_pre_opcode_hook(0xc0d1c6,exit_pre);
    g_tlk_cw_grip_pc_hook=grip_after;
    interp_bridge_add_pre_opcode_hook(0xc0cb46,TlkCantWaitMonkeyGripPostOpcode);
    interp_bridge_add_pre_opcode_hook(0xc0cb54,TlkCantWaitMonkeyGripPostOpcode);
    interp_bridge_add_pre_opcode_hook(0xc0cb82,TlkCantWaitMonkeyGripPostOpcode);
    g_tlk_cw_hippo_pc_hook=hippo_after;
    TlkCwTerrainInstall();
    interp_bridge_add_pre_opcode_hook(0xc49326,TlkCantWaitHippoPostOpcode);
    static const unsigned ride_pcs[]={0xc4326d,0xc0b625,0xc0b62b,0xc0bb96,0xc0c4c6,0x00c4c6};
    for(unsigned i=0;i<sizeof ride_pcs/sizeof *ride_pcs;i++)interp_bridge_add_pre_opcode_hook(ride_pcs[i],TlkCantWaitRidePostOpcode);
    interp_bridge_add_pre_opcode_hook(0xc439d3,TlkCantWaitOstrichDelayPostOpcode);
    interp_bridge_add_pre_opcode_hook(0xc18f74,TlkCantWaitGiraffePostOpcode);
    interp_bridge_add_pre_opcode_hook(0xc45687,TlkCantWaitRoarPostOpcode);
    interp_bridge_add_pre_opcode_hook(0xc4569c,TlkCantWaitRoarPostOpcode);
}

#include "tlk_layout.h"
#include "tlk_destiny_monkey.h"
#include "tlk_guest.h"
#include "tlk_md_assets.h"
#include "tlk_resources.h"
#include "tlk_start_data.h"
#include "tlk_hunt_data.h"
#include "tlk_graveyard_data.h"
#include "tlk_next_scene_data.h"
#include "tlk_late_scene_data.h"
#include "tlk_scar_contact.h"
#include "tlk_adult_ledge.h"
#include "tlk_adult_hyena.h"
#include "tlk_return_hyenas.h"
#include "tlk_return_door.h"
#include "tlk_return_exit.h"
#include "tlk_scar_activation.h"
#include "tlk_be_prepared_gameplay.h"
#include "tlk_be_prepared_behavior.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static uint64_t previous_source;
static uint64_t previous_source_extra;
static unsigned previous_toss_reward_eligibility;
static unsigned previous_continue_positions;
static unsigned previous_ending_rain;
static const char *later_start_choices[]={
    "gameplay.levels.simbas_exile.start","gameplay.levels.hakuna_matata.start",
    "gameplay.levels.simbas_destiny.start","gameplay.levels.be_prepared.start",
    "gameplay.levels.simbas_return.start","gameplay.levels.pride_rock.start"};
void (*g_tlk_layout_pc_hook)(CpuState *cpu,uint32_t pc);
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static void put(unsigned at,int value) { g_ram[at]=(uint8_t)value;g_ram[at+1]=(uint8_t)(value>>8); }
int TlkLayoutProfileChanged(void) {
    uint64_t source=TlkResourcesUseMd("gameplay.levels.pride_lands.pickups") |
               (TlkResourcesUseMd("gameplay.levels.pride_lands.start")<<1) |
               (TlkResourcesUseMd("gameplay.levels.pride_lands.activation")<<2) |
               (TlkResourcesUseMd("gameplay.levels.pride_lands.lizard_reactivation")<<3) |
               (TlkResourcesUseMd("gameplay.hitboxes.simba")<<4) |
               (TlkResourcesUseMd("gameplay.hitboxes.enemies")<<5) |
               (TlkResourcesUseMd("gameplay.levels.pride_lands.ceiling_rows")<<6) |
               (TlkResourcesUseMd("gameplay.levels.pride_lands.ceiling_clearance")<<7) |
               (TlkResourcesUseMd("gameplay.levels.pride_lands.streaming_top")<<8) |
               (TlkResourcesUseMd("gameplay.bonus.bug_toss.start")<<9) |
               (TlkResourcesUseMd("gameplay.bonus.bug_toss.arena")<<10) |
               (TlkResourcesUseMd("gameplay.levels.cant_wait.start")<<11) |
               (TlkResourcesUseMd("gameplay.levels.cant_wait.giraffe_platforms")<<12) |
               (TlkResourcesUseMd("gameplay.levels.cant_wait.ostrich_obstacles")<<13) |
               (TlkResourcesUseMd("gameplay.levels.cant_wait.monkey_roar_range")<<14) |
               (TlkResourcesUseMd("gameplay.levels.cant_wait.rhino_tail_bounds")<<15) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.start")<<16) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.placements1")<<17) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.timer")<<18) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.rewards")<<19) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.bug_bounds")<<20) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.clock_start")<<21) |
               (TlkResourcesUseMd("gameplay.bonus.bug_hunt.movement_profile")<<22) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.start")<<23) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.entry_input_delay")<<24) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.opening_skull_trigger")<<25) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.control_handoff")<<26) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.entry_input_filter")<<27) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bone_bridge_positions")<<28) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bone_contact")<<29) |
               (TlkResourcesUseMd("gameplay.levels.elephant_graveyard.vulture_positions")<<30);
    for(unsigned i=0;i<6;i++)source|=(uint64_t)TlkResourcesUseMd(later_start_choices[i])<<(31+i);
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.movement_bounds")<<37;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.obstacle_lanes")<<38;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.damage")<<39;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.rock_contacts")<<40;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.rock_perspective")<<41;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.simba_bounds")<<42;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.running_timing")<<43;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.simbas_exile.grip_points")<<44;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.simbas_exile.ledge_wall_probes")<<45;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.simbas_exile.exit_start_skip")<<46;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.retry_controls")<<47;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.spider_positions")<<48;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.frog_positions")<<49;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.spider_initialization")<<50;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.streaming_top")<<51;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.grip_points")<<52;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.ledge_wall_probes")<<53;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.ceiling_rows")<<54;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.ceiling_clearance")<<55;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.poison_bug_positions")<<56;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.poison_bug_bounds")<<57;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.checkpoint_positions")<<58;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.fatal_contact_handling")<<59;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.log_positions")<<60;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.log_continuity")<<61;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_arena_positions")<<62;
    source|=(uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_bounds")<<63;
    /* All64 original bits are occupied. Keep further restart choices in a
     * separate word so they remain independent and never shift by64. */
    uint64_t extra=TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_initialization") |
        (TlkResourcesUseMd("gameplay.levels.hakuna_matata.bonus_bug_positions")<<1) |
        (TlkResourcesUseMd("gameplay.levels.hakuna_matata.bonus_bug_bounds")<<2) |
        (TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_defeat_pauses")<<3) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_contact")<<4) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.terrain")<<5) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.obstacle_positions")<<6) |
        (TlkResourcesUseMd("gameplay.hitboxes.adult_points")<<7) |
        (TlkResourcesUseMd("gameplay.simba.adult_turn_motion")<<8) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_positions")<<9) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_surface")<<10) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.arena_barrier")<<11) |
        (TlkResourcesUseMd("gameplay.simba.adult_roar")<<12) |
        (TlkResourcesUseMd("gameplay.simba.adult_ceiling_rows")<<13) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.monkey_behavior")<<14) |
        (TlkResourcesUseMd("gameplay.levels.simbas_destiny.exit_start_skip")<<15) |
        (TlkResourcesUseMd("gameplay.bonus.round_selection")<<16) |
        (TlkResourcesUseMd("gameplay.levels.be_prepared.rock_positions")<<17) |
        (TlkResourcesUseMd("gameplay.levels.be_prepared.terrain")<<18) |
        (TlkResourcesUseMd("gameplay.levels.be_prepared.retry_controls")<<19) |
        (TlkResourcesUseMd("gameplay.levels.simbas_return.terrain")<<20) |
        (TlkResourcesUseMd("gameplay.levels.simbas_return.pickup_positions")<<21) |
        (TlkResourcesUseMd("gameplay.levels.pride_rock.terrain")<<22) |
        (TlkResourcesUseMd("gameplay.levels.pride_rock.object_positions")<<23) |
        (TlkResourcesUseMd("gameplay.levels.pride_rock.scar_contact_response")<<24) |
        (TlkResourcesUseMd("gameplay.simba.adult_ledge_reactions")<<25) |
        (TlkResourcesUseMd("gameplay.enemies.hyenas.adult_culling")<<26) |
        (TlkResourcesUseMd("gameplay.levels.simbas_return.doorway_hyenas")<<27) |
        (TlkResourcesUseMd("gameplay.levels.simbas_return.doorway_timing")<<28) |
        (TlkResourcesUseMd("gameplay.levels.simbas_return.ledge_wall_probes")<<29) |
        (TlkResourcesUseMd("gameplay.levels.simbas_return.exit_timing")<<30) |
        ((uint32_t)TlkResourcesUseMd("gameplay.levels.pride_rock.scar_activation")<<31) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.leaper_bounds")<<32) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.rock_bounds")<<33) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.geyser_projectile_bounds")<<34) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.lava_spread")<<35) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.emitter_positions")<<36) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.geyser_initialization")<<37) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.streaming_top")<<38) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.ledge_wall_probes")<<39) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.leaper_behavior")<<40) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.attack_events")<<41) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.be_prepared.death_update_order")<<42) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.falling_bone_shake")<<43) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.pickup_positions")<<44) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.grip_points")<<45) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bug_positions")<<46) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.hyena_wall_probes")<<47) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.perched_vulture_positions")<<48) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.ledge_wall_probes")<<49) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.upper_bone_position")<<50) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.upper_vulture_positions")<<51) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.falling_bone_support")<<52) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.streaming_top")<<53) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bonus_bug_bounds")<<54) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.elephant_graveyard.mufasa_farewell")<<55) |
        ((uint64_t)TlkResourcesUseMd("gameplay.bonus.bug_toss.culling_bounds")<<56) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.exit_flow")<<57) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.stampede.camera_shake")<<58) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.simbas_exile.falling_rock_bounds")<<59) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.simbas_exile.culling_bounds")<<60) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.hakuna_matata.pickup_positions")<<61) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.cant_wait.hippo_positions")<<62) |
        ((uint64_t)TlkResourcesUseMd("gameplay.levels.simbas_destiny.monkey_positions")<<63);
    unsigned reward_eligibility=TlkResourcesUseMd("gameplay.bonus.bug_toss.reward_eligibility");
    unsigned ending_rain=TlkResourcesUseMd("gameplay.levels.pride_rock.rain");
    unsigned continue_positions=TlkResourcesUseMd("gameplay.continue_token_positions");
    int changed=ending_rain!=previous_ending_rain || source!=previous_source || extra!=previous_source_extra || reward_eligibility!=previous_toss_reward_eligibility || continue_positions!=previous_continue_positions;
    previous_ending_rain=ending_rain;
    previous_continue_positions=continue_positions;
    previous_toss_reward_eligibility=reward_eligibility;
    previous_source=source;previous_source_extra=extra;return changed;
}
RecompReturn TlkMarkerDispatch(CpuState *cpu) { return TlkRunOriginal(cpu,0xb804,2); }
void (*g_tlk_stampede_pc_hook)(CpuState *,uint32_t);
static void stampede_after(CpuState *cpu,uint32_t pc){
    const uint32_t *r=TlkNextSceneStampedeRules();
    if(!r || word(0x1ff9e)!=3 || word(0xdf)!=0x41d || g_ram[0xe1]!=0xc0 ||
       cpu->DB!=0x7e || (cpu->m_flag && pc!=0xc28e3e) || cpu->_flag_D)return;
    unsigned actor=word(0x68),native,external;
    if(pc==0xc0e19f){
        if(!TlkResourcesUseMd("gameplay.levels.stampede.running_timing") || cpu->PB!=0xc0 || !cpu->x_flag || cpu->D ||
           actor!=0xb293 || word(actor+4)!=0x858a || g_ram[actor+6]!=0xc5 ||
           word(actor+48)!=0x5a5b || g_ram[actor+50]!=0xc4 || word(actor+14)!=0xe188 || g_ram[actor+16]!=0xc0 ||
           word(actor+18)!=0xed1c || g_ram[actor+20]!=0xc0 || cpu->A!=r[14])return;
        /* MD's run-start header first yields with the previous draw pose.
         * The native continuation callback already owns its sequence counter;
         * use its existing CLC/RTL no-op for this one dispatch, then allow
         * the ordinary continuation to advance on the next game update. */
        native=r[14];external=r[15];put(actor+14,r[16]);g_ram[actor+16]=0xc0;
        cpu->A=(uint16_t)external;cpu->_flag_Z=external==0;cpu->_flag_N=!!(external&32768);cpu_mirrors_to_p(cpu);
    }else if(pc>=0xc0cf10 && pc<=0xc0cfc7){
        static const struct {unsigned pc,component,operation;} sites[]={
            {0xc0cf10,0,0},{0xc0cf20,2,1},{0xc0cf2f,0,2},{0xc0cf3c,2,2},
            {0xc0cf9b,1,0},{0xc0cfab,3,1},{0xc0cfba,1,2},{0xc0cfc7,3,2}};
        unsigned i;for(i=0;i<sizeof sites/sizeof *sites;i++)if(sites[i].pc==pc)break;
        if(i==sizeof sites/sizeof *sites || !TlkResourcesUseMd("gameplay.levels.stampede.simba_bounds") ||
           cpu->PB!=0xc0 || cpu->D || cpu->x_flag || word(0x6c)!=0xb293 || word(0xb297)!=0x858a || g_ram[0xb299]!=0xc5 ||
           actor<0xb313 || actor>=0xdc13 || ((actor-0xb213)&127) || g_ram[actor+6]!=0xc5)return;
        unsigned desc=word(actor+4);if(desc!=0x8b0c&&desc!=0x8b18&&desc!=0x8b24&&desc!=0x8b30&&desc!=0x8b3c)return;
        unsigned draw=word(0x0a),pose=word(0x0d)|(unsigned)g_ram[0x0f]<<16;
        if(draw<0x8000||draw>0xffe8||word(0xb29f)!=draw||word(draw+4)!=0xb29b||
           (word(draw+10)|(unsigned)g_ram[draw+12]<<16)!=pose||cpu->Y!=12+sites[i].component*2||
           !TlkNextSceneStampedeBox(pose,sites[i].component,&native,&external))return;
        unsigned result,input,before=cpu->A,op=sites[i].operation;
        if(!op){if(before!=native)return;result=external;}
        else if(op==1){input=(before-native)&65535;unsigned sum=input+external;result=sum&65535;cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);}
        else{input=(before+native)&65535;result=(input-external)&65535;cpu->_flag_C=input>=external;cpu->_flag_V=!!(((input^external)&(input^result))&32768);}
        cpu->A=(uint16_t)result;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
    }else if(pc==0xc28e3e){
        if(!TlkResourcesUseMd("gameplay.levels.stampede.rock_perspective") || cpu->PB!=0xc2 || !cpu->m_flag || cpu->x_flag ||
           actor<0xb313 || actor>=0xdc13 || ((actor-0xb213)&127) || word(actor+4)!=0x8b3c || g_ram[actor+6]!=0xc5 ||
           (cpu->A&255)!=r[12])return;
        native=r[12];external=r[13];cpu->A=(cpu->A&0xff00)|external;
        cpu->_flag_Z=external==0;cpu->_flag_N=(external&128)!=0;cpu->P=(cpu->P&~0x82)|(cpu->_flag_Z<<1)|(cpu->_flag_N<<7);
    }else if(pc==0xc4627c){
        if(!TlkResourcesUseMd("gameplay.levels.stampede.damage") || cpu->PB!=0xc4 || cpu->x_flag ||
           word(0x6e)!=0xb293 || word(0xb297)!=0x858a || g_ram[0xb299]!=0xc5 || word(0xb2d9) ||
           actor<0xb313 || actor>=0xdc13 || ((actor-0xb213)&127) || g_ram[actor+6]!=0xc5)return;
        unsigned desc=word(actor+4);if(desc!=0x8b0c && desc!=0x8b18 && desc!=0x8b24 && desc!=0x8b30)return;
        native=r[6];external=r[7];unsigned value=(word(0x2004)+native-external)&65535;put(0x2004,value);
        cpu->_flag_Z=value==0;cpu->_flag_N=(value&0x8000)!=0;cpu->P=(cpu->P&~0x82)|(cpu->_flag_Z<<1)|(cpu->_flag_N<<7);
    }else if(pc==0xc1a3ac || pc==0xc1a3b9){
        if(!TlkResourcesUseMd("gameplay.levels.stampede.rock_contacts") || cpu->PB!=0xc1 || cpu->x_flag ||
           actor<0xb313 || actor>=0xdc13 || ((actor-0xb213)&127) || word(actor+4)!=0x8b3c || g_ram[actor+6]!=0xc5 ||
           word(actor+48)!=0xa35c || g_ram[actor+50]!=0xc1 || cpu->A!=word(actor+30))return;
        unsigned i=pc==0xc1a3ac?8:10;native=r[i];external=r[i+1];unsigned value=(cpu->A-external)&65535;
        cpu->_flag_C=cpu->A>=external;cpu->_flag_Z=value==0;cpu->_flag_N=(value&0x8000)!=0;
        cpu->P=(cpu->P&~0x83)|cpu->_flag_C|(cpu->_flag_Z<<1)|(cpu->_flag_N<<7);
    }else if(pc==0xc0bbf1){
        if(!TlkResourcesUseMd("gameplay.levels.stampede.obstacle_lanes") || cpu->PB!=0xc0 || cpu->D || !cpu->x_flag ||
           (word(0xba)|((unsigned)g_ram[0xbc]&63)<<16)!=r[2] || word(0xa40)<r[3] ||
           actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127) || word(actor+0x44)!=6 ||
           word(actor+4)!=0x8b3c || g_ram[actor+6]!=0xc5 || cpu->A!=r[4])return;
        native=r[4];external=r[5];cpu->A=(uint16_t)external;
        cpu->_flag_Z=external==0;cpu->_flag_N=(external&0x8000)!=0;
        cpu->P=(cpu->P&~0x82)|(cpu->_flag_Z<<1)|(cpu->_flag_N<<7);
    }else{
        if(!TlkResourcesUseMd("gameplay.levels.stampede.movement_bounds") || cpu->PB!=0xc4 || cpu->x_flag ||
           actor!=0xb293 || word(actor+4)!=0x858a || g_ram[actor+6]!=0xc5 || cpu->A!=word(actor+8))return;
        unsigned airborne=pc==0xc45ec5 || pc==0xc45fc4;
        if(!airborne && pc!=0xc45afc && pc!=0xc45b43)return;
        unsigned action=word(actor+0x30)|(unsigned)g_ram[actor+0x32]<<16;
        if(action!=(pc==0xc45ec5?0xc45d93:pc==0xc45fc4?0xc45f2d:0xc45a5b))return;
        native=r[0]+airborne;external=r[1]+airborne;
        unsigned result=(cpu->A-external)&65535;cpu->_flag_C=cpu->A>=external;cpu->_flag_Z=result==0;cpu->_flag_N=(result&0x8000)!=0;
        cpu->P=(cpu->P&~0x83)|cpu->_flag_C|(cpu->_flag_Z<<1)|(cpu->_flag_N<<7);
    }
    static FILE *trace;static int checked;
    if(!checked){checked=1;const char *path=getenv("TLK_STAMPEDE_RULE_TRACE");if(path){trace=fopen(path,"w");if(trace)fputs("field,pc,actor,native,selected,x,y,clock\n",trace);}}
    if(trace){fprintf(trace,"%u,%06x,%04x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,native,external,word(actor+8),word(actor+10),word(0xa40));fflush(trace);}
}
static void stampede_pre(CpuState *cpu,uint32_t pc){stampede_after(cpu,pc-((pc==0xc0bbf3 || pc==0xc28e40 || (pc>=0xc0cf12&&pc<=0xc0cfc9))?2:3));}
/* Original ledge query: selected pose point before native mirroring and stores. */
void (*g_tlk_exile_grip_pc_hook)(CpuState *,uint32_t);
static void exile_grip_after(CpuState *cpu,uint32_t pc){
    int exile=word(0x1ff9e)==4 && word(0xdf)==0x44f;
    int hakuna=word(0x1ff9e)==5 && word(0xdf)==0x481 && word(0xd0)==450 && word(0xd4)==71;
    int graveyard=word(0x1ff9e)==2 && word(0xdf)==0x3eb && word(0xd0)==520 && word(0xd4)==48;
    unsigned level=word(0x1ff9e);
    int adult=level>=6 && level<=9 && word(0xdf)==0x4b3+(level-6)*50 && word(0x2000)==65535;
    const char *choice=graveyard?"gameplay.levels.elephant_graveyard.grip_points":adult?"gameplay.hitboxes.adult_points":hakuna?"gameplay.levels.hakuna_matata.grip_points":"gameplay.levels.simbas_exile.grip_points";
    if((pc!=0xc0c875 && pc!=0xc0c893 && pc!=0xc0c89a) || (!exile && !hakuna && !adult && !graveyard) ||
       g_ram[0xe1]!=0xc0 || cpu->PB!=0xc0 || cpu->DB!=0x7e ||
       cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D || word(0x68)!=0xb213 ||
       word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
       !TlkResourcesUseMd(choice))return;
    unsigned draw=word(0x7c),pose=word(0x99)|(unsigned)g_ram[0x9b]<<16,axis=pc==0xc0c875;
    if(draw<0x8000 || draw>0xffe8 || word(0xb21f)!=draw || word(draw+4)!=0xb21b ||
       (word(draw+10)|(unsigned)g_ram[draw+12]<<16)!=pose || cpu->Y!=20+axis*2)return;
    /* C89C is also reached by the mirrored branch, skipping the ADC.
     * Its interpreter hook must only observe the operation actually taken. */
    if((pc==0xc0c893 && !(g_ram[draw+8]&64)) ||
       (pc==0xc0c89a && (g_ram[draw+8]&64)))return;
    unsigned native,external,before=cpu->A,result,input;
    if(adult?!TlkNextSceneSimbaPoint(pose,axis,&native,&external):!TlkNextSceneExileGrip(pose,axis,&native,&external))return;
    if(axis){if(before!=native)return;result=external;}
    else if(pc==0xc0c893){
        input=(before+native)&65535;result=(input-external)&65535;
        cpu->_flag_C=input>=external;cpu->_flag_V=!!(((input^external)&(input^result))&32768);
    }else{
        input=(before-native)&65535;unsigned sum=input+external;result=sum&65535;
        cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);
    }
    cpu->A=(uint16_t)result;cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_EXILE_GRIP_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,pc,pose,axis,native,md,before,after\n",trace);}}
    if(trace){fprintf(trace,"%u,%06x,%06x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,pose,axis,native,external,before,result);fflush(trace);}
}
static void exile_grip_pre(CpuState *cpu,uint32_t pc){exile_grip_after(cpu,pc-2);}
/* MD1A5EE8 tests held Start after phase1 before the actor wait-word test.
 * This native helper remains interpreted in both execution modes. Extend its
 * existing branch predicate; the original completion store/cleanup still run. */
void (*g_tlk_destiny_exit_pc_hook)(CpuState *,uint32_t);
static void destiny_exit_start_pre(CpuState *cpu,uint32_t pc){
    unsigned actor=word(0x68),native,md;
    if(pc!=0xc1aacd || word(0x1ff9e)!=6 || word(0xdf)!=0x4b3 || g_ram[0xe1]!=0xc0 || word(0x2000)!=65535 ||
       cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || word(actor+4)!=0x86a8 || g_ram[actor+6]!=0xc5 ||
       word(actor+48)!=0xaa3f || g_ram[actor+50]!=0xc1 || cpu->D<0x600 || cpu->D>=0x1f00 ||
       word(cpu->D)!=actor || word(0xa68c)!=cpu->D+0x26 || cpu->Y!=0x2e || cpu->A || word(actor+46) ||
       !TlkResourcesUseMd("gameplay.levels.simbas_destiny.exit_start_skip") ||
       !TlkNextSceneDestinyExitStart(&native,&md) || !(word(0x62)&native))return;
    /* MD tests real held Start before waiting for the caption's phase. Select
     * that predicate; the existing native request branch/loader owns the exit. */
    cpu->A=1;cpu->_flag_N=0;cpu->_flag_Z=0;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_DESTINY_EXIT_START_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,actor,held,phase,native_button,md_button,predicate\n",trace);}}
    if(trace){fprintf(trace,"%u,%04x,%04x,%u,%04x,%04x,1\n",snes_frame_counter+1,actor,word(0x62),word(actor+46),native,md);fflush(trace);}
}
static void destiny_exit_start_after(CpuState *cpu,uint32_t pc){destiny_exit_start_pre(cpu,pc+2);}
/* The native reload marker is not an earned checkpoint. With an MD start,
 * compare saved coordinates against that selected default at both revival
 * decisions. Pride's owned death controller already performs this policy;
 * Stampede explicitly bypasses these comparisons in the original program. */
static void default_revival_compare(CpuState *cpu,uint32_t pc) {
    unsigned level=word(0x1ff9e),axis=pc==0xc087bf || pc==0xc08827;
    if((pc!=0xc087b5 && pc!=0xc087bf && pc!=0xc0881d && pc!=0xc08827) ||
       level<1 || level>9 || level==3 || word(0xdf)!=0x387+level*50 || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       !word(0x1ffa2) || cpu->Y!=22+axis*2 || cpu->A!=word(0x1ffa4+axis*2))return;
    unsigned native,selected;const char *id;
    int ready;
    if(level==1){ready=TlkStartDataCantWaitValue(axis,&native,&selected);id="gameplay.levels.cant_wait.start";}
    else if(level==2){ready=TlkStartDataGraveyardValue(axis,&native,&selected);id="gameplay.levels.elephant_graveyard.start";}
    else {ready=TlkStartDataLaterValue(level,axis,&native,&selected);id=later_start_choices[level-4];}
    if(!ready || !TlkResourcesUseMd(id))return;
    unsigned before=cpu->_flag_C | cpu->_flag_Z<<1 | cpu->_flag_N<<2;
    unsigned native_flags=(cpu->A>=native) | ((cpu->A==native)<<1) | ((((cpu->A-native)&65535)>>15)<<2);
    if(before!=native_flags)return;
    unsigned after=(cpu->A>=selected) | ((cpu->A==selected)<<1) | ((((cpu->A-selected)&65535)>>15)<<2);
    cpu->_flag_C=after&1;cpu->_flag_Z=(after>>1)&1;cpu->_flag_N=(after>>2)&1;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_DEFAULT_REVIVAL_TRACE");if(path)trace=fopen(path,"w");
        if(trace)fputs("field,level,pc,axis,saved,native,selected,before,after,saved_x,saved_y\n",trace);}
    if(trace){fprintf(trace,"%u,%u,%06x,%u,%u,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,level,pc,axis,
        cpu->A,native,selected,before,after,word(0x1ffa4),word(0x1ffa6));fflush(trace);}
}

static void exile_exit_start_pre(CpuState *cpu,uint32_t pc){
    if(pc!=0xc1a630 || word(0x1ff9e)!=4 || word(0xdf)!=0x44f || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1fda || word(0xa68c)!=cpu->D+0x22 ||
       word(0x68)!=0xb213 || word(cpu->D)!=0xb213 || word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
       word(0xb243)!=0xa4c8 || g_ram[0xb245]!=0xc1 || cpu->Y!=0x2e ||
       cpu->A || word(0xb241) || word(0xa6b4)<=1 || !(word(0x62)&0x1000) ||
       !TlkResourcesUseMd("gameplay.levels.simbas_exile.exit_start_skip"))return;
    cpu->A=1;cpu->_flag_N=0;cpu->_flag_Z=0;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_EXILE_EXIT_START_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,phase,held,actor_wait,predicate\n",trace);}}
    if(trace){fprintf(trace,"%u,%u,%04x,%u,%u\n",snes_frame_counter+1,word(0xa6b4),word(0x62),word(0xb241),cpu->A);fflush(trace);}
}
static void exile_wall_pre(CpuState *cpu,uint32_t pc){
    int graveyard=word(0x1ff9e)==2 && word(0xdf)==0x3eb && word(0xd0)==520 && word(0xd4)==48;
    int exile=word(0x1ff9e)==4 && word(0xdf)==0x44f;
    int hakuna=word(0x1ff9e)==5 && word(0xdf)==0x481 && word(0xd0)==450 && word(0xd4)==71;
    int returning=word(0x1ff9e)==8 && word(0xdf)==0x517;
    int prepared=word(0x1ff9e)==7 && word(0xdf)==0x4e5;
    const char *choice=graveyard?"gameplay.levels.elephant_graveyard.ledge_wall_probes":prepared?"gameplay.levels.be_prepared.ledge_wall_probes":returning?"gameplay.levels.simbas_return.ledge_wall_probes":hakuna?"gameplay.levels.hakuna_matata.ledge_wall_probes":"gameplay.levels.simbas_exile.ledge_wall_probes";
    if((pc!=0xc0c627 && pc!=0xc0c711) || (!graveyard && !exile && !hakuna && !returning && !prepared) || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       cpu->Y!=0x48 || word(0x68)!=0xb213 || word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
       !TlkResourcesUseMd(choice))return;
    unsigned native,external,flags=word(0xb25b);
    if(!TlkNextSceneExileWallMask(pc==0xc0c711,&native,&external)||cpu->A!=(flags&native))return;
    cpu->A=(uint16_t)(flags&external);cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_EXILE_WALL_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,pc,flags,native,md,result\n",trace);}}
    if(trace){fprintf(trace,"%u,%06x,%u,%u,%u,%u\n",snes_frame_counter+1,pc,flags,native,external,cpu->A);fflush(trace);}
}
/* Original platform surface query. Keep the original comparisons, flags,
 * support/crumble notification and player stores; supply prepared operands. */
static void destiny_boulder_surface_pre(CpuState *cpu,uint32_t pc){
    unsigned right=pc==0xc0d879 || pc==0xc0d8a1;
    if(!right && pc!=0xc0d887 && pc!=0xc0d897)return;
    if(word(0x1ff9e)!=6 || word(0xdf)!=0x4b3 || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       cpu->Y!=(right?16:12) || !TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_surface"))return;
    unsigned actor=word(0x68),draw=word(0x7c),native,external;
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       (word(actor+4)!=0x88dd && word(actor+4)!=0x88ed) || g_ram[actor+6]!=0xc5 ||
       draw<0x8000 || draw>0xffe8 || word(actor+12)!=draw || word(draw+4)!=actor+8 ||
       word(0x99)!=0x014a || g_ram[0x9b]!=0xc6 || word(draw+10)!=0x014a || g_ram[draw+12]!=0xc6 ||
       !TlkNextSceneDestinyBoulderSurface(right,&native,&external) || cpu->A!=native)return;
    cpu->A=(uint16_t)external;cpu->_flag_N=!!(external&32768);cpu->_flag_Z=!external;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_DESTINY_BOULDER_SURFACE_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,right,native,md,x,y\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,right,native,external,word(actor+8),word(actor+10));fflush(trace);}
}
static void bone_contact_pre(CpuState *cpu,uint32_t pc){
    destiny_boulder_surface_pre(cpu,pc);
    if(word(0x1ff9e)!=2 || word(0xdf)!=0x3eb || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x68),draw=word(0x7c),pose=word(0x99)|(unsigned)g_ram[0x9b]<<16;
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || draw<0x8000 || draw>0xffe8 ||
       word(actor+12)!=draw || word(draw+4)!=actor+8 ||
       (word(draw+10)|(unsigned)g_ram[draw+12]<<16)!=pose)return;
    if(pc==0xc0d8b5 && pose==0xc30001 && word(0x14)==0xddb2 && g_ram[0x16]==0xc0 &&
       cpu->Y==word(0x1f) && TlkResourcesUseMd("gameplay.levels.elephant_graveyard.falling_bone_support")){
        const unsigned heads[]={0xc58d90,0xc58da2,0xc58db4,0xc58dce,0xc58de8,0xc58e02};
        unsigned descriptor=word(actor+4)|(unsigned)g_ram[actor+6]<<16,external;
        for(unsigned i=0;i<sizeof heads/sizeof *heads;i++)if(descriptor==heads[i] &&
           TlkGraveyardHeadSurface(word(0x1f),cpu->A,&external)){
            /* After native byte masking: MD sign-extends its surface byte.
             * Keep the shared helper's original comparisons and position store. */
            cpu->A=(uint16_t)external;cpu->_flag_N=!!(external&32768);cpu->_flag_Z=!external;cpu_mirrors_to_p(cpu);
            return;
        }
    }
    /* MD093450 arms the same failed-support retry byte for the six large
     * falling bones too. Native rechecks immediately, keeping Simba grounded
     * across a falling chain after MD would release him. Their invisible SNES
     * collision pose is shared; it is not evidence of missing artwork. */
    if(pc==0xc0d8ef && cpu->Y==8 && word(0x93)==0xb213 && (g_ram[0xb257]&128) &&
       pose==0xc30001 && TlkResourcesUseMd("gameplay.levels.elephant_graveyard.falling_bone_support")){
        const unsigned heads[]={0xc58d90,0xc58da2,0xc58db4,0xc58dce,0xc58de8,0xc58e02};
        unsigned descriptor=word(actor+4)|(unsigned)g_ram[actor+6]<<16,delay;
        for(unsigned i=0;i<sizeof heads/sizeof *heads;i++)if(descriptor==heads[i] && TlkGraveyardBoneContactDelay(&delay)){
            g_ram[actor+0x64]=(uint8_t)delay;
            static FILE *trace;static int opened;
            if(!opened){const char *p=getenv("TLK_GRAVEYARD_HEAD_SUPPORT_TRACE");opened=1;
                if(p){trace=fopen(p,"w");if(trace)fputs("field,actor,descriptor,x,y,player_x,player_y,delay\n",trace);}}
            if(trace){fprintf(trace,"%u,%04x,%06x,%u,%u,%u,%u,%u\n",snes_frame_counter+1,
                actor,descriptor,word(actor+8),word(actor+10),word(0xb21b),word(0xb21d),delay);fflush(trace);}
            return;
        }
    }
    if(!TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bone_contact"))return;
    const unsigned descriptors[]={0x8e1c,0x8e36,0x8e50,0x8e6a},poses[]={0xc3b437,0xc3b466,0xc3b491,0xc3b4b6},heights[]={0xdde4,0xddff,0xde13,0xde29};
    unsigned family=4;
    for(unsigned i=0;i<4;i++)if(word(actor+4)==descriptors[i] && g_ram[actor+6]==0xc5 && pose==poses[i])family=i;
    if(family==4)return;
    if(pc==0xc0d8ef){
        unsigned player=word(0x93),delay;
        if(cpu->Y!=8 || player!=0xb213 || !(g_ram[player+0x44]&128) ||
           !TlkGraveyardBoneContactDelay(&delay))return;
        /* Same guest byte the native platform dispatcher already decrements.
         * Airborne queries can still bypass the delay, as in original MD.
         * No host timer or player-position/velocity changes. */
        g_ram[actor+0x64]=(uint8_t)delay;
        return;
    }
    unsigned component,index=0,native,external;
    if(pc==0xc0d879 || pc==0xc0d8a1){if(cpu->Y!=16)return;component=2;}
    else if(pc==0xc0d887 || pc==0xc0d897){if(cpu->Y!=12)return;component=0;}
    else if(pc==0xc0d8b2){
        index=word(0x1f);if(cpu->Y!=index || index>=39 || word(0x14)!=heights[family] || g_ram[0x16]!=0xc0)return;
        component=4;
    }else return;
    if(!TlkGraveyardBoneContact(pose,component,index,&native,&external) || cpu->A!=native)return;
    unsigned before=cpu->A;cpu->A=external;cpu->_flag_Z=!external;cpu->_flag_N=!!(external&32768);cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *path=getenv("TLK_GRAVEYARD_BONE_CONTACT_TRACE");opened=1;if(path)trace=fopen(path,"w");
        if(trace)fputs("field,pc,actor,pose,component,index,native,md\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%06x,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,pose,component,index,before,external);fflush(trace);}
}
void (*g_tlk_gy_bone_pc_hook)(CpuState *,uint32_t);
static void bone_contact_after(CpuState *cpu,uint32_t pc){bone_contact_pre(cpu,pc+(pc==0xc0d8b2?3:2));}
static void input_pre(CpuState *cpu,uint32_t pc){
    if((pc!=0xc32857 && pc!=0xc32fe6) || word(0x1ff9e)!=2 || word(0xdf)!=0x3eb || g_ram[0xe1]!=0xc0 ||
       cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>0x1fda ||
       word(0xa68c)!=cpu->D+0x26 || word(0x68)!=0xb213 ||
       word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
       word(0xb243)!=(pc==0xc32857?0x2389:0x2b24) || g_ram[0xb245]!=0xc3 ||
       cpu->A!=word(0x5a) || !TlkGraveyardDataReady() ||
       !TlkResourcesUseMd("gameplay.levels.elephant_graveyard.entry_input_filter"))return;
    /* MD CCB8 is countdown-filtered, before the later wall-mask CCBA.
     * Native5A precedes the countdown;62 follows both filters. Restore the
     * direction bits removed by native wall queries (64), while honoring
     * the existing countdown. Keep raw pad, contacts and tape unchanged.
     * At countdown expiry against a wall, native state cannot distinguish
     * that last suppressed update; retain the native wall-start query. */
    unsigned before=cpu->A,value=word(0xa63)?0:(word(0x62)|(before&word(0x64)&0x300));cpu->A=value;
    cpu->_flag_Z=!value;cpu->_flag_N=!!(value&32768);cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_GRAVEYARD_INPUT_FILTER_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,raw,filtered,countdown\n",trace);}
    if(trace && before!=value){fprintf(trace,"%u,%06x,%04x,%04x,%u\n",snes_frame_counter+1,pc,before,value,word(0xa63));fflush(trace);}
}
void (*g_tlk_gy_input_pc_hook)(CpuState *,uint32_t);
static void input_after(CpuState *cpu,uint32_t pc){input_pre(cpu,pc+3);}
static void handoff_pre(CpuState *cpu,uint32_t pc){
    unsigned native,limit;
    if((pc!=0xc33176 && pc!=0xc33179) || word(0x1ff9e)!=2 ||
       word(0xdf)!=0x3eb || g_ram[0xe1]!=0xc0 || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>0x1fda ||
       word(0xa68c)!=cpu->D+0x26 || word(0x68)!=0xb213 ||
       word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
       word(0xb243)!=0x30ef || g_ram[0xb245]!=0xc3 || (word(0xa52)&1) ||
       !TlkResourcesUseMd("gameplay.levels.elephant_graveyard.control_handoff") ||
       !TlkStartDataGraveyardInputDelay(&native,&limit))return;
    unsigned count=word(0xa63);
    if(pc==0xc33176){
        if(cpu->A || count>limit)return;
        /* MD191F40 changes action without the native STZ A63. The prior
         * native LDA/branch has A=0 here; carry the counter across this STZ
         * in that dead A, then restore both the counter and original A=0.
         * No host pending state: an intervening yield/save retains it. STZ
         * changes no flags, so the original comparison flags stay intact. */
        cpu->A=count;
    }else{
        if(count || cpu->A>limit)return;
        put(0xa63,cpu->A);cpu->A=0;
    }
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_GRAVEYARD_HANDOFF_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,counter_before,counter_after,accumulator\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%u,%u,%u\n",snes_frame_counter+1,pc,count,word(0xa63),cpu->A);fflush(trace);}
}
void (*g_tlk_gy_handoff_pc_hook)(CpuState *,uint32_t);
static void handoff_after(CpuState *cpu,uint32_t pc){handoff_pre(cpu,pc==0xc3316c?0xc33176:0xc33179);}
static void retry_pre(CpuState *cpu,uint32_t pc){
    unsigned native,external,level=word(0x1ff9e);
    const char *choice=level==5?"gameplay.levels.hakuna_matata.retry_controls":level==7?"gameplay.levels.be_prepared.retry_controls":NULL;
    if(pc!=0xc08859 || !choice || word(0xdf)!=(level==7?0x4e5:0x481) || g_ram[0xe1]!=0xc0 ||
       (level==7 && word(0x2000)!=65535) ||
       cpu->D || cpu->DB || cpu->PB!=0xc0 || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       word(0x1ffa2)!=1 || word(0x6e)!=0xb213 ||
       word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 || word(0xb243) || g_ram[0xb245] ||
       !word(0x2004) || word(0xa692) ||
       !TlkResourcesUseMd(choice) ||
       !TlkStartDataRetryInputDelay(&native,&external) || word(0xa63)!=native)return;
    /* This is a global retry service. A default start retains the last
     * constructed actor in68; only the checkpoint-symbol loop selects Simba
     * there. The initialized global hero above owns this input filter.
     * MD1D717E assigns the filter after its idle initializer. The native
     * completion boundary precedes one input/update that initializes idle
     * without movement. B427 decrements before that update,
     * so retain one initialization count plus the prepared MD filter. The
     * existing native decrement/input mask owns all later control handling. */
    put(0xa63,external+1);
    static FILE *trace[2];static int opened[2];unsigned scope=level==7;
    if(!opened[scope]){const char *p=getenv(scope?"TLK_BE_PREPARED_RETRY_TRACE":"TLK_HAKUNA_RETRY_TRACE");opened[scope]=1;if(p)trace[scope]=fopen(p,"w");
        if(trace[scope])fputs("field,pc,native,md_filter,native_initialization,selected,checkpoint\n",trace[scope]);}
    if(trace[scope]){fprintf(trace[scope],"%u,%06x,%u,%u,1,%u,%u\n",snes_frame_counter+1,pc,native,external,word(0xa63),word(0x1ffa2));fflush(trace[scope]);}
}
static void start_pre(CpuState *cpu,uint32_t pc) {
    unsigned level=word(0x1ff9e),scene=word(0xdf);
    if((level==8||level==9) && scene==(level==8?0x517:0x549) && g_ram[0xe1]==0xc0 &&
       ((pc&65535)==0xb7df||(pc&65535)==0x8560)){
        unsigned retry=(pc&65535)==0x8560,row=level==8?550:200,rows=level==8?43:100,bytes=row*rows;
        if(cpu->D||cpu->DB!=0x7e||cpu->m_flag||(!retry&&cpu->x_flag)||cpu->_flag_D||
           (cpu->PB!=0xc0&&cpu->PB)||word(0xd0)!=row||word(0xd4)!=rows||
           !TlkResourcesUseMd(level==8?"gameplay.levels.simbas_return.pickup_positions":"gameplay.levels.pride_rock.object_positions"))return;
        unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16,at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)-2;
        if(base<0x7e0000||base>0x800000-bytes||at<base||at-base>=bytes||((at-base)&1))return;
        unsigned cell=(at-base)/2,x=word(retry?0xa9f:0x14),y=word(retry?0xa97:0x16),md;
        if(x!=(cell%(row/2))*16||y!=(cell/(row/2))*16||
           !TlkLateSceneMarker(level,cell,word(at-0x7e0000),cpu->A&255,&md))return;
        cpu->A=(cpu->A&0xff00)|md;cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);return;
    }
    if(pc==0xc0856e && level==5 && scene==0x481 && g_ram[0xe1]==0xc0){
        if(cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
           cpu->A!=65535 || word(0xa68e)!=65535 || word(0xaa1)!=g_ram[0x0d] ||
           !((g_ram[0x0d]==41 && TlkResourcesUseMd("gameplay.levels.hakuna_matata.bonus_bug_positions")) ||
             (g_ram[0x0d]==1 && TlkResourcesUseMd("gameplay.levels.hakuna_matata.pickup_positions"))))return;
        /* Native7AB7 excludes bonus and life pickups from checkpoint rebuilding.
         * Original MD makes the selected families available after death too.
         * Permit ordinary registration of its selected home; normal activation,
         * contact and bonus collection still decide the outcome. */
        cpu->A=0;cpu->_flag_N=0;cpu->_flag_Z=1;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_HAKUNA_BONUS_RETRY_TRACE");opened=1;if(p)trace=fopen(p,"w");
            if(trace)fputs("field,pc,marker,native,selected,x,y\n",trace);}
        if(trace){fprintf(trace,"%u,%06x,%u,65535,0,%u,%u\n",snes_frame_counter+1,pc,g_ram[0x0d],word(0xa9f),word(0xa97));fflush(trace);}
        return;
    }
    if(pc==0xc08921 && level==5 && scene==0x481 && g_ram[0xe1]==0xc0){
        if(cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
           cpu->A || word(0xa3c) || word(0x2004) || word(0x2000) || word(0xa692) ||
           word(0x6e)!=0xb213 || word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
           !TlkResourcesUseMd("gameplay.levels.hakuna_matata.fatal_contact_handling"))return;
        /* MD1D7848 checks health after ordinary actor updates, before the
         * next pad update. Select the native death entry through the original
         * frame-end callback operand. Its own PEA/RTS pair and death program
         * own the guest frame, presentation, rebuild and control countdown.
         * No pad/tape cursor, actor state, health or guest stack writes here. */
        cpu->A=0x89b7;cpu->_flag_N=1;cpu->_flag_Z=0;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int opened;
        if(!opened){opened=1;const char *p=getenv("TLK_HAKUNA_FATAL_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,pc,health,actor,checkpoint_x,callback\n",trace);}}
        if(trace){fprintf(trace,"%u,%06x,%u,%04x,%u,%04x\n",snes_frame_counter+1,pc,word(0x2004),word(0x6e),word(0x1ffa4),cpu->A);fflush(trace);}
        return;
    }

    if((pc==0xc0cc55 || pc==0xc0cc5b) && level==5 && scene==0x481 && g_ram[0xe1]==0xc0){
        unsigned actor=word(0x68),second=pc==0xc0cc5b;
        if(cpu->D==0 && cpu->DB==0x7e && !cpu->m_flag && cpu->x_flag && !cpu->_flag_D &&
           cpu->Y==9+second && actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           word(actor+4)==0x8a7f && g_ram[actor+6]==0xc5 && !word(actor+48) && !g_ram[actor+50] &&
           word(0x8e)==0x8a7f && g_ram[0x90]==0xc5 && cpu->A==(second?0xc585:0x8589) &&
           TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_initialization")){
            /* Original MD18D474 invokes descriptor0E9250's main1A7DCA
             * during creation; the native descriptor instead has RTL.
             * Supply C03CAF through that same native callback. Its ordinary
             * initialization, timer, gravity and actor update remain in charge. */
            unsigned before=cpu->A;cpu->A=second?0xc03c:0x3caf;
            cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
            static FILE *trace;static int opened;
            if(!opened){const char *p=getenv("TLK_HAKUNA_GORILLA_INIT_TRACE");opened=1;if(p)trace=fopen(p,"w");
                if(trace)fputs("field,pc,actor,axis,native,selected\n",trace);}
            if(trace){fprintf(trace,"%u,%06x,%04x,%u,%04x,%04x\n",snes_frame_counter+1,pc,actor,second,before,cpu->A);fflush(trace);}
            return;
        }
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag || cpu->_flag_D || cpu->Y!=9+second ||
           actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
           word(actor+4)!=0x8e9c || g_ram[actor+6]!=0xc5 || word(actor+48) || g_ram[actor+50] ||
           word(0x8e)!=0x8e9c || g_ram[0x90]!=0xc5 || cpu->A!=(second?0xc585:0x8589) ||
           !TlkResourcesUseMd("gameplay.levels.hakuna_matata.spider_initialization"))return;
        /* Native descriptor's construction callback is the C58589 no-op.
         * MD has initialized its spider before its first ordinary update.
         * Select the native C3A0DA initializer through that same real callback
         * pointer/RTL frame, for initial and streamed/retry spawns alike. */
        unsigned before=cpu->A;cpu->A=second?0xc3a0:0xa0da;
        cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_HAKUNA_SPIDER_INIT_TRACE");opened=1;if(p)trace=fopen(p,"w");
            if(trace)fputs("field,pc,actor,axis,native,selected\n",trace);}
        if(trace){fprintf(trace,"%u,%06x,%04x,%u,%04x,%04x\n",snes_frame_counter+1,pc,actor,second,before,cpu->A);fflush(trace);}
        return;
    }
    if(((pc&65535)==0xb7df || (pc&65535)==0x8560) && level==7 && scene==0x4e5 && g_ram[0xe1]==0xc0){
        unsigned retry=(pc&65535)==0x8560;
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || (!retry && cpu->x_flag) || cpu->_flag_D ||
           word(0xd0)!=610 || word(0xd4)!=45 || !TlkResourcesUseMd("gameplay.levels.be_prepared.rock_positions"))return;
        unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16,at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)-2;
        if(base<0x7e0000 || base>0x800000-27450 || at<base || at-base>=27450 || ((at-base)&1))return;
        unsigned cell=(at-base)/2,native=cpu->A&255,external;
        unsigned x=word(retry?0xa9f:0x14),y=word(retry?0xa97:0x16);
        if(x!=(cell%305)*16 || y!=(cell/305)*16 ||
           !TlkNextSceneBePreparedRock(cell,word(at-0x7e0000),native,&external))return;
        cpu->A=(cpu->A&0xff00)|external;
        static FILE *trace;static int opened;
        if(!opened){opened=1;const char *p=getenv("TLK_BE_PREPARED_ROCK_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,cell,x,y,native,md\n",trace);}}
        if(trace){fprintf(trace,"%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,cell,x,y,native,external);fflush(trace);}
        return;
    }
    if(((pc&65535)==0xb7df || (pc&65535)==0x8560) && level==6 && scene==0x4b3 && g_ram[0xe1]==0xc0){
        unsigned retry=(pc&65535)==0x8560;
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || (!retry && cpu->x_flag) || cpu->_flag_D ||
           word(0xd0)!=604 || word(0xd4)!=44 ||
           (!TlkResourcesUseMd("gameplay.levels.simbas_destiny.obstacle_positions") && !TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_positions") && !TlkResourcesUseMd("gameplay.levels.simbas_destiny.monkey_positions")))return;
        unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16,at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)-2;
        if(base<0x7e0000 || base>0x800000-26576 || at<base || at-base>=26576 || ((at-base)&1))return;
        unsigned cell=(at-base)/2,native=cpu->A&255,external;
        unsigned x=word(retry?0xa9f:0x14),y=word(retry?0xa97:0x16);
        if(x!=(cell%302)*16 || y!=(cell/302)*16 ||
           !((TlkResourcesUseMd("gameplay.levels.simbas_destiny.monkey_positions") && TlkNextSceneDestinyMonkeyMarker(cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.simbas_destiny.obstacle_positions") && TlkNextSceneDestinyMarker(cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.simbas_destiny.boulder_positions") && TlkNextSceneDestinyBoulderMarker(cell,word(at-0x7e0000),native,&external))))return;
        cpu->A=(cpu->A&0xff00)|external;
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_DESTINY_MARKER_TRACE");opened=1;if(p)trace=fopen(p,"w");
            if(trace)fputs("field,cell,x,y,native,md\n",trace);}
        if(trace){fprintf(trace,"%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,cell,x,y,native,external);fflush(trace);}
        return;
    }
    if(((pc&65535)==0xb7df || (pc&65535)==0x8560) && level==5 && scene==0x481 && g_ram[0xe1]==0xc0){
        unsigned retry=(pc&65535)==0x8560;
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || (!retry && cpu->x_flag) || cpu->_flag_D ||
           word(0xd0)!=450 || word(0xd4)!=71 ||
           (!TlkResourcesUseMd("gameplay.levels.hakuna_matata.spider_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.frog_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.poison_bug_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.checkpoint_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.log_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_arena_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.bonus_bug_positions") &&
            !TlkResourcesUseMd("gameplay.levels.hakuna_matata.pickup_positions")))return;
        unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16,at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)-2;
        if(base<0x7e0000 || base>0x800000-31950 || at<base || at-base>=31950 || ((at-base)&1))return;
        unsigned cell=(at-base)/2,native=cpu->A&255,external;
        unsigned x=word(retry?0xa9f:0x14),y=word(retry?0xa97:0x16);
        if(x!=(cell%225)*16 || y!=(cell/225)*16 ||
           !((TlkResourcesUseMd("gameplay.levels.hakuna_matata.spider_positions") && TlkNextSceneHakunaMarker(59,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.frog_positions") && TlkNextSceneHakunaMarker(47,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.poison_bug_positions") && TlkNextSceneHakunaMarker(19,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.checkpoint_positions") && TlkNextSceneHakunaMarker(3,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.log_positions") && TlkNextSceneHakunaMarker(48,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.bonus_bug_positions") && TlkNextSceneHakunaMarker(41,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.pickup_positions") && TlkNextSceneHakunaMarker(1,cell,word(at-0x7e0000),native,&external)) ||
             (TlkResourcesUseMd("gameplay.levels.hakuna_matata.gorilla_arena_positions") &&
              (TlkNextSceneHakunaMarker(15,cell,word(at-0x7e0000),native,&external) || TlkNextSceneHakunaMarker(121,cell,word(at-0x7e0000),native,&external)))))return;
        /* Supply the original selected marker before registration/activation.
         * Added and removed homes use the native list builder and spawn code. */
        cpu->A=(cpu->A&0xff00)|external;
        static FILE *trace;static int opened;
        if(!opened){const char *p=getenv("TLK_HAKUNA_SPIDER_MARKER_TRACE");opened=1;if(p)trace=fopen(p,"w");
            if(trace)fputs("field,cell,x,y,native,md\n",trace);}
        if(trace){fprintf(trace,"%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,cell,x,y,native,external);fflush(trace);}
        return;
    }
    if(pc==0xc196d5 || pc==0xc196f2){
        /* MD Hunt sets CCFA=1, so its two-operand movement queries select
         * the second profile. Native Timon retains 2000=0. Select the same
         * existing operands locally; never change Simba's global age flag. */
        if(level<11 || level>13 || scene!=0x60f+(level-11)*50 || g_ram[0xe1]!=0xc0 ||
           cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
           word(0x68)!=0xb213 || word(0xb217)!=0x858a || g_ram[0xb219]!=0xc5 ||
           word(0x2000) || !TlkHuntDataSize() ||
           !TlkResourcesUseMd("gameplay.bonus.bug_hunt.movement_profile"))return;
        unsigned before=pc==0xc196d5?cpu->A:cpu->X;
        if(before)return;
        if(pc==0xc196d5)cpu->A=1;else cpu->X=1;
        cpu->_flag_Z=0;cpu->_flag_N=0;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int opened;
        if(!opened){const char *path=getenv("TLK_HUNT_PROFILE_TRACE");opened=1;
            if(path)trace=fopen(path,"w");if(trace)fputs("field,pc,native_profile,md_profile\n",trace);}
        if(trace){fprintf(trace,"%u,%06x,0,1\n",(unsigned)snes_frame_counter+1,pc);fflush(trace);}
        return;
    }
    if(pc==0xc58124){
        unsigned actor=word(0x68);
        if(level<11 || level>13 || scene!=0x60f+(level-11)*50 || g_ram[0xe1]!=0xc0 ||
           cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
           actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
           word(actor+4)!=0x85a0 || g_ram[actor+6]!=0xc5 ||
           word(actor+0x30) || word(actor+0x32) || word(actor+0x34) || cpu->A ||
           !TlkResourcesUseMd("gameplay.bonus.bug_hunt.clock_start"))return;
        /* MD8EB2A creates its clock without the native130-update delay.
         * Take the original ready branch instead: it initializes the selected
         * clock and reveals its drawing. The separately owned opening
         * caption remains visible, as it does in the original MD game.
         * Timon already accepts input throughout either introduction. */
        cpu->A=1;cpu->_flag_Z=0;cpu->_flag_N=0;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int initialized;
        if(!initialized){const char *path=getenv("TLK_HUNT_INTRO_TRACE");initialized=1;if(path)trace=fopen(path,"w");
            if(trace)fputs("field,actor,native_delay,md_delay\n",trace);}
        if(trace){fprintf(trace,"%u,%04x,130,0\n",(unsigned)snes_frame_counter+1,actor);fflush(trace);}
        return;
    }
    if(pc==0xc5830a || pc==0xc58327 || pc==0xc58456){
        unsigned actor=word(0x68);
        if(level<11 || level>13 || scene!=0x60f+(level-11)*50 || g_ram[0xe1]!=0xc0 ||
           cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
           actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
           word(actor+4)!=0x85ac || g_ram[actor+6]!=0xc5 ||
           word(actor+0x30)!=0x81fa || g_ram[actor+0x32]!=0xc5 ||
           !TlkResourcesUseMd("gameplay.bonus.bug_hunt.rewards"))return;
        if(pc!=0xc58456){
            /* Native decrements its remaining tally once when a count
             * changes, losing simultaneous catches. Let its own last-count
             * stores consume the real count one catch per controller update.
             * Backlogged catches then reach the same ten-catch thresholds
             * without extra host history or altering the true player count. */
            unsigned consumed=word(actor+0x34),actual=word(0xb231);
            if(cpu->A!=actual || consumed>=actual)return;
            cpu->A=consumed+1;cpu->_flag_Z=!cpu->A;cpu->_flag_N=!!(cpu->A&32768);cpu_mirrors_to_p(cpu);
            return;
        }
        /* MD8EAC2 masks its reward index to one bit. There is no native
         * phase2/max-health reward: make this separate eligibility query
         * false while leaving the real bug count and award stores alone. */
        unsigned count=cpu->A;cpu->A=0;cpu->_flag_Z=1;cpu->_flag_N=0;cpu_mirrors_to_p(cpu);
        static FILE *trace;static int initialized;
        if(!initialized){const char *path=getenv("TLK_HUNT_REWARD_TRACE");initialized=1;if(path)trace=fopen(path,"w");
            if(trace)fputs("field,actor,count,next_phase,health_eligible\n",trace);}
        if(trace){fprintf(trace,"%u,%04x,%u,%u,0\n",(unsigned)snes_frame_counter+1,actor,count,word(actor+0x2c));fflush(trace);}
        return;
    }
    if(pc==0xc5816b || pc==0xc58173 || pc==0xc581cb){
        unsigned actor=word(0x68),native,md,field=pc==0xc5816b?0:pc==0xc58173?1:2;
        if(level<11 || level>13 || scene!=0x60f+(level-11)*50 || g_ram[0xe1]!=0xc0 ||
           cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
           actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
           word(actor+4)!=0x85a0 || g_ram[actor+6]!=0xc5 ||
           !TlkResourcesUseMd("gameplay.bonus.bug_hunt.timer") ||
           !TlkHuntDataTimer(field,&native,&md) || cpu->A!=native)return;
        /* Original stores, decrement/expiry path and HUD own the clock. */
        cpu->A=md;cpu->_flag_Z=!md;cpu->_flag_N=!!(md&32768);cpu_mirrors_to_p(cpu);
        static FILE *trace;static int initialized;
        if(!initialized){const char *path=getenv("TLK_HUNT_TIMER_TRACE");initialized=1;if(path)trace=fopen(path,"w");
            if(trace)fputs("pc,actor,field,native,md\n",trace);}
        if(trace){fprintf(trace,"%06x,%04x,%u,%u,%u\n",pc,actor,field,native,md);fflush(trace);}
        return;
    }
    if(((pc&65535)==0xb7df || (pc&65535)==0x8560) && level==2 && scene==0x3eb && g_ram[0xe1]==0xc0){
        unsigned retry=(pc&65535)==0x8560;
        unsigned skull=!retry && TlkResourcesUseMd("gameplay.levels.elephant_graveyard.opening_skull_trigger"),
            bones=!retry && TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bone_bridge_positions"),
            vultures=!retry && TlkResourcesUseMd("gameplay.levels.elephant_graveyard.vulture_positions"),
            pickups=TlkResourcesUseMd("gameplay.levels.elephant_graveyard.pickup_positions"),
            bugs=TlkResourcesUseMd("gameplay.levels.elephant_graveyard.bug_positions"),
            perched=TlkResourcesUseMd("gameplay.levels.elephant_graveyard.perched_vulture_positions"),
            upper_bone=TlkResourcesUseMd("gameplay.levels.elephant_graveyard.upper_bone_position"),
            upper_vulture=TlkResourcesUseMd("gameplay.levels.elephant_graveyard.upper_vulture_positions");
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || (!retry && cpu->x_flag) || cpu->_flag_D ||
           word(0xd0)!=520 || word(0xd4)!=48 || (!skull && !bones && !vultures && !pickups && !bugs && !perched && !upper_bone && !upper_vulture))return;
        unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16,at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)-2;
        if(base<0x7e0000 || base>0x800000-24960 || at<base || at-base>=24960 || ((at-base)&1))return;
        unsigned cell=(at-base)/2,external,native=cpu->A&255;
        if(word(retry?0xa9f:0x14)!=(cell%260)*16 || word(retry?0xa97:0x16)!=(cell/260)*16 ||
           !((skull && TlkGraveyardRevealMarker(cell,word(at-0x7e0000),native,&external)) ||
             (bones && TlkGraveyardBoneMarker(cell,word(at-0x7e0000),native,&external)) ||
             (vultures && TlkGraveyardVultureMarker(cell,word(at-0x7e0000),native,&external)) ||
             (pickups && TlkGraveyardPickupMarker(cell,word(at-0x7e0000),native,&external)) ||
             (bugs && TlkGraveyardBugMarker(cell,word(at-0x7e0000),native,&external)) ||
             (perched && TlkGraveyardPerchedMarker(cell,word(at-0x7e0000),native,&external)) ||
             (upper_bone && TlkGraveyardUpperMarker(83,cell,word(at-0x7e0000),native,&external)) ||
             (upper_vulture && TlkGraveyardUpperMarker(118,cell,word(at-0x7e0000),native,&external))))return;
        /* Relocate the actual registered marker before activation/list building.
         * Moving a live actor later would miss the earlier original contact.
         * Geometry, native initialization,50-update reveal wait and input
         * ownership remain with the existing controller. PLY/AND own flags. */
        cpu->A=(cpu->A&0xff00)|external;
        static FILE *trace;static int opened;
        if(!opened){const char *path=getenv("TLK_GRAVEYARD_MARKER_TRACE");if(!path)path=getenv("TLK_GRAVEYARD_REVEAL_MARKER_TRACE");opened=1;if(path)trace=fopen(path,"w");
            if(trace)fputs("cell,x,y,native,md\n",trace);}
        if(trace){fprintf(trace,"%u,%u,%u,%u,%u\n",cell,word(0x14),word(0x16),native,external);fflush(trace);}
        return;
    }
    if((pc&65535)==0xb7df){
        if(level!=11 || scene!=0x60f || g_ram[0xe1]!=0xc0 || cpu->D || cpu->DB!=0x7e ||
           cpu->m_flag || cpu->x_flag || cpu->_flag_D || word(0xd0)!=80 || word(0xd4)!=97 ||
           !TlkResourcesUseMd("gameplay.bonus.bug_hunt.placements1"))return;
        unsigned base=word(0xe9)|(unsigned)g_ram[0xeb]<<16,at=(word(0xdc)|(unsigned)g_ram[0xde]<<16)-2;
        if(base!=0x7f0000 || at<base || at-base>=7760 || ((at-base)&1))return;
        unsigned cell=(at-base)/2,native=cpu->A&255,external;
        if(word(0x14)!=(cell%40)*16 || word(0x16)!=(cell/40)*16 ||
           !TlkHuntDataMarker(cell,word(at-0x7e0000),native,&external))return;
        /* The following PLY and AND FF set their original flags. Let the
         * original registration/list-building code own every marker record. */
        cpu->A=(cpu->A&0xff00)|external;
        static FILE *trace;static int initialized;
        if(!initialized){const char *path=getenv("TLK_HUNT_MARKER_TRACE");initialized=1;if(path)trace=fopen(path,"w");
            if(trace)fputs("cell,x,y,native,md\n",trace);}
        if(trace){fprintf(trace,"%u,%u,%u,%u,%u\n",cell,word(0x14),word(0x16),native,external);fflush(trace);}
        return;
    }
    if(level==10 && scene==0x5dd && g_ram[0xe1]==0xc0 && cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D &&
       (pc==0xc53bea || pc==0xc53c5a || pc==0xc542c9 || pc==0xc54301 || pc==0xc54827 || pc==0xc54834)){
        unsigned actor=word(0x68),native,external;
        if(actor<0xb213 || actor>=0xc213 || ((actor-0xb213)&127) || g_ram[actor+6]!=0xc5)return;
        if(TlkResourcesUseMd("gameplay.bonus.bug_toss.arena") && TlkStartDataBonusValue(2,&native,&external) && cpu->A==native){
            /* Replace the completed original LDA. Original comparisons,
             * movement, turn animations and stores retain their ownership. */
            cpu->A=external;cpu->_flag_Z=!external;cpu->_flag_N=!!(external&32768);cpu_mirrors_to_p(cpu);
        }
        return;
    }
    if (!((!level && scene==0x387) || (level==1 && scene==0x3b9) || (level==2 && scene==0x3eb) || (level>=4 && level<=9 && scene==0x387+level*50) || (level==10 && scene==0x5dd) || (level>=11 && level<=13 && scene==0x60f+(level-11)*50)) || g_ram[0xe1]!=0xc0 ||
        cpu->D || cpu->DB!=0x7e || cpu->m_flag) return;
    unsigned at=pc&65535,axis,native,external;
    if (at==0x867d || at==0x8689) {
        if (!cpu->x_flag || word(0x68)!=0xb213 || word(0x1ffa2)) return;
        axis=at==0x8689;
    } else if (at==0x7765) {
        /* This comparison must use the same selected default X. Otherwise
         * the original code would mistake the MD default for a checkpoint. */
        if (cpu->x_flag || level>=10) return;
        axis=0;
    } else return;
    if (cpu->Y!=22+axis*2) return;
    const char *choice=level>=4 && level<=9?later_start_choices[level-4]:level>=11?"gameplay.bonus.bug_hunt.start":level==1?"gameplay.levels.cant_wait.start":level==2?"gameplay.levels.elephant_graveyard.start":level==10?"gameplay.bonus.bug_toss.start":"gameplay.levels.pride_lands.start";
    if(level==2 && at==0x8689 && !word(0xa63) &&
       TlkResourcesUseMd("gameplay.levels.elephant_graveyard.entry_input_delay")) {
        unsigned native_delay,md_delay;
        if(TlkStartDataGraveyardInputDelay(&native_delay,&md_delay)) {
            /* Normal-entry initialization, before the first player update.
             * Native B427 owns decrement/input suppression. No new timer,
             * input tape changes or checkpoint replay policy. */
            put(0xa63,md_delay);
            static FILE *trace;static int opened;
            if(!opened){const char *path=getenv("TLK_GRAVEYARD_ENTRY_DELAY_TRACE");opened=1;if(path)trace=fopen(path,"w");
                if(trace)fputs("native_delay,md_delay,checkpoint,actor\n",trace);}
            if(trace){fprintf(trace,"%u,%u,%u,%04x\n",native_delay,md_delay,word(0x1ffa2),word(0x68));fflush(trace);}
        }
    }
    unsigned original=cpu->A,selected=TlkResourcesUseMd(choice),changed=0;
    if (selected && (level>=4 && level<=9?TlkStartDataLaterValue(level,axis,&native,&external):level>=11?TlkHuntDataEntry(level,axis,&native,&external):level==1?TlkStartDataCantWaitValue(axis,&native,&external):level==2?TlkStartDataGraveyardValue(axis,&native,&external):level==10?TlkStartDataBonusValue(axis,&native,&external):TlkStartDataValue(axis,&native,&external)) && cpu->A==native) {
        cpu->A=(uint16_t)external;changed=1;
        cpu->_flag_N=!!(external&32768);cpu->_flag_Z=!external;cpu_mirrors_to_p(cpu);
    }
    static FILE *trace;static int opened;
    if (!opened) { const char *path=getenv("TLK_START_TRACE");opened=1;if(path)trace=fopen(path,"w");
        if(trace)fprintf(trace,"pc,axis,native,selected,source_md,changed,checkpoint,actor\n"); }
    if(trace) { fprintf(trace,"%06x,%u,%u,%u,%u,%u,%u,%04x\n",pc,axis,original,(unsigned)cpu->A,selected,changed,word(0x1ffa2),word(0x68));fflush(trace); }
}
/* MD19F3A2/19F5C0 keep a log set only while a generator has been visible
 * within one guest actor update. Native A69A/A69C are a gate/live count and
 * do not express that gap. Actor-local extension words +70/+72 are unused by
 * these two native descriptors. They follow the ordinary actor lifetime and
 * native saves; constructors clear/reinitialize them on pool reuse.
 * No host frame, pad read, movie position, actor coordinate or RNG is used. */
static void hakuna_log_pre(CpuState *cpu,uint32_t pc){
    if(word(0x1ff9e)!=5 || word(0xdf)!=0x481 || g_ram[0xe1]!=0xc0 ||
       !TlkResourcesUseMd("gameplay.levels.hakuna_matata.log_continuity") ||
       cpu->PB!=0xc4 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x68),clock=word(0xf930);
    if(actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127))return;
    unsigned desc=word(actor+4)|(unsigned)g_ram[actor+6]<<16;
    unsigned before=cpu->A,event=0;
    if(desc==0xc58ad7 && (pc==0xc48c5c || pc==0xc48c7a)){
        if(word(0xa68c)!=cpu->D+0x22)return;
        if(pc==0xc48c5c){
            if(!word(actor+48) && !g_ram[actor+50])put(actor+114,0);
            return;
        }
        /* The original visibility helper just returned zero. */
        if(cpu->A)return;
        put(actor+112,clock);put(actor+114,0x474c);event=1;
    }else if(desc==0xc58aec && (pc==0xc48e26 || pc==0xc48f89)){
        if(word(0xa68c)!=cpu->D+0x2e)return;
        if(pc==0xc48e26){
            if(cpu->A){put(actor+112,clock);put(actor+114,0x504c);}
            return;
        }
        if(word(actor+114)!=0x504c || cpu->A!=word(0xa69a))return;
        unsigned last=word(actor+112),age=(clock-last)&65535;
        unsigned cursor=word(0x76);
        for(unsigned n=0;n<84 && cursor>=0xb213 && cursor<0xdc13 && !((cursor-0xb213)&127);n++){
            if(word(cursor+4)==0x8ad7 && g_ram[cursor+6]==0xc5 && word(cursor+114)==0x474c){
                unsigned candidate=word(cursor+112),elapsed=(clock-candidate)&65535;
                if(elapsed<age){age=elapsed;last=candidate;}
            }
            cursor=word(cursor+2);
        }
        put(actor+112,last);
        /* Original BNE -> DEC live count -> C0AC84 owns removal. A live log
         * continues through the original motion/draw calls. MD's threshold1
         * is the immediate in19F5CC, verified against the known cartridge. */
        cpu->A=age>1;
        cpu->_flag_N=0;cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);event=cpu->A?3:2;
    }else return;
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_HAKUNA_LOG_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,event,clock,last,native,selected,count\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,event,clock,word(actor+112),before,cpu->A,word(0xa69c));fflush(trace);}
}
/* MD uses a wider right boundary and an inclusive bottom boundary.
 * Retain the original offscreen branches, cleanup and loss callbacks. */
static void exile_cull_after(CpuState *cpu,uint32_t pc){
    if(pc!=0xc0bb24 || word(0x1ff9e)!=4 || word(0xdf)!=0x44f || g_ram[0xe1]!=0xc0 ||
       !TlkResourcesUseMd("gameplay.levels.simbas_exile.culling_bounds") || cpu->PB!=0xc0 ||
       cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x68),bottom=word(0xb201);
    if(actor<0xb313 || actor>=0xdc13 || ((actor-0xb213)&127) || g_ram[actor+6]!=0xc5 ||
       (g_ram[actor+67]&2) || cpu->Y!=10 || cpu->A!=((word(actor+10)+1)&65535) || bottom>=32766)return;
    /* MD0928D4/BGT removes a point actor only at Y>bottom. Native C0BB20
     * increments Y before CMP/BPL, so compare that existing accumulator
     * with bottom+2. No bound, position, lifetime or queue store is forced.
     * Rectangle-culling actors use a different path and remain untouched. */
    unsigned md=bottom+2,difference=(cpu->A-md)&65535;
    cpu->_flag_C=cpu->A>=md;cpu->_flag_Z=!difference;cpu->_flag_N=!!(difference&32768);cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_EXILE_CULL_TRACE");if(path){trace=fopen(path,"w");if(trace)fputs("field,actor,x,y,bottom,selected_threshold\n",trace);}}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,actor,word(actor+8),word(actor+10),bottom,md);fflush(trace);}
}
static void toss_cull_after(CpuState *cpu,uint32_t pc){
    exile_cull_after(cpu,pc);
    if((pc!=0xc0bb32 && pc!=0xc0bb24) || word(0x1ff9e)!=10 || word(0xdf)!=0x5dd || g_ram[0xe1]!=0xc0 ||
       !TlkResourcesUseMd("gameplay.bonus.bug_toss.culling_bounds") || cpu->PB!=0xc0 ||
       cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x68),native,md;
    if(actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127) || g_ram[actor+6]!=0xc5 ||
       !TlkStartDataBonusValue(2,&native,&md))return;
    if(pc==0xc0bb32){
        if(cpu->Y!=8 || cpu->A!=word(actor+8) || word(0xb205)!=native+31)return;
        native+=31;md+=31;
    }else{
        if(cpu->Y!=10 || cpu->A!=((word(actor+10)+1)&65535) || word(0xb201)!=223)return;
        /* Native INC Y/CMP bottom/BPL removes Y>=bottom-1. MD compares
         * the unincremented Y and removes only Y>bottom. Comparing the
         * existing incremented accumulator against bottom+2 gives that
         * inclusive MD decision through the original BPL, without stores. */
        native=word(0xb201);md=native+2;
    }
    unsigned difference=(cpu->A-md)&65535;
    /* Replace CMP flags after its original read; original BEQ/BMI, object
     * teardown and loss callback still own the decision. No guest stores. */
    cpu->_flag_C=cpu->A>=md;cpu->_flag_Z=!difference;cpu->_flag_N=!!(difference&32768);cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *path=getenv("TLK_TOSS_CULL_TRACE");opened=1;if(path)trace=fopen(path,"w");
        if(trace)fputs("field,actor,x,native,md\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u\n",snes_frame_counter+1,actor,cpu->A,native,md);fflush(trace);}
}

static void stampede_exit_after(CpuState *cpu){
    const uint32_t *rules=TlkNextSceneStampedeRules();
    if(!rules || !TlkResourcesUseMd("gameplay.levels.stampede.exit_flow") ||
       word(0x1ff9e)!=3 || word(0xdf)!=0x41d || g_ram[0xe1]!=0xc0 ||
       !word(0xa692) || word(0xa692)>=32768 || !word(0x2004) ||
       cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag ||
       cpu->_flag_D || cpu->Y!=46 || cpu->A!=rules[18])return;
    /* The original coordinator just loaded its next-level descriptor word.
     * Supply the prepared MD canonical destination, then its original STA,
     * bonus eligibility, fade, scene cleanup and normal loader retain control. */
    cpu->A=(uint16_t)rules[19];cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *path=getenv("TLK_STAMPEDE_EXIT_TRACE");opened=1;if(path)trace=fopen(path,"w");
        if(trace)fputs("field,native,md,health\n",trace);}
    if(trace){fprintf(trace,"%u,%u,%u,%u\n",snes_frame_counter+1,rules[18],rules[19],word(0x2004));fflush(trace);}
}
static void stampede_exit_pre(CpuState *cpu,uint32_t pc){if(pc==0xc0894e)stampede_exit_after(cpu);}
/* Original MD001A70 signed BLE retains nonpositive shake at its inherited
 * post-bonus camera limit. Keep the native branch and STZ as the sole writer. */
static void stampede_shake_pre(CpuState *cpu,uint32_t pc){
    const uint32_t *rules=TlkNextSceneStampedeRules();
    if(pc!=0xc088ca || !rules || word(0x1ff9e)!=3 || word(0xdf)!=0x41d || g_ram[0xe1]!=0xc0 ||
       word(0x1ffa0)!=3 || word(0xda)!=rules[20] || word(0x4c) ||
       cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       !TlkResourcesUseMd("gameplay.levels.stampede.camera_shake"))return;
    cpu->_flag_C=(int16_t)cpu->A>(int32_t)rules[21];cpu_mirrors_to_p(cpu);
}
/* The common 1UP has a different original availability rule: SNES hides
 * at eight lives, MD only at nine. Keep its normal lifetime/contact/reward
 * handlers; selecting this rule does not alter other reward sources. */
static void life_pickup_pre(CpuState *cpu,uint32_t pc) {
    if(pc==0xc001d7){
        /* The ordinary HUD updater also clamps the stored counter to eight.
         * Admit the selected 1UP's ninth life on later HUD updates too. */
        if(cpu->DB!=0x7e || cpu->m_flag || cpu->_flag_D || cpu->A!=9 ||
           word(0x1ffaa)!=9 || !TlkResourcesUseMd("gameplay.life_pickup_limit"))return;
        cpu->_flag_C=0;cpu->_flag_Z=0;cpu->_flag_N=1;cpu_mirrors_to_p(cpu);return;
    }

    if(pc==0xc075d7 || pc==0xc075dc){
        if(cpu->DB!=0x7e || cpu->m_flag || cpu->_flag_D ||
           !TlkResourcesUseMd("gameplay.life_pickup_limit"))return;
        /* All normal life awards share this clamp. A later award must not
         * reduce an already earned ninth life back to the native eight. */
        if(pc==0xc075d7){unsigned result=(cpu->A-10)&65535;
            cpu->_flag_C=cpu->A>=10;cpu->_flag_Z=!result;cpu->_flag_N=!!(result&32768);
        }else if(cpu->A==8 && word(0x1ffaa)>=8){cpu->A=9;cpu->_flag_Z=0;cpu->_flag_N=0;}
        cpu_mirrors_to_p(cpu);return;
    }
    if(cpu->D<0x600 || cpu->D>0x1f00 || cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->DB!=0x7e ||
       word(0x1ff9e)>9 || !TlkResourcesUseMd("gameplay.life_pickup_limit"))return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       (word(actor+4)|g_ram[actor+6]<<16)!=0xc58981 ||
       (word(actor+48)|g_ram[actor+50]<<16)!=0xc5567e)return;
    if(pc==0xc556da){
        if(cpu->A!=word(0x1ffaa))return;
        /* Native BMI now expresses MD's BNE: retain the pickup unless
         * lives equals nine. No guest life count or actor is spoofed. */
        cpu->_flag_N=cpu->A!=9;cpu->_flag_Z=cpu->A==9;cpu->_flag_C=cpu->A>=9;
    }else if(pc==0xc556ea){
        if(cpu->Y!=8 || word(0x1ffaa)!=9)return;
        unsigned input=(cpu->A-400)&65535,sum=input+4000;
        cpu->A=sum&65535;cpu->_flag_C=sum>65535;
        cpu->_flag_V=!!((~(input^4000)&(input^cpu->A))&32768);
        cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;
    }else return;
    cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_LIFE_PICKUP_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,lives,a,negative,carry\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,pc,actor,word(0x1ffaa),cpu->A,cpu->_flag_N,cpu->_flag_C);fflush(trace);}
}
#include "tlk_toss_reward_eligibility.inc"
#include "tlk_ending_rain.inc"
static void start_after(CpuState *cpu,uint32_t pc) {
    if(pc==0xc67fba){ending_rain_pre(cpu,pc+2);return;}
    if(pc==0xc68167){ending_rain_pre(cpu,pc+3);return;}
    if(pc==0xc087b3 || pc==0xc087bd || pc==0xc0881b || pc==0xc08825){default_revival_compare(cpu,pc+2);return;}
    if(pc==0xc5498d || pc==0xc549a9){toss_reward_eligibility_pre(cpu,pc);return;}
    if(pc==0xc001d4 || pc==0xc556d7 || pc==0xc556e7 || pc==0xc075d4 || pc==0xc075d9){life_pickup_pre(cpu,pc+3);return;}
    if(pc==0xc088c7){stampede_shake_pre(cpu,pc+3);return;}
    if(pc==0xc0894c){stampede_exit_after(cpu);return;}
    if(pc==0xc0bb2f || pc==0xc0bb21){toss_cull_after(cpu,pc+3);return;}
    if(pc==0xc48c5a || pc==0xc48c77 || pc==0xc48e24 || pc==0xc48f86){hakuna_log_pre(cpu,pc+((pc==0xc48c77 || pc==0xc48f86)?3:2));return;}
    start_pre(cpu,pc+(pc==0xc0891d?4:pc==0xc0856b?3:(pc==0xc58168 || pc==0xc58170 || pc==0xc581c8 || pc==0xc196d2 || pc==0xc196ef)?3:2)); }
void TlkLayoutBonusPreOpcode(CpuState *cpu,uint32_t pc){start_pre(cpu,pc);}
void TlkLayoutRetryPreOpcode(CpuState *cpu,uint32_t pc){retry_pre(cpu,pc);}
static void pre(CpuState *cpu,uint32_t pc) {
    (void)pc;
    unsigned level=word(0x1ff9e),scene=word(0xdf);
    if(cpu->A==40 && TlkResourcesUseMd("gameplay.continue_token_positions") &&
       level<=9 && level!=3 && g_ram[0xe1]==0xc0 &&
       (scene==0x387+level*50 || (!level && scene==0x80d)) &&
       !cpu->D && cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D) {
        int x=word(0x14),y=word(0x16),mx,my;
        /* Select the authored home at the original spawn ABI. The original
         * stack restores scratch coordinates; no live actor is relocated. */
        if(word((cpu->S+1)&65535)==(unsigned)y && word((cpu->S+3)&65535)==(unsigned)x &&
           TlkMdSceneMarkerMove(level,40,x,y,&mx,&my)) {
            put(0x14,mx);put(0x16,my);
            static FILE *trace;static int checked;
            if(!checked){checked=1;const char *p=getenv("TLK_CONTINUE_HOME_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,level,marker,native_x,native_y,md_x,md_y\n",trace);}}
            if(trace){fprintf(trace,"%u,%u,40,%d,%d,%d,%d\n",snes_frame_counter+1,level,x,y,mx,my);fflush(trace);}
        }
        return;
    }
    if (!TlkResourcesUseMd("gameplay.levels.pride_lands.pickups") || word(0x1ff9e) ||
        (word(0xdf)!=0x387 && word(0xdf)!=0x80d) || cpu->D || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag) return;
    /* Reviewed semantic IDs: spotted ground bug and bonus bug. Their frame
     * pointers agree in both original spawn tables; other IDs stay native. */
    unsigned marker=cpu->A;
    if (marker!=0x12 && marker!=0x29) return;
    int x=word(0x14),y=word(0x16),mx,my;
    if (!TlkMdSceneMarkerMove(0,marker,x,y,&mx,&my)) return;
    /* Original PHX pairs already saved these coordinates. Its own epilogue
     * restores them, including across interpreter yields and saved states. */
    if (word((cpu->S+1)&65535)!=(unsigned)y || word((cpu->S+3)&65535)!=(unsigned)x) return;
    put(0x14,mx);put(0x16,my);
    static FILE *trace;
    const char *path=getenv("TLK_LAYOUT_TRACE");
    if (path && !trace) { trace=fopen(path,"w");if(trace) fprintf(trace,"marker,native_x,native_y,md_x,md_y\n"); }
    if (trace) { fprintf(trace,"%u,%d,%d,%d,%d\n",marker,x,y,mx,my);fflush(trace); }
}
void (*g_tlk_adult_turn_pc_hook)(CpuState *,uint32_t);
static void adult_turn_pre(CpuState *cpu,uint32_t pc){
    unsigned level=word(0x1ff9e),actor=word(0x68),native,external;
    if(pc!=0xc0aebd || level<6 || level>9 || word(0xdf)!=0x4b3+(level-6)*50 || g_ram[0xe1]!=0xc0 ||
       word(0x2000)!=0xffff || cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       actor!=0xb213 || word(actor+4)!=0x858a || g_ram[actor+6]!=0xc5 ||
       (word(actor+48)!=0x20c8 && word(actor+48)!=0x1e57) || g_ram[actor+50]!=0xc3 ||
       (word(actor+14)!=0xe5a6 && word(actor+14)!=0xe604) || g_ram[actor+16]!=0xc0 ||
       word(0x14)!=0xf7de || g_ram[0x16]!=0xc0 || cpu->Y!=1 ||
       !TlkResourcesUseMd("gameplay.simba.adult_turn_motion") || !TlkNextSceneAdultTurn(&native,&external) || cpu->A!=native)return;
    cpu->A=(uint16_t)external;cpu->_flag_N=!!(external&32768);cpu->_flag_Z=!external;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_ADULT_TURN_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,level,actor,cursor,native,md,x,y\n",trace);}
    if(trace){fprintf(trace,"%u,%u,%04x,c0f7de,%u,%u,%u,%u\n",snes_frame_counter+1,level,actor,native,external,word(actor+8),word(actor+10));fflush(trace);}
}
static void adult_turn_after(CpuState *cpu,uint32_t pc){adult_turn_pre(cpu,pc+2);}
void (*g_tlk_destiny_arena_pc_hook)(CpuState *,uint32_t);
static void destiny_arena_pre(CpuState *cpu,uint32_t pc){
    if(pc!=0xc00f85 || word(0x1ff9e)!=6 || word(0xdf)!=0x4b3 || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>0x1f00 || word(0xa68c)!=cpu->D+0x2c || word(0x6e)!=0xb213 ||
       !TlkResourcesUseMd("gameplay.levels.simbas_destiny.arena_barrier"))return;
    unsigned actor=word(0x68),native,external;
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || word(actor+4)!=0x86f0 || g_ram[actor+6]!=0xc5 ||
       word(actor+48)!=0x0fdd || g_ram[actor+50]!=0xc0 || word(cpu->D+0x26)!=word(actor+8) ||
       !TlkNextSceneDestinyArenaRadius(&native,&external) || cpu->A!=((word(actor+8)+native)&65535))return;
    unsigned input=(cpu->A-native)&65535,sum=input+external,result=sum&65535;
    cpu->A=(uint16_t)result;cpu->_flag_C=sum>65535;cpu->_flag_V=!!((~(input^external)&(input^result))&32768);
    cpu->_flag_N=!!(result&32768);cpu->_flag_Z=!result;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_DESTINY_ARENA_BARRIER_TRACE");opened=1;if(p)trace=fopen(p,"w");
        if(trace)fputs("field,actor,native,md,x,right,player_x,player_y\n",trace);}
    if(trace){fprintf(trace,"%u,%04x,%u,%u,%u,%u,%u,%u\n",snes_frame_counter+1,actor,native,external,input,result,word(0xb21b),word(0xb21d));fflush(trace);}
}
static void destiny_arena_after(CpuState *cpu,uint32_t pc){destiny_arena_pre(cpu,pc+3);}
static void bonus_selection_pre(CpuState *cpu,uint32_t pc){
    unsigned next=word(0x1ff9e),selected;
    if(pc!=0xc08963 || cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->_flag_D ||
       word(0x1ffa0)!=next || word(0x2430)!=0xffff || cpu->A!=next ||
       !TlkResourcesUseMd("gameplay.bonus.round_selection") || !TlkNextSceneBonusSelection(next,&selected))return;
    /* Replace SNES's random layout decision with MD's prepared stage table.
     * Native CLC/ADC10/STA and the normal bonus loader retain ownership. */
    cpu->A=selected-10;cpu->_flag_Z=0;cpu->_flag_N=0;cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_BONUS_SELECTION_TRACE");if(p){trace=fopen(p,"w");if(trace)fputs("field,next_main,selected\n",trace);}}
    if(trace){fprintf(trace,"%u,%u,%u\n",snes_frame_counter+1,next,selected);fflush(trace);}
    interp_bridge_pre_opcode_redirect(0xc0896c);
}
void TlkLayoutInstall(void) {
    interp_bridge_add_pre_opcode_hook(0xc5498d,toss_reward_eligibility_pre);
    interp_bridge_add_pre_opcode_hook(0xc549a9,toss_reward_eligibility_pre);
    static const unsigned life_points[]={0xc001d7,0xc556da,0xc556ea,0xc075d7,0xc075dc};
    for(unsigned i=0;i<sizeof life_points/sizeof *life_points;i++)interp_bridge_add_pre_opcode_hook(life_points[i],life_pickup_pre);
    TlkBePreparedBehaviorInstall();
    TlkBePreparedGameplayInstall();
    TlkScarActivationInstall();
    TlkReturnExitInstall();
    TlkReturnDoorInstall();
    TlkReturnHyenasInstall();
    TlkAdultHyenaInstall();
    TlkScarContactInstall();
    TlkAdultLedgeInstall();
    interp_bridge_add_pre_opcode_hook(0xc08963,bonus_selection_pre);
    g_tlk_destiny_exit_pc_hook=destiny_exit_start_after;
    interp_bridge_add_pre_opcode_hook(0xc1aacd,destiny_exit_start_pre);
    TlkDestinyMonkeyInstall();
    g_tlk_destiny_arena_pc_hook=destiny_arena_after;
    interp_bridge_add_pre_opcode_hook(0xc00f85,destiny_arena_pre);
    g_tlk_adult_turn_pc_hook=adult_turn_after;
    interp_bridge_add_pre_opcode_hook(0xc0aebd,adult_turn_pre);
    static const unsigned log_continuity[]={0xc48c5c,0xc48c7a,0xc48e26,0xc48f89};
    for(unsigned i=0;i<sizeof log_continuity/sizeof *log_continuity;i++)interp_bridge_add_pre_opcode_hook(log_continuity[i],hakuna_log_pre);
    interp_bridge_add_pre_opcode_hook(0xc08921,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc08560,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc0856e,start_pre);
    interp_bridge_add_pre_opcode_hook(0x008560,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc0cc55,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc0cc5b,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc08859,retry_pre);
    interp_bridge_add_pre_opcode_hook(0xc1a630,exile_exit_start_pre);
    interp_bridge_add_pre_opcode_hook(0xc0c627,exile_wall_pre);
    interp_bridge_add_pre_opcode_hook(0xc0c711,exile_wall_pre);
    g_tlk_exile_grip_pc_hook=exile_grip_after;
    static const unsigned exile_grips[]={0xc0c877,0xc0c895,0xc0c89c};
    for(unsigned i=0;i<sizeof exile_grips/sizeof *exile_grips;i++)interp_bridge_add_pre_opcode_hook(exile_grips[i],exile_grip_pre);
    g_tlk_stampede_pc_hook=stampede_after;
    static const unsigned stampede[]={0xc45aff,0xc45b46,0xc45ec8,0xc45fc7,0xc0bbf3,0xc4627f,0xc1a3af,0xc1a3bc,0xc28e40,0xc0e1a2};
    for(unsigned i=0;i<sizeof stampede/sizeof *stampede;i++)interp_bridge_add_pre_opcode_hook(stampede[i],stampede_pre);
    static const unsigned stampede_boxes[]={0xc0cf12,0xc0cf22,0xc0cf31,0xc0cf3e,0xc0cf9d,0xc0cfad,0xc0cfbc,0xc0cfc9};
    for(unsigned i=0;i<sizeof stampede_boxes/sizeof *stampede_boxes;i++)interp_bridge_add_pre_opcode_hook(stampede_boxes[i],stampede_pre);
    g_tlk_layout_pc_hook=start_after;
    interp_bridge_add_pre_opcode_hook(0xc67fbc,ending_rain_pre);
    interp_bridge_add_pre_opcode_hook(0xc6816a,ending_rain_pre);
    static const unsigned revival_compares[]={0xc087b5,0xc087bf,0xc0881d,0xc08827};
    for(unsigned i=0;i<sizeof revival_compares/sizeof *revival_compares;i++)
        interp_bridge_add_pre_opcode_hook(revival_compares[i],default_revival_compare);
    interp_bridge_add_pre_opcode_hook(0xc088ca,stampede_shake_pre);
    interp_bridge_add_pre_opcode_hook(0xc0894e,stampede_exit_pre);
    interp_bridge_add_pre_opcode_hook(0xc0bb32,toss_cull_after);
    interp_bridge_add_pre_opcode_hook(0xc0bb24,toss_cull_after);
    g_tlk_gy_bone_pc_hook=bone_contact_after;
    static const unsigned contacts[]={0xc0d879,0xc0d887,0xc0d897,0xc0d8a1,0xc0d8b2,0xc0d8b5,0xc0d8ef};
    for(unsigned i=0;i<sizeof contacts/sizeof *contacts;i++)interp_bridge_add_pre_opcode_hook(contacts[i],bone_contact_pre);
    g_tlk_gy_input_pc_hook=input_after;
    interp_bridge_add_pre_opcode_hook(0xc32857,input_pre);
    interp_bridge_add_pre_opcode_hook(0xc32fe6,input_pre);
    g_tlk_gy_handoff_pc_hook=handoff_after;
    interp_bridge_add_pre_opcode_hook(0xc33176,handoff_pre);
    interp_bridge_add_pre_opcode_hook(0xc33179,handoff_pre);
    interp_bridge_add_pre_opcode_hook(0xc196d5,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc196f2,start_pre);
    static const unsigned positions[]={0x867d,0x8689,0x7765,0xb7df};
    for(unsigned i=0;i<sizeof positions/sizeof positions[0];i++) {
        interp_bridge_add_pre_opcode_hook(0xc00000|positions[i],start_pre);
        interp_bridge_add_pre_opcode_hook(positions[i],start_pre);
    }
    interp_bridge_add_pre_opcode_hook(0xc0b819,pre);
    interp_bridge_add_pre_opcode_hook(0x00b819,pre);
    static const unsigned bonus[]={0xc53bea,0xc53c5a,0xc542c9,0xc54301,0xc54827,0xc54834};
    for(unsigned i=0;i<sizeof bonus/sizeof bonus[0];i++)interp_bridge_add_pre_opcode_hook(bonus[i],start_pre);
    static const unsigned hunt_timer[]={0xc58124,0xc5816b,0xc58173,0xc581cb};
    for(unsigned i=0;i<sizeof hunt_timer/sizeof hunt_timer[0];i++)interp_bridge_add_pre_opcode_hook(hunt_timer[i],start_pre);
    interp_bridge_add_pre_opcode_hook(0xc58456,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc5830a,start_pre);
    interp_bridge_add_pre_opcode_hook(0xc58327,start_pre);
}

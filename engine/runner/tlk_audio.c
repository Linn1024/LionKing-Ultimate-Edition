#include "tlk_fallback_log.h"
#include "tlk_audio.h"
#include "tlk_destiny_monkey_data.h"
#include "tlk_be_prepared_data.h"
#include "tlk_interlevel_scene.h"
#include "tlk_interlevel_data.h"
#include "tlk_bonus_result_scene.h"
#include "tlk_graveyard_hyena_owner.h"
#include "tlk_native_audio_owner.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include "tlk_resources.h"
#include "tlk_md_sound.h"
#include "tlk_hyena_audio.h"
#include "tlk_battle_music_policy.h"
#include "tlk_porcupine_voice_policy.h"
#include "tlk_lizard_audio.h"
#include "tlk_pickup_audio.h"
#include "tlk_ledge_audio.h"
#include "tlk_defeat_audio_scene.h"
#include "tlk_health_death_audio_context.h"
#include "tlk_state_bytes.h"
#include "tlk_continue_token_role.h"
#include "tlk_cw_audio_metadata.h"
#include "tlk_graveyard_audio_metadata.h"
#include "sha256.h"
#include "tlk_final_art.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef TLK_FINAL_MENU_ART_AVAILABLE
#define TLK_FINAL_MENU_ART_AVAILABLE 0
#endif

void (*g_tlk_audio_pc_hook)(CpuState *cpu, uint32_t pc);
/* Defined in every host's audio module; final-player gameplay installs it. */
void (*g_tlk_graveyard_gameplay_pc_hook)(CpuState *cpu,uint32_t pc);
static FILE *trace;
static unsigned frame;
static FILE *stems;
static int music_active,music_choice,pending_stop,fx_tail,menu_fx,cant_wait_fx,graveyard_fx,hunt_fx,prepared_fx,prepared_choice;
static unsigned music_track;
static unsigned exile_exit_age,exile_exit_phase,exile_exit_delay;
static int exile_exit_fx;
static int exile_exit_choice;
static int music_entry_seen;
static unsigned music_scene;
static const TlkFinalArt *sound_test_art;
void TlkAudioSetSoundTestAssets(const TlkFinalArt *art){sound_test_art=art;}
static unsigned battle_ready;
/* 0: normal scene, 1: native death fade before Music Off, 2: health-death
 * hold, 3: other death holds on the native event path.
 * This is audio continuation only; the original game owns death/revival. */
static unsigned death_phase;
static const char *music_sources[]={
    "audio.music.pride_lands", "audio.music.cant_wait_to_be_king",
    "audio.music.elephant_graveyard.track", "audio.music.stampede",
    "audio.music.simbas_exile.track", "audio.music.hakuna_matata.track",
    "audio.music.simbas_destiny.track", "audio.music.be_prepared.track",
    "audio.music.simbas_return.track", "audio.music.pride_rock.track"
};
enum { MUSIC_COUNT=sizeof music_sources/sizeof music_sources[0] };
/* Semantic first-level cues. Actor scope: 1 Simba, 2 other actors, 3 Sun owner. */
static const struct { const char *id;unsigned native_event,selector,value,actor,caller; } cues[]={
    {"audio.effects.simba.roar",5,19,10,1,0},
    {"audio.effects.simba.hurt",0x12,19,1,1,0},
#if TLK_LIZARD_VOICE_TIMING_AVAILABLE
    /* MD plays at counter32; replace only the later native attack cue. */
    {"audio.effects.world.lizard",0x14,0,0,2,0xc16527},
#else
    {"audio.effects.world.lizard",0x14,2,124,2,0},
#endif
    {"audio.effects.world.one_up",0x13,19,15,2,0xc55714},
    {"audio.effects.world.bonus_bug",0x13,19,15,2,0xc559b8},
    {"audio.effects.world.bonus_bug",0x13,19,15,2,0xc55a02},
    {"audio.effects.world.continue_token",0x13,19,15,3,0xc55970},
    {"audio.effects.world.checkpoint",0x13,2,101,2,0xc55785},
    {"audio.effects.world.checkpoint",0x13,2,101,2,0xc55872},
    {"audio.effects.world.health_bug",0x13,2,97,2,0xc55087},
    {"audio.effects.world.full_health_bug",0x13,2,98,2,0xc550d5},
    {"audio.effects.world.life_bug",0x13,2,112,2,0xc5514d},
    {"audio.effects.world.life_bug",0x13,2,112,2,0xc55232},
    {"audio.effects.world.roar_bug",0x13,2,116,2,0xc551a9},
    {"audio.effects.world.harmful_bug",0x12,2,117,2,0xc54fe2},
    {"audio.effects.world.harmful_bug",0x12,2,117,2,0xc55040},
    {"audio.effects.simba.bounce",0x11,2,123,1,0xc36686},
#if TLK_PORCUPINE_VOICE_TIMING_AVAILABLE
    /* MD cue belongs to counter28, independently of native contact timing. */
    {"audio.effects.world.porcupine",0x15,0,0,2,0xc15cb0},
#else
    {"audio.effects.world.porcupine",0x15,2,105,2,0xc15cb0},
#endif
#if TLK_HYENA_VOICE_ENTRY_AVAILABLE
    /* Original MD19B6D6 emits once on entry, not at the native tag2 cues. */
    {"audio.effects.world.hyena_hurt",0x20,0,0,2,0xc1458d},
#else
    {"audio.effects.world.hyena_hurt",0x20,19,4,2,0xc1458d},
#endif
    /* MD emits once at the parent trigger; suppress each native child cue. */
    {"audio.effects.world.leaves",0x17,0,0,2,0xc1fe7d},
    /* Original MD 196406/196566 omit the native rolling cue. Contact
     * sounds belong to the contacted actor and remain independent. */
    {"audio.effects.simba.roll",0x0a,0,0,1,0xc355c2},
    {"audio.effects.simba.roll",0x0a,0,0,1,0xc35769},
    {"audio.effects.world.hyena_pant",0x1f,19,7,2,0xc146cc},
    /* MD 19BA8C transitions to 19BB52 without a separate jump voice. */
    {"audio.effects.world.hyena_jump",0x1e,0,0,2,0xc1496e},
    /* MD plays PCM3 on action entry; its animation omits native event2. */
    {"audio.effects.world.hyena_taunt",0x1e,0,0,2,0xc14262},
};
enum { CUE_COUNT=sizeof cues/sizeof cues[0] };
static int cue_choices[CUE_COUNT];
enum { CW_RHINO, CW_CONTACT, CW_REACTION, CW_STEPS, CW_JUMP, CW_TAKEOFF, CW_LIFE, CW_BONUS, CW_SOUND_COUNT };
static const char *cw_sources[CW_SOUND_COUNT]={
    "audio.effects.world.cant_wait.rhino",
    "audio.effects.world.cant_wait.monkey_contacts",
    "audio.effects.world.cant_wait.monkey_reaction",
    "audio.effects.world.cant_wait.ostrich_steps",
    "audio.effects.world.cant_wait.ostrich_jump",
    "audio.effects.world.cant_wait.flying_takeoff",
    "audio.effects.world.cant_wait.extra_life",
    "audio.effects.world.cant_wait.bonus"
};
static int cw_choices[CW_SOUND_COUNT];
enum { GY_VULTURE, GY_SHAKE, GY_PLATFORM, GY_BREAK, GY_PILLAR, GY_SOUND_COUNT };
static const char *gy_sources[GY_SOUND_COUNT]={
    "audio.effects.world.graveyard.vulture",
    "audio.effects.world.graveyard.bone_shake",
    "audio.effects.world.graveyard.bone_platform",
    "audio.effects.world.graveyard.bone_break",
    "audio.effects.world.graveyard.pillar"
};
static int gy_choices[GY_SOUND_COUNT];
enum { HUNT_COLLECT,HUNT_HURT,TOSS_COLLECT,TOSS_CHEW,TOSS_REWARDS,HUNT_SOUND_COUNT };
static const char *hunt_sources[HUNT_SOUND_COUNT]={
    "audio.effects.bonus.hunt_collect","audio.effects.bonus.hunt_hurt","audio.effects.bonus.toss_collect","audio.effects.bonus.toss_chew","audio.effects.bonus.toss_rewards"
};
static int hunt_choices[HUNT_SOUND_COUNT];
static const char *monkey_sources[]={"audio.effects.world.simbas_destiny.monkey_movement","audio.effects.world.simbas_destiny.monkey_shot","audio.effects.world.simbas_destiny.monkey_defeat"};
static int monkey_choices[3];
static int adult_roar_choice;
static int gorilla_defeat_choice;
static int gorilla_jump_choice;
static int gorilla_attack_choice;
static int gorilla_grab_choice;
static int coconut_bounce_choice,coconut_break_choice;
static int scar_attack_choice;
static int pride_fire_choice;
static int prepared_rock_choice;
static int arena_gate_choice;
static int adult_taunt_choice;
static const char *victory_voice_sources[]={"audio.effects.simba.scar_finish_roar","audio.effects.simba.postfight_roars"};
static int victory_voice_choices[2];

/* Pending reactions are a derived view of live guest actors and their native
 * countdown. Reconstruct them after a current save load; do not serialize
 * a second timer or maintain an independent wall-clock delay. */
static struct {unsigned actor,descriptor,draw;} cw_reactions[32];
static unsigned cw_reaction_count;
/* Title and Options calls share event numbers with gameplay sounds. Match
 * their original caller and scene, never just event05/event06. */
static const struct { const char *id; unsigned event,caller,value; } menu_cues[]={
    {"audio.effects.title_cursor",5,0xc46849,100},
    {"audio.effects.title_cursor",5,0xc468a2,100},
    {"audio.effects.title_selection",6,0xc467cf,101},
    {"audio.effects.title_selection",6,0xc46804,101},
    {"audio.effects.options_adjustment",6,0xc46a56,101},
    {"audio.effects.options_cursor",5,0xc46ace,100},
    {"audio.effects.options_cursor",5,0xc46b25,100},
    {"audio.effects.options_exit",5,0xc469db,0},
    {"audio.effects.level_select",5,0xc46fba,100},
    {"audio.effects.level_select",5,0xc47011,100},
    {"audio.effects.level_select",6,0xc46f42,0},
    {"audio.effects.level_select",5,0xc46f12,0},
};
enum { MENU_CUE_COUNT=sizeof menu_cues/sizeof menu_cues[0] };
static int menu_cue_choices[MENU_CUE_COUNT];
/* These original MD cues have no native audio event to replace. */
static const char *trigger_sources[]={"audio.effects.world.defeat_puff","audio.effects.world.pickup_arrival","audio.effects.simba.ledge_grab","audio.effects.world.lizard_launch"};
enum { TRIGGER_COUNT=sizeof trigger_sources/sizeof trigger_sources[0] };
static int trigger_choices[TRIGGER_COUNT];
static unsigned word(unsigned at) { return g_ram[at] | (unsigned)g_ram[at+1]<<8; }
static int pride(void) { return word(0x1ff9e)==0 && (word(0xdf)==0x387 || word(0xdf)==0x80d); }
static int cant_wait(void) { return word(0x1ff9e)==1 && word(0xdf)==0x3b9 && g_ram[0xe1]==0xc0; }
int TlkAudioGraveyardScene(void) {return word(0x1ff9e)==2 && word(0xdf)==0x3eb && g_ram[0xe1]==0xc0;}
static int exile(void) {return word(0x1ff9e)==4 && word(0xdf)==0x44f && g_ram[0xe1]==0xc0;}
static int stampede(void) {return word(0x1ff9e)==3 && word(0xdf)==0x41d && g_ram[0xe1]==0xc0;}
static int hakuna(void) {return word(0x1ff9e)==5 && word(0xdf)==0x481 && g_ram[0xe1]==0xc0;}
static int destiny(void) {return word(0x1ff9e)==6 && word(0xdf)==0x4b3 && g_ram[0xe1]==0xc0;}
static int be_prepared(void) {return word(0x1ff9e)==7 && word(0xdf)==0x4e5 && g_ram[0xe1]==0xc0;}
static int simbas_return(void) {return word(0x1ff9e)==8 && word(0xdf)==0x517 && g_ram[0xe1]==0xc0;}
static int pride_rock(void) {return word(0x1ff9e)==9 && word(0xdf)==0x549 && g_ram[0xe1]==0xc0;}
static int bonus_scene(void) {
    unsigned level=word(0x1ff9e);
    return level>=10 && level<=13 && word(0xdf)==0x5dd+(level-10)*0x32 && g_ram[0xe1]==0xc0;
}
static int hunt_scene(void) {return bonus_scene() && word(0x1ff9e)>=11;}
static unsigned bonus_music(void) {
    if(!bonus_scene())return 0;
    if(word(0x1ff9e)!=10)return 281;
    return word(0xb243)==0x3f6f && g_ram[0xb245]==0xc5?0:134;
}
static const char *bonus_music_source(void){return word(0x1ff9e)==10?"audio.music.bug_toss":"audio.music.bug_hunt";}
static int late_adult(void) {return be_prepared() || simbas_return() || pride_rock();}
static int next_scene(void) {return exile() || stampede() || hakuna() || destiny() || late_adult();}
static unsigned address(unsigned at) {return word(at)|(unsigned)g_ram[at+2]<<16;}
static int opening_timon_selected(void) {
    return !word(0x1ff9e) && address(0xdf)==0xc005ab &&
        address(0xb217)==0xc5858a && address(0xb243)==0xc47146 &&
        word(0xb21b)==128 && word(0xb21d)==64 && TlkMdSoundReady() &&
        TlkResourcesUseMd("audio.voices.opening_timon");
}
static int ending_owner(void){return word(0x1ff9e)==9 && word(0x2000)==0xffff &&
    address(0xb217)==0xc5858a && address(0xb243)==0xc473e4;}
static int ending_sunrise(void){return ending_owner() && address(0xdf)==0xc007a9;}
static int ending_credits(void){return ending_owner() && address(0xdf)==0xc0083f;}
static int ending_credits_ready(void){return ending_credits() && word(0xa6f0)==3 &&
    word(0xb21b)==118 && word(0xb21d)==30;}
static int finale_scene(void){return word(0x1ff9e)==9 && word(0x2000)==0xffff &&
    address(0xdf)==0xc007db && address(0xb217)==0xc5858a && address(0xb243)==0xc674be;}
static int finale_carry(void){return music_track==339 && word(0x1ff9e)==9 && word(0x2000)==0xffff &&
    (finale_scene() || ending_sunrise() || address(0xdf)==0xc005ab);}
static int ending_speech_selected(void){return ending_sunrise() && word(0x1ff96) &&
    TlkResourcesUseMd("audio.voices.ending") && TlkInterlevelDataReady() && TlkMdSoundReady();}
#include "tlk_ending_timing.inc"

static unsigned cw_descriptor(unsigned actor) {
    if(actor<0x8000 || actor>0xff80)return 0;
    unsigned draw=word(actor+12),descriptor=address(actor+4);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 || (g_ram[draw+9]&0x40))return 0;
    return descriptor;
}
static int cw_actor(unsigned actor,int monkey) {
    unsigned descriptor=cw_descriptor(actor);
    if(!monkey)return descriptor==0xc58c14;
    for(unsigned i=0;i<sizeof cw_audio_monkey_descriptors/sizeof *cw_audio_monkey_descriptors;i++)
        if(descriptor==cw_audio_monkey_descriptors[i])return 1;
    return 0;
}
static void cw_tail(void) {fx_tail=120;cant_wait_fx=1;}
static void effect_tail(void) {
    fx_tail=120;
    if(cant_wait())cant_wait_fx=1;
    if(TlkAudioGraveyardScene())graveyard_fx=1;
}
static int prepared_scene(void) {
    return word(0x1ff9e)==7 && address(0xdf)==0xc004e5 && word(0x2000)==65535;
}
static int prepared_actor(unsigned actor) {
    return actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) && address(actor+4)==0xc587d6;
}
static void prepared_sound_log(unsigned actor,unsigned md,unsigned native_event,unsigned method,unsigned accepted) {
    static FILE*f;static int checked;
    if(!checked){checked=1;const char*p=getenv("TLK_BE_PREPARED_GROUP_AUDIO_TRACE");if(p)f=fopen(p,"w");if(f)fputs("field,actor,md,native_event,method,accepted\n",f);}
    if(f){fprintf(f,"%u,%04x,%u,%u,%u,%u\n",snes_frame_counter+1,actor,md,native_event,method,accepted);fflush(f);}
}
static int prepared_native_sound(const uint16_t*r) {
    /* Source C21C68's unlocked eight-byte effect packet. The ordinary native
     * wait/audio service flushes it; no fabricated guest call or RNG request.
     * Queue/scratch state has the same normal RAM ownership as other effects. */
    unsigned index=word(0x1f6d);
    if(word(0x1fbf)!=65535 || index>0x48 || (index&3))return 0;
    unsigned event=r[TLK_BP_SOUND_NATIVE_EVENT]|r[TLK_BP_SOUND_NATIVE_EVENT_FLAG];
    unsigned y=(r[TLK_BP_SOUND_NATIVE_PAN]&255)|(r[TLK_BP_SOUND_NATIVE_VOLUME]<<8);
    g_ram[0x1f15]=(uint8_t)event;g_ram[0x1f16]=(uint8_t)(event>>8);
    g_ram[0x1f17]=(uint8_t)y;g_ram[0x1f18]=(uint8_t)(y>>8);
    g_ram[0x1f19]=g_ram[0x1f1a]=0;g_ram[0x1fc7]=2;
    unsigned at=0x1f6f+index;
    g_ram[at]=2;g_ram[at+1]=(uint8_t)event;g_ram[at+2]=0;g_ram[at+3]=(uint8_t)y;
    g_ram[at+4]=3;g_ram[at+5]=(uint8_t)(event>>8);g_ram[at+6]=(uint8_t)(y>>8);g_ram[at+7]=0;
    index+=8;g_ram[0x1f6d]=(uint8_t)index;g_ram[0x1f6e]=(uint8_t)(index>>8);return 1;
}
static int prepared_md_sound(const uint16_t*r) {
    if(!TlkMdSoundReady())return 0;
    TlkMdSoundPcm(r[TLK_BP_SOUND_MD_SAMPLE],r[TLK_BP_SOUND_MD_PARAMETER]);
    fx_tail=120;prepared_fx=1;return 1;
}
void TlkAudioBePreparedGroupCall(unsigned actor) {
    const uint16_t*r=TlkBePreparedGroupSoundRules();
    if(!prepared_scene() || !prepared_actor(actor) || !word(0x1ff96) || !r)return;
    unsigned md=TlkResourcesUseMd("audio.effects.world.be_prepared.group_call");
    unsigned accepted=md?prepared_md_sound(r):prepared_native_sound(r);
    prepared_sound_log(actor,md,r[TLK_BP_SOUND_NATIVE_EVENT],0,accepted);
}
static int has_descriptor(unsigned value,const unsigned *items,unsigned count) {
    for(unsigned i=0;i<count;i++)if(value==items[i])return 1;
    return 0;
}
#define GY_FAMILY(value,items) has_descriptor(value,items,sizeof(items)/sizeof *(items))
static int graveyard_pillar_active(void) {
    /* Native actor-pool slots. The serialized pillar action owns its long
     * rumble, including pause/load; no independent sound-duration timer. */
    for(unsigned actor=0xb293;actor<0xc213;actor+=128)
        if(cw_descriptor(actor)==0xc58d44 && address(actor+0x30)==0xc2d1d3)return 1;
    return 0;
}
static void graveyard_opcode(CpuState *cpu,uint32_t pc,int before) {
    if(!TlkAudioGraveyardScene() || !word(0x1ff96) || !TlkMdSoundReady())return;
    unsigned actor=word(0x68),descriptor=cw_descriptor(actor),choice=GY_SOUND_COUNT,value=0;
    if(!descriptor)return;
    /* Observe each actual store once. Interpreter observes BEFORE that same
     * store (A=0, old counter=1), compiled mode AFTER it (counter=0). Hooking
     * the following interpreter instruction would repeat a completed AOT event
     * when a paced yield resumes there. No frame latch or guest write needed. */
    int completed=before ? cpu->A==0 && word(actor+0x2c)==1 : !word(actor+0x2c);
    if(pc==0xc19ac7 && address(actor+0x30)==0xc199f9 && completed &&
       GY_FAMILY(descriptor,gy_shake_descriptors)){choice=GY_SHAKE;value=105;}
    else if(pc==0xc19f87 && address(actor+0x30)==0xc19e97 && completed &&
       GY_FAMILY(descriptor,gy_platform_descriptors)){choice=GY_PLATFORM;value=127;}
    else if(pc==0xc22cbf && (before?word((cpu->S+4)&65535):cpu->A)==11 && descriptor==0xc58d44 &&
       address(actor+0x30)==0xc2d1d3){choice=GY_PILLAR;value=92;}
    if(choice<GY_SOUND_COUNT && TlkResourcesUseMd(gy_sources[choice])) {
        TlkMdSoundCommand(2,value);effect_tail();
    }
}
void TlkAudioAnimationToken(CpuState *cpu,uint32_t pc) {
    if((pc!=0xc0ad50 && pc!=0xad50) || cpu->D || cpu->DB!=0x7e ||
       !cpu->m_flag || !cpu->x_flag || !cant_wait() || !word(0x1ff96) ||
       !TlkMdSoundReady())return;
    unsigned cursor=address(0x14),descriptor=cw_descriptor(word(0x68));
    unsigned choice=CW_SOUND_COUNT,selector=0,value=0;
    if(descriptor==0xc58c20 || descriptor==0xc58c2c) {
        /* Original MD running stream B902C has FD01 markers before the
         * first, sixth and eleventh shared poses. Native uses the same11
         * three-update poses. Observe token entry, never a host-frame timer. */
        if(cursor==0xc26c41 || cursor==0xc26c55 || cursor==0xc26c69)
            {choice=CW_STEPS;selector=2;value=94;}
        /* The first jump pose is outside its loop, so it emits once per
         * take-off. The native jump action/velocity remains untouched. */
        else if(cursor==0xc26cb1){choice=CW_JUMP;selector=2;value=169;}
    } else if((descriptor==0xc58814 || descriptor==0xc5881d) && cursor==0xc25847) {
        /* Original MD B8CA6/19FC1A: these are flying creatures, not the
         * monkey actors which happened to occupy their slots earlier. */
        choice=CW_TAKEOFF;selector=19;value=5;
    }
    if(choice<CW_SOUND_COUNT && TlkResourcesUseMd(cw_sources[choice])) {
        TlkMdSoundCommand(selector,value);cw_tail();
    }
}
static void cw_reaction_remember(unsigned actor) {
    if(!cw_actor(actor,1))return;
    for(unsigned i=0;i<cw_reaction_count;i++)if(cw_reactions[i].actor==actor)return;
    if(cw_reaction_count>=sizeof cw_reactions/sizeof *cw_reactions)return;
    unsigned i=cw_reaction_count++;cw_reactions[i].actor=actor;
    cw_reactions[i].descriptor=address(actor+4);cw_reactions[i].draw=word(actor+12);
}
static void cw_reaction_rebuild(void) {
    cw_reaction_count=0;
    if(!cant_wait() || !word(0x1ff96) || !TlkResourcesUseMd(cw_sources[CW_REACTION]))return;
    for(unsigned actor=0x8000;actor<=0xff80;actor++)
        if(address(actor+0x30)==0xc455ac && word(actor+0x2e)>0 && word(actor+0x2e)<=18)
            cw_reaction_remember(actor);
}
static void cw_reaction_frame(void) {
    if(!cw_reaction_count)return;
    if(!cant_wait() || !word(0x1ff96) || !TlkResourcesUseMd(cw_sources[CW_REACTION])){cw_reaction_count=0;return;}
    if(word(0x0a89))return;
    for(unsigned i=0;i<cw_reaction_count;) {
        unsigned actor=cw_reactions[i].actor;
        int owned=cw_actor(actor,1) && address(actor+4)==cw_reactions[i].descriptor && word(actor+12)==cw_reactions[i].draw;
        if(owned && word(actor+0x2e)==0){TlkMdSoundCommand(19,8);cw_tail();}
        else if(owned && address(actor+0x30)==0xc455ac){i++;continue;}
        cw_reactions[i]=cw_reactions[--cw_reaction_count];
    }
}
static int menu_effect_scene(void) {
    return word(0xdf)==0x5ab && g_ram[0xe1]==0xc0;
}
static int level_select_effect_owner(void) {
    unsigned actor=word(0x68);
    return actor>=0x2000 && actor<=0xffa0 && actor==word(0x6e) &&
        address(actor+48)==0xc46e59;
}
static int sound_test_scene(void) {
    unsigned actor=word(0x6e);
    return TLK_FINAL_MENU_ART_AVAILABLE && menu_effect_scene() && actor>=0x2000 && actor<=0xffa0 &&
        address(actor+48)==0xc46b68 && TlkResourcesUseMd("audio.music.sound_test");
}
static void sound_test_frame(void) {
    if(music_scene!=16) {
        /* The original audition opens on Circle of Life and keeps the title
         * score running. A native-title mix starts MD73 once on entry. */
        if(music_active && music_track!=73)TlkMdSoundCommand(1,0);
        if(word(0x1ff94) && (!music_active || music_track!=73))TlkMdSoundCommand(1,73);
        music_active=word(0x1ff94)!=0;music_track=music_active?73:0;music_scene=16;pending_stop=0;
    }
    if(!word(0x1ff94) && music_active){TlkMdSoundCommand(1,0);music_active=0;music_track=0;}
    if(fx_tail)fx_tail--;
}
static void sound_test_opcode(CpuState *cpu,uint32_t pc) {
#if TLK_FINAL_MENU_ART_AVAILABLE
    if(!sound_test_scene() || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag)return;
    unsigned actor=word(0x68);if(actor!=word(0x6e))return;
    if(pc==0xc07889 && !word(0x1ff94) && cpu->A==1) {
        /* Native C07882 enables music for every audition. Original MD keeps
         * Music Off; retain its setting before the native long-address store. */
        cpu->A=0;cpu->_flag_Z=1;cpu->_flag_N=0;cpu->P=(uint8_t)((cpu->P&~0x82)|2);return;
    }
    if(pc==0xc46bd7){
        g_ram[actor+46]=3;g_ram[actor+47]=0;
        if(word(0x1ff96) && TlkMdSoundReady()){TlkMdSoundCommand(2,101);fx_tail=120;menu_fx=1;}
        return;
    }
    if(pc==0xc46d4c) {
        unsigned row=word(actor+46),input=word(0x62),dirty=word(cpu->D+0x22),next=row;
        if(row==0 && !dirty && (input&0xc00)==0x800)next=15;
        else if(row==16 && dirty && (input&0xc00)==0x400)next=0;
        if(next!=row){g_ram[actor+46]=(uint8_t)next;g_ram[actor+47]=0;g_ram[cpu->D+0x22]=1;g_ram[cpu->D+0x23]=0;cpu->A=(uint16_t)next;}
        return;
    }
    if(pc==0xc46c88){sound_test_frame();TlkMdSoundCommand(1,0);music_active=0;music_track=pending_stop=0;return;}
    if(pc==0xc46ccf) {
        unsigned program;
        if(!TlkFinalArtSoundTestProgram(sound_test_art,word(actor+46),&program)) {
            fprintf(stderr,"Installed Sound Test catalogue unavailable. Run Setup.\n");exit(114);
        }
        if(word(0x1ff94)){TlkMdSoundCommand(1,program);music_track=program;music_active=1;}
        music_scene=16;pending_stop=0;
    }
#else
    (void)cpu;(void)pc;
#endif
}
static int title_music_scene(void) {
    unsigned actor=word(0x6e);
    if(actor<0x2000 || actor>0xffa0)return 0;
    unsigned action=address(actor+48);
    /* Options and level selection retain the title score, even when the
     * chosen stage changes. Sound-test C46B68 has its own audition source
     * and must not acquire title-score ownership. */
    if(menu_effect_scene())return action==0xc462f6 || action==0xc465f0 || action==0xc4690e || action==0xc46e59;
    return word(0x1ff9e)==14 && address(0xdf)==0xc0057b && action==0xc462f6;
}
/* The ordinary opening becomes ready by changing level14 to0. That is still
 * the same title song, not a new level entry or a reason to rewind the driver. */
static unsigned music_scene_id(void) { return title_music_scene()?14:word(0x1ff9e); }
/* The shared Continue initializer retains the outgoing main-level number. */
static int game_over_scene(void) { return word(0x1ff9e)<=9 && address(0xdf)==0xc0057b && !word(0x1ffaa); }
static unsigned pride_music(void) { return word(0xdf)==0x80d?134:137; }
static int death_scene(void) { return pride() || cant_wait() || TlkAudioGraveyardScene() || exile() || hakuna() || destiny() || late_adult(); }
static const char *death_music_source(void) {
    if(hakuna())return "audio.music.hakuna_matata.death";
    if(destiny())return "audio.music.simbas_destiny.death";
    if(be_prepared())return "audio.music.be_prepared.death";
    if(simbas_return())return "audio.music.simbas_return.death";
    if(pride_rock())return "audio.music.pride_rock.death";
    return exile()?"audio.music.simbas_exile.death":TlkAudioGraveyardScene()?"audio.music.elephant_graveyard.death":"audio.music.pride_health_death";
}
static int md_death_music(void) { return death_scene() && TlkResourcesUseMd(death_music_source()); }
static int health_death(void) {
    return death_scene() && ((destiny() || late_adult())?word(0x2000)==0xffff:!word(0x2000)) && !word(0x2004) && word(0x1ffaa) &&
           ((word(0xb243)==0x5a82 && word(0xb245)==0xc3) || TlkHealthDeathAudioNested(g_ram,word(0x2000)==0xffff));
}
static unsigned scene_music(void) {
    if(title_music_scene()) {
        unsigned actor=word(0x6e);
        if(TlkResourcesUseMd("graphics.menus.publisher_cards") && word(0x1ff9e)==14 &&
           address(0xdf)==0xc0057b && actor>=0x2000 && actor<=0xffa0 && address(actor+48)==0xc462f6 &&
           !word(actor+46) && word(actor+44)>=130 && word(actor+44)<=319)return 0;
        return 73;
    }
    /* The guest sets118/30 after credits initialization returns, immediately
     * before its song55 request. Start MD61 on that ordinary frame boundary,
     * rather than at the earlier descriptor write or through the FX gate. */
    if(ending_credits())return ending_credits_ready() || music_track==61?61:0;
    if(finale_carry())return 339;
    if (pride()) return death_phase>=2 ? (death_phase==2 && md_death_music()?430:0) : pride_music();
    if (game_over_scene()) return 327;
    if(bonus_scene())return bonus_music();
    if ((cant_wait() || TlkAudioGraveyardScene() || exile() || hakuna() || destiny() || late_adult()) && death_phase>=2)
        return death_phase==2 && md_death_music()?430:0;
    unsigned level=word(0x1ff9e),descriptor=word(0xdf);
    /* Original level-music table 1D723C, observed at original driver entry.
     * Unsupported scene descriptors retain their native path. */
    static const unsigned tracks[]={137,2,83,145,258,40,281,327,311,432};
    if (level>0 && level<MUSIC_COUNT && descriptor==0x387+level*0x32) return tracks[level];
    return 0;
}
static int selected_music(void) {
    if(title_music_scene())return word(0x1ff94) && TlkResourcesUseMd("audio.music.title");
    if(finale_carry())return TlkResourcesUseMd("audio.music.pride_rock.finale");
    if(ending_credits())return scene_music()==61 && TlkResourcesUseMd("audio.music.ending_credits");
    /* The original game-over initializer, not the descriptor write, starts
     * this theme. The already serialized track retains that event across saves. */
    if(game_over_scene())return music_track==327 && TlkResourcesUseMd("audio.music.pride_game_over");
    if(death_scene() && death_phase>=2)return death_phase==2 && md_death_music();
    if(bonus_scene())return bonus_music() && TlkResourcesUseMd(bonus_music_source());
    unsigned level=word(0x1ff9e);
    return level<MUSIC_COUNT && scene_music() && TlkResourcesUseMd(music_sources[level]);
}
/* The native exit assigns the next main level before removing its bonus
 * scene. Keep the already-owned outgoing music dry voices under that source
 * choice until the incoming scene takes over; gameplay FX remain independent. */
static int bonus_music_tail_selected(void) {
    unsigned scene=address(0xdf);
    if(music_scene<10 || music_scene>13 ||
       (scene && scene!=0xc005dd+(music_scene-10)*0x32))return 0;
    return TlkResourcesUseMd(music_scene==10?"audio.music.bug_toss":"audio.music.bug_hunt");
}
int TlkAudioNativeMusicSelected(void) {
    /* Original SEGA prefix is silent. Keep selected native title music muted
     * while the added card's native countdown postpones MD program73. */
    int publisher_title=title_music_scene() && TlkResourcesUseMd("graphics.menus.publisher_cards");
    /* The selected final-life cue has already stopped. Its silence still
     * owns native music output until the Continue initializer takes over;
     * otherwise the old SPC score/tail becomes audible again. FX stay live. */
    int final_death_silence=death_scene() && death_phase==3 && !word(0x1ffaa) &&
        word(0x1ff94) && md_death_music();
    return TlkMdSoundReady() && (final_death_silence || bonus_music_tail_selected() ||
        ((title_music_scene() || cant_wait() || stampede() || death_scene() || game_over_scene() || bonus_scene() || finale_carry()) &&
         (music_active || publisher_title) && selected_music()));
}
int TlkAudioMusicAvailable(const char *id) {
    if(!TlkMdSoundReady())return 0;
    if(id && !strcmp(id,"audio.music.title"))return title_music_scene();
    if(id && !strcmp(id,"audio.music.pride_rock.finale"))return finale_carry();
    if(finale_carry())return 0;
    if(id && !strcmp(id,"audio.music.ending_credits"))return ending_credits() && scene_music()==61;
    if(id && (!strcmp(id,"audio.music.bug_toss") || !strcmp(id,"audio.music.bug_hunt")))return bonus_music() && !strcmp(id,bonus_music_source());
    if(id && !strcmp(id,"audio.music.pride_game_over"))return game_over_scene();
    if(game_over_scene())return 0;
    if(id && !strcmp(id,"audio.music.pride_health_death"))return pride() && !word(0x2000) &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.elephant_graveyard.death"))return TlkAudioGraveyardScene() && !word(0x2000) &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.simbas_exile.death"))return exile() && !word(0x2000) &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.hakuna_matata.death"))return hakuna() && !word(0x2000) &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.simbas_destiny.death"))return destiny() && word(0x2000)==0xffff &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.be_prepared.death"))return be_prepared() && word(0x2000)==0xffff &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.simbas_return.death"))return simbas_return() && word(0x2000)==0xffff &&
        (death_phase==2 || word(0x1ffaa));
    if(id && !strcmp(id,"audio.music.pride_rock.death"))return pride_rock() && word(0x2000)==0xffff && (death_phase==2 || word(0x1ffaa));
    unsigned level=word(0x1ff9e);
    return id && level<MUSIC_COUNT && !strcmp(id,music_sources[level]) && scene_music()!=0;
}
static int music_mask(void) {
    int mask=0;
    for (unsigned i=0;i<MUSIC_COUNT;i++) if (TlkResourcesUseMd(music_sources[i])) mask|=1<<i;
    if(TlkResourcesUseMd("audio.music.pride_health_death"))mask|=1<<MUSIC_COUNT;
    if(TlkResourcesUseMd("audio.music.pride_game_over"))mask|=1<<(MUSIC_COUNT+1);
    if(TlkResourcesUseMd("audio.music.elephant_graveyard.death"))mask|=1<<(MUSIC_COUNT+2);
    if(TlkResourcesUseMd("audio.music.simbas_exile.death"))mask|=1<<(MUSIC_COUNT+3);
    if(TlkResourcesUseMd("audio.effects.world.stampede.start"))mask|=1<<(MUSIC_COUNT+4);
    if(TlkResourcesUseMd("audio.effects.world.stampede.hurt"))mask|=1<<(MUSIC_COUNT+5);
    if(TlkResourcesUseMd("audio.effects.world.simbas_exile.rocks"))mask|=1<<(MUSIC_COUNT+6);
    if(TlkResourcesUseMd("audio.music.hakuna_matata.death"))mask|=1<<(MUSIC_COUNT+7);
    if(TlkResourcesUseMd("audio.music.simbas_destiny.death"))mask|=1<<(MUSIC_COUNT+8);
    if(TlkResourcesUseMd("audio.music.be_prepared.death"))mask|=1<<(MUSIC_COUNT+9);
    if(TlkResourcesUseMd("audio.music.simbas_return.death"))mask|=1<<(MUSIC_COUNT+10);
    if(TlkResourcesUseMd("audio.effects.world.adult_hyenas.attack"))mask|=1<<(MUSIC_COUNT+11);
    if(TlkResourcesUseMd("audio.effects.world.adult_hyenas.reaction"))mask|=1<<(MUSIC_COUNT+12);
    if(TlkResourcesUseMd("audio.music.pride_rock.death"))mask|=1<<(MUSIC_COUNT+13);
    if(TlkResourcesUseMd("audio.music.bug_toss"))mask|=1<<(MUSIC_COUNT+14);
    if(TlkResourcesUseMd("audio.music.bug_hunt"))mask|=1<<(MUSIC_COUNT+15);
    if(TlkResourcesUseMd("audio.voices.ending"))mask|=1<<(MUSIC_COUNT+16);
    if(TlkResourcesUseMd("audio.music.ending_credits"))mask|=1<<(MUSIC_COUNT+17);
    if(TlkResourcesUseMd("audio.music.pride_rock.finale"))mask|=1<<(MUSIC_COUNT+18);
    if(TlkResourcesUseMd("audio.music.title"))mask|=1<<(MUSIC_COUNT+19);
    if(TlkResourcesUseMd("audio.music.sound_test"))mask|=1<<(MUSIC_COUNT+20);
    return mask;
}
static void start_music(void) {
    if(!TlkMdSoundReady() || (title_music_scene() && !scene_music()))return;
    if(music_scene!=music_scene_id())music_entry_seen=0;
    if(TLK_BATTLE_MUSIC_TRIGGER_AVAILABLE && pride() && scene_music()==134) {
        /* The native bank cue precedes its opening jump. Original MD issues
         * battle program134 at that jump; keep the preceding song until then. */
        if(!battle_ready || (music_active && music_track==134))return;
    }
    /* A death song is an in-scene driver command: keep already produced FX
     * samples and the resampler phase, including the hurt voice just queued. */
    if(death_phase!=2)TlkMdSoundClearOutput();
    /* A cold native research load may already be in ordinary gameplay.
     * Current frontend saves retain this flag explicitly below. Initial
     * level construction has not enabled controls or installed a C3 action. */
    if(!music_active && word(0x1ff9e)<10 && word(0xdf)==0x387+word(0x1ff9e)*0x32 &&
       !death_phase && word(0xa8b) && (address(0xb243)>>16)==0xc3)music_entry_seen=1;
    music_track=scene_music();music_scene=music_scene_id();
    TlkMdSoundCommand(1,music_track);music_active=1;pending_stop=!title_music_scene() && !ending_credits() && !finale_carry();
    static FILE *start_trace;static int start_trace_open;
    if(!start_trace_open){start_trace_open=1;const char *p=getenv("TLK_MUSIC_START_TRACE");if(p)start_trace=fopen(p,"w");
        if(start_trace)fputs("field,level,descriptor,track\n",start_trace);}
    if(start_trace){fprintf(start_trace,"%u,%u,%06x,%u\n",snes_frame_counter+1,music_scene,address(0xdf),music_track);fflush(start_trace);}
}
void TlkAudioHyenaBattleJump(CpuState *cpu,uint32_t pc) {
    if(!TLK_BATTLE_MUSIC_TRIGGER_AVAILABLE || (pc!=0xc14453 && pc!=0xc144d8) ||
       cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0x1ff9e) || word(0x2000) || word(0xdf)!=0x80d || g_ram[0xe1]!=0xc0 ||
       word(0xabf) || cpu->D<0x600 || cpu->D>0x1fdb || word(0xa68c)!=cpu->D+0x22)return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       word(actor+4)!=0x8c68 || g_ram[actor+6]!=0xc5 ||
       word(actor+0x30)!=0x43ae || g_ram[actor+0x32]!=0xc1 || !word(actor+0x2a))return;
    battle_ready=1;
    if(selected_music() && word(0x1ff94))start_music();
    static FILE *log;const char *path=getenv("TLK_BATTLE_MUSIC_TRACE");
    if(path) {
        if(!log){log=fopen(path,"w");if(log)fputs("field,pc,actor,music_track,active,audio_wait\n",log);}
        if(log){fprintf(log,"%u,%06x,%04x,%u,%u,%u\n",(unsigned)snes_frame_counter+1,pc,actor,music_track,music_active,word(0xabf));fflush(log);}
    }
}
static void stop_music(void) {
    if(music_active) {
        TlkMdSoundCommand(1,0);
        /* Consume Music Off while preserving independently selected FX. */
        fx_tail=120;
    }
    music_active=pending_stop=0;music_track=0;
}
static unsigned music_caller(const CpuState *cpu) {
    unsigned sp=cpu->S,offset;
    if(g_ram[(sp+5)&65535]!=0xc2)return 0;
    if(word((sp+3)&65535)==0x2d16)offset=6; /* C22CEC parameter wrapper */
    else if(word((sp+3)&65535)==0x2d4d)offset=7; /* C22D1F retains PHP */
    else return 0;
    return (unsigned)g_ram[(sp+offset+2)&65535]<<16|((word((sp+offset)&65535)+1)&65535);
}
/* These four owned native defeat markers correspond to original MD1A8A30.
 * Preserve the independently selected native animation/recovery clock. */
/* Native C04D15 adds cue35 before the ordinary jump/landing continuation.
 * Original counterpart1A8E80 calls1A8EEE directly with no corresponding cue. */
static int gorilla_jump_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x35 || !hakuna() || word(0x2000) ||
       !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_jump"))return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58a7f || address(actor+48)!=0xc04d15 ||
       music_caller(cpu)!=0xc04d84)return 0;
    static FILE *log;static int checked;
    if(!checked){checked=1;const char *p=getenv("TLK_GORILLA_JUMP_AUDIO_TRACE");if(p)log=fopen(p,"w");if(log)fputs("field,actor,action,event,caller,selector,value\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,53,c04d84,0,0\n",snes_frame_counter+1,actor,address(actor+48));fflush(log);}
    cpu->A=0;effect_tail();return 1;
}

/* Corresponding original phase-three marker: nativeC043F3 / MD1A85BC.
 * This is distinct from the correctly silent ordinary jump marker. */
/* Original coconut descriptor0E9296: FM123 bounce / FM103 break.
 * Only the corresponding owned native C58E84 requests are replaced. */
static int coconut_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || !hakuna() || word(0x2000) ||
       !word(0x1ff96) || !TlkMdSoundReady())return 0;
    unsigned actor=word(0x68),caller=music_caller(cpu);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58e84)return 0;
    unsigned value=0;
    if(cpu->X==0x25 && caller==0xc05691 && address(actor+48)==0xc053d4 &&
       TlkResourcesUseMd("audio.effects.world.hakuna.coconut_bounce"))value=123;
    if(cpu->X==0x1c && caller==0xc053a7 && address(actor+48)==0xc05336 &&
       TlkResourcesUseMd("audio.effects.world.hakuna.coconut_break"))value=103;
    if(!value)return 0;
    TlkMdSoundCommand(2,value);
    static FILE *log;static int checked;
    if(!checked){checked=1;const char*p=getenv("TLK_COCONUT_AUDIO_TRACE");if(p)log=fopen(p,"w");if(log)fputs("field,actor,action,event,caller,selector,value\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,%u,%06x,2,%u\n",snes_frame_counter+1,actor,address(actor+48),cpu->X,caller,value);fflush(log);}
    cpu->A=0;effect_tail();return 1;
}

static int gorilla_attack_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x35 || !hakuna() || word(0x2000) ||
       !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_attack"))return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58a7f || address(actor+48)!=0xc04301 ||
       word(actor+46)!=3 || music_caller(cpu)!=0xc043f7)return 0;
    TlkMdSoundCommand(2,166);
    static FILE *log;static int checked;
    if(!checked){checked=1;const char*p=getenv("TLK_GORILLA_ATTACK_AUDIO_TRACE");if(p)log=fopen(p,"w");if(log)fputs("field,actor,action,phase,event,caller,selector,value\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,3,53,c043f7,2,166\n",snes_frame_counter+1,actor,address(actor+48));fflush(log);}
    cpu->A=0;effect_tail();return 1;
}

/* MD1A9056 requests PCM13 on the grabbed-player release branches.
 * Select its response at the native grab animation cue, retaining native timing. */
static int gorilla_grab_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x2b || !hakuna() || word(0x2000) ||
       !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_grab"))return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58a7f || address(actor+48)!=0xc04f34 ||
       word(actor+46)!=2 || music_caller(cpu)!=0xc04fb9)return 0;
    TlkMdSoundPcm(13,96);
    static FILE *log;static int checked;
    if(!checked){checked=1;const char*p=getenv("TLK_GORILLA_GRAB_AUDIO_TRACE");if(p)log=fopen(p,"w");if(log)fputs("field,actor,action,phase,event,caller,selector,value,parameter\n",log);}
    if(log){fprintf(log,"%u,%04x,%06x,2,43,c04fb9,19,13,96\n",snes_frame_counter+1,actor,address(actor+48));fflush(log);}
    cpu->A=0;effect_tail();return 1;
}

static int gorilla_defeat_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || !hakuna() || word(0x2000) || !word(0x1ff96) ||
       !TlkMdSoundReady() || !TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_defeat"))return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58a7f || address(actor+48)!=0xc04880)return 0;
    static const struct {unsigned event,caller,selector,value;} cues[]={
        {0x29,0xc04ab5,2,172}, {0x2a,0xc04a82,19,14},
        {0x18,0xc04ae4,2,92}, {0x1c,0xc04b04,2,163}
    };
    unsigned caller=music_caller(cpu);
    for(unsigned i=0;i<sizeof cues/sizeof *cues;i++) {
        if(cpu->X!=cues[i].event || caller!=cues[i].caller)continue;
        /* Original2210 table gives gorilla sample14 parameter128, rather
         * than the generic cub/hyena parameter96. No music driver restart. */
        if(cues[i].selector==19)TlkMdSoundPcm(cues[i].value,128);
        else TlkMdSoundCommand(cues[i].selector,cues[i].value);
        static FILE *log;static int checked;
        if(!checked){checked=1;const char *p=getenv("TLK_GORILLA_DEFEAT_AUDIO_TRACE");if(p)log=fopen(p,"w");if(log)fputs("field,actor,action,event,caller,selector,value,parameter\n",log);}
        if(log){fprintf(log,"%u,%04x,%06x,%u,%06x,%u,%u,%u\n",snes_frame_counter+1,actor,address(actor+48),cpu->X,caller,cues[i].selector,cues[i].value,cues[i].selector==19?128:0);fflush(log);}
        cpu->A=0;effect_tail();return 1;
    }
    return 0;
}

static void victory_voice_log(const char *event,unsigned caller,unsigned selected,unsigned emitted){
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_VICTORY_VOICE_TRACE");if(path){log=fopen(path,"w");if(log)fputs("field,event,caller,phase,target,target_descriptor,selected,emitted\n",log);}}
    unsigned target=word(0xa6d0);
    if(log){fprintf(log,"%u,%s,%06x,%u,%04x,%06x,%u,%u\n",snes_frame_counter+1,event,caller,word(0xb23f),target,target<0xff80?address(target+4):0,selected,emitted);fflush(log);}
}
static int scar_finish_context(void){
    unsigned target=word(0xa6d0);
    return pride_rock() && word(0x2000)==65535 && word(0x68)==0xb213 &&
        address(0xb217)==0xc5858a && address(0xb243)==0xc378e9 &&
        g_ram[0xa6d2]==0x7e && target>=0xb293 && target<0xdc13 &&
        !((target-0xb213)&127) && address(target+4)==0xc58600;
}
static void scar_finish_entry(CpuState *cpu,uint32_t pc){
    if(pc!=0xc37a34 || cpu->PB!=0xc3 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       cpu->_flag_D || cpu->D<0x600 || cpu->D>=0x1f00 || word(0xa68c)!=cpu->D+0x2a ||
       !pride_rock() || word(0x68)!=0xb213)return;
    unsigned selected=TlkResourcesUseMd(victory_voice_sources[0]);
    unsigned emitted=selected && scar_finish_context() && word(0x1ff96) && TlkMdSoundReady();
    /* This serialized action's first-entry branch has just installed C378E9.
     * Original198C8A requests adult11 on the corresponding Scar finish entry.
     * No new action, delay, actor write, random draw or input is introduced. */
    if(emitted){TlkMdSoundPcm(11,96);effect_tail();}
    victory_voice_log("finish_entry",pc,selected,emitted);
}

void TlkAudioDestinyMonkeyShot(void) {
    if(destiny() && word(0x1ff96) && TlkDestinyMonkeyDataReady() && TlkMdSoundReady() &&
       TlkResourcesUseMd("audio.effects.world.simbas_destiny.monkey_shot")) {
        TlkMdSoundCommand(2,TlkDestinyMonkeyParameter(TLK_MONKEY_SHOOT_CUE));effect_tail();
    }
}
static int adult_roar_context(void){
    unsigned level=word(0x1ff9e);
    return level>=6 && level<=9 && address(0xdf)==0xc004b3+(level-6)*50 &&
        word(0x2000)==65535 && word(0x68)==0xb213 &&
        address(0xb217)==0xc5858a && address(0xb243)==0xc3589c;
}
static void adult_roar_log(const char *event,unsigned selected){
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_ADULT_ROAR_AUDIO_TRACE");if(path){log=fopen(path,"w");if(log)fputs("field,event,level,counter,source_md,selector,value\n",log);}}
    if(log){fprintf(log,"%u,%s,%u,%u,%u,19,11\n",snes_frame_counter+1,event,word(0x1ff9e),g_ram[0xb255],selected);fflush(log);}
}
void TlkAudioAdultRoarPulse(CpuState *cpu,uint32_t pc){
    if(pc!=0xc35971 || !adult_roar_context() || cpu->PB!=0xc3 || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>=0x1f00 ||
       word(0xa68c)!=cpu->D+0x24)return;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.adult_roar");
    adult_roar_log("pulse",selected);
    /* MD196770/18F0DE selects11 for adult and10 for cub by AGE, not RNG.
     * Trigger at the real pulse for either independently selected gameplay
     * timing. Preserve all actor stores, counters and random state. */
    if(selected && word(0x1ff96) && TlkMdSoundReady()){
        TlkMdSoundCommand(19,11);effect_tail();
    }
}
void TlkAudioLeafTrigger(void) {
    if ((pride() || exile()) && word(0x1ff96) && TlkResourcesUseMd("audio.effects.world.leaves") && TlkMdSoundReady()) {
        TlkMdSoundCommand(2,94);fx_tail=120;
    }
}
void TlkAudioAdultHyenaTauntEntry(CpuState *cpu,uint32_t pc) {
    if((pc!=0xc1ac50 && pc!=0xc1ad78) || cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       cpu->_flag_D || cpu->D<0x600 || cpu->D>=0x1f00 || word(0xa68c)!=cpu->D+0x24 ||
       !late_adult() || word(0x2000)!=65535)return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58ecc ||
       address(actor+48)!=(pc==0xc1ac50?0xc1abf6:0xc1ad1e) ||
       address(actor+14)!=(pc==0xc1ac50?0xc24d5c:0xc24d7c) || word(actor+46))return;
    /* Native first-entry branch only; normal updates and restored initialized
     * actors skip these entry branches. MD1ADC76 and1ADD90 both request3/96.
     * No host latch, actor/CPU writes, RNG call or animation substitution. */
    unsigned selected=TlkResourcesUseMd("audio.effects.world.adult_hyenas.taunt");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    if(emitted){TlkMdSoundPcm(3,96);effect_tail();}
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_ADULT_HYENA_TAUNT_TRACE");if(path){log=fopen(path,"w");if(log)fputs("field,actor,selected,emitted,entry,action\n",log);}}
    if(log){fprintf(log,"%u,%04x,%u,%u,%06x,%06x\n",snes_frame_counter+1,actor,selected,emitted,pc,address(actor+48));fflush(log);}
}
int TlkAudioHyenaTauntTrigger(void) {
    if ((!pride() && !TlkAudioGraveyardScene()) || !word(0x1ff96) || !TlkMdSoundReady() ||
        !TlkResourcesUseMd("audio.effects.world.hyena_taunt")) return 0;
    TlkMdSoundCommand(19,3);effect_tail();return 1;
}
int TlkAudioHyenaVoiceTrigger(void) {
    if((!pride() && !TlkAudioGraveyardScene()) || word(0x2000) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.hyena_hurt"))return 0;
    TlkMdSoundCommand(19,4);effect_tail();return 1;
}
int TlkAudioLizardDefeatTrigger(void) {
    if(!TlkDefeatAudioScene(g_ram) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.defeat_puff"))return 0;
    TlkMdSoundCommand(2,165);fx_tail=120;return 1;
}
int TlkAudioLizardLaunchTrigger(void) {
    if((!pride() && !exile()) || word(0x2000) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.lizard_launch"))return 0;
    TlkMdSoundCommand(2,123);fx_tail=120;return 1;
}
void TlkAudioPorcupineAttackVoice(CpuState *cpu,uint32_t pc) {
    if(!TLK_PORCUPINE_VOICE_TIMING_AVAILABLE || pc!=0xc15d14 ||
       cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !pride() || word(0x2000) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.porcupine"))return;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xc213 || ((actor-0xb213)&127) ||
       word(actor+4)!=0x8c5c || g_ram[actor+6]!=0xc5 ||
       word(actor+0x30)!=0x5b87 || g_ram[actor+0x32]!=0xc1 ||
       word(actor+0x2c)!=28 || cpu->D<0x600 || cpu->D>0x1f00 ||
       word(cpu->D)!=actor || word(0xa68c)!=cpu->D+0x22)return;
    /* Both gameplay paths reach this original seam after the nonpersistent
     * timer clear. The original countdown then advances, owning exactly one
     * cue without host latches or guest writes. Keep the native sound queue. */
    TlkMdSoundCommand(2,105);fx_tail=120;
    static FILE *log;const char *path=getenv("TLK_PORCUPINE_VOICE_TRACE");
    if(path) {
        if(!log){log=fopen(path,"w");if(log)fputs("field,actor,counter,gameplay_md\n",log);}
        if(log){fprintf(log,"%u,%04x,28,%d\n",(unsigned)snes_frame_counter+1,actor,
            TlkResourcesUseMd("gameplay.levels.pride_lands.porcupine_attack"));fflush(log);}
    }
}
int TlkAudioLizardAttackTrigger(void) {
    if((!pride() && !exile()) || word(0x2000) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.lizard"))return 0;
    TlkMdSoundCommand(2,124);fx_tail=120;return 1;
}
int TlkAudioPickupArrivalTrigger(void) {
    if((!pride() && !TlkAudioGraveyardScene()) || word(0x2000) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.pickup_arrival"))return 0;
    TlkMdSoundCommand(2,112);effect_tail();return 1;
}
static int continue_world_scene(void);
int TlkAudioLedgeGrabTrigger(void) {
    unsigned level=word(0x1ff9e);
    if((!continue_world_scene() && !(level==9 && address(0xdf)==0xc007db)) ||
       word(0x2000)!=(level<6?0:0xffff) || !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.simba.ledge_grab"))return 0;
    TlkMdSoundCommand(2,94);effect_tail();return 1;
}
/* C5567E/C55714 is the common1UP collection program. Its audio follows
 * the submitted request in any scene; placement is not sound ownership. */
static int shared_one_up_request(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x13)return 0;
    unsigned actor=word(0x68);
    unsigned caller=((unsigned)g_ram[(cpu->S+8)&65535]<<16)|((word((cpu->S+6)&65535)+1)&65535);
    return caller==0xc55714 && actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
        address(actor+4)==0xc58981 && address(actor+48)==0xc5567e;
}
static int continue_world_scene(void) {
    unsigned level=word(0x1ff9e),scene=address(0xdf);
    return level<=9 && level!=3 &&
        (scene==0xc00387+level*50 || (!level && scene==0xc0080d));
}
static int cue_in_scene(const char *id) {
    if((destiny() || late_adult()) && !strcmp(id,"audio.effects.simba.hurt"))return 1;
    if(continue_world_scene() && !strcmp(id,"audio.effects.world.continue_token"))return 1;
    if(!strcmp(id,"audio.effects.world.one_up"))return 1;
    if(pride())return 1;
    /* Shared pickup programs use the same original sound in every main
     * world. The cue table still qualifies each exact native caller and
     * excludes Simba; level placement must not change sound ownership. */
    if(cant_wait() || TlkAudioGraveyardScene() || exile() || hakuna() || destiny() || late_adult()) {
        static const char *shared[]={"audio.effects.world.health_bug","audio.effects.world.full_health_bug",
            "audio.effects.world.life_bug","audio.effects.world.roar_bug","audio.effects.world.harmful_bug",
            "audio.effects.world.checkpoint","audio.effects.world.bonus_bug"};
        for(unsigned i=0;i<sizeof shared/sizeof *shared;i++)if(!strcmp(id,shared[i]))return 1;
    }
    /* Shared cub controller07D728 and its native C3 action family, also
     * used in Hakuna. Adult voices and scene-owned enemy FX stay separate. */
    if(hakuna())return !strcmp(id,"audio.effects.simba.roar") || !strcmp(id,"audio.effects.simba.hurt") ||
        !strcmp(id,"audio.effects.simba.bounce") || !strcmp(id,"audio.effects.simba.roll") ||
        !strcmp(id,"audio.effects.world.bonus_bug");
    if(cant_wait())return !strcmp(id,"audio.effects.simba.roar") || !strcmp(id,"audio.effects.simba.hurt") ||
        !strcmp(id,"audio.effects.world.checkpoint") || !strcmp(id,"audio.effects.world.continue_token");
    if(exile())return !strcmp(id,"audio.effects.simba.roar") || !strcmp(id,"audio.effects.simba.hurt") ||
        !strcmp(id,"audio.effects.simba.bounce") || !strcmp(id,"audio.effects.simba.roll") ||
        !strcmp(id,"audio.effects.world.lizard") || !strcmp(id,"audio.effects.world.leaves") ||
        !strcmp(id,"audio.effects.world.health_bug") || !strcmp(id,"audio.effects.world.full_health_bug") ||
        !strcmp(id,"audio.effects.world.life_bug") || !strcmp(id,"audio.effects.world.bonus_bug") ||
        !strcmp(id,"audio.effects.world.harmful_bug") || !strcmp(id,"audio.effects.world.checkpoint");
    if(!TlkAudioGraveyardScene())return 0;
    static const char *ids[]={"audio.effects.simba.roar","audio.effects.simba.hurt","audio.effects.simba.bounce",
        "audio.effects.simba.roll","audio.effects.world.hyena_hurt","audio.effects.world.hyena_pant",
        "audio.effects.world.hyena_jump","audio.effects.world.hyena_taunt","audio.effects.world.bonus_bug",
        "audio.effects.world.checkpoint","audio.effects.world.continue_token","audio.effects.world.health_bug",
        "audio.effects.world.full_health_bug","audio.effects.world.life_bug","audio.effects.world.roar_bug",
        "audio.effects.world.harmful_bug"};
    for(unsigned i=0;i<sizeof ids/sizeof *ids;i++)if(!strcmp(id,ids[i]))return 1;
    return 0;
}
static void scar_jump_entry(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc6653a || !pride_rock() || word(0x2000)!=0xffff || cpu->PB!=0xc6 ||
       cpu->DB!=0x7e || word(0xa68c)!=(unsigned short)(cpu->D+0x2a) || cpu->m_flag || cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x68),desc=address(actor+4);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       (desc!=0xc585e8 && desc!=0xc585f4 && desc!=0xc58600) ||
       address(actor+48)!=0xc664e0 || word(actor+46))return;
    /* Native C66538 has just installed phase0 and animation C240B7.
     * Original 1B16D8 installs the paired1569D4 and requests FM96 once. */
    unsigned selected=TlkResourcesUseMd("audio.effects.world.scar.attack");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    if(emitted){TlkMdSoundCommand(2,96);effect_tail();}
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_SCAR_JUMP_AUDIO_TRACE");if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,descriptor,action,selected,emitted\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%06x,%06x,%u,%u\n",snes_frame_counter+1,pc,actor,desc,address(actor+48),selected,emitted);fflush(trace);}
}
/* The original player stream calls1CAF9A after its three blank operands,
 * then1CAFB0 after31 updates at the last drawing. Source4329 proves the same
 * first45 drawings/durations; retain native movement and scene completion. */
static int exile_exit_opcode(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || !exile() || !TlkMdSoundReady())return 0;
    unsigned actor=word(0x68),caller=music_caller(cpu);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc587a4 || address(actor+48)!=0xc1a651 ||
       !((cpu->X==1 && caller==0xc1a6e3) || (cpu->X==2 && caller==0xc1a6fe)))return 0;
    int fx=TlkResourcesUseMd("audio.effects.world.simbas_exile.exit") && TlkInterlevelDataCliffReady();
    if(cpu->X==1 && !exile_exit_age && (fx || TlkResourcesUseMd("audio.music.simbas_exile.track")))exile_exit_age=1;
    if(fx && word(0x1ff96)){cpu->A=0;return 1;}
    return 0;
}
static void exile_exit_audio_frame(void) {
    int owner=exile() && address(0xb217)==0xc5858a && address(0xb243)==0xc1a4c8;
    if(!owner){
        /* A shorter native outro may end during the delay to sample2. Keep
         * the selected MD sequence as a bounded audio tail, independently
         * of gameplay; an actual Start skip cancels it. */
        exile_exit_age=0;
        if(!exile_exit_fx || exile_exit_phase<2 || (word(0x62)&0x1000)){
            if(exile_exit_fx && TlkMdSoundReady())TlkMdSoundInterlevelStop();
            exile_exit_phase=exile_exit_delay=exile_exit_fx=0;return;
        }
    }
    if(word(0xa89) || !TlkMdSoundReady())return;
    if(exile_exit_age && exile_exit_age<=49){
        if(TlkResourcesUseMd("audio.music.simbas_exile.track") && word(0x1ff94) && music_active){
            if(exile_exit_age<=40){TlkMdSoundCommand(9,exile_exit_age);TlkMdSoundCommand(10,exile_exit_age);}
            if(exile_exit_age==41){
                TlkMdSoundCommand(9,127);TlkMdSoundCommand(10,127);TlkMdSoundCommand(1,0);
                /* Keep ownership of the selected silent score, preventing a
                 * native song or an automatic MD restart during the outro. */
            }
            if(exile_exit_age==49){TlkMdSoundCommand(9,0);TlkMdSoundCommand(10,0);}
        }
        if(exile_exit_age<49)exile_exit_age++;
        else exile_exit_age=50;
    }
    if(!word(0x1ff96) || !TlkResourcesUseMd("audio.effects.world.simbas_exile.exit") ||
       !TlkInterlevelDataCliffReady())return;
    unsigned draw=word(0xb21f),pose=draw>=0x8000 && draw<=0xffe8?address(draw+10):0;
    if(!exile_exit_phase && pose==0xc5f682){TlkMdSoundExileExitSample(0);fx_tail=120;exile_exit_fx=1;exile_exit_phase=1;}
    else if(exile_exit_phase==1 && pose==0xc5fa10){exile_exit_phase=2;exile_exit_delay=31;}
    else if(exile_exit_phase==2 && exile_exit_delay && !--exile_exit_delay){TlkMdSoundExileExitSample(1);fx_tail=120;exile_exit_fx=1;exile_exit_phase=3;}
}
#include "tlk_toss_audio.inc"
#include "tlk_spider_audio.inc"
#include "tlk_spider_projectile_audio.inc"
#include "tlk_adult_swipe_audio.inc"
#include "tlk_adult_pounce_audio.inc"
#include "tlk_adult_landing_audio.inc"
#include "tlk_grapple_audio.inc"
#include "tlk_big_cat_audio.inc"
#include "tlk_big_cat_hit_audio.inc"
#include "tlk_destiny_boulder_audio.inc"
#include "tlk_stalactite_audio.inc"
#include "tlk_geyser_audio.inc"
#include "tlk_prepared_launch_audio.inc"
#include "tlk_prepared_leaper_defeat_audio.inc"
#include "tlk_lava_bubble_audio.inc"
#include "tlk_frog_audio.inc"
#include "tlk_hazard_death_audio.inc"
#include "tlk_shared_harmful_audio.inc"
#include "tlk_revival_audio.inc"
static void observe_inner(CpuState *cpu, uint32_t pc) {
    if(toss_audio_opcode(cpu,pc))return;
    if(spider_audio(cpu,pc))return;
    if(spider_projectile_audio(cpu,pc))return;
    if(adult_swipe_audio(cpu,pc))return;
    if(adult_pounce_audio(cpu,pc))return;
    if(adult_landing_thud_audio(cpu,pc))return;
    if(grapple_contact_audio(cpu,pc))return;
    if(pc==0xc37d25){grapple_entry(cpu,pc,0);return;}
    if(big_cat_audio(cpu,pc))return;
    if(big_cat_hit_audio(cpu,pc))return;
    if(destiny_boulder_audio(cpu,pc,0))return;
    if(stalactite_audio(cpu,pc))return;
    if(geyser_audio(cpu,pc,0))return;
    if(prepared_launch_audio(cpu,pc))return;
    if(prepared_leaper_defeat_audio(cpu,pc))return;
    if(lava_bubble_audio(cpu,pc))return;
    if(pc==0xc63f64){stalactite_entry(cpu,pc,0);return;}
    if(pc==0xc5d241){big_cat_entry(cpu,pc,0);return;}
    if(frog_attack_audio(cpu,pc))return;
    if(hazard_death_audio(cpu,pc))return;
    if(shared_harmful_audio(cpu,pc))return;
    if(revival_voice_audio(cpu,pc))return;
    if(pc==0xc46bd7 || pc==0xc46d4c || pc==0xc46c88 || pc==0xc46ccf || pc==0xc07889){sound_test_opcode(cpu,pc);return;}
    if(coconut_audio(cpu,pc))return;
    if(gorilla_grab_audio(cpu,pc))return;
    if(gorilla_attack_audio(cpu,pc))return;
    if(gorilla_jump_audio(cpu,pc))return;
    if(gorilla_defeat_audio(cpu,pc))return;
    if(pc==0xc6653a){scar_jump_entry(cpu,pc);return;}
    if((pc>=0xc67721 && pc<=0xc679f3) && (pc>>16)==0xc6){postfight_timing_pre(cpu,pc+3);return;}
    if(pc==0xc37a32){scar_finish_entry(cpu,0xc37a34);return;}
    graveyard_opcode(cpu,pc,0);
    if(pc==0xc22c2c && destiny() && cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag &&
       cpu->X==0x36 && music_caller(cpu)==0xc011c2) {
        unsigned actor=word(0x68);
        /* Original MD111F10/1ADAA6 plays FM122 at the opening animation's
         * marker3. Native C586FE/C01147 reaches the corresponding opening
         * cue at marker1, four animation updates later. Keep native animation
         * and gate logic; replace only its sound at this ordinary event. */
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           cw_descriptor(actor)==0xc586fe && address(actor+48)==0xffffff && word(actor+46)==1){
            unsigned selected=TlkResourcesUseMd("audio.effects.world.simbas_destiny.arena_gate"),emitted=0;
            if(selected && word(0x1ff96) && TlkMdSoundReady()){
                cpu->A=0;TlkMdSoundCommand(2,122);effect_tail();emitted=1;
            }
            static FILE *log;static int opened;
            if(!opened){opened=1;const char *path=getenv("TLK_ARENA_GATE_AUDIO_TRACE");if(path)log=fopen(path,"w");
                if(log)fputs("field,actor,descriptor,phase,selected,emitted\n",log);}
            if(log){fprintf(log,"%u,%04x,c586fe,1,%u,%u\n",snes_frame_counter+1,actor,selected,emitted);fflush(log);}
            if(emitted)return;
        }
    }
    if(pc==0xc22c2c && word(0x1ff9e)>=6 && word(0x1ff9e)<=9){
        static FILE *owners;static int opened;
        if(!opened){opened=1;const char *path=getenv("TLK_LATE_AUDIO_CONTEXT_TRACE");if(path){owners=fopen(path,"w");if(owners)fputs("field,scene,caller,event,parameter,actor,descriptor,action,player_action,db,m8,x8\n",owners);}}
        if(owners){unsigned actor=word(0x68);fprintf(owners,"%u,%06x,%06x,%u,%u,%04x,%06x,%06x,%06x,%u,%u,%u\n",snes_frame_counter+1,address(0xdf),music_caller(cpu),cpu->X,cpu->A,actor,address(actor+4),address(actor+48),address(0xb243),cpu->DB,cpu->m_flag,cpu->x_flag);fflush(owners);}
    }
    if(pc==0xc22c2c && pride_rock() && word(0x68)==0xb213 && address(0xb243)==0xc378e9 &&
       cpu->X==54 && music_caller(cpu)==0xc37ac8 && cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag){
        unsigned selected=TlkResourcesUseMd(victory_voice_sources[0]);
        victory_voice_log("finish_late",0xc37ac8,selected,0);
        if(selected && scar_finish_context() && word(0x1ff96) && TlkMdSoundReady()){cpu->A=0;return;}
    }
    if(pc==0xc22c2c && finale_scene() && word(0x68)==0xb213 && cpu->X==5 &&
       cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D){
        unsigned caller=music_caller(cpu),phase=word(0xb23f);
        if((caller==0xc6777f && phase==4) || (caller==0xc67990 && phase==12) ||
           (caller==0xc67a51 && phase==16)){
            unsigned selected=TlkResourcesUseMd(victory_voice_sources[1]);
            unsigned emitted=selected && phase!=16 && word(0x1ff96) && TlkMdSoundReady();
            /* Original1B2828 has voices at phases4 and12, then exits after14.
             * Native16 is an extra voice. Keep its independently owned scene
             * animation/clock, but silence it when MD owns these sounds. */
            if(emitted){TlkMdSoundPcm(11,96);effect_tail();}
            victory_voice_log("postfight",caller,selected,emitted);
            if(selected && word(0x1ff96) && TlkMdSoundReady()){cpu->A=0;return;}
        }
    }
    if(pc==0xc22c2c && adult_roar_context() && cpu->X==8 && music_caller(cpu)==0xc4707a &&
       cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D && word(0x1ff96)){
        unsigned selected=TlkResourcesUseMd("audio.effects.simba.adult_roar");
        adult_roar_log("native_late",selected);
        /* Original MD07DA7A is RTS. Keep the original native call/queue
         * scheduling, but silence this late voice when MD owns the pulse. */
        if(selected && TlkMdSoundReady()){cpu->A=0;return;}
    }
    if(pc==0xc22c2c && address(0xdf)==0xc007db && cpu->X==0){
        static FILE *probe;static int probed;
        if(!probed){const char *path=getenv("TLK_FINALE_CONTEXT_TRACE");probed=1;if(path)probe=fopen(path,"w");
            if(probe)fputs("field,caller,actor,descriptor,action,db,m,x,parameter,player_action\n",probe);}
        if(probe){unsigned actor=word(0x68);fprintf(probe,"%u,%06x,%04x,%06x,%06x,%02x,%u,%u,%04x,%06x\n",
            (unsigned)snes_frame_counter+1,music_caller(cpu),actor,address(actor+4),address(actor+0x30),
            cpu->DB,cpu->m_flag,cpu->x_flag,cpu->A,address(0xb243));fflush(probe);}
    }
    if(pc==0xc22c2c && finale_scene() && cpu->X==0 &&
       (cpu->A==0xe078 || cpu->A==0xe000) && cpu->DB==0 &&
       !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D){
        unsigned actor=word(0x68),caller=music_caller(cpu);
        if(caller==0xc0fb39 && actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           address(actor+4)==0xc58678 && address(actor+0x30)==0xc67def){
            /* Clock belongs to gameplay, including native/disabled music. */
            if(ending_timing_selected())ending_timing_epoch=(unsigned)snes_frame_counter+1;
            unsigned selected=TlkResourcesUseMd("audio.music.pride_rock.finale");
            static FILE *log;static int initialized;
            if(!initialized){const char *path=getenv("TLK_FINALE_AUDIO_TRACE");initialized=1;if(path)log=fopen(path,"w");
                if(log)fputs("field,caller,actor,scene,source_md,music_enabled\n",log);}
            if(log){fprintf(log,"%u,%06x,%04x,%06x,%u,%u\n",(unsigned)snes_frame_counter+1,
                caller,actor,address(0xdf),selected,word(0x1ff94));fflush(log);}
            if(selected && word(0x1ff94) && TlkMdSoundReady()){
                if(!music_active || music_track!=339){
                    TlkMdSoundCommand(1,339);music_track=339;music_scene=9;
                    music_active=1;pending_stop=0;
                }
                /* Original native Music Off still runs. Preserve separately
                 * owned native rain/roars while replacing only the score. */
                return;
            }
        }
    }
    if(pc==0xc22c2c && opening_timon_selected() && word(0x68)==0xb213 &&
       cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D &&
       cpu->X==1 && cpu->A==0xe078 && music_caller(cpu)==0xc47234 && word(0xb241)==2) {
        /* This black OBJ-only speech scene owns the complete native bus.
         * Keep its bank upload/queue/PCM untouched; select output only. */
        TlkAudioReset();
        if(word(0x1ff96)){TlkMdSoundOpeningTimonSample();fx_tail=120;}
        return;
    }
    if(pc==0xc22c2c && ending_owner() && word(0x68)==0xb213 &&
       cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && !cpu->_flag_D){
        unsigned caller=music_caller(cpu),sample=2,credits=0;
        if(ending_sunrise() && cpu->A==0xe078){
            if(cpu->X==1 && caller==0xc47514)sample=0;
            if(cpu->X==2 && caller==0xc4754a)sample=1;
        }
        if(ending_credits() && cpu->X==55 && caller==0xc475b8 &&
           (cpu->A==0x78 || !cpu->A))credits=1;
        if(sample<2 || credits){
            unsigned selected=TlkResourcesUseMd(credits?"audio.music.ending_credits":"audio.voices.ending");
            static FILE *log;static int initialized;
            if(!initialized){const char *path=getenv("TLK_ENDING_AUDIO_TRACE");initialized=1;if(path)log=fopen(path,"w");
                if(log)fputs("field,caller,scene,event,parameter,sample,credits,source_md\n",log);}
            if(log){fprintf(log,"%u,%06x,%06x,%u,%04x,%u,%u,%u\n",(unsigned)snes_frame_counter+1,
                caller,address(0xdf),cpu->X,cpu->A,sample,credits,selected);fflush(log);}
            /* The original MD339 tail has finished by these native speech
             * cues. Release only that score's ownership for either speech
             * choice, so native speech is never muted as background music. */
            if(sample<2 && finale_carry() && TlkMdSoundReady()){
                TlkMdSoundCommand(1,0);music_active=pending_stop=0;music_track=0;
            }
            if(selected && TlkMdSoundReady() && (credits || TlkInterlevelDataReady())){
                /* Preserve native bank loading, cue/counter/control flow and
                 * its saved request/return. Only speech uses a zero-volume
                 * native parameter. Credits keeps its native request intact;
                 * the scene's complete score is replaced in TlkAudioMix. */
                if(sample<2){
                    cpu->A=0;
                    TlkMdSoundCommand(1,0);TlkMdSoundInterlevelSample(sample);
                    music_active=pending_stop=0;music_track=0;fx_tail=120;
                }
                /* Credits starts through its real guest readiness below,
                 * including when native FX is off but music is enabled. */
                return;
            }
        }
    }
    if(pc==0xc22c2c && hunt_scene() && word(0x1ff96) && TlkMdSoundReady()) {
        unsigned actor=word(0x68),caller=music_caller(cpu),descriptor=cw_descriptor(actor),choice=HUNT_SOUND_COUNT,value=0;
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127)) {
            if(cpu->X==5 && caller==0xc580c6 && descriptor>=0xc58a11 && descriptor<=0xc58a65 &&
               !((descriptor-0xc58a11)%12) && address(actor+0x30)==0xc5805d){choice=HUNT_COLLECT;value=93;}
            else if(cpu->X==0x12 && (caller==0xc5565b || caller==0xc55a53) && descriptor==0xc58975){choice=HUNT_HURT;value=117;}
        }
        if(choice<HUNT_SOUND_COUNT) {
            unsigned selected=TlkResourcesUseMd(hunt_sources[choice]);
            static FILE *log;static int initialized;
            if(!initialized){const char *path=getenv("TLK_HUNT_AUDIO_TRACE");initialized=1;if(path)log=fopen(path,"w");
                if(log)fputs("field,caller,actor,descriptor,event,md_program,source_md\n",log);}
            if(log){fprintf(log,"%u,%06x,%04x,%06x,%u,%u,%u\n",(unsigned)snes_frame_counter+1,caller,actor,descriptor,cpu->X,value,selected);fflush(log);}
            if(selected){
                /* Suppress only this original native effect request. The
                 * original collision, count, damage and actor cleanup run. */
                /* This caller ends the round immediately. Release the old
                 * song's ownership without Music Off or a driver reset: both
                 * discard this effect. The next scene takes over the song. */
                if(choice==HUNT_HURT && caller==0xc55a53){music_active=pending_stop=0;music_track=0;}
                TlkMdSoundCommand(2,value);
                cpu->A=0;effect_tail();hunt_fx=1;return;
            }
        }
    }
    if(pc==0xc22c2c && word(0x1ff9e)==9 &&
       (address(0xdf)==0xc00549 || address(0xdf)==0xc007db) && word(0x1ff96) &&
       TlkMdSoundReady() && cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag &&
       cpu->X==55 && music_caller(cpu)==0xc2e6fd &&
       TlkResourcesUseMd("audio.effects.world.pride_rock_fire")) {
        unsigned actor=word(0x68);
        /* Original1565CA/1B3B2E emits FM166 at1B3B8A. Native C58618's
         * ordinary frame event is the corresponding fire pulse. */
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           address(actor+4)==0xc58618 && address(actor+48)==0xffffff){
            cpu->A=0;TlkMdSoundCommand(2,166);effect_tail();return;
        }
    }
    if(pc==0xc22c2c && pride_rock() && word(0x2000)==0xffff && word(0x1ff96) &&
       TlkMdSoundReady() && cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag &&
       cpu->X==0x3f && music_caller(cpu)==0xc666f7 &&
       TlkResourcesUseMd("audio.effects.world.scar.attack")) {
        unsigned actor=word(0x68);
        /* Original MD156918/1B1874 emits raw29 at1B18C4: PCM13/80.
         * The native summit attack is C58600/C66683, not an adult hyena.
         * Preserve the native attack stores, damage and event scheduling. */
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           address(actor+4)==0xc58600 && address(actor+48)==0xc66683){
            cpu->A=0;TlkMdSoundPcm(13,80);effect_tail();return;
        }
    }
    if(pc==0xc22c2c && late_adult() && word(0x2000)==0xffff && word(0x1ff96) && TlkMdSoundReady() &&
       cw_descriptor(word(0x68))==0xc58ecc) {
        unsigned caller=music_caller(cpu);const char *source=NULL;unsigned voice=0;
        /* Separate adult family: original1ADEAA/1ADEF0 reaction requests4;
         * original1AED00/1AEDCC attack voice requests PCM13. The same native
         * event sites are observed in both later scenes, not inferred from
         * the cub hyena's deliberately silent ordinary leap. */
        if(cpu->X==0x20 && caller==0xc1af34){source="audio.effects.world.adult_hyenas.reaction";voice=4;}
        if(cpu->X==0x3f && caller==0xc1be37){source="audio.effects.world.adult_hyenas.attack";voice=13;}
        if(cpu->X==0x1e &&
           ((caller==0xc1ace5 && address(word(0x68)+48)==0xc1abf6) ||
            (caller==0xc1ae0d && address(word(0x68)+48)==0xc1ad1e && word(word(0x68)+46)==2)) &&
           TlkResourcesUseMd("audio.effects.world.adult_hyenas.taunt")){
            /* The MD entry already owns this voice. Preserve native queue
             * scheduling with zero volume, without emitting a second taunt. */
            cpu->A=0;return;
        }
        if(cpu->X==0x1e && caller==0xc1b48b && address(word(0x68)+48)==0xc1b37f &&
           word(word(0x68)+46)==1 && TlkResourcesUseMd("audio.effects.world.adult_hyenas.leap")) {
            /* Original1AE3F4 phase1 launches silently. Attack PCM13 and both
             * taunts are different actions, not owners of this native cry. */
            cpu->A=0;return;
        }
        if(source && TlkResourcesUseMd(source)){
            cpu->A=0;
            /* MD attack encodes raw29 before2210: its table parameter80
             * survives normalization to sample13. Reaction4 uses96. */
            TlkMdSoundPcm(voice,voice==13?80:96);effect_tail();return;
        }
    }
    if(pc==0xc22c2c && be_prepared() && word(0x1ff96) && TlkMdSoundReady() &&
       cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && cpu->X==16 && music_caller(cpu)==0xc070cb &&
       TlkResourcesUseMd("audio.effects.world.be_prepared.rock_impact")) {
        unsigned actor=word(0x68);
        /* Native C06F5B phase1 lands, changes to phase2 and requests event16.
         * Original13FE04/1B0236 requests FM167 at the corresponding impact. */
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) &&
           address(actor+4)==0xc58780 && address(actor+48)==0xc06f5b && word(actor+46)==2){
            cpu->A=0;TlkMdSoundCommand(2,167);effect_tail();return;
        }
    }
    if(pc==0xc22c2c && exile() && word(0x1ff96) && TlkMdSoundReady() && cpu->X==0x22 &&
       TlkResourcesUseMd("audio.effects.world.simbas_exile.rocks")) {
        unsigned caller=music_caller(cpu),actor=word(0x68);
        /* Native C16941 controller, original MD1A5764: both original MD
         * rumble/impact sites1A5ADA/1A5B10 request FM165 through228A. */
        if((caller==0xc16c87 || caller==0xc16cc3) && actor>=0xb293 && actor<0xc213 && address(actor+4)==0xc58cbc) {
            cpu->A=0;TlkMdSoundCommand(2,165);effect_tail();return;
        }
    }
    if(pc==0xc22c2c && stampede() && word(0x1ff96) && TlkMdSoundReady()) {
        unsigned caller=music_caller(cpu);
        if(cpu->X==0x3c && caller==0xc45d30 && TlkResourcesUseMd("audio.effects.world.stampede.start")) {
            cpu->A=0;TlkMdSoundCommand(2,172);effect_tail();return;
        }
        if(cpu->X==0x12 && caller==0xc46296 && TlkResourcesUseMd("audio.effects.world.stampede.hurt")) {
            cpu->A=0;TlkMdSoundCommand(19,16);effect_tail();return;
        }
    }
    if (pc==0xc22c2c && trace) {
        unsigned sp=cpu->S;
        fprintf(trace,"%u,%04x,%04x,%04x,%04x,%04x,%04x,%04x,%04x,%04x,%04x,",frame,
                cpu->X,cpu->A,word(0x1ff9e),word(0xdf),word(0x1ff94),word(0x1ff96),
                word((sp+3)&65535),word((sp+5)&65535),word(0xb21b),word(0x68));
        for (unsigned n=1;n<=24;n++) fprintf(trace,"%02x",g_ram[(sp+n)&65535]);
        fprintf(trace,"\n");
    }
    if(exile_exit_opcode(cpu,pc))return;
    if(pc==0xc22c2c && prepared_scene() && word(0x1ff96) &&
       TlkResourcesUseMd("audio.effects.world.be_prepared.group_call")) {
        const uint16_t*r=TlkBePreparedGroupSoundRules();unsigned actor=word(0x68);
        if(r && prepared_actor(actor) && address(actor+48)==0xc38d65 &&
           cpu->X==r[TLK_BP_SOUND_NATIVE_EVENT] && music_caller(cpu)==0xc38e54 && TlkMdSoundReady()) {
            cpu->A=0;unsigned accepted=prepared_md_sound(r);
            prepared_sound_log(actor,1,r[TLK_BP_SOUND_NATIVE_EVENT],1,accepted);return;
        }
    }
    if (pc==0xc22c2c && game_over_scene() && TlkMdSoundReady()) {
        unsigned caller=music_caller(cpu);
        if(cpu->X==0) {
            if(caller==0xc08c06) {
                /* Native music-bank6 initialization; original MD1D692A uses
                 * program327 on this continue/game-over screen. Scene change
                 * discards old level/FX state regardless of the level source. */
                TlkAudioReset();
                if(TlkResourcesUseMd("audio.music.pride_game_over") && word(0x1ff94))start_music();
            } else stop_music();
        } else if(cpu->X==1 && caller==0xc08dc8)stop_music(); /* Continue accepted. */
        return;
    }
    if(pc==0xc22c2c && menu_effect_scene() && word(0x1ff96) && TlkMdSoundReady()) {
        unsigned caller=music_caller(cpu);
        for(unsigned i=0;i<MENU_CUE_COUNT;i++) {
            if(cpu->X!=menu_cues[i].event || caller!=menu_cues[i].caller ||
               !TlkResourcesUseMd(menu_cues[i].id))continue;
            if(!strcmp(menu_cues[i].id,"audio.effects.level_select") && !level_select_effect_owner())continue;
            /* Native queue/SPC work continues; verified voice ownership
             * removes only this selected effect at DSP output. */
            if(menu_cues[i].value) { TlkMdSoundCommand(2,menu_cues[i].value);fx_tail=120;menu_fx=1; }
            break;
        }
    }
    if (pc==0xc22c2c && cpu->X==0 && TlkMdSoundReady()) {
        unsigned caller=music_caller(cpu);
        unsigned real_retry=caller==0xc329fa && music_entry_seen && music_scene==word(0x1ff9e);
        if(death_scene() && caller==0xc329fa) {
            /* Original player initializer starts a fresh level/revival. */
            death_phase=0;
            if(!selected_music())stop_music();
        }
        if(death_scene() && caller==0xc08ab8) {
            /* Original health-death Music Off, after its native fade. */
            death_phase=death_phase?2:3;
            if(death_phase==3 || !md_death_music())stop_music();
        } else if(!death_phase && !ending_credits() && !finale_carry() && selected_music() && word(0x1ff94) &&
                  (!music_active || music_scene!=music_scene_id() || music_track!=scene_music() || real_retry)) {
            /* The native Music Off request also runs during level/player
             * initialization. The selected scene song may already be playing
             * from the frame boundary; do not rewind it at that same cue.
             * A later real player initialization is a death/retry and must
             * restart the song even when the same track survived the fall. */
            start_music();
        }
        if(caller==0xc329fa)music_entry_seen=1;
    }
    if(pc==0xc22c2c && cant_wait() && word(0x1ff96) && TlkMdSoundReady()) {
        unsigned actor=word(0x68);
        unsigned caller=((unsigned)g_ram[(cpu->S+8)&65535]<<16)|((word((cpu->S+6)&65535)+1)&65535);
        if(cpu->X==0x13 && ((caller==0xc55714 && TlkResourcesUseMd(cw_sources[CW_LIFE])) ||
           (caller==0xc559b8 && TlkResourcesUseMd(cw_sources[CW_BONUS])))) {
            cpu->A=0;TlkMdSoundCommand(19,15);cw_tail();return;
        }
        if(cpu->X==0x11 && caller==0xc2e99f && TlkResourcesUseMd(cw_sources[CW_RHINO]) && cw_actor(actor,0)) {
            cpu->A=0;TlkMdSoundCommand(2,106);cw_tail();return;
        }
        if(cpu->X==0xb && (caller==0xc44dee || caller==0xc452e3 || caller==0xc45556) &&
           TlkResourcesUseMd(cw_sources[CW_CONTACT]) && cw_actor(actor,1)) {
            cpu->A=0;TlkMdSoundCommand(2,119);cw_tail();return;
        }
        if(cpu->X==0x1a && caller==0xc45610 && TlkResourcesUseMd(cw_sources[CW_REACTION]) && cw_actor(actor,1)) {
            cpu->A=0;cw_reaction_remember(actor);cw_tail();return;
        }
    }
    if(pc==0xc22c2c && TlkAudioGraveyardScene() && word(0x1ff96) && TlkMdSoundReady()) {
        unsigned actor=word(0x68),descriptor=cw_descriptor(actor),choice=GY_SOUND_COUNT,value=0,selector=2;
        unsigned caller=music_caller(cpu);
        if(cpu->X==0x35 && caller==0xc19ab0 && GY_FAMILY(descriptor,gy_shake_descriptors))choice=GY_SHAKE;
        else if(cpu->X==0x35 && caller==0xc19f23 && GY_FAMILY(descriptor,gy_platform_descriptors))choice=GY_PLATFORM;
        /* MD1A3BBA requests FM105 when the separate breakable pile enters
         * its burst program; native C47AC2 emits the same semantic cue35. */
        else if(cpu->X==0x35 &&
                ((caller==0xc48411 && (descriptor==0xc58820 || descriptor==0xc5882c)) ||
                 (caller==0xc47ac6 && descriptor==0xc588d1)))
            {choice=GY_BREAK;value=105;}
        else if(cpu->X==0x1d && caller==0xc17986 && GY_FAMILY(descriptor,gy_vulture_descriptors))
            {choice=GY_VULTURE;selector=19;value=2;}
        else if(cpu->X==0x22 && caller==0xc2d248 && descriptor==0xc58d44)
            {choice=GY_PILLAR;value=171;}
        if(choice<GY_SOUND_COUNT && TlkResourcesUseMd(gy_sources[choice])) {
            cpu->A=0;
            if(value){TlkMdSoundCommand(selector,value);effect_tail();}
            return;
        }
    }
    if(pc==0xc22c2c && destiny() && word(0x1ff96) && TlkDestinyMonkeyDataReady() && TlkMdSoundReady()) {
        unsigned actor=word(0x68),caller=music_caller(cpu);
        if(actor>=0xb293 && actor<0xdc13 && !((actor-0xb213)&127) && address(actor+4)==0xc586d8) {
            if(cpu->X==26 && caller==0xc4d270 && TlkResourcesUseMd("audio.effects.world.simbas_destiny.monkey_movement")) {
                /* Original2210 maps semantic33 to PCM17; its priority is96. */
                unsigned cue=TlkDestinyMonkeyParameter(TLK_MONKEY_MOVE_CUE);
                if(cue>=48)cue-=16;if(cue>=16)cue-=16;
                cpu->A=0;TlkMdSoundCommand(19,cue);effect_tail();return;
            }
            if(cpu->X==63 && (caller==0xc4cf6a || caller==0xc4d0d0 || caller==0xc4d2b4) &&
               TlkResourcesUseMd("audio.effects.world.simbas_destiny.monkey_defeat")){cpu->A=0;return;}
        }
    }
    if (pc==0xc22c2c && (pride() || cant_wait() || TlkAudioGraveyardScene() || exile() || hakuna() || destiny() || late_adult() || shared_one_up_request(cpu,pc)) && word(0x1ff96) && TlkMdSoundReady())
        for (unsigned i=0;i<CUE_COUNT;i++) {
            /* The second-level extension is deliberate per cue. Other Pride
             * mappings keep their established scene scope. */
            if(!cue_in_scene(cues[i].id))continue;
            int simba=word(0x68)==0xb213;
            unsigned caller=((unsigned)g_ram[(cpu->S+8)&65535]<<16)|((word((cpu->S+6)&65535)+1)&65535);
            if (cpu->X!=cues[i].native_event || !TlkResourcesUseMd(cues[i].id) ||
                (cues[i].actor==1 && !simba) || (cues[i].actor==2 && simba) ||
                (cues[i].caller && caller!=cues[i].caller)) continue;
            if(TlkAudioGraveyardScene() && !strncmp(cues[i].id,"audio.effects.world.hyena_",26) &&
               !TlkGraveyardHyenaDescriptor(cw_descriptor(word(0x68))))continue;
            int one_up=!strcmp(cues[i].id,"audio.effects.world.one_up");
            if(caller==0xc55872 && !strcmp(cues[i].id,"audio.effects.world.checkpoint")) {
                unsigned actor=word(0x68);
                if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
                   (cw_descriptor(actor)!=0xc588b2 && cw_descriptor(actor)!=0xc588be))continue;
            }
            /* King has an existing explicit override; its native choice must
             * not fall through into the shared MD source. */
            if(one_up && (cant_wait() || !shared_one_up_request(cpu,pc)))continue;
            int bonus=!strcmp(cues[i].id,"audio.effects.world.bonus_bug");
            if(bonus){
                /* King's first bug already has its dedicated CW_BONUS choice.
                 * Its native setting must not fall through to this shared leaf. */
                if(cant_wait() && caller==0xc559b8)continue;
                unsigned actor=word(0x68),expected=caller==0xc559b8?0xc586b4:0xc586c0;
                if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
                   cw_descriptor(actor)!=expected)continue;
            }
            if(cues[i].actor==3) {
                unsigned actor=word(0x68),draw=actor<=0xff80?word(actor+12):0;
                if(draw<0x8000 || draw>0xffe8)continue;
                /* The shared Sun owns this cue, independent of graphics.
                 * Exact ordinary actor/action, reciprocal live draw and pose. */
                int owned=continue_world_scene() && actor>=0xb293 && actor<0xdc13 &&
                    !((actor-0xb213)&127) && cw_descriptor(actor)==0xc586cc &&
                    address(actor+0x30)==0xc558ff && word(draw+4)==actor+8 &&
                    !(g_ram[draw+9]&0x40) && TlkContinueTokenPose(address(draw+10));
                if(!owned)continue;
            }
            unsigned selector=cues[i].selector,value=cues[i].value;
            /* Original 18FDD8/18FE78 and Sun18FD02 test scene7: cub pickups
             * use PCM15, adult pickups use FM114. Collection stays native. */
            if((bonus || one_up || cues[i].actor==3) && word(0x1ff9e)>=6 && word(0x1ff9e)<=9){selector=2;value=114;}
            {
                static FILE *log;static int opened;
                if(!opened){opened=1;const char *path=getenv("TLK_SHARED_PICKUP_AUDIO_TRACE");if(path)log=fopen(path,"w");
                    if(log)fputs("field,level,actor,descriptor,caller,source,selector,value\n",log);}
                if(log && (cpu->X==0x13 || !strcmp(cues[i].id,"audio.effects.world.harmful_bug"))){
                    unsigned actor=word(0x68);fprintf(log,"%u,%u,%04x,%06x,%06x,%s,%u,%u\n",snes_frame_counter+1,
                        word(0x1ff9e),actor,actor<=0xff80?address(actor+4):0,caller,cues[i].id,selector,value);fflush(log);}
            }
            if(!pride() || !TLK_NATIVE_AUDIO_OWNER_AVAILABLE || strcmp(cues[i].id,"audio.effects.simba.bounce"))cpu->A=0;
            if (selector) { TlkMdSoundCommand(selector,value);effect_tail(); }
            break;
        }
}
/* Requests retained here can be muted later by a native voice owner.
 * Keep them as unclassified evidence, never assert they are audible fallbacks. */
static void observe(CpuState *cpu,uint32_t pc) {
    int audit=TlkFallbackEnabled() && pc==0xc22c2c;
    unsigned actor=0,caller=0,selector=0,parameter=0;
    if(audit){actor=word(0x68);caller=music_caller(cpu);selector=cpu->X;parameter=cpu->A;
        TlkFallbackContext((unsigned)snes_frame_counter+1,word(0x1ff9e),address(0xdf));}
    observe_inner(cpu,pc);
    if(audit && parameter && cpu->A && TlkResourcesGroupMd("audio"))
        TlkFallbackRecord("unclassified_audio",selector?"audio.effects":"audio.music",
            "native_request_retained_before_voice_filter",actor,caller,(selector<<16)|(parameter&65535),1);
}
static void pre(CpuState *cpu, uint32_t pc) { (void)pc; observe(cpu,0xc22c2c); }
static void graveyard_pre(CpuState *cpu,uint32_t pc) {graveyard_opcode(cpu,pc,1);}
static void install_graveyard_observers(void) {
    interp_bridge_add_pre_opcode_hook(0xc19ac7,graveyard_pre);
    interp_bridge_add_pre_opcode_hook(0xc19f87,graveyard_pre);
    interp_bridge_add_pre_opcode_hook(0xc22cbf,graveyard_pre);
}
void TlkAudioInstall(void) {
    ending_timing_install();
    TlkNativeAudioOwnerInstall();
    TlkHyenaAudioInstall(0);
    TlkLizardAudioInstall(0);
    TlkPickupAudioInstall(0);
    TlkLedgeAudioInstall(0);
    if(TLK_BATTLE_MUSIC_TRIGGER_AVAILABLE) {
        interp_bridge_add_pre_opcode_hook(0xc14453,TlkAudioHyenaBattleJump);
        interp_bridge_add_pre_opcode_hook(0xc144d8,TlkAudioHyenaBattleJump);
    }
    const char *path=getenv("TLK_AUDIO_EVENTS");
    if (path && !trace) trace=fopen(path,"w");
    if (trace) fprintf(trace,"frame,event,parameter,level,descriptor,music_enabled,fx_enabled,return0,return1,simba_x,actor,stack\n");
    path=getenv("TLK_AUDIO_STEMS");
    if (path && !stems) stems=fopen(path,"w");
    if (stems) fprintf(stems,"frame,samples,native_peak,md_peak\n");
    music_choice=music_mask();
    for (unsigned i=0;i<CUE_COUNT;i++) cue_choices[i]=TlkResourcesUseMd(cues[i].id);
    for(unsigned i=0;i<CW_SOUND_COUNT;i++)cw_choices[i]=TlkResourcesUseMd(cw_sources[i]);
    for(unsigned i=0;i<GY_SOUND_COUNT;i++)gy_choices[i]=TlkResourcesUseMd(gy_sources[i]);
    for(unsigned i=0;i<HUNT_SOUND_COUNT;i++)hunt_choices[i]=TlkResourcesUseMd(hunt_sources[i]);
    for(unsigned i=0;i<MENU_CUE_COUNT;i++)menu_cue_choices[i]=TlkResourcesUseMd(menu_cues[i].id);
    for(unsigned i=0;i<TRIGGER_COUNT;i++)trigger_choices[i]=TlkResourcesUseMd(trigger_sources[i]);
    for(unsigned i=0;i<3;i++)monkey_choices[i]=TlkResourcesUseMd(monkey_sources[i]);
    adult_roar_choice=TlkResourcesUseMd("audio.effects.simba.adult_roar");
    scar_attack_choice=TlkResourcesUseMd("audio.effects.world.scar.attack");
    pride_fire_choice=TlkResourcesUseMd("audio.effects.world.pride_rock_fire");
    prepared_rock_choice=TlkResourcesUseMd("audio.effects.world.be_prepared.rock_impact");
    arena_gate_choice=TlkResourcesUseMd("audio.effects.world.simbas_destiny.arena_gate");
    adult_taunt_choice=TlkResourcesUseMd("audio.effects.world.adult_hyenas.taunt");
    for(unsigned i=0;i<2;i++)victory_voice_choices[i]=TlkResourcesUseMd(victory_voice_sources[i]);
    g_tlk_audio_pc_hook=observe;
    /* Both paths observe immediately after PHA at C22C2C. */
    interp_bridge_add_pre_opcode_hook(0xc22c2d,pre);
    interp_bridge_add_pre_opcode_hook(0xc545fb,observe);
    interp_bridge_add_pre_opcode_hook(0xc37a34,scar_finish_entry);
    interp_bridge_add_pre_opcode_hook(0xc6653a,scar_jump_entry);
    install_graveyard_observers();
    interp_bridge_add_pre_opcode_hook(0xc63f64,stalactite_entry_pre);
    interp_bridge_add_pre_opcode_hook(0xc22cbf,destiny_boulder_pre);
    interp_bridge_add_pre_opcode_hook(0xc22cbf,geyser_audio_pre);
    interp_bridge_add_pre_opcode_hook(0xc37d25,grapple_entry_pre);
    interp_bridge_add_pre_opcode_hook(0xc5d241,big_cat_entry_pre);
    static const uint32_t sound_pcs[]={0xc46bd7,0xc46d4c,0xc46c88,0xc46ccf,0xc07889};
    for(unsigned i=0;i<sizeof sound_pcs/sizeof *sound_pcs;i++)interp_bridge_add_pre_opcode_hook(sound_pcs[i],sound_test_opcode);
}
void TlkAudioFrame(unsigned value) {
    static FILE *scar_trace;static int scar_trace_open;
    if(!scar_trace_open){scar_trace_open=1;const char*p=getenv("TLK_SCAR_ACTION_TRACE");if(p)scar_trace=fopen(p,"w");
        if(scar_trace)fputs("field,actor,descriptor,action,animation,pose,x,y,phase\n",scar_trace);}
    if(scar_trace && pride_rock())for(unsigned a=0xb293;a<0xdc13;a+=128){
        unsigned d=address(a+4),draw=word(a+12);
        if((d==0xc585e8 || d==0xc585f4 || d==0xc58600) && draw>=0x8000 && draw<=0xffe8 && word(draw+4)==a+8)
            fprintf(scar_trace,"%u,%04x,%06x,%06x,%06x,%06x,%u,%u,%u\n",value,a,d,address(a+48),address(a+14),address(draw+10),word(a+8),word(a+10),word(a+46));
    }
    ending_timing_frame();
    TlkNativeAudioOwnerInstall();
    frame=value;
    if(opening_timon_selected()) {
        if(music_active)stop_music();
        if(fx_tail)fx_tail--;
        return;
    }
    if(sound_test_scene() && TlkMdSoundReady()){sound_test_frame();return;}
    if(TlkBonusResultSceneActive()){
        TlkBonusResultSceneAudioFrame();
        TlkBonusResultScene *s=&tlk_bonus_result_scene;
        if(!s->native_stopped && !TlkBonusResultSceneNativeGain() && word(0x1fbf)==0xffff && word(0x1f6d)<=0x48){
            /* Original Music Off packet, through the existing unlocked queue.
             * The selected native song fades at output before this stop. */
            unsigned at=0x1f6f+word(0x1f6d),next=word(0x1f6d)+4;
            g_ram[at]=1;g_ram[at+1]=0x82;g_ram[at+2]=0xe0;g_ram[at+3]=0;
            g_ram[0x1f6d]=next;g_ram[0x1f6e]=next>>8;s->native_stopped=1;
        }
        return;
    }
    if(TlkInterlevelSceneAudioSelected()){TlkInterlevelSceneAudioFrame();return;}
    if(ending_speech_selected()){
        if(music_active && !finale_carry())stop_music();
        if(fx_tail)fx_tail--;
        return;
    }
    if(!pride() || word(0xdf)!=0x80d)battle_ready=0;
    TlkHyenaAudioInstall(value);
    TlkLizardAudioInstall(value);
    TlkPickupAudioInstall(value);
    TlkLedgeAudioInstall(value);
    interp_bridge_add_pre_opcode_hook(0xc22c2d,pre);
    interp_bridge_add_pre_opcode_hook(0xc545fb,observe);
    install_graveyard_observers();
    interp_bridge_add_pre_opcode_hook(0xc63f64,stalactite_entry_pre);
    interp_bridge_add_pre_opcode_hook(0xc22cbf,destiny_boulder_pre);
    interp_bridge_add_pre_opcode_hook(0xc22cbf,geyser_audio_pre);
    interp_bridge_add_pre_opcode_hook(0xc37d25,grapple_entry_pre);
    interp_bridge_add_pre_opcode_hook(0xc5d241,big_cat_entry_pre);
    if (fx_tail && !word(0x0a89)) fx_tail--;
    /* Only menu-owned tails may survive in the title scene. Gameplay tails
     * still end there, and menu effects end when leaving their scene. */
    if(menu_fx && !menu_effect_scene())TlkAudioReset();
    if(cant_wait_fx && !cant_wait())TlkAudioReset();
    if(graveyard_fx && !TlkAudioGraveyardScene())TlkAudioReset();
    /* A harmful Hunt bug ends the round in the same guest field. Retain its
     * bounded effect tail through the outgoing scene, just as the native SPC
     * keeps sounding; changing music must not reset that effect's driver. */
    if(hunt_fx && !fx_tail)hunt_fx=0;
    if(exile_exit_fx && !fx_tail)exile_exit_fx=0;
    if(prepared_fx && !fx_tail)prepared_fx=0;
    if(graveyard_fx && TlkAudioGraveyardScene() && word(0x1ff96) &&
       TlkResourcesUseMd(gy_sources[GY_PILLAR]) && graveyard_pillar_active())fx_tail=120;
    cw_reaction_frame();
    if(!death_scene())death_phase=0;
    if(!death_phase && health_death()) {
        death_phase=md_death_music()?2:1;
        if(death_phase==2 && word(0x1ff94) && TlkMdSoundReady())start_music();
    }
    if ((music_active && (!selected_music() || music_scene!=music_scene_id())) ||
        (!pride() && !next_scene() && !ending_credits() && !ending_sunrise() && !finale_scene() && !finale_carry() && !(cant_wait_fx && cant_wait()) && !(graveyard_fx && TlkAudioGraveyardScene()) && !hunt_fx && !prepared_fx && !exile_exit_fx && !(menu_fx && menu_effect_scene()) && fx_tail)) {
        if(title_music_scene() || death_scene() || hunt_fx || prepared_fx || exile_exit_fx)stop_music();else TlkAudioReset();
    }
    if (!death_scene() && !ending_sunrise() && !finale_scene() && !hunt_fx && !prepared_fx && !exile_exit_fx && !(menu_fx && menu_effect_scene()) && !scene_music()) {
        if (music_active || fx_tail) TlkAudioReset();
    }
    else if (!(hunt_fx && address(0xb243)==0xc580df) &&
             (!music_active || (ending_credits() && music_track!=61) ||
             (TLK_BATTLE_MUSIC_TRIGGER_AVAILABLE && battle_ready &&
             scene_music()==134 && music_track!=134)) && selected_music() && word(0x1ff94) && TlkMdSoundReady()) {
        start_music();
    }
    /* Pride music is removed at DSP output. Leave the original queue and
     * sound driver running: injecting Music Off changes gameplay scheduling. */
    /* Hunt's native music uses echo. Its original E0 Music Off command
     * below removes that song/echo input while leaving native FX intact;
     * dry-only DSP ownership filtering is insufficient in those rounds. */
    if (pending_stop && (death_scene() || game_over_scene() || (bonus_scene() && word(0x1ff9e)==10))) pending_stop=0;
    if (music_active && pending_stop && word(0x1fbf)==0xffff && word(0x1f6d)<=0x48) {
        /* Same four-byte queue packet emitted by C21D4A for the Options
         * Music Off command: C218FD(X=82,Y=E0,A=0). Publish between frames,
         * when the guest producer is unlocked; the original SPC driver
         * consumes it normally. Music's priority group stops, FX stay active. */
        unsigned at=0x1f6f+word(0x1f6d);
        g_ram[at]=1;g_ram[at+1]=0x82;g_ram[at+2]=0xe0;g_ram[at+3]=0;
        unsigned next=word(0x1f6d)+4;g_ram[0x1f6d]=(uint8_t)next;g_ram[0x1f6e]=(uint8_t)(next>>8);
        pending_stop=0;
    }
    exile_exit_audio_frame();
    if (trace) fflush(trace);
}
void TlkAudioReset(void) { exile_exit_fx=0;exile_exit_age=exile_exit_phase=exile_exit_delay=0;music_active=pending_stop=fx_tail=menu_fx=cant_wait_fx=graveyard_fx=hunt_fx=prepared_fx=0;cw_reaction_count=0;music_track=death_phase=battle_ready=music_entry_seen=0;TlkMdSoundRestart(); }
int TlkAudioProfileChanged(void) {
    int choice=music_mask();
    int exit_choice=TlkResourcesUseMd("audio.effects.world.simbas_exile.exit");
    int group_choice=TlkResourcesUseMd("audio.effects.world.be_prepared.group_call");
    int changed=choice!=music_choice || group_choice!=prepared_choice;prepared_choice=group_choice;
    int spider=TlkResourcesUseMd("audio.effects.world.hakuna.spider");
    changed|=spider!=spider_choice;spider_choice=spider;
    int spider_projectile=TlkResourcesUseMd("audio.effects.world.hakuna.spider_projectile");
    changed|=spider_projectile!=spider_projectile_choice;spider_projectile_choice=spider_projectile;
    int adult_swipe=TlkResourcesUseMd("audio.effects.simba.adult_swipe");
    changed|=adult_swipe!=adult_swipe_choice;adult_swipe_choice=adult_swipe;
    int adult_pounce=TlkResourcesUseMd("audio.effects.simba.adult_pounce");
    changed|=adult_pounce!=adult_pounce_choice;adult_pounce_choice=adult_pounce;
    int grapple_contact=TlkResourcesUseMd("audio.effects.simba.grapple_contact");
    changed|=grapple_contact!=grapple_contact_choice;grapple_contact_choice=grapple_contact;
    int big_cat=TlkResourcesUseMd("audio.effects.world.big_cats");
    changed|=big_cat!=big_cat_choice;big_cat_choice=big_cat;
    int big_cat_hit=TlkResourcesUseMd("audio.effects.world.big_cat_hit");
    changed|=big_cat_hit!=big_cat_hit_choice;big_cat_hit_choice=big_cat_hit;
    int destiny_boulder=TlkResourcesUseMd("audio.effects.world.simbas_destiny.boulders");
    changed|=destiny_boulder!=destiny_boulder_choice;destiny_boulder_choice=destiny_boulder;
    int stalactite=TlkResourcesUseMd("audio.effects.world.be_prepared.stalactites");
    changed|=stalactite!=stalactite_choice;stalactite_choice=stalactite;
    int geyser_audio_source=TlkResourcesUseMd("audio.effects.world.be_prepared.geysers");
    changed|=geyser_audio_source!=geyser_audio_choice;geyser_audio_choice=geyser_audio_source;
    int prepared_launch=TlkResourcesUseMd("audio.effects.world.be_prepared.exit_launch");
    changed|=prepared_launch!=prepared_launch_choice;prepared_launch_choice=prepared_launch;
    int leaper_defeat=TlkResourcesUseMd("audio.effects.world.be_prepared.leaper_defeat");
    changed|=leaper_defeat!=prepared_leaper_defeat_choice;prepared_leaper_defeat_choice=leaper_defeat;
    int lava_bubble=TlkResourcesUseMd("audio.effects.world.lava_bubbles");
    changed|=lava_bubble!=lava_bubble_choice;lava_bubble_choice=lava_bubble;
    int frog_attack=TlkResourcesUseMd("audio.effects.world.hakuna.frog_attack");
    changed|=frog_attack!=frog_attack_choice;frog_attack_choice=frog_attack;
    int hazard_death=TlkResourcesUseMd("audio.effects.simba.hazard_death");
    changed|=hazard_death!=hazard_death_choice;hazard_death_choice=hazard_death;
    int revival_voice=TlkResourcesUseMd("audio.effects.simba.revival_roar");
    changed|=revival_voice!=revival_voice_choice;revival_voice_choice=revival_voice;
    changed|=exit_choice!=exile_exit_choice;exile_exit_choice=exit_choice;
    int coconut_bounce=TlkResourcesUseMd("audio.effects.world.hakuna.coconut_bounce");
    int coconut_break=TlkResourcesUseMd("audio.effects.world.hakuna.coconut_break");
    changed|=coconut_bounce!=coconut_bounce_choice || coconut_break!=coconut_break_choice;
    coconut_bounce_choice=coconut_bounce;coconut_break_choice=coconut_break;
    int gorilla_grab=TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_grab");
    changed|=gorilla_grab!=gorilla_grab_choice;gorilla_grab_choice=gorilla_grab;
    int gorilla_attack=TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_attack");
    changed|=gorilla_attack!=gorilla_attack_choice;gorilla_attack_choice=gorilla_attack;
    int gorilla_jump=TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_jump");
    changed|=gorilla_jump!=gorilla_jump_choice;gorilla_jump_choice=gorilla_jump;
    int gorilla_choice=TlkResourcesUseMd("audio.effects.world.hakuna.gorilla_defeat");
    changed|=gorilla_choice!=gorilla_defeat_choice;gorilla_defeat_choice=gorilla_choice;
    int adult_choice=TlkResourcesUseMd("audio.effects.simba.adult_roar");
    changed|=adult_choice!=adult_roar_choice;adult_roar_choice=adult_choice;
    int scar_choice=TlkResourcesUseMd("audio.effects.world.scar.attack");
    changed|=scar_choice!=scar_attack_choice;scar_attack_choice=scar_choice;
    int fire_choice=TlkResourcesUseMd("audio.effects.world.pride_rock_fire");
    changed|=fire_choice!=pride_fire_choice;pride_fire_choice=fire_choice;
    int rock_choice=TlkResourcesUseMd("audio.effects.world.be_prepared.rock_impact");
    changed|=rock_choice!=prepared_rock_choice;prepared_rock_choice=rock_choice;
    int gate_choice=TlkResourcesUseMd("audio.effects.world.simbas_destiny.arena_gate");
    changed|=gate_choice!=arena_gate_choice;arena_gate_choice=gate_choice;
    int taunt_choice=TlkResourcesUseMd("audio.effects.world.adult_hyenas.taunt");
    changed|=taunt_choice!=adult_taunt_choice;adult_taunt_choice=taunt_choice;
    for(unsigned i=0;i<2;i++){int source=TlkResourcesUseMd(victory_voice_sources[i]);changed|=source!=victory_voice_choices[i];victory_voice_choices[i]=source;}
    for (unsigned i=0;i<CUE_COUNT;i++) {
        int source=TlkResourcesUseMd(cues[i].id);changed|=source!=cue_choices[i];cue_choices[i]=source;
    }
    for(unsigned i=0;i<CW_SOUND_COUNT;i++) {
        int source=TlkResourcesUseMd(cw_sources[i]);changed|=source!=cw_choices[i];cw_choices[i]=source;
    }
    for(unsigned i=0;i<GY_SOUND_COUNT;i++) {
        int source=TlkResourcesUseMd(gy_sources[i]);changed|=source!=gy_choices[i];gy_choices[i]=source;
    }
    for(unsigned i=0;i<HUNT_SOUND_COUNT;i++) {
        int source=TlkResourcesUseMd(hunt_sources[i]);changed|=source!=hunt_choices[i];hunt_choices[i]=source;
    }
    for(unsigned i=0;i<MENU_CUE_COUNT;i++) {
        int source=TlkResourcesUseMd(menu_cues[i].id);changed|=source!=menu_cue_choices[i];menu_cue_choices[i]=source;
    }
    for(unsigned i=0;i<TRIGGER_COUNT;i++) {
        int source=TlkResourcesUseMd(trigger_sources[i]);changed|=source!=trigger_choices[i];trigger_choices[i]=source;
    }
    for(unsigned i=0;i<3;i++){int source=TlkResourcesUseMd(monkey_sources[i]);changed|=source!=monkey_choices[i];monkey_choices[i]=source;}
    if (!changed) return 0;
    music_choice=choice;TlkAudioReset();return 1;
}
static void audit_native_output(const int16_t *samples,unsigned count,unsigned gain) {
    if(!gain || !samples || !count || count>4096 || !TlkFallbackEnabled() || !TlkResourcesGroupMd("audio"))return;
    unsigned peak=0;for(unsigned i=0;i<count*2;i++){
        unsigned value=(unsigned)abs((int)samples[i]*(int)gain/32768);if(value>peak)peak=value;}
    if(peak){TlkFallbackContext(frame,word(0x1ff9e),address(0xdf));
        TlkFallbackRecord("unclassified_audio","audio","native_output_retained",0,0,peak,count*2);}
}
void TlkAudioMix(int16_t *dst,unsigned count,unsigned output_rate) {
    if(opening_timon_selected() && dst && count && count<=4096) {
        memset(dst,0,count*2*sizeof *dst);
        if(word(0x1ff96))TlkMdSoundRender(dst,count,output_rate);
        if(stems){unsigned peak=0;for(unsigned i=0;i<count*2;i++){unsigned v=(unsigned)abs(dst[i]);if(v>peak)peak=v;}
            fprintf(stems,"%u,%u,0,%u\n",frame,count,peak);fflush(stems);}
        return;
    }
    if(sound_test_scene() && TlkMdSoundReady() && dst && count && count<=4096) {
        /* This source selects the complete MD audition catalogue. Native
         * song uploads retain guest scheduling but cannot sound underneath. */
        memset(dst,0,count*2*sizeof *dst);TlkMdSoundRender(dst,count,output_rate);
        if(stems){unsigned peak=0;for(unsigned i=0;i<count*2;i++){unsigned v=(unsigned)abs(dst[i]);if(v>peak)peak=v;}
            fprintf(stems,"%u,%u,0,%u\n",frame,count,peak);fflush(stems);}
        return;
    }
    if(ending_sunrise() && finale_carry() && music_active &&
       TlkResourcesUseMd("audio.music.pride_rock.finale") && TlkMdSoundReady() &&
       dst && count && count<=4096){
        /* Sunrise has no gameplay FX before the first speech cue. Its native
         * illustrated-scene music is bank-started, so replace the complete
         * background bus here. Rain/roars in07DB keep their native owners. */
        memset(dst,0,count*2*sizeof *dst);TlkMdSoundRender(dst,count,output_rate);
        if(stems){unsigned peak=0;for(unsigned i=0;i<count*2;i++){unsigned v=(unsigned)abs(dst[i]);if(v>peak)peak=v;}
            fprintf(stems,"%u,%u,0,%u\n",frame,count,peak);fflush(stems);}
        return;
    }

    if(ending_credits() && TlkResourcesUseMd("audio.music.ending_credits") &&
       TlkMdSoundReady() && dst && count && count<=4096){
        /* This non-gameplay credits scene owns its entire score. Keep the
         * original song/driver/queue running for native scheduling, but do
         * not mix it underneath MD61. Also honor Music Off with FX enabled. */
        memset(dst,0,count*2*sizeof *dst);
        if(music_active && selected_music() && word(0x1ff94))TlkMdSoundRender(dst,count,output_rate);
        if(stems){unsigned peak=0;for(unsigned i=0;i<count*2;i++){unsigned v=(unsigned)abs(dst[i]);if(v>peak)peak=v;}
            fprintf(stems,"%u,%u,0,%u\n",frame,count,peak);fflush(stems);}
        return;
    }
    if(TlkBonusResultSceneActive() && dst && count && count<=4096){
        unsigned gain=tlk_bonus_result_scene.phase<TLK_RESULT_SETUP && music_active && selected_music()?0:TlkBonusResultSceneNativeGain();
        audit_native_output(dst,count,gain);
        int16_t md[8192]={0};if(TlkMdSoundReady())TlkMdSoundRender(md,count,output_rate);
        for(unsigned i=0;i<count*2;i++){
            int value=((int)dst[i]*(int)gain>>15)+md[i];dst[i]=value<-32768?-32768:value>32767?32767:value;
        }
        return;
    }
    if(TlkInterlevelSceneAudioSelected() && TlkMdSoundReady() && dst && count && count<=4096){
        /* The new scene owns its complete soundtrack; keep guest SPC scheduling
         * intact and replace its output, including the outgoing music tail. */
        memset(dst,0,count*2*sizeof *dst);TlkMdSoundRender(dst,count,output_rate);return;
    }
    if ((!music_active && !fx_tail && !ending_speech_selected() && !destiny_boulder_running() && !geyser_audio_running()) || word(0x0a89) || !count || count>4096 || !TlkMdSoundReady()) {audit_native_output(dst,count,32768);return;}
    int16_t md[8192];
    if (!TlkMdSoundRender(md,count,output_rate)) {audit_native_output(dst,count,32768);return;}
    audit_native_output(dst,count,32768);
    unsigned native_peak=0,md_peak=0;
    for (unsigned i=0;i<count*2;i++) {
        unsigned a=(unsigned)abs(dst[i]),b=(unsigned)abs(md[i]);
        if (a>native_peak) native_peak=a;
        if (b>md_peak) md_peak=b;
        int value=dst[i]+md[i];dst[i]=(int16_t)(value<-32768?-32768:value>32767?32767:value);
    }
    if (stems) { fprintf(stems,"%u,%u,%u,%u\n",frame,count,native_peak,md_peak);fflush(stems); }
}

/* MD driver and host output continuation are independent of the guest's SPC
 * snapshot. Presentation choices may differ on load; audio history only follows
 * matching effective audio choices and the same output sample rate. */
enum { AUDIO_HEADER=140 };
size_t TlkNativeAudioHistorySize(void);
int TlkNativeAudioSaveHistory(uint8_t *,size_t);
int TlkNativeAudioValidateHistory(const uint8_t *,size_t);
int TlkNativeAudioLoadHistory(const uint8_t *,size_t);
static double *host_fraction, saved_fraction;
static unsigned host_rate,saved_rate;
void TlkAudioBindHost(double *fraction,unsigned rate) {
    host_fraction=fraction;host_rate=rate;
    if(fraction)*fraction=0;
}
static int audio_fingerprint(uint8_t hash[32]) {
    char ids[16384];size_t used=0;int selected=0;
    for(int i=0;i<TlkResourcesCount();i++) {
        const TlkResourceNode *node=TlkResourcesNode(i);
        if(!node->leaf || strncmp(node->id,"audio.",6) || !TlkResourcesUseMd(node->id))continue;
        size_t n=strlen(node->id)+1;
        if(n>sizeof ids-used)return -1;
        memcpy(ids+used,node->id,n);used+=n;selected=1;
    }
    sha256_compute(ids,used,hash);return selected;
}
static int audio_hash(const uint8_t *data,size_t size,uint8_t hash[32]) {
    uint8_t *copy=malloc(size);if(!copy)return 0;
    memcpy(copy,data,size);memset(copy+80,0,32);sha256_compute(copy,size,hash);free(copy);return 1;
}
#if TLK_NATIVE_AUDIO_OWNER_AVAILABLE
#define TlkAudioHistorySize TlkBaseAudioHistorySize
#define TlkAudioSaveHistory TlkBaseAudioSaveHistory
#define TlkAudioValidateHistory TlkBaseAudioValidateHistory
#define TlkAudioLoadHistory TlkBaseAudioLoadHistory
#endif
size_t TlkAudioHistorySize(void) {
    uint8_t fingerprint[32];int selected=audio_fingerprint(fingerprint);
    if(selected<0)return 0;
    size_t nested=selected && TlkMdSoundReady()?TlkMdSoundStateSize():0;
    if(selected && TlkMdSoundReady() && !nested)return 0;
    return AUDIO_HEADER+TlkNativeAudioHistorySize()+nested;
}
int TlkAudioSaveHistory(uint8_t *out,size_t size) {
    size_t expected=TlkAudioHistorySize();if(!out || !expected || size!=expected)return 0;
    memset(out,0,AUDIO_HEADER);memcpy(out,"TLKAUD01",8);TlkPut32(out+8,6);
    TlkPut32(out+120,ending_timing_epoch);TlkPut32(out+124,ending_timing_selected());
    TlkPut32(out+128,exile_exit_age);TlkPut32(out+132,exile_exit_phase);TlkPut32(out+136,exile_exit_delay);
    TlkPut32(out+112,death_phase);
    TlkPut32(out+116,battle_ready);
    TlkPut32(out+12,(music_active?1u:0u)|(pending_stop?2u:0u)|(menu_fx?4u:0u)|(cant_wait_fx?8u:0u)|(graveyard_fx?16u:0u)|(hunt_fx?32u:0u)|(prepared_fx?64u:0u)|(music_entry_seen?128u:0u)|(exile_exit_fx?256u:0u));
    TlkPut32(out+16,fx_tail);TlkPut32(out+20,music_track);TlkPut32(out+24,music_scene);
    TlkPut32(out+28,host_rate?host_rate:saved_rate);TlkPutDouble(out+32,host_fraction?*host_fraction:saved_fraction);
    size_t native=TlkNativeAudioHistorySize(),nested=size-AUDIO_HEADER-native;
    TlkPut32(out+40,(uint32_t)nested);TlkPut32(out+44,(uint32_t)native);
    if(audio_fingerprint(out+48)<0)return 0;
    if(!TlkNativeAudioSaveHistory(out+AUDIO_HEADER,native))return 0;
    if(nested && !TlkMdSoundSaveState(out+AUDIO_HEADER+native,nested))return 0;
    uint8_t hash[32];if(!audio_hash(out,size,hash))return 0;memcpy(out+80,hash,32);return 1;
}
int TlkAudioValidateHistory(const uint8_t *data,size_t size) {
    if(!data || size<AUDIO_HEADER || size>TLK_AUDIO_HISTORY_MAX || memcmp(data,"TLKAUD01",8) ||
       TlkGet32(data+8)!=6 || TlkGet32(data+12)>511 || TlkGet32(data+16)>120 ||
       TlkGet32(data+20)>65535 || TlkGet32(data+24)>65535)return 0;
    unsigned rate=TlkGet32(data+28),nested=TlkGet32(data+40),native=TlkGet32(data+44);
    double fraction=TlkGetDouble(data+32);
    if((rate && (rate<8000 || rate>192000)) || !isfinite(fraction) || fraction<0 || fraction>=1 ||
       native!=TlkNativeAudioHistorySize() || native>size-AUDIO_HEADER || nested!=size-AUDIO_HEADER-native)return 0;
    if(TlkGet32(data+112)>3 || TlkGet32(data+116)>1)return 0;
    if(TlkGet32(data+124)>1)return 0;
    if(TlkGet32(data+128)>50 || TlkGet32(data+132)>3 || TlkGet32(data+136)>31)return 0;
    uint8_t hash[32];
    return TlkNativeAudioValidateHistory(data+AUDIO_HEADER,native) &&
        (!nested || TlkMdSoundValidateState(data+AUDIO_HEADER+native,nested)) &&
        audio_hash(data,size,hash) && !memcmp(hash,data+80,32);
}
int TlkAudioLoadHistory(const uint8_t *data,size_t size) {
    if(!data && !size) {
        ending_timing_epoch=0;
        TlkAudioReset();saved_fraction=0;saved_rate=0;if(host_fraction)*host_fraction=0;return 1;
    }
    if(!TlkAudioValidateHistory(data,size))return 0;
    ending_timing_epoch=TlkGet32(data+124)==(unsigned)ending_timing_selected()?TlkGet32(data+120):0;
    uint8_t fingerprint[32];if(audio_fingerprint(fingerprint)<0)return 0;
    unsigned rate=TlkGet32(data+28),nested=TlkGet32(data+40),native=TlkGet32(data+44);
    int same_rate=!host_rate || rate==host_rate;
    int compatible=same_rate && !memcmp(fingerprint,data+48,32) && (!nested || TlkMdSoundReady());
    if(compatible && nested && !TlkMdSoundLoadState(data+AUDIO_HEADER+native,nested))return 0;
    if(same_rate && !TlkNativeAudioLoadHistory(data+AUDIO_HEADER,native))return 0;
    if(compatible) {
        unsigned flags=TlkGet32(data+12);music_active=!!(flags&1);pending_stop=!!(flags&2);menu_fx=!!(flags&4);cant_wait_fx=!!(flags&8);graveyard_fx=!!(flags&16);hunt_fx=!!(flags&32);prepared_fx=!!(flags&64);
        music_entry_seen=!!(flags&128);exile_exit_fx=!!(flags&256);
        exile_exit_age=TlkGet32(data+128);exile_exit_phase=TlkGet32(data+132);exile_exit_delay=TlkGet32(data+136);
        fx_tail=TlkGet32(data+16);music_track=TlkGet32(data+20);music_scene=TlkGet32(data+24);
        death_phase=TlkGet32(data+112);battle_ready=TlkGet32(data+116);
        cw_reaction_rebuild();
    } else TlkAudioReset();
    saved_fraction=same_rate?TlkGetDouble(data+32):0;
    saved_rate=rate;
    if(host_fraction)*host_fraction=saved_fraction;
    return 1;
}

#if TLK_NATIVE_AUDIO_OWNER_AVAILABLE
#include "tlk_audio_owner_history.inc"
#endif

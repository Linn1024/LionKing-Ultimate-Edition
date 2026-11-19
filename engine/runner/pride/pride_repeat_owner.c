/* Research-only native preparation scheduling under the verified MD clock.
 * Physical readiness/return ownership, not a selectable complete death mode. */
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include "snes/snes.h"
#include "tlk_death_scene.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static TlkDeathProgram owner_program;
static TlkDeathScene owner_scene;
static unsigned owner_installed,owner_enabled,owner_loop,owner_skip,owner_hold_count,owner_ended;
static unsigned owner_initial_hold,owner_waiting;
static unsigned owner_normal_release;
static unsigned owner_first_hold_pose;
static unsigned owner_entry_field;
static unsigned owner_normal_latch_serial;
unsigned PrideNativeLatchSerial(void);
void PrideRepeatSceneBegin(void);
static unsigned owner_default_initialized,owner_default_prepared;
static unsigned owner_default_advancing,owner_default_advanced,owner_default_advance_wait;
static unsigned owner_default_callback;
static uint16_t owner_wait_sp,owner_wait_a,owner_wait_x,owner_wait_y,owner_wait_d;
static uint8_t owner_wait_p,owner_wait_db;
static FILE *owner_events,*owner_fields;
static FILE *owner_after_ready;
static unsigned ow(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned ol(unsigned at) { return ow(at)|(unsigned)g_ram[at+2]<<16; }
static unsigned owner_ready_age(void) { return owner_scene.has_checkpoint?345:300; }
static unsigned owner_age(void) { return owner_scene.started?owner_scene.age:0; }
static void owner_log(const char *event,CpuState *cpu,uint32_t pc,unsigned value) {
    fprintf(owner_events,"%s,%u,%u,%06x,%u,%04x,%02x,%04x,%02x,%04x,%04x,%04x,%u,%u,%06x\n",event,
        (unsigned)snes_frame_counter+1,(unsigned)snes_frame_counter+1-owner_entry_field,pc,value,cpu->S,cpu->DB,cpu->D,cpu->P,cpu->A,cpu->X,cpu->Y,
        ow(0x2004),ow(0x1ffaa),ol(0xb243));fflush(owner_events);
}
#include "pride_repeat_service.h"
#include "pride_actor_handoff_policy.h"
static int PrideRepeatEligible(void) {
    /* The hyena arena uses a separate descriptor on the same level. Its
     * nonfinal health death enters the same coordinator and restores the
     * collected checkpoint through the main-scene loader. */
    unsigned descriptor=ol(0xdf);
    return !ow(0x1ff9e) && !ow(0x2000) && !ow(0x2004) && !ow(0xa6ba) &&
        !ow(0x1ff90) && ow(0x1ffaa) &&
        (descriptor==0xc00387 || descriptor==0xc0080d) && ol(0xb243)==0xc35a82;
}
static void owner_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(pc==0xc089b9 && (!owner_scene.started || owner_ended)) {
        if(!PrideRepeatEligible())return;
        /* 1FFA2 is a reload marker: it becomes1 even for a default revival.
         * The saved spawn coordinates identify the original default branch. */
        PrideRepeatSceneBegin();
        unsigned checkpoint=spawn_policy_checkpoint();
        TlkDeathContext c={.md_selected=1,.level=ow(0x1ff9e),.descriptor=ol(0xdf),.cub_age=ow(0x2000),
            .health=ow(0x2004),.skip_display=ow(0xa6ba),.actor=ow(0x6e),.state_marker=ol(0xb243),
            .entry_pc=0xc089b7,.owner=1,.has_checkpoint=checkpoint,.x=ow(0xb21b),.y=ow(0xb21d),
            .camera_x=ow(0xb29b),.camera_y=ow(0xb29d)};
        unsigned events=0;
        if(!TlkDeathSceneBegin(&owner_scene,&owner_program,&c,(uint64_t)snes_frame_counter+1,&events))exit(50);
        owner_entry_field=(unsigned)snes_frame_counter+1;owner_log("begin",cpu,pc,events);
        spawn_policy_log(cpu,pc,2,0,0);return;
    }
    if(!owner_scene.started || owner_ended)return;
    if(pc==0xc08b15)owner_log("native_health",cpu,pc,ow(0x2004));
    if(pc==0xc08652)owner_log("native_actor",cpu,pc,ow(0x6e));
    if(pc==0xc32b27) { owner_normal_latch_serial=PrideNativeLatchSerial();owner_log("normal",cpu,pc,0);owner_ended=1;return; }
    if(!owner_enabled)return;
    if(pc==0xc087b5 || pc==0xc087bf || pc==0xc0881d || pc==0xc08827)spawn_policy_compare(cpu,pc);
    if(pc==0xc08ac6 && !owner_loop) {
        if(cpu->D || cpu->m_flag || cpu->A!=279 || ow(0x2004) || ol(0xb243)!=0xc35a82)exit(51);
        owner_log("shorten_display",cpu,pc,cpu->A);cpu->A=160;owner_loop=1;
    }
    if(pc==0xc08e62 && !owner_skip && ow(cpu->S+1)==0x8b1e) {
        if(cpu->m_flag || cpu->D || cpu->A!=32 || !owner_loop)exit(51);
        owner_log("skip_post_health_wait",cpu,pc,cpu->A);
        cpu->A=0;cpu->_flag_Z=1;cpu->_flag_N=0;cpu_mirrors_to_p(cpu);
        owner_skip=1;interp_bridge_pre_opcode_redirect(0xc08e6a);
    }
    if(!owner_scene.has_checkpoint && pc==0xc087bf && !owner_default_initialized) {
        if(cpu->D || cpu->m_flag || !cpu->x_flag || cpu->DB || !cpu->_flag_Z ||
           ow(0x1ffa2)!=1 || ow(0x2004) || ow(0x6e)!=0xb213)exit(85);
        owner_default_initialized=1;owner_log("default_initialize",cpu,pc,0);
        interp_bridge_pre_opcode_redirect(0xc087c1);return;
    }
    if(!owner_scene.has_checkpoint && pc==0xc087c5 && owner_default_initialized) {
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag ||
           (owner_default_advancing && !owner_default_advance_wait))exit(85);
        /* Original bank setup has run. Reuse its real JSL animation/draw/wait
         * tail without repeating the sound/bank selection or initializer. */
        if(owner_default_advancing)interp_bridge_pre_opcode_redirect(0xc087f6);
        else if(!owner_default_prepared) {
            /* The checkpoint-only C22D1F audio command is not part of default
             * idle preparation. Keep audio ownership independent. */
            interp_bridge_pre_opcode_redirect(0xc087e8);
        }
        return;
    }
    if(!owner_scene.has_checkpoint && pc==0xc087eb) {
        if(!owner_default_initialized || owner_default_advancing || cpu->D || cpu->DB!=0x7e ||
           cpu->m_flag || cpu->A!=0xdebd || ow(0x6e)!=0xb213)exit(85);
        /* The actual native idle initializer owns cursor/pose/timer writes. */
        cpu->A=0xe3a6;cpu->_flag_Z=0;cpu->_flag_N=1;cpu_mirrors_to_p(cpu);
        owner_log("default_idle_parameter",cpu,pc,cpu->A);
    }
    if(!owner_scene.has_checkpoint && pc==0xc087fe) {
        if(!grounded_service(cpu,pc))return;
        unsigned draw=ow(0xb21f);
        if(!owner_default_initialized || draw<0x8000 || draw>0xffe8 ||
           ol(draw+10)!=owner_program.idle.snes_pose ||
           ow(0xb22d)!=owner_program.idle.duration-(owner_default_advancing?1:0))exit(85);
        owner_default_prepared=1;
        if(!owner_default_callback)owner_default_callback=ol(0xb221);
        if(owner_default_advancing) { owner_default_advanced=1;owner_default_advancing=0; }
        owner_log(owner_default_advanced?"default_idle_advanced":"default_idle_prepared",cpu,pc,ow(0xb22d));
    }
    if(pc==0xc08808) {
        if(owner_waiting) {
            if(cpu->S!=owner_wait_sp || cpu->D!=owner_wait_d || cpu->DB!=owner_wait_db)exit(52);
            cpu->A=owner_wait_a;cpu->X=owner_wait_x;cpu->Y=owner_wait_y;cpu->P=owner_wait_p;cpu_p_to_mirrors(cpu);
            owner_waiting=0;
            owner_log(owner_default_advance_wait?"default_idle_advance_return":"hold_return",cpu,pc,owner_hold_count);
            owner_default_advance_wait=0;
        }
        if(!owner_scene.has_checkpoint && owner_age()==274 && !owner_default_advanced) {
            if(!owner_default_prepared || owner_default_advancing || cpu->D || cpu->DB || cpu->S!=0x2ff ||
               cpu->m_flag || cpu->PB!=0xc0 || ow(0x2004)!=ow(0x1ffac))exit(85);
            owner_wait_sp=cpu->S;owner_wait_a=cpu->A;owner_wait_x=cpu->X;owner_wait_y=cpu->Y;
            owner_wait_p=cpu->P;owner_wait_d=cpu->D;owner_wait_db=cpu->DB;owner_waiting=1;
            owner_default_advancing=owner_default_advance_wait=1;
            owner_log("default_idle_advance_call",cpu,pc,0);
            interp_bridge_pre_opcode_redirect(0xc087c1);return;
        }
        if(owner_age()<(owner_scene.has_checkpoint?296:300)) {
            if(!owner_skip || cpu->S<0x204 || cpu->S>0x2ff || cpu->PB!=0xc0 || cpu->emulation)exit(52);
            owner_wait_sp=cpu->S;owner_wait_a=cpu->A;owner_wait_x=cpu->X;owner_wait_y=cpu->Y;
            owner_wait_p=cpu->P;owner_wait_d=cpu->D;owner_wait_db=cpu->DB;owner_waiting=1;
            /* A real bank-local JSR frame for the native one-field service.
             * Its RTS returns to this boundary; caller/live frames stay put. */
            cpu_write8(cpu,0,cpu->S--,0x88);cpu_write8(cpu,0,cpu->S--,0x07);
            owner_log("hold_call",cpu,pc,++owner_hold_count);
            interp_bridge_pre_opcode_redirect(0xc0983d);
        } else owner_log("hold_release",cpu,pc,owner_hold_count);
    }
    if(pc==0xc0882c && !owner_initial_hold) {
        if(cpu->m_flag || cpu->A!=49 || owner_age()!=296)exit(53);
        /* Native BPL loop runs50 invocations. Original MD hold has49. */
        owner_log("checkpoint_hold_count",cpu,pc,cpu->A);cpu->A=48;owner_initial_hold=1;
    }
    if(pc==0xc08860 && !owner_normal_release) {
        /* The native loop otherwise waits one more field before its first
         * update. The MD controller has already delivered READY in this field. */
        if(owner_age()!=owner_ready_age() || (owner_scene.has_checkpoint && !owner_initial_hold) || owner_waiting || cpu->S!=0x2ff || cpu->D || cpu->DB || cpu->A)exit(55);
        owner_log("normal_release",cpu,pc,0);owner_normal_release=1;
        interp_bridge_pre_opcode_redirect(0xc08863);
    }
    if(pc==0xc08837 && !owner_first_hold_pose) {
        unsigned draw=ow(0xb21f);
        if(owner_age()!=296 || !owner_initial_hold || draw<0x8000 || draw>=0xffe0 ||
           ol(draw+10)!=owner_program.revival[0].snes_pose || ow(0xb22d)!=3)exit(56);
        /* Original MD's first hold invocation retains the already displayed
         * pose/timer. Subsequent49-loop invocations advance normally. */
        owner_log("retain_first_hold_pose",cpu,pc,3);owner_first_hold_pose=1;
        interp_bridge_pre_opcode_redirect(0xc0883b);
    }
}
static void owner_init(void) {
    const char *folder=TlkPrideSetting("TLK_SCENE_OWNER_PROBE"),*path=TlkPrideSetting("TLK_SCENE_OWNER_MD_ROM");
    if(!folder || !path)exit(50);
    FILE *rom=TlkPrideFileOpen(path,"rb");uint8_t *md=malloc(0x300000);if(!rom || !md)exit(50);
    if(fread(md,1,0x300000,rom)!=0x300000 || fgetc(rom)!=EOF)exit(50);fclose(rom);
    if(!TlkDeathProgramInit(&owner_program,g_rom,0x300000,md,0x300000))exit(50);memset(md,0,0x300000);free(md);
    const char *mode=TlkPrideSetting("TLK_SCENE_OWNER_ENABLE");owner_enabled=mode && !strcmp(mode,"1");
    char file[2048];snprintf(file,sizeof file,"%s/owner-events.csv",folder);owner_events=TlkPrideFileOpen(file,"w");
    snprintf(file,sizeof file,"%s/owner-fields.csv",folder);owner_fields=TlkPrideFileOpen(file,"w");if(!owner_events || !owner_fields)exit(50);
    fprintf(owner_events,"event,field,age,pc,value,stack,db,direct_page,p,a,x,y,health,lives,state\n");
    fprintf(owner_fields,"field,age,events,model_phase,native_health,native_state,draw_pose,animation,raw_timer,x,y\n");
    snprintf(file,sizeof file,"%s/post-ready.csv",folder);owner_after_ready=TlkPrideFileOpen(file,"w");if(!owner_after_ready)exit(50);
    fprintf(owner_after_ready,"field,elapsed,pose,callback,cursor,timer,x,y\n");
    static const uint32_t points[]={0xc0881d,0xc08827,0xc087b5,0xc087bf,0xc087c5,0xc087eb,0xc087fe,0xc089b9,0xc08ac6,0xc08e62,0xc08b15,0xc08652,0xc08808,0xc0882c,0xc08837,0xc08860,0xc32b27};
    for(unsigned i=0;i<sizeof points/sizeof *points;i++)interp_bridge_add_pre_opcode_hook(points[i],owner_hook);
}
static bool owner_frame(uint32 inputs) {
    if(!owner_installed) { owner_installed=1;owner_init(); }
    unsigned events=0,field=(unsigned)snes_frame_counter+1;
    if(owner_scene.started && !owner_ended && !TlkDeathSceneAdvance(&owner_scene,&owner_program,field,0,&events))exit(54);
    bool result=RtlRunFrame(inputs);
    if(owner_scene.started && owner_ended && !owner_scene.has_checkpoint &&
       field>=owner_entry_field+300 && field<=owner_entry_field+308) {
        unsigned draw=ow(0xb21f);
        fprintf(owner_after_ready,"%u,%u,%06x,%06x,%06x,%u,%u,%u\n",field,field-owner_entry_field,
            draw>=0x8000 && draw<0xffe0?ol(draw+10):0,ol(0xb221),ol(0xb225),ow(0xb22d),ow(0xb21b),ow(0xb21d));fflush(owner_after_ready);
    }
    if(owner_scene.started && (!owner_ended || owner_scene.last_field==field)) {
        TlkDeathView v;if(!TlkDeathSceneView(&owner_scene,&owner_program,&v))exit(54);
        unsigned draw=ow(0xb21f),pose=draw>=0x8000 && draw<0xffe0?ol(draw+10):0;
        fprintf(owner_fields,"%u,%u,%u,%u,%u,%06x,%06x,%06x,%u,%u,%u\n",field,owner_age(),events,v.phase,
            ow(0x2004),ol(0xb243),pose,ol(0xb221),ow(0xb22d),ow(0xb21b),ow(0xb21d));fflush(owner_fields);
    }
    return result;
}
#undef RtlRunFrame
#define RtlRunFrame owner_frame
#include "pride_repeat_prepare.c"

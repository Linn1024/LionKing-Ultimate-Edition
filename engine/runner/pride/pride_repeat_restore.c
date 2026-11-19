/* Isolated semantic restore-request/publication ownership. No per-field RAM
 * masking: an unowned early health writer stops the experiment for inspection. */
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include "snes/snes.h"
#include "tlk_death_scene.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef TLK_PRIVATE_COMPILED_HOOKS
#include "pride_actor_handoff_compiled_hooks.h"
#endif
/* Shared with the included coordinator in this single research translation
 * unit. Its clock advances before this wrapper calls the original frame. */
static TlkDeathProgram owner_program;
static TlkDeathScene owner_scene;
static unsigned owner_enabled,owner_ended,owner_entry_field;
static unsigned owner_ready_age(void);
static unsigned owner_default_callback;
static unsigned restore_installed,restore_enabled,restore_pending,restore_committed;
static unsigned restore_canonical,restore_canonical_calls,restore_idle_cursor;
static unsigned restore_roar_zero;
static unsigned restore_roar_font_valid,restore_roar_font_maximum,restore_roar_font_current;
static uint16_t restore_roar_font_initial;
static uint16_t restore_health,restore_roar;
static FILE *restore_events,*restore_fields;
static unsigned rw(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static unsigned rl(unsigned at) { return rw(at)|(unsigned)g_ram[at+2]<<16; }
static void restore_log(const char *event,unsigned value,uint32_t pc) {
    fprintf(restore_events,"%s,%u,%u,%06x,%u,%u,%u\n",event,(unsigned)snes_frame_counter+1,
        (unsigned)snes_frame_counter+1-owner_entry_field,pc,value,rw(0x2004),rw(0x2002));fflush(restore_events);
}
static void restore_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(!restore_enabled || !owner_enabled || !owner_scene.started || owner_ended)return;
    if(cpu->D || cpu->m_flag || cpu->DB!=0x7e || owner_scene.age!=225 || rw(0x2004))exit(57);
    if(pc==0xc08b09) {
        if(restore_pending || cpu->A!=rw(0x1ffac) || !cpu->A || cpu->A>255)exit(57);
        restore_health=cpu->A;restore_pending|=1;restore_log("request_health",cpu->A,pc);
        interp_bridge_pre_opcode_redirect(0xc08b0d);
    } else if(pc==0xc08b11) {
        if(restore_pending!=1 || cpu->A!=rw(0x1ffae))exit(57);
        restore_roar=restore_roar_zero?0:cpu->A;restore_pending|=2;restore_log("request_roar",restore_roar,pc);
        interp_bridge_pre_opcode_redirect(0xc08b15);
    }
}
static void restore_hud_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(!restore_enabled || !owner_enabled || !owner_scene.started || owner_ended || restore_committed || restore_pending!=3)return;
    /* C00201 owns the native health meter AND transfers to death on HP=0.
     * During owned revival, zero is intentional until the restore event. The
     * health widget waits with the scene; it must not initiate another death. */
    unsigned object=rw(0x68);
    /* The checkpoint rebuild moves this task (B493 -> B413 in the observed
     * route). Its verified callback is semantic identity, not the heap slot. */
    if(rw(0x2004) || object<0xa000 || object>0xff80 || cpu->m_flag || cpu->D || cpu->DB!=0x7e) {
        fprintf(stderr,"restore widget context age=%u object=%04x D=%04x DB=%02x M=%u X=%u health=%u local_object=%04x\n",
            owner_scene.age,object,cpu->D,cpu->DB,cpu->m_flag,cpu->x_flag,rw(0x2004),rw((cpu->D+0x68)&65535));exit(59);
    }
    restore_log("hold_health_widget",object,pc);
    /* No PHP has executed yet. Use the routine's real RTL, preserving the
     * entry flags/direct page/bank and the actual long-call return frame. */
    interp_bridge_pre_opcode_redirect(0xc00356);
}
static void restore_roar_font_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(!restore_roar_zero || cpu->D || cpu->DB!=0x7e || cpu->m_flag || rw(0x0a56) ||
       rw(0x1ff9e) || rl(0xdf)!=0xc00387)return;
    unsigned task=rw(0x68),maximum=rw(0x1ffae),current=rw(0x2002);
    if(task<0xa000 || task>0xff80 || maximum<8 || maximum>64 || current>maximum)return;
    /* A cache hit does not rebuild. Retain the flag from the actual most
     * recent original rebuild, not unrelated scratch from a later task. */
    if(rw(task+16)==maximum && rw(task+14)==current)return;
    restore_roar_font_initial=(uint16_t)rw(0x21);restore_roar_font_maximum=maximum;
    restore_roar_font_current=current;restore_roar_font_valid=1;
    if(owner_scene.started && !owner_ended)restore_log("roar_font_context",restore_roar_font_initial,pc);
}
int PrideSceneRestoreRoarContext(unsigned maximum,unsigned current,uint16_t *initial_full) {
    if(!restore_roar_font_valid || !initial_full || maximum!=restore_roar_font_maximum ||
       current!=restore_roar_font_current)return 0;
    *initial_full=restore_roar_font_initial;return 1;
}
static void restore_ready_roar_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(!restore_roar_zero || !restore_committed || !owner_scene.started || owner_scene.age!=owner_ready_age() ||
       (unsigned)snes_frame_counter+1!=owner_entry_field+owner_ready_age())return;
    /* The original ready path independently restores full roar a second time.
     * Preserve the selected zero value at this actual writer, not by masking
     * subsequent fields. A is immediately overwritten by the following LDA. */
    if(cpu->D || cpu->DB || cpu->m_flag || cpu->A!=rw(0x1ffae) ||
       rw(0x2002) || rw(0x2004)!=restore_health)exit(57);
    restore_log("retain_zero_roar_ready",cpu->A,pc);
    interp_bridge_pre_opcode_redirect(0xc08859);
}
static void restore_animation_hook(CpuState *cpu,uint32_t pc) {
    if(!TlkPrideHealthDeathSelected())return;
    if(!restore_canonical || !restore_committed || !owner_scene.started || owner_scene.age!=owner_ready_age() ||
       (unsigned)snes_frame_counter+1!=owner_entry_field+owner_ready_age())return;
    unsigned player=rw(0x6e),object=rw(0x68);
    if(!player || player!=object || player>0xff80)return;
    unsigned draw=rw(player+12);
    if(draw<0x8000 || draw>=0xffe0 || rl(draw+10)!=owner_program.idle.snes_pose ||
       rl(player+18)!=restore_idle_cursor || rw(player+26)!=owner_program.idle.duration-(owner_scene.has_checkpoint?0:1))return;
    if(!owner_scene.has_checkpoint && (rl(player+14)&65535)==0xe3a6 && (rl(player+14)>>16)==0xc0) {
        /* The original initializer has already run before fade. Normal-entry
         * dispatch requests it again; retain its observed continuation before
         * skipping this duplicate, or the following field would restart idle. */
        if(!owner_default_callback || (owner_default_callback>>16)!=0xc0)exit(85);
        cpu_write16(cpu,0x7e,player+14,(uint16_t)owner_default_callback);
        cpu_write8(cpu,0x7e,player+16,(uint8_t)(owner_default_callback>>16));
        restore_log("retain_default_idle_callback",owner_default_callback,pc);
    }
    /* The controller already returned to idle at344. Retain that canonical
     * state for the handoff field, without resetting the live timer afterward.
     * A newly selected action has another cursor and proceeds normally. */
    restore_log("retain_ready_idle",rw(player+26),pc);restore_canonical_calls++;
    /* The original wrapper returns C=0 for an active frame; PLD supplies N/Z
     * from the entry D. Use its real RTL with no unmatched PHD/PLD frame. */
    cpu->_flag_C=0;cpu->_flag_Z=cpu->D==0;cpu->_flag_N=(cpu->D&0x8000)!=0;cpu_mirrors_to_p(cpu);
    interp_bridge_pre_opcode_redirect(0xc0af12);
}
static bool restore_frame(uint32 inputs) {
    if(!restore_installed) {
        restore_installed=1;const char *folder=TlkPrideSetting("TLK_SCENE_RESTORE_PROBE"),*mode=TlkPrideSetting("TLK_SCENE_RESTORE_ENABLE");
        if(!folder)exit(57);restore_enabled=mode && !strcmp(mode,"1");
        mode=TlkPrideSetting("TLK_SCENE_RESTORE_CANONICAL");restore_canonical=restore_enabled && mode && !strcmp(mode,"1");
        mode=TlkPrideSetting("TLK_SCENE_RESTORE_ROAR_ZERO");
        if(mode && strcmp(mode,"0") && strcmp(mode,"1"))exit(57);
        restore_roar_zero=restore_enabled && mode && !strcmp(mode,"1");
        unsigned end=0xdedd+TLK_REVIVAL_TOKENS*4;
        restore_idle_cursor=(g_rom[end+1]|(unsigned)g_rom[end+2]<<8|(unsigned)g_rom[end+3]<<16)+4;
        char path[2048];snprintf(path,sizeof path,"%s/restore-events.csv",folder);restore_events=TlkPrideFileOpen(path,"w");if(!restore_events)exit(57);
        snprintf(path,sizeof path,"%s/restore-fields.csv",folder);restore_fields=TlkPrideFileOpen(path,"w");if(!restore_fields)exit(57);
        fprintf(restore_events,"event,field,age,pc,value,health,roar\n");
        fprintf(restore_fields,"field,age,health,roar,pending,published,canonical_calls\n");
        interp_bridge_add_pre_opcode_hook(0xc08b09,restore_hook);interp_bridge_add_pre_opcode_hook(0xc08b11,restore_hook);
        interp_bridge_add_pre_opcode_hook(0xc00201,restore_hud_hook);
        interp_bridge_add_pre_opcode_hook(0xc0d6a6,restore_roar_font_hook);
        interp_bridge_add_pre_opcode_hook(0xc08855,restore_ready_roar_hook);
        interp_bridge_add_pre_opcode_hook(0xc0af09,restore_animation_hook);
    }
    if(restore_enabled && owner_scene.started && !owner_ended && !restore_committed) {
        TlkDeathView view;if(!TlkDeathSceneView(&owner_scene,&owner_program,&view))exit(57);
        if(view.phase==TLK_DEATH_REVIVAL_FADE) {
            if(restore_pending!=3 || rw(0x2004))exit(57);
            /* Publish the native resource values at the controller's event,
             * with actual bus writes, before executing this field's CPU work. */
            cpu_write16(&g_cpu,0x7e,0x2004,restore_health);cpu_write16(&g_cpu,0x7e,0x2002,restore_roar);
            restore_committed=1;restore_log("publish",restore_health,0);
        }
    }
    unsigned field=(unsigned)snes_frame_counter+1;bool result=RtlRunFrame(inputs);
    if(owner_scene.started && (owner_scene.last_field==field || restore_roar_zero)) {
        fprintf(restore_fields,"%u,%u,%u,%u,%u,%u,%u\n",field,field-owner_entry_field,rw(0x2004),rw(0x2002),
            restore_pending,restore_committed,restore_canonical_calls);fflush(restore_fields);
    }
    if(restore_enabled && owner_scene.started && !owner_ended && !restore_committed && rw(0x2004)) {
        restore_log("unowned_early_health",rw(0x2004),0);
        fprintf(stderr,"restore early health age=%u value=%u\n",owner_scene.age,rw(0x2004));exit(58);
    }
    return result;
}
#undef RtlRunFrame
#define RtlRunFrame restore_frame
#include "pride_repeat_owner.c"

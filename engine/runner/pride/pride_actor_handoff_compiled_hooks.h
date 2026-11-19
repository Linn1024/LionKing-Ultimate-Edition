/* Research-only bridge. Included in ONE host TU after the original bridge
 * declarations. Generated clones call this before selected real instructions.
 * Registration/redirect semantics are shared with the existing LLE callbacks. */
#ifndef PRIDE_SCENE_COMPILED_HOOKS_H
#define PRIDE_SCENE_COMPILED_HOOKS_H
#include "pride_scene_compiled_hooks_api.h"
#include "tlk_native_audio_owner.h"
#include "tlk_layout.h"
#include "tlk_rng_runtime.h"
#include "tlk_hitboxes.h"
#include "tlk_cant_wait_gameplay.h"
#include "tlk_destiny_monkey.h"
#include <stdio.h>
#include <stdlib.h>
typedef struct PrideCompiledHook { uint32_t pc;InterpPreOpcodeHook callback; } PrideCompiledHook;
static PrideCompiledHook pride_compiled_hooks[256];
static unsigned pride_compiled_count,pride_compiled_active,pride_compiled_redirect;
static unsigned long pride_compiled_calls,pride_compiled_hits,pride_compiled_local,pride_compiled_services;
static uint32_t pride_compiled_target;
static void pride_compiled_stats(void) {
    fprintf(stderr,"pride_compiled_hook_calls=%lu callbacks=%lu redirects=%lu paired_services=%lu\n",
        pride_compiled_calls,pride_compiled_hits,pride_compiled_local,pride_compiled_services);
}
static bool PrideRegisterOpcodeHook(uint32_t pc,InterpPreOpcodeHook callback) {
    if(!interp_bridge_add_pre_opcode_hook(pc,callback))return false;
    uint32_t key=pc&0x7fffff;
    for(unsigned n=0;n<pride_compiled_count;n++)
        if(pride_compiled_hooks[n].pc==key && pride_compiled_hooks[n].callback==callback)return true;
    if(pride_compiled_count==256)abort();
    if(!pride_compiled_count)atexit(pride_compiled_stats);
    pride_compiled_hooks[pride_compiled_count++]=(PrideCompiledHook){key,callback};return true;
}
static void PrideRedirectOpcode(uint32_t pc) {
    if(pride_compiled_active) { pride_compiled_target=pc&0xffffff;pride_compiled_redirect=1; }
    else interp_bridge_pre_opcode_redirect(pc);
}
void PrideSceneCompiledUnmapped(CpuState *cpu,uint32_t source,uint32_t target) {
    fprintf(stderr,"pride compiled unsupported redirect %06x -> %06x M%uX%u S%04x\n",
        source,target,cpu->m_flag,cpu->x_flag,cpu->S);exit(81);
}
uint32_t PrideSceneCompiledPreOpcode(CpuState *cpu,uint32_t pc) {
    TlkNativeAudioOwnerCpu(cpu,pc);
    if(pc==0xc4326d || pc==0xc0bb96)TlkCantWaitRidePostOpcode(cpu,pc);
    if(pc==0xc439d3)TlkCantWaitOstrichDelayPostOpcode(cpu,pc);
    if(pc==0xc18f74)TlkCantWaitGiraffePostOpcode(cpu,pc);
    if(pc==0xc45687 || pc==0xc4569c)TlkCantWaitRoarPostOpcode(cpu,pc);
    if(pc==0xc2ebce)TlkTailContactPostOpcode(cpu,pc);
    if(pc==0xc08808)TlkRngStageBeginOpcode(cpu,pc);
    if(pc==0xc08859)TlkLayoutRetryPreOpcode(cpu,pc);
    if(pc==0xc53bea || pc==0xc53c5a || pc==0xc542c9 || pc==0xc54301 || pc==0xc54827 || pc==0xc54834)
        TlkLayoutBonusPreOpcode(cpu,pc);
    pride_compiled_calls++;
    if(TlkDestinyMonkeyHookSite(pc)) {
        uint32_t target=TlkDestinyMonkeyOpcode(cpu,pc);
        if(target) {
            /* These reviewed action suffixes share the enclosing routine's
             * actual hardware return frame. Continue from the selected suffix,
             * with its original entry-S watermark, then return to that caller.
             * This uses existing interpreter services for the short shared
             * native suffix; no MD instructions or fabricated frames. */
            if(g_recomp_stack_top<1)
                PrideSceneCompiledUnmapped(cpu,pc,target);
            uint16_t entry=g_cpu_entry_s[g_recomp_stack_top-1];
            if((pc>>16)!=0xc4 || (uint16_t)(entry-cpu->S)!=3)
                PrideSceneCompiledUnmapped(cpu,pc,target);
            /* Every reviewed C4 action has PHP/PHD and an actual JSL/RTL
             * frame. host_return_valid is transient across native services;
             * it is not the enclosing frame's original cached _hrv. */
            uint32_t returned=(uint32_t)cpu_read8(cpu,0,(uint16_t)(entry+3))<<16 |
                (uint16_t)(cpu_read16(cpu,0,(uint16_t)(entry+1))+1u);
            RecompReturn r=interp_tier_dispatch_balanced(cpu,target,pc,entry,3,false);
            if(r==RECOMP_RETURN_NORMAL) {
                extern uint32_t g_tlk_tail_ret_pc24;
                if(cpu->S!=(uint16_t)(entry+3))PrideSceneCompiledUnmapped(cpu,pc,target);
                /* Publish the actual consumed RTL frame for an enclosing
                 * indirect-JMP bounce, just as generated RTL bodies do. */
                g_tlk_tail_ret_pc24=returned;
            }
            /* Generated hook propagation removes its one callback level. */
            return 0x80000000u|((uint32_t)r+1u);
        }
    }
    for(;;) {
        uint16_t before=cpu->S;
        cpu_mirrors_to_p(cpu);
        pride_compiled_active=1;pride_compiled_redirect=0;
        for(unsigned n=0;n<pride_compiled_count;n++)if(pride_compiled_hooks[n].pc==(pc&0x7fffff)) {
            pride_compiled_hits++;pride_compiled_hooks[n].callback(cpu,pc);
            if(pride_compiled_redirect)break;
        }
        pride_compiled_active=0;
        if(!pride_compiled_redirect)return 0;
        uint32_t target=pride_compiled_target;
        if(target!=0xc0983d && target!=0xc0a323 && target!=0xc0a073 && target!=0xc0748a) { pride_compiled_local++;return target; }
        /* Only reviewed paired wait, input and floor-contact services leave this C body.
         * Its REAL JSR/JSL frame was pushed by the original shared callback. Use
         * normal compiled/callee dispatch, then recheck the same source hook.
         * The enclosing compiled loop and hardware return context stay live. */
        unsigned frame_size=(target==0xc0a323 || target==0xc0748a)?3:2;
        if(cpu->PB!=0xc0 || cpu->S!=(uint16_t)(before-frame_size) ||
           (cpu_read16(cpu,0,(uint16_t)(cpu->S+1))+1u)!=(pc&65535u) ||
           (target==0xc0983d && pc!=0xc08808 && pc!=0xc08cce && pc!=0xc08952 && pc!=0xc08866 && pc!=0xc0d130) ||
           (target==0xc0a073 && pc!=0xc08cce && pc!=0xc08952 && pc!=0xc08866 && pc!=0xc0d130) ||
           (target==0xc0748a && (pc!=0xc08866 || cpu_read8(cpu,0,(uint16_t)(cpu->S+3))!=(pc>>16))) ||
           (target==0xc0a323 && (pc!=0xc087fe || cpu_read8(cpu,0,(uint16_t)(cpu->S+3))!=(pc>>16))))
            PrideSceneCompiledUnmapped(cpu,pc,target);
        uint8_t hrv=cpu->host_return_valid;uint32_t returned=0xffffffff;
        RecompReturn result=cpu_dispatch_call_pc_pushed(cpu,target,pc,(uint8_t)frame_size,&returned);
        cpu->host_return_valid=hrv;
        /* A real scheduler unwind or nonlocal return is propagated by the
         * generated caller exactly like an ordinary generated JSR. Its live
         * hardware frames must not be mistaken for a completed call. */
        if(result!=RECOMP_RETURN_NORMAL)return 0x80000000u|(uint32_t)result;
        /* Compiled dispatch host-returns directly and does not write the
         * optional out-PC. Interpreter fallback writes its actual popped PC.
         * The input return frame was validated above for both paths. */
        if(cpu->S!=before || (returned!=0xffffffff && returned!=pc))
            PrideSceneCompiledUnmapped(cpu,pc,returned);
        pride_compiled_services++;
    }
}
#define interp_bridge_add_pre_opcode_hook PrideRegisterOpcodeHook
#define interp_bridge_pre_opcode_redirect PrideRedirectOpcode
#endif

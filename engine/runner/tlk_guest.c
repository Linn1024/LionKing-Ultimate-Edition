#include "tlk_guest.h"
#include "common_cpu_infra.h"
RecompReturn TlkRunOriginal(CpuState *cpu,unsigned entry,unsigned frame_size) {
    uint32_t target=entry>65535 ? entry&0xffffff : ((uint32_t)cpu->PB<<16)|entry;
    uint32_t returned=0xffffffffu;
    uint16_t inherited_s=cpu->S;
    uint8_t inherited_frame=cpu->host_return_valid;
    if (cpu_take_tailcall_return_context(&inherited_s,&inherited_frame)) {
        /* A ptrtail may have pushed a callback return below its own entry S.
         * Continue through that callback until the enclosing tail routine has
         * actually returned, using the bridge's existing unwind contract. */
        cpu->host_return_valid=inherited_frame;
        return interp_tier_dispatch_tail(cpu,target,target,inherited_s,inherited_frame);
    }
    RecompReturn result=interp_tier_run_call_frame(cpu,target,target,(uint8_t)frame_size,&returned);
    /* TLK's JMP-bounce extension needs the consumed RTS/RTL address even when
     * the original body was delegated through an HLE forwarding stub. */
    if (result==RECOMP_RETURN_NORMAL && returned<=0xffffffu) {
        extern uint32_t g_tlk_tail_ret_pc24;
        g_tlk_tail_ret_pc24=returned;
    }
    return result;
}

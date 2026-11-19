#include "tlk_reset.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "cpu_state.h"
#include "beam_frame_driver.h"
#include "snes/interp_bridge.h"
#include "tlk_wide.h"

void tlk_fiber_discard(void);
void rtl_reset_audio_for_new_machine(void);
void TlkAudioMachineReset(void);
extern uint64_t g_aot_pace_next;

void TlkResetMachine(void) {
    /* A suspended compiled stack belongs to the discarded execution. */
    tlk_fiber_discard();
    /* Soft resets keep the host's master-clock origin. Reset all CPU registers
     * while retaining those monotonic clocks, as the runtime's pacing expects. */
    uint64_t master=g_cpu.master_cycles, coprocessor=g_cpu.coprocessor_master_cycles;
    cpu_state_init(&g_cpu,g_ram);
    g_cpu.master_cycles=master;g_cpu.coprocessor_master_cycles=coprocessor;
    g_aot_pace_next=0;
    interp_bridge_reset_dynamic_cache();
    snes_beam_frame_driver_reset();
    TlkWideReset();
    TlkAudioMachineReset();
    rtl_reset_audio_for_new_machine();
}

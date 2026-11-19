/* Exact interpreter-equivalent pacing for generated (AOT) code.
 *
 * The LLE step loop charges each opcode as sum(region speed of every bus
 * transfer) + 6 per remaining internal cycle, then (per opcode) charges DRAM
 * refresh, walks the beam (which latches H/V IRQs), and samples the master
 * deadline and pending IRQs before the next opcode. Generated code used to
 * charge `block cycles x code-region speed` as one lump at block entry and
 * check the deadline only per block, so long compiled loops finished at a
 * different master clock than --lle and lag frames moved (docs/devlog.md,
 * task M).
 *
 * With patches/snesrecomp/0003-aot-exact-pacing.patch the emitter charges
 * every instruction after its effects with the cost the interpreter would
 * charge (recompiler/v2/aot_pace.py, verified against interp816.c), and calls
 * aot_pace_point() at each instruction boundary. The slow path runs only when
 * master_cycles reaches g_aot_pace_next = min(next refresh line, armed
 * deadline, next H/V IRQ latch) or the interpreter's pending APU master
 * clocks reach their flush threshold; it does exactly what the step loop does
 * after an opcode (refresh, beam, SPC catch-up) and reports whether the
 * interpreter would yield before the next one (deadline reached, or IRQ
 * asserted with I clear).
 *
 * g_aot_pace_next is cleared (forcing the slow path) whenever anything other
 * than generated code advances the clock or changes the inputs: every
 * interpreted opcode, every armed deadline change, every hardware register
 * access (cmake/runtime-patches). */
#ifndef TLK_AOT_PACE_H
#define TLK_AOT_PACE_H

#include <stdint.h>
#include "cpu_state.h"

extern uint64_t g_aot_pace_next;
extern uint64_t s_apu_pending_master;   /* interp_bridge.c (runtime patch) */
extern uint64_t g_aot_apu_thresh;
/* Bus clocks of the current compiled instruction up to its data access
 * (codegen patch 0004); times an APU-port access like the interpreter. */
extern uint32_t g_aot_bus_mc;
int aot_pace_event(CpuState *cpu);
/* runner/tlk_fiber.c (task Q): suspend the compiled chain at a due yield
 * (0 = resumed in place, 1 = take the unwind), and run a memory-poll routine
 * in a nested interpreter frame (-1 = not on the fiber). */
int tlk_fiber_yield(CpuState *cpu, uint32_t resume_pc24);
int tlk_fiber_poll_entry(CpuState *cpu, uint32_t entry_pc24);
uint8_t aot_peek_slow(CpuState *cpu, uint32_t adr24);

/* cpu_region_speed (cpu_state.c), inline for generated code. */
static inline uint32_t aot_spd(uint32_t adr) {
    uint8_t bank = (uint8_t)(adr >> 16);
    uint16_t a = (uint16_t)adr;
    if (bank >= 0x40 && bank <= 0x7f) return 8;
    if (bank >= 0xc0) return g_memsel ? 6 : 8;
    if (a >= 0x8000) {
        if (bank <= 0x3f) return 8;
        return g_memsel ? 6 : 8;
    }
    if (a < 0x2000) return 8;
    if (a < 0x4000) return 6;
    if (a < 0x4200) return 12;
    if (a < 0x6000) return 6;
    return 8;
}

/* Side-effect-free byte at a 24-bit address (pointer bytes for the cost of
 * an indirect access; read before the instruction runs). */
static inline uint8_t aot_peek(CpuState *cpu, uint32_t adr24) {
    uint8_t bank = (uint8_t)(adr24 >> 16);
    uint16_t a = (uint16_t)adr24;
    if (a < 0x2000 && (bank < 0x40 || (bank >= 0x80 && bank < 0xc0)))
        return cpu->ram[a];
    return aot_peek_slow(cpu, adr24 & 0xFFFFFFu);
}
#define AOT_PEEK0(a) aot_peek(cpu, (uint32_t)((a) & 0xFFFF))
#define AOT_XCROSS(b, i) ((((uint32_t)(b) >> 8) != (((uint32_t)(b) + (uint32_t)(i)) >> 8)) ? 1u : 0u)
#define AOT_DPL ((cpu->D & 0xFF) ? 1u : 0u)

/* Charge one executed instruction; nonzero when the interpreter would stop
 * before the next instruction (deadline / IRQ). */
#ifdef AOT_PACE_TRACE
void aot_pace_trace(uint32_t pc24, uint32_t cyc, uint32_t mc);
#endif
/* Widescreen (tlk_wide.c) watches nine instructions, just after they run: the
 * first of each sprite piece writer and of the NMI's OAM upload, three in the
 * spawn window and object cull routines, and three in the ostrich ride's
 * obstacle script. pc24 is a constant at every call site, so the test folds
 * away everywhere else. The interpreter side is an interp_bridge pre-opcode
 * hook. */
extern void (*g_tlk_wide_pc_hook)(CpuState *cpu, uint32_t pc24);
extern void (*g_tlk_audio_pc_hook)(CpuState *cpu, uint32_t pc24);
extern void (*g_tlk_graveyard_gameplay_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_roar_pc_hook)(CpuState *cpu, uint32_t pc24);
extern void (*g_tlk_reactivation_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_destiny_exit_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_destiny_arena_pc_hook)(CpuState *cpu, uint32_t pc24);
extern void (*g_tlk_adult_turn_pc_hook)(CpuState *cpu, uint32_t pc24);
extern void (*g_tlk_layout_pc_hook)(CpuState *cpu, uint32_t pc24);
extern void (*g_tlk_camera_operand_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_stampede_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_gy_handoff_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_gy_bone_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_gy_input_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_cw_rhino_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_destiny_boulder_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_adult_direct_body_pc_hook)(CpuState *,uint32_t);
extern void (*g_tlk_cw_hippo_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_cw_grip_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_cw_exit_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_cw_terrain_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_scar_contact_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_adult_ledge_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_adult_hyena_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_return_hyenas_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_return_door_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_return_exit_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_scar_activation_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_be_prepared_pc_hook)(CpuState *cpu,uint32_t pc24);
extern void (*g_tlk_exile_grip_pc_hook)(CpuState *cpu,uint32_t pc24);
static inline int aot_pace_point(CpuState *cpu, uint32_t cyc, uint32_t mc,
                                 uint32_t pc24) {
#ifdef AOT_PACE_TRACE
    aot_pace_trace(pc24, cyc, mc);
#endif
    if((pc24==0xC0B7DDu || pc24==0xC0855Eu || pc24==0xC0CC53u || pc24==0xC0CC59u ||
        pc24==0xC40160u || pc24==0xC40165u) && g_tlk_be_prepared_pc_hook)g_tlk_be_prepared_pc_hook(cpu,pc24);
    if((pc24==0xC0CC53u || pc24==0xC0CC59u || pc24==0xC65D73u ||
        pc24==0xC672EFu || pc24==0xC67318u || pc24==0xC67345u) &&
       g_tlk_scar_activation_pc_hook)g_tlk_scar_activation_pc_hook(cpu,pc24);
    if(pc24==0xC0D439u && g_tlk_return_exit_pc_hook)g_tlk_return_exit_pc_hook(cpu,pc24);
    if(pc24==0xC388D8u && g_tlk_return_door_pc_hook)g_tlk_return_door_pc_hook(cpu,pc24);
    if((pc24==0xC076DBu || pc24==0xC076E9u || pc24==0xC076EEu) &&
       g_tlk_return_hyenas_pc_hook)g_tlk_return_hyenas_pc_hook(cpu,pc24);
    if((pc24==0xC1AC58u || pc24==0xC1AD80u || pc24==0xC1AEAEu ||
        pc24==0xC1AFD6u || pc24==0xC1B175u || pc24==0xC1B2ECu || pc24==0xC1B72Au || pc24==0xC1AC50u || pc24==0xC1AD78u) &&
       g_tlk_adult_hyena_pc_hook)g_tlk_adult_hyena_pc_hook(cpu,pc24);
    if((pc24==0xC66AE0u || pc24==0xC66B1Fu) && g_tlk_scar_contact_pc_hook)g_tlk_scar_contact_pc_hook(cpu,pc24);
    if((pc24==0xC38A9Fu || pc24==0xC1C04Eu || pc24==0xC1C0CFu ||
        pc24==0xC33DCFu || pc24==0xC33FB9u || pc24==0xC34007u ||
        pc24==0xC33E2Bu || pc24==0xC33E7Eu || pc24==0xC33F01u ||
        pc24==0xC34015u || pc24==0xC34068u || pc24==0xC340C6u) &&
       g_tlk_adult_ledge_pc_hook)g_tlk_adult_ledge_pc_hook(cpu,pc24);
    if(pc24==0xC1AACBu && g_tlk_destiny_exit_pc_hook)g_tlk_destiny_exit_pc_hook(cpu,pc24);
    if(pc24==0xC00F82u && g_tlk_destiny_arena_pc_hook)g_tlk_destiny_arena_pc_hook(cpu,pc24);
    if(pc24==0xC0AEBBu && g_tlk_adult_turn_pc_hook)g_tlk_adult_turn_pc_hook(cpu,pc24);
    if((pc24==0xC16A92u || pc24==0xC16BDBu) && g_tlk_camera_operand_pc_hook)
        g_tlk_camera_operand_pc_hook(cpu,pc24);
    if(pc24==0xC0E19Fu && g_tlk_stampede_pc_hook)g_tlk_stampede_pc_hook(cpu,pc24);
    if((pc24==0xC0CF10u || pc24==0xC0CF20u || pc24==0xC0CF2Fu || pc24==0xC0CF3Cu || pc24==0xC0CF9Bu || pc24==0xC0CFABu || pc24==0xC0CFBAu || pc24==0xC0CFC7u) && g_tlk_stampede_pc_hook)g_tlk_stampede_pc_hook(cpu,pc24);
    if((pc24==0xC45AFCu || pc24==0xC45B43u || pc24==0xC45EC5u || pc24==0xC45FC4u || pc24==0xC0BBF1u || pc24==0xC4627Cu || pc24==0xC1A3ACu || pc24==0xC1A3B9u || pc24==0xC28E3Eu) && g_tlk_stampede_pc_hook)g_tlk_stampede_pc_hook(cpu,pc24);
    if((pc24==0xC0D877u || pc24==0xC0D885u || pc24==0xC0D895u || pc24==0xC0D89Fu || pc24==0xC0D8B0u || pc24==0xC0D8B2u || pc24==0xC0D8EDu) && g_tlk_gy_bone_pc_hook)g_tlk_gy_bone_pc_hook(cpu,pc24);
    if((pc24==0xC32854u || pc24==0xC32FE3u) && g_tlk_gy_input_pc_hook)g_tlk_gy_input_pc_hook(cpu,pc24);
    if((pc24==0xC3316Cu || pc24==0xC33176u) && g_tlk_gy_handoff_pc_hook)g_tlk_gy_handoff_pc_hook(cpu,pc24);
    if((pc24==0xC0C875u || pc24==0xC0C893u || pc24==0xC0C89Au) && g_tlk_exile_grip_pc_hook)g_tlk_exile_grip_pc_hook(cpu,pc24);
    if((pc24==0xC0CB44u || pc24==0xC0CB52u || pc24==0xC0CB80u) && g_tlk_cw_grip_pc_hook)g_tlk_cw_grip_pc_hook(cpu,pc24);
    if(pc24==0xC0D1C3u && g_tlk_cw_exit_pc_hook)g_tlk_cw_exit_pc_hook(cpu,pc24);
    if(pc24==0xC2E855u && g_tlk_cw_rhino_pc_hook)g_tlk_cw_rhino_pc_hook(cpu,pc24);
    if((pc24==0xC0CDA1u || pc24==0xC0CDB1u || pc24==0xC0CDC0u || pc24==0xC0CDCDu ||
        pc24==0xC0CE1Du || pc24==0xC0CE2Du || pc24==0xC0CE3Cu || pc24==0xC0CE49u ||
        pc24==0xC0CF10u || pc24==0xC0CF20u || pc24==0xC0CF2Fu || pc24==0xC0CF3Cu ||
        pc24==0xC0CF9Bu || pc24==0xC0CFABu || pc24==0xC0CFBAu || pc24==0xC0CFC7u ||
        pc24==0xC0CED3u || pc24==0xC0CEE3u || pc24==0xC0CEF2u || pc24==0xC0CEFFu ||
        pc24==0xC0CF5Eu || pc24==0xC0CF6Eu || pc24==0xC0CF7Du || pc24==0xC0CF8Au) &&
       g_tlk_adult_direct_body_pc_hook)g_tlk_adult_direct_body_pc_hook(cpu,pc24);
    if(pc24==0xC0CE5Au && g_tlk_destiny_boulder_pc_hook)g_tlk_destiny_boulder_pc_hook(cpu,pc24);
    if(pc24==0xC49323u && g_tlk_cw_hippo_pc_hook)g_tlk_cw_hippo_pc_hook(cpu,pc24);
    if((pc24==0xC07A1Au || pc24==0xC0CBAFu) && g_tlk_cw_terrain_pc_hook)g_tlk_cw_terrain_pc_hook(cpu,pc24);
    if((pc24==0xC16D9Fu || pc24==0xC140A8u || pc24==0xC140C6u ||
        pc24==0xC13ED9u || pc24==0xC13F5Cu || pc24==0xC19ACDu) && g_tlk_graveyard_gameplay_pc_hook)
        g_tlk_graveyard_gameplay_pc_hook(cpu,pc24);
    if(pc24==0xC19AEEu && g_tlk_graveyard_gameplay_pc_hook)
        g_tlk_graveyard_gameplay_pc_hook(cpu,pc24+2);
    if((pc24==0xC175CDu || pc24==0xC17635u) && g_tlk_graveyard_gameplay_pc_hook)
        g_tlk_graveyard_gameplay_pc_hook(cpu,pc24+3);
    if(pc24==0xC17155u && g_tlk_graveyard_gameplay_pc_hook)
        g_tlk_graveyard_gameplay_pc_hook(cpu,pc24+2);
    /* Sound starts, bone countdown completion and pillar's native group stop.
     * Read-only observers; the three additional constant seams add no guest work. */
    if ((pc24==0xC22C2Cu || pc24==0xC19AC7u || pc24==0xC19F87u || pc24==0xC22CBFu || pc24==0xC37A32u) &&
        g_tlk_audio_pc_hook) g_tlk_audio_pc_hook(cpu,pc24);
    /* Original big-cat chase-entry sound, after its action-low store.
     * The interpreter observes BEFORE this same store to avoid yield repeats. */
    if(pc24==0xC5D241u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24);
    if(pc24==0xC37D25u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24);
    if(pc24==0xC63F64u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24);
    /* Native successful Toss contact: after storing catch count, before reward callback. */
    if(pc24==0xC545F9u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,0xC545FBu);
    if(pc24==0xC67FBAu && g_tlk_layout_pc_hook)g_tlk_layout_pc_hook(cpu,pc24);
    if(pc24==0xC68167u && g_tlk_layout_pc_hook)g_tlk_layout_pc_hook(cpu,pc24);
    if((pc24==0xC5498Du || pc24==0xC549A9u) && g_tlk_layout_pc_hook)g_tlk_layout_pc_hook(cpu,pc24);
    if(pc24==0xC07888u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24+1);
    if(pc24==0xC46BD6u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24+1);
    if(pc24==0xC46D4Au && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24+2);
    if((pc24==0xC46C88u || pc24==0xC46CCFu) && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24);
    if(pc24==0xC66538u && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24+2);
    if ((pc24==0xC67721u || pc24==0xC677E2u || pc24==0xC67831u || pc24==0xC67887u ||
         pc24==0xC678DCu || pc24==0xC6799Au || pc24==0xC679D4u || pc24==0xC679EEu ||
         pc24==0xC679F3u) && g_tlk_audio_pc_hook)g_tlk_audio_pc_hook(cpu,pc24);
    if (pc24==0xC0CC36u && g_tlk_reactivation_pc_hook) g_tlk_reactivation_pc_hook(cpu,pc24);
    if((pc24==0xC001D4u || pc24==0xC556D7u || pc24==0xC556E7u || pc24==0xC075D4u || pc24==0xC075D9u) && g_tlk_layout_pc_hook)g_tlk_layout_pc_hook(cpu,pc24);
    /* Selected immutable default-position data, immediately after LDA.
     * The original stores and checkpoint comparison remain compiled. */
    if ((pc24==0xC087B3u || pc24==0xC087BDu || pc24==0xC0881Bu || pc24==0xC08825u ||
         pc24==0xC0867Bu || pc24==0xC08687u || pc24==0xC07763u || pc24==0xC0B7DDu ||
         pc24==0xC48C5Au || pc24==0xC48C77u || pc24==0xC48E24u || pc24==0xC48F86u ||
         pc24==0xC0891Du || pc24==0xC0855Eu || pc24==0xC0856Bu || pc24==0xC0CC53u || pc24==0xC0CC59u ||
         pc24==0xC58122u || pc24==0xC58168u || pc24==0xC58170u || pc24==0xC581C8u ||
         pc24==0xC58308u || pc24==0xC58325u || pc24==0xC58454u ||
         pc24==0xC196D2u || pc24==0xC196EFu || pc24==0xC0BB2Fu || pc24==0xC0BB21u || pc24==0xC0894Cu || pc24==0xC088C7u) && g_tlk_layout_pc_hook)
        g_tlk_layout_pc_hook(cpu,pc24);
    /* Resource-selected animation data, after the original parser loads.
     * Constant PCs fold this away outside the five load instructions. */
    if ((pc24==0xC0AD4Eu || pc24==0xC0AD58u || pc24==0xC0AD62u ||
         pc24==0xC0ADD0u || pc24==0xC0ADD5u || pc24==0xC0AE39u) && g_tlk_roar_pc_hook)
        g_tlk_roar_pc_hook(cpu,pc24);
    if ((pc24 == 0xC0A727u || pc24 == 0xC0A7AEu || pc24 == 0xC0A033u || pc24 == 0xC0B915u ||
         pc24 == 0xC0A5C2u || pc24 == 0xC0A5CFu || pc24 == 0xC0B618u || pc24 == 0xC0B69Fu ||
         pc24 == 0xC0BB98u) && g_tlk_wide_pc_hook)
        g_tlk_wide_pc_hook(cpu, pc24);
    /* The waterfall's four arithmetic seams have equivalent pre-opcode
     * callbacks in LLE. Forward the preceding completed instruction here. */
    if((pc24==0xC48EF9u || pc24==0xC48F09u || pc24==0xC48F3Eu || pc24==0xC48F4Cu) && g_tlk_wide_pc_hook)
        g_tlk_wide_pc_hook(cpu,pc24+3);
    cpu->cycles += cyc;
    cpu->master_cycles += mc;
    s_apu_pending_master += mc;
    return (cpu->master_cycles >= g_aot_pace_next ||
            s_apu_pending_master >= g_aot_apu_thresh) ? aot_pace_event(cpu) : 0;
}

/* Block / function entry: the same boundary test without a charge. */
static inline int aot_pace_block(CpuState *cpu) {
    return (cpu->master_cycles >= g_aot_pace_next ||
            s_apu_pending_master >= g_aot_apu_thresh) ? aot_pace_event(cpu) : 0;
}

/* Charge without the boundary event (the next block / function entry runs
 * it), so it can be undone exactly when the interpreter re-executes the
 * instruction (unresolved indirect jump). */
static inline void aot_pace_charge(CpuState *cpu, uint32_t cyc, uint32_t mc) {
    cpu->cycles += cyc;
    cpu->master_cycles += mc;
    s_apu_pending_master += mc;
}
static inline void aot_pace_refund(CpuState *cpu, uint32_t cyc, uint32_t mc) {
    cpu->cycles -= cyc;
    cpu->master_cycles -= mc;
    s_apu_pending_master -= mc;
}

#ifdef AOT_PACE_GENERATED
/* Generated blocks test this at entry; route it through the paced check. */
#define interp_bridge_lle_master_deadline_reached(c) aot_pace_block(c)
#endif

#endif

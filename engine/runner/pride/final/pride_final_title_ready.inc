/* MD final-exit title timing. The original title actor still constructs the
 * menu and owns selection/new-game; installed media and audio are independent. */
static void ContinueTitleReadySetup(CpuState *cpu,uint32_t pc) {
    TitleOpeningControl(cpu,pc);
    (void)pc;
    if(!continue_transition_mode || !continue_title_ready_field || !final_scene_entry ||
       !final_scene_have_target || continue_title_pending || continue_transition.confirmed_field ||
       reload_fast_used || FinalAddress(0xdf)!=0xc005ab || FinalWord(0x1ff9e)!=14)return;
    unsigned now=(unsigned)snes_frame_counter+1;
    if(now<continue_title_ready_field-3)return;
    unsigned actor=FinalWord(0x68);
    if(now!=continue_title_ready_field-3 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag ||
       !cpu->D || actor<0x2000 || actor>0xffa0 || FinalWord(cpu->D)!=actor ||
       FinalAddress(actor+0x30)!=0xc462f6 || FinalWord(actor+0x2e)!=4)exit(117);
    /* Original phase4 exit values, C4657E..C465AC. Skip its native wait and
     * enter the original phase5 child/UI/menu setup, which spans three fields. */
    ReloadFastWord(actor+0x34,0);ReloadFastWord(actor+0x36,0);
    ReloadFastWord(actor+0x1c,0x77);ReloadFastWord(actor+0x1e,0x1e);
    ReloadFastWord(actor+0x2c,12);ReloadFastWord(actor+0x2e,5);
    interp_bridge_pre_opcode_redirect(0xc465c0);
}
static void ContinueTitleReadyInput(CpuState *cpu,uint32_t pc) {
    (void)pc;
    if(!continue_transition_mode || !continue_title_ready_field)return;
    unsigned now=(unsigned)snes_frame_counter+1;
    if(now<continue_title_ready_field)return;
    if(now!=continue_title_ready_field || !final_scene_entry || !final_scene_have_target ||
       continue_title_pending || continue_transition.confirmed_field || reload_fast_used ||
       FinalAddress(0xdf)!=0xc005ab || FinalWord(0x1ff9e) || cpu->D)exit(118);
    /* The outgoing button remains the previous sample until the first ready
     * field. Earlier native intro polling must not consume a held Start edge.
     * The real service computes fresh input using its live mapping/mask. */
    ReloadFastWord(0x5c,continue_title_previous_pad);
    continue_title_ready_field=continue_title_previous_pad=0;
}

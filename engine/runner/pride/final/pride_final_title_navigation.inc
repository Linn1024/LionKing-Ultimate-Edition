static int ContinueTitleNavigationSelected(void) {
    return TlkResourcesUseMd("gameplay.menus.title_navigation");
}
static void ContinueTitleNavigationInput(CpuState *cpu,uint32_t pc) {
    (void)pc;
    ReadyTitleArtObserve(cpu);
    if(!ContinueTitleNavigationSelected())return;
    /* The practice shortcut visits Options with its requested level already
     * selected. That menu owns its native input; this adapter owns level0's
     * two-choice title menu only. Do not treat another scene as a bad title. */
    if(FinalAddress(0xdf)!=0xc005ab || FinalWord(0x1ff9e))return;
    unsigned actor=FinalWord(0x68),now=(unsigned)snes_frame_counter+1;
    if(cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || !cpu->D || actor<0x2000 || actor>0xffa0 ||
       FinalWord(cpu->D)!=actor || FinalAddress(actor+0x30)!=0xc465f0 ||
       FinalWord(actor+0x2e)>1 || now>0xffffffffu-9)exit(120);
    unsigned input=TlkTitleNavigationInput(&title_navigation,now,actor,
        FinalWord(0x5c)|title_navigation_opposing_directions,
        FinalWord(0x62)|title_navigation_opposing_directions,FinalWord(actor+0x2e));
    ReloadFastWord(0x62,input);
}
static void ContinueTitleNavigationCapture(void) {
    if(!title_navigation.owner)return;
    if(!ContinueTitleNavigationSelected() || FinalAddress(0xdf)!=0xc005ab ||
       FinalWord(0x1ff9e) || FinalAddress(title_navigation.owner+0x30)!=0xc465f0)
        TlkTitleNavigationClear(&title_navigation);
}

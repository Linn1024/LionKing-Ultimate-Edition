/* Independent sunrise and title artwork; selected ending flow owns timing. */
static void EndingSunrisePaint(uint32_t *pixels,int width){
    int credits_tick=TlkEndingCreditsTick();
    if(pixels && credits_tick>=0 && TlkResourcesUseMd("graphics.ending_credits") && TlkInterlevelDataCreditsReady()){
        unsigned b=g_snes->ppu->inidisp&0x80?0:g_snes->ppu->inidisp&15;
        TlkInterlevelDataRenderCredits((unsigned)credits_tick,b,(unsigned)width,pixels);TlkFallbackCanvasOwned((unsigned)snes_frame_counter);return;
    }
    if(!pixels || (width!=256 && width!=320) ||
       FinalWord(0x1ff9e)!=9 || FinalAddress(0xdf)!=0xc007a9 ||
       FinalWord(0x2000)!=0xffff || FinalAddress(0xb217)!=0xc5858a ||
       FinalAddress(0xb243)!=0xc473e4)return;
    unsigned brightness=g_snes->ppu->inidisp&0x80?0:g_snes->ppu->inidisp&15;
    unsigned draw=FinalWord(0xb21f);
    if(TlkResourcesUseMd("graphics.ending_sunrise") && TlkInterlevelDataReady() &&
       draw>=0xdc13 && draw<=0xffe8 && FinalWord(draw+4)==0xb21b && !(g_ram[draw+9]&0x40))
        {TlkInterlevelDataRenderEnding(FinalAddress(draw+10),brightness,(unsigned)width,pixels);TlkFallbackCanvasOwned((unsigned)snes_frame_counter);}
    /* Transparent title may also be selected over the native illustration. */
    if(TlkResourcesUseMd("graphics.ending_title") && TlkEndingTitleActive())
        TlkInterlevelDataRenderEndingTitle(brightness,(unsigned)width,pixels);
}

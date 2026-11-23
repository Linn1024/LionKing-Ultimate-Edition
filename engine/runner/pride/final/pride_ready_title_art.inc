/* The native controller owns selection and input. Artwork observes the ready
 * two-choice menu independently of the title-navigation gameplay choice. */
static unsigned ready_title_art_owner;

/* Three source cards over the existing cold-start controller. Native card
 * holds remain native; the original189-field SEGA palette cycle precedes them.
 * Its countdown lives in the actual startup actor, including ordinary saves. */
static void PublisherStartup(CpuState *cpu) {
    if(!TlkResourcesUseMd("graphics.menus.publisher_cards") || continue_title_pending || final_scene_entry ||
       FinalWord(0x1ff9e)!=14 || FinalAddress(0xdf)!=0xc0057b)return;
    unsigned actor=FinalWord(0x68);
    if(cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || !cpu->D ||
       actor<0x2000 || actor>0xffa0 || FinalWord(cpu->D)!=actor ||
       FinalAddress(actor+48)!=0xc462f6 || FinalWord(actor+46) || FinalWord(actor+44)!=130)return;
    unsigned ticks=TlkFinalArtPublisherPrefixTicks(final_menu_art);
    if(ticks!=189){fprintf(stderr,"Installed publisher artwork is missing. Run Setup.\n");exit(114);}
    ReloadFastWord(actor+44,130+ticks);
}
static int PublisherPaint(uint32_t *pixels,int width) {
    unsigned actor=FinalWord(0x6e);
    if((width!=256 && width!=320) || FinalWord(0x1ff9e)!=14 || FinalAddress(0xdf)!=0xc0057b ||
       actor<0x2000 || actor>0xffa0 || FinalAddress(actor+48)!=0xc462f6)return 0;
    unsigned phase=FinalWord(actor+46),wait=FinalWord(actor+44),card,age=0;
    if(phase>3 || wait>319)return 0;
    if(phase==0){card=wait>130?0:1;if(card==0)age=319-wait;}
    else if(phase==2)card=2;
    else card=3;
    if(card==3)for(unsigned i=0;i<320*224;i++)final_menu_canvas[i]=0xff000000u;
    else if(!TlkFinalArtDrawPublisher(final_menu_art,card,age,final_menu_canvas)) {
        fprintf(stderr,"Installed publisher artwork is missing. Run Setup.\n");exit(114);
    }
    for(unsigned y=0;y<224;y++)memcpy(pixels+y*width,final_menu_canvas+y*320+(width==256?32:0),(size_t)width*sizeof *pixels);
    return 1;
}

/* Native startup actor owns the countdown, so ordinary saves already retain
 * this presentation clock. Its phase9 setup and nine-field delay precede the
 * native140-update animation. Original MD first Simba submission is age2. */
static int TitleOpeningPaint(uint32_t *pixels,int width){
    unsigned actor=FinalWord(0x6e),level=FinalWord(0x1ff9e);
    if((width!=256 && width!=320) || (level!=14 && level!=0) ||
       FinalAddress(0xdf)!=0xc005ab || actor<0x2000 || actor>0xffa0 ||
       (FinalAddress(actor+0x30)!=0xc462f6 &&
        !(FinalAddress(actor+0x30)==0xc465f0 && FinalWord(actor+0x2e)==5 &&
          !FinalWord(actor+0x34))))return 0;
    unsigned phase=FinalWord(actor+0x2e),wait=FinalWord(actor+0x2c),remaining=FinalWord(actor+0x34),age;
    if(remaining>140 || wait>12)return 0;
    if(phase==3)age=0;
    else if(phase==9)age=0;
    else if(phase==4)age=1+(9-(wait>9?9:wait))+(140-remaining);
    else if(phase==5)age=150;
    else return 0;
    if(!(phase==3?TlkFinalArtDrawTitleBackdrop(final_menu_art,final_menu_canvas):TlkFinalArtDrawTitleOpening(final_menu_art,age,final_menu_canvas))){
        fprintf(stderr,"Installed title opening artwork is missing. Run Setup.\n");exit(114);
    }
    for(unsigned y=0;y<224;y++)memcpy(pixels+y*width,final_menu_canvas+y*320+(width==256?32:0),(size_t)width*sizeof *pixels);
    return 1;
}
static void TitleOpeningControl(CpuState *cpu,uint32_t pc){
    if(pc!=0xc463fc || !TlkResourcesUseMd("gameplay.menus.title_navigation") ||
       continue_title_ready_field || continue_title_pending ||
       FinalAddress(0xdf)!=0xc005ab || FinalWord(0x1ff9e)!=14)return;
    unsigned actor=FinalWord(0x68);
    if(cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || !cpu->D ||
       actor<0x2000 || actor>0xffa0 || actor!=FinalWord(0x6e) ||
       FinalWord(cpu->D)!=actor || FinalAddress(actor+0x30)!=0xc462f6 ||
       FinalWord(actor+0x2e)!=4 || FinalWord(actor+0x2c))return;
    unsigned remaining=FinalWord(actor+0x34);
    if(!remaining || remaining>31)return;
    /* MD builds its choices at opening age123. Begin the same reviewed native
     * three-field UI construction used by Continue return at age120. Keep its
     * real child creation, input edges, DMA, settings and new-game handling. */
    ReloadFastWord(actor+0x34,0);ReloadFastWord(actor+0x36,0);
    ReloadFastWord(actor+0x1c,0x77);ReloadFastWord(actor+0x1e,0x1e);
    ReloadFastWord(actor+0x2c,12);ReloadFastWord(actor+0x2e,5);
    interp_bridge_pre_opcode_redirect(0xc465c0);
}

static void ReadyTitleArtObserve(CpuState *cpu) {
    if(FinalAddress(0xdf)!=0xc005ab) {ready_title_art_owner=0;return;}
    unsigned actor=FinalWord(0x68);
    if(cpu->DB==0x7e && !cpu->m_flag && !cpu->x_flag && cpu->D &&
       actor>=0x2000 && actor<=0xffa0 && FinalWord(cpu->D)==actor &&
       FinalAddress(actor+0x30)==0xc465f0 && FinalWord(actor+0x2e)<=1)
        ready_title_art_owner=actor;
    else ready_title_art_owner=0;
}
static void ReadyTitleArtPaint(uint32_t *pixels,int width) {
    if(TlkResourcesUseMd("graphics.menus.publisher_cards") && PublisherPaint(pixels,width)){TlkFallbackCanvasOwned((unsigned)snes_frame_counter);return;}
    if(TlkResourcesUseMd("graphics.menus.title") && TitleOpeningPaint(pixels,width)){TlkFallbackCanvasOwned((unsigned)snes_frame_counter);return;}
    /* The real ready controller may initialize its selection before the first
     * input callback. Reconstruct this derived owner from its validated root.
     * Level select retains its chosen stage in1FF9E while this same title
     * controller is active; that stage is not an artwork ownership test. */
    unsigned root=FinalWord(0x6e);
    int menu_root=root>=0x2000 && root<=0xffa0 && FinalAddress(0xdf)==0xc005ab;
    unsigned action=menu_root?FinalAddress(root+0x30):0;
    unsigned selection=menu_root?FinalWord(root+0x2e):0;
    /* Native Options constructs its rows over three updates. New Game keeps
     * the outgoing title alive through its brightness fade. Both still own
     * the title canvas; neither should expose its native artwork underneath. */
    int options_entry=action==0xc4690e && selection==0xffff;
    /* Exit retains Options row5/cursor position until the ready controller's
     * next update. It is not the startup phase5 with an exhausted countdown. */
    int options_return=action==0xc465f0 && selection>=2 && selection<=5 && FinalWord(root+0x34)!=0;
    int game_fade=action==0xc470d2 && selection==0;
    if(options_entry || options_return || game_fade)ready_title_art_owner=root;
    if(root>=0x2000 && root<=0xffa0 && FinalAddress(0xdf)==0xc005ab &&
       FinalAddress(root+0x30)==0xc465f0 && FinalWord(root+0x2e)<=1)
        ready_title_art_owner=root;
    if(!TlkResourcesUseMd("graphics.menus.title") || !ready_title_art_owner ||
       FinalAddress(0xdf)!=0xc005ab ||
       (!options_entry && !options_return && !game_fade &&
        (FinalAddress(ready_title_art_owner+0x30)!=0xc465f0 ||
         FinalWord(ready_title_art_owner+0x2e)>1)) || (width!=256 && width!=320))return;
    /* Decorative horizontal selector bob; no gameplay clock or ROM code runs.
     * Native saved field count preserves this small continuous animation. */
    unsigned phase=(unsigned)(snes_frame_counter%22),bob=128-(phase<11?phase:21-phase);
    unsigned selected=options_entry?1:(options_return || game_fade)?0:FinalWord(ready_title_art_owner+0x2e);
    if(!TlkFinalArtDrawReadyTitle(final_menu_art,selected,bob,final_menu_canvas)) {
        fprintf(stderr,"Installed title menu artwork is missing. Run Setup.\n");exit(114);
    }
    unsigned brightness=game_fade?(g_snes->ppu->inidisp&0x80?0:g_snes->ppu->inidisp&15):15;
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<(unsigned)width;x++) {
        uint32_t color=final_menu_canvas[y*320+x+(width==256?32:0)];
        if(game_fade) {
            uint32_t faded=0xff000000u;
            for(unsigned shift=0;shift<24;shift+=8) {
                unsigned v=((color>>shift)&255)>>3;v=v*brightness/15;
                faded|=((v<<3)|(v>>2))<<shift;
            }
            color=faded;
        }
        pixels[y*width+x]=color;
    }
    TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
}

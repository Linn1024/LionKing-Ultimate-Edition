/* Installed MD pictures/programs over the native final-menu lifetime.
 * Guest controls, counters, scene duration and brightness remain native. */
static unsigned native_menu_armed,native_menu_active,native_menu_exiting;
static unsigned native_menu_updates,native_menu_credits,native_menu_no;
static unsigned native_menu_confirmed,native_menu_confirm_updates;
static int NativeMenuEnabled(void) {
    return final_menu_art_mode && !continue_transition_mode;
}
static int NativeMenuOwned(void) {return NativeMenuEnabled() && native_menu_armed;}
static void NativeMenuClear(void) {
    native_menu_armed=native_menu_active=native_menu_exiting=0;
    native_menu_updates=native_menu_credits=native_menu_no=0;
    native_menu_confirmed=native_menu_confirm_updates=0;
}
static void NativeMenuEvent(unsigned event) {
    if(!NativeMenuEnabled())return;
    unsigned scene=FinalAddress(0xdf);
    if(event==NATIVE_MENU_BEGIN && !FinalWord(0x1ff9e) && !FinalWord(0x2000) &&
       !FinalWord(0x2004) && !FinalWord(0x1ffaa) && FinalWord(0x1ffa8)<=9 &&
       (scene==0xc00387 || scene==0xc0080d) && FinalAddress(0xb243)==0xc35a82) {
        NativeMenuClear();native_menu_armed=1;native_menu_credits=FinalWord(0x1ffa8);
    }
    if(!native_menu_armed)return;
    if(event==NATIVE_MENU_LOOP && scene==0xc0057b && !native_menu_exiting) {
        if(native_menu_active)native_menu_updates++;
        else native_menu_active=1;
    }
    if(event==NATIVE_MENU_CONFIRM && native_menu_active && native_menu_credits) {
        native_menu_confirmed=(unsigned)snes_frame_counter+1;
        native_menu_confirm_updates=native_menu_updates;
        native_menu_exiting=1;native_menu_no=0;
    }
    if(event==NATIVE_MENU_TITLE_EXIT && native_menu_active)native_menu_exiting=1;
    if(event==NATIVE_MENU_FRAME && native_menu_active) {
        if(!native_menu_exiting && native_menu_credits) {
            unsigned cursor=FinalWord(0xa68e);
            /* Confirmation cleanup reuses this pointer. Read only during the
             * owned selector loop and retain its choice/count for the exit. */
            if(cursor<0xb213 || cursor>=0xc213 || ((cursor-0xb213)&127))exit(123);
            native_menu_no=FinalWord(cursor+8)>=64;
        }
        if((native_menu_exiting && !(g_snes->ppu->inidisp&15)) ||
           (!native_menu_exiting && scene!=0xc0057b))NativeMenuClear();
    }
}
static void NativeMenuPaint(uint32_t *pixels,int width) {
    if(!NativeMenuEnabled() || !native_menu_active || (width!=256 && width!=320))return;
    unsigned now=(unsigned)snes_frame_counter;
    /* The frontend transports the256 centre after drawing the wide sides.
     * Anchor HUDs to the selected viewport, even for that centre buffer. */
    unsigned viewport=(unsigned)WideWidth();
    int ok;
    if(native_menu_confirmed) {
        if(now<native_menu_confirmed)exit(123);
        unsigned confirmed_age=124+native_menu_confirm_updates;
        ok=TlkFinalArtDrawConfirmedMenuViewport(final_menu_art,confirmed_age+now-native_menu_confirmed,
            confirmed_age,native_menu_credits,viewport,final_menu_canvas);
    } else ok=TlkFinalArtDrawMenuViewport(final_menu_art,124+native_menu_updates,
        native_menu_credits,native_menu_no,viewport,final_menu_canvas);
    if(!ok)exit(123);
    unsigned brightness=g_snes->ppu->inidisp&0x80?0:g_snes->ppu->inidisp&15;
    unsigned start=(320-width)/2;
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<(unsigned)width;x++) {
        uint32_t c=final_menu_canvas[y*320+x+start],rgb=0xff000000u;
        for(unsigned shift=0;shift<24;shift+=8) {
            unsigned v=(c>>shift&255)>>3;v=v*brightness/15;rgb|=((v<<3)|(v>>2))<<shift;
        }
        pixels[y*width+x]=rgb;
    }
    TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
}

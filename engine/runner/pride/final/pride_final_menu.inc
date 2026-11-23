/* Development integration of installed MD artwork for final menus.
 * No ROM preparation is linked here. Source-tree activation follows complete
 * native-timeline and remaining context coverage, which remain separate work. */
static TlkFinalArt *final_menu_art;
static uint32_t final_menu_canvas[320*224];
static int ContinueMenuSource(void) {
    if(TlkResourcesUseMd("graphics.pride_final_menu"))return 1;
    const char *mode=getenv("TLK_FINAL_MD_ART");return mode && !strcmp(mode,"1");
}
static int ContinueMenuAssetsLoad(const char *path) {
    final_menu_art_mode=ContinueMenuSource();
    const char *timing=ContinueModeSetting("TLK_CONTINUE_TRANSITION");
    if(final_menu_art_mode && !TlkResourcesUseMd("graphics.pride_final_menu") && (!timing || strcmp(timing,"1"))) {
        fprintf(stderr,"Development MD menu art requires the reviewed MD final-life timeline\n");return 0;
    }
    size_t size=0;uint8_t *data=path?read_file(path,&size):NULL;
    final_menu_art=data?TlkFinalArtLoad(data,size):NULL;
    if(!final_menu_art || !TlkFinalArtDrawMenu(final_menu_art,118,0,0,final_menu_canvas)) {
        free(data);TlkFinalArtFree(final_menu_art);final_menu_art=NULL;
        fprintf(stderr,"Installed menu assets are missing or incompatible. Run Setup.\n");return 0;
    }
    TlkAudioSetSoundTestAssets(final_menu_art);
    sha256_compute(data,size,final_menu_asset_digest);free(data);return 1;
}
static void ContinueMenuDraw(void) {
    unsigned credits=FinalWord(0x1ffa8),selected=0;
    if(credits) {
        /* Native C08D2A/C08D60: A68E is the selector actor, whose X word at8
         * selects YES below64 and NO otherwise. It is not a boolean choice. */
        unsigned actor=FinalWord(0xa68e);
        if(actor<0x2000 || actor>0xfff6) {
            fprintf(stderr,"Invalid menu cursor %x at age %u\n",actor,final_scene_age);exit(114);
        }
        selected=FinalWord(actor+8)>=0x40;
    }
    if(!TlkFinalArtDrawMenuViewport(final_menu_art,final_scene_age,credits,selected,(unsigned)WideWidth(),final_menu_canvas))exit(114);
}
static void ContinueMenuCapture(const uint8_t *native,uint32_t *centre,uint32_t *sides) {
    if(!final_menu_art_mode){memcpy(centre,native,256*224*sizeof *centre);return;}
    ContinueMenuDraw();ContinueSplitCanvas(final_menu_canvas,320,centre,sides);
}
static void ContinueMenuConfirmedCapture(uint32_t *centre,uint32_t *sides) {
    uint64_t confirmed=continue_transition.confirmed_field;
    if(confirmed<final_scene_entry || confirmed-final_scene_entry>UINT32_MAX ||
       !TlkFinalArtDrawConfirmedMenuViewport(final_menu_art,final_scene_age,
          (uint32_t)(confirmed-final_scene_entry),final_menu_confirmed_credits,(unsigned)WideWidth(),final_menu_canvas)) {
        fprintf(stderr,"Invalid confirmed drawing: age %u confirm %llu entry %u credits %u\n",
            final_scene_age,(unsigned long long)confirmed,final_scene_entry,final_menu_confirmed_credits);exit(114);
    }
    ContinueSplitCanvas(final_menu_canvas,320,centre,sides);
}
static void ContinueMenuPaint(uint32_t *pixels,int width) {
    if(!final_menu_art_mode || !final_scene_entry || final_scene_age<121 ||
       continue_title_fade_field || continue_transition.confirmed_field || FinalAddress(0xdf)!=0xc0057b)return;
    ContinueMenuDraw();
    for(unsigned y=0;y<224;y++) {
        if(width==256)memcpy(pixels+y*256,final_menu_canvas+y*320+32,256*sizeof *pixels);
        else {
            memcpy(pixels+y*320,final_menu_canvas+y*320,32*sizeof *pixels);
            memcpy(pixels+y*320+288,final_menu_canvas+y*320+288,32*sizeof *pixels);
        }
    }
    TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
}

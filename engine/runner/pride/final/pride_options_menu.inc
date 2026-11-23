/* Options art and input are independent choices. Native handlers still own
 * setting updates, sound cues, redraws and the return to the title. */
static unsigned options_art_owner,options_direction;
static int OptionsMenuActor(unsigned *out) {
    unsigned actor=FinalWord(0x68);
    if(FinalAddress(0xdf)!=0xc005ab || actor<0x2000 || actor>0xffa0 ||
       FinalAddress(actor+0x30)!=0xc4690e)return 0;
    *out=actor;return 1;
}
static void OptionsMenuOpcode(CpuState *cpu,uint32_t pc) {
    unsigned actor;
    if(!OptionsMenuActor(&actor)){if(pc==0xc4695c)options_art_owner=0;return;}
    if(pc==0xc4695c){options_art_owner=actor;return;}
    if(!TlkResourcesUseMd("gameplay.menus.options_navigation"))return;
    unsigned row=FinalWord(actor+0x2e);
    if(pc==0xc469c2) {
        if(row>5 || cpu->m_flag || cpu->x_flag || cpu->DB!=0x7e)return;
        unsigned input=FinalWord(0x62);options_direction=(input&0x200)?2:1;
        unsigned confirm=input&0xc080;
        /* Original MD directions adjust values; native uses its normal
         * confirmation path. Left/right do not open the sound-test submenu. */
        if(row<5 && row!=3 && (input&0x300)){input|=0x80;confirm=1;}
        if(row==5 && confirm)input=(input&~0xc080u)|0x1000;
        if(!confirm && !(input&0x1000)) {
            /* Let the original directional path issue its cursor sound.
             * The temporary neighbour wraps to the desired real row. */
            if(row==0 && (input&0x800)){ReloadFastWord(actor+0x2e,6);ReloadFastWord(actor+0x36,0xb8);}
            else if(row==5 && (input&0x400)){ReloadFastWord(actor+0x2e,0xffff);ReloadFastWord(actor+0x36,0x48);}
        }
        ReloadFastWord(0x62,input);return;
    }
    if((pc==0xc46b16 || pc==0xc46b4d) && row==5 && cpu->A==5 && !cpu->m_flag) {
        /* Exit is the sixth MD row. Preserve the native cursor cue and
         * skip its five-row clamp through the existing comparison paths. */
        cpu->A=4;return;
    }
    if(pc==0xc3be21 && !cpu->m_flag && !cpu->x_flag && !cpu->D) {
        unsigned setting=FinalWord((cpu->S+6)&65535);if(setting!=row || row>4 || row==3)return;
        unsigned current=FinalWord(0x1ff92+row*2),next,count=row==0?3:row==1?3:row==2?2:6;
        if(current>=count)return;
        if(row==1)next=current?0:1; /* MD has enabled/disabled, no mono stop. */
        else if(row==4) {
            /* Native physical A/Y/B labels remain truthful. These are the
             * same action permutations in original MD preset order. */
            static const unsigned native_for_md[6]={0,3,1,2,4,5};unsigned index=0;
            while(index<6 && native_for_md[index]!=current)index++;
            if(index==6)return;next=native_for_md[(index+(options_direction==2?5:1))%6];
        } else next=(current+(options_direction==2?count-1:1))%count;
        /* C3BE1C performs its ordinary increment, audio and redraw. */
        ReloadFastWord(0x1ff92+row*2,(next+count-1)%count);
    }
}
static void OptionsMenuInstall(void) {
    TlkAttractInstall();
    static const uint32_t pcs[]={0xc4695c,0xc469c2,0xc46b16,0xc46b4d,0xc3be21};
    for(unsigned i=0;i<sizeof pcs/sizeof *pcs;i++)if(!interp_bridge_add_pre_opcode_hook(pcs[i],OptionsMenuOpcode))exit(120);
}
static int OptionsMenuBindings(unsigned layout,char out[3]) {
    if(layout>5)return 0;
    /* Original native physical->canonical masks at C3BED8/E2/EC; layout0
     * is the normal identity case. Inverse lookup labels actual controls. */
    static const unsigned remap[3][5]={{0x8000,0x4000,0x80,0x8000,0x4000},
        {0x80,0x80,0x4000,0x4000,0x8000},{0x4000,0x8000,0x8000,0x80,0x80}};
    static const unsigned masks[3]={0x80,0x4000,0x8000};
    static const unsigned physical_masks[3]={0x80,0x8000,0x4000};
    static const char physical_names[3]={'a','b','y'};
    for(unsigned action=0;action<3;action++) {
        unsigned physical;for(physical=0;physical<3;physical++) {
            unsigned canonical=layout?remap[physical][layout-1]:physical_masks[physical];
            if(canonical==masks[action])break;
        }
        if(physical==3)return 0;out[action]=physical_names[physical];
    }
    return 1;
}
static void OptionsMenuPaint(uint32_t *pixels,int width) {
    unsigned audition=FinalWord(0x6e);
    if(TlkResourcesUseMd("graphics.menus.level_select") && FinalAddress(0xdf)==0xc005ab &&
       audition>=0x2000 && audition<=0xffa0 && FinalAddress(audition+0x30)==0xc46e59 &&
       (width==256 || width==320)) {
        unsigned phase=(unsigned)(snes_frame_counter%22),bob=31-(phase<11?phase:21-phase);
        if(!TlkFinalArtDrawDebugMenu(final_menu_art,FinalWord(audition+0x2e),bob,
            FinalWord(0x1ff9c),FinalWord(0x1ff9e),final_menu_canvas)) {
            fprintf(stderr,"Installed level-select artwork unavailable. Run Setup.\n");exit(114);
        }
        for(unsigned y=0;y<224;y++)memcpy(pixels+y*width,final_menu_canvas+y*320+(width==256?32:0),(size_t)width*sizeof *pixels);
        TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
        return;
    }
    /* The native root already owns its initialized row before its old cursor
     * pointer is retired. Derive this artwork owner after ordinary restores too. */
    if(audition>=0x2000 && audition<=0xffa0 && FinalAddress(0xdf)==0xc005ab &&
       FinalAddress(audition+0x30)==0xc4690e && FinalWord(audition+0x2e)<=5)
        options_art_owner=audition;
    if(FinalAddress(0xdf)==0xc005ab &&
       audition>=0x2000 && audition<=0xffa0 && FinalAddress(audition+0x30)==0xc46b68 &&
       (width==256 || width==320)) {
        int catalogue_md=TlkResourcesUseMd("audio.music.sound_test");
        if(!TlkResourcesUseMd("graphics.menus.sound_test")) {
            if(catalogue_md) {
                char names[16][21];
                for(unsigned i=0;i<16;i++)if(!TlkFinalArtSoundTestName(final_menu_art,1,i,names[i])) {
                    fprintf(stderr,"Installed Sound Test catalogue unavailable. Run Setup.\n");exit(114);
                }
                SoundTestNativeRows(pixels,width,names);
            }
            return;
        }
        unsigned phase=(unsigned)(snes_frame_counter%22),bob=80-(phase<11?phase:21-phase);
        if(!TlkFinalArtDrawSoundTestCatalog(final_menu_art,catalogue_md,FinalWord(audition+0x2e),bob,final_menu_canvas)) {
            fprintf(stderr,"Installed Sound Test artwork unavailable. Run Setup.\n");exit(114);
        }
        for(unsigned y=0;y<224;y++)memcpy(pixels+y*width,final_menu_canvas+y*320+(width==256?32:0),(size_t)width*sizeof *pixels);
        TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
        return;
    }
    if(!options_art_owner ||
       FinalAddress(0xdf)!=0xc005ab || FinalAddress(options_art_owner+0x30)!=0xc4690e ||
       FinalWord(options_art_owner+0x2e)>5 || (width!=256 && width!=320))return;
    if(!TlkResourcesUseMd("graphics.menus.options")) {
        /* Keep the native source's existing label-construction boundary. */
        if(FinalWord(0xa68e))return;
        if(!TlkResourcesUseMd("gameplay.menus.options_navigation"))return;
        /* The added Exit row also needs its native-source label. The original
         * Options font is already decoded in BG3 VRAM (C537F3/C5383D).
         * Read those same2bpp glyphs/palette; do not substitute MD artwork. */
        const Ppu *ppu=g_snes->ppu;const char *text="EXIT";
        for(unsigned i=0;i<4;i++)for(unsigned y=0;y<8;y++)for(unsigned x=0;x<8;x++) {
            unsigned tile=0x100+(unsigned char)text[i]-32;
            unsigned bits=ppu->vram[(PPU_bgTileAdr(ppu,2)+tile*8+y)&0x7fff];
            unsigned index=((bits>>(7-x))&1)|(((bits>>(15-x))&1)<<1);
            if(index) {
                unsigned c=ppu->cgram[12+index];uint32_t color=0xff000000u;
                for(unsigned j=0;j<3;j++){unsigned v=(c>>(j*5))&31;color|=((v<<3)|(v>>2))<<((2-j)*8);}
                pixels[(160+y)*width+40+(width==320?32:0)+i*8+x]=color;
            }
        }
        return;
    }
    unsigned phase=(unsigned)(snes_frame_counter%22),bob=48-(phase<11?phase:21-phase);char buttons[3];
    if(!OptionsMenuBindings(FinalWord(0x1ff9a),buttons) ||
       !TlkFinalArtDrawOptions(final_menu_art,FinalWord(options_art_owner+0x2e),bob,
           FinalWord(0x1ff92),FinalWord(0x1ff94)!=0,FinalWord(0x1ff96)!=0,buttons,final_menu_canvas)) {
        fprintf(stderr,"Installed Options artwork or settings unavailable. Run Setup.\n");exit(114);
    }
    for(unsigned y=0;y<224;y++)memcpy(pixels+y*width,final_menu_canvas+y*320+(width==256?32:0),(size_t)width*sizeof *pixels);
    TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
}

/* Private presentation-only recomposition of the fully initialized Pride field.
 * Retain every captured layer, scroll, object, colour-math and source choice;
 * override only master brightness on the host snapshot, never guest registers. */
int SoundTestNativeRows(uint32_t *out,int width,const char names[16][21]) {
    if(!out || !names || !s_frame.valid || (width!=256 && width!=320) ||
       rd24(s_frame.ram+0xdf)!=0xc005ab)return 0;
    unsigned actor=rd16(s_frame.ram+0x6e);
    if(actor<0x2000 || actor>0xffa0 || rd24(s_frame.ram+actor+48)!=0xc46b68)return 0;
    unsigned selected=rd16(s_frame.ram+actor+46);if(selected>=16)return 0;
    for(unsigned y=96;y<136;y++)if((s_frame.lines[y].bgmode&7)!=1)return 0;
    for(unsigned i=0;i<5;i++)memcpy(s_sound_test_text[i],names[(selected+i+14)%16],21);
    static uint32_t scratch[256*224];TlkWideStats saved=s_stats;
    if(!PrideNativeWideDraw(scratch,256,false)){s_stats=saved;return 0;}
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_SOUND_TEST_ART_TRACE");if(p)trace=fopen(p,"w");
        if(trace)fputs("field,width,selection,native_base_mismatch,changed_pixels,row0,row1,row2,row3,row4\n",trace);}
    unsigned mismatch=0,changed=0;uint32_t row[256];
    for(unsigned y=96;y<136;y++) {
        if(trace) {
            ComposeLine(row,256,0,(int)y);
            for(unsigned x=72;x<232;x++)mismatch+=(row[x]&0xffffff)!=(s_frame.stock[y*256+x]&0xffffff);
        }
        s_sound_test_text_on=1;ComposeLine(row,256,0,(int)y);s_sound_test_text_on=0;
        for(unsigned x=72;x<232;x++) {
            changed+=(row[x]&0xffffff)!=(s_frame.stock[y*256+x]&0xffffff);
            out[y*width+(width-256)/2+x]=row[x];
        }
    }
    s_stats=saved;
    if(trace){extern int snes_frame_counter;fprintf(trace,"%u,%d,%u,%u,%u",(unsigned)snes_frame_counter,width,selected,mismatch,changed);
        for(unsigned i=0;i<5;i++)fprintf(trace,",%s",s_sound_test_text[i]);fputc('\n',trace);fflush(trace);}
    return 1;
}
int BonusResultOriginCanvas(uint32_t *out,int width,int hud){
    if(!out || !s_frame.valid || !s_frame.stage || rd16(s_frame.ram+0x1ff9e)!=10 ||
       rd24(s_frame.ram+0xdf)!=0xc005dd || (width!=256 && width!=320))return 0;
    TlkWideStats stats=s_stats;int ok=PrideNativeWideDraw(out,width,hud!=0);s_stats=stats;return ok;
}
int ContinueTransitionOriginCanvas(uint32_t *out,int width,int hud) {
    if(!out || !s_frame.valid || !s_frame.stage || rd16(s_frame.ram+0x1ff9e) ||
       (rd16(s_frame.ram+0xdf)!=0x387 && rd16(s_frame.ram+0xdf)!=0x80d))return 0;
    if(width!=256 && width!=320)return 0;
    static uint32_t selected[320*TLK_WIDE_HEIGHT];
    TlkWideStats stats=s_stats;
    int ok=PrideNativeWideDraw(selected,width,hud!=0);
    s_stats=stats;
    if(ok)memcpy(out,selected,(size_t)width*TLK_WIDE_HEIGHT*sizeof *out);
    return ok;
}
int ContinueTransitionFullCanvas(uint32_t *out,int width,int hud) {
    if(!out || !s_frame.valid || !s_frame.stage || rd16(s_frame.ram+0x1ff9e) ||
       rd16(s_frame.ram+0xdf)!=0x387 || (width!=256 && width!=320))return 0;
    uint8_t saved[TLK_WIDE_HEIGHT];
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        const Line *l=&s_frame.lines[y];
        if((l->inidisp&0x80) || !LineHasStage(l))return 0;
        saved[y]=l->inidisp;
    }
    TlkWideStats stats=s_stats;
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++)s_frame.lines[y].inidisp=(saved[y]&0xf0)|15;
    int ok=PrideNativeWideDraw(out,width,hud!=0);
    if(s_stats.fallback_lines)ok=0;
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++)s_frame.lines[y].inidisp=saved[y];
    s_stats=stats;return ok;
}

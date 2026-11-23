/* Excluded native-art presentation prototype. The reviewed fast loader runs
 * first; this component freezes the actual last-hit picture and destination,
 * and holds the original coordinator with its real wait service. */
static unsigned final_scene_mode,final_scene_installed,final_scene_entry,final_scene_age;
static unsigned final_scene_have_origin,final_scene_have_target,final_scene_waiting;
static uint32_t final_scene_origin[256*224],final_scene_target[256*224];
static uint16_t final_scene_a,final_scene_x,final_scene_y,final_scene_s,final_scene_d;
static uint8_t final_scene_p,final_scene_db;
static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {
    NativeMenuEvent(NATIVE_MENU_BEGIN);
    (void)cpu;(void)pc;
    if(!final_scene_mode || final_scene_entry || FinalWord(0x1ff9e) || FinalWord(0x2000) ||
       FinalWord(0x2004) || FinalWord(0x1ffaa) ||
       (FinalAddress(0xdf)!=0xc00387 && FinalAddress(0xdf)!=0xc0080d) ||
       FinalAddress(0xb243)!=0xc35a82)return;
    final_scene_entry=(unsigned)snes_frame_counter+1;
}
static void FinalSceneHold(CpuState *cpu,uint32_t pc) {
    (void)pc;
    if(!final_scene_mode || !final_scene_entry)return;
    if(final_scene_waiting) {
        if(cpu->S!=final_scene_s)exit(101);
        cpu->A=final_scene_a;cpu->X=final_scene_x;cpu->Y=final_scene_y;cpu->D=final_scene_d;
        cpu->DB=final_scene_db;cpu->P=final_scene_p;cpu_p_to_mirrors(cpu);final_scene_waiting=0;
    }
    unsigned age=(unsigned)snes_frame_counter+1-final_scene_entry;
    if(age<90 || age>=121)return;
    if(FinalAddress(0xdf)!=0xc0057b || FinalWord(0x1ff9e) || cpu->D || cpu->DB ||
       cpu->m_flag || !cpu->x_flag || cpu->S!=0x2ee)exit(101);
    final_scene_a=cpu->A;final_scene_x=cpu->X;final_scene_y=cpu->Y;final_scene_s=cpu->S;
    final_scene_d=cpu->D;final_scene_db=cpu->DB;cpu_mirrors_to_p(cpu);final_scene_p=cpu->P;
    final_scene_waiting=1;
    cpu_write8(cpu,0,cpu->S--,0x8d);cpu_write8(cpu,0,cpu->S--,0x82);
    interp_bridge_pre_opcode_redirect(0xc0983d);
}
void FinalSceneCaptureNative(const uint8_t *pixels) {
    if(!final_scene_mode || !final_scene_entry)return;
    final_scene_age=(unsigned)snes_frame_counter-final_scene_entry;
    if(!final_scene_age && !final_scene_have_origin) {
        memcpy(final_scene_origin,pixels,sizeof final_scene_origin);final_scene_have_origin=1;
    }
    if(final_scene_age==90 && !final_scene_have_target) {
        memcpy(final_scene_target,pixels,sizeof final_scene_target);final_scene_have_target=1;
    }
}
static void FinalScenePaintInitialPlane(uint32_t *pixels,unsigned count,
    const uint32_t *origin,const uint32_t *target) {
    if(!final_scene_mode || !final_scene_entry || final_scene_age>=121)return;
    if(!final_scene_have_origin || (final_scene_age>=97 && !final_scene_have_target))exit(102);
    const uint32_t *source=final_scene_age<25?origin:target;
    for(unsigned i=0;i<count;i++) {
        uint32_t rgb=0;
        for(unsigned shift=0;shift<24;shift+=8) {
            unsigned c=(source[i]>>shift&255)>>3;
            if(final_scene_age<25) {
                unsigned step=(final_scene_age+2)/3;
                unsigned loss=(step*31+3)/7;c=c>loss?c-loss:0;
            } else if(final_scene_age<97)c=0;
            else { unsigned step=(final_scene_age-97)/3;
                unsigned rise=final_menu_art_mode?(step*4+(step>>2)):(step*31+3)/7;
                c=c<rise?c:rise; }
            rgb|=((c<<3)|(c>>2))<<shift;
        }
        pixels[i]=(pixels[i]&0xff000000u)|rgb;
    }
}
void FinalScenePaintNative(uint32_t *pixels) {
    FinalScenePaintInitialPlane(pixels,256*224,final_scene_origin,final_scene_target);
}
_Bool __wrap_RtlRunFrame(uint32 inputs) {
    if(!final_scene_installed) {
        const char *mode=getenv("TLK_FINAL_SCENE_PRESENT");final_scene_mode=mode && !strcmp(mode,"1");
        if(!interp_bridge_add_pre_opcode_hook(0xc089b9,FinalSceneBegin) ||
           !interp_bridge_add_pre_opcode_hook(0xc08d83,FinalSceneHold))exit(101);
        final_scene_installed=1;
    }
    return FinalSceneRunNative(inputs);
}

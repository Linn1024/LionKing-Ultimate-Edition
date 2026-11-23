/* Native Pride completion controller. Original wait/input services retain their
 * real hardware frames. The installed data supplies drawings and schedules. */
static unsigned interlevel_installed,interlevel_finished,interlevel_pending,interlevel_field;
static uint32_t interlevel_canvas[320*224];
static struct {uint16_t a,x,y,d,s;uint8_t db,p,pb;} interlevel_cpu;
#include "pride_cliff.inc"
static void InterlevelClear(void){
    CliffClear();
    TlkInterlevelSceneClear();interlevel_finished=interlevel_pending=interlevel_field=0;
    memset(&interlevel_cpu,0,sizeof interlevel_cpu);
}
static void InterlevelRestore(CpuState *cpu){
    cpu->A=interlevel_cpu.a;cpu->X=interlevel_cpu.x;cpu->Y=interlevel_cpu.y;cpu->D=interlevel_cpu.d;
    cpu->DB=interlevel_cpu.db;cpu->PB=interlevel_cpu.pb;cpu->P=interlevel_cpu.p;cpu_p_to_mirrors(cpu);
}
static void InterlevelService(CpuState *cpu,uint32_t pc,uint32_t service){
    InterlevelRestore(cpu);
    /* The earlier D130 entry retains the actor's WRAM bank7E. These native
     * foreground services expect bank00: A073 reads absolute4212/4218/4219.
     * Keep the entry bank saved for the original exit, but use the actual
     * hardware bank while waiting/sampling the pad. */
    cpu->DB=0;
    unsigned ret=(pc-1)&65535;
    cpu_write8(cpu,0,cpu->S--,ret>>8);cpu_write8(cpu,0,cpu->S--,ret);
    interp_bridge_pre_opcode_redirect(service);
}
static void InterlevelTrace(const char *event,CpuState *cpu){
    const char *path=getenv("TLK_INTERLEVEL_TRACE");static FILE *f;
    if(path && !f){f=fopen(path,"w");if(f)fputs("event,field,phase,age,tick,fade,pad,stack,pb,db,m,x,scene,level,finish,selected,ready\n",f);}
    if(f){fprintf(f,"%s,%u,%u,%u,%u,%u,%04x,%04x,%02x,%02x,%u,%u,%06x,%u,%04x,%u,%u\n",event,
        (unsigned)snes_frame_counter+1,tlk_interlevel_scene.phase,tlk_interlevel_scene.age,tlk_interlevel_scene.tick,
        tlk_interlevel_scene.fade,FinalWord(0x5a),cpu->S,cpu->PB,cpu->DB,cpu->m_flag,cpu->x_flag,
        FinalAddress(0xdf),FinalWord(0x1ff9e),FinalWord(0xa692),TlkResourcesUseMd("gameplay.levels.pride_lands.interlevel_scene"),TlkInterlevelDataReady());fflush(f);}
}
static void InterlevelPoint(CpuState *cpu,uint32_t pc){
    if(CliffPoint(cpu,pc))return;
    InterlevelTrace("boundary",cpu);
    if(interlevel_finished)return;
    if(!TlkInterlevelSceneActive()){
        /* D130 follows the outgoing fade/teardown, before native C472CE
         * schedules the SNES illustration. C08952 is after that whole scene;
         * inserting here used to display both versions in succession. */
        if(pc!=0xc0d130 || !TlkResourcesUseMd("gameplay.levels.pride_lands.interlevel_scene") || !TlkInterlevelDataReady() ||
           FinalAddress(0xdf)!=0xc005ab || FinalWord(0x1ff9e) || FinalWord(0x2000) ||
           !FinalWord(0xa6c4) || FinalWord(0xa6c4)>=32768 || !FinalWord(0x2004))return;
        InterlevelTrace("entry_context",cpu);
        if(cpu->PB!=0xc0 || cpu->DB!=0x7e || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->S<0x200 || cpu->S>=0x300){
            fprintf(stderr,"Unsupported Pride interlevel entry ABI\n");exit(124);
        }
        cpu_mirrors_to_p(cpu);interlevel_cpu.a=cpu->A;interlevel_cpu.x=cpu->X;interlevel_cpu.y=cpu->Y;
        interlevel_cpu.d=cpu->D;interlevel_cpu.s=cpu->S;interlevel_cpu.db=cpu->DB;interlevel_cpu.pb=cpu->PB;interlevel_cpu.p=cpu->P;
        TlkInterlevelSceneBegin();interlevel_field=(unsigned)snes_frame_counter+1;InterlevelTrace("begin",cpu);
    }
    if(cpu->S!=interlevel_cpu.s){fprintf(stderr,"Unbalanced Pride interlevel service\n");exit(124);}
    unsigned now=(unsigned)snes_frame_counter+1;
    if(interlevel_pending==1 && now!=interlevel_field){
        interlevel_field=now;
        if(TlkInterlevelSceneInput()){
            interlevel_pending=2;InterlevelService(cpu,pc,0xc0a073);return;
        }
        TlkInterlevelSceneAdvance(0);InterlevelTrace("wait",cpu);
    }else if(interlevel_pending==2){
        unsigned events=TlkInterlevelSceneAdvance(!!(FinalWord(0x5a)&0x1000));InterlevelTrace("input",cpu);
        if(TlkInterlevelSceneAudioSelected()){
            if(events&4)TlkMdSoundInterlevelSample(0);
            if(events&8)TlkMdSoundInterlevelSample(1);
            if(events&16)TlkMdSoundInterlevelStop();
        }
        if(!TlkInterlevelSceneActive()){
            InterlevelTrace("end",cpu);interlevel_finished=1;interlevel_pending=0;InterlevelRestore(cpu);
            /* The native exit branch owns A692 and the original RTL frame. */
            interp_bridge_pre_opcode_redirect(0xc0d170);return;
        }
    }
    interlevel_pending=1;InterlevelService(cpu,pc,0xc0983d);
}
static void InterlevelEnsureInstalled(void){
    if(!interlevel_installed){if(!interp_bridge_add_pre_opcode_hook(0xc08952,InterlevelPoint) ||
        !interp_bridge_add_pre_opcode_hook(0xc0d130,InterlevelPoint))exit(124);interlevel_installed=1;}
}
/* DONE completes the selected drawing, not the native controller teardown.
 * Its old illustrated PPU canvas can brighten again during that teardown.
 * Retire this ownership once at the actual next descriptor, never by level
 * number: the guest assigns the next level before releasing the old scene.
 * A zero descriptor is still its teardown gap, not the new renderer. */
static int InterlevelRetiring(void){
    if(interlevel_finished!=1)return 0;
    unsigned scene=FinalAddress(0xdf);
    if(!TlkResourcesUseMd("gameplay.levels.pride_lands.interlevel_scene") ||
       (scene && scene!=0xc005ab)){interlevel_finished=2;return 0;}
    return 1;
}
static void InterlevelPaint(uint32_t *pixels,int width){
    if(TlkCliffSceneActive()){CliffPaint(pixels,width);TlkFallbackCanvasOwned((unsigned)snes_frame_counter);return;}
    if(!pixels || width<256 || width>1024)return;
    if(InterlevelRetiring()){
        memset(pixels,0,(size_t)width*224*sizeof *pixels);TlkFallbackCanvasOwned((unsigned)snes_frame_counter);return;
    }
    if(!TlkInterlevelSceneActive())return;
    TlkInterlevelScene *s=&tlk_interlevel_scene;
    if(s->phase==TLK_INTERLEVEL_PRE){
        memset(interlevel_canvas,0,sizeof interlevel_canvas);

    }else{
        /* A prepared SNES illustration is not available at this seam.
         * The selected Genesis scene owns its sole available illustration,
         * even under a globally SNES artwork preset. Never show a black wait. */
        if(!TlkResourcesUseMd("graphics.interlevel.pride_lands"))
            TlkFallbackRecord("source_unavailable","graphics.interlevel.pride_lands","native_illustration_unavailable_using_available_genesis_art",0,0,0,1);
        if(!TlkInterlevelDataRenderFade(s->tick,TlkInterlevelSceneCap(),TlkInterlevelSceneLoss(),320,interlevel_canvas))exit(124);
    }
    for(unsigned y=0;y<224;y++)for(int x=0;x<width;x++){
        int source=x+(320-width)/2;pixels[y*width+x]=source>=0 && source<320?interlevel_canvas[y*320+source]|0xff000000u:0xff000000u;
    }
    TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
}

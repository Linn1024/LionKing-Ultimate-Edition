/* The missing post-Stampede scene owns its own waits and real pad samples. */
static unsigned cliff_finished,cliff_pending,cliff_field;
static struct {uint16_t a,x,y,d,s;uint8_t db,p,pb;} cliff_cpu;
static void CliffClear(void){TlkCliffSceneClear();cliff_finished=cliff_pending=cliff_field=0;memset(&cliff_cpu,0,sizeof cliff_cpu);}
static void CliffRestore(CpuState *cpu){
    cpu->A=cliff_cpu.a;cpu->X=cliff_cpu.x;cpu->Y=cliff_cpu.y;cpu->D=cliff_cpu.d;
    cpu->DB=cliff_cpu.db;cpu->PB=cliff_cpu.pb;cpu->P=cliff_cpu.p;cpu_p_to_mirrors(cpu);
}
static void CliffService(CpuState *cpu,uint32_t pc,uint32_t service){
    CliffRestore(cpu);unsigned ret=(pc-1)&65535;
    cpu_write8(cpu,0,cpu->S--,ret>>8);cpu_write8(cpu,0,cpu->S--,ret);interp_bridge_pre_opcode_redirect(service);
}
static void CliffTrace(const char *event){
    const char *path=getenv("TLK_CLIFF_TRACE");static FILE *f;
    if(path&&!f){f=fopen(path,"w");if(f)fputs("event,field,phase,age,tick,pad\n",f);}
    if(f){fprintf(f,"%s,%u,%u,%u,%u,%04x\n",event,(unsigned)snes_frame_counter+1,tlk_cliff_scene.phase,tlk_cliff_scene.age,tlk_cliff_scene.tick,FinalWord(0x5a));fflush(f);}
}
static int CliffPoint(CpuState *cpu,uint32_t pc){
    if(cliff_finished)return 0;
    if(!TlkCliffSceneActive()){
        if(pc!=0xc08952 || !TlkResourcesUseMd("gameplay.levels.stampede.exit_flow") || !TlkInterlevelDataCliffReady() ||
           FinalAddress(0xdf)!=0xc0041d || FinalWord(0x1ff9e)!=4 || FinalWord(0x2000) ||
           !FinalWord(0xa692) || FinalWord(0xa692)>=32768 || !FinalWord(0x2004))return 0;
        if(cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->S<0x200 || cpu->S>=0x300){fprintf(stderr,"Unsupported cliff entry ABI\n");exit(124);}
        cpu_mirrors_to_p(cpu);cliff_cpu.a=cpu->A;cliff_cpu.x=cpu->X;cliff_cpu.y=cpu->Y;cliff_cpu.d=cpu->D;cliff_cpu.s=cpu->S;
        cliff_cpu.db=cpu->DB;cliff_cpu.pb=cpu->PB;cliff_cpu.p=cpu->P;cliff_field=(unsigned)snes_frame_counter+1;
        TlkCliffSceneBegin();CliffTrace("begin");
    }
    if(cpu->S!=cliff_cpu.s){fprintf(stderr,"Unbalanced cliff service\n");exit(124);}
    unsigned now=(unsigned)snes_frame_counter+1;
    if(cliff_pending==1 && now!=cliff_field){
        cliff_field=now;TlkCliffSceneWait();
        if(TlkCliffSceneInput()){cliff_pending=2;CliffService(cpu,pc,0xc0a073);return 1;}
    }else if(cliff_pending==2){TlkCliffSceneAdvance(!!(FinalWord(0x5a)&0x1000));CliffTrace("input");}
    if(!TlkCliffSceneActive()){CliffTrace("end");cliff_finished=1;cliff_pending=0;CliffRestore(cpu);return 1;}
    cliff_pending=1;CliffService(cpu,pc,0xc0983d);return 1;
}
static void CliffPaint(uint32_t *pixels,int width){
    if(!pixels || width<256 || width>1024)return;
    if(tlk_cliff_scene.phase==TLK_CLIFF_PRE || tlk_cliff_scene.phase==TLK_CLIFF_INIT)memset(interlevel_canvas,0,sizeof interlevel_canvas);
    else {
        /* The Genesis transition currently has one prepared illustration.
         * Keep the scene visible under mixed presets, as for Pride Lands. */
        if(!TlkResourcesUseMd("graphics.interlevel.stampede"))
            TlkFallbackRecord("source_unavailable","graphics.interlevel.stampede","native_illustration_unavailable_using_available_genesis_art",0,0,0,1);
        if(!TlkInterlevelDataRenderCliff(tlk_cliff_scene.tick,TlkCliffSceneCap(),TlkCliffSceneLoss(),320,interlevel_canvas))exit(124);
    }
    for(unsigned y=0;y<224;y++)for(int x=0;x<width;x++){
        int source=x+(320-width)/2;pixels[y*width+x]=source>=0 && source<320?interlevel_canvas[y*320+source]|0xff000000u:0xff000000u;
    }
}

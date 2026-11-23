/* MD normal Toss completion, using the native wait/pad/teardown services. */
static unsigned bonus_result_installed,bonus_result_pending,bonus_result_field,bonus_result_reset;
static uint32_t bonus_result_origin[320*224];
static struct {uint16_t a,x,y,d,s;uint8_t db,p,pb;} bonus_result_cpu;
static void BonusResultClear(void){
    TlkBonusResultSceneClear();bonus_result_pending=bonus_result_field=bonus_result_reset=0;
    memset(&bonus_result_cpu,0,sizeof bonus_result_cpu);
}
static int BonusResultSelected(void){
    return TlkResourcesUseMd("gameplay.bonus.bug_toss.result_flow") && TlkBonusResultDataReady();
}
static int BonusResultOwner(void){
    return FinalWord(0x1ff9e)==10 && FinalAddress(0xdf)==0xc005dd &&
        FinalAddress(0xb217)==0xc5858a && FinalAddress(0xb243)==0xc53e5e;
}
static void BonusResultRestore(CpuState *cpu){
    cpu->A=bonus_result_cpu.a;cpu->X=bonus_result_cpu.x;cpu->Y=bonus_result_cpu.y;
    cpu->D=bonus_result_cpu.d;cpu->S=bonus_result_cpu.s;cpu->DB=bonus_result_cpu.db;
    cpu->PB=bonus_result_cpu.pb;cpu->P=bonus_result_cpu.p;cpu_p_to_mirrors(cpu);
}
static void BonusResultService(CpuState *cpu,uint32_t pc,uint32_t service){
    BonusResultRestore(cpu);unsigned ret=(pc-1)&65535;
    if(service==0xc0748a){
        cpu->P&=~0x10;cpu_p_to_mirrors(cpu); /* original teardown requires X16 */
        cpu_write8(cpu,0,cpu->S--,cpu->PB);
    }
    cpu_write8(cpu,0,cpu->S--,ret>>8);cpu_write8(cpu,0,cpu->S--,ret);
    interp_bridge_pre_opcode_redirect(service);
}
static void BonusResultTrace(const char *event,CpuState *cpu){
    const char *path=getenv("TLK_BONUS_RESULT_TRACE");static FILE *f;
    if(path && !f){f=fopen(path,"w");if(f)fputs("event,field,phase,age,count,display,timer,stack,scene,level\n",f);}
    TlkBonusResultScene *s=&tlk_bonus_result_scene;
    if(f){fprintf(f,"%s,%u,%u,%u,%u,%u,%u,%04x,%06x,%u\n",event,(unsigned)snes_frame_counter+1,
        s->phase,s->age,s->count,s->display,s->timer,cpu->S,FinalAddress(0xdf),FinalWord(0x1ff9e));fflush(f);}
}
static void BonusResultPoint(CpuState *cpu,uint32_t pc){
    TlkBonusResultScene *s=&tlk_bonus_result_scene;
    if(pc==0xc53ea0){
        /* F28F is a request in MD; the native corresponding store starts a
         * palette fade immediately. The owned MD controller fades audio first. */
        if(BonusResultSelected() && BonusResultOwner() && cpu->DB==0x7e && cpu->m_flag && !cpu->x_flag &&
           (cpu->A&255)==255)cpu->A&=0xff00;
        return;
    }
    if(s->phase==TLK_RESULT_DONE){if(FinalWord(0x1ff9e)!=10)BonusResultClear();return;}
    if(!TlkBonusResultSceneActive()){
        if(!BonusResultSelected() || !BonusResultOwner() || FinalWord(0xb241)!=1 || FinalWord(0xa692) ||
           FinalWord(0xb231)>110)return;
        if(cpu->PB!=0xc0 || cpu->DB || cpu->D || cpu->m_flag || !cpu->x_flag || cpu->S<0x200 || cpu->S>=0x300){
            fprintf(stderr,"Unsupported MD bonus-result entry ABI\n");exit(126);
        }
        cpu_mirrors_to_p(cpu);bonus_result_cpu.a=cpu->A;bonus_result_cpu.x=cpu->X;bonus_result_cpu.y=cpu->Y;
        bonus_result_cpu.d=cpu->D;bonus_result_cpu.s=cpu->S;bonus_result_cpu.db=cpu->DB;
        bonus_result_cpu.pb=cpu->PB;bonus_result_cpu.p=cpu->P;
        if(!BonusResultOriginCanvas(bonus_result_origin,320,s_wide_hud)){fprintf(stderr,"Missing initialized bonus result origin\n");exit(126);}
        TlkBonusResultSceneBegin(FinalWord(0xb231));bonus_result_field=(unsigned)snes_frame_counter+1;
        BonusResultTrace("begin",cpu);
    }
    if(cpu->S!=bonus_result_cpu.s){fprintf(stderr,"Unbalanced MD bonus-result service\n");exit(126);}
    unsigned now=(unsigned)snes_frame_counter+1;
    if(bonus_result_pending==1 && now!=bonus_result_field){
        bonus_result_field=now;
        if(TlkBonusResultSceneInput()){
            bonus_result_pending=2;BonusResultService(cpu,pc,0xc0a073);return;
        }
        TlkBonusResultSceneAdvance(0);BonusResultTrace("wait",cpu);
    }else if(bonus_result_pending==2){
        TlkBonusResultSceneAdvance(1);BonusResultTrace("input",cpu);
        if(!TlkBonusResultSceneActive()){
            /* Source MD's result returns to the ordinary bonus-return path.
             * The native normal-level slot and loader retain ownership. */
            g_ram[0xa692]=g_ram[0xa693]=255;bonus_result_pending=0;
            BonusResultRestore(cpu);BonusResultTrace("end",cpu);
            interp_bridge_pre_opcode_redirect(0xc0891d);return;
        }
    }else if(bonus_result_pending==3){bonus_result_reset=1;BonusResultTrace("teardown",cpu);}
    if(s->phase==TLK_RESULT_SETUP){
        if(!bonus_result_reset){bonus_result_pending=3;BonusResultService(cpu,pc,0xc0748a);return;}
        bonus_result_pending=2;BonusResultService(cpu,pc,0xc0a073);return;
    }
    bonus_result_pending=1;BonusResultService(cpu,pc,0xc0983d);
}
static void BonusResultEnsureInstalled(void){
    if(!bonus_result_installed){
        if(!interp_bridge_add_pre_opcode_hook(0xc08866,BonusResultPoint) ||
           !interp_bridge_add_pre_opcode_hook(0xc53ea0,BonusResultPoint))exit(126);
        bonus_result_installed=1;
    }
}
static void BonusResultPaint(uint32_t *pixels,int width){
    TlkBonusResultScene *s=&tlk_bonus_result_scene;
    if(!pixels || width<256 || width>1024 || !s->phase)return;
    if(s->phase==TLK_RESULT_DONE){if(FinalAddress(0xdf)==0xc005dd){memset(pixels,0,width*224*4);TlkFallbackCanvasOwned((unsigned)snes_frame_counter);}return;}
    if(s->phase<=TLK_RESULT_FADE_OUT){
        unsigned loss=TlkBonusResultSceneLoss()*4;
        for(unsigned y=0;y<224;y++)for(int x=0;x<width;x++){
            int source=x+(320-width)/2;uint32_t rgb=0xff000000;
            if(source>=0 && source<320){uint32_t c=bonus_result_origin[y*320+source];
                for(unsigned shift=0;shift<24;shift+=8){unsigned v=(c>>shift&255)>>3;v=v>loss?v-loss:0;rgb|=((v<<3)|(v>>2))<<shift;}}
            pixels[y*width+x]=rgb;
        }
    }else if(s->phase>=TLK_RESULT_SETUP){
        if(!TlkBonusResultDataRender(s->display,TlkResourcesUseMd("graphics.bonus_results"),
            TlkBonusResultSceneCap(),0,width,pixels))exit(126);
    }else memset(pixels,0,width*224*4);
    TlkFallbackCanvasOwned((unsigned)snes_frame_counter);
}

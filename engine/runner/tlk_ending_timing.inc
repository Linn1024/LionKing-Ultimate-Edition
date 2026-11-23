/* Original NTSC ending schedule (1CDE10..1CDED8), independent of sound/art.
 * The native controller still performs speech requests, fades and credits
 * loading. Replace its SPC marker with the original MD clock, and its two
 * waits with the original 116 / (201+201) update intervals. The latter spans
 * the original static title overlay / impact cue, not a Simba roar animation.
 * These controller/poll sites currently execute in the interpreter in both
 * AOT and LLE hosts. No compiled function covers them in the retained graph.
 */
static unsigned ending_timing_epoch;
static int ending_timing_selected(void){return TlkResourcesUseMd("gameplay.levels.pride_rock.ending_timing");}
/* Paired original postfight phases, source3538. The native terminal18 is the
 * equivalent of MD15; retain that semantic identity for the native controller.
 * Change the original LDA operands before their ordinary stores/countdowns.
 * Voice, artwork, movement and the later4701-update finale clock are separate. */
static const unsigned postfight_timing_loads[][4]={
    {0xc67721,200,120,3},{0xc677e2,90,60,7},{0xc67831,60,40,8},
    {0xc67887,90,60,9},{0xc678dc,230,200,10},{0xc6799a,96,66,13},
    {0xc679d4,400,200,14},{0xc679ee,15,18,14},{0xc679f3,250,65535,18}
};
static void postfight_timing_pre(CpuState *cpu,uint32_t pc){
    if(!ending_timing_selected() || !finale_scene() || word(0x68)!=0xb213 ||
       cpu->PB!=0xc6 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->D<0x600 || cpu->D>=0x1f00 || word(0xa68c)!=cpu->D+0x26)return;
    for(unsigned i=0;i<sizeof postfight_timing_loads/sizeof*postfight_timing_loads;i++){
        const unsigned *r=postfight_timing_loads[i];
        if(pc!=r[0]+3 || cpu->A!=r[1] || word(0xb23f)!=r[3])continue;
        static FILE *log;static int opened;
        if(!opened){opened=1;const char *path=getenv("TLK_POSTFIGHT_TIMING_TRACE");if(path){log=fopen(path,"w");if(log)fputs("field,pc,phase,before,after\n",log);}}
        if(log){fprintf(log,"%u,%06x,%u,%u,%u\n",snes_frame_counter+1,r[0],r[3],r[1],r[2]);fflush(log);}
        cpu->A=(uint16_t)r[2];cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
        return;
    }
}
int TlkEndingTitleActive(void){return ending_timing_epoch && ending_timing_selected() &&
    ending_sunrise() && word(0xa6f0)==3 && !word(0xb249) && word(0xb247)<=200;}
/* The existing native credits controller provides a saved, pause-aware clock.
 * Its120-update initial hold and subsequent one-unit scroll updates both count
 * elapsed fields; MD artwork consumes that elapsed time at one pixel per3.
 * Native terminal hold/fade/exit remain independent, without a new save timer. */
int TlkEndingCreditsTick(void){
    if(!ending_credits() || word(0xa6f0)!=3)return -1;
    unsigned phase=word(0xb249),left=word(0xb247),scroll=word(0x4c);
    if(phase==9 && left<=119)return 119-left;
    if(phase==1 && left<=118 && scroll<=6400)return 120+scroll-left;
    if(phase==2 && left<=600)return 6520+600-left;
    if(phase==3)return 7120;
    return -1;
}
static void ending_timing_log(unsigned pc,unsigned before,unsigned after){
    static FILE *log;static int initialized;
    if(!initialized){const char *path=getenv("TLK_ENDING_TIMING_TRACE");initialized=1;
        if(path)log=fopen(path,"w");if(log)fputs("field,pc,elapsed,before,after\n",log);}
    if(log){fprintf(log,"%u,%06x,%u,%u,%u\n",(unsigned)snes_frame_counter+1,pc,
        (unsigned)snes_frame_counter+1-ending_timing_epoch,before,after);fflush(log);}
}
static void ending_timing_pre(CpuState *cpu,uint32_t pc){
    if(!ending_timing_epoch || !ending_timing_selected() || !ending_owner() ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D)return;
    if(pc==0xc0fc3c){
        /* C0FC08 normally forwards a changed SPC marker1 to the ending.
         * Selected MD timing owns that marker instead. Preserve its current
         * value so a later native song marker cannot restart the speeches. */
        if(cpu->A==1){unsigned before=cpu->A;cpu->A=word(0xa6f0);
            ending_timing_log(pc,before,cpu->A);}
        return;
    }
    if(!ending_sunrise() || word(0x68)!=0xb213 || cpu->DB!=0x7e)return;
    if(pc==0xc47502 || pc==0xc47509){ending_timing_log(pc,0,0);
    }else if(pc==0xc47495){
        unsigned now=(unsigned)snes_frame_counter+1;
        if(word(0xa6f0)==3 && !word(0xb249) && word(0xb247)==201){
            /* Original1CDEA0 title and1CDEBA selector2/program165,201 updates
             * after speech2. The native countdown then falls to200, exposing
             * the independently selected transparent title overlay. */
            unsigned selected=TlkResourcesUseMd("audio.effects.ending_title");
            if(selected && word(0x1ff96) && TlkMdSoundReady()){
                TlkMdSoundCommand(2,165);fx_tail=120;
            }
            ending_timing_log(0x1cdea0,selected,word(0x1ff96));
        }
        if(now>=ending_timing_epoch && now-ending_timing_epoch>=4701 && !word(0xa6f0)){
            /* A real selected-flow event, consumed by the unchanged native
             * animation/speech controller below; no diagnostic/test injection. */
            g_ram[0xa6f0]=1;g_ram[0xa6f1]=0;
            ending_timing_log(pc,0,1);
        }
    }else if(pc==0xc47524 && cpu->A==110){cpu->A=115;ending_timing_log(pc,110,115);
    }else if(pc==0xc4755a && cpu->A==100){cpu->A=401;ending_timing_log(pc,100,401);}
}
static void ending_timing_install(void){
    for(unsigned i=0;i<sizeof postfight_timing_loads/sizeof*postfight_timing_loads;i++)
        interp_bridge_add_pre_opcode_hook(postfight_timing_loads[i][0]+3,postfight_timing_pre);
    static const unsigned sites[]={0xc0fc3c,0xc47495,0xc47524,0xc4755a,0xc47502,0xc47509};
    for(unsigned i=0;i<sizeof sites/sizeof *sites;i++)
        interp_bridge_add_pre_opcode_hook(sites[i],ending_timing_pre);
}
static void ending_timing_frame(void){
    ending_timing_install();
    if(word(0x1ff9e)!=9 || word(0x2000)!=0xffff ||
       (!finale_scene() && !ending_owner() && address(0xdf)!=0xc005ab))ending_timing_epoch=0;
}

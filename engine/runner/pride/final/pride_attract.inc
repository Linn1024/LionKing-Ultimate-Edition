/* Native demo coordinator/input decoder retained. Only the installed source
 * recording and (when selected) MD's three-level rotation replace its data. */
static FILE *attract_trace;
static void AttractTrace(const char *event,unsigned level,unsigned run,unsigned pad,unsigned duration,unsigned md) {
    if(attract_trace){fprintf(attract_trace,"%u,%s,%u,%u,%04x,%u,%u,%04x,%u,%u,%u\n",(unsigned)snes_frame_counter,event,level,run,pad,duration,md,FinalWord(0x1e03),FinalWord(0x2004),FinalWord(0xb21b),FinalWord(0xb21d));fflush(attract_trace);}
}
static void AttractSetA(CpuState *cpu,unsigned value) {
    cpu->A=(uint16_t)value;cpu->_flag_Z=!value;cpu->_flag_N=!!(value&0x8000);
    cpu->P=(cpu->P&~0x82)|(cpu->_flag_Z?2:0)|(cpu->_flag_N?0x80:0);
}
static const char *AttractLevelChoice(unsigned level) {
    return level==0?"gameplay.levels.pride_lands":level==2?"gameplay.levels.elephant_graveyard":
           level==8?"gameplay.levels.simbas_return":NULL;
}
void TlkAttractOpcode(CpuState *cpu,uint32_t pc) {
    if(!g_ram || cpu->D!=0x1e00 || cpu->m_flag || cpu->x_flag || !(FinalWord(0x1e03)&0x8000))return;
    if(pc==0xc5012f) {
        /* SNES has an additional Hakuna recording; MD cycles Pride/Graveyard/Return.
         * Skip Hakuna only when its level-design source is MD. The native exit
         * increments this ordinary saved slot back to zero after Return. */
        if((FinalWord(0x1e03)&3)==2 && TlkResourcesUseMd("gameplay.levels.hakuna_matata")) {
            ReloadFastWord(0x1e03,(FinalWord(0x1e03)&~3u)|3u);AttractSetA(cpu,8);
        }
        AttractTrace("entry",cpu->A,0,0,0,0);
        return;
    }
    unsigned level=FinalWord(0x1ff9e);const char *choice=AttractLevelChoice(level);
    if(!choice || !TlkResourcesUseMd(choice)) {
        if(pc==0xc501d6)AttractTrace("run",level,FinalWord(0x1e05)/4,cpu->A,0,0);
        return;
    }
    unsigned offset=FinalWord(0x1e05),pad,duration;
    if(offset&3 || !TlkFinalArtAttractRun(final_menu_art,level,offset/4,&pad,&duration)) {
        fprintf(stderr,"Installed MD attract recording unavailable. Run Setup.\n");exit(114);
    }
    if(pc==0xc501d6){AttractSetA(cpu,pad);AttractTrace("run",level,offset/4,pad,duration,1);}
    else if(pc==0xc501eb)AttractSetA(cpu,duration);
}
static void TlkAttractInstall(void) {
    const char *trace=getenv("TLK_ATTRACT_TRACE");if(trace && *trace){attract_trace=fopen(trace,"w");if(attract_trace)fputs("field,event,level,run,pad,duration,md,demo,health,x,y\n",attract_trace);}
    static const uint32_t sites[]={0xc5012f,0xc501d6,0xc501eb};
    for(unsigned i=0;i<3;i++)if(!interp_bridge_add_pre_opcode_hook(sites[i],TlkAttractOpcode))exit(120);
}

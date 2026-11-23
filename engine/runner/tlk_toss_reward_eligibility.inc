/* Original MD1B4B48..1B4B88 rejects a special life/continue bug only at9.
 * Retain the ordinary chooser, random calls, spawn and award programs. */
static unsigned TossRewardAddress(unsigned at){return word(at)|(unsigned)g_ram[at+2]<<16;}
static void toss_reward_eligibility_pre(CpuState *cpu,uint32_t pc){
    if((pc!=0xc5498d && pc!=0xc549a9) || cpu->PB!=0xc5 || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D || cpu->D<0x600 || cpu->D>0x1f00 ||
       word(0xa68c)!=cpu->D+0x24 || word(cpu->S+7)!=1 ||
       word(0x1ff9e)!=10 || TossRewardAddress(0xdf)!=0xc005dd ||
       TossRewardAddress(0xb217)!=0xc5858a)return;
    unsigned actor=word(0x68),kind=pc==0xc5498d?3:4;
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       TossRewardAddress(actor+4)!=0xc58a71 || TossRewardAddress(actor+48)!=0xc53989 ||
       word(cpu->D+0x22)!=kind)return;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return;
    unsigned count=word(kind==3?0x1ffaa:0x1ffa8),before=cpu->_flag_Z;
    unsigned selected=TlkResourcesUseMd("gameplay.bonus.bug_toss.reward_eligibility");
    if(selected){cpu->_flag_Z=count!=9;cpu_mirrors_to_p(cpu);}
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_TOSS_REWARD_TRACE");if(path)log=fopen(path,"w");
        if(log)fputs("field,pc,actor,kind,count,native_z,selected_z,source_md\n",log);}
    if(log){fprintf(log,"%u,%06x,%04x,%u,%u,%u,%u,%u\n",(unsigned)snes_frame_counter+1,pc,actor,kind,count,before,cpu->_flag_Z,selected);fflush(log);}
}

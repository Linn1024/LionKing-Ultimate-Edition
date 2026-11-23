/* Source5211: MD has a separate adult voice11 on grapple entry, in addition
 * to ordinary roar11, and no late contact swish. Native C37CEB requests54. */
static int grapple_contact_choice;
static void grapple_entry(CpuState *cpu,uint32_t pc,int before) {
    if(pc!=0xc37d25 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       cpu->A!=0x7ceb || cpu->Y!=0x30 || word(0x2000)!=0xffff || !continue_world_scene())return;
    unsigned actor=word(0x68),target=word(0xa6d0);
    if(actor!=word(0x6e) || actor!=0xb213 || address(actor+4)!=0xc5858a ||
       word(0xa6d2)!=0x7e || target<0xb293 || target>=0xdc13 || ((target-0xb213)&127))return;
    unsigned descriptor=address(target+4),draw=word(actor+12);
    if((descriptor!=0xc58ea8 && descriptor!=0xc58eb4) || draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return;
    if(before?address(actor+48)==0xc37ceb:word(actor+48)!=0x7ceb)return;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.grapple_contact");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_GRAPPLE_ENTRY_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,target,target_descriptor,raw_action,pc,selected,emitted,value,parameter\n",log);}
    if(log){fprintf(log,"%u,%04x,%04x,%06x,%06x,%06x,%u,%u,11,96\n",snes_frame_counter+1,actor,target,descriptor,address(actor+48),pc,selected,emitted);fflush(log);}
    if(emitted){TlkMdSoundPcm(11,96);effect_tail();}
}
static void grapple_entry_pre(CpuState *cpu,uint32_t pc){grapple_entry(cpu,pc,1);}
static int grapple_contact_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=54 || music_caller(cpu)!=0xc37dcf ||
       cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0x2000)!=0xffff || !continue_world_scene())return 0;
    unsigned actor=word(0x68);
    if(actor!=word(0x6e) || actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc5858a || address(actor+48)!=0xc37ceb || word(actor+46)!=2)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.simba.grapple_contact");
    unsigned suppressed=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_GRAPPLE_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,caller,selected,suppressed,native_event\n",log);}
    if(log){fprintf(log,"%u,%04x,c5858a,c37ceb,c37dcf,%u,%u,54\n",snes_frame_counter+1,actor,selected,suppressed);fflush(log);}
    if(!suppressed)return 0;
    cpu->A=0;return 1;
}

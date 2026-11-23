/* Original MD emitter1567C4 and particle1B3400, source audit5825.
 * Keep normal allocation, random motion, update cadence and ending controller.
 * The emitter's ordinary pointer advances through the longer selected stream;
 * override its loaded byte before the native store, in AOT and interpreter. */
static void ending_rain_pre(CpuState *cpu,uint32_t pc) {
    static const uint8_t buildup[]={50,50,50,50,50,30,20,20,20,10,10,10,
        9,9,9,9,8,7,6,5,4,3,2,1,1,1,1,1,255};
    if(!TlkResourcesUseMd("gameplay.levels.pride_rock.rain") ||
       word(0x1ff9e)!=9 || word(0xdf)!=0x7db || g_ram[0xe1]!=0xc0 ||
       cpu->PB!=0xc6 || cpu->DB!=0x7e || cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=word(0x68);
    if(actor<0xb213 || actor>0xfe93 || ((actor-0xb213)&127))return;
    unsigned descriptor=word(actor+4)|(g_ram[actor+6]<<16);
    if(pc==0xc67fbc) {
        unsigned stream=word(actor+14),index=stream-0x3bd5;
        if(!cpu->m_flag || descriptor!=0xc585c4 ||
           (word(actor+48)|(g_ram[actor+50]<<16))!=0xc67ee1 ||
           word(actor+16)!=0xc2 || index>=sizeof buildup ||
           cpu->D>0xfffd || word(cpu->D)!=stream || g_ram[cpu->D+2]!=0xc2)return;
        cpu->A=(cpu->A&0xff00)|buildup[index];
        cpu->_flag_N=!!(cpu->A&0x80);cpu->_flag_Z=!(cpu->A&255);
    }else if(pc==0xc6816a) {
        unsigned draw=word(actor+12);int x=(int16_t)word(actor+8);
        if(cpu->m_flag || descriptor!=0xc585d0 || cpu->X!=actor ||
           draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8 ||
           (word(draw+10)|(g_ram[draw+12]<<16))!=0xc2f33e ||
           x>=0 || x< -256 || cpu->A!=(uint16_t)(x+256))return;
        cpu->A=(uint16_t)(x+320);
        cpu->_flag_N=!!(cpu->A&0x8000);cpu->_flag_Z=!cpu->A;
    }else return;
    cpu_mirrors_to_p(cpu);
    static FILE *trace;static int opened;
    if(!opened){const char *p=getenv("TLK_ENDING_RAIN_TRACE");opened=1;
        if(p)trace=fopen(p,"w");
        if(trace)fputs("field,pc,actor,stream,x,y,a\n",trace);}
    if(trace){fprintf(trace,"%u,%06x,%04x,%04x,%d,%d,%u\n",snes_frame_counter+1,
        pc,actor,word(actor+14),(int16_t)word(actor+8),(int16_t)word(actor+10),cpu->A);fflush(trace);}
}

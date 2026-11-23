/* Source5158: original paired projectile spawn requests FM167, not native38.
 * The shooting action is C3A896; C3A1F2 is the pre-cue initializer. */
static int spider_projectile_choice;
static int spider_projectile_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=0x26 || !hakuna() || word(0x2000) ||
       music_caller(cpu)!=0xc3a9c0)return 0;
    unsigned actor=word(0x68);
    static FILE *guard;static int guard_open;
    if(!guard_open){guard_open=1;const char *p=getenv("TLK_SPIDER_PROJECTILE_GUARD_TRACE");if(p)guard=fopen(p,"w");
        if(guard)fputs("field,actor,descriptor,action,draw,owner,pose,phase,caller\n",guard);}
    if(guard){unsigned d=word(actor+12);fprintf(guard,"%u,%04x,%06x,%06x,%04x,%04x,%06x,%u,%06x\n",snes_frame_counter+1,actor,address(actor+4),address(actor+48),d,word(d+4),address(d+10),word(actor+46),music_caller(cpu));fflush(guard);}
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       address(actor+4)!=0xc58e9c || address(actor+48)!=0xc3a896)return 0;
    unsigned draw=word(actor+12);
    if(draw<0x8000 || draw>0xffe8 || word(draw+4)!=actor+8)return 0;
    /* The sound opcode runs before the next drawing is submitted. Source5163
     * sees the reciprocal preceding shooting pose here, not the later latch. */
    unsigned pose=address(draw+10);
    if(pose!=0xc3b2db && pose!=0xc3b308)return 0;
    unsigned selected=TlkResourcesUseMd("audio.effects.world.hakuna.spider_projectile");
    unsigned emitted=selected && word(0x1ff96) && TlkMdSoundReady();
    static FILE *log;static int opened;
    if(!opened){opened=1;const char *p=getenv("TLK_SPIDER_PROJECTILE_AUDIO_TRACE");if(p)log=fopen(p,"w");
        if(log)fputs("field,actor,descriptor,action,pose,caller,selected,emitted,selector,value\n",log);}
    if(log){fprintf(log,"%u,%04x,c58e9c,c3a896,%06x,c3a9c0,%u,%u,2,167\n",snes_frame_counter+1,actor,pose,selected,emitted);fflush(log);}
    if(!emitted)return 0;
    cpu->A=0;TlkMdSoundCommand(2,167);effect_tail();return 1;
}

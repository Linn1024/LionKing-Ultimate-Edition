/* Reviewed bank5 transfer: native data slice, original CPU/SPC completion.
 * All ownership is already serialized in final intent plus live CPU cursors. */
static void ContinueTitleUploadError(unsigned code) {
    fprintf(stderr,"Incompatible title sound transfer context; prepared playback cannot continue.\n");exit(code);
}
static const TlkTitleBankPacket *ContinueTitleUploadWindow(CpuState *cpu,unsigned *index,unsigned *offset) {
    unsigned dest=cpu->X,end=FinalWord(0x1f06),source=((unsigned)g_ram[0x1f0e]<<16)+cpu->Y;
    for(unsigned i=0;i<TLK_TITLE_BANK_PACKETS;i++) {
        const TlkTitleBankPacket *p=TlkTitleBankPacketAt(i);
        unsigned origin=i==1?0x7f0000:p->source;
        if(dest>=p->destination && end==p->destination+p->size && dest<end &&
           source==origin+dest-p->destination) {
            *index=i;*offset=dest-p->destination;return p;
        }
    }
    return NULL;
}
static void ContinueTitleUpload(CpuState *cpu,uint32_t pc) {
    (void)pc;
    if(!continue_transition_mode || !final_scene_entry || !continue_title_pending ||
       continue_transition.confirmed_field || reload_fast_used || FinalAddress(0xdf)!=0xc0057b)return;
    unsigned index=0,offset=0;
    const TlkTitleBankPacket *p=ContinueTitleUploadWindow(cpu,&index,&offset);
    if(!p || cpu->D!=0x1f00 || cpu->DB || cpu->m_flag || cpu->x_flag ||
       FinalWord(0x1f0c))ContinueTitleUploadError(115);
    size_t size=0;const uint8_t *bytes=TlkTitleBankPayload(title_bank_assets,index,&size);
    if(!bytes || size!=p->size || offset+2>size)ContinueTitleUploadError(115);
    unsigned remaining=p->size-offset,tail=4+(remaining&2);
    if(remaining>tail) {
        unsigned skip=remaining-tail;
        if(cpu->Y+skip>0xffff)ContinueTitleUploadError(115);
        tlk_bridge_apu_flush(cpu);RtlApuLock();Apu *apu=g_snes->apu;
        /* Same masked original driver identity as native audio ownership.
         * Only the four directory-store operands are self-modifying. */
        static const uint8_t expected[32]={
            0xdc,0xe6,0x8c,0x13,0x2e,0x0d,0x7c,0x29,0xa8,0xa0,0x02,0x4f,0x73,0xfb,0xdb,0x6e,
            0x3c,0x5b,0x5e,0x64,0x71,0xe4,0x59,0xdc,0xc7,0x36,0xaa,0xb4,0xc7,0xeb,0xf5,0x1f};
        uint8_t code[0x1800],hash[32];memcpy(code,apu->ram+0x600,sizeof code);
        const unsigned operands[]={0x1a76,0x1a77,0x1a7f,0x1a80};
        for(unsigned i=0;i<4;i++)code[operands[i]-0x600]=0;
        sha256_compute(code,sizeof code,hash);
        int valid=!memcmp(hash,expected,32) && !apu_portQueueDepth(apu);
        for(unsigned i=0;i<8;i++)if(apu->dsp->channel[i].gain || apu->dsp->channel[i].keyOn)valid=0;
        if(!valid) {RtlApuUnlock();ContinueTitleUploadError(115);}
        unsigned wait=0;
        while((apu->spc->pc!=0x19cf && apu->spc->pc!=0x19d1) || apu->outPorts[0]!=255) {
            if(++wait>65536 || apu_portQueueDepth(apu)) {RtlApuUnlock();ContinueTitleUploadError(116);}
            apu_cycle(apu);
        }
        /* Skip even word pairs so the real receive-loop phase remains intact.
         * Keep its final4/6 bytes, terminator and header/directory processing. */
        memcpy(apu->ram+p->destination+offset,bytes+offset,skip);RtlApuUnlock();
        cpu->X+=skip;cpu->Y+=skip;offset+=skip;
        if(continue_exit_log) {
            fprintf(continue_exit_log,"title_upload,%u,%06x,%u,%u,%u,%u\n",
                (unsigned)snes_frame_counter+1-final_scene_entry,p->source,skip,wait,index,offset);fflush(continue_exit_log);
        }
    }
    /* Supply even the remaining data reads from the installed packet. */
    unsigned value=bytes[offset]|(unsigned)bytes[offset+1]<<8;
    cpu->A=value;cpu->_flag_Z=!value;cpu->_flag_N=!!(value&0x8000);cpu_mirrors_to_p(cpu);
    interp_bridge_pre_opcode_redirect(0xc22038);
}

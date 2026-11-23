/* Original MD1AFD58 phase20 only decrements/draws; native C64321 emits8.
 * Keep native scheduling/transport; silence only this owned warning cue. */
static int prepared_launch_choice;
static int prepared_launch_audio(CpuState *cpu,uint32_t pc) {
    if(pc!=0xc22c2c || cpu->X!=8 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       !be_prepared() || word(0x2000)!=0xffff || music_caller(cpu)!=0xc64321)return 0;
    unsigned actor=word(0x68);
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || address(actor+4)!=0xc58758 ||
       address(actor+48)!=0xc6429e || word(actor+44)!=20 ||
       !word(0x1ff96) || !TlkMdSoundReady() ||
       !TlkResourcesUseMd("audio.effects.world.be_prepared.exit_launch"))return 0;
    cpu->A=0;return 1;
}

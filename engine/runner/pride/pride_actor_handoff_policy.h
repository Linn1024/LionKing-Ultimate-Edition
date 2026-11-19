/* Chosen-source default spawn identity, shared by classification and the
 * original revival comparisons. No saved coordinates or ROM bytes are edited. */
#include "tlk_resources.h"
#include "tlk_start_data.h"
static unsigned spawn_native[2],spawn_selected[2],spawn_md,spawn_checkpoint;
static FILE *spawn_policy_file;
static unsigned spawn_policy_checkpoint(void) {
    spawn_md=TlkResourcesUseMd("gameplay.levels.pride_lands.start");
    for(unsigned axis=0;axis<2;axis++) {
        unsigned native,external;
        if(!TlkStartDataValue(axis,&native,&external) || native!=(g_rom[0x39d + axis*2]|(unsigned)g_rom[0x39e + axis*2]<<8))exit(88);
        spawn_native[axis]=native;spawn_selected[axis]=spawn_md?external:native;
    }
    spawn_checkpoint=ow(0x1ffa4)!=spawn_selected[0] || ow(0x1ffa6)!=spawn_selected[1];
    return spawn_checkpoint;
}
static void spawn_policy_log(CpuState *cpu,uint32_t pc,unsigned axis,unsigned before,unsigned after) {
    if(!spawn_policy_file) {
        char file[2048];snprintf(file,sizeof file,"%s/spawn-policy.csv",TlkPrideSetting("TLK_SCENE_OWNER_PROBE"));
        spawn_policy_file=TlkPrideFileOpen(file,"w");if(!spawn_policy_file)exit(88);
        fprintf(spawn_policy_file,"field,age,md,native_x,native_y,selected_x,selected_y,saved_x,saved_y,checkpoint,pc,axis,a,original_czn,selected_czn\n");
    }
    fprintf(spawn_policy_file,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%06x,%u,%u,%u,%u\n",
        (unsigned)snes_frame_counter+1,owner_age(),spawn_md,spawn_native[0],spawn_native[1],spawn_selected[0],spawn_selected[1],
        ow(0x1ffa4),ow(0x1ffa6),spawn_checkpoint,pc,axis,cpu->A,before,after);fflush(spawn_policy_file);
}
static unsigned spawn_cmp_flags(unsigned a,unsigned b) {
    return (a>=b) | ((a==b)<<1) | ((((a-b)&65535)>>15)<<2);
}
static void spawn_policy_compare(CpuState *cpu,uint32_t pc) {
    unsigned axis=pc==0xc087bf || pc==0xc08827;
    if(cpu->D || cpu->DB || cpu->m_flag || !cpu->x_flag || cpu->Y!=22+axis*2 ||
       cpu->A!=ow(0x1ffa4+axis*2) || spawn_md!=(unsigned)TlkResourcesUseMd("gameplay.levels.pride_lands.start"))exit(88);
    /* The real CMP [$DF],Y just executed. Check its native operand result
     * before supplying the selected descriptor's result to its real branch.
     * CMP owns C/Z/N only: overflow and all unrelated flags remain live. */
    unsigned before=cpu->_flag_C | cpu->_flag_Z<<1 | cpu->_flag_N<<2;
    if(before!=spawn_cmp_flags(cpu->A,spawn_native[axis]))exit(88);
    unsigned after=before;
    if(spawn_md && !spawn_checkpoint) {
        after=spawn_cmp_flags(cpu->A,spawn_selected[axis]);
        cpu->_flag_C=after&1;cpu->_flag_Z=(after>>1)&1;cpu->_flag_N=(after>>2)&1;cpu_mirrors_to_p(cpu);
    }
    spawn_policy_log(cpu,pc,axis,before,after);
}

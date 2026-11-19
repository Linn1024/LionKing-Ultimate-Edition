/* Actual original floor-contact service after idle initialization, before draw.
 * No geometry, collision result, actor field or scratch result is synthesized. */
static unsigned grounded_waiting,grounded_done;
static uint16_t grounded_a,grounded_x,grounded_y,grounded_sp,grounded_d;
static uint8_t grounded_p,grounded_db;
const char *PrideRepeatDebugFolder(void);
static void grounded_dump(CpuState *cpu,const char *label) {
    char path[2048];const char *folder=PrideRepeatDebugFolder();
    snprintf(path,sizeof path,"%s/ground-%s.bin",folder,label);
    FILE *f=TlkPrideFileOpen(path,"wb");if(!f || fwrite(g_ram,1,0x20000,f)!=0x20000)exit(87);fclose(f);
    snprintf(path,sizeof path,"%s/ground-%s.csv",folder,label);
    f=TlkPrideFileOpen(path,"w");if(!f)exit(87);
    fprintf(f,"a,x,y,stack,direct_page,db,p,emulation,field,age\n");
    fprintf(f,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\n",cpu->A,cpu->X,cpu->Y,cpu->S,cpu->D,cpu->DB,cpu->P,
        cpu->emulation,(unsigned)snes_frame_counter+1,owner_age());fclose(f);
}
#include "tlk_pride_ground_window.inc"
static int grounded_service(CpuState *cpu,uint32_t pc) {
    if(grounded_done)return 1;
    if(!grounded_waiting) {
        if(!PrideDefaultGroundWindow(owner_age(),owner_default_initialized,owner_default_advancing) || cpu->D || cpu->DB!=0x7e || cpu->PB!=0xc0 ||
           cpu->S!=0x2ff || cpu->m_flag || !cpu->x_flag || cpu->emulation || ow(0x68)!=ow(0x6e))exit(87);
        grounded_a=cpu->A;grounded_x=cpu->X;grounded_y=cpu->Y;grounded_sp=cpu->S;
        grounded_d=cpu->D;grounded_db=cpu->DB;grounded_p=cpu->P;grounded_waiting=1;
        /* A genuine long-call return frame returns to this boundary. */
        unsigned target=(pc-1)&65535;
        cpu_write8(cpu,0,cpu->S--,(uint8_t)(pc>>16));
        cpu_write8(cpu,0,cpu->S--,(uint8_t)(target>>8));cpu_write8(cpu,0,cpu->S--,(uint8_t)target);
        grounded_dump(cpu,"entry");owner_log("default_ground_call",cpu,pc,ow(0xb21d));
        interp_bridge_pre_opcode_redirect(0xc0a323);return 0;
    }
    if(cpu->S!=grounded_sp || cpu->D!=grounded_d || cpu->DB!=grounded_db || cpu->PB!=0xc0)exit(87);
    grounded_dump(cpu,"return");owner_log("default_ground_return",cpu,pc,ow(0xb21d));
    /* The scheduled caller did not originally call this helper. Its live
     * register values belong to the pending draw, not to the floor query. */
    cpu->A=grounded_a;cpu->X=grounded_x;cpu->Y=grounded_y;cpu->P=grounded_p;cpu_p_to_mirrors(cpu);
    grounded_waiting=0;grounded_done=1;return 1;
}

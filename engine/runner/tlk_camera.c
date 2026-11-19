#include "tlk_camera.h"
#include "tlk_guest.h"
#include "tlk_md_camera.h"
#include "tlk_resources.h"
#include "tlk_cant_wait_data.h"
#include "tlk_cant_wait_policy.h"
#include "common_rtl.h"
#include "common_cpu_infra.h"
#include "snes/interp_bridge.h"
#include <stdio.h>
#include <stdlib.h>
static int view_width=256,previous_width=256,previous_source,load_width;
void TlkCameraLoadViewport(int width){load_width=width>=256&&width<=1024&&!(width&1)?width:0;}
void (*g_tlk_camera_operand_pc_hook)(CpuState *,uint32_t);
static unsigned word(unsigned a) { return g_ram[a]|(unsigned)g_ram[a+1]<<8; }
static void put(unsigned a,int value) { g_ram[a]=(uint8_t)value;g_ram[a+1]=(uint8_t)(value>>8); }
static int cant_wait_available(void) {
    /* The final resource catalog is compiled in the core object target, while
     * this camera is an executable source. Consult that validated catalog and
     * installed data instead of a private compile flag with a different value
     * in this translation unit. Script selection remains independent. */
    static int index=-2;
    if(index==-2)index=TlkResourcesFind("gameplay.levels.cant_wait.ostrich_obstacles");
    const TlkResourceNode *node=TlkResourcesNode(index);
    unsigned native,external;
    return node && node->md_supported && TlkCantWaitRideValue(0,&native,&external);
}
int TlkCameraActive(void) {
    unsigned level=word(0x1ff9e);
    return TlkResourcesUseMd("gameplay.camera") &&
        ((!word(0x1ff9e) && (word(0xdf)==0x387 || word(0xdf)==0x80d)) ||
         (word(0x1ff9e)==1 && word(0xdf)==0x3b9 && g_ram[0xe1]==0xc0 && cant_wait_available()) ||
         (word(0x1ff9e)==2 && word(0xdf)==0x3eb && g_ram[0xe1]==0xc0 && word(0xd0)==520 && word(0xd4)==48) ||
         (word(0x1ff9e)==4 && word(0xdf)==0x44f && g_ram[0xe1]==0xc0 && word(0xd0)==200 && word(0xd4)==155) ||
         (word(0x1ff9e)==5 && word(0xdf)==0x481 && g_ram[0xe1]==0xc0 && word(0xd0)==450 && word(0xd4)==71) ||
         /* MD postfight retains the level9 world/scroll/camera (3553/3555).
          * Reuse its real320-wide lead window: Simba678 settles at camera486,
          * rather than reverting to native502 when the descriptor changes. */
         (level==9 && word(0xdf)==0x7db && g_ram[0xe1]==0xc0 && word(0x2000)==65535) ||
         (level>=6 && level<=9 && word(0xdf)==0x4b3+(level-6)*50 && g_ram[0xe1]==0xc0 && word(0x2000)==65535));
}
void TlkCameraSetWidth(int width) { view_width=width>=256?width:256; }
int TlkCameraViewWidth(void) {
    /* Summit and postfight use the finite scripted camera, including when
     * entered during a free-size update before the host changes its view. */
    if(word(0x1ff9e)==9 && word(0xdf)==0x7db && g_ram[0xe1]==0xc0)
        return TlkResourcesViewportForScene(9);
    if(load_width)return load_width;
    /* A ride can begin inside the CPU update before its first displayed frame.
     * Its looping obstacle strip has console-width camera/trigger coordinates. */
    if(word(0x1ff9e)==1 && word(0xdf)==0x3b9 && g_ram[0xe1]==0xc0 && word(0xa56))
        return TlkResourcesViewportForScene(1);
    return view_width;
}
int TlkCameraProfileChanged(void) {
    int source=TlkResourcesUseMd("gameplay.camera");
    int changed=source!=previous_source || (source && previous_width!=view_width);
    previous_source=source;previous_width=view_width;return changed;
}
static int step(CpuState *cpu) {
    if (!TlkCameraActive() || cpu->m_flag || !cpu->x_flag || cpu->D || cpu->DB!=0x7e ||
        word(0x68)!=0xb293 || word(0xb2b7)!=0xb213) return 0;
    int ride=word(0x0a56)!=0;
    if(ride && word(0x1ff9e)!=1)return 0;
    int width=TlkCameraViewWidth();
    const unsigned c=0xb293,p=0xb213,draw=word(p+12);
    if (draw>0xfff5) return 0;
    TlkMdCameraState state={(int)word(c+8),(int)word(c+10)+1,(int)word(c+42),
        (int)word(c+44),word(c+38),word(c+40)};
    int min=(int)word(0xa6ec),max=(int)word(0xd8)+256-width;
    if (max<min) max=min;
    TlkMdCameraRules rules={min,max,16,(int)word(0xda)+1,width/2-32,
        width/2+32,128,210,64,20};
    /* A wider window moves the map's right camera limit left. Reaching that
     * new limit must still use the original eight-pixel streaming steps:
     * clamping hundreds of pixels at once leaves the native tile ring stale. */
    if(!ride && state.x>max+8)rules.max_x=state.x-8;
    /* Free-view look-ahead can be wider than the entire ride camera. Rebase
     * it on entry instead of leaving Simba outside its drawing range while
     * the ordinary one-pixel look adjustment catches up. */
    if(ride && state.look>width/2+32){
        /* Reframe the free-view camera before counting this update's road
         * travel. Otherwise its catch-up is credited as hundreds of pixels
         * ridden while Simba has barely moved, so the exit occurs too early.
         * The original accumulator compares current X with camera+12. Move
         * both references by the same framing shift; retain genuine motion. */
        int shift=state.look-(width/2-32),old_x=state.x;
        state.look=width/2-32;state.x+=shift;
        if(state.x<min)state.x=min;if(state.x>max)state.x=max;
        put(c+12,(int)word(c+12)+state.x-old_x);
    }
    if(ride){unsigned native,external;
        if(!TlkCantWaitRideValue(2,&native,&external))return 0;
        if(!g_ram[0x0a3e])rules.look_min=(int)external+(width-320)/2;
        rules.forward_only=1;
    }
    TlkMdCameraStep(&state,&rules,word(p+8),word(p+10),
        !!(word(draw+8)&0x40),g_ram[p+67],word(0x0a65)!=0);
    put(c+8,state.x);put(c+10,state.y-1);put(c+38,state.fraction_x);
    put(c+40,state.fraction_y);put(c+42,state.look);put(c+44,state.target_y);
    static FILE *trace;
    const char *path=getenv("TLK_CAMERA_TRACE");
    if (path && !trace) { trace=fopen(path,"w");if(trace) fprintf(trace,"width,x,y,look,player_x,player_y,frozen\n"); }
    if (trace) fprintf(trace,"%d,%d,%d,%d,%u,%u,%u\n",width,state.x,state.y,state.look,word(p+8),word(p+10),word(0x0a65));
    return 1;
}
RecompReturn TlkCameraDispatch(CpuState *cpu) {
    /* The caller already pushed its real RTL frame. Both sources run the
     * original prologue, frozen/script checks and streaming/return path.
     * The MD pre-opcode seam replaces only the arithmetic in between. */
    return TlkRunOriginal(cpu,0xb155,3);
}
static void pre(CpuState *cpu,uint32_t pc) {
    /* Keep the actual original distance accumulator,512-coordinate wrap,
     * actor relocation and streaming after selected MD camera arithmetic. */
    if (step(cpu)) interp_bridge_pre_opcode_redirect((pc&0xff0000)|(word(0x0a56)?0xb35f:0xb3c2));
}
/* The MD bridge stores logical camera Y minus one for the native raster.
 * Exile's falling rock reads that field for world placement and recycling.
 * Restore its logical value at those reads; keep the original allocator,
 * physics/floor query, contact, countdown and random decisions unchanged.
 * At 289/495 the original floor query reaches the ledge at507. Reading494
 * instead falls outside its +/-12 range and delays the real landing. */
static void world_camera_pre(CpuState *cpu,uint32_t pc){
    if((pc!=0xc16a94 && pc!=0xc16bdd) || word(0x1ff9e)!=4 || !TlkCameraActive() ||
       cpu->PB!=0xc1 || cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || cpu->_flag_D ||
       word(0xaa)!=0xb293 || cpu->A!=word(0xb29d))return;
    unsigned actor=word(0x68);
    if(actor<0xb313 || actor>=0xc213 || ((actor-0xb213)&127) ||
       word(actor+4)!=0x8cbc || g_ram[actor+6]!=0xc5)return;
    cpu->A=(cpu->A+1)&65535;cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
}
static void world_camera_after(CpuState *cpu,uint32_t pc){world_camera_pre(cpu,pc+2);}
void TlkCameraInstall(void) {
    g_tlk_camera_operand_pc_hook=world_camera_after;
    interp_bridge_add_pre_opcode_hook(0xc16a94,world_camera_pre);
    interp_bridge_add_pre_opcode_hook(0xc16bdd,world_camera_pre);
    interp_bridge_add_pre_opcode_hook(0xc0b19c,pre);
    interp_bridge_add_pre_opcode_hook(0x00b19c,pre);
}

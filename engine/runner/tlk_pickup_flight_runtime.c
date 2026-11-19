#include "tlk_pickup_flight_runtime.h"
#include "tlk_pickup_flight_motion.h"
#include "tlk_pickup_flight_role.h"
#include "tlk_camera.h"
#include "tlk_resources.h"
#include "tlk_wide.h"
#include "common_rtl.h"
#include <stdio.h>
#include <stdlib.h>
static unsigned word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static void put(unsigned at,unsigned value) { g_ram[at]=value;g_ram[at+1]=value>>8; }
int TlkPickupFlightSelected(void) { return TlkResourcesUseMd("gameplay.levels.pride_lands.pickup_flight"); }
int TlkPickupFlightProfileChanged(void) {
    static int previous;
    int next=TlkPickupFlightSelected(),changed=next!=previous;previous=next;return changed;
}
uint32_t TlkPickupFlightOpcode(CpuState *cpu,uint32_t pc) {
    if(!TlkPickupFlightSelected())return 0;
    unsigned actor=word(0x68),draw=actor<=0xff80?word(actor+12):0;
    int right=pc==0xc5531b || pc==0xc55343;
    uint32_t pose=right?0xc528bc:0xc528dd;
    if(cpu->m_flag || cpu->x_flag || cpu->DB!=0x7e || !cpu->D ||
       word(cpu->D)!=actor || !TlkPickupFlightDrawRole(g_ram,0x20000,draw,pose,true))return 0;
    unsigned width=(unsigned)TlkCameraViewWidth(),offset=right?width-256:0;
    /* Free view uses the same edge-relative flight coordinates as the original
     * viewports. The right-hand offset keeps its target at236 in actor space;
     * the presenter places that actor beside the selected view's right HUD. */
    if(width<256 || width>TLK_WIDE_MAX_WIDTH || (width&1)) {
        fprintf(stderr,"Unsupported pickup viewport %u\n",width);exit(121);
    }
    unsigned target=right?width-20-offset:16;
    TlkPickupFlightMotion motion={(uint16_t)word(actor+8),(uint16_t)word(actor+10),(uint16_t)word(actor+0x34)};
    unsigned before_x=motion.x,before_y=motion.y,before_step=motion.step;
    int initialize=pc==0xc5531b || pc==0xc554e7,arrived=0;
    if(initialize) {
        unsigned camera=word(0xaa);
        int column=TlkWideViewColumn((int)word(camera+8),(int)width);
        uint16_t x=(uint16_t)(motion.x+column-offset);
        if(!TlkPickupFlightBegin(&motion,x,motion.y,target,20)) {
            fprintf(stderr,"Unsupported pickup initialization at %u,%u\n",x,motion.y);exit(121);
        }
        put(actor+8,motion.x);put(0xa68e,motion.step);
    } else {
        /* Original code already added step and executed the shared animation.
         * Preserve its real displacement, then replace the clamp/arrival math. */
        motion.x=(uint16_t)(motion.x-motion.step);
        arrived=TlkPickupFlightAdvance(&motion,target,20,0,right);
        put(actor+8,motion.x);put(actor+10,motion.y);put(actor+0x34,motion.step);
    }
    const char *path=getenv("TLK_PICKUP_FLIGHT_TRACE");
    if(path && *path) {
        static FILE *log;
        if(!log) {log=fopen(path,"w");if(log)fputs("pc,actor,width,right,init,before_x,before_y,before_step,x,y,step,screen_x,arrived\n",log);}
        if(log) {fprintf(log,"%06x,%u,%u,%d,%d,%u,%u,%u,%u,%u,%u,%u,%d\n",pc,actor,width,right,initialize,before_x,before_y,before_step,motion.x,motion.y,motion.step,(motion.x+offset)&65535,arrived);fflush(log);}
    }
    if(initialize)return 0;
    return right?(arrived?0xc553b4:0xc5540c):(arrived?0xc5557e:0xc555c7);
}

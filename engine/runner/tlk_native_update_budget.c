/* Extra visible actors must not recreate the console CPU's RAM-only
 * collision/streaming bottleneck. Hardware/NMI/audio code retains its clocks. */
#include "common_rtl.h"
#include <stdint.h>
#include "tlk_resources.h"
extern int g_tlk_smooth_updates,g_tlk_render_world_ready,g_tlk_update_pending;
extern unsigned g_tlk_render_world_level,g_tlk_update_start_serial;
extern const unsigned *g_tlk_live_update_serial;
static unsigned word(unsigned p){return g_ram[p]|(unsigned)g_ram[p+1]<<8;}
uint64_t TlkNativeUpdateMasterBudget(unsigned pc,unsigned db,uint64_t original) {
    if(!g_tlk_smooth_updates || !g_tlk_render_world_ready || !g_tlk_update_pending ||
       !g_tlk_live_update_serial || db!=0x7e || !g_ram)
        return original;
    /* An NMI can upload OAM while the current update is still assembling it.
     * Upload serial changes do not end the RAM-work budget. The reviewed PC,
     * DB and live-world guards below exclude hardware transfers and waits. */
    /* These original routines only query/update WRAM, ROM map dictionaries,
     * actor queues, collision geometry and the sprite-tile cache lookup/LRU scan.
     * A84B builds RAM transfer packets; AA6B clears/packs RAM OAM entries;
     * AAFD..AF54 walks task lists/animation records (callbacks keep their timing).
     * C1C8DC..C958 scans cache metadata/timestamps, without touching the PPU.
     * Calls outside these intervals keep
     * their own normal timing, including all SPC/PPU accesses and waits. */
    pc&=0x3fffff;
    if(!((pc>=0x00a323 && pc<0x00a3a9) || (pc>=0x00a3c5 && pc<0x00a50f) || (pc>=0x00a84b && pc<0x00a96b) ||
         (pc>=0x00aa6b && pc<0x00aaf9) ||
         (pc>=0x00aafd && pc<0x00af55) ||
         (pc>=0x00b000 && pc<0x00c000) || (pc>=0x00c4a7 && pc<0x00cb00) ||
         (pc>=0x00d500 && pc<0x00d7d1) ||
         (pc>=0x0160d5 && pc<0x016451) ||
         (pc>=0x01c8dc && pc<0x01c959)))return original;
    unsigned level=word(0x1ff9e),scene=word(0xdf)|(unsigned)g_ram[0xe1]<<16;
    unsigned action=word(0xb243)|(unsigned)g_ram[0xb245]<<16,health=word(0x2004);
    /* Genesis rain moves every NTSC field. The native finale sets its ordinary
     * finished flag before creating all29 drops; excluding finished actors here
     * recreates the SNES CPU bottleneck and halves the visible rain/roar rate.
     * Only the previously reviewed RAM work above gets the extra budget.
     * Actor callbacks, waits, NMI, audio and source-off timing keep their clocks. */
    int md_finale=level==9 && level==g_tlk_render_world_level &&
        scene==0xc007db && action==0xc674be && word(0x2000)==0xffff &&
        !word(0xa89) && TlkResourcesUseMd("gameplay.levels.pride_rock.ending_timing");
    if(md_finale)return 1;
    if(level!=g_tlk_render_world_level || !health || health>=100 ||
       word(0xa6c2) || word(0xa6ba) || word(0xa89))return original;
    int main_scene=level<10 && level!=3 && action>=0xc30000 && action<0xc40000 &&
        (scene==0xc00387+level*50 || (level==0 && scene==0xc0080d) || (level==9 && scene==0xc007db));
    /* The live Timon controller already uses native sprite projection. Its
     * remaining tile-cache scans, RAM draw/upload packets and task-queue
     * administration can still consume a second NMI in crowded Hunts. Reuse
     * only those previously reviewed RAM regions: callbacks, movement, catch,
     * timer, hardware transfers and explicit waits keep their own clocks. */
    int hunt_work=(pc>=0x00a323 && pc<0x00af55) ||
        (pc>=0x00bb03 && pc<0x00bb80) || (pc>=0x01c8dc && pc<0x01c959);
    int hunt_scene=level>=11 && level<=13 && scene==0xc005dd+(level-10)*50 &&
        (word(0xb217)|(unsigned)g_ram[0xb219]<<16)==0xc5858a &&
        action>=0xc56000 && action<0xc58000;
    if(!main_scene && !(hunt_scene && hunt_work))return original;
    return 1;
}

/* Optional host presentation counter. No guest state or pacing changes.
 * Enable with TLK_FPS_COUNTER=1; TLK_FPS_LOG optionally records frame timing.
 * The SDL presenter shows an overlay; OpenGL shows the same counter in its
 * window title. Link wrappers keep the frozen gameplay/host objects intact. */
#include <SDL3/SDL.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "tlk_font8x8.h"
#include "common_rtl.h"
#include "snes/interp_bridge.h"
#include "tlk_wide.h"
#include "tlk_resources.h"

extern int snes_frame_counter;
extern int g_tlk_smooth_updates;
int g_tlk_main_update_field=-1;
int g_tlk_render_world_ready;
unsigned g_tlk_render_world_level=~0u;
const unsigned *g_tlk_live_update_serial;
unsigned g_tlk_update_start_serial;
int g_tlk_update_pending;
static void BeginGameUpdate(void) {
    g_tlk_main_update_field=snes_frame_counter;
    g_tlk_update_pending=g_tlk_live_update_serial!=NULL;
    if(g_tlk_live_update_serial)g_tlk_update_start_serial=*g_tlk_live_update_serial;
}
static int initialized,enabled;
static uint64_t first,last,sample_start,frequency;
static unsigned count;
static uint64_t updates,sample_updates;
static double update_fps;
static uint64_t render_updates,sample_render_updates;
static unsigned previous_serial;
static int have_serial;
static double render_update_fps;
static void (*previous_pad_hook)(void);
extern void (*g_tlk_aot_pad_read_hook)(void);
static void CountCompiledUpdate(void) {
    BeginGameUpdate();
    updates++;
    if(previous_pad_hook)previous_pad_hook();
}
static void CountInterpretedUpdate(CpuState *cpu,uint32_t pc) {
    (void)cpu;(void)pc;BeginGameUpdate();updates++;
}
static double fps,worst,shown_worst;
static FILE *log_file;
static char label[80]="FPS: measuring...";

static int UpdateCounter(void) {
    if(!initialized) {
        initialized=1;
        const char *value=getenv("TLK_FPS_COUNTER");
        enabled=value && !strcmp(value,"1");
        frequency=SDL_GetPerformanceFrequency();
        const char *path=getenv("TLK_FPS_LOG");
        if(path && *path) {
            log_file=fopen(path,"w");
            if(log_file)fputs("seconds,field,interval_ms,fps,max_frame_ms,updates,update_fps,level,scene,pause,health,render_updates,render_update_fps,stage,finished,hazard,action\n",log_file);
        }
    }
    /* The game's single pad read marks a main-loop update. Chain the normal
     * tape/live-input callback; never consume an extra word or change the pad.
     * A repeated PC presentation does not increment this counter. */
    if(g_tlk_aot_pad_read_hook!=CountCompiledUpdate) {
        previous_pad_hook=g_tlk_aot_pad_read_hook;
        g_tlk_aot_pad_read_hook=CountCompiledUpdate;
    }
    interp_bridge_add_pre_opcode_hook(0xc0a07c,CountInterpretedUpdate);
    /* Observe completed draws in the native viewport too. Enabling capture
     * leaves the selected viewport/presenter and guest spawn lead unchanged. */
    if((enabled || log_file || g_tlk_smooth_updates) && !TlkWideEnabled())TlkWideEnable(true);
    g_tlk_live_update_serial=TlkWideUpdateSerialSource();
    g_tlk_render_world_ready=TlkWideGetStats().stage;
    if(TlkResourcesViewportWidth()==256)g_tlk_render_world_ready=TlkWideFrameStageActive();
    g_tlk_render_world_level=TlkWideFrameLevel();
    if(!enabled && !log_file)return 0;
    unsigned serial=TlkWideFrameUpdateSerial();
    if(have_serial && serial!=previous_serial)render_updates++;
    previous_serial=serial;have_serial=1;
    uint64_t now=SDL_GetPerformanceCounter();
    double ms=last?(now-last)*1000.0/frequency:0;
    if(!first)first=sample_start=now;
    if(ms>worst)worst=ms;
    if(last)count++;
    if(now-sample_start>=frequency/2) {
        fps=count*(double)frequency/(now-sample_start);
        update_fps=(updates-sample_updates)*(double)frequency/(now-sample_start);
        sample_updates=updates;
        render_update_fps=(render_updates-sample_render_updates)*(double)frequency/(now-sample_start);
        sample_render_updates=render_updates;
        shown_worst=worst;
        snprintf(label,sizeof label,"UPDATES:%5.1f  FPS:%5.1f  MAX:%5.1fms",render_update_fps,fps,shown_worst);
        count=0;sample_start=now;worst=0;
        if(log_file)fflush(log_file);
    }
    if(log_file)fprintf(log_file,"%.6f,%d,%.3f,%.2f,%.3f,%llu,%.2f,%u,%06x,%u,%u,%llu,%.2f,%u,%u,%u,%06x\n",
        (now-first)/(double)frequency,snes_frame_counter,ms,fps,shown_worst,
        (unsigned long long)updates,update_fps,
        (unsigned)(g_ram[0x1ff9e]|g_ram[0x1ff9f]<<8),
        (unsigned)(g_ram[0xdf]|g_ram[0xe0]<<8|g_ram[0xe1]<<16),
        (unsigned)(g_ram[0xa89]|g_ram[0xa8a]<<8),
        (unsigned)(g_ram[0x2004]|g_ram[0x2005]<<8),
        (unsigned long long)render_updates,render_update_fps,TlkWideGetStats().stage,
        (unsigned)(g_ram[0xa6c2]|g_ram[0xa6c3]<<8),
        (unsigned)(g_ram[0xa6ba]|g_ram[0xa6bb]<<8),
        (unsigned)(g_ram[0xb243]|g_ram[0xb244]<<8|g_ram[0xb245]<<16));
    last=now;
    return enabled;
}

static void DrawCounter(SDL_Renderer *renderer) {
    int w,h;if(!SDL_GetCurrentRenderOutputSize(renderer,&w,&h))return;
    const int scale=w>=850?2:1;
    int text_width=(int)strlen(label)*8*scale,x=(w-text_width)/2,y=6;
    SDL_Rect viewport,clip;float sx,sy;Uint8 r,g,b,a;
    bool viewport_set=SDL_RenderViewportSet(renderer);
    SDL_GetRenderViewport(renderer,&viewport);SDL_GetRenderClipRect(renderer,&clip);
    bool clipped=SDL_RenderClipEnabled(renderer);
    SDL_GetRenderScale(renderer,&sx,&sy);SDL_GetRenderDrawColor(renderer,&r,&g,&b,&a);
    SDL_SetRenderScale(renderer,1,1);SDL_SetRenderViewport(renderer,NULL);SDL_SetRenderClipRect(renderer,NULL);
    SDL_SetRenderDrawColor(renderer,0,0,0,255);
    SDL_FRect panel={(float)(x-4),(float)(y-3),(float)(text_width+8),(float)(8*scale+6)};
    SDL_RenderFillRect(renderer,&panel);
    SDL_FRect pixels[2048];int n=0;
    for(unsigned i=0;label[i];i++) {
        unsigned c=(unsigned char)label[i];if(c<32 || c>126)c='?';
        for(int row=0;row<8;row++)for(int col=0;col<8;col++)
            if(kTlkFont8x8[c-32][row]&(1u<<col)) {
                if(n<(int)(sizeof pixels/sizeof *pixels))pixels[n++]=(SDL_FRect){
                    (float)(x+((int)i*8+col)*scale),(float)(y+row*scale),(float)scale,(float)scale};
            }
    }
    SDL_SetRenderDrawColor(renderer,render_update_fps<55?255:240,render_update_fps<55?100:240,80,255);
    SDL_RenderFillRects(renderer,pixels,n);
    SDL_SetRenderViewport(renderer,viewport_set?&viewport:NULL);SDL_SetRenderClipRect(renderer,clipped?&clip:NULL);
    SDL_SetRenderScale(renderer,sx,sy);SDL_SetRenderDrawColor(renderer,r,g,b,a);
}

extern bool __real_SDL_RenderPresent(SDL_Renderer *renderer);
bool __wrap_SDL_RenderPresent(SDL_Renderer *renderer) {
    if(UpdateCounter())DrawCounter(renderer);
    return __real_SDL_RenderPresent(renderer);
}

extern bool __real_SDL_GL_SwapWindow(SDL_Window *window);
bool __wrap_SDL_GL_SwapWindow(SDL_Window *window) {
    static char previous[80];
    if(UpdateCounter() && strcmp(previous,label)) {
        char title[128];snprintf(title,sizeof title,"The Lion King | %s",label);
        SDL_SetWindowTitle(window,title);snprintf(previous,sizeof previous,"%s",label);
    }
    return __real_SDL_GL_SwapWindow(window);
}

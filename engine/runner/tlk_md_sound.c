#include "tlk_md_sound.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include "sha256.h"
#include "tlk_state_bytes.h"
#ifdef _WIN32
#include <windows.h>
#else
#include <dlfcn.h>
#endif

typedef struct { const char *key,*value; } Variable;
typedef struct { const char *path; const void *data; size_t size; const char *meta; } GameInfo;
typedef struct {
    const char *full_path,*archive_path,*archive_file,*dir,*name,*ext,*meta;
    const void *data;size_t size;bool file_in_archive,persistent_data;
} GameInfoExt;
typedef struct { unsigned base_w,base_h,max_w,max_h; float aspect; } Geometry;
typedef struct { double fps,sample_rate; } Timing;
typedef struct { Geometry geometry; Timing timing; } AvInfo;
typedef int (*Environment)(unsigned,void*);
/* libretro bool is a C bool (one byte), including callback return values. */
#include <stdbool.h>
typedef bool (*EnvCallback)(unsigned,void*);
static void *library;
static void (*run)(void),(*unload)(void),(*deinit)(void),(*reset)(void),(*set_reg)(int,unsigned);
static size_t (*serialize_size)(void);
static unsigned (*state_revision)(void);
static bool (*serialize)(void*,size_t),(*unserialize)(const void*,size_t);
static uint8_t rom_hash[32];
/* A driver restart must not inherit libretro soft-reset randomness or clocks
 * from a prior song/session. The pinned continuation backend can restore its
 * complete warmed startup state, including chip/filter/sample timing. */
static uint8_t *startup_state;
static size_t startup_size;
static uint8_t *ram,*rom_copy;
static GameInfoExt content;
static int ready,loaded,initialized;
static char status[160]="MD sound driver unavailable";
static struct { char key[128],value[256]; } variables[256];
static unsigned variable_count;
enum { RING=32768, QUEUE=32 };
static int16_t samples[RING*2];
static uint64_t write_at,read_at;
static double phase,rate=44100;
static struct { unsigned selector,value; } commands[QUEUE];
static unsigned command_count;
static int recording;
static FILE *command_trace;
static unsigned long command_serial;

static void *symbol(const char *name) {
#ifdef _WIN32
    return (void*)GetProcAddress((HMODULE)library,name);
#else
    return dlsym(library,name);
#endif
}
static bool environment(unsigned cmd,void *data) {
    /* The pinned core uses GET_GAME_INFO_EXT for memory content; ordinary
     * retro_game_info.data is ignored by its need_fullpath path. Keep the
     * verified payload alive until deinit, independent of cwd/source filename. */
    if(cmd==65)return true; /* content-info override: frontend supplies memory */
    if(cmd==66 && content.data) { *(const GameInfoExt**)data=&content;return true; }
    if (cmd==10) { int format=*(int*)data; return format>=0 && format<=2; }
    if (cmd==16) {
        const Variable *v=(const Variable*)data; variable_count=0;
        for (unsigned i=0;v[i].key && variable_count<256;i++) {
            const char *start=strstr(v[i].value,"; "); start=start?start+2:v[i].value;
            size_t length=strcspn(start,"|");
            snprintf(variables[variable_count].key,128,"%s",v[i].key);
            snprintf(variables[variable_count].value,256,"%.*s",(int)length,start);
            variable_count++;
        }
        return true;
    }
    if (cmd==15) {
        Variable *v=(Variable*)data;
        for (unsigned i=0;i<variable_count;i++) if (!strcmp(v->key,variables[i].key)) {
            v->value=variables[i].value; return true;
        }
        v->value=NULL; return false;
    }
    if (cmd==17) { *(bool*)data=false; return true; }
    if (cmd==9 || cmd==31) { *(const char**)data="."; return true; }
    if (cmd==3 || cmd==18) { *(bool*)data=true; return true; }
    return false;
}
static void video(const void *data,unsigned w,unsigned h,size_t pitch) { (void)data;(void)w;(void)h;(void)pitch; }
static void sample(int16_t l,int16_t r) { (void)l;(void)r; }
static size_t batch(const int16_t *data,size_t count) {
    if (recording) for (size_t i=0;i<count;i++) {
        if (write_at-read_at>=RING) break;
        unsigned at=(unsigned)(write_at++&(RING-1))*2;
        samples[at]=data[i*2]; samples[at+1]=data[i*2+1];
    }
    return count;
}
static void poll(void) {}
static int16_t input(unsigned port,unsigned device,unsigned index,unsigned id) { (void)port;(void)device;(void)index;(void)id;return 0; }
void TlkMdSoundClearOutput(void) { read_at=write_at=0;phase=0; }
void TlkMdSoundClose(void) {
    ready=0;recording=0;
    free(startup_state);startup_state=NULL;startup_size=0;
    if (library) {
        if (loaded && unload) unload();
        if (initialized && deinit) deinit();
#ifdef _WIN32
        FreeLibrary((HMODULE)library);
#else
        dlclose(library);
#endif
    }
    library=NULL;loaded=initialized=0;ram=NULL;run=NULL;unload=NULL;deinit=NULL;set_reg=NULL;
    serialize_size=NULL;serialize=NULL;unserialize=NULL;state_revision=NULL;
    memset(&content,0,sizeof content);
    free(rom_copy);rom_copy=NULL;command_count=0;TlkMdSoundClearOutput();
    if (command_trace) { fclose(command_trace);command_trace=NULL; }command_serial=0;
}
int TlkMdSoundInit(const uint8_t *rom,size_t size) {
    if (ready) return 1;
    TlkMdSoundClose();
    if (!rom || size!=0x300000) return 0;
#ifdef _WIN32
    /* Search beside the player, never in a writable current-directory DLL path. */
    char path[4096];
    DWORD n=GetModuleFileNameA(NULL,path,sizeof path);
    if (!n || n>=sizeof path) return 0;
    char *sep=strrchr(path,'\\');
    if (!sep || (size_t)(sep-path)+40>=sizeof path) return 0;
    strcpy(sep+1,"genesis_plus_gx_libretro.dll");
    library=(void*)LoadLibraryA(path);
#else
    library=dlopen("./genesis_plus_gx_libretro.so",RTLD_NOW|RTLD_LOCAL);
#endif
    if (!library) { snprintf(status,sizeof status,"MD sound library missing beside player");return 0; }
#define LOAD(ret,args,name,var) ret (*var) args=(ret(*)args)symbol(name); if (!var) goto failed
    LOAD(void,(EnvCallback),"retro_set_environment",set_environment);
    LOAD(void,(void(*)(const void*,unsigned,unsigned,size_t)),"retro_set_video_refresh",set_video);
    LOAD(void,(void(*)(int16_t,int16_t)),"retro_set_audio_sample",set_sample);
    LOAD(void,(size_t(*)(const int16_t*,size_t)),"retro_set_audio_sample_batch",set_batch);
    LOAD(void,(void(*)(void)),"retro_set_input_poll",set_poll);
    LOAD(void,(int16_t(*)(unsigned,unsigned,unsigned,unsigned)),"retro_set_input_state",set_input);
    LOAD(void,(void),"retro_init",init);
    LOAD(bool,(const GameInfo*),"retro_load_game",load);
    LOAD(void,(AvInfo*),"retro_get_system_av_info",get_av);
    run=(void(*)(void))symbol("retro_run");unload=(void(*)(void))symbol("retro_unload_game");
    reset=(void(*)(void))symbol("retro_reset");
    deinit=(void(*)(void))symbol("retro_deinit");set_reg=(void(*)(int,unsigned))symbol("m68k_set_reg");
    ram=(uint8_t*)symbol("work_ram");
    serialize_size=(size_t(*)(void))symbol("retro_serialize_size");
    serialize=(bool(*)(void*,size_t))symbol("retro_serialize");
    unserialize=(bool(*)(const void*,size_t))symbol("retro_unserialize");
    state_revision=(unsigned(*)(void))symbol("tlk_audio_state_revision");
    if (!run || !unload || !deinit || !reset || !set_reg || !ram || !serialize_size || !serialize || !unserialize) goto failed;
    rom_copy=(uint8_t*)malloc(size);if (!rom_copy) goto failed;
    memcpy(rom_copy,rom,size);
    content=(GameInfoExt){"lionking-verified.md",NULL,NULL,".","lionking-verified","md",NULL,rom_copy,size,false,true};
    sha256_compute(rom,size,rom_hash);
    set_environment(environment);set_video(video);set_sample(sample);set_batch(batch);set_poll(poll);set_input(input);
    init();initialized=1;
    GameInfo game={"Lion King, The (World).md",rom_copy,size,NULL};
    if (!load(&game)) goto failed;
    loaded=1;
    AvInfo av;memset(&av,0,sizeof av);get_av(&av);rate=av.timing.sample_rate;
    if (rate<8000 || rate>192000) goto failed;
    for (unsigned i=0;i<180;i++) run();
    if(state_revision && state_revision()==1) {
        startup_size=serialize_size();
        if(!startup_size || startup_size>8u*1024u*1024u)goto failed;
        startup_state=(uint8_t*)malloc(startup_size);
        if(!startup_state || !serialize(startup_state,startup_size))goto failed;
    }
    TlkMdSoundClearOutput();ready=1;recording=1;
    const char *trace_path=getenv("TLK_MD_SOUND_COMMANDS");
    if (trace_path) { command_trace=fopen(trace_path,"w");if (command_trace) fprintf(command_trace,"serial,selector,value\n"); }
    snprintf(status,sizeof status,"Original MD sound driver ready");return 1;
failed:
    snprintf(status,sizeof status,"MD sound library initialization failed");
    TlkMdSoundClose();return 0;
#undef LOAD
}
int TlkMdSoundReady(void) { return ready; }
const char *TlkMdSoundStatus(void) { return status; }
void TlkMdSoundRestart(void) {
    if (!ready) return;
    recording=0;
    if(startup_state) {
        if(!unserialize(startup_state,startup_size)) {
            ready=0;snprintf(status,sizeof status,"MD startup checkpoint rejected; native audio fallback");
        }
    } else {
        /* Legacy libraries have no full audio continuation extension. Keep
         * their prior reset fallback; exact restart requires the pinned core. */
        reset();for (unsigned i=0;i<180;i++) run();
    }
    command_count=0;TlkMdSoundClearOutput();recording=ready;
}
void TlkMdSoundCommand(unsigned selector,unsigned value) {
    if (!ready || selector>29 || selector==24 || command_count>=QUEUE || (selector>=20 && value!=(selector==23?113:125))) return;
    commands[command_count].selector=selector;commands[command_count++].value=value&65535;
    if (command_trace) { fprintf(command_trace,"%lu,%u,%u\n",command_serial++,selector,value&65535);fflush(command_trace); }
}
void TlkMdSoundPcm(unsigned sample,unsigned parameter) {
    if(!ready || command_count>=QUEUE || sample>65535 || parameter>65535)return;
    /* Internal selector24 keeps the explicit pair in the existing queue
     * envelope. The driver receives selector19, zero-extended D0 and D1. */
    commands[command_count].selector=24;
    commands[command_count++].value=sample|(parameter<<16);
    if(command_trace){fprintf(command_trace,"%lu,19,%u\n",command_serial++,sample);fflush(command_trace);}
    static FILE *pcm_trace;static int checked;
    if(!checked){checked=1;const char*p=getenv("TLK_MD_PCM_REQUESTS");if(p)pcm_trace=fopen(p,"w");if(pcm_trace)fputs("sample,parameter\n",pcm_trace);}
    if(pcm_trace){fprintf(pcm_trace,"%u,%u\n",sample,parameter);fflush(pcm_trace);}
}
void TlkMdSoundInterlevelSample(unsigned sample){if(sample<2)TlkMdSoundCommand(20+sample,125);}
void TlkMdSoundInterlevelStop(void){TlkMdSoundCommand(22,125);}
void TlkMdSoundBonusResultSample(void){TlkMdSoundCommand(23,113);}
void TlkMdSoundCliffSample(void){TlkMdSoundCommand(25,125);}
void TlkMdSoundCliffStop(void){TlkMdSoundCommand(26,125);}
void TlkMdSoundExileExitSample(unsigned sample){if(sample<2)TlkMdSoundCommand(27+sample,125);}
void TlkMdSoundOpeningTimonSample(void){TlkMdSoundCommand(29,125);}
static void emit_word(unsigned *at,unsigned word) {
    ram[(*at)++]=(uint8_t)word;ram[(*at)++]=(uint8_t)(word>>8);
}
static int produce(void) {
    unsigned at=0xfe00;
    unsigned used=0;
    for (;used<command_count;used++) {
        unsigned i=used,selector=commands[i].selector;
        unsigned bytes=selector==24?20:selector>=20?22:selector==19?14:12;
        if(at+bytes+10>65536)break; /* Retain overflow commands for the next audio field. */
        if(selector==24){
            emit_word(&at,0x7000); /* original wrapper clears full D0 */
            emit_word(&at,0x303c);emit_word(&at,commands[i].value&65535);
            emit_word(&at,0x7200); /* original wrapper clears full D1 */
            emit_word(&at,0x323c);emit_word(&at,commands[i].value>>16);
            emit_word(&at,0x7e13);
            emit_word(&at,0x4eb9);emit_word(&at,0x002d);emit_word(&at,0x0000);continue;
        }
        if(selector>=20){
            unsigned source=selector==29?0x2d191e:selector==28?0x2e8000:selector==27?0x2e0000:selector>=25?0x2d4ab8:selector==23?0x2f2d6a:selector==21?0x2dc756:0x2d8000;
            unsigned size=selector==29?0x319a:selector==28?0x3a08:selector==27?0x2bbe:selector==26?2:selector==25?0x17c2:selector==23?0x51c3:selector==22?2:selector==21?0x2922:0x4756;
            emit_word(&at,0x203c);emit_word(&at,source>>16);emit_word(&at,source&65535);
            emit_word(&at,0x243c);emit_word(&at,0);emit_word(&at,size);
            emit_word(&at,0x323c);emit_word(&at,selector==23?113:125);
            emit_word(&at,0x4eb9);emit_word(&at,0x002d);emit_word(&at,0x08d8);continue;
        }
        emit_word(&at,0x303c);emit_word(&at,commands[i].value);
        if (commands[i].selector==19) emit_word(&at,0x7260); /* original PCM parameter D1=96 */
        emit_word(&at,0x7e00|commands[i].selector);
        emit_word(&at,0x4eb9);emit_word(&at,0x002d);emit_word(&at,0x0000);
    }
    command_count-=used;if(command_count)memmove(commands,commands+used,command_count*sizeof *commands);
    emit_word(&at,0x7e00);emit_word(&at,0x4eb9);emit_word(&at,0x002d);emit_word(&at,0x0000);emit_word(&at,0x60fe);
    set_reg(17,0x2700);set_reg(15,0xfffd00);set_reg(16,0xfffe00);
    uint64_t before=write_at;run();return write_at>before;
}
int TlkMdSoundRender(int16_t *dst,unsigned frames,unsigned output_rate) {
    if (!dst || !ready || output_rate<8000 || output_rate>192000) return 0;
    double step=rate/output_rate;
    for (unsigned i=0;i<frames;i++) {
        while (write_at-read_at<2+(unsigned)step) if (!produce()) return 0;
        unsigned a=(unsigned)(read_at&(RING-1))*2,b=(unsigned)((read_at+1)&(RING-1))*2;
        for (unsigned ch=0;ch<2;ch++) dst[i*2+ch]=(int16_t)(samples[a+ch]+(samples[b+ch]-samples[a+ch])*phase);
        phase+=step;unsigned advance=(unsigned)phase;read_at+=advance;phase-=advance;
    }
    return 1;
}

/* Explicit envelope around the pinned core's opaque libretro state. Host
 * queues/ring/resampling are outside that blob and must travel with it. */
enum { SOUND_HEADER=120, SOUND_CORE_MAX=8*1024*1024 };
size_t TlkMdSoundStateSize(void) {
    if (!ready || !state_revision || state_revision()!=1) return 0;
    size_t core=serialize_size();
    return core && core<=SOUND_CORE_MAX ? SOUND_HEADER+RING*4+command_count*8+core : 0;
}
static int state_hash(const uint8_t *data,size_t size,uint8_t hash[32]) {
    uint8_t *copy=(uint8_t*)malloc(size);if(!copy)return 0;
    memcpy(copy,data,size);memset(copy+88,0,32);sha256_compute(copy,size,hash);free(copy);return 1;
}
int TlkMdSoundSaveState(uint8_t *out,size_t size) {
    size_t total=TlkMdSoundStateSize();if(!out || !total || size!=total)return 0;
    size_t core=serialize_size();memset(out,0,size);memcpy(out,"TLKMDS01",8);
    TlkPut32(out+8,1);TlkPut32(out+12,(uint32_t)core);
    TlkPut64(out+16,write_at);TlkPut64(out+24,read_at);
    TlkPutDouble(out+32,phase);TlkPutDouble(out+40,rate);TlkPut32(out+48,command_count);
    TlkPut32(out+52,state_revision());
    memcpy(out+56,rom_hash,32);
    size_t at=SOUND_HEADER;
    for(unsigned i=0;i<RING*2;i++,at+=2) { unsigned v=(uint16_t)samples[i];out[at]=(uint8_t)v;out[at+1]=(uint8_t)(v>>8); }
    for(unsigned i=0;i<command_count;i++,at+=8) { TlkPut32(out+at,commands[i].selector);TlkPut32(out+at+4,commands[i].value); }
    if(!serialize(out+at,core))return 0;
    uint8_t hash[32];if(!state_hash(out,size,hash))return 0;memcpy(out+88,hash,32);return 1;
}
int TlkMdSoundValidateState(const uint8_t *data,size_t size) {
    if(!data || size<SOUND_HEADER+RING*4 || size>SOUND_HEADER+RING*4+QUEUE*8+SOUND_CORE_MAX ||
       memcmp(data,"TLKMDS01",8) || TlkGet32(data+8)!=1 || TlkGet32(data+52)!=1)return 0;
    unsigned core=TlkGet32(data+12),count=TlkGet32(data+48);
    uint64_t w=TlkGet64(data+16),r=TlkGet64(data+24);
    double p=TlkGetDouble(data+32),hz=TlkGetDouble(data+40);
    if(!core || core>SOUND_CORE_MAX || count>QUEUE || size!=SOUND_HEADER+RING*4+count*8+core ||
       w<r || w-r>RING || !isfinite(p) || p<0 || p>=1 || !isfinite(hz) || hz<8000 || hz>192000)return 0;
    for(unsigned i=0;i<count;i++) {
        size_t at=SOUND_HEADER+RING*4+i*8;
        unsigned selector=TlkGet32(data+at),value=TlkGet32(data+at+4);
        if(selector>29 || (selector!=24 && value>65535) ||
           (selector>=20 && selector!=24 && value!=(selector==23?113:125)))return 0;
    }
    uint8_t hash[32];return state_hash(data,size,hash) && !memcmp(hash,data+88,32);
}
int TlkMdSoundLoadState(const uint8_t *data,size_t size) {
    if(!ready || !state_revision || state_revision()!=1 || !TlkMdSoundValidateState(data,size) || memcmp(data+56,rom_hash,32) ||
       TlkGet32(data+12)!=serialize_size() || TlkGetDouble(data+40)!=rate)return 0;
    unsigned core=TlkGet32(data+12),count=TlkGet32(data+48);
    uint8_t *backup=(uint8_t*)malloc(core);if(!backup)return 0;
    if(!serialize(backup,core)) { free(backup);return 0; }
    int was_recording=recording;recording=0;
    int ok=unserialize(data+SOUND_HEADER+RING*4+count*8,core);
    if(!ok)unserialize(backup,core);
    recording=was_recording;free(backup);if(!ok)return 0;
    size_t at=SOUND_HEADER;
    for(unsigned i=0;i<RING*2;i++,at+=2)samples[i]=(int16_t)((unsigned)data[at]|(unsigned)data[at+1]<<8);
    for(unsigned i=0;i<count;i++,at+=8) { commands[i].selector=TlkGet32(data+at);commands[i].value=TlkGet32(data+at+4); }
    command_count=count;write_at=TlkGet64(data+16);read_at=TlkGet64(data+24);phase=TlkGetDouble(data+32);return 1;
}

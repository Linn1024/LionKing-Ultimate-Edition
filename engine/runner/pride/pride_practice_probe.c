/* Extend complete prepared saves to the earlier checkpoint reload. */
#include "common_rtl.h"
static bool preparation_frame(uint32 inputs);
#define RtlRunFrame preparation_frame
#include "tlk_resources.h"
static int preparation_scene_presentation(void) { return 1; }
#define TlkResourcesPresentation preparation_scene_presentation
#include "pride_practice_context.c"
#undef TlkResourcesPresentation
#undef RtlRunFrame
#include "pride_scene_render_bridge.h"
#include "pride_prepared_history_api.h"
#include "pride_preparation_cache.h"
#include <errno.h>
static void practice_frame_begin(void);
static void practice_frame_complete(void);
static bool preparation_frame(uint32 inputs) {
    if(!TlkPrideHealthDeathSelected())return RtlRunFrame(inputs);
    practice_frame_begin();preparation_rehydrate();bool result=RtlRunFrame(inputs);
    practice_frame_complete();
#ifdef TLK_NATIVE_BANK_SDL
    static FILE *journal;
    if(!journal) {
        char path[4096];snprintf(path,sizeof path,"%s/practice-fields.csv",TlkPrideSetting("TLK_SCENE_OWNER_PROBE"));
        journal=TlkPrideFileOpen(path,"w");if(!journal)exit(95);
        fprintf(journal,"field,frontend_before_increment,level,state,pr_state,fresh,loading,practice,health,wav_frames_before_audio\n");
    }
    fprintf(journal,"%u,%ld,%u,%u,%u,%u,%u,%u,%u,%u\n",(unsigned)snes_frame_counter,frame,
        ow(0x1ff9e),ow(8),(unsigned)pr.st,(unsigned)pr.fresh,(unsigned)pr.loading,(unsigned)s_practice,ow(0x2004),s_wav_frames);fflush(journal);
#endif
    return result;
}
void PrideRepeatRenderBegin(unsigned);
static char repeat_debug_folder[4096];
static char restart_debug_folder[4096];
static unsigned restart_serial;
const char *PrideRepeatDebugFolder(void) {
    return repeat_debug_folder[0]?repeat_debug_folder:TlkPrideSetting("TLK_SCENE_OWNER_PROBE");
}
void PrideRepeatSceneBegin(void) {
    /* A genuine new eligible death owns this transition. Keep immutable cold
     * payloads, program identities and live producer/audio clocks. */
    if(owner_waiting || grounded_waiting || scene_active || preparation_pending)exit(92);
    if(owner_scene.started) {
        snprintf(repeat_debug_folder,sizeof repeat_debug_folder,"%s/scene-%u",restart_debug_folder[0]?restart_debug_folder:TlkPrideSetting("TLK_SCENE_OWNER_PROBE"),(unsigned)snes_frame_counter+1);
#ifdef _WIN32
        TlkPrideMakeDirectory(repeat_debug_folder);
#endif
        probe_dir=repeat_debug_folder;scene_folder=repeat_debug_folder;
    }
    memset(&owner_scene,0,sizeof owner_scene);
    owner_loop=owner_skip=owner_hold_count=owner_ended=0;
    owner_initial_hold=owner_waiting=owner_normal_release=owner_first_hold_pose=0;
    owner_normal_latch_serial=0;
    owner_default_initialized=owner_default_prepared=owner_default_advancing=0;
    owner_default_advanced=owner_default_advance_wait=owner_default_callback=0;
    grounded_done=grounded_waiting=0;
    restore_pending=restore_committed=restore_canonical_calls=0;
    restore_health=restore_roar=0;
    /* Font context is the last actual native rebuild, even on cache hits.
     * It is a live producer cache rather than a death-local reset flag. */
    applied=0;scene_template_applies=0;scene_death=1;
    PrideRepeatRenderBegin((unsigned)snes_frame_counter+1);
}
int PrideSceneRenderView(TlkDeathScene *scene,TlkDeathProgram *program) {
    if(!owner_enabled || !owner_scene.started)return 0;
    *scene=owner_scene;*program=owner_program;return 1;
}
int PrideSceneNormalStarted(void) { return owner_scene.started && owner_enabled && owner_normal_release && owner_ended; }
unsigned PrideSceneNormalLatch(void) { return owner_normal_latch_serial; }
int PrideHandoffHistoryCheck(const PridePreparedHistory *,const TlkDeathScene *,uint32_t,unsigned,unsigned,
    const uint8_t *,size_t);
uint32_t PrideCurrentGraphicsChoices(void);
int __real_tlk_state_save(const char *,uint32_t);
int __real_tlk_state_load(const char *,uint32_t *);
int __wrap_tlk_state_save(const char *path,uint32_t field) {
#ifdef TLK_NATIVE_BANK_SDL
    /* SDL saves after audio but before Present; headless already composed the
     * completed field. Materialize this field's owned history before recording
     * it, including the very first freeze and the final staged draw batch.
     * This touches presentation storage only, never guest/PPU/audio clocks. */
    int width=WideWidth();
    if(width<256)return 0;
    int rendered=0;
    if(s_view_height!=224 && TlkWideAreaSupported())rendered=TlkWideDrawArea(s_wide_px,width,s_view_height,s_wide_hud!=0,NULL);
    else rendered=TlkWideDraw(s_wide_px,width,s_wide_hud!=0);
    if(!rendered)return 0;
#endif
    uint8_t *history=NULL,*cache=NULL;size_t history_size=0,cache_size=0;
    if(!PridePreparedHistorySave(field,&history,&history_size) || !preparation_save(field,&cache,&cache_size)) {
        free(history);free(cache);return 0;
    }
    if(!__real_tlk_state_save(path,field)) { free(history);free(cache);return 0; }
    size_t native_size=0;uint8_t *native=read_file(path,&native_size);
    size_t size=native_size+history_size+cache_size+32;
    uint8_t *out=native && size<=64*1024*1024?malloc(size):NULL;
    if(!out) { free(native);free(history);free(cache);remove(path);return 0; }
    memcpy(out,native,native_size);memcpy(out+native_size,history,history_size);
    memcpy(out+native_size+history_size,cache,cache_size);
    uint8_t *footer=out+size-32;memset(footer,0,32);memcpy(footer,"PRPEND01",8);
    TlkPut32(footer+8,(uint32_t)native_size);TlkPut32(footer+12,(uint32_t)history_size);
    TlkPut32(footer+16,(uint32_t)cache_size);TlkPut32(footer+20,1);
    char temporary[4096]={0};int ok=temp_path(temporary,sizeof temporary,path,".prepared.part");
    if(ok)ok=write_file(temporary,out,size);free(out);free(native);free(history);free(cache);
    if(ok) {
#ifdef _WIN32
        ok=MoveFileExA(temporary,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
        ok=rename(temporary,path)==0;
#endif
    }
    if(!ok) { remove(path);if(temporary[0])remove(temporary); }return ok;
}
int __wrap_tlk_state_load(const char *path,uint32_t *field) {
    size_t size=0;uint8_t *data=read_file(path,&size);if(!data)return 0;
    int ok=size>=68 && !preparation_pending;const uint8_t *footer=ok?data+size-32:NULL;
    uint32_t native_size=0,history_size=0,cache_size=0,saved_field=0;
    if(ok) {
        native_size=TlkGet32(footer+8);history_size=TlkGet32(footer+12);cache_size=TlkGet32(footer+16);
        ok=!memcmp(footer,"PRPEND01",8) && TlkGet32(footer+20)==1 && !TlkGet32(footer+24) && !TlkGet32(footer+28) &&
            native_size>=36 && history_size>=96 && cache_size>=96 &&
            (uint64_t)native_size+history_size+cache_size+32==size;
        if(ok)saved_field=TlkGet32(data+12);
    }
    if(ok && !memcmp(data+native_size,"PRHHIST1",8) && TlkGet32(data+native_size+8)==1 &&
       TlkGet32(data+native_size+80)!=PrideCurrentGraphicsChoices())
        pride_state_set_error("Match the saved graphics choices and retry");
    PridePreparedHistory *candidate=ok?PridePreparedHistoryStage(data+native_size,history_size,saved_field):NULL;
    if(candidate && (!handoff_load_scene || !handoff_load_values ||
       !PrideHandoffHistoryCheck(candidate,handoff_load_scene,
            handoff_load_values[STATE_owner_entry_field],handoff_load_values[STATE_owner_ended],
            handoff_load_values[STATE_owner_normal_latch_serial],data,native_size))) {
        PridePreparedHistoryFree(candidate);candidate=NULL;
    }
    PreparationCache *cache=candidate?preparation_stage(data+native_size+history_size,cache_size,saved_field):NULL;
    if(!candidate || !cache)ok=0;
    char temporary[4096]={0};if(ok)ok=temp_path(temporary,sizeof temporary,path,".native.part");
    if(ok) {
        ok=write_file(temporary,data,native_size);
        if(ok) {
            ok=__real_tlk_state_load(temporary,field);
            if(!ok) { const char *native=tlk_state_error();if(native && *native)pride_state_set_error(native); }
        }
    }
    if(temporary[0])remove(temporary);free(data);
    if(ok) { PridePreparedHistoryCommit(candidate);preparation_pending=cache; }
    else { PridePreparedHistoryFree(candidate);preparation_free(cache); }return ok;
}

/* Only a real pristine power-on save gets this record. Owned saves retain the
 * existing strict context/history/cache format and validation. */
enum { RESTART_BOOT_HEADER=128 };
int PrideRestartRendererReady(void);
void PrideRestartRendererReset(const char *);
static int PrideRestartSave(const char *path,uint32_t field) {
    if(field || snes_frame_counter || owner_scene.started || owner_installed)
        return PrideStateSave(path,field);
    char inner_path[4096],temporary[4096];
    if(!path || !temp_path(inner_path,sizeof inner_path,path,".boot-guest.part") ||
       !temp_path(temporary,sizeof temporary,path,".boot.part"))return 0;
    if(!__real_tlk_state_save(inner_path,0))return 0;
    size_t native_size=0;uint8_t *native=read_file(inner_path,&native_size);remove(inner_path);
    if(!native || native_size>64*1024*1024-RESTART_BOOT_HEADER) { free(native);return 0; }
    size_t size=RESTART_BOOT_HEADER+native_size;uint8_t *record=calloc(1,size);
    if(!record) { free(native);return 0; }
    memcpy(record,"PRHBOOT1",8);TlkPut32(record+8,1);TlkPut32(record+12,RESTART_BOOT_HEADER);
    TlkPut32(record+16,(uint32_t)native_size);memcpy(record+24,build_digest,32);
    memcpy(record+RESTART_BOOT_HEADER,native,native_size);free(native);
    sha256_compute(record,size,record+56);
    int ok=write_file(temporary,record,size);free(record);
    if(ok) {
#ifdef _WIN32
        ok=MoveFileExA(temporary,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
        ok=rename(temporary,path)==0;
#endif
    }
    if(!ok)remove(temporary);return ok;
}
static int PrideRestartLoad(const char *path,uint32_t *field) {
    size_t size=0;uint8_t *record=read_file(path,&size);
    if(!record || size<8 || memcmp(record,"PRHBOOT1",8)) {
        free(record);return PrideStateLoad(path,field);
    }
    uint32_t attempted=(uint32_t)snes_frame_counter;
    pride_state_set_error("Power-on save is incompatible or damaged");
    int ok=size>RESTART_BOOT_HEADER+36 && TlkGet32(record+8)==1 &&
        TlkGet32(record+12)==RESTART_BOOT_HEADER && TlkGet32(record+16)==size-RESTART_BOOT_HEADER &&
        !TlkGet32(record+20) && !memcmp(record+24,build_digest,32) && PrideRestartRendererReady();
    uint8_t expected[32],actual[32];
    if(ok) {
        memcpy(expected,record+56,32);memset(record+56,0,32);sha256_compute(record,size,actual);
        ok=!memcmp(expected,actual,32);
        for(unsigned n=88;ok && n<RESTART_BOOT_HEADER;n++)ok=!record[n];
        const uint8_t *inner=record+RESTART_BOOT_HEADER;
        ok=ok && !memcmp(inner,"TLKSTAT1",8) && TlkGet32(inner+8)==4 && !TlkGet32(inner+12);
    }
    /* Allocate every replacement before native guest publication. The actual
     * cold run must recapture its own decoder ABI and audio-bank state. */
    TlkNativeBank *fresh_bank=ok && installed?TlkNativeBankCreate():NULL;
    if(ok && installed && !fresh_bank)ok=0;
    uint8_t *before[7]={0};
    if(ok && scene_installed)for(unsigned n=0;n<7;n++) {
        before[n]=malloc(0x20000);if(!before[n])ok=0;
    }
    char folder[4096]={0},temporary[4096]={0};
    if(ok) {
        int n=snprintf(folder,sizeof folder,"%s/restart-%u",TlkPrideSetting("TLK_SCENE_OWNER_PROBE"),restart_serial+1);
        ok=n>0 && (size_t)n<sizeof folder && restart_serial!=0xffffffffu;
#ifdef _WIN32
        if(ok) {
            int made=TlkPrideMakeDirectory(folder);
            DWORD attributes=GetFileAttributesA(folder);
            ok=made==0 || (errno==EEXIST && attributes!=INVALID_FILE_ATTRIBUTES && (attributes&FILE_ATTRIBUTE_DIRECTORY));
        }
#else
        if(ok)ok=mkdir(folder,0755)==0 || errno==EEXIST;
#endif
    }
    if(ok)ok=temp_path(temporary,sizeof temporary,path,".boot-load.part");
    if(ok) {
        ok=write_file(temporary,record+RESTART_BOOT_HEADER,size-RESTART_BOOT_HEADER);
        uint32_t loaded=0;
        if(ok)ok=__real_tlk_state_load(temporary,&loaded);
        if(!ok) { const char *error=tlk_state_error();if(error && *error)pride_state_set_error(error); }
    }
    if(temporary[0])remove(temporary);free(record);
    if(!ok) {
        TlkNativeBankFree(fresh_bank);for(unsigned n=0;n<7;n++)free(before[n]);
        pride_error_ui_log(attempted,0,0);return 0;
    }
    /* Successful cold restore discards all former death-local/pending state.
     * Hook registration and immutable ROM programs/payloads stay installed. */
    unsigned enabled=owner_enabled,restore=restore_enabled,canonical=restore_canonical,roar_zero=restore_roar_zero;
    /* This cursor is derived once from the immutable original idle program,
     * rather than captured from a particular death or native task. */
    unsigned canonical_cursor=restore_idle_cursor;
#define RESTART_CLEAR(name,limit) name=0;
    PRIDE_STATE_FIELDS(RESTART_CLEAR)
#undef RESTART_CLEAR
    owner_enabled=enabled;restore_enabled=restore;restore_canonical=canonical;restore_roar_zero=roar_zero;
    restore_idle_cursor=canonical_cursor;
    memset(&owner_scene,0,sizeof owner_scene);
    candidate_dumped=record_loaded=0;
    preparation_free(preparation_pending);preparation_pending=NULL;
    if(installed) { TlkNativeBankFree(prepared);prepared=fresh_bank; }
    if(scene_installed)for(unsigned n=0;n<7;n++) {
        SceneTemplate *t=&scene_templates[n];free(t->before);
        unsigned source=t->source,destination=t->destination,expected=t->expected;
        uint8_t *payload=t->payload;memset(t,0,sizeof *t);
        t->source=source;t->destination=destination;t->expected=expected;t->payload=payload;t->before=before[n];
    }
    restart_serial++;snprintf(restart_debug_folder,sizeof restart_debug_folder,"%s",folder);
    snprintf(repeat_debug_folder,sizeof repeat_debug_folder,"%s",folder);
    probe_dir=repeat_debug_folder;scene_folder=repeat_debug_folder;
    PrideRestartRendererReset(folder);
    pride_state_error[0]=0;pride_error_ui_log(attempted,0,1);
    if(field)*field=0;return 1;
}

/* Ordinary completed Pride play has no owned scene/history to serialize, but
 * a later revival still requires the actual cold decoder ABI and native bank.
 * Do not manufacture an age-zero scene for these saves. */
enum { PRACTICE_HEADER=256,PRACTICE_FIELDS=9 };
static int practice_context_ready(void) {
    const TlkPrideSaveContext context={
        .owner_installed=!!owner_installed, .restore_installed=!!restore_installed,
        .have_return=!!have_return, .owner_started=!!owner_scene.started,
        .preparation_pending=!!preparation_pending, .owner_waiting=!!owner_waiting,
        .grounded_waiting=!!grounded_waiting, .scene_active=!!scene_active, .active=!!active,
        .level=ow(0x1ff9e), .descriptor=ol(0xdf), .cub_age=ow(0x2000),
        .health=ow(0x2004), .word_1ff90=ow(0x1ff90), .phase=ow(8)
    };
    return TlkPrideIdleSaveEligible(&context);
}
static int practice_publish(const char *path,const uint8_t *record,size_t size) {
    char temporary[4096];if(!temp_path(temporary,sizeof temporary,path,".practice.part"))return 0;
    int ok=write_file(temporary,record,size);
    if(ok) {
#ifdef _WIN32
        ok=MoveFileExA(temporary,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
        ok=rename(temporary,path)==0;
#endif
    }
    if(!ok)remove(temporary);return ok;
}
static int PridePrivateSave(const char *path,uint32_t field) {
    {
        char journal_path[4096];snprintf(journal_path,sizeof journal_path,"%s/practice-saves.csv",TlkPrideSetting("TLK_SCENE_OWNER_PROBE"));
        FILE *journal=TlkPrideFileOpen(journal_path,"a+");if(!journal)exit(95);
        fseek(journal,0,SEEK_END);if(!ftell(journal))fprintf(journal,"host_field,native_field,ordinary,bank_ready,recipes_ready,scene_active,owner_started,state\n");
        unsigned recipes=0;for(unsigned n=0;n<7;n++)recipes+=scene_templates[n].ready!=0;
        fprintf(journal,"%u,%u,%u,%u,%u,%u,%u,%u\n",field,(unsigned)snes_frame_counter,(unsigned)practice_context_ready(),
            (unsigned)TlkNativeBankReady(prepared,program),recipes,scene_active,(unsigned)owner_scene.started,ow(8));fclose(journal);
    }
    int idle_ready=practice_context_ready();
#ifdef TLK_PRIDE_EXTRA_IDLE_SAVE_READY
    /* A separate scene owner may serialize a complete idle preparation cache.
     * Its caller supplies the additional scene/lifetime eligibility contract. */
    if(!idle_ready)idle_ready=TLK_PRIDE_EXTRA_IDLE_SAVE_READY();
#endif
    if(!idle_ready)return PrideRestartSave(path,field);
    if(!path || field!=(uint32_t)snes_frame_counter || !PrideRestartRendererReady())return 0;
    uint8_t *cache=NULL;size_t cache_size=0;
    if(!preparation_save(field,&cache,&cache_size))return 0;
    char native_path[4096];
    if(!temp_path(native_path,sizeof native_path,path,".practice-guest.part")) { free(cache);return 0; }
    int ok=__real_tlk_state_save(native_path,field);size_t native_size=0;
    uint8_t *native=ok?read_file(native_path,&native_size):NULL;remove(native_path);
    size_t size=PRACTICE_HEADER+native_size+cache_size;
    uint8_t *record=native && size<=64*1024*1024?calloc(1,size):NULL;
    if(!record) { free(native);free(cache);return 0; }
    memcpy(record,"PRPRAC01",8);TlkPut32(record+8,1);TlkPut32(record+12,PRACTICE_HEADER);
    TlkPut32(record+16,(uint32_t)native_size);TlkPut32(record+20,field);
    memcpy(record+24,build_digest,32);TlkPut32(record+88,(uint32_t)cache_size);
    TlkPut32(record+92,owner_enabled | restore_enabled<<1 | restore_canonical<<2 |
        restore_roar_zero<<3 | apply_bank<<4 | scene_apply_templates<<5);
    uint32_t values[]={have_return,return_a,return_x,return_y,restore_roar_font_valid,
        restore_roar_font_maximum,restore_roar_font_current,restore_roar_font_initial,
        (unsigned)TlkResourcesUseMd("gameplay.levels.pride_lands.start")};
    for(unsigned n=0;n<PRACTICE_FIELDS;n++)TlkPut32(record+96+n*4,values[n]);
    memcpy(record+PRACTICE_HEADER,native,native_size);free(native);
    memcpy(record+PRACTICE_HEADER+native_size,cache,cache_size);free(cache);
    sha256_compute(record,size,record+56);ok=practice_publish(path,record,size);free(record);return ok;
}
static int PridePracticeLoadInner(const char *path,uint32_t *field) {
    size_t size=0;uint8_t *record=read_file(path,&size);
    if(!record || size<8 || memcmp(record,"PRPRAC01",8)) {
        free(record);return PrideRestartLoad(path,field);
    }
    uint32_t attempted=(uint32_t)snes_frame_counter,saved=0;
    pride_state_set_error("Ordinary-play save is incompatible or damaged");
    int ok=size>PRACTICE_HEADER+36 && TlkGet32(record+8)==1 && TlkGet32(record+12)==PRACTICE_HEADER &&
        !memcmp(record+24,build_digest,32) && TlkGet32(record+92)<=63 && PrideRestartRendererReady();
    if(ok) {
        static const char *policies[]={"TLK_SCENE_OWNER_ENABLE","TLK_SCENE_RESTORE_ENABLE","TLK_SCENE_RESTORE_CANONICAL",
            "TLK_SCENE_RESTORE_ROAR_ZERO","TLK_NATIVE_BANK_APPLY","TLK_SCENE_PREPARE_APPLY"};
        unsigned flags=TlkGet32(record+92);
        for(unsigned n=0;n<6;n++)if(!policy(policies[n],flags>>n&1))ok=0;
    }
    uint32_t native_size=0,cache_size=0,values[PRACTICE_FIELDS]={0};uint8_t expected[32],actual[32];
    if(ok) {
        native_size=TlkGet32(record+16);cache_size=TlkGet32(record+88);saved=TlkGet32(record+20);
        memcpy(expected,record+56,32);memset(record+56,0,32);sha256_compute(record,size,actual);
        ok=!memcmp(expected,actual,32) && saved && native_size>=36 && cache_size>=96 &&
            (uint64_t)PRACTICE_HEADER+native_size+cache_size==size;
        for(unsigned n=96+PRACTICE_FIELDS*4;ok && n<PRACTICE_HEADER;n++)ok=!record[n];
        for(unsigned n=0;n<PRACTICE_FIELDS;n++)values[n]=TlkGet32(record+96+n*4);
        const uint32_t limits[]={1,65535,65535,65535,1,64,64,65535,1};
        for(unsigned n=0;ok && n<PRACTICE_FIELDS;n++)ok=values[n]<=limits[n];
        if(values[8]!=(unsigned)TlkResourcesUseMd("gameplay.levels.pride_lands.start")) {
            pride_state_set_error("Match the saved gameplay choices and retry");ok=0;
        }
        if(values[0]!=1 || (values[4] && (values[5]<8 || values[6]>values[5])))ok=0;
        const uint8_t *native=record+PRACTICE_HEADER;
        ok=ok && !memcmp(native,"TLKSTAT1",8) && TlkGet32(native+8)==4 && TlkGet32(native+12)==saved;
    }
    TlkDeathProgram candidate_program;if(ok)ok=read_program(&candidate_program);
    PreparationCache *cache=ok?preparation_stage(record+PRACTICE_HEADER+native_size,cache_size,saved):NULL;
    if(!cache)ok=0;
    char folder[4096]={0},temporary[4096]={0};
    if(ok) {
        int n=snprintf(folder,sizeof folder,"%s/restart-%u",TlkPrideSetting("TLK_SCENE_OWNER_PROBE"),restart_serial+1);
        ok=n>0 && (size_t)n<sizeof folder && restart_serial!=0xffffffffu;
#ifdef _WIN32
        if(ok) {
            int made=TlkPrideMakeDirectory(folder);DWORD attributes=GetFileAttributesA(folder);
            ok=made==0 || (errno==EEXIST && attributes!=INVALID_FILE_ATTRIBUTES && (attributes&FILE_ATTRIBUTE_DIRECTORY));
        }
#else
        if(ok)ok=mkdir(folder,0755)==0 || errno==EEXIST;
#endif
    }
    if(ok)ok=temp_path(temporary,sizeof temporary,path,".practice-load.part");
    if(ok) {
        ok=write_file(temporary,record+PRACTICE_HEADER,native_size);
        uint32_t loaded=0;if(ok)ok=__real_tlk_state_load(temporary,&loaded);
        if(!ok) { const char *error=tlk_state_error();if(error && *error)pride_state_set_error(error); }
    }
    if(temporary[0])remove(temporary);free(record);
    if(!ok) { preparation_free(cache);pride_error_ui_log(attempted,0,0);return 0; }
    unsigned enabled=owner_enabled,restore=restore_enabled,canonical=restore_canonical,roar_zero=restore_roar_zero;
    unsigned cursor=restore_idle_cursor;
#define PRACTICE_CLEAR(name,limit) name=0;
    PRIDE_STATE_FIELDS(PRACTICE_CLEAR)
#undef PRACTICE_CLEAR
    owner_enabled=enabled;restore_enabled=restore;restore_canonical=canonical;
    restore_roar_zero=roar_zero;restore_idle_cursor=cursor;
    memset(&owner_scene,0,sizeof owner_scene);owner_program=candidate_program;
    have_return=values[0];return_a=values[1];return_x=values[2];return_y=values[3];
    restore_roar_font_valid=values[4];restore_roar_font_maximum=values[5];
    restore_roar_font_current=values[6];restore_roar_font_initial=(uint16_t)values[7];
    candidate_dumped=1;record_loaded=0;
    preparation_free(preparation_pending);preparation_pending=cache;
    restart_serial++;snprintf(restart_debug_folder,sizeof restart_debug_folder,"%s",folder);
    snprintf(repeat_debug_folder,sizeof repeat_debug_folder,"%s",folder);
    probe_dir=repeat_debug_folder;scene_folder=repeat_debug_folder;
    PrideRestartRendererReset(folder);
    pride_state_error[0]=0;pride_error_ui_log(attempted,saved,1);
    if(field)*field=saved;return 1;
}
static int PridePrivateLoad(const char *path,uint32_t *field) {
    practice_frame_begin();
    uint32_t loaded=0;int ok=PridePracticeLoadInner(path,&loaded);
    if(!ok)return 0;
#ifdef TLK_NATIVE_BANK_SDL
    /* The private controller/history records use the restored guest timeline.
     * Ordinary interactive input has no tape, so the frontend's tape-only
     * frame assignment otherwise leaves these clocks different after a load. */
    frame=(long)loaded;
#endif
    if(field)*field=loaded;return 1;
}

#ifdef TLK_NATIVE_BANK_SDL
static char practice_pending_path[4096];
static uint32_t practice_pending_field;
static uint8_t practice_pending_profile[32];
static int practice_profile(uint8_t hash[32]) {
    uint32_t choices[1024];int count=TlkResourcesCount();if(count<0 || count>1024)return 0;
    int used=0;
    for(int n=0;n<count;n++) {
        /* Optional presentation enhancements do not bind the gameplay save.
         * Excluding the newly appended IDs also retains existing choice hashes. */
        const char *resource_id=TlkResourcesNode(n)->id;
        if(!strncmp(resource_id,"graphics.scenery.snes_motion",28) || !strcmp(resource_id,"graphics.scenery.firelight"))continue;
#ifdef TLK_PRIDE_EXTRA_PROFILE_RESOURCE
        /* This owner's outer record binds its mode and presentation. */
        if(!strcmp(TlkResourcesNode(n)->id,TLK_PRIDE_EXTRA_PROFILE_RESOURCE))continue;
#endif
        choices[used++]=(uint32_t)TlkResourcesResolved(n,0);
    }
    sha256_compute((const uint8_t *)choices,(size_t)used*sizeof *choices,hash);return 1;
}
#endif
static void practice_frame_begin(void) {
#ifdef TLK_NATIVE_BANK_SDL
    if(!practice_pending_path[0])return;
    char path[sizeof practice_pending_path];snprintf(path,sizeof path,"%s",practice_pending_path);
    practice_pending_path[0]=0;
    uint8_t profile[32];
    /* This boundary precedes all next-field guest instructions. Previous-field
     * audio has completed even when the frontend skipped presenting it. If a
     * paused resource commit changed the profile, do not mislabel old state. */
    int ok=(uint32_t)snes_frame_counter==practice_pending_field && practice_profile(profile) &&
        !memcmp(profile,practice_pending_profile,32) && PridePracticeSave(path,practice_pending_field);
    if(!ok)Toast("Practice restart save could not be written");
#endif
}
static void practice_frame_complete(void) {
#ifdef TLK_NATIVE_BANK_SDL
    if(!s_practice || !pr.loading || !practice_context_ready() || !TlkNativeBankReady(prepared,program))return;
    for(unsigned n=0;n<7;n++)if(!scene_templates[n].ready || scene_templates[n].capturing)return;
    /* Ordinary play uses state4; debug level selection reaches state6. The
     * verified gameplay descriptor and completed cold captures exclude intros
     * and intermediate loading that also use these values. */
    pr.loading=0;pr.st=PR_ARMED;pr.level=ow(0x1ff9e);pr.eligible=pr.fresh;
    if(pr.fresh && practice_profile(practice_pending_profile)) {
        PrRestartPath(practice_pending_path,sizeof practice_pending_path);
        practice_pending_field=(uint32_t)snes_frame_counter;
    }
    pr.fresh=0;
#endif
}

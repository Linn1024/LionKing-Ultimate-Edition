/* Extended checkpoint lifecycle context. Earlier preparation caches are staged
 * by pride_preparation_state_probe.c before original native publication. */
#include "tlk_savestate.h"
static int PrideStateSave(const char *,uint32_t);
static int PrideStateLoad(const char *,uint32_t *);
static int PrideRestartSave(const char *,uint32_t);
static int PridePracticeSave(const char *,uint32_t);
static int PridePracticeLoad(const char *,uint32_t *);
static int PrideRestartLoad(const char *,uint32_t *);
static char pride_state_error[192];
static const char *PrideStateError(void);
#define tlk_state_error PrideStateError
#define tlk_state_save PridePracticeSave
#define tlk_state_load PridePracticeLoad
#include "pride_repeat_restore.c"
#undef tlk_state_save
#undef tlk_state_load
#undef tlk_state_error
#include "tlk_state_bytes.h"
#ifdef _WIN32
#undef FORCEINLINE
#include <windows.h>
#endif
static const char *PrideStateError(void) {
    if(pride_state_error[0])return pride_state_error;
    const char *native=tlk_state_error();
    return native && *native?native:"Save is incompatible or damaged";
}
static void pride_state_set_error(const char *message) {
    snprintf(pride_state_error,sizeof pride_state_error,"%s",message);
}
static void pride_error_ui_log(uint32_t attempted,uint32_t loaded,unsigned success) {
    const char *folder=TlkPrideSetting("TLK_SCENE_OWNER_PROBE");if(!folder)return;
    char path[4096];snprintf(path,sizeof path,"%s/live-load.csv",folder);
    FILE *f=TlkPrideFileOpen(path,"a+");if(!f)return;
    fseek(f,0,SEEK_END);if(!ftell(f))fprintf(f,"attempt_field,loaded_field,success\n");
    fprintf(f,"%u,%u,%u\n",attempted,loaded,success);fclose(f);
}

/* Explicit little-endian scalars. No pointers, FILEs, compiler struct layout,
 * opcode-hook registrations or suspended C/fiber frames enter the record. */
#define spawn_native_x spawn_native[0]
#define spawn_native_y spawn_native[1]
#define spawn_selected_x spawn_selected[0]
#define spawn_selected_y spawn_selected[1]
#define PRIDE_STATE_FIELDS(X) \
 X(owner_enabled,1) X(owner_loop,1) X(owner_skip,1) X(owner_hold_count,64) \
 X(owner_ended,1) X(owner_initial_hold,1) X(owner_waiting,1) \
 X(owner_normal_release,1) X(owner_first_hold_pose,1) X(owner_entry_field,0xffffffffu) \
 X(owner_wait_sp,65535) X(owner_wait_a,65535) X(owner_wait_x,65535) X(owner_wait_y,65535) \
 X(owner_wait_d,65535) X(owner_wait_p,255) X(owner_wait_db,255) \
 X(restore_enabled,1) X(restore_canonical,1) X(restore_roar_zero,1) \
 X(restore_pending,3) X(restore_committed,1) X(restore_canonical_calls,0xffffffffu) \
 X(restore_idle_cursor,0xffffff) X(restore_health,255) X(restore_roar,65535) \
 X(restore_roar_font_valid,1) X(restore_roar_font_maximum,64) \
 X(restore_roar_font_current,64) X(restore_roar_font_initial,65535) \
 X(applied,1) X(active,1) X(have_return,1) X(return_a,65535) X(return_x,65535) X(return_y,65535) \
 X(scene_calls,0xffffffffu) X(scene_number,0xffffffffu) X(scene_source,0xffffff) \
 X(scene_dest,0xffffff) X(scene_return,0xffffff) X(scene_death,1) X(scene_started,1) \
 X(scene_active,1) X(scene_template_applies,7) \
 X(owner_normal_latch_serial,0xffffffffu) \
 X(owner_default_initialized,1) X(owner_default_prepared,1) \
 X(owner_default_advancing,1) X(owner_default_advanced,1) X(owner_default_advance_wait,1) \
 X(owner_default_callback,0xffffff) X(grounded_done,1) X(grounded_waiting,1) \
 X(spawn_native_x,65535) X(spawn_native_y,65535) \
 X(spawn_selected_x,65535) X(spawn_selected_y,65535) X(spawn_md,1) X(spawn_checkpoint,1)
#define STATE_ENUM(name,limit) STATE_##name,
enum { PRIDE_STATE_FIELDS(STATE_ENUM) STATE_COUNT, STATE_BYTES=768, STATE_SCENE=96, STATE_WORDS=224 };
#undef STATE_ENUM
_Static_assert(STATE_WORDS+STATE_COUNT*4<=STATE_BYTES,"private context record overflow");
static const TlkDeathScene *handoff_load_scene;
static const uint32_t *handoff_load_values;

static int policy(const char *key,unsigned expected) {
    const char *s=TlkPrideSetting(key);return s && ((!strcmp(s,"1") && expected==1) || (!strcmp(s,"0") && !expected));
}
static int context_valid(const TlkDeathScene *s,const uint32_t *v,uint32_t field) {
#define STATE_CHECK(name,limit) if(v[STATE_##name]>(limit))return 0;
    PRIDE_STATE_FIELDS(STATE_CHECK)
#undef STATE_CHECK
    unsigned ready=s->has_checkpoint?345:300,health=s->has_checkpoint?270:274;
    /* The controller stops at READY; the presenter can remain owned briefly
     * while actual normal OAM/widgets settle. Retain the real completed field. */
    if(!s->started || s->final_life || s->age>ready || s->last_field>field ||
       (uint64_t)v[STATE_owner_entry_field]+s->age!=s->last_field ||
       (field!=s->last_field && (!v[STATE_owner_ended] || s->age!=ready)) ||
       !v[STATE_owner_enabled] || !v[STATE_restore_enabled] ||
       (s->age>=65 && !v[STATE_owner_loop]) ||
       (s->age>=225 && (!v[STATE_owner_skip] || v[STATE_restore_pending]!=3)) ||
       (s->age>=health && !v[STATE_restore_committed]) ||
       (s->age>=239 && !v[STATE_applied]))return 0;
    if(v[STATE_grounded_waiting] || v[STATE_spawn_checkpoint]!=(unsigned)s->has_checkpoint ||
       v[STATE_spawn_md]!=(unsigned)TlkResourcesUseMd("gameplay.levels.pride_lands.start"))return 0;
    for(unsigned axis=0;axis<2;axis++) {
        unsigned native,external;
        if(!TlkStartDataValue(axis,&native,&external) ||
           v[axis?STATE_spawn_native_y:STATE_spawn_native_x]!=native ||
           v[axis?STATE_spawn_selected_y:STATE_spawn_selected_x]!=(v[STATE_spawn_md]?external:native))return 0;
    }
    if(!s->has_checkpoint && ((s->age>=269 && (!v[STATE_owner_default_prepared] ||
       !v[STATE_grounded_done])) || (s->age>=274 && !v[STATE_owner_default_advanced])))return 0;
    if(v[STATE_owner_ended] && (!v[STATE_owner_normal_release] || s->age!=ready))return 0;
    if(!v[STATE_owner_ended] && v[STATE_owner_normal_latch_serial])return 0;
    if(v[STATE_owner_waiting] && (v[STATE_owner_wait_sp]<0x204 || v[STATE_owner_wait_sp]>0x2ff ||
       v[STATE_owner_wait_d] || v[STATE_owner_wait_db]))return 0;
    if(v[STATE_restore_roar_font_valid] && (v[STATE_restore_roar_font_maximum]<8 ||
       v[STATE_restore_roar_font_current]>v[STATE_restore_roar_font_maximum]))return 0;
    return policy("TLK_NATIVE_BANK_APPLY",1) && policy("TLK_SCENE_PREPARE_APPLY",1) &&
        policy("TLK_SCENE_OWNER_ENABLE",v[STATE_owner_enabled]) &&
        policy("TLK_SCENE_RESTORE_ENABLE",v[STATE_restore_enabled]) &&
        policy("TLK_SCENE_RESTORE_CANONICAL",v[STATE_restore_canonical]) &&
        policy("TLK_SCENE_RESTORE_ROAR_ZERO",v[STATE_restore_roar_zero]);
}
static uint8_t *read_file(const char *path,size_t *size) {
    FILE *f=TlkPrideFileOpen(path,"rb");if(!f)return NULL;
    if(fseek(f,0,SEEK_END)) { fclose(f);return NULL; }
    long n=ftell(f);rewind(f);
    if(n<=0 || n>64*1024*1024) { fclose(f);return NULL; }
    uint8_t *data=malloc((size_t)n);
    int ok=data && fread(data,1,(size_t)n,f)==(size_t)n;fclose(f);
    if(!ok) { free(data);return NULL; }*size=(size_t)n;return data;
}
static int write_file(const char *path,const uint8_t *data,size_t size) {
    FILE *f=TlkPrideFileOpen(path,"wb");if(!f)return 0;
    int ok=fwrite(data,1,size,f)==size;if(fclose(f))ok=0;return ok;
}
static int temp_path(char *out,size_t capacity,const char *path,const char *suffix) {
    return TlkTemporaryPath(out,capacity,path,suffix);
}
static int PrideStateSave(const char *path,uint32_t field) {
    uint32_t values[STATE_COUNT];
#define STATE_CAPTURE(name,limit) values[STATE_##name]=(uint32_t)name;
    PRIDE_STATE_FIELDS(STATE_CAPTURE)
#undef STATE_CAPTURE
    if(!path || !context_valid(&owner_scene,values,field))return 0;
    uint8_t header[STATE_BYTES]={0};memcpy(header,"PRHSAVE1",8);
    TlkPut32(header+8,1);TlkPut32(header+12,STATE_BYTES);TlkPut32(header+20,field);
    memcpy(header+24,build_digest,32);
    if(!TlkDeathSceneSave(&owner_scene,&owner_program,header+STATE_SCENE,TLK_DEATH_SCENE_RECORD_SIZE))return 0;
    for(unsigned i=0;i<STATE_COUNT;i++)TlkPut32(header+STATE_WORDS+i*4,values[i]);
    char inner_path[4096],temporary[4096];
    if(!temp_path(inner_path,sizeof inner_path,path,".guest.part") || !temp_path(temporary,sizeof temporary,path,".part"))return 0;
    if(!tlk_state_save(inner_path,field))return 0;
    size_t inner_size=0;uint8_t *inner=read_file(inner_path,&inner_size);remove(inner_path);
    if(!inner)return 0;
    size_t size=STATE_BYTES+inner_size;uint8_t *record=malloc(size);
    if(!record) { free(inner);return 0; }
    TlkPut32(header+16,(uint32_t)inner_size);memcpy(record,header,STATE_BYTES);
    memcpy(record+STATE_BYTES,inner,inner_size);free(inner);
    uint8_t hash[32];sha256_compute(record,size,hash);memcpy(record+56,hash,32);
    int ok=write_file(temporary,record,size);free(record);
    if(ok) {
#ifdef _WIN32
        ok=MoveFileExA(temporary,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
        ok=rename(temporary,path)==0;
#endif
    }
    if(!ok)remove(temporary);
    return ok;
}
static int read_program(TlkDeathProgram *out) {
    const char *path=TlkPrideSetting("TLK_SCENE_OWNER_MD_ROM");if(!path)return 0;
    size_t size=0;uint8_t *md=read_file(path,&size);if(!md)return 0;
    int ok=TlkDeathProgramInit(out,g_rom,0x300000,md,size);free(md);return ok;
}
#include "pride_legacy_save_guard.inc"
static int PrideStateLoad(const char *path,uint32_t *field) {
    uint32_t attempt_field=(uint32_t)snes_frame_counter;
    pride_state_set_error("Save is incompatible or damaged");
    size_t size=0;uint8_t *record=read_file(path,&size);
    if(!record) { pride_state_set_error("Save could not be read");pride_error_ui_log(attempt_field,0,0);return 0; }
    if(PrideLegacyNativeSave(record,size)) { free(record);pride_error_ui_log(attempt_field,0,0);return 0; }
    int ok=size>STATE_BYTES && !memcmp(record,"PRHSAVE1",8) && TlkGet32(record+8)==1 &&
        TlkGet32(record+12)==STATE_BYTES && TlkGet32(record+16)==size-STATE_BYTES &&
        !memcmp(record+24,build_digest,32);
    uint8_t expected[32],actual[32];
    if(ok) {
        memcpy(expected,record+56,32);memset(record+56,0,32);
        sha256_compute(record,size,actual);ok=!memcmp(expected,actual,32);
        for(unsigned i=88;ok && i<STATE_SCENE;i++)ok=record[i]==0;
        for(unsigned i=STATE_WORDS+STATE_COUNT*4;ok && i<STATE_BYTES;i++)ok=record[i]==0;
    }
    TlkDeathProgram candidate_program;TlkDeathScene candidate_scene;uint32_t values[STATE_COUNT],saved_field=0;
    if(ok) {
        for(unsigned i=0;i<STATE_COUNT;i++)values[i]=TlkGet32(record+STATE_WORDS+i*4);
        if(values[STATE_spawn_md]!=(unsigned)TlkResourcesUseMd("gameplay.levels.pride_lands.start"))
            pride_state_set_error("Match the saved gameplay choices and retry");
        saved_field=TlkGet32(record+20);
        ok=read_program(&candidate_program) && TlkDeathSceneLoad(&candidate_scene,&candidate_program,
            record+STATE_SCENE,TLK_DEATH_SCENE_RECORD_SIZE) && context_valid(&candidate_scene,values,saved_field);
        const uint8_t *inner=record+STATE_BYTES;
        ok=ok && size-STATE_BYTES>=36 && !memcmp(inner,"TLKSTAT1",8) && TlkGet32(inner+12)==saved_field;
    }
    char inner_path[4096];
    if(ok)ok=temp_path(inner_path,sizeof inner_path,path,".load.part");
    if(ok) {
        ok=write_file(inner_path,record+STATE_BYTES,size-STATE_BYTES);
        if(ok) {
            uint32_t loaded=0;handoff_load_scene=&candidate_scene;handoff_load_values=values;
            ok=tlk_state_load(inner_path,&loaded);handoff_load_scene=NULL;handoff_load_values=NULL;
        }
        remove(inner_path);
    }
    free(record);if(!ok) { fprintf(stderr,"private scene state preflight/load rejected\n");pride_error_ui_log(attempt_field,0,0);return 0; }
    /* No fallible work follows guest publication. Initialization will register
     * callbacks/open telemetry normally on the first new-process frame. */
    owner_program=candidate_program;owner_scene=candidate_scene;
#define STATE_COMMIT(name,limit) name=values[STATE_##name];
    PRIDE_STATE_FIELDS(STATE_COMMIT)
#undef STATE_COMMIT
    pride_state_error[0]=0;
    pride_error_ui_log(attempt_field,saved_field,1);
    if(field)*field=saved_field;return 1;
}

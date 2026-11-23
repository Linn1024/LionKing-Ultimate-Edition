/* Private integration of the maintained final-scene record with native saves.
 * Native state, presentation record and bank are validated before guest load. */
#include "tlk_final_scene_state.h"
#include "tlk_final_scene_lifecycle.h"
static int ContinueLifecycleEnabled(void) {
    const char *s=ContinueModeSetting("TLK_CONTINUE_TRANSITION");return (s && !strcmp(s,"1")) || ContinueTitleNavigationSelected();
}
static int ContinueIdleBackendReady(void) {
    /* No nonfinal episode is being borrowed here. The final owner serializes
     * its own timeline/canvas, while the ordinary backend retains the complete
     * preexisting decoder/bank cache for a future nonfinal death. */
    return ContinueLifecycleEnabled() && final_scene_entry && final_scene_mode &&
        owner_installed && restore_installed && have_return && !owner_scene.started &&
        !preparation_pending && !owner_waiting && !grounded_waiting && !scene_active && !active &&
        !FinalWord(0x1ff9e) && !FinalWord(0x2000) && !FinalWord(0x2004) &&
        (FinalAddress(0xdf)==0xc00387 || FinalAddress(0xdf)==0xc0080d || FinalAddress(0xdf)==0xc0057b);
}
static int ContinueBackendField(const uint8_t *data,size_t size,uint32_t field) {
    if(!data || size<36)return 0;
    if(!memcmp(data,"TLKSTAT1",8))return TlkGet32(data+12)==field;
    if(!memcmp(data,"PRPRAC01",8) || !memcmp(data,"PRHSAVE1",8))
        return TlkGet32(data+20)==field;
    return 0;
}
static void ContinueLocalClear(void) {
    InterlevelClear();
    BonusResultClear();
    NativeMenuClear();
    /* The independently selected title navigator has its own capture/reset
     * lifetime. Retiring this final episode must not discard its first input. */
    final_once=final_fast_applied=final_scene_entry=final_scene_age=0;
    final_scene_have_origin=final_scene_have_target=final_scene_waiting=final_input_reading=0;
    final_scene_a=final_scene_x=final_scene_y=final_scene_s=final_scene_d=0;final_scene_p=final_scene_db=0;
    reload_fast_used=continue_transition_level_ready=continue_transition_input_started=0;
    continue_title_pending=0;
    continue_title_ready_field=continue_title_previous_pad=0;
    continue_menu_field=continue_title_fade_field=0;
    final_menu_confirmed_credits=0;
    memset(&continue_transition,0,sizeof continue_transition);
    memset(final_scene_origin,0,sizeof final_scene_origin);memset(final_scene_target,0,sizeof final_scene_target);
    memset(continue_transition_menu,0,sizeof continue_transition_menu);memset(continue_transition_level,0,sizeof continue_transition_level);
    memset(continue_canvas_sides,0,sizeof continue_canvas_sides);
}
static void ContinueLifecycleEntry(CpuState *cpu,uint32_t pc) {
    (void)cpu;(void)pc;
    if(!final_scene_entry || (FinalAddress(0xdf)!=0xc00387 && FinalAddress(0xdf)!=0xc0080d) ||
       FinalWord(0x1ff9e) || FinalWord(0x2000) || FinalWord(0x2004) || FinalWord(0x1ffaa) ||
       FinalAddress(0xb243)!=0xc35a82)return;
    if(TlkFinalSceneRearmReady(final_scene_entry,reload_fast_used,&continue_transition,
        (unsigned)snes_frame_counter+1))ContinueLocalClear();
}
static void ContinueStateExport(TlkFinalSceneState *s,uint32_t field) {
    TlkFinalSceneStateClear(s);s->field=field;s->entry_field=final_scene_entry;s->age=final_scene_age;
    s->flags=(final_once?TLK_FINAL_ONCE:0)|(final_fast_applied?TLK_FINAL_FAST_ASSETS:0)|
        (final_scene_have_origin?TLK_FINAL_ORIGIN:0)|(final_scene_have_target?TLK_FINAL_TARGET:0)|
        (final_scene_waiting?TLK_FINAL_WAITING:0)|(continue_transition_level_ready?TLK_FINAL_LEVEL:0)|
        (continue_transition_input_started?TLK_FINAL_INPUT_STARTED:0)|
        (continue_title_pending?TLK_FINAL_TITLE_EXIT:0)|
        (continue_menu_field?TLK_FINAL_MENU_CANVAS:0);
    s->reload_used=reload_fast_used;s->continuation=continue_transition;
    s->menu_field=continue_menu_field;s->title_fade_field=continue_title_fade_field;
    s->menu_credits=final_menu_confirmed_credits;
    s->title_ready_field=continue_title_ready_field;s->title_previous_pad=continue_title_previous_pad;
    s->title_navigation=title_navigation;
    if(final_scene_waiting) {
        s->wait_a=final_scene_a;s->wait_x=final_scene_x;s->wait_y=final_scene_y;s->wait_s=final_scene_s;
        s->wait_d=final_scene_d;s->wait_p=final_scene_p;s->wait_db=final_scene_db;s->input_stage=final_input_reading;
    }
    if(s->flags&TLK_FINAL_ORIGIN)memcpy(s->canvas[0],final_scene_origin,sizeof final_scene_origin);
    if(s->flags&TLK_FINAL_TARGET)memcpy(s->canvas[1],final_scene_target,sizeof final_scene_target);
    if(s->continuation.confirmed_field || s->menu_field)memcpy(s->canvas[2],continue_transition_menu,sizeof continue_transition_menu);
    if(s->flags&TLK_FINAL_LEVEL)memcpy(s->canvas[3],continue_transition_level,sizeof continue_transition_level);
}
static void ContinueStateImport(const TlkFinalSceneState *s) {
    final_menu_confirmed_credits=s->menu_credits;
    continue_title_ready_field=s->title_ready_field;continue_title_previous_pad=s->title_previous_pad;
    title_navigation=s->title_navigation;
    title_navigation_source_known=1;title_navigation_last_source=ContinueTitleNavigationSelected();
    final_once=!!(s->flags&TLK_FINAL_ONCE);final_fast_applied=!!(s->flags&TLK_FINAL_FAST_ASSETS);
    final_scene_entry=s->entry_field;final_scene_age=s->age;
    final_scene_have_origin=!!(s->flags&TLK_FINAL_ORIGIN);final_scene_have_target=!!(s->flags&TLK_FINAL_TARGET);
    final_scene_waiting=!!(s->flags&TLK_FINAL_WAITING);final_input_reading=s->input_stage;
    continue_transition_level_ready=!!(s->flags&TLK_FINAL_LEVEL);
    continue_transition_input_started=!!(s->flags&TLK_FINAL_INPUT_STARTED);
    continue_title_pending=!!(s->flags&TLK_FINAL_TITLE_EXIT);
    continue_menu_field=s->menu_field;continue_title_fade_field=s->title_fade_field;
    reload_fast_used=s->reload_used;continue_transition=s->continuation;
    final_scene_a=s->wait_a;final_scene_x=s->wait_x;final_scene_y=s->wait_y;final_scene_s=s->wait_s;
    final_scene_d=s->wait_d;final_scene_p=s->wait_p;final_scene_db=s->wait_db;
    memcpy(final_scene_origin,s->canvas[0],sizeof final_scene_origin);memcpy(final_scene_target,s->canvas[1],sizeof final_scene_target);
    memcpy(continue_transition_menu,s->canvas[2],sizeof continue_transition_menu);memcpy(continue_transition_level,s->canvas[3],sizeof continue_transition_level);
}
static int ContinueStateIdentity(uint8_t out[32]) {
    uint8_t bytes[96]={0};memcpy(bytes,build_digest,32);if(!practice_profile(bytes+32))return 0;
    const char *names[]={"TLK_FINAL_SKIP","TLK_FINAL_LATE_SKIP","TLK_FINAL_FAST_ASSETS","TLK_FINAL_SCENE_PRESENT",
        "TLK_CONTINUE_FAST_RELOAD","TLK_CONTINUE_BANK_APPLY","TLK_CONTINUE_TRANSITION"};
    for(unsigned i=0;i<7;i++) {const char *v=ContinueModeSetting(names[i]);bytes[64+i]=v && !strcmp(v,"1");}
    /* Stampede temporarily renders256 inside a configured320 viewport.
     * Bind the selected viewport, not the currently running scene: a cold
     * load begins in the title and must accept that scene's own narrow record. */
    unsigned viewport=(unsigned)TlkResourcesViewportWidth();
    bytes[71]=final_menu_art_mode?(viewport==256?3:2):0;
    bytes[76]=1; /* Reviewed MD Game Over dismissal/timeout policy. */
    bytes[77]=1; /* Installed real-driver title upload slice. */
    bytes[78]=1; /* Reviewed title readiness and retained outgoing pad history. */
    bytes[79]=1; /* Independently selected title navigation and saved sampling. */
    TlkPut32(bytes+72,viewport);memcpy(bytes+80,"FINAL-SCENE-001",15);
    sha256_compute(bytes,sizeof bytes,out);
    if(final_menu_art_mode) {
        uint8_t bound[64];memcpy(bound,out,32);memcpy(bound+32,final_menu_asset_digest,32);
        sha256_compute(bound,sizeof bound,out);
    }
    /* Combined presentation saves bind the mandatory installed native bytes.
     * Raw native/backend saves retain their existing source identity. */
    uint8_t installed[64];memcpy(installed,out,32);memcpy(installed+32,final_native_asset_digest,32);
    sha256_compute(installed,sizeof installed,out);
    memcpy(installed,out,32);memcpy(installed+32,title_bank_asset_digest,32);
    sha256_compute(installed,sizeof installed,out);
    return 1;
}
static int InterlevelRetiring(void);
static int ContinueLifecycleSave(const char *path,uint32_t field) {
    if(field && TlkBonusResultSceneActive()){
        pride_state_set_error("Finish the bonus result before saving");return 0;
    }
    if(field && (TlkInterlevelSceneActive() || InterlevelRetiring() || TlkCliffSceneActive())){
        pride_state_set_error("Finish the interlevel scene before saving");return 0;
    }
    if(field && NativeMenuOwned()) {
        pride_state_set_error("Finish Continue or Game Over before saving");return 0;
    }
    if(!ContinueLifecycleEnabled() || !field)return PridePracticeSave(path,field);
    ContinueEnsureInstalled();
    /* Final-menu canvases keep their console width; a scrolling-world save
     * must not bind itself to the current OS window dimensions. */
    int width=TlkResourcesViewportWidth();
    if((width!=256 && width!=320) || field!=(unsigned)snes_frame_counter)return 0;
    uint8_t identity[32];TlkFinalSceneState *state=calloc(1,sizeof *state);
    if(!state || !ContinueStateIdentity(identity)) {free(state);return 0;}
    ContinueStateExport(state,field);
    if(!TlkFinalSceneStateValid(state)) {free(state);pride_state_set_error("Final scene state is not save-ready");return 0;}
    char native_path[4096]={0},temporary[4096]={0};uint8_t *native=NULL,*out=NULL;size_t native_size=0;
    size_t bank_size=TlkNativeBankRecordSize(continue_bank);int ok=bank_size<=262144;
    if(ok)ok=temp_path(native_path,sizeof native_path,path,".final-native") && PridePracticeSave(native_path,field);
    if(ok) {native=read_file(native_path,&native_size);ok=ContinueBackendField(native,native_size,field);}
    size_t side_size=width==320?FINAL_SIDE_BYTES:0;
    size_t size=96+native_size+TLK_FINAL_STATE_BYTES+bank_size+side_size;
    if(ok) {ok=size<=64*1024*1024;out=ok?calloc(1,size):NULL;ok=out!=NULL;}
    if(ok) {
        memcpy(out,"TLKFSV01",8);TlkPut32(out+8,4);TlkPut32(out+12,96);TlkPut32(out+16,(uint32_t)size);
        TlkPut32(out+20,(uint32_t)native_size);TlkPut32(out+24,TLK_FINAL_STATE_BYTES);TlkPut32(out+28,(uint32_t)bank_size);
        TlkPut32(out+32,field);memcpy(out+96,native,native_size);
        TlkPut32(out+36,(uint32_t)width);TlkPut32(out+40,(uint32_t)side_size);
        TlkPut32(out+44,TlkPrideHealthDeathSelected()?2:1);
        TlkPut32(out+48,(uint32_t)TlkCameraViewWidth());TlkPut32(out+52,(uint32_t)s_view_height);
        if(side_size) {
            uint8_t *sides=out+size-side_size;
            for(unsigned slot=0;slot<4;slot++)for(unsigned i=0;i<FINAL_SIDE_PIXELS;i++)
                TlkPut32(sides+((size_t)slot*FINAL_SIDE_PIXELS+i)*4,continue_canvas_sides[slot][i]);
        }
        ok=TlkFinalSceneStateSave(state,identity,out+96+native_size,TLK_FINAL_STATE_BYTES);
        if(ok && bank_size)ok=TlkNativeBankSave(continue_bank,continue_bank_program,out+96+native_size+TLK_FINAL_STATE_BYTES,bank_size);
        if(ok)sha256_compute(out,size,out+64);
    }
    if(ok)ok=temp_path(temporary,sizeof temporary,path,".final-part") && write_file(temporary,out,size);
    if(ok)ok=MoveFileExA(temporary,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
    if(native_path[0])remove(native_path);if(temporary[0])remove(temporary);
    free(state);free(native);free(out);return ok;
}
static int ContinueLifecycleLoad(const char *path,uint32_t *field) {
    size_t size=0;uint8_t *data=read_file(path,&size);if(!data)return 0;
    if(size<8 || memcmp(data,"TLKFSV01",8)) {
        free(data);uint32_t loaded=0;int ok=PridePracticeLoad(path,&loaded);
        if(ok) {
            ContinueLocalClear();TlkTitleNavigationClear(&title_navigation);
            title_navigation_source_known=1;title_navigation_last_source=ContinueTitleNavigationSelected();
            if(field)*field=loaded;
        }return ok;
    }
    if(!ContinueLifecycleEnabled()) {free(data);pride_state_set_error("Enable the saved Continue transition");return 0;}
    ContinueEnsureInstalled();uint8_t identity[32],expected[32],actual[32];
    uint32_t version=size>=96?TlkGet32(data+8):0;
    uint32_t backend=TlkPrideHealthDeathSelected()?2u:1u;
    int flexible=version==4;
    int wide=version==3 || (flexible && TlkGet32(data+36)==320);
    int ok=size>=96 && size<=64*1024*1024 && (flexible || wide || version==backend) && TlkGet32(data+12)==96 &&
        TlkGet32(data+16)==size && ContinueStateIdentity(identity);
    /* The record declares its actual canvas width; the stable identity above
     * still rejects a different requested viewport or resource profile. */
    uint32_t native_size=ok?TlkGet32(data+20):0,private_size=ok?TlkGet32(data+24):0,bank_size=ok?TlkGet32(data+28):0;
    uint32_t saved=ok?TlkGet32(data+32):0;
    uint32_t side_size=wide?FINAL_SIDE_BYTES:0;
    if(ok)ok=native_size>=36 && private_size==TLK_FINAL_STATE_BYTES && bank_size<=262144 && saved &&
        (uint64_t)96+native_size+private_size+bank_size+side_size==size;
    if(ok && (wide || flexible))ok=TlkGet32(data+36)==(wide?320:256) && TlkGet32(data+40)==side_size && TlkGet32(data+44)==backend;
    unsigned saved_viewport=flexible?TlkGet32(data+48):0;
    if(ok && flexible)ok=saved_viewport>=256 && saved_viewport<=TLK_WIDE_MAX_WIDTH && !(saved_viewport&1) &&
        TlkGet32(data+52)>=128 && TlkGet32(data+52)<=TLK_WIDE_MAX_VIEW_HEIGHT;
    if(ok)for(unsigned i=flexible?56:wide?48:36;i<64;i++)if(data[i])ok=0;
    if(ok) {memcpy(expected,data+64,32);memset(data+64,0,32);sha256_compute(data,size,actual);ok=!memcmp(expected,actual,32);}
    if(getenv("TLK_SAVE_TRACE"))fprintf(stderr,"save_load envelope=%d version=%u backend=%u canonical=%d saved=%u\n",ok,version,backend,TlkResourcesViewportWidth(),saved);
    TlkFinalSceneState *candidate=ok?calloc(1,sizeof *candidate):NULL;
    TlkNativeBank *bank=ok?TlkNativeBankCreate():NULL;
    if(ok)ok=candidate && bank && ContinueBackendField(data+96,native_size,saved) &&
        TlkFinalSceneStateLoad(candidate,identity,data+96+native_size,private_size) && candidate->field==saved;
    if(ok)ok=!!candidate->menu_credits==!!(final_menu_art_mode && candidate->continuation.confirmed_field);
    if(ok && candidate->title_navigation.owner)ok=ContinueTitleNavigationSelected();
    if(ok && bank_size)ok=TlkNativeBankLoad(bank,continue_bank_program,data+96+native_size+private_size,bank_size);
    /* Validate absent canvas slots before delegating any guest-state load. */
    if(ok && wide) {
        unsigned present[4]={candidate->flags&TLK_FINAL_ORIGIN,candidate->flags&TLK_FINAL_TARGET,
            candidate->continuation.confirmed_field || candidate->menu_field,candidate->flags&TLK_FINAL_LEVEL};
        const uint8_t *sides=data+size-side_size;
        for(unsigned slot=0;slot<4;slot++)if(!present[slot])
            for(unsigned i=0;i<FINAL_SIDE_PIXELS*4;i++)if(sides[(size_t)slot*FINAL_SIDE_PIXELS*4+i])ok=0;
    }
    if(getenv("TLK_SAVE_TRACE"))fprintf(stderr,"save_load presentation=%d\n",ok);
    char temporary[4096]={0};uint32_t loaded=0;
    if(ok)ok=temp_path(temporary,sizeof temporary,path,".final-load") && write_file(temporary,data+96,native_size);
    if(ok){
        /* Validate the recorded simulation viewport, then resume with the
         * user's current requested view. Window size is not a resource source. */
        TlkCameraLoadViewport((int)saved_viewport);
        ok=PridePracticeLoad(temporary,&loaded);
        TlkCameraLoadViewport(0);
    }
    if(getenv("TLK_SAVE_TRACE"))fprintf(stderr,"save_load backend=%d loaded=%u reason=%s\n",ok,loaded,pride_state_error);
    if(ok) {
        ContinueStateImport(candidate);memset(continue_canvas_sides,0,sizeof continue_canvas_sides);
        if(wide)for(unsigned slot=0;slot<4;slot++)for(unsigned i=0;i<FINAL_SIDE_PIXELS;i++)
            continue_canvas_sides[slot][i]=TlkGet32(data+size-side_size+((size_t)slot*FINAL_SIDE_PIXELS+i)*4);
        TlkNativeBankFree(continue_bank);continue_bank=bank;bank=NULL;if(field)*field=loaded;
    }
    else pride_state_set_error("Final scene save is invalid or source choices differ");
    if(temporary[0])remove(temporary);TlkNativeBankFree(bank);free(candidate);free(data);return ok;
}
/* Capture only the genuine fresh machine, before a CLI load. Stage separately
 * so a rejected load preserves both its input (even the boot file itself) and
 * the preceding restart checkpoint. No late guest state is relabelled as boot. */
static int ContinuePrepareBoot(char *pending,unsigned capacity) {
    char boot[1100];PrBootPath(boot,sizeof boot);pending[0]=0;
    if(!temp_path(pending,capacity,boot,".cold-boot"))return 0;
    if(ContinueLifecycleSave(pending,0))return 1;
    remove(pending);pending[0]=0;return 0;
}
static void ContinuePublishBoot(const char *pending) {
    if(!pending || !*pending)return;
    char boot[1100];PrBootPath(boot,sizeof boot);
    if(!MoveFileExA(pending,boot,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)) {
        fprintf(stderr,"Cannot publish the power-on checkpoint for level restarts\n");remove(pending);
    }
}
void __wrap_TlkResetMachine(void) {
    int menu_reset=final_menu_source_changed || final_menu_art_mode;
    unsigned before_entry=final_scene_entry,before_ready=continue_transition_level_ready;
    unsigned before_bank=TlkNativeBankReady(continue_bank,continue_bank_program);
    ContinuePreviousMachineReset();ContinueLocalClear();
    final_menu_source_changed=0;
    TlkTitleNavigationClear(&title_navigation);
    if(continue_bank)TlkNativeBankClear(continue_bank);
    /* The preceding health-death wrapper is inactive in the native profile.
     * Keep frontend time/input bookkeeping at the real reset boundary too. */
    if(ContinueLifecycleEnabled() || menu_reset) {
        frame=0;s_polls_frame=0;s_macro_n=s_macro_i=0;s_toast[0]=0;s_toast_until=0;
    }
    const char *path=getenv("TLK_FINAL_RESET_LOG");if(path) {
        FILE *f=fopen(path,"w");if(!f)exit(110);
        fprintf(f,"{\"before_entry\":%u,\"before_level_ready\":%u,\"before_bank_ready\":%u,"
            "\"after_entry\":%u,\"after_level_ready\":%u,\"after_bank_ready\":%u,\"frontend_frame\":%ld}\n",
            before_entry,before_ready,before_bank,final_scene_entry,continue_transition_level_ready,
            TlkNativeBankReady(continue_bank,continue_bank_program),frame);fclose(f);
    }
}

/* Appended to the private host's preprocessed translation unit. All state
 * changes here are lifecycle cleanup around the real machine reset API. */
void __real_TlkResetMachine(void);
void PrideMachineRendererReset(const char *folder);
static unsigned machine_reset_serial,machine_injected;
void __wrap_TlkResetMachine(void) {
    __real_TlkResetMachine();
    if(!installed && !scene_installed && !owner_installed)return;
    TlkNativeBank *fresh=installed?TlkNativeBankCreate():NULL;
    if(installed && !fresh)exit(95);
    unsigned enabled=owner_enabled,restore=restore_enabled,canonical=restore_canonical,roar_zero=restore_roar_zero;
    unsigned cursor=restore_idle_cursor;
    owner_enabled=0;
    owner_loop=0;
    owner_skip=0;
    owner_hold_count=0;
    owner_ended=0;
    owner_initial_hold=0;
    owner_waiting=0;
    owner_normal_release=0;
    owner_first_hold_pose=0;
    owner_entry_field=0;
    owner_wait_sp=0;
    owner_wait_a=0;
    owner_wait_x=0;
    owner_wait_y=0;
    owner_wait_d=0;
    owner_wait_p=0;
    owner_wait_db=0;
    restore_enabled=0;
    restore_canonical=0;
    restore_roar_zero=0;
    restore_pending=0;
    restore_committed=0;
    restore_canonical_calls=0;
    restore_idle_cursor=0;
    restore_health=0;
    restore_roar=0;
    restore_roar_font_valid=0;
    restore_roar_font_maximum=0;
    restore_roar_font_current=0;
    restore_roar_font_initial=0;
    applied=0;
    active=0;
    have_return=0;
    return_a=0;
    return_x=0;
    return_y=0;
    scene_calls=0;
    scene_number=0;
    scene_source=0;
    scene_dest=0;
    scene_return=0;
    scene_death=0;
    scene_started=0;
    scene_active=0;
    scene_template_applies=0;
    owner_normal_latch_serial=0;
    owner_default_initialized=0;
    owner_default_prepared=0;
    owner_default_advancing=0;
    owner_default_advanced=0;
    owner_default_advance_wait=0;
    owner_default_callback=0;
    grounded_done=0;
    grounded_waiting=0;
    spawn_native[0]=0;
    spawn_native[1]=0;
    spawn_selected[0]=0;
    spawn_selected[1]=0;
    spawn_md=0;
    spawn_checkpoint=0;
    owner_enabled=enabled;restore_enabled=restore;restore_canonical=canonical;
    restore_roar_zero=roar_zero;restore_idle_cursor=cursor;
    memset(&owner_scene,0,sizeof owner_scene);
    candidate_dumped=record_loaded=0;
    preparation_free(preparation_pending);preparation_pending=NULL;
    if(installed) { TlkNativeBankFree(prepared);prepared=fresh; }
    if(scene_installed)for(unsigned n=0;n<7;n++) {
        SceneTemplate *t=&scene_templates[n];unsigned source=t->source,destination=t->destination,expected=t->expected;
        uint8_t *payload=t->payload,*before=t->before;
        memset(t,0,sizeof *t);t->source=source;t->destination=destination;t->expected=expected;t->payload=payload;t->before=before;
        if(!t->before)t->before=malloc(0x20000);if(!t->before)exit(95);memset(t->before,0,0x20000);
    }
    char folder[4096];snprintf(folder,sizeof folder,"%s/machine-reset-%u",TlkPrideSetting("TLK_SCENE_OWNER_PROBE"),++machine_reset_serial);
    if(TlkPrideMakeDirectory(folder))exit(95);
    snprintf(restart_debug_folder,sizeof restart_debug_folder,"%s",folder);
    snprintf(repeat_debug_folder,sizeof repeat_debug_folder,"%s",folder);
    probe_dir=repeat_debug_folder;scene_folder=repeat_debug_folder;
    PrideMachineRendererReset(folder);
    practice_pending_path[0]=0;practice_pending_field=0;memset(practice_pending_profile,0,sizeof practice_pending_profile);
    pride_state_error[0]=0;
    int hook=pr.hook;memset(&pr,0,sizeof pr);pr.hook=hook;PrSync();
    frame=0;s_polls_frame=0;s_macro_n=s_macro_i=0;
    s_toast[0]=0;s_toast_until=0;
}
_Bool __real_RtlRunFrame(uint32 inputs);
_Bool __wrap_RtlRunFrame(uint32 inputs) {
    const char *at=TlkPrideSetting("TLK_MACHINE_RESET_AT");
    if(at && !machine_injected && (unsigned)snes_frame_counter==(unsigned)strtoul(at,NULL,10)) {
        machine_injected=1;
        const char *root=TlkPrideSetting("TLK_SCENE_OWNER_PROBE"),*kind=TlkPrideSetting("TLK_MACHINE_RESET_KIND");
        char path[4096];snprintf(path,sizeof path,"%s/machine-boundary.json",root);
        FILE *f=TlkPrideFileOpen(path,"w");if(!f)exit(95);
        fprintf(f,"{\"field_before\":%u,\"owner_before\":%u,\"age_before\":%u,\"audio_samples_before\":%u,",
            (unsigned)snes_frame_counter,(unsigned)owner_scene.started,(unsigned)owner_scene.age,s_wav_frames);
        if(kind && !strcmp(kind,"init")) {
            uint8_t *copy=malloc(0x300000);if(!copy)exit(95);memcpy(copy,g_rom,0x300000);
            if(!SnesInit(copy,0x300000))exit(95);
            /* SnesInit copied cartridge data; the frontend's original verified
             * ROM remains the widescreen source for this session. */
            free(copy);
        } else RtlReset(1);
        fprintf(f,"\"field_after\":%u,\"owner_after\":%u,\"pending_after\":%u,\"bank_ready_after\":%u,\"practice_after\":%d,\"audio_profile_changed\":%d}\n",
            (unsigned)snes_frame_counter,(unsigned)owner_scene.started,(unsigned)(preparation_pending!=NULL),
            (unsigned)TlkNativeBankReady(prepared,program),pr.st,TlkAudioProfileChanged());fclose(f);
        inputs=0;
    }
    return __real_RtlRunFrame(inputs);
}

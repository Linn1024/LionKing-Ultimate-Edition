/* Included after the private helpers until their owned-module integration.
 * Non-Pride levels use the native format: the Pride-only controller does not
 * participate there. Never fall back after a failed private save in Pride. */
static int PrideScenePracticeSave(const char *path,uint32_t field) {
    if(!field || !TlkPrideHealthDeathSelected() || ow(0x1ff9e)!=0)
        return __real_tlk_state_save(path,field);
    return PridePrivateSave(path,field);
}
static int PridePracticeLoad(const char *path,uint32_t *field) {
    uint8_t header[36];FILE *file=TlkPrideFileOpen(path,"rb");
    size_t size=file?fread(header,1,sizeof header,file):0;if(file)fclose(file);
    pride_state_error[0]=0;
    int native=size>=32 && !memcmp(header,"TLKSTAT1",8);
    if(native) {
        uint32_t saved=TlkGet32(header+12);
        /* STATE_PRIDE identifies the saved scene, not the current scene. The
         * native loader still validates the full header, sources and payload.
         * A non-Pride record needs no private history even when MD is selected.
         * A late Pride record always needs its matching source/private format.
         * Version1 lacks this scene tag; retain the conservative old guard. */
        uint32_t version=TlkGet32(header+8);
        int pride=version<2 || (size>=36 && (TlkGet32(header+32)&0x80000000u));
        if(saved && pride && TlkPrideHealthDeathSelected()) {
            pride_state_set_error("Select SNES health death to load this native save");
            pride_error_ui_log((uint32_t)snes_frame_counter,0,0);return 0;
        }
        uint32_t loaded=0,attempted=(uint32_t)snes_frame_counter;
        int ok=__real_tlk_state_load(path,&loaded);
        if(!ok)pride_state_set_error(tlk_state_error());
        else {
            /* Discard any prior owned Pride scene only after successful load.
             * Native presentation/audio histories have already been restored;
             * this clears the private controller and renderer, not those. */
            PrideLaunchClearPrivate();
            frame=(long)loaded;if(field)*field=loaded;
        }
        pride_error_ui_log(attempted,ok?loaded:0,ok);return ok;
    }
    if(size>=8 && (!memcmp(header,"PRHSAVE1",8) || !memcmp(header,"PRPRAC01",8) || !memcmp(header,"PRHBOOT1",8)) && !TlkPrideHealthDeathSelected()) {
        pride_state_set_error("Select MD health death to load this save");
        pride_error_ui_log((uint32_t)snes_frame_counter,0,0);return 0;
    }
    return PridePrivateLoad(path,field);
}

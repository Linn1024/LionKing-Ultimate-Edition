/* Read-only observer. The virtual-device exercise lives in --selftest-remap. */
static void TreeHelpJsonString(FILE *log,const char *text) {
    fputc('"',log);
    for(;*text;text++) {
        unsigned char c=(unsigned char)*text;
        if(c=='"' || c=='\\') { fputc('\\',log);fputc(c,log); }
        else if(c<32)fprintf(log,"\\u%04x",c);else fputc(c,log);
    }
    fputc('"',log);
}
static void Present(void) {
    unsigned long before=s_sp_toast_calls;int prompt=s_rom_prompt;PresentCore();
    unsigned long calls=s_sp_toast_calls-before;if(calls!=(prompt?0ul:1ul))exit(95);
    const char *path=TlkPrideSetting("TLK_SOFT_TREE_LOG");
    if(path) {
        static FILE *log;if(!log) { log=TlkPrideFileOpen(path,"w");if(!log)exit(95); }
        fprintf(log,"{\"field\":%u,\"passes\":%lu,\"menu\":%d,\"about\":%d,\"gl\":%d,\"selected\":%d,\"top\":%d,\"action\":%d,\"dirty\":%d,\"modal\":%d,\"width\":%d,\"page\":%d,\"pages\":%d,\"help\":",
            (unsigned)snes_frame_counter,calls,s_menu_open,s_about,s_menu_gl,s_resource_selected,s_resource_top,s_resource_action,TlkResourcesDirty(),!!s_resource_message[0],WideWidth(),s_resource_page,ResourceMessagePages());
        TreeHelpJsonString(log,s_resource_message);
        fprintf(log,",\"level\":%u,\"descriptor\":%u,\"difficulty\":%u,\"control_layout\":%u,\"lives\":%u,\"health\":%u,\"macro_index\":%d,\"macro_length\":%d,\"poll_index\":%llu,\"choices\":[",
            (unsigned)(g_ram[0x1ff9e]|g_ram[0x1ff9f]<<8),
            (unsigned)(g_ram[0xdf]|g_ram[0xe0]<<8|g_ram[0xe1]<<16),
            (unsigned)(g_ram[0x1ff92]|g_ram[0x1ff93]<<8),
            (unsigned)(g_ram[0x1ff9a]|g_ram[0x1ff9b]<<8),
            (unsigned)(g_ram[0x1ffaa]|g_ram[0x1ffab]<<8),
            (unsigned)(g_ram[0x2004]|g_ram[0x2005]<<8),s_macro_i,s_macro_n,(unsigned long long)s_poll_idx);
        for(int i=0;i<TlkResourcesCount();i++) {
            if(i)fputc(',',log);
            fprintf(log,"[\"%s\",%d,%d,%d,%d]",TlkResourcesNode(i)->id,TlkResourcesChoice(i,1),TlkResourcesChoice(i,0),TlkResourcesResolved(i,1),TlkResourcesResolved(i,0));
        }
        fprintf(log,"]}\n");fflush(log);
    }
}

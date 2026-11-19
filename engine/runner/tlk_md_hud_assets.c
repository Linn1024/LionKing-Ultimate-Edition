/* Playback reader: no source-ROM access or HUD resource extraction. */
#include "tlk_md_hud_assets_internal.h"
#include <stdio.h>
static uint8_t installed[TLK_MD_HUD_PAYLOAD_BYTES];
static int installed_ready;
int TlkMdHudAssetsLoad(const uint8_t *record,size_t size){
    if(!hud_record_valid(record,size))return 0;
    memmove(installed,record+TLK_HUD_HEADER,sizeof installed);installed_ready=1;return 1;
}
int TlkMdHudAssetsReadFile(const char *path){
    FILE *file=path && *path?fopen(path,"rb"):NULL;if(!file)return 0;
    uint8_t record[TLK_HUD_HEADER+TLK_MD_HUD_PAYLOAD_BYTES];
    int ok=fread(record,1,sizeof record,file)==sizeof record && fgetc(file)==EOF;
    if(fclose(file))ok=0;
    return ok && TlkMdHudAssetsLoad(record,sizeof record);
}
int TlkMdHudAssetsReady(void){return installed_ready;}
int TlkMdHudAssetsActivate(void){return installed_ready && TlkMdHudInitPrepared(installed,sizeof installed);}

/* Installer-only command. Playback links the package reader separately. */
#include "tlk_final_art.h"
#include "tlk_final_art_prepare.h"
#include "tlk_final_native.h"
#include "tlk_final_native_prepare.h"
#include "tlk_title_bank.h"
#include "tlk_title_bank_prepare.h"
#include "tlk_temp_path.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#include <io.h>
#else
#include <unistd.h>
#endif

int main(int argc,char **argv) {
    int both=argc==7 && !strcmp(argv[1],"--md-rom") && !strcmp(argv[3],"--snes-rom") && !strcmp(argv[5],"--output");
    if(!both && (argc!=5 || (strcmp(argv[1],"--md-rom") && strcmp(argv[1],"--snes-rom") &&
                  strcmp(argv[1],"--snes-title-bank")) || strcmp(argv[3],"--output"))) {
        fprintf(stderr,"Usage: PrepareFinalAssets --md-rom PATH [--snes-rom PATH] --output PATH; or --snes-rom|--snes-title-bank PATH --output PATH\n");return 2;
    }
    const char *output=argv[argc-1];
    int native=!strcmp(argv[1],"--snes-rom"),title=!strcmp(argv[1],"--snes-title-bank");
    FILE *file=fopen(argv[2],"rb");if(!file){fprintf(stderr,"Cannot read source ROM\n");return 3;}
    uint8_t *rom=malloc(0x300000);int ok=rom && fread(rom,1,0x300000,file)==0x300000 && fgetc(file)==EOF;
    fclose(file);uint8_t *record=NULL;size_t size=0;
    uint8_t *snes=NULL;
    if(ok && both) {
        file=fopen(argv[4],"rb");snes=malloc(0x300000);
        ok=file && snes && fread(snes,1,0x300000,file)==0x300000 && fgetc(file)==EOF;
        if(file)fclose(file);
    }
    if(ok)ok=both?TlkFinalArtPrepareMenuSources(rom,0x300000,snes,0x300000,&record,&size):
        title?TlkTitleBankPrepare(rom,0x300000,&record,&size):
        native?TlkFinalNativePrepare(rom,0x300000,&record,&size):TlkFinalArtPrepareMenus(rom,0x300000,&record,&size);free(rom);free(snes);
    if(!ok){fprintf(stderr,"Unsupported or incomplete assets\n");free(record);return 4;}
    if(title) {
        TlkTitleBank *checked=TlkTitleBankLoad(record,size);if(!checked){free(record);return 5;}TlkTitleBankFree(checked);
    } else if(native) {
        TlkFinalNative *checked=TlkFinalNativeLoad(record,size);if(!checked){free(record);return 5;}TlkFinalNativeFree(checked);
    } else {
        TlkFinalArt *checked=TlkFinalArtLoad(record,size);if(!checked){free(record);return 5;}TlkFinalArtFree(checked);
    }
    char temporary[4096]={0};ok=TlkTemporaryPath(temporary,sizeof temporary,output,".install-part");
    file=ok?fopen(temporary,"wb"):NULL;ok=file!=NULL;
    if(file) {
        ok=fwrite(record,1,size,file)==size && fflush(file)==0;
#ifdef _WIN32
        if(ok)ok=_commit(_fileno(file))==0;
#else
        if(ok)ok=fsync(fileno(file))==0;
#endif
        if(fclose(file))ok=0;
    }
#ifdef _WIN32
    if(ok)ok=MoveFileExA(temporary,output,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
    if(ok)ok=rename(temporary,output)==0;
#endif
    if(temporary[0])remove(temporary);free(record);
    if(!ok){fprintf(stderr,"Cannot publish prepared menu assets\n");return 6;}
    printf("%s=prepared bytes=%lu\n",title?"title_bank_assets":native?"final_native_assets":"final_menu_assets",(unsigned long)size);return 0;
}

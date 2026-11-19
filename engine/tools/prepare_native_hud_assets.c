/* Installer-only native command; outputs an atomic prepared HUD package. */
#include "tlk_native_hud.h"
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
int main(int argc,char **argv){
    if(argc!=5 || strcmp(argv[1],"--snes-rom") || strcmp(argv[3],"--output")){
        fprintf(stderr,"Usage: PrepareNativeHudAssets --snes-rom PATH --output PATH\n");return 2;
    }
    FILE *file=fopen(argv[2],"rb");if(!file){fprintf(stderr,"Cannot read source ROM\n");return 3;}
    uint8_t *rom=malloc(0x300000),*record=NULL;size_t size=0;
    int ok=rom && fread(rom,1,0x300000,file)==0x300000 && fgetc(file)==EOF;
    fclose(file);if(ok)ok=TlkNativeHudPrepare(rom,0x300000,&record,&size);free(rom);
    if(!ok){fprintf(stderr,"Unsupported HUD source ROM\n");free(record);return 4;}
    char temporary[4096]={0};ok=TlkTemporaryPath(temporary,sizeof temporary,argv[4],".native-hud-install-part");
    file=ok?fopen(temporary,"wb"):NULL;ok=file!=NULL;
    if(file){
        ok=fwrite(record,1,size,file)==size && fflush(file)==0;
#ifdef _WIN32
        if(ok)ok=_commit(_fileno(file))==0;
#else
        if(ok)ok=fsync(fileno(file))==0;
#endif
        if(fclose(file))ok=0;
    }
#ifdef _WIN32
    if(ok)ok=MoveFileExA(temporary,argv[4],MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
    if(ok)ok=rename(temporary,argv[4])==0;
#endif
    if(temporary[0])remove(temporary);free(record);
    if(!ok){fprintf(stderr,"Cannot publish prepared HUD assets\n");return 6;}
    printf("native_hud_assets=prepared bytes=%lu\n",(unsigned long)size);return 0;
}

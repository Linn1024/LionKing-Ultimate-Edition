/* Installer-only executable; original ROMs are never modified or bundled. */
#include "tlk_title_art.h"
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
static uint8_t *read_rom(const char *path){
    FILE *f=fopen(path,"rb");if(!f)return NULL;uint8_t *p=malloc(0x300000);
    int ok=p && fread(p,1,0x300000,f)==0x300000 && fgetc(f)==EOF;fclose(f);
    if(!ok){free(p);return NULL;}return p;
}
int main(int argc,char **argv){
    if(argc!=7 || strcmp(argv[1],"--snes-rom") || strcmp(argv[3],"--md-rom") || strcmp(argv[5],"--output")){
        fprintf(stderr,"Usage: PrepareCaptionAssets --snes-rom PATH --md-rom PATH --output PATH\n");return 2;
    }
    uint8_t *snes=read_rom(argv[2]),*md=read_rom(argv[4]),*record=NULL;size_t size=0;
    int ok=snes && md && TlkTitleArtPrepare(snes,0x300000,md,0x300000,&record,&size);free(snes);free(md);
    if(!ok){fprintf(stderr,"Unsupported or incomplete caption sources\n");free(record);return 4;}
    char temporary[4096]={0};ok=TlkTemporaryPath(temporary,sizeof temporary,argv[6],".caption-install-part");
    FILE *f=ok?fopen(temporary,"wb"):NULL;ok=f!=NULL;
    if(f){
        ok=fwrite(record,1,size,f)==size && fflush(f)==0;
#ifdef _WIN32
        if(ok)ok=_commit(_fileno(f))==0;
#else
        if(ok)ok=fsync(fileno(f))==0;
#endif
        if(fclose(f))ok=0;
    }
#ifdef _WIN32
    if(ok)ok=MoveFileExA(temporary,argv[6],MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
    if(ok)ok=rename(temporary,argv[6])==0;
#endif
    if(temporary[0])remove(temporary);free(record);
    if(!ok){fprintf(stderr,"Cannot publish prepared captions\n");return 6;}
    printf("caption_assets=prepared bytes=%lu\n",(unsigned long)size);return 0;
}

/* Install-time scene decoding and geometry-safe cross-version artwork mapping. */
#include "tlk_md_assets.h"
#include "tlk_contact_map.h"
#include "sha256.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint8_t *read_rom(const char *path,const char *expected,uint8_t hash[32]) {
    if(!path)return NULL;FILE *f=fopen(path,"rb");if(!f)return NULL;
    uint8_t *bytes=malloc(0x300000);int ok=bytes && fread(bytes,1,0x300000,f)==0x300000 && fgetc(f)==EOF;fclose(f);
    if(!ok){free(bytes);return NULL;}sha256_compute(bytes,0x300000,hash);
    static const char hex[]="0123456789abcdef";
    for(unsigned i=0;i<32;i++)if(hex[hash[i]>>4]!=expected[i*2] || hex[hash[i]&15]!=expected[i*2+1]){free(bytes);return NULL;}
    return bytes;
}
int main(int argc,char **argv) {
    const char *snes_path=NULL,*md_path=NULL,*output=NULL;
    for(int i=1;i<argc;i++) {
        if(i+1>=argc)return 2;
        if(!strcmp(argv[i],"--snes-rom"))snes_path=argv[++i];
        else if(!strcmp(argv[i],"--md-rom"))md_path=argv[++i];
        else if(!strcmp(argv[i],"--output"))output=argv[++i];
        else return 2;
    }
    uint8_t snes_hash[32],md_hash[32];
    uint8_t *snes=read_rom(snes_path,"457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712",snes_hash);
    uint8_t *md=read_rom(md_path,"e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5",md_hash);
    if(!snes || !md || !output){fprintf(stderr,"Verified SNES USA and Mega Drive World ROMs and --output are required.\n");free(snes);free(md);return 3;}
    int decoded=TlkMdAssetsInit(md,0x300000),mapped=TlkMdAssetsBindSnes(snes,0x300000);
    unsigned matched=0,total=0;TlkMdSceneCoverage(1,&matched,&total);
    int contacts=TlkContactMapInit(snes,0x300000,md,0x300000);
    int ok=decoded && mapped && total && contacts && TlkMdAssetsSaveCache(output,snes_hash,md_hash);
    TlkMdAssetsClear();free(snes);free(md);
    if(!ok){fprintf(stderr,"Scene preparation failed.\n");return 4;}
    printf("resource_cache=prepared\ndecoded_scenes=%d\ncant_wait_foreground=%u/%u\npride_contact_cells=8000\n",decoded,matched,total);return 0;
}

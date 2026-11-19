#include "tlk_checkpoint_art.h"
#include "tlk_revival_art.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "sha256.h"

struct TlkCheckpointArt {
    TlkRevivalArt *images;
    uint16_t native[16],md[16];
    int geometry[3][4];uint8_t *pixels[3];
};
#ifdef TLK_CHECKPOINT_ART_PREPARE
TlkCheckpointArt *TlkCheckpointArtCreate(const uint8_t *snes,size_t ss,const uint8_t *md,size_t ms) {
    TlkRevivalArt *images=TlkRevivalArtCreateCheckpoint(snes,ss,md,ms);
    if(!images)return NULL;
    TlkCheckpointArt *art=calloc(1,sizeof *art);
    if(!art) { TlkRevivalArtFree(images);return NULL; }
    art->images=images;
    for(unsigned i=0;i<16;i++) {
        art->native[i]=(uint16_t)(snes[0x7b93+i*2]|(unsigned)snes[0x7b94+i*2]<<8);
        unsigned raw=(unsigned)md[0x1d78aa+i*2]<<8|md[0x1d78ab+i*2];
        unsigned r=(raw>>1)&7,g=(raw>>5)&7,b=(raw>>9)&7;
        art->md[i]=(uint16_t)((r*4+(r>>2))|((g*4+(g>>2))<<5)|((b*4+(b>>2))<<10));
    }
    return art;
}
#endif
void TlkCheckpointArtFree(TlkCheckpointArt *art) {
    if(!art)return;
    TlkRevivalArtFree(art->images);for(unsigned i=0;i<3;i++)free(art->pixels[i]);memset(art,0,sizeof *art);free(art);
}
int TlkCheckpointArtBounds(const TlkCheckpointArt *art,int *x,int *y,int *w,int *h) {
    return TlkCheckpointArtPoseBounds(art,0xc456de,x,y,w,h);
}
int TlkCheckpointArtPixel(const TlkCheckpointArt *art,int x,int y,unsigned source) {
    return TlkCheckpointArtPosePixel(art,0xc456de,x,y,source);
}
static const uint32_t checkpoint_poses[3]={0xc456de,0xc2fde1,0xc2fe18};
static int CheckpointPoseIndex(uint32_t pose) {for(int i=0;i<3;i++)if(checkpoint_poses[i]==pose)return i;return -1;}
int TlkCheckpointArtPoseBounds(const TlkCheckpointArt *art,uint32_t pose,int *x,int *y,int *w,int *h) {
    if(!art || !x || !y || !w || !h)return 0;
    if(art->images)return TlkRevivalArtBounds(art->images,pose,x,y,w,h);
    int i=CheckpointPoseIndex(pose);if(i<0 || !art->pixels[i])return 0;
    *x=art->geometry[i][0];*y=art->geometry[i][1];*w=art->geometry[i][2];*h=art->geometry[i][3];return 1;
}
int TlkCheckpointArtPosePixel(const TlkCheckpointArt *art,uint32_t pose,int x,int y,unsigned source) {
    if(!art || source>1)return -1;
    if(art->images)return TlkRevivalArtPixel(art->images,pose,x,y,source);
    int i=CheckpointPoseIndex(pose);if(i<0 || !art->pixels[i])return -1;
    const int *g=art->geometry[i];x-=g[0];y-=g[1];
    return x<0 || y<0 || x>=g[2] || y>=g[3]?0:art->pixels[i][y*g[2]+x];
}
int TlkCheckpointArtPoseSample(const TlkCheckpointArt *art,uint32_t pose,int x,int y,unsigned frames,unsigned palette,
                          const uint16_t cgram[256],uint16_t *color) {
    if(!art || !cgram || !color || frames>1 || palette>1 ||
       memcmp(cgram+129,art->native+1,15*sizeof(uint16_t)))return -1;
    int pixel=TlkCheckpointArtPosePixel(art,pose,x,y,frames);
    if(pixel<=0)return pixel;
    *color=palette?art->md[pixel]:cgram[128+pixel];return 1;
}
int TlkCheckpointArtSample(const TlkCheckpointArt *art,int x,int y,unsigned frames,unsigned palette,
                          const uint16_t cgram[256],uint16_t *color) {
    return TlkCheckpointArtPoseSample(art,0xc456de,x,y,frames,palette,cgram,color);
}
#include "tlk_checkpoint_art_assets.inc"

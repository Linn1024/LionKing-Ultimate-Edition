#include "tlk_resources.h"
/* Strict installed Timon payload; all source banks were decoded at install. */
#include "sha256.h"
static int timon_valid(const uint8_t *p,size_t n){
    if(n<128+22*48 || n>LIMIT || memcmp(p,"TLKTMN01",8) || get(p,8)!=1 || get(p,12)!=n || get(p,16)!=22 || get(p,20)!=31744)return 0;
    for(unsigned i=120;i<128;i++)if(p[i])return 0;
    for(unsigned i=0;i<32;i++)if(word(p+56+i*2)>0x7fff)return 0;
    if(word(p+56) || word(p+88))return 0;
    size_t at=128+22*48;
    for(unsigned i=0;i<22;i++){
        const uint8_t *f=p+128+i*48;
        if(get(f,0)<0xc1da38 || get(f,0)>0xc1e545 || get(f,4)<0x1dadca || get(f,4)>0x1ddfb2 || !get(f,8) || get(f,8)>256 || get(f,12)!=4)return 0;
        for(unsigned k=0;k<i;k++)if(get(p+128+k*48,0)==get(f,0) || get(p+128+k*48,4)==get(f,4))return 0;
        for(unsigned j=0;j<2;j++){
            const uint8_t *d=f+16+j*8;unsigned w=word(d+4),h=word(d+6),size=get(f,40+j*4);
            if(!w || w>256 || !h || h>224 || size!=w*h || coord(d)<-256 || coord(d)>256 || coord(d+2)<-224 || coord(d+2)>224 || get(f,32+j*4)!=at || size>n-at)return 0;
            for(unsigned k=0;k<size;k++)if(p[at+k]>=16)return 0;
            at+=size;
        }
    }
    return at==n;
}
static const uint8_t *timon_record(void){
    const uint8_t *cliff=cliff_record();return cliff && get(record,8)==4?cliff+get(cliff,12):NULL;
}
int TlkInterlevelDataTimonReady(void){return timon_record()!=NULL;}
int TlkInterlevelDataTimonBankMatches(const uint8_t *ram,size_t n){
    const uint8_t *p=timon_record();if(!p || !ram || n<get(p,20))return 0;
    uint8_t hash[32];sha256_compute(ram,get(p,20),hash);return !memcmp(hash,p+24,32);
}
static unsigned timon_nearest(unsigned c,const uint8_t *palette){
    unsigned best=1,distance=~0u;
    for(unsigned i=1;i<16;i++){unsigned other=word(palette+i*2),d=0;
        for(unsigned k=0;k<3;k++){int v=(int)((c>>(k*5))&31)-(int)((other>>(k*5))&31);d+=(unsigned)(v*v);}
        if(d<distance){distance=d;best=i;}
    }
    return best;
}
static int RenderTimonColours(int custom,unsigned native_pose,unsigned tick,int md_timing,int md_frames,int md_palette,int ox,int oy,unsigned width,const uint16_t *cgram,const uint8_t *brightness,uint32_t *pixels){
    const uint8_t *p=timon_record();if(!p || !cgram || !brightness || !pixels || (width!=256 && width!=320))return 0;
    unsigned index=22;for(unsigned i=0;i<22;i++)if(get(p+128+i*48,0)==native_pose){index=i;break;}if(index==22)return 0;
    /* Timon's prepared source bank has no palette animation or damage flash. */
    for(unsigned i=1;i<16;i++)if(cgram[i]!=word(p+56+i*2))return 0;
    if(md_timing){index=0;while(index<21 && tick>=get(p+128+index*48,12)){tick-=get(p+128+index*48,12);index++;}}
    unsigned side=!!md_frames;const uint8_t *f=p+128+index*48,*d=f+16+side*8,*image=p+get(f,32+side*4);unsigned w=word(d+4),h=word(d+6);
    uint16_t colors[16]={0};
    for(unsigned i=1;i<16;i++){
        unsigned n=i;
        if(md_frames && !md_palette)n=timon_nearest(word(p+88+i*2),p+56);
        if(!md_frames && md_palette)n=timon_nearest(word(p+56+i*2),p+88);
        colors[i]=md_palette?(uint16_t)word(p+88+n*2):cgram[n];
        if(custom)colors[i]=TlkResourcesSpritePaletteMap(TlkResourcesFind("graphics.sprites.cinematics.timon.palette"),md_palette,colors[i]);
    }
    memset(pixels,0,(size_t)width*224*sizeof *pixels);ox+=coord(d);oy+=coord(d+2);
    for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
        unsigned v=image[y*w+x];int xx=ox+(int)x,yy=oy+(int)y;if(!v || xx<0 || xx>=(int)width || yy<0 || yy>=224)continue;
        unsigned bright=brightness[yy];uint32_t rgb=0xff000000u;
        for(unsigned k=0;k<3;k++){unsigned c=(colors[v]>>(k*5))&31;rgb|=(((c<<3)|(c>>2))*bright/15)<<((2-k)*8);}
        pixels[yy*width+xx]=rgb;
    }
    return (int)index+1;
}

int TlkInterlevelDataRenderTimon(unsigned pose,unsigned tick,int timing,int frames,int palette,int x,int y,unsigned width,const uint16_t *colors,const uint8_t *bright,uint32_t *out){return RenderTimonColours(0,pose,tick,timing,frames,palette,x,y,width,colors,bright,out);}
int TlkInterlevelDataRenderTimonCustom(unsigned pose,unsigned tick,int timing,int frames,int palette,int x,int y,unsigned width,const uint16_t *colors,const uint8_t *bright,uint32_t *out){return RenderTimonColours(1,pose,tick,timing,frames,palette,x,y,width,colors,bright,out);}

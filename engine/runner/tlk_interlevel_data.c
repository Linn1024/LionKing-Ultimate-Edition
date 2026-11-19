#include "tlk_interlevel_data.h"
#include "tlk_data_record.h"
#include <stdlib.h>
#include <string.h>

enum { HEADER=64,PALETTE=128,PIXELS=320*224,MAX_FRAMES=64,MAX_STEPS=128,LIMIT=1024*1024 };
static uint8_t *record;
static size_t record_size;
static unsigned frames[MAX_FRAMES];
static unsigned get(const uint8_t *p,unsigned at){return TlkDataGet32(p+at);}
static unsigned word(const uint8_t *p){return TlkDataGet16(p);}
static int coord(const uint8_t *p){unsigned v=word(p);return v<32768?(int)v:(int)v-65536;}
#include "tlk_ending_credits_data.inc"
#include "tlk_cliff_data.inc"
#include "tlk_timon_data.inc"
void TlkInterlevelDataClear(void){free(record);record=NULL;record_size=0;memset(frames,0,sizeof frames);}
int TlkInterlevelDataReady(void){return record!=NULL;}
size_t TlkInterlevelDataRecordSize(void){return record_size;}
int TlkInterlevelDataWrite(uint8_t *p,size_t n){if(!record || !p || n!=record_size)return 0;memcpy(p,record,n);return 1;}
int TlkInterlevelDataRead(const uint8_t *p,size_t n,int apply){
    if(!p || n<HEADER+PALETTE+PIXELS || n>LIMIT || memcmp(p,"TLKILV01",8) ||
       (get(p,8)<1 || get(p,8)>4) || get(p,12)!=n || (get(p,8)==1 && get(p,60)))return 0;
    unsigned count=get(p,16),n0=get(p,20),n1=get(p,24),bg=get(p,44),program=get(p,40),image=get(p,36),audio=get(p,48);
    if(!count || count>MAX_FRAMES || !n0 || n0>MAX_STEPS || !n1 || n1>MAX_STEPS ||
       get(p,28)>=n0 || get(p,32)>=n1 || bg!=HEADER+PALETTE || program!=bg+PIXELS ||
       image!=program+(n0+n1)*12 || image>n || audio>n || audio<image ||
       get(p,52)!=0x4756 || get(p,56)!=0x2922 || n-audio<0x4756+0x2922)return 0;
    size_t clips_end=audio+0x4756+0x2922;
    if(get(p,8)==1){if(n!=clips_end)return 0;}
    else {
        if(get(p,60)!=clips_end || n-clips_end<16)return 0;
        size_t credit_size=get(p+clips_end,12);
        if(credit_size>n-clips_end || !credits_valid(p+clips_end,credit_size))return 0;
        size_t end=clips_end+credit_size;
        if(get(p,8)==2){if(end!=n)return 0;}
        else if(get(p,8)==3){if(!cliff_valid(p+end,n-end))return 0;}
        else {
            if(n-end<16)return 0;size_t cliff_size=get(p+end,12);
            if(cliff_size>n-end || !cliff_valid(p+end,cliff_size) || !timon_valid(p+end+cliff_size,n-end-cliff_size))return 0;
        }
    }
    for(unsigned i=0;i<64;i++)if(word(p+HEADER+i*2)>0x7fff)return 0;
    for(unsigned i=0;i<PIXELS;i++)if(p[bg+i]>=64)return 0;
    for(unsigned i=0;i<n0+n1;i++){
        const uint8_t *s=p+program+i*12;
        if(get(s,0)>=count || !get(s,4) || get(s,4)>256 || (get(s,8)&~14u))return 0;
    }
    unsigned offsets[MAX_FRAMES];size_t at=image;
    for(unsigned i=0;i<count;i++){
        if(at>audio || audio-at<16)return 0;const uint8_t *f=p+at;
        unsigned w=word(f+8),h=word(f+10),bytes=get(f,12);
        if(!w || !h || w>256 || h>224 || bytes!=w*h || coord(f+4)<-256 || coord(f+4)>256 ||
           coord(f+6)<-224 || coord(f+6)>224 || bytes>audio-at-16)return 0;
        for(unsigned k=0;k<i;k++)if(get(p+offsets[k],0)==get(f,0))return 0;
        for(unsigned k=0;k<bytes;k++)if(f[16+k]>=16)return 0;
        offsets[i]=(unsigned)at;at+=16+bytes;
    }
    if(at!=audio)return 0;
    if(apply){uint8_t *copy=malloc(n);if(!copy)return 0;memcpy(copy,p,n);TlkInterlevelDataClear();record=copy;record_size=n;memcpy(frames,offsets,count*sizeof *frames);}
    return 1;
}
static const uint8_t *step(unsigned program,unsigned tick,unsigned *first){
    if(!record || program>1)return NULL;
    unsigned count=get(record,20+program*4),loop=get(record,28+program*4),base=get(record,40)+(program?get(record,20)*12:0);
    unsigned total=0,prefix=0;
    for(unsigned i=0;i<count;i++){if(i==loop)prefix=total;total+=get(record+base+i*12,4);}
    if(tick>=total)tick=prefix+(tick-prefix)%(total-prefix);
    for(unsigned i=0;i<count;i++){const uint8_t *s=record+base+i*12;unsigned duration=get(s,4);if(tick<duration){if(first)*first=tick==0;return s;}tick-=duration;}
    return NULL;
}
unsigned TlkInterlevelDataPose(unsigned program,unsigned tick){const uint8_t *s=step(program,tick,NULL);return s?get(record+frames[get(s,0)],0):0;}
unsigned TlkInterlevelDataEvents(unsigned tick){unsigned events=0;for(unsigned i=0;i<2;i++){unsigned first=0;const uint8_t *s=step(i,tick,&first);if(s && first)events|=get(s,8);}return events;}
unsigned TlkInterlevelDataDuration(void){
    if(!record)return 0;unsigned n=get(record,24),base=get(record,40)+get(record,20)*12,total=0;
    for(unsigned i=0;i<n;i++){const uint8_t *s=record+base+i*12;if(get(s,8)&2)return total;total+=get(s,4);}return 0;
}
static uint32_t color(unsigned index,unsigned brightness,unsigned cap,unsigned loss){
    unsigned c=word(record+HEADER+index*2);uint32_t rgb=0xff000000u;
    for(unsigned i=0;i<3;i++){unsigned v=((c>>(i*5))&31)>>2;if(v>cap)v=cap;v=v>loss?v-loss:0;v=(v*4+(v>>2))*brightness/15;rgb|=((v<<3)|(v>>2))<<((2-i)*8);}return rgb;
}
static int render(unsigned tick,unsigned brightness,unsigned cap,unsigned loss,unsigned width,uint32_t *pixels,unsigned actors){
    if(!record || !pixels || brightness>15 || cap>7 || loss>8 || (width!=256 && width!=320))return 0;
    unsigned start=(320-width)/2;uint32_t palette[64];for(unsigned i=0;i<64;i++)palette[i]=color(i,brightness,cap,loss);
    const uint8_t *bg=record+get(record,44);
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<width;x++)pixels[y*width+x]=palette[bg[y*320+x+start]];
    for(unsigned i=0;i<actors;i++){
        const uint8_t *s=step(i,tick,NULL);if(!s)return 0;const uint8_t *f=record+frames[get(s,0)];
        int ox=128+coord(f+4)-(int)start,oy=160+coord(f+6);unsigned w=word(f+8),h=word(f+10);
        for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
            unsigned value=f[16+y*w+x];int xx=ox+(int)x,yy=oy+(int)y;
            if(value && xx>=0 && xx<(int)width && yy>=0 && yy<224)pixels[yy*width+xx]=palette[32+value];
        }
    }
    return 1;
}
int TlkInterlevelDataRender(unsigned tick,unsigned brightness,unsigned width,uint32_t *pixels){return render(tick,brightness,7,0,width,pixels,2);}
int TlkInterlevelDataRenderFade(unsigned tick,unsigned cap,unsigned loss,unsigned width,uint32_t *pixels){return render(tick,15,cap,loss,width,pixels,2);}
/* The ending initializer1CDD3A reuses these same planes/bank/palette but
 * creates only adult descriptor18DAC6, at128/160. Native idle drawings pair
 * exactly with the five prepared adult images. Retain native animation cues;
 * do not replay the earlier interlevel's cub or voice/timing program here. */
int TlkInterlevelDataRenderEnding(unsigned pose,unsigned brightness,unsigned width,uint32_t *pixels){
    static const unsigned native[]={0xc0186d,0xc018a8,0xc018e3,0xc01922,0xc0195d};
    for(unsigned i=0;i<sizeof native/sizeof native[0];i++)if(pose==native[i])
        return render(i*8,brightness,7,0,width,pixels,1);
    return 0;
}
static const uint8_t *ending_title_image(void){
    if(record)for(unsigned i=0;i<get(record,16);i++)
        if(get(record+frames[i],0)==0x290c62)return record+frames[i];
    return NULL;
}
int TlkInterlevelDataEndingTitleReady(void){return ending_title_image()!=NULL;}
int TlkInterlevelDataRenderEndingTitle(unsigned brightness,unsigned width,uint32_t *pixels){
    const uint8_t *f=ending_title_image();
    if(!f || !pixels || brightness>15 || (width!=256 && width!=320))return 0;
    int ox=coord(f+4)-(int)((320-width)/2),oy=coord(f+6);
    unsigned w=word(f+8),h=word(f+10);uint32_t palette[16];
    for(unsigned i=0;i<16;i++)palette[i]=color(48+i,brightness,7,0);
    for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++){
        unsigned v=f[16+y*w+x];int xx=ox+(int)x,yy=oy+(int)y;
        if(v && xx>=0 && xx<(int)width && yy>=0 && yy<224)pixels[yy*width+xx]=palette[v];
    }
    return 1;
}
const uint8_t *TlkInterlevelDataSample(unsigned sample,size_t *size,unsigned *period){
    if(!record || sample>1 || !size || !period)return NULL;*size=get(record,52+sample*4);*period=125;
    return record+get(record,48)+(sample?get(record,52):0);
}

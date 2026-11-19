/* Installed result artwork and timing operands, with no runtime ROM decoder. */
#include "tlk_bonus_result_data.h"
#include "tlk_data_record.h"
#include <stdlib.h>
#include <string.h>
enum { HEADER=64, LABEL=320*224, DIGITS=10*16*18, FONT=36*16*16,
       LABEL_AT=224, DIGITS_AT=LABEL_AT+LABEL, FONT_AT=DIGITS_AT+DIGITS,
       SAMPLE_AT=FONT_AT+FONT, TOTAL=SAMPLE_AT+0x51c3 };
static uint8_t *record;
static unsigned get(unsigned at){return TlkDataGet32(record+at);}
void TlkBonusResultDataClear(void){free(record);record=NULL;}
int TlkBonusResultDataReady(void){return record!=NULL;}
size_t TlkBonusResultDataRecordSize(void){return record?TOTAL:0;}
int TlkBonusResultDataWrite(uint8_t *p,size_t n){if(!record || !p || n!=TOTAL)return 0;memcpy(p,record,n);return 1;}
int TlkBonusResultDataRead(const uint8_t *p,size_t n,int apply){
    if(!p || n!=TOTAL || memcmp(p,"TLKBR001",8) || TlkDataGet32(p+8)!=1 || TlkDataGet32(p+12)!=n ||
       TlkDataGet32(p+16)!=LABEL_AT || TlkDataGet32(p+20)!=DIGITS_AT || TlkDataGet32(p+24)!=FONT_AT ||
       TlkDataGet32(p+28)!=SAMPLE_AT || TlkDataGet32(p+32)!=0x51c3 || TlkDataGet32(p+36)!=113)return 0;
    unsigned ramp=TlkDataGet32(p+40),quiet=TlkDataGet32(p+44),fade=TlkDataGet32(p+48),timer=TlkDataGet32(p+52);
    if(!ramp || ramp>120 || !quiet || quiet>60 || fade<2 || fade>60 || !timer || timer>600 ||
       TlkDataGet32(p+56)>timer || TlkDataGet32(p+60)>99)return 0;
    for(unsigned i=64;i<LABEL_AT;i+=2)if(TlkDataGet16(p+i)>32767)return 0;
    for(unsigned i=LABEL_AT;i<SAMPLE_AT;i++)if(p[i]>15)return 0;
    if(apply){uint8_t *copy=malloc(n);if(!copy)return 0;memcpy(copy,p,n);TlkBonusResultDataClear();record=copy;}
    return 1;
}
unsigned TlkBonusResultDataParameter(unsigned p){return record && p<6?get(40+p*4):0;}
static uint32_t color(unsigned index,unsigned md,unsigned cap,unsigned loss){
    unsigned c=TlkDataGet16(record+(md?64:192)+index*2),rgb=0xff000000;
    for(unsigned channel=0;channel<3;channel++){
        unsigned v=(c>>(channel*5))&31;
        if(md){v=(v*7+15)/31;v=v>cap?cap:v;v=v>loss?v-loss:0;v=v*4+(v>>2);}
        else {unsigned gain=cap>loss?cap-loss:0;v=v*gain/7;}
        rgb|=((v<<3)|(v>>2))<<(16-channel*8);
    }
    return rgb;
}
int TlkBonusResultDataRender(unsigned count,unsigned md,unsigned cap,unsigned loss,unsigned width,uint32_t *out){
    if(!record || !out || width<256 || width>1024 || cap>7 || loss>8)return 0;
    count=count>99?99:count;uint32_t colors[16];
    for(unsigned i=0;i<16;i++)colors[i]=color(i,md!=0,cap,loss);
    for(unsigned i=0;i<width*224;i++)out[i]=0xff000000;
    int origin=((int)width-320)/2;
    if(md){
        for(unsigned y=0;y<224;y++)for(unsigned x=0;x<320;x++){
            unsigned v=record[LABEL_AT+y*320+x];int xx=origin+(int)x;
            if(v && xx>=0 && xx<(int)width)out[y*width+xx]=colors[v];
        }
        for(unsigned digit=0;digit<2;digit++){
            const uint8_t *pixels=record+DIGITS_AT+(digit?count%10:count/10)*16*18;
            for(unsigned y=0;y<18;y++)for(unsigned x=0;x<16;x++){
                unsigned v=pixels[y*16+x];int xx=origin+240+(int)digit*16+x;
                if(v && xx>=0 && xx<(int)width)out[(96+y)*width+xx]=colors[v];
            }
        }
    }else{
        static const char text[]="00 BUGS CAUGHT";
        for(unsigned letter=0;letter<sizeof text-1;letter++){
            unsigned c=letter==0?'0'+count/10:letter==1?'0'+count%10:(unsigned)text[letter];
            if(c==' ')continue;unsigned glyph=c>='A'?c-'A':c-'0'+26;
            const uint8_t *pixels=record+FONT_AT+glyph*256;
            for(unsigned y=0;y<16;y++)for(unsigned x=0;x<16;x++){
                unsigned v=pixels[y*16+x];int xx=((int)width-256)/2+16+(int)letter*16+x;
                if(v && xx>=0 && xx<(int)width)out[(80+y)*width+xx]=colors[v];
            }
        }
    }
    return 1;
}

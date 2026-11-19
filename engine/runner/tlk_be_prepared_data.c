/* Installation owns source decoding. Playback imports explicit validated records. */
#include "tlk_be_prepared_data.h"
#include "tlk_data_record.h"
#include <string.h>
#ifdef TLK_INTERLEVEL_PREPARER
#include "tlk_md_assets.h"
#include "tlk_md_sprites.h"
#include "pride_sprite_map.h"
#include <stdlib.h>
#endif
enum{BOXES=36,MARKERS=2,HEADER=32,BOX_BYTES=24,MARKER_BYTES=8,RULE_BYTES=16+(TLK_BP_LEAPER_RULES+TLK_BP_SOUND_RULES)*2,
     BYTES=HEADER+BOXES*BOX_BYTES+MARKERS*MARKER_BYTES+RULE_BYTES};
static uint8_t boxes[BOXES][BOX_BYTES],markers[MARKERS][MARKER_BYTES];
static int ready;
static uint16_t leaper[TLK_BP_LEAPER_RULES],group_sound[TLK_BP_SOUND_RULES];
const uint16_t *TlkBePreparedGroupSoundRules(void){return ready?group_sound:NULL;}
const uint16_t *TlkBePreparedLeaperRules(void){return ready?leaper:NULL;}
static uint16_t spread[4];static uint32_t initialization[2];
int TlkBePreparedDataReady(void){return ready;}
size_t TlkBePreparedDataRecordSize(void){return ready?BYTES:0;}
const uint16_t *TlkBePreparedSpreadRules(void){return ready?spread:NULL;}
int TlkBePreparedGeyserInitialization(unsigned*n,unsigned*m){if(!ready||!n||!m)return 0;*n=initialization[0];*m=initialization[1];return 1;}
#ifdef TLK_INTERLEVEL_PREPARER
static unsigned be16(const uint8_t*p){return (unsigned)p[0]<<8|p[1];}
static unsigned sn24(const uint8_t*p){return TlkDataGet16(p)|(unsigned)p[2]<<16;}
static unsigned md32(const uint8_t*p){return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3];}
static int box(unsigned i,unsigned descriptor,unsigned native,unsigned md,const uint8_t*s,const uint8_t*m){
    unsigned off=native&0x3fffff;if(i>=BOXES||off>0x300000-20||md>0x300000-20)return 0;
    uint8_t*q=boxes[i];TlkDataPut32(q,descriptor);TlkDataPut32(q+4,off|0xc00000);
    for(unsigned j=0;j<4;j++){TlkDataPut16(q+8+j*2,TlkDataGet16(s+off+12+j*2));TlkDataPut16(q+16+j*2,(uint16_t)be16(m+md+12+j*2));}return 1;
}
static int command(const uint8_t*p,unsigned*at,int md,unsigned*duration,unsigned*pose){
    for(unsigned i=0;i<8;i++){
        if(*at>0x300000-4)return 0;
        unsigned d=p[*at];
        if(d<240){*duration=d;const uint8_t*q=p+*at+1;*pose=md?((unsigned)q[0]<<16|(unsigned)q[1]<<8|q[2]):sn24(q);*at+=4;return 1;}
        if(d!=250&&d!=253)return 0;*at+=2;
    }
    return 0;
}
static int prepare_markers(const uint8_t*s,const uint8_t*m){
    const uint8_t*sr=s+0x4e5,*mr=m+0x1cfdb4+7*48;
    if(TlkDataGet16(sr+18)!=610||TlkDataGet16(sr+20)!=45||be16(mr+12)!=610||be16(mr+14)!=45)return 0;
    uint8_t*sm=malloc(27450),*mm=malloc(27450),*sc=malloc(65536);size_t a=0,b=0,c=0;
    int ok=sm&&mm&&sc&&TlkMdDecompress(s,0x300000,sn24(sr+9)&0x3fffff,sm,27450,&a)&&a==27450&&
        TlkMdDecompress(m,0x300000,md32(mr+16),mm,27450,&b)&&b==27450&&
        TlkMdDecompress(s,0x300000,sn24(sr)&0x3fffff,sc,65536,&c);
    unsigned mc=md32(mr+4),count=0;
    for(unsigned cell=0;ok&&cell<13725;cell++){
        unsigned sw=TlkDataGet16(sm+cell*2),mw=be16(mm+cell*2),so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if(so+4>c||mc>0x300000-4||mo>0x300000-mc-4){ok=0;break;}
        unsigned n=sc[so+3],v=m[mc+mo+3];
        if(n==v||(n!=128&&v!=128))continue;
        if(count>=MARKERS){ok=0;break;}
        uint8_t*q=markers[count++];TlkDataPut32(q,cell);TlkDataPut16(q+4,sw);q[6]=(uint8_t)n;q[7]=(uint8_t)v;
    }
    free(sm);free(mm);free(sc);return ok&&count==MARKERS;
}
#endif
int TlkBePreparedDataPrepare(const uint8_t*s,size_t sn,const uint8_t*m,size_t mn){
    ready=0;
#ifdef TLK_INTERLEVEL_PREPARER
    if(!s||!m||sn!=0x300000||mn!=0x300000)return 0;
    if(sn24(s+0x58768+6)!=0xc60466||md32(m+0x13ff26+6)!=0x10ebc0)return 0;
    if(!box(0,0xc58768,0xc60466,0x10ebc0,s,m))return 0;
    unsigned sa=0x23d7c,ma=0x13fe1c;
    for(unsigned i=0;i<13;i++){
        unsigned nd,md,np,mp;
        if(!command(s,&sa,0,&nd,&np)||!command(m,&ma,1,&md,&mp)||nd!=md||!box(i+1,0xc58780,np,mp,s,m))return 0;
    }
    unsigned count=14;
    for(unsigned i=0;i<sizeof sprite_map/sizeof*sprite_map;i++){
        const struct SpriteMap*p=&sprite_map[i];
        if(p->role!=TLK_MD_SPRITE_LATER_ENEMY||p->snes<0x38feb||p->snes>0x393e8)continue;
        if(!box(count++,0xc587d6,p->snes,p->md,s,m))return 0;
    }
    if(count!=BOXES||!prepare_markers(s,m))return 0;
    if(memcmp(s+0x40160,"\x29\x1f\x00",3)||memcmp(s+0x40165,"\xa9\x10\x00",3)||
       memcmp(m+0x1af8cc,"\x02\x42\x00\x3f\x3e\x3c\x00\x20",8))return 0;
    spread[0]=TlkDataGet16(s+0x40161);spread[1]=(uint16_t)be16(m+0x1af8ce);
    spread[2]=TlkDataGet16(s+0x40166);spread[3]=(uint16_t)be16(m+0x1af8d2);
    initialization[0]=sn24(s+0x5874a+9);initialization[1]=sn24(s+0x5874a);
    if(initialization[0]!=0xc58589||initialization[1]!=0xc2d7ca||md32(m+0x13fefc)!=0x1a3168||md32(m+0x13fefc+10)!=0x1a3168)return 0;
    /* Reviewed native operands and MD chain/controller instruction operands.
     * Installation verifies source instructions; playback imports these words. */
    if(memcmp(s+0x38da8,"\xa9\x00\xc0",3)||memcmp(s+0x38dad,"\xa9\x01\x00",3)||
       memcmp(s+0x38f12,"\xa9\xf0\x00",3)||memcmp(m+0x1aa754,"\x22\x3c\x00\x02\x80\x00",6)||
       memcmp(m+0x1aa89e,"\x33\x7c\x00\xb4\x00\x28",6)||memcmp(m+0x1aa8c2,"\x04\x41\x00\x10",4)||
       memcmp(m+0x1aa9ba,"\x0c\x6e\x01\x2c\xff\xfe",6)||memcmp(m+0x1aa9c4,"\x0c\x6e\x01\x2c\xff\xfc",6)||
       memcmp(m+0x1aaa64,"\x0c\x6e\x00\x78\xff\xfe",6)||memcmp(m+0x1aaa6e,"\x0c\x6e\x00\x96\xff\xfc",6)||
       memcmp(m+0x1aaafe,"\x04\x43\x00\x0a",4)||memcmp(m+0x1aab08,"\x06\x42\x00\x0a",4)||
       memcmp(m+0x1aa7ce,"\x04\x43\x00\x10",4)||memcmp(m+0x1aa7ec,"\x04\x41\x00\x10",4))return 0;
    leaper[0]=TlkDataGet16(s+0x38da9);leaper[1]=(uint16_t)md32(m+0x1aa756);
    leaper[2]=TlkDataGet16(s+0x38dae);leaper[3]=(uint16_t)(md32(m+0x1aa756)>>16);
    leaper[4]=TlkDataGet16(s+0x38f13);leaper[5]=(uint16_t)be16(m+0x1aa8a0);
    leaper[6]=(uint16_t)be16(m+0x1aa8c4);leaper[7]=(uint16_t)be16(m+0x1aa9bc);
    leaper[8]=(uint16_t)be16(m+0x1aaa66);leaper[9]=(uint16_t)be16(m+0x1aaa70);
    leaper[10]=(uint16_t)be16(m+0x1aab0a);leaper[11]=(uint16_t)be16(m+0x1aab00);
    leaper[12]=(uint16_t)be16(m+0x1aa7d0);leaper[13]=(uint16_t)be16(m+0x1aa7ee);
    if(memcmp(s+0x38e4a,"\xf4\x00\x00\xf4\x1d\x00\x22\xec\x2c\xc2",10)||
       memcmp(s+0x22d10,"\x09\x78\x00",3)||memcmp(s+0x22c35,"\x09\x00\x80",3)||
       memcmp(s+0x218ee,"\xa9\x00\x1f\x60",4)||
       memcmp(m+0x1aa8d0,"\x32\x3c\x00\x21\x06\x41\x00\x10\x3f\x01\x4e\xb9\x00\x00\x22\x10",16)||
       memcmp(m+0x223c,"\x7e\x13\x4e\xb9\x00\x2d\x00\x00",8)||
       memcmp(m+0x2220,"\x0c\x40\x00\x30\x6d\x04\x04\x40\x00\x10\x0c\x40\x00\x10\x6d\x04\x04\x40\x00\x10",20))return 0;
    group_sound[0]=TlkDataGet16(s+0x38e4e);group_sound[1]=TlkDataGet16(s+0x38e4b);
    group_sound[2]=TlkDataGet16(s+0x22d11);group_sound[3]=(uint16_t)(be16(m+0x1aa8d2)+be16(m+0x1aa8d6));
    group_sound[4]=m[0x223d];group_sound[5]=group_sound[3];
    if(group_sound[5]>=48)group_sound[5]-=16;if(group_sound[5]>=16)group_sound[5]-=16;
    group_sound[6]=m[0x224a+group_sound[3]];group_sound[7]=TlkDataGet16(s+0x22c36);
    if(group_sound[6]!=255||group_sound[5]!=17)return 0;
    ready=1;return 1;
#else
    (void)s;(void)sn;(void)m;(void)mn;return 0;
#endif
}
int TlkBePreparedDataWrite(uint8_t*p,size_t n){
    if(!ready||!p||n!=BYTES)return 0;
    memcpy(p,"TLKBP003",8);TlkDataPut32(p+8,3);TlkDataPut32(p+12,BYTES);TlkDataPut32(p+16,BOXES);
    TlkDataPut32(p+20,MARKERS);TlkDataPut32(p+24,RULE_BYTES);TlkDataPut32(p+28,0);
    size_t at=HEADER;memcpy(p+at,boxes,sizeof boxes);at+=sizeof boxes;memcpy(p+at,markers,sizeof markers);at+=sizeof markers;
    for(unsigned i=0;i<4;i++)TlkDataPut16(p+at+i*2,spread[i]);TlkDataPut32(p+at+8,initialization[0]);TlkDataPut32(p+at+12,initialization[1]);
    for(unsigned i=0;i<TLK_BP_LEAPER_RULES;i++)TlkDataPut16(p+at+16+i*2,leaper[i]);
    for(unsigned i=0;i<TLK_BP_SOUND_RULES;i++)TlkDataPut16(p+at+16+(TLK_BP_LEAPER_RULES+i)*2,group_sound[i]);return 1;
}
int TlkBePreparedDataRead(const uint8_t*p,size_t n,int apply){
    if(!p||n!=BYTES||memcmp(p,"TLKBP003",8)||TlkDataGet32(p+8)!=3||TlkDataGet32(p+12)!=n||
       TlkDataGet32(p+16)!=BOXES||TlkDataGet32(p+20)!=MARKERS||TlkDataGet32(p+24)!=RULE_BYTES||TlkDataGet32(p+28))return 0;
    size_t at=HEADER;unsigned previous_desc=0,previous_pose=0,counts[3]={0,0,0};
    for(unsigned i=0;i<BOXES;i++,at+=BOX_BYTES){
        unsigned descriptor=TlkDataGet32(p+at),pose=TlkDataGet32(p+at+4),kind;
        if(descriptor==0xc58768)kind=0;else if(descriptor==0xc58780)kind=1;else if(descriptor==0xc587d6)kind=2;else return 0;
        if(pose<0xc00000||pose>=0xc80000||(i&&(descriptor<previous_desc||(descriptor==previous_desc&&pose<=previous_pose))))return 0;
        previous_desc=descriptor;previous_pose=pose;counts[kind]++;
        for(unsigned j=0;j<8;j++){int v=(int16_t)TlkDataGet16(p+at+8+j*2);if(v<-512||v>512)return 0;}
    }
    if(counts[0]!=1||counts[1]!=13||counts[2]!=22)return 0;
    for(unsigned i=0;i<MARKERS;i++,at+=MARKER_BYTES){
        if(TlkDataGet32(p+at)!=12922+i||p[at+6]!=(i?0:128)||p[at+7]!=(i?128:0))return 0;
    }
    if(TlkDataGet16(p+at)!=31||TlkDataGet16(p+at+2)!=63||TlkDataGet16(p+at+4)!=16||TlkDataGet16(p+at+6)!=32||
       TlkDataGet32(p+at+8)!=0xc58589||TlkDataGet32(p+at+12)!=0xc2d7ca)return 0;
    static const uint16_t expected[TLK_BP_LEAPER_RULES]={0xc000,0x8000,1,2,240,180,16,300,120,150,10,10,16,16};
    for(unsigned i=0;i<TLK_BP_LEAPER_RULES;i++)if(TlkDataGet16(p+at+16+i*2)!=expected[i])return 0;
    static const uint16_t sound_expected[TLK_BP_SOUND_RULES]={29,0,120,49,19,17,255,0x8000};
    for(unsigned i=0;i<TLK_BP_SOUND_RULES;i++)if(TlkDataGet16(p+at+16+(TLK_BP_LEAPER_RULES+i)*2)!=sound_expected[i])return 0;
    if(apply){for(unsigned i=0;i<TLK_BP_SOUND_RULES;i++)group_sound[i]=TlkDataGet16(p+at+16+(TLK_BP_LEAPER_RULES+i)*2);for(unsigned i=0;i<TLK_BP_LEAPER_RULES;i++)leaper[i]=TlkDataGet16(p+at+16+i*2);memcpy(boxes,p+HEADER,sizeof boxes);memcpy(markers,p+HEADER+sizeof boxes,sizeof markers);
        for(unsigned i=0;i<4;i++)spread[i]=TlkDataGet16(p+at+i*2);initialization[0]=TlkDataGet32(p+at+8);initialization[1]=TlkDataGet32(p+at+12);ready=1;}
    return 1;
}
int TlkBePreparedBodyBounds(unsigned descriptor,unsigned pose,unsigned side,unsigned*n,unsigned*m){
    if(!ready||!n||!m||side>3)return 0;
    for(unsigned i=0;i<BOXES;i++)if(TlkDataGet32(boxes[i])==descriptor&&TlkDataGet32(boxes[i]+4)==pose){
        *n=TlkDataGet16(boxes[i]+8+side*2);*m=TlkDataGet16(boxes[i]+16+side*2);return 1;}
    return 0;
}
int TlkBePreparedEmitterMarker(unsigned cell,unsigned live,unsigned native,unsigned*md){
    if(!ready||!md)return 0;
    for(unsigned i=0;i<MARKERS;i++)if(TlkDataGet32(markers[i])==cell&&TlkDataGet16(markers[i]+4)==live&&markers[i][6]==native){*md=markers[i][7];return 1;}
    return 0;
}

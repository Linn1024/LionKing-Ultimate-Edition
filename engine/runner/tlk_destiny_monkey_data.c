#include "tlk_destiny_monkey_data.h"
#include "tlk_data_record.h"
#include "tlk_md_sprites.h"
#include <string.h>

enum { HEADER=64, PAYLOAD=TLK_MONKEY_STREAMS*TLK_MONKEY_STREAM_STRIDE,
       RECORD=HEADER+PAYLOAD };
static uint8_t streams[PAYLOAD];
static uint16_t lengths[TLK_MONKEY_STREAMS];
static uint32_t parameters[6];
static int ready;
static unsigned be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static unsigned be32(const uint8_t *p){return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3];}
static unsigned le24(const uint8_t *p){return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16;}
static void put24(uint8_t *p,unsigned v){p[0]=v;p[1]=v>>8;p[2]=v>>16;}
static unsigned base(unsigned i){return TLK_MONKEY_STREAM_BASE+i*TLK_MONKEY_STREAM_STRIDE;}

/* Seven wind-up and five release drawings, reviewed against both source
 * animation sequences and actual loaded SNES RAM artwork (research2564).
 * The earlier artwork catalog omitted this action. These are pose identities,
 * not pixel data, and do not imply that a renderer imports these MD drawings. */
static const uint32_t shooting_poses[12][2]={
 {0xc1eea7,0x13d63c},{0xc1eeda,0x13d674},{0xc1ef11,0x13d6bc},
 {0xc1ef48,0x13d704},{0xc1ef7f,0x13d74c},{0xc1efb6,0x13d794},
 {0xc1eff9,0x13d7cc},{0xc1f034,0x13d824},{0xc1f06f,0x13d87c},
 {0xc1f0b2,0x13d8d4},{0xc1f0ed,0x13d92c},{0xc1f12c,0x13d964}};
static unsigned native_pose(unsigned md){
    for(unsigned i=0;i<12;i++)if(shooting_poses[i][1]==md)return shooting_poses[i][0];
    return TlkMdSpritesNativePose(md);
}
void TlkDestinyMonkeyDataClear(void){ready=0;memset(streams,0,sizeof streams);memset(lengths,0,sizeof lengths);memset(parameters,0,sizeof parameters);}
int TlkDestinyMonkeyDataReady(void){return ready;}
size_t TlkDestinyMonkeyDataRecordSize(void){return ready?RECORD:0;}
unsigned TlkDestinyMonkeyStream(unsigned i){return ready && i<TLK_MONKEY_STREAMS?base(i):0;}
unsigned TlkDestinyMonkeyParameter(unsigned i){return ready && i<6?parameters[i]:0;}
int TlkDestinyMonkeyByte(unsigned at,unsigned *value){
    if(!ready || !value || at<TLK_MONKEY_STREAM_BASE)return 0;
    unsigned offset=at-TLK_MONKEY_STREAM_BASE,i=offset/TLK_MONKEY_STREAM_STRIDE;
    if(i>=TLK_MONKEY_STREAMS || offset%TLK_MONKEY_STREAM_STRIDE>=lengths[i])return 0;
    *value=streams[offset];return 1;
}

static int valid_primary(const uint8_t *p,unsigned n,unsigned start){
    uint8_t boundary[TLK_MONKEY_STREAM_STRIDE]={0};unsigned at=0;
    if(!n || n>TLK_MONKEY_STREAM_STRIDE)return 0;
    while(at<n){
        boundary[at]=1;unsigned op=p[at],size=op<128 || op==255?4:op==250?2:op==253?1:0;
        if(!size || size>n-at)return 0;
        if(op<128){unsigned pose=le24(p+at+1);if(pose<0xc1e5cc || pose>0xc1f12c)return 0;}
        if(op==250 && (p[at+1]<1 || p[at+1]>3))return 0;
        at+=size;
    }
    for(at=0;at<n;){unsigned op=p[at],size=op<128 || op==255?4:op==250?2:1;
        if(op==255){unsigned target=le24(p+at+1);if(target<start || target>=start+n || !boundary[target-start])return 0;}
        at+=size;
    }
    return n>=4 && p[n-4]==255;
}
static int valid(const uint8_t *p,size_t n){
    if(!p || n!=RECORD || memcmp(p,"TLKDMK01",8) || TlkDataGet32(p+8)!=RECORD || TlkDataGet32(p+12)!=1)return 0;
    /* The reviewed source pair has these values; reject stale/corrupt records
     * before they can affect any actor or animation cursor. */
    static const unsigned expected[6]={100,100,50,94,33,0x50000};
    for(unsigned i=0;i<6;i++)if(TlkDataGet32(p+28+i*4)!=expected[i])return 0;
    for(unsigned i=52;i<HEADER;i++)if(p[i])return 0;
    for(unsigned i=0;i<TLK_MONKEY_STREAMS;i++){
        unsigned len=TlkDataGet16(p+16+i*2);const uint8_t *s=p+HEADER+i*TLK_MONKEY_STREAM_STRIDE;
        if(len>TLK_MONKEY_STREAM_STRIDE)return 0;
        if(i<TLK_MONKEY_AUX){if(!valid_primary(s,len,base(i)))return 0;}
        else if(len!=10 || s[0]!=48 || s[1] || s[2] || s[3]!=176 || s[4]!=2 || s[5] || s[6]!=255 || le24(s+7)!=base(i)+3)return 0;
        for(unsigned j=len;j<TLK_MONKEY_STREAM_STRIDE;j++)if(s[j])return 0;
    }
    return 1;
}
int TlkDestinyMonkeyDataWrite(uint8_t *p,size_t n){
    if(!ready || !p || n!=RECORD)return 0;memset(p,0,n);memcpy(p,"TLKDMK01",8);
    TlkDataPut32(p+8,RECORD);TlkDataPut32(p+12,1);
    for(unsigned i=0;i<TLK_MONKEY_STREAMS;i++)TlkDataPut16(p+16+i*2,lengths[i]);
    for(unsigned i=0;i<6;i++)TlkDataPut32(p+28+i*4,parameters[i]);
    memcpy(p+HEADER,streams,sizeof streams);return valid(p,n);
}
int TlkDestinyMonkeyDataRead(const uint8_t *p,size_t n,int apply){
    if(!valid(p,n))return 0;
    if(apply){memcpy(streams,p+HEADER,sizeof streams);for(unsigned i=0;i<TLK_MONKEY_STREAMS;i++)lengths[i]=TlkDataGet16(p+16+i*2);for(unsigned i=0;i<6;i++)parameters[i]=TlkDataGet32(p+28+i*4);ready=1;}
    return 1;
}
static int translate(const uint8_t *m,unsigned begin,unsigned end,unsigned index){
    uint16_t offsets[256];unsigned reloc_at[64],reloc_target[64],relocs=0,at=begin,n=0;
    if(end<=begin || end-begin>256 || index>=TLK_MONKEY_AUX)return 0;
    for(unsigned i=0;i<256;i++)offsets[i]=65535;
    uint8_t *out=streams+index*TLK_MONKEY_STREAM_STRIDE;
    while(at<end){
        offsets[at-begin]=n;unsigned op=m[at],size=op<128 || (op==255 && m[at+1]!=255)?4:2;
        if(size>end-at || n+4>TLK_MONKEY_STREAM_STRIDE)return 0;
        if(op<128){unsigned pose=native_pose(be32(m+at)&0xffffff);if(!pose)return 0;out[n++]=op;put24(out+n,pose);n+=3;}
        else if(op==253){out[n++]=250;out[n++]=m[at+1];}
        else if(op==255 && m[at+1]==255)out[n++]=253;
        else if(op==255){if(relocs==64)return 0;out[n++]=255;reloc_at[relocs]=n;reloc_target[relocs++]=be32(m+at)&0xffffff;n+=3;}
        else return 0;
        at+=size;
    }
    for(unsigned i=0;i<relocs;i++){
        unsigned target=reloc_target[i];if(target<begin || target>=end || offsets[target-begin]==65535)return 0;
        put24(out+reloc_at[i],base(index)+offsets[target-begin]);
    }
    lengths[index]=n;return valid_primary(out,n,base(index));
}
int TlkDestinyMonkeyDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    TlkDestinyMonkeyDataClear();
    static const uint8_t native_descriptor[]={0x7e,0xcd,0xc4,0x2a,0,0,0xcc,0xe5,0xc1,0x89,0x85,0xc5};
    static const uint8_t md_descriptor[]={0,0x1a,0xab,0xf6,0,0,0,0x0d,0x19,0xfc,0,0x1a,0xab,0xf6};
    static const uint8_t md_aux[]={48,0,0,0,176,2,0,0,255,0x11,0x24,0xae};
    if(!s || !m || sn!=0x300000 || mn!=0x300000 || memcmp(s+0x586d8,native_descriptor,sizeof native_descriptor) || memcmp(m+0x112330,md_descriptor,sizeof md_descriptor) || memcmp(m+0x1124aa,md_aux,sizeof md_aux))return 0;
    static const unsigned ranges[5][2]={{0x112412,0x11241a},{0x11241a,0x112456},{0x112456,0x1124aa},{0x1124da,0x1124fc},{0x1124b6,0x1124da}};
    for(unsigned i=0;i<5;i++)if(!translate(m,ranges[i][0],ranges[i][1],i)){TlkDestinyMonkeyDataClear();return 0;}
    uint8_t *aux=streams+TLK_MONKEY_AUX*TLK_MONKEY_STREAM_STRIDE;
    aux[0]=m[0x1124aa];aux[1]=m[0x1124ab];aux[2]=m[0x1124ad];aux[3]=m[0x1124ae];aux[4]=m[0x1124af];aux[5]=m[0x1124b1];aux[6]=255;put24(aux+7,base(TLK_MONKEY_AUX)+3);lengths[TLK_MONKEY_AUX]=10;
    static const unsigned operands[5]={0x1aac10,0x1aaee6,0x1aafb6,0x1aae4a,0x1aaf44};
    for(unsigned i=0;i<5;i++){if(be16(m+operands[i])!=0x3f3c){TlkDestinyMonkeyDataClear();return 0;}parameters[i]=be16(m+operands[i]+2);}
    if(be16(m+0x1aae82)!=0x223c){TlkDestinyMonkeyDataClear();return 0;}parameters[5]=be32(m+0x1aae84);
    ready=1;uint8_t record[RECORD];if(!TlkDestinyMonkeyDataWrite(record,sizeof record)){TlkDestinyMonkeyDataClear();return 0;}return 1;
}

#include "tlk_start_data.h"
#include "tlk_data_record.h"
#include <string.h>
static unsigned native_position[2],md_position[2];
static unsigned md_entry_seed;
static unsigned bonus_native[3],bonus_md[3];
static unsigned cant_wait_native[2],cant_wait_md[2];
static unsigned graveyard_native[2],graveyard_md[2];
static unsigned graveyard_input_delay;
static unsigned retry_input_delay;
static unsigned later_native[6][2],later_md[6][2];
enum { RECORD_BYTES=96 };
static int ready;
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]<<8|p[1]; }
size_t TlkStartDataRecordSize(void) {return ready?RECORD_BYTES:0;}
int TlkStartDataWrite(uint8_t *data,size_t size) {
    if(!ready || !data || size!=RECORD_BYTES)return 0;
    for(unsigned i=0;i<2;i++){TlkDataPut16(data+i*2,native_position[i]);TlkDataPut16(data+4+i*2,md_position[i]);}
    TlkDataPut32(data+8,md_entry_seed);
    for(unsigned i=0;i<3;i++){TlkDataPut16(data+12+i*2,bonus_native[i]);TlkDataPut16(data+18+i*2,bonus_md[i]);}
    for(unsigned i=0;i<2;i++){TlkDataPut16(data+24+i*2,cant_wait_native[i]);TlkDataPut16(data+28+i*2,cant_wait_md[i]);}
    for(unsigned i=0;i<2;i++){TlkDataPut16(data+32+i*2,graveyard_native[i]);TlkDataPut16(data+36+i*2,graveyard_md[i]);}
    for(unsigned i=0;i<6;i++)for(unsigned axis=0;axis<2;axis++){
        TlkDataPut16(data+44+i*8+axis*2,later_native[i][axis]);
        TlkDataPut16(data+48+i*8+axis*2,later_md[i][axis]);
    }
    TlkDataPut16(data+40,0);TlkDataPut16(data+42,graveyard_input_delay);
    TlkDataPut16(data+92,0);TlkDataPut16(data+94,retry_input_delay);
    return 1;
}
int TlkStartDataRead(const uint8_t *data,size_t size,int apply) {
    if(!data || size!=RECORD_BYTES || TlkDataGet32(data+8)>0xffffff)return 0;
    unsigned n[2],m[2];
    for(unsigned i=0;i<2;i++){n[i]=TlkDataGet16(data+i*2);m[i]=TlkDataGet16(data+4+i*2);if(n[i]>=(i?1280:1600) || m[i]>=(i?1280:1600))return 0;}
    unsigned bn[3],bm[3];
    for(unsigned i=0;i<3;i++){bn[i]=TlkDataGet16(data+12+i*2);bm[i]=TlkDataGet16(data+18+i*2);if(bn[i]>1024 || bm[i]>1024)return 0;}
    if(bn[0]>=bn[2] || bm[0]>=bm[2] || bn[1]>=224 || bm[1]>=224 || bn[2]<32 || bm[2]<32)return 0;
    unsigned cn[2],cm[2];
    for(unsigned i=0;i<2;i++){cn[i]=TlkDataGet16(data+24+i*2);cm[i]=TlkDataGet16(data+28+i*2);if(cn[i]>=4096 || cm[i]>=4096)return 0;}
    unsigned gn[2],gm[2];for(unsigned i=0;i<2;i++){gn[i]=TlkDataGet16(data+32+i*2);gm[i]=TlkDataGet16(data+36+i*2);}
    if(gn[0]!=1008 || gn[1]!=336 || gm[0]!=981 || gm[1])return 0;
    if(TlkDataGet16(data+40) || TlkDataGet16(data+42)!=100)return 0;
    if(TlkDataGet16(data+92) || TlkDataGet16(data+94)!=3)return 0;
    for(unsigned i=0;i<6;i++)for(unsigned axis=0;axis<2;axis++){
        if(TlkDataGet16(data+44+i*8+axis*2)>=(axis?4096:8192) ||
           TlkDataGet16(data+48+i*8+axis*2)>=(axis?4096:8192))return 0;
    }
    if(apply){
        retry_input_delay=TlkDataGet16(data+94);
        for(unsigned i=0;i<6;i++)for(unsigned axis=0;axis<2;axis++){
            later_native[i][axis]=TlkDataGet16(data+44+i*8+axis*2);
            later_md[i][axis]=TlkDataGet16(data+48+i*8+axis*2);
        }
        graveyard_input_delay=TlkDataGet16(data+42);for(unsigned i=0;i<2;i++){graveyard_native[i]=gn[i];graveyard_md[i]=gm[i];}for(unsigned i=0;i<2;i++){native_position[i]=n[i];md_position[i]=m[i];cant_wait_native[i]=cn[i];cant_wait_md[i]=cm[i];}for(unsigned i=0;i<3;i++){bonus_native[i]=bn[i];bonus_md[i]=bm[i];}md_entry_seed=TlkDataGet32(data+8);ready=1;}return 1;
}
void TlkStartDataClear(void) { ready=0; }
int TlkStartDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    ready=0;
    if (!s || !m || sn!=0x300000 || mn!=0x300000) return 0;
    const uint8_t *sr=s+0x387,*mr=m+0x1cfdb4;
    if (le16(sr+18)!=200 || le16(sr+20)!=80 || be16(mr+12)!=200 || be16(mr+14)!=80) return 0;
    /* Original default-position loads: native C0867B/C08687 and MD1D017A
     * (stream cursor at descriptor+36; direct loader1D6E72 agrees).
     * The former writes checkpoint defaults as well as the new player. */
    if (s[0x867b]!=0xb7 || s[0x867c]!=0xdf || s[0x8687]!=0xb7 || s[0x8688]!=0xdf ||
        m[0x1d6e72]!=0x20 || m[0x1d6e73]!=0xac || be16(m+0x1d6e74)!=36 ||
        m[0x1d017a]!=0x20 || m[0x1d017b]!=0x9c) return 0;
    for (unsigned axis=0;axis<2;axis++) {
        unsigned n=le16(sr+22+axis*2),x=be16(mr+36+axis*2);
        unsigned limit=axis?1280:1600;
        if (n>=limit || x>=limit) return 0;
        native_position[axis]=n;md_position[axis]=x;
    }
    /* Installer-only decoding of the original normal scene-entry assignment.
     * Runtime imports this operand with the other scene-entry values. */
    if(memcmp(s+0x7970,"\x9e\x00\x00\xca\xe0\xff\x02\xd0",8) || s[0x7979]!=0x28)return 0;
    md_entry_seed=0;
    for(unsigned i=0;i<3;i++) {
        const uint8_t *p=m + 0x1d77de + i*8;
        if(p[0]!=0x13 || p[1]!=0xfc || p[2] || p[4]!=0xff || p[5]!=0xff || p[6]!=0x81 || p[7]!=0xad+i)return 0;
        md_entry_seed=md_entry_seed<<8|p[3];
    }
    /* Same original default-position loaders, actual bonus scene10 records.
     * Six native right-edge loads correspond to MD width320 minus margin32. */
    for(unsigned i=0;i<2;i++){bonus_native[i]=le16(s+0x5dd+22+i*2);bonus_md[i]=be16(m+0x1cfdb4+10*48+36+i*2);}
    static const unsigned sites[]={0x53be7,0x53c57,0x542c6,0x542fe,0x54824,0x54831};
    bonus_native[2]=le16(s+sites[0]+1);
    for(unsigned i=0;i<6;i++)if(s[sites[i]]!=0xa9 || le16(s+sites[i]+1)!=bonus_native[2])return 0;
    if(memcmp(m+0x1b3e9e,"\x36\x3c\x01\x40\x04\x43\x00\x20",8))return 0;
    bonus_md[2]=be16(m+0x1b3ea0)-be16(m+0x1b3ea4);
    if(bonus_native[0]!=128 || bonus_native[1]!=218 || bonus_native[2]!=224 || bonus_md[0]!=100 || bonus_md[1]!=214 || bonus_md[2]!=288)return 0;
    for(unsigned i=0;i<2;i++) {
        cant_wait_native[i]=le16(s+0x3b9+22+i*2);
        cant_wait_md[i]=be16(m+0x1cfdb4+48+36+i*2);
        if(cant_wait_native[i]>=4096 || cant_wait_md[i]>=4096)return 0;
    }
    for(unsigned i=0;i<2;i++){
        graveyard_native[i]=le16(s+0x3eb+22+i*2);graveyard_md[i]=be16(m+0x1cfdb4+2*48+36+i*2);
    }
    if(graveyard_native[0]!=1008 || graveyard_native[1]!=336 || graveyard_md[0]!=981 || graveyard_md[1])return 0;
    /* MD normal Graveyard (level3 in its one-based scene table), with no
     * checkpoint, replaces its ordinary3-update delay by100 after loading. */
    if(memcmp(m+0x1d7186,"\x0c\x79\x00\x03\xff\xff\xcc\xce\x66\x10\x4a\xb9\xff\xff\xcc\xd6",16) ||
       memcmp(m+0x1d7198,"\x33\xfc\x00\x64\xff\xff\xe9\xba",8))return 0;
    graveyard_input_delay=be16(m+0x1d719a);
    /* The retry coordinator assigns this after rebuilding/fading the player.
     * Normal level entry uses a different path and does not assign it. */
    if(memcmp(m+0x1d717e,"\x33\xfc\x00\x03\xff\xff\xe9\xba",8) ||
       memcmp(s+0x8859,"\xa9\x00\x00\x8f\xa2\xff\x7f",7))return 0;
    retry_input_delay=be16(m+0x1d7180);
    /* Actual normal-entry assignments1D017A/1D6E72 and the ready-before-seed
     * original actor positions agree for levels4..9. Stampede uses a different
     * player loader/coordinate system and is deliberately excluded. */
    for(unsigned i=0;i<6;i++){
        unsigned level=i+4;const uint8_t *ns=s+0x387+level*50,*ms=m+0x1cfdb4+level*48;
        unsigned width=le16(ns+18),rows=le16(ns+20);
        if(!width || (width&1) || !rows || width!=be16(ms+12) || rows!=be16(ms+14))return 0;
        for(unsigned axis=0;axis<2;axis++){
            unsigned n=le16(ns+22+axis*2),v=be16(ms+36+axis*2),limit=axis?rows*16:width*8;
            if(n>=limit || v>=limit)return 0;
            later_native[i][axis]=n;later_md[i][axis]=v;
        }
    }
    ready=1;return 1;
}
int TlkStartDataValue(unsigned axis,unsigned *native,unsigned *external) {
    if (!ready || axis>1 || !native || !external) return 0;
    *native=native_position[axis];*external=md_position[axis];return 1;
}
int TlkStartDataEntrySeed(unsigned *seed) {
    if(!ready || !seed)return 0;*seed=md_entry_seed;return 1;
}
int TlkStartDataBonusValue(unsigned axis,unsigned *native,unsigned *external){
    if(!ready || axis>2 || !native || !external)return 0;*native=bonus_native[axis];*external=bonus_md[axis];return 1;
}
int TlkStartDataCantWaitValue(unsigned axis,unsigned *native,unsigned *external){
    if(!ready || axis>1 || !native || !external)return 0;
    *native=cant_wait_native[axis];*external=cant_wait_md[axis];return 1;
}

int TlkStartDataGraveyardValue(unsigned axis,unsigned *native,unsigned *external){
    if(!ready || axis>1 || !native || !external)return 0;
    *native=graveyard_native[axis];*external=graveyard_md[axis];return 1;
}

int TlkStartDataGraveyardInputDelay(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;*native=0;*external=graveyard_input_delay;return 1;
}
int TlkStartDataRetryInputDelay(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;*native=0;*external=retry_input_delay;return 1;
}

int TlkStartDataLaterValue(unsigned level,unsigned axis,unsigned *native,unsigned *external){
    if(!ready || level<4 || level>9 || axis>1 || !native || !external)return 0;
    *native=later_native[level-4][axis];*external=later_md[level-4][axis];return 1;
}

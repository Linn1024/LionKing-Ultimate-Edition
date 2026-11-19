/* Hunt worlds share geometry after MD's extra top row is removed.
 * Prepare actual entry operands and the nine Hunt1 marker differences only. */
#include "tlk_hunt_data.h"
#include "tlk_data_record.h"
#include "tlk_md_assets.h"
#include <stdlib.h>
#include <string.h>
enum { HEADER=136,DELTAS=9,RULES=HEADER+DELTAS*8,BYTES=RULES+24 };
static const unsigned scenes[]={0x60f,0x641,0x673},widths[]={80,200,120},rows[]={97,26,41};
static uint8_t *record;
static unsigned be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static unsigned be32(const uint8_t *p){return be16(p)<<16|be16(p+2);}
static unsigned le24(const uint8_t *p){return (TlkDataGet16(p)|(unsigned)p[2]<<16)&0x3fffff;}
void TlkHuntDataClear(void){free(record);record=NULL;}
int TlkHuntDataOrigin(unsigned level,unsigned *md_y_offset){
    if(!record || level<11 || level>13 || !md_y_offset)return 0;
    *md_y_offset=TlkDataGet32(record+16+(level-11)*40+24);return 1;
}
size_t TlkHuntDataSize(void){return record?BYTES:0;}
int TlkHuntDataWrite(uint8_t *p,size_t n){if(!record || !p || n!=BYTES)return 0;memcpy(p,record,n);return 1;}
int TlkHuntDataRead(const uint8_t *p,size_t n,int apply){
    if(!p || n!=BYTES || memcmp(p,"TLKHNT03",8) || TlkDataGet32(p+8)!=3 || TlkDataGet32(p+12)!=BYTES)return 0;
    for(unsigned i=0;i<3;i++){
        const uint8_t *q=p+16+i*40;
        if(TlkDataGet32(q)!=0xc00000+scenes[i] || TlkDataGet32(q+4)!=widths[i] ||
           TlkDataGet32(q+8)!=rows[i] || TlkDataGet32(q+12)!=rows[i]+1 || TlkDataGet32(q+24)!=16 ||
           TlkDataGet32(q+28)!=(i?0:DELTAS) || TlkDataGet32(q+32)!=(i?RULES:HEADER) ||
           TlkDataGet32(q+36)!=0x1cfdb4+(i+11)*48)return 0;
        if(TlkDataGet16(q+16)>=widths[i]*8 || TlkDataGet16(q+18)>=rows[i]*16 ||
           TlkDataGet16(q+20)>=widths[i]*8 || TlkDataGet16(q+22)<16 || TlkDataGet16(q+22)>=(rows[i]+1)*16)return 0;
    }
    unsigned previous=0;
    for(unsigned i=0;i<DELTAS;i++){
        const uint8_t *q=p+HEADER+i*8;unsigned cell=TlkDataGet32(q);
        if(cell>=3880 || (i && cell<=previous) || q[6]==q[7])return 0;previous=cell;
    }
    for(unsigned i=0;i<3;i++){
        unsigned native=TlkDataGet32(p+RULES+i*8),md=TlkDataGet32(p+RULES+i*8+4);
        if(native!=(i?60u:40u) || md!=(i==0?30u:i==1?0u:50u))return 0;
    }
    if(apply){uint8_t *copy=malloc(n);if(!copy)return 0;memcpy(copy,p,n);TlkHuntDataClear();record=copy;}return 1;
}
int TlkHuntDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    TlkHuntDataClear();if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    uint8_t data[BYTES];memset(data,0,sizeof data);memcpy(data,"TLKHNT03",8);TlkDataPut32(data+8,3);TlkDataPut32(data+12,BYTES);
    /* Original MD decrements its zero initial subcounter before testing;
     * reload50 therefore gives51 controller updates per displayed second. */
    static const unsigned native_at[]={0x58168,0x58170,0x581c8};
    if(be16(m+0x8eb34)!=0x317c || be16(m+0x8eb38)!=0x2c ||
       memcmp(m+0x8eafe,"\x20\x79\xff\xff\x81\xc4\x53\x68\x00\x2e\x6a\x16",12) ||
       be16(m+0x8eb0a)!=0x317c || be16(m+0x8eb0e)!=0x2e)return 0;
    for(unsigned i=0;i<3;i++){
        unsigned at=native_at[i];if(s[at]!=0xa9 || s[at+3]!=0xa0 || s[at+4]!=(i?0x2c:0x2e) || s[at+5] || s[at+6]!=0x91 || s[at+7])return 0;
        TlkDataPut32(data+RULES+i*8,TlkDataGet16(s+at+1));
        TlkDataPut32(data+RULES+i*8+4,i==0?be16(m+0x8eb36):i==1?0:be16(m+0x8eb0c));
    }
    int ok=1;unsigned changes=0;
    for(unsigned i=0;i<3 && ok;i++){
        const uint8_t *sr=s+scenes[i],*mr=m+0x1cfdb4+(i+11)*48;
        unsigned count=widths[i]/2*rows[i],md_count=count+widths[i]/2;
        if(TlkDataGet16(sr+18)!=widths[i] || TlkDataGet16(sr+20)!=rows[i] ||
           be16(mr+12)!=widths[i] || be16(mr+14)!=rows[i]+1){ok=0;break;}
        uint8_t *sm=malloc(count*2),*mm=malloc(md_count*2),*sc=malloc(65536);size_t a=0,b=0,c=0;
        ok=sm && mm && sc && TlkMdDecompress(s,sn,le24(sr+9),sm,count*2,&a) && a==count*2 &&
            TlkMdDecompress(m,mn,be32(mr+16),mm,md_count*2,&b) && b==md_count*2 &&
            TlkMdDecompress(s,sn,le24(sr),sc,65536,&c);
        uint8_t *q=data+16+i*40;TlkDataPut32(q,0xc00000+scenes[i]);TlkDataPut32(q+4,widths[i]);
        TlkDataPut32(q+8,rows[i]);TlkDataPut32(q+12,rows[i]+1);
        for(unsigned axis=0;axis<2;axis++){TlkDataPut16(q+16+axis*2,TlkDataGet16(sr+22+axis*2));TlkDataPut16(q+20+axis*2,be16(mr+36+axis*2));}
        TlkDataPut32(q+24,16);TlkDataPut32(q+28,i?0:DELTAS);TlkDataPut32(q+32,i?RULES:HEADER);TlkDataPut32(q+36,0x1cfdb4+(i+11)*48);
        unsigned sh=le24(sr+3),mc=be32(mr+4),mh=be32(mr+8);
        for(unsigned cell=0;cell<count && ok;cell++){
            unsigned sw=TlkDataGet16(sm+cell*2),mw=be16(mm+cell*2+widths[i]),so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
            if(so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
            unsigned sp=TlkDataGet16(sc+so),mp=m[mc+mo]*16u;
            if(sh>=sn || sp+16>sn-sh || mh>=mn || mp+16>mn-mh || sc[so+2]!=m[mc+mo+2]){ok=0;break;}
            /* Scene normalization is proven across every original floor cell,
             * not guessed from dimensions or from decoded foreground art. */
            for(unsigned x=0;x<16;x++)if((s[sh+sp+x]&31)!=(m[mh+mp+x]&31))ok=0;
            if(sc[so+3]!=m[mc+mo+3]){
                if(i || changes>=DELTAS){ok=0;break;}
                uint8_t *d=data+HEADER+changes++*8;TlkDataPut32(d,cell);TlkDataPut16(d+4,sw);d[6]=sc[so+3];d[7]=m[mc+mo+3];
            }
        }
        free(sm);free(mm);free(sc);
    }
    return ok && changes==DELTAS && TlkHuntDataRead(data,BYTES,1);
}
int TlkHuntDataEntry(unsigned level,unsigned axis,unsigned *native,unsigned *md){
    if(!record || level<11 || level>13 || axis>1 || !native || !md)return 0;
    const uint8_t *q=record+16+(level-11)*40;
    *native=TlkDataGet16(q+16+axis*2);*md=TlkDataGet16(q+20+axis*2)-(axis?TlkDataGet32(q+24):0);return 1;
}
int TlkHuntDataMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!record || !md)return 0;
    for(unsigned i=0;i<DELTAS;i++){
        const uint8_t *q=record+HEADER+i*8;
        if(TlkDataGet32(q)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(q+4)&0xfff8) || native!=q[6])return 0;
        *md=q[7];return 1;
    }
    return 0;
}

int TlkHuntDataTimer(unsigned field,unsigned *native,unsigned *md){
    if(!record || field>=3 || !native || !md)return 0;
    *native=TlkDataGet32(record+RULES+field*8);*md=TlkDataGet32(record+RULES+field*8+4);return 1;
}

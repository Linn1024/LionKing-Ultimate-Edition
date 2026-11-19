#include "tlk_cant_wait_data.h"
#include "tlk_data_record.h"
#include <string.h>
#include "tlk_cw_terrain_data.h"
#include "tlk_cw_monkey_grip_map.h"
enum { GRIPS=sizeof cw_monkey_grip_map/sizeof *cw_monkey_grip_map,EXIT_SIZE=16,GRIP_SIZE=16+GRIPS*16 };
static uint16_t native_grips[GRIPS][2],md_grips[GRIPS][2];
static unsigned native_range,md_range;
static uint16_t native_exit,md_exit;
static unsigned native_hippo,md_hippo;
static unsigned native_giraffe,md_giraffe;
static unsigned native_ostrich_delay,md_ostrich_delay;
enum { NATIVE_EVENTS=19,MD_EVENTS=18,FIRST_EVENTS=10,RECORD_SIZE=28+4*(NATIVE_EVENTS+MD_EVENTS+FIRST_EVENTS) };
static uint16_t native_ride[3],md_ride[3],native_events[NATIVE_EVENTS][2],md_events[MD_EVENTS][2];
static uint16_t first_events[FIRST_EVENTS][2];
static int ready;
void TlkCantWaitDataClear(void){ready=0;TlkCwTerrainDataClear();}
size_t TlkCantWaitDataRecordSize(void){return ready?RECORD_SIZE+TlkCwTerrainDataSize()+4+GRIP_SIZE+EXIT_SIZE:0;}
int TlkCantWaitExitBoundary(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;
    *native=native_exit;*external=md_exit;return 1;
}
int TlkCantWaitMonkeyGrip(unsigned pose,unsigned axis,unsigned *native,unsigned *external){
    if(!ready || axis>1 || !native || !external)return 0;
    for(unsigned i=0;i<GRIPS;i++)if(cw_monkey_grip_map[i].native==pose){
        *native=native_grips[i][axis];*external=md_grips[i][axis];return 1;}
    return 0;
}
int TlkCantWaitRideValue(unsigned i,unsigned *native,unsigned *external){
    if(!ready || i>=3 || !native || !external)return 0;
    *native=native_ride[i];*external=md_ride[i];return 1;
}
int TlkCantWaitRideEvent(unsigned cursor,unsigned *distance,unsigned *flags){
    if(ready && distance && flags && cursor>=0xc4e1b9 && cursor<0xc4e1b9+FIRST_EVENTS*4 && !((cursor-0xc4e1b9)&3)){
        unsigned i=(cursor-0xc4e1b9)/4;*distance=first_events[i][0];*flags=first_events[i][1];return 1;
    }
    if(!ready || !distance || !flags || cursor<0xc4e1f1 ||
       cursor>=0xc4e1f1+MD_EVENTS*4 || ((cursor-0xc4e1f1)&3))return 0;
    unsigned i=(cursor-0xc4e1f1)/4;*distance=md_events[i][0];*flags=md_events[i][1];return 1;
}
int TlkCantWaitOstrichDelay(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;
    *native=native_ostrich_delay;*external=md_ostrich_delay;return 1;
}
int TlkCantWaitGiraffeOffset(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;
    *native=native_giraffe;*external=md_giraffe;return 1;
}
int TlkCantWaitHippoOffset(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;
    *native=native_hippo;*external=md_hippo;return 1;
}
int TlkCantWaitRoarRange(unsigned *native,unsigned *external){
    if(!ready || !native || !external)return 0;
    *native=native_range;*external=md_range;return 1;
}
int TlkCantWaitDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    ready=0;TlkCwTerrainDataClear();
    if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    /* Original per-scene completion comparisons, not a fitted TAS threshold. */
    if(s[0xd1c3]!=0xc9 || s[0xd1c6]!=0x90 ||
       memcmp(m+0x1cad02,"\x20\x79\xff\xff\xcd\x46\x0c\x68",8) ||
       m[0x1cad0c] || m[0x1cad0d]!=8 || m[0x1cad0e]!=0x6d)return 0;
    native_exit=TlkDataGet16(s+0xd1c4);md_exit=(unsigned)m[0x1cad0a]<<8|m[0x1cad0b];
    if(native_exit!=6372 || md_exit!=6360)return 0;
    /* Both axes use the same absolute-distance bound in the original roar
     * decision, before the existing target-tag/turn/reaction state machine. */
    if(s[0x45684]!=0xc9 || s[0x45699]!=0xc9 || s[0x45687]!=0x10 || s[0x4569c]!=0x10 ||
       m[0x19dfb4]!=0x0c || m[0x19dfb5]!=0x40 || m[0x19dfd0]!=0x0c || m[0x19dfd1]!=0x40)return 0;
    unsigned n=TlkDataGet16(s+0x45685),v=(unsigned)m[0x19dfb6]<<8|m[0x19dfb7];
    if(n!=TlkDataGet16(s+0x4569a) || v!=((unsigned)m[0x19dfd2]<<8|m[0x19dfd3]) ||
       !n || n>256 || !v || v>256)return 0;
    /* Native flat giraffe platform always runs its field34 initializer.
     * MD descriptor0B8E36 already supplies action19E098; that action's
     * zero-action initialization branch is skipped. Thus no X addition.
     * Original actors1308 appear at2080/304; native appears at2086/304. */
    if(s[0x18f71]!=0x69 || TlkDataGet16(s+0x18f72)!=6 ||
       s[0x58d8d]!=0x39 || s[0x58d8e]!=0x8f || s[0x58d8f]!=0xc1 ||
       m[0xb8e4c]!=0 || m[0xb8e4d]!=0x19 || m[0xb8e4e]!=0xe0 || m[0xb8e4f]!=0x98 ||
       m[0x19e0a6]!=0x0c || m[0x19e0a7]!=0xa9 ||
       m[0x19e0aa] || m[0x19e0ab] || m[0x19e0ae]!=0x66)return 0;
    native_giraffe=TlkDataGet16(s+0x18f72);md_giraffe=0;
    /* Original jump/duck warning initial countdown. The following nine
     * phase delays, transition order and jump/duck controls agree; preserve
     * those native decisions rather than retiming individual obstacles. */
    if(s[0x439d0]!=0xa9 || s[0x439d3]!=0xa0 ||
       m[0x19eb26]!=0x33 || m[0x19eb27]!=0x7c || m[0x19eb2a]!=0 || m[0x19eb2b]!=0x2c)return 0;
    native_ostrich_delay=TlkDataGet16(s+0x439d1);
    md_ostrich_delay=(unsigned)m[0x19eb28]<<8|m[0x19eb29];
    if(!native_ostrich_delay || native_ostrich_delay>1024 || !md_ostrich_delay || md_ostrich_delay>1024)return 0;
    static const unsigned ns[]={0x4326a,0xbb93,0xb1dd},ms[]={0x19e520,0x923de,0x8b82a};
    static const unsigned opcodes[]={0xe9,0x69,0xa9};
    for(unsigned i=0;i<3;i++){
        if(s[ns[i]]!=opcodes[i])return 0;
        native_ride[i]=TlkDataGet16(s+ns[i]+1);
        md_ride[i]=(unsigned)m[ms[i]+2]<<8|m[ms[i]+3];
    }
    if(native_ride[0]!=256 || md_ride[0]!=320 || native_ride[1]!=320 || md_ride[1]!=380 ||
       native_ride[2]!=16 || md_ride[2]!=48)return 0;
    /* Second ride: C430FB selects C4E1F1; MD19E3D0 selects09243C.
     * First ride uses C4E1B9 /092404; its ten records already agree. */
    for(unsigned family=0;family<2;family++){
        unsigned count=family?MD_EVENTS:NATIVE_EVENTS,previous=0;
        for(unsigned i=0;i<count;i++){
            unsigned a=(family?0x9243c:0x4e1f1)+i*4;
            unsigned distance=family?((unsigned)m[a]<<8|m[a+1]):TlkDataGet16(s+a);
            unsigned flags=family?((unsigned)m[a+2]<<8|m[a+3]):TlkDataGet16(s+a+2);
            if(distance<previous || !distance || (i+1==count?flags!=65535:(!flags || (flags&~31u))))return 0;
            uint16_t (*events)[2]=family?md_events:native_events;
            events[i][0]=distance;events[i][1]=flags;previous=distance;
        }
    }
    for(unsigned i=0;i<FIRST_EVENTS;i++)for(unsigned component=0;component<2;component++){
        unsigned a=0x4e1b9+i*4+component*2,b=0x92404+i*4+component*2;
        unsigned value=TlkDataGet16(s+a),external=(unsigned)m[b]<<8|m[b+1];
        if(value!=external)return 0;first_events[i][component]=value;
    }
    /* Native hippo initializer adds12 before storing its animation base Y.
     * MD19F8DE stores the incoming marker Y directly; retain its animation
     * displacement and ordinary platform contact/launch decisions. */
    if(s[0x49323]!=0x69 || TlkDataGet16(s+0x49324)!=12 ||
       s[0x49326]!=0x91 || s[0x58ac7+13]!=0xf4 || s[0x58ac7+14]!=0x92 ||
       m[0x19f904]!=0x22 || m[0x19f905]!=0x79 ||
       m[0x19f90a]!=0x33 || m[0x19f90b]!=0x69 ||
       ((unsigned)m[0x19f90c]<<8|m[0x19f90d])!=10 ||
       ((unsigned)m[0x19f90e]<<8|m[0x19f90f])!=44 ||
       m[0x19f910]!=0x4e || m[0x19f911]!=0xb9)return 0;
    native_hippo=TlkDataGet16(s+0x49324);md_hippo=0;
    for(unsigned i=0;i<GRIPS;i++)for(unsigned axis=0;axis<2;axis++){
        unsigned a=(cw_monkey_grip_map[i].native&0x3fffff)+20+axis*2,b=cw_monkey_grip_map[i].md+20+axis*2;
        if(a>sn-2 || b>mn-2)return 0;
        native_grips[i][axis]=TlkDataGet16(s+a);md_grips[i][axis]=(unsigned)m[b]<<8|m[b+1];
        if((int16_t)native_grips[i][axis]<-256 || (int16_t)native_grips[i][axis]>256 ||
           (int16_t)md_grips[i][axis]<-256 || (int16_t)md_grips[i][axis]>256)return 0;
    }
    if(!TlkCwTerrainDataPrepare(s,sn,m,mn))return 0;
    native_range=n;md_range=v;ready=1;return 1;
}
int TlkCantWaitDataWrite(uint8_t *p,size_t size){
    if(!ready || !p || size!=RECORD_SIZE+TlkCwTerrainDataSize()+4+GRIP_SIZE+EXIT_SIZE)return 0;
    size-=EXIT_SIZE;
    uint8_t *exit=p+size;memcpy(exit,"TLKCWX01",8);TlkDataPut32(exit+8,native_exit);TlkDataPut32(exit+12,md_exit);
    TlkDataPut16(p,native_range);TlkDataPut16(p+2,md_range);
    TlkDataPut16(p+4,native_giraffe);TlkDataPut16(p+6,md_giraffe);
    TlkDataPut16(p+8,native_ostrich_delay);TlkDataPut16(p+10,md_ostrich_delay);
    for(unsigned i=0;i<3;i++){TlkDataPut16(p+12+i*4,native_ride[i]);TlkDataPut16(p+14+i*4,md_ride[i]);}
    TlkDataPut16(p+24,NATIVE_EVENTS);TlkDataPut16(p+26,MD_EVENTS);
    unsigned at=28;
    for(unsigned family=0;family<2;family++)for(unsigned i=0;i<(family?MD_EVENTS:NATIVE_EVENTS);i++){
        uint16_t (*events)[2]=family?md_events:native_events;
        TlkDataPut16(p+at,events[i][0]);TlkDataPut16(p+at+2,events[i][1]);at+=4;
    }
    for(unsigned i=0;i<FIRST_EVENTS;i++){TlkDataPut16(p+at,first_events[i][0]);TlkDataPut16(p+at+2,first_events[i][1]);at+=4;}
    size_t end=size-GRIP_SIZE;
    TlkDataPut16(p+end-4,native_hippo);TlkDataPut16(p+end-2,md_hippo);
    uint8_t *g=p+end;memcpy(g,"TLKGRP01",8);TlkDataPut32(g+8,GRIP_SIZE);TlkDataPut32(g+12,GRIPS);
    for(unsigned i=0;i<GRIPS;i++){
        uint8_t *v=g+16+i*16;TlkDataPut32(v,cw_monkey_grip_map[i].native);TlkDataPut32(v+4,cw_monkey_grip_map[i].md);
        for(unsigned axis=0;axis<2;axis++){TlkDataPut16(v+8+axis*2,native_grips[i][axis]);TlkDataPut16(v+12+axis*2,md_grips[i][axis]);}
    }
    return TlkCwTerrainDataWrite(p+at,end-at-4);
}
int TlkCantWaitDataRead(const uint8_t *p,size_t size,int apply){
    if(!p || size<EXIT_SIZE || memcmp(p+size-EXIT_SIZE,"TLKCWX01",8) ||
       TlkDataGet32(p+size-8)!=6372 || TlkDataGet32(p+size-4)!=6360)return 0;
    unsigned nx=TlkDataGet32(p+size-8),mx=TlkDataGet32(p+size-4);size-=EXIT_SIZE;
    if(!p || size<RECORD_SIZE+4+GRIP_SIZE || !TlkCwTerrainDataRead(p+RECORD_SIZE,size-RECORD_SIZE-4-GRIP_SIZE,0) ||
       TlkDataGet16(p+24)!=NATIVE_EVENTS || TlkDataGet16(p+26)!=MD_EVENTS)return 0;
    if(TlkDataGet16(p+size-GRIP_SIZE-4)!=12 || TlkDataGet16(p+size-GRIP_SIZE-2))return 0;
    const uint8_t *g=p+size-GRIP_SIZE;
    if(memcmp(g,"TLKGRP01",8) || TlkDataGet32(g+8)!=GRIP_SIZE || TlkDataGet32(g+12)!=GRIPS)return 0;
    for(unsigned i=0;i<GRIPS;i++){
        const uint8_t *v=g+16+i*16;
        if(TlkDataGet32(v)!=cw_monkey_grip_map[i].native || TlkDataGet32(v+4)!=cw_monkey_grip_map[i].md)return 0;
        for(unsigned j=0;j<4;j++){int value=(int16_t)TlkDataGet16(v+8+j*2);if(value<-256 || value>256)return 0;}
    }
    unsigned n=TlkDataGet16(p),m=TlkDataGet16(p+2);
    if(!n || n>256 || !m || m>256)return 0;
    unsigned ng=TlkDataGet16(p+4),mg=TlkDataGet16(p+6);
    if(ng!=6 || mg)return 0;
    unsigned nd=TlkDataGet16(p+8),md=TlkDataGet16(p+10);
    if(!nd || nd>1024 || !md || md>1024)return 0;
    for(unsigned i=0;i<6;i++){unsigned v=TlkDataGet16(p+12+i*2);if(!v || v>1024)return 0;}
    unsigned at=28;
    for(unsigned family=0;family<2;family++){
        unsigned count=family?MD_EVENTS:NATIVE_EVENTS,previous=0;
        for(unsigned i=0;i<count;i++){
            unsigned distance=TlkDataGet16(p+at),flags=TlkDataGet16(p+at+2);at+=4;
            if(distance<previous || !distance || (i+1==count?flags!=65535:(!flags || (flags&~31u))))return 0;
            previous=distance;
        }
    }
    unsigned first_at=at,previous=0;
    for(unsigned i=0;i<FIRST_EVENTS;i++){
        unsigned distance=TlkDataGet16(p+at),flags=TlkDataGet16(p+at+2);at+=4;
        if(!distance || distance<previous || (i+1==FIRST_EVENTS?flags!=65535:(!flags || (flags&~31u))))return 0;
        previous=distance;
    }
    if(apply){native_exit=nx;md_exit=mx;native_range=n;md_range=m;native_giraffe=ng;md_giraffe=mg;
        for(unsigned i=0;i<3;i++){native_ride[i]=TlkDataGet16(p+12+i*4);md_ride[i]=TlkDataGet16(p+14+i*4);}
        at=28;
        for(unsigned family=0;family<2;family++)for(unsigned i=0;i<(family?MD_EVENTS:NATIVE_EVENTS);i++){
            uint16_t (*events)[2]=family?md_events:native_events;
            events[i][0]=TlkDataGet16(p+at);events[i][1]=TlkDataGet16(p+at+2);at+=4;
        }
        for(unsigned i=0;i<FIRST_EVENTS;i++){first_events[i][0]=TlkDataGet16(p+first_at+i*4);first_events[i][1]=TlkDataGet16(p+first_at+i*4+2);}
        if(!TlkCwTerrainDataRead(p+RECORD_SIZE,size-RECORD_SIZE-4-GRIP_SIZE,1))return 0;
        native_hippo=TlkDataGet16(p+size-GRIP_SIZE-4);md_hippo=TlkDataGet16(p+size-GRIP_SIZE-2);
        for(unsigned i=0;i<GRIPS;i++)for(unsigned axis=0;axis<2;axis++){
            native_grips[i][axis]=TlkDataGet16(g+16+i*16+8+axis*2);
            md_grips[i][axis]=TlkDataGet16(g+16+i*16+12+axis*2);
        }
        native_ostrich_delay=nd;md_ostrich_delay=md;ready=1;}return 1;
}

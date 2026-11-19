#include "tlk_hitbox_data.h"
#include "pride_hitbox_map.h"
#include "tlk_data_record.h"
enum { COUNT=sizeof hitbox_map/sizeof hitbox_map[0] };
static uint16_t native_bounds[COUNT][4],md_bounds[COUNT][4];
static uint8_t valid[COUNT];
static int ready;
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]<<8|p[1]; }
size_t TlkHitboxDataPolicySize(void) {return 4+(size_t)COUNT*12;}
int TlkHitboxDataPolicyWrite(uint8_t *data,size_t size) {
    if(!data || size!=TlkHitboxDataPolicySize())return 0;
    TlkDataPut32(data,COUNT);
    for(unsigned n=0;n<COUNT;n++) {
        uint8_t *p=data+4+n*12;TlkDataPut32(p,hitbox_map[n].snes);
        TlkDataPut32(p+4,hitbox_map[n].md);TlkDataPut32(p+8,hitbox_map[n].role);
    }
    return 1;
}
size_t TlkHitboxDataRecordSize(void) {return ready?4+(size_t)COUNT*26:0;}
int TlkHitboxDataWrite(uint8_t *data,size_t size) {
    if(!ready || !data || size!=TlkHitboxDataRecordSize())return 0;TlkDataPut32(data,COUNT);
    for(unsigned n=0;n<COUNT;n++) {
        uint8_t *p=data+4+n*26;TlkDataPut32(p,hitbox_map[n].snes);TlkDataPut32(p+4,hitbox_map[n].md);p[8]=(uint8_t)hitbox_map[n].role;p[9]=valid[n];
        for(unsigned i=0;i<4;i++){TlkDataPut16(p+10+i*2,native_bounds[n][i]);TlkDataPut16(p+18+i*2,md_bounds[n][i]);}
    }return 1;
}
int TlkHitboxDataRead(const uint8_t *data,size_t size,int apply) {
    if(!data || size!=4+(size_t)COUNT*26 || TlkDataGet32(data)!=COUNT)return 0;unsigned enabled=0;
    for(unsigned n=0;n<COUNT;n++) {
        const uint8_t *p=data+4+n*26;
        if(TlkDataGet32(p)!=hitbox_map[n].snes || TlkDataGet32(p+4)!=hitbox_map[n].md || p[8]!=hitbox_map[n].role || p[9]>1)return 0;
        enabled+=p[9];if(!p[9])continue;
        for(unsigned side=0;side<2;side++) {
            int bounds[4];for(unsigned i=0;i<4;i++){bounds[i]=(int16_t)TlkDataGet16(p+10+side*8+i*2);if(bounds[i]<-256 || bounds[i]>256)return 0;}
            if(bounds[0]>bounds[2] || bounds[1]>bounds[3])return 0;
        }
    }
    if(!enabled)return 0;
    if(apply){for(unsigned n=0;n<COUNT;n++){const uint8_t *p=data+4+n*26;valid[n]=p[9];for(unsigned i=0;i<4;i++){native_bounds[n][i]=TlkDataGet16(p+10+i*2);md_bounds[n][i]=TlkDataGet16(p+18+i*2);}}ready=(int)enabled;}return 1;
}
void TlkHitboxDataClear(void) { ready=0; }
int TlkHitboxDataReady(void) { return ready; }
int TlkHitboxDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    ready=0;
    if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    for(unsigned n=0;n<COUNT;n++) {
        const struct HitboxPoseMap *map=&hitbox_map[n];valid[n]=0;
        if(map->role>10 || map->snes>sn-20 || map->md>mn-20)continue;
        int ok=1;
        for(unsigned i=0;i<4;i++) {
            native_bounds[n][i]=(uint16_t)le16(s+map->snes+12+i*2);
            md_bounds[n][i]=(uint16_t)be16(m+map->md+12+i*2);
            int a=(int16_t)native_bounds[n][i],b=(int16_t)md_bounds[n][i];
            if(a < -256 || a > 256 || b < -256 || b > 256)ok=0;
        }
        if((int16_t)native_bounds[n][0]>(int16_t)native_bounds[n][2] ||
           (int16_t)native_bounds[n][1]>(int16_t)native_bounds[n][3] ||
           (int16_t)md_bounds[n][0]>(int16_t)md_bounds[n][2] ||
           (int16_t)md_bounds[n][1]>(int16_t)md_bounds[n][3])ok=0;
        valid[n]=(uint8_t)ok;ready+=ok;
    }
    return ready!=0;
}
int TlkHitboxDataGet(unsigned pose,unsigned enemy,unsigned component,unsigned *native,unsigned *md) {
    if(!ready || !native || !md || enemy>8 || component>3 || pose<0xc00000 || pose>=0xf00000)return 0;
    pose&=0x3fffff;unsigned lo=0,hi=COUNT;
    while(lo<hi) { unsigned mid=(lo+hi)/2;if(hitbox_map[mid].snes<pose)lo=mid+1;else hi=mid; }
    /* A pose may have independently reviewed owners. Select by both pose
     * and family; retain every previously prepared correspondence. */
    for(;lo<COUNT && hitbox_map[lo].snes==pose;lo++){
        unsigned role=hitbox_map[lo].role;
        if(!valid[lo] || (enemy==8 ? role!=10 : enemy==7 ? role!=9 : enemy==6 ? role!=8 : enemy==5 ? role!=7 : enemy==4 ? role!=6 : enemy==3 ? role!=5 : enemy==2 ? role!=4 : enemy ? role<1 || role>3 : role!=0))continue;
        *native=native_bounds[lo][component];*md=md_bounds[lo][component];return 1;
    }
    return 0;
}

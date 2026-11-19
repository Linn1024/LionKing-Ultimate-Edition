#include "tlk_roar_data.h"
#include "tlk_md_sprites.h"
#include "tlk_data_record.h"
static struct { unsigned duration,value; } tokens[64];
static unsigned count,fire_delay;
static unsigned be32(const uint8_t *p) { return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3]; }
size_t TlkRoarDataRecordSize(void) {return count?8+(size_t)count*8:0;}
int TlkRoarDataWrite(uint8_t *data,size_t size) {
    if(!count || !data || size!=TlkRoarDataRecordSize())return 0;TlkDataPut32(data,count);TlkDataPut32(data+4,fire_delay);
    for(unsigned i=0;i<count;i++){TlkDataPut32(data+8+i*8,tokens[i].duration);TlkDataPut32(data+12+i*8,tokens[i].value);}return 1;
}
int TlkRoarDataRead(const uint8_t *data,size_t size,int apply) {
    if(!data || size<16)return 0;unsigned n=TlkDataGet32(data),delay=TlkDataGet32(data+4);
    if(n<2 || n>64 || size!=8+(size_t)n*8 || !delay || delay>127)return 0;
    for(unsigned i=0;i<n;i++) {
        unsigned duration=TlkDataGet32(data+8+i*8),value=TlkDataGet32(data+12+i*8);
        if(i+1==n){if(duration!=255 || value<TLK_ROAR_STREAM || value>=TLK_ROAR_STREAM+i*4 || (value-TLK_ROAR_STREAM)%4)return 0;}
        else if(duration>127 || value<0xc00000 || value>=0xf00000)return 0;
    }
    if(apply){for(unsigned i=0;i<n;i++){tokens[i].duration=TlkDataGet32(data+8+i*8);tokens[i].value=TlkDataGet32(data+12+i*8);}count=n;fire_delay=delay;}return 1;
}
void TlkRoarDataClear(void) { count=fire_delay=0; }
int TlkRoarDataReady(void) { return count!=0; }
unsigned TlkRoarFireDelay(void) { return count?fire_delay:0; }
int TlkRoarToken(unsigned index,unsigned *duration,unsigned *pose_or_target) {
    if (!count || index>=count || !duration || !pose_or_target) return 0;
    *duration=tokens[index].duration;*pose_or_target=tokens[index].value;return 1;
}
int TlkRoarDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    TlkRoarDataClear();
    if (!s || !m || sn!=0x300000 || mn!=0x300000 ||
        s[0xe979]!=0xa9 || s[0xe97a]!=0x06 || s[0xe97b]!=0xf0 ||
        m[0x196758]!=0x3f || m[0x196759]!=0x3c) return 0;
    unsigned delay=(unsigned)m[0x19675a]<<8|m[0x19675b];
    if (!delay || delay>127) return 0;
    const unsigned start=0x7f032;
    for (unsigned i=0;i<64;i++) {
        unsigned raw=be32(m+start+i*4),duration=raw>>24,pose=raw&0xffffff;
        tokens[i].duration=duration;
        if (duration==255) {
            if (pose<start || pose>=start+i*4 || ((pose-start)&3)) return 0;
            tokens[i].value=TLK_ROAR_STREAM+pose-start;
            count=i+1;fire_delay=delay;return 1;
        }
        if (duration&128) return 0;
        unsigned native=TlkMdSpritesNativePose(pose);
        if (!native || native<0xc00000 || native>=0xf00000) return 0;
        tokens[i].value=native;
    }
    return 0;
}

#include "tlk_reactivation_data.h"
static unsigned native_flags,md_flags;
static int ready;
size_t TlkReactivationDataRecordSize(void) {return ready?2:0;}
int TlkReactivationDataWrite(uint8_t *data,size_t size) {
    if(!ready || !data || size!=2)return 0;data[0]=(uint8_t)native_flags;data[1]=(uint8_t)md_flags;return 1;
}
int TlkReactivationDataRead(const uint8_t *data,size_t size,int apply) {
    if(!data || size!=2 || (data[0]^data[1])!=2)return 0;
    if(apply){native_flags=data[0];md_flags=data[1];ready=1;}return 1;
}
static unsigned le24(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16; }
static unsigned be32(const uint8_t *p) { return (unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3]; }
void TlkReactivationDataClear(void) { ready=0; }
int TlkReactivationDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    ready=0;if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    const uint8_t *a=s+0xbe11+14*6,*b=m+0x92adc+14*8;
    if(le24(a)!=0xc0cbfc || le24(a+3)!=0xc58ca4 || be32(b)!=0x18d414 || be32(b+4)!=0x9798e)return 0;
    if(le24(s+0x58ca4)!=0xc15dc7 || be32(m+0x9798e)!=0x19bd2e || s[0xcc36]!=0xb7 || s[0xcc37]!=0x8e)return 0;
    native_flags=s[0x58ca4 + 5];md_flags=m[0x9798e + 5];
    if((native_flags^md_flags)!=2)return 0;
    ready=1;return 1;
}
int TlkReactivationDataFlags(unsigned *native,unsigned *external) {
    if(!ready || !native || !external)return 0;*native=native_flags;*external=md_flags;return 1;
}

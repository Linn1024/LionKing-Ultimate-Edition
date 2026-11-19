#include "tlk_contact_map.h"
#include "tlk_md_assets.h"
#include <stdlib.h>
#include <string.h>

static uint16_t native_cells[8000];
static uint8_t native_attributes[8000],md_attributes[8000];
static int ready;
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static unsigned be16(const uint8_t *p) { return (unsigned)p[0]<<8|p[1]; }
static unsigned le24(const uint8_t *p) { return (le16(p)|(unsigned)p[2]<<16)&0x3fffff; }
static unsigned be32(const uint8_t *p) { return be16(p)<<16|be16(p+2); }
void TlkContactMapClear(void) { ready=0; }
int TlkContactMapReady(void) { return ready; }
unsigned TlkContactMapRowBytes(void) { return ready?200:0; }
int TlkContactMapExport(uint8_t *data,size_t size) {
    if(!ready || !data || size!=TLK_CONTACT_MAP_BYTES)return 0;
    for(unsigned i=0;i<8000;i++) {data[i*2]=(uint8_t)native_cells[i];data[i*2+1]=(uint8_t)(native_cells[i]>>8);}
    memcpy(data+16000,native_attributes,8000);memcpy(data+24000,md_attributes,8000);return 1;
}
int TlkContactMapImport(const uint8_t *data,size_t size) {
    if(!data || size!=TLK_CONTACT_MAP_BYTES)return 0;
    for(unsigned i=0;i<8000;i++)native_cells[i]=(uint16_t)le16(data+i*2);
    memcpy(native_attributes,data+16000,8000);memcpy(md_attributes,data+24000,8000);ready=1;return 1;
}
int TlkContactMapInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    ready=0;
    if (!s || !m || sn!=0x300000 || mn!=0x300000) return 0;
    const uint8_t *sr=s+0x387,*mr=m+0x1cfdb4;
    if (le16(sr+18)!=200 || le16(sr+20)!=80 || be16(mr+12)!=200 || be16(mr+14)!=80) return 0;
    uint8_t *sm=malloc(16000),*mm=malloc(16000),*sc=malloc(65536);
    size_t a=0,b=0,c=0;
    int ok=sm && mm && sc &&
        TlkMdDecompress(s,sn,le24(sr+9),sm,16000,&a) && a==16000 &&
        TlkMdDecompress(m,mn,be32(mr+16),mm,16000,&b) && b==16000 &&
        TlkMdDecompress(s,sn,le24(sr),sc,65536,&c);
    unsigned sh=le24(sr+3),mc=be32(mr+4),mh=be32(mr+8);
    for (unsigned i=0;i<8000 && ok;i++) {
        unsigned sw=le16(sm+i*2),mw=be16(mm+i*2),so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if ((sw&7)!=(mw&7) || so+4>c || mc>=mn || mo+4>mn-mc) { ok=0;break; }
        unsigned sp=le16(sc+so),mp=m[mc+mo]*16u;
        if (sh>=sn || sp+16>sn-sh || mh>=mn || mp+16>mn-mh) { ok=0;break; }
        for (unsigned x=0;x<16;x++) if ((s[sh+sp+x]&31)!=(m[mh+mp+x]&31)) { ok=0;break; }
        native_cells[i]=(uint16_t)sw;
        native_attributes[i]=sc[so+2];md_attributes[i]=m[mc+mo+2];
    }
    free(sm);free(mm);free(sc);ready=ok;return ready;
}
int TlkContactMapAttribute(unsigned cell,unsigned live_word,unsigned native_attribute,unsigned *attribute) {
    if (!ready || !attribute || cell>=8000 || live_word!=native_cells[cell] ||
        native_attribute!=native_attributes[cell]) return 0;
    *attribute=md_attributes[cell];return 1;
}

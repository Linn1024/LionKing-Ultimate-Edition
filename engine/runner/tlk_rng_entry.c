#include "tlk_rng_entry.h"
#include <string.h>
static unsigned entry_word(const uint8_t *r,unsigned a) { return r[a]|(unsigned)r[a+1]<<8; }
int TlkRngEntryInit(TlkRngEntryData *d,const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    if(!d)return 0;memset(d,0,sizeof *d);
    if(!s || !m || sn!=0x300000 || mn!=0x300000 ||
       memcmp(s+0x7970,"\x9e\x00\x00\xca\xe0\xff\x02\xd0",8) || s[0x7979]!=0x28)return 0;
    for(unsigned i=0;i<3;i++) {
        const uint8_t *p=m + 0x1d77de + i*8;
        if(p[0]!=0x13 || p[1]!=0xfc || p[2] || p[4]!=0xff || p[5]!=0xff || p[6]!=0x81 || p[7]!=0xad+i)return 0;
        d->seed=d->seed<<8|p[3];
    }
    d->ready=1;return 1;
}
int TlkRngEntryApply(const TlkRngEntryData *d,const CpuState *c,uint32_t pc,uint8_t *r,size_t n,int selected) {
    if(!d || !d->ready || !c || !r || n!=0x20000 || !selected || pc!=0xc07979 ||
       c->PB!=0xc0 || c->D || (c->DB!=0 && c->DB!=0x7e) || c->emulation || c->m_flag || c->x_flag ||
       c->X!=0x2ff || c->A || entry_word(r,0x1ff9e) || entry_word(r,0x1ffa2) ||
       entry_word(r,0xdf) || r[0xe1])return 0;
    r[0x1e00]=(uint8_t)d->seed;r[0x1e01]=(uint8_t)(d->seed>>8);r[0x1e02]=(uint8_t)(d->seed>>16);
    return 1;
}
int TlkRngStagePreserve(CpuState *c,uint32_t pc,const uint8_t *r,size_t n,int selected){
    if(!c || !r || n!=0x20000 || !selected || pc!=0xc07970 || c->PB!=0xc0 || c->D ||
       (c->DB!=0 && c->DB!=0x7e) || c->emulation || c->m_flag || c->x_flag ||
       c->X!=0x1dff || !entry_word(r,0x1ff9e) || entry_word(r,0x1ff9e)>13 ||
       entry_word(r,0x1ffa2) || entry_word(r,0xdf) || r[0xe1])return 0;
    /* Native word STZ at1DFF also clears random byte1E00. MD retains its
     * stream through stage changes. Starting one byte earlier still clears
     * every byte300..1DFF through the original overlapping word loop. */
    c->X=0x1dfe;return 1;
}

#include "tlk_native_bank.h"
#include "tlk_md_assets.h"
#include "tlk_state_bytes.h"
#include "sha256.h"
#include "snes/apu.h"
#include "snes/saveload.h"
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

enum { HEADER=128,DRIVER=256,ALIASES=4,SCORE=6250,SAMPLES=43560,DIR_COUNT=178,MAX_BLOB=262144 };
typedef struct Sample { unsigned offset,size,id; } Sample;
struct TlkNativeBankProgram {
    uint8_t identity[32],payload[SCORE+SAMPLES],directory[DIR_COUNT*4],written[DIR_COUNT],aliases[ALIASES];
    Sample samples[20];size_t apu_size;
};
struct TlkNativeBank { uint8_t *body,identity[32];size_t size;uint64_t field; };
typedef struct Io { SaveLoadInfo base;uint8_t *data;size_t size,pos;int load,error; } Io;
static unsigned word(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static unsigned addr(const uint8_t *p) { return word(p)|(unsigned)p[2]<<16; }
static int zero(const uint8_t *p,size_t n) { for(size_t i=0;i<n;i++)if(p[i])return 0;return 1; }
static void transfer(SaveLoadInfo *base,void *data,size_t size) {
    Io *io=(Io*)base;
    if(io->pos>io->size || size>io->size-io->pos) { io->error=1;return; }
    if(io->data) {
        if(io->load)memcpy(data,io->data+io->pos,size);
        else memcpy(io->data+io->pos,data,size);
    }
    io->pos+=size;
}
static int serial(Apu *apu,uint8_t *data,size_t size,int load) {
    Io io={.base={.func=transfer},.data=data,.size=size,.load=load};
    apu_saveload(apu,&io.base);return !io.error && io.pos==size;
}
static int raw_bool(const void *object,size_t at) { return ((const uint8_t*)object)[at]<=1; }
#define BOOL(o,t,f) do { if(!raw_bool(o,offsetof(t,f)))return 0; } while(0)
static int core_valid(const Apu *a,int canonical) {
    if(!a || !a->dsp || !a->spc || a->dsp->shadow)return 0;
    BOOL(a,Apu,romReadable);
    for(unsigned i=0;i<3;i++) {
        BOOL(&a->timer[i],Timer,enabled);
        if(a->timer[i].counter>15 || a->timer[i].cycles>(i==2?16:128))return 0;
    }
    /* TLK's patched APU defers an opcode until its final base cycle. The
     * high bit marks a pending opcode, with 1..12 base cycles remaining.
     * It is real serialized execution state, not an oversized delay. */
    if(a->cpuCyclesLeft&0x80) {
        unsigned left=a->cpuCyclesLeft&0x7f;
        if(!left || left>12)return 0;
    } else if(a->cpuCyclesLeft>32)return 0;
    const Spc *s=a->spc;
    BOOL(s,Spc,c);BOOL(s,Spc,z);BOOL(s,Spc,v);BOOL(s,Spc,n);BOOL(s,Spc,i);
    BOOL(s,Spc,h);BOOL(s,Spc,p);BOOL(s,Spc,b);BOOL(s,Spc,stopped);
    if(s->stopped)return 0;
    const Dsp *d=a->dsp;
    BOOL(d,Dsp,evenCycle);BOOL(d,Dsp,mute);BOOL(d,Dsp,reset);BOOL(d,Dsp,echoWrites);
    if(d->firBufferIndex>=8 || !d->echoDelay || !d->echoRemain || d->echoDelay>7680 || d->echoRemain>d->echoDelay ||
       d->echoBufferIndex>d->echoDelay || d->dirPage!=0x2300 || d->ram[0x5d]!=0x23 ||
       (uint32_t)(d->sampleWrite-d->sampleRead)>DSP_SAMPLE_RING)return 0;
    for(unsigned i=0;i<8;i++) {
        const DspChannel *c=&d->channel[i];
        BOOL(c,DspChannel,pitchModulation);BOOL(c,DspChannel,useNoise);BOOL(c,DspChannel,useGain);
        BOOL(c,DspChannel,directGain);BOOL(c,DspChannel,keyOn);BOOL(c,DspChannel,keyOff);BOOL(c,DspChannel,echoEnable);
        if(c->adsrState>4 || c->gainMode>3 || c->pitch>0x3fff || c->gain>0x7ff || c->gainValue>0x7f0 ||
           c->sustainLevel>0x800)return 0;
        for(unsigned j=0;j<4;j++)if(c->adsrRates[j]>2048)return 0;
        if(canonical && (c->gain || c->keyOn))return 0;
    }
    if(canonical && (d->sampleRead || d->sampleWrite || !zero((const uint8_t*)d->sampleBuffer,sizeof d->sampleBuffer)))return 0;
    return 1;
}
#undef BOOL
static int driver_valid(const TlkNativeBankProgram *p,const uint8_t *driver,const uint8_t *aliases) {
    return driver[0x2b]<=56 && driver[0x2b]==driver[0x2c] && !(driver[0x2b]&7) &&
        !(driver[0xc3]&5) && word(driver+0xce)==0xe870 && !memcmp(aliases,p->aliases,ALIASES);
}
static int payload_valid(const TlkNativeBankProgram *p,const Apu *a) {
    if(memcmp(a->ram+0x25de,p->payload,SCORE))return 0;
    for(unsigned i=0;i<20;i++) {
        const Sample *s=&p->samples[i];
        if(memcmp(a->ram+s->offset,p->payload+SCORE+s->offset-0x3e48,s->size) ||
           memcmp(a->ram+0x2300+s->id*4,p->directory+s->id*4,4))return 0;
    }
    return 1;
}
static int context(const uint8_t *r,size_t size,uint32_t pc,int apply) {
    if(!r || size!=0x20000 || word(r+0x1ff9e) || addr(r+0xdf)!=0xc00387 || word(r+0x2000) || word(r+0x1ff90))return 0;
    if(!apply)return pc==0xc082bb || pc==0xc082fa;
    return pc==0xc082a5 && word(r+0x1ffa2)==1 && addr(r+0xb243)==0xc35a82 && !word(r+0xa6ba);
}
TlkNativeBankProgram *TlkNativeBankProgramCreate(const uint8_t *rom,size_t size,const uint8_t build[32]) {
    static const char expected[]="457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712";
    static const char hex[]="0123456789abcdef";
    if(!rom || size!=0x300000 || !build || zero(build,32))return NULL;
    uint8_t hash[32];sha256_compute(rom,size,hash);
    for(unsigned i=0;i<32;i++)if(expected[i*2]!=hex[hash[i]>>4] || expected[i*2+1]!=hex[hash[i]&15])return NULL;
    TlkNativeBankProgram *p=calloc(1,sizeof *p);uint8_t *scratch=malloc(65536);
    if(!p || !scratch) { free(p);free(scratch);return NULL; }
    size_t written=0;
    unsigned score=addr(rom+0x223cf+12*3)&0x3fffff;
    if(!TlkMdDecompress(rom,size,score,scratch,65536,&written) || written!=SCORE)goto fail;
    memcpy(p->payload,scratch,SCORE);free(scratch);scratch=NULL;
    unsigned list=addr(rom+0x22428+12*12)&0x3fffff,count=0,total=0;
    for(unsigned i=0;i<64;i++) {
        unsigned at=list+i*4;if(at>size-4)goto fail;
        unsigned low=word(rom+at);if(!low)break;
        if(low<3) {
            if(word(rom+at+2))goto fail;
            unsigned relative=0x3e48+total-0x2400,index=(low-1)*2;
            p->aliases[index]=(uint8_t)relative;p->aliases[index+1]=(uint8_t)(relative>>8);
            continue;
        }
        unsigned source=addr(rom+at)&0x3fffff;if(source>size-8 || count>=20)goto fail;
        unsigned n=word(rom+source),id=rom[source+3];
        if(n<8 || n>size-source || n>SAMPLES-total || rom[source+2]!=1 || id>=DIR_COUNT || p->written[id])goto fail;
        unsigned target=0x3e48+total,start=target+3+word(rom+source+4),loop=target+3+word(rom+source+6);
        if(start>=target+n || loop>=target+n)goto fail;
        p->samples[count++]=(Sample){target,n,id};p->written[id]=1;
        p->directory[id*4]=(uint8_t)start;p->directory[id*4+1]=(uint8_t)(start>>8);
        p->directory[id*4+2]=(uint8_t)loop;p->directory[id*4+3]=(uint8_t)(loop>>8);
        memcpy(p->payload+SCORE+total,rom+source,n);total+=n;
    }
    if(count!=20 || total!=SAMPLES)goto fail;
    Apu *probe=apu_init();if(!probe)goto fail;
    Io measure={.base={.func=transfer},.size=MAX_BLOB};apu_saveload(probe,&measure.base);apu_free(probe);
    if(measure.error || !measure.pos || measure.pos>MAX_BLOB)goto fail;
    p->apu_size=measure.pos;
    uint8_t identity[112]={0};memcpy(identity,"TLKNATIVEBANK001",15);memcpy(identity+16,hash,32);memcpy(identity+48,build,32);
    TlkPut32(identity+80,(uint32_t)p->apu_size);TlkPut32(identity+84,(uint32_t)sizeof(Apu));
    TlkPut32(identity+88,(uint32_t)sizeof(Dsp));TlkPut32(identity+92,(uint32_t)sizeof(Spc));
    TlkPut32(identity+96,(uint32_t)sizeof(void*));sha256_compute(identity,sizeof identity,p->identity);
    return p;
fail:
    free(scratch);free(p);return NULL;
}
void TlkNativeBankProgramFree(TlkNativeBankProgram *p) { free(p); }
TlkNativeBank *TlkNativeBankCreate(void) { return calloc(1,sizeof(TlkNativeBank)); }
void TlkNativeBankClear(TlkNativeBank *b) { if(b) { free(b->body);memset(b,0,sizeof *b); } }
void TlkNativeBankFree(TlkNativeBank *b) { if(b) { TlkNativeBankClear(b);free(b); } }
int TlkNativeBankReady(const TlkNativeBank *b,const TlkNativeBankProgram *p) {
    return b && p && b->body && b->size==p->apu_size+DRIVER+ALIASES && !memcmp(b->identity,p->identity,32);
}
static Apu *decode(const TlkNativeBankProgram *p,const uint8_t *body,size_t size) {
    if(!p || !body || size!=p->apu_size+DRIVER+ALIASES)return NULL;
    Apu *a=apu_init();if(!a)return NULL;
    if(!serial(a,(uint8_t*)body,p->apu_size,1) || !core_valid(a,1) || !payload_valid(p,a) ||
       !driver_valid(p,body+p->apu_size,body+p->apu_size+DRIVER)) { apu_free(a);return NULL; }
    return a;
}
int TlkNativeBankCapture(TlkNativeBank *b,const TlkNativeBankProgram *p,const Apu *a,const uint8_t *r,size_t size,uint32_t pc,uint64_t field) {
    if(!b || !p || !field || !context(r,size,pc,0) || !core_valid(a,0) || apu_portQueueDepth(a) ||
       !driver_valid(p,r+0x1f00,r+0xaa3) || !payload_valid(p,a))return 0;
    for(unsigned i=0;i<8;i++)if(a->dsp->channel[i].gain || a->dsp->channel[i].keyOn)return 0;
    size_t n=p->apu_size+DRIVER+ALIASES;uint8_t *body=malloc(n);if(!body)return 0;
    if(!serial((Apu*)a,body,p->apu_size,0)) { free(body);return 0; }
    Apu *candidate=apu_init();if(!candidate) { free(body);return 0; }
    int valid=serial(candidate,body,p->apu_size,1);
    candidate->dsp->sampleRead=candidate->dsp->sampleWrite=0;
    memset(candidate->dsp->sampleBuffer,0,sizeof candidate->dsp->sampleBuffer);
    valid=valid && core_valid(candidate,1) && payload_valid(p,candidate) && serial(candidate,body,p->apu_size,0);
    apu_free(candidate);
    if(!valid) { free(body);return 0; }
    memcpy(body+p->apu_size,r+0x1f00,DRIVER);memcpy(body+p->apu_size+DRIVER,r+0xaa3,ALIASES);
    TlkNativeBank next={.body=body,.size=n,.field=field};memcpy(next.identity,p->identity,32);
    TlkNativeBankClear(b);*b=next;return 1;
}
static int apply_validated_bank(const TlkNativeBank *b,const TlkNativeBankProgram *p,Apu *a,uint8_t *r) {
    if(!TlkNativeBankReady(b,p) || !core_valid(a,0) || apu_portQueueDepth(a))return 0;
    if(r[0x1f2b]>56 || r[0x1f2b]!=r[0x1f2c] || (r[0x1f2b]&7) || (r[0x1fc3]&5))return 0;
    for(unsigned i=0;i<8;i++)if(a->dsp->channel[i].gain || a->dsp->channel[i].keyOn)return 0;
    Apu *candidate=decode(p,b->body,b->size);if(!candidate)return 0;
    for(unsigned i=0;i<DIR_COUNT;i++)if(!p->written[i])memcpy(candidate->ram+0x2300+i*4,a->ram+0x2300+i*4,4);
    /* The bank changes source data and the idle SPC driver, not already produced
     * PCM or live DSP/echo/noise history. The hardware echo arena must be outside
     * resident code, directory and new source data for this scoped adapter. */
    unsigned echo=a->dsp->echoBufferAdr,echo_bytes=(unsigned)a->dsp->echoDelay*4;
    if(a->dsp->echoWrites || a->dsp->echoVolumeL || a->dsp->echoVolumeR) {
        if(echo<0xe870 || echo_bytes>65536-echo) { apu_free(candidate);return 0; }
    }
    /* This bank never writes the upper tail. Preserve it even while echo is
     * disabled, so a later enable cannot resurrect the cold template's RAM. */
    memcpy(candidate->ram+0xe870,a->ram+0xe870,65536-0xe870);
    memcpy(&candidate->dsp->ram,&a->dsp->ram,sizeof(Dsp)-offsetof(Dsp,ram));
    candidate->cycles=a->cycles;
    if(!core_valid(candidate,0) || !payload_valid(p,candidate)) { apu_free(candidate);return 0; }
    uint8_t *commit=malloc(p->apu_size);if(!commit) { apu_free(candidate);return 0; }
    int valid=serial(candidate,commit,p->apu_size,0);apu_free(candidate);
    if(!valid) { free(commit);return 0; }
    /* All allocation, source/shape validation and candidate work completed.
     * The fixed-layout copy below cannot fail for this measured codec. */
    serial(a,commit,p->apu_size,1);free(commit);apu_clearPortQueue(a);
    memcpy(r+0x1f00,b->body+p->apu_size,DRIVER);memcpy(r+0xaa3,b->body+p->apu_size+DRIVER,ALIASES);
    return 1;
}
int TlkNativeBankApply(const TlkNativeBank *b,const TlkNativeBankProgram *p,Apu *a,uint8_t *r,size_t size,uint32_t pc) {
    if(!context(r,size,pc,1))return 0;
    return apply_validated_bank(b,p,a,r);
}
int TlkNativeBankApplyContinue(const TlkNativeBank *b,const TlkNativeBankProgram *p,Apu *a,uint8_t *r,size_t size,uint32_t pc,
                              uint32_t origin_descriptor) {
    if(!r || size!=0x20000 || pc!=0xc082a5 || origin_descriptor!=0xc00387 ||
       word(r+0x1ff9e) || addr(r+0xdf)!=0xc00387 || word(r+0x2000) || word(r+0x1ff90) ||
       word(r+0x1ffa2) || addr(r+0xb243) || word(r+0xa6ba) || word(r+0x2004) ||
       word(r+0x1ffaa)!=2)return 0;
    return apply_validated_bank(b,p,a,r);
}
size_t TlkNativeBankRecordSize(const TlkNativeBank *b) { return b && b->body?HEADER+b->size:0; }
int TlkNativeBankSave(const TlkNativeBank *b,const TlkNativeBankProgram *p,uint8_t *out,size_t size) {
    if(!out || !TlkNativeBankReady(b,p) || size!=HEADER+b->size)return 0;
    memset(out,0,HEADER);memcpy(out,"TLKNBK01",8);TlkPut32(out+8,1);TlkPut32(out+12,HEADER);
    TlkPut32(out+16,(uint32_t)size);TlkPut32(out+20,(uint32_t)p->apu_size);memcpy(out+24,p->identity,32);
    TlkPut64(out+56,b->field);memcpy(out+HEADER,b->body,b->size);
    uint8_t hash[32];sha256_compute(out,size,hash);memcpy(out+96,hash,32);return 1;
}
int TlkNativeBankLoad(TlkNativeBank *b,const TlkNativeBankProgram *p,const uint8_t *data,size_t size) {
    if(!b || !p || !data || size!=HEADER+p->apu_size+DRIVER+ALIASES || memcmp(data,"TLKNBK01",8) ||
       TlkGet32(data+8)!=1 || TlkGet32(data+12)!=HEADER || TlkGet32(data+16)!=size ||
       TlkGet32(data+20)!=p->apu_size || memcmp(data+24,p->identity,32) || !TlkGet64(data+56) || !zero(data+64,32))return 0;
    uint8_t *copy=malloc(size);if(!copy)return 0;memcpy(copy,data,size);memset(copy+96,0,32);
    uint8_t hash[32];sha256_compute(copy,size,hash);free(copy);if(memcmp(hash,data+96,32))return 0;
    Apu *candidate=decode(p,data+HEADER,size-HEADER);if(!candidate)return 0;apu_free(candidate);
    uint8_t *body=malloc(size-HEADER);if(!body)return 0;memcpy(body,data+HEADER,size-HEADER);
    TlkNativeBank next={.body=body,.size=size-HEADER,.field=TlkGet64(data+56)};memcpy(next.identity,p->identity,32);
    TlkNativeBankClear(b);*b=next;return 1;
}

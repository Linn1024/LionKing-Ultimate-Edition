/* Private checkpoint cache codec. No host layout, process pointers or FILEs.
 * Payload bytes are regenerated from the pinned ROM; observed decoder ABI and
 * DMA terminal values are explicit little-endian scalars. Cold captures must
 * already be complete, so no borrowed in-flight cold decoder frame is stored. */
typedef struct PreparationIo { uint8_t *data;size_t size,at;int reading,ok; } PreparationIo;
typedef struct PreparationCache {
    SceneTemplate recipes[7];
    TlkNativeBankProgram *program;
    TlkNativeBank *bank;
} PreparationCache;
static PreparationCache *preparation_pending;
static void preparation_bytes(PreparationIo *io,void *data,size_t n) {
    if(!io->ok || n>io->size-io->at) { io->ok=0;return; }
    if(io->data) {
        if(io->reading)memcpy(data,io->data+io->at,n);else memcpy(io->data+io->at,data,n);
    }
    io->at+=n;
}
static uint32_t preparation_word(PreparationIo *io,uint32_t v) {
    uint8_t data[4];TlkPut32(data,v);preparation_bytes(io,data,4);return TlkGet32(data);
}
#define PC_WORD(member,limit) do { uint32_t v=preparation_word(io,(uint32_t)(member)); \
    if(v>(limit))io->ok=0;if(io->reading)(member)=v; } while(0)
static void preparation_dma(PreparationIo *io,DmaChannel *d) {
    PC_WORD(d->bAdr,255);PC_WORD(d->aAdr,65535);PC_WORD(d->aBank,255);PC_WORD(d->size,65535);
    PC_WORD(d->indBank,255);PC_WORD(d->tableAdr,65535);PC_WORD(d->repCount,255);PC_WORD(d->unusedByte,255);
    PC_WORD(d->dmaActive,1);PC_WORD(d->hdmaActive,1);PC_WORD(d->mode,7);PC_WORD(d->fixed,1);
    PC_WORD(d->decrement,1);PC_WORD(d->indirect,1);PC_WORD(d->fromB,1);PC_WORD(d->unusedBit,1);
    PC_WORD(d->doTransfer,1);PC_WORD(d->terminated,1);PC_WORD(d->offIndex,3);
}
static void preparation_recipes(PreparationIo *io,SceneTemplate *recipes) {
    for(unsigned n=0;n<7 && io->ok;n++) {
        SceneTemplate *t=&recipes[n];const SceneTemplate *recipe=&scene_templates[n];
        PC_WORD(t->source,0xffffff);PC_WORD(t->destination,0xffffff);PC_WORD(t->expected,65536);
        if(t->source!=recipe->source || t->destination!=recipe->destination || t->expected!=recipe->expected)io->ok=0;
        preparation_bytes(io,t->input,10);preparation_bytes(io,t->scratch,10);preparation_bytes(io,t->stack,5);
        PC_WORD(t->p,255);PC_WORD(t->a,65535);PC_WORD(t->x,65535);PC_WORD(t->y,65535);PC_WORD(t->sp,65535);
        preparation_dma(io,&t->dma_input);preparation_dma(io,&t->dma_output);
        PC_WORD(t->port,0x1ffff);PC_WORD(t->ready,1);PC_WORD(t->capturing,1);
        if(!t->ready || t->capturing || t->sp<0x205 || t->sp>=0x300 ||
           t->port!=((t->destination-0x7e0000+t->expected)&0x1ffff))io->ok=0;
    }
}
#undef PC_WORD
static void preparation_free(PreparationCache *cache) {
    if(!cache)return;TlkNativeBankFree(cache->bank);TlkNativeBankProgramFree(cache->program);free(cache);
}
static int preparation_save(uint32_t field,uint8_t **data,size_t *size) {
    if(preparation_pending || !program || !prepared || !TlkNativeBankReady(prepared,program))return 0;
    PreparationIo count={.size=SIZE_MAX,.ok=1};preparation_recipes(&count,scene_templates);
    size_t bank_size=TlkNativeBankRecordSize(prepared),n=96+count.at+bank_size;
    uint8_t *out=count.ok && bank_size?calloc(1,n):NULL;if(!out)return 0;
    memcpy(out,"PRPREP01",8);TlkPut32(out+8,1);TlkPut32(out+12,(uint32_t)n);
    memcpy(out+16,build_digest,32);TlkPut32(out+80,field);TlkPut32(out+84,(uint32_t)count.at);
    TlkPut32(out+88,(uint32_t)bank_size);
    PreparationIo writer={.data=out,.size=n,.at=96,.ok=1};preparation_recipes(&writer,scene_templates);
    if(!writer.ok || !TlkNativeBankSave(prepared,program,out+writer.at,bank_size)) { free(out);return 0; }
    sha256_compute(out,n,out+48);*data=out;*size=n;return 1;
}
static PreparationCache *preparation_stage(const uint8_t *data,size_t size,uint32_t field) {
    if(!data || size<96 || size>1024*1024 || memcmp(data,"PRPREP01",8) || TlkGet32(data+8)!=1 ||
       TlkGet32(data+12)!=size || memcmp(data+16,build_digest,32) || TlkGet32(data+80)!=field ||
       TlkGet32(data+92) || (uint64_t)96+TlkGet32(data+84)+TlkGet32(data+88)!=size)return NULL;
    uint8_t *copy=malloc(size),hash[32];if(!copy)return NULL;
    memcpy(copy,data,size);memset(copy+48,0,32);sha256_compute(copy,size,hash);free(copy);
    if(memcmp(hash,data+48,32))return NULL;
    PreparationCache *cache=calloc(1,sizeof *cache);if(!cache)return NULL;
    PreparationIo reader={.data=(uint8_t*)data,.size=96+TlkGet32(data+84),.at=96,.reading=1,.ok=1};
    preparation_recipes(&reader,cache->recipes);
    if(!reader.ok || reader.at!=reader.size)goto fail;
    cache->program=TlkNativeBankProgramCreate(g_rom,0x300000,build_digest);cache->bank=TlkNativeBankCreate();
    if(!cache->program || !cache->bank ||
       !TlkNativeBankLoad(cache->bank,cache->program,data+reader.at,TlkGet32(data+88)))goto fail;
    return cache;
fail: preparation_free(cache);return NULL;
}
/* Runs after ordinary wrapper initialization but before guest instructions.
 * Initialization rebuilds immutable payloads from ROM and registers normal
 * hooks. Only then publish retained ABI/cache data, never a suspended host call.
 * Dynamic native decoder returns are registered if still outstanding. */
static void preparation_rehydrate(void) {
    PreparationCache *cache=preparation_pending;if(!cache)return;
    for(unsigned n=0;n<7;n++) {
        SceneTemplate *target=&scene_templates[n];uint8_t *payload=target->payload;
        free(target->before);*target=cache->recipes[n];target->payload=payload;target->before=NULL;
    }
    TlkNativeBankFree(prepared);prepared=cache->bank;cache->bank=NULL;
    if(scene_active)interp_bridge_add_pre_opcode_hook(scene_return,scene_hook);
    preparation_pending=NULL;preparation_free(cache);
}

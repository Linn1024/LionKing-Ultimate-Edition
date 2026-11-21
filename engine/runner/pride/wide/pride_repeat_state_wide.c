/* All serialization has visibility of the private renderer's owned storage.
 * The established renderer itself stays unchanged for predecessor evidence. */
#include "pride_repeat_prepared.c"
#include "../pride_prepared_history_api.h"
#include "tlk_state_bytes.h"
#include "sha256.h"

typedef __typeof__(s_frame) HistoryFrame;
typedef struct HistoryIo { uint8_t *data;size_t size,at;int reading,ok; } HistoryIo;
struct PridePreparedHistory {
    uint32_t field,age,health_age,ready_age,normal_started,normal_latch,native_latch;
    int width,column,y_offset,flip,previous_valid,previous_camera[2];
    unsigned draws,released,background_field,count,hud,prepared_age;
    HistoryFrame frame;
    uint16_t vram[kVramCopies][0x8000],cgram[256];
    uint32_t background[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
    uint32_t tags[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
    Piece pieces[kMaxPieces];uint8_t cub[kMaxPieces],health[512],roar[512];
    Level last;uint8_t map[0x10000],limits[4];int have_last;
    TlkNativeHud *font;TlkRevivalArt *art;
};
/* Cached presentation/release decisions belong to these resolved leaves.
 * Cross-artwork loads need a separate re-composition policy, not stale release. */
static uint32_t history_graphics(void) {
    static const char *ids[]={"graphics.scenery.foreground","graphics.scenery.background","graphics.scenery.palettes",
        "graphics.sprites.simba.cub.frames","graphics.sprites.simba.cub.palette","graphics.hud.frames","graphics.hud.palette",
        "graphics.sprites.enemies.hyenas.frames","graphics.sprites.enemies.hyenas.palette",
        "graphics.sprites.enemies.other.frames","graphics.sprites.enemies.other.palette",
        "graphics.sprites.pickups.frames","graphics.sprites.pickups.palette","graphics.sprites.leaves.frames","graphics.sprites.leaves.palette",
        "graphics.sprites.effects.defeat_puff.frames","graphics.sprites.effects.defeat_puff.palette",
        "graphics.sprites.checkpoints.frames","graphics.sprites.checkpoints.palette",
        "graphics.sprites.enemies.chameleons.frames","graphics.sprites.enemies.chameleons.palette",
        "graphics.sprites.enemies.porcupines.frames","graphics.sprites.enemies.porcupines.palette",
        "graphics.scenery.foreground.palette","graphics.scenery.background.palette"};
    uint32_t flags=0;for(unsigned n=0;n<sizeof ids/sizeof *ids;n++)if(TlkResourcesUseMd(ids[n]))flags|=1u<<n;
    return flags;
}
static void history_bytes(HistoryIo *io,void *data,size_t n) {
    if(!io->ok || n>io->size-io->at) { io->ok=0;return; }
    if(io->data) {
        if(io->reading)memcpy(data,io->data+io->at,n);
        else memcpy(io->data+io->at,data,n);
    }
    io->at+=n;
}
static uint32_t history_word(HistoryIo *io,uint32_t v) {
    uint8_t b[4];TlkPut32(b,v);history_bytes(io,b,4);return TlkGet32(b);
}
#define HU(member,maximum) do { uint32_t v=history_word(io,(uint32_t)(member)); \
    if(v>(maximum))io->ok=0;if(io->reading)(member)=v; } while(0)
#define HS(member,minimum,maximum) do { int32_t v=(int32_t)history_word(io,(uint32_t)(member)); \
    if(v<(minimum) || v>(maximum))io->ok=0;if(io->reading)(member)=v; } while(0)
static void history_piece(HistoryIo *io,Piece *p) {
    HS(p->x,-32768,32767);HS(p->y,-32768,32767);HU(p->attr,65535);HU(p->obj,65535);
    HU(p->size,16);HU(p->slot,127);HU(p->kept,1);HU(p->fixed,1);HS(p->side,-64,64);
    HU(p->pose,0xffffff);HS(p->local_x,-32768,32767);HS(p->local_y,-32768,32767);
    if(p->size!=8 && p->size!=16)io->ok=0;
}
static void history_level(HistoryIo *io,Level *p) {
    uint32_t kind=0,offset=0;uintptr_t pointer=(uintptr_t)p->map;
    if(!io->reading && pointer) {
        uintptr_t ram=(uintptr_t)s_frame.ram,map=(uintptr_t)s_last_map;
        if(pointer>=ram && pointer<ram+sizeof s_frame.ram) { kind=1;offset=(uint32_t)(pointer-ram); }
        else if(pointer>=map && pointer<map+sizeof s_last_map) { kind=2;offset=(uint32_t)(pointer-map); }
        else io->ok=0;
    }
    HU(p->rowb,65536);HU(p->rows,65536);HU(p->blk,0xffffff);
    HU(kind,2);HU(offset,0x1ffff);
    uint64_t bytes=(uint64_t)p->rowb*p->rows;
    if((!kind && (p->rowb || p->rows || p->blk || offset)) ||
       (kind && (!p->rowb || !p->rows || bytes>65536 ||
        (uint64_t)offset+bytes>(kind==1?sizeof s_frame.ram:sizeof s_last_map))))io->ok=0;
    if(io->reading)p->map=!io->ok?NULL:kind==1?s_frame.ram+offset:kind==2?s_last_map+offset:NULL;
}
static void history_frame(HistoryIo *io,HistoryFrame *f) {
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        Line *l=&f->lines[y];
        HU(l->inidisp,255);HU(l->obsel,255);HU(l->bgmode,255);HU(l->mosaic,255);HU(l->setini,255);
        HU(l->oamaddl,255);HU(l->oamaddh,255);
        for(unsigned n=0;n<4;n++) { HU(l->bgsc[n],255);HU(l->hofs[n],65535);HU(l->vofs[n],65535); }
        HU(l->bgchr,65535);HU(l->fixed,65535);HU(l->windowsel,0xffffffffu);
        HU(l->w1l,255);HU(l->w1r,255);HU(l->w2l,255);HU(l->w2r,255);HU(l->wlog,65535);
        HU(l->tm,255);HU(l->ts,255);HU(l->tmw,255);HU(l->tsw,255);HU(l->cgadsub,255);HU(l->cgwsel,255);
        HU(l->vram,kVramCopies-1);
        for(unsigned n=0;n<256;n++) { HU(l->cgram[n],65535);HU(l->oam[n],65535); }
        history_bytes(io,l->hoam,sizeof l->hoam);
    }
    HS(f->captured,0,TLK_WIDE_HEIGHT);history_bytes(io,f->ram,sizeof f->ram);
    HU(f->piece_count,kMaxPieces);HU(f->latch_serial,0xffffffffu);
    for(unsigned n=0;n<f->piece_count && io->ok;n++)history_piece(io,&f->pieces[n]);
    for(unsigned n=0;n<2;n++)HS(f->raster_camera[n],-65536,65535);
    HS(f->hud_end,-1,(int)f->piece_count);
    for(unsigned n=0;n<256*TLK_WIDE_HEIGHT;n++)HU(f->stock[n],0xffffffffu);
    HU(f->valid,1);HU(f->stage,1);history_level(io,&f->level);HU(f->stage_sc,255);HU(f->stage_chr,65535);
}
static void history_body(HistoryIo *io,PridePreparedHistory *h) {
    HU(h->field,0xffffffffu);HU(h->age,0xffffffffu);
    HU(h->health_age,274);HU(h->ready_age,345);
    HU(h->normal_started,1);HU(h->normal_latch,0xffffffffu);HU(h->native_latch,0xffffffffu);
    if((!h->normal_started && h->normal_latch) ||
       (h->normal_started && (h->age<h->ready_age ||
        (uint32_t)(h->native_latch-h->normal_latch)>=0x80000000u)))io->ok=0;
    if(!((h->health_age==270 && h->ready_age==345) || (h->health_age==274 && h->ready_age==300)))io->ok=0;
    HS(h->width,256,320);
    if(h->width!=256 && h->width!=320)io->ok=0;
    HS(h->column,0,64);HS(h->y_offset,-512,512);HU(h->flip,1);HU(h->draws,0xffffffffu);
    HU(h->released,1);HU(h->previous_valid,1);HU(h->background_field,0xffffffffu);
    for(unsigned n=0;n<2;n++)HS(h->previous_camera[n],-65536,65535);
    HU(h->count,kMaxPieces);HU(h->hud,h->count);HU(h->prepared_age,h->health_age-1);
    if(!h->previous_valid || (h->age>=h->health_age && (!h->count || h->prepared_age<254)) ||
       (h->count && (h->prepared_age<254 || h->prepared_age>h->age)))io->ok=0;
    history_frame(io,&h->frame);
    for(unsigned b=0;b<kVramCopies;b++)for(unsigned n=0;n<0x8000;n++)HU(h->vram[b][n],65535);
    for(unsigned n=0;n<256;n++)HU(h->cgram[n],65535);
    for(unsigned n=0;n<(unsigned)h->width*TLK_WIDE_HEIGHT && io->ok;n++) {
        HU(h->background[n],0xffffffffu);HU(h->tags[n],0xffffffffu);
    }
    for(unsigned n=0;n<h->count && io->ok;n++) {
        history_piece(io,&h->pieces[n]);HU(h->cub[n],1);
    }
    history_bytes(io,h->health,sizeof h->health);history_bytes(io,h->roar,sizeof h->roar);
    HU(h->have_last,1);history_bytes(io,h->map,sizeof h->map);history_bytes(io,h->limits,sizeof h->limits);
    history_level(io,&h->last);
    if((h->have_last && h->last.map!=s_last_map) || !h->frame.valid || !h->frame.stage ||
       h->column>h->width-256 || (h->released && h->age<h->ready_age))io->ok=0;
}
#undef HU
#undef HS
int PridePreparedHistorySave(uint32_t field,uint8_t **data,size_t *size) {
    TlkDeathScene scene;TlkDeathProgram program;
    if(!data || !size || prepared_changed || scene_palette_active || scene_tag_mode ||
       !PrideSceneRenderView(&scene,&program) || scene.last_field>field || scene.age>(scene.has_checkpoint?345u:300u) ||
       !scene_mode || !scene_have_background || !scene_previous_valid || (scene.age>=scene_health_age && !prepared_count))return 0;
    PridePreparedHistory *h=calloc(1,sizeof *h);if(!h)return 0;
    h->field=field;h->age=scene.age+field-(uint32_t)scene.last_field;
    h->health_age=scene_health_age;h->ready_age=scene_ready_age;
    h->normal_started=PrideSceneNormalStarted();h->normal_latch=PrideSceneNormalLatch();h->native_latch=s_latch_serial;
    h->width=scene_width;h->column=scene_column;h->y_offset=scene_y_offset;
    h->flip=scene_flipx;h->draws=scene_draws;h->released=scene_released;h->previous_valid=scene_previous_valid;
    h->background_field=scene_background_field;memcpy(h->previous_camera,scene_previous_camera,sizeof h->previous_camera);
    h->count=prepared_count;h->hud=prepared_hud;h->prepared_age=prepared_age;
    memcpy(&h->frame,scene_previous_frame,sizeof h->frame);memcpy(h->vram,scene_previous_vram,sizeof h->vram);
    memcpy(h->cgram,scene_cgram,sizeof h->cgram);memcpy(h->background,scene_background,sizeof h->background);
    memcpy(h->tags,scene_background_tags,sizeof h->tags);memcpy(h->pieces,prepared_pieces,sizeof h->pieces);
    memcpy(h->cub,prepared_cub,sizeof h->cub);
    memcpy(h->health,prepared_health,sizeof h->health);memcpy(h->roar,prepared_roar,sizeof h->roar);
    h->last=s_last_level;h->have_last=s_have_last;memcpy(h->map,s_last_map,sizeof h->map);memcpy(h->limits,s_last_limits,4);
    HistoryIo count={.size=SIZE_MAX,.ok=1};history_body(&count,h);
    size_t n=96+count.at;uint8_t *out=count.ok?calloc(1,n):NULL;
    if(!out) { free(h);return 0; }
    memcpy(out,"PRHHIST1",8);TlkPut32(out+8,1);TlkPut32(out+12,(uint32_t)n);TlkPut32(out+80,history_graphics());
    sha256_compute(s_rom,s_rom_size,out+16);
    HistoryIo writer={.data=out,.size=n,.at=96,.ok=1};history_body(&writer,h);free(h);
    if(!writer.ok || writer.at!=n) { free(out);return 0; }
    sha256_compute(out,n,out+48);*data=out;*size=n;return 1;
}
PridePreparedHistory *PridePreparedHistoryStage(const uint8_t *data,size_t size,uint32_t field) {
    if(!data || size<96 || size>8*1024*1024 || memcmp(data,"PRHHIST1",8) ||
       TlkGet32(data+8)!=1 || TlkGet32(data+12)!=size || !s_rom || TlkGet32(data+80)!=history_graphics())return NULL;
    for(unsigned n=84;n<96;n++)if(data[n])return NULL;
    uint8_t source[32];sha256_compute(s_rom,s_rom_size,source);if(memcmp(source,data+16,32))return NULL;
    uint8_t *copy=malloc(size);if(!copy)return NULL;memcpy(copy,data,size);memset(copy+48,0,32);
    uint8_t hash[32];sha256_compute(copy,size,hash);free(copy);if(memcmp(hash,data+48,32))return NULL;
    PridePreparedHistory *h=calloc(1,sizeof *h);if(!h)return NULL;
    HistoryIo reader={.data=(uint8_t*)data,.size=size,.at=96,.reading=1,.ok=1};history_body(&reader,h);
    if(!reader.ok || reader.at!=size || h->field!=field || h->width!=(int)TlkResourcesViewportForScene(0))goto fail;
    const char *enabled=getenv("TLK_SCENE_RENDER_ENABLE");if(!enabled || strcmp(enabled,"1"))goto fail;
    h->font=TlkResourcesNativeHudCopy();if(!h->font)goto fail;
    h->art=TlkResourcesRevivalArtCopy();
    if(!h->art)goto fail;return h;
fail: PridePreparedHistoryFree(h);return NULL;
}
void PridePreparedHistoryFree(PridePreparedHistory *h) {
    if(!h)return;TlkNativeHudFree(h->font);TlkRevivalArtFree(h->art);free(h);
}
int PrideHandoffHistoryCheck(const PridePreparedHistory *h,const TlkDeathScene *scene,
    uint32_t entry,unsigned ended,unsigned normal_latch,const uint8_t *native,size_t size) {
    if(!h || !scene || h->field<entry || h->age!=h->field-entry ||
       h->ready_age!=(scene->has_checkpoint?345u:300u) ||
       h->normal_started!=ended || h->normal_latch!=normal_latch ||
       size<36 || memcmp(native,"TLKSTAT1",8) || TlkGet32(native+12)!=h->field)return 0;
    uint64_t at=36+TlkGet64(native+24);
    if(at>size || size-at<4)return 0;
    uint32_t bytes=TlkGet32(native+(size_t)at);at+=4;
    if(bytes>size-at || !TlkWideValidateHistory(native+(size_t)at,bytes) || bytes<24)return 0;
    return TlkGet32(native+(size_t)at+20)==h->native_latch;
}
void PridePreparedHistoryCommit(PridePreparedHistory *h) {
    if(!h)return;
    if(scene_mode<0)render_init();
    /* The original logger opens with a header only at ready+1. A new-process
     * resume after that field must initialize the later append-only trace. */
    if(h->age>h->ready_age && !h->released) {
        char path[2100];snprintf(path,sizeof path,"%s/normal-owner.csv",scene_folder);
        FILE *trace=fopen(path,"w");if(!trace)exit(60);
        fprintf(trace,"field,age,normal_started,begin_latch,visible_latch,native_pose,native_pieces,normal_actor\n");
        fclose(trace);
    }
    scene_health_age=h->health_age;scene_ready_age=h->ready_age;scene_normal_actor=0;
    scene_have_background=1;scene_width=h->width;scene_column=h->column;scene_y_offset=h->y_offset;
    scene_flipx=h->flip;scene_draws=h->draws;scene_released=h->released;scene_previous_valid=h->previous_valid;
    scene_background_field=h->background_field;memcpy(scene_previous_camera,h->previous_camera,sizeof scene_previous_camera);
    memcpy(scene_previous_frame,&h->frame,sizeof h->frame);memcpy(scene_previous_vram,h->vram,sizeof h->vram);
    memcpy(scene_cgram,h->cgram,sizeof scene_cgram);memcpy(scene_background,h->background,sizeof scene_background);
    memcpy(scene_background_tags,h->tags,sizeof scene_background_tags);
    prepared_count=h->count;prepared_hud=h->hud;prepared_age=h->prepared_age;
    memcpy(prepared_pieces,h->pieces,sizeof prepared_pieces);memcpy(prepared_health,h->health,sizeof prepared_health);
    memcpy(prepared_cub,h->cub,sizeof prepared_cub);
    memcpy(prepared_roar,h->roar,sizeof prepared_roar);s_last_level=h->last;s_have_last=h->have_last;
    memcpy(s_last_map,h->map,sizeof s_last_map);memcpy(s_last_limits,h->limits,4);
    TlkNativeHudFree(prepared_native_hud);prepared_native_hud=h->font;h->font=NULL;
    TlkRevivalArtFree(scene_revival_art);scene_revival_art=h->art;h->art=NULL;
    PridePreparedHistoryFree(h);
}

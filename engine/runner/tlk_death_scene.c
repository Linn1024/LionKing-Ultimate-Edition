#include "tlk_death_scene.h"
#include "tlk_state_bytes.h"
#include "sha256.h"
#include <string.h>

#define PROGRAM_READY 0x4d444431u
static unsigned le16(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8; }
static unsigned le24(const uint8_t *p) { return le16(p)|(unsigned)p[2]<<16; }
static unsigned be24(const uint8_t *p) { return (unsigned)p[0]<<16|(unsigned)p[1]<<8|p[2]; }
static void put16(uint8_t *p,unsigned n) { p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8); }
static int zero(const uint8_t *p,size_t n) { for(size_t i=0;i<n;i++)if(p[i])return 0;return 1; }
static int rom_hash(const uint8_t *rom,size_t size,const char *hex,uint8_t *hash) {
    static const char digits[]="0123456789abcdef";
    if(!rom || size!=0x300000)return 0;
    sha256_compute(rom,size,hash);
    for(unsigned i=0;i<32;i++)if(digits[hash[i]>>4]!=hex[i*2] || digits[hash[i]&15]!=hex[i*2+1])return 0;
    return 1;
}
int TlkDeathProgramInit(TlkDeathProgram *out,const uint8_t *snes,size_t snes_size,
                       const uint8_t *md,size_t md_size) {
    if(!out)return 0;
    memset(out,0,sizeof *out);
    uint8_t identity[76]={0};memcpy(identity,"TLKDEATH003",11);
    if(!rom_hash(snes,snes_size,"457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712",identity+12) ||
       !rom_hash(md,md_size,"e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5",identity+44))return 0;
    TlkDeathProgram candidate={0};
    for(unsigned i=0;i<TLK_DEATH_TOKENS;i++) {
        const uint8_t *s=snes+0xebec+i*4,*m=md+0x7e5b2+i*4;
        if(s[0]>=128 || s[0]!=m[0])return 0;
        candidate.tokens[i]=(TlkDeathToken){le24(s+1),be24(m+1),s[0]};
        if((candidate.tokens[i].snes_pose&0x3fffff)>=snes_size || candidate.tokens[i].md_pose>=md_size)return 0;
    }
    const uint8_t *s=snes+0xebec+TLK_DEATH_TOKENS*4,*m=md+0x7e5b2+TLK_DEATH_TOKENS*4;
    if(s[0]!=255 || m[0]!=255 || (le24(s+1)&0x3fffff)!=0xec6c || be24(m+1)!=0x7e632)return 0;
    for(unsigned i=0;i<TLK_REVIVAL_TOKENS;i++) {
        const uint8_t *rs=snes+0xdedd+i*4,*rm=md+0x9786c+i*4;
        if(rs[0]!=3 || rm[0]!=rs[0])return 0;
        candidate.revival[i]=(TlkDeathToken){le24(rs+1),be24(rm+1),rs[0]};
        if((candidate.revival[i].snes_pose&0x3fffff)>=snes_size || candidate.revival[i].md_pose>=md_size)return 0;
    }
    const uint8_t *rs=snes+0xdedd+TLK_REVIVAL_TOKENS*4,*rm=md+0x9786c+TLK_REVIVAL_TOKENS*4;
    if(rs[0]!=255 || rm[0]!=255 || le24(rs+1)!=0xc0f3e6 || be24(rm+1)!=0x7e96a ||
       snes[0xf3e6]!=5 || md[0x7e96a]!=5)return 0;
    candidate.idle=(TlkDeathToken){le24(snes+0xf3e7),be24(md+0x7e96b),5};
    if((candidate.idle.snes_pose&0x3fffff)>=snes_size || candidate.idle.md_pose>=md_size)return 0;
    sha256_compute(identity,sizeof identity,candidate.identity);candidate.ready=PROGRAM_READY;
    *out=candidate;return 1;
}
void TlkDeathSceneReset(TlkDeathScene *scene) { if(scene)memset(scene,0,sizeof *scene); }
static unsigned health_age(const TlkDeathScene *s) { return s->has_checkpoint?270u:274u; }
static unsigned ready_age(const TlkDeathScene *s) { return s->has_checkpoint?345u:300u; }
static int valid(const TlkDeathScene *s,const TlkDeathProgram *p) {
    if(!s || !p || p->ready!=PROGRAM_READY || s->started>1 || s->final_life>1 || s->has_checkpoint>1)return 0;
    if(!s->started)return !s->last_field && !s->owner && !s->origin_x && !s->origin_y &&
        !s->camera_x && !s->camera_y && !s->age && !s->final_life && !s->has_checkpoint;
    return s->owner && s->age<=ready_age(s) && s->last_field>=s->age && (!s->final_life || !s->age);
}
int TlkDeathSceneBegin(TlkDeathScene *scene,const TlkDeathProgram *program,
                      const TlkDeathContext *c,uint64_t field,unsigned *events) {
    if(events)*events=0;
    if(!valid(scene,program) || scene->started || !c || c->md_selected!=1 || c->level ||
       (c->descriptor!=0xc00387 && c->descriptor!=0xc0080d) || c->cub_age || c->health || c->skip_display ||
       c->actor!=0xb213 || c->state_marker!=0xc35a82 || c->entry_pc!=0xc089b7 || !c->owner || c->final_life>1 || c->has_checkpoint>1)return 0;
    *scene=(TlkDeathScene){.last_field=field,.owner=c->owner,.origin_x=c->x,.origin_y=c->y,
        .camera_x=c->camera_x,.camera_y=c->camera_y,.started=1,.final_life=(uint8_t)c->final_life,
        .has_checkpoint=(uint8_t)c->has_checkpoint};
    if(events && scene->final_life)*events=TLK_DEATH_EVENT_GAME_OVER;
    return 1;
}
static enum TlkDeathPhase phase(const TlkDeathScene *s) {
    if(!s->started)return TLK_DEATH_NONE;
    if(s->final_life)return TLK_DEATH_GAME_OVER;
    return s->age<24?TLK_DEATH_SCENERY_FADE:s->age<225?TLK_DEATH_DISPLAY:
        s->age<249?TLK_DEATH_ACTOR_FADE:s->age<health_age(s)?TLK_DEATH_RELOAD:
        s->age<health_age(s)+26?TLK_DEATH_REVIVAL_FADE:s->age<ready_age(s)?TLK_DEATH_REVIVAL_HOLD:TLK_DEATH_READY;
}
int TlkDeathSceneAdvance(TlkDeathScene *scene,const TlkDeathProgram *program,
                        uint64_t field,unsigned paused,unsigned *events) {
    if(events)*events=0;
    if(!valid(scene,program) || !scene->started || paused>1 || field<scene->last_field)return 0;
    if(field==scene->last_field)return 1;
    if(scene->last_field==UINT64_MAX || field!=scene->last_field+1)return 0;
    scene->last_field=field;
    if(paused || scene->final_life || scene->age==ready_age(scene))return 1;
    scene->age++;
    if(events)*events=scene->age==225?TLK_DEATH_EVENT_DISPLAY_END:scene->age==249?TLK_DEATH_EVENT_BLACK:
        scene->age==254?TLK_DEATH_EVENT_REPLACE_ACTOR:scene->age==health_age(scene)?TLK_DEATH_EVENT_RESTORE_HEALTH:
        scene->age==ready_age(scene)?TLK_DEATH_EVENT_READY:
        scene->has_checkpoint && scene->age==health_age(scene)+26?TLK_DEATH_EVENT_REVIVAL_HOLD:0;
    return 1;
}
static uint16_t centered(unsigned origin,unsigned camera,unsigned target,unsigned steps) {
    int delta=(int)((origin-camera)&65535);if(delta>=32768)delta-=65536;
    int distance=(int)target-delta;
    unsigned amount=(unsigned)(distance<0?-distance:distance);
    if(amount>steps)amount=steps;
    return (uint16_t)(distance<0?origin-amount:origin+amount);
}
int TlkDeathSceneView(const TlkDeathScene *scene,const TlkDeathProgram *program,TlkDeathView *view) {
    if(!view || !valid(scene,program))return 0;
    TlkDeathView v={.phase=phase(scene),.age=scene->age,.x=scene->origin_x,.y=scene->origin_y};
    if(scene->started && !scene->final_life) {
        unsigned steps=scene->age<24?0:scene->age<225?scene->age-23:201;
        v.x=centered(scene->origin_x,scene->camera_x,160,steps);
        v.y=centered(scene->origin_y,scene->camera_y,128,steps);
        if(scene->age<249) {
            unsigned tick=scene->age<225?scene->age:224;
            for(unsigned i=0;i<TLK_DEATH_TOKENS;i++) {
                const TlkDeathToken *t=&program->tokens[i];
                if(tick<=t->duration) { v.token=i;v.timer=t->duration-tick;v.snes_pose=t->snes_pose;v.md_pose=t->md_pose;break; }
                tick-=t->duration+1;
            }
            if(!v.md_pose)return 0;
        }
    }
    *view=v;return 1;
}
int TlkDeathSceneRevivalView(const TlkDeathScene *scene,const TlkDeathProgram *program,TlkDeathRevivalView *view) {
    if(!view || !valid(scene,program))return 0;
    TlkDeathRevivalView v={0};
    if(scene->started && !scene->final_life && scene->age>=254) {
        const TlkDeathToken *token=&program->idle;
        v.prepared=1;v.timer=token->duration;v.md_cursor=0x7e96e;
        if(scene->has_checkpoint && scene->age>=270 && scene->age<344) {
            unsigned tick=scene->age<=296?0:scene->age-296;
            v.checkpoint_animation=1;v.token=tick/4;token=&program->revival[v.token];
            v.timer=token->duration-tick%4;v.md_cursor=0x97870+v.token*4;
        } else if(!scene->has_checkpoint && scene->age>=274) {
            /* Original default path advances idle once before the blocking
             * fade; it does not run the checkpoint animation hold. */
            v.timer--;
        }
        v.snes_pose=token->snes_pose;v.md_pose=token->md_pose;
    }
    *view=v;return 1;
}
int TlkDeathScenePalette(const TlkDeathScene *scene,const TlkDeathProgram *program,
                        unsigned index,unsigned death_color,unsigned next_color,uint16_t *color) {
    if(!color || !valid(scene,program) || !scene->started || scene->final_life || index>=64 || death_color>511 || next_color>511)return 0;
    unsigned age=scene->age,result=0;
    for(unsigned shift=0;shift<9;shift+=3) {
        unsigned old=(death_color>>shift)&7,next=(next_color>>shift)&7,c=0;
        if(age<225) {
            unsigned step=age<24?(age+2)/3:8;
            c=index<16?old:old>step?old-step:0;
        } else if(age<249) {
            unsigned step=(age-225+2)/3;
            c=index<16 && old>step?old-step:0;
        } else if(age>=health_age(scene)) {
            unsigned step=(age-health_age(scene))/3;
            c=next<step?next:step;
        }
        result|=c<<shift;
    }
    *color=(uint16_t)result;return 1;
}
int TlkDeathSceneSave(const TlkDeathScene *scene,const TlkDeathProgram *program,uint8_t *out,size_t size) {
    if(!out || size!=TLK_DEATH_SCENE_RECORD_SIZE || !valid(scene,program))return 0;
    uint8_t record[TLK_DEATH_SCENE_RECORD_SIZE]={0};memcpy(record,"TLKDSC01",8);
    TlkPut32(record+8,1);TlkPut32(record+12,sizeof record);memcpy(record+16,program->identity,32);
    TlkPut64(record+48,scene->last_field);TlkPut64(record+56,scene->owner);
    put16(record+64,scene->origin_x);put16(record+66,scene->origin_y);put16(record+68,scene->camera_x);put16(record+70,scene->camera_y);
    put16(record+72,scene->age);record[74]=(uint8_t)(scene->started|scene->final_life<<1|scene->has_checkpoint<<2);
    uint8_t hash[32];sha256_compute(record,sizeof record,hash);memcpy(record+96,hash,32);
    memcpy(out,record,sizeof record);return 1;
}
int TlkDeathSceneLoad(TlkDeathScene *scene,const TlkDeathProgram *program,const uint8_t *data,size_t size) {
    if(!scene || !program || program->ready!=PROGRAM_READY || !data || size!=TLK_DEATH_SCENE_RECORD_SIZE ||
       memcmp(data,"TLKDSC01",8) || TlkGet32(data+8)!=1 || TlkGet32(data+12)!=size ||
       memcmp(data+16,program->identity,32) || !zero(data+75,21) || (data[74]&~7))return 0;
    uint8_t copy[TLK_DEATH_SCENE_RECORD_SIZE],hash[32];memcpy(copy,data,size);memset(copy+96,0,32);
    sha256_compute(copy,sizeof copy,hash);if(memcmp(hash,data+96,32))return 0;
    TlkDeathScene candidate={.last_field=TlkGet64(data+48),.owner=TlkGet64(data+56),.origin_x=(uint16_t)le16(data+64),
        .origin_y=(uint16_t)le16(data+66),.camera_x=(uint16_t)le16(data+68),.camera_y=(uint16_t)le16(data+70),
        .age=(uint16_t)le16(data+72),.started=data[74]&1,.final_life=(data[74]>>1)&1,.has_checkpoint=(data[74]>>2)&1};
    if(!valid(&candidate,program))return 0;
    *scene=candidate;return 1;
}

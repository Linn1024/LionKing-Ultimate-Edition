#include "tlk_final_scene_state.h"
#include "tlk_state_bytes.h"
#include "sha256.h"
#include <stdlib.h>
#include <string.h>

static int zero(const void *data,size_t size) {
    const uint8_t *p=data;for(size_t i=0;i<size;i++)if(p[i])return 0;return 1;
}
void TlkFinalSceneStateClear(TlkFinalSceneState *s) {if(s)memset(s,0,sizeof *s);}
int TlkFinalSceneStateValid(const TlkFinalSceneState *s) {
    if(!s || !s->field || (s->flags&~511u) || (s->reload_used&~511u))return 0;
    if(!TlkTitleNavigationValid(&s->title_navigation,s->field))return 0;
    if(s->title_navigation.owner && (s->entry_field || s->title_ready_field || s->menu_credits))return 0;
    if(s->menu_credits>9 || (s->menu_credits && !s->continuation.confirmed_field))return 0;
    if(!s->entry_field) {
        if(s->age || s->flags || s->reload_used || s->continuation.confirmed_field || s->continuation.origin_descriptor)return 0;
    } else {
        if(s->entry_field>s->field || s->age!=s->field-s->entry_field || !(s->flags&TLK_FINAL_ORIGIN))return 0;
        if((s->flags&TLK_FINAL_FAST_ASSETS) && !(s->flags&TLK_FINAL_ONCE))return 0;
        if((s->flags&TLK_FINAL_TARGET) && s->age<90)return 0;
    }
    if(s->reload_used && (!s->entry_field || !(s->flags&TLK_FINAL_FAST_ASSETS) || s->age<200))return 0;
    if((s->flags&TLK_FINAL_TITLE_EXIT) &&
       (!s->entry_field || s->age<124 || !(s->flags&TLK_FINAL_TARGET) ||
        s->reload_used || s->continuation.confirmed_field))return 0;
    if(!!(s->flags&TLK_FINAL_MENU_CANVAS)!=!!s->menu_field)return 0;
    if(s->menu_field && (!s->entry_field || !(s->flags&TLK_FINAL_TARGET) ||
       (uint64_t)s->menu_field<(uint64_t)s->entry_field+124 || s->menu_field>s->field ||
       s->continuation.confirmed_field || s->reload_used))return 0;
    if(s->title_fade_field && (!s->menu_field || (uint64_t)s->title_fade_field<(uint64_t)s->entry_field+124 ||
       s->title_fade_field>s->field || s->menu_field<s->title_fade_field ||
       (uint64_t)s->menu_field>(uint64_t)s->title_fade_field+1))return 0;
    if(s->title_ready_field) {
        if(!s->entry_field || !(s->flags&TLK_FINAL_TARGET) || s->age<124 ||
           s->continuation.confirmed_field || s->reload_used || s->menu_credits ||
           s->title_previous_pad>65535 || s->title_ready_field<=s->field ||
           (uint64_t)s->title_ready_field>(uint64_t)s->field+191 ||
           (uint64_t)s->title_ready_field<(uint64_t)s->entry_field+315 ||
           (s->title_fade_field && (uint64_t)s->title_ready_field!=(uint64_t)s->title_fade_field+191))return 0;
    } else if(s->title_previous_pad)return 0;
    if(s->flags&TLK_FINAL_WAITING) {
        if(s->age<90 || s->age>=124 || s->wait_s<0x200 || s->wait_s>=0x300 || s->wait_d ||
           s->wait_a>65535 || s->wait_x>65535 || s->wait_y>65535 || s->wait_p>255 || s->wait_db>255 || s->input_stage>1)return 0;
    } else if(s->wait_a || s->wait_x || s->wait_y || s->wait_s || s->wait_d || s->wait_p || s->wait_db || s->input_stage)return 0;
    if(s->continuation.confirmed_field) {
        if(!s->entry_field || s->continuation.origin_descriptor!=0xc00387 ||
           s->continuation.confirmed_field>s->field || s->continuation.confirmed_field<s->entry_field ||
           s->continuation.confirmed_field-s->entry_field<124 || !(s->flags&TLK_FINAL_TARGET))return 0;
        TlkContinueView v;if(!TlkContinueSceneView(&s->continuation,s->field,&v))return 0;
        if((s->flags&TLK_FINAL_INPUT_STARTED) && !v.controls_ready)return 0;
    } else if(s->continuation.origin_descriptor || (s->flags&(TLK_FINAL_LEVEL|TLK_FINAL_INPUT_STARTED)))return 0;
    const unsigned present[4]={s->flags&TLK_FINAL_ORIGIN,s->flags&TLK_FINAL_TARGET,
        s->continuation.confirmed_field!=0 || s->menu_field,s->flags&TLK_FINAL_LEVEL};
    for(unsigned i=0;i<4;i++)if(!present[i] && !zero(s->canvas[i],sizeof s->canvas[i]))return 0;
    return 1;
}
static void metadata(uint8_t *p,const TlkFinalSceneState *s) {
    const uint32_t values[]={s->field,s->entry_field,s->age,s->flags,s->reload_used,s->wait_a,s->wait_x,
        s->wait_y,s->wait_s,s->wait_d,s->wait_p,s->wait_db,s->input_stage};
    for(unsigned i=0;i<13;i++)TlkPut32(p+i*4,values[i]);
    TlkPut64(p+52,s->continuation.confirmed_field);TlkPut32(p+60,s->continuation.origin_descriptor);
    TlkPut32(p+64,s->menu_field);TlkPut32(p+68,s->title_fade_field);
    TlkPut32(p+72,s->menu_credits);
    TlkPut32(p+76,s->title_ready_field);TlkPut32(p+80,s->title_previous_pad);
    TlkPut32(p+84,s->title_navigation.owner);TlkPut32(p+88,s->title_navigation.next_field);
    TlkPut32(p+92,s->title_navigation.previous_pad);
}
int TlkFinalSceneStateSave(const TlkFinalSceneState *s,const uint8_t source[32],uint8_t *out,size_t size) {
    if(!out || !source || zero(source,32) || size!=TLK_FINAL_STATE_BYTES || !TlkFinalSceneStateValid(s))return 0;
    uint8_t *candidate=calloc(1,size);if(!candidate)return 0;
    memcpy(candidate,"TLKFNL01",8);TlkPut32(candidate+8,s->title_navigation.owner?4:s->title_ready_field?3:s->menu_credits?2:1);TlkPut32(candidate+12,(uint32_t)size);
    memcpy(candidate+16,source,32);metadata(candidate+96,s);
    uint8_t *pixels=candidate+192;
    for(unsigned c=0;c<4;c++)for(unsigned i=0;i<TLK_FINAL_CANVAS_PIXELS;i++,pixels+=4)TlkPut32(pixels,s->canvas[c][i]);
    sha256_compute(candidate,size,candidate+48);memcpy(out,candidate,size);free(candidate);return 1;
}
int TlkFinalSceneStateLoad(TlkFinalSceneState *s,const uint8_t source[32],const uint8_t *data,size_t size) {
    if(!s || !source || zero(source,32) || !data || size!=TLK_FINAL_STATE_BYTES || memcmp(data,"TLKFNL01",8) ||
       (TlkGet32(data+8)<1 || TlkGet32(data+8)>4) || TlkGet32(data+12)!=size || memcmp(data+16,source,32) ||
       !zero(data+80,16) ||
       (TlkGet32(data+8)==4 ? !TlkGet32(data+180) : !zero(data+180,12)) ||
       (TlkGet32(data+8)<4 && (TlkGet32(data+8)==3 ? (!TlkGet32(data+172) || TlkGet32(data+168)!=0) :
        (!zero(data+172,8) || (TlkGet32(data+8)==1 ? TlkGet32(data+168)!=0 : TlkGet32(data+168)==0)))))return 0;
    uint8_t *copy=malloc(size);TlkFinalSceneState *candidate=calloc(1,sizeof *candidate);
    if(!copy || !candidate) {free(copy);free(candidate);return 0;}
    memcpy(copy,data,size);memset(copy+48,0,32);uint8_t hash[32];sha256_compute(copy,size,hash);free(copy);
    if(memcmp(hash,data+48,32)) {free(candidate);return 0;}
    const uint8_t *p=data+96;uint32_t *values[]={&candidate->field,&candidate->entry_field,&candidate->age,&candidate->flags,
        &candidate->reload_used,&candidate->wait_a,&candidate->wait_x,&candidate->wait_y,&candidate->wait_s,&candidate->wait_d,
        &candidate->wait_p,&candidate->wait_db,&candidate->input_stage};
    for(unsigned i=0;i<13;i++)*values[i]=TlkGet32(p+i*4);
    candidate->continuation.confirmed_field=TlkGet64(p+52);candidate->continuation.origin_descriptor=TlkGet32(p+60);
    candidate->menu_field=TlkGet32(p+64);candidate->title_fade_field=TlkGet32(p+68);
    candidate->menu_credits=TlkGet32(p+72);
    candidate->title_ready_field=TlkGet32(p+76);candidate->title_previous_pad=TlkGet32(p+80);
    candidate->title_navigation.owner=TlkGet32(p+84);candidate->title_navigation.next_field=TlkGet32(p+88);
    candidate->title_navigation.previous_pad=TlkGet32(p+92);
    const uint8_t *pixels=data+192;
    for(unsigned c=0;c<4;c++)for(unsigned i=0;i<TLK_FINAL_CANVAS_PIXELS;i++,pixels+=4)candidate->canvas[c][i]=TlkGet32(pixels);
    int ok=TlkFinalSceneStateValid(candidate);if(ok)memcpy(s,candidate,sizeof *s);free(candidate);return ok;
}

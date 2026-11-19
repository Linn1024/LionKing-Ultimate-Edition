#include "tlk_continue_scene.h"
#include <string.h>

int TlkContinueSceneBegin(TlkContinueScene *s,uint32_t origin,uint64_t field) {
    if(!s || !field || origin!=0xc00387 || s->confirmed_field)return 0;
    s->confirmed_field=field;s->origin_descriptor=origin;return 1;
}
int TlkContinueSceneView(const TlkContinueScene *s,uint64_t field,TlkContinueView *v) {
    if(!s || !v || !s->confirmed_field || s->origin_descriptor!=0xc00387 || field<s->confirmed_field)return 0;
    uint64_t age=field-s->confirmed_field;memset(v,0,sizeof *v);
    v->controls_ready=age>=309;
    if(age<209)v->phase=TLK_CONTINUE_MENU;
    else if(age<227) {v->phase=TLK_CONTINUE_FADE_OUT;v->step=(unsigned)((age-206)/3);}
    else if(age<284) {v->phase=TLK_CONTINUE_BLACK;v->step=7;}
    else if(age<302) {v->phase=TLK_CONTINUE_FADE_IN;v->step=(unsigned)((age-281)/3);}
    else {v->phase=TLK_CONTINUE_LEVEL;v->step=7;}
    return 1;
}
static unsigned component(const TlkContinueView *v,unsigned c,unsigned maximum) {
    if(!v || c>maximum || v->step>7)return 0;
    unsigned amount=(v->step*maximum+3)/7;
    if(v->phase==TLK_CONTINUE_BLACK)return 0;
    if(v->phase==TLK_CONTINUE_FADE_OUT)return c>amount?c-amount:0;
    if(v->phase==TLK_CONTINUE_FADE_IN)return c<amount?c:amount;
    return c;
}
unsigned TlkContinueSceneMdComponent(const TlkContinueView *v,unsigned c) {return component(v,c,7);}
unsigned TlkContinueSceneNativeComponent(const TlkContinueView *v,unsigned c) {return component(v,c,31);}

#include "tlk_title_navigation.h"
#include <string.h>
void TlkTitleNavigationClear(TlkTitleNavigation *s) {if(s)memset(s,0,sizeof *s);}
int TlkTitleNavigationValid(const TlkTitleNavigation *s,uint32_t field) {
    if(!s)return 0;
    if(!s->owner)return !s->next_field && !s->previous_pad;
    return field && s->owner>=0x2000 && s->owner<=0xffa0 && s->previous_pad<=65535 &&
        (!s->next_field || (s->next_field>field && (uint64_t)s->next_field<=(uint64_t)field+9));
}
uint16_t TlkTitleNavigationInput(TlkTitleNavigation *s,uint32_t field,
    uint16_t owner,uint16_t held,uint16_t native_input,unsigned selection) {
    if(!s || !field || owner<0x2000 || owner>0xffa0 || selection>1)return 0;
    if(s->owner!=owner) {
        TlkTitleNavigationClear(s);s->owner=owner;
        s->previous_pad=held&~native_input;
    }
    if(s->next_field && field<s->next_field)return 0;
    uint16_t fresh=held&~s->previous_pad;s->previous_pad=held;s->next_field=0;
    if(fresh&0x0c00) {
        if(field>0xffffffffu-9)return 0;
        s->next_field=field+9;
        /* Drive the original native branch toward the opposite selection. */
        return selection?0x0800:0x0400;
    }
    return fresh&0xd0c0;
}

#include "tlk_bonus_result_scene.h"
#include "tlk_bonus_result_data.h"
#include "tlk_md_sound.h"
#include "tlk_resources.h"
#include <string.h>
#include <stdint.h>
extern uint8_t g_ram[0x20000];
TlkBonusResultScene tlk_bonus_result_scene;
void TlkBonusResultSceneClear(void){memset(&tlk_bonus_result_scene,0,sizeof tlk_bonus_result_scene);}
void TlkBonusResultSceneBegin(unsigned count){
    TlkBonusResultSceneClear();tlk_bonus_result_scene.phase=TLK_RESULT_AUDIO1;
    tlk_bonus_result_scene.target=count>99?99:count;
}
int TlkBonusResultSceneActive(void){return tlk_bonus_result_scene.phase>=TLK_RESULT_AUDIO1 && tlk_bonus_result_scene.phase<=TLK_RESULT_CARD;}
int TlkBonusResultSceneInput(void){return tlk_bonus_result_scene.phase==TLK_RESULT_SETUP || tlk_bonus_result_scene.phase==TLK_RESULT_CARD;}
void TlkBonusResultSceneAdvance(unsigned sampled){
    TlkBonusResultScene *s=&tlk_bonus_result_scene;
    unsigned audio=TlkBonusResultDataParameter(TLK_BONUS_RAMP)+2*TlkBonusResultDataParameter(TLK_BONUS_QUIET);
    unsigned fade=TlkBonusResultDataParameter(TLK_BONUS_FADE_IN);
    if(s->phase==TLK_RESULT_AUDIO1 || s->phase==TLK_RESULT_AUDIO2){
        if(++s->age>=audio){s->phase=s->phase==TLK_RESULT_AUDIO1?TLK_RESULT_EXIT_WAIT:TLK_RESULT_SETUP;s->age=0;}
    }else if(s->phase==TLK_RESULT_EXIT_WAIT){s->phase=TLK_RESULT_FADE_OUT;s->age=0;}
    else if(s->phase==TLK_RESULT_FADE_OUT){if(++s->age>=fade-1){s->phase=TLK_RESULT_AUDIO2;s->age=0;}}
    else if(s->phase==TLK_RESULT_SETUP && sampled){s->phase=TLK_RESULT_FADE_IN;s->age=0;}
    else if(s->phase==TLK_RESULT_FADE_IN){
        if(++s->age>=fade){s->phase=TLK_RESULT_CARD;s->age=0;s->timer=TlkBonusResultDataParameter(TLK_BONUS_RESULT_TIMER);}
    }else if(s->phase==TLK_RESULT_CARD && sampled){
        s->display=s->count;
        if(s->timer<=TlkBonusResultDataParameter(TLK_BONUS_COUNT_START)){
            if(s->count<s->target)s->count++;
        }
        if(!s->timer)s->phase=TLK_RESULT_DONE;else s->timer--;
    }
}
unsigned TlkBonusResultSceneCap(void){
    TlkBonusResultScene *s=&tlk_bonus_result_scene;
    if(s->phase==TLK_RESULT_SETUP)return 0;
    if(s->phase!=TLK_RESULT_FADE_IN)return 7;
    unsigned cap=s->age/3;return cap<7?cap:7;
}
unsigned TlkBonusResultSceneLoss(void){return tlk_bonus_result_scene.phase==TLK_RESULT_FADE_OUT?tlk_bonus_result_scene.age/3+1:0;}
unsigned TlkBonusResultSceneNativeGain(void){
    TlkBonusResultScene *s=&tlk_bonus_result_scene;unsigned ramp=TlkBonusResultDataParameter(TLK_BONUS_RAMP);
    if(s->phase>=TLK_RESULT_SETUP && s->voice_sent && s->target>=20 &&
       !TlkResourcesUseMd("audio.effects.bonus.result_voice"))return 32768;
    return s->phase==TLK_RESULT_AUDIO1 && s->age<ramp?(ramp-s->age)*32768/ramp:0;
}
void TlkBonusResultSceneAudioFrame(void){
    TlkBonusResultScene *s=&tlk_bonus_result_scene;
    if(!TlkBonusResultSceneActive() || (s->audio_seen && s->audio_phase==s->phase && s->audio_age==s->age))return;
    s->audio_seen=1;s->audio_phase=s->phase;s->audio_age=s->age;
    unsigned ramp=TlkBonusResultDataParameter(TLK_BONUS_RAMP),quiet=TlkBonusResultDataParameter(TLK_BONUS_QUIET);
    if(s->phase==TLK_RESULT_AUDIO1 || s->phase==TLK_RESULT_AUDIO2){
        if(s->age && s->age<=ramp){TlkMdSoundCommand(9,s->age);TlkMdSoundCommand(10,s->age);}
        if(s->age==ramp+1){TlkMdSoundCommand(9,127);TlkMdSoundCommand(10,127);TlkMdSoundCommand(1,0);}
        if(s->age==ramp+quiet+1){TlkMdSoundCommand(9,0);TlkMdSoundCommand(10,0);}
    }
    if(s->phase>=TLK_RESULT_SETUP && !s->voice_sent){
        if(TlkResourcesUseMd("audio.effects.bonus.result_voice")) {
            s->voice_sent=1;
            if(s->target>TlkBonusResultDataParameter(TLK_BONUS_VOICE_THRESHOLD))TlkMdSoundBonusResultSample();
        }else if(s->target<20 || !(g_ram[0x1ff96]|g_ram[0x1ff97]))s->voice_sent=1;
        else {
            /* Original C5402B requests native cue7 after the qualifying
             * count reaches its end. The selected MD controller owns the
             * card timing here; retain the independently selected voice. */
            unsigned offset=g_ram[0x1f6d]|(unsigned)g_ram[0x1f6e]<<8;
            if(offset<=0x40 && g_ram[0x1fbf]==255 && g_ram[0x1fc0]==255) {
                const uint8_t packet[8]={2,7,0,0xe0,0,0x80,0x78,0};
                memcpy(g_ram+0x1f6f+offset,packet,sizeof packet);offset+=sizeof packet;
                g_ram[0x1f6d]=(uint8_t)offset;g_ram[0x1f6e]=(uint8_t)(offset>>8);s->voice_sent=1;
            }
        }
    }
}

#include "tlk_interlevel_scene.h"
#include "tlk_interlevel_data.h"
#include "tlk_resources.h"
#include "tlk_md_sound.h"
#include <string.h>
TlkInterlevelScene tlk_interlevel_scene;
void TlkInterlevelSceneClear(void){memset(&tlk_interlevel_scene,0,sizeof tlk_interlevel_scene);}
void TlkInterlevelSceneBegin(void){TlkInterlevelSceneClear();tlk_interlevel_scene.phase=TLK_INTERLEVEL_PRE;
    /* C08952 follows native D4AE/D4B8 fade and canvas teardown. Do not
     * redisplay the outgoing world or repeat its fade at this seam. */
    tlk_interlevel_scene.age=24;
}
int TlkInterlevelSceneActive(void){return tlk_interlevel_scene.phase>=TLK_INTERLEVEL_PRE && tlk_interlevel_scene.phase<=TLK_INTERLEVEL_FADE;}
int TlkInterlevelSceneInput(void){return tlk_interlevel_scene.phase==TLK_INTERLEVEL_ART || tlk_interlevel_scene.phase==TLK_INTERLEVEL_FADE;}
unsigned TlkInterlevelSceneAdvance(unsigned start_edge){
    TlkInterlevelScene *s=&tlk_interlevel_scene;unsigned events=0;
    if(s->phase==TLK_INTERLEVEL_PRE){
        /* Original fade-out24, audio-volume ramp40 and two quiet8 waits.
         * ROM decompression/DMA time adds no gameplay updates or input reads. */
        if(++s->age>=80)s->phase=TLK_INTERLEVEL_ART;
        return 0;
    }
    if(!TlkInterlevelSceneInput())return 0;
    s->tick++;unsigned e=TlkInterlevelDataEvents(s->tick);if(e)s->pending=e;
    if(s->phase==TLK_INTERLEVEL_FADE){if(++s->fade>=24)s->phase=TLK_INTERLEVEL_DONE;return 0;}
    /* Original initialization owns animation update0 (the outgoing native
     * poll already sampled). Fade-in completes24 updates including that
     * initial one; the first ordinary Start decision is update24. */
    if(s->tick>=24){
        if(start_edge || (s->pending&2)){s->phase=TLK_INTERLEVEL_FADE;s->fade=1;return 16;}
        events=s->pending&12;s->pending=0;
    }
    return events;
}
unsigned TlkInterlevelSceneCap(void){unsigned tick=tlk_interlevel_scene.tick;return tick?((tick-1)/3+1<7?(tick-1)/3+1:7):0;}
unsigned TlkInterlevelSceneLoss(void){return tlk_interlevel_scene.phase==TLK_INTERLEVEL_FADE?(tlk_interlevel_scene.fade-1)/3+1:0;}
#include "tlk_cliff_scene.inc"
int TlkInterlevelSceneAudioSelected(void){return TlkCliffSceneAudioSelected() || (TlkInterlevelSceneActive() && TlkResourcesUseMd("audio.effects.interlevel.pride_lands"));}
void TlkInterlevelSceneAudioFrame(void){
    if(TlkCliffSceneActive()){CliffAudioFrame();return;}
    static unsigned previous_phase,previous_age;
    TlkInterlevelScene *s=&tlk_interlevel_scene;
    if(!TlkInterlevelSceneAudioSelected()){previous_phase=previous_age=0;return;}
    if(s->phase==previous_phase && s->age==previous_age)return;
    previous_phase=s->phase;previous_age=s->age;
    if(s->phase==TLK_INTERLEVEL_PRE && s->age>=25 && s->age<=64){
        unsigned volume=s->age-24;TlkMdSoundCommand(9,volume);TlkMdSoundCommand(10,volume);
    }
    if(s->phase==TLK_INTERLEVEL_PRE && s->age==65){
        TlkMdSoundCommand(9,127);TlkMdSoundCommand(10,127);TlkMdSoundCommand(1,0);
    }
    if(s->phase==TLK_INTERLEVEL_ART && s->tick==0){TlkMdSoundCommand(9,0);TlkMdSoundCommand(10,0);}
}

/* Native scene lifecycle translated from MD1CAD9C/1CAF00/1A60E8. */
TlkCliffScene tlk_cliff_scene;
void TlkCliffSceneClear(void){memset(&tlk_cliff_scene,0,sizeof tlk_cliff_scene);}
void TlkCliffSceneBegin(void){TlkCliffSceneClear();tlk_cliff_scene.phase=TLK_CLIFF_PRE;}
int TlkCliffSceneActive(void){return tlk_cliff_scene.phase>=TLK_CLIFF_PRE && tlk_cliff_scene.phase<=TLK_CLIFF_FADEOUT;}
int TlkCliffSceneInput(void){return tlk_cliff_scene.phase==TLK_CLIFF_INIT || tlk_cliff_scene.phase==TLK_CLIFF_ART;}
int TlkCliffSceneAudioSelected(void){return TlkCliffSceneActive() && TlkResourcesUseMd("audio.effects.interlevel.stampede");}
void TlkCliffSceneWait(void){
    TlkCliffScene *s=&tlk_cliff_scene;
    if(s->phase==TLK_CLIFF_PRE && ++s->age==56){s->phase=TLK_CLIFF_INIT;s->age=0;}
    else if(s->phase==TLK_CLIFF_FADEIN && ++s->age==26){s->phase=TLK_CLIFF_ART;s->age=0;}
    else if(s->phase==TLK_CLIFF_FADEOUT && ++s->age==24){
        if(TlkCliffSceneAudioSelected())TlkMdSoundCliffStop();s->phase=TLK_CLIFF_DONE;
    }
}
void TlkCliffSceneAdvance(unsigned start){
    TlkCliffScene *s=&tlk_cliff_scene;
    if(s->phase==TLK_CLIFF_INIT){s->phase=TLK_CLIFF_FADEIN;s->age=s->tick=0;return;}
    if(s->phase!=TLK_CLIFF_ART)return;
    /* Phase2 is observed by1A6126 on the next actor update. The same loop
     * owns the held-Start decision at1CAF12. No pause flag or pad is erased. */
    unsigned finish=s->pending&4;
    if(!finish){s->tick++;s->pending=TlkInterlevelDataCliffEvents(s->tick);}
    if(start || finish){if(TlkCliffSceneAudioSelected())TlkMdSoundInterlevelStop();s->phase=TLK_CLIFF_FADEOUT;s->age=0;}
}
unsigned TlkCliffSceneCap(void){return tlk_cliff_scene.phase==TLK_CLIFF_FADEIN?(tlk_cliff_scene.age/3+1<7?tlk_cliff_scene.age/3+1:7):7;}
unsigned TlkCliffSceneLoss(void){return tlk_cliff_scene.phase==TLK_CLIFF_FADEOUT?tlk_cliff_scene.age/3+1:0;}
static void CliffAudioFrame(void){
    static unsigned phase,age;
    TlkCliffScene *s=&tlk_cliff_scene;
    if(!TlkCliffSceneAudioSelected()){phase=age=0;return;}
    if(phase==s->phase && age==s->age)return;phase=s->phase;age=s->age;
    if(phase==TLK_CLIFF_PRE && age>=1 && age<=40){TlkMdSoundCommand(9,age);TlkMdSoundCommand(10,age);}
    if(phase==TLK_CLIFF_PRE && age==41){TlkMdSoundCommand(9,127);TlkMdSoundCommand(10,127);TlkMdSoundCommand(1,0);}
    if(phase==TLK_CLIFF_PRE && age==49){TlkMdSoundCommand(9,0);TlkMdSoundCommand(10,0);}
    if(phase==TLK_CLIFF_FADEIN && age==25)TlkMdSoundCliffSample();
}

#ifndef TLK_BONUS_RESULT_SCENE_H
#define TLK_BONUS_RESULT_SCENE_H
enum { TLK_RESULT_OFF,TLK_RESULT_AUDIO1,TLK_RESULT_EXIT_WAIT,TLK_RESULT_FADE_OUT,
       TLK_RESULT_AUDIO2,TLK_RESULT_SETUP,TLK_RESULT_FADE_IN,TLK_RESULT_CARD,TLK_RESULT_DONE };
typedef struct {
    unsigned phase,age,target,count,display,timer,audio_seen,audio_phase,audio_age,native_stopped,voice_sent;
} TlkBonusResultScene;
extern TlkBonusResultScene tlk_bonus_result_scene;
void TlkBonusResultSceneClear(void);
void TlkBonusResultSceneBegin(unsigned count);
int TlkBonusResultSceneActive(void);
int TlkBonusResultSceneInput(void);
void TlkBonusResultSceneAdvance(unsigned sampled);
unsigned TlkBonusResultSceneCap(void);
unsigned TlkBonusResultSceneLoss(void);
unsigned TlkBonusResultSceneNativeGain(void);
void TlkBonusResultSceneAudioFrame(void);
#endif

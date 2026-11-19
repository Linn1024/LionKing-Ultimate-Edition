#ifndef TLK_INTERLEVEL_SCENE_H
#define TLK_INTERLEVEL_SCENE_H
enum { TLK_INTERLEVEL_OFF,TLK_INTERLEVEL_PRE,TLK_INTERLEVEL_ART,TLK_INTERLEVEL_FADE,TLK_INTERLEVEL_DONE };
typedef struct {unsigned phase,age,tick,fade,pending;} TlkInterlevelScene;
extern TlkInterlevelScene tlk_interlevel_scene;
void TlkInterlevelSceneBegin(void);
void TlkInterlevelSceneClear(void);
unsigned TlkInterlevelSceneAdvance(unsigned start_edge);
int TlkInterlevelSceneActive(void);
int TlkInterlevelSceneInput(void);
unsigned TlkInterlevelSceneCap(void);
unsigned TlkInterlevelSceneLoss(void);
void TlkInterlevelSceneAudioFrame(void);
int TlkInterlevelSceneAudioSelected(void);
enum { TLK_CLIFF_OFF,TLK_CLIFF_PRE,TLK_CLIFF_INIT,TLK_CLIFF_FADEIN,TLK_CLIFF_ART,TLK_CLIFF_FADEOUT,TLK_CLIFF_DONE };
typedef struct {unsigned phase,age,tick,pending;} TlkCliffScene;
extern TlkCliffScene tlk_cliff_scene;
void TlkCliffSceneClear(void);
void TlkCliffSceneBegin(void);
int TlkCliffSceneActive(void);
int TlkCliffSceneInput(void);
void TlkCliffSceneWait(void);
void TlkCliffSceneAdvance(unsigned start);
unsigned TlkCliffSceneCap(void);
unsigned TlkCliffSceneLoss(void);
int TlkCliffSceneAudioSelected(void);
#endif

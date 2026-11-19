#ifndef TLK_LATE_SCENE_DATA_H
#define TLK_LATE_SCENE_DATA_H
#include <stddef.h>
#include <stdint.h>
/* Installation owns decoding. Playback imports only these validated records. */
int TlkLateSceneDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
int TlkLateSceneDataReady(void);
size_t TlkLateSceneDataRecordSize(void);
int TlkLateSceneDataWrite(uint8_t *,size_t);
int TlkLateSceneDataRead(const uint8_t *,size_t,int);
/* Active/release bits and native/MD left-release arithmetic operands. */
const uint16_t *TlkLateSceneAdultLedgeRules(void);
const uint16_t *TlkLateSceneReturnDoorRules(void);
/* Native wait, MD count-up initial/limit, reserved zero. */
const uint16_t *TlkLateSceneReturnExitRules(void);
int TlkLateSceneScarActivation(unsigned descriptor,unsigned *native_callback,unsigned *md_callback);
const uint16_t *TlkLateSceneScarRevealRules(void);
int TlkLateSceneHyenaBounds(unsigned pose,unsigned cursor,unsigned side,unsigned *native,unsigned *md);
/* Changed Return doorway spawn lists; raw native slots guard ordinary loads. */
int TlkLateSceneReturnHyenas(unsigned door,unsigned *pointer,unsigned *native_count,unsigned *md_count);
int TlkLateSceneReturnHyenaPosition(unsigned door,unsigned slot,unsigned side,unsigned native,unsigned *md);
int TlkLateSceneTerrain(unsigned level,unsigned cell,unsigned live,unsigned height,
    unsigned native_column,unsigned md_column,unsigned native,unsigned *md);
int TlkLateSceneMarker(unsigned level,unsigned cell,unsigned live,unsigned native,unsigned *md);
#endif

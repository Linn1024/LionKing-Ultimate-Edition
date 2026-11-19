#ifndef TLK_NEXT_SCENE_DATA_H
#define TLK_NEXT_SCENE_DATA_H
#include <stdint.h>
#include <stddef.h>
int TlkNextSceneDataReady(void);
int TlkNextSceneDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
size_t TlkNextSceneDataRecordSize(void);
int TlkNextSceneDataWrite(uint8_t *,size_t);
int TlkNextSceneDataRead(const uint8_t *,size_t,int);
const uint16_t *TlkNextSceneMdPalette(unsigned level);
const uint16_t *TlkNextSceneNativeObj(unsigned level,unsigned bank);
const uint16_t *TlkNextSceneStampedeBg(void);
const uint16_t *TlkNextScenePrideRockPhase(unsigned phase);
const uint16_t *TlkNextScenePrideRockRainTarget(void);
/* Source MD3-bit channel steps followed by the existing RGB555 conversion. */
int TlkNextScenePrideRockRainColors(unsigned phase,unsigned step,uint16_t result[64]);
/* Prepared fixed H32 Stampede planes; token bit7 is high background priority. */
const uint8_t *TlkNextSceneStampedeFrame(unsigned phase);
uint16_t TlkNextSceneStampedeColor(unsigned index,int md);
/* Fourteen values: prior bounds/lane operands, native/MD damage, contact
 * lower/exclusive upper depths, and native/MD rock perspective divisors. */
const uint32_t *TlkNextSceneStampedeRules(void);
int TlkNextSceneStampedeBox(unsigned pose,unsigned component,unsigned *native,unsigned *external);
/* Three paired falling-rock poses; body operands prepared at installation. */
int TlkNextSceneExileRockBounds(unsigned pose,unsigned component,unsigned *native,unsigned *external);
int TlkNextSceneExileGrip(unsigned pose,unsigned axis,unsigned *native,unsigned *external);
int TlkNextSceneExileWallMask(unsigned left,unsigned *native,unsigned *external);
/* A point query may index the native and MD height profiles differently. */
int TlkNextSceneTerrainPoint(unsigned level,unsigned cell,unsigned live,unsigned native_column,unsigned md_column,unsigned native,unsigned *external);
int TlkNextSceneTerrain(unsigned level,unsigned cell,unsigned live,unsigned height,unsigned column,unsigned native,unsigned *external);
int TlkNextSceneHakunaMarker(unsigned marker,unsigned cell,unsigned live,unsigned native,unsigned *external);
/* Native first/split hold, MD first hold, native/MD second hold, reserved. */
const uint16_t *TlkNextSceneHakunaDefeat(void);
int TlkNextSceneDestinyBoulderTop(unsigned *native,unsigned *md);
int TlkNextSceneDestinyMarker(unsigned cell,unsigned live,unsigned native,unsigned *external);
int TlkNextSceneDestinyMonkeyMarker(unsigned cell,unsigned live,unsigned native,unsigned *external);
int TlkNextSceneSimbaPoint(unsigned pose,unsigned axis,unsigned *native,unsigned *external);
int TlkNextSceneAdultTurn(unsigned *native,unsigned *external);
int TlkNextSceneDestinyBoulderMarker(unsigned cell,unsigned live,unsigned native,unsigned *external);
int TlkNextSceneDestinyBoulderSurface(unsigned right,unsigned *native,unsigned *external);
int TlkNextSceneAdultRoar(unsigned *native,unsigned *external);
int TlkNextSceneDestinyArenaRadius(unsigned *native,unsigned *external);
int TlkNextSceneDestinyExitStart(unsigned *,unsigned *);
int TlkNextSceneBonusSelection(unsigned next_main,unsigned *level);
int TlkNextSceneBePreparedRock(unsigned cell,unsigned live,unsigned native,unsigned *external);
#endif

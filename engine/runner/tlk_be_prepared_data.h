#ifndef TLK_BE_PREPARED_DATA_H
#define TLK_BE_PREPARED_DATA_H
#include <stddef.h>
#include <stdint.h>
int TlkBePreparedDataPrepare(const uint8_t*,size_t,const uint8_t*,size_t);
int TlkBePreparedDataReady(void);
size_t TlkBePreparedDataRecordSize(void);
int TlkBePreparedDataWrite(uint8_t*,size_t);
int TlkBePreparedDataRead(const uint8_t*,size_t,int);
int TlkBePreparedBodyBounds(unsigned descriptor,unsigned pose,unsigned side,unsigned *native,unsigned *md);
int TlkBePreparedEmitterMarker(unsigned cell,unsigned native_word,unsigned native_marker,unsigned *md_marker);
const uint16_t *TlkBePreparedSpreadRules(void);
int TlkBePreparedGeyserInitialization(unsigned *native_callback,unsigned *md_callback);
enum {
    TLK_BP_NATIVE_SPEED_FRACTION,TLK_BP_MD_SPEED_FRACTION,
    TLK_BP_NATIVE_SPEED_WHOLE,TLK_BP_MD_SPEED_WHOLE,TLK_BP_NATIVE_WAIT,
    TLK_BP_LEADER_PERIOD,TLK_BP_LEADER_Y_OFFSET,TLK_BP_FAR_DISTANCE,
    TLK_BP_WAKE_X,TLK_BP_WAKE_Y,TLK_BP_INITIAL_X,TLK_BP_INITIAL_Y,
    TLK_BP_TARGET_Y_OFFSET,TLK_BP_TARGET_X_OFFSET,TLK_BP_LEAPER_RULES
};
const uint16_t *TlkBePreparedLeaperRules(void);
enum {
    TLK_BP_SOUND_NATIVE_EVENT,TLK_BP_SOUND_NATIVE_PAN,TLK_BP_SOUND_NATIVE_VOLUME,
    TLK_BP_SOUND_MD_REQUEST,TLK_BP_SOUND_MD_SELECTOR,TLK_BP_SOUND_MD_SAMPLE,
    TLK_BP_SOUND_MD_PARAMETER,TLK_BP_SOUND_NATIVE_EVENT_FLAG,TLK_BP_SOUND_RULES
};
const uint16_t *TlkBePreparedGroupSoundRules(void);
#endif

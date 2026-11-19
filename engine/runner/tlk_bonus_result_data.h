#ifndef TLK_BONUS_RESULT_DATA_H
#define TLK_BONUS_RESULT_DATA_H
#include <stddef.h>
#include <stdint.h>
enum { TLK_BONUS_RAMP, TLK_BONUS_QUIET, TLK_BONUS_FADE_IN,
       TLK_BONUS_RESULT_TIMER, TLK_BONUS_COUNT_START, TLK_BONUS_VOICE_THRESHOLD };
int TlkBonusResultDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
void TlkBonusResultDataClear(void);
int TlkBonusResultDataReady(void);
size_t TlkBonusResultDataRecordSize(void);
int TlkBonusResultDataWrite(uint8_t *,size_t);
int TlkBonusResultDataRead(const uint8_t *,size_t,int);
unsigned TlkBonusResultDataParameter(unsigned);
int TlkBonusResultDataRender(unsigned count,unsigned md,unsigned cap,unsigned loss,unsigned width,uint32_t *);
#endif

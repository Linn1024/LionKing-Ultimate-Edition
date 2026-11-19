#ifndef TLK_DESTINY_MONKEY_DATA_H
#define TLK_DESTINY_MONKEY_DATA_H
#include <stddef.h>
#include <stdint.h>
/* Logical animation cursors, consumed only by the scoped monkey adapter.
 * No executable code or runtime cartridge reader is stored in this record. */
enum { TLK_MONKEY_STREAMS=6, TLK_MONKEY_STREAM_STRIDE=256,
       TLK_MONKEY_STREAM_BASE=0xc2f100,
       TLK_MONKEY_IDLE=0, TLK_MONKEY_SHOOT, TLK_MONKEY_MOVE,
       TLK_MONKEY_STOP, TLK_MONKEY_DEAD, TLK_MONKEY_AUX,
       TLK_MONKEY_INITIAL_WAIT=0, TLK_MONKEY_SHOOT_WAIT,
       TLK_MONKEY_MOVE_WAIT, TLK_MONKEY_SHOOT_CUE,
       TLK_MONKEY_MOVE_CUE, TLK_MONKEY_PROJECTILE_SPEED };
void TlkDestinyMonkeyDataClear(void);
int TlkDestinyMonkeyDataReady(void);
int TlkDestinyMonkeyDataPrepare(const uint8_t *,size_t,const uint8_t *,size_t);
size_t TlkDestinyMonkeyDataRecordSize(void);
int TlkDestinyMonkeyDataWrite(uint8_t *,size_t);
int TlkDestinyMonkeyDataRead(const uint8_t *,size_t,int);
int TlkDestinyMonkeyByte(unsigned,unsigned *);
unsigned TlkDestinyMonkeyStream(unsigned);
unsigned TlkDestinyMonkeyParameter(unsigned);
#endif

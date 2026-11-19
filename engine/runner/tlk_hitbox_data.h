#ifndef TLK_HITBOX_DATA_H
#define TLK_HITBOX_DATA_H
#include <stddef.h>
#include <stdint.h>
void TlkHitboxDataClear(void);
int TlkHitboxDataInit(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn);
int TlkHitboxDataReady(void);
/* enemy=0 is Simba, enemy=1 is a reviewed Pride enemy, enemy=2 is a reviewed Graveyard vulture.
 * enemy=5 is a reviewed Can't Wait rhino tail; enemy=7 is a Hunt bug.
 * enemy=8 is a reviewed Hakuna gorilla pose.
 * Components are original signed
 * left/top/right/bottom header words. */
int TlkHitboxDataGet(unsigned pose,unsigned enemy,unsigned component,unsigned *native,unsigned *md);
size_t TlkHitboxDataRecordSize(void);
int TlkHitboxDataWrite(uint8_t *data,size_t size);
int TlkHitboxDataRead(const uint8_t *data,size_t size,int apply);
size_t TlkHitboxDataPolicySize(void);
int TlkHitboxDataPolicyWrite(uint8_t *data,size_t size);
#endif

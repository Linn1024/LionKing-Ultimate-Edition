#include "tlk_pride_data.h"
#include "tlk_data_record.h"
#include "tlk_start_data.h"
#include "tlk_reactivation_data.h"
#include "tlk_hitbox_data.h"
#include "tlk_roar_data.h"
#include "tlk_graveyard_data.h"
#include "tlk_next_scene_data.h"
#include "tlk_late_scene_data.h"
#include "tlk_be_prepared_data.h"
#include "tlk_interlevel_data.h"
#include "tlk_bonus_result_data.h"
#include "tlk_cant_wait_data.h"
#include "tlk_hunt_data.h"
#include "tlk_destiny_monkey_data.h"
#include <string.h>
static size_t (*const sizes[])(void)={TlkStartDataRecordSize,TlkReactivationDataRecordSize,TlkHitboxDataRecordSize,TlkRoarDataRecordSize,TlkGraveyardDataRecordSize,TlkNextSceneDataRecordSize,TlkInterlevelDataRecordSize,TlkBonusResultDataRecordSize,TlkCantWaitDataRecordSize,TlkHuntDataSize,TlkDestinyMonkeyDataRecordSize,TlkLateSceneDataRecordSize,TlkBePreparedDataRecordSize};
static int (*const writers[])(uint8_t *,size_t)={TlkStartDataWrite,TlkReactivationDataWrite,TlkHitboxDataWrite,TlkRoarDataWrite,TlkGraveyardDataWrite,TlkNextSceneDataWrite,TlkInterlevelDataWrite,TlkBonusResultDataWrite,TlkCantWaitDataWrite,TlkHuntDataWrite,TlkDestinyMonkeyDataWrite,TlkLateSceneDataWrite,TlkBePreparedDataWrite};
static int (*const readers[])(const uint8_t *,size_t,int)={TlkStartDataRead,TlkReactivationDataRead,TlkHitboxDataRead,TlkRoarDataRead,TlkGraveyardDataRead,TlkNextSceneDataRead,TlkInterlevelDataRead,TlkBonusResultDataRead,TlkCantWaitDataRead,TlkHuntDataRead,TlkDestinyMonkeyDataRead,TlkLateSceneDataRead,TlkBePreparedDataRead};
enum { SECTIONS=sizeof sizes/sizeof sizes[0],HEADER=16+SECTIONS*4 };
#ifdef TLK_INTERLEVEL_PREPARER
int TlkPrideDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn) {
    return TlkStartDataInit(s,sn,m,mn) && TlkReactivationDataInit(s,sn,m,mn) && TlkHitboxDataInit(s,sn,m,mn) && TlkRoarDataInit(s,sn,m,mn) && TlkGraveyardDataPrepare(s,sn,m,mn) && TlkNextSceneDataPrepare(s,sn,m,mn) && TlkInterlevelDataPrepare(s,sn,m,mn) && TlkBonusResultDataPrepare(s,sn,m,mn) && TlkCantWaitDataInit(s,sn,m,mn) && TlkHuntDataPrepare(s,sn,m,mn) && TlkDestinyMonkeyDataPrepare(s,sn,m,mn) && TlkLateSceneDataPrepare(s,sn,m,mn) && TlkBePreparedDataPrepare(s,sn,m,mn);
}
#endif
size_t TlkPrideDataRecordSize(void) {
    size_t total=HEADER;for(unsigned i=0;i<SECTIONS;i++){size_t size=sizes[i]();if(!size)return 0;total+=size;}return total;
}
int TlkPrideDataWrite(uint8_t *data,size_t size) {
    if(!data || !TlkPrideDataRecordSize() || size!=TlkPrideDataRecordSize())return 0;
    memcpy(data,"TLKPRD01",8);TlkDataPut32(data+8,28);TlkDataPut32(data+12,(uint32_t)size);size_t at=HEADER;
    for(unsigned i=0;i<SECTIONS;i++){size_t n=sizes[i]();TlkDataPut32(data+16+i*4,(uint32_t)n);if(!writers[i](data+at,n))return 0;at+=n;}return at==size;
}
int TlkPrideDataRead(const uint8_t *data,size_t size,int apply) {
    if(!data || size<HEADER || memcmp(data,"TLKPRD01",8) || TlkDataGet32(data+8)!=28 || TlkDataGet32(data+12)!=size)return 0;
    size_t at=HEADER;for(unsigned i=0;i<SECTIONS;i++){size_t n=TlkDataGet32(data+16+i*4);if(n>size-at || !readers[i](data+at,n,0))return 0;at+=n;}
    if(at!=size)return 0;
    if(apply){at=HEADER;for(unsigned i=0;i<SECTIONS;i++){size_t n=TlkDataGet32(data+16+i*4);if(!readers[i](data+at,n,1))return 0;at+=n;}}return 1;
}

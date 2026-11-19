#ifndef PRIDE_PREPARED_HISTORY_API_H
#define PRIDE_PREPARED_HISTORY_API_H
#include <stddef.h>
#include <stdint.h>
typedef struct PridePreparedHistory PridePreparedHistory;
int PridePreparedHistorySave(uint32_t field,uint8_t **data,size_t *size);
PridePreparedHistory *PridePreparedHistoryStage(const uint8_t *data,size_t size,uint32_t field);
void PridePreparedHistoryCommit(PridePreparedHistory *history);
void PridePreparedHistoryFree(PridePreparedHistory *history);
#endif

#ifndef TLK_FINAL_ART_PREPARE_H
#define TLK_FINAL_ART_PREPARE_H
#include <stddef.h>
#include <stdint.h>
/* Installer-only API. Decode verified ROM into an owned portable asset record.
 * Caller frees *record. Failure leaves both outputs empty. */
int TlkFinalArtPrepare(const uint8_t *rom,size_t size,const uint32_t *frames,unsigned count,
                      uint8_t **record,size_t *record_size);
/* Installer inventory from the original menu descriptors, animation streams,
 * digit table and animated credit icon. No research captures are inputs. */
int TlkFinalArtPrepareMenus(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size);
int TlkFinalArtPrepareMenuSources(const uint8_t *md,size_t md_size,const uint8_t *snes,size_t snes_size,
                                 uint8_t **record,size_t *record_size);
#endif

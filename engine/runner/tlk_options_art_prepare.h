#ifndef TLK_OPTIONS_ART_PREPARE_H
#define TLK_OPTIONS_ART_PREPARE_H
#include <stddef.h>
#include <stdint.h>
/* Installer-only original MD Options recipe. Never linked into gameplay. */
int TlkOptionsArtPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size);
/* Original MD sound-test backdrop and sixteen name/program records. The menu
 * reader/runtime will consume this separately; preparation alone is no UI. */
int TlkOptionsSoundTestPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size);
int TlkOptionsDebugMenuPrepare(const uint8_t *rom,size_t size,uint8_t **record,size_t *record_size);
#endif

#ifndef TLK_CONTACT_MAP_H
#define TLK_CONTACT_MAP_H
#include <stdint.h>
#include <stddef.h>
void TlkContactMapClear(void);
int TlkContactMapInit(const uint8_t *snes,size_t snes_size,const uint8_t *md,size_t md_size);
int TlkContactMapReady(void);
unsigned TlkContactMapRowBytes(void);
int TlkContactMapAttribute(unsigned cell,unsigned live_word,unsigned native_attribute,unsigned *attribute);
/* Install-time record: 8000 LE native words, native tags, then MD tags. */
enum { TLK_CONTACT_MAP_BYTES=32000 };
int TlkContactMapExport(uint8_t *data,size_t size);
int TlkContactMapImport(const uint8_t *data,size_t size);
#endif

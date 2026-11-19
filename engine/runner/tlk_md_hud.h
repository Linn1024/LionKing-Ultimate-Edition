#ifndef TLK_MD_HUD_H
#define TLK_MD_HUD_H
#include <stddef.h>
#include <stdint.h>
int TlkMdHudInit(const uint8_t *rom,size_t size);
int TlkMdHudReady(void);
/* Original left roar and right health meter generation, 704 packed bytes. */
int TlkMdHudGenerate(unsigned kind,int maximum,int current,uint8_t *out,size_t capacity);
void TlkMdHudPrepare(int roar_max,int roar_current,int health_max,int health_current,unsigned lives);
/* Render-only selection; the saved native age determines the portrait. */
void TlkMdHudSetAdult(int adult);
int TlkMdHudHealthMaximum(void);
int TlkMdHudLifeReady(void);
/* Local original MD frame coordinates: 0 roar, 1 health, 2 portrait/counter. */
unsigned TlkMdHudPixel(unsigned kind,int x,int y);
#endif

#ifndef TLK_NATIVE_HUD_H
#define TLK_NATIVE_HUD_H
#include <stddef.h>
#include <stdint.h>
typedef struct TlkNativeHud TlkNativeHud;
enum { TLK_NATIVE_HUD_ROAR=0, TLK_NATIVE_HUD_HEALTH=1, TLK_NATIVE_HUD_BYTES=512 };
/* Owns original native meter glyph tables; verifies the complete pinned ROM.
 * No ROM, WRAM, VRAM or CPU pointer is retained. */
TlkNativeHud *TlkNativeHudCreate(const uint8_t *rom,size_t size);
/* Prepared immutable glyph bytes, independent copies for revived/saved scenes. */
TlkNativeHud *TlkNativeHudLoad(const uint8_t *record,size_t size);
TlkNativeHud *TlkNativeHudReadFile(const char *path);
TlkNativeHud *TlkNativeHudClone(const TlkNativeHud *hud);
/* Installer-only, with TLK_NATIVE_HUD_PREPARE. */
int TlkNativeHudPrepare(const uint8_t *rom,size_t bytes,uint8_t **record,size_t *size);
void TlkNativeHudFree(TlkNativeHud *hud);
/* Build the original full/restored widget, not an arbitrary current value.
 * Existing512-byte font includes its original left border and trailing data.
 * Native code's different conditional trailing-clear tests are preserved.
 * Health maximum4..12; roar maximum8..64. Atomic on rejection; alias-safe. */
int TlkNativeHudRestored(const TlkNativeHud *hud,unsigned kind,unsigned maximum,
                         const uint8_t previous[TLK_NATIVE_HUD_BYTES],uint8_t out[TLK_NATIVE_HUD_BYTES]);
/* Original roar builder for current0..maximum, maximum8..64. initial_full is
 * the caller's original16-bit scratch transition flag ($21); it affects the
 * first empty boundary and wraps on full segments exactly as the CPU does.
 * Preserves the previous border/trailing bytes and conditional clear. Atomic
 * on rejection; alias-safe. Does not choose or modify gameplay counters. */
int TlkNativeHudRoarCurrent(const TlkNativeHud *hud,unsigned maximum,unsigned current,
                           uint16_t initial_full,const uint8_t previous[TLK_NATIVE_HUD_BYTES],
                           uint8_t out[TLK_NATIVE_HUD_BYTES]);
#endif

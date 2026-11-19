#ifndef TLK_FINAL_NATIVE_H
#define TLK_FINAL_NATIVE_H
#include <stddef.h>
#include <stdint.h>

enum { TLK_FINAL_NATIVE_COUNT=20,TLK_FINAL_NATIVE_RELOAD_COUNT=9,
       TLK_FINAL_NATIVE_TITLE_FIRST=10,TLK_FINAL_NATIVE_TITLE_COUNT=10 };
typedef struct TlkFinalNative TlkFinalNative;
typedef struct TlkFinalNativeRecipe {
    uint32_t source,destination,source_end,destination_end,size;
} TlkFinalNativeRecipe;
/* Reviewed semantic substitutions:0 final-menu bank,1..9 Continue reloads,
 * 10..19 startup/title data used by the selected final-scene return.
 * Source end0 means the original caller replaces it; no pointer update is used. */
const TlkFinalNativeRecipe *TlkFinalNativeRecipeAt(unsigned index);
/* Play-side package reader. Owns its bytes; no ROM decoding/preparation fallback. */
TlkFinalNative *TlkFinalNativeLoad(const uint8_t *record,size_t size);
void TlkFinalNativeFree(TlkFinalNative *assets);
const uint8_t *TlkFinalNativePayload(const TlkFinalNative *assets,unsigned index,size_t *size);
#endif

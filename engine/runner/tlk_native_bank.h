#ifndef TLK_NATIVE_BANK_H
#define TLK_NATIVE_BANK_H
#include <stddef.h>
#include <stdint.h>
typedef struct Apu Apu;
typedef struct TlkNativeBankProgram TlkNativeBankProgram;
typedef struct TlkNativeBank TlkNativeBank;
/* Immutable, owned Pride bank12 recipe. The caller supplies the actual host
 * executable/build digest; records from another codec/build are incompatible. */
TlkNativeBankProgram *TlkNativeBankProgramCreate(const uint8_t *rom,size_t size,const uint8_t build_id[32]);
void TlkNativeBankProgramFree(TlkNativeBankProgram *program);
TlkNativeBank *TlkNativeBankCreate(void);
void TlkNativeBankClear(TlkNativeBank *bank);
void TlkNativeBankFree(TlkNativeBank *bank);
int TlkNativeBankReady(const TlkNativeBank *bank,const TlkNativeBankProgram *program);
/* Caller holds the audio lock. Capture only at original quiet setup boundaries;
 * source payload, SRCN assignments and idle transfer state are checked. Failure
 * preserves a prior valid bank. No live guest/chip state is changed. */
int TlkNativeBankCapture(TlkNativeBank *bank,const TlkNativeBankProgram *program,
                         const Apu *apu,const uint8_t *wram,size_t size,uint32_t pc,uint64_t field);
/* Original Pride health-death reload boundary only. Validate a private candidate
 * before committing. Preserve live DSP/queued PCM, echo history, chip clocks and
 * directory entries not assigned by this source. CPU stack/return handling is
 * the caller's responsibility. Unsupported contexts reject without mutation. */
int TlkNativeBankApply(const TlkNativeBank *bank,const TlkNativeBankProgram *program,
                       Apu *apu,uint8_t *wram,size_t size,uint32_t pc);
/* Confirmed ordinary Pride Continue reload only. The caller owns proof of the
 * final-life/YES lifecycle and supplies its original scene descriptor. The
 * reviewed normal-mode entry has no player yet, zero health and two spare lives.
 * All quiet-chip, source, PCM/clock preservation and transactional checks above
 * still apply. A cold/missing cache or unsupported context rejects unchanged. */
int TlkNativeBankApplyContinue(const TlkNativeBank *bank,const TlkNativeBankProgram *program,
                               Apu *apu,uint8_t *wram,size_t size,uint32_t pc,
                               uint32_t origin_descriptor);
/* Pointer-free, versioned, source/build-bound private record. Queued PCM is not
 * stored. Load validates on an isolated chip before replacing the bank. */
size_t TlkNativeBankRecordSize(const TlkNativeBank *bank);
int TlkNativeBankSave(const TlkNativeBank *bank,const TlkNativeBankProgram *program,uint8_t *out,size_t size);
int TlkNativeBankLoad(TlkNativeBank *bank,const TlkNativeBankProgram *program,const uint8_t *data,size_t size);
#endif

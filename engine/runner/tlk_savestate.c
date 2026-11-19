/* tlk_savestate.c -- savestates for both hosts (task S, docs/devlog.md).
 *
 * File layout (little-endian, this build only: the blob is the runtime's
 * in-process rollback snapshot, which has no cross-build promise):
 *   "TLKSTAT1"  u32 version  u32 host_frame
 *   u32 resume_pc  u8 wai_halted  u8 short_field  u8 late_nmi  u8 pad
 *   u64 blob_len  u32 gameplay_sources (version >= 2)  blob
 *   u32 presentation_len + presentation history (version >= 3)
 *   u32 audio_len + audio continuation history (version >= 4)
 *   (RtlRollbackSaveToMemory: guest snapshot + timing residue,
 *                       incl. g_cpu, interp bridge state, refresh carry, PPU/DMA residue)
 *
 * Taken between frames only. A fiber suspended mid-routine (task Q) cannot be
 * serialized; on load it is discarded and the driver resumes at the saved PC,
 * which exact pacing (task M) makes indistinguishable from the in-place resume. */
#include "tlk_savestate.h"

#ifdef _WIN32
#include <windows.h>
#undef FORCEINLINE
#endif
#include "tlk_resources.h"
#include "tlk_camera.h"
#include "tlk_wide.h"
#include "tlk_audio.h"
#include "common_rtl.h"
#include "cpu_state.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

uint32_t tlk_bfd_resume_pc_get(void);
void tlk_bfd_resume_pc_set(uint32_t pc);
int tlk_bfd_wai_halted_get(void);
void tlk_bfd_wai_halted_set(int v);
int tlk_snes_short_field_get(void);
void tlk_snes_short_field_set(int v);
int tlk_snes_late_nmi_get(void);
void tlk_snes_late_nmi_set(int v);
void tlk_fiber_discard(void);
extern uint64_t g_aot_pace_next;

#define TLKS_MAGIC "TLKSTAT1"
#define TLKS_VERSION 4u
#define STATE_PRIDE 0x80000000u
static char load_error[128];
const char *tlk_state_error(void) { return load_error; }
static unsigned state_word(unsigned at) { return g_ram[at]|(unsigned)g_ram[at+1]<<8; }
static uint32_t gameplay_sources(void) {
    uint32_t flags=TlkResourcesUseMd("gameplay.camera")?1u:0u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.pickups")) flags|=2u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.leaves")) flags|=4u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.contacts")) flags|=8u;
    if (TlkResourcesUseMd("gameplay.simba.roar")) flags|=16u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.start")) flags|=32u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.activation")) flags|=64u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.lizard_reactivation")) flags|=128u;
    if (TlkResourcesUseMd("gameplay.hitboxes.simba")) flags|=0x01000000u;
    if (TlkResourcesUseMd("gameplay.hitboxes.enemies")) flags|=0x02000000u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.ceiling_rows")) flags|=0x04000000u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.ceiling_clearance")) flags|=0x08000000u;
    if (TlkResourcesUseMd("gameplay.levels.pride_lands.streaming_top")) flags|=0x10000000u;
    if (flags&1) flags|=((uint32_t)TlkCameraViewWidth()&65535u)<<8;
    if (!state_word(0x1ff9e) && (state_word(0xdf)==0x387 || state_word(0xdf)==0x80d)) flags|=STATE_PRIDE;
    return flags;
}

typedef struct {
    char magic[8];
    uint32_t version, host_frame;
    uint32_t resume_pc;
    uint8_t wai_halted, short_field, late_nmi, pad;
    uint64_t blob_len;
} TlkStateHeader;

int tlk_state_save(const char *path, uint32_t host_frame) {
    size_t cap = RtlRollbackSnapshotBound();
    uint8_t *blob = (uint8_t *)malloc(cap);
    if (!blob) return 0;
    size_t n = RtlRollbackSaveToMemory(blob, cap);
    if (!n) { free(blob); return 0; }
    TlkStateHeader h;
    memset(&h, 0, sizeof h);
    memcpy(h.magic, TLKS_MAGIC, 8);
    h.version = TLKS_VERSION;
    h.host_frame = host_frame;
    h.resume_pc = tlk_bfd_resume_pc_get();
    h.wai_halted = (uint8_t)tlk_bfd_wai_halted_get();
    h.short_field = (uint8_t)tlk_snes_short_field_get();
    h.late_nmi = (uint8_t)tlk_snes_late_nmi_get();
    h.blob_len = n;
    uint32_t sources=gameplay_sources();
    uint8_t view[TLK_WIDE_HISTORY_MAX];
    uint32_t view_len=(uint32_t)TlkWideSaveHistory(view,sizeof view);
    size_t audio_size=TlkAudioHistorySize();
    uint8_t *audio=audio_size && audio_size<=TLK_AUDIO_HISTORY_MAX?malloc(audio_size):NULL;
    if(!audio || !TlkAudioSaveHistory(audio,audio_size)) { free(audio);free(blob);return 0; }
    uint32_t audio_len=(uint32_t)audio_size;
    char tmp[4096];
    snprintf(tmp, sizeof tmp, "%s.tmp", path);
    FILE *f = fopen(tmp, "wb");
    int ok = f && fwrite(&h, sizeof h, 1, f) == 1 &&
        fwrite(&sources,sizeof sources,1,f)==1 && fwrite(blob, 1, n, f) == n &&
        fwrite(&view_len,4,1,f)==1 && fwrite(view,1,view_len,f)==view_len &&
        fwrite(&audio_len,4,1,f)==1 && fwrite(audio,1,audio_len,f)==audio_len;
    if (f && fclose(f) != 0) ok = 0;
    free(blob);
    free(audio);
    if (ok) {
#ifdef _WIN32
        ok = MoveFileExA(tmp, path, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
#else
        ok = rename(tmp, path) == 0;
#endif
    }
    if (!ok) remove(tmp);
    return ok;
}

int tlk_state_load(const char *path, uint32_t *host_frame) {
    snprintf(load_error,sizeof load_error,"No saved state");
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    snprintf(load_error,sizeof load_error,"Unsupported or damaged state");
    TlkStateHeader h;
    int ok = fread(&h, sizeof h, 1, f) == 1 && !memcmp(h.magic, TLKS_MAGIC, 8) &&
             (h.version >= 1u && h.version <= TLKS_VERSION) && h.blob_len > 0 && h.blob_len < (64u << 20);
    uint32_t sources=0,current=gameplay_sources();
    if (ok && h.version>=2u) ok=fread(&sources,sizeof sources,1,f)==1;
    if (ok && h.version==1u && h.host_frame && (current&0x1f0000ffu)) {
        snprintf(load_error,sizeof load_error,"Older state: select SNES gameplay sources in F12");ok=0;
    }
    if (ok && (sources&STATE_PRIDE)) {
        if ((sources^current)&1u) {
            snprintf(load_error,sizeof load_error,"State camera source differs; match it in F12");ok=0;
        } else if ((sources^current)&2u) {
            snprintf(load_error,sizeof load_error,"State pickup source differs; match it in F12");ok=0;
        } else if ((sources^current)&4u) {
            snprintf(load_error,sizeof load_error,"State leaf behavior differs; match it in F12");ok=0;
        } else if ((sources^current)&8u) {
            snprintf(load_error,sizeof load_error,"State terrain contact source differs; match it in F12");ok=0;
        } else if ((sources^current)&16u) {
            snprintf(load_error,sizeof load_error,"State roar behavior differs; match it in F12");ok=0;
        } else if ((sources^current)&32u) {
            snprintf(load_error,sizeof load_error,"State initial position source differs; match it in F12");ok=0;
        } else if ((sources^current)&64u) {
            snprintf(load_error,sizeof load_error,"State initial enemy activation source differs; match it in F12");ok=0;
        } else if ((sources^current)&128u) {
            snprintf(load_error,sizeof load_error,"State lizard reactivation source differs; match it in F12");ok=0;
        } else if ((sources^current)&0x01000000u) {
            snprintf(load_error,sizeof load_error,"State Simba body bounds source differs; match it in F12");ok=0;
        } else if ((sources^current)&0x02000000u) {
            snprintf(load_error,sizeof load_error,"State enemy body bounds source differs; match it in F12");ok=0;
        } else if ((sources^current)&0x04000000u) {
            snprintf(load_error,sizeof load_error,"State ceiling row source differs; match it in F12");ok=0;
        } else if ((sources^current)&0x08000000u) {
            snprintf(load_error,sizeof load_error,"State ceiling clearance source differs; match it in F12");ok=0;
        } else if ((sources^current)&0x10000000u) {
            snprintf(load_error,sizeof load_error,"State streaming top margin source differs; match it in F12");ok=0;
        } else if ((sources^current)&0x00ffff00u) {
            snprintf(load_error,sizeof load_error,"State needs a %u-pixel camera viewport",(unsigned)((sources>>8)&65535u));ok=0;
        }
    }
    uint8_t *blob = ok ? (uint8_t *)malloc((size_t)h.blob_len) : NULL;
    ok = ok && blob && fread(blob, 1, (size_t)h.blob_len, f) == h.blob_len;
    uint8_t view[TLK_WIDE_HISTORY_MAX];uint32_t view_len=0;
    if (ok && h.version>=3u) {
        ok=fread(&view_len,4,1,f)==1 && view_len<=sizeof view &&
           fread(view,1,view_len,f)==view_len && TlkWideValidateHistory(view,view_len);
    }
    uint8_t *audio=NULL;uint32_t audio_len=0;
    if(ok && h.version>=4u) {
        ok=fread(&audio_len,4,1,f)==1 && audio_len && audio_len<=TLK_AUDIO_HISTORY_MAX;
        if(ok)audio=malloc(audio_len);
        ok=ok && audio && fread(audio,1,audio_len,f)==audio_len && TlkAudioValidateHistory(audio,audio_len);
    }
    if(ok && h.version>=3u)ok=fgetc(f)==EOF;
    fclose(f);
    if (!ok) { free(blob);free(audio); return 0; }
    /* Keep the current guest intact if the opaque backend rejects its record. */
    size_t old_cap=RtlRollbackSnapshotBound();uint8_t *old=malloc(old_cap);
    size_t old_size=old?RtlRollbackSaveToMemory(old,old_cap):0;
    size_t old_audio_size=TlkAudioHistorySize();
    uint8_t *old_audio=old_audio_size?malloc(old_audio_size):NULL;
    if(!old_size || !old_audio || !TlkAudioSaveHistory(old_audio,old_audio_size)) {
        free(old);free(old_audio);free(blob);free(audio);return 0;
    }
    tlk_fiber_discard();
    ok = RtlRollbackLoadFromMemory(blob, (size_t)h.blob_len);
    free(blob);
    if(ok)ok=TlkAudioLoadHistory(audio,audio_len);
    free(audio);
    if(!ok) {
        RtlRollbackLoadFromMemory(old,old_size);
        TlkAudioLoadHistory(old_audio,old_audio_size);
        free(old);free(old_audio);g_aot_pace_next=0;
        snprintf(load_error,sizeof load_error,"State audio continuation is incompatible or damaged");return 0;
    }
    free(old);free(old_audio);
    TlkWideLoadHistory(view,view_len);
    tlk_bfd_resume_pc_set(h.resume_pc);
    tlk_bfd_wai_halted_set(h.wai_halted);
    tlk_snes_short_field_set(h.short_field);
    tlk_snes_late_nmi_set(h.late_nmi);
    g_aot_pace_next = 0;
    if (host_frame) *host_frame = h.host_frame;
    load_error[0]=0;
    return 1;
}

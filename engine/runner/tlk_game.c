/* tlk_game.c -- The Lion King (SNES, USA) game adapter.
 *
 * Standard NTSC HiROM title, no coprocessor. Starts on the framework's
 * beam-aligned driver (runner/src/beam_frame_driver.h): one host frame is
 * one PPU field, interrupts are delivered where the beam latches them, and
 * the field is rasterized from the raster journal with real HDMA. Anything
 * not recompiled runs in the 65816 interpreter tier. */
#include "tlk_game.h"
#include "tlk_audio.h"
#include "tlk_camera.h"
#include "tlk_layout.h"
#include "tlk_leaves.h"
#include "tlk_terrain.h"
#include "tlk_roar.h"
#include "tlk_spawn_init.h"
#include "tlk_reactivation.h"
#include "tlk_hitboxes.h"
#include "tlk_ceiling.h"
#include "tlk_streaming_top.h"

#include "beam_frame_driver.h"

void aot_pace_diag_frame(void);  /* aot_pace.c (TLK_HWLOG) */
static void TlkRunOneFrame(void) { TlkCameraInstall(); TlkLayoutInstall(); TlkLeavesInstall(); TlkTerrainInstall(); TlkRoarInstall(); TlkSpawnInitInstall(); TlkReactivationInstall(); TlkHitboxesInstall(); TlkCeilingInstall(); TlkStreamingTopInstall(); aot_pace_diag_frame(); snes_beam_frame_driver_run_frame(); }
/* Set by tlk_wide.c while widescreen is on: sees each visible line's PPU state. */
SnesBeamRasterObserver *g_tlk_raster_observer;
static void TlkDrawPpuFrame(void) { snes_beam_frame_driver_draw_ppu_frame_observed(g_tlk_raster_observer, NULL); }
static void TlkSessionReset(void) { snes_beam_frame_driver_reset(); TlkAudioReset(); }

void TlkDecompInstall(void);  /* tlk_decomp.c */
/* Runs inside SnesInit, after the interpreter bridge exists. */
void aot_pace_diag_init(void);
static void TlkInitialize(void) { TlkDecompInstall(); TlkAudioInstall(); aot_pace_diag_init(); }

const RtlGameInfo kTlkGameInfo = {
    .title            = "tlk",
    .initialize       = &TlkInitialize,
    .run_frame        = &TlkRunOneFrame,
    .draw_ppu_frame   = &TlkDrawPpuFrame,
    .save_name_prefix = "tlk",
    .session_reset    = &TlkSessionReset,
};

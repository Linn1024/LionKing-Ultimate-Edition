#include "tlk_fallback_log.h"
/* Optional final-scene coordinator; the ordinary player host stays unchanged. */
#include <stdint.h>
#include "tlk_final_art.h"
#include "tlk_final_native.h"
#include "tlk_title_bank.h"
#include "tlk_title_navigation.h"
#include "tlk_interlevel_data.h"
#include "tlk_interlevel_scene.h"
#include "tlk_bonus_result_data.h"
#include "tlk_bonus_result_scene.h"
static void BonusResultClear(void);
static void BonusResultPaint(uint32_t *,int);
static void EndingSunrisePaint(uint32_t *,int);
static void BonusResultEnsureInstalled(void);
int BonusResultOriginCanvas(uint32_t *,int,int);
static void InterlevelPaint(uint32_t *,int);
static void InterlevelEnsureInstalled(void);
static void InterlevelClear(void);
static const char *title_bank_asset_path;
static const char *caption_asset_path;
static const char *checkpoint_asset_path;
static const char *revival_asset_path;
static const char *native_hud_asset_path;
static TlkTitleBank *title_bank_assets;
static uint8_t title_bank_asset_digest[32];
static int ContinueTitleBankAssetsLoad(const char *);
static const char *final_native_asset_path;
static TlkFinalNative *final_native_assets;
static uint8_t final_native_asset_digest[32];
static int ContinueNativeAssetsLoad(const char *);
static const char *final_menu_asset_path;
static int final_menu_art_mode;
static uint8_t final_menu_asset_digest[32];
static unsigned final_menu_confirmed_credits;
enum { NATIVE_MENU_BEGIN, NATIVE_MENU_LOOP, NATIVE_MENU_CONFIRM, NATIVE_MENU_TITLE_EXIT, NATIVE_MENU_FRAME };
static int final_menu_source_changed;
static int ContinueMenuSource(void);
static int NativeMenuOwned(void);
static void NativeMenuClear(void);
static void NativeMenuEvent(unsigned);
static void NativeMenuPaint(uint32_t *,int);
static int ContinueMenuAssetsLoad(const char *);
static void ContinueMenuCapture(const uint8_t *,uint32_t *,uint32_t *);
static void ContinueMenuPaint(uint32_t *,int);
static void ReadyTitleArtPaint(uint32_t *,int);
static void OptionsMenuPaint(uint32_t *,int);
static void OptionsMenuInstall(void);
static void TlkAttractInstall(void);
int SoundTestNativeRows(uint32_t *,int,const char [16][21]);
static void ContinueMenuConfirmedCapture(uint32_t *,uint32_t *);
void FinalSceneCaptureNative(const uint8_t *);
void FinalScenePaintNative(uint32_t *);
void FinalScenePaintWide(uint32_t *,int);
static int ContinueResourcesApplied(void);
static int ContinuePrepareBoot(char *,unsigned);
static void ContinuePublishBoot(const char *);
static int ContinueLifecycleSave(const char *,uint32_t);
static int ContinueLifecycleLoad(const char *,uint32_t *);
static int ContinueIdleBackendReady(void);
#define TLK_PRIDE_EXTRA_IDLE_SAVE_READY ContinueIdleBackendReady
#define TLK_PRIDE_EXTRA_PROFILE_RESOURCE "gameplay.levels.pride_lands.final_life"
#define __wrap_TlkResetMachine ContinuePreviousMachineReset
#define __wrap_RtlRunFrame PrideObservedRunFrame
#include "../tlk_pride_host.c"
#undef TLK_PRIDE_EXTRA_IDLE_SAVE_READY
#undef TLK_PRIDE_EXTRA_PROFILE_RESOURCE
#undef __wrap_TlkResetMachine
#undef __wrap_RtlRunFrame
#include "pride_final_assets.inc"
#include "pride_final_runtime.inc"
#include "pride_final_menu.inc"
#include "pride_ready_title_art.inc"
#include "pride_options_menu.inc"
#include "pride_final_menu_native.inc"
#include "pride_final_installed.inc"
#include "pride_interlevel.inc"
#include "pride_bonus_result.inc"

#include "pride_ending_sunrise.inc"
#include "pride_attract.inc"

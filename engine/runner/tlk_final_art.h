#ifndef TLK_FINAL_ART_H
#define TLK_FINAL_ART_H
#include <stddef.h>
#include <stdint.h>

typedef struct TlkFinalArt TlkFinalArt;
/* Play-side API: load only installer-prepared data. No ROM decode or fallback.
 * Owns all pixels/palette. This is asset infrastructure, not scene ownership,
 * animation timing or proof of complete renderer coverage. */
TlkFinalArt *TlkFinalArtLoad(const uint8_t *record,size_t size);
void TlkFinalArtFree(TlkFinalArt *art);
int TlkFinalArtBounds(const TlkFinalArt *art,uint32_t frame,int *x,int *y,int *w,int *h);
/* Original frame-local coordinates. -1 unavailable,0 transparent,1..15 index.
 * Caller owns placement, flips, palette bank, scene guards and lifetime. */
int TlkFinalArtPixel(const TlkFinalArt *art,uint32_t frame,int x,int y);
int TlkFinalArtColor(const TlkFinalArt *art,unsigned bank,unsigned index,uint16_t *rgb555);
/* Package-v2 scene information, prepared during installation. Programs:0 idle,
 * 1 exit,2 credit icon. Steps use original update counts, not video timestamps. */
int TlkFinalArtAnimation(const TlkFinalArt *art,unsigned program,uint64_t updates,uint32_t *frame);
/* Unfaded original320x224 menu; age is caller-owned final-scene age. This covers
 * the unconfirmed menu. Exit motion, scene guards and fades belong to caller.
 * Failure requests installation repair; there is no ROM or native-art fallback. */
int TlkFinalArtDrawMenu(const TlkFinalArt *art,uint32_t age,unsigned credits,unsigned selected_no,uint32_t *out);
/* Explicit animation updates for the confirmed scene controller. Program0 is
 * idle,1 exit. Installation supplies images/programs; caller supplies clocks. */
int TlkFinalArtDrawMenuClocks(const TlkFinalArt *art,unsigned rafiki_program,
    uint64_t rafiki_updates,uint64_t icon_updates,unsigned credits,unsigned selected_no,uint32_t *out);
/* Confirmed MD menu before its outgoing fade. Scene age and confirmation age
 * use the same saved timeline. Credits remain caller-owned gameplay state. */
int TlkFinalArtDrawConfirmedMenu(const TlkFinalArt *art,uint32_t age,
    uint32_t confirmed_age,unsigned credits,uint32_t *out);
/* Canonical320 canvas for a selected256/320 viewport. Centre content retains
 * its original placement; the credit icon/digit preserve their original
 * distances from the right edge. Crop256 at X32 after drawing. */
int TlkFinalArtDrawMenuViewport(const TlkFinalArt *art,uint32_t age,
    unsigned credits,unsigned selected_no,unsigned width,uint32_t *out);
int TlkFinalArtDrawConfirmedMenuViewport(const TlkFinalArt *art,uint32_t age,
    uint32_t confirmed_age,unsigned credits,unsigned width,uint32_t *out);
/* Package-v3 ready initial title only: independent original two-plane backdrop,
 * logo, labels, copyright and selector. Caller owns scene lifetime, bob X118..128,
 * selected0(Start)/1(Options), viewport crop and fades. Options/intro not covered. */
int TlkFinalArtDrawReadyTitle(const TlkFinalArt *art,unsigned selected,unsigned bob_x,uint32_t *out);
/* Package-v4 original Options screen; actual active bindings in roar/adult
 * slash/jump order. Host owns selection, settings, input and audition submenus. */
int TlkFinalArtDrawOptions(const TlkFinalArt *art,unsigned selected,unsigned bob_x,
    unsigned difficulty,unsigned music,unsigned effects,const char buttons[3],uint32_t *out);
/* Package-v5 original ordinary title opening; age0 is its first backdrop. */
int TlkFinalArtDrawTitleBackdrop(const TlkFinalArt *,uint32_t *);
int TlkFinalArtDrawTitleOpening(const TlkFinalArt *,unsigned,uint32_t *);
/* Package-v6 cold-start SEGA/Disney-Virgin/Westwood cards. Indexed artwork and
 * original SEGA palette cycle are installed data; host owns sequence/fades. */
unsigned TlkFinalArtPublisherPrefixTicks(const TlkFinalArt *);
int TlkFinalArtDrawPublisher(const TlkFinalArt *,unsigned,unsigned,uint32_t *);
/* Package-v7 original Sound Test. Installed catalogue order and backdrop;
 * caller owns circular selection, input, playback and scene lifetime. */
int TlkFinalArtSoundTestProgram(const TlkFinalArt *,unsigned,unsigned *);
int TlkFinalArtDrawSoundTest(const TlkFinalArt *,unsigned,unsigned,uint32_t *);
/* Catalogue follows playback; artwork/layout is independently selected. */
int TlkFinalArtSoundTestName(const TlkFinalArt *,int,unsigned,char name[21]);
int TlkFinalArtDrawSoundTestCatalog(const TlkFinalArt *,int,unsigned,unsigned,uint32_t *);
/* Package-v8 original cheat/level-select artwork. Actual native settings,
 * controls and three-state invulnerability remain owned by the game. */
int TlkFinalArtDrawDebugMenu(const TlkFinalArt *,unsigned,unsigned,unsigned,unsigned,uint32_t *);
/* Installed original MD attract-controller records, indexed by input run.
 * Returns0 when unavailable; terminator returns padFFFF and duration0. */
int TlkFinalArtAttractRun(const TlkFinalArt *,unsigned level,unsigned run,
                         unsigned *pad,unsigned *duration);
#endif

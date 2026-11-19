#ifndef TLK_FINAL_ART_INTERNAL_H
#define TLK_FINAL_ART_INTERNAL_H
#include "tlk_final_art.h"
#include "tlk_options_art.h"
#include "tlk_title_opening_art.h"
typedef struct FinalImage { uint32_t frame;int x,y,w,h;uint8_t *pixels; } FinalImage;
typedef struct FinalStep { uint32_t frame,ticks; } FinalStep;
typedef struct FinalProgram { unsigned count,loop;FinalStep *steps; } FinalProgram;
typedef struct FinalPlan { uint32_t slots[13];int coordinates[8];unsigned banks[5];FinalProgram programs[3]; } FinalPlan;
typedef struct ReadyTitleArt { uint16_t palette[64];uint8_t base[320*224],selector[24*24]; } ReadyTitleArt;
enum { PUBLISHER_PIXELS=320*224,PUBLISHER_BYTES=32+3*128+62+3*PUBLISHER_PIXELS,PUBLISHER_PREFIX_TICKS=189 };
typedef struct PublisherArt { uint16_t palette[3][64],cycle[31];uint8_t base[3][PUBLISHER_PIXELS]; } PublisherArt;
enum { SOUND_TEST_BYTES=32+320*224+16*18,DEBUG_MENU_BYTES=32+320*224+14*20,NATIVE_SOUND_CATALOG_BYTES=64+16*20,ATTRACT_BYTES=64+3*168 };
struct TlkFinalArt { unsigned count;uint16_t palette[64];FinalImage *images;FinalPlan *plan;ReadyTitleArt *title;TlkOptionsArt *options;TlkTitleOpeningArt *opening;PublisherArt *publisher;uint8_t *sound_test,*debug_menu,*native_sound_catalog,*attract; };

#endif

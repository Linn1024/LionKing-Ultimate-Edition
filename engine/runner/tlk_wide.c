#include "tlk_fallback_log.h"
/* tlk_wide.c -- widescreen compositor for The Lion King (see tlk_wide.h).
 *
 * Mode 1 decode and composition follow snesrecomp's PPU (ppu.c): the same
 * priorities, windows, colour math, brightness and sprite range/time limits,
 * so the centre 256 columns of a level frame equal the PPU's own picture
 * (headless --wide reports any difference as native_mismatch). Only where
 * the inputs come from differs, and only in the margins. */
#include "tlk_wide.h"
#include "tlk_cant_wait_data.h"
/* Temporary host-only Sound Test text substitution. The caller restores this
 * after composing the native text rectangle; guest RAM/VRAM are never edited. */
static int s_sound_test_text_on;
static char s_sound_test_text[5][21];
#include "tlk_camera.h"
#include "tlk_contact_search.h"
#include "common_cpu_infra.h"
#include "tlk_resources.h"
#include "tlk_md_assets.h"
#include "tlk_next_scene_data.h"
#include "tlk_md_sprites.h"
#include "tlk_world_life_sprite.h"
#include "tlk_adult_death_metadata.h"
#include "tlk_prepared_splash_metadata.h"
#include "tlk_health_death_audio_context.h"
#include "sha256.h"
#include "tlk_cw_monkey_metadata.h"
#include "tlk_cw_ostrich_metadata.h"
#include "tlk_cw_tail_metadata.h"
#include "tlk_flying_creature_metadata.h"
#include "tlk_cw_rhino_metadata.h"
#include "tlk_cw_ride_owner.h"
#include "tlk_graveyard_enemy_metadata.h"
#include "tlk_graveyard_hyena_owner.h"
#include "tlk_next_scene_data.h"
#include "next_scene_metadata.h"
#include "tlk_graveyard_data.h"
#include "tlk_graveyard_bone_metadata.h"
#include "tlk_graveyard_mufasa_metadata.h"
#include "tlk_exile_exit_hyena_metadata.h"
#include "tlk_exile_falling_rock_metadata.h"
#include "tlk_md_hud.h"
#include "tlk_hud_role.h"
#include "tlk_continue_token_role.h"
#include "tlk_graveyard_bone_object_metadata.h"
#include "tlk_graveyard_jaw_metadata.h"
#include "tlk_graveyard_pillar_metadata.h"
#include "tlk_checkpoint_role.h"
#include "tlk_pickup_flight_role.h"
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
#include "tlk_pickup_flight_runtime.h"
#endif
#include "tlk_pickup_popup_role.h"
#include "tlk_title_role.h"
#include "tlk_cant_wait_view.h"
#include "tlk_hunt_data.h"
#include "tlk_start_data.h"
#include "tlk_interlevel_data.h"

#include "common_rtl.h"
#include "cpu_state.h"
#include "snes/interp_bridge.h"
#include "snes/ppu.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* aot_pace.h: generated code, after the watched instructions. */
void (*g_tlk_wide_pc_hook)(CpuState *cpu, uint32_t pc24);
/* tlk_game.c: passed to the beam driver's per-line raster observer. */
extern void (*g_tlk_raster_observer)(const Ppu *ppu, unsigned line, void *context);

/* Resource choices cannot change while a synchronous draw is in progress.
 * Cache literal IDs for that draw only; CPU hooks and later UI edits still
 * read live choices. Large/tall views otherwise repeat these lookups per row. */
static struct {const char *id;unsigned epoch;int value;} s_draw_choices[2048];
static unsigned s_draw_choice_epoch;
static uint32_t s_sprite_colour_seen[1024];
static int s_custom_palette_colours;
static int s_draw_choices_active;
static void SpritePaletteBegin(void);
static void DrawChoicesBegin(void) {
    memset(s_sprite_colour_seen,0,sizeof s_sprite_colour_seen);
    SpritePaletteBegin();
    s_custom_palette_colours=TlkResourcesPaletteCount(0)||TlkResourcesPaletteCount(1);
    if(!++s_draw_choice_epoch){memset(s_draw_choices,0,sizeof s_draw_choices);s_draw_choice_epoch=1;}
    s_draw_choices_active=1;
}
static int DrawUseMd(const char *id) {
    if(!s_draw_choices_active)return TlkResourcesUseMd(id);
    unsigned slot=(unsigned)(((uintptr_t)id>>3)^((uintptr_t)id>>14))&2047;
    while(s_draw_choices[slot].epoch==s_draw_choice_epoch && s_draw_choices[slot].id!=id)slot=(slot+1)&2047;
    if(s_draw_choices[slot].epoch!=s_draw_choice_epoch){
        s_draw_choices[slot].id=id;s_draw_choices[slot].epoch=s_draw_choice_epoch;
        s_draw_choices[slot].value=TlkResourcesUseMd(id);
    }
    return s_draw_choices[slot].value;
}
#define TlkResourcesUseMd DrawUseMd
static uint16_t s_area_sky_color;
static int s_area_sky_edge_valid;
static int s_ride_scene,s_toss_canvas;
static int s_handoff_width;
static struct {int camera,background,shift,background_shift;unsigned loop;int native_camera,head_x,head_y;unsigned head_attributes;} s_ride_handoff={.camera=-1,.native_camera=-1};
static int s_ride_raster_anchor=-1;
/* Presentation camera for tall views; independent of the console camera.
 * Stored in spare history words, so a mid-jump save retains its framing. */
static unsigned s_free_view_key,s_free_view_scene;
static int s_free_view_origin;
static uint16_t s_edge_stable[2],s_edge_pending[2];
static unsigned s_edge_seen[2],s_edge_count[2],s_edge_serial[2];
static uint16_t StableEdge(unsigned side,uint16_t value) {
    if(!s_edge_seen[side]){s_edge_seen[side]=1;s_edge_stable[side]=value;}
    unsigned serial=TlkWideFrameUpdateSerial();
    if(s_edge_serial[side]!=serial){
        s_edge_serial[side]=serial;
        if(value==s_edge_stable[side])s_edge_count[side]=0;
        else {
            if(value!=s_edge_pending[side]){s_edge_pending[side]=value;s_edge_count[side]=1;}
            else if(s_edge_count[side]<12)s_edge_count[side]++;
            if(s_edge_count[side]>=12){s_edge_stable[side]=value;s_edge_count[side]=0;}
        }
    }
    return s_edge_stable[side];
}

enum {
    kPcPiece16 = 0x00A727,   /* one 16x16 piece; drops x outside [-15,255], y outside [-15,238] */
    kPcPiece8 = 0x00A7AE,    /* one 8x8 piece; drops x outside [-7,255], y outside [-7,223] */
    kPcOamDma = 0x00A033,    /* NMI's OAM upload, made only for a frame the game finished */
    kPcSpawnWindow = 0x00B915, /* FN_C0B8EA: its left/right tile columns $46/$14 are set, not yet used */
    kPcCullRight = 0x00A5C2, /* FN_C0A5BA: right limit camera+256 in $14, about to be compared */
    kPcCullLeft = 0x00A5CF,  /* FN_C0A5BA: LDY between LDA $9C (box left) and ADC width; compare with camera */
    kPcRideScript = 0x00B618, /* $C0B5FD: LDA $0A56 before the obstacle script reads distance $0A40 */
    kPcRideScriptEnd = 0x00B69F, /* its common exit (PLA) */
    kPcRideSpawnX = 0x00BB98,  /* $C0BB80: LDY after STA $88, the new obstacle's x */
    kMaxPieces = 512,
    kVramCopies = 4,
    kHudSlotsMax = 16,
};

#include "tlk_hyena_context_art.h"

typedef struct Piece {
    int16_t x, y;            /* signed screen position, OAM convention (row = line - 1 - y) */
    uint16_t attr;           /* OAM attribute word: tile, name select, palette, priority, flips */
    uint16_t obj;            /* the object being drawn ($7C) */
    uint8_t size, slot;      /* 16 or 8; the OAM slot it gets if the game keeps it */
    bool kept;               /* the game wrote it to OAM (inside its screen test) */
    bool fixed;              /* a screen-fixed object (HUD): obj+9 bit 6, drawn with no camera */
    int8_t side;             /* HUD at the edges: -64 (left edge) .. 64 (right edge), 0 stays (set at latch) */
    uint32_t pose;
    int16_t local_x,local_y;
    uint32_t actor_descriptor; /* owner at draw submission, before its next update */
    uint8_t hyena_art_context; /* original pose/cursor pair at that same submission */
} Piece;

/* One visible line as the PPU drew it. */
typedef struct Line {
    uint8_t inidisp, obsel, bgmode, mosaic, setini, oamaddl, oamaddh;
    uint8_t bgsc[4];
    uint16_t bgchr;
    uint16_t hofs[4], vofs[4];
    uint16_t fixed;
    uint32_t windowsel;
    uint8_t w1l, w1r, w2l, w2r;
    uint16_t wlog;
    uint8_t tm, ts, tmw, tsw, cgadsub, cgwsel;
    uint8_t vram;            /* which s_vram copy */
    uint16_t cgram[256];
    uint16_t oam[256];
    uint8_t hoam[32];
} Line;

/* The level's BG1 source: map at $7F0000 (or a copy of it), row size and
 * height from the level record, block table in ROM. */
typedef struct Level {
    unsigned rowb, rows;
    uint32_t blk;
    const uint8_t *map;
} Level;

static const uint8_t *s_rom;
static size_t s_rom_size;
/* Original BG2 descriptor+1A maps:45/31 rows, streamed into a32-row VRAM
 * ring. Keep the complete decoded names for tall-window presentation. */
static uint8_t s_native_panorama[14][5760];
static unsigned s_native_panorama_height[14];
static bool s_enabled;
static int s_spawn_lead;   /* pixels added to each side of the game's spawn window; 0 = the game's own */
static unsigned s_ride_cursor;
static int s_ride_lead;    /* pixels the ride script runs ahead this call (kPcRideScript..End), 0 outside */
static int s_draw_extra;   /* the last drawn view's (width - 256) / 2, for ObjLog */
/* Transient host drawing coordinates only, never serialized or guest-visible. */
static int s_area_active,s_area_top,s_area_height,s_area_min_y,s_area_max_y;
static int s_area_view_width=256,s_area_view_height=224,s_area_view_top;
static bool (*s_area_base_draw)(uint32_t *,int,bool);
static bool (*s_area_scene_allowed)(void);
static uint32_t s_area_base[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];

static Piece s_build[kMaxPieces], s_latched[kMaxPieces];
static unsigned s_build_count, s_latched_count;
static unsigned s_latch_serial;

static uint16_t s_vram[kVramCopies][0x8000];
static uint32_t s_vram_count[kVramCopies];
/* Palette-independent BG2 tokens, rebuilt only when original tile data changes.
 * Check each VRAM version once per draw; fades and palette animation stay live. */
static uint16_t s_panorama_pixels[kVramCopies][512*360];
static uint16_t s_panorama_tiles[kVramCopies][0x4000];
static unsigned s_panorama_epoch,s_panorama_checked[kVramCopies],s_panorama_owner[kVramCopies];
static unsigned s_panorama_base[kVramCopies];

static bool s_vram_have;
static int s_vram_used, s_vram_cur;

static struct {
    Line lines[TLK_WIDE_HEIGHT];
    int captured;
    uint8_t ram[0x20000];
    Piece pieces[kMaxPieces];
    unsigned piece_count;
    unsigned latch_serial;
    int raster_camera[2];
    int hud_end;
    uint32_t stock[256 * TLK_WIDE_HEIGHT];
    bool valid, stage;
    Level level;
    uint8_t stage_sc;
    uint16_t stage_chr;
} s_frame;

static TlkWideStats s_stats;
static unsigned s_md_level;
static int s_md_foreground, s_md_background,s_md_cub_frames,s_cub_death_frame;
static int s_md_layout;
static int s_native_md_layout;
static unsigned s_md_layout_y;
static int s_native_pride_bg_edges;
/* Internal source routing; serialized sprite-map roles remain unchanged. */
#include "tlk_enemy_art_family.h"
enum { kAdultCheckpointRole=TLK_MD_SPRITE_ROLE_COUNT, kPorcupineArtRole, kSceneRoleCount };
static int s_md_npc_frames[kSceneRoleCount],s_md_npc_palette[kSceneRoleCount];
static uint16_t s_npc_color[TLK_WIDE_MAX_WIDTH];
static uint16_t s_obj_palette[TLK_WIDE_MAX_WIDTH];
static uint16_t PaletteToken(const char *id);
static const Piece *s_fallback_piece[TLK_WIDE_MAX_WIDTH];
static const char *s_fallback_reason[TLK_WIDE_MAX_WIDTH];
static int s_fallback_enabled,s_fallback_all_sprites,s_fallback_all_graphics;
static TlkFallbackSpriteInfo s_fallback_sprite_info[kMaxPieces];
static uint8_t s_fallback_sprite_valid[kMaxPieces];

static uint8_t s_obj_slot[TLK_WIDE_MAX_WIDTH];
static unsigned s_current_obj_slot;
static int s_hud_pass;
static int s_md_hud_frames[3],s_hud_present[3];
static unsigned s_hud_slot[3];
static uint16_t s_hud_attr[3];
static int s_bg_camera[2],s_bg_previous_raster[2],s_bg_history,s_bg_view_left;
static bool s_bg_hold_next;
static unsigned s_bg_last_latch;
static int s_bg_level=-1;
static struct { unsigned active,phase,delay,latch; } s_scene_animation;
/* The saved phase word retains the original lightning base and MD rain step.
 * No guest-state writes or independent wall-clock animation are involved. */
static int PrideRockRainPhase(unsigned phase) {
    return (phase&0x100u) && !(phase&~0x137u) && ((phase>>4)&3u)<3;
}
static TlkCantWaitView s_cant_wait;
static uint16_t s_cw_native[128],s_cw_colors[100],s_cw_external[2][64],s_cw_native_mapped[2][128];
static int s_scenery_palette[2],s_cw_palette_sources;
static int s_cw_palette_valid,s_cw_palette_mode,s_cw_scene,s_cw_monkey_palette,s_cw_ostrich_palette,s_cw_tail_palette;
static unsigned CantWaitColorDistance(unsigned a,unsigned b) {
    int r=(int)(a&31)-(int)(b&31),g=(int)(a>>5&31)-(int)(b>>5&31),bl=(int)(a>>10&31)-(int)(b>>10&31);
    return (unsigned)(r*r+g*g+bl*bl);
}
/* The native event replaces all CGRAM at once (C0D178). MD18D79E instead
 * advances colour channels every nine completed updates. Keep that timing
 * independent of the selected artwork/colour source; never rewrite CGRAM. */
static unsigned s_cw_palette_phase;
static unsigned CantWaitSunrisePhase(void) {
    if(!s_cant_wait.triggered || s_cant_wait.updates>=100)return 100;
    /* A settled checkpoint starts in daylight and must not replay sunrise. */
    const uint8_t *ram=s_frame.ram;
    unsigned checkpoint=ram[0x1ffa2]|ram[0x1ffa3]<<8;
    unsigned kind=ram[0x1ffa4]|ram[0x1ffa5]<<8;
    if(checkpoint && kind!=66)return 100;
    return s_cant_wait.updates;
}
static unsigned CantWaitNativeSunrise(unsigned i,unsigned captured,unsigned phase) {
    if(phase==100 || !s_rom || s_rom_size<0x602b5)return captured;
    const uint8_t *start=s_rom+0x50b7a+i*2,*end=s_rom+0x601b5+i*2;
    unsigned a=i?(start[0]|start[1]<<8):0,b=end[0]|end[1]<<8;
    /* Preserve per-row effects and banks subsequently owned by other actors. */
    if(captured!=b)return captured;
    unsigned steps=phase>=2?1+(phase-2)/9:0,out=0;
    for(unsigned shift=0;shift<15;shift+=5) {
        int from=a>>shift&31,to=b>>shift&31,d=(int)steps*4;
        int c=from<to?(from+d<to?from+d:to):(from-d>to?from-d:to);
        out|=(unsigned)c<<shift;
    }
    return out;
}
static void CantWaitPalette(const uint16_t *native) {
    int mode=s_scenery_palette[0]|s_scenery_palette[1]<<1;
    int gradual=TlkResourcesUseMd("gameplay.levels.cant_wait.sunrise_timing");
    unsigned phase=gradual?CantWaitSunrisePhase():100;
    unsigned key=phase|(unsigned)gradual<<8;
    if(s_cw_palette_valid && mode==s_cw_palette_sources && key==s_cw_palette_phase &&
       !memcmp(native,s_cw_native,sizeof s_cw_native) &&
       !memcmp(s_cant_wait.colors,s_cw_colors,sizeof s_cw_colors))return;
    memcpy(s_cw_native,native,sizeof s_cw_native);memcpy(s_cw_colors,s_cant_wait.colors,sizeof s_cw_colors);
    s_cw_palette_valid=1;s_cw_palette_sources=mode;s_cw_palette_mode=s_scenery_palette[1];s_cw_palette_phase=key;
    uint16_t colors[64],settled[64];
    const uint16_t *md=s_cw_colors;
    if(!gradual && s_cant_wait.triggered && TlkMdCantWaitInitialPalette(1,settled))md=settled;
    for(unsigned i=0;i<64;i++)colors[i]=TlkMdColor555(md[i]);
    for(unsigned i=0;i<128;i++) {
        unsigned best=~0u,index=16;
        for(unsigned n=16;n<64;n++){unsigned d=CantWaitColorDistance(native[i],colors[n]);if(d<best){best=d;index=n;}}
        for(unsigned layer=0;layer<2;layer++)s_cw_native_mapped[layer][i]=s_scenery_palette[layer]?colors[index]:CantWaitNativeSunrise(i,native[i],phase);
    }
    for(unsigned i=0;i<64;i++) {
        unsigned best=~0u,index=0;
        for(unsigned n=0;n<128;n++){unsigned d=CantWaitColorDistance(colors[i],native[n]);if(d<best){best=d;index=n;}}
        for(unsigned layer=0;layer<2;layer++)s_cw_external[layer][i]=s_scenery_palette[layer]?colors[i]:s_cw_native_mapped[layer][index];
    }
}

static unsigned rd16(const uint8_t *p) { return p[0] | p[1] << 8; }
static uint32_t rd24(const uint8_t *p) { return p[0] | p[1] << 8 | (uint32_t)p[2] << 16; }
#include "tlk_graveyard_pillar_owner.h"
/* Destiny's native face is placed at a fixed world point. MD instead anchors
 * it to Simba. Its face records use local coordinates +128/+120 relative to
 * the native records, so MD's (-228,-248) spawn becomes (-100,-128) here.
 * Keep this a presentation choice: never move an actor or its completion task. */
static bool s_destiny_face_position;
static int s_destiny_face_dx,s_destiny_face_dy;
static bool DestinySkyFacePiece(const Piece *p) {
    if(!s_destiny_face_position || !p || p->fixed || p->obj<0x8000 || p->obj>0xffe8)return false;
    unsigned pos=rd16(s_frame.ram+p->obj+4);
    if(pos<0xb29b || pos>=0xdc1b || ((pos-0xb21b)&127))return false;
    unsigned actor=pos-8;
    if(rd16(s_frame.ram+actor+12)!=p->obj || rd24(s_frame.ram+actor+4)!=0xc586a8 ||
       rd24(s_frame.ram+actor+48)!=0xc1aa3f || rd16(s_frame.ram+pos)!=183 || rd16(s_frame.ram+pos+2)!=552)return false;
    static const unsigned poses[]={0xc4d5f3,0xc4d616,0xc4d641,0xc4d678,0xc4d6d7,0xc4d752,
        0xc4d7f9,0xc4d8cc,0xc4d98f,0xc4da46,0xc4db01,0xc4dbc8,0xc4dc83,0xc4dd3a,0xc4ddf5,0xc4debc,0xc4df77};
    for(unsigned i=0;i<sizeof poses/sizeof *poses;i++)if(p->pose==poses[i])return true;
    return false;
}
static void PrepareDestinySkyFace(void) {
    s_destiny_face_position=s_frame.stage && rd16(s_frame.ram+0x1ff9e)==6 &&
        rd24(s_frame.ram+0xdf)==0xc004b3 && rd16(s_frame.ram+0x2000)==0xffff &&
        rd24(s_frame.ram+0xb217)==0xc5858a && rd24(s_frame.ram+0xb243)==0xc1a8c8 &&
        TlkResourcesUseMd("graphics.scenery.destiny_face_position");
    s_destiny_face_dx=(int)rd16(s_frame.ram+0xb21b)-100-183;
    s_destiny_face_dy=(int)rd16(s_frame.ram+0xb21d)-128-552;
}

/* Draw-list records move. Their +4 field points at the semantic object's
 * position; Simba's fixed state starts at $B21B (also used by RAM logging). */
static int BonusScene(void) {
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    return level>=10 && level<=13 && rd24(s_frame.ram+0xdf)==0xc005dd+(level-10)*0x32;
}
/* Hunt worlds scroll and have complete finite terrain. Their bonus status
 * does not make them a fixed224-line picture like the Pumbaa arena. */
static bool HuntScene(void) {
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    return level>=11 && level<=13 && BonusScene();
}
static bool CubPiece(const Piece *p) {
    if(BonusScene())return false;
    return !p->fixed && p->obj <= 0xFFFA && rd16(s_frame.ram + p->obj + 4) == 0xB21B;
}
/* Original adult lava splash: actual Prepared palette5/packed7F banks and
 * source animation operands verified5542. The MD images already belong to
 * the installed shared splash atlas; keep the native controller and timing. */
static unsigned PreparedSplashPose(const Piece *p,const uint16_t *cgram) {
    if(!p || !CubPiece(p) || p->actor_descriptor!=0xc5858a || ((p->attr>>9)&7)!=5 ||
       rd16(s_frame.ram+0x1ff9e)!=7 || rd24(s_frame.ram+0xdf)!=0xc004e5 ||
       rd16(s_frame.ram+0x2000)!=0xffff || rd24(s_frame.ram+0xb243)!=0xc3857f ||
       p->obj>0xffe8 || rd16(s_frame.ram+0xb21f)!=p->obj)return 0;
    const uint16_t *normal=TlkNextSceneNativeObj(7,5);
    if(!normal || !cgram || memcmp(normal+1,cgram+208+1,15*sizeof *normal))return 0;
    for(unsigned i=0;i<sizeof prepared_splash_frames/sizeof *prepared_splash_frames;i++) {
        if(p->pose!=prepared_splash_frames[i].native)continue;
        unsigned hash=2166136261u;
        for(unsigned n=0;n<prepared_splash_frames[i].length;n++)
            hash=(hash^s_frame.ram[prepared_splash_frames[i].address+n])*16777619u;
        return hash==prepared_splash_frames[i].fnv?prepared_splash_frames[i].alias:0;
    }
    return 0;
}
static uint16_t PreparedSplashColor(unsigned pixel,int frames,int palette,const uint16_t *cgram) {
    const uint16_t *md=TlkNextSceneMdPalette(7);
    return palette && md?md[16+(frames?pixel:prepared_splash_native_to_md[pixel])]:
        cgram[208+(frames?prepared_splash_md_to_native[pixel]:pixel)];
}
static struct { unsigned live,active,age,latch; int x,y;uint16_t colors[16]; } s_gy_death;
static int GraveyardDeathSelected(void) {
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    return s_gy_death.active && TlkGraveyardDataReady() && TlkMdSpritesCubDeathAssetCount()==20 &&
          TlkResourcesUseMd(level>=6?"graphics.sprites.simba.adult.death_motion":
            level==1?"graphics.sprites.simba.cub.king_death_motion":
            level==3?"graphics.sprites.simba.cub.stampede_death_motion":
            level==5?"graphics.sprites.simba.cub.hakuna_death_motion":
            level==4?"graphics.sprites.simba.cub.exile_death_motion":"graphics.sprites.simba.cub.graveyard_death_motion");
}
static int DeathApproach(int distance,unsigned steps) {
    int amount=distance<0?-distance:distance;
    if((unsigned)amount>steps)amount=(int)steps;
    return distance<0?distance+amount:distance-amount;
}
static unsigned SpriteDeathColor(unsigned level,uint16_t color);
static int CustomObjectColours(unsigned level) {
    int count=TlkResourcesPaletteCount(0);
    for(int i=0;i<count;i++){int e[4];if(TlkResourcesPaletteEntry(i,0,e)&&((e[0]==(int)level&&e[1]==2)||e[0]==14))return 1;}
    return 0;
}
static void GraveyardDeathActor(uint32_t *out,int width) {
    if(!GraveyardDeathSelected() || s_gy_death.age>=249)return;
    unsigned level=rd16(s_frame.ram+0x1ff9e),adult=level>=6,pose;
    if(adult) {
        /* Source4161: thirteen equal-duration native/MD records, with one
         * repeated pose. Both indexed drawings and anchors are identical. */
        static const unsigned durations[]={1,1,1,1,1,1,3,3,3,3,3,3,20};
        static const unsigned indices[]={0,1,2,3,4,5,6,7,8,9,10,10,11};
        unsigned age=s_gy_death.age,i=0;
        while(i<12 && age>durations[i]){age-=durations[i]+1;i++;}
        pose=tlk_adult_death_poses[indices[i]]|0xc00000;
    } else if(!TlkGraveyardDeathPose(s_gy_death.age,&pose))return;
    int bx,by,bw,bh;if(!TlkMdSpritesBounds(pose,&bx,&by,&bw,&bh))return;
    unsigned steps=s_gy_death.age<24?0:s_gy_death.age-23;
    int px=width/2+DeathApproach(s_gy_death.x,steps),py=128+DeathApproach(s_gy_death.y-128,steps);
    uint16_t colors[256]={0};memcpy(colors+128,s_gy_death.colors,sizeof s_gy_death.colors);
    unsigned fade=s_gy_death.age<225?0:(s_gy_death.age-225+2)/3;
    const uint16_t *scene_colors=NULL;
    if(level>=3 && TlkResourcesUseMd(adult?"graphics.sprites.simba.adult.palette":"graphics.sprites.simba.cub.palette")) {
        const uint16_t *normal=TlkNextSceneNativeObj(level,0),*md=TlkNextSceneMdPalette(level);
        if(normal && md && !memcmp(normal+1,s_gy_death.colors+1,15*sizeof *normal))scene_colors=md;
    }
    int frames=TlkResourcesUseMd("graphics.sprites.simba.cub.frames");
    for(int y=by;y<by+bh;y++)for(int x=bx;x<bx+bw;x++){
        int dx=px+x,dy=py+y;if(dx<0 || dx>=width || dy<0 || dy>=TLK_WIDE_HEIGHT)continue;
        int pixel=adult?TlkMdSpritesPixel(pose,x,y):TlkMdSpritesCubDeathPixel(pose,x,y,frames);if(pixel<=0)continue;
        unsigned color=scene_colors?scene_colors[pixel]:TlkResourcesCubColor(level,128+(unsigned)pixel,colors,colors[128+pixel]);color=SpriteDeathColor(level,(uint16_t)color);uint32_t rgb=0;
        for(unsigned c=0;c<3;c++){
            unsigned v=(color>>(c*5))&31,sub=fade*4;v=v>sub?v-sub:0;
            rgb|=(v*8+(v>>2))<<(c==0?16:c==1?8:0);
        }
        out[(size_t)dy*width+dx]=rgb;
    }
}
static bool CubDeathFrame(void) {
    const uint8_t *ram=s_frame.ram;
    unsigned descriptor=rd16(ram+0xdf),draw=rd16(ram+0xb21f);
    return !rd16(ram+0x1ff9e) && (descriptor==0x387 || descriptor==0x80d) && ram[0xe1]==0xc0 &&
           !rd16(ram+0x2000) && !rd16(ram+0x2004) && !rd16(ram+0xa6ba) &&
           rd24(ram+0xb243)==0xc35a82 && draw>=0x8000 && draw<=0xffe8 &&
           TlkMdSpritesCubDeathReady(rd24(ram+draw+10),ram,sizeof s_frame.ram);
}
static bool CubDeathLine(const Line *l) {
    /* This verified screen has an OBJ-only black backdrop. Other non-stage
     * modes, windows and color-math combinations retain the PPU picture. */
    return (s_cub_death_frame || GraveyardDeathSelected()) && (l->bgmode&7)==1 && l->tm==0x10 && !l->ts &&
           !l->windowsel && !l->wlog && !l->tmw && !l->tsw &&
           (!l->cgadsub || GraveyardDeathSelected());
}
static int StampedeScene(void) {
    return rd16(s_frame.ram+0x1ff9e)==3 && rd24(s_frame.ram+0xdf)==0xc0041d && TlkNextSceneDataReady();
}
static int StampedeHudPalette(const uint16_t *cgram){
    const uint16_t *native=TlkNextSceneNativeObj(3,0);
    return StampedeScene() && native && !memcmp(cgram+128,native,32);
}
static uint16_t SceneHudColor(unsigned index,const uint16_t *cgram,uint16_t original){
    if(index>=128 && index<144 && StampedeHudPalette(cgram))
        return TlkResourcesUseMd("graphics.hud.palette")?TlkNextSceneMdPalette(3)[index-128]:original;
    return TlkResourcesHudColor(index,cgram,original);
}
static int ExileScene(void) {
    return s_frame.stage && rd16(s_frame.ram+0x1ff9e)==4 && rd24(s_frame.ram+0xdf)==0xc0044f && TlkNextSceneDataReady();
}
static bool StampedeLine(const Line *l) {
    return StampedeScene() && (l->bgmode&7)==1 && !l->windowsel && !l->wlog && !l->tmw && !l->tsw;
}
static unsigned DrawActorDescriptor(const uint8_t *ram,unsigned obj,unsigned pose) {
    if(TlkCwRidePose(pose))
        return TlkCwRideDrawDescriptor(ram,0x20000,s_rom,s_rom_size,obj,pose);
    if(obj>0xffe8)return 0;
    unsigned position=rd16(ram+obj+4);
    if(position<0x8008 || position>0xff88)return 0;
    unsigned actor=position-8;
    return rd16(ram+actor+12)==obj && rd24(ram+obj+10)==pose?rd24(ram+actor+4):0;
}
static unsigned NextPieceDescriptor(const Piece *p) {
    /* Rain owns screen-space draw records but retains the ordinary actor link. */
    if(!p || (p->fixed && !(s_md_level==9 && p->pose==0xc2f33e && !((p->attr>>9)&7))) || p->obj>0xffe8)return 0;
    return p->actor_descriptor;
}
static uint16_t StampedeColor(unsigned index,uint16_t original) {
    const uint16_t *native=TlkNextSceneStampedeBg(),*external=TlkNextSceneMdPalette(3);
    static unsigned char mapping[128];static int initialized;
    if(!native || !external || index>=128)return original;
    if(!index)return external[0];
    if(original!=native[index])return original;
    /* The native frame matte uses opaque palette1/color15. Its original MD
     * counterpart is black in that slot; nearest RGB picks an unrelated red. */
    if(index==31)return external[31];
    if(!initialized){
        for(unsigned i=0;i<128;i++){
            unsigned best=~0u,target=0;
            for(unsigned j=0;j<64;j++){
                int r=(int)(native[i]&31)-(int)(external[j]&31),g=(int)(native[i]>>5&31)-(int)(external[j]>>5&31),b=(int)(native[i]>>10&31)-(int)(external[j]>>10&31);
                unsigned distance=(unsigned)(3*r*r+6*g*g+2*b*b);
                if(distance<best){best=distance;target=j;}
            }mapping[i]=(unsigned char)target;
        }initialized=1;
    }return external[mapping[index]];
}
static int s_stampede_cub_death_palette;
static int s_stampede_wildebeest_palette;
static const uint16_t *StampedeWildebeestPalette(const Piece *p,unsigned bank,const uint16_t *cgram) {
    if(!s_stampede_wildebeest_palette || bank!=6)return NULL;
    unsigned desc=NextPieceDescriptor(p);
    if(desc!=0xc58b0c && desc!=0xc58b18 && desc!=0xc58b24 && desc!=0xc58b30)return NULL;
    int found=0;for(unsigned i=0;i<sizeof next_wildebeest_poses/sizeof *next_wildebeest_poses;i++)if(next_wildebeest_poses[i]==p->pose)found=1;
    const uint16_t *expected=TlkNextSceneNativeObj(3,6),*external=TlkNextSceneMdPalette(3);
    if(!found || memcmp(cgram+224+1,expected+1,30))return NULL;
    return external+48;
}
/* The20 common death drawings have identical original pixels and anchors.
 * Stampede owns its hero outside the usual B213 task; color its captured death
 * drawings directly, without changing that task, clocks or shared artwork. */
static const uint16_t *StampedeCubDeathPalette(const Piece *p,unsigned bank,const uint16_t *cgram) {
    if(!s_stampede_cub_death_palette || bank || !p || p->fixed ||
       p->actor_descriptor!=0xc5858a || !TlkMdSpritesCubDeathPose(p->pose) ||
       !TlkResourcesSharedPaletteMatches(cgram))return NULL;
    return TlkNextSceneMdPalette(3);
}
static int HudMeter(const Piece *p) {
    return p ? TlkHudMeterRole(s_frame.ram, sizeof s_frame.ram,
                              s_rom, s_rom_size, p->obj, p->fixed) : -1;
}
static int s_flying_creature_palette;
static bool FlyingCreaturePalette(const Piece *p,unsigned attr,const uint16_t *cgram) {
    if(!s_flying_creature_palette || !p || p->fixed || ((attr>>9)&7) ||
       (p->actor_descriptor!=0xc58814 && p->actor_descriptor!=0xc5881d))return false;
    /* RecordPiece captures the descriptor only after reciprocal task/draw and
     * submitted-pose validation. Use that identity, not a later live pose. */
    unsigned i=0;
    for(;i<sizeof flying_creature_poses/sizeof *flying_creature_poses;i++)
        if(p->pose==flying_creature_poses[i])break;
    if(i==sizeof flying_creature_poses/sizeof *flying_creature_poses)return false;
    if(TlkResourcesSharedPaletteMatches(cgram))return true;
    if(s_fallback_enabled)TlkFallbackRecord("sampling_failure",
        "graphics.sprites.animals.flying_creatures.palette","flying_palette_guard",
        p->obj,p->pose,p->actor_descriptor,1);
    return false;
}
/* Both original guidance glyphs share exact indexed artwork. Keep the native
 * anchors and movement; the shared HUD palette owns their color selection. */
static bool SharedGuidancePiece(const Piece *p,unsigned attr) {
    if(!s_frame.stage || s_md_level>9 || !p || p->fixed || ((attr>>9)&7))return false;
    unsigned expected=0;
    if(p->actor_descriptor==0xc58684 && p->pose==0xc6f85f)expected=0xcdfc2;
    else if((p->actor_descriptor==0xc58690 || p->actor_descriptor==0xc5869c) &&
            p->pose==0xc6f834)expected=0xcdf8a;
    if(!expected)return false;
    unsigned md=0,role=0,native_bank=0,md_bank=0,ready=0;
    return TlkMdSpritesDescribe(p->pose,&md,&role,&native_bank,&md_bank,&ready) &&
           md==expected && !role && !native_bank && !md_bank && ready;
}
static int CantWaitAnimalPaletteBank(const Piece *p,unsigned attr,const uint16_t *cgram) {
    if((!s_cw_monkey_palette && !s_cw_ostrich_palette && !s_cw_tail_palette) || !p || p->fixed || p->obj>0xffe8)return -1;
    unsigned bank=(attr>>9)&7;
    if(bank<1 || bank>3)return -1;
    const unsigned *poses=NULL,*descriptors=NULL;unsigned count=0,descriptor_count=0,n;
    if(s_cw_tail_palette && bank==1)for(n=0;n<sizeof cw_tail_poses/sizeof *cw_tail_poses;n++)
        if(cw_tail_poses[n]==p->pose){poses=cw_tail_poses;count=sizeof cw_tail_poses/sizeof *cw_tail_poses;descriptors=cw_tail_descriptors;descriptor_count=sizeof cw_tail_descriptors/sizeof *cw_tail_descriptors;break;}
    if(s_cw_monkey_palette && bank>=2)for(n=0;n<sizeof cw_monkey_poses/sizeof *cw_monkey_poses;n++)
        if(cw_monkey_poses[n]==p->pose){poses=cw_monkey_poses;count=sizeof cw_monkey_poses/sizeof *cw_monkey_poses;descriptors=cw_monkey_descriptors;descriptor_count=sizeof cw_monkey_descriptors/sizeof *cw_monkey_descriptors;break;}
    if(!poses && s_cw_ostrich_palette && bank==2)for(n=0;n<sizeof cw_ostrich_poses/sizeof *cw_ostrich_poses;n++)
        if(cw_ostrich_poses[n]==p->pose){poses=cw_ostrich_poses;count=sizeof cw_ostrich_poses/sizeof *cw_ostrich_poses;descriptors=cw_ostrich_descriptors;descriptor_count=sizeof cw_ostrich_descriptors/sizeof *cw_ostrich_descriptors;break;}
    if(!count)return -1;
    /* Shared animal artwork needs the same draw-time ownership as replaced
     * sprites. A later animation pose must not restore native colors on a
     * perfectly valid submitted drawing. RecordPiece validated the backlink
     * and pose together when it captured this descriptor. */
    unsigned descriptor=p->actor_descriptor;
    for(n=0;n<descriptor_count;n++)if(descriptors[n]==descriptor)break;
    if(n==descriptor_count)return -1;
    /* Preserve flashes/repurposed banks. Cache only this derived comparison;
     * actual MD colors come from the already saved, live scene controller. */
    static uint16_t previous[3][15];static unsigned valid[3],matches[3];
    unsigned index=bank-1;const uint16_t *colors=cgram+128+bank*16+1;
    if(!valid[index] || memcmp(previous[index],colors,sizeof previous[index])) {
        uint8_t bytes[30],hash[32];
        memcpy(previous[index],colors,sizeof previous[index]);valid[index]=1;
        for(n=0;n<15;n++){bytes[n*2]=(uint8_t)colors[n];bytes[n*2+1]=(uint8_t)(colors[n]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);
        const unsigned char (*expected)[32]=bank==1?cw_rhino_palette_hashes:cw_monkey_palette_hashes[bank-2];
        matches[index]=!memcmp(hash,expected[0],32) || (bank!=1 && !memcmp(hash,expected[1],32));
    }
    static int trace_opened;static FILE *trace;
    static unsigned traced_latch,traced_obj;
    if(!trace_opened){trace_opened=1;const char *path=getenv("TLK_CW_PALETTE_OWNER_TRACE");
        if(path)trace=fopen(path,"w");
        if(trace)fputs("field,latch,object,pose,live_pose,descriptor,bank,palette_matches\n",trace);}
    unsigned live_pose=rd24(s_frame.ram+p->obj+10);
    if(trace && live_pose!=p->pose &&
       (traced_latch!=s_frame.latch_serial || traced_obj!=p->obj)) {
        fprintf(trace,"%d,%u,%04x,%06x,%06x,%06x,%u,%u\n",snes_frame_counter,
            s_frame.latch_serial,p->obj,p->pose,live_pose,descriptor,bank,matches[index]);fflush(trace);
        traced_latch=s_frame.latch_serial;traced_obj=p->obj;
    }
    return matches[index]?(int)bank:-1;
}
static int s_graveyard_bone_palette;
static uint16_t s_graveyard_bone_colors[16];
static int s_exile_exit_hyena_palette;
static int s_graveyard_mufasa_palette;
static uint16_t s_graveyard_mufasa_colors[16];
/* These28 original silhouettes have identical indexed pixels. Selecting MD
 * colors needs no duplicate image bank or change to native animation clocks. */
static const uint16_t *ExileExitHyenaPalette(const Piece *p,unsigned attr,const uint16_t *cgram) {
    if(!s_exile_exit_hyena_palette || !p || p->fixed || ((attr>>9)&7)!=1 ||
       p->actor_descriptor!=0xc587a4)return NULL;
    unsigned i=0;
    for(;i<sizeof exile_exit_hyena_poses/sizeof *exile_exit_hyena_poses;i++)
        if(p->pose==exile_exit_hyena_poses[i])break;
    if(i==sizeof exile_exit_hyena_poses/sizeof *exile_exit_hyena_poses)return NULL;
    const uint16_t *expected=TlkNextSceneNativeObj(4,1),*colors=TlkNextSceneMdPalette(4);
    /* Leave palette flashes and repurposed banks to their native controller. */
    return expected && colors && !memcmp(cgram+145,expected+1,15*sizeof(uint16_t))?colors+16:NULL;
}
static bool GraveyardMufasaPalette(const Piece *p,unsigned attr,const uint16_t *cgram) {
    if(!s_graveyard_mufasa_palette || !p || p->fixed || ((attr>>9)&7)!=4 || p->obj>0xffe8)return false;
    unsigned n=0;
    for(;n<sizeof graveyard_mufasa_poses/sizeof *graveyard_mufasa_poses;n++)if(p->pose==graveyard_mufasa_poses[n])break;
    if(n==sizeof graveyard_mufasa_poses/sizeof *graveyard_mufasa_poses)return false;
    /* Pose and owner belong to this submitted picture. The live object may
     * already contain the next animation pose when this picture is drawn. */
    if(p->actor_descriptor!=0xc5882c)return false;
    /* These shared drawings use only indices8..15. Guard that exact native
     * half-palette, leaving flashes and repurposed colors on the native path. */
    static uint16_t previous[8];static int valid,matches;
    const uint16_t *colors=cgram+200;
    if(!valid || memcmp(previous,colors,sizeof previous)) {
        unsigned char bytes[16],hash[32];memcpy(previous,colors,sizeof previous);valid=1;
        for(unsigned i=0;i<8;i++){bytes[i*2]=(unsigned char)colors[i];bytes[i*2+1]=(unsigned char)(colors[i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);matches=!memcmp(hash,graveyard_mufasa_palette_hash,32);
    }
    return matches;
}
static bool GraveyardSharedJaw(const Piece *p) {
    return p && !p->fixed && p->obj<=0xffe8 &&
        (p->actor_descriptor==0xc58820 || p->actor_descriptor==0xc5882c) && TlkGraveyardJawPose(p->pose);
}
static bool GraveyardBonePalette(const Piece *p,unsigned attr,const uint16_t *cgram) {
    if(!s_graveyard_bone_palette || !p || p->fixed || p->obj>0xffe8)return false;
    if(((attr>>9)&7)==2 && GraveyardSharedJaw(p)) {
        /* Use the submitted owner/pose together. A newer live actor pose
         * must not reject a valid captured drawing during jaw animation. */
        static uint16_t previous[15];static int valid,matches;
        const uint16_t *colors=cgram+161;
        if(!valid || memcmp(previous,colors,sizeof previous)) {
            unsigned char bytes[30],hash[32];memcpy(previous,colors,sizeof previous);valid=1;
            for(unsigned i=0;i<15;i++){bytes[2*i]=(unsigned char)colors[i];bytes[2*i+1]=(unsigned char)(colors[i]>>8);}
            sha256_compute(bytes,sizeof bytes,hash);matches=!memcmp(hash,graveyard_bone_object_palette_hash,32);
        }
        return matches;
    }
    if(((attr>>9)&7)!=7)return false;
    if(p->pose==0xc30001) {
        unsigned n=0;
        for(;n<sizeof graveyard_falling_bone_descriptors/sizeof *graveyard_falling_bone_descriptors;n++)
            if(p->actor_descriptor==graveyard_falling_bone_descriptors[n])break;
        if(n==sizeof graveyard_falling_bone_descriptors/sizeof *graveyard_falling_bone_descriptors)return false;
        /* RecordPiece captured this verified descriptor/pose/backlink together.
         * The generic construction pose is not a global recoloring permission. */
    } else {
        unsigned n=0;
        for(;n<sizeof graveyard_bone_poses/sizeof *graveyard_bone_poses;n++)
            if(p->pose==graveyard_bone_poses[n] && p->actor_descriptor==graveyard_bone_descriptors[n])break;
        if(n==sizeof graveyard_bone_poses/sizeof *graveyard_bone_poses)return false;
        unsigned position=rd16(s_frame.ram+p->obj+4);
        if(position<0x8008 || position>0xff88)return false;
        unsigned actor=position-8;
        if(rd16(s_frame.ram+actor+12)!=p->obj || rd24(s_frame.ram+actor+4)!=graveyard_bone_descriptors[n] ||
           rd24(s_frame.ram+p->obj+10)!=p->pose)return false;
    }
    static uint16_t previous[15];static int valid,matches;
    const uint16_t *colors=cgram+241;
    if(!valid || memcmp(previous,colors,sizeof previous)) {
        unsigned char bytes[30],hash[32];memcpy(previous,colors,sizeof previous);valid=1;
        for(unsigned i=0;i<15;i++){bytes[i*2]=(unsigned char)colors[i];bytes[i*2+1]=(unsigned char)(colors[i]>>8);}
        sha256_compute(bytes,sizeof bytes,hash);matches=!memcmp(hash,graveyard_bone_palette_hash,32);
    }
    return matches;
}
static bool CheckpointPiece(const Piece *p) {
    return p && s_frame.stage && !((p->attr>>9)&7) &&
           TlkCheckpointCapturedDrawRole(s_frame.ram,sizeof s_frame.ram,s_rom,s_rom_size,
                                        p->obj,p->pose,p->fixed,p->actor_descriptor);
}
/* Original5762/5765: adult checkpoint head stays on MD079000, while
 * native activation blinks two different drawings. Keep that source choice
 * independent of generic pickups and preserve flashes/foreign owners. */
static bool AdultCheckpointPiece(const Piece *p) {
    if(!p || !s_frame.stage || s_md_level<6 || s_md_level>9 || p->fixed ||
       p->obj>0xffe8 || ((p->attr>>9)&7) || rd16(s_frame.ram+0x2000)!=0xffff ||
       (p->actor_descriptor!=0xc588b2 && p->actor_descriptor!=0xc588be) ||
       (p->pose!=0xc01998 && p->pose!=0xc2fd87 && p->pose!=0xc2fdb4))return false;
    unsigned scene=rd24(s_frame.ram+0xdf);
    if(scene!=0xc00387+s_md_level*50 && !(s_md_level==9 && scene==0xc007db))return false;
    unsigned position=rd16(s_frame.ram+p->obj+4);
    if(position<0x8008 || position>0xff88)return false;
    unsigned actor=position-8,descriptor=rd24(s_frame.ram+actor+4);
    return rd16(s_frame.ram+actor+12)==p->obj &&
           (descriptor==0xc588b2 || descriptor==0xc588be);
}
static bool CommonPickupFlightPiece(const Piece *p) {
    return p && p->kept && s_frame.stage && !((p->attr>>9)&7) &&
        TlkPickupFlightCommonDrawRole(s_frame.ram,sizeof s_frame.ram,p->obj,p->pose,p->fixed);
}
static bool PreparedFallingRock(const Piece *p,unsigned palette) {
    return p && s_frame.stage && s_md_level==7 && rd24(s_frame.ram+0xdf)==0xc004e5 &&
        !p->fixed && palette==3 && NextPieceDescriptor(p)==0xc58768 && p->pose==0xc60466;
}
static int ExileFallingRockPhase(const Piece *p,unsigned palette) {
    if(!p || !s_frame.stage || s_md_level!=4 || rd24(s_frame.ram+0xdf)!=0xc0044f ||
       p->fixed || palette!=2 || NextPieceDescriptor(p)!=0xc58cbc)return -1;
    for(unsigned i=0;i<sizeof exile_falling_rock_frames/sizeof *exile_falling_rock_frames;i++) {
        if(p->pose!=exile_falling_rock_frames[i].native)continue;
        unsigned md=0,role=0,native_bank=0,md_bank=0,ready=0;
        return TlkMdSpritesDescribe(p->pose,&md,&role,&native_bank,&md_bank,&ready) &&
               md==exile_falling_rock_frames[i].md && role==TLK_MD_SPRITE_COCONUT &&
               !native_bank && !md_bank && ready?(int)i:-1;
    }
    return -1;
}
static int ExileFallingRockSample(const Piece *p,int x,int y,unsigned pixel,int frames,int palette,
                                 const uint16_t *cgram,uint16_t *color) {
    int phase=ExileFallingRockPhase(p,(p->attr>>9)&7);
    if(phase<0)return -1;
    const uint16_t *expected=TlkNextSceneNativeObj(4,2),*external=TlkNextSceneMdPalette(4);
    if(!expected || !external || memcmp(cgram+161,expected+1,30))return -1;
    if(frames) {
        int sample=TlkMdSpritesPixel(p->pose,x,y);if(sample<0)return -1;pixel=(unsigned)sample;
    }
    if(!pixel)return 0;
    *color=palette?external[32+(frames?pixel:exile_falling_rock_frames[phase].native_to_md[pixel])]:
        cgram[160+(frames?exile_falling_rock_frames[phase].md_to_native[pixel]:pixel)];
    return 1;
}
static int PreparedFallingRockSample(const Piece *p,int x,int y,unsigned pixel,int frames,int palette,
                                    const uint16_t *cgram,uint16_t *color) {
    if(!PreparedFallingRock(p,(p->attr>>9)&7))return -1;
    const uint16_t *expected=TlkNextSceneNativeObj(7,3),*external=TlkNextSceneMdPalette(7);
    if(!expected || !external || memcmp(cgram+177,expected+1,30))return -1;
    static const unsigned char md_to_native[16]={0,1,5,3,5,5,5,9,10,7,8,4,12,5,4,2};
    static const unsigned char native_to_md[16]={0,2,3,3,3,3,4,4,10,7,14,5,12,5,9,4};
    if(frames) {
        int sample=TlkMdSpritesPixel(p->pose,x,y);if(sample<0)return -1;pixel=(unsigned)sample;
    }
    if(!pixel)return 0;
    *color=palette?external[48+(frames?pixel:native_to_md[pixel])]:cgram[176+(frames?md_to_native[pixel]:pixel)];
    return 1;
}
static unsigned s_hyena_context_seen; /* Diagnostic only; never guest/save state. */
static unsigned HyenaContextPose(const Piece *p) {
    if(!p || !s_frame.stage || s_md_level<7 || s_md_level>9 || p->fixed ||
       p->actor_descriptor!=0xc58ecc || ((p->attr>>9)&7)!=6)return 0;
    unsigned scene=rd24(s_frame.ram+0xdf);
    if(scene!=0xc00387+s_md_level*50 && !(s_md_level==9 && scene==0xc007db))return 0;
    return TlkHyenaContextAlias(p->hyena_art_context,p->pose);
}
static unsigned SceneNpcPose(const Piece *p) {
    if(AdultCheckpointPiece(p))return 0xc01998;
    unsigned context=HyenaContextPose(p);
    return context?context:p->pose;
}
static unsigned SceneNpcMappedRole(const Piece *p,unsigned palette) {
    if(!palette && AdultCheckpointPiece(p))return kAdultCheckpointRole;
    unsigned context_pose=HyenaContextPose(p);
    if(context_pose)return TlkMdSpritesDrawRole(context_pose,palette);
    if(PreparedFallingRock(p,palette))return TLK_MD_SPRITE_LATER_WORLD;
    if(ExileFallingRockPhase(p,palette)>=0)return TLK_MD_SPRITE_LATER_WORLD;
    if(!p)return 0;
    unsigned role=TlkMdSpritesDrawRole(p->pose,palette);
    unsigned next_desc=NextPieceDescriptor(p);
    {
        static int initialized;static FILE *file;static unsigned serial,count;
        static struct {unsigned obj,pose;} seen[512];
        if(!initialized){initialized=1;const char *path=getenv("TLK_NPC_OWNER_TRACE");
            if(path)file=fopen(path,"w");
            if(file)fputs("latch,level,obj,pose,live_pose,palette,role,descriptor,live_descriptor,backlink,fixed\n",file);}
        if(file && p->obj<=0xffe8){
            unsigned position=rd16(s_frame.ram+p->obj+4),actor=position>=0x8008 && position<=0xff88?position-8:0;
            unsigned desc=actor?rd24(s_frame.ram+actor+4):0;
            if(role || desc==0xc58a7f){
                if(serial!=s_frame.latch_serial){serial=s_frame.latch_serial;count=0;}
                unsigned i=0;for(;i<count;i++)if(seen[i].obj==p->obj && seen[i].pose==p->pose)break;
                if(i==count && count<512){seen[count].obj=p->obj;seen[count++].pose=p->pose;
                    fprintf(file,"%u,%u,%04x,%06x,%06x,%u,%u,%06x,%06x,%04x,%u\n",serial,s_md_level,p->obj,p->pose,
                        rd24(s_frame.ram+p->obj+10),palette,role,next_desc,desc,actor?rd16(s_frame.ram+actor+12):0,p->fixed);fflush(file);}
            }
        }
    }
    /* Shared world1UP: all six original stream drawings, any main level.
     * Bonus life rewards keep their independent source ownership below. */
    if(s_frame.stage && s_md_level<=9 && !p->fixed &&
       role==TLK_MD_SPRITE_LATER_PICKUP && next_desc==0xc58981 &&
       TlkWorldLifeSpritePose(p->pose))return role;
    /* Shared bonus pickup programs keep these captured identities across main
     * worlds. Their bank/pose/palette checks remain in the sprite reader. */
    if(s_frame.stage && s_md_level<=9 && !p->fixed && role==TLK_MD_SPRITE_PICKUP &&
       (next_desc==0xc586b4 || next_desc==0xc586c0))return role;
    if(s_frame.stage && !p->fixed && role==TLK_MD_SPRITE_CONTINUE_TOKEN &&
       next_desc==0xc586cc)return role;
    if(s_frame.stage && s_md_level==2 && rd24(s_frame.ram+0xdf)==0xc003eb &&
       !p->fixed && role==TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT &&
       next_desc==TlkGraveyardBoneObjectDescriptor(p->pose))return role;
    /* The shared poisonous bug uses the same marker19 descriptor and original
     * installed image in every main world. Bonus bugs retain their own choices. */
    if(s_frame.stage && s_md_level<=9 && !p->fixed &&
       role==TLK_MD_SPRITE_PICKUP && next_desc==0xc58975 && p->pose==0xc5293f)return role;
    /* Original marker33 uses this same static pickup in every main world. */
    if(s_frame.stage && s_md_level<=9 && !p->fixed &&
       role==TLK_MD_SPRITE_PICKUP && next_desc==0xc58921 && p->pose==0xc529a1)return role;
    /* Original shared world pickup programs, independent of their level.
     * Fixed flights additionally require their reciprocal live action. */
    if(s_frame.stage && role==TLK_MD_SPRITE_PICKUP &&
       ((!p->fixed && ((next_desc==0xc5892d && p->pose==0xc5287a) ||
                      (next_desc==0xc58939 && p->pose==0xc5289b) ||
                      (next_desc==0xc58945 && p->pose==0xc528bc) ||
                      (next_desc==0xc58951 && p->pose==0xc528dd))) ||
        CommonPickupFlightPiece(p)))return role;
    if(s_frame.stage && BonusScene()) {
        if(role==TLK_MD_SPRITE_BONUS_PUMBAA && s_md_level==10 && next_desc==0xc5858a)return role;
        if(role==TLK_MD_SPRITE_BONUS_TIMON && ((s_md_level==10 && next_desc==0xc58a71) ||
           (s_md_level>=11 && next_desc==0xc5858a)))return role;
        /* Toss reuses the original life/continue pictures from other worlds.
         * Captured reward identity keeps their source under bonus bug choices. */
        if(s_md_level==10 && ((role==TLK_MD_SPRITE_LATER_PICKUP && next_desc==0xc589bd && p->pose==0xc50216) ||
           (role==TLK_MD_SPRITE_CONTINUE_TOKEN && next_desc==0xc589c9 && p->pose==0xc6f764)))return TLK_MD_SPRITE_BONUS_BUG;
        if(role==TLK_MD_SPRITE_PICKUP && ((s_md_level==10 && (next_desc>=0xc58999 && next_desc<=0xc58a05 && (next_desc-0xc58999)%12==0)) ||
           (s_md_level>=11 && (next_desc==0xc58975 || (next_desc>=0xc58a11 && next_desc<=0xc58a65 && (next_desc-0xc58a11)%12==0)))))return TLK_MD_SPRITE_BONUS_BUG;
        return 0;
    }
    if(s_frame.stage && s_md_level==9 && (rd16(s_frame.ram+0xdf)==0x549 || rd16(s_frame.ram+0xdf)==0x7db)) {
        if(role==TLK_MD_SPRITE_SCAR && (next_desc==0xc585e8 || next_desc==0xc585f4 || next_desc==0xc58600))return role;
        if(role==TLK_MD_SPRITE_ADULT_HYENA && next_desc==0xc58ecc)return role;
        if(role==TLK_MD_SPRITE_LATER_WORLD && (next_desc==0xc585d0 || next_desc==0xc5866c || next_desc==0xc58678 || next_desc==0xc58618 || next_desc==0xc5863c || next_desc==0xc58624 || next_desc==0xc58630 || next_desc==0xc58648))return role;
        if(role==TLK_MD_SPRITE_PICKUP && (next_desc==0xc5892d || next_desc==0xc58939))return role;
        return 0;
    }
    if(s_frame.stage && ((s_md_level==7 && rd16(s_frame.ram+0xdf)==0x4e5) ||
                        (s_md_level==8 && rd16(s_frame.ram+0xdf)==0x517))) {
        if(role==TLK_MD_SPRITE_ADULT_HYENA && next_desc==0xc58ecc)return role;
        if(s_md_level==7) {
            if(role==TLK_MD_SPRITE_LATER_ENEMY && (next_desc==0xc58ea8 || next_desc==0xc58eb4 || next_desc==0xc587d6))return role;
            if(role==TLK_MD_SPRITE_LATER_WORLD && (next_desc==0xc58774 || next_desc==0xc58780 || next_desc==0xc5878c || next_desc==0xc5873a || next_desc==0xc58758 || next_desc==0xc5870a || next_desc==0xc5872a || next_desc==0xc58909))return role;
            if(role==TLK_MD_SPRITE_LATER_PICKUP && (next_desc==0xc58981 || next_desc==0xc588b2 || next_desc==0xc588be))return role;
        }
        if(role==TLK_MD_SPRITE_PICKUP && (next_desc==0xc5892d || next_desc==0xc58939 || next_desc==0xc58945 || next_desc==0xc58951 || next_desc==0xc58975 || next_desc==0xc586b4))return role;
        return 0;
    }
    if(s_frame.stage && s_md_level==5 && rd16(s_frame.ram+0xdf)==0x481) {
        if(role==TLK_MD_SPRITE_GORILLA && next_desc==0xc58a7f)return role;
        if(role==TLK_MD_SPRITE_COCONUT && next_desc==0xc58e84)return role;
        if(role==TLK_MD_SPRITE_LATER_ENEMY && (next_desc==0xc58ee4 || next_desc==0xc58ed8 || next_desc==0xc58e9c))return role;
        if(role==TLK_MD_SPRITE_LATER_WORLD && (next_desc==0xc58afc || next_desc==0xc58aec || next_desc==0xc58a97 || next_desc==0xc58ec0))return role;
        if(role==TLK_MD_SPRITE_DEFEAT_PUFF && (next_desc==0xc58ed8 || next_desc==0xc58e9c))return role;
        if(role==TLK_MD_SPRITE_LATER_PICKUP && (next_desc==0xc58981 || next_desc==0xc5889a || next_desc==0xc588a6))return role;
        if(role==TLK_MD_SPRITE_PICKUP && (next_desc==0xc5892d || next_desc==0xc58939 || next_desc==0xc58945 || next_desc==0xc58975 || next_desc==0xc586b4))return role;
        return 0;
    }
    if(s_frame.stage && s_md_level==6 && rd16(s_frame.ram+0xdf)==0x4b3) {
        if(role==TLK_MD_SPRITE_LATER_ENEMY && (next_desc==0xc58eb4 || next_desc==0xc58ea8))return role;
        if(role==TLK_MD_SPRITE_DESTINY_MONKEY && next_desc==0xc586d8)return role;
        if(role==TLK_MD_SPRITE_LATER_WORLD && (next_desc==0xc588dd || next_desc==0xc588ed || next_desc==0xc588fd || next_desc==0xc587e4 || next_desc==0xc587f0 || next_desc==0xc587fc || next_desc==0xc58808 || next_desc==0xc58844 || next_desc==0xc586f0))return role;
        if(role==TLK_MD_SPRITE_LATER_EFFECT && next_desc==0xc586cc)return role;
        if(role==TLK_MD_SPRITE_LATER_PICKUP && (next_desc==0xc588b2 || next_desc==0xc588be))return role;
        if(role==TLK_MD_SPRITE_PICKUP && (next_desc==0xc5892d || next_desc==0xc58939 || next_desc==0xc58945 || next_desc==0xc58951 || next_desc==0xc58975))return role;
        return 0;
    }
    if(StampedeScene())return (role==TLK_MD_SPRITE_STAMPEDE_CUB && next_desc==0xc5858a) ||
        (role==TLK_MD_SPRITE_STAMPEDE_ROCK && next_desc==0xc58b3c)?role:0;
    if(ExileScene())return (role==TLK_MD_SPRITE_LIZARD && (next_desc==0xc58c50 || next_desc==0xc58ca4)) ||
        (role==TLK_MD_SPRITE_LATER_WORLD && next_desc==0xc58cb0) ||
        (role==TLK_MD_SPRITE_PORCUPINE && next_desc==0xc58c5c) ||
        (role==TLK_MD_SPRITE_LEAVES && next_desc==0xc5888e) ||
        (role==TLK_MD_SPRITE_PICKUP && (next_desc==0xc5892d || next_desc==0xc58939 || next_desc==0xc586c0))?role:0;
    if(role==TLK_MD_SPRITE_CW_HIPPO)
        return s_cw_scene && !p->fixed && p->actor_descriptor==0xc58ac7?role:0;
    if(role==TLK_MD_SPRITE_CW_RIDE_OBSTACLE)
        return s_cw_scene && !p->fixed &&
            (p->actor_descriptor==0xc4e18d || p->actor_descriptor==0xc4e198 ||
             p->actor_descriptor==0xc4e1a3 || p->actor_descriptor==0xc4e1ae)?role:0;
    if(role==TLK_MD_SPRITE_CW_GIRAFFE)
        return s_cw_scene && !p->fixed &&
            (p->actor_descriptor==0xc58d60 || p->actor_descriptor==0xc58d70 ||
             (p->actor_descriptor==0xc58d80 && p->pose==0xc07f59))?role:0;
    if(role!=TLK_MD_SPRITE_CW_RHINO) {
        if(s_md_level==0)return role>=TLK_MD_SPRITE_GRAVEYARD_VULTURE?0:role;
        if((role!=TLK_MD_SPRITE_HYENA && role!=TLK_MD_SPRITE_GRAVEYARD_VULTURE) || !s_frame.stage || s_md_level!=2 ||
           rd16(s_frame.ram+0xdf)!=0x3eb || p->fixed || p->obj>0xffe8)return 0;
        unsigned descriptor=p->actor_descriptor;
        int owned=role==TLK_MD_SPRITE_HYENA && TlkGraveyardHyenaDrawDescriptor(descriptor);
        if(role==TLK_MD_SPRITE_GRAVEYARD_VULTURE)
            for(unsigned i=0;i<sizeof graveyard_vulture_descriptors/sizeof *graveyard_vulture_descriptors;i++)
                if(descriptor==graveyard_vulture_descriptors[i])owned=1;
        return owned?role:0;
    }
    if(!s_cw_scene || p->fixed || p->obj>0xffe8)return 0;
    return p->actor_descriptor==0xc58c14?role:0;
}
static unsigned SceneNpcRole(const Piece *p,unsigned palette) {
    unsigned role=SceneNpcMappedRole(p,palette);
    return role==TLK_MD_SPRITE_LIZARD && p && TlkEnemyArtPorcupine(p->pose)?kPorcupineArtRole:role;
}
static int SceneNpcSample(const Piece *p,int x,int y,unsigned pixel,int frames,int palette,const uint16_t *cgram,uint16_t *color) {
    unsigned context_pose=SceneNpcPose(p);
    if(context_pose!=p->pose)return TlkMdSpritesNpcSample(context_pose,x,y,pixel,frames,palette,cgram,color);
    if(p && ExileFallingRockPhase(p,(p->attr>>9)&7)>=0)
        return ExileFallingRockSample(p,x,y,pixel,frames,palette,cgram,color);
    if(PreparedFallingRock(p,(p->attr>>9)&7))
        return PreparedFallingRockSample(p,x,y,pixel,frames,palette,cgram,color);
    if(p && s_md_level==5 && ((p->attr>>9)&7)==5 && NextPieceDescriptor(p)==0xc58e9c &&
       TlkMdSpritesDrawRole(p->pose,5)==TLK_MD_SPRITE_LATER_ENEMY)
        return TlkMdSpritesHakunaSpiderSample(p->pose,x,y,pixel,frames,palette,cgram,color);
    if(p && s_md_level==7 && rd16(s_frame.ram+0xdf)==0x4e5 && NextPieceDescriptor(p)==0xc58909 &&
       TlkMdSpritesRole(p->pose)==TLK_MD_SPRITE_LATER_WORLD)
        return TlkMdSpritesNpcSampleBank(p->pose,x,y,pixel,frames,palette,3,cgram,color);
    if(s_md_level==5 && ((p->attr>>9)&7)==5 && NextPieceDescriptor(p)==0xc58e9c &&
       TlkMdSpritesRole(p->pose)==TLK_MD_SPRITE_DEFEAT_PUFF)
        return TlkMdSpritesNpcSampleBank(p->pose,x,y,pixel,frames,palette,5,cgram,color);
    return TlkMdSpritesNpcSample(p->pose,x,y,pixel,frames,palette,cgram,color);
}
static bool ContinueTokenPiece(const Piece *p) {
    return p && s_frame.stage && !((p->attr>>9)&7) &&
        TlkContinueTokenCommonDrawRole(s_frame.ram,sizeof s_frame.ram,p->obj,p->pose,p->fixed);
}
static bool PickupFlightPiece(const Piece *p) {
    return p && p->kept && s_frame.stage && !((p->attr>>9)&7) &&
           TlkPickupFlightDrawRole(s_frame.ram,sizeof s_frame.ram,p->obj,p->pose,p->fixed);
}
static bool PickupPopupPiece(const Piece *p) {
    return p && p->kept && s_frame.stage && !((p->attr>>9)&7) &&
           TlkPickupPopupDrawRole(s_frame.ram,sizeof s_frame.ram,p->obj,p->pose,p->fixed);
}
static int PickupFlightMotionSide(const Piece *p) {
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
    if(TlkPickupFlightSelected() && PickupFlightPiece(p))
        return p->pose==0xc528bc?64:-64;
#endif
    return 0;
}
static int s_md_ending_rain;
static int s_rain_viewport=256;
static bool EndingRainPiece(const Piece *p) {
    return p && p->fixed && s_frame.stage && s_md_level==9 &&
        (rd16(s_frame.ram+0xdf)==0x549 || rd16(s_frame.ram+0xdf)==0x7db) &&
        p->pose==0xc2f33e && !((p->attr>>9)&7) && NextPieceDescriptor(p)==0xc585d0;
}
/* Weather belongs to the screen, not the map or the HUD's top/bottom bands.
 * Repeat the current source particle field into added view space. No new
 * actors, clocks or random motion are introduced by the presentation. */
static bool ExpandedEndingRain(const Piece *p,int width) {
    return EndingRainPiece(p) && (width>s_rain_viewport ||
           (s_area_active && s_area_height>224));
}
static int RainModulo(int value,int period) {
    int result=value%period;return result<0?result+period:result;
}
static bool FixedEffectPiece(const Piece *p) {
    return EndingRainPiece(p) || CommonPickupFlightPiece(p) || PickupPopupPiece(p);
}
/* Expanded views expose the flat endpoint behind the ordinary camera.
 * Its native shared neck tiles match the static flat-head body exactly:
 * translating the664/289 head's neck by1424/16 reaches the original2086/304
 * static head attachment, giving662/288. Keep gameplay anchors independent.
 * Static heads with MD contacts omit the native six-pixel X initializer;
 * restore that artwork attachment only when drawing native scenery/head art. */
static void GiraffeSceneryShift(const Piece *p,int *x,int *y) {
    *x=*y=0;
    if(!p || p->fixed || !s_enabled || (s_handoff_width<=320 && (!s_area_active || s_area_height<=224)) ||
       rd16(s_frame.ram+0x1ff9e)!=1 || rd24(s_frame.ram+0xdf)!=0xc003b9 || p->pose!=0xc07f59 ||
       TlkResourcesUseMd("graphics.scenery.foreground") ||
       TlkResourcesUseMd("graphics.sprites.animals.giraffes.frames"))return;
    if(p->actor_descriptor==0xc58d70 && (p->attr&0x4000)){*x=-2;*y=-1;}
    if(p->actor_descriptor==0xc58d80 && TlkResourcesUseMd("gameplay.levels.cant_wait.giraffe_platforms"))*x=6;
}
static void ScenePieceShift(const Piece *p,int *x,int *y) {
    GiraffeSceneryShift(p,x,y);
    if(s_area_active&&p&&p->fixed){
        /* HUD-bound pickup effects must not change vertical anchors when
         * their moving X crosses the centre (where the inferred side is0),
         * or when individual drawing pieces cross the generic Y bands. */
        if(EndingRainPiece(p))*y=(s_area_height-224)/2-s_area_top;
        else if(CommonPickupFlightPiece(p))*y=-s_area_top;
        else if(p->y>=168)*y=s_area_height-224-s_area_top;
        else if(HudMeter(p)>=0||(p->y<=64&&p->side))*y=-s_area_top;
        else *y=(s_area_height-224)/2-s_area_top;
    }
    /* Fixed native pieces are centred on256. MD weather occupies320,
     * independently of the selected rain image or palette. */
    if(EndingRainPiece(p) && s_md_ending_rain)*x=-32;
    if(PickupPopupPiece(p) && TlkResourcesUseMd("graphics.sprites.effects.pickup_arrival.position")) {
        unsigned position=rd16(s_frame.ram+p->obj+4);
        *x=rd16(s_frame.ram+position)==226 ? 4 : 2;
        *y=-4;
    }
}
static bool TitlePiece(const Piece *p) {
    if(!p || !s_frame.stage || (p->attr>>9&7) || (p->attr&0xc000) || p->size!=16 ||
       p->local_x<0 || p->local_x>208 || (p->local_x&15) || p->local_x==48 ||
       !TlkPrideTitleDrawRole(s_frame.ram,sizeof s_frame.ram,s_rom,s_rom_size,p->obj,p->pose,p->fixed))return false;
    unsigned cell=(unsigned)p->local_x/16,glyph=cell-(cell>3);
    int live=(int16_t)rd16(s_frame.ram+0x17dd+27+glyph*6+2);
    int next=p->local_y+4;if(next>0)next=0;
    return p->local_y>=-128 && p->local_y<=0 && (p->local_y==live || next==live);
}

/* Later main levels use the same falling-font task, sometimes with several
 * lines. Its native anchor uses the last line's width. Centre each displayed
 * line independently, retaining the original glyphs and vertical motion. */
static int s_caption_centre[kMaxPieces];
static unsigned s_caption_slot[kMaxPieces];
static bool s_caption_pass;
static int OpeningCaptionCentre(const Piece *p) {
    return p?s_caption_centre[p-s_frame.pieces]:0;
}
static unsigned OpeningCaptionSlot(const Piece *p) {
    return p?s_caption_slot[p-s_frame.pieces]:0;
}
static void PrepareOpeningCaptions(void) {
    memset(s_caption_centre,0,sizeof s_caption_centre);
    memset(s_caption_slot,0,sizeof s_caption_slot);
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    if(!s_frame.stage || level<1 || level>13 ||
       (rd16(s_frame.ram+0x2000)!=0 && rd16(s_frame.ram+0x2000)!=0xffff) ||
       (!BonusScene() && TlkTitlePointer(s_frame.ram,0xdf)!=0xc00387+level*0x32))return;
    for(unsigned start=0,end;start<s_frame.piece_count;start=end) {
        const Piece *first=&s_frame.pieces[start];end=start+1;
        while(end<s_frame.piece_count && s_frame.pieces[end].obj==first->obj)end++;
        unsigned draw=first->obj;
        if((first->pose!=0x7e17dd && first->pose!=0x7e19f8) || draw<0x8000 || draw>0xffe8)continue;
        unsigned pos=rd16(s_frame.ram+draw+4);if(pos<0x8008 || pos>0xff88)continue;
        unsigned actor=pos-8,packet=first->pose&65535,count=rd16(s_frame.ram+packet);
        unsigned action=TlkTitlePointer(s_frame.ram,actor+0x30);
        bool hint=level==1 && action==0xc06973 &&
            (TlkResourcesUseMd("graphics.titles.remaining.frames") ||
             TlkResourcesUseMd("graphics.titles.remaining.palette") ||
             TlkResourcesUseMd("graphics.titles.remaining.position"));
        if(rd16(s_frame.ram+actor+12)!=draw || TlkTitlePointer(s_frame.ram,draw+10)!=first->pose ||
           TlkTitlePointer(s_frame.ram,actor+4)!=(hint?0xc588ce:0xc588cb) ||
           (first->fixed && !hint) ||
           (action!=0xc0679e && !hint) ||
           (s_frame.ram[draw+8]&14) || ((s_frame.ram[draw+9]&0x40) && !hint) ||
           rd16(s_frame.ram+actor+0x2c)>150 || !count || count>64 || end-start!=count ||
           rd16(s_frame.ram+packet+8)!=255 || s_frame.ram[packet+26]!=0xe8)continue;
        unsigned caption=TlkResourcesCaptionMatch(level,hint,s_frame.ram+packet,sizeof s_frame.ram-packet);
        if(hint && !caption)continue;
        int centres[64],row=0;unsigned line=0;bool valid=true;
        for(unsigned n=0;n<count;n++) {
            unsigned at=packet+27+n*6;int x=(int16_t)rd16(s_frame.ram+at);
            if(n && x<=(int16_t)rd16(s_frame.ram+at-6)) {
                int centre=((int16_t)rd16(s_frame.ram+packet+27+line*6)+
                            (int16_t)rd16(s_frame.ram+at-6)+16)/2;
                for(unsigned k=line;k<n;k++)centres[k]=centre;
                line=n;if(++row>3){valid=false;break;}
            }
            const Piece *p=&s_frame.pieces[start+n];int y=(int16_t)rd16(s_frame.ram+at+2);
            unsigned glyph=rd16(s_frame.ram+at+4);
            /* Lines can enter from opposite edges. Use the captured piece's
             * actual Y; RAM can already contain the following animation step.
             * Punctuation has a shorter advance (Destiny's apostrophe is6),
             * so valid glyph X positions need not be multiples of16. */
            if(p->pose!=first->pose || p->fixed!=first->fixed || p->size!=16 || (p->attr&0xce00) ||
               x<0 || x>496 || p->local_x!=x || y< -256 || y>512 ||
               abs(p->local_y-y)>16 || glyph<0x88ef || glyph>0x9fff ||
               (glyph&127)!=0x6f){valid=false;break;}
        }
        if(!valid)continue;
        int centre=((int16_t)rd16(s_frame.ram+packet+27+line*6)+
                    (int16_t)rd16(s_frame.ram+packet+27+(count-1)*6)+16)/2;
        for(unsigned n=line;n<count;n++)centres[n]=centre;
        for(unsigned n=0;n<count;n++) {
            s_caption_centre[start+n]=centres[n];s_caption_slot[start+n]=caption;
        }
    }
}

/* Where the wide view sits. The game clamps its camera x between $A6EC and
 * $D8 ($C0B273..$C0B284; in every level 0 and the map width - 256), and the
 * wide view stops where the camera stops: its left edge is the camera minus
 * the margin, kept inside [$A6EC, $D8 + 256]. A level narrower than the view
 * is centred. Returns the native picture's column in a view width wide;
 * *lo/*hi get the view columns that lie inside the camera's range. */
/* Reproject the completed ride camera while its wide-window entry framing
 * eases over the first512 pixels actually ridden. Guest travel/camera stay
 * console-sized; pause and saves use the same completed source distance. */
static int RideHandoffWeight(void) {
    unsigned travel=rd16(s_frame.ram+0xa40);
    if(!s_ride_handoff.loop || s_ride_handoff.loop!=rd16(s_frame.ram+0xa56) || travel>=512)return 0;
    /* Ease the presentation offset at both ends. A linear decay starts an
     * extra pan instantly and stops it instantly; the full-width handoff is
     * conspicuous at3x scale. Distance comes from the completed ride update,
     * so pause, repeated draws and saved history keep the same position. */
    int64_t distance=travel;
    return (int)((512LL*512*512-3*distance*distance*512+2*distance*distance*distance)/(512LL*512));
}
static int RideHandoffColumn(int width) {
    if(width<=320)return 0;
    int shift=s_ride_handoff.shift*RideHandoffWeight()/512;
    return shift>width-256?width-256:shift;
}
static int ViewColumn(const uint8_t *ram, int camera, int width, int *lo, int *hi) {
    extern int TlkCameraActive(void);
    if (TlkCameraActive()) {
        *lo=0;*hi=width;
        /* The summit/ending camera remains scripted at console width. Centre
         * that framing inside a taller free view without enlarging its pixels
         * or feeding the extra presentation width back into the script. */
        if(ram==s_frame.ram && s_area_active && s_area_height>224 &&
           rd16(ram+0x1ff9e)==9 && rd24(ram+0xdf)==0xc007db){
            int canonical=TlkResourcesViewportForScene(9);
            if(width>canonical)return (width-canonical)/2;
        }
        if(ram==s_frame.ram && rd16(ram+0x1ff9e)==1 && rd24(ram+0xdf)==0xc003b9)
            return RideHandoffColumn(width);
        return 0;
    }
    int extra = (width - 256) / 2, min = (int)rd16(ram + 0xA6EC), max = (int)rd16(ram + 0xD8);
    *lo = 0;
    *hi = width;
    if (min > max) return extra;
    int left = camera - extra, last = max + 256 - width;
    if (last < min) left = (min + last) / 2;
    else left = left < min ? min : left > last ? last : left;
    int column = camera - left;
    column = column < 0 ? 0 : column > width - 256 ? width - 256 : column;
    left = camera - column;
    if (min - left > 0) *lo = min - left;
    if (max + 256 - left < width) *hi = max + 256 - left;
    return column;
}

/* How far towards an edge a HUD sprite centred at native column c goes, in
 * 64ths: all the way within 64 pixels of the native edge (health, roar,
 * lives), not at all within 16 of the middle (titles, centred text), and in
 * between in proportion, so one that flies across the screen (a bug on its
 * way to the health box) moves smoothly instead of jumping by the margin. */
int TlkWideViewColumn(int camera,int width) {
    int lo,hi;
    return ViewColumn(g_ram,camera,width,&lo,&hi);
}
static int8_t HudSide(int c) {
    int d = c - 128, a = d < 0 ? -d : d;
    int w = a <= 16 ? 0 : a >= 64 ? 64 : (a - 16) * 64 / 48;
    return (int8_t)(d < 0 ? -w : w);
}

/* The view's margins left and right of the native picture, from the live
 * camera ($B29B), for the spawn and draw tests. */
static int s_spawn_height=224;
/* The adult-level loader flies its camera across the map before creating
 * Simba and the HUD. Extra world visibility waits until the player is ready;
 * the selected console's own activation rectangle still initializes normally.
 * Cub stages retain their established initial-activation scans, including
 * Pride's selected settled-camera scan before the player controller starts. */
static bool LiveSpawnViewport(void) {
    unsigned level=rd16(g_ram+0x1ff9e);
    if(level>=10)return true;
    if(s_spawn_height<=224 && 256+2*s_spawn_lead<=TlkResourcesViewportForScene(level))return true;
    unsigned action=rd24(g_ram+0xb243);
    /* Cub checkpoint reloads also fly the camera before the hero controller
     * is initialized. Extra activation along that flight can exhaust the
     * native actor pool. Keep the console scan until the retry initializer
     * hands back a live controller; ordinary cub cold starts stay unchanged. */
    if(level<6 && !(rd16(g_ram+0x1ffa2) && rd16(g_ram+0x2004) && !action))return true;
    return rd24(g_ram+0xb217)==0xc5858a && action>=0xc30000 && action<0xc40000;
}
static void VerticalMargins(int *top,int *bottom) {
    *top=*bottom=0;
    unsigned level=rd16(g_ram+0x1ff9e);
    bool hunt=level>=11 && level<=13 && rd24(g_ram+0xdf)==0xc0060f+(level-11)*0x32;
    if(s_spawn_height<=224 || (level>9 && !hunt) || level==3 ||
       (rd16(g_ram+0x1ff9e)==1 && rd16(g_ram+0xa56)))return;
    int camera=(int)rd16(g_ram+0xb29d)+1,map_height=(int)rd16(g_ram+0xd4)*16;
    if(map_height<224)return;
    int origin=camera-(s_spawn_height-224)/2;
    unsigned key=0x80000000u|(rd16(g_ram+0x1ff9e)<<10)|(unsigned)s_spawn_height;
    unsigned scene=rd16(g_ram+0xdf)|(rd16(g_ram+0xa56)<<16);
    if(s_free_view_key==key && s_free_view_scene==scene)origin=s_free_view_origin;
    if(map_height>=s_spawn_height){if(origin<0)origin=0;if(origin>map_height-s_spawn_height)origin=map_height-s_spawn_height;}
    else origin=(map_height-s_spawn_height)/2;
    *top=camera-origin;if(*top<0)*top=0;
    *bottom=s_spawn_height-224-*top;if(*bottom<0)*bottom=0;
}
static void WidenVertical(CpuState *cpu,unsigned pc) {
    if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag)return;
    if((pc==0xb927 || pc==0xb932) && !LiveSpawnViewport())return;
    int top,bottom;VerticalMargins(&top,&bottom);if(!top&&!bottom)return;
    if(pc==0xb927){
        /* Original STA $16 has completed: widen the bottom queue/cull row. */
        unsigned row=rd16(g_ram+0x16)+(unsigned)((bottom+15)/16)*2;
        unsigned limit=rd16(g_ram+0xd4)*2-2;if(row>limit)row=limit;
        g_ram[0x16]=(uint8_t)row;g_ram[0x17]=(uint8_t)(row>>8);
    }else if(pc==0xb932){
        /* Before LDA $48, after the bottom bound was calculated. The original
         * top-margin subtraction and source-selected queue behavior follow. */
        unsigned row=rd16(g_ram+0x48),extra=(unsigned)((top+15)/16)*2;
        row=row>extra?row-extra:0;g_ram[0x48]=(uint8_t)row;g_ram[0x49]=(uint8_t)(row>>8);
    }else{
        unsigned object=rd16(g_ram+0x7c);
        if(object<0x8000 || object>0xffe8 || (g_ram[object+9]&0x40))return;
        if(pc==0xa5e3){unsigned limit=rd16(g_ram+0x14)+(unsigned)bottom;
            g_ram[0x14]=(uint8_t)limit;g_ram[0x15]=(uint8_t)(limit>>8);
        }else if(pc==0xa5ed)cpu->A=(uint16_t)(cpu->A+top);
    }
}
/* The original300px cycle is gameplay, independent of window height.
 * Lengthening it with the same actor count left gaps in the platform stream.
 * Extra visible turns are presented without changing these operands. */
static void WaterfallLogViewport(CpuState *cpu,unsigned pc) {
    if(!s_enabled || rd16(g_ram+0x1ff9e)!=5 ||
       rd24(g_ram+0xdf)!=0xc00481 || cpu->PB!=0xc4 || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->_flag_D)return;
    unsigned actor=rd16(g_ram+0x68);
    if(actor<0xb213 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       rd24(g_ram+actor+4)!=0xc58aec)return;
    int top,bottom;VerticalMargins(&top,&bottom);
    int adjust=pc==0x8efc?bottom:pc==0x8f0c?-(top+bottom):
               pc==0x8f41?-top:top+bottom;
    /* The following original ADC/SBC consumes its original carry and
     * produces the flags used by its branch. Leave those flags alone here. */
    (void)adjust;
    static FILE *f;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_WATERFALL_VIEW_TRACE");if(path){f=fopen(path,"w");if(f)fputs("field,pc,actor,x,y,top,bottom,period\n",f);}}
    if(f){extern int snes_frame_counter;fprintf(f,"%d,%04x,%04x,%u,%u,%d,%d,%d\n",snes_frame_counter+1,pc,actor,rd16(g_ram+actor+8),rd16(g_ram+actor+10),top,bottom,300);fflush(f);}
}
static void PresentationMargins(int lead,int *left,int *right) {
    int lo,hi,width=256+2*lead;
    *left=ViewColumn(g_ram,(int)rd16(g_ram+0xb29b),width,&lo,&hi);
    *right=width-256-*left;
}
static void LiveMargins(int lead, int *left, int *right) {
    /* The ride parser can start within a field, before the presenter sees its
     * first latched ride frame. Never advance that finite strip by a free-view
     * margin from the preceding ordinary terrain. */
    if(rd16(g_ram+0x1ff9e)==1 && rd24(g_ram+0xdf)==0xc003b9 && rd16(g_ram+0xa56)) {
        int maximum=(TlkResourcesViewportForScene(1)-256)/2;
        if(lead>maximum)lead=maximum;
    }
    int lo, hi, width = 256 + 2 * lead;
    *left = ViewColumn(g_ram, (int)rd16(g_ram + 0xB29B), width, &lo, &hi);
    *right = width - 256 - *left;
}
bool TlkWideActorInView(int x,int y,int margin) {
    if(!s_enabled || (s_spawn_lead<=0 && s_spawn_height<=224) || !LiveSpawnViewport())return false;
    int left=0,right=0,top,bottom;
    if(s_spawn_lead>0)LiveMargins(s_spawn_lead,&left,&right);
    VerticalMargins(&top,&bottom);
    int cx=rd16(g_ram+0xb29b),cy=(int)rd16(g_ram+0xb29d)+1;
    return x>=cx-left-margin && x<cx+256+right+margin &&
           y>=cy-top-margin && y<cy+224+bottom+margin;
}
bool TlkWideRetreatMargins(int *left,int *right,int *bottom) {
    if(!s_enabled || !LiveSpawnViewport() ||
       (s_spawn_height<=224 && 256+2*s_spawn_lead<=TlkResourcesViewportForScene(rd16(g_ram+0x1ff9e))))return false;
    int top;
    *left=*right=0;
    if(s_spawn_lead>0)LiveMargins(s_spawn_lead,left,right);
    VerticalMargins(&top,bottom);
    return true;
}

/* ── Piece recorder ────────────────────────────────────────────────────── */

/* A guest read for the recorder: WRAM or HiROM, nothing with side effects. */
static int Bus8(uint32_t a) {
    unsigned bank = (a >> 16) & 0xFF, off = a & 0xFFFF;
    if (bank == 0x7E) return g_ram[off];
    if (bank == 0x7F) return g_ram[0x10000 + off];
    if ((bank & 0x7F) < 0x40 && off < 0x2000) return g_ram[off];
    if (bank >= 0xC0 || ((bank & 0x7F) >= 0x40 && (bank & 0x7F) < 0x7E) ||
        ((bank & 0x7F) < 0x40 && off >= 0x8000)) {
        uint32_t r = ((uint32_t)(bank & 0x3F) << 16) | off;
        return s_rom && r < s_rom_size ? s_rom[r] : -1;
    }
    return -1;
}
static int Bus16(uint32_t a) {
    int lo = Bus8(a), hi = Bus8((a & 0xFF0000) | ((a + 1) & 0xFFFF));
    return lo < 0 || hi < 0 ? -1 : lo | hi << 8;
}

/* $C0A727 / $C0A7AE at entry (M=0 X=1, D=0 in every recorded call): the
 * piece's offset is at [$99], the object's screen position at $B4/$B6, its
 * flips at $AF/$B2, tile index at $93, attribute bits at $B1. This repeats
 * the routine's arithmetic without its screen test. */
static void RecordPiece(const CpuState *cpu, bool big) {
    if (cpu->m_flag || !cpu->x_flag || s_build_count >= kMaxPieces) return;
    const uint32_t d = cpu->D;
#define DP8(a) Bus8((d + (a)) & 0xFFFF)
#define DP16(a) Bus16((d + (a)) & 0xFFFF)
    int lo = DP16(0x99), bank = DP8(0x9B);
    if (lo < 0 || bank < 0) return;
    uint32_t ptr = (uint32_t)bank << 16 | (uint32_t)lo;
    int dx = Bus16(ptr), dy = Bus16((ptr & 0xFF0000) | ((ptr + 2) & 0xFFFF));
    int vflip = DP8(0xB2), hflip = DP8(0xAF), sx = DP16(0xB4), sy = DP16(0xB6);
    int index = DP16(0x93), bits = DP16(0xB1), slot = DP8(0xA8), yoff = DP8(0x8C), obj = DP16(0x7C);
    if (dx < 0 || dy < 0 || vflip < 0 || hflip < 0 || sx < 0 || sy < 0 || index < 0 || bits < 0 ||
        slot < 0 || yoff < 0 || obj < 0)
        return;
    /* $C0A58E: an object with obj+9 bit 6 is drawn with the camera ($52/$54) at zero. */
    int flags = Bus8((uint32_t)cpu->DB << 16 | ((obj + 9) & 0xFFFF));
    int local_x=dx,local_y=dy;
    int pose_lo=DP16(0x85),pose_bank=DP8(0x87);
    if (vflip & 0x80) dy = ((dy ^ 0xFFFF) - (big ? 0x10 : 0x08)) & 0xFFFF;
    if (hflip) dx = ((dx ^ 0xFFFF) - (big ? 0x0F : 0x07)) & 0xFFFF;
    int16_t y = (int16_t)(dy + sy), x = (int16_t)(dx + sx);
    /* 16x16: TAY with 8-bit index; 8x8: REP #$10 first. */
    unsigned table = big ? 0xACFD + ((index << 1) & 0xFF) : 0xACFD + 0x100 + ((index << 1) & 0xFFFF);
    int attr = Bus16((uint32_t)cpu->DB << 16 | (table & 0xFFFF));
    if (attr < 0) return;
#undef DP8
#undef DP16
    int lo_lim = big ? -15 : -7, y_lim = big ? 0xEF : 0xE0;
    bool kept = x >= lo_lim && x < 256 && y >= lo_lim && y < y_lim;
    s_build[s_build_count++] = (Piece){ x, (int16_t)(y - yoff), (uint16_t)(attr | bits), (uint16_t)obj,
                                        (uint8_t)(big ? 16 : 8), (uint8_t)slot, kept,
                                        flags >= 0 && (flags & 0x40), 0,
                                        pose_lo>=0 && pose_bank>=0 ? (uint32_t)pose_lo | (uint32_t)pose_bank<<16 : 0,
                                        (int16_t)local_x,(int16_t)local_y,0 };
    Piece *submitted=&s_build[s_build_count-1];
    submitted->actor_descriptor=DrawActorDescriptor(g_ram,submitted->obj,submitted->pose);
    submitted->hyena_art_context=(uint8_t)TlkHyenaContextCapture(g_ram,0x20000,submitted->obj,
        submitted->pose,submitted->fixed,submitted->actor_descriptor);
    if(submitted->hyena_art_context)s_hyena_context_seen|=1u<<(submitted->hyena_art_context-1);
    if(!submitted->actor_descriptor && TlkGraveyardPillarOwner(g_ram,submitted->obj,submitted->pose))
        submitted->actor_descriptor=0xc58d44;
    /* Replace the provisional source part with the actual native submission.
     * Keep its OAM slot/tile/kept state and avoid a duplicate host drawing. */
    for(unsigned n=0;n+1<s_build_count;n++) {
        Piece *prior=&s_build[n];
        if(prior->slot==127 && !prior->kept && prior->obj==submitted->obj &&
           prior->pose==submitted->pose && prior->local_x==submitted->local_x &&
           prior->local_y==submitted->local_y && prior->size==submitted->size) {
            *prior=*submitted;s_build_count--;submitted=prior;break;
        }
    }
    if (rd16(g_ram+0x1ff9e)==0 && (rd16(g_ram+0xdf)==0x387 || rd16(g_ram+0xdf)==0x80d))
        TlkMdSpritesObserveNpc(submitted->pose,((unsigned)(attr|bits)>>9)&7);
    /* Unique native pose/palette evidence for semantic MD sprite adapters. */
    static FILE *pose_trace;static int opened;
    static uint32_t logged[8192];static unsigned logged_count;
    if (!opened) { const char *path=getenv("TLK_SPRITE_OBJECTS");opened=1;if (path) pose_trace=fopen(path,"w");
        if (pose_trace) fprintf(pose_trace,"frame,object,position,pose,flags,palette,colors\n"); }
    if (pose_trace && rd16(g_ram+0x1ff9e)==0 && (rd16(g_ram+0xdf)==0x387 || rd16(g_ram+0xdf)==0x80d)) {
        const Piece *piece=submitted;
        unsigned palette=((unsigned)(attr|bits)>>9)&7;
        uint32_t key=piece->pose | palette<<24;unsigned n=0;
        for (;n<logged_count;n++) if (logged[n]==key) break;
        if (n==logged_count && n<8192) {
            logged[logged_count++]=key;
            fprintf(pose_trace,"%d,%04x,%04x,%06x,%04x,%u,",snes_frame_counter,(unsigned)obj,
                    (unsigned)(obj<=0xfffa?rd16(g_ram+(unsigned)obj+4):0),piece->pose,(unsigned)flags,palette);
            for (unsigned c=0;c<16;c++) fprintf(pose_trace,"%04x",g_ppu->cgram[128+palette*16+c]);
            fprintf(pose_trace,"\n");fflush(pose_trace);
        }
    }
}

/* Wide/tall margins can admit more drawings than the original127-piece
 * guest submission budget. Keep a source-validated static bonus-bug intent
 * when that budget is full; guest OAM, allocator and gameplay stay unchanged.
 * This existing seam is after original hidden/blink and horizontal tests. */
static void RecordBonusPickupIntent(const CpuState *cpu) {
    if(!s_enabled || cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag ||
       s_build_count>=kMaxPieces || g_ram[0xad]<127)return;
    unsigned obj=rd16(g_ram+0x7c),pose=rd24(g_ram+0x85);
    if(obj<0x8000 || obj>0xffe8)return;
    unsigned descriptor=DrawActorDescriptor(g_ram,obj,pose);
    if(!((descriptor==0xc586b4 && pose==0xc52a0e) ||
         (descriptor==0xc586c0 && pose==0xc529ed)))return;
    unsigned at=pose&0x3fffff;if(at+33>s_rom_size || rd16(s_rom+at)!=0x8101)return;
    int dx=(int16_t)rd16(s_rom+at+29),dy=(int16_t)rd16(s_rom+at+31);
    unsigned flags=rd16(g_ram+obj+8);int lx=dx,ly=dy;
    if(flags&0x40)dx=-dx-16;if(flags&0x80)dy=-dy-17;
    int x=(int16_t)(rd16(g_ram+0x88)-rd16(g_ram+0x52))+dx;
    int y=(int16_t)(rd16(g_ram+0x8a)-rd16(g_ram+0x54))+dy-g_ram[0x8c];
    if(x<256 && x+16>0 && y<224 && y+16>0)return;
    s_build[s_build_count++]=(Piece){.x=(int16_t)x,.y=(int16_t)y,.attr=(uint16_t)(flags<<8),
        .obj=(uint16_t)obj,.size=16,.slot=127,.kept=false,.fixed=false,.pose=pose,
        .local_x=(int16_t)lx,.local_y=(int16_t)ly,.actor_descriptor=descriptor};
    static FILE *trace;static int opened;extern int snes_frame_counter;
    if(!opened){opened=1;const char *path=getenv("TLK_PICKUP_BUDGET_TRACE");if(path)trace=fopen(path,"w");
        if(trace)fputs("field,packet,pose,native_pieces,x,y\n",trace);}
    if(trace){fprintf(trace,"%d,%04x,%06x,%u,%d,%d\n",snes_frame_counter,obj,pose,g_ram[0xad],x,y);fflush(trace);}
}

/* The game's spawn window ($C0B8EA, run by the camera object): tile columns
 * from 12 (96 px) left of the camera to 42 (336 px, 80 past the native right
 * edge) right of it, 16-pixel aligned, clamped to the map ($D0 = its width in
 * tiles). Enemies inside it are created; the despawn bounds $B203/$B205 come
 * from the same columns. Widening both by the picture's margin keeps the
 * game's own lead beyond the wider view. This changes the game. */
static void WidenSpawn(CpuState *cpu) {
    const uint32_t d = cpu->D;
    /* The MD camera is stored at native raster Y = MD Y - 1. Convert back
     * before the original spawn grid quantizes it: at Y=16n-1, using native
     * Y would select the preceding row. This seam follows STA $48 and precedes
     * CLC/ADC of the bottom row, so both bounds and the original queue scan
     * consume the same selected row. Horizontal width remains independent. */
    if (TlkCameraActive() && d==0 && cpu->DB==0x7e && !cpu->m_flag && cpu->x_flag &&
        rd16(g_ram+0x68)==0xb293) {
        unsigned y=rd16(g_ram+0xb29d),row=(y>>3)&65534;
        if ((y&15)==15 && cpu->A==row && rd16(g_ram+0x48)==row) {
            cpu->A=(uint16_t)(row+2);g_ram[0x48]=(uint8_t)cpu->A;g_ram[0x49]=(uint8_t)(cpu->A>>8);
            cpu->_flag_N=!!(cpu->A&32768);cpu->_flag_Z=!cpu->A;cpu_mirrors_to_p(cpu);
        }
    }
    /* Observe the initial spawn pass as well as later per-frame updates:
     * a level can become active partway through the original loader. */
    static FILE *trace;static int trace_init;
    if (!trace_init) { const char *p=getenv("TLK_SPAWN_WINDOW_TRACE");trace_init=1;
        if(p)trace=fopen(p,"w");
        if(trace)fprintf(trace,"frame,level,descriptor,d,db,m,x,cached_lead,camera_active,camera_width,left,right,camera_x,camera_y,caller\n"); }
    if(trace && d==0) {
        extern int snes_frame_counter;extern int TlkCameraActive(void);extern int TlkCameraViewWidth(void);
        unsigned camera=rd16(g_ram+0x68);
        fprintf(trace,"%d,%u,%u,%u,%u,%u,%u,%d,%d,%d,%u,%u,%u,%u,%04x\n",snes_frame_counter,
            rd16(g_ram+0x1ff9e),rd16(g_ram+0xdf),(unsigned)d,(unsigned)cpu->DB,
            (unsigned)cpu->m_flag,(unsigned)cpu->x_flag,s_spawn_lead,TlkCameraActive(),TlkCameraViewWidth(),
            rd16(g_ram+0x46),rd16(g_ram+0x14),rd16(g_ram+((camera+8)&65535)),
            rd16(g_ram+((camera+10)&65535)),rd16(g_ram+((cpu->S+1)&65535)));fflush(trace);
    }
    if (s_spawn_lead <= 0 || ((d + 0xD1) & 0xFFFF) >= 0x2000 || !LiveSpawnViewport()) return;
    int ml, mr;
    LiveMargins(s_spawn_lead, &ml, &mr);
    unsigned kl = (unsigned)(ml + 15) / 16 * 2, kr = (unsigned)(mr + 15) / 16 * 2;
    uint8_t *left = &g_ram[(d + 0x46) & 0xFFFF], *right = &g_ram[(d + 0x14) & 0xFFFF];
    unsigned l = left[0] | left[1] << 8, r = right[0] | right[1] << 8;
    unsigned cap = (unsigned)(g_ram[(d + 0xD0) & 0xFFFF] | g_ram[(d + 0xD1) & 0xFFFF] << 8) - 2;
    l = l > kl ? l - kl : 0;
    r = r + kr < cap ? r + kr : (cap > r ? cap : r);
    left[0] = (uint8_t)l; left[1] = (uint8_t)(l >> 8);
    right[0] = (uint8_t)r; right[1] = (uint8_t)(r >> 8);
}

/* Diagnostics: TLK_WIDE_OBJLOG=<path> writes, at each latch, one line per
 * drawn object: frame, object, x0 x1 y0 y1 of its pieces, fixed, obj+4, and
 * the view's left and right margins (from the camera, as drawn). Pop-in
 * shows as an object whose first box is already inside the view
 * (scripts/wide_popin.py). */
static void ObjLog(void) {
    static FILE *f;
    static int init;
    if (!init) { const char *e = getenv("TLK_WIDE_OBJLOG"); if (e) f = fopen(e, "w"); init = 1; }
    extern int snes_frame_counter;
    for (unsigned i = 0, j; f && i < s_latched_count; i = j) {
        int x0 = 1 << 15, x1 = -(1 << 15), y0 = 1 << 15, y1 = -(1 << 15);
        for (j = i; j < s_latched_count && s_latched[j].obj == s_latched[i].obj; j++) {
            const Piece *q = &s_latched[j];
            if (q->x < x0) x0 = q->x;
            if (q->x + q->size > x1) x1 = q->x + q->size;
            if (q->y < y0) y0 = q->y;
            if (q->y + q->size > y1) y1 = q->y + q->size;
        }
        unsigned o = s_latched[i].obj;
        int ml = s_draw_extra, mr = s_draw_extra;
        if (s_draw_extra) LiveMargins(s_draw_extra, &ml, &mr);
        fprintf(f, "%d %04x %d %d %d %d %d %u %d %d\n", snes_frame_counter, o, x0, x1, y0, y1, s_latched[i].fixed,
                (unsigned)(g_ram[(o + 4) & 0xFFFF] | g_ram[(o + 5) & 0xFFFF] << 8), ml, mr);
    }
}

/* FN_C0A5BA draws an object only if its box overlaps camera..camera+256
 * horizontally; otherwise no piece is even submitted, so an object alive in a
 * margin is never seen. Widen that test by the margin: the right limit in $14,
 * and the box's left edge in A for the left test (the hook point is an LDY, so
 * A holds the same value before and after it, compiled or interpreted). Every
 * piece of such an object still fails the game's own OAM test, so OAM is the
 * same; what changes is the drawing work itself (tile uploads, CPU time). */
static bool HuntBugDrawMargins(const CpuState *cpu,int *left,int *right) {
    unsigned level=rd16(g_ram+0x1ff9e);
    if(level<11 || level>13 || rd24(g_ram+0xdf)!=0xc0060f+(level-11)*0x32 ||
       cpu->D || cpu->DB!=0x7e || !cpu->x_flag ||
       !TlkResourcesUseMd("gameplay.bonus.bug_hunt.draw_bounds"))return false;
    unsigned obj=rd16(g_ram+0x7c);
    if(obj<0x8000 || obj>0xffe8 || (g_ram[obj+9]&0x40))return false;
    unsigned position=rd16(g_ram+obj+4),actor=position>=0x8008?position-8:0;
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) || rd16(g_ram+actor+12)!=obj)return false;
    unsigned descriptor=rd24(g_ram+actor+4);
    if(descriptor!=0xc58975 && !(descriptor>=0xc58a11 && descriptor<=0xc58a65 &&
                               (descriptor-0xc58a11)%12==0))return false;
    /* Match the visible world window without changing camera tracking or the
     * original activation/catch code. Optional extra widening still applies. */
    int lead=(TlkResourcesViewportWidth()-256)/2;
    if(s_spawn_lead>lead)lead=s_spawn_lead;
    if(lead<=0)return false;
    LiveMargins(lead,left,right);return true;
}
static void WidenCull(CpuState *cpu, bool right) {
    if (cpu->m_flag) return;
    int ml, mr;
    unsigned native, external;
    if (rd16(g_ram+0x1ff9e)==10 && rd24(g_ram+0xdf)==0xc005dd &&
        TlkResourcesUseMd("gameplay.bonus.bug_toss.culling_bounds") &&
        TlkStartDataBonusValue(2,&native,&external) && external>native) {
        /* Toss uses a fixed MD canvas beginning at X=0. Its actors can reach
         * the prepared wider arena even with optional enemy widening off.
         * Keep their drawing alive there too; symmetric world-view margins
         * can still reject Timon while he throws at the right-hand limit. */
        ml=0;mr=(int)(external-native);
    } else if(HuntBugDrawMargins(cpu,&ml,&mr)) {
        /* Hunt bugs may be alive in the wide margins before the native
         * 256-pixel draw test admits them. Submit their actual source pieces. */
    } else {
        if (s_spawn_lead <= 0) return;
        PresentationMargins(s_spawn_lead, &ml, &mr);
    }
    if (right) {
        uint8_t *lim = &g_ram[(cpu->D + 0x14) & 0x1FFF];
        unsigned v = (unsigned)(lim[0] | lim[1] << 8) + (unsigned)mr;
        lim[0] = (uint8_t)v; lim[1] = (uint8_t)(v >> 8);
    } else {
        cpu->A = (uint16_t)(cpu->A + ml);
    }
}

/* The ostrich ride's obstacles come from a script, not the spawn window:
 * while $0A56 is set, $C0B5FD compares the distance ridden ($0A40, the
 * camera's x travel) with the next entry of a table at [$BA] and, once
 * reached, $C0BB80 creates the obstacles at x + $140 of the object at $AA,
 * some 30-90 pixels past the native right edge; the draw test then shows them
 * only on reaching it. The obstacles stand still in the world, so running the script ahead by
 * the view's right margin and placing each one that much further right
 * leaves every obstacle where and when the game puts it, but created beyond
 * the wider view. All three hook points leave alone what they change ($0A40,
 * $88): an LDA of $0A56, a PLA, an LDY. This changes the game. */
int TlkWideRideScriptLead(void) { return s_ride_lead; }
static void RideScript(CpuState *cpu, int stage) {
    if(stage==0 || stage==1)s_ride_cursor=rd24(g_ram+0xba);
    uint8_t *dist = &g_ram[0x0A40];
    if (stage == 0) {
        if (s_spawn_lead <= 0 || s_ride_lead || cpu->DB != 0x7E || !(g_ram[0x0A56] | g_ram[0x0A57])) return;
        int ml, mr;
        LiveMargins(s_spawn_lead, &ml, &mr);
        s_ride_lead = (mr + 15) & ~15;   /* the script places on 16-pixel steps */
    } else if (stage == 2) {
        if (s_ride_lead) {
            unsigned x = (unsigned)(g_ram[(cpu->D + 0x88) & 0xFFFF] | g_ram[(cpu->D + 0x89) & 0xFFFF] << 8) + (unsigned)s_ride_lead;
            g_ram[(cpu->D + 0x88) & 0xFFFF] = (uint8_t)x;
            g_ram[(cpu->D + 0x89) & 0xFFFF] = (uint8_t)(x >> 8);
        }
        return;
    }
    if (!s_ride_lead) return;
    unsigned v = (unsigned)(dist[0] | dist[1] << 8) + (unsigned)(stage == 0 ? s_ride_lead : -s_ride_lead);
    dist[0] = (uint8_t)v;
    dist[1] = (uint8_t)(v >> 8);
    if (stage == 1) s_ride_lead = 0;
}

/* Switching from the finite ride camera to a free window can reveal columns
 * on the right while the camera itself moves left. The incremental scanner
 * only visits the entering left strip, so it misses the exit platform. Reuse
 * the original full column scanner once at this viewport handoff. */
static int s_ride_rescan_pending;

static void RideScanPush(CpuState *cpu,unsigned value){g_ram[cpu->S--]=(uint8_t)value;}
static void RideScanPut(unsigned a,unsigned value){g_ram[a]=(uint8_t)value;g_ram[a+1]=(uint8_t)(value>>8);}
/* Incremental streaming visits entering strips, not a resized/reframed view's
 * entire rectangle. A registered marker can consequently remain queued even
 * inside the current picture. Let the original dual-index scanner and original
 * constructors consume that queue; never fabricate an actor or pickup flag.
 * B742 is the ordinary stream cleanup, distinct from the ride's B69F exit.
 * Both execution modes forward this original stream through TlkRunOriginal. */
static void WideQueuedRescan(CpuState *cpu,unsigned pc) {
    unsigned level=rd16(g_ram+0x1ff9e);
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_QUEUED_RESCAN_TRACE");if(path)trace=fopen(path,"w");}
    if(trace && pc==0xb742){fprintf(trace,"%d,%04x,%u,%u,%u,%u,%u,%u,%04x,%d,%d,%06x\n",snes_frame_counter,cpu->S,level,cpu->D,cpu->DB,cpu->m_flag,cpu->x_flag,rd16(g_ram+0xa89),rd16(g_ram+0x68),s_spawn_lead,s_spawn_height,rd24(g_ram+0xb243));fflush(trace);}
    /* Constructors leave $68 pointing at the newly created actor. Only the
     * entry requires the camera owner; an already committed column scan must
     * retain its original scan type through every constructor and saved yield.
     * Its guest-stack return is the continuation's ownership, not mutable $68. */
    if(!cpu->D && cpu->DB==0x7e && !cpu->m_flag && cpu->x_flag &&
       cpu->S>=32 && cpu->S<=0x1fe0) {
        if(pc==0xb97b && rd16(g_ram+cpu->S+1)==0xb8d6 && rd16(g_ram+cpu->S+9)==0xb741) {
            interp_bridge_pre_opcode_redirect(0xc0ba3f);return;
        }
        if(pc==0xb8c6 && rd16(g_ram+cpu->S+3)==0xb741) {
            unsigned left=rd16(g_ram+0x46),right=rd16(g_ram+0x14),row=rd16(g_ram+0x48),bottom=rd16(g_ram+0x16);
            unsigned columns=rd16(g_ram+0x52),rows=rd16(g_ram+0x54),top=row>12?row-12:0;
            if(left>right || right>=rd16(g_ram+0xd0) || row>bottom || bottom>=rd16(g_ram+0xd4)*2 ||
               columns!=0xe4c1 || rows!=columns+rd16(g_ram+0xd0))return;
            RideScanPut(0x46,top);RideScanPut(0x14,bottom);RideScanPut(0x48,left);RideScanPut(0x16,right-left);
            RideScanPut(0x52,rows);RideScanPut(0x54,columns);return;
        }
    }
    if(!s_enabled || s_spawn_lead<=0 || level>=10 || level==3 ||
       (s_spawn_height<=224 && 256+2*s_spawn_lead<=TlkResourcesViewportForScene(level)) ||
       (level==1 && rd16(g_ram+0xa56)) || rd24(g_ram+0xdf)!=0xc00387+level*50 ||
       rd24(g_ram+0xb217)!=0xc5858a || rd24(g_ram+0xb243)<0xc30000 ||
       rd24(g_ram+0xb243)>=0xc40000 || !rd16(g_ram+0x2004) || rd16(g_ram+0x2004)>99 ||
       rd16(g_ram+0xa6c2) || rd16(g_ram+0xa6ba) ||
       rd16(g_ram+0xa89) || cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag ||
       rd16(g_ram+0x68)!=0xb293 || cpu->S<32 || cpu->S>0x1fe0)return;
    if(pc==0xb742) {
        static int last=-1;extern int snes_frame_counter;
        if(last==snes_frame_counter)return;
        last=snes_frame_counter;
        unsigned rowb=rd16(g_ram+0xd0),rows=rd16(g_ram+0xd4);
        if(!rowb || rowb>1024 || !rows || rows>512 || 0xe4c1+rowb+rows*2>0xffff)return;
        int top,bottom;VerticalMargins(&top,&bottom);
        int cx=rd16(g_ram+0xb29b),cy=rd16(g_ram+0xb29d)+1;
        int left,right;LiveMargins(s_spawn_lead,&left,&right);
        int x0=cx-left,x1=cx+256+right,y0=cy-top,y1=cy+224+bottom;
        int first=y0>0?y0/16:0,last_row=(y1-1)/16;if(last_row>=(int)rows)last_row=rows-1;
        bool pending=false;
        for(int y=first;y<=last_row && !pending;y++) {
            unsigned node=rd16(g_ram+0xe4c1+rowb+y*2);
            for(unsigned n=0;n<256 && node>=0xe4c1+rowb+rows*2 && node<=0xfff9;n++) {
                int x=(int)rd16(g_ram+node+4)*8;
                if(x>=x1)break;
                if(x>=x0 && rd16(g_ram+node+2)>0 && rd16(g_ram+node+2)<256){pending=true;break;}
                unsigned next=rd16(g_ram+node);if(next==node)break;node=next;
            }
        }
        if(!pending)return;
        RideScanPush(cpu,0xb7);RideScanPush(cpu,0x41);
        cpu->host_return_valid=2;interp_bridge_pre_opcode_redirect(0xc0b8b9);
    }
}
static void RideRescan(CpuState *cpu,unsigned pc) {
    if(rd16(g_ram+0x1ff9e)!=1 || rd24(g_ram+0xdf)!=0xc003b9 || cpu->D || cpu->DB!=0x7e)return;
    if(pc==0xb62d){
        s_ride_rescan_pending=s_spawn_lead>0 && 256+2*s_spawn_lead>TlkResourcesViewportForScene(1);
    }else if(pc==0xb69f){
        if(!s_ride_rescan_pending || rd16(g_ram+0xa56) || cpu->m_flag || !cpu->x_flag || rd16(g_ram+0x68)!=0xb293)return;
        s_ride_rescan_pending=0;
        RideScanPush(cpu,0xb6);RideScanPush(cpu,0x9e);
        cpu->host_return_valid=2;interp_bridge_pre_opcode_redirect(0xc0b8b9);
    }else if(pc==0xb8c6){
        if(rd16(g_ram+cpu->S+3)!=0xb69e || rd16(g_ram+0x68)!=0xb293)return;
        unsigned left=rd16(g_ram+0x46),right=rd16(g_ram+0x14),row=rd16(g_ram+0x48),bottom=rd16(g_ram+0x16);
        unsigned columns=rd16(g_ram+0x52),rows=rd16(g_ram+0x54),top=row>12?row-12:0;
        if(left>right || right>=rd16(g_ram+0xd0) || row>bottom || bottom>=rd16(g_ram+0xd4)*2 || columns!=0xe4c1 || rows!=columns+rd16(g_ram+0xd0))return;
        RideScanPut(0x46,top);RideScanPut(0x14,bottom);RideScanPut(0x48,left);RideScanPut(0x16,right-left);
        RideScanPut(0x52,rows);RideScanPut(0x54,columns);
        static FILE *f;static int opened;if(!opened){opened=1;const char *path=getenv("TLK_RIDE_RESCAN_TRACE");if(path){f=fopen(path,"w");if(f)fputs("field,left,right,top,bottom\n",f);}}
        if(f){extern int snes_frame_counter;fprintf(f,"%d,%u,%u,%u,%u\n",snes_frame_counter+1,left,right,top,bottom);fflush(f);}
    }else if(pc==0xb97b && rd16(g_ram+cpu->S+1)==0xb8d6 && rd16(g_ram+cpu->S+9)==0xb69e){
        interp_bridge_pre_opcode_redirect(0xc0ba3f);
    }
}
static void RecordWideSpriteBudgetIntent(const CpuState *cpu);
static int ContactSearchExpanded(void) {
    return s_enabled && s_spawn_lead>0 && (s_spawn_height>224 ||
        256+2*s_spawn_lead>TlkResourcesViewportForScene(rd16(g_ram+0x1ff9e)));
}
unsigned TlkContactSearchTailStep(CpuState *cpu,unsigned pc) {
    if(!ContactSearchExpanded() || cpu->PB!=0xc5 || cpu->DB!=0x7e ||
       cpu->m_flag || cpu->x_flag || cpu->D<0x600 || cpu->D>0x9d8 ||
       cpu->S<32 || cpu->S>0x1ff0)return 0;
    unsigned node=rd16(g_ram+cpu->S+1);
    if(node && (node<0xb213 || node>=0xdc13 || ((node-0xb213)&127)))return 0;
    /* Both recursive C54CF2 branches are tail calls. Their only subsequent
     * store is an unread local +0C, followed by the common frame epilogue.
     * Consume the just-pushed next-node argument and reuse the current 40-byte
     * frame. C54D0D overwrites every local needed for the next comparison;
     * the caller's original argument/return/PHD/PHP stay on the guest stack.
     * This keeps list order and C0CE9B queries, without growing the original
     * $0600..$09FF arena into game controls at $0A00. */
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_CONTACT_SEARCH_TRACE");if(path)trace=fopen(path,"w");}
    if(trace){fprintf(trace,"%d,%06x,%04x,%04x,%04x\n",snes_frame_counter,pc,cpu->D,cpu->S,node);fflush(trace);}
    cpu->S+=2;cpu->A=node;cpu->_flag_N=!!(node&0x8000);cpu->_flag_Z=!node;cpu_mirrors_to_p(cpu);
    return node?0xc54d0d:0xc54d05;
}
static void Observe(CpuState *cpu, uint32_t pc24) {
    switch (pc24 & 0x3FFFFF) {
    case 0x054d52:case 0x054d8c:{unsigned target=TlkContactSearchTailStep(cpu,pc24);if(target)interp_bridge_pre_opcode_redirect(target);return;}
    case 0x048efc:case 0x048f0c:case 0x048f41:case 0x048f4f:WaterfallLogViewport(cpu,pc24&65535);return;
    case 0x00b62d:case 0x00b8c6:case 0x00b97b:RideRescan(cpu,pc24&65535);WideQueuedRescan(cpu,pc24&65535);return;
    case 0x00b742:WideQueuedRescan(cpu,pc24&65535);return;
    case kPcSpawnWindow: WidenSpawn(cpu); return;
    case 0x00b927: case 0x00b932: case 0x00a5e3: WidenVertical(cpu,pc24&65535);return;
    case 0x00a5ed:WidenVertical(cpu,pc24&65535);RecordBonusPickupIntent(cpu);return;
    case 0x00a6a4:RecordWideSpriteBudgetIntent(cpu);return;
    case kPcCullRight: WidenCull(cpu, true); return;
    case kPcCullLeft: WidenCull(cpu, false); return;
    case kPcRideScript: RideScript(cpu, 0); return;
    case kPcRideScriptEnd: RideScript(cpu, 1);RideRescan(cpu,pc24&65535);return;
    case kPcRideSpawnX: RideScript(cpu, 2); return;
    }
    if (!s_enabled) return;
    switch (pc24 & 0x3FFFFF) {
    case kPcPiece16: RecordPiece(cpu, true); break;
    case kPcPiece8: RecordPiece(cpu, false); break;
    case kPcOamDma:
        /* A busy guest frame can reupload the displayed OAM without running
         * its draw pass. Keep the provenance of those same visible sprites:
         * an empty replacement list would put the HUD back in native columns
         * and lose selected artwork for one field. A changed/cleared upload
         * must still discard the old list. Hardware OAM already survives saves. */
        if(!s_build_count && s_latched_count && g_ppu) {
            bool same=true;
            for(unsigned n=0;n<256 && same;n++)
                same=rd16(g_ram+0x300+n*2)==g_ppu->oam[n];
            if(same && !memcmp(g_ram+0x500,g_ppu->highOam,32))break;
        }
        s_latch_serial++;
        memcpy(s_latched, s_build, s_build_count * sizeof *s_build);
        s_latched_count = s_build_count;
        s_build_count = 0;
        ObjLog();
        /* A screen-fixed object goes towards the edge it sits nearer, by
         * HudSide of its centre: the HUD boxes all the way, a title or text
         * across the middle not at all. */
        for (unsigned i = 0, j; i < s_latched_count; i = j) {
            int lo = 1 << 15, hi = -(1 << 15);
            for (j = i; j < s_latched_count && s_latched[j].obj == s_latched[i].obj &&
                        s_latched[j].fixed == s_latched[i].fixed; j++)
                if (s_latched[j].kept) {
                    if (s_latched[j].x < lo) lo = s_latched[j].x;
                    if (s_latched[j].x + s_latched[j].size > hi) hi = s_latched[j].x + s_latched[j].size;
                }
            int8_t side = !s_latched[i].fixed || lo > hi ? 0 : HudSide((lo + hi) / 2);
            for (unsigned k = i; k < j; k++) s_latched[k].side = side;
        }
        break;
    }
}

static void ArmInterpreterHooks(void) {
    static const uint32_t pcs[] = { 0xC0A727, 0x00A727, 0xC0A7AE, 0x00A7AE, 0xC0A033, 0x00A033,
                                    0xC54D52,0xC54D8C,
                                    0xC48EFC,0xC48F0C,0xC48F41,0xC48F4F,
                                    0xC0B927,0x00B927,0xC0B932,0x00B932,0xC0A5E3,0x00A5E3,0xC0A5ED,0x00A5ED,0xC0A6A4,0x00A6A4,
                                    0xC0B62D,0x00B62D,0xC0B8C6,0x00B8C6,0xC0B97B,0x00B97B,0xC0B915, 0x00B915, 0xC0A5C2, 0x00A5C2, 0xC0A5CF, 0x00A5CF,
                                    0xC0B618, 0x00B618, 0xC0B69F, 0x00B69F, 0xC0B742,0x00B742,0xC0BB98, 0x00BB98 };
    for (size_t i = 0; i < sizeof pcs / sizeof pcs[0]; i++) interp_bridge_add_pre_opcode_hook(pcs[i], Observe);
}

/* ── Line capture ──────────────────────────────────────────────────────── */

static void CaptureLine(const Ppu *p, unsigned line, void *context) {
    (void)context;
    if (line < 1 || line > TLK_WIDE_HEIGHT) return;
    if (line == 1) {
        s_frame.captured = 0;
        s_frame.valid = false;
        memcpy(s_frame.ram, g_ram, sizeof s_frame.ram);
        memcpy(s_frame.pieces, s_latched, s_latched_count * sizeof *s_latched);
        s_frame.piece_count = s_latched_count;
        s_frame.latch_serial=s_latch_serial;
        s_frame.hud_end = s_latched_count && s_latched[0].slot <= kHudSlotsMax ? s_latched[0].slot : 0;
        /* VRAM changes rarely: keep the first copy while its write count holds. */
        s_vram_used = 1;
        s_vram_cur = 0;
        if (!s_vram_have || s_vram_count[0] != p->vramWriteCount) {
            memcpy(s_vram[0], p->vram, sizeof s_vram[0]);
            s_vram_count[0] = p->vramWriteCount;
            s_vram_have = true;
        }
    } else if (s_vram_count[s_vram_cur] != p->vramWriteCount) {
        if (s_vram_used < kVramCopies) s_vram_cur = s_vram_used++;
        memcpy(s_vram[s_vram_cur], p->vram, sizeof s_vram[0]);
        s_vram_count[s_vram_cur] = p->vramWriteCount;
        if (s_vram_cur == 0) s_vram_have = false;
    }
    if ((int)line != s_frame.captured + 1) return;
    Line *l = &s_frame.lines[line - 1];
    l->inidisp = p->inidisp; l->obsel = p->obsel; l->bgmode = p->bgmode; l->mosaic = p->mosaic;
    l->setini = p->setini; l->oamaddl = p->oamaddl; l->oamaddh = p->oamaddh;
    memcpy(l->bgsc, p->bgXsc, 4);
    l->bgchr = p->bgTileAdr;
    memcpy(l->hofs, p->hScroll, sizeof l->hofs);
    memcpy(l->vofs, p->vScroll, sizeof l->vofs);
    l->fixed = p->fixedColor;
    l->windowsel = p->windowsel;
    l->w1l = p->window1left; l->w1r = p->window1right; l->w2l = p->window2left; l->w2r = p->window2right;
    l->wlog = p->wbgobjlog;
    l->tm = p->screenEnabled[0]; l->ts = p->screenEnabled[1];
    l->tmw = p->screenWindowed[0]; l->tsw = p->screenWindowed[1];
    l->cgadsub = p->cgadsub; l->cgwsel = p->cgwsel;
    l->vram = (uint8_t)s_vram_cur;
    memcpy(l->cgram, p->cgram, sizeof l->cgram);
    memcpy(l->oam, p->oam, sizeof l->oam);
    memcpy(l->hoam, p->highOam, sizeof l->hoam);
    s_frame.captured = (int)line;
}

/* ── Level map ─────────────────────────────────────────────────────────── */

/* Exile reuses7F0000 for the DEAE73 sprite bank while the final native
 * tilemap is still displayed. That memory is no longer a terrain source.
 * Reconstruct only the exact identified overwritten bytes for presentation;
 * preserve the remaining live map and all guest state. */
static const uint8_t *ExileMapView(const uint8_t *ram,unsigned rec,unsigned bytes) {
    static uint8_t initial[0x10000],scratch[0x10000],view[0x10000];
    static unsigned owner;static size_t scratch_bytes;
    if(rd16(ram+0x1ff9e)!=4 || rd24(ram+0xdf)!=0xc0044f ||
       !bytes || bytes>sizeof view)return ram+0x10000;
    if(owner!=rec) {
        size_t count=0;owner=0;scratch_bytes=0;
        if(!TlkMdDecompress(s_rom,s_rom_size,rd24(s_rom+rec+9)&0x3fffff,
            initial,sizeof initial,&count) || count!=bytes ||
           !TlkMdDecompress(s_rom,s_rom_size,0x1eae73,scratch,sizeof scratch,&scratch_bytes) ||
           !scratch_bytes || scratch_bytes>bytes)return ram+0x10000;
        owner=rec;
    }
    if(memcmp(ram+0x10000,scratch,scratch_bytes))return ram+0x10000;
    memcpy(view,initial,scratch_bytes);
    memcpy(view+scratch_bytes,ram+0x10000+scratch_bytes,bytes-scratch_bytes);
    return view;
}
static bool LevelOf(const uint8_t *ram, Level *lv) {
    unsigned n = rd16(ram + 0x1FF9E);   /* $7FFF9E current level */
    if (!s_rom || n >= 16 || 0x357 + n * 3 + 3 > s_rom_size) return false;
    uint32_t rec = rd24(s_rom + 0x357 + n * 3) & 0x3FFFFF;
    if (rec + 0x32 > s_rom_size) return false;
    lv->rowb = rd16(s_rom + rec + 0x12);
    lv->rows = rd16(s_rom + rec + 0x14);
    lv->blk = rd24(s_rom + rec + 0x0F) & 0x3FFFFF;
    lv->map = ram + 0x10000;
    if(n==4 && lv->rowb && lv->rows && lv->rowb*lv->rows<=0x10000)
        lv->map=ExileMapView(ram,rec,lv->rowb*lv->rows);
    return lv->rowb && !(lv->rowb & 1) && lv->rows && lv->rowb * lv->rows <= 0x10000 && lv->blk < s_rom_size;
}

static void KeepOutgoingHuntLimits(void);
static void DisplaySceneContext(void) {
    /* Hunt assigns the next main-level number before its visible fade. The
     * descriptor and raster still belong to the outgoing world. Keep that
     * world's map/resources together in this presentation snapshot only. */
    unsigned descriptor=rd24(s_frame.ram+0xdf),guest=rd16(s_frame.ram+0x1ff9e),display=guest;
    /* The loader clears its descriptor before blanking the outgoing Hunt
     * raster. The preceding display level is already saved with background
     * history. Keep its descriptor/map/source together through this gap;
     * the next nonzero descriptor ends the bridge. Never alter guest RAM. */
    if(!descriptor && guest<10 && s_bg_level>=11 && s_bg_level<=13 &&
       s_rom && s_rom_size>=0x381) {
        descriptor=rd24(s_rom+0x357+(unsigned)s_bg_level*3);
        s_frame.ram[0xdf]=(uint8_t)descriptor;
        s_frame.ram[0xe0]=(uint8_t)(descriptor>>8);
        s_frame.ram[0xe1]=(uint8_t)(descriptor>>16);
        display=(unsigned)s_bg_level;
        KeepOutgoingHuntLimits();
    }
    if(s_rom && s_rom_size>=0x381 && (descriptor>>16)==0xc0)
        for(unsigned n=0;n<14;n++)if(rd24(s_rom+0x357+n*3)==descriptor){display=n;break;}
    if(display==guest)return;
    s_frame.ram[0x1ff9e]=(uint8_t)display;s_frame.ram[0x1ff9f]=(uint8_t)(display>>8);
    static FILE *trace;static int initialized;
    if(!initialized){initialized=1;const char *path=getenv("TLK_DISPLAY_SCENE_TRACE");
        if(path)trace=fopen(path,"w");if(trace)fputs("field,guest_level,display_level,descriptor\n",trace);}
    if(trace){fprintf(trace,"%u,%u,%u,%06x\n",snes_frame_counter,guest,display,descriptor);fflush(trace);}
}

static int Reflect(int v, int n) {
    if (v < 0) v = -v - 1;
    if (v >= n) v = 2 * n - 1 - v;
    return v < 0 ? 0 : v >= n ? n - 1 : v;
}

/* Periodic mirror, including windows wider than two copies or scrolled
 * past their first join. Reflect() below intentionally clamps map edges. */
static int s_panorama_phase,s_panorama_phase_level=-1;
/* The PPU exposes only the nine-bit scroll of this512-wide plane. The added
 * mirrored pair is1024 wide: dropping bit9 at an original plane wrap would
 * reflect the entire picture at once. Unwrap completed raster scroll first. */
static int PanoramaScroll(const Line *l) {
    int raw=l->hofs[1]&511;
    int phase=s_panorama_phase_level==(int)s_md_level?
        s_panorama_phase+((raw-(s_panorama_phase&511)+256)&511)-256:raw;
    if(s_md_level==1 && s_handoff_width>320)
        phase+=s_ride_handoff.background_shift*RideHandoffWeight()/512;
    return phase;
}
static unsigned PanoramaX(int x) {unsigned u=(unsigned)x&1023;return u<512?u:1023-u;}

/* The BG1 tilemap word at world pixel (*wx, *wy). Past the level's edges the
 * map is reflected, and *wx/*wy become the reflected position. */
static bool MapTile(const Level *lv, int *wx, int *wy, uint16_t *word) {
    *wx = Reflect(*wx, (int)lv->rowb * 8);
    *wy = Reflect(*wy, (int)lv->rows * 16);
    unsigned cell = rd16(lv->map + (*wy >> 4) * lv->rowb + (*wx >> 4) * 2) & 0xFFF8;
    uint32_t a = lv->blk + cell + (((*wx >> 3) & 1) | ((*wy >> 3) & 1) << 1) * 2;
    if (a + 2 > s_rom_size) return false;
    *word = (uint16_t)rd16(s_rom + a);
    return true;
}

/* World position nearest the camera with this scroll phase. */
static int Expand(int camera, unsigned scroll, int period) {
    int d = (int)((scroll - (unsigned)camera) & (unsigned)(period - 1));
    if (d >= period / 2) d -= period;
    return camera + d;
}

static uint16_t VramTilemap(const uint16_t *vram, unsigned sc, unsigned px, unsigned py, unsigned size) {
    unsigned tx = px / size, ty = py / size;
    unsigned a = (sc & 0xFC) << 8;
    a += (tx & 31) + (ty & 31) * 32;
    if ((sc & 1) && (tx & 32)) a += 0x400;
    if ((sc & 2) && (ty & 32)) a += (sc & 1) ? 0x800 : 0x400;
    return vram[a & 0x7FFF];
}

/* BG1's world origin on a line: world x of column 0, world y of the line. */
static void Bg1Origin(const Line *l, int y0, int *wx, int *wy) {
    *wx = Expand(s_ride_raster_anchor>=0?s_ride_raster_anchor:rd16(s_frame.ram + 0xB29B), l->hofs[0] & 0x1FF, 512);
    *wy = Expand((int)rd16(s_frame.ram + 0xB29D) + y0 + 1, (l->vofs[0] + (unsigned)y0 + 1) & 0xFF, 256);
}

static bool LineHasStage(const Line *l) {
    return (l->bgmode & 7) == 1 && !(l->bgmode & 0x10) && !(l->mosaic & 0xF0 && l->mosaic & 7) &&
           !(l->setini & 0x0B) && l->bgsc[0] == s_frame.stage_sc && l->bgchr == s_frame.stage_chr;
}

/* How many sampled cells of the native BG1 tilemap agree with s_frame.level's
 * map (*same of *total). */
/* Both original worlds stream the first512 strip only after the camera
 * actually wraps. Loop-base initialization alone still shows the giraffe. */
static int RideViewportWidth(void) {
    /* This is also queried for each foreground pixel. Cache only the stable
     * catalogue index; resolve the current source so profile changes stay live. */
    return TlkResourcesHasMd() && TlkResourcesUseMd("gameplay.camera")?320:256;
}
static int s_ride_exit_shift=-1,s_ride_map_viewport=256;
static int RideExitShift(void) {
    unsigned loop=rd16(s_frame.ram+0xa56),cursor=rd24(s_frame.ram+0xba);
    if(!loop || rd16(s_frame.ram+0x1ff9e)!=1 || rd24(s_frame.ram+0xdf)!=0xc003b9)return -1;
    int md=TlkResourcesUseMd("gameplay.levels.cant_wait.ostrich_obstacles");
    for(unsigned i=0;i<32 && cursor>=0xc4e1b9 && cursor<0xc4e23d;i++,cursor+=4){
        unsigned distance=rd16(s_rom+(cursor&0x3fffff)),flags=rd16(s_rom+(cursor&0x3fffff)+2);
        if(md && !TlkCantWaitRideEvent(cursor,&distance,&flags))return -1;
        if(flags&0x8000){
            int remaining=(int)distance-(int)rd16(s_frame.ram+0xa40);
            int end=(int)rd16(s_frame.ram+0xb29b)+remaining-(int)loop;
            return remaining>=0 && end>=0?(end/512)*512:-1;
        }
    }
    return -1;
}
static int RideMapSourceX(int wx,int wy) {
    unsigned loop=rd16(s_frame.ram+0xa56);
    int local_camera=(int)rd16(s_frame.ram+0xb29b)-(int)loop;
    /* The finite exit is ahead of the repeating road, even before its last
     * camera wrap. Project authored exit terrain by the remaining ring count
     * so the giraffe body approaches continuously instead of appearing when
     * A56 clears. Original terrain/collision queries remain unchanged. */
    if(loop && s_ride_exit_shift>=0 && wx-s_ride_exit_shift>=(int)loop+512)
        return wx-s_ride_exit_shift;
    /* A58 is cumulative across both rides. A40 restarts at each entrance;
     * once it exceeds the local ring camera offset, this ride has wrapped.
     * The last road row belongs to the same current ride: cumulative A58
     * can already be nonzero at the second entrance before any local wrap. */
    bool wrapped=local_camera>=0 && rd16(s_frame.ram+0xa40)>(unsigned)local_camera;
    if(rd16(s_frame.ram+0x1ff9e)==1 && rd24(s_frame.ram+0xdf)==0xc003b9 &&
       loop && wrapped &&
       wx<(int)loop+s_ride_map_viewport)wx+=512;
    /* The running road is an authored512-pixel ring. Extra presentation
     * columns repeat that ring, without advancing the original parser/camera. */
    if(loop && ((wrapped && wx<(int)loop+s_ride_map_viewport) || wx>=(int)loop+s_ride_map_viewport+512)) {
        int base=(int)loop+s_ride_map_viewport,local=(wx-base)%512;if(local<0)local+=512;wx=base+local;
    }
    return wx;
}
static void MapScore(unsigned *same_out, unsigned *total_out) {
    unsigned total = 0, same = 0;
    *same_out = *total_out = 0;
    for (int y0 = 8; y0 < TLK_WIDE_HEIGHT; y0 += 32) {
        const Line *l = &s_frame.lines[y0];
        if (!LineHasStage(l) || (l->inidisp & 0x80)) continue;
        int ox, oy;
        Bg1Origin(l, y0, &ox, &oy);
        for (int x = 16; x < 248; x += 32) {
            int expected_x=RideMapSourceX(ox+x,oy),wx=expected_x,wy=oy;
            uint16_t word;
            if (!MapTile(&s_frame.level, &wx, &wy, &word)) return;
            if (wx != expected_x || wy != oy) continue;   /* only inside the level */
            total++;
            same += VramTilemap(s_vram[l->vram], l->bgsc[0], (unsigned)(l->hofs[0] + x) & 1023,
                                (unsigned)(l->vofs[0] + y0 + 1) & 1023, 8) == word;
        }
    }
    *same_out = same;
    *total_out = total;
}

/* A level frame when most of it agrees. Not all of it: after the ostrich
 * ride's warp some cells differ for a while (the margins then follow
 * SeamAgrees); a title or menu agrees nowhere. */
static bool Agrees(unsigned same, unsigned total) { return total >= 20 && same * 2 >= total; }

static Level s_last_level;   /* the last level whose map agreed everywhere, map copied to s_last_map */
static uint8_t s_last_map[0x10000];
static uint8_t s_last_limits[4];   /* its camera limits, $A6EC and $D8 */
static bool s_have_last;
static void KeepOutgoingHuntLimits(void) {
    if(!s_have_last)return;
    memcpy(s_frame.ram+0xa6ec,s_last_limits,2);
    memcpy(s_frame.ram+0xd8,s_last_limits+2,2);
}

/* A level frame when a map agrees. The map in RAM can stop describing the
 * screen while the level is still shown: a level's closing scene overwrites
 * it (levels 4 and 6), and a Bug Hunt changes the level number about 14
 * frames before its fade (and zeroes the camera's right limit 2 frames
 * before). Then a copy of the last map that agreed everywhere is tried, and
 * the one that agrees more is used, with the camera limits it had. */
static bool StageMap(void) {
    /* Line 112, or the first line shown when the game has turned the screen
     * off below the top (a Bug Hunt's last frame: dark from line 30). */
    const Line *mid = &s_frame.lines[112];
    for (int y = 0; y < TLK_WIDE_HEIGHT && ((mid->inidisp & 0x80) || !(mid->inidisp & 15)); y++) mid = &s_frame.lines[y];
    if ((mid->bgmode & 7) != 1 || (mid->bgmode & 0x10) || !(mid->tm & 1)) return false;
    s_frame.stage_sc = mid->bgsc[0];
    s_frame.stage_chr = mid->bgchr;
    unsigned same = 0, total = 0, kept_same = 0, kept_total = 0;
    Level live;
    bool have_live = LevelOf(s_frame.ram, &live);
    if (have_live) {
        s_frame.level = live;
        MapScore(&same, &total);
        if (total >= 20 && same == total) {
            s_last_level = live;
            memcpy(s_last_map, live.map, live.rowb * live.rows);
            s_last_level.map = s_last_map;
            memcpy(s_last_limits, s_frame.ram + 0xA6EC, 2);
            memcpy(s_last_limits + 2, s_frame.ram + 0xD8, 2);
            return s_have_last = true;
        }
    }
    if (s_have_last) {
        s_frame.level = s_last_level;
        MapScore(&kept_same, &kept_total);
        /* Inside the run a few lines that all agree will do (that last frame
         * leaves one sampled line, 8 cells). */
        bool kept_ok = Agrees(kept_same, kept_total) || (kept_total >= 8 && kept_same == kept_total);
        if (kept_ok && (!have_live || !Agrees(same, total) || kept_same * total > same * kept_total)) {
            memcpy(s_frame.ram + 0xA6EC, s_last_limits, 2);
            memcpy(s_frame.ram + 0xD8, s_last_limits + 2, 2);
            return true;
        }
    }
    s_frame.level = live;
    /* King switches its source ring before the newly streamed names agree.
     * The initialized King map and displayed layer registers still own this
     * field; disagreement here must not collapse a free window to224 lines. */
    if(have_live && rd16(s_frame.ram+0x1ff9e)==1 &&
       rd24(s_frame.ram+0xdf)==0xc003b9 && rd16(s_frame.ram+0xa56) &&
       live.rowb==800 && live.rows==31 && rd16(s_frame.ram+0x2004)>0)
        return true;
    return have_live && Agrees(same, total);
}

/* The copy only bridges an unbroken run of level frames: after a frame that
 * is not one (a fade to black, a title) it could match a mostly blank
 * tilemap, as the title screen's after the attract demo. */
static bool DetectStage(void) {
    if (StageMap()) return true;
    s_have_last = false;
    return false;
}

/* ── Compositor ────────────────────────────────────────────────────────── */

static unsigned TilePixel(const uint16_t *vram, unsigned address, unsigned x, unsigned y, unsigned bpp) {
    unsigned a = (address + y) & 0x7FFF, shift = 7 - x;
    unsigned bits = vram[a] >> shift;
    unsigned pixel = (bits & 1) | ((bits >> 7) & 2);
    if (bpp == 4) {
        bits = vram[(a + 8) & 0x7FFF] >> shift;
        pixel |= ((bits & 1) << 2) | ((bits >> 5) & 8);
    }
    return pixel;
}

static void PreparePanorama(const Line *l,unsigned level) {
    if(level>=14 || !s_native_panorama_height[level])return;
    unsigned v=l->vram,base=((l->bgchr>>4)&15)<<12,key=level+1;
    if(s_panorama_checked[v]==s_panorama_epoch)return;
    s_panorama_checked[v]=s_panorama_epoch;
    int equal=s_panorama_owner[v]==key && s_panorama_base[v]==base;
    for(unsigned i=0;i<0x4000 && equal;i++)if(s_panorama_tiles[v][i]!=s_vram[v][(base+i)&0x7fff])equal=0;
    if(equal)return;
    for(unsigned i=0;i<0x4000;i++)s_panorama_tiles[v][i]=s_vram[v][(base+i)&0x7fff];
    s_panorama_owner[v]=key;s_panorama_base[v]=base;
    for(unsigned y=0;y<s_native_panorama_height[level];y++)for(unsigned x=0;x<512;x++){
        unsigned tile=rd16(s_native_panorama[level]+(y/8*64+x/8)*2),cx=x&7,cy=y&7;
        if(tile&0x4000)cx=7-cx;if(tile&0x8000)cy=7-cy;
        unsigned pixel=TilePixel(s_vram[v],base+(tile&1023)*16,cx,cy,4);
        s_panorama_pixels[v][y*512+x]=pixel?(uint16_t)(((tile&0x2000?11:7)<<12)|0x100|((tile>>10&7)*16+pixel)):0;
    }
}

/* Expanded native scenery has no per-pixel blend in these normal rows.
 * Resolve its selected palette once, preserving the existing scene-color hook. */

/* Original MD scroll callbacks applied to the native BG2 artwork only.
 * Each source keeps its own name table, vertical scroll and priority. */
static int s_native_background_motion,s_native_firelight;
static int SceneryFloor(int n,unsigned shift){return n>=0?n/(1<<shift):-((-n+(1<<shift)-1)/(1<<shift));}
static int NativeMotionOffset(unsigned level,int camera,int y){
 if(level==1)return (int)TlkMdCantWaitLineOffset((unsigned)camera,s_cant_wait.wrap,(unsigned)y);
 if(level==5){int row=s_bg_camera[1]*5/16+y;return row<8?0:SceneryFloor(camera,row<144?3:row<240?2:1);}
 if(level==8)return SceneryFloor(camera,y<112?3:y<151?2:1);
 if(level==9)return SceneryFloor(camera,y<96?1:y<184?2:1);
 return 0;
}
static unsigned SceneryCustomColor(unsigned layer,unsigned color){
 unsigned target=layer==0?0:layer==1||layer==5?1:2;
 if(target==2)s_sprite_colour_seen[(color&32767)>>5]|=1u<<(color&31);
 if(s_custom_palette_colours)color=TlkResourcesPaletteMap(s_md_level,target,(uint16_t)color);
 if(target || !s_native_firelight)return color;
 unsigned phase=s_scene_animation.phase;if(phase>=3)return color;
 static uint8_t tags[32768];static uint16_t cache[32768];
 if(tags[color]==phase+1)return cache[color];
 unsigned result=color,r=color&31,g=color>>5&31,b=color>>10&31;
 const uint16_t *base=TlkNextScenePrideRockPhase(2),*now=TlkNextScenePrideRockPhase(phase);
 if(base&&now&&r>g&&r>b){
  unsigned best=~0u,index=16;
  for(unsigned j=16;j<64;j++){int dr=(int)r-(base[j]&31),dg=(int)g-(base[j]>>5&31),db=(int)b-(base[j]>>10&31);unsigned d=dr*dr+dg*dg+db*db;if(d<best){best=d;index=j;}}
  result=0;for(unsigned sh=0;sh<=10;sh+=5){int v=(int)(color>>sh&31)+(int)(now[index]>>sh&31)-(int)(base[index]>>sh&31);if(v<0)v=0;if(v>31)v=31;result|=(unsigned)v<<sh;}
 }
 tags[color]=(uint8_t)(phase+1);cache[color]=(uint16_t)result;return result;
}
static struct {unsigned epoch,bright;uint16_t colors[128];uint32_t rgb[128];} s_bg_rgb[2];
static const uint32_t *NativeBackgroundRgb(unsigned slot,const uint16_t *colors,unsigned bright,
                                         const uint8_t *mult,int md_scene,int king) {
    if(s_bg_rgb[slot].epoch!=s_draw_choice_epoch || s_bg_rgb[slot].bright!=bright ||
       memcmp(s_bg_rgb[slot].colors,colors,128*sizeof *colors)){
        s_bg_rgb[slot].epoch=s_draw_choice_epoch;s_bg_rgb[slot].bright=bright;
        memcpy(s_bg_rgb[slot].colors,colors,128*sizeof *colors);
        for(unsigned i=0;i<128;i++){
            unsigned c=king?s_cw_native_mapped[slot][i]:md_scene?TlkMdSceneModeColor(i,0,colors[i],s_scenery_palette[slot]):colors[i];
            c=SceneryCustomColor(slot,c);
            s_bg_rgb[slot].rgb[i]=(uint32_t)mult[c&31]<<16|(uint32_t)mult[c>>5&31]<<8|mult[c>>10&31];
        }
    }
    return s_bg_rgb[slot].rgb;
}

/* Fixed-colour math depends on the palette entry and scanline registers,
 * not on the horizontal pixel. Keep it out of the expanded pixel loop while
 * preserving the scalar path's saturation, half-brightness and scene colours.
 * Subscreen blends and colour windows continue through the scalar compositor. */
static const uint32_t *NativeFixedBackgroundRgb(unsigned layer,const Line *l,unsigned bright,
                                               const uint8_t *mult,const uint8_t *half,int md_scene,int king) {
    static struct {unsigned epoch,key;uint16_t colors[128];uint32_t rgb[128];} cache[2];
    unsigned key=bright|((unsigned)l->fixed<<4)|((unsigned)l->cgadsub<<20)|((unsigned)(l->cgwsel&2)<<28);
    if(cache[layer].epoch!=s_draw_choice_epoch || cache[layer].key!=key ||
       memcmp(cache[layer].colors,l->cgram,sizeof cache[layer].colors)){
        cache[layer].epoch=s_draw_choice_epoch;cache[layer].key=key;
        memcpy(cache[layer].colors,l->cgram,sizeof cache[layer].colors);
        for(unsigned i=0;i<128;i++){
            unsigned c=king?s_cw_native_mapped[layer][i]:md_scene?TlkMdSceneModeColor(i,0,l->cgram[i],s_scenery_palette[layer]):l->cgram[i];
            c=SceneryCustomColor(layer,c);
            unsigned r=c&31,g=c>>5&31,b=c>>10&31;const uint8_t *map=mult;
            if(l->cgadsub&(1u<<layer)){
                unsigned r2=l->fixed&31,g2=l->fixed>>5&31,b2=l->fixed>>10&31;
                if((l->cgadsub&0x40) && !(l->cgwsel&2))map=half;
                if(l->cgadsub&0x80){r=r>=r2?r-r2:0;g=g>=g2?g-g2:0;b=b>=b2?b-b2:0;}
                else {r+=r2;g+=g2;b+=b2;}
            }
            cache[layer].rgb[i]=(uint32_t)map[r]<<16|(uint32_t)map[g]<<8|map[b];
        }
    }
    return cache[layer].rgb;
}
static uint32_t NativeFixedBackdropRgb(const Line *l,const uint8_t *mult,const uint8_t *half) {
    unsigned c=s_cw_scene && !s_cw_palette_mode?s_cw_native_mapped[1][0]:l->cgram[0];
    c=SceneryCustomColor(5,c);
    unsigned r=c&31,g=c>>5&31,b=c>>10&31;const uint8_t *map=mult;
    if(l->cgadsub&0x20){
        unsigned r2=l->fixed&31,g2=l->fixed>>5&31,b2=l->fixed>>10&31;
        if((l->cgadsub&0x40) && !(l->cgwsel&2))map=half;
        if(l->cgadsub&0x80){r=r>=r2?r-r2:0;g=g>=g2?g-g2:0;b=b>=b2?b-b2:0;}
        else {r+=r2;g+=g2;b+=b2;}
    }
    return (uint32_t)map[r]<<16|(uint32_t)map[g]<<8|map[b];
}

/* z<<12 | layer<<8 | CGRAM index, 0 for transparent. map: BG1 at x comes
 * from the level map (a margin column on a side where map and VRAM agree). */
static unsigned BottomBackgroundBandSize(void);
/* The selected native material word is constant throughout its8x8 source
 * cell. Tall views revisit that same correspondence on eight scanlines and
 * during margin inspection. Cache only within this draw's choice epoch:
 * original maps, material masks, animation state and source selection still
 * come from the existing sampler; the cache does not persist in save data. */
static int NativeLayoutTile(int x,int y,uint16_t *word) {
    enum { CAPACITY=32768 };
    static struct {unsigned epoch,level;int x,y;uint16_t word;uint8_t found;} cells[CAPACITY];
    static unsigned previous_epoch;
    if(x<0 || y<0 || !s_draw_choice_epoch)
        return TlkMdSceneNativeLayoutTile(s_md_level,x,y,s_rom,s_rom_size,word);
    if(previous_epoch>s_draw_choice_epoch)memset(cells,0,sizeof cells);
    previous_epoch=s_draw_choice_epoch;
    int tx=x/8,ty=y/8;
    unsigned slot=((unsigned)tx*73856093u^(unsigned)ty*19349663u^s_md_level*83492791u)&(CAPACITY-1);
    /* Bound probing too: an unusual raster must not turn a full cache into
     * a long stall. A miss simply calls the same selected source sampler. */
    for(unsigned n=0;n<64;n++,slot=(slot+1)&(CAPACITY-1)) {
        if(cells[slot].epoch!=s_draw_choice_epoch) {
            uint16_t value=0;
            int found=TlkMdSceneNativeLayoutTile(s_md_level,x,y,s_rom,s_rom_size,&value);
            cells[slot].epoch=s_draw_choice_epoch;cells[slot].level=s_md_level;
            cells[slot].x=tx;cells[slot].y=ty;cells[slot].word=value;cells[slot].found=found!=0;
            if(found)*word=value;return found;
        }
        if(cells[slot].level==s_md_level && cells[slot].x==tx && cells[slot].y==ty) {
            if(cells[slot].found)*word=cells[slot].word;
            return cells[slot].found;
        }
    }
    return TlkMdSceneNativeLayoutTile(s_md_level,x,y,s_rom,s_rom_size,word);
}
static uint16_t BgPixel(const Line *l, const uint16_t *vram, unsigned layer, int x, int y0, bool map,
                        int ox, int oy, int column, int width) {
    /* Native BG2's 28-row picture ends at source223. Raster223 samples224,
     * an unused black row: hide that exposed border at the extension join. */
    if(layer==1 && y0==223 && s_area_active && s_area_height>224 &&
       !s_md_background && BottomBackgroundBandSize())y0=222;
    if (layer==0 && s_md_foreground) {
        if(s_md_level==10 && BonusScene()){
            /* Toss normal Plane A: all1120 visible names equal the prepared
             * 320x224 map at E000, with zero scroll. Hunt uses different
             * foreground maps/cameras and does not share this recipe. */
            return TlkMdScenePixel(10,0,x+column+(320-width)/2,y0,0,0,0,0,0,0,0,width);
        }
        /* The ostrich ride streams the next512-pixel strip into Plane A's
         * ring below loop_base+viewport. Looking up the unwrapped world map
         * restores the earlier giraffes across the ride. Original completed
         * VDP names at the user's location match this source wrap exactly.
         * Keep the independent native foreground path and gameplay untouched. */
        if(s_cw_scene && rd16(s_frame.ram+0x0a56)) {
            int wx=RideMapSourceX(ox+x,oy);
            return TlkMdScenePixel(1,0,wx,oy,0,0,0,0,0,0,0,width);
        }
        /* Selected MD collision layouts must display their own platforms and
         * gaps. The native-cell artwork correspondence deliberately preserves
         * SNES opacity, which is wrong when these terrain choices are MD.
         * These reviewed worlds share exact map dimensions and origin. */
        if(s_md_layout)return TlkMdScenePixel(s_md_level,0,ox+x,oy+(int)s_md_layout_y,0,0,0,0,0,0,0,width);
        int wx=ox+x, wy=oy;
        const Level *level=&s_frame.level;
        if (wx>=0 && wy>=0 && wx<(int)level->rowb*8 && wy<(int)level->rows*16) {
            size_t at=(size_t)(wy/16)*level->rowb+(unsigned)(wx/16)*2;
            unsigned cell=rd16(level->map+at);
            uint16_t pixel=TlkMdSceneMappedPixel(s_md_level,cell,(unsigned)wx,(unsigned)wy);
            if (pixel!=0xffff) return pixel;
        }
    }
    if(layer==1 && s_md_background && s_cw_scene)
        return TlkMdCantWaitBackgroundPixel(s_cant_wait.camera-RideHandoffColumn(width),s_cant_wait.wrap,
            x+column+(320-width)/2,y0);
    /* Original MD Exile upper152 rows author only320 pixels; columns40..63
     * are empty. Reflect its fixed picture into wider margins. The lower
     * scrolling bands retain their complete512-pixel names and own recipe. */
    if(layer==1 && s_md_background && s_md_level==4 && width>320 && y0>=0 && y0<152) {
        int sx=Reflect(x+column+(320-width)/2,320);
        return TlkMdSceneBackgroundViewPixel(4,s_bg_view_left,s_bg_camera[1],sx,y0,320);
    }
    if (layer==1 && s_md_background)
        return TlkMdSceneBackgroundViewPixel(s_md_level,s_bg_view_left,s_bg_camera[1],x+column,y0,width);
    if(s_toss_canvas && layer<2){
        x=x*256/s_toss_canvas;map=false;
    }
    static const uint8_t low[3] = { 8, 7, 1 }, high[3] = { 12, 11, 3 };
    unsigned bpp = layer == 2 ? 2 : 4, size = (l->bgmode >> (4 + layer)) & 1 ? 16 : 8;
    uint16_t tile;
    int px, py;
    /* MD ride-camera warps leave an incomplete native BG1 ring visible at
     * the strip joint. Native artwork needs the same scene-specific source
     * addressing used to recognize the submitted map, across the full view.
     * Keep SNES-camera playback and decoded MD scenery on their own paths. */
    bool native_ride=layer==0 && s_ride_scene;
    bool native_hunt=layer==0 && s_area_active && HuntScene();
    if(layer==0 && s_native_md_layout && NativeLayoutTile(ox+x,oy,&tile)) {
        px=ox+x;py=oy;
    } else if (layer == 0 && (map || native_ride || native_hunt)) {
        px = native_ride?RideMapSourceX(ox+x,oy):ox+x;
        py = oy;
        if (!MapTile(&s_frame.level, &px, &py, &tile)) return 0;
    } else {
        if (layer == 2 && (x < 0 || x >= 256)) return 0;   /* BG3 carries text, not scenery */
        int source_x=x+(int)(l->hofs[layer]&1023);
        /* Exile's fixed upper152 rows use the first256 pixels of the native
         * background. The rest of that map row is unused black, unlike its
         * fully authored scrolling lower bands. Reflect the fixed picture in
         * added columns; keep every original column and lower-band scroll. */
        if(layer==1 && s_frame.stage && s_md_level==4 &&
           rd24(s_frame.ram+0xdf)==0xc0044f && !s_md_background && size==8 &&
           y0>=0 && y0<152 && !(l->hofs[1]&1023)) {
            unsigned u=(unsigned)source_x&511;
            source_x=u<256?(int)u:511-(int)u;
        }
        /* Pride's finite 64-column panorama has no authored negative columns.
         * Extend its edge into added margins; retain every native PPU column. */
        if (layer==1 && s_native_pride_bg_edges && (x<0 || x>=256)) {
            if (source_x<0) source_x=0;
            if (source_x>511) source_x=511;
        }
        px = source_x & 1023;
        py = (int)(((unsigned)y0 + 1 + l->vofs[layer]) & 1023);
        if(layer==1 && s_area_active && s_area_height>224 && (s_md_level<2 || HuntScene()) &&
           !s_md_background && s_native_panorama_height[s_md_level] && size==8){
            py=y0;if(py<0)py=0;if(py>=(int)s_native_panorama_height[s_md_level])py=s_native_panorama_height[s_md_level]-1;
            /* A mirrored copy meets the same edge at each join. This is a
             * wide-window presentation extension, not additional original art. */
            int source_x=x+(int)(l->hofs[layer]&1023);
            return s_panorama_pixels[l->vram][(unsigned)py*512+PanoramaX(x+PanoramaScroll(l))];
        }else tile = VramTilemap(vram, l->bgsc[layer], (unsigned)px, (unsigned)py, size);
    }
    if(layer==2 && s_sound_test_text_on && size==8 && px>=72 && px<232 && py>=96 && py<136) {
        unsigned c=(unsigned char)s_sound_test_text[(py-96)/8][(px-72)/8];
        /* Native menu atlas has uppercase letters; MD catalogue uses title
         * case. Select the actual native letter glyph, never unrelated tiles. */
        if(c>='a' && c<='z')c-=32;
        tile=(uint16_t)(c>32 && c<=127?0x2d00+c-32:0x100);
    }
    unsigned cx = (unsigned)px & (size - 1), cy = (unsigned)py & (size - 1);
    if (tile & 0x4000) cx = size - 1 - cx;
    if (tile & 0x8000) cy = size - 1 - cy;
    unsigned number = ((tile & 1023) + cx / 8 + cy / 8 * 16) & 1023;
    unsigned base = ((l->bgchr >> (layer * 4)) & 15) << 12;
    unsigned pixel = TilePixel(vram, (base + number * bpp * 4) & 0x7FFF, cx & 7, cy & 7, bpp);
    if (!pixel) return 0;
    unsigned index = (((tile >> 10) & 7) << bpp) | pixel;
    unsigned z = tile & 0x2000 ? (layer == 2 && (l->bgmode & 8) ? 15 : high[layer]) : low[layer];
    return (uint16_t)(z << 12 | layer << 8 | index);
}

/* Assemble a native foreground row in tile-sized runs. Source selection,
 * palettes and priorities match BgPixel; only repeated dictionary/bitplane
 * work is shared by the eight pixels of a tile. */
static void NativeAreaForegroundRow(uint16_t *out,int width,int column,const Line *l,int y0,int ox,int oy,bool left_map,bool right_map) {
    const uint16_t *vram=s_vram[l->vram];unsigned base=(l->bgchr&15)<<12;
    for(int i=0;i<width;){
        int x=i-column,px,py,step=1;uint16_t tile=0;
        bool map=s_ride_scene || (s_area_active && HuntScene()) || y0<0 || y0>=224 || (x<0?left_map:x>=256&&right_map);
        if(s_native_md_layout && NativeLayoutTile(ox+x,oy,&tile)) {
            px=ox+x;py=oy;
        }else if(map){
            px=s_ride_scene?RideMapSourceX(ox+x,oy):ox+x;py=oy;
            int source_x=px;
            if(!MapTile(&s_frame.level,&px,&py,&tile)){out[i++]=0;continue;}
            /* Preserve the existing reflected/clamped map coordinates, but
             * decode reflected tile rows in runs too. A large view near a
             * level edge otherwise repeats full per-pixel material lookup. */
            int next=Reflect(source_x+1,(int)s_frame.level.rowb*8);
            step=next-px;
            if(step!=1 && step!=-1)step=0;
        }else{
            px=(x+l->hofs[0])&1023;py=(y0+1+l->vofs[0])&1023;
            tile=VramTilemap(vram,l->bgsc[0],(unsigned)px,(unsigned)py,8);
        }
        int run=step<0?(px&7)+1:step>0?8-(px&7):1;if(run>width-i)run=width-i;
        if(x<0 && run>-x)run=-x;
        if(x>=0 && x<256 && run>256-x)run=256-x;
        unsigned cy=py&7;if(tile&0x8000)cy=7-cy;
        unsigned a=(base+(tile&1023)*16+cy)&0x7fff,lo=vram[a],hi=vram[(a+8)&0x7fff];
        unsigned token=((tile&0x2000?12:8)<<12)|((tile>>10&7)<<4);
        for(int j=0;j<run;j++){
            unsigned sx=px+step*j,bit=tile&0x4000?sx&7:7-(sx&7);
            unsigned pixel=((lo>>bit)&1)|((lo>>(bit+8))&1)<<1|((hi>>bit)&1)<<2|((hi>>(bit+8))&1)<<3;
            out[i+j]=pixel?(uint16_t)(token|pixel):0;
        }
        i+=run;
    }
}

/* Ordinary native8x8 BG2 names. Decode each tile row once, retaining the
 * selected captured row's actual name table, scroll, priority and palette.
 * Preserve Exile's existing fixed upper256-pixel reflection; panoramas and
 * rides stay on their own paths. This changes decoding work, not addressing. */
static void NativeReturnBackgroundRow(uint16_t *out,int width,int column,const Line *l,int y0) {
    if(y0<0)y0=0;if(y0>=224)y0=223;
    /* Match BgPixel's existing authored bottom-band join exactly. */
    if(y0==223 && s_area_active && s_area_height>224 &&
       !s_md_background && BottomBackgroundBandSize())y0=222;
    const uint16_t *vram=s_vram[l->vram];unsigned base=((l->bgchr>>4)&15)<<12;
    unsigned py=(y0+1+l->vofs[1])&1023;
    int reflect=s_frame.stage && s_md_level==4 && rd24(s_frame.ram+0xdf)==0xc0044f &&
        y0<152 && !(l->hofs[1]&1023);
    for(int i=0;i<width;){
        unsigned px=(i-column+l->hofs[1])&1023;
        int step=1;
        if(reflect){unsigned u=(unsigned)(i-column)&511;px=u<256?u:511-u;step=u<256?1:-1;}
        unsigned tile=VramTilemap(vram,l->bgsc[1],px,py,8),cy=py&7;
        if(tile&0x8000)cy=7-cy;
        unsigned a=(base+(tile&1023)*16+cy)&0x7fff,lo=vram[a],hi=vram[(a+8)&0x7fff];
        unsigned token=((tile&0x2000?11:7)<<12)|0x100|((tile>>10&7)<<4);
        int run=step<0?(px&7)+1:8-(px&7);if(run>width-i)run=width-i;
        for(int j=0;j<run;j++){
            unsigned sx=px+step*j,bit=tile&0x4000?sx&7:7-(sx&7);
            unsigned pixel=((lo>>bit)&1)|((lo>>(bit+8))&1)<<1|((hi>>bit)&1)<<2|((hi>>(bit+8))&1)<<3;
            out[i+j]=pixel?(uint16_t)(token|pixel):0;
        }
        i+=run;
    }
}


/* Authored bottom bands in these two scenes have uniform scroll. Continuing
 * them is an expanded-view fallback, not additional original level artwork. */
static unsigned BottomBackgroundBandSize(void) {
    unsigned level=rd16(s_frame.ram+0x1ff9e),scene=rd24(s_frame.ram+0xdf);
    if(!s_frame.stage)return 0;
    unsigned span=level==2 && scene==0xc003eb?64:level==4 && scene==0xc0044f?24:0;
    if(!span)return 0;
    const Line *last=&s_frame.lines[223];
    for(unsigned y=224-span;y<224;y++) {
        const Line *l=&s_frame.lines[y];
        if(l->hofs[1]!=last->hofs[1] || l->vofs[1]!=last->vofs[1] ||
           l->bgsc[1]!=last->bgsc[1] || l->bgchr!=last->bgchr)return 0;
    }
    return span;
}
static const uint16_t *BottomBackgroundRow(const Line *l,int width,int column,int y0,int ox,int oy) {
    if(!s_area_active || s_area_height<=224 || y0<224)return NULL;
    unsigned span=BottomBackgroundBandSize();if(!span)return NULL;
    unsigned first=224-span;
    if(!s_md_background)span--; /* Exclude the unused native source224 row. */
    unsigned phase=(unsigned)(y0-224)%(span*2);
    unsigned row=phase<span?span-1-phase:phase-span;
    static uint16_t tokens[64][TLK_WIDE_MAX_WIDTH];
    static unsigned epoch,ready[64];static int cached_width,cached_column;
    if(epoch!=s_draw_choice_epoch || cached_width!=width || cached_column!=column){
        epoch=s_draw_choice_epoch;cached_width=width;cached_column=column;
        memset(ready,0,sizeof ready);
    }
    if(!ready[row]){
        int source_y=(int)first+(int)row;
        for(int i=0;i<width;i++)tokens[row][i]=BgPixel(l,s_vram[l->vram],1,i-column,source_y,false,ox,oy,column,width);
        ready[row]=1;
    }
    return tokens[row];
}

static const uint8_t kSpriteSizes[8][2] = {
    { 8, 16 }, { 8, 32 }, { 8, 64 }, { 16, 32 }, { 16, 64 }, { 32, 64 }, { 16, 32 }, { 16, 32 } };

#include "tlk_monkey_projectile.inc"
#include "tlk_arena_debris.inc"
#include "tlk_shared_ambient_effect.inc"
static const uint16_t *s_pillar_vram[kMaxPieces];
static unsigned s_pillar_key[kMaxPieces],s_pillar_obsel[kMaxPieces];
static bool GraveyardPillarPiece(const Piece *p) {
    return p && s_frame.stage &&
        ((s_md_level==2 && rd24(s_frame.ram+0xdf)==0xc003eb && p->actor_descriptor==0xc58d44) ||
         (s_md_level==7 && rd24(s_frame.ram+0xdf)==0xc004e5 && (p->actor_descriptor==0xc58d52 || p->actor_descriptor==0xc5874a))) &&
        !p->fixed && p->pose==0x7eab06 && p->size==16 &&
        ((p->attr>>9)&7)==4 && !(p->attr&0xc000) &&
        (p->local_x==-16 || p->local_x==0) && p->local_y>=0 && !(p->local_y&15);
}
/* C1CC50 caps the dynamic frame at208 although C2D35A positions the
 * liquid top using its full actor height. Extend only tall-view presentation,
 * using the factory's live base and its existing alternating32-pixel tail.
 * When a tall view exposes the final32px below this bottom-edge fountain,
 * continue its existing body to the finite map edge. This is presentation
 * below the original base, not an extra liquid plane or a larger hazard. */
static unsigned GraveyardLiquidHeight(const Piece *p) {
    if(s_spawn_height<=224 || !GraveyardPillarPiece(p) || s_md_level!=2)return 0;
    unsigned actor=TlkGraveyardPillarOwner(s_frame.ram,p->obj,p->pose);
    if(!actor)return 0;
    unsigned height=rd16(s_frame.ram+actor+44);
    int top=(int16_t)rd16(s_frame.ram+actor+10);
    int base=(int16_t)rd16(s_frame.ram+actor+94);
    if(height<32 || height>768 || base-top!=(int)height)return 0;
    unsigned map_bottom=s_frame.level.rows*16;
    if(map_bottom==(unsigned)base+32)return height+32;
    return height>208?height:0;
}
static void GraveyardLiquidTailParts(void) {
    unsigned count=s_frame.piece_count;
    for(unsigned i=0;i<count;i++) {
        const Piece first=s_frame.pieces[i];
        if(first.local_x!=-16 || first.local_y)continue;
        unsigned height=GraveyardLiquidHeight(&first);if(!height)continue;
        unsigned actor=TlkGraveyardPillarOwner(s_frame.ram,first.obj,first.pose);
        unsigned native_height=rd16(s_frame.ram+actor+44);
        unsigned start=((native_height<208?native_height:208)+15)&~15u;
        for(unsigned y=start;y<height;y+=16)for(int x=-16;x<=0;x+=16) {
            unsigned j=0;
            for(;j<s_frame.piece_count;j++)if(s_frame.pieces[j].obj==first.obj &&
                s_frame.pieces[j].local_x==x && s_frame.pieces[j].local_y==(int)y)break;
            if(j<s_frame.piece_count)continue;
            unsigned source=count;
            for(j=0;j<count;j++) {
                const Piece *p=&s_frame.pieces[j];
                if(p->obj!=first.obj || p->local_x!=x || p->local_y<16 || !GraveyardPillarPiece(p))continue;
                if(p->local_y==(int)(32+(y-32)%32)){source=j;break;}
                if(source==count || p->local_y>s_frame.pieces[source].local_y)source=j;
            }
            /* A short, retracting column can expose only one body row.
             * Continue that live row rather than borrowing a stale phase. */
            if(source==count)continue;
            if(s_frame.piece_count>=kMaxPieces)return;
            Piece tail=s_frame.pieces[source];tail.y+=(int)y-tail.local_y;tail.local_y=(int)y;tail.kept=false;
            s_frame.pieces[s_frame.piece_count++]=tail;
        }
    }
    /* The factory's second current draw has the same generated source frame
     * at actor+28. Expanded-view submissions can exhaust OAM before that draw
     * is visited. Recover only its missing outside-console pieces, using the
     * reciprocal factory owner and the primary's actual current tile phase. */
    if(s_enabled && s_frame.stage && (s_spawn_height>224 || s_spawn_lead>0) &&
       s_md_level==2 && rd24(s_frame.ram+0xdf)==0xc003eb) {
        unsigned original=s_frame.piece_count;
        for(unsigned i=0;i<original;i++) {
            const Piece first=s_frame.pieces[i];
            if(first.local_x!=-16 || first.local_y || !GraveyardPillarPiece(&first))continue;
            unsigned actor=TlkGraveyardPillarOwner(s_frame.ram,first.obj,first.pose);
            if(!actor || rd16(s_frame.ram+actor+12)!=first.obj)continue;
            unsigned secondary=rd24(s_frame.ram+actor+36)&65535;
            if(TlkGraveyardPillarOwner(s_frame.ram,secondary,first.pose)!=actor ||
               (rd16(s_frame.ram+secondary+8)&0xe0c0) ||
               rd16(s_frame.ram+secondary+8)!=rd16(s_frame.ram+first.obj+8))continue;
            int dx=(int16_t)(rd16(s_frame.ram+actor+28)-rd16(s_frame.ram+actor+8));
            int dy=(int16_t)(rd16(s_frame.ram+actor+30)-rd16(s_frame.ram+actor+10));
            for(unsigned n=0;n<original && s_frame.piece_count<kMaxPieces;n++) {
                Piece part=s_frame.pieces[n];
                if(part.obj!=first.obj || !GraveyardPillarPiece(&part))continue;
                part.x+=dx;part.y+=dy;
                if(part.x<256 && part.x+part.size>0 && part.y<224 && part.y+part.size>0)continue;
                unsigned j=0;
                for(;j<s_frame.piece_count;j++)if(s_frame.pieces[j].obj==secondary &&
                    s_frame.pieces[j].local_x==part.local_x && s_frame.pieces[j].local_y==part.local_y)break;
                if(j<s_frame.piece_count)continue;
                if(s_frame.piece_count>=kMaxPieces)return;
                part.obj=secondary;part.kept=false;part.slot=127;
                s_frame.pieces[s_frame.piece_count++]=part;
            }
        }
    }
}
/* Display the adjacent turns of the same original cyclic stream. The real
 * platforms and collision code keep their300px window around the gameplay
 * camera; adjacent turns are wholly outside that console window and become
 * the real source drawing as its original wrap occurs. Each wrap resets X
 * and toggles horizontal facing, which these presentation pieces follow. */
static void WaterfallLogCycleParts(void) {
    const uint8_t *ram=s_frame.ram;
    if(!s_enabled || !s_frame.stage || s_spawn_height<=224 ||
       rd16(ram+0x1ff9e)!=5 || rd24(ram+0xdf)!=0xc00481)return;
    unsigned count=s_frame.piece_count;
    int camera=(int)rd16(ram+0xb29d);
    for(unsigned i=0;i<count;i++) {
        Piece p=s_frame.pieces[i];
        if(p.fixed || p.actor_descriptor!=0xc58aec || p.obj>0xffe8)continue;
        unsigned position=rd16(ram+p.obj+4);
        if(position<0xb21b || position>0xdc0b)continue;
        unsigned actor=position-8;
        if(((actor-0xb213)&127) || rd16(ram+actor+12)!=p.obj ||
           rd24(ram+actor+4)!=0xc58aec || rd24(ram+actor+48)!=0xc48df7 ||
           (rd16(ram+p.obj+8)&0xe000))continue;
        /* RecordPiece already validated the submitted pose and captured its
         * owner. The animation cursor can advance after that completed draw;
         * comparing it with p.pose would drop every adjacent turn for a frame. */
        int y=(int16_t)rd16(ram+actor+10),home=(int16_t)rd16(ram+actor+46);
        /* C48DF7 tests its wrap bounds before C19711 moves the log. Recover
         * that tested Y from the actual fixed-point step; the displayed log
         * can already be one step beyond the bound until its next update. */
        int step=(int16_t)rd16(ram+actor+62)+
            (rd16(ram+actor+54)<rd16(ram+actor+60));
        int tested_y=y-step;
        if(tested_y<camera-40 || tested_y>camera+260 || !rd16(ram+actor+8) || home<=0)continue;
        for(int turn=-3;turn<=3 && s_frame.piece_count<kMaxPieces;turn++) {
            if(!turn || y+turn*300<0 || y+turn*300>1080)continue;
            Piece copy=p;copy.y+=turn*300;copy.kept=false;
            if(turn&1)copy.attr^=0x4000;
            int anchor=home-s_frame.raster_camera[0];
            copy.x=(copy.attr&0x4000)?anchor-copy.local_x-copy.size:anchor+copy.local_x;
            s_frame.pieces[s_frame.piece_count++]=copy;
        }
    }
}
static unsigned GraveyardPillarPose(const Piece *p,const Line *l,const uint16_t *vram) {
    if(!GraveyardPillarPiece(p))return 0;
    unsigned n=0;
    for(;n<s_frame.piece_count;n++) {
        const Piece *first=&s_frame.pieces[n];
        if(first->obj==p->obj && first->local_x==-16 && !first->local_y && GraveyardPillarPiece(first))break;
    }
    if(n==s_frame.piece_count)return 0;
    if(s_pillar_vram[n]!=vram || s_pillar_obsel[n]!=l->obsel) {
        s_pillar_vram[n]=vram;s_pillar_obsel[n]=l->obsel;s_pillar_key[n]=0;
        unsigned attr=s_frame.pieces[n].attr,base=(l->obsel&7u)<<13;
        if(attr&0x100)base+=((l->obsel&0x18u)+8)<<9;
        unsigned hash=2166136261u;
        for(unsigned y=0;y<16;y++)for(unsigned x=0;x<16;x++) {
            unsigned t=(((((attr&255u)>>4)+(y>>3))<<4)|(((attr&15u)+(x>>3))&15));
            hash=(hash^TilePixel(vram,base+t*16,x&7,y&7,4))*16777619u;
        }
        for(unsigned phase=0;phase<8;phase++)if(hash==graveyard_pillar_piece_hashes[phase][0]) {
            s_pillar_key[n]=graveyard_pillar_keys[phase];break;
        }
    }
    return s_pillar_key[n];
}
static int GraveyardPillarSample(unsigned pose,int x,int y,unsigned pixel,int frames,int palette,
                                const uint16_t *cgram,uint16_t *color) {
    if(y>=64)y=32+(y-32)%32;
    return TlkMdSpritesNpcSample(pose,x,y,pixel,frames,palette,cgram,color);
}

/* One row of a sprite into obj (indexed by screen x + column), screen
 * columns [lo, hi) only. Later calls overwrite, so callers go from the lowest
 * priority sprite to the highest. Returns pixels drawn. */
static unsigned DiagnosticBytes(unsigned h,const uint8_t *bytes,unsigned n) {
    for(unsigned i=0;i<n;i++)h=(h^bytes[i])*16777619u;
    return h;
}
static TlkFallbackSpriteInfo *SpriteDiagnostic(const Piece *p,const Line *l,const uint16_t *vram,
                                               int width,int screen_x,unsigned attr,unsigned role,bool cub) {
    if(!s_fallback_enabled || !p)return NULL;
    unsigned n=(unsigned)(p-s_frame.pieces);if(n>=s_frame.piece_count || n>=kMaxPieces)return NULL;
    TlkFallbackSpriteInfo *d=&s_fallback_sprite_info[n];
    if(!s_fallback_sprite_valid[n]){
        memset(d,0,sizeof *d);s_fallback_sprite_valid[n]=1;
        d->descriptor=p->actor_descriptor;d->size=p->size;d->attributes=attr;d->draw_width=(unsigned)width;
        d->screen_x=screen_x;d->screen_y=p->y+1;d->local_x=p->local_x;d->local_y=p->local_y;
        d->player_x=(int16_t)rd16(s_frame.ram+0xb21b);d->player_y=(int16_t)rd16(s_frame.ram+0xb21d);
        d->camera_x=s_frame.raster_camera[0];d->camera_y=s_frame.raster_camera[1];
        unsigned pos=p->obj<=0xffe8?rd16(s_frame.ram+p->obj+4):0;
        if(pos>=0x8008 && pos<=0xff88){
            unsigned actor=pos-8;d->actor=actor;d->latched_descriptor=rd24(s_frame.ram+actor+4);
            d->action=rd24(s_frame.ram+actor+48);d->actor_x=(int16_t)rd16(s_frame.ram+actor+8);d->actor_y=(int16_t)rd16(s_frame.ram+actor+10);
            d->owner_valid=rd16(s_frame.ram+actor+12)==p->obj && d->latched_descriptor==p->actor_descriptor;
        }
        unsigned bank=0;
        TlkMdSpritesDescribe(SceneNpcPose(p),&d->mapped_pose,&d->mapped_role,&bank,&d->md_palette,&d->image_ready);
        d->scene_role=role;
        d->frames_md=cub?s_md_cub_frames:role?s_md_npc_frames[role]:s_fallback_all_sprites;
        d->palette_md=role?s_md_npc_palette[role]:s_fallback_all_sprites;
        if((p->pose&0xfe0000)==0x7e0000){
            unsigned at=p->pose&0x1ffff,nbytes=sizeof s_frame.ram-at;if(nbytes>64)nbytes=64;
            d->pose_header_fnv32=DiagnosticBytes(2166136261u,s_frame.ram+at,nbytes);
        }
        unsigned base=(l->obsel&7u)<<13;if(attr&0x100)base+=((l->obsel&0x18u)+8)<<9;
        unsigned hash=2166136261u;
        for(unsigned y=0;y<p->size;y++)for(unsigned x=0;x<p->size;x++){
            unsigned t=(((((attr&255u)>>4)+(y>>3))<<4)|(((attr&15u)+(x>>3))&15));
            hash=(hash^TilePixel(vram,base+t*16,x&7,y&7,4))*16777619u;
        }
        d->tile_fnv32=hash;
    }
    d->native_palette=(attr>>9)&7;unsigned hash=2166136261u;
    for(unsigned i=0;i<16;i++){
        unsigned c=l->cgram[128+d->native_palette*16+i];hash=(hash^(c&255))*16777619u;hash=(hash^(c>>8))*16777619u;
    }
    d->palette_fnv32=hash;
    return d;
}
static int CapturedByte(unsigned address) {
    unsigned bank=address>>16,offset=address&65535;
    if(bank==0x7e || bank==0x7f)return s_frame.ram[(bank-0x7e)*65536+offset];
    if(bank>=0xc0){unsigned at=address&0x3fffff;if(at<s_rom_size)return s_rom[at];}
    return -1;
}
static int OriginalPieceSource(const Piece *p,unsigned *source,unsigned *stride) {
    if(!p || p->kept || p->fixed)return 0;
    unsigned pose=p->pose&0x3fffff;if(pose+29>s_rom_size)return 0;
    const uint8_t *h=s_rom+pose;unsigned flags=rd16(h),slots=flags&127;
    if(!slots || slots>32)return 0;
    if(flags&0x8000){
        unsigned large=flags&0x4000?(flags>>8)&63:slots,base=rd24(h+26);
        if(large>slots)return 0;unsigned count=large*4;
        for(unsigned i=0;i<large;i++){
            if(pose+29+i*4+4>s_rom_size)return 0;const uint8_t *q=h+29+i*4;
            if(p->size==16 && (int16_t)rd16(q)==p->local_x && (int16_t)rd16(q+2)==p->local_y){*source=base+i*64;*stride=slots*64;return CapturedByte(*source)>=0&&CapturedByte(*source+*stride+63)>=0;}
        }
        if(flags&0x4000)for(unsigned i=large;count<slots*4;i++,count++){
            if(pose+29+i*4+4>s_rom_size)return 0;const uint8_t *q=h+29+i*4;if(rd16(q)==0xaaaa)break;
            if(p->size==8 && (int16_t)rd16(q)==p->local_x && (int16_t)rd16(q+2)==p->local_y){*source=base+count/4*64+(count%2)*32+(count%4/2)*slots*64;*stride=0;return CapturedByte(*source)>=0&&CapturedByte(*source+31)>=0;}
        }
    }else {
        unsigned bank=(unsigned)h[26]<<16;
        for(unsigned i=0;i<64;i++){
            if(i>=slots && !(flags&0x4000))break;
            if(pose+27+i*6+6>s_rom_size)return 0;const uint8_t *q=h+27+i*6;if(rd16(q)==0xaaaa)break;
            unsigned size=i<slots?16:8;
            if(p->size==size && (int16_t)rd16(q)==p->local_x && (int16_t)rd16(q+2)==p->local_y){*source=bank|rd16(q+4);*stride=size==16?64:0;return CapturedByte(*source)>=0&&CapturedByte(*source+size*size/2-1)>=0;}
        }
    }
    return 0;
}
static int RidePieceSource(const Piece *p,unsigned role,unsigned *source,unsigned *stride) {
    if(!s_ride_scene || !p || p->kept || p->fixed)return 0;
    int ostrich=0;
    for(unsigned n=0;n<sizeof cw_ostrich_descriptors/sizeof *cw_ostrich_descriptors;n++)
        ostrich|=p->actor_descriptor==cw_ostrich_descriptors[n];
    if(role!=TLK_MD_SPRITE_CW_RIDE_OBSTACLE && role!=TLK_MD_SPRITE_CW_GIRAFFE &&
       role!=TLK_MD_SPRITE_CW_HIPPO && role!=TLK_MD_SPRITE_CW_RHINO && !ostrich)return 0;
    return OriginalPieceSource(p,source,stride);
}
/* Native world animals can be visible before the console tile uploader admits
 * them. Their submitted pose/part metadata already identifies the exact source
 * glyph. Preserve the live palette, flips, positions and original draw lifetime.
 * King monkeys use these shared native drawings in either palette style. */
static int NativeAnimalPieceSource(const Piece *p,unsigned role,unsigned *source,unsigned *stride) {
    if(p && !p->kept && !p->fixed && s_frame.stage && s_md_level==2 &&
       rd24(s_frame.ram+0xdf)==0xc003eb && role==TLK_MD_SPRITE_GRAVEYARD_VULTURE &&
       DrawActorDescriptor(s_frame.ram,p->obj,p->pose)==p->actor_descriptor && !s_md_npc_frames[role])
        return OriginalPieceSource(p,source,stride);
    if(!s_cw_scene || s_ride_scene || !p || p->kept || p->fixed)return 0;
    int monkey=0;
    for(unsigned n=0;n<sizeof cw_monkey_descriptors/sizeof *cw_monkey_descriptors;n++)
        if(p->actor_descriptor==cw_monkey_descriptors[n]){monkey=1;break;}
    int rhino=(p->actor_descriptor==0xc58c08 || p->actor_descriptor==0xc58c14) &&
        !s_md_npc_frames[TLK_MD_SPRITE_CW_RHINO];
    if(!monkey && !rhino)return 0;
    return OriginalPieceSource(p,source,stride);
}
/* C0A6A2 refuses an entire drawing once the native127-piece counter is
 * full. A tall King view can fill it with extra giraffe parts before visiting
 * the rhino, another giraffe head or later monkeys. Recover only their actual
 * submitted pose parts in expanded views, at the
 * existing seam after the game's visibility/blink and horizontal tests.
 * Guest OAM, uploads, counter and actor state stay untouched. */
static unsigned AppendKingAnimalParts(Piece *out,unsigned *used,unsigned obj,unsigned pose,
                                     unsigned descriptor,unsigned attributes,int x,int y,unsigned yoff) {
    unsigned at=pose&0x3fffff;
    if(at+29>s_rom_size)return 0;
    unsigned flags=rd16(s_rom+at),slots=flags&127;
    if(!(flags&0x8000) || !slots || slots>32)return 0;
    unsigned large=flags&0x4000?(flags>>8)&63:slots;
    if(large>slots)return 0;
    unsigned count=large*4,added=0;
    if(attributes&0x4000)return 0;
    for(unsigned n=0;n<128 && *used<kMaxPieces;n++) {
        unsigned size;
        if(n<large)size=16;
        else {
            if(!(flags&0x4000) || count>=slots*4)break;
            size=8;count++;
        }
        unsigned q=at+29+n*4;
        if(q+4>s_rom_size || rd16(s_rom+q)==0xaaaa)break;
        int lx=(int16_t)rd16(s_rom+q),ly=(int16_t)rd16(s_rom+q+2);
        int dx=attributes&0x40?-lx-(int)size:lx;
        int dy=attributes&0x80?-ly-(int)size-1:ly;
        Piece p={.x=(int16_t)(x+dx),.y=(int16_t)(y+dy-(int)yoff),
            .attr=(uint16_t)(attributes<<8),.obj=(uint16_t)obj,.size=(uint8_t)size,
            .slot=127,.kept=false,.fixed=false,.pose=pose,
            .local_x=(int16_t)lx,.local_y=(int16_t)ly,.actor_descriptor=descriptor};
        unsigned source,stride;if(!OriginalPieceSource(&p,&source,&stride))continue;
        out[(*used)++]=p;added++;
    }
    return added;
}
/* Complete an original approved draw when expanded-view work exhausts the
 * native budget. This follows the submitted pose and its exact source parts;
 * original hidden/blink/fixed state, native OAM and gameplay stay intact. */
static unsigned AppendWideSpriteParts(Piece *out,unsigned *used,const uint8_t *ram,
    unsigned obj,unsigned pose,unsigned descriptor,unsigned attributes,int x,int y,unsigned yoff) {
    if((pose>>16)<0xc0 || obj<0x8000 || obj>0xffe8 || (attributes&0xe000) ||
       !descriptor || DrawActorDescriptor(ram,obj,pose)!=descriptor)return 0;
    unsigned at=pose&0x3fffff;if(at+29>s_rom_size)return 0;
    unsigned flags=rd16(s_rom+at),slots=flags&127;if(!slots || slots>32)return 0;
    Piece source[128];unsigned count=0;
    if(flags&0x8000)AppendKingAnimalParts(source,&count,obj,pose,descriptor,attributes,x,y,yoff);
    else for(unsigned n=0;n<64 && count<128;n++) {
        if(n>=slots && !(flags&0x4000))break;
        unsigned q=at+27+n*6;if(q+6>s_rom_size || rd16(s_rom+q)==0xaaaa)break;
        unsigned size=n<slots?16:8;
        int lx=(int16_t)rd16(s_rom+q),ly=(int16_t)rd16(s_rom+q+2);
        Piece pc={.x=(int16_t)(x+(attributes&0x40?-lx-(int)size:lx)),
            .y=(int16_t)(y+(attributes&0x80?-ly-(int)size-1:ly)-(int)yoff),
            .attr=(uint16_t)(attributes<<8),.obj=(uint16_t)obj,.size=(uint8_t)size,.slot=127,
            .kept=false,.fixed=false,.pose=pose,.local_x=(int16_t)lx,.local_y=(int16_t)ly,.actor_descriptor=descriptor};
        unsigned glyph,stride;if(OriginalPieceSource(&pc,&glyph,&stride))source[count++]=pc;
    }
    int left=0,right=0,top,bottom;
    if(s_spawn_lead>0)PresentationMargins(s_spawn_lead,&left,&right);
    VerticalMargins(&top,&bottom);
    unsigned added=0;
    for(unsigned i=0;i<count && *used<kMaxPieces;i++) {
        const Piece *pc=&source[i];
        if(pc->x+pc->size<=-left-16 || pc->x>=256+right+16 ||
           pc->y+pc->size<=-top-16 || pc->y>=224+bottom+16)continue;
        unsigned n=0;for(;n<*used;n++)if(out[n].obj==obj && out[n].pose==pose &&
            out[n].local_x==pc->local_x && out[n].local_y==pc->local_y && out[n].size==pc->size)break;
        if(n<*used)continue;
        out[(*used)++]=*pc;added++;
    }
    return added;
}
static void RecordWideSpriteBudgetIntent(const CpuState *cpu) {
    if(!s_enabled || (s_spawn_height<=224 && s_spawn_lead<=0) || cpu->D ||
       cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag)return;
    unsigned obj=rd16(g_ram+0x7c),pose=rd24(g_ram+0x85);
    unsigned descriptor=DrawActorDescriptor(g_ram,obj,pose);
    unsigned before=s_build_count;
    AppendWideSpriteParts(s_build,&s_build_count,g_ram,obj,pose,descriptor,
        obj<=0xffe8?rd16(g_ram+obj+8):0,
        (int16_t)rd16(g_ram+0xb4),(int16_t)rd16(g_ram+0xb6),g_ram[0x8c]);
    unsigned at=pose&0x3fffff;if(at+29>s_rom_size)return;
    unsigned flags=rd16(s_rom+at),large=flags&0x8000?
        (flags&0x4000?(flags>>8)&63:flags&127):flags&127;
    unsigned initial=rd16(g_ram+0x93),bits=rd16(g_ram+0xb1);
    for(unsigned n=before;n<s_build_count;n++) {
        Piece *pc=&s_build[n];unsigned ordinal=0;int found=0;
        unsigned start=flags&0x8000?29:27,step=flags&0x8000?4:6;
        for(unsigned j=0;j<128;j++) {
            unsigned q=at+start+j*step;
            if(q+step>s_rom_size || rd16(s_rom+q)==0xaaaa)break;
            if((int16_t)rd16(s_rom+q)==pc->local_x && (int16_t)rd16(s_rom+q+2)==pc->local_y){ordinal=j;found=1;break;}
        }
        if(!found)continue;
        unsigned index=ordinal<large?initial+ordinal:(initial+large)*4+ordinal-large;
        unsigned table=pc->size==16?0xacfd+((index*2)&255):0xadfd+((index*2)&65535);
        pc->attr=(uint16_t)(rd16(g_ram+(table&65535))|bits);
    }
}
static void CompleteWideSpriteParts(void) {
    if(!s_enabled || !s_frame.stage || (s_spawn_height<=224 && s_spawn_lead<=0) ||
       rd16(s_frame.ram+0xad)<127)return;
    unsigned count=s_frame.piece_count;
    for(unsigned i=0;i<count;i++) {
        Piece pc=s_frame.pieces[i];if(pc.fixed || !pc.actor_descriptor)continue;
        unsigned before=0;for(;before<i;before++)if(s_frame.pieces[before].obj==pc.obj)break;
        if(before<i || pc.obj>0xffe8)continue;
        unsigned attributes=rd16(s_frame.ram+pc.obj+8);
        int dx=attributes&0x40?-pc.local_x-pc.size:pc.local_x;
        int dy=attributes&0x80?-pc.local_y-pc.size-1:pc.local_y;
        AppendWideSpriteParts(s_frame.pieces,&s_frame.piece_count,s_frame.ram,
            pc.obj,pc.pose,pc.actor_descriptor,attributes,pc.x-dx,pc.y-dy,0);
    }
}
static int WideSpritePieceSource(const Piece *p,unsigned role,int cub,unsigned *source,unsigned *stride) {
    if(!s_enabled || (s_spawn_height<=224 && s_spawn_lead<=0) || !p || p->kept || p->fixed ||
       (p->pose>>16)<0xc0 || !p->actor_descriptor ||
       p->obj>0xffe8 ||
       (cub?s_md_cub_frames:s_md_npc_frames[role]))return 0;
    unsigned pos=rd16(s_frame.ram+p->obj+4);
    if(pos<0x8008 || pos>0xff88 || rd16(s_frame.ram+pos-8+12)!=p->obj ||
       rd24(s_frame.ram+pos-8+4)!=p->actor_descriptor)return 0;
    if(!OriginalPieceSource(p,source,stride))return 0;
    return (*source>>16)>=0xc0;
}
/* A paused current save preserves its last submitted piece list. If that
 * original draw hit the budget before a head, no new draw hook runs until
 * resume. Recover only a completely absent, live, initialized head packet;
 * original hidden/blink/fixed packets and incomplete or retiring owners stay
 * untouched. This is source-validated presentation, never an actor update. */
static void PausedGiraffeBudgetParts(void) {
    const uint8_t *ram=s_frame.ram;
    if(!s_frame.stage || !rd16(ram+0xa89) || rd16(ram+0xad)<127 ||
       rd16(ram+0x1ff9e)!=1 || rd24(ram+0xdf)!=0xc003b9 || rd16(ram+0xa56) ||
       (s_spawn_height<=224 && s_spawn_lead<=32))return;
    unsigned actor=rd16(ram+0x76);
    for(unsigned step=0;step<96 && actor>=0xb213 && actor<0xdc13 && !((actor-0xb213)&127);step++,actor=rd16(ram+actor+2)) {
        unsigned descriptor=rd24(ram+actor+4),obj=rd16(ram+actor+12);
        if(descriptor!=0xc58d60 && descriptor!=0xc58d70 && descriptor!=0xc58d80)continue;
        if(obj<0x8000 || obj>0xffe8 || rd16(ram+obj+4)!=actor+8 || (ram[obj+9]&0xe0))continue;
        unsigned pose=rd24(ram+obj+10);
        static const unsigned poses[]={0xc07d93,0xc07de6,0xc07e35,0xc07e78,0xc07ebf,0xc07f12,0xc07f59};
        unsigned n=0;for(;n<7;n++)if(pose==poses[n])break;if(n==7)continue;
        if(DrawActorDescriptor(ram,obj,pose)!=descriptor)continue;
        for(n=0;n<s_frame.piece_count;n++)if(s_frame.pieces[n].obj==obj)break;
        if(n<s_frame.piece_count)continue;
        AppendKingAnimalParts(s_frame.pieces,&s_frame.piece_count,obj,pose,descriptor,rd16(ram+obj+8),
            (int16_t)(rd16(ram+actor+8)-rd16(ram+0xb29b)),
            (int16_t)(rd16(ram+actor+10)-rd16(ram+0xb29d)),ram[0x8c]);
    }
}
/* A riding Simba can jump independently while his bird remains on the road.
 * The native224-row draw cull then skips the whole bird although the taller
 * bottom-anchored view still includes it. Keep the original finite ride spawn
 * window and guest drawing untouched; recover the current owned source pose
 * only when its entire box is outside the native camera and no part submitted. */
static void RideOstrichPresentationParts(void) {
    const uint8_t *ram=s_frame.ram;
    if(!s_enabled || !s_frame.stage || s_spawn_height<=224 ||
       rd16(ram+0x1ff9e)!=1 || rd24(ram+0xdf)!=0xc003b9 || !rd16(ram+0xa56))return;
    int origin=(int)rd16(ram+0xd4)*16-s_spawn_height;
    unsigned actor=rd16(ram+0x76);
    for(unsigned step=0;step<96 && actor>=0xb213 && actor<0xdc13 && !((actor-0xb213)&127);step++,actor=rd16(ram+actor+2)) {
        unsigned descriptor=rd24(ram+actor+4),kind=0;
        for(;kind<sizeof cw_ostrich_descriptors/sizeof *cw_ostrich_descriptors;kind++)
            if(descriptor==cw_ostrich_descriptors[kind])break;
        if(kind==sizeof cw_ostrich_descriptors/sizeof *cw_ostrich_descriptors)continue;
        unsigned obj=rd16(ram+actor+12);
        if(obj<0x8000 || obj>0xffe8 || rd16(ram+obj+4)!=actor+8 || (ram[obj+9]&0xe0))continue;
        unsigned pose=rd24(ram+obj+10),n=0;
        for(;n<sizeof cw_ostrich_poses/sizeof *cw_ostrich_poses;n++)if(pose==cw_ostrich_poses[n])break;
        if(n==sizeof cw_ostrich_poses/sizeof *cw_ostrich_poses || DrawActorDescriptor(ram,obj,pose)!=descriptor)continue;
        unsigned at=pose&0x3fffff;if(at+29>s_rom_size)return;
        int top=(int16_t)rd16(s_rom+at+4),height=rd16(s_rom+at+8);
        int world_y=rd16(ram+actor+10),native_y=world_y-(int)rd16(ram+0xb29d);
        if(native_y+top<224 && native_y+top+height>0)continue;
        if(world_y+top>=origin+s_spawn_height || world_y+top+height<=origin)continue;
        for(n=0;n<s_frame.piece_count;n++)if(s_frame.pieces[n].obj==obj)break;
        if(n<s_frame.piece_count)continue;
        AppendKingAnimalParts(s_frame.pieces,&s_frame.piece_count,obj,pose,descriptor,rd16(ram+obj+8),
            (int16_t)(rd16(ram+actor+8)-rd16(ram+0xb29b)),native_y,ram[0x8c]);
    }
}
/* The original draw list can mark a live attacking vulture hidden while it
 * is wholly outside the console picture. In a larger world that body can
 * already reach Simba. Render its exact current source pose only in the
 * additional view; never clear the guest hide bit or change its hit box. */
static void GraveyardVulturePresentationParts(void) {
    const uint8_t *ram=s_frame.ram;
    if(!s_enabled || !s_frame.stage || (s_spawn_height<=224 && s_spawn_lead<=0) ||
       rd16(ram+0x1ff9e)!=2 || rd24(ram+0xdf)!=0xc003eb)return;
    unsigned actor=rd16(ram+0x76);
    for(unsigned step=0;step<96 && actor>=0xb213 && actor<0xdc13 && !((actor-0xb213)&127);step++,actor=rd16(ram+actor+2)) {
        unsigned descriptor=rd24(ram+actor+4),action=rd24(ram+actor+48);
        unsigned kind=0;
        for(;kind<sizeof graveyard_vulture_descriptors/sizeof *graveyard_vulture_descriptors;kind++)
            if(descriptor==graveyard_vulture_descriptors[kind])break;
        if(kind==sizeof graveyard_vulture_descriptors/sizeof *graveyard_vulture_descriptors ||
           (action!=0xc173e7 && action!=0xc17911) ||
           !rd16(ram+actor+42) || rd16(ram+actor+42)>=100)continue;
        unsigned obj=rd16(ram+actor+12);
        if(obj<0x8000 || obj>0xffe8 || rd16(ram+obj+4)!=actor+8 ||
           (rd16(ram+obj+8)&0xe000)!=0x8000)continue;
        unsigned pose=rd24(ram+obj+10),at=pose&0x3fffff;
        if(at+29>s_rom_size || DrawActorDescriptor(ram,obj,pose)!=descriptor ||
           TlkMdSpritesRole(pose)!=TLK_MD_SPRITE_GRAVEYARD_VULTURE)continue;
        int x=(int16_t)(rd16(ram+actor+8)-rd16(ram+0xb29b));
        int y=(int16_t)(rd16(ram+actor+10)-rd16(ram+0xb29d));
        /* Expanded camera tracking and the original draw-hide test can use
         * different origins. A hidden live body can overlap the nominal
         * 256x224 rectangle while still belonging to the additional view.
         * The normal-resolution path above remains unchanged. */
        int left=(int16_t)rd16(s_rom+at+2),top=(int16_t)rd16(s_rom+at+4);
        int width=rd16(s_rom+at+6),height=rd16(s_rom+at+8);
        if(s_spawn_height<=224 && s_spawn_lead<=64 &&
           x+left<256 && x+left+width>0 && y+top<224 && y+top+height>0)continue;
        unsigned n=0;for(;n<s_frame.piece_count;n++)if(s_frame.pieces[n].obj==obj)break;
        if(n<s_frame.piece_count)continue;
        AppendKingAnimalParts(s_frame.pieces,&s_frame.piece_count,obj,pose,descriptor,
            rd16(ram+obj+8),x,y,ram[0x8c]);
    }
}
#include "tlk_ride_preview.inc"
static int BonusPickupPieceSource(const Piece *p,unsigned *source) {
    if(!p || p->kept || p->fixed || p->size!=16 ||
       !((p->actor_descriptor==0xc586b4 && p->pose==0xc52a0e) ||
         (p->actor_descriptor==0xc586c0 && p->pose==0xc529ed)))return 0;
    unsigned at=p->pose&0x3fffff;if(at+33>s_rom_size || rd16(s_rom+at)!=0x8101)return 0;
    if(p->local_x!=(int16_t)rd16(s_rom+at+29) || p->local_y!=(int16_t)rd16(s_rom+at+31))return 0;
    *source=rd24(s_rom+at+26)&0x3fffff;return *source+128<=s_rom_size;
}
static int GiraffePieceSource(const Piece *p,unsigned *source,unsigned *stride) {
    if(!p || p->kept || p->fixed || s_md_npc_frames[TLK_MD_SPRITE_CW_GIRAFFE] || ((p->attr>>9)&7)!=5 ||
       (p->actor_descriptor!=0xc58d60 && p->actor_descriptor!=0xc58d70 && p->actor_descriptor!=0xc58d80))return 0;
    unsigned pose=p->pose&0x3fffff;if(pose<0x7d93 || pose>0x7f59 || pose+29>s_rom_size)return 0;
    const uint8_t *h=s_rom+pose;unsigned flags=rd16(h),slots=flags&127;
    if(!(flags&0x8000) || !slots || slots>32)return 0;
    unsigned large=flags&0x4000?(flags>>8)&63:slots,base=rd24(h+26)&0x3fffff;
    if(large>slots)return 0;
    unsigned count=large*4;
    for(unsigned i=0;i<large;i++){
        if(pose+29+i*4+4>s_rom_size)return 0;const uint8_t *q=h+29+i*4;
        if(p->size==16 && (int16_t)rd16(q)==p->local_x && (int16_t)rd16(q+2)==p->local_y){*source=base+i*64;*stride=slots*64;return *source+*stride+64<=s_rom_size;}
    }
    if(flags&0x4000)for(unsigned i=large;count<slots*4;i++,count++){
        if(pose+29+i*4+4>s_rom_size)return 0;const uint8_t *q=h+29+i*4;if(rd16(q)==0xaaaa)break;
        if(p->size==8 && (int16_t)rd16(q)==p->local_x && (int16_t)rd16(q+2)==p->local_y){*source=base+count/4*64+(count%2)*32+(count%4/2)*slots*64;*stride=0;return *source+32<=s_rom_size;}
    }
    return 0;
}
static bool RideHiddenGiraffe(const Piece *p) {
    if(!s_ride_scene || !p || p->fixed || rd16(s_frame.ram+0xa40)<512 ||
       (p->actor_descriptor!=0xc58d60 && p->actor_descriptor!=0xc58d70 && p->actor_descriptor!=0xc58d80))return false;
    int x=(p->attr&0x4000)?p->x+p->local_x+p->size:p->x-p->local_x;
    int exit=(int)rd16(s_frame.ram+0xa56)+s_ride_map_viewport+560;
    return x+s_frame.raster_camera[0]<exit-32;
}
/* A live world1UP is hidden at the selected spare-life limit, even when it
 * existed before the last award. The native controller temporarily moves it
 * offscreen; the expanded coordinate ring can wrap that hiding offset back
 * into view. Use the owned pickup's real availability, not its shifted X.
 * Collected HUD flights and bonus rewards have different owners/actions. */
static int UnavailableWorldLifePiece(const Piece *p) {
    if(!p || p->fixed || !s_frame.stage || rd16(s_frame.ram+0x1ff9e)>9 ||
       p->actor_descriptor!=0xc58981 || !TlkWorldLifeSpritePose(p->pose) || p->obj>0xffe8)return 0;
    unsigned position=rd16(s_frame.ram+p->obj+4),actor=position>=0xb29b?position-8:0;
    if(actor<0xb293 || actor>=0xdc13 || ((actor-0xb213)&127) ||
       rd16(s_frame.ram+actor+12)!=p->obj || rd24(s_frame.ram+actor+4)!=0xc58981 ||
       rd24(s_frame.ram+actor+48)!=0xc5567e)return 0;
    unsigned lives=rd16(s_frame.ram+0x1ffaa);
    return TlkResourcesUseMd("gameplay.life_pickup_limit")?lives==9:(int16_t)lives>=8;
}
#include "tlk_sprite_palette.inc"

static unsigned SpriteRow(uint16_t *obj, int width, int column, const Line *l, const uint16_t *vram, int x,
                          int row, int size, uint16_t attr, int lo, int hi, bool cub,const Piece *owner) {
    if(UnavailableWorldLifePiece(owner))return 0;
    if(RideHiddenGiraffe(owner))return 0;
    if(owner && owner->pose==0x7eab06) {
        unsigned height=GraveyardLiquidHeight(owner);
        if(height && owner->local_y+row>=(int)height)return 0;
    }
    if(!s_caption_pass && OpeningCaptionCentre(owner))return 0;
    unsigned caption=OpeningCaptionSlot(owner);uint16_t caption_probe=0;
    if(caption && TlkResourcesUseMd("graphics.titles.remaining.frames") &&
       TlkResourcesCaptionSample(caption,0,0,0,l->cgram,&caption_probe)>=0)return 0;
    bool caption_palette=caption && TlkResourcesUseMd("graphics.titles.remaining.palette") &&
        TlkResourcesCaptionColor(caption,1,l->cgram,&caption_probe)>=0;
    if(TitlePiece(owner)) {
        uint16_t probe;
        if(TlkResourcesTitleSample(0,0,TlkResourcesUseMd("graphics.titles.pride_lands.frames"),
            TlkResourcesUseMd("graphics.titles.pride_lands.palette"),l->cgram,&probe)>=0)return 0;
    }
    int meter=HudMeter(owner);
    if ((meter>=0 && s_md_hud_frames[meter]) ||
        (s_md_hud_frames[2] && s_current_obj_slot<(unsigned)s_frame.hud_end && TlkMdHudLifeReady())) return 0;
    if (attr & 0x8000) row = size - 1 - row;
    unsigned base = (l->obsel & 7u) << 13;
    if (attr & 0x100) base += ((l->obsel & 0x18u) + 8) << 9;
    unsigned z = ((((attr >> 12) & 3u) * 4 + 2) << 12) | ((attr & 0x800) ? 4u : 6u) << 8 |
                 (0x80 + 16 * ((attr >> 9) & 7u));
    /* Bit 11 is free in the compositor's layer field. Preserve semantic
     * ownership through priority resolution, without touching guest OAM. */
    if (cub) z |= 0x800;
    unsigned role=owner && !cub && (!owner->fixed || FixedEffectPiece(owner)) ?
                  SceneNpcRole(owner,(attr>>9)&7) : 0;
    if(role==TLK_MD_SPRITE_PICKUP_POPUP && !PickupPopupPiece(owner))role=0;
    if(role==TLK_MD_SPRITE_CONTINUE_TOKEN && !ContinueTokenPiece(owner))role=0;
    unsigned bonus_source=0;int bonus_ready=!s_md_npc_frames[role] && BonusPickupPieceSource(owner,&bonus_source);
    unsigned giraffe_source=0,giraffe_stride=0;
    int giraffe_ready=GiraffePieceSource(owner,&giraffe_source,&giraffe_stride);
    unsigned ride_source=0,ride_stride=0;int ride_ready=!s_md_npc_frames[role] && RidePieceSource(owner,role,&ride_source,&ride_stride);
    unsigned king_source=0,king_stride=0;
    int king_ready=NativeAnimalPieceSource(owner,role,&king_source,&king_stride);
    if(!king_ready)king_ready=WideSpritePieceSource(owner,role,cub,&king_source,&king_stride);
    /* Extra-view actors can be submitted before their native VRAM/palette
     * transfer is eligible. This head uses the same authored palette as the
     * rhino; accept only the exact live loader palette, preserving flashes. */
    const uint16_t *giraffe_colors=NULL;
    int king_rhino_head=king_ready && owner && owner->actor_descriptor==0xc58c14 &&
        !s_md_npc_palette[TLK_MD_SPRITE_CW_RHINO] && ((attr>>9)&7)==5 &&
        s_rom_size>=0x50c1c+30 && !memcmp(l->cgram+209,s_rom+0x50c1c,30);
    if(((giraffe_ready && !s_md_npc_palette[TLK_MD_SPRITE_CW_GIRAFFE]) || king_rhino_head) && s_rom_size>=0x50b9c+30 &&
       !memcmp(l->cgram+145,s_rom+0x50b9c,30) && memcmp(l->cgram+209,s_rom+0x50b9c,30))
        giraffe_colors=l->cgram+144;
    /* The wide normal scene can submit a monkey before its native palette
     * upload, just as it can precede the glyph upload. Recover only the exact
     * initial scene bank; animation colour changes and flashes keep live CGRAM.
     * These are the original monkey palette operands, not a guessed tint. */
    unsigned king_monkey_colors=0,king_bank=(attr>>9)&7;
    if(king_ready && !s_cw_monkey_palette && (king_bank==2 || king_bank==3) &&
       s_rom_size>=0x60317+30) {
        int monkey=0;for(unsigned n=0;n<sizeof cw_monkey_descriptors/sizeof *cw_monkey_descriptors;n++)
            monkey|=owner->actor_descriptor==cw_monkey_descriptors[n];
        unsigned initial=king_bank==2?0x50bbc:0x50bdc;
        if(monkey && !memcmp(l->cgram+128+king_bank*16+1,s_rom+initial,30))
            king_monkey_colors=king_bank==2?0x602f7:0x60317;
    }
    int checkpoint=CheckpointPiece(owner);
    int checkpoint_frames=checkpoint && TlkResourcesUseMd("graphics.sprites.checkpoints.frames");
    int checkpoint_palette=checkpoint && TlkResourcesUseMd("graphics.sprites.checkpoints.palette");
    int animal_bank=CantWaitAnimalPaletteBank(owner,attr,l->cgram);
    bool flying_palette=FlyingCreaturePalette(owner,attr,l->cgram);
    bool shared_guidance=SharedGuidancePiece(owner,attr);
    bool shared_monkey_projectile=SharedMonkeyProjectile(owner,l,vram,attr);
    bool shared_arena_debris=SharedArenaDebris(owner,l,vram,attr);
    bool shared_ambient_effect=SharedAmbientEffect(owner,l,vram,attr);
    const uint16_t *ambient_effect_colors=shared_ambient_effect && s_md_npc_palette[TLK_MD_SPRITE_LATER_WORLD]?
        TlkNextSceneMdPalette(s_md_level):NULL;
    const uint16_t *arena_debris_colors=shared_arena_debris && s_md_npc_palette[TLK_MD_SPRITE_LATER_WORLD]?
        TlkNextSceneMdPalette(5):NULL;
    const uint16_t *monkey_projectile_colors=shared_monkey_projectile && s_md_npc_palette[TLK_MD_SPRITE_DESTINY_MONKEY]?
        TlkNextSceneMdPalette(6):NULL;
    int bone_palette=GraveyardBonePalette(owner,attr,l->cgram);
    int mufasa_palette=GraveyardMufasaPalette(owner,attr,l->cgram);
    unsigned pillar_pose=GraveyardPillarPose(owner,l,vram);
    unsigned pillar_role=s_md_level==7?TLK_MD_SPRITE_LATER_WORLD:TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT;
    int pillar_frames=pillar_pose && s_md_npc_frames[pillar_role];
    int pillar_palette=pillar_pose && s_md_npc_palette[pillar_role];
    const uint16_t *exit_hyena_colors=ExileExitHyenaPalette(owner,attr,l->cgram);
    const uint16_t *wildebeest_colors=StampedeWildebeestPalette(owner,(attr>>9)&7,l->cgram);
    const uint16_t *stampede_death_colors=StampedeCubDeathPalette(owner,(attr>>9)&7,l->cgram);
    unsigned splash_pose=PreparedSplashPose(owner,l->cgram);
    int splash_palette=splash_pose && TlkResourcesUseMd("graphics.sprites.simba.adult.palette");
    unsigned drawn = 0;
    TlkFallbackSpriteInfo *diagnostic=SpriteDiagnostic(owner,l,vram,width,x+column,attr,role,cub);
    if(diagnostic && caption) {
        diagnostic->frames_md=TlkResourcesUseMd("graphics.titles.remaining.frames");
        diagnostic->palette_md=TlkResourcesUseMd("graphics.titles.remaining.palette");
    }
    if(s_fallback_enabled)TlkFallbackSpriteContext(diagnostic);
    for (int c = 0; c < size; c++) {
        int sx = x + c, dest = sx + column;
        if (sx < lo || sx >= hi || dest < 0 || dest >= width) continue;
        int uc = (attr & 0x4000) ? size - 1 - c : c;
        unsigned t = ((((attr & 0xFFu) >> 4) + ((unsigned)row >> 3)) << 4) | (((attr & 0xFu) + ((unsigned)uc >> 3)) & 0xF);
        unsigned pixel = TilePixel(vram, base + t * 16, (unsigned)uc & 7, (unsigned)row & 7, 4);
        if(bonus_ready){
            unsigned at=bonus_source+((unsigned)uc>>3)*32+((unsigned)row>>3)*64+((unsigned)row&7)*2;
            unsigned bit=7-((unsigned)uc&7);const uint8_t *q=s_rom+at;
            pixel=((q[0]>>bit)&1)|((q[1]>>bit)&1)<<1|((q[16]>>bit)&1)<<2|((q[17]>>bit)&1)<<3;
        }
        if(giraffe_ready){
            unsigned at=giraffe_source+((unsigned)uc>>3)*32+((unsigned)row>>3)*giraffe_stride+((unsigned)row&7)*2;
            unsigned bit=7-((unsigned)uc&7);const uint8_t *q=s_rom+at;
            pixel=((q[0]>>bit)&1)|((q[1]>>bit)&1)<<1|((q[16]>>bit)&1)<<2|((q[17]>>bit)&1)<<3;
        }
        if(ride_ready){
            unsigned at=ride_source+((unsigned)uc>>3)*32+((unsigned)row>>3)*ride_stride+((unsigned)row&7)*2;
            unsigned bit=7-((unsigned)uc&7);int a=CapturedByte(at),b=CapturedByte(at+1),c=CapturedByte(at+16),d=CapturedByte(at+17);
            if(a>=0&&b>=0&&c>=0&&d>=0)pixel=((a>>bit)&1)|((b>>bit)&1)<<1|((c>>bit)&1)<<2|((d>>bit)&1)<<3;
        }
        if(king_ready){
            unsigned at=king_source+((unsigned)uc>>3)*32+((unsigned)row>>3)*king_stride+((unsigned)row&7)*2;
            unsigned bit=7-((unsigned)uc&7);int a=CapturedByte(at),b=CapturedByte(at+1),c=CapturedByte(at+16),d=CapturedByte(at+17);
            if(a>=0&&b>=0&&c>=0&&d>=0)pixel=((a>>bit)&1)|((b>>bit)&1)<<1|((c>>bit)&1)<<2|((d>>bit)&1)<<3;
        }
        uint16_t npc_color=giraffe_colors && pixel?giraffe_colors[pixel]:0xffff;
        if(king_monkey_colors && pixel)npc_color=rd16(s_rom+king_monkey_colors+(pixel-1)*2);

        /* These strict metadata/owner/palette guards identify drawings whose
         * original MD and SNES anchored indices are equal. Native storage of
         * a proven shared drawing is not a source fallback. */
        int diagnostic_frame_adapted=caption_palette || animal_bank>=0 || flying_palette || shared_guidance || mufasa_palette || shared_monkey_projectile || shared_arena_debris || shared_ambient_effect ||
            (bone_palette && owner && (owner->pose==0xc110fa || GraveyardSharedJaw(owner)));
        if(pixel && wildebeest_colors)npc_color=wildebeest_colors[next_wildebeest_colors[pixel&15]];
        if(pixel && stampede_death_colors)npc_color=stampede_death_colors[pixel&15];
        if(splash_pose) {
            if(s_md_cub_frames){pixel=0;diagnostic_frame_adapted=1;}
            else if(pixel && splash_palette)npc_color=PreparedSplashColor(pixel,0,1,l->cgram);
        }
        if(pixel && animal_bank>=0)
            npc_color=TlkMdColor555(s_cant_wait.colors[animal_bank*16+pixel]);
        if(pixel && flying_palette)
            npc_color=TlkResourcesSharedObjColor(128+pixel,l->cgram,l->cgram[128+pixel]);
        if(pixel && shared_guidance)
            npc_color=TlkResourcesHudColor(128+pixel,l->cgram,l->cgram[128+pixel]);
        if(pixel && monkey_projectile_colors)npc_color=monkey_projectile_colors[pixel];
        if(pixel && arena_debris_colors)npc_color=arena_debris_colors[16+pixel];
        if(pixel && ambient_effect_colors)npc_color=ambient_effect_colors[pixel];
        if(pixel && bone_palette)npc_color=s_graveyard_bone_colors[graveyard_bone_to_md[pixel]];
        if(pixel>=8 && mufasa_palette)npc_color=s_graveyard_mufasa_colors[pixel];
        if(pillar_pose && (pillar_frames || pillar_palette)) {
            uint16_t color=0;
            int adapted=GraveyardPillarSample(pillar_pose,0,0,pixel?pixel:1,0,pillar_palette,l->cgram,&color);
            if(adapted>=0) {
                if(pillar_frames){pixel=0;diagnostic_frame_adapted=1;}
                else if(pixel && adapted)npc_color=color;
            }
        }
        if(pixel && exit_hyena_colors)npc_color=exit_hyena_colors[pixel];
        int hud=(s_hud_pass || (owner && owner->fixed) || s_current_obj_slot<(unsigned)s_frame.hud_end) &&
                !FixedEffectPiece(owner);
        if (pixel && hud && (s_frame.stage || StampedeScene()) && TlkResourcesUseMd("graphics.hud.palette")) {
            unsigned color_index=0x80+16*((attr>>9)&7)+pixel;
            npc_color=SceneHudColor(color_index,l->cgram,l->cgram[color_index]);
        }
        if(pixel && caption_palette)TlkResourcesCaptionColor(caption,pixel,l->cgram,&npc_color);
        if (role && (s_md_npc_frames[role] || s_md_npc_palette[role])) {
            uint16_t color=0;
            int adapted=SceneNpcSample(owner,0,0,pixel,0,s_md_npc_palette[role],l->cgram,&color);
            if (adapted>=0) {
                /* Complete MD actors are drawn once below, including pixels
                 * outside the original SNES piece rectangles. */
                if (s_md_npc_frames[role]) pixel=0;
                else if (adapted) npc_color=color;
            }
        }
        if (cub && owner && !splash_pose && (s_cub_death_frame || s_md_cub_frames)) {
            int external=-1;
            if(s_cub_death_frame && TlkMdSpritesCubDeathPose(owner->pose))
                external=TlkMdSpritesCubDeathPixel(owner->pose,owner->local_x+uc,owner->local_y+row,s_md_cub_frames!=0);
            else if(s_md_cub_frames && !TlkMdSpritesCubDeathPose(owner->pose))
                external=TlkMdSpritesPixel(owner->pose,owner->local_x+uc,owner->local_y+row);
            if (external>=0) {pixel=(unsigned)external;diagnostic_frame_adapted=1;}
        }
        if(checkpoint_frames || checkpoint_palette) {
            uint16_t color=0;
            int adapted=TlkResourcesCheckpointSample(owner->pose,owner->local_x+uc,owner->local_y+row,
                checkpoint_frames,checkpoint_palette,l->cgram,&color);
            if(adapted>=0) {
                if(checkpoint_frames)diagnostic_frame_adapted=1;
                if(adapted) { pixel=1;npc_color=color;s_stats.checkpoint_pixels++; }
                else pixel=0;
            } else if(pixel)s_stats.checkpoint_fallback_pixels++;
        }
        /* A moved native HUD object still obeys its original OAM priority.
         * The HUD pass runs after world sprites, so unconditional writes here
         * would incorrectly cover earlier caption/world objects. */
        if (pixel && (!s_hud_pass || s_current_obj_slot<=s_obj_slot[dest])) {
            obj[dest] = (uint16_t)(z | pixel);s_obj_slot[dest]=(uint8_t)s_current_obj_slot;s_obj_palette[dest]=SpritePaletteToken(owner);s_npc_color[dest]=npc_color;drawn++;
            if(s_fallback_enabled) {
                int expected=cub?s_md_cub_frames:
                    role?s_md_npc_frames[role]:s_fallback_all_sprites && !hud;
                s_fallback_piece[dest]=owner;
                s_fallback_reason[dest]=expected && !diagnostic_frame_adapted && (!role || npc_color==0xffff)?
                    cub?"simba_frame_unavailable":role?"sprite_sample_rejected":
                    owner?"unclassified_native_sprite":"unowned_native_oam":NULL;
            }
        }
    }
    if(s_fallback_enabled)TlkFallbackSpriteContext(NULL);
    return drawn;
}

static int OamX(const Line *l, unsigned index) {
    int x = (l->oam[index] & 0xFF) | ((l->hoam[index >> 3] >> (index & 7)) & 1) << 8;
    return x >= 256 ? x - 512 : x;
}
static int OamSize(const Line *l, unsigned index) {
    return kSpriteSizes[l->obsel >> 5][(l->hoam[index >> 3] >> ((index & 7) + 1)) & 1];
}

/* The PPU's sprites for one line (ppu_evaluateSprites: 32 in range, 34 slivers
 * fetched backwards), inside the native columns. Slots marked in skip (HUD
 * moved to the edges) are counted but left for the caller to place. */
static void NativeSprites(uint16_t *obj, int width, int column, const Line *l, const uint16_t *vram, int y0,
                          const bool *skip) {
    bool cub_slot[128] = {false};
    const Piece *owners[128]={0};
    for (unsigned n = 0; n < s_frame.piece_count; n++) {
        const Piece *p = &s_frame.pieces[n];
        if (p->kept) {
            unsigned slot=p->slot&127,idx=slot*2;
            if(CheckpointPiece(p) && (p->x!=OamX(l,idx) || (p->y&255)!=(l->oam[idx]>>8) ||
                p->size!=OamSize(l,idx) || p->attr!=l->oam[idx+1])) {
                s_stats.checkpoint_stale_pieces++;continue;
            }
            cub_slot[slot]=CubPiece(p);owners[slot]=p;
        }
    }
    uint8_t found[32];
    int count = 0, tiles = 0;
    uint8_t index = (l->oamaddh & 0x80) ? (l->oamaddl & 0xFE) : 0;
    for (int i = 0; i < 128; i++, index += 2) {
        int dx,dy;GiraffeSceneryShift(owners[index>>1],&dx,&dy);
        uint8_t row = (uint8_t)(y0 - (l->oam[index] >> 8)-dy);
        int size = OamSize(l, index);
        if (row >= size || OamX(l, index) + size <= 0) continue;
        if (count == 32) break;
        found[count++] = index;
    }
    for (int i = count; i > 0; i--) {
        unsigned idx = found[i - 1];
        int dx,dy;GiraffeSceneryShift(owners[idx>>1],&dx,&dy);
        int size = OamSize(l, idx), x = OamX(l, idx)+dx;
        int row = (uint8_t)(y0 - (l->oam[idx] >> 8)-dy);
        uint16_t attr = l->oam[idx + 1];
        s_current_obj_slot=idx>>1;
        for (int col = 0; col < size; col += 8) {
            if (col + x <= -8 || col + x >= 256) continue;
            if (++tiles > 34) break;
            if (skip[idx >> 1] || DestinySkyFacePiece(owners[idx>>1])) continue;
            int lo = col + x < 0 ? 0 : col + x, hi = col + x + 8 > 256 ? 256 : col + x + 8;
            /* One sliver: draw the whole sprite row clipped to it. */
            SpriteRow(obj, width, column, l, vram, x, row, size, attr, lo, hi, cub_slot[idx >> 1],owners[idx>>1]);
        }
        if (tiles > 34) break;
    }
}

static bool Window(const Line *l, unsigned layer, int x, int column, int width) {
    unsigned f = (l->windowsel >> (layer * 4)) & 15;
    int w1l = l->w1l, w1r = l->w1r, w2l = l->w2l, w2r = l->w2r;
    /* A hardware edge pinned to 0/255 means the screen edge (ppu.c). */
    if (w1l == 0) w1l = -column;
    if (w1r == 255) w1r = width - 1 - column;
    if (w2l == 0) w2l = -column;
    if (w2r == 255) w2r = width - 1 - column;
    bool a = (f & 2) && w1l <= w1r && x >= w1l && x <= w1r;
    bool b = (f & 8) && w2l <= w2r && x >= w2l && x <= w2r;
    if ((f & 3) == 3) a = !a;
    if ((f & 12) == 12) b = !b;
    if ((f & 10) != 10) return a || b;
    switch ((l->wlog >> (layer * 2)) & 3) {
    case 0: return a || b;
    case 1: return a && b;
    case 2: return a != b;
    default: return a == b;
    }
}

/* Whether the level map and the native tilemap agree at native column x of
 * this line. After a warp (the ostrich ride jumps back 432 pixels) the map
 * behind the camera no longer shows what is on screen. */
static bool SeamAgrees(const Line *l, const uint16_t *vram, int y0, int ox, int oy, int x) {
    int wx = ox + x, wy = oy;
    uint16_t word;
    if (!MapTile(&s_frame.level, &wx, &wy, &word)) return false;
    return word == VramTilemap(vram, l->bgsc[0], ((unsigned)x + l->hofs[0]) & 1023,
                               ((unsigned)y0 + 1 + l->vofs[0]) & 1023, 8);
}

static bool s_hud_skip[128];   /* OAM slots the HUD pass places itself */
static int8_t s_hud_side[128];  /* where it places them, as Piece.side (64ths of the way to an edge) */
static bool s_hud_edges;
static bool s_map_left, s_map_right;   /* margins from the level map this frame, per side */
static int s_vis_lo, s_vis_hi;         /* view columns inside the camera's range */

/* How far the HUD pass moves a HUD sprite, in screen pixels: from where it
 * sits in a centred native picture, side 64ths of the margin towards an edge. */
static int HudShift(int side, int width, int column) {
    int extra = (width - 256) / 2;
    return extra + extra * side / 64 - column;
}

/* A DMA overrun can leave the top native scanline forced blank. Extending
 * that scanline into a tall window magnifies it into a large black band.
 * Use the nearest completed world line for presentation only. If every line
 * is dark (a real fade/transition), retain the original line and its darkness. */
static const Line *WorldPresentationLine(int y) {
    const Line *l=&s_frame.lines[y];
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    unsigned scene=rd24(s_frame.ram+0xdf);
    int isolated_blank=(level==2 && scene==0xc003eb) ||
                       (level==5 && scene==0xc00481) ||
                       (level==6 && scene==0xc004b3) ||
                       (level==7 && scene==0xc004e5);
    if(!(s_area_active && s_frame.stage && (level<=1 || isolated_blank)))return l;
    /* Streaming and hurt-animation uploads in these initialized worlds can
     * overrun the first few native
     * scanlines. Do not magnify those transient forced blanks into a whole
     * tall-view band. Ordinary dark rows and fully blank fades keep their
     * captured state; only an isolated forced blank borrows a completed row. */
    if(isolated_blank && !(l->inidisp&128))return l;
    if(!(l->inidisp&128) && (l->inidisp&15) && (l->tm&1) && LineHasStage(l))return l;
    for(int distance=1;distance<224;distance++){
        int candidates[2]={y-distance,y+distance};
        for(int i=0;i<2;i++)if(candidates[i]>=0 && candidates[i]<224){
            const Line *p=&s_frame.lines[candidates[i]];
            if(!(p->inidisp&128) && (p->inidisp&15) && (p->tm&1) && LineHasStage(p))return p;
        }
    }
    return l;
}
static void ComposeLine(uint32_t *out, int width, int column, int y0) {
    s_handoff_width=width;
    int source_line=y0<0?0:y0>=224?223:y0;
    const Line *l=WorldPresentationLine(source_line);
    const uint16_t *vram = s_vram[l->vram];
    if (l->inidisp & 0x80) { memset(out, 0, (size_t)width * 4); return; }
    s_md_level=rd16(s_frame.ram+0x1FF9E);
    unsigned descriptor=rd16(s_frame.ram+0xdf);
    int pride=s_md_level==0 && (descriptor==0x387 || descriptor==0x80d);
    int graveyard=s_frame.stage && s_md_level==2 && descriptor==0x3eb;
    int stampede=StampedeScene(),exile=ExileScene();
    int hakuna=s_frame.stage && s_md_level==5 && descriptor==0x481;
    int destiny=s_frame.stage && s_md_level==6 && descriptor==0x4b3;
    int be_prepared=s_frame.stage && s_md_level==7 && descriptor==0x4e5;
    int simbas_return=s_frame.stage && s_md_level==8 && descriptor==0x517;
    int pride_rock=s_frame.stage && s_md_level==9 && descriptor==0x549;
    int summit=s_frame.stage && s_md_level==9 && descriptor==0x7db;
    int bonus=s_frame.stage && BonusScene();
    TlkMdSceneAnimationPhase(5,s_scene_animation.active==5?s_scene_animation.phase:0);
    int postfight_scene=summit && TlkNextScenePrideRockRainTarget()!=NULL;
    if(pride_rock || postfight_scene){
        unsigned phase=s_scene_animation.phase;uint16_t rain[64];
        const uint16_t *colors=TlkNextScenePrideRockPhase(phase);
        if(PrideRockRainPhase(phase) && TlkNextScenePrideRockRainColors((phase>>4)&3,phase&7,rain))colors=rain;
        TlkMdScenePreparedPalette(9,colors);
    }
    int stampede_palette=stampede && TlkResourcesUseMd("graphics.scenery.stampede_palette");
    /* The existing native Stampede scheduler clock is reset at scene setup,
     * advances with C0FA58, and is already saved with WRAM. It stops with the
     * game's update loop, so repeated presentation, pause and load cannot
     * advance the prepared canyon independently of gameplay. */
    const uint8_t *stampede_background=stampede && TlkResourcesUseMd("graphics.scenery.background")?
        TlkNextSceneStampedeFrame((rd16(s_frame.ram+0xa40)/5)%3):NULL;
    s_stampede_cub_death_palette=stampede && TlkResourcesUseMd("graphics.sprites.simba.cub.palette");
    s_stampede_wildebeest_palette=stampede && TlkResourcesUseMd("graphics.sprites.stampede.wildebeests.palette");
    TlkMdSpritesNextScene(stampede?3:exile?4:hakuna?5:destiny?6:be_prepared?7:simbas_return?8:pride_rock || summit?9:bonus?s_md_level:0);
    uint16_t scene_colors[64];
    int graveyard_colors=graveyard && TlkMdScenePaletteColors(2,scene_colors);
    TlkMdSpritesGraveyardPalette(graveyard_colors?scene_colors:NULL);
    s_graveyard_bone_palette=graveyard_colors && TlkResourcesUseMd("graphics.sprites.bones.palette");
    if(s_graveyard_bone_palette)memcpy(s_graveyard_bone_colors,scene_colors+32,sizeof s_graveyard_bone_colors);
    s_md_npc_frames[TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT]=graveyard && TlkResourcesUseMd("graphics.sprites.bones.frames");
    s_md_npc_palette[TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT]=graveyard && TlkResourcesUseMd("graphics.sprites.bones.palette");
    s_exile_exit_hyena_palette=exile && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.palette");
    s_graveyard_mufasa_palette=graveyard && TlkResourcesUseMd("graphics.sprites.mufasa.palette") && TlkGraveyardFarewellPalette(s_graveyard_mufasa_colors+8);
    if(s_graveyard_mufasa_palette)for(unsigned i=8;i<16;i++)s_graveyard_mufasa_colors[i]=TlkMdColor555(s_graveyard_mufasa_colors[i]);
    /* The next two main stages use the same ROM-backed cub pose records.
     * Match the actual descriptor as well as the level variable: titles,
     * bonuses and retained level words must not activate a scene adapter.
     * Per-pose lookup still leaves unknown art on the original SNES path. */
    int adult=(destiny || be_prepared || simbas_return || pride_rock || summit) && rd16(s_frame.ram+0x2000)==0xffff;
    s_md_cub_frames=((s_frame.stage || s_cub_death_frame) && TlkMdSpritesCubScene(s_md_level,descriptor) &&
                    TlkResourcesUseMd("graphics.sprites.simba.cub.frames")) ||
                   (adult && TlkResourcesUseMd("graphics.sprites.simba.adult.frames"));
    s_md_npc_frames[1]=(pride || graveyard) && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.frames");
    s_md_npc_palette[1]=(pride || graveyard) && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.palette");
    s_md_npc_frames[TLK_MD_SPRITE_GRAVEYARD_VULTURE]=graveyard && TlkResourcesUseMd("graphics.sprites.enemies.vultures.frames");
    s_md_npc_palette[TLK_MD_SPRITE_GRAVEYARD_VULTURE]=graveyard && TlkResourcesUseMd("graphics.sprites.enemies.vultures.palette");
    s_md_npc_frames[TLK_MD_SPRITE_LIZARD]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.enemies.chameleons.frames");
    s_md_npc_palette[TLK_MD_SPRITE_LIZARD]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.enemies.chameleons.palette");
    s_md_npc_frames[kPorcupineArtRole]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.enemies.porcupines.frames");
    s_md_npc_palette[kPorcupineArtRole]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.enemies.porcupines.palette");
    s_md_npc_frames[TLK_MD_SPRITE_PORCUPINE]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.enemies.other.frames");
    s_md_npc_palette[TLK_MD_SPRITE_PORCUPINE]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.enemies.other.palette");
    s_md_npc_frames[TLK_MD_SPRITE_STAMPEDE_CUB]=stampede && TlkResourcesUseMd("graphics.sprites.simba.cub.frames");
    s_md_npc_palette[TLK_MD_SPRITE_STAMPEDE_CUB]=stampede && TlkResourcesUseMd("graphics.sprites.simba.cub.palette");
    s_md_npc_frames[TLK_MD_SPRITE_STAMPEDE_ROCK]=stampede && TlkResourcesUseMd("graphics.sprites.stampede.rocks.frames");
    s_md_npc_palette[TLK_MD_SPRITE_STAMPEDE_ROCK]=stampede && TlkResourcesUseMd("graphics.sprites.stampede.rocks.palette");
    s_md_npc_frames[TLK_MD_SPRITE_COCONUT]=hakuna && TlkResourcesUseMd("graphics.sprites.enemies.gorilla.coconuts.frames");
    s_md_npc_palette[TLK_MD_SPRITE_COCONUT]=hakuna && TlkResourcesUseMd("graphics.sprites.enemies.gorilla.coconuts.palette");
    s_md_npc_frames[TLK_MD_SPRITE_GORILLA]=hakuna && TlkResourcesUseMd("graphics.sprites.enemies.gorilla.frames");
    s_md_npc_palette[TLK_MD_SPRITE_GORILLA]=hakuna && TlkResourcesUseMd("graphics.sprites.enemies.gorilla.palette");
    s_md_npc_frames[4]=(pride || s_cw_scene || graveyard || exile || hakuna || destiny || be_prepared || simbas_return || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.pickups.frames");
    s_md_npc_palette[4]=(pride || s_cw_scene || graveyard || exile || hakuna || destiny || be_prepared || simbas_return || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.pickups.palette");
    s_md_npc_frames[TLK_MD_SPRITE_LEAVES]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.leaves.frames");
    s_md_npc_palette[TLK_MD_SPRITE_LEAVES]=(pride || exile) && TlkResourcesUseMd("graphics.sprites.leaves.palette");
    s_md_npc_frames[TLK_MD_SPRITE_DEFEAT_PUFF]=(pride || hakuna) && TlkResourcesUseMd("graphics.sprites.effects.defeat_puff.frames");
    s_md_npc_palette[TLK_MD_SPRITE_DEFEAT_PUFF]=(pride || hakuna) && TlkResourcesUseMd("graphics.sprites.effects.defeat_puff.palette");
    s_md_npc_frames[TLK_MD_SPRITE_LATER_ENEMY]=(hakuna || destiny || be_prepared) && TlkResourcesUseMd("graphics.sprites.enemies.other.frames");
    s_md_npc_palette[TLK_MD_SPRITE_LATER_ENEMY]=(hakuna || destiny || be_prepared) && TlkResourcesUseMd("graphics.sprites.enemies.other.palette");
    s_md_npc_frames[TLK_MD_SPRITE_LATER_WORLD]=(exile || hakuna || destiny || be_prepared || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.world_objects.frames");
    s_md_npc_palette[TLK_MD_SPRITE_LATER_WORLD]=(exile || hakuna || destiny || be_prepared || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.world_objects.palette");
    s_md_npc_frames[TLK_MD_SPRITE_LATER_EFFECT]=destiny && TlkResourcesUseMd("graphics.sprites.effects.defeat_puff.frames");
    s_md_npc_palette[TLK_MD_SPRITE_LATER_EFFECT]=destiny && TlkResourcesUseMd("graphics.sprites.effects.defeat_puff.palette");
    s_md_npc_frames[kAdultCheckpointRole]=adult && TlkResourcesUseMd("graphics.sprites.checkpoints.frames");
    s_md_npc_palette[kAdultCheckpointRole]=adult && TlkResourcesUseMd("graphics.sprites.checkpoints.palette");
    s_md_npc_frames[TLK_MD_SPRITE_LATER_PICKUP]=s_md_npc_frames[TLK_MD_SPRITE_PICKUP];
    s_md_npc_palette[TLK_MD_SPRITE_LATER_PICKUP]=s_md_npc_palette[TLK_MD_SPRITE_PICKUP];
    s_md_npc_frames[TLK_MD_SPRITE_ADULT_HYENA]=(be_prepared || simbas_return || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.adult.frames");
    s_md_npc_palette[TLK_MD_SPRITE_ADULT_HYENA]=(be_prepared || simbas_return || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.adult.palette");
    s_md_npc_frames[TLK_MD_SPRITE_DESTINY_MONKEY]=destiny && TlkResourcesUseMd("graphics.sprites.animals.monkeys.frames");
    s_md_npc_palette[TLK_MD_SPRITE_DESTINY_MONKEY]=destiny && TlkResourcesUseMd("graphics.sprites.animals.monkeys.palette");
    s_md_npc_frames[TLK_MD_SPRITE_PICKUP_POPUP]=pride && TlkResourcesUseMd("graphics.sprites.effects.pickup_arrival.frames");
    s_md_npc_palette[TLK_MD_SPRITE_PICKUP_POPUP]=pride && TlkResourcesUseMd("graphics.sprites.effects.pickup_arrival.palette");
    s_md_npc_frames[TLK_MD_SPRITE_CONTINUE_TOKEN]=s_frame.stage && TlkResourcesUseMd("graphics.sprites.pickups.continue_token.frames");
    s_md_npc_palette[TLK_MD_SPRITE_CONTINUE_TOKEN]=s_frame.stage && TlkResourcesUseMd("graphics.sprites.pickups.continue_token.palette");
    s_md_npc_frames[TLK_MD_SPRITE_SCAR]=(pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.scar.frames");
    s_md_npc_palette[TLK_MD_SPRITE_SCAR]=(pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.scar.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_PUMBAA]=bonus && s_md_level==10 && TlkResourcesUseMd("graphics.sprites.bonus.pumbaa.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_PUMBAA]=bonus && s_md_level==10 && TlkResourcesUseMd("graphics.sprites.bonus.pumbaa.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_TIMON]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.timon.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_TIMON]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.timon.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_BUG]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.bugs.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_BUG]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.bugs.palette");
    for (unsigned kind=0;kind<3;kind++)
        s_md_hud_frames[kind]=(s_frame.stage || stampede) && (pride || (s_md_level==1 && descriptor==0x3b9) || (s_md_level==2 && descriptor==0x3eb) || stampede || exile || hakuna || destiny || be_prepared || simbas_return || pride_rock || summit) && TlkResourcesHudFramesMd(kind) &&
                             TlkMdHudReady() && (TlkResourcesSharedPaletteMatches(l->cgram) || (stampede && StampedeHudPalette(l->cgram)));
    /* Original postfight retains both world planes and line scrolling.
     * Its separately prepared rain target is required before claiming it. */
    int md_scene=s_frame.stage && (s_md_level<=8 || pride_rock || postfight_scene || bonus) && TlkMdSceneReady(s_md_level) && (s_md_level!=0 || pride);
    s_cw_scene=s_frame.stage && s_md_level==1 && descriptor==0x3b9 && s_cant_wait.active;
    s_cw_monkey_palette=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.monkeys.palette");
    s_cw_ostrich_palette=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.ostriches.palette");
    s_cw_tail_palette=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.rhinos.tail.palette");
    s_flying_creature_palette=s_frame.stage && TlkResourcesUseMd("graphics.sprites.animals.flying_creatures.palette");
    s_md_npc_frames[TLK_MD_SPRITE_CW_RHINO]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.rhinos.frames");
    s_md_npc_palette[TLK_MD_SPRITE_CW_RHINO]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.rhinos.palette");
    s_md_npc_frames[TLK_MD_SPRITE_CW_HIPPO]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.hippos.frames");
    s_md_npc_palette[TLK_MD_SPRITE_CW_HIPPO]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.hippos.palette");
    s_md_npc_frames[TLK_MD_SPRITE_CW_RIDE_OBSTACLE]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.world_objects.ride_obstacles.frames");
    s_md_npc_palette[TLK_MD_SPRITE_CW_RIDE_OBSTACLE]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.world_objects.ride_obstacles.palette");
    s_md_npc_frames[TLK_MD_SPRITE_CW_GIRAFFE]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.giraffes.frames");
    s_md_npc_palette[TLK_MD_SPRITE_CW_GIRAFFE]=s_cw_scene && TlkResourcesUseMd("graphics.sprites.animals.giraffes.palette");
    if(s_cw_scene)TlkMdSpritesCantWaitPalette(s_cant_wait.colors);
    s_md_foreground=md_scene && TlkResourcesUseMd("graphics.scenery.foreground");
    unsigned layout_width=0,layout_height=0;
    s_md_layout_y=0;
    s_md_layout=s_md_foreground &&
        ((s_cw_scene && TlkResourcesUseMd("gameplay.levels.cant_wait.terrain")) ||
         (exile && TlkResourcesUseMd("gameplay.levels.simbas_exile.terrain")) ||
         (hakuna && TlkResourcesUseMd("gameplay.levels.hakuna_matata.terrain")) ||
         (destiny && TlkResourcesUseMd("gameplay.levels.simbas_destiny.terrain")) ||
         (simbas_return && TlkResourcesUseMd("gameplay.levels.simbas_return.terrain")) ||
         (be_prepared && TlkResourcesUseMd("gameplay.levels.be_prepared.terrain")) ||
         (pride_rock && TlkResourcesUseMd("gameplay.levels.pride_rock.terrain"))) &&
        TlkMdSceneSize(s_md_level,&layout_width,&layout_height) &&
        layout_width==s_frame.level.rowb*8 && layout_height==s_frame.level.rows*16;
    s_native_md_layout=!s_md_foreground &&
        ((be_prepared && TlkResourcesUseMd("gameplay.levels.be_prepared.terrain")) ||
         (hakuna && TlkResourcesUseMd("gameplay.levels.hakuna_matata.terrain")) ||
         (destiny && TlkResourcesUseMd("gameplay.levels.simbas_destiny.terrain")) ||
         (simbas_return && TlkResourcesUseMd("gameplay.levels.simbas_return.terrain"))) &&
        TlkMdSceneSize(s_md_level,&layout_width,&layout_height) &&
        layout_width==s_frame.level.rowb*8 && layout_height==s_frame.level.rows*16;
    /* Hunt's contact/floor grids are identical after removing the extra MD
     * top row. Render the original complete map in that prepared coordinate
     * system; partial native-cell matches can splice holes into the branch. */
    if(s_md_foreground && bonus && s_md_level>=11 &&
       TlkHuntDataOrigin(s_md_level,&s_md_layout_y) &&
       TlkMdSceneSize(s_md_level,&layout_width,&layout_height) &&
       layout_width==s_frame.level.rowb*8 && layout_height==s_frame.level.rows*16+s_md_layout_y)
        s_md_layout=1;
    s_md_background=md_scene && (pride || graveyard || exile || hakuna || destiny || be_prepared || simbas_return || pride_rock || postfight_scene || bonus) && TlkMdSceneBackgroundReady(s_md_level) && TlkResourcesUseMd("graphics.scenery.background");
    if(s_cw_scene)s_md_background=TlkResourcesUseMd("graphics.scenery.background");
    s_native_pride_bg_edges=pride && !s_md_background;
    /* These two scenes own a finite512-wide BG2 panorama. Tall windows show
     * every authored row instead of a224-row slice clipped by camera vofs.
     * Nearest-row fitting changes scenery only; foreground and actors retain
     * their pixel dimensions and original gameplay coordinates. */
    const char *motion_id=s_md_level==1?"graphics.scenery.snes_motion.king":s_md_level==5?"graphics.scenery.snes_motion.hakuna":s_md_level==8?"graphics.scenery.snes_motion.return":s_md_level==9?"graphics.scenery.snes_motion.pride_rock":NULL;
    s_native_background_motion=!s_md_background && motion_id && (s_cw_scene || hakuna || simbas_return || pride_rock || postfight_scene) && TlkResourcesUseMd(motion_id);
    s_native_firelight=(pride_rock || postfight_scene) && !TlkResourcesUseMd("graphics.scenery.foreground.palette") && TlkResourcesUseMd("graphics.scenery.firelight");
    int background_y=y0;
    const Line *background_line=l;
    Line panorama;
    /* These scenes' complete native BG2 composition is a finite 224-row
     * band schedule. Fit that picture to a tall view; choose each source
     * row's own scroll/palette rather than extending its last band below it. */
    int native_panorama=(pride || s_cw_scene || (bonus && HuntScene())) && !s_md_background &&
        s_md_level<14 && s_native_panorama_height[s_md_level];
    int fitted_bands=s_area_active && s_area_height>224 && !native_panorama;
    if(fitted_bands){
        background_y=(y0+s_area_top)*224/s_area_height;
        if(background_y<0)background_y=0;if(background_y>223)background_y=223;
        background_line=WorldPresentationLine(background_y);
    }
    int anchor_pride=s_area_active && s_area_height>224 &&
        (pride || (s_md_level==1 && s_frame.stage && rd24(s_frame.ram+0xdf)==0xc003b9) || (bonus && HuntScene())) && !s_md_background && s_native_panorama_height[s_md_level];
    if(anchor_pride){
        int view_y=y0+s_area_top;
        int panorama_height=(int)s_native_panorama_height[s_md_level];
        background_y=view_y*panorama_height/s_area_height;
        if(background_y<0)background_y=0;if(background_y>=panorama_height)background_y=panorama_height-1;
        int palette_y=view_y*224/s_area_height;
        if(palette_y<0)palette_y=0;if(palette_y>223)palette_y=223;
        panorama=*WorldPresentationLine(palette_y);panorama.vofs[1]=1023;
        background_line=&panorama;
        PreparePanorama(background_line,s_md_level);
        if(!s_area_sky_edge_valid){
            uint16_t values[256];static uint16_t counts[65536];unsigned best=0;
            Line edge=*background_line;edge.hofs[1]=0;edge.vofs[1]=1023;
            for(int sx=0;sx<256;sx++){values[sx]=BgPixel(&edge,s_vram[edge.vram],1,sx,0,false,0,0,column,width);counts[values[sx]]=0;}
            for(int sx=0;sx<256;sx++)counts[values[sx]]++;
            for(int sx=0;sx<256;sx++)if(counts[values[sx]]>best){best=counts[values[sx]];s_area_sky_color=values[sx];}
            s_area_sky_color=StableEdge(0,s_area_sky_color);s_area_sky_edge_valid=1;
        }
    }
    s_scenery_palette[0]=TlkResourcesUseMd("graphics.scenery.foreground.palette");
    Line moving_background,moving_source;
    if(s_native_background_motion){
        moving_background=*background_line;
        int row=background_y;if(row<0)row=0;if(row>223)row=223;
        moving_background.hofs[1]=(uint16_t)NativeMotionOffset(s_md_level,s_md_level==1?s_cant_wait.camera:s_bg_camera[0],row);
        background_line=&moving_background;moving_source=*l;moving_source.hofs[1]=moving_background.hofs[1];l=&moving_source;
    }
    s_scenery_palette[1]=TlkResourcesUseMd("graphics.scenery.background.palette");
    int md_palette=md_scene && s_scenery_palette[0];
    if (md_scene) TlkMdScenePalette(s_md_level,l->cgram,md_palette);
    if(s_cw_scene)CantWaitPalette(l->cgram);

    uint16_t obj[TLK_WIDE_MAX_WIDTH];
    memset(obj, 0, (size_t)width * sizeof obj[0]);
    memset(s_obj_slot,255,(size_t)width);
    memset(s_obj_palette,0,(size_t)width*sizeof *s_obj_palette);
    if(s_fallback_enabled)memset(s_fallback_reason,0,(size_t)width*sizeof *s_fallback_reason);
    memset(s_npc_color,255,(size_t)width*sizeof s_npc_color[0]);
    DrawRidePreviewRow(obj,width,column,y0,l);
    if (!GraveyardDeathSelected() && (l->tm & 0x10 || l->ts & 0x10)) {
        if(y0>=0&&y0<224)NativeSprites(obj, width, column, l, vram, y0, s_hud_skip);
        /* Margins: every piece the game submitted, last first (OAM order).
         * Screen-fixed pieces belong to the native picture only. */
        for (int i = (int)s_frame.piece_count - 1; i >= 0; i--) {
            const Piece *pc = &s_frame.pieces[i];
            int dx,dy;GiraffeSceneryShift(pc,&dx,&dy);
            int row = y0 - pc->y-dy;
            if (pc->fixed || DestinySkyFacePiece(pc) || row < 0 || row >= pc->size) continue;
            s_current_obj_slot=pc->slot&127;
            if((s_area_active&&(y0<0||y0>=224)) ||
               (!pc->kept && pc->slot==127 && (s_spawn_lead>0 || s_spawn_height>224))){
                s_stats.margin_sprite_pixels+=SpriteRow(obj,width,column,l,vram,pc->x+dx,row,pc->size,pc->attr,-column,width-column,CubPiece(pc),pc);
                continue;
            }
            s_stats.margin_sprite_pixels +=
                SpriteRow(obj, width, column, l, vram, pc->x+dx, row, pc->size, pc->attr, -column, 0, CubPiece(pc),pc) +
                SpriteRow(obj, width, column, l, vram, pc->x+dx, row, pc->size, pc->attr, 256, width - column, CubPiece(pc),pc);
        }
        /* The HUD: screen-fixed objects, then the slots reserved before the
         * object pass (lives), placed by the view, not by the camera. */
        s_hud_pass=1;
        for (int i = (int)s_frame.piece_count - 1; i >= 0; i--) {
            const Piece *pc = &s_frame.pieces[i];
            int dx,dy;ScenePieceShift(pc,&dx,&dy);
            int row = y0 - pc->y-dy;
            int expanded_rain=ExpandedEndingRain(pc,width);
            if(expanded_rain)row=RainModulo(row,224);
            int rain=EndingRainPiece(pc) && (s_md_ending_rain || expanded_rain);
            if (!pc->fixed || (!pc->kept && !rain) || (!s_hud_skip[pc->slot & 127] && !rain) || row < 0 || row >= pc->size) continue;
            s_current_obj_slot=pc->slot&127;
            int x=pc->x+dx+HudShift(rain?0:s_hud_side[pc->slot & 127],width,column);
            if(expanded_rain){
                int period=s_md_ending_rain?320:256;
                x=RainModulo(x+column,period)-column;
                if(x>-column)x-=period;
                for(;x<width-column;x+=period)
                    SpriteRow(obj,width,column,l,vram,x,row,pc->size,pc->attr,-column,width-column,false,pc);
            }else SpriteRow(obj,width,column,l,vram,x,row,pc->size,pc->attr,-column,width-column,false,pc);
        }
        for (int s = s_frame.hud_end - 1; s >= 0; s--) {
            unsigned idx = (unsigned)s * 2;
            int size = OamSize(l, idx), x = OamX(l, idx);
            int shift=s_area_active?s_area_height-224-s_area_top:0;
            int row=s_area_active?y0-(int)(l->oam[idx]>>8)-shift:(uint8_t)(y0-(l->oam[idx]>>8));
            if(row<0)continue;
            if (!s_hud_skip[s] || row >= size) continue;
            int side = s_hud_edges ? HudSide(x + size / 2) : 0;
            s_current_obj_slot=idx>>1;
            SpriteRow(obj, width, column, l, vram, x + HudShift(side, width, column), row, size, l->oam[idx + 1],
                      -column, width - column, false,NULL);
        }
        s_hud_pass=0;
        /* Rejected native pieces do not consume an OAM slot. Distinct actors
         * in an added margin can therefore share that slot. Draw complete MD
         * actors last-to-first, as for the captured native margin pieces, so
         * the earlier submitted actor wins ties instead of popping in when
         * its first native piece finally becomes visible. */
        for (int i=(int)s_frame.piece_count-1;i>=0;i--) {
            const Piece *pc=&s_frame.pieces[i];
            if (RideHiddenGiraffe(pc) || (pc->fixed && !FixedEffectPiece(pc)) || CubPiece(pc)) continue;
            unsigned role=SceneNpcRole(pc,(pc->attr>>9)&7);
            if(role==TLK_MD_SPRITE_PICKUP_POPUP && !PickupPopupPiece(pc))role=0;
            if(role==TLK_MD_SPRITE_CONTINUE_TOKEN && !ContinueTokenPiece(pc))role=0;
            if (!role || !s_md_npc_frames[role]) continue;
            unsigned before=0;for (;before<i;before++) if (s_frame.pieces[before].obj==pc->obj &&
                (pc->actor_descriptor!=0xc58aec ||
                 s_frame.pieces[before].y-s_frame.pieces[before].local_y==pc->y-pc->local_y)) break;
            if (before<i) continue;
            int bx,by,bw,bh;unsigned context_pose=SceneNpcPose(pc);
            if (!TlkMdSpritesBounds(context_pose,&bx,&by,&bw,&bh)) continue;
            int flipx=(pc->attr&0x4000)!=0,flipy=(pc->attr&0x8000)!=0;
            int origin_x=flipx ? pc->x+pc->local_x+pc->size : pc->x-pc->local_x;
            int expanded_rain=ExpandedEndingRain(pc,width);
            int rain=EndingRainPiece(pc) && (s_md_ending_rain || expanded_rain);
            if (pc->fixed && (rain || s_hud_skip[pc->slot&127]))
                origin_x+=HudShift(rain?0:s_hud_side[pc->slot&127],width,column);
            int origin_y=flipy ? pc->y+pc->local_y+pc->size+1 : pc->y-pc->local_y;
            int dx,dy;ScenePieceShift(pc,&dx,&dy);origin_x+=dx;origin_y+=dy;
            int local_y=flipy ? origin_y-y0-2 : y0-origin_y;
            if(expanded_rain)local_y=by+RainModulo(local_y-by,224);
            if (local_y<by || local_y>=by+bh) continue;
            unsigned slot=pc->slot&127;
            unsigned z=((((pc->attr>>12)&3u)*4+2)<<12)|((pc->attr&0x800)?4u:6u)<<8|
                       (0x80+16*((pc->attr>>9)&7u));
            for (int local_x=bx;local_x<bx+bw;local_x++) {
                int x=origin_x+(flipx?-local_x-1:local_x)+column;
                if(!expanded_rain && (x<0 || x>=width || slot>s_obj_slot[x]))continue;
                uint16_t color=0;
                if (SceneNpcSample(pc,local_x,local_y,0,1,s_md_npc_palette[role],l->cgram,&color)!=1) continue;
                int period=expanded_rain?(s_md_ending_rain?320:256):width;
                if(expanded_rain)x=RainModulo(x,period);
                for(;x<width;x+=period){
                    if(x<0 || slot>s_obj_slot[x])continue;
                    if(s_fallback_enabled)s_fallback_reason[x]=NULL;obj[x]=(uint16_t)(z|1u);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=SpritePaletteToken(pc);s_npc_color[x]=color;
                    if(!expanded_rain)break;
                }
            }
        }
        /* Draw the complete original splash once, rather than clipping it to
         * native tile rectangles. Preserve the captured flips and OAM order. */
        if(s_md_cub_frames)for(int i=(int)s_frame.piece_count-1;i>=0;i--) {
            const Piece *pc=&s_frame.pieces[i];unsigned pose=PreparedSplashPose(pc,l->cgram);
            if(!pose)continue;
            unsigned before=0;for(;before<(unsigned)i;before++)if(s_frame.pieces[before].obj==pc->obj)break;
            if(before<(unsigned)i)continue;
            int bx,by,bw,bh;if(!TlkMdSpritesBounds(pose,&bx,&by,&bw,&bh))continue;
            int flipx=(pc->attr&0x4000)!=0,flipy=(pc->attr&0x8000)!=0;
            int ox=flipx?pc->x+pc->local_x+pc->size:pc->x-pc->local_x;
            int oy=flipy?pc->y+pc->local_y+pc->size+1:pc->y-pc->local_y;
            int sy=flipy?oy-y0-2:y0-oy;if(sy<by || sy>=by+bh)continue;
            unsigned slot=pc->slot&127,z=((((pc->attr>>12)&3u)*4+2)<<12)|
                ((pc->attr&0x800)?4u:6u)<<8|0x800|0xd0;
            int palette=TlkResourcesUseMd("graphics.sprites.simba.adult.palette");
            for(int sx=bx;sx<bx+bw;sx++) {
                int x=ox+(flipx?-sx-1:sx)+column;if(x<0 || x>=width || slot>s_obj_slot[x])continue;
                int pixel=TlkMdSpritesPixel(pose,sx,sy);if(pixel<=0)continue;
                if(s_fallback_enabled)s_fallback_reason[x]=NULL;
                obj[x]=(uint16_t)(z|1u);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=SpritePaletteToken(pc);
                s_npc_color[x]=PreparedSplashColor((unsigned)pixel,1,palette,l->cgram);
            }
        }
        /* The original MD constructor adds a strip beyond the native piece
         * rectangles and repeats its tail bank for tall columns. Both factory
         * draws keep their original submission/OAM order and world anchors. */
        unsigned pillar_role=s_md_level==7?TLK_MD_SPRITE_LATER_WORLD:TLK_MD_SPRITE_GRAVEYARD_BONE_OBJECT;
        if(s_md_npc_frames[pillar_role])for(int i=(int)s_frame.piece_count-1;i>=0;i--) {
            const Piece *pc=&s_frame.pieces[i];
            if(!GraveyardPillarPiece(pc) || pc->local_x!=-16 || pc->local_y)continue;
            unsigned pose=GraveyardPillarPose(pc,l,vram);if(!pose)continue;
            unsigned height=rd16(s_frame.ram+0xab0e);if(height>208)continue;
            unsigned strips=2+(height>16?(height-16+15)/16:0);
            unsigned liquid_height=GraveyardLiquidHeight(pc);
            int sy=y0-pc->y;
            if(sy<0 || sy>=(int)(liquid_height?liquid_height:strips*16))continue;
            unsigned slot=pc->slot&127;
            unsigned z=((((pc->attr>>12)&3u)*4+2)<<12)|((pc->attr&0x800)?4u:6u)<<8|0xc0;
            for(int sx=0;sx<32;sx++) {
                int x=pc->x+sx+column;if(x<0 || x>=width || slot>s_obj_slot[x])continue;
                uint16_t color;
                if(GraveyardPillarSample(pose,sx-16,sy,0,1,
                    s_md_npc_palette[pillar_role],l->cgram,&color)!=1)continue;
                if(s_fallback_enabled)s_fallback_reason[x]=NULL;
                obj[x]=(uint16_t)(z|1u);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=SpritePaletteToken(pc);s_npc_color[x]=color;
            }
        }
        /* Submit the shifted complete face once, with its original native
         * pixels, per-line palette, OAM order and priority. */
        for(int i=(int)s_frame.piece_count-1;i>=0;i--) {
            const Piece *pc=&s_frame.pieces[i];if(!DestinySkyFacePiece(pc))continue;
            int row=y0-pc->y-s_destiny_face_dy;if(row<0 || row>=pc->size)continue;
            s_current_obj_slot=pc->slot&127;
            SpriteRow(obj,width,column,l,vram,pc->x+s_destiny_face_dx,row,
                      pc->size,pc->attr,-column,width-column,false,pc);
        }
        s_caption_pass=true;
        for(unsigned i=0;i<s_frame.piece_count;i++) {
            const Piece *pc=&s_frame.pieces[i];int centre=OpeningCaptionCentre(pc);
            unsigned caption=OpeningCaptionSlot(pc);uint16_t probe=0;int dy=0;
            if(caption && TlkResourcesUseMd("graphics.titles.remaining.position") &&
               TlkResourcesCaptionSample(caption,0,0,0,l->cgram,&probe)>=0)
                dy=72-(pc->y-pc->local_y);
            if(s_area_active)dy+=(s_area_height-224)/2-s_area_top;
            int row=y0-pc->y-dy;if(!centre || row<0 || row>=pc->size)continue;
            s_current_obj_slot=pc->slot&127;
            SpriteRow(obj,width,column,l,vram,width/2-centre+pc->local_x-column,
                      row,pc->size,pc->attr,-column,width-column,false,pc);
        }
        s_caption_pass=false;
        if(TlkResourcesUseMd("graphics.titles.remaining.frames"))for(unsigned i=0;i<s_frame.piece_count;i++) {
            const Piece *pc=&s_frame.pieces[i];unsigned caption=OpeningCaptionSlot(pc);if(!caption)continue;
            unsigned before=0;for(;before<i;before++)if(s_frame.pieces[before].obj==pc->obj)break;
            if(before<i)continue;
            int bx,by,bw,bh;if(!TlkResourcesCaptionBounds(caption,&bx,&by,&bw,&bh))continue;
            int base_y=TlkResourcesUseMd("graphics.titles.remaining.position")?72:pc->y-pc->local_y;
            if(s_area_active)base_y+=(s_area_height-224)/2-s_area_top;
            int sy=y0-base_y;if(sy<by || sy>=by+bh)continue;
            unsigned slot=pc->slot&127,z=((((pc->attr>>12)&3u)*4+2)<<12)|
                ((pc->attr&0x800)?4u:6u)<<8|0x80;
            unsigned palette=TlkResourcesUseMd("graphics.titles.remaining.palette");
            for(int dx=bx;dx<bx+bw;dx++) {
                int x=width/2+dx;if(x<0 || x>=width || slot>s_obj_slot[x])continue;
                uint16_t color=0;if(TlkResourcesCaptionSample(caption,dx,sy,palette,l->cgram,&color)!=1)continue;
                if(s_fallback_enabled)s_fallback_reason[x]=NULL;
                obj[x]=(uint16_t)(z|1u);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=SpritePaletteToken(pc);s_npc_color[x]=color;
            }
        }
        for(unsigned i=0;i<s_frame.piece_count;i++) {
            const Piece *pc=&s_frame.pieces[i];if(!TitlePiece(pc))continue;
            unsigned actor=rd16(s_frame.ram+pc->obj+4)-8;
            if(TlkResourcesUseMd("graphics.titles.pride_lands.duration") && rd16(s_frame.ram+actor+0x2c)<=50)continue;
            unsigned frames=TlkResourcesUseMd("graphics.titles.pride_lands.frames");
            unsigned palette=TlkResourcesUseMd("graphics.titles.pride_lands.palette");
            unsigned position=TlkResourcesUseMd("graphics.titles.pride_lands.position");
            if(frames) {
                unsigned before=0;for(;before<i;before++)if(s_frame.pieces[before].obj==pc->obj && TitlePiece(&s_frame.pieces[before]))break;
                if(before<i)continue;
            }
            /* Captions belong to the viewport, including the native falling
             * letters. World/camera anchoring drifts left at wide-view clamps.
             * Keep each letter's vertical entrance and the chosen baseline. */
            int x0=width/2,ybase=pc->y-pc->local_y;
            if(position)ybase=72;
            if(s_area_active)ybase+=(s_area_height-224)/2-s_area_top;
            int bx,by,bw,bh,sy=y0-ybase;
            if(frames) {
                if(!TlkResourcesTitleBounds(1,&bx,&by,&bw,&bh))continue;
            } else {
                /* Native letters retain their individually latched entrance
                 * offsets and OAM order, even with a different palette/anchor. */
                bx=pc->local_x-112;by=0;bw=bh=16;sy-=pc->local_y;
            }
            if(sy<by || sy>=by+bh)continue;
            unsigned slot=pc->slot&127;
            unsigned z=((((pc->attr>>12)&3u)*4+2)<<12)|((pc->attr&0x800)?4u:6u)<<8|0x80;
            for(int dx=bx;dx<bx+bw;dx++) {
                int x=x0+dx;if(x<0 || x>=width || slot>s_obj_slot[x])continue;
                uint16_t color;
                if(TlkResourcesTitleSample(dx,sy,frames,palette,l->cgram,&color)!=1)continue;
                if(s_fallback_enabled)s_fallback_reason[x]=NULL;obj[x]=(uint16_t)(z|1u);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=SpritePaletteToken(pc);s_npc_color[x]=color;
            }
        }
        if (s_md_cub_frames) for (unsigned i=0;i<s_frame.piece_count;i++) {
            const Piece *pc=&s_frame.pieces[i];
            if (!CubPiece(pc)) continue;
            unsigned before=0;for (;before<i;before++) if (s_frame.pieces[before].obj==pc->obj) break;
            if (before<i) continue;
            unsigned count=0;const TlkMdSpriteExtra *extra=TlkMdSpritesExtras(pc->pose,&count);
            int flipx=(pc->attr&0x4000)!=0,flipy=(pc->attr&0x8000)!=0;
            int origin_x=flipx ? pc->x+pc->local_x+pc->size : pc->x-pc->local_x;
            int origin_y=flipy ? pc->y+pc->local_y+pc->size+1 : pc->y-pc->local_y;
            unsigned slot=pc->slot&127;
            unsigned z=((((pc->attr>>12)&3u)*4+2)<<12)|((pc->attr&0x800)?4u:6u)<<8|
                       0x800|(0x80+16*((pc->attr>>9)&7u));
            for (unsigned n=0;n<count;n++) {
                int x=origin_x+(flipx?-extra[n].x-1:extra[n].x)+column;
                int y=origin_y+(flipy?-extra[n].y-2:extra[n].y);
                /* Small genuine MD art differences can extend beyond the
                 * original SNES piece rectangles. Preserve their source
                 * pixels and the actor's OAM ordering instead of clipping. */
                if (y==y0 && x>=0 && x<width && slot<=s_obj_slot[x]) {
                    if(s_fallback_enabled)s_fallback_reason[x]=NULL;obj[x]=(uint16_t)(z|(unsigned)extra[n].c);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=SpritePaletteToken(pc);s_npc_color[x]=0xffff;
                }
            }
        }
        s_md_npc_frames[TLK_MD_SPRITE_SCAR]=(pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.scar.frames");
    s_md_npc_palette[TLK_MD_SPRITE_SCAR]=(pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.scar.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_PUMBAA]=bonus && s_md_level==10 && TlkResourcesUseMd("graphics.sprites.bonus.pumbaa.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_PUMBAA]=bonus && s_md_level==10 && TlkResourcesUseMd("graphics.sprites.bonus.pumbaa.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_TIMON]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.timon.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_TIMON]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.timon.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_BUG]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.bugs.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_BUG]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.bugs.palette");
    for (unsigned kind=0;kind<3;kind++) {
            if (!s_md_hud_frames[kind] || !s_hud_present[kind] || (kind==2 && !TlkMdHudLifeReady())) continue;
            int origin_x=kind==1 ? width-32-TlkMdHudHealthMaximum()*4 : 16;
            /* Original Stampede health SAT is at Y28, below its top matte. */
            int shift=s_area_active?(kind==2?s_area_height-224-s_area_top:-s_area_top):0;
            int local_y=y0-(kind==2?200:(stampede && kind==1)?28:16)-shift;
            if (local_y<(kind==2?-6:0) || local_y>=(kind==2?18:16)) continue;
            unsigned slot=s_hud_slot[kind],attr=s_hud_attr[kind];
            unsigned z=((((attr>>12)&3u)*4+2)<<12)|((attr&0x800)?4u:6u)<<8;
            /* Original Stampede HUD records (8F9A8/8FE0E) set MD high
             * sprite priority. Native reserved life OAM on the first black
             * line can have low priority; don't put the MD counter behind
             * the original opaque canyon matte. */
            if(stampede)z=(z&0x0fff)|0xe000;
            for (int local_x=0;local_x<(kind==2?48:72);local_x++) {
                int x=origin_x+local_x;
                if (x<0 || x>=width || slot>s_obj_slot[x]) continue;
                unsigned pixel=TlkMdHudPixel(kind,local_x,local_y);if (!pixel) continue;
                unsigned index=128+pixel;
                if(s_fallback_enabled)s_fallback_reason[x]=NULL;obj[x]=(uint16_t)(z|index);s_obj_slot[x]=(uint8_t)slot;s_obj_palette[x]=PaletteToken("graphics.hud.palette");
                s_npc_color[x]=SceneHudColor(index,l->cgram,l->cgram[index]);
            }
        }
    }

    uint8_t mult[63], half[64];
    unsigned bright = l->inidisp & 15;
    for (int i = 0; i < 32; i++) mult[i] = (uint8_t)(((i << 3) | (i >> 2)) * bright / 15);
    for (int i = 32; i < 63; i++) mult[i] = mult[31];
    for (int i = 0; i < 64; i++) half[i] = mult[i >> 1];
    const unsigned clip_mode = l->cgwsel >> 6, prevent = (l->cgwsel >> 4) & 3;
    const bool add_sub = (l->cgwsel & 2) != 0, subtract = (l->cgadsub & 0x80) != 0;
    const bool halve = (l->cgadsub & 0x40) != 0;
    const bool need_sub = add_sub && (l->cgadsub & 0x3F) && prevent != 3 && l->ts;
    int ox = 0, oy = 0;
    Bg1Origin(l, y0, &ox, &oy);
    const bool map_left = s_map_left, map_right = s_map_right;
    uint16_t native_background[TLK_WIDE_MAX_WIDTH];
    int world_row=!s_area_active || (y0>=s_area_min_y && y0<s_area_max_y);
    int cached_return_bg=s_area_active && s_frame.stage && !s_md_background &&
        ((world_row && s_md_level==8 && !(l->bgmode&0x20)) ||
         (fitted_bands && !s_ride_scene &&
          (background_line->bgmode&7)==1 && !(background_line->bgmode&0x20)));
    if(cached_return_bg)NativeReturnBackgroundRow(native_background,width,column,
        fitted_bands?background_line:l,fitted_bands?background_y:y0);
    /* A layer that fills the native line but is nearly empty in the margins
     * (the sunset's sky: BG2 static, the other half of its 512-wide tilemap
     * unused but for a few stray tiles) shows the native columns mirrored
     * there instead. */
    bool mirror[2] = { false, false };
    for (unsigned layer = 0; layer < 2; layer++) {
        if(!world_row)continue;
        /* Decoded MD scenery spans the view directly. The native tilemap-ring
         * mirror heuristic must not substitute different margin coordinates. */
        if (s_ride_scene || (layer==1 && (anchor_pride || fitted_bands)) || (layer==0 ? s_md_foreground : s_md_background)) continue;
        /* A complete selected Return foreground already has world coordinates;
         * it does not sample the native ring in the margins. Tall BG2 rows
         * outside the authored canvas use boundary tokens below, so testing
         * that unused ring cannot affect their result either. */
        if((layer==0 && s_md_level==8 && s_native_md_layout) ||
           (layer==1 && s_area_active && (y0<0 || y0>=224)))continue;
        if (!((l->tm | (need_sub ? l->ts : 0)) & (1u << layer))) continue;
        unsigned native = 0, margin = 0, samples = 0;
        for (int x = 0; x < 256; x += 4)
            native += (layer==1 && cached_return_bg && x+column>=0 && x+column<width?
                native_background[x+column]:BgPixel(layer==1?background_line:l,s_vram[(layer==1?background_line:l)->vram],layer,x,y0,false,ox,oy,column,width))!=0;
        const int sides[2][2] = { { -column, 0 }, { 256, width - column } };
        for (int side = 0; side < 2; side++) {
            if (layer == 0 && (side ? map_right : map_left)) continue;   /* drawn from the level map */
            for (int x = sides[side][0]; x < sides[side][1]; x += 2, samples++)
                margin += (layer==1 && cached_return_bg?native_background[x+column]:
                    BgPixel(layer==1?background_line:l,s_vram[(layer==1?background_line:l)->vram],layer,x,y0,false,ox,oy,column,width))!=0;
        }
        mirror[layer] = samples && margin * 10 <= samples && native * 10 >= 64 * 9;
    }

    /* Each selected King background is a64-column (512-pixel) plane.
     * After the road wraps, its authored foreground ring is512 pixels too.
     * Cache tokens only within this row; sprites/windows still compose once
     * at their real positions and never repeat with the scenery. */
    int ride_view=s_ride_scene;
    int ring_camera=(int)rd16(s_frame.ram+0xb29b)-(int)rd16(s_frame.ram+0xa56);
    int ring_row=ride_view && ring_camera>=0 && rd16(s_frame.ram+0xa40)>(unsigned)ring_camera;
    uint16_t ride_tokens[2][512];
    /* Background-only fast paths can skip the first copy of a column.
     * Reuse a repeated token only if that column was actually sampled. */
    bool ride_token_valid[2][512]={{false}};
    int flat_ride_sky=!anchor_pride && !fitted_bands && s_area_active && ride_view && y0<s_area_min_y && !l->tmw && !l->tsw;
    const uint32_t *native_rgb[2]={NULL,NULL};
    int fast_native=s_area_active && s_frame.stage && !stampede && !(l->cgadsub&3) && !clip_mode &&
        !TlkResourcesUseMd("graphics.scenery.foreground") && !TlkResourcesUseMd("graphics.scenery.background");
    int fast_fixed=s_area_active && s_frame.stage && s_md_level==8 && !stampede && !clip_mode &&
        !prevent && !need_sub && (l->cgadsub&3) &&
        !TlkResourcesUseMd("graphics.scenery.foreground") && !TlkResourcesUseMd("graphics.scenery.background");
    if(fast_native){
        native_rgb[0]=NativeBackgroundRgb(0,l->cgram,bright,mult,md_scene,s_cw_scene);
        const uint16_t *bg_colors=(anchor_pride || fitted_bands)?background_line->cgram:l->cgram;
        native_rgb[1]=s_scenery_palette[0]!=s_scenery_palette[1] || memcmp(l->cgram,bg_colors,128*sizeof(uint16_t))?
            NativeBackgroundRgb(1,bg_colors,bright,mult,md_scene,s_cw_scene):native_rgb[0];
    }
    if(fast_fixed)for(unsigned layer=0;layer<2;layer++)
        native_rgb[layer]=NativeFixedBackgroundRgb(layer,l,bright,mult,half,md_scene,s_cw_scene);
    /* If both decoded planes are transparent, do not decode them a second
     * time through the scalar compositor. With no BG3 or backdrop math the
     * original result is exactly the scene's current backdrop colour. */
    int native_backdrop_ready=fast_fixed || (fast_native && !(l->tm&4) && !(l->cgadsub&0x20));
    uint32_t native_backdrop=native_backdrop_ready?NativeFixedBackdropRgb(l,mult,half):0;

    int panorama_scroll=anchor_pride?(s_native_background_motion?(int)background_line->hofs[1]:PanoramaScroll(background_line)):0;
    const uint16_t *bottom_background=BottomBackgroundRow(l,width,column,y0,ox,oy);
    uint16_t native_foreground[TLK_WIDE_MAX_WIDTH];
    int fast_native_row=world_row && fast_native && (anchor_pride || fitted_bands) && !s_native_md_layout &&
        (l->tm&3)==3 && !(l->tmw&3) && !(l->bgmode&0x30) && !mirror[0];
    int fast_material_row=world_row && (fast_native || fast_fixed) && s_native_md_layout && (l->tm&7)==3 &&
        !(l->tmw&3) && !(l->bgmode&0x30) && !mirror[0] && !mirror[1];
    if(fast_native_row || fast_material_row)NativeAreaForegroundRow(native_foreground,width,column,l,y0,ox,oy,map_left,map_right);
    for (int i = 0; i < width; i++) {
        if(flat_ride_sky && i>0 && !obj[i] && !obj[i-1]){out[i]=out[i-1];continue;}
        int x = i - column;
        uint16_t main = 0x0500, sub = 0x0500;
        if(fast_native_row && !obj[i] && i>=s_vis_lo && i<s_vis_hi && y0>=s_area_min_y && y0<s_area_max_y){
            uint16_t a=native_foreground[i],b=anchor_pride?
                s_panorama_pixels[background_line->vram][(unsigned)background_y*512+PanoramaX(x+panorama_scroll)]:
                cached_return_bg?native_background[i]:
                BgPixel(background_line,s_vram[background_line->vram],1,x,background_y,false,ox,oy,column,width);
            uint16_t pixel=(b>>12)>(a>>12)?b:a;
            if(pixel){out[i]=native_rgb[(pixel>>8)&1][pixel&127];continue;}
            if(native_backdrop_ready){out[i]=native_backdrop;continue;}
        }
        if(fast_material_row && !obj[i] && i>=s_vis_lo && i<s_vis_hi && y0>=s_area_min_y && y0<s_area_max_y){
            uint16_t a=native_foreground[i],b=fitted_bands?
                (cached_return_bg?native_background[i]:BgPixel(background_line,s_vram[background_line->vram],1,x,background_y,false,ox,oy,column,width)):
                fast_fixed?native_background[i]:BgPixel(l,vram,1,x,y0<0?0:y0>=224?223:y0,false,ox,oy,column,width);
            uint16_t pixel=(b>>12)>(a>>12)?b:a;
            if(pixel){out[i]=native_rgb[(pixel>>8)&1][pixel&127];continue;}
            if(native_backdrop_ready){out[i]=native_backdrop;continue;}
        }
   /* backdrop: layer 5, colour 0 */
        /* Past where the camera stops: nothing of the level, black. */
        bool outside = i < s_vis_lo || i >= s_vis_hi || (s_area_active&&!ride_view&&(y0<s_area_min_y||y0>=s_area_max_y));
        int background_view=s_area_active && (anchor_pride || fitted_bands);
        if (outside && !obj[i] && !background_view) { out[i] = 0; continue; }
        for (unsigned layer = 0; layer < 3; layer++) {
            if(outside && (!background_view || layer!=1))continue;
            unsigned bit = 1u << layer;
            if (!((l->tm | (need_sub ? l->ts : 0)) & bit)) continue;
            bool in_margin = x < 0 || x >= 256;
            if(s_area_active && ride_view && layer==0 && (y0<s_area_min_y || y0>=s_area_max_y))continue;
            if(s_area_active&&layer==2&&(y0<0||y0>=224))continue;
            // Screen-anchored parallax artwork has a finite original canvas.
            // Keep its boundary row outside that canvas; never wrap the sky.
            int by=(s_area_active&&layer==1)?(y0<0?0:y0>=224?223:y0):y0;
            uint16_t px;
            int live_reference=(i&511)-column;
            int repeat=ride_view && !flat_ride_sky && s_vis_lo==0 && s_vis_hi==width && layer<2 &&
                ((layer==1 && !anchor_pride) || (layer==0 && ring_row &&
                 !(s_ride_exit_shift>=0 && ox+x>=s_ride_exit_shift+(int)rd16(s_frame.ram+0xa56)+512)));
            if(repeat && i>=512 && ride_token_valid[layer][i&511])px=ride_tokens[layer][i&511];
            else if(layer==1 && anchor_pride)
                px=s_panorama_pixels[background_line->vram][(unsigned)background_y*512+
                    PanoramaX(x+panorama_scroll)];
            else if(layer==1 && fitted_bands)
                px=cached_return_bg?native_background[i]:BgPixel(background_line,s_vram[background_line->vram],1,x,background_y,false,ox,oy,column,width);
            else if(layer==1 && bottom_background)px=bottom_background[i];
            else if(s_area_active&&layer==1&&(y0<0||y0>=224))
                px=BgPixel(l,vram,1,x,by,false,ox,oy,column,width);
            else px = layer < 2 && mirror[layer] && in_margin ? BgPixel(l,vram,layer,Reflect(x,256),by,false,ox,oy,column,width)
                : BgPixel(l,vram,layer,x,by,(s_area_active&&(y0<0||y0>=224))||(x<0?map_left:x>=256&&map_right),ox,oy,column,width);
            if(repeat && i<512){ride_tokens[layer][i]=px;ride_token_valid[layer][i]=true;}
            if (!px) continue;
            if ((l->tm & bit) && (px >> 12) > (main >> 12) && !((l->tmw & bit) && Window(l, layer, x, column, width)))
                main = px;
            if (need_sub && (l->ts & bit) && (px >> 12) > (sub >> 12) &&
                !((l->tsw & bit) && Window(l, layer, x, column, width)))
                sub = px;
        }
        int stampede_token=-1;
        if(stampede_background && x>=0 && x<256 && (l->tm&3)){
            stampede_token=stampede_background[y0*256+x];
            main=(uint16_t)((stampede_token&128?12:7)<<12);sub=0x0500;
        }
        uint16_t o = obj[i];
        if (o) {
            if ((l->tm & 0x10) && (o >> 12) > (main >> 12) && !((l->tmw & 0x10) && Window(l, 4, x, column, width)))
                main = o;
            if (need_sub && (l->ts & 0x10) && (o >> 12) > (sub >> 12) &&
                !((l->tsw & 0x10) && Window(l, 4, x, column, width)))
                sub = o;
        }
        if(main==o && o && s_obj_slot[i]==254)s_ride_preview_visible++;
        unsigned resolved_layer=(main>>8)&7;
        if((fast_native || fast_fixed) && resolved_layer<=1 && !(main&0x800)){
            out[i]=native_rgb[resolved_layer][main&127];continue;
        }
        bool inside = (clip_mode == 1 || clip_mode == 2 || prevent == 1 || prevent == 2) && Window(l, 5, x, column, width);
        bool keep = clip_mode == 0 || (clip_mode == 1 && inside) || (clip_mode == 2 && !inside);
        bool math_ok = prevent == 0 || (prevent == 1 && inside) || (prevent == 2 && !inside);
        unsigned mask = keep ? 31 : 0, c = l->cgram[main & 255], layer = (main >> 8) & 7;
        if((anchor_pride || fitted_bands) && layer==1)c=background_line->cgram[main&255];
        int stampede_pixel=stampede_token>=0 && layer<=1;
        if(stampede_pixel)c=TlkNextSceneStampedeColor(stampede_token&63,stampede_palette);
        else if((layer<=1 || layer==5) && stampede_palette)c=StampedeColor(main&255,(uint16_t)c);
        else if(layer==5 && s_cw_scene && !s_cw_palette_mode)c=s_cw_native_mapped[1][0];
        else if(layer<=1 && s_cw_scene)c=(main&0x800)?s_cw_external[layer][main&63]:s_cw_native_mapped[layer][main&127];
        else if (layer<=1 && md_scene) c=TlkMdSceneModeColor(main&255,(main&0x800)!=0,(uint16_t)c,s_scenery_palette[layer]);
        else if (main & 0x800) c = TlkResourcesCubColor(s_md_level, main & 255, l->cgram, (uint16_t)c);
        if (layer>=4 && main==o && s_npc_color[i]!=0xffff) c=s_npc_color[i];
        if(s_fallback_enabled && keep && bright && !(l->inidisp&128)) {
            if(layer>=4 && main==o && s_fallback_reason[i]) {
                const Piece *p=s_fallback_piece[i];
                unsigned pi=p?(unsigned)(p-s_frame.pieces):kMaxPieces;
                const TlkFallbackSpriteInfo *info=pi<kMaxPieces && s_fallback_sprite_valid[pi]?&s_fallback_sprite_info[pi]:NULL;
                TlkFallbackSpriteRecord(p && !strstr(s_fallback_reason[i],"unclassified")?"fallback":"unclassified",
                    s_fallback_reason[i],p?p->obj:0,p?p->pose:0,info,1);
            } else if(layer<=1 && !(main&0x800) && !stampede_pixel) {
                const char *id=layer?"graphics.scenery.background":"graphics.scenery.foreground";
                if(TlkResourcesUseMd(id))TlkFallbackRecord("fallback",id,
                    layer?"native_background_pixel":"unmapped_native_foreground_pixel",0,0,
                    (((unsigned)oy>>4)&65535)<<16 | (((unsigned)(ox+x)>>4)&65535),1);
            }
        }
        c=layer>=4&&main==o?SpriteCustomColor(s_obj_palette[i],c):SceneryCustomColor(layer,c);
        unsigned r = c & mask, g = (c >> 5) & mask, b = (c >> 10) & mask;
        const uint8_t *map = mult;
        if (math_ok && !stampede_pixel && !(stampede_palette && (layer<=1 || layer==5)) && (l->cgadsub & 0x3F & (1u << layer))) {
            unsigned c2;
            if (add_sub && (sub & 0xFF)) {
                c2 = l->cgram[sub & 255];
                unsigned sub_layer=(sub>>8)&7;
                if((anchor_pride || fitted_bands) && sub_layer==1)c2=background_line->cgram[sub&255];
                if(sub_layer<=1 && stampede_palette)c2=StampedeColor(sub&255,(uint16_t)c2);
                else if(sub_layer<=1 && s_cw_scene)c2=(sub&0x800)?s_cw_external[sub_layer][sub&63]:s_cw_native_mapped[sub_layer][sub&127];
                else if (sub_layer<=1 && md_scene) c2=TlkMdSceneModeColor(sub&255,(sub&0x800)!=0,(uint16_t)c2,s_scenery_palette[sub_layer]);
                else if (sub & 0x800) c2 = TlkResourcesCubColor(s_md_level, sub & 255, l->cgram, (uint16_t)c2);
                if (sub_layer>=4 && sub==o && s_npc_color[i]!=0xffff) c2=s_npc_color[i];
                c2=sub_layer>=4&&sub==o?SpriteCustomColor(s_obj_palette[i],c2):SceneryCustomColor(sub_layer,c2);
                if (halve) map = half;
            }
            else if (add_sub) c2 = l->fixed;
            else { c2 = l->fixed; if (halve) map = half; }
            unsigned r2 = c2 & 31, g2 = (c2 >> 5) & 31, b2 = (c2 >> 10) & 31;
            if (subtract) {
                r = r >= r2 ? r - r2 : 0; g = g >= g2 ? g - g2 : 0; b = b >= b2 ? b - b2 : 0;
            } else {
                r += r2; g += g2; b += b2;
            }
        }
        out[i] = (uint32_t)map[r] << 16 | (uint32_t)map[g] << 8 | map[b];
    }
}

/* ── API ───────────────────────────────────────────────────────────────── */

void TlkWideSetRom(const uint8_t *rom,size_t size) {
    s_rom=rom;s_rom_size=size;memset(s_native_panorama_height,0,sizeof s_native_panorama_height);
    memset(s_panorama_owner,0,sizeof s_panorama_owner);
    if(!rom || size<0x400)return;
    for(unsigned level=0;level<14;level++){
        if(level>1 && level<11)continue;
        unsigned rec=rd24(rom+0x357+level*3)&0x3fffff;size_t written=0;
        if(rec+29>size)continue;
        if(TlkMdDecompress(rom,size,rd24(rom+rec+26)&0x3fffff,s_native_panorama[level],sizeof s_native_panorama[level],&written) &&
           written && !(written%128) && written==(level>=11?3584u:level?3968u:5760u))
            s_native_panorama_height[level]=(unsigned)written/128*8;
    }
}

void TlkWideEnable(bool on) {
    s_enabled = on;
    if (on) ArmInterpreterHooks();
    g_tlk_wide_pc_hook = on || s_spawn_lead ? Observe : NULL;
    g_tlk_raster_observer = on ? CaptureLine : NULL;
    if (!on) TlkWideReset();
}

bool TlkWideEnabled(void) { return s_enabled; }
unsigned TlkWideFrameLevel(void) { return s_frame.valid?rd16(s_frame.ram+0x1ff9e):0xffff; }
bool TlkWideFrameOstrichRide(void) {
    return s_frame.valid && rd16(s_frame.ram+0x1ff9e)==1 &&
        rd24(s_frame.ram+0xdf)==0xc003b9 && rd16(s_frame.ram+0xa56)!=0;
}
void TlkWideHoldBackgroundPhase(void) { s_bg_hold_next=true; }

void TlkWideSetSpawnHeight(int height) {
    s_spawn_height=height>224&&height<=TLK_WIDE_MAX_VIEW_HEIGHT?height:224;
}

void TlkWideSetSpawnLead(int pixels) {
    s_spawn_lead = pixels > 0 ? pixels : 0;
    if (s_spawn_lead) {
        ArmInterpreterHooks();
        g_tlk_wide_pc_hook = Observe;
    }
}

void TlkWideReset(void) {
    s_ride_rescan_pending=0;s_ride_cursor=0;
    s_free_view_key=s_free_view_scene=0;s_free_view_origin=0;
    memset(s_edge_stable,0,sizeof s_edge_stable);memset(s_edge_pending,0,sizeof s_edge_pending);
    memset(s_edge_seen,0,sizeof s_edge_seen);memset(s_edge_count,0,sizeof s_edge_count);memset(s_edge_serial,0,sizeof s_edge_serial);
    memset(&s_scene_animation,0,sizeof s_scene_animation);
    memset(&s_gy_death,0,sizeof s_gy_death);
    memset(&s_cant_wait,0,sizeof s_cant_wait);s_cw_palette_valid=s_cw_scene=0;
    s_build_count = s_latched_count = 0;
    s_frame.valid = false;
    s_frame.captured = 0;
    s_vram_have = false;
    s_have_last = false;
    s_bg_history=0;s_latch_serial=0;s_bg_level=-1;s_bg_hold_next=false;
    s_panorama_phase=0;s_panorama_phase_level=-1;
    memset(&s_ride_handoff,0,sizeof s_ride_handoff);s_ride_handoff.camera=s_ride_handoff.native_camera=-1;s_ride_raster_anchor=-1;
}

/* Pointer-free presentation history, separate from the guest rollback blob. */
static void ViewPut(uint8_t *p,uint32_t v) {
    for (unsigned i=0;i<4;i++) p[i]=(uint8_t)(v>>(i*8));
}
static uint32_t ViewGet(const uint8_t *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
size_t TlkWideSaveHistory(uint8_t *out,size_t cap) {
    /* The game can clear its RAM map while the last stage is still displayed.
     * Keep the already validated map, not a process-local pointer to it. */
    size_t map_bytes=s_have_last?(size_t)s_last_level.rowb*s_last_level.rows:0;
    size_t n=444+24*(s_build_count+s_latched_count)+map_bytes;
    if (!out || cap<n) return n;
    memset(out,0,n);memcpy(out,"TLKVIEW1",8);
    ViewPut(out+8,13);ViewPut(out+12,s_build_count);ViewPut(out+16,s_latched_count);
    ViewPut(out+20,s_latch_serial);ViewPut(out+24,s_bg_history);
    ViewPut(out+28,(uint32_t)s_bg_camera[0]);ViewPut(out+32,(uint32_t)s_bg_camera[1]);
    ViewPut(out+36,(uint32_t)s_bg_previous_raster[0]);ViewPut(out+40,(uint32_t)s_bg_previous_raster[1]);
    ViewPut(out+44,s_bg_last_latch);ViewPut(out+48,(uint32_t)s_bg_level);
    ViewPut(out+52,s_have_last);
    if(s_have_last) {
        ViewPut(out+56,s_last_level.rowb);ViewPut(out+60,s_last_level.rows);
        ViewPut(out+64,s_last_level.blk);ViewPut(out+68,(uint32_t)map_bytes);
        memcpy(out+72,s_last_limits,4);
    }
    const unsigned *fields[]={&s_cant_wait.active,&s_cant_wait.triggered,&s_cant_wait.delay,&s_cant_wait.updates,
        &s_cant_wait.latch,&s_cant_wait.camera,&s_cant_wait.previous_camera,&s_cant_wait.wrap,&s_cant_wait.previous_wrap};
    for(unsigned i=0;i<9;i++)ViewPut(out+80+i*4,*fields[i]);
    for(unsigned i=0;i<100;i++){out[116+i*2]=(uint8_t)s_cant_wait.colors[i];out[117+i*2]=(uint8_t)(s_cant_wait.colors[i]>>8);}
    ViewPut(out+76,(uint32_t)s_free_view_origin);
    ViewPut(out+316,(unsigned)s_edge_stable[0]|(unsigned)s_edge_stable[1]<<16);
    ViewPut(out+376,s_free_view_key);ViewPut(out+380,s_free_view_scene);
    ViewPut(out+320,s_gy_death.live);ViewPut(out+324,s_gy_death.active);ViewPut(out+328,s_gy_death.age);ViewPut(out+332,s_gy_death.latch);
    ViewPut(out+336,(uint32_t)s_gy_death.x);ViewPut(out+340,(uint32_t)s_gy_death.y);
    for(unsigned i=0;i<16;i++){out[344+i*2]=(uint8_t)s_gy_death.colors[i];out[345+i*2]=(uint8_t)(s_gy_death.colors[i]>>8);}
    ViewPut(out+384,s_scene_animation.active);ViewPut(out+388,s_scene_animation.phase);
    ViewPut(out+392,s_scene_animation.delay);ViewPut(out+396,s_scene_animation.latch);
    ViewPut(out+400,(uint32_t)s_panorama_phase);ViewPut(out+404,(uint32_t)s_panorama_phase_level);
    ViewPut(out+408,(uint32_t)s_ride_handoff.camera);ViewPut(out+412,(uint32_t)s_ride_handoff.background);
    ViewPut(out+416,(uint32_t)s_ride_handoff.shift);ViewPut(out+420,(uint32_t)s_ride_handoff.background_shift);
    ViewPut(out+424,s_ride_handoff.loop);ViewPut(out+428,(uint32_t)s_ride_handoff.native_camera);
    ViewPut(out+432,(uint32_t)s_ride_handoff.head_x);ViewPut(out+436,(uint32_t)s_ride_handoff.head_y);ViewPut(out+440,s_ride_handoff.head_attributes);
    for (unsigned i=0;i<s_build_count+s_latched_count;i++) {
        const Piece *q=i<s_build_count?&s_build[i]:&s_latched[i-s_build_count];
        uint8_t *p=out+444+24*i;
        ViewPut(p,(uint16_t)q->x|((uint32_t)(uint16_t)q->y<<16));
        ViewPut(p+4,q->attr|((uint32_t)q->obj<<16));
        p[8]=q->size;p[9]=q->slot;p[10]=q->kept;p[11]=q->fixed;p[12]=(uint8_t)q->side;
        p[13]=(uint8_t)q->actor_descriptor;p[14]=(uint8_t)(q->actor_descriptor>>8);p[15]=(uint8_t)(q->actor_descriptor>>16);
        ViewPut(p+16,q->pose|((uint32_t)q->hyena_art_context<<24));ViewPut(p+20,(uint16_t)q->local_x|((uint32_t)(uint16_t)q->local_y<<16));
    }
    if(map_bytes)memcpy(out+444+24*(s_build_count+s_latched_count),s_last_map,map_bytes);
    return n;
}
bool TlkWideValidateHistory(const uint8_t *p,size_t n) {
    if (!p || n<48 || memcmp(p,"TLKVIEW1",8) || ViewGet(p+8)<1 || ViewGet(p+8)>13 ||
        ViewGet(p+12)>kMaxPieces || ViewGet(p+16)>kMaxPieces || ViewGet(p+24)>1 ||
        n>TLK_WIDE_HISTORY_MAX) return false;
    unsigned version=ViewGet(p+8);
    size_t header=version>=13?444:version>=12?408:version>=6?400:version==5?384:version==4?320:version==1?48:version==2?52:80;
    if(n<header)return false;
    if(version>=13 && ((int32_t)ViewGet(p+408)<-1 || (int32_t)ViewGet(p+408)>65535 ||
       (int32_t)ViewGet(p+412)<-16777216 || (int32_t)ViewGet(p+412)>16777216 ||
       ViewGet(p+416)>1024 || (int32_t)ViewGet(p+420)<-1024 || (int32_t)ViewGet(p+420)>1024 ||
       ViewGet(p+424)>65535 || (int32_t)ViewGet(p+428)<-1 || (int32_t)ViewGet(p+428)>65535 || ViewGet(p+432)>65535 || ViewGet(p+436)>65535 || ViewGet(p+440)>255))return false;
    if(version>=12 && ((int32_t)ViewGet(p+404)<-1 || (int32_t)ViewGet(p+404)>1 ||
       (int32_t)ViewGet(p+400)<-16777216 || (int32_t)ViewGet(p+400)>16777216))return false;
    if(version>=11){
        unsigned key=ViewGet(p+376),height=key&1023,level=(key>>10)&15;
        if(key && (!(key&0x80000000u) || (key&0x7fffc000u) || height<=224 || height>TLK_WIDE_MAX_VIEW_HEIGHT || (level>9 && (level<11 || level>13)) ||
           (int32_t)ViewGet(p+76)<-65536 || (int32_t)ViewGet(p+76)>65535))return false;
        if(key && level>=11 && (ViewGet(p+380)&65535)!=0x60f+(level-11)*0x32)return false;
        if(!key && (ViewGet(p+76)||ViewGet(p+380)))return false;
    }
    if(version>=2 && ViewGet(p+48)>65535u && ViewGet(p+48)!=0xffffffffu)return false;
    size_t pieces=24*(ViewGet(p+12)+ViewGet(p+16)),map_bytes=0;
    if(version>=3) {
        unsigned kept=ViewGet(p+52),rowb=ViewGet(p+56),rows=ViewGet(p+60),blk=ViewGet(p+64);
        map_bytes=ViewGet(p+68);
        if(kept>1 || (version<11 && ViewGet(p+76)))return false;
        if(kept) {
            if(!rowb || (rowb&1) || !rows || (uint64_t)rowb*rows>65536 ||
               (uint64_t)rowb*rows!=map_bytes || blk>0x3fffff || (s_rom_size && blk>=s_rom_size))return false;
        } else if(rowb || rows || blk || map_bytes || ViewGet(p+72))return false;
    }
    if(version>=4) {
        if(ViewGet(p+80)>1 || ViewGet(p+84)>1 || ViewGet(p+88)>8 || ViewGet(p+92)>100 || (version<11 && ViewGet(p+316)))return false;
        for(unsigned i=100;i<116;i+=4)if(ViewGet(p+i)>65535)return false;
        for(unsigned i=0;i<100;i++)if(rd16(p+116+i*2)&~0xeee)return false;
    }
    if(version>=5 && (ViewGet(p+320)>1 || ViewGet(p+324)>1 || ViewGet(p+328)>249 ||
       (int32_t)ViewGet(p+336)<-4096 || (int32_t)ViewGet(p+336)>4096 ||
       (int32_t)ViewGet(p+340)<-4096 || (int32_t)ViewGet(p+340)>4096 || (version<11 && (ViewGet(p+376) || ViewGet(p+380)))))return false;
    if(version==6 && (ViewGet(p+384)>1 || ViewGet(p+388)>3 || ViewGet(p+392)>5))return false;
    if(version>=7) {
        unsigned owner=ViewGet(p+384),phase=ViewGet(p+388),delay=ViewGet(p+392);
        if((owner!=0 && owner!=5 && owner!=9) ||
           (owner==5 && (phase>3 || delay>5)) ||
           (owner==9 && !(phase<=2 && delay<=200) &&
             !(version>=8 && PrideRockRainPhase(phase) && delay<=8 && ((phase&7)<7 || !delay))) ||
           (!owner && (phase || delay)))return false;
    }
    if(n!=header+pieces+map_bytes)return false;
    for (size_t at=header;at<header+pieces;at+=24) {
        const uint8_t *q=p+at;
        if ((q[8]!=8 && q[8]!=16) || q[10]>1 || q[11]>1 ||
            (int8_t)q[12]<-64 || (int8_t)q[12]>64 || (version<9 && (q[13] || q[14] || q[15])) ||
            (version<10 && q[19]) || (version>=10 && q[19]>8)) return false;
        if(version>=10 && q[19] && (!TlkHyenaContextAlias(q[19],rd24(q+16)) ||
            rd24(q+13)!=0xc58ecc || q[11] || ((rd16(q+4)>>9)&7)!=6))return false;
    }
    return true;
}
void TlkWideLoadHistory(const uint8_t *p,size_t n) {
    TlkWideReset();
    if (!TlkWideValidateHistory(p,n)) return;
    s_build_count=ViewGet(p+12);s_latched_count=ViewGet(p+16);s_latch_serial=ViewGet(p+20);
    s_bg_history=ViewGet(p+24);s_bg_camera[0]=(int32_t)ViewGet(p+28);s_bg_camera[1]=(int32_t)ViewGet(p+32);
    s_bg_previous_raster[0]=(int32_t)ViewGet(p+36);s_bg_previous_raster[1]=(int32_t)ViewGet(p+40);
    s_bg_last_latch=ViewGet(p+44);
    unsigned version=ViewGet(p+8);
    s_bg_level=version==1?(s_bg_history?0:-1):(int32_t)ViewGet(p+48);
    if(version>=12){s_panorama_phase=(int32_t)ViewGet(p+400);s_panorama_phase_level=(int32_t)ViewGet(p+404);}
    if(version>=13){s_ride_handoff.camera=(int32_t)ViewGet(p+408);s_ride_handoff.background=(int32_t)ViewGet(p+412);
        s_ride_handoff.shift=(int32_t)ViewGet(p+416);s_ride_handoff.background_shift=(int32_t)ViewGet(p+420);s_ride_handoff.loop=ViewGet(p+424);s_ride_handoff.native_camera=(int32_t)ViewGet(p+428);s_ride_handoff.head_x=(int32_t)ViewGet(p+432);s_ride_handoff.head_y=(int32_t)ViewGet(p+436);s_ride_handoff.head_attributes=ViewGet(p+440);}
    size_t header=version>=13?444:version>=12?408:version>=6?400:version==5?384:version==4?320:version==1?48:version==2?52:80;
    if(version>=4) {
        unsigned *fields[]={&s_cant_wait.active,&s_cant_wait.triggered,&s_cant_wait.delay,&s_cant_wait.updates,
            &s_cant_wait.latch,&s_cant_wait.camera,&s_cant_wait.previous_camera,&s_cant_wait.wrap,&s_cant_wait.previous_wrap};
        for(unsigned i=0;i<9;i++)*fields[i]=ViewGet(p+80+i*4);
        for(unsigned i=0;i<100;i++)s_cant_wait.colors[i]=rd16(p+116+i*2);
    }
    if(version>=5){
        s_gy_death.live=ViewGet(p+320);s_gy_death.active=ViewGet(p+324);s_gy_death.age=ViewGet(p+328);s_gy_death.latch=ViewGet(p+332);
        s_gy_death.x=(int32_t)ViewGet(p+336);s_gy_death.y=(int32_t)ViewGet(p+340);
        for(unsigned i=0;i<16;i++)s_gy_death.colors[i]=rd16(p+344+i*2);
    }
    if(version>=11){
        s_free_view_origin=(int32_t)ViewGet(p+76);s_free_view_key=ViewGet(p+376);s_free_view_scene=ViewGet(p+380);
        s_edge_stable[0]=(uint16_t)ViewGet(p+316);s_edge_stable[1]=(uint16_t)(ViewGet(p+316)>>16);
        s_edge_seen[0]=s_edge_seen[1]=s_free_view_key!=0;
    }
    if(version>=6) {
        s_scene_animation.active=version==6?(ViewGet(p+384)?5:0):ViewGet(p+384);s_scene_animation.phase=ViewGet(p+388);
        s_scene_animation.delay=ViewGet(p+392);s_scene_animation.latch=ViewGet(p+396);
    }
    for (unsigned i=0;i<s_build_count+s_latched_count;i++) {
        Piece *q=i<s_build_count?&s_build[i]:&s_latched[i-s_build_count];
        const uint8_t *v=p+header+24*i;
        q->x=(int16_t)rd16(v);q->y=(int16_t)rd16(v+2);q->attr=rd16(v+4);q->obj=rd16(v+6);
        q->size=v[8];q->slot=v[9];q->kept=v[10];q->fixed=v[11];q->side=(int8_t)v[12];
        q->pose=rd24(v+16);q->hyena_art_context=version>=10?v[19]:0;q->local_x=(int16_t)rd16(v+20);q->local_y=(int16_t)rd16(v+22);
        q->actor_descriptor=rd24(v+13);
    }
    if(version>=3 && ViewGet(p+52)) {
        s_last_level.rowb=ViewGet(p+56);s_last_level.rows=ViewGet(p+60);s_last_level.blk=ViewGet(p+64);
        s_last_level.map=s_last_map;
        memset(s_last_map,0,sizeof s_last_map);
        memcpy(s_last_map,p+header+24*(s_build_count+s_latched_count),ViewGet(p+68));
        memcpy(s_last_limits,p+72,4);s_have_last=true;
    }
}

static void BackgroundFrame(void) {
    bool hold=s_bg_hold_next;s_bg_hold_next=false;
    int *camera=s_frame.raster_camera;
    camera[0]=(int)rd16(s_frame.ram+0xb29b);camera[1]=(int)rd16(s_frame.ram+0xb29d)+1;
    for (int y=0;y<TLK_WIDE_HEIGHT && s_frame.stage;y++) {
        const Line *l=&s_frame.lines[y];
        if (!LineHasStage(l) || (l->inidisp&0x80)) continue;
        int ox,oy;Bg1Origin(l,y,&ox,&oy);camera[0]=ox;camera[1]=oy-y;break;
    }
    int advanced=0;
    unsigned descriptor=rd16(s_frame.ram+0xdf);
    int pride=rd16(s_frame.ram+0x1ff9e)==0 && (descriptor==0x387 || descriptor==0x80d);
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    int hakuna=s_frame.stage && level==5 && descriptor==0x481;
    int postfight=s_frame.stage && level==9 && descriptor==0x7db;
    int pride_rock=s_frame.stage && level==9 && (descriptor==0x549 || postfight);
    unsigned postfight_phase=rd16(s_frame.ram+0xb23f);
    /* Original1B2C6C starts E9CE on entry to phase11, after phase10's wait.
     * A6C2/E9C2 starts the ember/rain choreography earlier; it is NOT this
     * palette event. Keep color timing tied to the actual player script. */
    int rain_event=postfight && rd24(s_frame.ram+0xb243)==0xc674be &&
                   postfight_phase>=11 && postfight_phase<=18;
    if(pride_rock) {
        if(s_scene_animation.active!=9) {
            s_scene_animation.active=9;s_scene_animation.phase=2;s_scene_animation.delay=200;
            s_scene_animation.latch=s_frame.latch_serial;
            /* A native-only research restore can start after the weather has
             * finished. Current frontend saves retain the exact phase/delay. */
            if(rain_event && postfight_phase>=12){s_scene_animation.phase=0x127;s_scene_animation.delay=0;}
        } else if(!hold && !rd16(s_frame.ram+0x0a89) && s_scene_animation.latch!=s_frame.latch_serial) {
            s_scene_animation.latch=s_frame.latch_serial;
            if(rain_event && !PrideRockRainPhase(s_scene_animation.phase)){
                s_scene_animation.phase=0x100|(s_scene_animation.phase<<4);s_scene_animation.delay=1;
            }else if(PrideRockRainPhase(s_scene_animation.phase)){
                unsigned step=s_scene_animation.phase&7;
                if(step<7){
                    if(s_scene_animation.delay)s_scene_animation.delay--;
                    else {s_scene_animation.phase++;s_scene_animation.delay=(step+1<7)?8:0;}
                }
            }else if(s_scene_animation.delay)s_scene_animation.delay--;
            else {s_scene_animation.delay=10;s_scene_animation.phase=(s_scene_animation.phase+1)%3;}
        }
    } else if(!hakuna)memset(&s_scene_animation,0,sizeof s_scene_animation);
    else if(s_scene_animation.active!=5) {
        s_scene_animation.active=5;s_scene_animation.phase=0;s_scene_animation.delay=5;
        s_scene_animation.latch=s_frame.latch_serial;
    } else if(!hold && !rd16(s_frame.ram+0x0a89) && s_scene_animation.latch!=s_frame.latch_serial) {
        s_scene_animation.latch=s_frame.latch_serial;
        /* Original08C49E checks player X before decrementing its six-update
         * timer. Keep the frozen phase at the gorilla end of the stage. */
        if(rd16(s_frame.ram+0xb21b)<0xa6e) {
            if(s_scene_animation.delay)s_scene_animation.delay--;
            else {s_scene_animation.delay=5;s_scene_animation.phase=(s_scene_animation.phase+1)&3;}
        }
    }
    static FILE *palette_trace;static int palette_opened;static unsigned palette_previous=~0u;
    if(!palette_opened){palette_opened=1;const char *path=getenv("TLK_POSTFIGHT_PALETTE_TRACE");if(path){palette_trace=fopen(path,"w");if(palette_trace)fputs("field,descriptor,phase,delay,rain_flag,actor_phase\n",palette_trace);}}
    if(palette_trace && pride_rock && palette_previous!=s_scene_animation.phase){
        fprintf(palette_trace,"%u,%x,%u,%u,%u,%u\n",snes_frame_counter,descriptor,s_scene_animation.phase,s_scene_animation.delay,rd16(s_frame.ram+0xa6c2),postfight_phase);fflush(palette_trace);palette_previous=s_scene_animation.phase;
    }
    int supported=pride || (level==2 && descriptor==0x3eb) || (level==4 && descriptor==0x44f) ||
                  hakuna || pride_rock || BonusScene() || (level==6 && descriptor==0x4b3) || (level==7 && descriptor==0x4e5) || (level==8 && descriptor==0x517);
    if (!s_frame.stage || !supported || s_bg_level!=(int)level) s_bg_history=0;
    s_bg_level=(int)level;
    if (!s_bg_history) {
        memcpy(s_bg_camera,camera,sizeof s_bg_camera);
        memcpy(s_bg_previous_raster,camera,sizeof s_bg_previous_raster);
        s_bg_last_latch=s_frame.latch_serial;
        s_bg_history=s_frame.stage && supported;
    } else if (!hold && !rd16(s_frame.ram+0x0a89) && (s_bg_last_latch!=s_frame.latch_serial ||
               memcmp(s_bg_previous_raster,camera,sizeof s_bg_previous_raster))) {
        /* Original MD Plane B follows the preceding camera update. Raster
         * origins account for the SNES camera RAM running ahead of its picture.
         * Repeated lag frames and pause retain the previous background phase. */
        memcpy(s_bg_camera,s_bg_previous_raster,sizeof s_bg_camera);
        memcpy(s_bg_previous_raster,camera,sizeof s_bg_previous_raster);
        s_bg_last_latch=s_frame.latch_serial;advanced=1;
    }
    static FILE *trace;static int opened;
    if (!opened) { const char *path=getenv("TLK_BG_TRACE");opened=1;if (path) trace=fopen(path,"w");
        if (trace) fprintf(trace,"frame,latch,stage,level,descriptor,raster_x,raster_y,md_camera_x,md_camera_y,advanced\n"); }
    if (trace) fprintf(trace,"%d,%u,%d,%u,%u,%d,%d,%d,%d,%d\n",snes_frame_counter,s_frame.latch_serial,
                       s_frame.stage,rd16(s_frame.ram+0x1ff9e),descriptor,camera[0],camera[1],s_bg_camera[0],s_bg_camera[1],advanced);
}
/* Optional read-only expanded-view inventory. Absence is evidence to inspect,
 * never permission to resurrect hidden, retired or intentionally blinking art. */
static void SpriteVisibilityLog(int width,int height,int column,int top) {
    static FILE *f;static int opened,last=-1,first=0;extern int snes_frame_counter;
    if(!opened){opened=1;const char *path=getenv("TLK_WIDE_VISIBILITY_LOG");
        const char *from=getenv("TLK_WIDE_VISIBILITY_FROM");if(from)first=atoi(from);
        if(path)f=fopen(path,"w");
        if(f)fputs("field,level,scene,stage,width,height,actor,descriptor,action,packet,pose,flags,x,y,left,top,right,bottom,parts,kept,native_overlap,draw_counter\n",f);}
    if(!f || snes_frame_counter==last || snes_frame_counter<first)return;
    last=snes_frame_counter;const uint8_t *ram=s_frame.ram;
    int cx=s_frame.raster_camera[0],cy=s_frame.raster_camera[1];
    unsigned actor=rd16(ram+0x76);
    for(unsigned step=0;step<96 && actor>=0xb213 && actor<0xdc13 && !((actor-0xb213)&127);step++,actor=rd16(ram+actor+2)) {
        unsigned packet=rd16(ram+actor+12);if(packet<0x8000 || packet>0xffe8 || rd16(ram+packet+4)!=actor+8)continue;
        unsigned pose=rd24(ram+packet+10),at=pose&0x3fffff;
        if((pose>>16)<0xc0 || at+29>s_rom_size)continue;
        int x=(int16_t)rd16(ram+actor+8),y=(int16_t)rd16(ram+actor+10);
        int left=x+(int16_t)rd16(s_rom+at+2),up=y+(int16_t)rd16(s_rom+at+4);
        unsigned w=rd16(s_rom+at+6),h=rd16(s_rom+at+8);if(!w || !h || w>1024 || h>1024)continue;
        int right=left+w,bottom=up+h;
        if(right<=cx-column || left>=cx-column+width || bottom<=cy-top || up>=cy-top+height)continue;
        unsigned parts=0,kept=0;
        for(unsigned n=0;n<s_frame.piece_count;n++)if(s_frame.pieces[n].obj==packet){parts++;kept+=s_frame.pieces[n].kept;}
        fprintf(f,"%d,%u,%06x,%u,%d,%d,%04x,%06x,%06x,%04x,%06x,%04x,%d,%d,%d,%d,%d,%d,%u,%u,%d,%u\n",
            snes_frame_counter,rd16(ram+0x1ff9e),rd24(ram+0xdf),s_frame.stage,width,height,actor,
            rd24(ram+actor+4),rd24(ram+actor+48),packet,pose,rd16(ram+packet+8),x,y,left,up,right,bottom,parts,kept,
            right>cx && left<cx+256 && bottom>cy && up<cy+224,rd16(ram+0xad));
    }
    fflush(f);
}

bool TlkWideEndFrame(const uint8_t *stock) {
    if (!s_enabled) return false;
    ArmInterpreterHooks();   /* idempotent; the bridge's table is runtime state */
    if (s_frame.captured != TLK_WIDE_HEIGHT || !stock) return s_frame.valid = false;
    memcpy(s_frame.stock, stock, sizeof s_frame.stock);
    DisplaySceneContext();
    s_ride_map_viewport=RideViewportWidth();s_ride_exit_shift=RideExitShift();
    s_ride_raster_anchor=-1;
    /* A guest rebase can run after the completed picture's scroll was latched.
     * Unwrap that raster against its producer, not the already advanced RAM
     * camera, which can otherwise pick the neighbouring512-pixel ring. */
    if(rd16(s_frame.ram+0x1ff9e)==1 && rd24(s_frame.ram+0xdf)==0xc003b9 &&
       rd16(s_frame.ram+0xa56) && rd16(s_frame.ram+0xa40)<32 &&
       s_ride_handoff.native_camera>=0 &&
       (int)rd16(s_frame.ram+0xb29b)-s_ride_handoff.native_camera>64)
        s_ride_raster_anchor=s_ride_handoff.native_camera;
    s_frame.stage = DetectStage();
    BackgroundFrame(); /* Every emulated frame, including frames skipped for turbo presentation. */
    PausedGiraffeBudgetParts();
    RideOstrichPresentationParts();
    GraveyardVulturePresentationParts();
    GraveyardLiquidTailParts();
    WaterfallLogCycleParts();
    {static FILE *trace;static int opened;extern int snes_frame_counter;
     if(!opened){opened=1;const char *path=getenv("TLK_PICKUP_VISIBILITY_TRACE");if(path)trace=fopen(path,"w");
         if(trace)fputs("field,actor,descriptor,action,packet,flags,pose,x,y,pieces,stage,camera_x,camera_y,position,top,bottom,left,right,actor_flags\n",trace);}
     if(trace)for(unsigned a=0xb213;a<0xdc13;a+=128){
         unsigned descriptor=rd24(s_frame.ram+a+4),packet=rd16(s_frame.ram+a+12);
         if(descriptor!=0xc586b4 && descriptor!=0xc586c0)continue;
         if(packet<0x8000 || packet>0xffe8)packet=0;
         unsigned pieces=0;for(unsigned i=0;i<s_frame.piece_count;i++)pieces+=s_frame.pieces[i].obj==packet;
         fprintf(trace,"%d,%04x,%06x,%06x,%04x,%04x,%06x,%u,%u,%u,%d,%u,%u,%04x,%u,%u,%u,%u,%04x\n",snes_frame_counter,a,descriptor,rd24(s_frame.ram+a+48),packet,rd16(s_frame.ram+packet+8),rd24(s_frame.ram+packet+10),rd16(s_frame.ram+a+8),rd16(s_frame.ram+a+10),pieces,s_frame.stage,rd16(s_frame.ram+0xb29b),rd16(s_frame.ram+0xb29d),rd16(s_frame.ram+packet+4),rd16(s_frame.ram+0xb1ff),rd16(s_frame.ram+0xb201),rd16(s_frame.ram+0xb203),rd16(s_frame.ram+0xb205),rd16(s_frame.ram+a+0x43));fflush(trace);
     }}
    if(s_frame.stage && rd16(s_frame.ram+0x1ff9e)<=1){
        int level=rd16(s_frame.ram+0x1ff9e);
        const Line *l=WorldPresentationLine(0);int raw=l->hofs[1]&511;
        if(s_panorama_phase_level!=level)s_panorama_phase=raw;
        else s_panorama_phase+=((raw-(s_panorama_phase&511)+256)&511)-256;
        s_panorama_phase_level=level;
    }
    if(s_frame.stage && rd16(s_frame.ram+0x1ff9e)==1 && rd24(s_frame.ram+0xdf)==0xc003b9) {
        int camera=s_frame.raster_camera[0],phase=s_panorama_phase;
        unsigned loop=rd16(s_frame.ram+0xa56),travel=rd16(s_frame.ram+0xa40);
        if(!loop){
            s_ride_handoff.shift=0;s_ride_handoff.background_shift=0;
            int best=256;for(unsigned n=0;n<s_frame.piece_count;n++) {
                const Piece *p=&s_frame.pieces[n];
                if(p->fixed || p->actor_descriptor!=0xc58d80 || p->pose!=0xc07f59)continue;
                int x=((p->attr&0x4000)?p->x+p->local_x+p->size:p->x-p->local_x)+camera;
                int distance=abs(x-(int)rd16(s_frame.ram+0xb21b));
                if(distance>=best)continue;best=distance;
                s_ride_handoff.head_x=x;
                s_ride_handoff.head_y=((p->attr&0x8000)?p->y+p->local_y+p->size+1:p->y-p->local_y)+s_frame.raster_camera[1];
                s_ride_handoff.head_attributes=p->attr>>8;
            }
        }
        else if(s_ride_handoff.camera>=0 && travel<32 && !s_ride_handoff.shift &&
                camera-s_ride_handoff.camera>64 && camera-s_ride_handoff.camera<1024) {
            /* Absorb the complete rebase. Adding eight pixels here makes a
             * visible jump before the gradual pan has even started. */
            s_ride_handoff.shift=camera-s_ride_handoff.camera;
            s_ride_handoff.background_shift=s_ride_handoff.shift-(phase-s_ride_handoff.background);
        }
        s_ride_handoff.camera=camera;s_ride_handoff.background=phase;s_ride_handoff.loop=loop;
        s_ride_handoff.native_camera=rd16(s_frame.ram+0xb29b);
    }else {memset(&s_ride_handoff,0,sizeof s_ride_handoff);s_ride_handoff.camera=s_ride_handoff.native_camera=-1;}
    {static FILE *trace;static int opened;extern int snes_frame_counter;
     if(!opened){opened=1;const char *path=getenv("TLK_WORLD_RASTER_TRACE");if(path)trace=fopen(path,"w");
       if(trace)fputs("field,level,stage,descriptor,player_x,player_y,camera_ram_y,raster_y,brightness,health,action,bad_lines,first_inidisp,last_inidisp,first_tm,last_tm\n",trace);}
     if(trace){unsigned bad=0;for(int y=0;y<224;y++)if((s_frame.lines[y].inidisp&128)||!(s_frame.lines[y].inidisp&15)||!(s_frame.lines[y].tm&1))bad++;fprintf(trace,"%d,%u,%d,%06x,%u,%u,%u,%d,%u,%u,%06x,%u,%u,%u,%u,%u\n",snes_frame_counter,
       rd16(s_frame.ram+0x1ff9e),s_frame.stage,rd24(s_frame.ram+0xdf),rd16(s_frame.ram+0xb21b),
       rd16(s_frame.ram+0xb21d),rd16(s_frame.ram+0xb29d),s_frame.raster_camera[1],s_frame.lines[112].inidisp,
       rd16(s_frame.ram+0x2004),rd24(s_frame.ram+0xb243),bad,s_frame.lines[0].inidisp,s_frame.lines[223].inidisp,s_frame.lines[0].tm,s_frame.lines[223].tm);fflush(trace);}}

    unsigned death_level=rd16(s_frame.ram+0x1ff9e),death_scene=rd24(s_frame.ram+0xdf);
    /* Pride has its own complete owned lifecycle. Stampede's special hero is
     * checked separately; never substitute the regular B213 player for it. */
    if(death_level>=1 && death_level<=9 && death_level!=3 &&
       (death_scene==0xc00387+death_level*50 || (death_level==9 && death_scene==0xc007db)) &&
       rd16(s_frame.ram+0x2000)==(death_level>=6?0xffff:0)) {
        /* Native health is refilled before its death picture is retired.
         * Releasing here on health alone exposes the old reflected corpse
         * and lives HUD on black. Retain the selected MD death canvas until
         * the ordinary world raster is actually back. */
        if(s_gy_death.live && !s_gy_death.active && !s_frame.stage &&
           rd16(s_frame.ram+0x2004) && rd24(s_frame.ram+0xb243)==0xc3857f) {
            /* Water/hazard deaths retire their splash before native health
             * refill. Keep that finished black canvas through level loading;
             * the stale native lives sprite is not a second death animation. */
            s_gy_death.active=1;s_gy_death.age=249;s_gy_death.latch=s_frame.latch_serial;
        } else if(rd16(s_frame.ram+0x2004) && (!s_gy_death.active || s_frame.stage)) {
            int lo,hi,column=ViewColumn(s_frame.ram,s_bg_camera[0],320,&lo,&hi);
            s_gy_death.live=1;s_gy_death.active=0;s_gy_death.age=0;
            s_gy_death.x=(int16_t)(rd16(s_frame.ram+0xb21b)-s_bg_camera[0])+column-160;
            s_gy_death.y=(int16_t)(rd16(s_frame.ram+0xb21d)-s_bg_camera[1]);
            if(s_frame.stage && s_area_view_height>=128 &&
               (s_area_view_width>TlkResourcesViewportForScene(death_level) || s_area_view_height!=224)) {
                /* The death picture uses a fixed224-line canvas, fitted to
                 * the same window. Map the displayed world position into
                 * that canvas before applying the original MD approach.
                 * Keeping world pixels here puts a wide-view corpse beyond
                 * the death screen edge for many updates. This is a change
                 * of display coordinates, not a clamp or a gameplay move. */
                int view_column=ViewColumn(s_frame.ram,s_bg_camera[0],s_area_view_width,&lo,&hi);
                int screen_x=(int16_t)(rd16(s_frame.ram+0xb21b)-s_bg_camera[0])+view_column;
                int screen_y=s_gy_death.y+s_area_view_top;
                s_gy_death.x=(screen_x-s_area_view_width/2)*224/s_area_view_height;
                s_gy_death.y=screen_y*224/s_area_view_height;
            }
            memcpy(s_gy_death.colors,s_frame.lines[112].cgram+128,sizeof s_gy_death.colors);
        /* Spare lives govern the guest's retry/Continue decision. The selected
         * death drawing also applies when the life counter is zero. Retain
         * scene/player/skip guards and leave the guest lifecycle untouched. */
        } else if(s_gy_death.live && !s_gy_death.active && !rd16(s_frame.ram+0xa6ba) &&
                  !rd16(s_frame.ram+0x1ff90) &&
                  (rd24(s_frame.ram+0xb243)==0xc35a82 ||
                   (death_level>=6 && !s_frame.stage && rd24(s_frame.ram+0xb243)==0xc37e76) ||
                   TlkHealthDeathAudioNested(s_frame.ram,death_level>=6))) {
            s_gy_death.active=1;s_gy_death.age=0;s_gy_death.latch=s_frame.latch_serial;
        } else if(s_gy_death.active && s_gy_death.latch!=s_frame.latch_serial) {
            s_gy_death.latch=s_frame.latch_serial;
            if(!rd16(s_frame.ram+0xa89) && s_gy_death.age<249)s_gy_death.age++;
        }
    } else if(death_level==3 && death_scene==0xc0041d && !rd16(s_frame.ram+0x2000)) {
        /* Stampede stores its hero in a separate task. Use the captured,
         * reciprocally owned draw rather than the empty regular-player slot. */
        const Piece *hero=NULL;unsigned action=0;
        for(unsigned i=0;i<s_frame.piece_count;i++) {
            const Piece *p=&s_frame.pieces[i];
            if(p->fixed || p->actor_descriptor!=0xc5858a || !p->kept || p->obj>0xffe8 ||
               DrawActorDescriptor(s_frame.ram,p->obj,p->pose)!=0xc5858a)continue;
            unsigned position=rd16(s_frame.ram+p->obj+4);
            hero=p;action=rd24(s_frame.ram+position-8+0x30);break;
        }
        if(hero && (int16_t)rd16(s_frame.ram+0x2004)>0 &&
           (!s_gy_death.active || (s_frame.lines[112].tm&3))) {
            int lo,hi,column=ViewColumn(s_frame.ram,s_bg_camera[0],320,&lo,&hi);
            s_gy_death.live=1;s_gy_death.active=0;s_gy_death.age=0;
            s_gy_death.x=(hero->attr&0x4000?hero->x+hero->local_x+hero->size-1:hero->x-hero->local_x)+column-160;
            s_gy_death.y=hero->attr&0x8000?hero->y+hero->local_y+hero->size:hero->y-hero->local_y;
            memcpy(s_gy_death.colors,s_frame.lines[112].cgram+128,sizeof s_gy_death.colors);
        } else if(s_gy_death.live && !s_gy_death.active && hero &&
                  (action==0xc45e93 || action==0xc45a5b) &&
                  TlkMdSpritesCubDeathReady(hero->pose,s_frame.ram,sizeof s_frame.ram) &&
                  !rd16(s_frame.ram+0xa6ba)) {
            s_gy_death.active=1;s_gy_death.age=0;s_gy_death.latch=s_frame.latch_serial;
        } else if(s_gy_death.active && s_gy_death.latch!=s_frame.latch_serial) {
            s_gy_death.latch=s_frame.latch_serial;
            if(!rd16(s_frame.ram+0xa89) && s_gy_death.age<249)s_gy_death.age++;
        }
    } else memset(&s_gy_death,0,sizeof s_gy_death);
    TlkCantWaitViewUpdate(&s_cant_wait,s_frame.stage && rd16(s_frame.ram+0x1ff9e)==1 &&
        TlkTitlePointer(s_frame.ram,0xdf)==0xc003b9,
        rd16(s_frame.ram+0x1ffa2) && rd16(s_frame.ram+0x1ffa4)!=66,
        rd16(s_frame.ram+0xa4a),rd16(s_frame.ram+0xa89),s_frame.latch_serial,
        (unsigned)s_frame.raster_camera[0],rd16(s_frame.ram+0xa58));
    return s_frame.valid = true;
}


/* The ordinary non-stage copy retains the native backdrop and HUD. Only the
 * verified shared adult death body is sampled again for its source choices. */
static bool AdultDeathPose(unsigned pose) {
    pose&=0x3fffff;
    for(unsigned i=0;i<sizeof tlk_adult_death_poses/sizeof *tlk_adult_death_poses;i++)
        if(tlk_adult_death_poses[i]==pose)return true;
    return false;
}
static bool AdultDeathFrame(void) {
    const uint8_t *ram=s_frame.ram;unsigned level=rd16(ram+0x1ff9e),draw=rd16(ram+0xb21f);
    unsigned scene=rd24(ram+0xdf),action=rd24(ram+0xb243);
    if(s_frame.stage || level<6 || level>9 || rd16(ram+0x2000)!=0xffff || rd16(ram+0x2004) ||
       (scene!=0xc004b3+(level-6)*0x32 && !(level==9 && scene==0xc007db)) ||
       rd24(ram+0xb217)!=0xc5858a || (action!=0xc35a82 && action!=0xc37e76) ||
       draw<0x8000 || draw>0xffe8 || !AdultDeathPose(rd24(ram+draw+10)))return false;
    uint8_t hash[32];sha256_compute(ram+0x10000,TLK_ADULT_DEATH_BANK_BYTES,hash);
    return !memcmp(hash,tlk_adult_death_bank_sha256,sizeof hash);
}
static void AdultDeathActor(uint32_t *out,int width,int column) {
    int frames=TlkResourcesUseMd("graphics.sprites.simba.adult.frames");
    int palette=TlkResourcesUseMd("graphics.sprites.simba.adult.palette");
    if(GraveyardDeathSelected() || (!frames && !palette && !CustomObjectColours(rd16(s_frame.ram+0x1ff9e))) || !AdultDeathFrame())return;
    for(unsigned remaining=s_frame.piece_count;remaining;remaining--) {
        const Piece *p=&s_frame.pieces[remaining-1];
        if(!p->kept || p->fixed || p->actor_descriptor!=0xc5858a || !CubPiece(p) ||
           ((p->attr>>9)&7) || !AdultDeathPose(p->pose))continue;
        for(int j=0;j<p->size;j++) {
            int dy=p->y+j;if(dy<0 || dy>=TLK_WIDE_HEIGHT)continue;
            const Line *l=&s_frame.lines[dy];
            if((l->inidisp&0x80) || (l->bgmode&7)!=1 || l->tm!=0x10 || l->ts ||
               l->windowsel || l->wlog || l->tmw || l->tsw || l->cgadsub)continue;
            int row=p->attr&0x8000?p->size-1-j:j;unsigned base=(l->obsel&7u)<<13;
            if(p->attr&0x100)base+=((l->obsel&0x18u)+8)<<9;
            const uint16_t *vram=s_vram[l->vram];unsigned bright=l->inidisp&15;
            for(int i=0;i<p->size;i++) {
                int sx=p->x+i,dx=column+sx;if(sx<0 || sx>=256 || dx<0 || dx>=width)continue;
                int uc=p->attr&0x4000?p->size-1-i:i;int pixel;
                if(frames)pixel=TlkMdSpritesPixel(p->pose,p->local_x+uc,p->local_y+row);
                else {
                    unsigned tile=((((p->attr&0xffu)>>4)+((unsigned)row>>3))<<4)|
                                  (((p->attr&15u)+((unsigned)uc>>3))&15u);
                    pixel=(int)TilePixel(vram,base+tile*16,(unsigned)uc&7,(unsigned)row&7,4);
                }
                if(pixel<=0)continue;
                unsigned index=128+(unsigned)pixel,color=l->cgram[index];
                if(palette)color=TlkResourcesCubColor(rd16(s_frame.ram+0x1ff9e),index,l->cgram,(uint16_t)color);
                color=SpriteDeathColor(rd16(s_frame.ram+0x1ff9e),(uint16_t)color);
                unsigned r=color&31,g=(color>>5)&31,b=(color>>10)&31;
                r=(r*8+(r>>2))*bright/15;g=(g*8+(g>>2))*bright/15;b=(b*8+(b>>2))*bright/15;
                out[(size_t)dy*width+dx]=(r<<16)|(g<<8)|b;
            }
        }
    }
}

bool TlkWideDraw(uint32_t *out, int width, bool hud_edges) {
    s_native_md_layout=0;
    /* Source choices apply between frames. Never search all495 resource
     * names for each rain piece on every scanline. */
    s_md_ending_rain=TlkResourcesUseMd("gameplay.levels.pride_rock.rain");
    s_rain_viewport=TlkResourcesViewportForScene(9);
    if (!out || !s_frame.valid || width < 256 || width > TLK_WIDE_MAX_WIDTH || (width & 1)) return false;
    s_area_view_width=width;s_area_view_height=224;s_area_view_top=0;
    if(!++s_panorama_epoch){memset(s_panorama_checked,0,sizeof s_panorama_checked);s_panorama_epoch=1;}
    s_ride_scene=TlkWideFrameOstrichRide();s_ride_map_viewport=RideViewportWidth();s_ride_exit_shift=RideExitShift();
    s_toss_canvas=s_frame.stage && rd16(s_frame.ram+0x1ff9e)==10 && rd24(s_frame.ram+0xdf)==0xc005dd?
        ((TlkResourcesUseMd("gameplay.bonus.bug_toss.arena") || TlkResourcesUseMd("graphics.scenery.foreground") ||
          TlkResourcesUseMd("graphics.scenery.background"))?320:256):0;
    DrawChoicesBegin();
    RidePreviewBegin(width);
    memset(s_pillar_vram,0,sizeof s_pillar_vram);
    s_fallback_enabled=TlkFallbackEnabled();
    if(s_fallback_enabled){extern int snes_frame_counter;
        memset(s_fallback_sprite_valid,0,sizeof s_fallback_sprite_valid);TlkFallbackSpriteContext(NULL);
        TlkFallbackContext((unsigned)snes_frame_counter,rd16(s_frame.ram+0x1ff9e),rd24(s_frame.ram+0xdf));
        s_fallback_all_sprites=TlkResourcesGroupMd("graphics.sprites");
        s_fallback_all_graphics=TlkResourcesGroupMd("graphics");
        static int inventory;
        if(!inventory && (s_fallback_all_graphics || TlkResourcesGroupMd("audio"))) {
            inventory=1;
            for(int i=0;i<TlkResourcesCount();i++) {
                const TlkResourceNode *node=TlkResourcesNode(i);
                if(node && node->leaf && !node->md_supported &&
                   (!strncmp(node->id,"graphics.",9) || !strncmp(node->id,"audio.",6)))
                    TlkFallbackRecord("coverage_gap",node->id,"md_source_not_implemented",0,0,0,1);
            }
        }
    }
    PrepareOpeningCaptions();
    PrepareDestinySkyFace();
    s_cub_death_frame=CubDeathFrame();
    int extra = (width - 256) / 2;
    s_draw_extra = extra;
    memset(&s_stats, 0, sizeof s_stats);
    s_stats.stage = s_frame.stage;
    s_stats.pieces = s_frame.piece_count;
    TlkMdHudSetAdult(rd16(s_frame.ram+0x2000)==0xffff);
    if (rd16(s_frame.ram+0x1ff9e)<=9 &&
        (TlkResourcesHudFramesMd(0) || TlkResourcesHudFramesMd(1) || TlkResourcesHudFramesMd(2)))
        TlkMdHudPrepare((int)rd16(s_frame.ram+0x1ffae),(int)(int16_t)rd16(s_frame.ram+0x2002),
                        (int)rd16(s_frame.ram+0x1ffac),(int)(int16_t)rd16(s_frame.ram+0x2004),rd16(s_frame.ram+0x1ffaa));
    memset(s_hud_present,0,sizeof s_hud_present);
    for (unsigned i=0;i<3;i++) s_hud_slot[i]=128;
    for (unsigned i=0;i<s_frame.piece_count;i++) {
        const Piece *p=&s_frame.pieces[i];int kind=HudMeter(p);
        if (kind>=0 && p->kept && (p->slot&127)<s_hud_slot[kind]) {
            s_hud_slot[kind]=p->slot&127;s_hud_attr[kind]=p->attr;s_hud_present[kind]=1;
        }
    }
    if (s_frame.hud_end>0) {
        s_hud_present[2]=1;s_hud_slot[2]=0;s_hud_attr[2]=s_frame.lines[0].oam[1];
    }
    /* A side takes its margin from the level map only if the map matches the
     * native picture at that edge on every line; else from the PPU's own
     * tilemap ring, as the hardware would show it. */
    s_map_left = s_map_right = s_frame.stage;
    for (int y = 0; y < TLK_WIDE_HEIGHT && (s_map_left || s_map_right); y++) {
        const Line *l = &s_frame.lines[y];
        if (!LineHasStage(l) || (l->inidisp & 0x80) || !(l->tm & 1)) continue;
        const uint16_t *vram = s_vram[l->vram];
        int ox, oy;
        Bg1Origin(l, y, &ox, &oy);
        s_map_left = s_map_left && SeamAgrees(l, vram, y, ox, oy, 0) && SeamAgrees(l, vram, y, ox, oy, 8);
        s_map_right = s_map_right && SeamAgrees(l, vram, y, ox, oy, 247) && SeamAgrees(l, vram, y, ox, oy, 255);
    }
    /* The view stops where the camera stops: at a level's ends the native
     * picture moves off centre instead of the margin showing past the end. */
    int column = extra,fixed_bonus_view=0;
    s_vis_lo = 0;
    s_vis_hi = width;
    for (int y = 0; y < TLK_WIDE_HEIGHT && s_frame.stage; y++) {
        const Line *l = &s_frame.lines[y];
        if (!LineHasStage(l) || (l->inidisp & 0x80)) continue;
        int ox, oy;
        Bg1Origin(l, y, &ox, &oy);
        column = ViewColumn(s_frame.ram, ox, width, &s_vis_lo, &s_vis_hi);
        break;
    }
    if(s_toss_canvas){
        int origin=(width-s_toss_canvas)/2;
        s_vis_lo=origin>0?origin:0;s_vis_hi=origin+s_toss_canvas<width?origin+s_toss_canvas:width;
        column=origin;fixed_bonus_view=1;
    }
    if(!s_toss_canvas && s_frame.stage && rd16(s_frame.ram+0x1ff9e)==10 && BonusScene() && TlkMdSceneReady(10)){
        int foreground=TlkResourcesUseMd("graphics.scenery.foreground");
        int background=TlkResourcesUseMd("graphics.scenery.background") && TlkMdSceneBackgroundReady(10);
        if(foreground || background){
            int origin=(width-320)/2;
            s_vis_lo=origin>0?origin:0;s_vis_hi=origin+320<width?origin+320:width;
            /* World pieces follow the selected foreground's coordinates.
             * A native256 viewport crops the MD scene centrally. */
            if(foreground){column=origin;fixed_bonus_view=1;}
        }
    }
    s_stats.column = column;
    int bg_lo,bg_hi;
    s_bg_view_left=s_bg_camera[0]-ViewColumn(s_frame.ram,s_bg_camera[0],width,&bg_lo,&bg_hi);
    /* HUD sprites the HUD pass places: at the edges, or where they sit in a
     * centred picture when the native one is off centre. */
    memset(s_hud_skip, 0, sizeof s_hud_skip);
    memset(s_hud_side, 0, sizeof s_hud_side);
    s_hud_edges = hud_edges;   /* the reserved slots' side comes from each sprite's x, per line */
    for (int i = 0; i < s_frame.hud_end; i++) s_hud_skip[i] = s_area_active || hud_edges || column != extra;
    for (unsigned i = 0; i < s_frame.piece_count; i++) {
        const Piece *pc = &s_frame.pieces[i];
        if(OpeningCaptionCentre(pc))s_hud_skip[pc->slot&127]=true;
        int motion_side=PickupFlightMotionSide(pc);
        int side = motion_side?motion_side:(hud_edges ? pc->side : 0);
        int dx,dy;ScenePieceShift(pc,&dx,&dy);
        if (pc->fixed && pc->kept && (HudShift(side, width, column) || dx || dy)) {
            s_hud_skip[pc->slot & 127] = true;
            s_hud_side[pc->slot & 127] = (int8_t)side;
        }
    }
    for (int y = 0; y < TLK_WIDE_HEIGHT; y++) {
        uint32_t *row = out + (size_t)y * width;
        const uint32_t *stock = s_frame.stock + y * 256;
        if ((!s_frame.stage || !LineHasStage(&s_frame.lines[y])) && !CubDeathLine(&s_frame.lines[y]) && !StampedeLine(&s_frame.lines[y])) {
            memset(row, 0, (size_t)width * 4);
            /* Fixed loading/title rows keep their native centre. The MD
             * world origin can be negative when cropping to256 pixels. */
            memcpy(row + (fixed_bonus_view?extra:column), stock, 256 * 4);
            s_stats.fallback_lines++;
            if(s_fallback_enabled && s_fallback_all_graphics) {
                unsigned nonblack=0;for(unsigned x=0;x<256;x++)nonblack+=(stock[x]&0x00ffffff)!=0;
                if(nonblack)TlkFallbackRecord("unclassified_canvas","graphics","native_raster_row_before_host_overlays",0,0,0,nonblack);
            }
            continue;
        }
        ComposeLine(row, width, column, y);
        s_stats.custom_lines++;
        /* The oracle: with the HUD where the game put it, the native columns
         * are the PPU's picture. */
        if (!s_area_active && !hud_edges && column == extra)
            for (int x = 0; x < 256; x++) s_stats.native_mismatch += (row[column + x] & 0xFFFFFF) != (stock[x] & 0xFFFFFF);
    }
    GraveyardDeathActor(out,width);
    AdultDeathActor(out,width,column);
    /* Scene-owned installed Timon pictures, independent of source placement.
     * Native fade/lifetime and all guest animation/voice state stay intact. */
    int timon_position=TlkResourcesUseMd("graphics.scenery.timon_start_position");
    int timon_frames=TlkResourcesUseMd("graphics.sprites.cinematics.timon.frames");
    int timon_palette=TlkResourcesUseMd("graphics.sprites.cinematics.timon.palette");
    int timon_timing=TlkResourcesUseMd("graphics.sprites.cinematics.timon.animation");
    if((timon_position || timon_frames || timon_palette || timon_timing) && !s_frame.stage &&
       !rd16(s_frame.ram+0x1ff9e) && rd24(s_frame.ram+0xdf)==0xc005ab &&
       rd24(s_frame.ram+0xb217)==0xc5858a && rd24(s_frame.ram+0xb243)==0xc47146 &&
       rd16(s_frame.ram+0xb21b)==128 && rd16(s_frame.ram+0xb21d)==64) {
        int owned=s_frame.piece_count!=0;
        for(unsigned i=0;i<s_frame.piece_count;i++)
            if(s_frame.pieces[i].fixed || s_frame.pieces[i].actor_descriptor!=0xc5858a ||
               s_frame.pieces[i].pose!=s_frame.pieces[0].pose ||
               ((s_frame.pieces[i].attr>>9)&7))owned=0;
        for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
            const Line *l=&s_frame.lines[y];
            if((l->bgmode&7)!=1 || l->tm!=0x10 || l->ts || l->windowsel || l->wlog ||
               l->tmw || l->tsw || l->cgadsub || (l->cgram[0]&0x7fff))owned=0;
        }
        int handled=0;
        if(owned && (timon_frames || timon_palette || timon_timing || TlkResourcesPaletteCount(0) || TlkResourcesPaletteCount(1)) &&
           TlkInterlevelDataTimonBankMatches(s_frame.ram+0x10000,0x10000)) {
            unsigned phase=rd16(s_frame.ram+0xb241),timer=rd16(s_frame.ram+0xb23f),tick=0;
            int valid=(phase==1 && timer<=18) || (phase==2 && timer<=66) || (phase==3 && timer<=40);
            if(phase==1)tick=18-timer;else if(phase==2)tick=19+66-timer;else if(phase==3)tick=86+40-timer;
            uint8_t brightness[224];for(unsigned y=0;y<224;y++)brightness[y]=(s_frame.lines[y].inidisp&128)?0:s_frame.lines[y].inidisp&15;
            int ox=(width-(timon_position?320:256))/2+128,oy=timon_position?32:64;
            if(valid)handled=TlkInterlevelDataRenderTimonCustom(s_frame.pieces[0].pose,tick,timon_timing,timon_frames,timon_palette,ox,oy,(unsigned)width,s_frame.lines[0].cgram+128,brightness,out);
            if(handled){
                static FILE *trace;const char *path=getenv("TLK_TIMON_PRESENTATION_TRACE");
                if(path && !trace){trace=fopen(path,"w");if(trace)fputs("field,phase,timer,tick,native_pose,selected_pose,frames,palette,timing\n",trace);}
                if(trace){fprintf(trace,"%u,%u,%u,%u,%06x,%u,%d,%d,%d\n",(unsigned)snes_frame_counter+1,phase,timer,tick,s_frame.pieces[0].pose,(unsigned)handled-1,timon_frames,timon_palette,timon_timing);fflush(trace);}
            }
        }
        if(owned && !handled && timon_position) {
            int origin=(width-320)/2;
            memset(out,0,(size_t)width*TLK_WIDE_HEIGHT*sizeof *out);
            for(int y=32;y<TLK_WIDE_HEIGHT;y++)for(int x=0;x<256;x++) {
                int dx=origin+x;if(dx>=0 && dx<width)out[(size_t)(y-32)*width+dx]=s_frame.stock[y*256+x];
            }
            TlkFallbackRecord("native_source_retained","graphics.scenery.timon_start_position",
                "placement_only_native_timon_art_and_animation",0,0,0,1);
        }
    }
    if(!s_area_active)SpriteVisibilityLog(width,224,s_stats.column,0);
    s_draw_choices_active=0;
    return true;
}

bool TlkWideAreaSupported(void) {
    if(s_area_scene_allowed&&!s_area_scene_allowed())return false;
    if(!s_frame.valid||!s_frame.stage||(rd16(s_frame.ram+0x1ff9e)>9 && !HuntScene())||
       (int16_t)rd16(s_frame.ram+0x2004)<=0||CubDeathFrame()||GraveyardDeathSelected())return false;
    unsigned level=rd16(s_frame.ram+0x1ff9e),scene=rd24(s_frame.ram+0xdf);
    if(level==3)return false;
    if(level==6)for(unsigned i=0;i<s_frame.piece_count;i++)if(DestinySkyFacePiece(&s_frame.pieces[i]))return false;
    if(scene!=0xc00387+level*50&&!(level==0&&scene==0xc0080d)&&
       !(level==9&&scene==0xc007db)&&!HuntScene())return false;
    return LineHasStage(&s_frame.lines[112]);
}
bool TlkWideDrawArea(uint32_t *out,int width,int height,bool hud_edges,int *native_row) {
    if(!out||width<256||width>TLK_WIDE_MAX_WIDTH||(width&1)||height<128||height>TLK_WIDE_MAX_VIEW_HEIGHT||!TlkWideAreaSupported())return false;
    if(height==224){if(!(s_area_base_draw?s_area_base_draw(out,width,hud_edges):TlkWideDraw(out,width,hud_edges)))return false;if(native_row)*native_row=0;return true;}
    /* The completed raster can precede the gameplay camera by an update.
     * Use the camera that owns these pixels, matching Bg1Origin and sprites. */
    int camera=s_frame.raster_camera[1],map_height=(int)s_frame.level.rows*16;
    int top=(height-224)/2,origin=camera-top;
    int ride=TlkWideFrameOstrichRide();
    if(ride){origin=map_height-height;top=camera-origin;}
    if(!ride){
    if(map_height>=height){if(origin<0)origin=0;if(origin>map_height-height)origin=map_height-height;}
    else origin=(map_height-height)/2;
    if(height<224){
        origin=(int)rd16(s_frame.ram+0xb21d)-height*7/8;
        if(origin<0)origin=0;if(origin>map_height-height)origin=map_height-height;
    }
    }
    if(height>224){
        unsigned level=rd16(s_frame.ram+0x1ff9e),key=0x80000000u|(level<<10)|(unsigned)height;
        unsigned scene=rd16(s_frame.ram+0xdf)|(rd16(s_frame.ram+0xa56)<<16);
        if(s_free_view_key!=key || s_free_view_scene!=scene){
            s_free_view_key=key;s_free_view_scene=scene;s_free_view_origin=origin;
            memset(s_edge_seen,0,sizeof s_edge_seen);memset(s_edge_count,0,sizeof s_edge_count);
        }else {
            origin=s_free_view_origin;
            if(!ride){
                int player=(int)rd16(s_frame.ram+0xb21d),upper=height/4,lower=height*3/4;
                if(player<origin+upper)origin=player-upper;
                if(player>origin+lower)origin=player-lower;
                if(map_height>=height){if(origin<0)origin=0;if(origin>map_height-height)origin=map_height-height;}
                else origin=(map_height-height)/2;
            }
            s_free_view_origin=origin;
        }
    }
    s_area_top=camera-origin;s_area_height=height;
    s_area_min_y=-camera;s_area_max_y=map_height-camera;s_area_active=1;s_area_sky_edge_valid=0;
    if(!(s_area_base_draw?s_area_base_draw(s_area_base,width,hud_edges):TlkWideDraw(s_area_base,width,hud_edges))){s_area_active=0;return false;}
    DrawChoicesBegin();
    for(int y=0;y<height;y++){
        int source_y=y-s_area_top;
        if(source_y>=0&&source_y<224)memcpy(out+(size_t)y*width,s_area_base+(size_t)source_y*width,(size_t)width*4);
        else ComposeLine(out+(size_t)y*width,width,s_stats.column,source_y);
    }
    if(native_row)*native_row=s_area_top;
    s_area_view_width=width;s_area_view_height=height;s_area_view_top=s_area_top;
    {static FILE *trace;static int opened,last_field=-1;extern int snes_frame_counter;
     if(!opened){opened=1;const char *path=getenv("TLK_FREE_VIEW_TRACE");if(path)trace=fopen(path,"w");
        if(trace)fputs("field,level,width,height,camera_y,origin,player_y,native_row,sky_token,sky_color\n",trace);}
     if(trace && last_field!=snes_frame_counter){last_field=snes_frame_counter;
        fprintf(trace,"%d,%u,%d,%d,%d,%d,%u,%d,%u,%u\n",snes_frame_counter,rd16(s_frame.ram+0x1ff9e),width,height,
            camera,origin,rd16(s_frame.ram+0xb21d),s_area_top,s_area_sky_color,s_frame.lines[0].cgram[s_area_sky_color&255]);fflush(trace);}}
    SpriteVisibilityLog(width,height,s_stats.column,s_area_top);
    s_area_active=0;s_draw_choices_active=0;
    return true;
}

bool TlkWidePreview(uint32_t *out,int width) {
    void *frame=malloc(sizeof s_frame);
    uint8_t *history=malloc(TLK_WIDE_HISTORY_MAX);
    if(!frame || !history){free(frame);free(history);return false;}
    memcpy(frame,&s_frame,sizeof s_frame);
    size_t size=TlkWideSaveHistory(history,TLK_WIDE_HISTORY_MAX);
    bool vram_have=s_vram_have,hold=s_bg_hold_next;
    TlkWideStats stats=s_stats;
    bool ok=TlkWideDraw(out,width,true);
    TlkWideLoadHistory(history,size);
    memcpy(&s_frame,frame,sizeof s_frame);s_vram_have=vram_have;s_bg_hold_next=hold;s_stats=stats;
    free(frame);free(history);return ok;
}
TlkWideStats TlkWideGetStats(void) { return s_stats; }
unsigned TlkWideFrameUpdateSerial(void) { return s_frame.latch_serial; }
const unsigned *TlkWideUpdateSerialSource(void) { return &s_latch_serial; }
bool TlkWideFrameStageActive(void) { return s_frame.valid && s_frame.stage; }

bool TlkWideDumpScene(const char *path) {
    if (!path || !s_frame.valid) return false;
    FILE *f=fopen(path,"w");
    if (!f) return false;
    fprintf(f,"{\n\"checkpoint_adapter\":{\"pixels\":%u,\"fallback_pixels\":%u,\"stale_pieces\":%u},\n",
            s_stats.checkpoint_pixels,s_stats.checkpoint_fallback_pixels,s_stats.checkpoint_stale_pieces);
    fputs("\"sprite_colours\":[",f);int colour_comma=0;
    for(unsigned i=0;i<16384;i++)if(s_sprite_shades[i]){
        unsigned k=s_sprite_shades[i];const TlkResourceNode *n=TlkResourcesNode((int)(k>>16)-1);
        if(n){fprintf(f,"%s[\"%s\",%u,%u]",colour_comma?",":"",n->id,(k>>15)&1,k&32767);colour_comma=1;}
    }fputs("],\n",f);
    fprintf(f,"\"scenery_effects\":{\"native_motion\":%d,\"native_firelight\":%d,\"custom_colours\":%d},\n",s_native_background_motion,s_native_firelight,TlkResourcesPaletteCount(0));
    fprintf(f,"\"editable_colours\":[");for(unsigned t=0;t<3;t++){uint16_t colors[128];int count=TlkWidePaletteColors(t,colors,128);if(t)fputc(',',f);fputc('[',f);for(int i=0;i<count;i++)fprintf(f,"%s%u",i?",":"",colors[i]);fputc(']',f);}fputs("],\n",f);


    fprintf(f,"\"ride_preview\":{\"cursor\":%u,\"drawings\":%u,\"pixels\":%u,\"visible_pixels\":%u,\"items\":[",s_ride_cursor,s_ride_preview_count,s_ride_preview_pixels,s_ride_preview_visible);
    for(unsigned i=0;i<s_ride_preview_count;i++){
        RidePreviewImage *im=&s_ride_images[s_ride_preview[i].image];
        fprintf(f,"%s{\"x\":%d,\"y\":%d,\"pose\":%u,\"bounds\":[%d,%d,%d,%d]}",i?",":"",s_ride_preview[i].x,s_ride_preview[i].y,im->pose,im->left,im->top,im->right,im->bottom);
    }
    fputs("]},\n",f);
    fprintf(f,"\"stampede_canyon\":{\"prepared\":%s,\"clock\":%u,\"phase\":%u},\n",
        StampedeScene() && TlkResourcesUseMd("graphics.scenery.background")?"true":"false",
        rd16(s_frame.ram+0xa40),(rd16(s_frame.ram+0xa40)/5)%3);
    fprintf(f,"\"view_area\":{\"width\":%d,\"height\":%d,\"native_row\":%d,\"height_supported\":%s,\"background_extension\":\"%s\"},\n",s_area_view_width,s_area_view_height,s_area_view_top,TlkWideAreaSupported()?"true":"false",
        s_area_view_height<=224?"source_canvas":
        !TlkResourcesUseMd("graphics.scenery.background") && (rd16(s_frame.ram+0x1ff9e)<=1 || HuntScene())?
            "native_full_panorama_fit":TlkResourcesUseMd("graphics.scenery.background")?
            "genesis_captured_background_fit":"native_banded_panorama_fit");
    fprintf(f,"\"ride_handoff\":{\"column\":%d,\"shift\":%d,\"background_shift\":%d,\"travel\":%u,\"raster_x\":%d},\n",RideHandoffColumn(s_area_view_width),s_ride_handoff.shift,s_ride_handoff.background_shift,rd16(s_frame.ram+0xa40),s_frame.raster_camera[0]);
    fprintf(f,"\"free_camera\":{\"key\":%u,\"origin\":%d,\"scene\":%u,\"sky_token\":%u},\n",s_free_view_key,s_free_view_origin,s_free_view_scene,s_area_sky_color);
    int spawn_top,spawn_bottom;VerticalMargins(&spawn_top,&spawn_bottom);
    fprintf(f,"\"spawn_view\":{\"height\":%d,\"top\":%d,\"bottom\":%d},\n",s_spawn_height,spawn_top,spawn_bottom);
    fprintf(f,"\"foreground_geometry\":\"%s\",\n",s_native_md_layout?"md_layout_native_materials":s_md_layout?"md_layout":"native_layout");
    fprintf(f,"\"foreground_origin_y\":%u,\n",s_md_layout?s_md_layout_y:0);
    fprintf(f,"\"hud_adapter\":{\"frames\":[%d,%d,%d],\"present\":[%d,%d,%d],\"health_max\":%d,\"stampede_bank\":%d},\n",
        s_md_hud_frames[0],s_md_hud_frames[1],s_md_hud_frames[2],s_hud_present[0],s_hud_present[1],s_hud_present[2],
        TlkMdHudHealthMaximum(),StampedeHudPalette(s_frame.lines[16].cgram));
    fprintf(f,"\"schema\":1,\"level\":%u,\"stage_detected\":%s,\"camera\":[%u,%u],\n\"md_background_camera\":[%d,%d],\n",
            rd16(s_frame.ram+0x1ff9e),s_frame.stage?"true":"false",
            rd16(s_frame.ram+0xb29b),rd16(s_frame.ram+0xb29d),s_bg_camera[0],s_bg_camera[1]);
    /* Read-only evidence for the same displayed guest snapshot as the planes;
     * music/graphics verifiers must not infer health or revival from pictures. */
    fprintf(f,"\"latched_gameplay\":{\"descriptor\":%u,\"age\":%u,\"player\":[%u,%u],\"health\":%u,\"lives\":%u,\"checkpoint\":[%u,%u,%u]},\n",
            rd16(s_frame.ram+0xdf),rd16(s_frame.ram+0x2000),
            rd16(s_frame.ram+0xb21b),rd16(s_frame.ram+0xb21d),rd16(s_frame.ram+0x2004),
            rd16(s_frame.ram+0x1ffaa),rd16(s_frame.ram+0x1ffa2),
            rd16(s_frame.ram+0x1ffa4),rd16(s_frame.ram+0x1ffa6));
    fprintf(f,"\"hakuna_waterfall\":{\"active\":%u,\"phase\":%u,\"delay\":%u,\"latch\":%u},\n",
            s_scene_animation.active==5,s_scene_animation.phase,s_scene_animation.delay,s_scene_animation.latch);
    fprintf(f,"\"pride_rock_palette\":{\"active\":%u,\"phase\":%u,\"delay\":%u,\"latch\":%u,\"rain\":%u,\"rain_step\":%u},\n",
            s_scene_animation.active==9,s_scene_animation.phase,s_scene_animation.delay,s_scene_animation.latch,
            s_scene_animation.active==9 && PrideRockRainPhase(s_scene_animation.phase),s_scene_animation.phase&7);
    fprintf(f,"\"cub_death_frame\":%s,\n\"graveyard_death\":{\"active\":%u,\"selected\":%u,\"age\":%u,\"origin_offset_x\":%d,\"origin_y\":%d},\n\"obj_palette0\":[",(CubDeathFrame() || GraveyardDeathSelected())?"true":"false",s_gy_death.active,GraveyardDeathSelected(),s_gy_death.age,s_gy_death.x,s_gy_death.y);
    for(unsigned i=0;i<16;i++)fprintf(f,"%s%u",i?",":"",s_frame.lines[0].cgram[128+i]);
    fprintf(f,"],\n\"obj_palettes\":[");
    for(unsigned i=128;i<256;i++)fprintf(f,"%s%u",i==128?"":",",s_frame.lines[0].cgram[i]);
    fprintf(f,"],\n\"lines\":[\n");
    for (int y=0;y<TLK_WIDE_HEIGHT;y++) {
        const Line *l=&s_frame.lines[y];
        fprintf(f,"{\"y\":%d,\"mode\":%u,\"blank\":%s,\"brightness\":%u,\"main\":%u,\"sub\":%u,\"bgsc\":[%u,%u,%u,%u],\"bgchr\":%u,\"scroll\":[",
                y,l->bgmode,l->inidisp&0x80?"true":"false",l->inidisp&15,l->tm,l->ts,
                l->bgsc[0],l->bgsc[1],l->bgsc[2],l->bgsc[3],l->bgchr);
        for (unsigned bg=0;bg<4;bg++) fprintf(f,"[%u,%u]%s",l->hofs[bg],l->vofs[bg],bg==3?"":",");
        fprintf(f,"],\"windows\":[%u,%u,%u,%u,%u,%u,%u],\"math\":[%u,%u,%u]}%s\n",
                l->windowsel,l->wlog,l->w1l,l->w1r,l->w2l,l->w2r,l->tmw | l->tsw<<8,
                l->cgwsel,l->cgadsub,l->fixed,y==TLK_WIDE_HEIGHT-1?"":",");
    }
    fprintf(f,"],\n\"hyena_context_seen\":%u,\n\"pieces\":[\n",s_hyena_context_seen);
    for (unsigned i=0;i<s_frame.piece_count;i++) {
        const Piece *p=&s_frame.pieces[i];unsigned ptr=p->obj<=0xfffa?rd16(s_frame.ram+p->obj+4):0;
        unsigned actor=ptr>=0x8008 && ptr<=0xff88 ? ptr-8 : 0;
        fprintf(f,"{\"object\":%u,\"position_pointer\":%u,\"pose\":%u,\"screen\":[%d,%d],\"local\":[%d,%d],\"size\":%u,\"slot\":%u,\"kept\":%s,\"fixed\":%s,\"palette\":%u,\"attributes\":%u,\"draw_pose\":%u,\"actor_descriptor\":%u,\"captured_descriptor\":%u,\"actor_action\":%u,\"actor_owner\":%u,\"actor_xy\":[%u,%u],\"popup_owner\":%s,\"title_owner\":%s,\"actor_timer\":%u,\"hyena_art_context\":%u,\"actor_cursor\":%u}%s\n",
                p->obj,ptr,p->pose,p->x,p->y,p->local_x,p->local_y,p->size,p->slot,
                p->kept?"true":"false",p->fixed?"true":"false",(p->attr>>9)&7,p->attr,
                p->obj<=0xffe8?rd24(s_frame.ram+p->obj+10):0,
                actor?rd24(s_frame.ram+actor+4):0,p->actor_descriptor,actor?rd24(s_frame.ram+actor+0x30):0,
                actor?rd16(s_frame.ram+actor+12):0,actor?rd16(s_frame.ram+actor+8):0,
                actor?rd16(s_frame.ram+actor+10):0,PickupPopupPiece(p)?"true":"false",TitlePiece(p)?"true":"false",
                actor?rd16(s_frame.ram+actor+0x2c):0,p->hyena_art_context,actor?rd24(s_frame.ram+actor+0x12):0,
                i+1==s_frame.piece_count?"":",");
    }
    fprintf(f,"],\n\"layers\":[\n");
    int saved_foreground=s_md_foreground,saved_background=s_md_background;
    s_md_foreground=s_md_background=0;
    bool ok=true;
    for (unsigned bg=0;bg<3;bg++) {
        char image_path[4096];
        int length=snprintf(image_path,sizeof image_path,"%s.bg%u.ppm",path,bg+1);
        FILE *image=length>0 && (size_t)length<sizeof image_path ? fopen(image_path,"wb") : NULL;
        if (!image) ok=false;
        if (image) fprintf(image,"P6\n256 224\n255\n");
        unsigned enabled=0,decoded=0,opaque=0;
        for (int y=0;y<TLK_WIDE_HEIGHT;y++) {
            const Line *l=&s_frame.lines[y];
            bool active=!(l->inidisp&0x80) && ((l->tm|l->ts)&(1u<<bg));
            /* Other modes need their own decoder. Raw register lines remain
             * available; a black preview must not be mistaken for no layer. */
            bool supported=(l->bgmode&7)==1;
            if (active) enabled++;
            if (active && supported) decoded++;
            for (int x=0;x<256;x++) {
                uint16_t token=active && supported ? BgPixel(l,s_vram[l->vram],bg,x,y,false,0,0,0,256) : 0;
                uint16_t color=token ? l->cgram[token&255] : 0;
                if (token) opaque++;
                uint8_t rgb[3];
                for (unsigned component=0;component<3;component++) {
                    unsigned c=(color>>(component*5))&31;
                    rgb[component]=(uint8_t)((c*8+(c>>2))*(l->inidisp&15)/15);
                }
                if (image && fwrite(rgb,1,3,image)!=3) ok=false;
            }
        }
        if (image && fclose(image)) ok=false;
        fprintf(f,"{\"bg\":%u,\"enabled_lines\":%u,\"decoded_lines\":%u,\"opaque_pixels_before_composition\":%u}%s\n",
                bg+1,enabled,decoded,opaque,bg==2?"":",");
    }
    s_md_foreground=saved_foreground; s_md_background=saved_background;
    fprintf(f,"]}\n");
    if (ferror(f)) ok=false;
    if (fclose(f)) ok=false;
    return ok;
}

#undef TlkResourcesUseMd

int TlkWidePaletteColors(unsigned target,uint16_t *out,int capacity){
 if(!out||capacity<1||target>2||!s_frame.stage)return 0;
 const Line *l=WorldPresentationLine(112);int count=0;
 if(target==2){for(unsigned word=0;word<1024&&count<capacity;word++)if(s_sprite_colour_seen[word])for(unsigned bit=0;bit<32&&count<capacity;bit++)if(s_sprite_colour_seen[word]&(1u<<bit))out[count++]=(uint16_t)(word*32+bit);if(count)return count;}

 int external=target<2&&TlkResourcesUseMd(target?"graphics.scenery.background":"graphics.scenery.foreground");
 uint16_t md[64];int md_ok=TlkMdScenePaletteColors(s_md_level,md);
 for(unsigned i=0;i<(external?64u:128u)&&count<capacity;i++){
  unsigned c=target==2?l->cgram[128+i]:s_cw_scene?(external?s_cw_external[target][i]:s_cw_native_mapped[target][i]):TlkMdSceneModeColor(i,external,external&&md_ok?md[i]:l->cgram[i],s_scenery_palette[target<2?target:0]);
  if(target==2)c=l->cgram[128+i];
  int seen=0;for(int j=0;j<count;j++)if(out[j]==c){seen=1;break;}if(!seen)out[count++]=(uint16_t)c;
 }return count;
}

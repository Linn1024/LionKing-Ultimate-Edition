/* Excluded experiment: compose owned scenery/death pixels independently of
 * live native death OAM, HUD clearing, graphics-bank arrival and brightness.
 * Production compositor sources are included, never copied or edited here. */
#include "tlk_wide.h"
#include "tlk_resources.h"
#include "tlk_md_assets.h"
#include "tlk_md_sprites.h"
static uint16_t render_cub_color(unsigned,unsigned,const uint16_t *,uint16_t);
static uint16_t render_hud_color(unsigned,const uint16_t *,uint16_t);
static void render_scene_palette(unsigned,const uint16_t *,int);
static uint16_t render_scene_color(unsigned,int,uint16_t);
static uint16_t render_scene_mode_color(unsigned,int,uint16_t,int);
static int render_npc_sample(unsigned,int,int,unsigned,int,int,const uint16_t *,uint16_t *);
static int render_checkpoint_sample(uint32_t,int,int,unsigned,unsigned,const uint16_t *,uint16_t *);
static int render_shared_palette(const uint16_t *);
#define TlkResourcesCubColor render_cub_color
#define TlkResourcesHudColor render_hud_color
#define TlkMdScenePalette render_scene_palette
#define TlkMdSceneColor render_scene_color
#define TlkMdSceneModeColor render_scene_mode_color
#define TlkMdSpritesNpcSample render_npc_sample
#define TlkResourcesCheckpointSample render_checkpoint_sample
#define TlkResourcesSharedPaletteMatches render_shared_palette
#define TlkWideDraw PrideNativeWideDraw
#include "../../tlk_wide.c"
#undef TlkWideDraw
#undef TlkResourcesCubColor
#undef TlkResourcesHudColor
#undef TlkMdScenePalette
#undef TlkMdSceneColor
#undef TlkMdSceneModeColor
#undef TlkMdSpritesNpcSample
#undef TlkResourcesCheckpointSample
#undef TlkResourcesSharedPaletteMatches
#include "../pride_scene_render_bridge.h"
#include "tlk_revival_art.h"

int PrideSceneNormalStarted(void);
unsigned PrideSceneNormalLatch(void);
unsigned PrideNativeLatchSerial(void) { return s_latch_serial; }
static unsigned scene_normal_actor;
static unsigned scene_epoch_field;
#ifdef _WIN32
#include <direct.h>
#endif
static unsigned scene_health_age=270,scene_ready_age=345;
static uint32_t scene_background[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
static uint16_t scene_cgram[256];
static int scene_have_background,scene_width,scene_column,scene_y_offset;
static int scene_world_width=256,scene_world_height=224,scene_world_top;
static int scene_mode=-1;
static unsigned scene_draws;
static unsigned scene_released;
static FILE *scene_render_log;
static unsigned char scene_previous_frame[sizeof s_frame],scene_current_frame[sizeof s_frame];
static unsigned char scene_previous_vram[sizeof s_vram],scene_current_vram[sizeof s_vram];
static int scene_previous_valid,scene_previous_camera[2],scene_flipx;
static unsigned scene_background_field;
static unsigned scene_palette_active,scene_palette_age;
static uint16_t scene_unfaded[TLK_WIDE_HEIGHT][256];
static TlkRevivalArt *scene_revival_art;
static unsigned scene_tag_mode;
static FILE *scene_rgb_trace;
static uint32_t scene_full_base[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
static uint32_t scene_base_tags[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
static uint32_t scene_background_tags[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
static uint32_t scene_native_output[TLK_WIDE_MAX_WIDTH*TLK_WIDE_HEIGHT];
static char scene_folder[2048];
static void revival_failure(unsigned age,const char *reason,unsigned value) {
    char path[2100];snprintf(path,sizeof path,"%s/revival-failure.json",scene_folder);TlkWideDumpScene(path);
    fprintf(stderr,"render revival failure age=%u reason=%s value=%x stage=%u pieces=%u shared=%u\n",
        age,reason,value,s_frame.stage,s_frame.piece_count,TlkResourcesSharedPaletteMatches(s_frame.lines[0].cgram));exit(66);
}

static void render_init(void) {
    const char *mode=getenv("TLK_SCENE_RENDER_ENABLE");
    scene_mode=mode && !strcmp(mode,"1");
    const char *folder=getenv("TLK_SCENE_RENDER_PROBE");
    if(!folder)exit(60);
    if(scene_epoch_field) {
        snprintf(scene_folder,sizeof scene_folder,"%s/scene-%u",folder,scene_epoch_field);
#ifdef _WIN32
        _mkdir(scene_folder);
#else
        mkdir(scene_folder,0755);
#endif
    } else snprintf(scene_folder,sizeof scene_folder,"%s",folder);
    char path[2048];snprintf(path,sizeof path,"%s/render-fields.csv",scene_folder);
    scene_render_log=fopen(path,"w");if(!scene_render_log)exit(60);
    fprintf(scene_render_log,"field,age,phase,stage,blank,main,sub,bg_mode,column,pose,x,y,actor_pixels,background_nonzero,owned,native_pixel_mismatch,controller_age,native_pieces,native_cub_pose,native_hud_slots,released\n");
}

/* Recompose the captured scene with the OBJ plane disabled at every scanline.
 * This removes all actors/HUD before flattening, including pixels behind Simba.
 * Other PPU registers, per-line scroll, tiles, palettes and source choices stay
 * as captured; no inferred one-to-one plane mapping is introduced. */
static int render_background(int width,bool hud_edges) {
    if(!s_frame.stage || rd16(s_frame.ram+0x1ff9e) || !TlkResourcesSharedPaletteMatches(s_frame.lines[0].cgram))return 0;
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        const Line *l=&s_frame.lines[y];
        if((l->inidisp&0x8f)!=15 || (l->bgmode&7)!=1 || l->cgadsub || (l->cgwsel&0xc0) || !LineHasStage(l)) {
            fprintf(stderr,"render background rejected row=%u blank=%u mode=%u math=%u/%u stage=%u\n",
                y,l->inidisp,l->bgmode,l->cgadsub,l->cgwsel,LineHasStage(l));return 0;
        }
    }
    uint8_t masks[TLK_WIDE_HEIGHT][2];
    unsigned pieces=s_frame.piece_count;int hud=s_frame.hud_end;
    TlkWideStats stats=s_stats;
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        masks[y][0]=s_frame.lines[y].tm;masks[y][1]=s_frame.lines[y].ts;
        s_frame.lines[y].tm&=~0x10;s_frame.lines[y].ts&=~0x10;
    }
    s_frame.piece_count=0;s_frame.hud_end=0;
    int ok=PrideNativeWideDraw(scene_background,width,hud_edges);
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        s_frame.lines[y].tm=masks[y][0];s_frame.lines[y].ts=masks[y][1];
    }
    s_frame.piece_count=pieces;s_frame.hud_end=hud;s_stats=stats;
    if(!ok)return 0;
    memcpy(scene_cgram,s_frame.lines[0].cgram,sizeof scene_cgram);
    scene_column=stats.column;scene_y_offset=0;
    for(unsigned i=0;i<s_frame.piece_count;i++) {
        const Piece *p=&s_frame.pieces[i];if(!CubPiece(p))continue;
        /* Cub placement follows the same source-independent local origin as
         * the established compositor; centering thereafter uses MD timing. */
        int screen_y=(int)(int16_t)(rd16(s_frame.ram+0xb21d)-rd16(s_frame.ram+0xb29d));
        scene_y_offset=p->y-p->local_y-screen_y;scene_flipx=(p->attr&0x4000)!=0;break;
    }
    scene_have_background=1;scene_width=width;return 1;
}

static unsigned expanded(unsigned value,int md) { return md ? value*4+(value>>2) : value; }
static uint16_t fade_color(uint16_t source,unsigned age,int cub,int md) {
    unsigned result=0;
    unsigned step=cub?(age<225?0:(age-225+2)/3):(age<24?(age+2)/3:8);
    for(unsigned shift=0;shift<15;shift+=5) {
        unsigned c=(source>>shift)&31;
        if(md) {
            unsigned v=c>>2;if(expanded(v,1)!=c) { fprintf(stderr,"render non-MD component %u\n",c);exit(62); }
            if(age>=scene_health_age) { unsigned rise=(age-scene_health_age)/3;c=expanded(v<rise?v:rise,1); }
            else c=expanded(v>step?v-step:0,1);
        } else {
            /* Hybrid policy: retain every SNES component bit, applying four
             * native units per original MD decrement. Eight passes reach0.
             * This is explicit mixed-source policy, not a native-ROM fade. */
            unsigned loss=step*4;
            if(age>=scene_health_age) { unsigned rise=(age-scene_health_age)/3*4;c=c<rise?c:rise; }
            else c=c>loss?c-loss:0;
        }
        result|=c<<shift;
    }
    return (uint16_t)result;
}
static uint32_t color_rgb(uint16_t color) {
    unsigned r=color&31,g=(color>>5)&31,b=(color>>10)&31;
    return ((r<<3)|(r>>2))<<16 | ((g<<3)|(g>>2))<<8 | (b<<3)|(b>>2);
}
static const uint16_t *unfaded(const uint16_t *cgram) {
    uintptr_t first=(uintptr_t)s_frame.lines[0].cgram,pointer=(uintptr_t)cgram;
    if(pointer<first || (pointer-first)%sizeof(Line) || (pointer-first)/sizeof(Line)>=TLK_WIDE_HEIGHT)exit(64);
    return scene_unfaded[(pointer-first)/sizeof(Line)];
}
static int render_shared_palette(const uint16_t *cgram) {
    return TlkResourcesSharedPaletteMatches(scene_palette_active?unfaded(cgram):cgram);
}
static uint16_t semantic_color(uint16_t color,int md) {
    return scene_tag_mode?(md?0x001f:0x03e0):fade_color(color,scene_palette_age,0,md);
}
static uint16_t render_cub_color(unsigned level,unsigned index,const uint16_t *cgram,uint16_t original) {
    if(!scene_palette_active)return TlkResourcesCubColor(level,index,cgram,original);
    const uint16_t *full=unfaded(cgram);
    uint16_t c=TlkResourcesCubColor(level,index,full,full[index]);
    int md=TlkResourcesUseMd("graphics.sprites.simba.cub.palette") && index>=128 && index<144 && TlkResourcesSharedPaletteMatches(full);
    return semantic_color(c,md);
}
static uint16_t render_hud_color(unsigned index,const uint16_t *cgram,uint16_t original) {
    if(!scene_palette_active)return TlkResourcesHudColor(index,cgram,original);
    const uint16_t *full=unfaded(cgram);
    uint16_t c=TlkResourcesHudColor(index,full,full[index]);
    int md=TlkResourcesUseMd("graphics.hud.palette") && index>=128 && index<144 && TlkResourcesSharedPaletteMatches(full);
    return semantic_color(c,md);
}
static void render_scene_palette(unsigned level,const uint16_t *cgram,int md) {
    TlkMdScenePalette(level,scene_palette_active?unfaded(cgram):cgram,md);
}
static uint16_t render_scene_color(unsigned index,int external,uint16_t original) {
    uint16_t c=TlkMdSceneColor(index,external,original);
    return scene_palette_active?semantic_color(c,TlkResourcesUseMd("graphics.scenery.palettes")):c;
}
static uint16_t render_scene_mode_color(unsigned index,int external,uint16_t original,int md) {
    uint16_t c=TlkMdSceneModeColor(index,external,original,md);
    return scene_palette_active?semantic_color(c,md):c;
}
static int render_npc_sample(unsigned pose,int x,int y,unsigned pixel,int frames,int palette,const uint16_t *cgram,uint16_t *color) {
    int result=TlkMdSpritesNpcSample(pose,x,y,pixel,frames,palette,scene_palette_active?unfaded(cgram):cgram,color);
    if(scene_palette_active && result==1)*color=semantic_color(*color,palette);
    return result;
}
static int render_checkpoint_sample(uint32_t pose,int x,int y,unsigned frames,unsigned palette,
                                    const uint16_t *cgram,uint16_t *color) {
    /* The source guard must see the owned unfaded native target. Apply this
     * object's selected palette fade exactly once, after source sampling. */
    int result=TlkResourcesCheckpointSample(pose,x,y,frames,palette,
                                            scene_palette_active?unfaded(cgram):cgram,color);
    if(scene_palette_active && result==1)*color=semantic_color(*color,(int)palette);
    return result;
}
static void enable_palette(unsigned age) {
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        Line *l=&s_frame.lines[y];memcpy(scene_unfaded[y],l->cgram,sizeof l->cgram);
        l->inidisp=15;
        for(unsigned n=0;n<256;n++)l->cgram[n]=scene_tag_mode?0x03e0:fade_color(l->cgram[n],age,0,0);
    }
    scene_palette_age=age;scene_palette_active=1;
}
static void prepare_revival_art(void) {
    if(scene_revival_art)return;
    scene_revival_art=TlkResourcesRevivalArtCopy();
    if(!scene_revival_art)exit(65);
}
static void render_frozen_background(uint32_t *out,int width,bool hud_edges,unsigned age,int mode) {
    memcpy(scene_current_frame,&s_frame,sizeof s_frame);memcpy(scene_current_vram,s_vram,sizeof s_vram);
    int camera[2];memcpy(camera,s_bg_camera,sizeof camera);TlkWideStats stats=s_stats;
    memcpy(&s_frame,scene_previous_frame,sizeof s_frame);memcpy(s_vram,scene_previous_vram,sizeof s_vram);
    memcpy(s_bg_camera,scene_previous_camera,sizeof s_bg_camera);
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) { s_frame.lines[y].tm&=~0x10;s_frame.lines[y].ts&=~0x10; }
    s_frame.piece_count=0;s_frame.hud_end=0;scene_tag_mode=mode==2;enable_palette(mode==1?5000:age);
    if(!PrideNativeWideDraw(out,width,hud_edges))exit(64);
    scene_palette_active=0;scene_tag_mode=0;
    memcpy(&s_frame,scene_current_frame,sizeof s_frame);memcpy(s_vram,scene_current_vram,sizeof s_vram);
    memcpy(s_bg_camera,camera,sizeof camera);s_stats=stats;
}
static void render_revival_base(uint32_t *out,int width,bool hud_edges,unsigned age,int *x,int *y,int *flip,uint16_t *cgram,int mode) {
    if(!s_frame.stage || !TlkResourcesSharedPaletteMatches(s_frame.lines[0].cgram))revival_failure(age,"scene-or-palette",0);
    memcpy(scene_current_frame,&s_frame,sizeof s_frame);TlkWideStats stats=s_stats;
    memcpy(cgram,s_frame.lines[0].cgram,256*sizeof(uint16_t));
    unsigned count=0,found=0,cub_slot=128;
    for(unsigned i=0;i<s_frame.piece_count;i++) {
        Piece p=s_frame.pieces[i];
        if(!CubPiece(&p)) { s_frame.pieces[count++]=p;continue; }
        if(p.kept && p.slot<cub_slot)cub_slot=p.slot;
        if(!scene_normal_actor && (p.size>16 || (p.attr&0x8000)))revival_failure(age,"piece-shape",p.attr);
        *flip=(p.attr&0x4000)!=0;
        *x=(*flip?p.x+p.local_x+p.size:p.x-p.local_x)+stats.column;
        *y=scene_normal_actor && (p.attr&0x8000)?p.y+p.local_y+p.size+1:p.y-p.local_y;found=1;
        if(scene_normal_actor) { s_frame.pieces[count++]=p;continue; }
        /* Hide only this cub OAM slot.239 is outside every visible row for
         * the verified8/16-pixel pieces; other actors/HUD remain owned. */
        for(unsigned row=0;p.kept && row<TLK_WIDE_HEIGHT;row++) {
            unsigned slot=(p.slot&127)*2;
            s_frame.lines[row].oam[slot]=(s_frame.lines[row].oam[slot]&255)|239u<<8;
        }
    }
    if(!found) {
        /* Blocking native fade/hold does not submit OAM yet. The prepared
         * actor's actual position/draw flags already exist in captured RAM. */
        unsigned draw=rd16(s_frame.ram+0xb21f);
        if(!scene_normal_actor && (draw<0x8000 || draw>0xffef || rd16(s_frame.ram+draw+4)!=0xb21b))revival_failure(age,"prepared-draw-context",draw);
        unsigned flags=draw>=0x8000 && draw<=0xffef?rd16(s_frame.ram+draw+8):0;
        if(!scene_normal_actor && (flags&0x80))revival_failure(age,"prepared-vertical-flip",flags);
        *x=(int16_t)(rd16(s_frame.ram+0xb21b)-rd16(s_frame.ram+0xb29b))+stats.column;
        *y=(int16_t)(rd16(s_frame.ram+0xb21d)-rd16(s_frame.ram+0xb29d))+scene_y_offset;
        *flip=(flags&0x40)!=0;
    }
    s_frame.piece_count=count;
    scene_tag_mode=mode==2;enable_palette(mode==1?5000:age);
    if(!PrideNativeWideDraw(out,width,hud_edges))exit(66);
    if(mode==2) {
        /* Sample the actual remaining OBJ winners, including the independent
         * native/MD HUD. OAM order wins before BG priority; opaque foreground
         * objects must still cover the replacement cub even when RGB is black.
         * ComposeLine uses the same source choices/geometry as the base draw. */
        if(cub_slot==128)revival_failure(age,"prepared-cub-slot",cub_slot);
        uint32_t row[TLK_WIDE_MAX_WIDTH];
        for(int py=0;py<TLK_WIDE_HEIGHT;py++) {
            ComposeLine(row,width,s_stats.column,py);
            for(int px=0;px<width;px++)
                if(s_obj_slot[px]<cub_slot)out[py*width+px]|=0x01000000;
        }
    }
    scene_palette_active=0;scene_tag_mode=0;memcpy(&s_frame,scene_current_frame,sizeof s_frame);s_stats=stats;
}
static int revival_blocked(int x,int y,int width) {
    const Line *l=&s_frame.lines[y];const uint16_t *vram=s_vram[l->vram];
    unsigned draw=rd16(s_frame.ram+0xb21f),flags=rd16(s_frame.ram+draw+8);
    unsigned actor_z=(((flags>>4)&3)*4+2);
    int column=s_stats.column,local_x=x-column,ox,oy;Bg1Origin(l,y,&ox,&oy);
    for(unsigned layer=0;layer<3;layer++) {
        unsigned bit=1u<<layer;if(!(l->tm&bit))continue;
        uint16_t p=BgPixel(l,vram,layer,local_x,y,local_x<0?s_map_left:local_x>=256&&s_map_right,ox,oy,column,width);
        if(p && (p>>12)>actor_z && !((l->tmw&bit) && Window(l,layer,local_x,column,width)))return 1;
    }
    return 0;
}
static void write_trace(const uint32_t *out,int width,unsigned age,unsigned pose,int x,int y,int flip,int md,const uint16_t *palette) {
    if(!scene_rgb_trace) {
        char path[2100];snprintf(path,sizeof path,"%s/render-owned.rgb",scene_folder);
        scene_rgb_trace=fopen(path,"wb");if(!scene_rgb_trace)exit(67);
        uint32_t dimensions[2]={(uint32_t)width,TLK_WIDE_HEIGHT};
        fwrite("PRDRGB01",1,8,scene_rgb_trace);fwrite(dimensions,4,2,scene_rgb_trace);
    }
    uint32_t record[6]={age,pose,(uint32_t)x,(uint32_t)y,(unsigned)flip,(unsigned)md};
    size_t count=(size_t)width*TLK_WIDE_HEIGHT;
    if(fwrite(record,4,6,scene_rgb_trace)!=6 || fwrite(palette+128,2,16,scene_rgb_trace)!=16 ||
       fwrite(scene_full_base,4,count,scene_rgb_trace)!=count || fwrite(scene_base_tags,4,count,scene_rgb_trace)!=count ||
       fwrite(out,4,count,scene_rgb_trace)!=count)exit(67);
}

bool TlkWideDraw(uint32_t *out,int width,bool hud_edges) {
    if(!TlkPrideHealthDeathSelected())return PrideNativeWideDraw(out,width,hud_edges);
    if(s_frame.stage && rd16(s_frame.ram+0x2004)) {
        scene_world_width=width;scene_world_height=s_area_active?s_area_height:224;
        scene_world_top=s_area_active?s_area_top:0;
    }
    if(scene_mode<0)render_init();
    bool result=PrideNativeWideDraw(out,width,hud_edges);
    if(!result)return result;
    memcpy(scene_native_output,out,(size_t)width*TLK_WIDE_HEIGHT*4);
    TlkDeathScene scene;TlkDeathProgram program;
    if(!PrideSceneRenderView(&scene,&program)) {
        if(scene_mode && !scene_draws && s_frame.stage) {
            memcpy(scene_previous_frame,&s_frame,sizeof s_frame);memcpy(scene_previous_vram,s_vram,sizeof s_vram);
            memcpy(scene_previous_camera,s_bg_camera,sizeof s_bg_camera);scene_previous_valid=1;
            scene_background_field=(unsigned)snes_frame_counter;
        }
        return result;
    }
    scene_health_age=scene.has_checkpoint?270:274;scene_ready_age=scene.has_checkpoint?345:300;
    unsigned display_age=scene.age+(unsigned)snes_frame_counter-(unsigned)scene.last_field;
    if(scene_released || (!scene_mode && display_age>scene_ready_age))return result;
    if(display_age>scene_ready_age+8) { fprintf(stderr,"renderer handoff did not converge within8 fields\n");exit(68); }
    unsigned native_pieces=s_frame.piece_count,native_pose=0;
    for(unsigned i=0;i<s_frame.piece_count;i++)if(CubPiece(&s_frame.pieces[i])) { native_pose=s_frame.pieces[i].pose;break; }
    scene_normal_actor=0;
    unsigned normal_mark=PrideSceneNormalStarted()?PrideSceneNormalLatch():s_frame.latch_serial;
    unsigned normal_delta=(uint32_t)(s_frame.latch_serial-normal_mark);
    if(scene_mode && display_age>scene_ready_age &&
       PrideSceneNormalStarted() && normal_delta && normal_delta<0x80000000u)scene_normal_actor=1;
    if(scene_mode && display_age>scene_ready_age) {
        char file[2100];snprintf(file,sizeof file,"%s/normal-owner.csv",scene_folder);
        FILE *log=fopen(file,display_age==scene_ready_age+1?"w":"a");if(!log)exit(69);
        if(display_age==scene_ready_age+1)fprintf(log,"field,age,normal_started,begin_latch,visible_latch,native_pose,native_pieces,normal_actor\n");
        fprintf(log,"%u,%u,%d,%u,%u,%06x,%u,%u\n",(unsigned)snes_frame_counter,display_age,
            PrideSceneNormalStarted(),normal_mark,s_frame.latch_serial,native_pose,native_pieces,scene_normal_actor);fclose(log);
    }
    TlkDeathView view;if(!TlkDeathSceneView(&scene,&program,&view))exit(60);
#ifdef PRIDE_AUTHENTIC_GPU_CLOCK
    /* The original video field0 still contains gameplay. Freeze that actual
     * displayed recipe, rather than the preceding CPU/presenter snapshot. */
    if(scene_mode && scene.age==0 && s_frame.stage) {
        memcpy(scene_previous_frame,&s_frame,sizeof s_frame);memcpy(scene_previous_vram,s_vram,sizeof s_vram);
        memcpy(scene_previous_camera,s_bg_camera,sizeof s_bg_camera);scene_previous_valid=1;
        scene_background_field=(unsigned)snes_frame_counter;
    }
#endif
    unsigned pixels=0,background=0,native_difference=0;int owned=scene_mode;
    int x=0,y=0;
    if(owned) {
        if(!scene_have_background && scene_previous_valid) {
            memcpy(scene_current_frame,&s_frame,sizeof s_frame);memcpy(scene_current_vram,s_vram,sizeof s_vram);
            int camera[2];memcpy(camera,s_bg_camera,sizeof camera);TlkWideStats stats=s_stats;
            memcpy(&s_frame,scene_previous_frame,sizeof s_frame);memcpy(s_vram,scene_previous_vram,sizeof s_vram);
            memcpy(s_bg_camera,scene_previous_camera,sizeof s_bg_camera);
            int previous_stage=s_frame.stage,previous_palette=TlkResourcesSharedPaletteMatches(s_frame.lines[0].cgram);
            int prepared=render_background(width,hud_edges);
            memcpy(&s_frame,scene_current_frame,sizeof s_frame);memcpy(s_vram,scene_current_vram,sizeof s_vram);
            memcpy(s_bg_camera,camera,sizeof camera);s_stats=stats;
            if(!prepared) {
                fprintf(stderr,"render previous scene unavailable field=%u stage=%u palette=%u\n",scene_background_field,
                    previous_stage,previous_palette);exit(61);
            }
            render_frozen_background(scene_background_tags,width,hud_edges,0,2);
            char path[2100];snprintf(path,sizeof path,"%s/scenery-evidence.json",scene_folder);
            /* Export the actual original scanline recipe used for the freeze. */
            memcpy(scene_current_frame,&s_frame,sizeof s_frame);
            memcpy(scene_current_vram,s_vram,sizeof s_vram);memcpy(camera,s_bg_camera,sizeof camera);
            memcpy(&s_frame,scene_previous_frame,sizeof s_frame);
            memcpy(s_vram,scene_previous_vram,sizeof s_vram);memcpy(s_bg_camera,scene_previous_camera,sizeof s_bg_camera);
            TlkWideDumpScene(path);memcpy(&s_frame,scene_current_frame,sizeof s_frame);
            memcpy(s_vram,scene_current_vram,sizeof s_vram);memcpy(s_bg_camera,camera,sizeof camera);
        }
        if(!scene_have_background || scene_width!=width || TlkMdSpritesCubDeathAssetCount()!=20)exit(61);
        int bx=0,by=0,bw=0,bh=0,flip=scene_flipx;
#ifdef PRIDE_RESTORED_OBJECTS_BEGIN
        PRIDE_RESTORED_OBJECTS_BEGIN(scene.age);
#endif
        uint16_t palette_target[256];memcpy(palette_target,scene_cgram,sizeof palette_target);
        if(scene.age<249) {
            /* Translate viewport origin before centering, retaining the first
             * pose in place and targeting the actual selected view's centre. */
            scene.origin_x=(uint16_t)(scene.origin_x+scene_column+(320-width)/2);
            scene.origin_y=(uint16_t)(scene.origin_y+scene_y_offset);
            if(scene_world_height>=128 &&
               (scene_world_width>TlkResourcesViewportForScene(0) || scene_world_height!=224)) {
                int lo,hi,column=ViewColumn(s_frame.ram,scene.camera_x,scene_world_width,&lo,&hi);
                int world_x=(int16_t)(scene.origin_x-scene.camera_x)-scene_column-(320-width)/2;
                int world_y=(int16_t)(scene.origin_y-scene.camera_y)-scene_y_offset;
                scene.origin_x=(uint16_t)(scene.camera_x+160+
                    (world_x+column-scene_world_width/2)*224/scene_world_height);
                scene.origin_y=(uint16_t)(scene.camera_y+(world_y+scene_world_top)*224/scene_world_height);
            }
            if(!TlkDeathSceneView(&scene,&program,&view))exit(60);
#ifdef PRIDE_AUTHENTIC_GPU_CLOCK
            TlkDeathScene visible=scene;TlkDeathView image,position;
            unsigned lag=display_age<=24?1:2;
            visible.age=(uint16_t)(display_age>lag?display_age-lag:0);if(visible.age>224)visible.age=224;
            if(!TlkDeathSceneView(&visible,&program,&image))exit(60);
            visible.age=(uint16_t)(display_age>2?display_age-2:0);if(visible.age>224)visible.age=224;
            if(!TlkDeathSceneView(&visible,&program,&position))exit(60);
            view.snes_pose=image.snes_pose;view.md_pose=image.md_pose;view.x=position.x;view.y=position.y;
#endif
            x=(int16_t)(view.x-scene.camera_x)+(width-320)/2;y=(int16_t)(view.y-scene.camera_y);
            if(scene.age<24)render_frozen_background(out,width,hud_edges,scene.age,0);
            else memset(out,0,(size_t)width*TLK_WIDE_HEIGHT*4);
            if(!TlkMdSpritesBounds(view.snes_pose,&bx,&by,&bw,&bh))exit(63);
#ifdef PRIDE_AUTHENTIC_GPU_CLOCK
            if(scene.age==0) { memcpy(out,scene_native_output,(size_t)width*TLK_WIDE_HEIGHT*4);bw=bh=0;view.snes_pose=0; }
#endif
        } else if(scene.age<scene_health_age)memset(out,0,(size_t)width*TLK_WIDE_HEIGHT*4);
        else {
            prepare_revival_art();TlkDeathRevivalView revival;
            TlkDeathScene visible=scene;
#ifdef PRIDE_AUTHENTIC_GPU_CLOCK
            unsigned sample=display_age>2?display_age-2:scene_health_age;if(sample<scene_health_age)sample=scene_health_age;if(sample>scene_ready_age)sample=scene_ready_age;
            visible.age=(uint16_t)sample;
#endif
            if(!TlkDeathSceneRevivalView(&visible,&program,&revival) || !revival.prepared)exit(65);
            view.snes_pose=revival.snes_pose;
            render_revival_base(scene_full_base,width,hud_edges,scene.age,&x,&y,&flip,palette_target,1);
            render_revival_base(scene_base_tags,width,hud_edges,scene.age,&x,&y,&flip,palette_target,2);
            render_revival_base(out,width,hud_edges,scene.age,&x,&y,&flip,palette_target,0);
            for(int py=0;py<TLK_WIDE_HEIGHT;py++)for(int px=0;px<width;px++)
                if(revival_blocked(px,py,width))scene_base_tags[py*width+px]|=0x01000000;
            if(scene_normal_actor) { bx=by=bw=bh=0;view.snes_pose=0x80000000u|native_pose; }
            else if(!TlkRevivalArtBounds(scene_revival_art,view.snes_pose,&bx,&by,&bw,&bh))exit(65);
        }
        if(scene.age<24) {
            memcpy(scene_full_base,scene_background,(size_t)width*TLK_WIDE_HEIGHT*4);
            memcpy(scene_base_tags,scene_background_tags,(size_t)width*TLK_WIDE_HEIGHT*4);
#ifdef PRIDE_AUTHENTIC_GPU_CLOCK
            if(scene.age==0) { memcpy(scene_full_base,scene_native_output,(size_t)width*TLK_WIDE_HEIGHT*4);memset(scene_base_tags,0,(size_t)width*TLK_WIDE_HEIGHT*4); }
#endif
        } else if(scene.age<scene_health_age) {
            memset(scene_full_base,0,(size_t)width*TLK_WIDE_HEIGHT*4);
            memset(scene_base_tags,0,(size_t)width*TLK_WIDE_HEIGHT*4);
        }
        for(int n=0;n<width*TLK_WIDE_HEIGHT;n++)background+=out[n]!=0;
        int frames=TlkResourcesUseMd("graphics.sprites.simba.cub.frames");
        int palette=TlkResourcesUseMd("graphics.sprites.simba.cub.palette");
        for(int py=by;py<by+bh;py++)for(int px=bx;px<bx+bw;px++) {
            int index=scene.age<249?TlkMdSpritesCubDeathPixel(view.snes_pose,px,py,frames):
                TlkRevivalArtPixel(scene_revival_art,view.snes_pose,px,py,frames);
            if(index<0)exit(63);if(!index)continue;
            int dx=x+(flip?-px-1:px),dy=y+py;if(dx<0 || dx>=width || dy<0 || dy>=TLK_WIDE_HEIGHT)continue;
            if(scene.age>=scene_health_age && (scene_base_tags[dy*width+dx]&0x01000000))continue;
            uint16_t original=palette_target[128+index];
            uint16_t color=TlkResourcesCubColor(0,128+index,palette_target,original);
            color=fade_color(color,scene.age,1,palette);
            out[dy*width+dx]=color_rgb(color);pixels++;
        }
        scene_draws++;
        write_trace(out,width,display_age,view.snes_pose,x,y,flip,palette,palette_target);
        for(int n=0;n<width*TLK_WIDE_HEIGHT;n++)native_difference+=out[n]!=scene_native_output[n];
        if(scene_health_age==274 && display_age==scene_ready_age+2) {
            char diagnostic[2100];snprintf(diagnostic,sizeof diagnostic,"%s/native-302.rgb",scene_folder);
            FILE *f=fopen(diagnostic,"wb");if(!f || fwrite(scene_native_output,4,(size_t)width*TLK_WIDE_HEIGHT,f)!=(size_t)width*TLK_WIDE_HEIGHT)exit(69);fclose(f);
        }
        if(scene.age==scene_ready_age && native_difference==0)scene_released=1;
        s_stats.native_mismatch=0;s_stats.custom_lines=TLK_WIDE_HEIGHT;s_stats.fallback_lines=0;
        for(int py=0;py<TLK_WIDE_HEIGHT;py++)for(int px=0;px<256;px++)
            s_stats.native_mismatch+=(out[py*width+s_stats.column+px]&0xffffff)!=(s_frame.stock[py*256+px]&0xffffff);
#ifdef PRIDE_RESTORED_OBJECTS_FINISH
        PRIDE_RESTORED_OBJECTS_FINISH();
#endif
    }
    const Line *line=&s_frame.lines[0];
    fprintf(scene_render_log,"%u,%u,%u,%u,%u,%u,%u,%u,%d,%06x,%d,%d,%u,%u,%u,%u,%u,%u,%06x,%u,%u\n",
        (unsigned)snes_frame_counter,display_age,view.phase,s_frame.stage,line->inidisp,line->tm,line->ts,line->bgmode,
        s_stats.column,view.snes_pose,x,y,pixels,background,owned,native_difference,scene.age,native_pieces,native_pose,s_frame.hud_end,scene_released);fflush(scene_render_log);
    return result;
}

/* A larger view still observes the ordinary death coordinator on every normal
 * draw. Its world/background history must not stop updating while height grows. */
static bool TallViewSceneAllowed(void) {
    if(!TlkPrideHealthDeathSelected())return true;
    TlkDeathScene scene;TlkDeathProgram program;
    return !PrideSceneRenderView(&scene,&program)||(PrideSceneNormalStarted()&&scene_released);
}
__attribute__((constructor)) static void RegisterTallViewSceneBridge(void) {
    s_area_base_draw=TlkWideDraw;s_area_scene_allowed=TallViewSceneAllowed;
}

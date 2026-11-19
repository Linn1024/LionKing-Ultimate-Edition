/* Excluded presenter ownership of the real pre-fade draw batch and full native
 * widget art. All edits are to owned raster snapshots; never to guest state. */
static void restored_objects_begin(unsigned age);
static void restored_objects_finish(void);
#define PRIDE_RESTORED_OBJECTS_BEGIN restored_objects_begin
#define PRIDE_RESTORED_OBJECTS_FINISH restored_objects_finish
#define PRIDE_AUTHENTIC_GPU_CLOCK 1
#include "pride_repeat_render_wide.c"
#include "tlk_native_hud.h"

static Piece prepared_pieces[kMaxPieces];
static unsigned char prepared_cub[kMaxPieces];
static unsigned prepared_count,prepared_hud,prepared_age,prepared_changed;
static uint8_t prepared_health[512],prepared_roar[512];
static unsigned char prepared_frame[sizeof s_frame],prepared_vram[sizeof s_vram];
static TlkNativeHud *prepared_native_hud;
static FILE *prepared_events;
static FILE *prepared_font_trace;
void PrideRepeatRenderBegin(unsigned field) {
    if(!scene_have_background && !scene_draws && !scene_rgb_trace)return;
    if(prepared_changed || scene_palette_active || scene_tag_mode)exit(92);
    if(scene_render_log)fclose(scene_render_log);scene_render_log=NULL;
    if(scene_rgb_trace)fclose(scene_rgb_trace);scene_rgb_trace=NULL;
    if(prepared_events)fclose(prepared_events);prepared_events=NULL;
    if(prepared_font_trace)fclose(prepared_font_trace);prepared_font_trace=NULL;
    scene_epoch_field=field;scene_mode=-1;scene_draws=scene_released=0;
    scene_have_background=scene_previous_valid=scene_normal_actor=0;
    prepared_count=prepared_hud=prepared_age=0;
    memset(prepared_pieces,0,sizeof prepared_pieces);memset(prepared_cub,0,sizeof prepared_cub);
    memset(prepared_health,0,sizeof prepared_health);memset(prepared_roar,0,sizeof prepared_roar);
}
static void trace_installed_font(unsigned age,unsigned kind,unsigned maximum,unsigned current,unsigned initial) {
    unsigned attr=0;int x0=0,y0=0,found=0;
    for(unsigned n=0;n<s_frame.piece_count;n++) {
        const Piece *p=&s_frame.pieces[n];if(HudMeter(p)!=(int)kind)continue;
        attr=(p->attr&~255u)|((p->attr&255)-(unsigned)p->local_x/8);
        x0=p->x-p->local_x;y0=p->y-p->local_y;found=1;break;
    }
    if(!found || y0<0 || y0+16>TLK_WIDE_HEIGHT || (attr&0xc000))exit(76);
    uint8_t indices[1024];
    for(unsigned y=0;y<16;y++) {
        const Line *l=&s_frame.lines[y0+y];unsigned base=(l->obsel&7)<<13;
        if(attr&256)base+=((l->obsel&0x18)+8)<<9;
        const uint8_t *vram=(const uint8_t *)s_vram[l->vram];
        for(unsigned x=0;x<64;x++) {
            unsigned tile=(attr&255)+y/8*16+x/8;
            unsigned at=((base+tile*16)&32767)*2+(y&7)*2,c=0;
            for(unsigned plane=0;plane<4;plane++)c|=((vram[at+(plane&1)+(plane>=2?16:0)]>>(7-(x&7)))&1)<<plane;
            indices[y*64+x]=(uint8_t)c;
        }
    }
    if(!prepared_font_trace) {
        char path[2100];snprintf(path,sizeof path,"%s/prepared-fonts.bin",scene_folder);
        prepared_font_trace=fopen(path,"wb");if(!prepared_font_trace)exit(76);
        fwrite("PRDHUD01",1,8,prepared_font_trace);
    }
    uint32_t header[]={age,kind,maximum,current,initial,(unsigned)x0,(unsigned)y0};
    if(fwrite(header,4,7,prepared_font_trace)!=7 || fwrite(indices,1,sizeof indices,prepared_font_trace)!=sizeof indices)exit(76);
    fflush(prepared_font_trace);
}
static void prepared_log(unsigned age,unsigned staged,unsigned health,unsigned roar,unsigned current,unsigned initial) {
    if(!prepared_events) {
        char path[2100];snprintf(path,sizeof path,"%s/prepared-objects.csv",scene_folder);
        prepared_events=fopen(path,"w");if(!prepared_events)exit(75);
        fprintf(prepared_events,"field,age,source_age,staged_pieces,health_max,roar_max,roar_current,roar_initial_full\n");
    }
    fprintf(prepared_events,"%u,%u,%u,%u,%u,%u,%u,%u\n",(unsigned)snes_frame_counter,age,prepared_age,staged,health,roar,current,initial);fflush(prepared_events);
}
static void place_piece(const Piece *p) {
    if(p->size!=8 && p->size!=16)exit(75);
    unsigned slot=p->slot&127,shift=(slot&3)*2;
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        Line *l=&s_frame.lines[y];if((l->obsel>>5)!=0)exit(75);
        unsigned high=(unsigned)p->x>>8&1;unsigned size=p->size==16;
        l->oam[slot*2]=(uint16_t)((p->x&255)|((p->kept?p->y:239)&255)<<8);
        l->oam[slot*2+1]=p->attr;
        l->hoam[slot/4]=(uint8_t)((l->hoam[slot/4]&~(3u<<shift))|((high|size<<1)<<shift));
    }
}
static void install_font(unsigned kind,const uint8_t font[512]) {
    int found=0;unsigned attr=0;
    for(unsigned n=0;n<s_frame.piece_count;n++) {
        Piece *p=&s_frame.pieces[n];if(HudMeter(p)!=(int)kind)continue;
        if(p->size!=16 || p->local_y || p->local_x<0 || p->local_x>48 || (p->local_x&15) || (p->attr&0xc000))exit(76);
        unsigned first=(p->attr&255)-(unsigned)p->local_x/8;
        if(!found) { attr=(p->attr&~255u)|first;found=1; }
        else if(attr!=((p->attr&~255u)|first))exit(76);
        if(kind==TLK_NATIVE_HUD_HEALTH) {
            unsigned maximum=rd16(s_frame.ram+0x1ffac);
            p->x=(int16_t)(240-4*(maximum+4)+p->local_x);
            p->kept=p->x>=-15 && p->x<256 && p->y>=-15 && p->y<239;
            /* A clipped native piece never consumed this OAM slot: the next
             * visible owner may already use it. Only submitted pieces own it. */
            if(p->kept)place_piece(p);
        }
    }
    if(!found)exit(76);
    for(unsigned y=0;y<TLK_WIDE_HEIGHT;y++) {
        const Line *l=&s_frame.lines[y];unsigned base=(l->obsel&7)<<13;
        if(attr&256)base+=((l->obsel&0x18)+8)<<9;
        for(unsigned row=0;row<2;row++)for(unsigned column=0;column<8;column++) {
            unsigned tile=(attr&255)+row*16+column;
            unsigned at=(base+tile*16)&32767;
            memcpy(&s_vram[l->vram][at],font+row*256+column*32,32);
        }
    }
}
static void restored_objects_begin(unsigned age) {
    if(age>=254 && age<scene_health_age && s_frame.piece_count && s_frame.stage) {
        int health=0,roar=0,cub=0;
        for(unsigned n=0;n<s_frame.piece_count;n++) {
            health+=HudMeter(&s_frame.pieces[n])==1;roar+=HudMeter(&s_frame.pieces[n])==0;cub+=CubPiece(&s_frame.pieces[n]);
        }
        if(health!=4 || roar!=4 || !cub)
            fprintf(stderr,"default staged batch age=%u pieces=%u health=%d roar=%d cub=%d\n",age,s_frame.piece_count,health,roar,cub);
        if(health==4 && roar==4 && cub) {
            memcpy(prepared_pieces,s_frame.pieces,s_frame.piece_count*sizeof(Piece));prepared_count=s_frame.piece_count;
            for(unsigned n=0;n<prepared_count;n++)prepared_cub[n]=(unsigned char)CubPiece(&s_frame.pieces[n]);
            prepared_hud=s_frame.hud_end;prepared_age=age;
            memcpy(prepared_health,s_frame.ram+0x2230,512);memcpy(prepared_roar,s_frame.ram+0x2030,512);
        }
    }
    if(age<scene_health_age)return;
    if(!prepared_count || prepared_age<254 || prepared_age>=scene_health_age) {
        fprintf(stderr,"default prepared batch unavailable age=%u count=%u source_age=%u\n",age,prepared_count,prepared_age);exit(75);
    }
    if(!prepared_native_hud) { prepared_native_hud=TlkResourcesNativeHudCopy();if(!prepared_native_hud)exit(75); }
    unsigned health=rd16(s_frame.ram+0x1ffac),roar=rd16(s_frame.ram+0x1ffae);
    unsigned current=rd16(s_frame.ram+0x2002);
    if(rd16(s_frame.ram+0x2004)!=health || current>roar)exit(75);
    uint8_t health_font[512],roar_font[512];
    uint16_t initial=0;
    if(!TlkNativeHudRestored(prepared_native_hud,1,health,prepared_health,health_font))exit(75);
    if(current==roar) {
        if(!TlkNativeHudRestored(prepared_native_hud,0,roar,prepared_roar,roar_font))exit(75);
    } else {
        if(!PrideSceneRestoreRoarContext(roar,current,&initial)) {
            fprintf(stderr,"prepared roar context unavailable age=%u maximum=%u current=%u\n",age,roar,current);exit(75);
        }
        if(!TlkNativeHudRoarCurrent(prepared_native_hud,roar,current,initial,prepared_roar,roar_font))exit(75);
    }
    memcpy(prepared_frame,&s_frame,sizeof s_frame);memcpy(prepared_vram,s_vram,sizeof s_vram);prepared_changed=1;
    unsigned staged=0;
    if(!s_frame.piece_count) {
        s_frame.piece_count=0;
        for(unsigned n=0;n<prepared_count;n++)if(!scene_normal_actor || !prepared_cub[n])s_frame.pieces[s_frame.piece_count++]=prepared_pieces[n];
        s_frame.hud_end=(int)prepared_hud;staged=s_frame.piece_count;
        for(unsigned n=0;n<s_frame.piece_count;n++)if(s_frame.pieces[n].kept)place_piece(&s_frame.pieces[n]);
    }
    install_font(1,health_font);install_font(0,roar_font);prepared_log(age,staged,health,roar,current,initial);
    trace_installed_font(age,1,health,health,0);trace_installed_font(age,0,roar,current,initial);
}
static void restored_objects_finish(void) {
    if(!prepared_changed)return;
    memcpy(&s_frame,prepared_frame,sizeof s_frame);memcpy(s_vram,prepared_vram,sizeof s_vram);prepared_changed=0;
}

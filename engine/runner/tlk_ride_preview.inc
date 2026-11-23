#include "tlk_cant_wait_data.h"
#include "tlk_md_camera.h"
/* Show the original finite ride-script drawings before their actors are due.
 * No actor allocation, event advancement, collision or guest writes occur here.
 * BB80 places each descriptor at floor(camera/16)*16 + the selected offset;
 * A40 advances with that camera, including its original 512-coordinate wraps. */
typedef struct RidePreviewImage {
    unsigned pose,pieces;
    int left,top,right,bottom;
    uint8_t pixel[192*192];
} RidePreviewImage;
static RidePreviewImage s_ride_images[6]={{0xc45a16},{0xc3b6f7},{0xc3b756},{0xc3b77b},{0xc3b7f2},{0xc07f59}};
static uint8_t s_ride_image_bank[0x2000];
static int s_ride_images_ready;
static struct {int x,y;unsigned image,bank,flags;} s_ride_preview[64];
static unsigned s_ride_preview_count,s_ride_preview_pixels,s_ride_preview_visible;

static void RidePreviewDecode(void) {
    if(s_ride_images_ready && !memcmp(s_ride_image_bank,s_frame.ram+0x3000,sizeof s_ride_image_bank))return;
    memcpy(s_ride_image_bank,s_frame.ram+0x3000,sizeof s_ride_image_bank);
    s_ride_images_ready=1;
    for(unsigned image=0;image<6;image++) {
        RidePreviewImage *out=&s_ride_images[image];
        memset(out->pixel,0,sizeof out->pixel);out->left=out->top=192;out->right=out->bottom=0;
        out->pieces=0;
        unsigned at=out->pose&0x3fffff;if(at+29>s_rom_size)continue;
        const uint8_t *h=s_rom+at;unsigned flags=rd16(h),slots=flags&127;
        if(!(flags&0x8000) || !slots || slots>32)continue;
        unsigned large=flags&0x4000?(flags>>8)&63:slots,count=large*4;
        for(unsigned i=0;i<64;i++) {
            unsigned size=i<large?16:8;
            if(i>=large && (!(flags&0x4000) || count>=slots*4))break;
            if(at+29+i*4+4>s_rom_size)break;
            const uint8_t *q=h+29+i*4;if(rd16(q)==0xaaaa)break;
            Piece piece={0};piece.pose=out->pose;piece.size=size;
            piece.local_x=(int16_t)rd16(q);piece.local_y=(int16_t)rd16(q+2);
            unsigned source,stride;
            if(!RidePieceSource(&piece,image==5?TLK_MD_SPRITE_CW_GIRAFFE:TLK_MD_SPRITE_CW_RIDE_OBSTACLE,&source,&stride))break;
            out->pieces++;
            for(unsigned y=0;y<size;y++)for(unsigned x=0;x<size;x++) {
                unsigned a=source+x/8*32+y/8*stride+(y&7)*2,bit=7-(x&7);
                int p0=CapturedByte(a),p1=CapturedByte(a+1),p2=CapturedByte(a+16),p3=CapturedByte(a+17);
                if(p0<0||p1<0||p2<0||p3<0)continue;
                unsigned pixel=((p0>>bit)&1)|((p1>>bit)&1)<<1|((p2>>bit)&1)<<2|((p3>>bit)&1)<<3;
                int dx=piece.local_x+(int)x+96,dy=piece.local_y+(int)y+96;
                if(!pixel || dx<0||dx>=192||dy<0||dy>=192)continue;
                out->pixel[dy*192+dx]=pixel;
                if(dx<out->left)out->left=dx;if(dx+1>out->right)out->right=dx+1;
                if(dy<out->top)out->top=dy;if(dy+1>out->bottom)out->bottom=dy+1;
            }
            if(i>=large)count++;
        }
    }
}
static int RidePreviewSubmitted(unsigned image,int x) {
    const RidePreviewImage *drawing=&s_ride_images[image];
    unsigned count=0;
    for(unsigned i=0;i<s_frame.piece_count;i++) {
        const Piece *p=&s_frame.pieces[i];
        if(p->fixed || p->pose!=drawing->pose)continue;
        int origin=(p->attr&0x4000)?p->x+p->local_x+p->size:p->x-p->local_x;
        if(abs(origin-x)<=16)count++;
    }
    return drawing->pieces && count>=drawing->pieces;
}
/* The parser tests once per completed camera update, then floors that
 * camera to16 pixels. Interpolating directly to the event distance can land
 * on the previous tile: the actual four-pixel ride tick crosses the threshold
 * a few pixels later. Forecast the selected MD camera arithmetic without
 * running any guest instructions or changing actors. Camera/player wraps are
 * equal512 translations, so unwrapped coordinates retain the same phase. */
static int RidePreviewEventCamera(unsigned distance,unsigned travel,unsigned lead,int camera) {
    if(!TlkResourcesUseMd("gameplay.camera"))return camera+(int)distance-(int)travel;
    const uint8_t *ram=s_frame.ram;
    if(distance<=travel+lead)
        return camera+(int)distance-(int)travel+(int)((travel+lead-distance)&3);
    unsigned native,external;
    if(!TlkCantWaitRideValue(2,&native,&external))return camera+(int)distance-(int)travel;
    TlkMdCameraState state={camera,0,(int)rd16(ram+0xb293+42),0,rd16(ram+0xb293+38),0};
    int minimum=ram[0xa3e]?128:(int)external;
    TlkMdCameraRules rules={-65536,65536,-65536,65536,minimum,192,0,0,0,0,1};
    int player=rd16(ram+0xb21b);
    for(unsigned step=0;step<256 && travel+lead<distance;step++) {
        int old=state.x;player+=4;
        TlkMdCameraStep(&state,&rules,player,0,0,0,0);
        if(state.x<old)return camera+(int)distance-(int)travel;
        travel+=(unsigned)(state.x-old);
    }
    if(travel+lead<distance)return camera+(int)distance-(int)rd16(ram+0xa40);
    return state.x+(int)lead;
}
static void RidePreviewBegin(int width) {
    s_ride_preview_count=0;s_ride_preview_pixels=0;s_ride_preview_visible=0;
    if(!s_ride_scene || s_spawn_lead<=0 || width<=RideViewportWidth())return;
    int lo,hi,column=ViewColumn(s_frame.ram,s_frame.raster_camera[0],width,&lo,&hi);
    unsigned cursor=s_ride_cursor,travel=rd16(s_frame.ram+0xa40);
    /* Include the just-due event until its complete drawing is captured.
     * A script decision precedes the first submitted sprite packet. */
    if(cursor>=0xc4e1b9 && cursor<=0xc4e23d)
        cursor=cursor>=0xc4e1f1?0xc4e1f1:0xc4e1b9;
    unsigned offset=320,native,external;
    int md=TlkResourcesUseMd("gameplay.levels.cant_wait.ostrich_obstacles");
    if(md && TlkCantWaitRideValue(1,&native,&external))offset=external;
    unsigned lead=(unsigned)(TlkResourcesViewportForScene(1)-256);lead=(lead+15)&~15u;
    int camera=(int)rd16(s_frame.ram+0xb29b);
    RidePreviewDecode();
    for(unsigned event=0;event<32 && cursor+4<=0xc4e23d;event++,cursor+=4) {
        if(cursor<0xc4e1b9 || (cursor&0x3fffff)+4>s_rom_size)break;
        unsigned distance=rd16(s_rom+(cursor&0x3fffff)),flags=rd16(s_rom+(cursor&0x3fffff)+2);
        if(md && !TlkCantWaitRideEvent(cursor,&distance,&flags))break;
        if(flags&0x8000)break;
        /* The original actor retires soon after Simba passes it. Its static
         * drawing can still be visible in the expanded presentation. Project
         * that same script event until the drawing leaves the visible edge;
         * do not retain an actor, collision, or advance the script. */
        int x=(RidePreviewEventCamera(distance,travel,lead,camera)&~15)+(int)offset-s_frame.raster_camera[0];
        if(x+column-96>=width)break;
        if(x+column+96<=0)continue;
        static const unsigned desc[4]={0xc4e1ae,0xc4e1a3,0xc4e198,0xc4e18d};
        /* The original draw queue visits branch collision pieces, then the
         * co-located ground obstacle, then the branch's visual child. Drawing
         * each parent/child pair together puts the visual branch over the
         * rhino's ears until its real actor arrives. Keep this per-event order
         * for both artwork choices, matching actual native OAM ownership. */
        for(unsigned pass=0;pass<3;pass++)for(unsigned bit=0;bit<4;bit++)if(flags&(1u<<bit)) {
            if((bit==3)!=(pass==1))continue;
            unsigned d=desc[bit]&0x3fffff,bank=pass==2?1:(s_rom[d+3]>>1)&7;
            int y=(int)rd16(s_rom+d+6)-s_frame.raster_camera[1]+1;
            unsigned image=bit==3?0:pass==0?(bit==1?4:2):(bit==1?3:1);
            if(s_ride_preview_count>=64)break;
            if(distance<=travel+lead && RidePreviewSubmitted(image,x))continue;
            unsigned j=s_ride_preview_count++;
            s_ride_preview[j].x=x;s_ride_preview[j].y=y;
            s_ride_preview[j].image=image;s_ride_preview[j].bank=bank;
            s_ride_preview[j].flags=s_rom[d+3]&0xc0;
        }
    }
    /* The ordinary entrance retires its static head once the console camera
     * leaves it. Wide handoff framing can still show the painted BG1 neck.
     * Retain the last captured original flat head at that exact world anchor,
     * only until it leaves this view; no actor/platform is kept alive. */
    /* The camera rebases by512 on the first road wrap. Its entrance is now
     * behind that ring, not another head ahead of Simba. BG1 has already
     * replaced the entrance body with the running strip at this boundary. */
    int local_camera=(int)rd16(s_frame.ram+0xb29b)-(int)rd16(s_frame.ram+0xa56);
    int entrance_wrapped=local_camera>=0 && travel>(unsigned)local_camera;
    if(!entrance_wrapped && RideHandoffWeight() && s_ride_handoff.shift && s_ride_handoff.head_attributes && s_ride_preview_count<64) {
        int x=s_ride_handoff.head_x-s_frame.raster_camera[0];
        if(x+column-96<width && x+column+96>0 && !RidePreviewSubmitted(5,x)) {
            unsigned j=s_ride_preview_count++;
            s_ride_preview[j].x=x;s_ride_preview[j].y=s_ride_handoff.head_y-s_frame.raster_camera[1];
            Piece attachment={.pose=0xc07f59,.actor_descriptor=0xc58d80};int dx,dy;
            GiraffeSceneryShift(&attachment,&dx,&dy);s_ride_preview[j].x+=dx;s_ride_preview[j].y+=dy;
            s_ride_preview[j].image=5;s_ride_preview[j].bank=(s_ride_handoff.head_attributes>>1)&7;
            s_ride_preview[j].flags=s_ride_handoff.head_attributes&0xc0;
        }
    }
    if(s_ride_exit_shift>=0 && s_ride_preview_count<64){
        /* The two source exit markers are flat C58D80 heads at2768/4288,
         * Y288: loop base + selected viewport +560. Their bodies are BG1.
         * Keep a projected drawing until the real final-ring actor submits. */
        int world=(int)rd16(s_frame.ram+0xa56)+RideViewportWidth()+560;
        int owned=0;
        if(!s_ride_exit_shift)for(unsigned i=0;i<s_frame.piece_count;i++){
            const Piece *p=&s_frame.pieces[i];
            if(p->actor_descriptor==0xc58d80 && p->pose==0xc07f59 &&
               p->obj<=0xffe8 && rd16(s_frame.ram+rd16(s_frame.ram+p->obj+4))==(unsigned)world){owned=1;break;}
        }
        int x=world+s_ride_exit_shift-s_frame.raster_camera[0];
        if(!owned && x+column-96<width && x+column+96>0){unsigned j=s_ride_preview_count++;
            s_ride_preview[j].x=x;s_ride_preview[j].y=288-s_frame.raster_camera[1]+1;
            Piece attachment={.pose=0xc07f59,.actor_descriptor=0xc58d80};int dx,dy;
            GiraffeSceneryShift(&attachment,&dx,&dy);s_ride_preview[j].x+=dx;s_ride_preview[j].y+=dy;
            s_ride_preview[j].image=5;s_ride_preview[j].bank=1;
            s_ride_preview[j].flags=s_rom[0x58d80+3]&0xc0;
        }
    }
    static FILE *trace;static int opened;
    if(!opened){opened=1;const char *path=getenv("TLK_RIDE_PREVIEW_TRACE");if(path)trace=fopen(path,"w");
        if(trace)fputs("field,kind,pose,x,y,camera,raster,travel,loop,cursor,column,flags,descriptor,kept,fixed,role,source_ready\n",trace);}
    if(trace){extern int snes_frame_counter;
        for(unsigned i=0;i<s_ride_preview_count;i++)fprintf(trace,"%d,preview,%06x,%d,%d,%u,%d,%u,%u,%06x,%d,%02x,0,0,0,0,0\n",snes_frame_counter,s_ride_images[s_ride_preview[i].image].pose,s_ride_preview[i].x,s_ride_preview[i].y,rd16(s_frame.ram+0xb29b),s_frame.raster_camera[0],travel,rd16(s_frame.ram+0xa56),s_ride_cursor,column,s_ride_preview[i].flags);
        for(unsigned i=0;i<s_frame.piece_count;i++){const Piece *p=&s_frame.pieces[i];
            if(p->pose!=0xc45a16 && p->pose!=0xc3b756 && p->pose!=0xc3b7f2 &&
               p->pose!=0xc3b6f7 && p->pose!=0xc3b77b && p->pose!=0xc07f59)continue;
            unsigned j=0;for(;j<i;j++)if(s_frame.pieces[j].obj==p->obj)break;if(j<i)continue;
            int x=(p->attr&0x4000)?p->x+p->local_x+p->size:p->x-p->local_x;
            int y=p->y-p->local_y;
            unsigned role=SceneNpcRole(p,(p->attr>>9)&7),source=0,stride=0;int ready=RidePieceSource(p,role,&source,&stride);
            fprintf(trace,"%d,live,%06x,%d,%d,%u,%d,%u,%u,%06x,%d,%02x,%06x,%u,%u,%u,%u\n",snes_frame_counter,p->pose,x,y,rd16(s_frame.ram+0xb29b),s_frame.raster_camera[0],travel,rd16(s_frame.ram+0xa56),s_ride_cursor,column,(p->attr>>8)&0xc0,p->actor_descriptor,p->kept,p->fixed,role,ready);
        }fflush(trace);
    }
}
static void DrawRidePreviewRow(uint16_t *obj,int width,int column,int y0,const Line *l) {
    for(unsigned n=s_ride_preview_count;n>0;n--) {
        unsigned i=n-1;
        RidePreviewImage *image=&s_ride_images[s_ride_preview[i].image];
        int local_y=y0-s_ride_preview[i].y;
        if(s_ride_preview[i].flags&0x80)local_y=-local_y-2;
        int y=local_y+96;
        unsigned bank=s_ride_preview[i].bank;
        unsigned role=s_ride_preview[i].image==5?TLK_MD_SPRITE_CW_GIRAFFE:TLK_MD_SPRITE_CW_RIDE_OBSTACLE;
        int frames=s_md_npc_frames[role],palette=s_md_npc_palette[role];
        int left=image->left,right=image->right,top=image->top,bottom=image->bottom;
        if(frames){int bx,by,bw,bh;if(TlkMdSpritesBounds(image->pose,&bx,&by,&bw,&bh)){
            left=bx+96;right=left+bw;top=by+96;bottom=top+bh;
        }}
        if(y<top || y>=bottom)continue;
        for(int x=left;x<right;x++) {
            unsigned pixel=x>=0 && x<192 && y>=0 && y<192?image->pixel[y*192+x]:0;
            int local_x=x-96;
            int dest=s_ride_preview[i].x+((s_ride_preview[i].flags&0x40)?-local_x-1:local_x)+column;
            if(dest<0 || dest>=width)continue;
            uint16_t color=0xffff;
            if(frames || palette) {
                uint16_t colors[256];const uint16_t *cgram=l->cgram;
                if(s_ride_preview[i].image==5 && !palette){memcpy(colors,l->cgram,sizeof colors);memcpy(colors+208,l->cgram+144,32);cgram=colors;}
                int sampled=TlkMdSpritesNpcSample(image->pose,x-96,y-96,pixel,frames,palette,cgram,&color);
                if(sampled<=0)continue;
            }else if(!pixel)continue;
            s_ride_preview_pixels++;
            obj[dest]=(uint16_t)(0xa600|128|bank*16|(pixel?pixel:1));
            s_obj_slot[dest]=254;s_npc_color[dest]=color;
            s_obj_palette[dest]=PaletteToken(role==TLK_MD_SPRITE_CW_GIRAFFE?"graphics.sprites.animals.giraffes.palette":"graphics.sprites.world_objects.ride_obstacles.palette");
        }
    }
}

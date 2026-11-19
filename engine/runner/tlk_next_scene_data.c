/* Installer-owned scene palettes. No cartridge instructions read at runtime. */
#include "tlk_next_scene_data.h"
#include "tlk_md_assets.h"
#include "tlk_data_record.h"
#include "tlk_exile_grip_map.h"
#include "pride_hitbox_map.h"
#include <string.h>
#include <stdlib.h>
enum { WORDS=2432,COLOR_BYTES=16+WORDS*2,FRAME_BYTES=256*224,
       STAMPEDE_BYTES=16+3*FRAME_BYTES,RULE_WORDS=22,RULE_BYTES=8+RULE_WORDS*4,BOX_COUNT=10,BOX_BYTES=12+BOX_COUNT*20,
       EXILE_GRIPS=sizeof exile_grip_pairs/sizeof *exile_grip_pairs,GRIP_BYTES=12+EXILE_GRIPS*16,
       EXILE_ROCK_COUNT=3,EXILE_ROCK_BYTES=16+EXILE_ROCK_COUNT*24,
       WALL_BYTES=16,BYTES=EXILE_ROCK_BYTES+COLOR_BYTES+STAMPEDE_BYTES+RULE_BYTES+BOX_BYTES+GRIP_BYTES+WALL_BYTES,LATE_BANKS=0x41fdb56b };
static uint16_t exile_grips[EXILE_GRIPS][4];
static uint16_t exile_wall_masks[4];
static const uint32_t exile_rock_poses[EXILE_ROCK_COUNT][2]={
    {0xc60466,0x10ebc0},{0xc6048b,0x10ebe8},{0xc604b0,0x10ec10}};
static uint16_t exile_rock_bounds[EXILE_ROCK_COUNT][8];
enum { EXILE_CELLS=15500,EXILE_ROW_BYTES=200,EXILE_ROWS=155,EXILE_CELL_BYTES=40,EXILE_TERRAIN_HEADER=20 };
static uint8_t exile_terrain[EXILE_CELLS][EXILE_CELL_BYTES];
static unsigned exile_terrain_count;
enum { HAKUNA_ROW_BYTES=450,HAKUNA_ROWS=71,HAKUNA_CELLS=HAKUNA_ROW_BYTES/2*HAKUNA_ROWS };
static uint8_t hakuna_terrain[HAKUNA_CELLS][EXILE_CELL_BYTES];
static unsigned hakuna_terrain_count;
enum { DESTINY_ROW_BYTES=604,DESTINY_ROWS=44,DESTINY_CELLS=DESTINY_ROW_BYTES/2*DESTINY_ROWS };
static uint8_t destiny_terrain[DESTINY_CELLS][EXILE_CELL_BYTES];
static unsigned destiny_terrain_count;

enum { PREPARED_ROW_BYTES=610,PREPARED_ROWS=45,PREPARED_CELLS=PREPARED_ROW_BYTES/2*PREPARED_ROWS };
static uint8_t prepared_terrain[PREPARED_CELLS][EXILE_CELL_BYTES];
static unsigned prepared_terrain_count;
enum { DESTINY_MARKER_DELTAS=126,DESTINY_MARKER_BYTES=16+DESTINY_MARKER_DELTAS*8 };
static uint8_t destiny_markers[DESTINY_MARKER_DELTAS*8];
enum { DESTINY_ROCK_DELTAS=14,DESTINY_ROCK_BYTES=16+DESTINY_ROCK_DELTAS*8 };
static uint8_t destiny_rocks[DESTINY_ROCK_DELTAS*8];
enum { DESTINY_SURFACE_BYTES=20 };
static uint16_t destiny_surface[4];
enum { DESTINY_ARENA_BYTES=16 };
static uint16_t destiny_arena_radius[2];
enum { SIMBA_POINTS=sizeof simba_point_map/sizeof *simba_point_map,SIMBA_POINT_BYTES=12+SIMBA_POINTS*16 };
static uint16_t simba_points[SIMBA_POINTS][4];
enum { ADULT_TURN_BYTES=16 };
static uint16_t adult_turn[2];
enum { ADULT_ROAR_BYTES=16 };
static uint16_t adult_roar[2];
enum { DESTINY_EXIT_BYTES=16 };
static uint16_t destiny_exit_start[2];
enum { BONUS_SELECTION_BYTES=32 };
static uint16_t bonus_selection[10];
enum { PREPARED_ROCK_DELTAS=7,PREPARED_ROCK_BYTES=16+PREPARED_ROCK_DELTAS*8 };
static uint8_t prepared_rocks[PREPARED_ROCK_DELTAS*8];
enum { HAKUNA_MARKER_DELTAS=81,HAKUNA_MARKER_BYTES=16+HAKUNA_MARKER_DELTAS*8,HAKUNA_DEFEAT_BYTES=24,DESTINY_BOULDER_BYTES=16 };
static uint8_t hakuna_markers[HAKUNA_MARKER_DELTAS*8];
static uint16_t hakuna_defeat[6],destiny_boulder_top[2];
static uint16_t colors[WORDS];static int ready;
static uint32_t stampede_rules[RULE_WORDS];
static const uint32_t running_poses[BOX_COUNT][2]={
 {0xc23637,0x1c191a},{0xc23660,0x1c1952},{0xc23689,0x1c198a},{0xc236b2,0x1c19c2},{0xc236d7,0x1c19ea},
 {0xc236fc,0x1c1a12},{0xc23725,0x1c1a4a},{0xc23752,0x1c1a72},{0xc2377f,0x1c1a9a},{0xc237ac,0x1c1ae2}};
static uint16_t running_bounds[BOX_COUNT][8];
static uint8_t stampede[3*FRAME_BYTES],stampede_native[64];
static void StampedeColors(void){
    for(unsigned i=0;i<64;i++){
        unsigned best=~0u,target=0,c=colors[i];
        for(unsigned j=0;j<128;j++){
            unsigned n=colors[384+j];int r=(int)(c&31)-(int)(n&31),g=(int)(c>>5&31)-(int)(n>>5&31),b=(int)(c>>10&31)-(int)(n>>10&31);
            unsigned d=3*r*r+6*g*g+2*b*b;if(d<best){best=d;target=j;}
        }stampede_native[i]=(uint8_t)target;
    }
}
#ifdef TLK_INTERLEVEL_PREPARER
static unsigned TerrainPointer(const uint8_t *p,int md){return md?((unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3]):(TlkDataGet16(p)|(unsigned)p[2]<<16)&0x3fffff;}
static int PrepareHakunaDefeat(const uint8_t *s,const uint8_t *m){
    static const uint8_t native[]={0xfa,1,119,0x29,0x20,0xc0,35,0x29,0x20,0xc0,0xfa,6,34,0x29,0x20,0xc0,0xfa,5};
    static const uint8_t md[]={0xfd,1,99,0x10,0xa9,0x24,0xfd,6,89,0x10,0xa9,0xac,0xfd,5};
    if(memcmp(s+0x27da7,native,sizeof native)||memcmp(m+0xe9522,md,sizeof md))return 0;
    hakuna_defeat[0]=s[0x27da9];hakuna_defeat[1]=s[0x27dad];hakuna_defeat[2]=m[0xe9524];
    hakuna_defeat[3]=s[0x27db3];hakuna_defeat[4]=m[0xe952a];hakuna_defeat[5]=0;return 1;
}
static int PrepareDestinyBoulder(const uint8_t *s,const uint8_t *m){
    static const uint8_t native[]={0xf4,47,0,0xf4,48,0,0xf4,0xfe,0xff,0xf4,0xfc,0xff};
    static const uint8_t md[]={0x3f,0x3c,0,47,0x3f,0x3c,0,48,0x3f,0x3c,0,8,0x3f,0x3c,0xff,0xfc};
    if(memcmp(s+0x594df,native,sizeof native)||memcmp(s+0x59558,native,sizeof native)||
       memcmp(m+0x1ab6b8,md,sizeof md)||memcmp(m+0x1ab72e,md,sizeof md))return 0;
    destiny_boulder_top[0]=TlkDataGet16(s+0x594e6);
    destiny_boulder_top[1]=(unsigned)m[0x1ab6c2]<<8|m[0x1ab6c3];return 1;
}
static int PrepareHakunaMarkers(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    const uint8_t *sr=s+0x481,*mr=m+0x1cfdb4+5*48;
    uint8_t *sm=malloc(HAKUNA_ROW_BYTES*HAKUNA_ROWS),*mm=malloc(HAKUNA_ROW_BYTES*HAKUNA_ROWS),*sc=malloc(65536);
    size_t a=0,b=0,c=0;unsigned count=0,native_count=0,md_count=0,native_frogs=0,md_frogs=0,native_poison=0,md_poison=0,native_checkpoints=0,md_checkpoints=0,native_logs=0,md_logs=0,native_gorillas=0,md_gorillas=0,native_arena=0,md_arena=0,native_bonus=0,md_bonus=0,native_lives=0,md_lives=0,mc=TerrainPointer(mr+4,1);
    int ok=sm && mm && sc &&
        TlkMdDecompress(s,sn,TerrainPointer(sr+9,0),sm,HAKUNA_CELLS*2,&a) && a==HAKUNA_CELLS*2 &&
        TlkMdDecompress(m,mn,TerrainPointer(mr+16,1),mm,HAKUNA_CELLS*2,&b) && b==HAKUNA_CELLS*2 &&
        TlkMdDecompress(s,sn,TerrainPointer(sr,0),sc,65536,&c);
    for(unsigned i=0;i<HAKUNA_CELLS && ok;i++){
        unsigned sw=TlkDataGet16(sm+i*2),mw=(unsigned)mm[i*2]<<8|mm[i*2+1],so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if(so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
        unsigned native=sc[so+3],external=m[mc+mo+3];native_count+=native==59;md_count+=external==59;native_frogs+=native==47;md_frogs+=external==47;native_poison+=native==19;md_poison+=external==19;native_checkpoints+=native==3;md_checkpoints+=external==3;native_logs+=native==48;md_logs+=external==48;native_gorillas+=native==15;md_gorillas+=external==15;native_arena+=native==121;md_arena+=external==121;native_bonus+=native==41;md_bonus+=external==41;native_lives+=native==1;md_lives+=external==1;
        if(native==external || (native!=59 && external!=59 && native!=47 && external!=47 && native!=19 && external!=19 && native!=3 && external!=3 && native!=48 && external!=48 && native!=15 && external!=15 && native!=121 && external!=121 && native!=41 && external!=41 && native!=1 && external!=1))continue;
        if(count==HAKUNA_MARKER_DELTAS || (native && native!=59 && native!=47 && native!=19 && native!=3 && native!=48 && native!=15 && native!=121 && native!=41 && native!=1) || (external && external!=59 && external!=47 && external!=19 && external!=3 && external!=48 && external!=15 && external!=121 && external!=41 && external!=1)){ok=0;break;}
        uint8_t *p=hakuna_markers+count++*8;TlkDataPut32(p,i);TlkDataPut16(p+4,sw);p[6]=native;p[7]=external;
    }
    free(sm);free(mm);free(sc);return ok && count==HAKUNA_MARKER_DELTAS && native_count==13 && md_count==15 && native_frogs==9 && md_frogs==9 && native_poison==5 && md_poison==5 && native_checkpoints==2 && md_checkpoints==2 && native_logs==9 && md_logs==25 && native_gorillas==1 && md_gorillas==1 && native_arena==1 && md_arena==2 && native_bonus==0 && md_bonus==1 && native_lives==2 && md_lives==2;
}
/* Obstacle IDs108..114 and independent monkey96 use original registration homes. */
static int PrepareDestinyMarkers(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    const uint8_t *sr=s+0x4b3,*mr=m+0x1cfdb4+6*48;
    uint8_t *sm=malloc(DESTINY_CELLS*2),*mm=malloc(DESTINY_CELLS*2),*sc=malloc(65536);
    size_t a=0,b=0,c=0;unsigned count=0,rock_count=0,native_rocks=0,md_rocks=0,native_triggers=0,md_triggers=0,native_monkeys=0,md_monkeys=0,mc=TerrainPointer(mr+4,1);
    int ok=sm && mm && sc && TlkMdDecompress(s,sn,TerrainPointer(sr+9,0),sm,DESTINY_CELLS*2,&a) && a==DESTINY_CELLS*2 &&
        TlkMdDecompress(m,mn,TerrainPointer(mr+16,1),mm,DESTINY_CELLS*2,&b) && b==DESTINY_CELLS*2 && TlkMdDecompress(s,sn,TerrainPointer(sr,0),sc,65536,&c);
    for(unsigned i=0;i<DESTINY_CELLS && ok;i++){
        unsigned sw=TlkDataGet16(sm+i*2),mw=(unsigned)mm[i*2]<<8|mm[i*2+1],so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if(so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
        unsigned native=sc[so+3],external=m[mc+mo+3];
        native_rocks+=native==94;md_rocks+=external==94;native_triggers+=native==90;md_triggers+=external==90;native_monkeys+=native==96;md_monkeys+=external==96;
        if(native!=external && (native==94 || external==94 || native==90 || external==90)){
            if(rock_count==DESTINY_ROCK_DELTAS || (native && native!=94 && native!=90) || (external && external!=94 && external!=90)){ok=0;break;}
            uint8_t *p=destiny_rocks+rock_count++*8;TlkDataPut32(p,i);TlkDataPut16(p+4,sw);p[6]=native;p[7]=external;
        }
        if(native==external || !(native==96 || external==96 || (native>=108 && native<=114) || (external>=108 && external<=114)))continue;
        if(count==DESTINY_MARKER_DELTAS || (native && native!=96 && (native<108 || native>114)) || (external && external!=96 && (external<108 || external>114))){ok=0;break;}
        uint8_t *p=destiny_markers+count++*8;TlkDataPut32(p,i);TlkDataPut16(p+4,sw);p[6]=native;p[7]=external;
    }
    free(sm);free(mm);free(sc);return ok && count==DESTINY_MARKER_DELTAS && rock_count==DESTINY_ROCK_DELTAS && native_rocks==6 && md_rocks==6 && native_triggers==4 && md_triggers==4 && native_monkeys==13 && md_monkeys==19;
}
/* Be Prepared shares its map dimensions but has seven different falling-rock
 * markers. Prepare placements, not RNG outcomes or actor timers. */
static int PrepareBePreparedRocks(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    const uint8_t *sr=s+0x4e5,*mr=m+0x1cfdb4+7*48;
    unsigned bytes=610*45,mc=TerrainPointer(mr+4,1),count=0,native_count=0,md_count=0;
    if(TlkDataGet16(sr+18)!=610 || TlkDataGet16(sr+20)!=45 ||
       ((unsigned)mr[12]<<8|mr[13])!=610 || ((unsigned)mr[14]<<8|mr[15])!=45)return 0;
    uint8_t *sm=malloc(bytes),*mm=malloc(bytes),*sc=malloc(65536);size_t a=0,b=0,c=0;
    int ok=sm && mm && sc && TlkMdDecompress(s,sn,TerrainPointer(sr+9,0),sm,bytes,&a) && a==bytes &&
        TlkMdDecompress(m,mn,TerrainPointer(mr+16,1),mm,bytes,&b) && b==bytes &&
        TlkMdDecompress(s,sn,TerrainPointer(sr,0),sc,65536,&c);
    for(unsigned i=0;i<bytes/2 && ok;i++){
        unsigned sw=TlkDataGet16(sm+i*2),mw=(unsigned)mm[i*2]<<8|mm[i*2+1],so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if(so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
        unsigned native=sc[so+3],external=m[mc+mo+3];native_count+=native==135;md_count+=external==135;
        if(native==external || (native!=135 && external!=135))continue;
        if(count==PREPARED_ROCK_DELTAS || (native && native!=135) || (external && external!=135)){ok=0;break;}
        uint8_t *p=prepared_rocks+count++*8;TlkDataPut32(p,i);TlkDataPut16(p+4,sw);p[6]=native;p[7]=external;
    }
    free(sm);free(mm);free(sc);return ok && count==PREPARED_ROCK_DELTAS && native_count==20 && md_count==19;
}
static int PrepareTerrain(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn,unsigned descriptor,unsigned level,unsigned row_bytes,unsigned rows,uint8_t (*cells)[EXILE_CELL_BYTES],unsigned *count){
    const uint8_t *sr=s+descriptor,*mr=m+0x1cfdb4+level*48;unsigned bytes=row_bytes*rows;
    if(TlkDataGet16(sr+18)!=row_bytes || TlkDataGet16(sr+20)!=rows ||
       ((unsigned)mr[12]<<8|mr[13])!=row_bytes || ((unsigned)mr[14]<<8|mr[15])!=rows)return 0;
    uint8_t *sm=malloc(bytes),*mm=malloc(bytes),*sc=malloc(65536);size_t a=0,b=0,c=0;
    int ok=sm && mm && sc && TlkMdDecompress(s,sn,TerrainPointer(sr+9,0),sm,bytes,&a) && a==bytes &&
        TlkMdDecompress(m,mn,TerrainPointer(mr+16,1),mm,bytes,&b) && b==bytes &&
        TlkMdDecompress(s,sn,TerrainPointer(sr,0),sc,65536,&c);
    unsigned sh=TerrainPointer(sr+3,0),mc=TerrainPointer(mr+4,1),mh=TerrainPointer(mr+8,1);*count=0;
    for(unsigned i=0;i<bytes/2 && ok;i++){
        unsigned sw=TlkDataGet16(sm+i*2),mw=(unsigned)mm[i*2]<<8|mm[i*2+1],so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if((sw&7)!=(mw&7) || so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
        unsigned sp=TlkDataGet16(sc+so),mp=m[mc+mo]*16u;
        if(sh>=sn || sp+16>sn-sh || mh>=mn || mp+16>mn-mh){ok=0;break;}
        if(sc[so+2]==m[mc+mo+2] && !memcmp(s+sh+sp,m+mh+mp,16))continue;
        uint8_t *p=cells[(*count)++];TlkDataPut32(p,i);TlkDataPut16(p+4,sw);
        p[6]=sc[so+2];p[7]=m[mc+mo+2];memcpy(p+8,s+sh+sp,16);memcpy(p+24,m+mh+mp,16);
    }
    free(sm);free(mm);free(sc);return ok && *count>0;
}
static unsigned StWord(const uint8_t *p,int md){return md?((unsigned)p[0]<<8|p[1]):(p[0]|(unsigned)p[1]<<8);}
static int PrepareStampedeRules(const uint8_t *s,const uint8_t *m){
    stampede_rules[0]=StWord(s+0x45afd,0);stampede_rules[1]=StWord(m+0x1a46bc,1);
    if(s[0x45afc]!=0xc9 || stampede_rules[0]!=32 || stampede_rules[1]!=40)return 0;
    if(memcmp(s+0x4627c,"\xce\x04\x20",3) || StWord(m+0x1a4f58,1)!=3 || StWord(m+0x1a525e,1)!=3)return 0;
    stampede_rules[6]=1;stampede_rules[7]=StWord(m+0x1a4f58,1);
    stampede_rules[8]=StWord(s+0x1a3ad,0);stampede_rules[9]=StWord(m+0x1a5612,1);
    stampede_rules[10]=StWord(s+0x1a3ba,0);stampede_rules[11]=StWord(m+0x1a561c,1)+1;
    if(stampede_rules[8]!=8 || stampede_rules[9]!=9 || stampede_rules[10]!=10 || stampede_rules[11]!=11)return 0;
    stampede_rules[12]=s[0x28e3f];stampede_rules[13]=StWord(m+0x1b5878,1);
    if(s[0x28e3e]!=0xa9 || stampede_rules[12]!=44 || stampede_rules[13]!=28 ||
       memcmp(s+0x28dd3,m+0x1b595c,9) || memcmp(s+0x28de5,m+0x1b596e,9) || memcmp(s+0x28dee,m+0x1b5977,9) ||
       memcmp(s+0x28e88,m+0x1b58be,13) || memcmp(s+0x28e95,m+0x1b58cb,13))return 0;
    if(memcmp(s+0xe19f,"\xa9\x70\xea",3)||memcmp(s+0xbe0f,"\x18\x6b",2)||StWord(m+0x1b5a96,1)!=4)return 0;
    stampede_rules[14]=StWord(s+0xe1a0,0);stampede_rules[15]=0xbe0f;stampede_rules[16]=0xea93;stampede_rules[17]=1;
    /* These are next-stage table values, not complete transition programs.
     * MD names Exile directly (one-based5 -> canonical4), then runs the
     * separate cliff scene at 1CAD9C before initializing Exile's actors.
     * The native cliff controller owns that scene and its Start handling. */
    if(memcmp(s+0x894a,"\xa0\x2e\xb7\xdf\x8f\x9e\xff\x7f",8) ||
       memcmp(m+0x1d72f2,"\x20\x79\xff\xff\xe9\x58",6))return 0;
    stampede_rules[18]=StWord(s+0x41d+46,0);
    stampede_rules[19]=StWord(m+0x1d71dc,1)-1;
    if(stampede_rules[18]!=15 || stampede_rules[19]!=4)return 0;
    /* MD's custom Stampede entry inherits the prior Bug Toss height. Its
     * fourteen rows minus the 224-line viewport leave camera limit zero.
     * This rule is used only on that ordinary post-bonus entry route. */
    if(memcmp(s+0x88c7,"\xcd\xda\x00\x90\x03\x9c\x8c\x00",8) ||
       memcmp(m+0x1a66,"\x32\x29\x00\x0a\xd2\x79\xff\xff\xcd\x0a\xb2\x79\xff\xff\xcc\xc6\x6f\x06\x42\x79\xff\xff\xcd\x0a",24) ||
       s[0x45d3e]!=0xa9 || StWord(m+0x1d0096,1)!=224)return 0;
    stampede_rules[20]=StWord(s+0x45d3f,0);
    stampede_rules[21]=StWord(m+0x1cfdb4+10*48+14,1)*16-StWord(m+0x1d0096,1);
    if(stampede_rules[20]!=300 || stampede_rules[21])return 0;
    for(unsigned i=0;i<EXILE_ROCK_COUNT;i++)for(unsigned j=0;j<4;j++){
        unsigned n=StWord(s+(exile_rock_poses[i][0]&0x3fffff)+12+j*2,0);
        unsigned e=StWord(m+exile_rock_poses[i][1]+12+j*2,1);
        if((int16_t)n<-256 || (int16_t)n>256 || (int16_t)e<-256 || (int16_t)e>256)return 0;
        exile_rock_bounds[i][j]=n;exile_rock_bounds[i][4+j]=e;
    }
    for(unsigned i=0;i<BOX_COUNT;i++)for(unsigned j=0;j<4;j++){
        unsigned n=StWord(s+(running_poses[i][0]&0x3fffff)+12+j*2,0),e=StWord(m+running_poses[i][1]+12+j*2,1);
        if((uint16_t)(n+((j&1)?-1:3))!=e)return 0;
        running_bounds[i][j]=(uint16_t)n;running_bounds[i][4+j]=(uint16_t)e;
    }
    unsigned a=0x28a10,b=0x1b52f6,differences=0;
    for(unsigned i=0;i<86;i++){
        unsigned time=StWord(s+a,0),kind=StWord(s+a+2,0);
        if(time!=StWord(m+b,1)||kind!=StWord(m+b+2,1))return 0;
        if(kind&32768)return i==85 && time==4200 && differences==1;
        if(kind>6)return 0;
        unsigned from=StWord(s+a+4,0),to=StWord(m+b+4,1);
        if(from!=to){stampede_rules[2]=a+4;stampede_rules[3]=time;stampede_rules[4]=from;stampede_rules[5]=to;differences++;}
        if(kind<2){if(StWord(s+a+6,0)!=StWord(m+b+6,1)||StWord(s+a+8,0)!=StWord(m+b+8,1))return 0;a+=4;b+=4;}
        a+=6;b+=6;
    }return 0;
}
static unsigned StampedePixel(const uint8_t *v,unsigned x,unsigned y){
    unsigned a=0x8000+((y/8)*128+x/8)*2,t=(unsigned)v[a]<<8|v[a+1],tx=x&7,ty=y&7;
    if(t&0x800)tx=7-tx;if(t&0x1000)ty=7-ty;
    unsigned n=(v[(t&2047)*32+ty*4+tx/2]>>((tx&1)?0:4))&15;
    return n?0x100|((t>>8)&0x80)|((t>>13)&3)*16|n:0;
}
static int PrepareStampede(const uint8_t *m,size_t mn){
    uint8_t *v=calloc(65536,1);size_t n=0;if(!v)return 0;
    int ok=TlkMdDecompress(m,mn,0x1c6f5c,v,24736,&n)&&n==24736;
    memset(v+0x7fe0,255,32);for(unsigned i=0x8000;i<0xa000;i+=2){v[i]=0x83;v[i+1]=0xff;}
    ok=ok&&TlkMdDecompress(m,mn,0x1c9f7c,v+0x8300,5120,&n)&&n==5120;
    if(ok)for(unsigned p=0;p<3;p++)for(unsigned y=0;y<224;y++)for(unsigned x=0;x<256;x++){
        unsigned a=StampedePixel(v,x+p*256,y),b=StampedePixel(v,x+768,y);
        unsigned t=a&&(!b||(a&128)>=(b&128))?a:b;
        stampede[p*FRAME_BYTES+y*256+x]=(uint8_t)t;
    }free(v);return ok;
}
#endif
int TlkNextSceneDataReady(void){return ready;}
size_t TlkNextSceneDataRecordSize(void){return ready?BYTES+3*EXILE_TERRAIN_HEADER+(exile_terrain_count+hakuna_terrain_count+destiny_terrain_count)*EXILE_CELL_BYTES+HAKUNA_MARKER_BYTES+HAKUNA_DEFEAT_BYTES+DESTINY_BOULDER_BYTES+DESTINY_MARKER_BYTES+SIMBA_POINT_BYTES+ADULT_TURN_BYTES+DESTINY_ROCK_BYTES+DESTINY_SURFACE_BYTES+DESTINY_ARENA_BYTES+ADULT_ROAR_BYTES+DESTINY_EXIT_BYTES+BONUS_SELECTION_BYTES+PREPARED_ROCK_BYTES+EXILE_TERRAIN_HEADER+prepared_terrain_count*EXILE_CELL_BYTES:0;}
int TlkNextSceneDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    ready=0;if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    /* Actual native banks observed in both initialized scenes; original ROM
     * source offsets verified against all16 words, not inferred by bank ID. */
    static const unsigned native[2][8]={
        {31891,250241,250273,250305,250305,250241,250401,250305},
        {31891,331418,194791,194023,195335,331546,32083,331610}};
    unsigned md[2]={0x1cac22,0};
    const uint8_t *p=m+0x1cfdb4+4*48+44;md[1]=(unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3];
    for(unsigned scene=0;scene<2;scene++){
        if(md[scene]>mn-128)return 0;
        for(unsigned i=0;i<64;i++){const uint8_t *q=m+md[scene]+i*2;colors[scene*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);}
        for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++){
            const uint8_t *q=s+native[scene][bank]+i*2;colors[128+scene*128+bank*16+i]=q[0]|(unsigned)q[1]<<8;
        }
    }
    for(unsigned i=0;i<128;i++){const uint8_t *q=s+0x3d061+i*2;colors[384+i]=q[0]|(unsigned)q[1]<<8;}
    /* Normal later-scene banks verified against actual actor draws. Unknown
     * banks stay unavailable rather than matching a guessed palette. */
    static const unsigned later[2][8]={
        {0x7c93,0x60619,0,0x60659,0,0x60799,0x607b9,0},
        {0x7c93,0,0x2fbc7,0,0x2fd07,0x2fd27,0,0x2f967}};
    for(unsigned scene=0;scene<2;scene++) {
        const uint8_t *r=m+0x1cfdb4+(scene+5)*48+44;
        unsigned palette=(unsigned)r[0]<<24|(unsigned)r[1]<<16|(unsigned)r[2]<<8|r[3];
        if(palette>mn-128)return 0;
        for(unsigned i=0;i<64;i++){const uint8_t *q=m+palette+i*2;colors[512+scene*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);}
        for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++) {
            const uint8_t *q=s+later[scene][bank]+i*2;
            colors[640+scene*128+bank*16+i]=later[scene][bank]?(q[0]|(unsigned)q[1]<<8):0;
        }
    }
    /* Actual7/8 normal banks and MD CRAM, independently reviewed per scene.
     * Unknown banks remain zero/unavailable. Previous896 color words retain
     * their exact positions and values. Pride Rock colors are not assumed:
     * its observed live CRAM differs from the static level-table palette. */
    static const unsigned final[2][8]={
        {0x7c93,0,0x2f7c7,0x2f8e7,0x2f807,0x2f927,0x7d53,0x2f967},
        {0x7c93,0,0,0,0,0,0x7d53,0}};
    for(unsigned scene=0;scene<2;scene++) {
        const uint8_t *r=m+0x1cfdb4+(scene+7)*48+44;
        unsigned palette=(unsigned)r[0]<<24|(unsigned)r[1]<<16|(unsigned)r[2]<<8|r[3];
        if(palette>mn-128)return 0;
        for(unsigned i=0;i<64;i++){const uint8_t *q=m+palette+i*2;colors[896+scene*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);}
        for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++) {
            const uint8_t *q=s+final[scene][bank]+i*2;
            colors[1024+scene*128+bank*16+i]=final[scene][bank]?(q[0]|(unsigned)q[1]<<8):0;
        }
    }
    /* Original9 background callback cycles these three complete palettes;
     * the static level-table palette is not the normal live colors. */
    for(unsigned phase=0;phase<3;phase++)for(unsigned i=0;i<64;i++) {
        const uint8_t *q=m+0x8e538+phase*128+i*2;
        colors[1280+phase*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);
    }
    /* Original08E4F4 freezes lightning and approaches this separate rain
     * palette through18D7B0. Append it after all existing bank/bonus colors. */
    for(unsigned i=0;i<64;i++){
        const uint8_t *q=m+0x8e6b8+i*2;
        colors[2368+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);
    }
    static const unsigned pride_rock[8]={0x7c93,0,0,0,0x7d13,0,0x7d53,0x7d73};
    for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++) {
        const uint8_t *q=s+pride_rock[bank]+i*2;
        colors[1472+bank*16+i]=pride_rock[bank]?(q[0]|(unsigned)q[1]<<8):0;
    }
    /* Bonus normal palettes: actual Pumbaa/Timon bank3 and Hunt Timon bank4.
     * The shared gold/bug bank0 is unchanged; unknown banks stay unavailable. */
    for(unsigned scene=0;scene<4;scene++) {
        for(unsigned i=0;i<64;i++){const uint8_t *q=m+0x27d19c+i*2;colors[1600+scene*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);}
        for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++) {
            unsigned source=bank==0?0x7c93:!scene && bank==3?0x50ada:scene && bank==4?0x3d3e1:0;
            const uint8_t *q=s+source+i*2;colors[1856+scene*128+bank*16+i]=source?(q[0]|(unsigned)q[1]<<8):0;
        }
    }
    #ifdef TLK_INTERLEVEL_PREPARER
    if(!PrepareStampede(m,mn)||!PrepareStampedeRules(s,m) ||
       !PrepareTerrain(s,sn,m,mn,0x44f,4,EXILE_ROW_BYTES,EXILE_ROWS,exile_terrain,&exile_terrain_count) ||
       !PrepareTerrain(s,sn,m,mn,0x481,5,HAKUNA_ROW_BYTES,HAKUNA_ROWS,hakuna_terrain,&hakuna_terrain_count) ||
       !PrepareTerrain(s,sn,m,mn,0x4b3,6,DESTINY_ROW_BYTES,DESTINY_ROWS,destiny_terrain,&destiny_terrain_count) ||
       !PrepareTerrain(s,sn,m,mn,0x4e5,7,PREPARED_ROW_BYTES,PREPARED_ROWS,prepared_terrain,&prepared_terrain_count) || prepared_terrain_count!=1135 ||
       !PrepareDestinyMarkers(s,sn,m,mn) ||
       !PrepareBePreparedRocks(s,sn,m,mn)||!PrepareHakunaMarkers(s,sn,m,mn)||!PrepareHakunaDefeat(s,m)||!PrepareDestinyBoulder(s,m))return 0;
    if(memcmp(s+0xf82,"\x69\x28\x00",3) || memcmp(m+0x1ad8b0,"\x06\x42\x00\x50",4))return 0;
    /* Shared age-selection helper arguments: adult pulse38 versus30. */
    if(memcmp(s+0x35949,"\xf4\x26\x00\xf4\x14\x00",6) ||
       memcmp(s+0x3598b,"\xf4\x26\x00\xf4\x14\x00",6) ||
       memcmp(m+0x196754,"\x3f\x3c\x00\x1e\x3f\x3c\x00\x0e",8) ||
       memcmp(m+0x1967c4,"\x3f\x3c\x00\x1e\x3f\x3c\x00\x0e",8))return 0;
    adult_roar[0]=TlkDataGet16(s+0x3594a);adult_roar[1]=(unsigned)m[0x196756]<<8|m[0x196757];
    static const uint8_t exit_mask[]={0x02,0x41,0,0x80};
    if(memcmp(m+0x1abfb4,exit_mask,sizeof exit_mask) ||
       memcmp(s+0x1aacb,"\xb1\x00\xd0",3))return 0;
    /* Standard installed input translation maps MD Start80 to SNES1000. */
    destiny_exit_start[0]=0x1000;destiny_exit_start[1]=(unsigned)m[0x1abfb6]<<8|m[0x1abfb7];
    /* MD1D72A6 reads the next-main table pointer E958 and its +3E Hunt word;
     * native C08963 instead rejects zero from RNG&3. Prepare canonical IDs. */
    if(memcmp(m+0x1d72ac,"\x30\x28\x00\x3e",4) ||
       memcmp(s+0x8963,"\x22\xba\xcb\xc0\x29\x03\x00",7))return 0;
    for(unsigned i=0;i<10;i++){
        unsigned at=0x1d71d4+(i+1)*2;
        if(((unsigned)m[at]<<8|m[at+1])!=i+2)return 0;
        unsigned raw=(unsigned)m[at+0x3e]<<8|m[at+0x3f];
        if(raw<12 || raw>14)return 0;bonus_selection[i]=raw-1;
    }
    destiny_arena_radius[0]=TlkDataGet16(s+0xf83);destiny_arena_radius[1]=(unsigned)m[0x1ad8b2]<<8|m[0x1ad8b3];
    destiny_surface[0]=TlkDataGet16(s+0x6014a+12);destiny_surface[1]=TlkDataGet16(s+0x6014a+16);
    destiny_surface[2]=(unsigned)m[0x13cb04+12]<<8|m[0x13cb04+13];destiny_surface[3]=(unsigned)m[0x13cb04+16]<<8|m[0x13cb04+17];
    if(destiny_surface[0]!=4 || destiny_surface[1]!=48 || destiny_surface[2]!=65533 || destiny_surface[3]!=55)return 0;
    /* MD's adult turn program has no auxiliary movement operation. */
    if(memcmp(s+0xf7de,"\xe3\xff\x00\xff\xde\xf7\xc0",7) ||
       memcmp(s+0xe5bd,"\xa9\xde\xf7",3) || memcmp(m+0x7dfe6,"\x00\x00\x00\x07\xe3\x68\x00\x28\x06\x50",10) ||
       memcmp(m+0x7e640,"\x00\x04\x00\x5c\x00\x28\xff\xf8",8))return 0;
    adult_turn[0]=s[0xf7df];adult_turn[1]=0;
    for(unsigned i=0;i<SIMBA_POINTS;i++){
        unsigned sp=simba_point_map[i].snes,mp=simba_point_map[i].md;
        if(sp>sn-24 || mp>mn-24)return 0;
        for(unsigned axis=0;axis<2;axis++){
            unsigned native=TlkDataGet16(s+sp+20+axis*2),external=(unsigned)m[mp+20+axis*2]<<8|m[mp+21+axis*2];
            if((int16_t)native<-256 || (int16_t)native>256 || (int16_t)external<-256 || (int16_t)external>256)return 0;
            simba_points[i][axis]=native;simba_points[i][axis+2]=external;
        }
    }
    for(unsigned i=0;i<EXILE_GRIPS;i++)for(unsigned axis=0;axis<2;axis++){
        unsigned a=(exile_grip_pairs[i][0]&0x3fffff)+20+axis*2,b=exile_grip_pairs[i][1]+20+axis*2;
        if(a>sn-2 || b>mn-2)return 0;
        exile_grips[i][axis]=StWord(s+a,0);exile_grips[i][axis+2]=StWord(m+b,1);
        if((int16_t)exile_grips[i][axis]<-256 || (int16_t)exile_grips[i][axis]>256 ||
           (int16_t)exile_grips[i][axis+2]<-256 || (int16_t)exile_grips[i][axis+2]>256)return 0;
    }
    for(unsigned i=0;i<2;i++){
        unsigned a=i?0xc70e:0xc624,b=i?0x259e:0x2496;
        if(memcmp(s+a,"\x29\x80\x00",3)||memcmp(m+b,"\x08\x28\x00\x07\x00\x48",6))return 0;
        exile_wall_masks[i*2]=StWord(s+a+1,0);
        /* MD tests bit7 in the big-endian high byte at actor+48. */
        exile_wall_masks[i*2+1]=(uint16_t)(1u<<(m[b+3]+8));
    }
    #else
    return 0; /* Runtime accepts prepared data only. */
    #endif
    StampedeColors();ready=1;return 1;
}
int TlkNextSceneDataWrite(uint8_t *p,size_t n){
    if(!p || !ready || n!=TlkNextSceneDataRecordSize())return 0;memcpy(p,"TLKNXT10",8);TlkDataPut32(p+8,WORDS);TlkDataPut32(p+12,LATE_BANKS);
    for(unsigned i=0;i<WORDS;i++){p[16+i*2]=(uint8_t)colors[i];p[17+i*2]=(uint8_t)(colors[i]>>8);}
    memcpy(p+COLOR_BYTES,"TLKSTD01",8);TlkDataPut32(p+COLOR_BYTES+8,FRAME_BYTES);TlkDataPut32(p+COLOR_BYTES+12,3);
    memcpy(p+COLOR_BYTES+16,stampede,sizeof stampede);
    uint8_t *q=p+COLOR_BYTES+STAMPEDE_BYTES;memcpy(q,"TLKSTR03",8);
    for(unsigned i=0;i<RULE_WORDS;i++)TlkDataPut32(q+8+i*4,stampede_rules[i]);
    q+=RULE_BYTES;memcpy(q,"TLKSTH01",8);TlkDataPut32(q+8,BOX_COUNT);
    for(unsigned i=0;i<BOX_COUNT;i++){uint8_t *b=q+12+i*20;TlkDataPut32(b,running_poses[i][0]);for(unsigned j=0;j<8;j++)TlkDataPut16(b+4+j*2,running_bounds[i][j]);}
    q+=BOX_BYTES;memcpy(q,"TLKEXG01",8);TlkDataPut32(q+8,EXILE_GRIPS);
    for(unsigned i=0;i<EXILE_GRIPS;i++){uint8_t *b=q+12+i*16;TlkDataPut32(b,exile_grip_pairs[i][0]);TlkDataPut32(b+4,exile_grip_pairs[i][1]);for(unsigned j=0;j<4;j++)TlkDataPut16(b+8+j*2,exile_grips[i][j]);}
    q+=GRIP_BYTES;memcpy(q,"TLKEXW01",8);for(unsigned i=0;i<4;i++)TlkDataPut16(q+8+i*2,exile_wall_masks[i]);
    q+=WALL_BYTES;memcpy(q,"TLKEXR01",8);TlkDataPut32(q+8,EXILE_ROCK_BYTES);TlkDataPut32(q+12,EXILE_ROCK_COUNT);
    for(unsigned i=0;i<EXILE_ROCK_COUNT;i++){
        uint8_t *b=q+16+i*24;TlkDataPut32(b,exile_rock_poses[i][0]);TlkDataPut32(b+4,exile_rock_poses[i][1]);
        for(unsigned j=0;j<8;j++)TlkDataPut16(b+8+j*2,exile_rock_bounds[i][j]);
    }
    q+=EXILE_ROCK_BYTES;memcpy(q,"TLKEXT01",8);TlkDataPut32(q+8,EXILE_ROW_BYTES);TlkDataPut32(q+12,EXILE_ROWS);TlkDataPut32(q+16,exile_terrain_count);
    memcpy(q+EXILE_TERRAIN_HEADER,exile_terrain,exile_terrain_count*EXILE_CELL_BYTES);
    q+=EXILE_TERRAIN_HEADER+exile_terrain_count*EXILE_CELL_BYTES;
    memcpy(q,"TLKHKT01",8);TlkDataPut32(q+8,HAKUNA_ROW_BYTES);TlkDataPut32(q+12,HAKUNA_ROWS);TlkDataPut32(q+16,hakuna_terrain_count);
    memcpy(q+EXILE_TERRAIN_HEADER,hakuna_terrain,hakuna_terrain_count*EXILE_CELL_BYTES);
    q+=EXILE_TERRAIN_HEADER+hakuna_terrain_count*EXILE_CELL_BYTES;
    memcpy(q,"TLKHKM02",8);TlkDataPut32(q+8,HAKUNA_MARKER_BYTES);TlkDataPut32(q+12,HAKUNA_MARKER_DELTAS);
    memcpy(q+16,hakuna_markers,sizeof hakuna_markers);q+=HAKUNA_MARKER_BYTES;
    memcpy(q,"TLKHKD01",8);TlkDataPut32(q+8,HAKUNA_DEFEAT_BYTES);
    for(unsigned i=0;i<6;i++)TlkDataPut16(q+12+i*2,hakuna_defeat[i]);q+=HAKUNA_DEFEAT_BYTES;
    memcpy(q,"TLKDYC01",8);TlkDataPut32(q+8,DESTINY_BOULDER_BYTES);
    TlkDataPut16(q+12,destiny_boulder_top[0]);TlkDataPut16(q+14,destiny_boulder_top[1]);q+=DESTINY_BOULDER_BYTES;
    memcpy(q,"TLKDYT01",8);TlkDataPut32(q+8,DESTINY_ROW_BYTES);TlkDataPut32(q+12,DESTINY_ROWS);TlkDataPut32(q+16,destiny_terrain_count);
    memcpy(q+EXILE_TERRAIN_HEADER,destiny_terrain,destiny_terrain_count*EXILE_CELL_BYTES);q+=EXILE_TERRAIN_HEADER+destiny_terrain_count*EXILE_CELL_BYTES;
    memcpy(q,"TLKDYM01",8);TlkDataPut32(q+8,DESTINY_MARKER_BYTES);TlkDataPut32(q+12,DESTINY_MARKER_DELTAS);
    memcpy(q+16,destiny_markers,sizeof destiny_markers);q+=DESTINY_MARKER_BYTES;
    memcpy(q,"TLKSMP01",8);TlkDataPut32(q+8,SIMBA_POINTS);
    for(unsigned i=0;i<SIMBA_POINTS;i++){
        uint8_t *v=q+12+i*16;TlkDataPut32(v,simba_point_map[i].snes);TlkDataPut32(v+4,simba_point_map[i].md);
        for(unsigned j=0;j<4;j++)TlkDataPut16(v+8+j*2,simba_points[i][j]);
    }q+=SIMBA_POINT_BYTES;memcpy(q,"TLKATM01",8);TlkDataPut32(q+8,ADULT_TURN_BYTES);
    TlkDataPut16(q+12,adult_turn[0]);TlkDataPut16(q+14,adult_turn[1]);q+=ADULT_TURN_BYTES;
    memcpy(q,"TLKDYB01",8);TlkDataPut32(q+8,DESTINY_ROCK_BYTES);TlkDataPut32(q+12,DESTINY_ROCK_DELTAS);
    memcpy(q+16,destiny_rocks,sizeof destiny_rocks);q+=DESTINY_ROCK_BYTES;
    memcpy(q,"TLKDYF01",8);TlkDataPut32(q+8,DESTINY_SURFACE_BYTES);
    for(unsigned i=0;i<4;i++)TlkDataPut16(q+12+i*2,destiny_surface[i]);q+=DESTINY_SURFACE_BYTES;
    memcpy(q,"TLKDYA01",8);TlkDataPut32(q+8,DESTINY_ARENA_BYTES);
    TlkDataPut16(q+12,destiny_arena_radius[0]);TlkDataPut16(q+14,destiny_arena_radius[1]);q+=DESTINY_ARENA_BYTES;
    memcpy(q,"TLKART01",8);TlkDataPut32(q+8,ADULT_ROAR_BYTES);TlkDataPut16(q+12,adult_roar[0]);TlkDataPut16(q+14,adult_roar[1]);q+=ADULT_ROAR_BYTES;
    memcpy(q,"TLKDYE01",8);TlkDataPut32(q+8,DESTINY_EXIT_BYTES);
    TlkDataPut16(q+12,destiny_exit_start[0]);TlkDataPut16(q+14,destiny_exit_start[1]);q+=DESTINY_EXIT_BYTES;
    memcpy(q,"TLKBSEL1",8);TlkDataPut32(q+8,BONUS_SELECTION_BYTES);
    for(unsigned i=0;i<10;i++)TlkDataPut16(q+12+i*2,bonus_selection[i]);q+=BONUS_SELECTION_BYTES;
    memcpy(q,"TLKBPR01",8);TlkDataPut32(q+8,PREPARED_ROCK_BYTES);TlkDataPut32(q+12,PREPARED_ROCK_DELTAS);
    memcpy(q+16,prepared_rocks,sizeof prepared_rocks);q+=PREPARED_ROCK_BYTES;
    memcpy(q,"TLKBPT01",8);TlkDataPut32(q+8,PREPARED_ROW_BYTES);TlkDataPut32(q+12,PREPARED_ROWS);TlkDataPut32(q+16,prepared_terrain_count);
    memcpy(q+EXILE_TERRAIN_HEADER,prepared_terrain,prepared_terrain_count*EXILE_CELL_BYTES);return 1;
}
int TlkNextSceneDataRead(const uint8_t *p,size_t n,int apply){
    if(!p || n<BYTES+2*EXILE_TERRAIN_HEADER || memcmp(p,"TLKNXT10",8) || TlkDataGet32(p+8)!=WORDS || TlkDataGet32(p+12)!=LATE_BANKS)return 0;
    const uint8_t *terrain=p+BYTES;unsigned count=TlkDataGet32(terrain+16);
    if(memcmp(terrain,"TLKEXT01",8) || TlkDataGet32(terrain+8)!=EXILE_ROW_BYTES || TlkDataGet32(terrain+12)!=EXILE_ROWS ||
       !count || count>EXILE_CELLS || n<BYTES+2*EXILE_TERRAIN_HEADER+count*EXILE_CELL_BYTES)return 0;
    unsigned previous=0;
    for(unsigned i=0;i<count;i++){unsigned cell=TlkDataGet32(terrain+EXILE_TERRAIN_HEADER+i*EXILE_CELL_BYTES);if(cell>=EXILE_CELLS || (i && cell<=previous))return 0;previous=cell;}
    const uint8_t *hakuna=terrain+EXILE_TERRAIN_HEADER+count*EXILE_CELL_BYTES;unsigned hk_count=TlkDataGet32(hakuna+16);
    if(memcmp(hakuna,"TLKHKT01",8) || TlkDataGet32(hakuna+8)!=HAKUNA_ROW_BYTES || TlkDataGet32(hakuna+12)!=HAKUNA_ROWS ||
       !hk_count || hk_count>HAKUNA_CELLS || n<BYTES+3*EXILE_TERRAIN_HEADER+(count+hk_count)*EXILE_CELL_BYTES+HAKUNA_MARKER_BYTES+HAKUNA_DEFEAT_BYTES+DESTINY_BOULDER_BYTES)return 0;
    previous=0;
    for(unsigned i=0;i<hk_count;i++){unsigned cell=TlkDataGet32(hakuna+EXILE_TERRAIN_HEADER+i*EXILE_CELL_BYTES);if(cell>=HAKUNA_CELLS || (i && cell<=previous))return 0;previous=cell;}
    const uint8_t *boulder=hakuna+EXILE_TERRAIN_HEADER+hk_count*EXILE_CELL_BYTES+HAKUNA_MARKER_BYTES+HAKUNA_DEFEAT_BYTES;
    const uint8_t *destiny=boulder+DESTINY_BOULDER_BYTES;unsigned dy_count=TlkDataGet32(destiny+16);
    if(memcmp(destiny,"TLKDYT01",8) || TlkDataGet32(destiny+8)!=DESTINY_ROW_BYTES || TlkDataGet32(destiny+12)!=DESTINY_ROWS ||
       !dy_count || dy_count>DESTINY_CELLS || n<(size_t)(destiny-p)+EXILE_TERRAIN_HEADER+dy_count*EXILE_CELL_BYTES+DESTINY_MARKER_BYTES+SIMBA_POINT_BYTES+ADULT_TURN_BYTES+DESTINY_ROCK_BYTES+DESTINY_SURFACE_BYTES+DESTINY_ARENA_BYTES+ADULT_ROAR_BYTES+DESTINY_EXIT_BYTES+BONUS_SELECTION_BYTES+PREPARED_ROCK_BYTES+EXILE_TERRAIN_HEADER)return 0;
    previous=0;
    for(unsigned i=0;i<dy_count;i++){unsigned cell=TlkDataGet32(destiny+EXILE_TERRAIN_HEADER+i*EXILE_CELL_BYTES);if(cell>=DESTINY_CELLS || (i && cell<=previous))return 0;previous=cell;}
    const uint8_t *obstacles=destiny+EXILE_TERRAIN_HEADER+dy_count*EXILE_CELL_BYTES;
    if(memcmp(obstacles,"TLKDYM01",8) || TlkDataGet32(obstacles+8)!=DESTINY_MARKER_BYTES || TlkDataGet32(obstacles+12)!=DESTINY_MARKER_DELTAS)return 0;
    previous=0;
    for(unsigned i=0;i<DESTINY_MARKER_DELTAS;i++){
        const uint8_t *v=obstacles+16+i*8;unsigned cell=TlkDataGet32(v);
        if(cell>=DESTINY_CELLS || (i && cell<=previous) || v[6]==v[7] ||
           (v[6] && v[6]!=96 && (v[6]<108 || v[6]>114)) || (v[7] && v[7]!=96 && (v[7]<108 || v[7]>114)))return 0;previous=cell;
    }
    const uint8_t *points=obstacles+DESTINY_MARKER_BYTES;
    if(memcmp(points,"TLKSMP01",8) || TlkDataGet32(points+8)!=SIMBA_POINTS)return 0;
    for(unsigned i=0;i<SIMBA_POINTS;i++){
        const uint8_t *v=points+12+i*16;
        if(TlkDataGet32(v)!=simba_point_map[i].snes || TlkDataGet32(v+4)!=simba_point_map[i].md)return 0;
        for(unsigned j=0;j<4;j++){int value=(int16_t)TlkDataGet16(v+8+j*2);if(value<-256 || value>256)return 0;}
    }
    const uint8_t *turn=points+SIMBA_POINT_BYTES;
    if(memcmp(turn,"TLKATM01",8) || TlkDataGet32(turn+8)!=ADULT_TURN_BYTES || TlkDataGet16(turn+12)!=255 || TlkDataGet16(turn+14))return 0;
    const uint8_t *rocks=turn+ADULT_TURN_BYTES;
    if(memcmp(rocks,"TLKDYB01",8) || TlkDataGet32(rocks+8)!=DESTINY_ROCK_BYTES || TlkDataGet32(rocks+12)!=DESTINY_ROCK_DELTAS)return 0;
    previous=0;
    for(unsigned i=0;i<DESTINY_ROCK_DELTAS;i++){
        const uint8_t *v=rocks+16+i*8;unsigned cell=TlkDataGet32(v);
        if(cell>=DESTINY_CELLS || (i && cell<=previous) || v[6]==v[7] || (v[6] && v[6]!=94 && v[6]!=90) || (v[7] && v[7]!=94 && v[7]!=90))return 0;previous=cell;
    }
    const uint8_t *surface=rocks+DESTINY_ROCK_BYTES;
    if(memcmp(surface,"TLKDYF01",8) || TlkDataGet32(surface+8)!=DESTINY_SURFACE_BYTES ||
       TlkDataGet16(surface+12)!=4 || TlkDataGet16(surface+14)!=48 || TlkDataGet16(surface+16)!=65533 || TlkDataGet16(surface+18)!=55)return 0;
    const uint8_t *arena=surface+DESTINY_SURFACE_BYTES;
    if(memcmp(arena,"TLKDYA01",8) || TlkDataGet32(arena+8)!=DESTINY_ARENA_BYTES || TlkDataGet16(arena+12)!=40 || TlkDataGet16(arena+14)!=80)return 0;
    const uint8_t *roar=arena+DESTINY_ARENA_BYTES;
    if(memcmp(roar,"TLKART01",8) || TlkDataGet32(roar+8)!=ADULT_ROAR_BYTES || TlkDataGet16(roar+12)!=38 || TlkDataGet16(roar+14)!=30)return 0;
    const uint8_t *exit_start=roar+ADULT_ROAR_BYTES;
    if(memcmp(exit_start,"TLKDYE01",8) || TlkDataGet32(exit_start+8)!=DESTINY_EXIT_BYTES ||
       TlkDataGet16(exit_start+12)!=0x1000 || TlkDataGet16(exit_start+14)!=0x80)return 0;
    const uint8_t *selection=exit_start+DESTINY_EXIT_BYTES;
    if(memcmp(selection,"TLKBSEL1",8) || TlkDataGet32(selection+8)!=BONUS_SELECTION_BYTES)return 0;
    for(unsigned i=0;i<10;i++)if(TlkDataGet16(selection+12+i*2)<11 || TlkDataGet16(selection+12+i*2)>13)return 0;
    const uint8_t *rocks7=selection+BONUS_SELECTION_BYTES;
    if(memcmp(rocks7,"TLKBPR01",8) || TlkDataGet32(rocks7+8)!=PREPARED_ROCK_BYTES || TlkDataGet32(rocks7+12)!=PREPARED_ROCK_DELTAS)return 0;
    previous=0;
    for(unsigned i=0;i<PREPARED_ROCK_DELTAS;i++){
        const uint8_t *v=rocks7+16+i*8;unsigned cell=TlkDataGet32(v);
        if(cell>=305*45 || (i && cell<=previous) || v[6]==v[7] ||
           (v[6] && v[6]!=135) || (v[7] && v[7]!=135))return 0;previous=cell;
    }
    const uint8_t *prepared=rocks7+PREPARED_ROCK_BYTES;unsigned pr_count=TlkDataGet32(prepared+16);
    if(memcmp(prepared,"TLKBPT01",8) || TlkDataGet32(prepared+8)!=PREPARED_ROW_BYTES || TlkDataGet32(prepared+12)!=PREPARED_ROWS ||
       !pr_count || pr_count>PREPARED_CELLS || n!=(size_t)(prepared-p)+EXILE_TERRAIN_HEADER+pr_count*EXILE_CELL_BYTES)return 0;
    previous=0;
    for(unsigned i=0;i<pr_count;i++){
        unsigned cell=TlkDataGet32(prepared+EXILE_TERRAIN_HEADER+i*EXILE_CELL_BYTES);
        if(cell>=PREPARED_CELLS || (i && cell<=previous))return 0;previous=cell;
    }
    if(memcmp(boulder,"TLKDYC01",8)||TlkDataGet32(boulder+8)!=DESTINY_BOULDER_BYTES||
       TlkDataGet16(boulder+12)!=65534 || (int16_t)TlkDataGet16(boulder+14)<-128 || (int16_t)TlkDataGet16(boulder+14)>127)return 0;
    const uint8_t *defeat=boulder-HAKUNA_DEFEAT_BYTES;
    if(memcmp(defeat,"TLKHKD01",8)||TlkDataGet32(defeat+8)!=HAKUNA_DEFEAT_BYTES||TlkDataGet16(defeat+22))return 0;
    for(unsigned i=0;i<5;i++)if(!TlkDataGet16(defeat+12+i*2)||TlkDataGet16(defeat+12+i*2)>127)return 0;
    const uint8_t *spiders=defeat-HAKUNA_MARKER_BYTES;
    if(memcmp(spiders,"TLKHKM02",8) || TlkDataGet32(spiders+8)!=HAKUNA_MARKER_BYTES || TlkDataGet32(spiders+12)!=HAKUNA_MARKER_DELTAS)return 0;
    previous=0;
    for(unsigned i=0;i<HAKUNA_MARKER_DELTAS;i++){
        const uint8_t *v=spiders+16+i*8;unsigned cell=TlkDataGet32(v);
        if(cell>=HAKUNA_CELLS || (i && cell<=previous) || (v[6] && v[6]!=59 && v[6]!=47 && v[6]!=19 && v[6]!=3 && v[6]!=48 && v[6]!=15 && v[6]!=121 && v[6]!=41 && v[6]!=1) ||
           (v[7] && v[7]!=59 && v[7]!=47 && v[7]!=19 && v[7]!=3 && v[7]!=48 && v[7]!=15 && v[7]!=121 && v[7]!=41 && v[7]!=1) || v[6]==v[7])return 0;previous=cell;
    }
    for(unsigned i=0;i<WORDS;i++)if(p[17+i*2]&128)return 0;
    const uint8_t *q=p+COLOR_BYTES;
    if(memcmp(q,"TLKSTD01",8)||TlkDataGet32(q+8)!=FRAME_BYTES||TlkDataGet32(q+12)!=3)return 0;
    for(unsigned i=0;i<sizeof stampede;i++)if(q[16+i]&64)return 0;
    const uint8_t *r=p+COLOR_BYTES+STAMPEDE_BYTES;
    if(memcmp(r,"TLKSTR03",8)||TlkDataGet32(r+8)!=32||TlkDataGet32(r+12)!=40||TlkDataGet32(r+16)<0x28000||TlkDataGet32(r+16)>=0x29000||TlkDataGet32(r+20)>4200||TlkDataGet32(r+24)>8||TlkDataGet32(r+28)>8)return 0;
    static const unsigned contact[6]={1,3,8,9,10,11};for(unsigned i=0;i<6;i++)if(TlkDataGet32(r+32+i*4)!=contact[i])return 0;
    if(TlkDataGet32(r+56)!=44 || TlkDataGet32(r+60)!=28)return 0;
    if(TlkDataGet32(r+64)!=0xea70||TlkDataGet32(r+68)!=0xbe0f||TlkDataGet32(r+72)!=0xea93||TlkDataGet32(r+76)!=1)return 0;
    if(TlkDataGet32(r+80)!=15 || TlkDataGet32(r+84)!=4 || TlkDataGet32(r+88)!=300 || TlkDataGet32(r+92))return 0;
    const uint8_t *boxes=r+RULE_BYTES;if(memcmp(boxes,"TLKSTH01",8)||TlkDataGet32(boxes+8)!=BOX_COUNT)return 0;
    for(unsigned i=0;i<BOX_COUNT;i++){
        const uint8_t *b=boxes+12+i*20;if(TlkDataGet32(b)!=running_poses[i][0])return 0;
        for(unsigned j=0;j<8;j++){int value=(int16_t)TlkDataGet16(b+4+j*2);if(value<-256||value>256)return 0;}
    }
    const uint8_t *grips=boxes+BOX_BYTES;
    if(memcmp(grips,"TLKEXG01",8)||TlkDataGet32(grips+8)!=EXILE_GRIPS)return 0;
    for(unsigned i=0;i<EXILE_GRIPS;i++){
        const uint8_t *b=grips+12+i*16;
        if(TlkDataGet32(b)!=exile_grip_pairs[i][0]||TlkDataGet32(b+4)!=exile_grip_pairs[i][1])return 0;
        for(unsigned j=0;j<4;j++){int v=(int16_t)TlkDataGet16(b+8+j*2);if(v<-256||v>256)return 0;}
    }
    const uint8_t *wall=grips+GRIP_BYTES;if(memcmp(wall,"TLKEXW01",8))return 0;
    for(unsigned i=0;i<4;i++)if(TlkDataGet16(wall+8+i*2)!=(i&1?32768:128))return 0;
    const uint8_t *exile_rocks=wall+WALL_BYTES;
    if(memcmp(exile_rocks,"TLKEXR01",8) || TlkDataGet32(exile_rocks+8)!=EXILE_ROCK_BYTES || TlkDataGet32(exile_rocks+12)!=EXILE_ROCK_COUNT)return 0;
    for(unsigned i=0;i<EXILE_ROCK_COUNT;i++){
        const uint8_t *b=exile_rocks+16+i*24;
        if(TlkDataGet32(b)!=exile_rock_poses[i][0] || TlkDataGet32(b+4)!=exile_rock_poses[i][1])return 0;
        for(unsigned j=0;j<8;j++){int v=(int16_t)TlkDataGet16(b+8+j*2);if(v<-256 || v>256)return 0;}
    }
    if(apply){for(unsigned i=0;i<EXILE_ROCK_COUNT;i++)for(unsigned j=0;j<8;j++)exile_rock_bounds[i][j]=TlkDataGet16(exile_rocks+16+i*24+8+j*2);prepared_terrain_count=pr_count;memcpy(prepared_terrain,prepared+EXILE_TERRAIN_HEADER,pr_count*EXILE_CELL_BYTES);memcpy(prepared_rocks,rocks7+16,sizeof prepared_rocks);for(unsigned i=0;i<10;i++)bonus_selection[i]=TlkDataGet16(selection+12+i*2);destiny_exit_start[0]=TlkDataGet16(exit_start+12);destiny_exit_start[1]=TlkDataGet16(exit_start+14);adult_roar[0]=TlkDataGet16(roar+12);adult_roar[1]=TlkDataGet16(roar+14);destiny_arena_radius[0]=TlkDataGet16(arena+12);destiny_arena_radius[1]=TlkDataGet16(arena+14);for(unsigned i=0;i<4;i++)destiny_surface[i]=TlkDataGet16(surface+12+i*2);memcpy(destiny_rocks,rocks+16,sizeof destiny_rocks);adult_turn[0]=TlkDataGet16(turn+12);adult_turn[1]=TlkDataGet16(turn+14);for(unsigned i=0;i<SIMBA_POINTS;i++)for(unsigned j=0;j<4;j++)simba_points[i][j]=TlkDataGet16(points+12+i*16+8+j*2);memcpy(destiny_markers,obstacles+16,sizeof destiny_markers);destiny_terrain_count=dy_count;memcpy(destiny_terrain,destiny+EXILE_TERRAIN_HEADER,dy_count*EXILE_CELL_BYTES);destiny_boulder_top[0]=TlkDataGet16(boulder+12);destiny_boulder_top[1]=TlkDataGet16(boulder+14);for(unsigned i=0;i<6;i++)hakuna_defeat[i]=TlkDataGet16(defeat+12+i*2);memcpy(hakuna_markers,spiders+16,sizeof hakuna_markers);for(unsigned i=0;i<WORDS;i++)colors[i]=p[16+i*2]|(unsigned)p[17+i*2]<<8;memcpy(stampede,q+16,sizeof stampede);for(unsigned i=0;i<RULE_WORDS;i++)stampede_rules[i]=TlkDataGet32(r+8+i*4);for(unsigned i=0;i<BOX_COUNT;i++)for(unsigned j=0;j<8;j++)running_bounds[i][j]=TlkDataGet16(boxes+12+i*20+4+j*2);for(unsigned i=0;i<EXILE_GRIPS;i++)for(unsigned j=0;j<4;j++)exile_grips[i][j]=TlkDataGet16(grips+12+i*16+8+j*2);for(unsigned i=0;i<4;i++)exile_wall_masks[i]=TlkDataGet16(wall+8+i*2);exile_terrain_count=count;memcpy(exile_terrain,terrain+EXILE_TERRAIN_HEADER,count*EXILE_CELL_BYTES);hakuna_terrain_count=hk_count;memcpy(hakuna_terrain,hakuna+EXILE_TERRAIN_HEADER,hk_count*EXILE_CELL_BYTES);StampedeColors();ready=1;}return 1;
}
static int TerrainColumns(unsigned level,unsigned cell,unsigned live,unsigned height,unsigned native_column,unsigned column,unsigned native,unsigned *external){
    if(!ready || !external || (level!=4 && level!=5 && level!=6 && level!=7) || height>1 || native_column>=16 || column>=16)return 0;
    const uint8_t (*records)[EXILE_CELL_BYTES]=level==4?exile_terrain:level==5?hakuna_terrain:level==6?destiny_terrain:prepared_terrain;
    unsigned count=level==4?exile_terrain_count:level==5?hakuna_terrain_count:level==6?destiny_terrain_count:prepared_terrain_count,limit=level==4?EXILE_CELLS:level==5?HAKUNA_CELLS:level==6?DESTINY_CELLS:PREPARED_CELLS;
    if(cell>=limit)return 0;
    unsigned lo=0,hi=count;
    while(lo<hi){unsigned mid=(lo+hi)/2;if(TlkDataGet32(records[mid])<cell)lo=mid+1;else hi=mid;}
    if(lo==count || TlkDataGet32(records[lo])!=cell)return 0;
    const uint8_t *p=records[lo];if(live!=TlkDataGet16(p+4) || native!=(height?p[8+native_column]:p[6]))return 0;
    *external=height?p[24+column]:p[7];return 1;
}
int TlkNextSceneTerrain(unsigned level,unsigned cell,unsigned live,unsigned height,unsigned column,unsigned native,unsigned *external){
    return TerrainColumns(level,cell,live,height,column,column,native,external);
}
int TlkNextSceneTerrainPoint(unsigned level,unsigned cell,unsigned live,unsigned native_column,unsigned md_column,unsigned native,unsigned *external){
    return TerrainColumns(level,cell,live,1,native_column,md_column,native,external);
}
int TlkNextSceneHakunaMarker(unsigned marker,unsigned cell,unsigned live,unsigned native,unsigned *external){
    if(!ready || !external || cell>=HAKUNA_CELLS || (marker!=47 && marker!=59 && marker!=19 && marker!=3 && marker!=48 && marker!=15 && marker!=121 && marker!=41 && marker!=1))return 0;
    for(unsigned i=0;i<HAKUNA_MARKER_DELTAS;i++){
        const uint8_t *p=hakuna_markers+i*8;
        if(TlkDataGet32(p)!=cell || (p[6]!=marker && p[7]!=marker))continue;
        if((live&0xfff8)!=(TlkDataGet16(p+4)&0xfff8) || native!=p[6])return 0;
        *external=p[7];return 1;
    }
    return 0;
}
int TlkNextSceneExileWallMask(unsigned left,unsigned *native,unsigned *external){
    if(!ready||left>1||!native||!external)return 0;
    *native=exile_wall_masks[left*2];*external=exile_wall_masks[left*2+1];return 1;
}
int TlkNextSceneExileGrip(unsigned pose,unsigned axis,unsigned *native,unsigned *external){
    if(!ready||axis>=2||!native||!external)return 0;
    for(unsigned i=0;i<EXILE_GRIPS;i++)if(exile_grip_pairs[i][0]==pose){*native=exile_grips[i][axis];*external=exile_grips[i][axis+2];return 1;}return 0;
}
int TlkNextSceneStampedeBox(unsigned pose,unsigned component,unsigned *native,unsigned *external){
    if(!ready||component>=4||!native||!external)return 0;
    for(unsigned i=0;i<BOX_COUNT;i++)if(pose==running_poses[i][0]){*native=running_bounds[i][component];*external=running_bounds[i][4+component];return 1;}return 0;
}
const uint32_t *TlkNextSceneStampedeRules(void){return ready?stampede_rules:NULL;}
const uint8_t *TlkNextSceneStampedeFrame(unsigned phase){return ready&&phase<3?stampede+phase*FRAME_BYTES:NULL;}
uint16_t TlkNextSceneStampedeColor(unsigned index,int md){return ready&&index<64?colors[md?index:384+stampede_native[index]]:0;}
const uint16_t *TlkNextSceneMdPalette(unsigned level){return !ready?NULL:level>=3 && level<=4?colors+(level-3)*64:level>=5 && level<=6?colors+512+(level-5)*64:level>=7 && level<=8?colors+896+(level-7)*64:level==9?colors+1408:level>=10 && level<=13?colors+1600+(level-10)*64:NULL;}
const uint16_t *TlkNextSceneNativeObj(unsigned level,unsigned bank){
    if(!ready || bank>=8)return NULL;
    if(level>=10 && level<=13)return (((level==10?0x09u:0x11u)>>bank)&1)?colors+1856+(level-10)*128+bank*16:NULL;
    if(level==9)return (0xd1u&(1u<<bank))?colors+1472+bank*16:NULL;
    if(level>=3 && level<=4)return colors+128+(level-3)*128+bank*16;
    if(level>=5 && level<=6 && ((LATE_BANKS>>((level-5)*8))&(1u<<bank)))return colors+640+(level-5)*128+bank*16;
    return level>=7 && level<=8 && ((LATE_BANKS>>((level-5)*8))&(1u<<bank))?colors+1024+(level-7)*128+bank*16:NULL;
}
const uint16_t *TlkNextSceneStampedeBg(void){return ready?colors+384:NULL;}

const uint16_t *TlkNextScenePrideRockPhase(unsigned phase){return ready && phase<3?colors+1280+phase*64:NULL;}
const uint16_t *TlkNextScenePrideRockRainTarget(void){return ready?colors+2368:NULL;}
int TlkNextScenePrideRockRainColors(unsigned phase,unsigned step,uint16_t result[64]){
    if(!ready || phase>=3 || step>7 || !result)return 0;
    for(unsigned i=0;i<64;i++){
        unsigned start=colors[1280+phase*64+i],target=colors[2368+i],color=0;
        for(unsigned shift=0;shift<=10;shift+=5){
            unsigned a=((start>>shift)&31)>>2,b=((target>>shift)&31)>>2;
            unsigned c=a<b?(step<b-a?a+step:b):(step<a-b?a-step:b);
            color|=(c*4+(c>>2))<<shift;
        }
        result[i]=(uint16_t)color;
    }
    return 1;
}

const uint16_t *TlkNextSceneHakunaDefeat(void){return ready?hakuna_defeat:NULL;}

int TlkNextSceneDestinyBoulderTop(unsigned *native,unsigned *md){if(!ready||!native||!md)return 0;*native=destiny_boulder_top[0];*md=destiny_boulder_top[1];return 1;}

static int DestinyMarker(unsigned monkey,unsigned cell,unsigned live,unsigned native,unsigned *external){
    if(!ready || !external || cell>=DESTINY_CELLS)return 0;
    for(unsigned i=0;i<DESTINY_MARKER_DELTAS;i++){
        const uint8_t *p=destiny_markers+i*8;
        if(TlkDataGet32(p)!=cell || !!(p[6]==96 || p[7]==96)!=monkey)continue;
        if((live&0xfff8)!=(TlkDataGet16(p+4)&0xfff8) || native!=p[6])return 0;
        *external=p[7];return 1;
    }
    return 0;
}
int TlkNextSceneDestinyMarker(unsigned cell,unsigned live,unsigned native,unsigned *external){return DestinyMarker(0,cell,live,native,external);}
int TlkNextSceneDestinyMonkeyMarker(unsigned cell,unsigned live,unsigned native,unsigned *external){return DestinyMarker(1,cell,live,native,external);}

int TlkNextSceneSimbaPoint(unsigned pose,unsigned axis,unsigned *native,unsigned *external){
    if(!ready || axis>1 || !native || !external || pose<0xc00000 || pose>=0xf00000)return 0;
    pose&=0x3fffff;unsigned lo=0,hi=SIMBA_POINTS;
    while(lo<hi){unsigned mid=(lo+hi)/2;if(simba_point_map[mid].snes<pose)lo=mid+1;else hi=mid;}
    if(lo==SIMBA_POINTS || simba_point_map[lo].snes!=pose)return 0;
    *native=simba_points[lo][axis];*external=simba_points[lo][axis+2];return 1;
}

int TlkNextSceneAdultTurn(unsigned *native,unsigned *external){if(!ready||!native||!external)return 0;*native=adult_turn[0];*external=adult_turn[1];return 1;}

int TlkNextSceneDestinyBoulderMarker(unsigned cell,unsigned live,unsigned native,unsigned *external){
    if(!ready || !external || cell>=DESTINY_CELLS)return 0;
    for(unsigned i=0;i<DESTINY_ROCK_DELTAS;i++){
        const uint8_t *p=destiny_rocks+i*8;
        if(TlkDataGet32(p)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(p+4)&0xfff8) || native!=p[6])return 0;
        *external=p[7];return 1;
    }return 0;
}

int TlkNextSceneDestinyBoulderSurface(unsigned right,unsigned *native,unsigned *external){if(!ready||right>1||!native||!external)return 0;*native=destiny_surface[right];*external=destiny_surface[right+2];return 1;}

int TlkNextSceneDestinyArenaRadius(unsigned *native,unsigned *external){if(!ready||!native||!external)return 0;*native=destiny_arena_radius[0];*external=destiny_arena_radius[1];return 1;}

int TlkNextSceneAdultRoar(unsigned *native,unsigned *external){if(!ready||!native||!external)return 0;*native=adult_roar[0];*external=adult_roar[1];return 1;}

int TlkNextSceneDestinyExitStart(unsigned *native,unsigned *md){if(!ready || !native || !md)return 0;*native=destiny_exit_start[0];*md=destiny_exit_start[1];return 1;}

int TlkNextSceneBonusSelection(unsigned next,unsigned *level){if(!ready || !level || next<1 || next>10)return 0;*level=bonus_selection[next-1];return 1;}

int TlkNextSceneBePreparedRock(unsigned cell,unsigned live,unsigned native,unsigned *external){
    if(!ready || !external)return 0;
    for(unsigned i=0;i<PREPARED_ROCK_DELTAS;i++){
        const uint8_t *p=prepared_rocks+i*8;
        if(TlkDataGet32(p)!=cell)continue;
        if(TlkDataGet16(p+4)!=live || p[6]!=native)return 0;*external=p[7];return 1;
    }return 0;
}

int TlkNextSceneExileRockBounds(unsigned pose,unsigned component,unsigned *native,unsigned *external){
    if(!ready || component>=4 || !native || !external)return 0;
    for(unsigned i=0;i<EXILE_ROCK_COUNT;i++)if(exile_rock_poses[i][0]==pose){
        *native=exile_rock_bounds[i][component];*external=exile_rock_bounds[i][4+component];return 1;
    }return 0;
}

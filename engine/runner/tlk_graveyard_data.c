/* Installer-prepared terrain tags for hyena decisions; no runtime ROM access. */
#include "tlk_graveyard_data.h"
#include "tlk_md_assets.h"
#include "tlk_data_record.h"
#include <stdlib.h>
#include <string.h>
enum { ROW_BYTES=520, ROWS=48, CELLS=12480, DEATH_TOKENS=33, MARKER_BYTES=32,BONE_DELTAS=5,BONE_BYTES=16+BONE_DELTAS*8,CONTACT_BYTES=404,VULTURE_BYTES=32,SHAKE_BYTES=24,OLD_BYTES=16+CELLS*5+DEATH_TOKENS*4+MARKER_BYTES+BONE_BYTES+CONTACT_BYTES+VULTURE_BYTES,PICKUPS=6,PICKUP_BYTES=16+PICKUPS*8,BUGS=25,BUG_BYTES=16+BUGS*8,WALL_BYTES=24,PERCHED=3,PERCHED_BYTES=16+PERCHED*8,UPPER=3,UPPER_BYTES=16+UPPER*8,HEAD_BYTES=128,TURN_BYTES=24,LAUNCH_BYTES=20,FAREWELL_BYTES=66,FAREWELL_LENGTH=34,BYTES=OLD_BYTES+SHAKE_BYTES+PICKUP_BYTES+BUG_BYTES+WALL_BYTES+PERCHED_BYTES+UPPER_BYTES+HEAD_BYTES+TURN_BYTES+LAUNCH_BYTES+FAREWELL_BYTES };
static uint8_t cells[CELLS*5];static int ready;
static uint8_t death_tokens[DEATH_TOKENS*4];
static uint8_t reveal_markers[16],bone_markers[BONE_DELTAS*8],bone_contact[384],vulture_markers[16];
static unsigned bone_contact_delay;
static uint16_t vulture_turn[4],vulture_launch[2];
static uint8_t farewell_program[FAREWELL_LENGTH];
static uint16_t farewell_colors[8];
static const uint16_t farewell_expected[8]={0x48,0x268,0x226,0x202,0x200,0x22a,0x224,0};
static uint8_t head_native[55],head_md[55];
static uint16_t shake_rules[4],wall_rules[4];
static uint8_t perched_markers[PERCHED*8],upper_markers[UPPER*8];
static const unsigned upper_cells[]={1268,2276,3321};
static const unsigned upper_native[]={0,118,0},upper_md[]={83,0,118};
static const unsigned perched_cells[]={11103,11412,11672};
static const unsigned perched_native[]={50,0,50},perched_md[]={0,50,0};
static uint8_t pickup_markers[PICKUPS*8],bug_markers[BUGS*8];
static const unsigned bug_cells[]={2588,3022,4608,4609,4780,6438,6614,7204,7406,8340,8341,8617,8847,8891,8892,11360,11503,11507,11654,11655,11829,11949,12010,12088,12231};
static const unsigned bug_native[]={0,0,0,102,0,102,102,0,0,0,102,0,0,0,102,0,102,0,102,0,0,0,0,102,102},bug_md[]={102,102,102,0,102,0,0,102,102,102,0,102,102,102,0,102,0,102,0,102,102,102,102,0,0};
static const unsigned pickup_cells[]={1981,1983,8588,8591,9418,9677};
static const unsigned pickup_native[]={17,0,18,0,17,0},pickup_md[]={0,17,0,18,0,17};
static const unsigned bone_poses[]={0xc3b437,0xc3b466,0xc3b491,0xc3b4b6};
static unsigned le16(const uint8_t *p){return p[0]|(unsigned)p[1]<<8;}
static unsigned be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static unsigned le24(const uint8_t *p){return (le16(p)|(unsigned)p[2]<<16)&0x3fffff;}
static unsigned be32(const uint8_t *p){return be16(p)<<16|be16(p+2);}
int TlkGraveyardDataReady(void){return ready;}
const uint16_t *TlkGraveyardShakeRules(void){return ready?shake_rules:NULL;}
const uint16_t *TlkGraveyardWallRules(void){return ready?wall_rules:NULL;}
size_t TlkGraveyardDataRecordSize(void){return ready?BYTES:0;}
int TlkGraveyardDataWrite(uint8_t *p,size_t size){
    if(!p || !ready || size!=BYTES)return 0;size_t n=OLD_BYTES;
    memcpy(p,"TLKGYT13",8);TlkDataPut32(p+8,ROW_BYTES);TlkDataPut32(p+12,ROWS);memcpy(p+16,cells,sizeof cells);memcpy(p+16+sizeof cells,death_tokens,sizeof death_tokens);
    uint8_t *r=p+n-MARKER_BYTES-BONE_BYTES-CONTACT_BYTES-VULTURE_BYTES;memcpy(r,"TLKGYM01",8);TlkDataPut32(r+8,MARKER_BYTES);TlkDataPut32(r+12,2);memcpy(r+16,reveal_markers,16);
    r=p+n-BONE_BYTES-CONTACT_BYTES-VULTURE_BYTES;memcpy(r,"TLKGYB01",8);TlkDataPut32(r+8,BONE_BYTES);TlkDataPut32(r+12,BONE_DELTAS);memcpy(r+16,bone_markers,sizeof bone_markers);
    r=p+n-CONTACT_BYTES-VULTURE_BYTES;memcpy(r,"TLKGYC01",8);TlkDataPut32(r+8,CONTACT_BYTES);TlkDataPut32(r+12,4);memcpy(r+16,bone_contact,sizeof bone_contact);TlkDataPut32(r+400,bone_contact_delay);
    r=p+n-VULTURE_BYTES;memcpy(r,"TLKGYV01",8);TlkDataPut32(r+8,VULTURE_BYTES);TlkDataPut32(r+12,2);memcpy(r+16,vulture_markers,16);
    r=p+n;memcpy(r,"TLKGYS01",8);TlkDataPut32(r+8,SHAKE_BYTES);TlkDataPut32(r+12,4);
    for(unsigned i=0;i<4;i++)TlkDataPut16(r+16+i*2,shake_rules[i]);
    r=p+n+SHAKE_BYTES;memcpy(r,"TLKGYP01",8);TlkDataPut32(r+8,PICKUP_BYTES);TlkDataPut32(r+12,PICKUPS);memcpy(r+16,pickup_markers,sizeof pickup_markers);
    r+=PICKUP_BYTES;memcpy(r,"TLKGYA01",8);TlkDataPut32(r+8,BUG_BYTES);TlkDataPut32(r+12,BUGS);memcpy(r+16,bug_markers,sizeof bug_markers);
    r+=BUG_BYTES;memcpy(r,"TLKGYW01",8);TlkDataPut32(r+8,WALL_BYTES);TlkDataPut32(r+12,4);
    for(unsigned i=0;i<4;i++)TlkDataPut16(r+16+i*2,wall_rules[i]);
    r+=WALL_BYTES;memcpy(r,"TLKGYK01",8);TlkDataPut32(r+8,PERCHED_BYTES);TlkDataPut32(r+12,PERCHED);memcpy(r+16,perched_markers,sizeof perched_markers);
    r+=PERCHED_BYTES;memcpy(r,"TLKGYZ01",8);TlkDataPut32(r+8,UPPER_BYTES);TlkDataPut32(r+12,UPPER);memcpy(r+16,upper_markers,sizeof upper_markers);
    r+=UPPER_BYTES;memcpy(r,"TLKGYH01",8);TlkDataPut32(r+8,HEAD_BYTES);TlkDataPut32(r+12,55);memcpy(r+16,head_native,55);memcpy(r+71,head_md,55);r[126]=r[127]=0;
    r+=HEAD_BYTES;memcpy(r,"TLKGYQ01",8);TlkDataPut32(r+8,TURN_BYTES);TlkDataPut32(r+12,4);for(unsigned i=0;i<4;i++)TlkDataPut16(r+16+i*2,vulture_turn[i]);
    r+=TURN_BYTES;memcpy(r,"TLKGYJ01",8);TlkDataPut32(r+8,LAUNCH_BYTES);TlkDataPut32(r+12,2);for(unsigned i=0;i<2;i++)TlkDataPut16(r+16+i*2,vulture_launch[i]);
    r+=LAUNCH_BYTES;memcpy(r,"TLKGYF02",8);TlkDataPut32(r+8,FAREWELL_BYTES);TlkDataPut32(r+12,FAREWELL_LENGTH);memcpy(r+16,farewell_program,FAREWELL_LENGTH);for(unsigned i=0;i<8;i++)TlkDataPut16(r+50+i*2,farewell_colors[i]);return 1;
}
int TlkGraveyardDataRead(const uint8_t *p,size_t size,int apply){
    if(!p || size!=BYTES || memcmp(p,"TLKGYT13",8) || TlkDataGet32(p+8)!=ROW_BYTES || TlkDataGet32(p+12)!=ROWS)return 0;size_t n=OLD_BYTES;
    const uint8_t *shake=p+n;
    if(memcmp(shake,"TLKGYS01",8) || TlkDataGet32(shake+8)!=SHAKE_BYTES || TlkDataGet32(shake+12)!=4 ||
       TlkDataGet16(shake+16)!=30 || TlkDataGet16(shake+18)!=1 || TlkDataGet16(shake+20)!=0x34 || TlkDataGet16(shake+22)!=0x36)return 0;
    const uint8_t *pickups=shake+SHAKE_BYTES;
    if(memcmp(pickups,"TLKGYP01",8) || TlkDataGet32(pickups+8)!=PICKUP_BYTES || TlkDataGet32(pickups+12)!=PICKUPS)return 0;
    for(unsigned i=0;i<PICKUPS;i++){
        const uint8_t *v=pickups+16+i*8;
        if(TlkDataGet32(v)!=pickup_cells[i] || v[6]!=pickup_native[i] || v[7]!=pickup_md[i] ||
           TlkDataGet16(v+4)!=TlkDataGet16(p+16+pickup_cells[i]*5))return 0;
    }
    const uint8_t *bugs=pickups+PICKUP_BYTES;
    if(memcmp(bugs,"TLKGYA01",8) || TlkDataGet32(bugs+8)!=BUG_BYTES || TlkDataGet32(bugs+12)!=BUGS)return 0;
    for(unsigned i=0;i<BUGS;i++){
        const uint8_t *v=bugs+16+i*8;
        if(TlkDataGet32(v)!=bug_cells[i] || v[6]!=bug_native[i] || v[7]!=bug_md[i] ||
           TlkDataGet16(v+4)!=TlkDataGet16(p+16+bug_cells[i]*5))return 0;
    }
    const uint8_t *wall=bugs+BUG_BYTES;
    if(memcmp(wall,"TLKGYW01",8) || TlkDataGet32(wall+8)!=WALL_BYTES || TlkDataGet32(wall+12)!=4 ||
       TlkDataGet16(wall+16) || TlkDataGet16(wall+18)!=8 || TlkDataGet16(wall+20)!=0xffe0 || TlkDataGet16(wall+22)!=32)return 0;
    const uint8_t *perched=wall+WALL_BYTES;
    if(memcmp(perched,"TLKGYK01",8) || TlkDataGet32(perched+8)!=PERCHED_BYTES || TlkDataGet32(perched+12)!=PERCHED)return 0;
    for(unsigned i=0;i<PERCHED;i++){
        const uint8_t *v=perched+16+i*8;
        if(TlkDataGet32(v)!=perched_cells[i] || v[6]!=perched_native[i] || v[7]!=perched_md[i] ||
           TlkDataGet16(v+4)!=TlkDataGet16(p+16+perched_cells[i]*5))return 0;
    }
    const uint8_t *upper=perched+PERCHED_BYTES;
    if(memcmp(upper,"TLKGYZ01",8) || TlkDataGet32(upper+8)!=UPPER_BYTES || TlkDataGet32(upper+12)!=UPPER)return 0;
    for(unsigned i=0;i<UPPER;i++){
        const uint8_t *v=upper+16+i*8;
        if(TlkDataGet32(v)!=upper_cells[i] || v[6]!=upper_native[i] || v[7]!=upper_md[i] ||
           TlkDataGet16(v+4)!=TlkDataGet16(p+16+upper_cells[i]*5))return 0;
    }
    const uint8_t *head=upper+UPPER_BYTES;
    if(memcmp(head,"TLKGYH01",8) || TlkDataGet32(head+8)!=HEAD_BYTES || TlkDataGet32(head+12)!=55 || head[126] || head[127])return 0;
    for(unsigned i=0;i<51;i++)if(head[16+i]>24 || head[16+i]!=head[71+i])return 0;
    if(memcmp(head+16+51,"\x00\x01\x01\x02",4) || memcmp(head+71+51,"\x09\x36\xa0\x00",4))return 0;
    const uint8_t *turn=head+HEAD_BYTES;
    if(memcmp(turn,"TLKGYQ01",8) || TlkDataGet32(turn+8)!=TURN_BYTES || TlkDataGet32(turn+12)!=4 ||
       TlkDataGet16(turn+16)!=128 || TlkDataGet16(turn+18)!=160 || TlkDataGet16(turn+20)!=128 || TlkDataGet16(turn+22)!=160)return 0;
    const uint8_t *launch=turn+TURN_BYTES;
    if(memcmp(launch,"TLKGYJ01",8) || TlkDataGet32(launch+8)!=LAUNCH_BYTES || TlkDataGet32(launch+12)!=2 ||
       TlkDataGet16(launch+16)!=0 || TlkDataGet16(launch+18)!=1)return 0;
    const uint8_t *farewell=launch+LAUNCH_BYTES;
    if(memcmp(farewell,"TLKGYF02",8) || TlkDataGet32(farewell+8)!=FAREWELL_BYTES || TlkDataGet32(farewell+12)!=FAREWELL_LENGTH)return 0;
    const unsigned holds[]={100,48,14,16,16,48,100};
    const unsigned poses[]={0xc2fe4f,0xc2fe4f,0xc2feaa,0xc2ff01,0xc2ff58,0xc2ffaf,0xc2ffaf};
    for(unsigned i=0;i<7;i++)if(farewell[16+i*4]!=holds[i] || TlkDataGet32(farewell+16+i*4)>>8!=poses[i])return 0;
    if(memcmp(farewell+44,"\xfa\x02\xff\x6f\x56\xc2",6))return 0;
    for(unsigned i=0;i<CELLS;i++)if(p[16+i*5+4]>1)return 0;
    const uint8_t *tokens=p+16+sizeof cells;
    for(unsigned i=0;i<DEATH_TOKENS;i++)if(tokens[i*4]>=128 || tokens[i*4+3]!=0xc4)return 0;
    const uint8_t *r=p+n-MARKER_BYTES-BONE_BYTES-CONTACT_BYTES-VULTURE_BYTES;
    if(memcmp(r,"TLKGYM01",8) || TlkDataGet32(r+8)!=MARKER_BYTES || TlkDataGet32(r+12)!=2 ||
       TlkDataGet32(r+16)!=3443 || r[22] || r[23]!=88 ||
       TlkDataGet32(r+24)!=7081 || r[30]!=88 || r[31])return 0;
    const uint8_t *b=p+n-BONE_BYTES-CONTACT_BYTES-VULTURE_BYTES;
    if(memcmp(b,"TLKGYB01",8) || TlkDataGet32(b+8)!=BONE_BYTES || TlkDataGet32(b+12)!=BONE_DELTAS)return 0;
    for(unsigned i=0;i<BONE_DELTAS;i++){
        const uint8_t *v=b+16+i*8;
        if(TlkDataGet32(v)!=10248+i || v[6]!=(i?83+i:0) || v[7]!=(i<4?84+i:0))return 0;
    }
    const uint8_t *contact=p+n-CONTACT_BYTES-VULTURE_BYTES;
    if(memcmp(contact,"TLKGYC01",8) || TlkDataGet32(contact+8)!=CONTACT_BYTES || TlkDataGet32(contact+12)!=4)return 0;
    for(unsigned i=0;i<4;i++){
        const uint8_t *v=contact+16+i*96;
        for(unsigned j=0;j<8;j++){int value=(int16_t)TlkDataGet16(v+j*2);if(value < -256 || value >256)return 0;}
        if(TlkDataGet16(v) || TlkDataGet16(v+8) || TlkDataGet16(v+4)>36 ||
           TlkDataGet16(v+12)!=TlkDataGet16(v+4)+4 || TlkDataGet16(v+12)>38 ||
           (int16_t)TlkDataGet16(v+2)>(int16_t)TlkDataGet16(v+6) ||
           (int16_t)TlkDataGet16(v+10)>(int16_t)TlkDataGet16(v+14))return 0;
    }
    unsigned delay=TlkDataGet32(contact+400);if(!delay || delay>255)return 0;
    const uint8_t *v=p+n-VULTURE_BYTES;
    if(memcmp(v,"TLKGYV01",8) || TlkDataGet32(v+8)!=VULTURE_BYTES || TlkDataGet32(v+12)!=2 ||
       TlkDataGet32(v+16)!=10785 || v[22]!=34 || v[23] ||
       TlkDataGet32(v+24)!=10786 || v[30] || v[31]!=34)return 0;
    for(unsigned i=0;i<8;i++)if(TlkDataGet16(farewell+50+i*2)!=farewell_expected[i])return 0;
    if(apply){for(unsigned i=0;i<8;i++)farewell_colors[i]=TlkDataGet16(farewell+50+i*2);memcpy(farewell_program,farewell+16,FAREWELL_LENGTH);for(unsigned i=0;i<2;i++)vulture_launch[i]=TlkDataGet16(launch+16+i*2);for(unsigned i=0;i<4;i++)vulture_turn[i]=TlkDataGet16(turn+16+i*2);memcpy(head_native,head+16,55);memcpy(head_md,head+71,55);memcpy(upper_markers,upper+16,sizeof upper_markers);memcpy(perched_markers,perched+16,sizeof perched_markers);for(unsigned i=0;i<4;i++)wall_rules[i]=TlkDataGet16(wall+16+i*2);memcpy(bug_markers,bugs+16,sizeof bug_markers);memcpy(pickup_markers,pickups+16,sizeof pickup_markers);for(unsigned i=0;i<4;i++)shake_rules[i]=TlkDataGet16(shake+16+i*2);memcpy(vulture_markers,v+16,16);bone_contact_delay=delay;memcpy(bone_contact,contact+16,sizeof bone_contact);memcpy(bone_markers,b+16,sizeof bone_markers);memcpy(reveal_markers,r+16,16);memcpy(cells,p+16,sizeof cells);memcpy(death_tokens,tokens,sizeof death_tokens);ready=1;}return 1;
}
int TlkGraveyardDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    ready=0;if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    /* MD23F4/242E pass actorY-8 to the ordinary wall helper. Native C6DF/C5FA
     * pass actorY without that subtraction. Preserve the callers' signed X. */
    if(memcmp(m+0x2406,"\x32\x28\x00\x0a\x51\x41",6) ||
       memcmp(m+0x2440,"\x32\x28\x00\x0a\x51\x41",6) ||
       memcmp(m+0x19b204,"\x3f\x3c\xff\xe0",4) || memcmp(m+0x19b22a,"\x3f\x3c\x00\x20",4) ||
       memcmp(s+0xc6df,"\xa0\x0a\xb1\x68\x85\x50\x80",7) ||
       memcmp(s+0xc5fa,"\xa0\x0a\xb1\x68\x85\x50\x80",7) ||
       memcmp(s+0x1406a,"\xf4\xe0\xff\x22\x01\xc8\xc0",7) ||
       memcmp(s+0x14085,"\xf4\x20\x00\x22\x2b\xc8\xc0",7))return 0;
    wall_rules[0]=0;wall_rules[1]=(be16(m+0x240a)>>9)&7;if(!wall_rules[1])wall_rules[1]=8;
    wall_rules[2]=be16(m+0x19b206);wall_rules[3]=be16(m+0x19b22c);
    /* MD's actual random draw drives vertical shake; native fixed horizontal
     * animation is replaced by the runtime adapter, with original countdown. */
    if(memcmp(m+0x1a1b10,"\x4e\xb9\x00\x00\x0b\x28\x34\x00\x02\x42\x00\x01",12) ||
       memcmp(m+0x1a1a82,"\x33\x7c\x00\x1e\x00\x2c",6) ||
       memcmp(m+0x1a1a8e,"\x33\x69\x00\x08\x00\x34\x33\x69\x00\x0a\x00\x36",12) ||
       memcmp(s+0x19ac9,"\x22\x09\xaf\xc0\x4c\x03\x9b",7) ||
       memcmp(s+0x26da8,"\x00\x01\x00\x00\xff\x00\xff\xa8\x6d\xc2",10))return 0;
    shake_rules[0]=be16(m+0x1a1a84);shake_rules[1]=be16(m+0x1a1b1a);
    shake_rules[2]=be16(m+0x1a1a92);shake_rules[3]=be16(m+0x1a1a98);
    if(memcmp(s+0xbe11+50*6,"\xfc\xcb\xc0\xe6\x8c\xc5",6) ||
       memcmp(m+0x92adc+50*8,"\x00\x18\xd4\x14\x00\x0d\x14\x26",8))return 0;
    if(memcmp(s+0xbe11+83*6,"\xad\xdb\xc0\x02\x8e\xc5",6) ||
       memcmp(m+0x92adc+83*8,"\x00\x09\x32\x22\x00\x0d\x18\x1e",8) ||
       memcmp(s+0xbe11+118*6,"\xe6\xcb\xc0\xca\x8c\xc5",6) ||
       memcmp(m+0x92adc+118*8,"\x00\x18\xd3\xf2\x00\x0d\x13\xf6",8))return 0;
    const uint8_t *sr=s+0x3eb,*mr=m+0x1cfdb4+96;
    if(le16(sr+18)!=ROW_BYTES || le16(sr+20)!=ROWS || be16(mr+12)!=ROW_BYTES || be16(mr+14)!=ROWS)return 0;
    uint8_t *sm=malloc(CELLS*2),*mm=malloc(CELLS*2),*sc=malloc(65536);size_t a=0,b=0,c=0;
    int ok=sm && mm && sc && TlkMdDecompress(s,sn,le24(sr+9),sm,CELLS*2,&a) && a==CELLS*2 &&
        TlkMdDecompress(m,mn,be32(mr+16),mm,CELLS*2,&b) && b==CELLS*2 && TlkMdDecompress(s,sn,le24(sr),sc,65536,&c);
    unsigned sh=le24(sr+3),mc=be32(mr+4),mh=be32(mr+8),markers=0,bones=0,native_bones=0,md_bones=0,vultures=0,native_vultures=0,md_vultures=0,pickups=0,bugs=0,perched=0,native_perched=0,md_perched=0,upper=0,ns=0,ms=0,np=0,mp=0;
    for(unsigned i=0;i<CELLS && ok;i++){
        unsigned sw=le16(sm+i*2),mw=be16(mm+i*2),so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if(so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
        unsigned native_marker=sc[so+3],md_marker=m[mc+mo+3];
        if((native_marker==17 || native_marker==18 || md_marker==17 || md_marker==18) && native_marker!=md_marker){
            if(pickups>=PICKUPS || i!=pickup_cells[pickups] || native_marker!=pickup_native[pickups] || md_marker!=pickup_md[pickups]){ok=0;break;}
            uint8_t *v=pickup_markers+pickups++*8;TlkDataPut32(v,i);TlkDataPut16(v+4,sw);v[6]=native_marker;v[7]=md_marker;
        }
        if((native_marker==102 || md_marker==102) && native_marker!=md_marker){
            if(bugs>=BUGS || i!=bug_cells[bugs] || native_marker!=bug_native[bugs] || md_marker!=bug_md[bugs]){ok=0;break;}
            uint8_t *v=bug_markers+bugs++*8;TlkDataPut32(v,i);TlkDataPut16(v+4,sw);v[6]=native_marker;v[7]=md_marker;
        }
        ns+=native_marker==83;ms+=md_marker==83;np+=native_marker==118;mp+=md_marker==118;
        if((native_marker==83 || native_marker==118 || md_marker==83 || md_marker==118) && native_marker!=md_marker){
            if(upper>=UPPER || i!=upper_cells[upper] || native_marker!=upper_native[upper] || md_marker!=upper_md[upper]){ok=0;break;}
            uint8_t *v=upper_markers+upper++*8;TlkDataPut32(v,i);TlkDataPut16(v+4,sw);v[6]=native_marker;v[7]=md_marker;
        }
        native_perched+=native_marker==50;md_perched+=md_marker==50;
        if((native_marker==50 || md_marker==50) && native_marker!=md_marker){
            if(perched>=PERCHED || i!=perched_cells[perched] || native_marker!=perched_native[perched] || md_marker!=perched_md[perched]){ok=0;break;}
            uint8_t *v=perched_markers+perched++*8;TlkDataPut32(v,i);TlkDataPut16(v+4,sw);v[6]=native_marker;v[7]=md_marker;
        }
        int nv=native_marker>=33 && native_marker<=37,mv=md_marker>=33 && md_marker<=37;
        native_vultures+=nv;md_vultures+=mv;
        if((nv || mv) && native_marker!=md_marker){
            if(vultures>=2 || i!=10785+vultures || native_marker!=(vultures?0:34) || md_marker!=(vultures?34:0)){ok=0;break;}
            uint8_t *v=vulture_markers+vultures++*8;TlkDataPut32(v,i);TlkDataPut16(v+4,sw);v[6]=native_marker;v[7]=md_marker;
        }
        int nb=native_marker>=84 && native_marker<=87,mb=md_marker>=84 && md_marker<=87;
        native_bones+=nb;md_bones+=mb;
        if((nb || mb) && native_marker!=md_marker){
            if(bones>=BONE_DELTAS || i!=10248+bones || native_marker!=(bones?83+bones:0) || md_marker!=(bones<4?84+bones:0)){ok=0;break;}
            uint8_t *r=bone_markers+bones++*8;TlkDataPut32(r,i);TlkDataPut16(r+4,sw);r[6]=native_marker;r[7]=md_marker;
        }
        if(native_marker==88 || md_marker==88){
            if(markers>=2 || (markers==0?(i!=3443 || native_marker || md_marker!=88):(i!=7081 || native_marker!=88 || md_marker))){ok=0;break;}
            uint8_t *r=reveal_markers+markers++*8;TlkDataPut32(r,i);TlkDataPut16(r+4,sw);r[6]=native_marker;r[7]=md_marker;
        }
        unsigned sp=le16(sc+so),mp=m[mc+mo]*16u;
        if(sh>=sn || sp+16>sn-sh || mh>=mn || mp+16>mn-mh){ok=0;break;}
        uint8_t *p=cells+i*5;p[0]=(uint8_t)sw;p[1]=(uint8_t)(sw>>8);p[2]=sc[so+2];p[3]=m[mc+mo+2];p[4]=(sw&7)==(mw&7);
        for(unsigned x=0;x<16;x++)if((s[sh+sp+x]&31)!=(m[mh+mp+x]&31))p[4]=0;
    }
    for(unsigned i=0;i<DEATH_TOKENS && ok;i++){
        const uint8_t *a=s+0xebec+i*4,*b=m+0x7e5b2+i*4;
        if(a[0]>=128 || a[0]!=b[0] || a[3]!=0xc4){ok=0;break;}
        memcpy(death_tokens+i*4,a,4);
    }
    const unsigned md_poses[]={0xe69a6,0xe69fe,0xe6a26,0xe6a4e};
    const unsigned native_heights[]={0xdde4,0xddff,0xde13,0xde29},md_records[]={0x93696,0x936c0,0x936ea,0x93716};
    for(unsigned i=0;i<4 && ok;i++){
        uint8_t *v=bone_contact+i*96;unsigned mp=be32(m+md_records[i]);
        if(mp>mn-40){ok=0;break;}
        for(unsigned j=0;j<4;j++){
            TlkDataPut16(v+j*2,le16(s+(bone_poses[i]&0x3fffff)+12+j*2));
            TlkDataPut16(v+8+j*2,be16(m+md_poses[i]+12+j*2));
        }
        if(le16(v) || le16(v+8) || le16(v+4)+4!=le16(v+12) || le16(v+12)>38){ok=0;break;}
        memcpy(v+16,s+native_heights[i],40);memcpy(v+56,m+mp,40);
    }
    /* Native flight turns use cameraX+128. Original MD divides its320px
     * viewport by2 at both turn tests; presentation width stays independent. */
    if(memcmp(s+0x175cd,"\xa9\x80\x00",3) || memcmp(s+0x17635,"\xa9\x80\x00",3) ||
       memcmp(m+0x1a06b2,"\x36\x3c\x01\x40\x86\xfc\x00\x02",8) ||
       memcmp(m+0x1a0722,"\x36\x3c\x01\x40\x86\xfc\x00\x02",8))ok=0;
    /* Native branches on its high-word AND0; MD tests low-bit parity of a
     * global VBlank counter plus launch count. Decode the effective masks;
     * the runtime selects the clock domain without reading cartridge code. */
    if(memcmp(s+0x17152,"\x29\x00\x00\x85\x0e\xd0",6) ||
       memcmp(m+0x1a0232,"\x02\x82\x00\x00\x00\x01",6) ||
       memcmp(m+0x1a0226,"\x24\x39\xff\xff\x81\xbe",6) ||
       memcmp(m+0x1424,"\x52\xb8\x81\xbe",4))ok=0;
    vulture_launch[0]=le16(s+0x17153);vulture_launch[1]=(uint16_t)be32(m+0x1a0234);
    vulture_turn[0]=le16(s+0x175ce);vulture_turn[1]=be16(m+0x1a06b4)/2;
    vulture_turn[2]=le16(s+0x17636);vulture_turn[3]=be16(m+0x1a0724)/2;
    /* Normalize the original MD farewell tokens to native semantic pose
     * identities. Keep both repeated-pose holds and the real phase2/loop,
     * omitting the native-only phase3 callback. No ROM script is read at runtime. */
    const unsigned native_at[]={0,6,10,14,18},native_holds[]={100,14,16,16,100};
    const unsigned native_poses[]={0xc2fe4f,0xc2feaa,0xc2ff01,0xc2ff58,0xc2ffaf};
    const unsigned farewell_md_poses[]={0xe6a86,0xe6a86,0xe6b1e,0xe6b96,0xe6c0e,0xe6c86,0xe6c86};
    const unsigned md_holds[]={100,48,14,16,16,48,100},pose_index[]={0,0,1,2,3,4,4};
    unsigned np_at=0x2565b,mp_at=0xd16e4;
    if(memcmp(s+0x48495,"\xa9\x3b\x56",3) || memcmp(m+0x1a44ac,"\x41\xf9\x00\x0d\x16\xda",6) ||
       be32(m+0xd16dc)!=mp_at || le16(s+0x2563c)!=0x565b || s[0x25645]!=0xc2 ||
       memcmp(s+np_at+4,"\xfa\x03",2) || memcmp(s+np_at+22,"\xfa\x02\xff\x6d\x56\xc2",6) ||
       memcmp(m+mp_at+28,"\xfd\x02\xff\x0d\x16\xf8",6))ok=0;
    for(unsigned i=0;i<5;i++)if(s[np_at+native_at[i]]!=native_holds[i] ||
       (le16(s+np_at+native_at[i]+1)|(unsigned)s[np_at+native_at[i]+3]<<16)!=native_poses[i])ok=0;
    for(unsigned i=0;i<7;i++){
        if(m[mp_at+i*4]!=md_holds[i] || (be32(m+mp_at+i*4)&0xffffff)!=farewell_md_poses[i])ok=0;
        farewell_program[i*4]=m[mp_at+i*4];
        memcpy(farewell_program+i*4+1,s+np_at+native_at[pose_index[i]]+1,3);
    }
    farewell_program[28]=s[np_at+22];farewell_program[29]=m[mp_at+29];farewell_program[30]=m[mp_at+30];
    TlkDataPut16(farewell_program+31,(uint16_t)(le16(s+0x2563c)+(be32(m+mp_at+30)&0xffffff)-mp_at));
    farewell_program[33]=s[np_at+27];
    /* Original farewell palette: CRAM56..63 agrees with this ROM table,
     * rather than the ordinary Graveyard scene palette. */
    if(be32(m+0x1cad4c)!=0x1cad6e)ok=0;
    for(unsigned i=0;i<8;i++){farewell_colors[i]=be16(m+0x1cad7e + i*2);if(farewell_colors[i]!=farewell_expected[i])ok=0;}
    /* The legal inclusive head width reaches four bytes beyond the first
     * descending surface. Preserve the original data there, including MD's
     * signed byte, rather than inventing a repeated or clamped edge. */
    if(be32(m+0x93658)!=0x93664 || le16(s+0x30001+16)!=54 || be16(m+0xe692e +16)!=54)ok=0;
    memcpy(head_native,s+0xddb2,55);memcpy(head_md,m+0x93664,55);
    for(unsigned i=0;i<51;i++)if(head_native[i]>24 || head_native[i]!=head_md[i])ok=0;
    if(memcmp(head_native+51,"\x00\x01\x01\x02",4) || memcmp(head_md+51,"\x09\x36\xa0\x00",4))ok=0;
    /* Original MD93450 arms the existing contact suppression byte when a
     * previous-grounded platform query fails. SNES returns without that store. */
    if(memcmp(m+0x93450,"\x16\xbc\x00\x0a",4) || memcmp(s+0xd8ed,"\xa0\x08\x38\xf1\x68",5))ok=0;
    bone_contact_delay=be16(m+0x93452);
    free(sm);free(mm);free(sc);ready=ok && upper==UPPER && ns==0 && ms==1 && np==2 && mp==2 && perched==PERCHED && native_perched==4 && md_perched==3 && bugs==BUGS && pickups==PICKUPS && markers==2 && bones==BONE_DELTAS && native_bones==12 && md_bones==12 && vultures==2 && native_vultures==5 && md_vultures==5;return ready;
}
int TlkGraveyardDeathPose(unsigned age,unsigned *pose){
    if(!ready || !pose)return 0;if(age>224)age=224;
    for(unsigned i=0;i<DEATH_TOKENS;i++){
        const uint8_t *p=death_tokens+i*4;
        if(age<=p[0]){*pose=p[1]|(unsigned)p[2]<<8|(unsigned)p[3]<<16;return 1;}
        age-=p[0]+1;
    }return 0;
}
int TlkGraveyardGroundTag(unsigned x,unsigned y,unsigned native_tag,const uint8_t *ram,unsigned *tag){
    if(!ready || !ram || !tag || x>=4160 || y>=768 || le16(ram+0xd0)!=ROW_BYTES)return 0;
    unsigned base=ram[0xe9]|(unsigned)ram[0xea]<<8|(unsigned)ram[0xeb]<<16;
    if(base<0x7e0000 || base>0x800000-CELLS*2)return 0;
    unsigned i=(y/16)*(ROW_BYTES/2)+x/16;const uint8_t *p=cells+i*5;
    if(!p[4] || native_tag!=p[2] || le16(ram+base-0x7e0000+i*2)!=le16(p))return 0;
    *tag=p[3];return 1;
}

int TlkGraveyardRevealMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md)return 0;
    for(unsigned i=0;i<2;i++){
        const uint8_t *r=reveal_markers+i*8;
        if(TlkDataGet32(r)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(r+4)&0xfff8) || native!=r[6])return 0;
        *md=r[7];return 1;
    }
    return 0;
}

int TlkGraveyardBoneMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md)return 0;
    for(unsigned i=0;i<BONE_DELTAS;i++){
        const uint8_t *r=bone_markers+i*8;if(TlkDataGet32(r)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(r+4)&0xfff8) || native!=r[6])return 0;
        *md=r[7];return 1;
    }
    return 0;
}

int TlkGraveyardBoneContact(unsigned pose,unsigned component,unsigned index,unsigned *native,unsigned *md){
    if(!ready || !native || !md || component>4 || (component==4 && index>=39))return 0;
    for(unsigned i=0;i<4;i++)if(pose==bone_poses[i]){
        const uint8_t *v=bone_contact+i*96;
        *native=le16(v+(component==4?16+index:component*2));
        *md=le16(v+(component==4?56+index:8+component*2));return 1;
    }
    return 0;
}

int TlkGraveyardBoneContactDelay(unsigned *delay){if(!ready || !delay)return 0;*delay=bone_contact_delay;return 1;}

int TlkGraveyardVultureMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md)return 0;
    for(unsigned i=0;i<2;i++){
        const uint8_t *v=vulture_markers+i*8;if(TlkDataGet32(v)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(v+4)&0xfff8) || native!=v[6])return 0;
        *md=v[7];return 1;
    }
    return 0;
}

int TlkGraveyardPickupMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md)return 0;
    for(unsigned i=0;i<PICKUPS;i++){
        const uint8_t *v=pickup_markers+i*8;if(TlkDataGet32(v)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(v+4)&0xfff8) || native!=v[6])return 0;
        *md=v[7];return 1;
    }
    return 0;
}

int TlkGraveyardBugMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md)return 0;
    for(unsigned i=0;i<BUGS;i++){
        const uint8_t *v=bug_markers+i*8;if(TlkDataGet32(v)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(v+4)&0xfff8) || native!=v[6])return 0;
        *md=v[7];return 1;
    }
    return 0;
}

int TlkGraveyardPerchedMarker(unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md)return 0;
    for(unsigned i=0;i<PERCHED;i++){
        const uint8_t *v=perched_markers+i*8;if(TlkDataGet32(v)!=cell)continue;
        if((live&0xfff8)!=(TlkDataGet16(v+4)&0xfff8) || native!=v[6])return 0;
        *md=v[7];return 1;
    }
    return 0;
}

int TlkGraveyardUpperMarker(unsigned marker,unsigned cell,unsigned live,unsigned native,unsigned *md){
    if(!ready || !md || (marker!=83 && marker!=118))return 0;
    for(unsigned i=0;i<UPPER;i++){
        const uint8_t *v=upper_markers+i*8;if(TlkDataGet32(v)!=cell || (v[6]!=marker && v[7]!=marker))continue;
        if((live&0xfff8)!=(TlkDataGet16(v+4)&0xfff8) || native!=v[6])return 0;
        *md=v[7];return 1;
    }
    return 0;
}

int TlkGraveyardHeadSurface(unsigned index,unsigned live,unsigned *md){
    if(!ready || !md || index>=55 || live!=head_native[index])return 0;
    *md=(uint16_t)(int16_t)(int8_t)head_md[index];return 1;
}

int TlkGraveyardVultureTurn(unsigned left,unsigned *native,unsigned *md){
    if(!ready || !native || !md || left>1)return 0;
    *native=vulture_turn[left*2];*md=vulture_turn[left*2+1];return 1;
}

int TlkGraveyardVultureLaunch(unsigned *native,unsigned *md){
    if(!ready || !native || !md)return 0;
    *native=vulture_launch[0];*md=vulture_launch[1];return 1;
}

int TlkGraveyardFarewellValue(unsigned cursor,unsigned width,unsigned *value){
    if(!ready || !value || !width || width>3 || cursor<0xc2565b || cursor>0xc2565b+FAREWELL_LENGTH-width)return 0;
    unsigned offset=cursor-0xc2565b,result=0;
    for(unsigned i=0;i<width;i++)result|=(unsigned)farewell_program[offset+i]<<(i*8);
    *value=result;return 1;
}

int TlkGraveyardFarewellPalette(uint16_t colors[8]){
    if(!ready || !colors)return 0;memcpy(colors,farewell_colors,sizeof farewell_colors);return 1;
}

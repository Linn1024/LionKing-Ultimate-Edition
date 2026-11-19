/* Source map operands for Simba's Return and Pride Rock. No runtime ROM reads. */
#include "tlk_late_scene_data.h"
#include "tlk_data_record.h"
#include <string.h>
#ifdef TLK_INTERLEVEL_PREPARER
#include "tlk_md_assets.h"
#include <stdlib.h>
#endif
enum { SCENES=2,CELL_BYTES=40,MARKER_BYTES=8,HEADER=16,SCENE_HEADER=24,
       MAX_TERRAIN=1306,MAX_MARKERS=20,LEDGE_BYTES=16,ROOM_BYTES=64,DOOR_BYTES=12,HYENA_BYTES=184,EXIT_BYTES=16,SCAR_BYTES=48 };
static const struct {unsigned level,descriptor,row,rows,terrain,markers;} scenes[]={
    {8,0x517,550,43,1306,4},{9,0x549,200,100,410,20}};
static uint8_t terrain[SCENES][MAX_TERRAIN][CELL_BYTES];
static uint8_t markers[SCENES][MAX_MARKERS][MARKER_BYTES];
static int ready;
static uint16_t adult_ledge[4];
static uint16_t return_door[2];
static uint8_t hyena_bounds[7][24];
static uint16_t return_exit[4];
static uint8_t scar_activation[2][12];
static uint16_t scar_reveal[2];
const uint16_t *TlkLateSceneScarRevealRules(void){return ready?scar_reveal:NULL;}
const uint16_t *TlkLateSceneReturnExitRules(void){return ready?return_exit:NULL;}
const uint16_t *TlkLateSceneReturnDoorRules(void){return ready?return_door:NULL;}
static uint8_t room_hyenas[2][24];
const uint16_t *TlkLateSceneAdultLedgeRules(void){return ready?adult_ledge:NULL;}
static int index_for(unsigned level){return level==8?0:level==9?1:-1;}
int TlkLateSceneDataReady(void){return ready;}
static size_t record_size(void){
    size_t n=HEADER;
    for(unsigned i=0;i<SCENES;i++)n+=SCENE_HEADER+scenes[i].terrain*CELL_BYTES+scenes[i].markers*MARKER_BYTES;
    return n+LEDGE_BYTES+ROOM_BYTES+DOOR_BYTES+HYENA_BYTES+EXIT_BYTES+SCAR_BYTES;
}
size_t TlkLateSceneDataRecordSize(void){return ready?record_size():0;}
#ifdef TLK_INTERLEVEL_PREPARER
static unsigned be16(const uint8_t*p){return (unsigned)p[0]<<8|p[1];}
static unsigned pointer(const uint8_t*p,int md){
    return md?((unsigned)p[0]<<24|(unsigned)p[1]<<16|(unsigned)p[2]<<8|p[3]):
        (TlkDataGet16(p)|(unsigned)p[2]<<16)&0x3fffff;
}
static int prepare_scene(unsigned k,const uint8_t*s,size_t sn,const uint8_t*m,size_t mn){
    const uint8_t*sr=s+scenes[k].descriptor,*mr=m+0x1cfdb4+scenes[k].level*48;
    unsigned bytes=scenes[k].row*scenes[k].rows,tc=0,mcnt=0;
    if(TlkDataGet16(sr+18)!=scenes[k].row || TlkDataGet16(sr+20)!=scenes[k].rows ||
       be16(mr+12)!=scenes[k].row || be16(mr+14)!=scenes[k].rows)return 0;
    uint8_t *sm=malloc(bytes),*mm=malloc(bytes),*sc=malloc(65536);size_t a=0,b=0,c=0;
    int ok=sm&&mm&&sc&&TlkMdDecompress(s,sn,pointer(sr+9,0),sm,bytes,&a)&&a==bytes&&
        TlkMdDecompress(m,mn,pointer(mr+16,1),mm,bytes,&b)&&b==bytes&&
        TlkMdDecompress(s,sn,pointer(sr,0),sc,65536,&c);
    unsigned sh=pointer(sr+3,0),mc=pointer(mr+4,1),mh=pointer(mr+8,1);
    for(unsigned cell=0;ok&&cell<bytes/2;cell++){
        unsigned sw=TlkDataGet16(sm+cell*2),mw=be16(mm+cell*2),so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if((sw&7)!=(mw&7)||so+4>c||mc>=mn||mo+4>mn-mc){ok=0;break;}
        unsigned nh=TlkDataGet16(sc+so),eh=m[mc+mo]*16u;
        if(sh>=sn||nh+16>sn-sh||mh>=mn||eh+16>mn-mh){ok=0;break;}
        unsigned nm=sc[so+3],em=m[mc+mo+3];
        if(sc[so+2]!=m[mc+mo+2]||memcmp(s+sh+nh,m+mh+eh,16)||(k==1&&nm!=em)){
            if(tc>=scenes[k].terrain){ok=0;break;}
            uint8_t*p=terrain[k][tc++];TlkDataPut32(p,cell);TlkDataPut16(p+4,sw);
            p[6]=sc[so+2];p[7]=m[mc+mo+2];memcpy(p+8,s+sh+nh,16);memcpy(p+24,m+mh+eh,16);
        }
        if(nm!=em){
            if(mcnt>=scenes[k].markers){ok=0;break;}
            uint8_t*p=markers[k][mcnt++];TlkDataPut32(p,cell);TlkDataPut16(p+4,sw);p[6]=nm;p[7]=em;
        }
    }
    free(sm);free(mm);free(sc);return ok&&tc==scenes[k].terrain&&mcnt==scenes[k].markers;
}
#endif
int TlkLateSceneDataPrepare(const uint8_t*s,size_t sn,const uint8_t*m,size_t mn){
    ready=0;
#ifdef TLK_INTERLEVEL_PREPARER
    if(!s||!m||sn!=0x300000||mn!=0x300000)return 0;
    if(memcmp(s+0x33dcf,"\x29\xbf\xff",3)||memcmp(s+0x33fb9,"\x29\xbf\xff",3)||
       memcmp(m+0x194c28,"\x00\x69\x00\x80\x00\x4c",6)||
       memcmp(m+0x194e34,"\x00\x69\x00\x80\x00\x4c",6)||
       memcmp(m+0x18f398,"\x00\x69\x00\x40\x00\x4c",6)||
       memcmp(s+0x34007,"\x69\x0c\x00",3)||
       memcmp(m+0x194e86,"\x04\x69\x00\x0c\x00\x08",6))return 0;
    adult_ledge[0]=(uint16_t)be16(m+0x194c2a);
    adult_ledge[1]=(uint16_t)be16(m+0x18f39a);
    adult_ledge[2]=TlkDataGet16(s+0x34008);
    adult_ledge[3]=(uint16_t)(0-be16(m+0x194e88));
    if(memcmp(s+0x388d8,"\xa9\x1b\x00",3)||memcmp(m+0x1993e6,"\x33\x7c\x00\x1c\x00\x2c",6))return 0;
    return_door[0]=TlkDataGet16(s+0x388d9);return_door[1]=(uint16_t)be16(m+0x1993e8);
    if(memcmp(s+0xd439,"\xa9\x28\x00\x91\x68",5)||memcmp(s+0xd42f,"\xc9\x01\x00",3)||
       memcmp(m+0x1cdcc8,"\x52\x79\xff\xff\xe9\x90\x0c\x79\x00\x3c\xff\xff\xe9\x90",14)||
       memcmp(m+0x1cdcea,"\x33\xfc\x00\x01\xff\xff\xe9\x90",8))return 0;
    return_exit[0]=TlkDataGet16(s+0xd43a);return_exit[1]=(uint16_t)be16(m+0x1cdcec);
    return_exit[2]=(uint16_t)be16(m+0x1cdcd0);return_exit[3]=0;
    if(memcmp(s+0x65d73,"\xc9\x18\x00",3)||memcmp(m+0x1b0fb0,"\x0c\x40\x00\x10",4))return 0;
    scar_reveal[0]=TlkDataGet16(s+0x65d74);scar_reveal[1]=(uint16_t)be16(m+0x1b0fb2);
    for(unsigned i=0;i<2;i++){
        unsigned sa=0x585f4+i*12,ma=0x15690a+i*14;
        unsigned native=TlkDataGet16(s+sa+9)|(unsigned)s[sa+11]<<16;
        unsigned main=TlkDataGet16(s+sa)|(unsigned)s[sa+2]<<16;
        unsigned md_init=pointer(m+ma+10,1),md_main=pointer(m+ma,1);
        if(native!=0xc58589||main!=(i?0xc65da0u:0xc65c8au)||md_init!=md_main||md_init!=(i?0x1b0fe4u:0x1b0eb8u))return 0;
        uint8_t*q=scar_activation[i];TlkDataPut32(q,sa|0xc00000);TlkDataPut32(q+4,native);TlkDataPut32(q+8,main);
    }
    if(memcmp(s+0x24ee6,"\xfa\x00",2)||memcmp(m+0x14013e,"\xfd\x00",2))return 0;
    for(unsigned i=0;i<7;i++){
        unsigned sa=i?0x24ee8+(i-1)*4:0x24ddc,ma=i?0x140140+(i-1)*4:0x140044;
        if(s[sa]!=3||m[ma]!=3)return 0;
        unsigned pose=TlkDataGet16(s+sa+1)|(unsigned)s[sa+3]<<16;
        unsigned mp=(unsigned)m[ma+1]<<16|(unsigned)m[ma+2]<<8|m[ma+3],np=pose&0x3fffff;
        if(pose<0xc60000||pose>=0xc70000||np>sn-20||mp>mn-20)return 0;
        uint8_t*q=hyena_bounds[i];TlkDataPut32(q,pose);TlkDataPut32(q+4,(sa+4)|0xc00000);
        for(unsigned j=0;j<4;j++){
            TlkDataPut16(q+8+j*2,TlkDataGet16(s+np+12+j*2));
            TlkDataPut16(q+16+j*2,(uint16_t)be16(m+mp+12+j*2));
        }
    }
    unsigned changed=0;
    for(unsigned door=0;door<32;door++){
        unsigned np=TlkDataGet16(s+0x66bc+door*2),mp=pointer(m+0x7d902+door*4,1);
        if(0x66fc+np+10>sn||mp>mn-2)return 0;
        unsigned nc=TlkDataGet16(s+0x66fc+np),mc=be16(m+mp);
        if(nc>16||mc>16||0x66fc+np+2+nc*4>sn||mp+2+mc*4>mn)return 0;
        int different=nc!=mc;
        for(unsigned j=0;j<nc&&j<mc;j++)for(unsigned side=0;side<2;side++)
            if(TlkDataGet16(s+0x66fc+np+2+j*4+side*2)!=be16(m+mp+2+j*4+side*2))different=1;
        if(!different)continue;
        if(changed>=2||door!=(changed?29u:27u)||np!=64||nc!=1||mc!=2)return 0;
        uint8_t*q=room_hyenas[changed++];TlkDataPut16(q,door);TlkDataPut16(q+2,np);
        TlkDataPut16(q+4,nc);TlkDataPut16(q+6,mc);
        for(unsigned j=0;j<4;j++){
            TlkDataPut16(q+8+j*2,TlkDataGet16(s+0x66fc+np+2+j*2));
            TlkDataPut16(q+16+j*2,be16(m+mp+2+j*2));
        }
    }
    if(changed!=2)return 0;
    for(unsigned i=0;i<SCENES;i++)if(!prepare_scene(i,s,sn,m,mn))return 0;
    ready=1;return 1;
#else
    (void)s;(void)sn;(void)m;(void)mn;return 0;
#endif
}
int TlkLateSceneDataWrite(uint8_t*p,size_t n){
    if(!ready||!p||n!=record_size())return 0;
    memcpy(p,"TLKLTG07",8);TlkDataPut32(p+8,SCENES);TlkDataPut32(p+12,(uint32_t)n);size_t at=HEADER;
    for(unsigned i=0;i<SCENES;i++){
        uint8_t*q=p+at;TlkDataPut32(q,scenes[i].level);TlkDataPut32(q+4,scenes[i].row);TlkDataPut32(q+8,scenes[i].rows);
        TlkDataPut32(q+12,scenes[i].terrain);TlkDataPut32(q+16,scenes[i].markers);TlkDataPut32(q+20,0);at+=SCENE_HEADER;
        size_t bytes=scenes[i].terrain*CELL_BYTES;memcpy(p+at,terrain[i],bytes);at+=bytes;
        bytes=scenes[i].markers*MARKER_BYTES;memcpy(p+at,markers[i],bytes);at+=bytes;
    }
    memcpy(p+at,"TLKALR01",8);for(unsigned i=0;i<4;i++)TlkDataPut16(p+at+8+i*2,adult_ledge[i]);
    at+=LEDGE_BYTES;memcpy(p+at,"TLKRHY01",8);TlkDataPut32(p+at+8,2);TlkDataPut32(p+at+12,ROOM_BYTES);
    memcpy(p+at+16,room_hyenas,sizeof room_hyenas);at+=ROOM_BYTES;
    memcpy(p+at,"TLKRDT01",8);TlkDataPut16(p+at+8,return_door[0]);TlkDataPut16(p+at+10,return_door[1]);at+=DOOR_BYTES;
    memcpy(p+at,"TLKHYO01",8);TlkDataPut32(p+at+8,7);TlkDataPut32(p+at+12,HYENA_BYTES);
    memcpy(p+at+16,hyena_bounds,sizeof hyena_bounds);at+=HYENA_BYTES;
    memcpy(p+at,"TLKREX01",8);for(unsigned i=0;i<4;i++)TlkDataPut16(p+at+8+i*2,return_exit[i]);at+=EXIT_BYTES;
    memcpy(p+at,"TLKSCA01",8);TlkDataPut32(p+at+8,2);TlkDataPut32(p+at+12,SCAR_BYTES);memcpy(p+at+16,scar_activation,sizeof scar_activation);
    TlkDataPut16(p+at+40,scar_reveal[0]);TlkDataPut16(p+at+42,scar_reveal[1]);TlkDataPut32(p+at+44,0);return at+SCAR_BYTES==n;
}
static int ordered(const uint8_t*p,unsigned count,unsigned stride,unsigned limit){
    unsigned previous=0;
    for(unsigned i=0;i<count;i++,p+=stride){unsigned cell=TlkDataGet32(p);if(cell>=limit||(i&&cell<=previous))return 0;previous=cell;}
    return 1;
}
int TlkLateSceneDataRead(const uint8_t*p,size_t n,int apply){
    if(!p||n!=record_size()||memcmp(p,"TLKLTG07",8)||TlkDataGet32(p+8)!=SCENES||TlkDataGet32(p+12)!=n)return 0;
    size_t at=HEADER;
    for(unsigned i=0;i<SCENES;i++){
        const uint8_t*q=p+at;
        if(TlkDataGet32(q)!=scenes[i].level||TlkDataGet32(q+4)!=scenes[i].row||TlkDataGet32(q+8)!=scenes[i].rows||
           TlkDataGet32(q+12)!=scenes[i].terrain||TlkDataGet32(q+16)!=scenes[i].markers||TlkDataGet32(q+20))return 0;
        at+=SCENE_HEADER;unsigned limit=scenes[i].row/2*scenes[i].rows;
        if(!ordered(p+at,scenes[i].terrain,CELL_BYTES,limit))return 0;
        at+=scenes[i].terrain*CELL_BYTES;
        if(!ordered(p+at,scenes[i].markers,MARKER_BYTES,limit))return 0;
        at+=scenes[i].markers*MARKER_BYTES;
    }
    if(at+LEDGE_BYTES+ROOM_BYTES+DOOR_BYTES+HYENA_BYTES+EXIT_BYTES+SCAR_BYTES!=n||memcmp(p+at,"TLKALR01",8)||TlkDataGet16(p+at+8)!=128||
       TlkDataGet16(p+at+10)!=64||TlkDataGet16(p+at+12)!=12||TlkDataGet16(p+at+14)!=65524)return 0;
    const uint8_t*rh=p+at+LEDGE_BYTES;
    if(memcmp(rh,"TLKRHY01",8)||TlkDataGet32(rh+8)!=2||TlkDataGet32(rh+12)!=ROOM_BYTES)return 0;
    for(unsigned i=0;i<2;i++){
        const uint8_t*q=rh+16+i*24;
        if(TlkDataGet16(q)!=(i?29:27)||TlkDataGet16(q+2)!=64||TlkDataGet16(q+4)!=1||TlkDataGet16(q+6)!=2)return 0;
        for(unsigned j=0;j<8;j++)if(TlkDataGet16(q+8+j*2)>4095)return 0;
    }
    const uint8_t*rd=rh+ROOM_BYTES;
    if(memcmp(rd,"TLKRDT01",8)||TlkDataGet16(rd+8)!=27||TlkDataGet16(rd+10)!=28)return 0;
    const uint8_t*hy=rd+DOOR_BYTES;
    if(memcmp(hy,"TLKHYO01",8)||TlkDataGet32(hy+8)!=7||TlkDataGet32(hy+12)!=HYENA_BYTES)return 0;
    unsigned previous=0;
    for(unsigned i=0;i<7;i++){
        const uint8_t*q=hy+16+i*24;unsigned pose=TlkDataGet32(q),cursor=TlkDataGet32(q+4);
        if(pose<0xc60000||pose>=0xc70000||cursor<0xc20000||cursor>=0xc30000||(i&&cursor<=previous))return 0;
        previous=cursor;
        for(unsigned j=0;j<8;j++){int v=(int16_t)TlkDataGet16(q+8+j*2);if(v<-512||v>512)return 0;}
    }
    const uint8_t*ex=hy+HYENA_BYTES;
    if(memcmp(ex,"TLKREX01",8)||TlkDataGet16(ex+8)!=40||TlkDataGet16(ex+10)!=1||TlkDataGet16(ex+12)!=60||TlkDataGet16(ex+14))return 0;
    const uint8_t*sc=ex+EXIT_BYTES;
    if(memcmp(sc,"TLKSCA01",8)||TlkDataGet32(sc+8)!=2||TlkDataGet32(sc+12)!=SCAR_BYTES||
       TlkDataGet16(sc+40)!=24||TlkDataGet16(sc+42)!=16||TlkDataGet32(sc+44))return 0;
    for(unsigned i=0;i<2;i++){
        const uint8_t*q=sc+16+i*12;
        if(TlkDataGet32(q)!=(i?0xc58600u:0xc585f4u)||TlkDataGet32(q+4)!=0xc58589||TlkDataGet32(q+8)!=(i?0xc65da0u:0xc65c8au))return 0;
    }
    if(apply){
        at=HEADER;
        for(unsigned i=0;i<SCENES;i++){
            at+=SCENE_HEADER;size_t bytes=scenes[i].terrain*CELL_BYTES;memcpy(terrain[i],p+at,bytes);at+=bytes;
            bytes=scenes[i].markers*MARKER_BYTES;memcpy(markers[i],p+at,bytes);at+=bytes;
        }
        for(unsigned i=0;i<4;i++)adult_ledge[i]=TlkDataGet16(p+at+8+i*2);
        memcpy(room_hyenas,rh+16,sizeof room_hyenas);
        return_door[0]=TlkDataGet16(rd+8);return_door[1]=TlkDataGet16(rd+10);
        memcpy(hyena_bounds,hy+16,sizeof hyena_bounds);
        for(unsigned i=0;i<4;i++)return_exit[i]=TlkDataGet16(ex+8+i*2);
        memcpy(scar_activation,sc+16,sizeof scar_activation);scar_reveal[0]=TlkDataGet16(sc+40);scar_reveal[1]=TlkDataGet16(sc+42);
        ready=1;
    }
    return 1;
}
int TlkLateSceneScarActivation(unsigned descriptor,unsigned*n,unsigned*m){
    if(!ready||!n||!m)return 0;
    for(unsigned i=0;i<2;i++)if(TlkDataGet32(scar_activation[i])==descriptor){
        *n=TlkDataGet32(scar_activation[i]+4);*m=TlkDataGet32(scar_activation[i]+8);return 1;
    }
    return 0;
}
int TlkLateSceneHyenaBounds(unsigned pose,unsigned cursor,unsigned side,unsigned*n,unsigned*m){
    if(!ready||!n||!m||side>3)return 0;
    for(unsigned i=0;i<7;i++)if(TlkDataGet32(hyena_bounds[i])==pose&&TlkDataGet32(hyena_bounds[i]+4)==cursor){
        *n=TlkDataGet16(hyena_bounds[i]+8+side*2);*m=TlkDataGet16(hyena_bounds[i]+16+side*2);return 1;
    }
    return 0;
}
int TlkLateSceneReturnHyenas(unsigned door,unsigned*ptr,unsigned*nc,unsigned*mc){
    if(!ready||!ptr||!nc||!mc)return 0;
    for(unsigned i=0;i<2;i++)if(TlkDataGet16(room_hyenas[i])==door){
        *ptr=TlkDataGet16(room_hyenas[i]+2);*nc=TlkDataGet16(room_hyenas[i]+4);*mc=TlkDataGet16(room_hyenas[i]+6);return 1;
    }
    return 0;
}
int TlkLateSceneReturnHyenaPosition(unsigned door,unsigned slot,unsigned side,unsigned native,unsigned*md){
    if(!ready||!md||slot>=2||side>=2)return 0;
    for(unsigned i=0;i<2;i++)if(TlkDataGet16(room_hyenas[i])==door){
        unsigned at=slot*4+side*2;if(native!=TlkDataGet16(room_hyenas[i]+8+at))return 0;
        *md=TlkDataGet16(room_hyenas[i]+16+at);return 1;
    }
    return 0;
}
static const uint8_t* find(const uint8_t*p,unsigned count,unsigned stride,unsigned cell){
    unsigned lo=0,hi=count;
    while(lo<hi){unsigned mid=(lo+hi)/2;if(TlkDataGet32(p+mid*stride)<cell)lo=mid+1;else hi=mid;}
    return lo<count&&TlkDataGet32(p+lo*stride)==cell?p+lo*stride:NULL;
}
int TlkLateSceneTerrain(unsigned level,unsigned cell,unsigned live,unsigned height,unsigned nc,unsigned mc,unsigned native,unsigned*md){
    int i=index_for(level);if(!ready||!md||i<0||height>1||nc>15||mc>15)return 0;
    const uint8_t*p=find(&terrain[i][0][0],scenes[i].terrain,CELL_BYTES,cell);
    if(!p||TlkDataGet16(p+4)!=live||native!=(height?p[8+nc]:p[6]))return 0;
    *md=height?p[24+mc]:p[7];return 1;
}
int TlkLateSceneMarker(unsigned level,unsigned cell,unsigned live,unsigned native,unsigned*md){
    int i=index_for(level);if(!ready||!md||i<0)return 0;
    const uint8_t*p=find(&markers[i][0][0],scenes[i].markers,MARKER_BYTES,cell);
    if(!p||TlkDataGet16(p+4)!=live||native!=p[6])return 0;
    *md=p[7];return 1;
}

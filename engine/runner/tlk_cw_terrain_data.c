/* Immutable original per-cell collision geometry, prepared only at install. */
#include "tlk_cw_terrain_data.h"
#include "tlk_md_assets.h"
#include "tlk_data_record.h"
#include <stdlib.h>
#include <string.h>
enum { ROW_BYTES=800,ROWS=31,CELLS=ROW_BYTES/2*ROWS,STRIDE=36,BYTES=16+CELLS*STRIDE };
static uint8_t cells[CELLS*STRIDE];
static int ready;
static unsigned be16(const uint8_t *p){return (unsigned)p[0]<<8|p[1];}
static unsigned be32(const uint8_t *p){return be16(p)<<16|be16(p+2);}
static unsigned le24(const uint8_t *p){return (TlkDataGet16(p)|(unsigned)p[2]<<16)&0x3fffff;}
void TlkCwTerrainDataClear(void){ready=0;}
size_t TlkCwTerrainDataSize(void){return ready?BYTES:0;}
int TlkCwTerrainDataWrite(uint8_t *p,size_t n){
    if(!ready || !p || n!=BYTES)return 0;
    memcpy(p,"TLKCWT01",8);TlkDataPut32(p+8,ROW_BYTES);TlkDataPut32(p+12,ROWS);
    memcpy(p+16,cells,sizeof cells);return 1;
}
int TlkCwTerrainDataRead(const uint8_t *p,size_t n,int apply){
    if(!p || n!=BYTES || memcmp(p,"TLKCWT01",8) || TlkDataGet32(p+8)!=ROW_BYTES || TlkDataGet32(p+12)!=ROWS)return 0;
    if(apply){memcpy(cells,p+16,sizeof cells);ready=1;}return 1;
}
int TlkCwTerrainDataPrepare(const uint8_t *s,size_t sn,const uint8_t *m,size_t mn){
    ready=0;if(!s || !m || sn!=0x300000 || mn!=0x300000)return 0;
    const uint8_t *sr=s+0x3b9,*mr=m+0x1cfdb4+48;
    if(TlkDataGet16(sr+18)!=ROW_BYTES || TlkDataGet16(sr+20)!=ROWS || be16(mr+12)!=ROW_BYTES || be16(mr+14)!=ROWS)return 0;
    uint8_t *sm=malloc(CELLS*2),*mm=malloc(CELLS*2),*sc=malloc(65536);size_t a=0,b=0,c=0;
    int ok=sm && mm && sc && TlkMdDecompress(s,sn,le24(sr+9),sm,CELLS*2,&a) && a==CELLS*2 &&
        TlkMdDecompress(m,mn,be32(mr+16),mm,CELLS*2,&b) && b==CELLS*2 &&
        TlkMdDecompress(s,sn,le24(sr),sc,65536,&c);
    unsigned sh=le24(sr+3),mc=be32(mr+4),mh=be32(mr+8);
    for(unsigned i=0;i<CELLS && ok;i++){
        unsigned sw=TlkDataGet16(sm+i*2),mw=be16(mm+i*2),so=(sw&0xfff8)/2,mo=(mw&0xfff8)/2;
        if(so+4>c || mc>=mn || mo+4>mn-mc){ok=0;break;}
        unsigned sp=TlkDataGet16(sc+so),mp=m[mc+mo]*16u;
        if(sh>=sn || sp+16>sn-sh || mh>=mn || mp+16>mn-mh){ok=0;break;}
        uint8_t *p=cells+i*STRIDE;TlkDataPut16(p,sw);p[2]=sc[so+2];p[3]=m[mc+mo+2];
        memcpy(p+4,s+sh+sp,16);memcpy(p+20,m+mh+mp,16);
    }
    free(sm);free(mm);free(sc);ready=ok;return ready;
}
static int TerrainColumns(unsigned cell,unsigned live,unsigned kind,unsigned native_column,unsigned column,unsigned native,unsigned *external){
    if(!ready || !external || cell>=CELLS || kind>1 || native_column>=16 || column>=16)return 0;
    const uint8_t *p=cells+cell*STRIDE;
    if(live!=TlkDataGet16(p) || native!=(kind?p[4+native_column]:p[2]))return 0;
    *external=kind?p[20+column]:p[3];return 1;
}

int TlkCwTerrainDataGet(unsigned cell,unsigned live,unsigned kind,unsigned column,unsigned native,unsigned *external){
    return TerrainColumns(cell,live,kind,column,column,native,external);
}
int TlkCwTerrainDataPoint(unsigned cell,unsigned live,unsigned native_column,unsigned md_column,unsigned native,unsigned *external){
    return TerrainColumns(cell,live,1,native_column,md_column,native,external);
}

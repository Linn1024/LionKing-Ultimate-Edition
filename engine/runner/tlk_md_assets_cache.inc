/* Installation cache for the decoded scene assets and verified SNES mappings.
 * Included by tlk_md_assets.c to keep its owned buffers private. */
#include "sha256.h"
#include "tlk_contact_map.h"
#ifdef _WIN32
#include <windows.h>
#endif

enum { MD_CACHE_VERSION=3, MD_CACHE_LIMIT=16<<20, MD_CACHE_HEADER=112 };
typedef struct AssetCursor { uint8_t *at,*end;int ok; } AssetCursor;
static unsigned cache_u32(const uint8_t *p) { return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24; }
static void cache_put(uint8_t *p,unsigned n) { for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8)); }
static void cache_write(AssetCursor *c,const void *p,size_t n) {
    if(!c->ok || n>(size_t)(c->end-c->at)) { c->ok=0;return; }
    if(n)memcpy(c->at,p,n);c->at+=n;
}
static void cache_number(AssetCursor *c,unsigned n) { uint8_t b[4];cache_put(b,n);cache_write(c,b,4); }
static void cache_array(AssetCursor *c,const void *p,size_t n) { cache_number(c,p?(unsigned)n:0);if(p)cache_write(c,p,n); }
static unsigned cache_read_number(AssetCursor *c) {
    if(!c->ok || c->end-c->at<4) { c->ok=0;return 0; }
    unsigned n=cache_u32(c->at);c->at+=4;return n;
}
static void *cache_read_array(AssetCursor *c,size_t expected) {
    unsigned n=cache_read_number(c);
    if(!c->ok || !n)return NULL;
    if(n!=expected || n>(size_t)(c->end-c->at)) { c->ok=0;return NULL; }
    void *p=malloc(n);if(!p) { c->ok=0;return NULL; }
    memcpy(p,c->at,n);c->at+=n;return p;
}
static void cache_free_scenes(MdScene *all) {
    for(unsigned i=0;i<14;i++) {
        MdScene *s=all+i;
        free(s->map);free(s->tiles);free(s->background);free(s->blocks);
        free(s->native_blocks);free(s->native_map);free(s->floor_profiles);
        free(s->md_markers);free(s->native_markers);free(s->paired_blocks);
    }
}
int TlkMdAssetsSaveCache(const char *path,const uint8_t snes_hash[32],const uint8_t md_hash[32]) {
    if(!path || !*path || !snes_hash || !md_hash || !scenes[0].valid)return 0;
    uint8_t *data=(uint8_t*)malloc(MD_CACHE_LIMIT);if(!data)return 0;
    AssetCursor c={data,data+MD_CACHE_LIMIT,1};cache_number(&c,0x01020304);cache_number(&c,14);
    for(unsigned i=0;i<14;i++) {
        MdScene *s=scenes+i;
        unsigned fields[]={s->valid,s->row_bytes,s->rows,(unsigned)s->map_size,(unsigned)s->tile_size,
            (unsigned)s->bg_size,(unsigned)s->block_size,s->native_count,s->matched,
            (unsigned)s->native_map_size,s->native_row_bytes,s->paired_matched};
        for(unsigned n=0;n<12;n++)cache_number(&c,fields[n]);
        cache_write(&c,s->palette,sizeof s->palette);
        cache_array(&c,s->map,s->map_size);cache_array(&c,s->tiles,s->tile_size);
        cache_array(&c,s->background,s->bg_size);cache_array(&c,s->blocks,s->block_size);
        cache_array(&c,s->native_blocks,(size_t)s->native_count*2);
        cache_array(&c,s->native_map,s->native_map_size);
        cache_array(&c,s->floor_profiles,s->map_size/2*16);
        cache_array(&c,s->md_markers,s->map_size/2);
        cache_array(&c,s->native_markers,s->native_map_size/2);
        cache_array(&c,s->paired_blocks,s->native_map_size);
    }
    uint8_t contact[TLK_CONTACT_MAP_BYTES];
    if(!cant_wait.ready || !TlkContactMapExport(contact,sizeof contact))c.ok=0;
    cache_number(&c,0x32524450); /* PDR2: prepared immutable gameplay/colour data */
    cache_array(&c,contact,sizeof contact);
    for(unsigned variant=0;variant<2;variant++)
        for(unsigned i=0;i<64;i++)cache_number(&c,cant_wait.initial[variant][i]);
    for(unsigned i=0;i<100;i++)cache_number(&c,cant_wait.target[i]);
    if(!c.ok) { free(data);return 0; }
    size_t length=(size_t)(c.at-data);uint8_t header[MD_CACHE_HEADER]={0};
    memcpy(header,"TLKSCN01",8);cache_put(header+8,MD_CACHE_VERSION);cache_put(header+12,(unsigned)length);
    memcpy(header+16,snes_hash,32);memcpy(header+48,md_hash,32);sha256_compute(data,length,header+80);
    char temp[4096];if(snprintf(temp,sizeof temp,"%s.tmp",path)>=(int)sizeof temp) { free(data);return 0; }
    FILE *f=fopen(temp,"wb");int ok=f && fwrite(header,1,sizeof header,f)==sizeof header && fwrite(data,1,length,f)==length;
    if(f && fclose(f))ok=0;free(data);
    if(ok) {
#ifdef _WIN32
        ok=MoveFileExA(temp,path,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
#else
        ok=rename(temp,path)==0;
#endif
    }
    if(!ok)remove(temp);return ok;
}
int TlkMdAssetsLoadCache(const char *path,const uint8_t snes_hash[32],const uint8_t md_hash[32]) {
    if(!path || !*path || !snes_hash || !md_hash)return 0;
    FILE *f=fopen(path,"rb");if(!f)return 0;
    uint8_t header[MD_CACHE_HEADER],digest[32];uint8_t *data=NULL;
    int ok=fread(header,1,sizeof header,f)==sizeof header;
    unsigned length=ok?cache_u32(header+12):0;
    ok=ok && !memcmp(header,"TLKSCN01",8) && cache_u32(header+8)==MD_CACHE_VERSION &&
       length>=8 && length<=MD_CACHE_LIMIT && !memcmp(header+16,snes_hash,32) && !memcmp(header+48,md_hash,32);
    if(ok) { data=(uint8_t*)malloc(length);ok=data && fread(data,1,length,f)==length && fgetc(f)==EOF; }
    fclose(f);
    if(ok) { sha256_compute(data,length,digest);ok=!memcmp(digest,header+80,32); }
    if(!ok) { free(data);return 0; }
    AssetCursor c={data,data+length,1};MdScene pending[14]={0};
    if(cache_read_number(&c)!=0x01020304 || cache_read_number(&c)!=14)c.ok=0;
    for(unsigned i=0;i<14 && c.ok;i++) {
        MdScene *s=pending+i;unsigned fields[12];
        for(unsigned n=0;n<12;n++)fields[n]=cache_read_number(&c);
        s->valid=(int)fields[0];s->row_bytes=fields[1];s->rows=fields[2];s->map_size=fields[3];
        s->tile_size=fields[4];s->bg_size=fields[5];s->block_size=fields[6];
        s->native_count=fields[7];s->matched=fields[8];s->native_map_size=fields[9];
        s->native_row_bytes=fields[10];s->paired_matched=fields[11];
        if(fields[0]>1 || s->row_bytes>4096 || s->rows>4096 || s->map_size>65536 || s->tile_size>65536 ||
           s->bg_size>65536 || s->block_size>65536 || s->native_count>8192 || s->matched>s->native_count ||
           s->native_map_size>65536 || s->native_row_bytes>4096 || s->paired_matched>s->native_map_size/2 ||
           c.end-c.at<(ptrdiff_t)sizeof s->palette) { c.ok=0;break; }
        memcpy(s->palette,c.at,sizeof s->palette);c.at+=sizeof s->palette;
        s->map=cache_read_array(&c,s->map_size);s->tiles=cache_read_array(&c,s->tile_size);
        s->background=cache_read_array(&c,s->bg_size);s->blocks=cache_read_array(&c,s->block_size);
        s->native_blocks=cache_read_array(&c,(size_t)s->native_count*2);
        s->native_map=cache_read_array(&c,s->native_map_size);
        s->floor_profiles=cache_read_array(&c,s->map_size/2*16);
        s->md_markers=cache_read_array(&c,s->map_size/2);
        s->native_markers=cache_read_array(&c,s->native_map_size/2);
        s->paired_blocks=cache_read_array(&c,s->native_map_size);
        if(s->valid && (!s->map || !s->tiles || !s->background || !s->blocks || !s->map_size ||
           !s->tile_size || !s->bg_size || !s->row_bytes || (s->row_bytes&1) || s->map_size!=(size_t)s->row_bytes*s->rows ||
           s->bg_size%128))c.ok=0;
    }
    if(cache_read_number(&c)!=0x32524450)c.ok=0;
    uint8_t *contact=cache_read_array(&c,TLK_CONTACT_MAP_BYTES);
    uint16_t initial[2][64],target[100];
    for(unsigned variant=0;variant<2;variant++)for(unsigned i=0;i<64;i++) {
        unsigned value=cache_read_number(&c);if(value>65535)c.ok=0;initial[variant][i]=(uint16_t)value;
    }
    for(unsigned i=0;i<100;i++) {unsigned value=cache_read_number(&c);if(value>65535)c.ok=0;target[i]=(uint16_t)value;}
    ok=c.ok && c.at==c.end && pending[0].valid && pending[1].valid && contact &&
       pending[5].valid && pending[5].bg_size==8192 && pending[5].tile_size==28448+4*1440;
    if(ok)ok=TlkContactMapImport(contact,TLK_CONTACT_MAP_BYTES);
    free(contact);free(data);
    if(!ok) { cache_free_scenes(pending);return 0; }
    TlkMdAssetsClear();memcpy(scenes,pending,sizeof scenes);
    memcpy(cant_wait.initial,initial,sizeof initial);memcpy(cant_wait.target,target,sizeof target);cant_wait.ready=1;return 1;
}

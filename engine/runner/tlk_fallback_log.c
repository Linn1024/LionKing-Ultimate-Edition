#include "tlk_fallback_log.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifdef _WIN32
#include <process.h>
#define log_pid _getpid
#else
#include <unistd.h>
#define log_pid getpid
#endif

enum { SLOTS=2048, PATH_SIZE=4096 };
typedef struct {
    unsigned hash,object,pose,detail;
    uint64_t count;
    char kind[40],resource[128],reason[96];
    unsigned have_sprite;
    TlkFallbackSpriteInfo sprite;
} Entry;
static Entry entries[SLOTS];
static FILE *file;
static int enabled=-1,have_context,report_error;
static char path[PATH_SIZE];
static unsigned field,level,scene,used;
static unsigned long limit=8*1024*1024;
static uint64_t sequence,total_records,total_occurrences;
static const TlkFallbackSpriteInfo *sprite_context;
void TlkFallbackSpriteContext(const TlkFallbackSpriteInfo *info){sprite_context=info;}

static void quoted(FILE *out,const char *text) {
    fputc('"',out);
    for(const unsigned char *p=(const unsigned char *)(text?text:"");*p;p++) {
        if(*p=='"' || *p=='\\')fputc('\\',out);
        if(*p<32)fprintf(out,"\\u%04x",*p);else fputc(*p,out);
    }
    fputc('"',out);
}
static void failed(void) {
    enabled=0;
    if(!report_error){fprintf(stderr,"Fallback log write failed: %s\n",path);report_error=1;}
}
static void header(const char *type) {
    fprintf(file,"{\"type\":\"%s\",\"schema\":2,\"pid\":%u,\"sequence\":%llu,\"time\":%llu,\"build\":",
        type,(unsigned)log_pid(),(unsigned long long)sequence,(unsigned long long)time(NULL));
    quoted(file,getenv("TLK_FALLBACK_BUILD_HASH"));
    fprintf(file,",\"max_file_bytes\":%lu,\"files\":4,\"aggregation\":\"occurrences per frame and key; later frames retained\","
        "\"coverage\":\"native compositor pixels and rows, sprite sampler rejections, retained native audio requests/output; unclassified paths require ownership review\"}\n",limit);
}
static int writable(void) {
    if(!file)return 0;
    long size=ftell(file);
    if(size>=0 && (unsigned long)size>=limit) {
        fclose(file);file=NULL;
        char a[PATH_SIZE+32],b[PATH_SIZE+32];
        snprintf(a,sizeof a,"%s.3",path);remove(a);
        for(int n=2;n>=0;n--) {
            if(n)snprintf(a,sizeof a,"%s.%d",path,n);else snprintf(a,sizeof a,"%s",path);
            snprintf(b,sizeof b,"%s.%d",path,n+1);
            if(rename(a,b) && n==0){failed();return 0;}
        }
        file=fopen(path,"wb");if(!file){failed();return 0;}header("rotation");
    }
    return 1;
}
void TlkFallbackFlush(void) {
    if(!file || !have_context)return;
    for(unsigned i=0;i<SLOTS;i++) {
        Entry *e=&entries[i];if(!e->count || !strcmp(e->kind,"resolved_by_host"))continue;
        if(!writable())return;
        fprintf(file,"{\"type\":\"event\",\"sequence\":%llu,\"field\":%u,\"level\":%u,\"scene\":\"%06x\",\"kind\":",
            (unsigned long long)++sequence,field,level,scene);quoted(file,e->kind);
        fputs(",\"resource\":",file);quoted(file,e->resource);fputs(",\"reason\":",file);quoted(file,e->reason);
        fprintf(file,",\"object\":\"%04x\",\"pose\":\"%06x\",\"caller\":\"%06x\",\"detail\":%u,\"occurrences\":%llu",
            e->object,strncmp(e->resource,"audio",5)?e->pose:0,
            strncmp(e->resource,"audio",5)?0:e->pose,e->detail,(unsigned long long)e->count);
        if(e->have_sprite){const TlkFallbackSpriteInfo *s=&e->sprite;
            fprintf(file,",\"sprite_context\":{\"captured_descriptor\":\"%06x\",\"latched_descriptor\":\"%06x\",\"latched_actor\":\"%04x\",\"latched_action\":\"%06x\",\"latched_owner_valid\":%u,"
                "\"latched_actor_xy\":[%d,%d],\"player_xy\":[%d,%d],\"camera_xy\":[%d,%d],\"first_sample_screen_xy\":[%d,%d],\"local_xy\":[%d,%d],\"size\":%u,\"attributes\":\"%04x\",\"draw_width\":%u,"
                "\"requested_frames\":\"%s\",\"requested_palette\":\"%s\",\"mapped_md_pose\":\"%06x\",\"mapped_role\":%u,\"scene_role\":%u,\"image_ready\":%u,\"native_palette\":%u,\"mapped_md_palette\":%u,"
                "\"latched_ram_pose_header_fnv32\":\"%08x\",\"first_sample_tile_fnv32\":\"%08x\",\"first_sample_palette_fnv32\":\"%08x\"}",
                s->descriptor,s->latched_descriptor,s->actor,s->action,s->owner_valid,s->actor_x,s->actor_y,s->player_x,s->player_y,s->camera_x,s->camera_y,s->screen_x,s->screen_y,s->local_x,s->local_y,s->size,s->attributes,s->draw_width,
                s->frames_md?"md":"native_or_specialized",s->palette_md?"md":"native_or_specialized",s->mapped_pose,s->mapped_role,s->scene_role,s->image_ready,s->native_palette,s->md_palette,s->pose_header_fnv32,s->tile_fnv32,s->palette_fnv32);
        }
        fputs("}\n",file);
        total_records++;total_occurrences+=e->count;
    }
    if(writable())fprintf(file,"{\"type\":\"frame\",\"sequence\":%llu,\"field\":%u,\"level\":%u,\"scene\":\"%06x\",\"events\":%u}\n",
        (unsigned long long)++sequence,field,level,scene,used);
    if(file && (fflush(file) || ferror(file)))failed();
    memset(entries,0,sizeof entries);used=0;
}
static void finish(void) {
    if(!file)return;
    TlkFallbackFlush();
    if(writable())fprintf(file,"{\"type\":\"session_end\",\"event_records\":%llu,\"occurrences\":%llu}\n",
        (unsigned long long)total_records,(unsigned long long)total_occurrences);
    if(file)fclose(file);
    file=NULL;
}
int TlkFallbackEnabled(void) {
    if(enabled>=0)return enabled;
    enabled=0;const char *name=getenv("TLK_FALLBACK_LOG");
    if(!name || !*name)return 0;
    if(strlen(name)>=sizeof path){fputs("Fallback log path is too long\n",stderr);return 0;}
    memcpy(path,name,strlen(name)+1);
    const char *bytes=getenv("TLK_FALLBACK_LOG_BYTES");
    if(bytes){unsigned long n=strtoul(bytes,NULL,10);if(n>=4096 && n<=64*1024*1024)limit=n;}
    file=fopen(path,"ab");if(!file){failed();return 0;}
    fseek(file,0,SEEK_END);enabled=1;atexit(finish);
    if(writable())header("session_start");
    fflush(file);return 1;
}
void TlkFallbackContext(unsigned next,unsigned next_level,unsigned next_scene) {
    if(!TlkFallbackEnabled())return;
    if(have_context && (next!=field || next_level!=level || next_scene!=scene))TlkFallbackFlush();
    field=next;level=next_level;scene=next_scene;have_context=1;
}
static unsigned hash_text(unsigned h,const char *s) {
    for(;*s;s++)h=(h^(unsigned char)*s)*16777619u;
    return h;
}
static void record(const char *kind,const char *resource,const char *reason,
                   unsigned object,unsigned pose,unsigned detail,const TlkFallbackSpriteInfo *sprite,uint64_t count) {
    if(!count || !TlkFallbackEnabled())return;
    have_context=1;
    if(!kind)kind="unclassified";
    if(!resource)resource="unknown";
    if(!reason)reason="unknown";
    unsigned h=hash_text(hash_text(hash_text(2166136261u,kind),resource),reason)^object^(pose*31u)^(detail*131u);
    if(sprite)for(unsigned i=0;i<sizeof *sprite;i++)h=(h^((const unsigned char*)sprite)[i])*16777619u;
    for(unsigned n=0;n<SLOTS;n++) {
        Entry *e=&entries[(h+n)&(SLOTS-1)];
        if(e->count && (e->hash!=h || e->object!=object || e->pose!=pose || e->detail!=detail ||
           strcmp(e->kind,kind) || strcmp(e->resource,resource) || strcmp(e->reason,reason) ||
           e->have_sprite!=(sprite!=NULL) || (sprite && memcmp(&e->sprite,sprite,sizeof *sprite))))continue;
        if(!e->count){e->hash=h;e->object=object;e->pose=pose;e->detail=detail;
            snprintf(e->kind,sizeof e->kind,"%s",kind);snprintf(e->resource,sizeof e->resource,"%s",resource);
            snprintf(e->reason,sizeof e->reason,"%s",reason);e->have_sprite=sprite!=NULL;if(sprite)e->sprite=*sprite;used++;}
        e->count+=count;return;
    }
    /* Preserve every occurrence even if a pathological frame fills the table. */
    TlkFallbackFlush();record(kind,resource,reason,object,pose,detail,sprite,count);
}
void TlkFallbackRecord(const char *kind,const char *resource,const char *reason,
                       unsigned object,unsigned pose,unsigned detail,uint64_t count) {
    record(kind,resource,reason,object,pose,detail,resource && !strncmp(resource,"graphics",8)?sprite_context:NULL,count);
}
void TlkFallbackSpriteRecord(const char *kind,const char *reason,unsigned object,unsigned pose,
                             const TlkFallbackSpriteInfo *info,uint64_t count) {
    record(kind,"graphics.sprites",reason,object,pose,info?info->descriptor:0,info,count);
}

void TlkFallbackCanvasOwned(unsigned current_field) {
    if(!TlkFallbackEnabled() || !have_context || field!=current_field)return;
    for(unsigned i=0;i<SLOTS;i++) {
        Entry *e=&entries[i];if(!e->count || strncmp(e->resource,"graphics",8))continue;
        if(!strcmp(e->kind,"fallback") || !strcmp(e->kind,"unclassified") || !strcmp(e->kind,"unclassified_canvas")) {
            snprintf(e->kind,sizeof e->kind,"resolved_by_host");if(used)used--;
        }
    }
}

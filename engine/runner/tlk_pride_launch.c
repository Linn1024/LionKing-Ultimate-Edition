/* Configuration bridge for the reviewed nonfinal Pride health-death runtime.
 * Behavior comes from resources; diagnostics are optional and never enable it. */
#include "tlk_pride_launch.h"
#include "tlk_resources.h"
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <direct.h>
#else
#include <sys/stat.h>
#endif
static char *pride_md_path;
static int pride_last_choice;
static const char pride_trace_sink[]="@TLK-Pride-Trace";
int TlkPrideHealthDeathSelected(void) {
    int node=TlkResourcesFind("gameplay.levels.pride_lands.health_death");
    return node>=0 && TlkResourcesNode(node)->md_supported && TlkResourcesHasMd() && TlkResourcesUseMd("gameplay.levels.pride_lands.health_death");
}
int TlkPrideFinalLifeSelected(void) {
    int node=TlkResourcesFind("gameplay.levels.pride_lands.final_life");
    return node>=0 && TlkResourcesNode(node)->md_supported && TlkResourcesHasMd() &&
        TlkResourcesUseMd("gameplay.levels.pride_lands.final_life");
}
static int pride_choices(void) {
    return TlkPrideHealthDeathSelected() | (TlkPrideFinalLifeSelected()<<1);
}
void TlkPrideConfigure(const char *verified_md_path) {
    free(pride_md_path);pride_md_path=NULL;
    if(TlkResourcesHasMd() && verified_md_path) {
        size_t n=strlen(verified_md_path)+1;pride_md_path=malloc(n);
        if(pride_md_path)memcpy(pride_md_path,verified_md_path,n);
    }
    pride_last_choice=pride_choices();
}
int TlkPrideProfileChanged(void) {
    int current=pride_choices(),changed=current!=pride_last_choice;
    pride_last_choice=current;return changed;
}
char *TlkPrideSetting(const char *name) {
    static const char *const dirs[]={"TLK_NATIVE_BANK_PROBE","TLK_SCENE_PREPARE_PROBE","TLK_SCENE_OWNER_PROBE","TLK_SCENE_RESTORE_PROBE","TLK_SCENE_RENDER_PROBE"};
    static const char *const policies[]={"TLK_NATIVE_BANK_APPLY","TLK_SCENE_PREPARE_APPLY","TLK_SCENE_OWNER_ENABLE","TLK_SCENE_RESTORE_ENABLE","TLK_SCENE_RESTORE_CANONICAL","TLK_SCENE_RESTORE_ROAR_ZERO","TLK_SCENE_RENDER_ENABLE"};
    for(unsigned i=0;i<sizeof dirs/sizeof *dirs;i++)if(!strcmp(name,dirs[i])) {
        char *folder=getenv("TLK_PRIDE_DIAGNOSTICS");return folder && *folder?folder:(char*)pride_trace_sink;
    }
    for(unsigned i=0;i<sizeof policies/sizeof *policies;i++)if(!strcmp(name,policies[i]))return TlkPrideHealthDeathSelected()?"1":"0";
    if(!strcmp(name,"TLK_SCENE_OWNER_MD_ROM"))return pride_md_path;
    if(!strcmp(name,"TLK_NATIVE_BANK_RECORD"))return NULL;
    return getenv(name);
}
static int trace_sink_path(const char *path) {
    size_t n=sizeof pride_trace_sink-1;
    return path && !strncmp(path,pride_trace_sink,n) && (!path[n] || path[n]=='/' || path[n]=='\\');
}
FILE *TlkPrideFileOpen(const char *path,const char *mode) {
    if(trace_sink_path(path)) {
#ifdef _WIN32
        return fopen("NUL",mode);
#else
        return fopen("/dev/null",mode);
#endif
    }
    return fopen(path,mode);
}
int TlkPrideMakeDirectory(const char *path) {
    if(trace_sink_path(path))return 0;
#ifdef _WIN32
    return _mkdir(path);
#else
    return mkdir(path,0755);
#endif
}

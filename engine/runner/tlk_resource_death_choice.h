#ifndef TLK_RESOURCE_DEATH_CHOICE_H
#define TLK_RESOURCE_DEATH_CHOICE_H
#include <string.h>
/* Historical IDs need not dictate the player's grouping or inheritance. */
static const char *TlkResourceSemanticParent(const char *id) {
    if(!strcmp(id,"gameplay.levels.pride_lands.continue_token_animation"))return "gameplay";
    if(!strcmp(id,"gameplay.levels.pride_lands.health_death"))return "gameplay.simba";
    if(!strncmp(id,"audio.music.",12)) {
        size_t n=strlen(id);
        if((n>6&&!strcmp(id+n-6,".track"))||!strcmp(id,"audio.music.pride_rock.finale"))return "audio.music";
    }
    if(!strncmp(id,"graphics.titles.pride_lands.",27)&&strcmp(id,"graphics.titles.pride_lands.duration"))return "graphics.titles";
    if(!strncmp(id,"graphics.titles.remaining.",25))return "graphics.titles";
    return NULL;
}
/* One user-facing choice, including original per-stage call sites. IDs remain
 * readable in development profiles, but cannot create conflicting death music. */
static int TlkResourceSharedDeath(const char *id) {
    if(!strcmp(id,"audio.music.pride_health_death"))return 1;
    static const char *levels[]={"elephant_graveyard","simbas_exile","hakuna_matata","simbas_destiny","be_prepared","simbas_return","pride_rock"};
    for(unsigned i=0;i<sizeof levels/sizeof *levels;i++) {
        const char *p=id+(!strncmp(id,"audio.music.",12)?12:strlen(id));
        size_t n=strlen(levels[i]);if(!strncmp(p,levels[i],n)&&!strcmp(p+n,".death"))return 1;
    }
    return 0;
}
#endif

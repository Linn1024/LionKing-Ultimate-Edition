#include <stdlib.h>
#include <string.h>
/* Native interactive sprite assembly; original timing remains selectable. */
int g_tlk_smooth_updates;
__attribute__((constructor)) static void ConfigureSmoothUpdates(void) {
    const char *v=getenv("TLK_SMOOTH_UPDATES");
    g_tlk_smooth_updates=!v || strcmp(v,"0");
}

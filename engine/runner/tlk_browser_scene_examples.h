#ifndef TLK_BROWSER_SCENE_EXAMPLES_H
#define TLK_BROWSER_SCENE_EXAMPLES_H
#include <string.h>
static int TlkBrowserScenePicker(const char *id) {
 return !strcmp(id,"graphics.scenery")||!strcmp(id,"graphics.scenery.foreground")||
        !strcmp(id,"graphics.scenery.background")||!strcmp(id,"graphics.scenery.palettes");
}
static int TlkBrowserSceneExample(const char *id,unsigned requested) {
 if(TlkBrowserScenePicker(id))return requested<10?(int)requested:9;
 if(!strcmp(id,"graphics.scenery.stampede_palette"))return 3;
 if(!strcmp(id,"graphics.titles.pride_lands.position"))return 0;
 return -1;
}
static const char *TlkBrowserPlacementDescription(const char *id) {
 if(!strcmp(id,"graphics.scenery.timon_start_position"))return "Choose where Timon appears in the opening scene after you press Start. This setting applies only to that scene.";
 if(!strcmp(id,"graphics.scenery.destiny_face_position"))return "Choose where Mufasa's face appears in the sky at the end of Simba's Destiny. Genesis places it relative to Simba; SNES uses a fixed place.";
 return NULL;
}
static const char *TlkBrowserPlacementScene(const char *id) {
 return !strcmp(id,"graphics.scenery.timon_start_position")?"Scene: Opening after Start":"Scene: End of Simba's Destiny";
}
#endif

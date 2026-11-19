#pragma once
#include <string.h>
/* A route promises an actual resource image, never an unrelated level shot. */
static int TlkBrowserSpecialGallery(const char *id) {
    if(!strncmp(id,"graphics.sprites.checkpoints",27))return 1;
    if(!strncmp(id,"graphics.titles.pride_lands",27)&&!strstr(id,"duration")&&!strstr(id,"position"))return 2;
    if(!strncmp(id,"graphics.hud",12))return 3;
    if(!strcmp(id,"graphics.menus.title"))return 4;
    if(!strcmp(id,"graphics.menus.options"))return 5;
    if(!strcmp(id,"graphics.menus.publisher_cards"))return 6;
    if(!strcmp(id,"graphics.menus.sound_test"))return 7;
    if(!strcmp(id,"graphics.menus.level_select"))return 8;
    if(!strncmp(id,"graphics.sprites.cinematics.timon",32))return 9;
    if(!strcmp(id,"graphics.bonus_results"))return 10;
    if(!strcmp(id,"graphics.interlevel.pride_lands"))return 11;
    if(!strcmp(id,"graphics.interlevel.stampede"))return 12;
    if(!strcmp(id,"graphics.ending_sunrise"))return 13;
    if(!strcmp(id,"graphics.ending_title"))return 14;
    if(!strcmp(id,"graphics.ending_credits"))return 15;
    if(!strcmp(id,"graphics.pride_final_menu"))return 16;
    if(!strcmp(id,"graphics.scenery.timon_start_position"))return 17;
    if(!strcmp(id,"graphics.sprites.mufasa.palette"))return 18;
    return 0;
}
static bool TlkBrowserGallerySourceAvailable(const char *id,int source) {
    int kind=TlkBrowserSpecialGallery(id);
    return source!=0||!((kind>=11&&kind<=16)||kind==18);
}
static const char *TlkBrowserGalleryNote(const char *id) {
    int kind=TlkBrowserSpecialGallery(id);
    return kind==1?"The checkpoint head, including its blinking poses.":
           kind==2?"Example lettering: Pride Lands. Caption height is explained above.":
           kind==3?"The original meters and life counter, using sample values.":
           kind==4?"The original ready title menu.":
           kind==5?"Options menu example with normal difficulty and sound enabled.":
           kind==6?"The publisher card. Genesis also adds the animated SEGA opening.":
           kind==7?"Sound Test layout example. Its song catalogue is chosen separately.":
           kind==8?"The original level-select menu, reached through its normal cheat code.":
           kind==9?"Timon's opening-scene drawings and colours.":
           kind==10?"Bonus-result lettering and numbers. The counting sequence is chosen under Gameplay.":
           kind==11?"Original Genesis post-Pride Lands illustration. Drag the slider through scene samples. Both original games have a scene; the SNES picture preview is not available yet.":
           kind==12?"Original Genesis cliff scene after the Stampede. The SNES picture preview is not available yet; scene timing is chosen under Gameplay.":
           kind==13?"Original Genesis sunrise with adult Simba. The SNES picture preview is not available yet.":
           kind==14?"The Genesis title overlay on its sunrise backdrop. The SNES ending has no matching title interval; timing is chosen separately.":
           kind==15?"Original Genesis credit lettering and scrolling layout. The SNES picture preview is not available yet.":
           kind==16?"Original Genesis Continue screen with sample Continue counts. The SNES picture preview is not available yet.":
           kind==17?"Opening Timon's position on a 320-column canvas. Both panels use the same SNES drawing and colours so only placement changes. Drag the slider to inspect poses.":
           kind==18?"Scar's shared farewell drawings in Genesis colours. The SNES farewell colour preview is not available yet.":nullptr;
}

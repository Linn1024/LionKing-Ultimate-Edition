"""Integrate prepared bonus artwork/palettes, fixed backgrounds and independent music."""
from pathlib import Path

def edit(name,old,new):
 p=Path(name);s=p.read_text();assert old in s,(name,old[:80]);p.write_text(s.replace(old,new))
edit('tools/later_sprite_catalog.py',"('later_actor_pairs.json','pride_actor_pairs.json')","('later_actor_pairs.json','pride_actor_pairs.json','bonus_actor_pairs.json')")
edit('tools/later_sprite_catalog.py','        assert p not in npcs and q in md,(hex(p),hex(q))','        if p in npcs and pair["role"]==4 and npcs[p].get("role")==4:continue\n        assert p not in npcs and q in md,(hex(p),hex(q))')
edit('engine/runner/tlk_md_sprites.h','TLK_MD_SPRITE_ADULT_HYENA, TLK_MD_SPRITE_SCAR,','TLK_MD_SPRITE_ADULT_HYENA, TLK_MD_SPRITE_SCAR,\n       TLK_MD_SPRITE_BONUS_PUMBAA, TLK_MD_SPRITE_BONUS_TIMON, TLK_MD_SPRITE_BONUS_BUG,')
edit('engine/runner/tlk_md_sprites.c','level<=9?level:0','level<=13?level:0')
edit('engine/runner/tlk_md_sprites.c','m->role==TLK_MD_SPRITE_SCAR));','m->role==TLK_MD_SPRITE_SCAR)) ||\n             (next_scene>=10 && next_scene<=13 && (m->role==TLK_MD_SPRITE_BONUS_TIMON ||\n              m->role==TLK_MD_SPRITE_BONUS_PUMBAA || m->role==TLK_MD_SPRITE_PICKUP));')
edit('engine/runner/tlk_md_sprite_format.inc','SP_NUMBER(8); /* Owned Scar/fire art and original Pride Rock palette phases. */','SP_NUMBER(9); /* Prepared bonus Timon/Pumbaa/bug artwork and normal palettes. */')
edit('engine/runner/tlk_next_scene_data.c','WORDS=1600','WORDS=2368')
edit('engine/runner/tlk_next_scene_data.c','TLKNXT04','TLKNXT05')
edit('engine/runner/tlk_next_scene_data.c','    ready=1;return 1;','''    /* Bonus normal palettes: actual Pumbaa/Timon bank3 and Hunt Timon bank4.
     * The shared gold/bug bank0 is unchanged; unknown banks stay unavailable. */
    for(unsigned scene=0;scene<4;scene++) {
        for(unsigned i=0;i<64;i++){const uint8_t *q=m+0x27d19c+i*2;colors[1600+scene*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);}
        for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++) {
            unsigned source=bank==0?0x7c93:!scene && bank==3?0x50ada:scene && bank==4?0x3d3e1:0;
            const uint8_t *q=s+source+i*2;colors[1856+scene*128+bank*16+i]=source?(q[0]|(unsigned)q[1]<<8):0;
        }
    }
    ready=1;return 1;''')
edit('engine/runner/tlk_next_scene_data.c','level==9?colors+1408:NULL;','level==9?colors+1408:level>=10 && level<=13?colors+1600+(level-10)*64:NULL;')
edit('engine/runner/tlk_next_scene_data.c','    if(level==9)return','    if(level>=10 && level<=13)return (((level==10?0x09u:0x11u)>>bank)&1)?colors+1856+(level-10)*128+bank*16:NULL;\n    if(level==9)return')
edit('engine/runner/tlk_md_assets.c','level==8 || level==9) && TlkMdSceneReady','level==8 || level==9 || (level>=10 && level<=13)) && TlkMdSceneReady')
edit('engine/runner/tlk_md_assets.c','        int y=level==0 ?','''        if(level>=10 && level<=13) {
            /* Original08C252, common08E738 after Hunt's30-update init delay:
             * fixed plane offsets0, complete static names and used tiles. */
            x=sx+column+(320-width)/2;
        }
        int y=level==0 ?''')
edit('engine/runner/tlk_md_assets.c','level==8 || level==9) ? sy','level==8 || level==9 || (level>=10 && level<=13)) ? sy')
# The player slot belongs to Pumbaa/Timon in bonuses, not to Simba.
edit('engine/runner/tlk_wide.c','static bool CubPiece(const Piece *p) {','''static int BonusScene(void) {
    unsigned level=rd16(s_frame.ram+0x1ff9e);
    return level>=10 && level<=13 && rd24(s_frame.ram+0xdf)==0xc005dd+(level-10)*0x32;
}
static bool CubPiece(const Piece *p) {
    if(BonusScene())return false;''')
edit('engine/runner/tlk_wide.c','    unsigned next_desc=NextPieceDescriptor(p);','''    unsigned next_desc=NextPieceDescriptor(p);
    if(s_frame.stage && BonusScene()) {
        if(role==TLK_MD_SPRITE_BONUS_PUMBAA && s_md_level==10 && next_desc==0xc5858a)return role;
        if(role==TLK_MD_SPRITE_BONUS_TIMON && ((s_md_level==10 && next_desc==0xc58a71) ||
           (s_md_level>=11 && next_desc==0xc5858a)))return role;
        if(role==TLK_MD_SPRITE_PICKUP && ((s_md_level==10 && (next_desc==0xc58999 || next_desc==0xc589a5)) ||
           (s_md_level>=11 && (next_desc==0xc58975 || (next_desc>=0xc58a11 && next_desc<=0xc58a65 && (next_desc-0xc58a11)%12==0)))))return TLK_MD_SPRITE_BONUS_BUG;
        return 0;
    }''')
edit('engine/runner/tlk_wide.c','    if(!s_frame.stage || level<1 || level>9 ||','    if(!s_frame.stage || level<1 || level>13 ||')
edit('engine/runner/tlk_wide.c','TlkTitlePointer(s_frame.ram,0xdf)!=0xc00387+level*0x32)return;','(!BonusScene() && TlkTitlePointer(s_frame.ram,0xdf)!=0xc00387+level*0x32))return;')
edit('engine/runner/tlk_wide.c','first->pose!=0x7e17dd || draw<','(first->pose!=0x7e17dd && first->pose!=0x7e19f8) || draw<')
edit('engine/runner/tlk_wide.c','    int summit=s_frame.stage && s_md_level==9 && descriptor==0x7db;','    int summit=s_frame.stage && s_md_level==9 && descriptor==0x7db;\n    int bonus=s_frame.stage && BonusScene();')
edit('engine/runner/tlk_wide.c','pride_rock || summit?9:0);','pride_rock || summit?9:bonus?s_md_level:0);')
edit('engine/runner/tlk_wide.c','    for (unsigned kind=0;kind<3;kind++)','''    s_md_npc_frames[TLK_MD_SPRITE_BONUS_PUMBAA]=bonus && s_md_level==10 && TlkResourcesUseMd("graphics.sprites.bonus.pumbaa.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_PUMBAA]=bonus && s_md_level==10 && TlkResourcesUseMd("graphics.sprites.bonus.pumbaa.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_TIMON]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.timon.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_TIMON]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.timon.palette");
    s_md_npc_frames[TLK_MD_SPRITE_BONUS_BUG]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.bugs.frames");
    s_md_npc_palette[TLK_MD_SPRITE_BONUS_BUG]=bonus && TlkResourcesUseMd("graphics.sprites.bonus.bugs.palette");
    for (unsigned kind=0;kind<3;kind++)''')
edit('engine/runner/tlk_wide.c','(s_md_level<=8 || pride_rock) && TlkMdSceneReady','(s_md_level<=8 || pride_rock || bonus) && TlkMdSceneReady')
edit('engine/runner/tlk_wide.c','|| simbas_return || pride_rock) && TlkMdSceneBackgroundReady','|| simbas_return || pride_rock || bonus) && TlkMdSceneBackgroundReady')
edit('engine/runner/tlk_wide.c','hakuna || pride_rock || (level==6','hakuna || pride_rock || BonusScene() || (level==6')
edit('engine/runner/tlk_resources.c','    {"gameplay.levels.adult_hyenas.bounds",','''    {"graphics.sprites.bonus", "Bonus stages", 2, 0, 0, 0, "Introductory cards, counters and unknown effects retain native art"},
    {"graphics.sprites.bonus.pumbaa", "Pumbaa", 2, 0, 0, 0, "Bug Toss; native movement, timing and catches retained"},
    {"graphics.sprites.bonus.pumbaa.frames", "Frame artwork", 2, 1, 0, 1, "Original MD Pumbaa drawings paired by original animation phases; unknown poses remain native"},
    {"graphics.sprites.bonus.pumbaa.palette", "Palette", 2, 1, 0, 1, "Original MD bonus palette3, independently selected; flashes remain native"},
    {"graphics.sprites.bonus.timon", "Timon", 2, 0, 0, 0, "Bug Toss thrower and Bug Hunt player; introductory cards remain native"},
    {"graphics.sprites.bonus.timon.frames", "Frame artwork", 2, 1, 0, 1, "Original MD Timon throw/walk/hunt drawings; native timing and unknown-pose fallback"},
    {"graphics.sprites.bonus.timon.palette", "Palette", 2, 1, 0, 1, "Original MD bonus palette3 for reviewed Timon bodies; independent of scenery"},
    {"graphics.sprites.bonus.bugs", "Bugs", 2, 0, 0, 0, "Owned static/falling bonus bugs; counters and effects remain native"},
    {"graphics.sprites.bonus.bugs.frames", "Frame artwork", 2, 1, 0, 1, "Original MD drawings from corresponding eight-kind spawn records and shared exact-image links"},
    {"graphics.sprites.bonus.bugs.palette", "Palette", 2, 1, 0, 1, "Original common MD bug colors; independent of artwork and gameplay"},
    {"audio.music.bug_toss", "Bug Toss", 20, 1, 1, 1, "Original MD program134 during the round; stops for the native result card; other effects remain native"},
    {"audio.music.bug_hunt", "Bug Hunt", 20, 1, 1, 1, "Original MD program281 in all three Hunt variants; native timer, effects and reward logic retained"},
    {"gameplay.levels.adult_hyenas.bounds",''')
edit('engine/runner/tlk_resources.c','ending and bonus scenery remain native','ending scenery remains native; bonus backgrounds are fixed per-scene adapters')
# Music is independent and never overwrites the guest's native sound queue.
edit('engine/runner/tlk_audio.c','static int late_adult(void) {','''static int bonus_scene(void) {
    unsigned level=word(0x1ff9e);
    return level>=10 && level<=13 && word(0xdf)==0x5dd+(level-10)*0x32 && g_ram[0xe1]==0xc0;
}
static unsigned bonus_music(void) {
    if(!bonus_scene())return 0;
    if(word(0x1ff9e)!=10)return 281;
    return address(0xb243)==0xc53f6f?0:134;
}
static const char *bonus_music_source(void){return word(0x1ff9e)==10?"audio.music.bug_toss":"audio.music.bug_hunt";}
static int late_adult(void) {''')
edit('engine/runner/tlk_audio.c','    if (pride_game_over()) return 327;','    if (pride_game_over()) return 327;\n    if(bonus_scene())return bonus_music();')
edit('engine/runner/tlk_audio.c','    if(death_scene() && death_phase>=2)return death_phase==2 && md_death_music();','    if(death_scene() && death_phase>=2)return death_phase==2 && md_death_music();\n    if(bonus_scene())return bonus_music() && TlkResourcesUseMd(bonus_music_source());')
edit('engine/runner/tlk_audio.c','return (death_scene() || pride_game_over()) && music_active','return (death_scene() || pride_game_over() || bonus_scene()) && music_active')
edit('engine/runner/tlk_audio.c','    if(id && !strcmp(id,"audio.music.pride_game_over"))return pride_game_over();','    if(id && (!strcmp(id,"audio.music.bug_toss") || !strcmp(id,"audio.music.bug_hunt")))return bonus_music() && !strcmp(id,bonus_music_source());\n    if(id && !strcmp(id,"audio.music.pride_game_over"))return pride_game_over();')
edit('engine/runner/tlk_audio.c','    return mask;\n}','    if(TlkResourcesUseMd("audio.music.bug_toss"))mask|=1<<(MUSIC_COUNT+14);\n    if(TlkResourcesUseMd("audio.music.bug_hunt"))mask|=1<<(MUSIC_COUNT+15);\n    return mask;\n}')
edit('engine/runner/tlk_audio.c','if(TLK_BATTLE_MUSIC_TRIGGER_AVAILABLE && scene_music()==134)','if(TLK_BATTLE_MUSIC_TRIGGER_AVAILABLE && pride() && scene_music()==134)')
edit('engine/runner/tlk_audio.c','if (pending_stop && (death_scene() || pride_game_over()))','if (pending_stop && (death_scene() || pride_game_over() || bonus_scene()))')

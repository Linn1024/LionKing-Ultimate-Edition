"""Integrate reviewed Pride Rock cave resources and owned Scar artwork."""
from pathlib import Path

def edit(name,old,new):
 p=Path(name);s=p.read_text();assert old in s,(name,old[:80]);p.write_text(s.replace(old,new))
edit('tools/later_sprite_catalog.py',"json.loads((ROOT/'tools/later_actor_pairs.json').read_text())['pairs']","[pair for name in ('later_actor_pairs.json','pride_actor_pairs.json') for pair in json.loads((ROOT/'tools'/name).read_text())['pairs']]")
edit('engine/runner/tlk_md_sprites.h','       TLK_MD_SPRITE_ADULT_HYENA,','       TLK_MD_SPRITE_ADULT_HYENA, TLK_MD_SPRITE_SCAR,')
edit('engine/runner/tlk_next_scene_data.c','WORDS=1280','WORDS=1600')
edit('engine/runner/tlk_next_scene_data.c','TLKNXT03','TLKNXT04')
edit('engine/runner/tlk_next_scene_data.c','    ready=1;return 1;','''    /* Original9 background callback cycles these three complete palettes;
     * the static level-table palette is not the normal live colors. */
    for(unsigned phase=0;phase<3;phase++)for(unsigned i=0;i<64;i++) {
        const uint8_t *q=m+0x8e538+phase*128+i*2;
        colors[1280+phase*64+i]=TlkMdColor555((unsigned)q[0]<<8|q[1]);
    }
    static const unsigned pride_rock[8]={0x7c93,0,0,0,0x7d13,0,0x7d53,0x7d73};
    for(unsigned bank=0;bank<8;bank++)for(unsigned i=0;i<16;i++) {
        const uint8_t *q=s+pride_rock[bank]+i*2;
        colors[1472+bank*16+i]=pride_rock[bank]?(q[0]|(unsigned)q[1]<<8):0;
    }
    ready=1;return 1;''')
edit('engine/runner/tlk_next_scene_data.c','colors+896+(level-7)*64:NULL;','colors+896+(level-7)*64:level==9?colors+1408:NULL;')
edit('engine/runner/tlk_next_scene_data.c','    if(level>=3 && level<=4)return','    if(level==9)return (0xd1u&(1u<<bank))?colors+1472+bank*16:NULL;\n    if(level>=3 && level<=4)return')
p=Path('engine/runner/tlk_next_scene_data.c');p.write_text(p.read_text()+'\nconst uint16_t *TlkNextScenePrideRockPhase(unsigned phase){return ready && phase<3?colors+1280+phase*64:NULL;}\n')
edit('engine/runner/tlk_next_scene_data.h','#endif','const uint16_t *TlkNextScenePrideRockPhase(unsigned phase);\n#endif')
edit('engine/runner/tlk_md_assets.c','level==7 || level==8) &&','level==7 || level==8 || level==9) &&')
edit('engine/runner/tlk_md_assets.c','        int y=level==0 ?','''        if(level==9) {
            /* Original08E2B0/08E532:96/88/40 lines,1/2,1/4,1/2 X,Y=0. */
            unsigned shift=sy<96?1:sy<184?2:1;int origin=cx-column;
            x=(origin>=0?origin/(1<<shift):-((-origin+(1<<shift)-1)/(1<<shift)))+sx+column;
        }
        int y=level==0 ?''')
edit('engine/runner/tlk_md_assets.c','level==7 || level==8) ? sy','level==7 || level==8 || level==9) ? sy')
p=Path('engine/runner/tlk_md_assets.c');p.write_text(p.read_text()+'''\nvoid TlkMdScenePreparedPalette(unsigned level,const uint16_t colors[64]) {
    if(level!=9 || !colors || !TlkMdSceneReady(level))return;
    if(memcmp(scenes[level].palette,colors,sizeof scenes[level].palette)) {
        memcpy(scenes[level].palette,colors,sizeof scenes[level].palette);cache_level=-1;
    }
}
''')
edit('engine/runner/tlk_md_assets.h','void TlkMdScenePalette(unsigned level,','/* A scene owner may install its prepared normal animation colors. */\nvoid TlkMdScenePreparedPalette(unsigned level,const uint16_t colors[64]);\nvoid TlkMdScenePalette(unsigned level,')
edit('engine/runner/tlk_md_sprites.c','level<=8?level:0','level<=9?level:0')
edit('engine/runner/tlk_md_sprites.c','((next_scene==7 || next_scene==8) &&','((next_scene==7 || next_scene==8 || next_scene==9) &&')
edit('engine/runner/tlk_md_sprites.c','m->role==TLK_MD_SPRITE_LATER_PICKUP || m->role==TLK_MD_SPRITE_PICKUP));','m->role==TLK_MD_SPRITE_LATER_PICKUP || m->role==TLK_MD_SPRITE_PICKUP || m->role==TLK_MD_SPRITE_SCAR));')
p=Path('engine/runner/tlk_wide.c');s=p.read_text();s=s.replace('s_hakuna_waterfall','s_scene_animation');p.write_text(s)
edit('engine/runner/tlk_wide.c','    unsigned next_desc=NextPieceDescriptor(p);','''    unsigned next_desc=NextPieceDescriptor(p);
    if(s_frame.stage && s_md_level==9 && (rd16(s_frame.ram+0xdf)==0x549 || rd16(s_frame.ram+0xdf)==0x7db)) {
        if(role==TLK_MD_SPRITE_SCAR && (next_desc==0xc585e8 || next_desc==0xc585f4 || next_desc==0xc58600))return role;
        if(role==TLK_MD_SPRITE_ADULT_HYENA && next_desc==0xc58ecc)return role;
        if(role==TLK_MD_SPRITE_LATER_WORLD && (next_desc==0xc5866c || next_desc==0xc58678 || next_desc==0xc58618 || next_desc==0xc5863c || next_desc==0xc58624 || next_desc==0xc58630))return role;
        if(role==TLK_MD_SPRITE_PICKUP && (next_desc==0xc5892d || next_desc==0xc58939))return role;
        return 0;
    }''')
edit('engine/runner/tlk_wide.c','    TlkMdSceneAnimationPhase(5,s_scene_animation.phase);','''    int pride_rock=s_frame.stage && s_md_level==9 && descriptor==0x549;
    int summit=s_frame.stage && s_md_level==9 && descriptor==0x7db;
    TlkMdSceneAnimationPhase(5,s_scene_animation.active==5?s_scene_animation.phase:0);
    if(pride_rock)TlkMdScenePreparedPalette(9,TlkNextScenePrideRockPhase(s_scene_animation.phase));''')
edit('engine/runner/tlk_wide.c','simbas_return?8:0);','simbas_return?8:pride_rock || summit?9:0);')
# Only exact owned playable scenes get shared actors/HUD; ending/title scenes stay native.
edit('engine/runner/tlk_wide.c','destiny || be_prepared || simbas_return) && rd16','destiny || be_prepared || simbas_return || pride_rock || summit) && rd16')
edit('engine/runner/tlk_wide.c','(pride || exile || hakuna || destiny || be_prepared || simbas_return) &&','(pride || exile || hakuna || destiny || be_prepared || simbas_return || pride_rock || summit) &&')
edit('engine/runner/tlk_wide.c','(hakuna || destiny || be_prepared) && TlkResourcesUseMd("graphics.sprites.world_objects.','(hakuna || destiny || be_prepared || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.world_objects.')
edit('engine/runner/tlk_wide.c','(be_prepared || simbas_return) && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.adult.','(be_prepared || simbas_return || pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.hyenas.adult.')
edit('engine/runner/tlk_wide.c','    for (unsigned kind=0;kind<3;kind++)','''    s_md_npc_frames[TLK_MD_SPRITE_SCAR]=(pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.scar.frames");
    s_md_npc_palette[TLK_MD_SPRITE_SCAR]=(pride_rock || summit) && TlkResourcesUseMd("graphics.sprites.enemies.scar.palette");
    for (unsigned kind=0;kind<3;kind++)''')
edit('engine/runner/tlk_wide.c','|| be_prepared || simbas_return) && TlkResourcesHudFramesMd','|| be_prepared || simbas_return || pride_rock || summit) && TlkResourcesHudFramesMd')
edit('engine/runner/tlk_wide.c','s_frame.stage && s_md_level<=8 && TlkMdSceneReady','s_frame.stage && (s_md_level<=8 || pride_rock) && TlkMdSceneReady')
edit('engine/runner/tlk_wide.c','|| be_prepared || simbas_return) && TlkMdSceneBackgroundReady','|| be_prepared || simbas_return || pride_rock) && TlkMdSceneBackgroundReady')
edit('engine/runner/tlk_wide.c','    if(!hakuna)memset(&s_scene_animation,0,sizeof s_scene_animation);','''    int pride_rock=s_frame.stage && level==9 && descriptor==0x549;
    if(pride_rock) {
        if(s_scene_animation.active!=9) {
            s_scene_animation.active=9;s_scene_animation.phase=2;s_scene_animation.delay=200;
            s_scene_animation.latch=s_frame.latch_serial;
        } else if(!hold && !rd16(s_frame.ram+0x0a89) && s_scene_animation.latch!=s_frame.latch_serial) {
            s_scene_animation.latch=s_frame.latch_serial;
            if(s_scene_animation.delay)s_scene_animation.delay--;
            else {s_scene_animation.delay=10;s_scene_animation.phase=(s_scene_animation.phase+1)%3;}
        }
    } else if(!hakuna)memset(&s_scene_animation,0,sizeof s_scene_animation);''')
edit('engine/runner/tlk_wide.c','s_scene_animation.active=1;s_scene_animation.phase=0','s_scene_animation.active=5;s_scene_animation.phase=0')
edit('engine/runner/tlk_wide.c','hakuna || (level==6 && descriptor==0x4b3)','hakuna || pride_rock || (level==6 && descriptor==0x4b3)')
# Include declarations explicitly; no dependency from scene-helper into sprite-helper modules.
edit('engine/runner/tlk_wide.c','#include "tlk_md_assets.h"','#include "tlk_md_assets.h"\n#include "tlk_next_scene_data.h"')
edit('engine/runner/tlk_resources.c','{"audio.music.pride_rock", "Pride Rock", 20, 1, 1, 1, "Original MD program 432; changing audio restarts the current level"}','{"audio.music.pride_rock", "Pride Rock", 20, 0, 0, 0, "Cave scene; summit and ending music stay native"}')
edit('engine/runner/tlk_resources.c','Be Prepared and Simba\'s Return','Be Prepared, Simba\'s Return and Pride Rock')
edit('engine/runner/tlk_resources.c','palette3 in Be Prepared and Return','palette3 in Be Prepared, Return and Pride Rock')
edit('engine/runner/tlk_resources.c','Be Prepared and Return; voices','Be Prepared, Return and Pride Rock; voices')
edit('engine/runner/tlk_resources.c','    {"gameplay.levels.adult_hyenas.bounds",','''    {"graphics.sprites.enemies.scar", "Scar", 12, 0, 0, 0, "Native combat and animation timing; unknown poses use native art"},
    {"graphics.sprites.enemies.scar.frames", "Frame artwork", 12, 1, 0, 1, "Reviewed original MD Scar drawings in cave and summit encounters; flashes and unknown poses remain native"},
    {"graphics.sprites.enemies.scar.palette", "Palette", 12, 1, 0, 1, "Original MD Scar palette3, independent of scenery and artwork"},
    {"audio.music.pride_rock.track", "Level track", 20, 1, 1, 1, "Original MD program432 in the cave; summit/ending remain native"},
    {"audio.music.pride_rock.death", "Health-death cue", 20, 1, 1, 1, "Original shared adult MD program430; cave nonfinal health death only; native retry/fall/final-life paths"},
    {"gameplay.levels.adult_hyenas.bounds",''')
edit('engine/runner/tlk_hitboxes.c','(word(0x1ff9e)==8 && pointer(0xdf)==0xc00517))','(word(0x1ff9e)==8 && pointer(0xdf)==0xc00517) ||\n               (word(0x1ff9e)==9 && pointer(0xdf)==0xc00549))')
edit('engine/runner/tlk_audio.c','"audio.music.simbas_return.track", "audio.music.pride_rock"','"audio.music.simbas_return.track", "audio.music.pride_rock.track"')
edit('engine/runner/tlk_audio.c','static int late_adult(void) {return be_prepared() || simbas_return();}','static int pride_rock(void) {return word(0x1ff9e)==9 && word(0xdf)==0x549 && g_ram[0xe1]==0xc0;}\nstatic int late_adult(void) {return be_prepared() || simbas_return() || pride_rock();}')
edit('engine/runner/tlk_audio.c','    if(simbas_return())return "audio.music.simbas_return.death";','    if(simbas_return())return "audio.music.simbas_return.death";\n    if(pride_rock())return "audio.music.pride_rock.death";')
edit('engine/runner/tlk_audio.c','    unsigned level=word(0x1ff9e);\n    return id &&','    if(id && !strcmp(id,"audio.music.pride_rock.death"))return pride_rock() && word(0x2000)==0xffff && (death_phase==2 || word(0x1ffaa));\n    unsigned level=word(0x1ff9e);\n    return id &&')
edit('engine/runner/tlk_audio.c','    return mask;\n}','    if(TlkResourcesUseMd("audio.music.pride_rock.death"))mask|=1<<(MUSIC_COUNT+13);\n    return mask;\n}')

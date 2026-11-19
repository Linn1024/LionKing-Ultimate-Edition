#include "tlk_resource_death_choice.h"
#include <stdatomic.h>
#include "tlk_fallback_log.h"
#ifndef TLK_NATIVE_AUDIO_OWNER_AVAILABLE
#define TLK_NATIVE_AUDIO_OWNER_AVAILABLE 0
#endif
#ifndef TLK_LIFE_PICKUP_AVAILABLE
#define TLK_LIFE_PICKUP_AVAILABLE 0
#endif
#ifndef TLK_STAMPEDE_EXIT_AVAILABLE
#define TLK_STAMPEDE_EXIT_AVAILABLE 0
#endif
#ifndef TLK_BE_PREPARED_RETRY_AVAILABLE
#define TLK_BE_PREPARED_RETRY_AVAILABLE 0
#endif
#ifndef TLK_BE_PREPARED_TERRAIN_AVAILABLE
#define TLK_BE_PREPARED_TERRAIN_AVAILABLE 0
#endif
#ifndef TLK_BE_PREPARED_ROCKS_AVAILABLE
#define TLK_BE_PREPARED_ROCKS_AVAILABLE 0
#endif
#ifndef TLK_BONUS_SELECTION_AVAILABLE
#define TLK_BONUS_SELECTION_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_EXIT_AVAILABLE
#define TLK_DESTINY_EXIT_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_MONKEY_AVAILABLE
#define TLK_DESTINY_MONKEY_AVAILABLE 0
#endif
#ifndef TLK_ADULT_ROAR_AVAILABLE
#define TLK_ADULT_ROAR_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_ARENA_AVAILABLE
#define TLK_DESTINY_ARENA_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_ROCK_SURFACE_AVAILABLE
#define TLK_DESTINY_ROCK_SURFACE_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_ROCK_POSITIONS_AVAILABLE
#define TLK_DESTINY_ROCK_POSITIONS_AVAILABLE 0
#endif
#ifndef TLK_ADULT_TURN_AVAILABLE
#define TLK_ADULT_TURN_AVAILABLE 0
#endif
#ifndef TLK_ADULT_POINTS_AVAILABLE
#define TLK_ADULT_POINTS_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_OBSTACLES_AVAILABLE
#define TLK_DESTINY_OBSTACLES_AVAILABLE 0
#endif
#ifndef TLK_DESTINY_TERRAIN_AVAILABLE
#define TLK_DESTINY_TERRAIN_AVAILABLE 0
#endif
#include "tlk_resources.h"
#ifndef TLK_STAMPEDE_SHAKE_AVAILABLE
#define TLK_STAMPEDE_SHAKE_AVAILABLE 0
#endif
#include "tlk_late_scene_data.h"
#include "tlk_be_prepared_data.h"
#include "tlk_graveyard_data.h"
#ifndef TLK_GRAVEYARD_PICKUPS_AVAILABLE
#define TLK_GRAVEYARD_PICKUPS_AVAILABLE 0
#endif
#ifndef TLK_GRAVEYARD_WALL_AVAILABLE
#define TLK_GRAVEYARD_WALL_AVAILABLE 0
#endif
#ifndef TLK_GRAVEYARD_SHAKE_AVAILABLE
#define TLK_GRAVEYARD_SHAKE_AVAILABLE 0
#endif
#ifndef TLK_GRAVEYARD_TURN_AVAILABLE
#define TLK_GRAVEYARD_TURN_AVAILABLE 0
#endif
#ifndef TLK_GRAVEYARD_LAUNCH_AVAILABLE
#define TLK_GRAVEYARD_LAUNCH_AVAILABLE 0
#endif
#ifndef TLK_GRAVEYARD_FAREWELL_AVAILABLE
#define TLK_GRAVEYARD_FAREWELL_AVAILABLE 0
#endif
#ifndef TLK_LATE_LAYOUT_AVAILABLE
#define TLK_LATE_LAYOUT_AVAILABLE 0
#endif
#ifndef TLK_SCAR_CONTACT_RESPONSE_AVAILABLE
#define TLK_SCAR_CONTACT_RESPONSE_AVAILABLE 0
#endif
#ifndef TLK_ADULT_LEDGE_REACTIONS_AVAILABLE
#define TLK_ADULT_LEDGE_REACTIONS_AVAILABLE 0
#endif
#ifndef TLK_ADULT_HYENA_CULLING_AVAILABLE
#define TLK_ADULT_HYENA_CULLING_AVAILABLE 0
#endif
#ifndef TLK_RETURN_DOOR_TIMING_AVAILABLE
#define TLK_RETURN_DOOR_TIMING_AVAILABLE 0
#endif
#ifndef TLK_BE_PREPARED_GROUP_AUDIO_AVAILABLE
#define TLK_BE_PREPARED_GROUP_AUDIO_AVAILABLE 0
#endif
#ifndef TLK_BE_PREPARED_BEHAVIOR_AVAILABLE
#define TLK_BE_PREPARED_BEHAVIOR_AVAILABLE 0
#endif
#ifndef TLK_BE_PREPARED_AVAILABLE
#define TLK_BE_PREPARED_AVAILABLE 0
#endif
#ifndef TLK_SCAR_ACTIVATION_AVAILABLE
#define TLK_SCAR_ACTIVATION_AVAILABLE 0
#endif
#ifndef TLK_RETURN_EXIT_AVAILABLE
#define TLK_RETURN_EXIT_AVAILABLE 0
#endif
#ifndef TLK_RETURN_WALL_AVAILABLE
#define TLK_RETURN_WALL_AVAILABLE 0
#endif
#ifndef TLK_RETURN_DOORWAY_HYENAS_AVAILABLE
#define TLK_RETURN_DOORWAY_HYENAS_AVAILABLE 0
#endif
#ifndef TLK_EXILE_TERRAIN_AVAILABLE
#define TLK_EXILE_TERRAIN_AVAILABLE 0
#endif
#ifndef TLK_EXILE_EXIT_AVAILABLE
#define TLK_EXILE_EXIT_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_TERRAIN_AVAILABLE
#define TLK_HAKUNA_TERRAIN_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_RETRY_AVAILABLE
#define TLK_HAKUNA_RETRY_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_SPIDERS_AVAILABLE
#define TLK_HAKUNA_SPIDERS_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_FROGS_AVAILABLE
#define TLK_HAKUNA_FROGS_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_INITIALIZATION_AVAILABLE
#define TLK_HAKUNA_INITIALIZATION_AVAILABLE 0
#endif
#include "tlk_md_assets.h"
#include "tlk_md_sound.h"
#include "tlk_md_sprites.h"
#include "tlk_md_hud.h"
#include "tlk_checkpoint_art.h"
#include "tlk_title_art.h"
#include "tlk_revival_art.h"
#include "tlk_native_hud.h"
#include "tlk_contact_map.h"
#include "tlk_graveyard_data.h"
#include "tlk_next_scene_data.h"
#include "tlk_destiny_monkey_data.h"
#include "tlk_interlevel_data.h"
#include "tlk_interlevel_policy.h"
#include "tlk_bonus_policy.h"
#include "tlk_hunt_data.h"
#include "tlk_bonus_result_policy.h"
#include "tlk_cant_wait_policy.h"
#include "tlk_cant_wait_data.h"
#include "tlk_cw_terrain_data.h"
#include "tlk_bonus_result_data.h"
#include "tlk_roar_data.h"
#include "tlk_start_data.h"
#include "tlk_reactivation_data.h"
#include "tlk_hitbox_data.h"
#include "tlk_hyena_voice_policy.h"
#include "tlk_lizard_voice_policy.h"
#include "tlk_porcupine_voice_policy.h"
#include "tlk_menu_audio_policy.h"
#include "tlk_hyena_probe_policy.h"
#include "tlk_hyena_entrance_policy.h"
#include "tlk_final_menu_policy.h"
#include "tlk_resource_parent.h"
#include "native_adapters.h"
#include "sha256.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <windows.h>
#endif

/* Parent-before-child order is part of the schema; IDs persist across releases.
 * New leaves inherit naturally. Support is earned by a working adapter. */
static TlkResourceNode nodes[] = {
    {"game", "The Lion King", -1, 0, 0, 0, ""},
    {"graphics", "Graphics", 0, 0, 0, 0, ""},
    {"graphics.sprites", "Sprites", 1, 0, 0, 0, ""},
    {"graphics.sprites.simba", "Simba", 2, 0, 0, 0, ""},
    {"graphics.sprites.simba.cub", "Cub", 3, 0, 0, 0, ""},
    {"graphics.sprites.simba.cub.frames", "Animation frames", 4, 1, 0, 1, "ROM-backed shared cub art: Pride Lands including verified health-death poses, Can't Wait to Be King, Elephant Graveyard, reviewed Stampede running frames, Simba's Exile and Hakuna Matata; native fallback for unmapped poses; timing independent"},
    {"graphics.sprites.simba.cub.palette", "Palette", 4, 1, 0, 1, "Shared cub palette; flash palettes preserved"},
    {"graphics.sprites.simba.adult", "Adult", 3, 0, 0, 0, ""},
    {"graphics.sprites.simba.adult.frames", "Animation frames", 7, 1, 0, 1, "Reviewed shared adult artwork in Destiny, Be Prepared, Return and Pride Rock; native timing and fallback for unmapped poses"},
    {"graphics.sprites.simba.adult.palette", "Palette", 7, 1, 0, 1, "Shared Simba palette; flash palettes preserved"},
    {"graphics.sprites.enemies", "Enemies", 2, 0, 0, 0, ""},
    {"graphics.sprites.enemies.hyenas", "Hyenas", 10, 0, 0, 0, ""},
    {"graphics.sprites.enemies.other", "Other enemies", 10, 0, 0, 0, ""},
    {"graphics.sprites.pickups", "Pickups", 2, 0, 0, 0, ""},
    {"graphics.scenery", "Scenery", 1, 0, 0, 0, ""},
    {"graphics.scenery.foreground", "Foreground", 14, 1, 0, 1, "Bug Toss uses the complete original MD320x224 foreground and matching sprite origin; other supported scenes use prepared matching MD cells; unmatched/special scenes retain native artwork"},
    {"graphics.scenery.background", "Background", 14, 1, 0, 1, "MD backgrounds through Pride Rock and postfight, plus the original Stampede canyon; postfight requires prepared rain colors. Sunrise illustration has its own choice; bonus backgrounds follow their individual scenes"},
    {"graphics.scenery.palettes", "Scenery palettes", 14, 1, 0, 1, "MD scenery colours, including Can't Wait to Be King's changing foreground/background palette; nearest-colour mapping for mixed artwork"},
    {"graphics.hud", "HUD", 1, 0, 0, 0, ""},
    {"audio", "Audio", 0, 0, 0, 0, ""},
    {"audio.music", "Music", 19, 0, 0, 0, ""},
    {"audio.music.pride_lands", "Pride Lands", 20, 1, 1, 1, "Original MD driver; level restarts when changing this source"},
    {"audio.music.other", "Other tracks", 20, 1, 0, 0, ""},
    {"audio.effects", "Sound effects", 19, 0, 0, 0, ""},
    {"audio.effects.simba", "Simba", 23, 0, 0, 0, ""},
    {"audio.effects.world", "World and enemies", 23, 0, 0, 0, ""},
    {"audio.voices", "Voices", 19, 0, 0, 0, ""},
    {"gameplay", "Gameplay", 0, 0, 0, 0, ""},
    {"gameplay.simba", "Simba", 27, 0, 0, 0, ""},
    {"gameplay.simba.movement", "Movement and physics", 28, 1, 1, 0, ""},
    {"gameplay.simba.combat", "Combat", 28, 1, 1, 0, ""},
    {"gameplay.enemies", "Enemy behavior", 27, 1, 1, 0, ""},
    {"gameplay.collision", "Collision", 27, 1, 1, 0, ""},
    {"gameplay.levels", "Level layouts", 27, 0, 0, 0, ""},
    {"gameplay.levels.pride_lands", "Pride Lands", 33, 0, 0, 0, ""},
    {"gameplay.levels.other", "Other levels", 33, 1, 1, 0, ""},
    {"gameplay.difficulty", "Difficulty rules", 27, 1, 2, 0, ""},
    {"display", "Display", 0, 0, 0, 0, ""},
    {"display.viewport", "Viewport width", 37, 1, 0, 1, "Native viewport: SNES 256; MD 320 in reviewed scrolling scenes, 256 in Stampede"},
    {"audio.effects.simba.roar", "Roar", 24, 1, 1, 1, "Pride Lands, Can't Wait to Be King and Elephant Graveyard cub roar; original MD PCM driver; changing audio restarts the level"},
    {"audio.effects.simba.adult_roar", "Adult roar", 24, 1, 1, TLK_ROAR_AOT_AVAILABLE, "Original MD adult voice11 at the actual roar pulse in Destiny through Pride Rock; the later native voice is silent. Independent of cub voice, artwork and roar timing; changing audio restarts the level"},
    {"audio.effects.simba.adult_swipe", "Adult claw swipe", 24, 1, 1, 1, "Shared adult attack program: original MD FM96 at the native swipe cue in all main worlds. Ground and airborne attacks share this source; ledge contact, roar, damage, artwork and timing remain independent; changing audio restarts the level"},
    {"audio.effects.simba.adult_pounce", "Adult pounce", 24, 1, 1, 1, "Original MD pounce sound in all main worlds. Claw, grapple, roar, artwork, damage and gameplay timing remain independent; changing audio restarts the level"},
    {"audio.effects.simba.grapple_contact", "Adult grapple", 24, 1, 1, 1, "Original MD voice on big-cat grapple entry and no extra contact swipe. Ordinary roar, claw attacks, damage, artwork and gameplay timing remain independent; changing audio restarts the level"},
    {"audio.effects.world.big_cats", "Big-cat call", 25, 1, 1, 1, "Both big-cat variants: original MD voice18/96 once on action entry. Native later repeats are silent in the MD source. Artwork, movements, contacts, Simba sounds and music remain independent; changing audio restarts the level"},
    {"audio.effects.world.big_cat_hit", "Big-cat hit response", 25, 1, 1, 1, "Original MD voice when either big-cat variant is hit from either side. Big-cat calls, Simba sounds, artwork and gameplay remain independent; changing audio restarts the level"},
    {"audio.effects.world.simbas_destiny.boulders", "Destiny boulder sounds", 25, 1, 1, TLK_NATIVE_AUDIO_OWNER_AVAILABLE, "Original MD release rumble and landing impact for stationary and chasing boulders. Independent of Exile and Be Prepared rock sounds, artwork, movement and collision; changing audio restarts the level"},
    {"audio.effects.simba.other", "Other Simba effects", 24, 1, 0, 0, ""},
    {"graphics.sprites.enemies.hyenas.frames", "Frame artwork", 11, 1, 0, 1, "Pride Lands and Graveyard mapped hyena poses; Exile exit drawings share original pixels. Native animation timing retained; unknown poses remain native"},
    {"graphics.sprites.enemies.hyenas.palette", "Palette", 11, 1, 0, 1, "Original MD hyena colors in Pride Lands, Graveyard and the Exile exit; each scene uses its own palette; flashes preserved"},
    {"graphics.sprites.enemies.other.frames", "Frame artwork", 12, 1, 0, 1, "Beetles, Hakuna spiders and frogs, Destiny jaguars and Be Prepared flying enemies. Chameleons and porcupines have their own choices."},
    {"graphics.sprites.enemies.other.palette", "Palette", 12, 1, 0, 1, "Colors for beetles, spiders, frogs, jaguars and flying enemies. Chameleon and porcupine colors are chosen separately."},
    {"graphics.sprites.pickups.frames", "Frame artwork", 13, 1, 0, 1, "Original MD ground-bug drawings in supported scenes, including both bonus bugs; reviewed HUD flights; other effects retain native art"},
    {"graphics.sprites.pickups.palette", "Palette", 13, 1, 0, 1, "Original MD colors for supported ground bugs and both bonus bugs; independent of artwork and Simba; native flashes preserved"},
    {"graphics.hud.frames", "Meters and lives", 18, 0, 0, 0, "Choose all HUD artwork together, or override roar, health and lives separately; Pride Lands, Can't Wait to Be King and Elephant Graveyard"},
    {"graphics.hud.palette", "Palette", 18, 1, 0, 1, "Shared HUD and direction-hint palette; native artwork and flash palettes preserved"},
    {"audio.effects.simba.hurt", "Hurt", 24, 1, 1, 1, "Original MD PCM1 for ordinary cub and adult Simba hurt in the main worlds; Stampede's collision cry remains independently selected"},
    {"audio.effects.world.lizard", "Lizard attack", 25, 1, 1, 1, TLK_LIZARD_VOICE_TIMING_AVAILABLE ? "Pride Lands/Exile chameleon attack: original MD FM124 at counter32; native choice keeps counter51; artwork and gameplay independent" : "Pride Lands lizard call; original MD FM124 at native cue timing"},
    {"audio.effects.world.be_prepared.group_call", "Be Prepared group call", 25, 1, 1, TLK_BE_PREPARED_GROUP_AUDIO_AVAILABLE, "Original MD group PCM request and parameter, or native SNES voice; cadence follows the independently selected enemy behavior. Changing audio restarts the level"},
    {"audio.effects.world.other", "Other world effects", 25, 1, 0, 0, ""},
    {"audio.effects.world.bonus_bug", "Bonus bug cue", 25, 1, 1, 1, "Both bonus-bug programs: PCM15 in cub stages, FM114 in adult stages; King's first bug retains its separate sound choice; contact and collection unchanged"},
    {"audio.effects.world.checkpoint", "Checkpoint", 25, 1, 1, 1, "Shared main-level checkpoint program; original MD FM cue101 at the exact native pickup event"},
    {"gameplay.camera", "Camera", 27, 1, 1, TLK_CAMERA_AOT_AVAILABLE, "Pride Lands, Can't Wait to Be King, Elephant Graveyard, Simba's Exile, Hakuna Matata, normal adult stages and Pride Rock postfight MD tracking arithmetic, including forward-only ride tracking and original loop width; adapted to viewport width; source/width changes restart the level"},
    {"gameplay.levels.pride_lands.pickups", "Pickup positions", 34, 1, 1, TLK_LAYOUT_AOT_AVAILABLE, "Original MD bonus-bug and spotted-bug marker positions; other layout and collision rules remain separate"},
    {"gameplay.continue_token_positions", "Continue-token positions", 27, 1, 1, TLK_LAYOUT_AOT_AVAILABLE, "Original MD Sun placements across levels; shared homes retained. Artwork, sound, contact and pickup limits remain independent; changing source restarts the level"},
    {"gameplay.levels.pride_lands.other", "Other layout rules", 34, 1, 1, 0, ""},
    {"audio.effects.world.health_bug", "Health bug", 25, 1, 1, 1, "Shared health pickup in all main worlds, including Hakuna and adult levels; original MD FM cue97"},
    {"audio.effects.world.full_health_bug", "Full-health bug", 25, 1, 1, 1, "Shared full-health pickup in all main worlds, including Hakuna and adult levels; original MD FM cue98"},
    {"audio.effects.world.life_bug", "Extra-life bug", 25, 1, 1, 1, "Shared main-level extra-life pickup programs; original MD FM cue112, independent of reward rules"},
    {"audio.effects.world.roar_bug", "Roar-capacity bug", 25, 1, 1, 1, "Shared main-level roar-capacity pickup program; original MD FM cue116"},
    {"audio.effects.world.harmful_bug", "Harmful bug", 25, 1, 1, 1, "Shared main-level harmful pickup programs; original MD FM cue117, separate from Simba hurt and scene-specific hazards"},
    {"audio.effects.simba.bounce", "Enemy bounce", 24, 1, 1, 1, "Pride Lands and Elephant Graveyard cub enemy bounce; original MD FM cue 123; native timing"},
    {"audio.effects.simba.adult_landing", "Adult landing", 24, 1, 0, TLK_NATIVE_AUDIO_OWNER_AVAILABLE, "Original MD adult landing is silent; independent of the following jump sound, cub bounce, music and other actors. Live output selection; movement and animation unchanged"},
    {"audio.effects.world.porcupine", "Porcupine attack", 25, 1, 1, 1, TLK_PORCUPINE_VOICE_TIMING_AVAILABLE ? "Pride Lands original MD FM105 at counter28, independently of attack contact timing; native audio follows the selected gameplay cue" : "Pride Lands porcupine attack; original MD FM cue 105; native timing"},
    {"audio.effects.world.hyena_hurt", "Hyena voice", 25, 1, 1, 1, TLK_HYENA_VOICE_ENTRY_AVAILABLE ? "Pride Lands and Elephant Graveyard original MD PCM4 once on action entry; native choice retains its animation cues" : "Pride Lands and Elephant Graveyard hyena voice; original MD PCM4; native cue timing"},
    {"graphics.sprites.leaves", "Falling leaves", 2, 0, 0, 0, ""},
    {"graphics.sprites.leaves.frames", "Frame artwork", 65, 1, 0, 1, "Pride Lands 17 reviewed leaf poses; shared anchored artwork; native particle count and timing"},
    {"graphics.sprites.leaves.palette", "Palette", 65, 1, 0, 1, "Pride Lands original MD leaf palette; native flash and scene guards"},
    {"audio.effects.world.leaves", "Falling leaves", 25, 1, 1, TLK_LEAVES_AOT_AVAILABLE, "Pride Lands and Exile original MD FM rustle 94, once per emitter trigger; independent of leaf count and gravity"},
    {"gameplay.levels.pride_lands.leaves", "Falling leaves", 34, 1, 1, TLK_LEAVES_AOT_AVAILABLE, "Pride Lands original MD three-leaf emission and gravity; six-leaf cap; restarts the level"},
    {"audio.effects.simba.roll", "Rolling", 24, 1, 1, 1, "Pride Lands and Elephant Graveyard: MD omits the separate SNES rolling cue; enemy contact sounds remain independently selectable"},
    {"audio.effects.world.hyena_pant", "Hyena panting", 25, 1, 1, 1, "Pride Lands and Elephant Graveyard original MD panting PCM cue 7; native animation-event timing"},
    {"audio.effects.world.hyena_jump", "Hyena jump", 25, 1, 1, 1, "Pride Lands and Elephant Graveyard: MD omits the separate SNES jump voice; other hyena voices remain independently selectable"},
    {"audio.music.cant_wait_to_be_king", "Can't Wait to Be King", 20, 1, 1, 1, "Original MD level track 2; original driver; changing audio restarts the current level"},
    {"audio.music.elephant_graveyard", "Elephant Graveyard", 20, 0, 0, 0, "Level track and health-death cue; children inherit this source unless overridden"},
    {"gameplay.levels.pride_lands.contacts", "Terrain contact map", 34, 1, 1, TLK_TERRAIN_AOT_AVAILABLE, "Pride Lands original MD contact attributes per live cell; native movement and actor reactions; restarts the level"},
    {"audio.music.stampede", "Stampede", 20, 1, 1, 1, "Original MD program 145; changing audio restarts the current level"},
    {"audio.music.simbas_exile", "Simba's Exile", 20, 0, 0, 0, "Independent level and health-death tracks"},
    {"audio.music.hakuna_matata", "Hakuna Matata", 20, 0, 0, 0, "Independent level and health-death tracks; children inherit this source"},
    {"audio.music.simbas_destiny", "Simba's Destiny", 20, 0, 0, 0, "Independent level and health-death tracks; children inherit this source"},
    {"gameplay.simba.adult_turn_motion", "Adult turn motion", 28, 1, 1, TLK_ADULT_TURN_AVAILABLE, "Original MD adult turn stays in place while SNES shifts one pixel each update. Animation, controls, terrain and subsequent jump remain independent; restarts the level"},
    {"gameplay.simba.roar", "Cub roar timing", 28, 1, 1, TLK_ROAR_AOT_AVAILABLE, "Pride, Graveyard, Exile and Hakuna cub: original MD activation and animation; audio independent; changing this source restarts the level"},
    {"audio.effects.world.hyena_taunt", "Hyena taunt", 25, 1, 1, TLK_HYENA_TAUNT_AOT_AVAILABLE, "Pride Lands and Elephant Graveyard: original MD PCM3 once on action entry, replacing the later native cue; animation/gameplay remain independently controlled"},
    {"audio.music.be_prepared", "Be Prepared", 20, 0, 0, 0, "Independent level and health-death tracks; children inherit this source"},
    {"audio.music.simbas_return", "Simba's Return", 20, 0, 0, 0, "Independent level and health-death tracks; children inherit this source"},
    {"audio.music.pride_rock", "Pride Rock", 20, 0, 0, 0, "Independent cave and post-fight/sunrise scores; ending speech and credits have separate choices"},
    {"audio.effects.world.defeat_puff", "Defeat puff", 25, 1, 1, TLK_LIZARD_DEFEAT_AOT_AVAILABLE, "Shared main-world enemy defeat program: original MD FM165 at counter30; SNES has no separate cue. Enemy behavior, defeat animation, artwork and music remain independent"},
    {"graphics.sprites.effects", "Effects", 2, 0, 0, 0, ""},
    {"graphics.sprites.effects.defeat_puff", "Defeat puff", 86, 0, 0, 0, ""},
    {"graphics.sprites.effects.defeat_puff.frames", "Frame artwork", 87, 1, 0, 1, "Reviewed shared defeat effects in Pride, Hakuna and Destiny; native timing and unknown-art fallback"},
    {"graphics.sprites.effects.defeat_puff.palette", "Palette", 87, 1, 0, 1, "Pride Lands shared defeat puff: original MD palette 0; independent of enemy and Simba choices; native flashes preserved"},
    {"gameplay.levels.pride_lands.start", "Initial Simba position", 34, 1, 1, TLK_START_AOT_AVAILABLE, "Pride Lands default record: original MD initial X/Y; checkpoint coordinates and bonus-return records retain their own native paths; changing this source restarts the level"},
    {"gameplay.levels.pride_lands.activation", "Initial enemy activation", 34, 1, 1, TLK_SPAWN_INIT_AOT_AVAILABLE, "Pride Lands main record: original MD initial column scan after the camera settles; camera, positions and later enemy behavior remain independent; changing this source restarts the level"},
    {"gameplay.levels.pride_lands.lizard_reactivation", "Lizard reactivation position", 34, 1, 1, TLK_REACTIVATION_AOT_AVAILABLE, "Pride Lands lizards: MD offscreen marker is queued at current position; SNES uses original spawn position; other flags, enemy behavior and initial scan remain independent; changing this source restarts the level"},
    {"gameplay.hitboxes", "Actor collision bounds", 27, 0, 0, 0, ""},
    {"gameplay.hitboxes.adult_points", "Adult Simba contact points", 93, 1, 1, TLK_ADULT_POINTS_AVAILABLE, "Original MD sprite contact points for reviewed adult Simba poses in Destiny through Pride Rock. Corrects strike reach on obstacle columns and ledge-grip probes; body bounds, terrain, art and controls remain independent; ambiguous points keep native values; restarts the level"},
    {"gameplay.hitboxes.simba", "Simba body bounds", 93, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Pride Lands, Can't Wait to Be King, Hakuna Matata, Graveyard random-bug contacts and adult levels Destiny through Pride Rock: original MD left/top/right/bottom words for reviewed Simba poses, including ostrich riding; artwork, animation and terrain collision remain independent; unknown poses retain native bounds"},
    {"gameplay.hitboxes.enemies", "Enemy body bounds", 93, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Pride Lands: original MD pose bounds for mapped hyenas, lizards and porcupines; separate attack regions and unknown poses retain native behavior"},
    {"gameplay.levels.pride_lands.ceiling", "Ceiling collision", 34, 0, 0, 0, ""},
    {"gameplay.levels.pride_lands.ceiling_rows", "Row checks", 96, 1, 1, TLK_TERRAIN_AOT_AVAILABLE, "Pride Lands: original MD lower-row ceiling decision versus native two-row checks; terrain attributes and pose clearance stay independent; changing this source restarts the level"},
    {"gameplay.levels.pride_lands.ceiling_clearance", "Pose clearance", 96, 1, 1, TLK_TERRAIN_AOT_AVAILABLE && TLK_HITBOX_AOT_AVAILABLE, "Pride Lands mapped cub/enemy poses: original MD pose-top word for the ceiling probe; unknown/ambiguous poses retain native clearance; independent of row rules, body contacts and artwork"},
    {"gameplay.levels.pride_lands.streaming_top", "Streaming top margin", 34, 1, 1, TLK_STREAMING_TOP_AOT_AVAILABLE, "Pride Lands: original MD six-tile activation margin above the camera; initial scan, camera, actor motion and culling stay independent; changing this source restarts the level"},
    {"audio.music.pride_health_death", "Pride Lands health death", 20, 1, 1, 1, "Pride Lands cub health death: original MD program 430; independent of level/battle music; fall death and game over retain their separate native paths; changing audio restarts the level"},
    {"audio.music.pride_game_over", "Continue / Game over", 20, 1, 1, 1, "Shared continue/game-over screen after any main level: original MD program327; independent of level and death music; changing audio restarts the level"},
    {"graphics.sprites.checkpoints", "Checkpoint heads", 2, 0, 0, 0, ""},
    {"graphics.sprites.checkpoints.frames", "Frame artwork", 102, 1, 0, 1, "Shared checkpoint program and three original head drawings; independent of Simba; exact owner and native palette checks required"},
    {"graphics.sprites.checkpoints.palette", "Palette", 102, 1, 0, 1, "Shared checkpoint head palette; independent of Simba and HUD; exact native palette check preserves flashes"},
    {"audio.effects.world.pickup_arrival", "Pickup arrival", 25, 1, 1, TLK_PICKUP_ARRIVAL_AOT_AVAILABLE, "Pride Lands and Elephant Graveyard two reviewed HUD pickup arrivals: original MD FM112 on popup entry; SNES is silent; independent of collection sounds and artwork; changing audio restarts the level"},
    {"audio.effects.simba.ledge_grab", "Platform contact", 24, 1, 1, TLK_LEDGE_GRAB_AOT_AVAILABLE, "Original MD FM94 at both shared cub/adult ledge and platform-contact helpers in normal main levels; SNES is silent; artwork and gameplay timing remain independent; changing audio restarts the level"},
    {"audio.effects.world.lizard_launch", "Lizard launch", 25, 1, 1, TLK_LIZARD_LAUNCH_AOT_AVAILABLE, "Pride Lands lizard launch: original MD FM123 on initialization; SNES is silent; independent of Simba bounce, lizard attack, defeat puff, artwork and gameplay; changing audio restarts the level"},
    {"graphics.sprites.effects.pickup_arrival", "Pickup arrival sparkle", 86, 0, 0, 0, ""},
    {"graphics.sprites.effects.pickup_arrival.frames", "Animation artwork", 108, 1, 0, 1, "Pride Lands two HUD arrivals: six original MD sparkle phases over the native 36-update lifecycle; sound, palette and position independent; unrelated owners retain native art"},
    {"graphics.sprites.effects.pickup_arrival.palette", "Palette", 108, 1, 0, 1, "Pride Lands HUD arrival sparkle: original MD palette 0; independent of HUD, flight and collection choices; native flashes preserved"},
    {"graphics.sprites.effects.pickup_arrival.position", "HUD arrival position", 108, 1, 0, 1, "Pride Lands two HUD sparkles: original MD anchors at Y20, left X18 and right 26 pixels from the viewport edge; flight motion and HUD artwork remain independent"},
    {"graphics.titles", "Level captions", 1, 0, 0, 0, ""},
    {"graphics.titles.pride_lands", "The Pridelands", 112, 0, 0, 0, ""},
    {"graphics.titles.pride_lands.frames", "Caption artwork", 113, 1, 0, 1, "Pride Lands opening: original complete MD caption image, independently decoded from the ROM; spacing is part of that image; other strings retain native art"},
    {"graphics.titles.pride_lands.palette", "Palette", 113, 1, 0, 1, "Pride Lands opening caption: original MD shared palette; independent of HUD and Simba; native transition/flash palettes retain native fallback"},
    {"graphics.titles.pride_lands.position", "Caption position", 113, 1, 0, 1, "Pride Lands opening caption: always horizontally centred; MD selects Y72, SNES retains its original height and falling-letter offsets"},
    {"graphics.titles.pride_lands.duration", "Caption duration", 113, 1, 0, 1, "Pride Lands opening caption: original MD 100 updates instead of native 150; changes presentation only; other text and game updates remain independent"},
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
    {"gameplay.levels.pride_lands.final_life", "Final-life transition", 34, 1, 1, 1, "Pride Lands cub health death: MD frozen-picture fade, Continue input/timeout and return-to-level timing; menu artwork, nonfinal revival and audio are selected independently; later title-screen delay remains native; changing this source restarts the level"},
    {"gameplay.menus", "Menus", 27, 0, 0, 0, ""},
    {"gameplay.menus.title_navigation", "Title menu navigation", 119, 1, 1, 1, "MD opening readiness and two-choice title directions, nine-field action wait and sampled button history. Artwork, Options controls and new-game sequence stay independent; changing this source restarts the level"},
#endif
    {"audio.effects.title_cursor", "Title cursor", 23, 1, 1, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Initial title menu: MD FM100 at native Up/Down calls; verified dry native voice replaced at output, original queue and menu timing retained; other scenes retain native audio"},
    {"audio.effects.title_selection", "Title selection", 23, 1, 1, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Initial title Start/Options selection: MD FM101 at native action calls; verified dry native voice replaced at output; cursor, music and menu navigation behavior independent"},
    {"audio.effects.options_adjustment", "Options adjustment", 23, 1, 1, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Initial title Options value changes: MD FM101 at native adjustment calls; verified dry native voice replaced at output; sound-test playback and cursor behavior independent"},
    {"audio.effects.options_exit", "Leave Options", 23, 1, 1, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Initial title Options return: MD omits a separate effect at the sampled Start return; verified dry native return voice removed at output, original queue retained"},
    {"gameplay.levels.pride_lands.hyena_probe_height", "Hyena walking wall-probe height", 34, 1, 1, TLK_HYENA_PROBE_AVAILABLE, "Pride Lands hyena walking turns: original MD wall probe eight pixels higher; native choice keeps its original height; independent of terrain map, body bounds, artwork and audio; changing this source restarts the level"},
    {"gameplay.levels.pride_lands.hyena_entrance_window", "Hyena entrance countdown window", 34, 1, 1, TLK_HYENA_ENTRANCE_AVAILABLE, "Pride Lands hyena entrance: original MD 320-pixel camera window instead of 256 pixels for countdown updates; native audio synchronization and other AI retained; independent of viewport, camera, terrain, artwork and sound; changing this source restarts the level"},
    {"graphics.pride_final_menu", "Pride Lands Continue / Game Over", 1, 1, 1, TLK_FINAL_MENU_ART_AVAILABLE, "Installed MD menu artwork, palette and animation; final-life controls, duration and audio remain independently selected; other levels retain native menus; changing this source restarts the level"},
    {"graphics.hud.frames.roar", "Roar meter", 18, 1, 0, 1, "Pride Lands, Can't Wait to Be King and Elephant Graveyard original MD roar meter artwork; palette and gameplay remain independent"},
    {"graphics.hud.frames.health", "Health meter", 18, 1, 0, 1, "Pride Lands, Can't Wait to Be King and Elephant Graveyard original MD health meter artwork; palette and gameplay remain independent"},
    {"graphics.hud.frames.lives", "Lives display", 18, 1, 0, 1, "Original MD cub/adult portraits and life digits in reviewed main scenes through Pride Rock; independent palette and gameplay"},
    {"graphics.sprites.animals", "Animals", 2, 0, 0, 0, ""},
    {"graphics.sprites.animals.monkeys", "Monkeys", 2, 0, 0, 0, ""},
    {"graphics.sprites.animals.monkeys.palette", "Palette", 2, 1, 0, 1, "Can't Wait's two live coat palettes and Destiny's prepared monkey colors; independent of artwork and gameplay; native flashes preserved"},
    {"graphics.sprites.animals.ostriches", "Ostriches", 2, 0, 0, 0, ""},
    {"graphics.sprites.animals.hippos", "Hippo ledges", 2, 0, 0, 0, "Moving lips and ears; the large bodies belong to scenery"},
    {"graphics.sprites.animals.hippos.frames", "Frame artwork", 2, 1, 0, 1, "Can't Wait to Be King: original MD drawings and anchors for all14 idle/contact hippo ledge poses; fixes floating native lips with MD platform height. Animation, platform height, contacts, palette and scenery remain independent"},
    {"graphics.sprites.animals.hippos.palette", "Palette", 2, 1, 0, 1, "Can't Wait to Be King: original MD hippo ledge palette1 from the live scene controller; independent of frame artwork, platform height, scenery and other animals; native flashes retained"},
    {"graphics.sprites.animals.ostriches.palette", "Palette", 2, 1, 0, 1, "Can't Wait to Be King: original MD ostrich colors for 12 reviewed shared poses; follows the live scene palette; independent of monkeys, scenery and gameplay; unrecognized/flash palettes retain native colors"},
    {"graphics.sprites.animals.rhinos", "Rhinos", 2, 0, 0, 0, ""},
    {"graphics.sprites.animals.rhinos.frames", "Head artwork", 2, 1, 0, 1, "Can't Wait to Be King: prepared original MD head artwork for 13 native poses, paired in original bounce/idle order; native animation timing and gameplay retained; palette independent"},
    {"graphics.sprites.animals.rhinos.palette", "Head palette", 2, 1, 0, 1, "Can't Wait to Be King: original MD rhino palette1 from the live scene controller; independent of head artwork, monkeys, ostriches and scenery; unknown/flash native palettes retained"},
    {"graphics.sprites.animals.rhinos.tail", "Tail", 2, 0, 0, 0, ""},
    {"graphics.sprites.animals.rhinos.tail.palette", "Palette", 2, 1, 0, 1, "Can't Wait to Be King: original MD rhino tail colors for all 11 reviewed shared poses; prepared/live scene palette1; head, tail motion and other animals remain independent; unknown/flash palettes retain native colors"},
    {"graphics.sprites.enemies.vultures", "Vultures", 10, 0, 0, 0, ""},
    {"graphics.sprites.enemies.vultures.frames", "Frame artwork", 10, 1, 0, 1, "Elephant Graveyard: original MD vulture artwork paired through original animation-family phases; native timing and behavior retained; unknown owners/poses keep native art"},
    {"graphics.sprites.enemies.vultures.palette", "Palette", 10, 1, 0, 1, "Elephant Graveyard: original MD vulture palette3 from its prepared scene; independent of artwork, scenery and hyenas; native flashes preserved"},
    {"graphics.sprites.bones", "Bone platforms", 2, 0, 0, 0, ""},
    {"graphics.sprites.bones.frames", "Frame artwork", 2, 1, 0, 1, "Elephant Graveyard: original MD breakable bone structure and all twelve fragment drawings; other bone drawings retain reviewed shared art. Palette and movement independent"},
    {"graphics.sprites.bones.palette", "Palette", 2, 1, 0, 1, "Elephant Graveyard: original MD colors for reviewed moving, falling and curved tusks, eleven shared bone-jaw drawings and breakable bone structure; drawing and movement independent; native flashes preserved"},
    {"graphics.sprites.mufasa.palette", "Scar farewell palette", 2, 1, 0, 1, "Original MD farewell palette for five shared drawings; independent of timing, scenery and sound. Native flashes and unreviewed poses retain native colors"},
    {"audio.effects.world.cant_wait", "Can't Wait to Be King", 25, 0, 0, 0, ""},
    {"audio.effects.world.cant_wait.rhino", "Rhino bounce", 25, 1, 1, 1, "Original MD FM106 on the rhino's native bounce/launch cue; other animals and gameplay independent; changing audio restarts the level"},
    {"audio.effects.world.simbas_destiny.monkey_movement", "Destiny monkey movement voice", 25, 1, 1, TLK_DESTINY_MONKEY_AVAILABLE, "Original MD semantic cue33 / PCM17 at movement entry; independent of monkey behavior and artwork; restarts the level"},
    {"audio.effects.world.simbas_destiny.monkey_shot", "Destiny monkey projectile", 25, 1, 1, TLK_DESTINY_MONKEY_AVAILABLE, "Original MD FM94 when the projectile is released; independent of monkey behavior and artwork; restarts the level"},
    {"audio.effects.world.simbas_destiny.arena_gate", "Rafiki arena gate", 25, 1, 1, 1, "Original MD opening sound122 after the panther arena is cleared, at the native opening cue; independent of combat, artwork and music; restarts the level"},
    {"audio.effects.world.simbas_destiny.monkey_defeat", "Destiny monkey defeat sound", 25, 1, 1, TLK_DESTINY_MONKEY_AVAILABLE, "Original MD omits the native strike-defeat cue; independent of monkey behavior and artwork; restarts the level"},
    {"audio.effects.world.cant_wait.monkey_contacts", "Monkey catches and throws", 25, 1, 1, 1, "Original MD FM119 on the three reviewed monkey interaction cues; reaction voice and gameplay independent; changing audio restarts the level"},
    {"audio.effects.world.cant_wait.monkey_reaction", "Monkey roar reaction", 25, 1, 1, 1, "Original MD PCM8 after the monkey's existing reaction countdown; SNES voice remains at entry; native monkey behavior unchanged; changing audio restarts the level"},
    {"audio.effects.world.cant_wait.ostrich_steps", "Ostrich running", 25, 1, 1, 1, "Original MD FM94 on the three original running animation markers; SNES is silent; controls and physics independent"},
    {"audio.effects.world.cant_wait.ostrich_jump", "Ostrich jump", 25, 1, 1, 1, "Original MD FM169 once on jump animation entry; SNES is silent; controls and physics independent"},
    {"audio.effects.world.cant_wait.flying_takeoff", "Flying creature take-off", 25, 1, 1, 1, "Original MD PCM5 once at the reviewed flying creature's take-off; independent of monkey voices; SNES is silent"},
    {"audio.effects.world.cant_wait.extra_life", "Extra-life pickup", 25, 1, 1, 1, "Original MD cub PCM15 at the native extra-life pickup; pickup rules unchanged"},
    {"audio.effects.world.cant_wait.bonus", "Bonus-stage pickup", 25, 1, 1, 1, "Original MD PCM15 at the native bonus-stage pickup; bonus rules unchanged"},
    {"audio.effects.world.graveyard", "Elephant Graveyard", 25, 0, 0, 0, ""},
    {"audio.effects.world.graveyard.vulture", "Vulture voice", 25, 1, 1, 1, "Original MD PCM2 on the owned vulture action; artwork, flight and attack rules independent"},
    {"audio.effects.world.graveyard.bone_shake", "Shaking bone release", 25, 1, 1, 1, "Original MD FM105 when the existing bone countdown ends; native sound remains at entry; movement and collapse rules unchanged"},
    {"audio.effects.world.graveyard.bone_platform", "Moving bone release", 25, 1, 1, 1, "Original MD FM127 when the existing platform countdown ends; native sound remains at entry; movement unchanged"},
    {"audio.effects.world.graveyard.bone_break", "Crumbling bones", 25, 1, 1, 1, "Original MD FM105 on the owned bone-break action; physics unchanged"},
    {"audio.effects.world.graveyard.pillar", "Pillar collapse", 25, 1, 1, 1, "Original MD FM171 fall and FM92 impact at the native pillar events; collapse and collision rules unchanged"},
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
    {"gameplay.levels.stampede", "The Stampede", 32, 0, 0, 0, ""},
    {"gameplay.levels.stampede.exit_flow", "Post-Stampede transition", 32, 1, 1, TLK_STAMPEDE_EXIT_AVAILABLE, "Original MD cliff sequence with normal Start skip and natural completion before Exile; illustration and sound selected separately. SNES retains its native cliff sequence; restarts the level"},
    {"gameplay.levels.stampede.movement_bounds", "Movement bounds", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "Original MD left limit40 instead of native32, on the ground and in both jump phases; speed and right limit retained; independent of graphics, enemies and sounds; restarts the level"},
    {"gameplay.levels.stampede.obstacle_lanes", "Obstacle lanes", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "Original MD late rock at update3950 uses lane6 instead of native4; all85 event times/types and the other84 lanes agree; independent of movement and artwork; restarts the level"},
    {"gameplay.levels.stampede.damage", "Collision damage", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "Original MD wildebeest damage3 instead of native1; rocks remain1. Existing invulnerability60 and reaction20 already agree; independent of collision timing, graphics and sound; restarts the level"},
    {"gameplay.levels.stampede.rock_contacts", "Rock contacts", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "Original MD rocks can hit at projection depths9 and10 instead of native8 and9; original sprite intersection and approach animation retained; independent of damage and lane selection; restarts the level"},
    {"gameplay.levels.stampede.rock_perspective", "Rock perspective", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "Original MD rock approach divisor28 instead of native44; outer rocks spread farther from the center, affecting both their visible position and contacts. Original tables, hardware arithmetic, depth updates and Wildebeest projection retained; restarts the level"},
    {"gameplay.levels.stampede.simba_bounds", "Simba running contact boxes", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "Original MD contact boxes for ten reviewed running poses: offset3 right and1 up relative to SNES, before mirroring. Keeps original contacts, positions and artwork independent; unknown poses retain native boxes; restarts the level"},
    {"gameplay.levels.stampede.running_timing", "Run-start animation timing", 32, 1, 1, TLK_STAMPEDE_RULES_AVAILABLE, "MD run start retains the previous draw pose for the first update, matching original one-tap controls and contact shape. Uses the native animation continuation; positions, drawings and health remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard", "Elephant Graveyard", 32, 0, 0, 0, ""},
    {"gameplay.levels.elephant_graveyard.vulture_health", "Patrolling vulture health", 32, 1, 1, 1, "MD: one fewer hit point for patrolling vultures, matching original difficulty+1; other vultures unchanged; level restart"},
    {"gameplay.levels.elephant_graveyard.vulture_turn_point", "Flying vulture turn point", 32, 1, 1, TLK_GRAVEYARD_TURN_AVAILABLE, "Original MD flight turns at cameraX+160 instead of SNES cameraX+128, with the original wing-phase decision and acceleration. Independent of display width, homes, health, contact boxes, artwork and sound; restarts the level"},
    {"gameplay.levels.elephant_graveyard.vulture_launch_timing", "Launching vulture timing", 32, 1, 1, TLK_GRAVEYARD_LAUNCH_AVAILABLE, "MD launch parity gate uses a video-field clock that continues across level loading; SNES starts immediately using its cleared scene clock. Movement, homes, turn point, health, contact boxes, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.vulture_bounds", "Vulture contact boxes", 32, 1, 1, 1, "Original MD collision rectangles for four reviewed vulture poses; independent of artwork, health and sound; prepared during Setup; level restart"},
    {"gameplay.levels.elephant_graveyard.hyena_ground_tags", "Hyena turns and jump approach", 32, 1, 1, 1, "Original MD floor tags for hyena turn and jump decisions; fixes opening-skull convergence; only verified unchanged floor shapes/cells; independent of sprites and sound; level restart"},
    {"gameplay.levels.elephant_graveyard.hyena_wall_probes", "Hyena wall probe height", 32, 1, 1, TLK_GRAVEYARD_WALL_AVAILABLE, "Original MD walking-hyena wall queries eight pixels above the feet; avoids turning at the base of a slope and restores the later jump. Terrain, movement, ground tags, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.ledge_wall_probes", "Ledge-jump wall probes", 32, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "Original MD ledge-jump flag moves wall probes down32 and inward4 pixels, avoiding blocked sideways jumps from bone ledges. Grip points, terrain, artwork and controls remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.grip_points", "Ledge grip points", 32, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "Original MD hand probe points for reviewed cub poses; fixes missed bone ledge grabs. Terrain, body bounds, artwork and controls remain independent; unreviewed poses retain native points; restarts the level"},
    {"gameplay.levels.elephant_graveyard.bug_positions", "Random bug spawn positions", 32, 1, 1, TLK_GRAVEYARD_PICKUPS_AVAILABLE, "Original MD random-bug marker placements. Normal spawning, random type and movement, contacts, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.pickup_positions", "Health and roar pickup positions", 32, 1, 1, TLK_GRAVEYARD_PICKUPS_AVAILABLE, "Original MD placements for two health bugs and one roar bug; ordinary pickup contacts, effects, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.falling_bone_shake", "Falling bone shake motion", 32, 1, 1, TLK_GRAVEYARD_SHAKE_AVAILABLE, "Original MD random vertical shake instead of SNES fixed horizontal motion, using the actual game random draw. Ordinary countdown, falling and artwork remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.falling_bone_support", "Falling bone support retry", 32, 1, 1, TLK_GRAVEYARD_BONE_CONTACT_AVAILABLE && TLK_GRAVEYARD_SHAKE_AVAILABLE, "Original MD ten-update contact delay during falling and after a failed support check, avoiding immediate catches across the chain. Covers all six large bones; small moving pieces, shake, homes, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.streaming_top", "Enemy activation top margin", 32, 1, 1, TLK_STREAMING_TOP_AOT_AVAILABLE, "Original MD six-tile margin above the camera when scanning queued enemies; affects launching vultures during the descent. Initial scan, homes, camera, culling, movement, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.bonus_bug_bounds", "Bonus-bug contact box", 32, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD bonus-bug contact rectangle; normal collection sets the bonus-entry flag. Placement, Simba bounds, artwork, sound and bonus rules stay independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.mufasa_farewell", "Scar farewell timing", 32, 1, 1, TLK_GRAVEYARD_FAREWELL_AVAILABLE, "Original MD farewell sequence retains two additional48-update pose holds and phase2 completion, omitting the native phase3 event. Walk-out, artwork, palette, sound and bonus selection remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.hyena_bounds", "Hyena contact boxes", 32, 1, 1, 1, "Original installed MD collision rectangles for regular and scripted hyenas; independent of artwork, sound and approach; level restart"},
    {"graphics.sprites.simba.cub.graveyard_death_motion", "Graveyard death movement", 4, 1, 1, 1, "Nonfinal cub health death: original MD death artwork sequence and movement from the level position to screen centre; frame artwork, palette and music sources remain independent; native retry and final-life path retained"},
    {"graphics.sprites.simba.cub.king_death_motion", "Can't Wait death movement", 4, 1, 1, 1, "Nonfinal health death moves from the level position to screen centre; artwork, palette and music remain independent"},
    {"graphics.scenery.timon_start_position", "Opening Timon placement", 4, 1, 0, 1, "Original MD opening position after Start; independent of opening artwork, palette, pose timing and voice"},
    {"graphics.sprites.simba.cub.stampede_death_motion", "Stampede death movement", 4, 1, 1, 1, "Nonfinal Stampede death moves the special player actor from its level position to screen centre; artwork, palette and music remain independent"},
    {"graphics.sprites.simba.adult.death_motion", "Adult death movement", 4, 1, 1, 1, "Shared adult nonfinal health-death sequence and movement to screen centre in every adult level; artwork, palette and music remain independent; hazard and final-life paths retained"},
#endif
    {"audio.music.elephant_graveyard.track", "Level track", 20, 1, 1, 1, "Original MD track83; stops for death and returns on retry; changing audio restarts the level"},
    {"audio.music.elephant_graveyard.death", "Health-death cue", 20, 1, 1, 1, "Original shared MD health-death program430; independent of level music; fall death keeps its native stop/retry path; changing audio restarts the level"},
    {"graphics.sprites.stampede", "The Stampede", 2, 0, 0, 0, ""},
    {"graphics.sprites.stampede.wildebeests", "Wildebeests", 2, 0, 0, 0, "All80 observed drawings are shared by the original versions"},
    {"graphics.sprites.stampede.wildebeests.palette", "Palette", 2, 1, 0, 1, "Original MD Wildebeest colors; shared original artwork and native approach patterns"},
    {"graphics.sprites.stampede.rocks", "Rocks", 2, 0, 0, 0, ""},
    {"graphics.sprites.stampede.rocks.frames", "Animation frames", 2, 1, 0, 1, "Reviewed original MD rock drawings; unmapped poses retain native artwork"},
    {"graphics.sprites.stampede.rocks.palette", "Palette", 2, 1, 0, 1, "Original MD rock colors; independent of animation frames"},
    {"graphics.scenery.stampede_palette", "Stampede canyon colors", 14, 1, 0, 1, "Original MD canyon colors; independent of the background choice. Native canyon uses a palette mapping; MD canyon uses original indexed colors"},
    {"graphics.scenery.destiny_face_position", "Destiny sky face position", 14, 1, 0, 1, "Anchor Mufasa's sky face relative to Simba as in MD; SNES keeps its fixed level position. Artwork, animation, palette, sound and level completion stay independently selected"},
    {"audio.effects.world.stampede", "The Stampede", 25, 0, 0, 0, ""},
    {"audio.effects.world.stampede.start", "Stampede rumble", 25, 1, 1, 1, "Original MD FM172 at the native start event"},
    {"audio.effects.world.stampede.hurt", "Simba collision cry", 25, 1, 1, 1, "Original MD PCM16 for Stampede collisions; independent of the shared cub hurt voice"},
    {"audio.effects.world.simbas_exile", "Simba's Exile", 25, 0, 0, 0, ""},
    {"audio.effects.world.simbas_exile.rocks", "Rock rumble and impacts", 25, 1, 1, 1, "Original MD FM165 at the two native rock-controller sound events; native hazards and timing remain independent"},
    {"audio.effects.world.simbas_exile.exit", "Exit sounds", 25, 1, 1, 1, "Original MD outro samples2E0000/2E8000 at matched Simba animation phases, replacing native exit-hyena cues. Music fade follows its independent level-track choice; native movement, Start skip and scene completion retained; restarts the level"},
    {"audio.music.simbas_exile.track", "Level track", 20, 1, 1, 1, "Original MD program258; fades out during the Exile outro and returns on retry; exit sounds independently selected"},
    {"audio.music.simbas_exile.death", "Health-death cue", 20, 1, 1, 1, "Original shared cub MD program430; independent of level music; native retry/final-life logic retained"},
    {"graphics.sprites.simba.cub.exile_death_motion", "Exile death movement", 4, 1, 1, 1, "Nonfinal health death moves Simba toward screen centre; artwork, palette and music remain independent; native fall/final-life paths retained"},
    {"graphics.sprites.enemies.gorilla", "Gorilla", 12, 0, 0, 0, ""},
    {"graphics.sprites.enemies.gorilla.frames", "Frame artwork", 184, 1, 0, 1, "Hakuna Matata: original MD gorilla drawings paired by original action phases; native animation timing and behavior retained; unknown poses use native art"},
    {"graphics.sprites.enemies.gorilla.palette", "Palette", 184, 1, 0, 1, "Prepared original MD gorilla palette3, independent of artwork and scenery; native flashes preserved"},
    {"graphics.sprites.world_objects", "World objects", 2, 0, 0, 0, ""},
    {"graphics.sprites.world_objects.frames", "Frame artwork", 187, 1, 0, 1, "Exile rolling rocks, Hakuna logs, Destiny forest objects, reviewed Be Prepared rocks, Pride Rock fire and rain; native motion/collision and unknown art retained"},
    {"graphics.sprites.world_objects.palette", "Palette", 187, 1, 0, 1, "Original MD colors for reviewed Exile, Hakuna, Destiny, Be Prepared and Pride Rock world objects; independent of scenery and artwork"},
    {"graphics.sprites.animals.monkeys.frames", "Frame artwork", 132, 1, 0, 1, "Reviewed Destiny monkey movement and all twelve shooting drawings; independent timing/behavior; Can't Wait's monkey artwork remains native"},
    {"audio.music.hakuna_matata.track", "Level track", 20, 1, 1, 1, "Original MD program40; returns on retry"},
    {"audio.music.hakuna_matata.death", "Health-death cue", 20, 1, 1, 1, "Original MD program430; independent of level music; native fall/final-life paths retained"},
    {"audio.music.simbas_destiny.track", "Level track", 20, 1, 1, 1, "Original MD program281; returns on retry"},
    {"audio.music.simbas_destiny.death", "Health-death cue", 20, 1, 1, 1, "Original MD adult health-death program430; independent of level music; native fall/final-life paths retained"},
    {"graphics.sprites.simba.cub.hakuna_death_motion", "Hakuna death movement", 4, 1, 1, 1, "Nonfinal cub health death moves Simba from his level position toward screen centre; art, colors and music independent; native fall/final-life paths retained"},
    {"gameplay.levels.hakuna_matata", "Hakuna Matata", 33, 0, 0, 0, ""},
    {"gameplay.levels.hakuna_matata.gorilla_recovery", "Gorilla landing recovery", 33, 1, 1, TLK_ROAR_AOT_AVAILABLE, "Original normal MD landing pause11 updates instead of SNES59; final landing stays59 in both; other AI and artwork remain independent"},
    {"graphics.sprites.enemies.hyenas.adult", "Adult hyenas", 11, 0, 0, 0, "Be Prepared, Simba's Return and Pride Rock; native behavior/timing remain independent"},
    {"graphics.sprites.enemies.hyenas.adult.frames", "Frame artwork", 11, 1, 0, 1, "Original MD adult-hyena drawings paired by corresponding original action phases; ambiguous native poses and flashes remain native"},
    {"graphics.sprites.enemies.hyenas.adult.palette", "Palette", 11, 1, 0, 1, "Reviewed original MD adult-hyena palette3 in Be Prepared, Return and Pride Rock; independent of artwork"},
    {"audio.music.be_prepared.track", "Level track", 20, 1, 1, 1, "Original MD program327; returns on retry"},
    {"audio.music.be_prepared.death", "Health-death cue", 20, 1, 1, 1, "Shared original adult MD health-death program430; native fall/final-life paths retained"},
    {"audio.music.simbas_return.track", "Level track", 20, 1, 1, 1, "Original MD program311; returns on retry"},
    {"audio.music.simbas_return.death", "Health-death cue", 20, 1, 1, 1, "Shared original adult MD health-death program430; native fall/final-life paths retained"},
    {"audio.effects.world.adult_hyenas", "Adult hyenas", 25, 0, 0, 0, "Be Prepared, Return and Pride Rock; voices independent of drawings and gameplay"},
    {"audio.effects.world.adult_hyenas.attack", "Attack voice", 25, 1, 1, 1, "Original MD PCM13 at the corresponding adult-hyena attack event; cub hyena jump remains separate"},
    {"audio.effects.world.adult_hyenas.leap", "Ordinary leap", 25, 1, 1, 1, "Original MD adult hyena ordinary leap is silent; native cry remains available independently of attack, taunt and hurt voices; animation and behavior unchanged"},
    {"audio.effects.world.adult_hyenas.reaction", "Hurt/reaction voice", 25, 1, 1, 1, "Original MD PCM4 at the adult-hyena reaction event; separate from cub hyena voices"},
    {"audio.effects.world.adult_hyenas.taunt", "Taunt voice", 25, 1, 1, TLK_ADULT_HYENA_CULLING_AVAILABLE, "Original MD PCM3/96 once on adult-hyena taunt entry, replacing the later native cue; animation and behavior independent"},
    {"audio.effects.world.scar", "Scar", 25, 0, 0, 0, "Scar voices independent of artwork and combat"},
    {"audio.effects.world.scar.attack", "Attack sounds", 25, 1, 1, 1, "Original MD FM96 at Scar's leap entry and PCM13/80 at the summit attack; combat, artwork and music remain independent"},
    {"audio.effects.world.pride_rock_fire", "Pride Rock fire", 25, 1, 1, 1, "Original MD FM166 at owned Pride Rock fire pulses, including postfight; independent of artwork and music"},
    {"audio.effects.world.be_prepared.rock_impact", "Be Prepared rock impact", 25, 1, 1, 1, "Original MD FM167 when a falling rock hits the floor; movement, placement, contact boxes, artwork and music remain independent"},
    {"audio.effects.world.be_prepared.stalactites", "Be Prepared stalactites", 25, 1, 1, 1, "Original MD wobble and falling sounds; artwork, movement, collisions and music remain independent. Changing audio restarts the level"},
    {"audio.effects.world.be_prepared.geysers", "Be Prepared geysers", 25, 1, 1, 1, "Original MD geyser rumble and stopping impact; native scheduling, movement, collision, artwork and music remain independent. Changing audio restarts the level"},
    {"audio.effects.world.be_prepared.exit_launch", "Be Prepared launch cue", 25, 1, 1, 1, "Original MD omits the SNES warning cue before the final lava launch. Eruption rumble, movement, artwork and music remain independent; changing audio restarts the level"},
    {"audio.effects.world.be_prepared.leaper_defeat", "Jumping enemy defeat", 25, 1, 1, 1, "Original MD jumping enemies have no defeat voice; selects silence instead of the SNES cry. Movement, contacts, artwork and other enemy sounds remain independent; changing audio restarts the level"},
    {"audio.effects.world.lava_bubbles", "Lava bubbles", 25, 1, 1, 1, "Original MD silence for lava bubbles, or native SNES bubbling sound; artwork, animation and placement remain independent. Changing audio restarts the level"},
    {"audio.effects.simba.scar_finish_roar", "Scar finishing roar", 24, 1, 1, TLK_ADULT_ROAR_AVAILABLE, "Original MD adult PCM11/96 on the actual Scar finishing action entry; later native attack cue silenced; combat, movement and animation independent"},
    {"audio.effects.simba.postfight_roars", "Postfight roars", 24, 1, 1, 1, "Original MD PCM11/96 at the two corresponding postfight phases; extra third native voice silenced; animation and ending timing independent"},
    {"gameplay.levels.adult_hyenas", "Adult hyenas", 33, 0, 0, 0, "Be Prepared, Simba's Return and Pride Rock"},
    {"graphics.sprites.enemies.scar", "Scar", 12, 0, 0, 0, "Native combat and animation timing; unknown poses use native art"},
    {"graphics.sprites.enemies.scar.frames", "Frame artwork", 12, 1, 0, 1, "Reviewed original MD Scar drawings in cave and summit encounters; flashes and unknown poses remain native"},
    {"graphics.sprites.enemies.scar.palette", "Palette", 12, 1, 0, 1, "Original MD Scar palette3, independent of scenery and artwork"},
    {"audio.music.pride_rock.track", "Level track", 20, 1, 1, 1, "Original MD program432 in the cave; post-fight/sunrise score is independently selectable"},
    {"audio.music.pride_rock.death", "Health-death cue", 20, 1, 1, 1, "Original shared adult MD program430; cave nonfinal health death only; native retry/fall/final-life paths"},
    {"graphics.sprites.bonus", "Bonus stages", 2, 0, 0, 0, "Introductory cards, counters and unknown effects retain native art"},
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
    {"gameplay.levels.adult_hyenas.bounds", "Contact boxes", 33, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD body rectangles for84 reviewed adult-hyena poses plus seven animation-specific contexts, including direct and paired combat queries; independent of artwork, sound and AI; unknown contexts keep native bounds; restarts the level"},
    {"gameplay.levels.pride_rock", "Pride Rock", 33, 0, 0, 0, ""},
    {"gameplay.levels.pride_rock.scar_bounds", "Scar contact boxes", 33, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD rectangles for56 unambiguous Scar poses in the three encounters; independent of artwork and AI; unknown/flashing poses retain native bounds; restarts the level"},
    {"gameplay.levels.pride_lands.bonus_bug_bounds", "Bonus-bug contact box", 34, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Pride Lands bonus bug: original MD contact rectangle; independent of its position, artwork, palette, sounds and Simba bounds; native bonus selection rules retained; restarts the level"},
    {"gameplay.levels.pride_lands.interlevel_scene", "Completion interlevel scene", 34, 1, 1, TLK_INTERLEVEL_AVAILABLE, "Original MD animated interlevel scene after the first hyena, including its normal Start skip and natural ending; SNES omits the scene; illustration and sound are independent; restarts the level"},
    {"graphics.interlevel", "Interlevel scenes", 1, 0, 0, 0, ""},
    {"graphics.interlevel.pride_lands", "Pride Lands illustration", 1, 1, 0, TLK_INTERLEVEL_AVAILABLE, "Original MD two-plane illustration, palette and animated drawings when the completion interlevel scene is enabled; SNES retains the black completion backdrop; fixed320 canvas, centred/cropped to the chosen viewport"},
    {"graphics.interlevel.stampede", "Post-Stampede cliff illustration", 1, 1, 0, TLK_STAMPEDE_EXIT_AVAILABLE, "Scar's scene after the Stampede. With Genesis scene timing, the available Genesis illustration is shown for either artwork choice; a separate SNES illustration is not yet available here. SNES scene timing keeps the original SNES scene"},
    {"audio.effects.interlevel", "Interlevel scenes", 23, 0, 0, 0, ""},
    {"audio.effects.interlevel.pride_lands", "Pride Lands interlevel sound", 23, 1, 1, TLK_INTERLEVEL_AVAILABLE, "Original MD outgoing music fade and two animation-triggered sample spans when the completion interlevel scene is enabled; the SNES choice keeps native completion audio; restarts the level"},
    {"audio.effects.interlevel.stampede", "Post-Stampede cliff sound", 23, 1, 1, TLK_STAMPEDE_EXIT_AVAILABLE, "Original MD outgoing music fade, cliff speech and skip/completion stops with the MD transition; other audio choices are independent; restarts the level"},
    {"gameplay.bonus", "Bonus stages", 33, 0, 0, 0, ""},
    {"gameplay.bonus.bug_toss", "Bug Toss", 33, 0, 0, 0, ""},
    {"gameplay.bonus.bug_toss.start", "Pumbaa entry position", 33, 1, 1, TLK_INTERLEVEL_AVAILABLE, "Original MD Pumbaa start100/214 instead of native128/218; independent of artwork and movement limits; restarts the level"},
    {"gameplay.bonus.bug_toss.arena", "Movement limits", 33, 1, 1, TLK_BONUS_ARENA_AVAILABLE, "Original MD right margin288 instead of native224 for Pumbaa, thrower Timon and sliding bugs; native six-pixel movement, catches, scoring and timers retained; restarts the level"},
    {"gameplay.bonus.bug_toss.culling_bounds", "Falling bug screen bounds", 33, 1, 1, TLK_BONUS_CULL_AVAILABLE, "Original MD right boundary319 instead of255 and inclusive bottom223; falling bugs remain active across the wider arena and through the original bottom edge. Movement, catches, timing, artwork and result sequence independent; restarts the level"},
    {"gameplay.scene_random_state", "Random state between stages", 33, 1, 1, TLK_RNG_ENTRY_STAGED_AVAILABLE, "Original MD normal entry for stages1-13: preserve the incoming random stream during actor setup, then reset to the prepared gameplay seed; initial Pride seed and checkpoint resumes are separate; restarts the level"},
    {"gameplay.bonus.bug_toss.reward_eligibility", "Special bug eligibility", 33, 1, 1, TLK_BONUS_TOSS_REWARDS_AVAILABLE, "Original MD keeps special life/continue bugs unless the respective count equals9; SNES eligibility is independent. Chooser random stream, spawn, shared award caps, artwork and sound remain separate; restarts the level"},
    {"gameplay.bonus.bug_toss.result_flow", "Result sequence", 33, 1, 1, TLK_BONUS_RESULT_AVAILABLE, "Original MD round-completion audio/fades, separate result card, animated count and input ownership; artwork and voice independent; restarts the level"},
    {"gameplay.bonus.bug_hunt", "Bug Hunt", 33, 0, 0, 0, "Shared floor geometry; entry, placement, timer and reward choices are independent; catches retain native behavior"},
    {"gameplay.bonus.round_selection", "Bonus round selection", 33, 1, 1, TLK_BONUS_SELECTION_AVAILABLE, "MD selects the Bug Hunt layout from the completed level; SNES chooses randomly. Bonus collection, layouts, movement, timers and rewards remain independent; restarts the level"},
    {"gameplay.bonus.bug_hunt.start", "Entry positions", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "Original MD starting spots in all three Hunts; independent of artwork, object placements and rewards; restarts the level"},
    {"gameplay.bonus.bug_hunt.clock_start", "Clock startup", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "Original MD clock starts immediately during the opening banner, instead of waiting130 native updates; Timon accepts input in both versions; timer length, caption artwork and duration, sounds and rewards independent; restarts the level"},
    {"gameplay.bonus.bug_hunt.timer", "Round timer", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "Original MD30-count clock, initial subcounter0 and51-update ticks instead of native40 and61-update ticks; intro, movement, catches and rewards independent; restarts the level"},
    {"gameplay.bonus.bug_hunt.rewards", "Reward cycle", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "Original MD alternating extra life and continue per10 catches; no SNES max-health upgrade after40; equivalent total-life and continue caps retained; sound, timer and catches independent; restarts the level"},
    {"gameplay.bonus.bug_hunt.bug_bounds", "Bug contact areas", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "Original MD contact areas for collectible and harmful Hunt bugs; independent of Timon's shared body bounds, artwork, sounds, timer and rewards; restarts the level"},
    {"gameplay.bonus.bug_hunt.draw_bounds", "Bug drawing window", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "MD Hunt bug visibility across the selected viewport; SNES retains its native 256-pixel drawing window. Camera, activation, contacts, artwork, sounds, timer and rewards remain independent; restarts the level"},
    {"gameplay.bonus.bug_hunt.placements1", "Bug Hunt 1 object placements", 33, 1, 1, TLK_BONUS_HUNT_AVAILABLE, "Original MD moved and additional objects in Bug Hunt1; Hunt2/3 placements already agree in the shared world; original activation and reward rules retained; restarts the level"},
    {"graphics.bonus_results", "Bonus result card", 1, 1, 0, TLK_BONUS_RESULT_AVAILABLE, "Original MD Bugs Collected artwork/digits or native Bugs Caught font during the MD result sequence; centred in the selected viewport"},
    {"audio.effects.bonus", "Bonus stages", 23, 0, 0, 0, ""},
    {"audio.effects.bonus.toss_rewards", "Bug Toss special rewards", 23, 1, 1, 1, "Original MD voice15 for extra-life/continue bugs and FM98 for health rewards; independent of eligibility, common catch sounds, music and artwork"},
    {"audio.effects.bonus.toss_chew", "Pumbaa burp", 23, 1, 1, 1, "Original MD voice12 on Pumbaa burp input; independent of catch sounds, special rewards, music, animation and gameplay"},
    {"audio.effects.bonus.toss_collect", "Bug Toss catches", 23, 1, 1, 1, "Original MD FM93 on each caught falling bug; independent of music, special-reward sounds, artwork and scoring"},
    {"audio.effects.bonus.hunt_collect", "Bug Hunt catches", 23, 1, 1, 1, "Original MD FM93 on collected Hunt bugs; independent of music, artwork, catches and scoring"},
    {"audio.effects.bonus.hunt_hurt", "Bug Hunt harmful bugs", 23, 1, 1, 1, "Original MD FM117 on harmful Hunt bug contacts; independent of Timon movement, damage and round ending"},
    {"audio.effects.bonus.result_voice", "Result voice", 23, 1, 1, TLK_BONUS_RESULT_AVAILABLE, "Choose Pumbaa's result speech. SNES speaks from20 bugs; Genesis speaks above20. Independent of the result caption and counting rules; restarts the level"},
    {"gameplay.levels.cant_wait", "Can't Wait to Be King", 33, 0, 0, 0, ""},
    {"gameplay.levels.cant_wait.sunrise_timing", "Sunrise transition", 33, 1, 0, 1, "SNES changes the scenery colours at once when Simba leaves the starting branch. Genesis blends them gradually. Scenery colours and sprite colours are separate choices."},
    {"gameplay.levels.cant_wait.rhino_bounds", "Rhino body contact bounds", 33, 1, 1, TLK_CANT_WAIT_RHINO_AVAILABLE, "Original MD rhino body rectangles and inclusive contact edges; Simba bounds, tail catches, bounce physics, artwork and sound independent; restarts the level"},
    {"gameplay.levels.cant_wait.hippo_height", "Hippo platform height", 33, 1, 1, TLK_CANT_WAIT_HIPPO_AVAILABLE, "Original MD hippo base height; SNES adds twelve pixels at initialization; animation, artwork and other animals independent; restarts the level"},
    {"gameplay.levels.cant_wait.hippo_positions", "Hippo positions", 33, 1, 1, 1, "Original MD final hippo16 pixels left of the native placement; the other three agree. Uses the installed original marker grids and normal actor spawn; independent of platform height, artwork, animation and contacts; restarts the level"},
    {"gameplay.levels.cant_wait.terrain", "Terrain layout and floor shapes", 33, 1, 1, TLK_CANT_WAIT_TERRAIN_AVAILABLE, "Original MD terrain contacts and floor shapes; independent of scenery, animal bounds and ride scripts; restarts the level"},
    {"gameplay.levels.cant_wait.ostrich_obstacles", "Ostrich ride script", 33, 1, 1, TLK_CANT_WAIT_OSTRICH_AVAILABLE, "Original MD second-ride obstacle sequence, both rides' spawn distance and jump/duck warning delay; first-ride events agree; camera, body bounds, art and sound independent; restarts the level"},
    {"gameplay.levels.cant_wait.giraffe_platforms", "Giraffe head platform positions", 33, 1, 1, TLK_CANT_WAIT_GIRAFFE_AVAILABLE, "Original MD flat giraffe head collision placement; SNES adds six pixels at initialization; art and animation independent; restarts the level"},
    {"gameplay.levels.cant_wait.rhino_tail_bounds", "Rhino tail catch region", 33, 1, 1, TLK_CANT_WAIT_TAIL_AVAILABLE, "Original MD tail pose rectangles and inclusive catch edges; player probe, tail animation, cooldown and launch behavior remain independent; restarts the level"},
    {"gameplay.levels.cant_wait.start", "Entry position", 33, 1, 1, TLK_CANT_WAIT_TAIL_AVAILABLE, "Original MD normal entry67/387 instead of native66/389, prepared from the level descriptors; checkpoint resumes keep their stored position; restarts the level"},
    {"gameplay.levels.cant_wait.monkey_roar_range", "Monkey roar range", 33, 1, 1, TLK_CANT_WAIT_ROAR_AVAILABLE, "Original MD monkey roar range90 instead of native80 on both axes; original turns and target graph keep running; sound and frame artwork independent; restarts the level"},
    {"graphics.ending_sunrise", "Ending sunrise illustration", 1, 1, 0, TLK_INTERLEVEL_AVAILABLE, "Original MD320-pixel two-plane sunrise, colors and adult Simba drawings; native animation cues and fades retained; ending timing and audio independent; unknown poses use native art; other ending scenes and credits independent"},
    {"audio.voices.ending", "Ending speech", 26, 1, 1, TLK_INTERLEVEL_AVAILABLE, "Original MD two speech clips at the selected sunrise flow cues; native effects switch retained; independent of illustration and credits music; restarts the level"},
    {"audio.voices.opening_timon", "Opening Timon speech", 26, 1, 1, 1, "Original MD opening recording at the native speech cue; native artwork and animation retained; independent of opening placement and music; effects switch retained; restarts the scene"},
    {"audio.music.ending_credits", "Ending credits", 20, 1, 1, 1, "Original MD program61 when credits initialization completes; native music switch, credits loader and scrolling retained; ending timing independent; independent of sunrise speech/artwork; restarts the level"},
    {"audio.music.pride_rock.finale", "After Scar / sunrise", 20, 1, 1, 1, "Original MD finale program339 at the owned native post-fight music boundary, continuing naturally into sunrise until speech; ending timing and FX, speech and credits choices are independently selectable; restarts the level"},
    {"gameplay.levels.pride_rock.ending_timing", "Postfight / ending timing", 33, 1, 1, 1, "Original MD postfight waits and two-roar phase sequence, NTSC finale clock, speech spacing, title cue and waits before credits loading; independent of music, voices and artwork. Native movement and credits loader remain; restarts the level"},
    {"graphics.ending_title", "Sunrise title overlay", 1, 1, 0, TLK_INTERLEVEL_AVAILABLE, "Original MD static title over either sunrise illustration, during the selected MD ending waits; independent of background, speech and impact audio; SNES ending timing has no matching sunrise title interval"},
    {"audio.effects.ending_title", "Sunrise title impact", 23, 1, 1, 1, "Original MD selector2/program165 once at the selected MD ending title cue,201 updates after speech2; native effects switch retained; independent of title/illustration artwork and speech clips; SNES ending timing has no corresponding cue; restarts the level"},
    {"gameplay.levels.cant_wait.monkey_grips", "Monkey hold / throw points", 33, 1, 1, TLK_CANT_WAIT_GRIP_AVAILABLE, "Original MD hand points for29 reviewed monkey drawings, including reflected horizontal points; fixes earlier throw alignment that can cause a later edge jump to miss. Body contact, roar range, artwork and sound remain independent; restarts the level"},
    {"graphics.ending_credits", "Ending credits text", 1, 1, 0, TLK_INTERLEVEL_AVAILABLE, "Original MD320-wide credits font, names, palette, layout and one-pixel-per-three-update scrolling;256 viewport crops the outer columns. Native final hold/fade/exit retained; independent of ending speech/timing/title and credits music"},
    {"gameplay.bonus.bug_hunt.movement_profile", "Timon movement profile", 33, 1, 1, TLK_HUNT_MOTION_AVAILABLE, "Original MD Timon running, air control and gravity profile in all three Hunts; original movement and contact code retained; independent of entries, bug contact areas, timer, rewards, artwork and sounds; restarts the level"},
    {"gameplay.levels.cant_wait.exit_boundary", "Level completion boundary", 33, 1, 1, TLK_CANT_WAIT_EXIT_AVAILABLE, "Original MD King completion boundary6360 instead of native6372; retains the ordinary completion and bonus flow; independent of terrain, monkey throws, artwork, sound and bonus movement; restarts the level"},
    {"gameplay.levels.elephant_graveyard.start", "Entry position", 32, 1, 1, TLK_GRAVEYARD_ENTRY_AVAILABLE, "Original MD normal entry981/0 instead of native1008/336; Simba falls into the opening skull from above; checkpoint resumes keep their stored position; independent of enemies, graphics and sound; restarts the level"},
    {"gameplay.levels.elephant_graveyard.entry_input_delay", "Entry control delay", 32, 1, 1, TLK_GRAVEYARD_INPUT_DELAY_AVAILABLE, "Original MD100-update input countdown on a fresh Graveyard entry, keeping Simba falling straight into the opening skull; native countdown and input handling retained; checkpoint entries unchanged; independent of entry position, enemies, art and sound; restarts the level"},
    {"gameplay.levels.elephant_graveyard.opening_skull_trigger", "Opening skull reveal trigger", 32, 1, 1, TLK_GRAVEYARD_REVEAL_MARKER_AVAILABLE, "Original MD hidden reveal marker1008/208 instead of native976/432; controls when skull hyenas appear and Simba is released from the entry wait; native contact, reveal countdown and spawns retained; independent of entry position/delay, hyena behavior, art and sound; restarts the level"},
    {"gameplay.levels.elephant_graveyard.control_handoff", "Skull reveal control handoff", 32, 1, 1, TLK_GRAVEYARD_CONTROL_HANDOFF_AVAILABLE, "Original MD keeps the remaining input countdown when Simba leaves the skull-reveal crouch; SNES clears it early. Native action/animation handoff stays; independent of trigger placement, entry delay, art and sound; restarts the level"},
    {"gameplay.levels.elephant_graveyard.entry_input_filter", "Direction controls during lock", 32, 1, 1, TLK_GRAVEYARD_INPUT_FILTER_AVAILABLE, "Original MD idle/braking direction checks honor the input countdown; SNES uses raw Left and Right in two queries. Existing wall contacts and raw input stay; independent of skull trigger, countdown duration, art and sound; Graveyard only; restarts the level"},
    {"gameplay.levels.elephant_graveyard.bone_bridge_positions", "Moving-bone bridge positions", 32, 1, 1, TLK_GRAVEYARD_BONE_MARKERS_AVAILABLE, "Original MD four-piece bridge16 pixels left of the SNES placement; the other eight bone-piece markers agree. Native movement, crumble, contacts and geometry stay; independent of art, sounds and skull trigger; restarts the level"},
    {"gameplay.levels.elephant_graveyard.bone_contact", "Moving-bone platform contact", 32, 1, 1, TLK_GRAVEYARD_BONE_CONTACT_AVAILABLE, "Original MD contact rectangles, surface heights and failed-support retry delay for all four moving-bone pieces; native support, crumble and player movement retained. Independent of bridge placement, artwork and sound; restarts the level"},
    {"gameplay.levels.elephant_graveyard.ceiling_rows", "Ceiling row checks", 32, 1, 1, TLK_TERRAIN_AOT_AVAILABLE, "Original MD lower-row ceiling decision instead of native upper/lower checks; preserves higher jumps under the Graveyard bones. Terrain attributes, pose clearance, art and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.upper_bone_position", "Upper falling-bone placement", 32, 1, 1, TLK_GRAVEYARD_PICKUPS_AVAILABLE, "Original MD adds a falling bone at3648/64, supporting the upper route. Normal initialization, shake, falling, contacts, artwork and sound remain independently selected; restarts the level"},
    {"gameplay.levels.elephant_graveyard.upper_vulture_positions", "Upper patrolling vulture positions", 32, 1, 1, TLK_GRAVEYARD_PICKUPS_AVAILABLE, "Original MD patrol home3216/192 instead of3136/128; the other special patrol home1936/368 agrees. Activation, health, behavior, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.perched_vulture_positions", "Perched vulture home positions", 32, 1, 1, TLK_GRAVEYARD_PICKUPS_AVAILABLE, "Original MD omits the extra perched vulture at2928/672 and moves the last one to3712/688 instead of704; two other perched homes agree. Ordinary activation, behavior, contacts, artwork and sound remain independent; restarts the level"},
    {"gameplay.levels.elephant_graveyard.vulture_positions", "Flying vulture home positions", 32, 1, 1, TLK_GRAVEYARD_VULTURE_MARKERS_AVAILABLE, "Original MD flying-vulture home at2016/656 instead of native2000/656; four other vulture markers agree. Native pursuit, dive, contact and damage flow retained; independent of vulture art, sound and other gameplay; restarts the level"},
    {"gameplay.levels.simbas_exile", "Simba's Exile", 33, 0, 0, 0, ""},
    {"gameplay.levels.simbas_exile.culling_bounds", "Enemy lifetime at lower edge", 33, 1, 1, TLK_BONUS_CULL_AVAILABLE, "Original MD inclusive lower activation boundary for ordinary Exile enemies; avoids early removal and respawning. Independent of activation, placements, camera, artwork and sound; restarts the level"},
    {"gameplay.levels.simbas_exile.leaves", "Falling leaves", 33, 1, 1, TLK_LEAVES_AOT_AVAILABLE, "Original MD three-leaf burst and lower gravity in Exile; shared six-leaf cap. Independent of Pride Lands leaves, artwork and sound; restarts the level"},
    {"gameplay.levels.simbas_exile.falling_rock_bounds", "Falling-rock collision boxes", 33, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD contact rectangles for three paired falling-rock poses; independent of terrain, artwork and sound; restarts the level"},
    {"gameplay.levels.stampede.camera_shake", "Post-bonus camera shake", 32, 1, 1, TLK_STAMPEDE_SHAKE_AVAILABLE, "Original MD shake clipping on entry from Bug Toss; affects visible shake and wildebeest decisions. Other entry routes retain native clipping; restarts the level"},
    {"gameplay.levels.simbas_destiny", "Simba's Destiny", 33, 0, 0, 0, ""},
    {"gameplay.levels.be_prepared", "Be Prepared", 33, 0, 0, 0, ""},
    {"gameplay.levels.simbas_return", "Simba's Return", 33, 0, 0, 0, ""},
    {"gameplay.levels.simbas_exile.start", "Entry position", 33, 1, 1, TLK_LATE_ENTRY_AVAILABLE, "Original MD normal-entry world coordinates, prepared from the level descriptors and verified at original gameplay readiness; collected checkpoints keep their stored position. Terrain, enemies, art and sound remain independent; restarts the level"},
#ifndef TLK_EXILE_GRIP_AVAILABLE
#define TLK_EXILE_GRIP_AVAILABLE 0
#endif
    {"gameplay.levels.simbas_exile.grip_points", "Ledge grip points", 33, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "Original MD probe points for reviewed cub poses; avoids grabbing the wrong ledge during the opening descent. Terrain, artwork and controls remain independent; unknown poses retain native points; restarts the level"},
    {"gameplay.levels.simbas_exile.ledge_wall_probes", "Ledge-jump wall probes", 33, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "Original MD wall probes recognize the ledge-jump flag and shift down32 and inward4 pixels during the jump; independent of grip points, terrain and artwork; restarts the level"},
    {"gameplay.levels.simbas_exile.ceiling_rows", "Ceiling row checks", 33, 1, 1, TLK_TERRAIN_AOT_AVAILABLE, "Original MD lower-row ceiling decision for Simba in Exile; preserves jump clearance under overhangs. Terrain, pose clearance and artwork remain independent; restarts the level"},
    {"gameplay.levels.simbas_exile.ceiling_clearance", "Ceiling pose clearance", 33, 1, 1, TLK_TERRAIN_AOT_AVAILABLE && TLK_HITBOX_AOT_AVAILABLE, "Original MD pose-top word for Simba's ceiling probe in Exile; unknown poses retain native clearance. Independent of ceiling-row rules, terrain and artwork; restarts the level"},
    {"gameplay.levels.simbas_exile.terrain", "Terrain layout and floor shapes", 33, 1, 1, TLK_EXILE_TERRAIN_AVAILABLE, "Original MD collision attributes and floor profiles for Exile; removes native-only ledges and follows the original slopes. Independent of scenery, camera, grip points and enemy rules; restarts the level"},
    {"gameplay.levels.simbas_exile.exit_start_skip", "Exit scene Start skip", 33, 1, 1, TLK_EXILE_EXIT_AVAILABLE, "Original MD held Start can finish Exile's exit scene after its first phase; keeps the ordinary level completion and bonus flow. Independent of movement, artwork and sound; restarts the level"},
    {"gameplay.levels.simbas_exile.outro_holds", "Exit animation end holds", 33, 1, 1, TLK_EXILE_EXIT_AVAILABLE, "Original MD final holds30/80/100 before normal phase completion; retains time for the full independently selected outro sounds. Start skipping, colors, sounds and music independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.start", "Entry position", 33, 1, 1, TLK_LATE_ENTRY_AVAILABLE, "Original MD normal-entry world coordinates, prepared from the level descriptors and verified at original gameplay readiness; collected checkpoints keep their stored position. Terrain, enemies, art and sound remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.terrain", "Terrain layout and floor shapes", 33, 1, 1, TLK_HAKUNA_TERRAIN_AVAILABLE, "Original MD collision attributes and floor profiles for Hakuna Matata, including the opening slide and stream-edge slopes. Independent of scenery, camera and movement rules; restarts the level"},
    {"gameplay.levels.hakuna_matata.retry_controls", "Controls after restarting", 33, 1, 1, TLK_HAKUNA_RETRY_AVAILABLE, "Original MD brief control filter after a death/restart rebuild; normal level entry is unchanged. Independent of terrain, camera, artwork and sound; restarts the level"},
    {"gameplay.levels.hakuna_matata.spider_positions", "Spider placements", 33, 1, 1, TLK_HAKUNA_SPIDERS_AVAILABLE, "All fifteen original MD spider homes, including additional placements; native registration, activation and AI retained. Independent of terrain, camera, artwork and sound; restarts the level"},
#ifndef TLK_HAKUNA_POISON_AVAILABLE
#define TLK_HAKUNA_POISON_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_CHECKPOINT_AVAILABLE
#define TLK_HAKUNA_CHECKPOINT_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_LOG_CONTINUITY_AVAILABLE
#define TLK_HAKUNA_LOG_CONTINUITY_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_ARENA_AVAILABLE
#define TLK_HAKUNA_ARENA_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_LOGS_AVAILABLE
#define TLK_HAKUNA_LOGS_AVAILABLE 0
#endif
#ifndef TLK_HAKUNA_FATAL_AVAILABLE
#define TLK_HAKUNA_FATAL_AVAILABLE 0
#endif
    {"gameplay.levels.hakuna_matata.fatal_contact_handling", "Fatal contact handling", 33, 1, 1, TLK_HAKUNA_FATAL_AVAILABLE, "MD checks fatal damage after actor updates before the next control read; native death/rebuild routines and retry delay retained. Damage, enemy contact and checkpoint positions independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.log_continuity", "Log activation and reset", 33, 1, 1, TLK_HAKUNA_LOG_CONTINUITY_AVAILABLE, "Original MD waterfall log lifetime across gaps between active spawners. Placements, terrain, art and sound remain independent; restarts the level"},
#ifndef TLK_HAKUNA_BONUS_AVAILABLE
#define TLK_HAKUNA_BONUS_AVAILABLE 0
#endif
    {"gameplay.levels.hakuna_matata.bonus_bug_bounds", "Bonus-bug contact box", 33, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD bonus-bug contact rectangle; normal collection selects the bonus. Placement, artwork, palette and sound stay independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.bonus_bug_positions", "Bonus-bug placement", 33, 1, 1, TLK_HAKUNA_BONUS_AVAILABLE, "Original MD bonus bug at2048/240, absent in SNES; normal contact and collection decide bonus entry. Bounds, artwork, sound and other placements independent; restarts the level"},
#ifndef TLK_DESTINY_BOULDER_AVAILABLE
#define TLK_DESTINY_BOULDER_AVAILABLE 0
#endif
    {"gameplay.levels.simbas_destiny.obstacle_positions", "Obstacle placements", 33, 1, 1, TLK_DESTINY_OBSTACLES_AVAILABLE, "Original MD homes and segment types for Destiny obstacle columns and stacks, markers108 through114. Normal streaming, activation and destruction retained; body bounds, other actors, terrain and artwork independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.terrain", "Terrain layout and floor shapes", 33, 1, 1, TLK_DESTINY_TERRAIN_AVAILABLE, "Original MD collision attributes and floor profiles for Destiny; removes native-only ledges and follows original slopes. Scenery, obstacle contact, artwork and controls remain independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.exit_start_skip", "Exit scene Start skip", 33, 1, 1, TLK_DESTINY_EXIT_AVAILABLE, "Original MD held Start skips the completion caption and continues through the ordinary bonus/next-level loader. Countdown, placement, artwork and audio independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.monkey_behavior", "Monkey attack and movement", 33, 1, 1, TLK_DESTINY_MONKEY_AVAILABLE, "Original MD idle countdown, shooting, turning/movement and stopping cycle. Normal strikes, projectiles, gravity and enemy lifetime retained; artwork, palette and sounds independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.monkey_positions", "Monkey placements", 33, 1, 1, TLK_DESTINY_OBSTACLES_AVAILABLE, "Original MD19 monkey homes instead of SNES13, including moved and additional monkeys. Normal registration, streaming and combat retained; attack/movement, obstacle placements, artwork and terrain independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.arena_barrier", "Arena barrier", 33, 1, 1, TLK_DESTINY_ARENA_AVAILABLE, "Original MD arena controller blocks from80 pixels on the right instead of SNES40; left and vertical limits unchanged. Normal blocking, enemy spawning and fight progression retained; artwork, terrain, hyena behavior and bounds independent; restarts the level"},
    {"gameplay.simba.adult_roar", "Adult roar timing", 28, 1, 1, TLK_ADULT_ROAR_AVAILABLE, "Original MD adult roar takes effect at counter30 instead of SNES38; original strength, charge, duration and enemy reactions retained. Artwork and sound source remain independent; restarts the level"},
    {"gameplay.simba.adult_ceiling_rows", "Adult ceiling collision", 28, 1, 1, TLK_TERRAIN_AOT_AVAILABLE && TLK_HITBOX_AOT_AVAILABLE, "Original MD reviewed pose-top clearance and lower-row ceiling checks for adult Simba in Destiny through Pride Rock. Unknown poses retain native clearance; terrain, body contacts, artwork and controls remain independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.boulder_surface", "Stationary boulder support surface", 33, 1, 1, TLK_DESTINY_ROCK_SURFACE_AVAILABLE, "Original MD standing surface extends from -3 to55 rather than SNES4 to48. Normal support, stepping and jumping retained; boulder homes, side-contact box, terrain and artwork independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.boulder_positions", "Boulder and release-trigger placements", 33, 1, 1, TLK_DESTINY_ROCK_POSITIONS_AVAILABLE, "Original MD homes for all six Destiny boulders and their four linked release triggers. Keeps normal coordinate-based linking, release, support and streaming; terrain, contact box and artwork independent; restarts the level"},
    {"gameplay.levels.simbas_destiny.boulder_contact", "Stationary boulder contact", 33, 1, 1, TLK_DESTINY_BOULDER_AVAILABLE, "Original MD stationary-boulder rectangle top+8 instead of SNES-2. Normal contact and pushing retained; placement, artwork, sound and other obstacles independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.gorilla_defeat_pauses", "Gorilla defeat pauses", 33, 1, 1, TLK_ROAR_AOT_AVAILABLE, "Original MD defeat holds99 and89 instead of SNES119+35 and34; original animation parser, motion and completion retained. Artwork, sound and other boss behavior independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.gorilla_initialization", "Gorilla initialization", 33, 1, 1, TLK_HAKUNA_INITIALIZATION_AVAILABLE, "Original MD gorilla initializes when created, before its first ordinary update; uses the native initializer and normal timer, movement and contact routines. Placements, bounds, art and sound independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.coconut_lifetime", "Coconut screen lifetime", 33, 1, 1, TLK_HYENA_ENTRANCE_AVAILABLE, "Original MD320-pixel horizontal lifetime viewport instead of SNES256, with the original128-pixel margin. Keeps thrown coconuts alive to enter the view; normal motion, bounces and destruction retained. Artwork, sounds and other actors independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.gorilla_bounds", "Gorilla body bounds", 33, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD body rectangles for reviewed gorilla action poses; unknown poses retain native bounds. Placements, AI, art and sound remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.gorilla_arena_positions", "Gorilla arena placements", 33, 1, 1, TLK_HAKUNA_ARENA_AVAILABLE, "Original MD gorilla home and nearby visibility-marker homes, selected together where their source cells overlap. Boss behavior, terrain, art and sound remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.log_positions", "Log placements", 33, 1, 1, TLK_HAKUNA_LOGS_AVAILABLE, "All original MD log-generator homes; ordinary log spawning, motion and landing retained. Other enemies, terrain and artwork remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.checkpoint_positions", "Checkpoint placements", 33, 1, 1, TLK_HAKUNA_CHECKPOINT_AVAILABLE, "Both original MD checkpoint homes. Normal contact, checkpoint storage and restart code retained; other placements, controls and artwork independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.poison_bug_bounds", "Poisonous bug body bounds", 33, 1, 1, TLK_HITBOX_AOT_AVAILABLE, "Original MD contact rectangle for mapped poisonous bug poses. Placements, damage, artwork and sound stay independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.poison_bug_positions", "Poisonous bug placements", 33, 1, 1, TLK_HAKUNA_POISON_AVAILABLE, "All five original MD poisonous bug homes; native contact damage and removal preserved. Other enemy families, terrain, art and sound remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.ceiling_clearance", "Ceiling pose clearance", 33, 1, 1, TLK_TERRAIN_AOT_AVAILABLE && TLK_HITBOX_AOT_AVAILABLE, "Original MD pose-top word for Simba's ceiling probe; unknown poses retain native clearance. Terrain, row rules, body bounds and artwork remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.ceiling_rows", "Ceiling row checks", 33, 1, 1, TLK_TERRAIN_AOT_AVAILABLE, "Original MD lower-row ceiling decision for Simba in Hakuna; preserves jumps under overhangs. Terrain, pose clearance and artwork remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.ledge_wall_probes", "Ledge-jump wall probes", 33, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "MD wall probes recognize ledge-jump state and shift down32 and inward4 pixels; terrain, grip points and artwork stay independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.grip_points", "Ledge grip points", 33, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "Original MD hand probe points for reviewed cub poses; fixes missed ledge grabs. Terrain, artwork and controls remain independent; unknown poses retain native points; restarts the level"},
    {"gameplay.levels.hakuna_matata.streaming_top", "Enemy activation top margin", 33, 1, 1, TLK_STREAMING_TOP_AOT_AVAILABLE, "MD six-tile margin above the camera when streaming enemies; fixes early frog reactivation. Initial scan, placements, movement and culling remain independent; restarts the level"},
    {"gameplay.levels.hakuna_matata.frog_positions", "Frog placements", 33, 1, 1, TLK_HAKUNA_FROGS_AVAILABLE, "All nine original MD frog homes; native registration, activation and AI retained. Independent of spiders, terrain, camera, artwork and sound; restarts the level"},
    {"gameplay.levels.hakuna_matata.spider_initialization", "Spider initialization", 33, 1, 1, TLK_HAKUNA_INITIALIZATION_AVAILABLE, "Original MD spiders are initialized when spawned, before their first ordinary update; uses the native initializer for initial, streamed and restarted spawns. Independent of placements, camera, artwork and sound; restarts the level"},
    {"gameplay.levels.simbas_destiny.start", "Entry position", 33, 1, 1, TLK_LATE_ENTRY_AVAILABLE, "Original MD normal-entry world coordinates, prepared from the level descriptors and verified at original gameplay readiness; collected checkpoints keep their stored position. Terrain, enemies, art and sound remain independent; restarts the level"},
    {"gameplay.levels.be_prepared.retry_controls", "Controls after restarting", 33, 1, 1, TLK_BE_PREPARED_RETRY_AVAILABLE, "Original MD brief control filter after a death/restart rebuild; normal entry is unchanged. Independent of terrain, artwork, sound and other levels; restarts the level"},
    {"gameplay.levels.be_prepared.terrain", "Terrain collision", 33, 1, 1, TLK_BE_PREPARED_TERRAIN_AVAILABLE, "Original MD terrain tags, ledges and height profiles; ordinary native floor, wall and ledge decisions remain. Independent of object placements, graphics and sound; restarts the level"},
    {"gameplay.levels.be_prepared.rock_positions", "Falling rock placements", 33, 1, 1, TLK_BE_PREPARED_ROCKS_AVAILABLE, "Original MD removed and moved falling rocks. Their ordinary constructors, random delay, attacks and contacts remain; independent of terrain, art and audio; restarts the level"},
    {"gameplay.levels.be_prepared.start", "Entry position", 33, 1, 1, TLK_LATE_ENTRY_AVAILABLE, "Original MD normal-entry world coordinates, prepared from the level descriptors and verified at original gameplay readiness; collected checkpoints keep their stored position. Terrain, enemies, art and sound remain independent; restarts the level"},
    {"gameplay.levels.simbas_return.start", "Entry position", 33, 1, 1, TLK_LATE_ENTRY_AVAILABLE, "Original MD normal-entry world coordinates, prepared from the level descriptors and verified at original gameplay readiness; collected checkpoints keep their stored position. Terrain, enemies, art and sound remain independent; restarts the level"},
    {"gameplay.levels.pride_rock.start", "Entry position", 33, 1, 1, TLK_LATE_ENTRY_AVAILABLE, "Original MD normal-entry world coordinates, prepared from the level descriptors and verified at original gameplay readiness; collected checkpoints keep their stored position. Terrain, enemies, art and sound remain independent; restarts the level"},
    {"gameplay.levels.simbas_return.terrain", "Terrain collision", 33, 1, 1, TLK_LATE_LAYOUT_AVAILABLE, "Original terrain tags and height profiles; independent of placements, graphics and sound. Restarts the level"},
    {"gameplay.levels.simbas_return.pickup_positions", "Pickup placements", 33, 1, 1, TLK_LATE_LAYOUT_AVAILABLE, "Original pickup locations; independent of terrain, enemies, graphics and sound. Restarts the level"},
    {"gameplay.levels.pride_rock.terrain", "Terrain collision", 33, 1, 1, TLK_LATE_LAYOUT_AVAILABLE, "Original terrain tags and height profiles; independent of placements, graphics and sound. Restarts the level"},
    {"gameplay.levels.pride_rock.object_positions", "Object placements", 33, 1, 1, TLK_LATE_LAYOUT_AVAILABLE, "Original Scar, hyena and other level object locations; behavior, terrain, graphics and sound stay independent. Restarts the level"},
    {"gameplay.levels.pride_rock.scar_contact_response", "Scar contact response", 33, 1, 1, TLK_SCAR_CONTACT_RESPONSE_AVAILABLE, "Original overlap separation after contact; independent of Simba and Scar collision boxes, placements, graphics and sound. Restarts the level"},
    {"gameplay.simba.adult_ledge_reactions", "Adult ledge reactions", 33, 1, 1, TLK_ADULT_LEDGE_REACTIONS_AVAILABLE, "Original hanging/release reactions and enemy approach rules; collision boxes, terrain, art and sound remain independent. Restarts the level"},
    {"gameplay.enemies.hyenas.adult_culling", "Adult hyena lifetime", 33, 1, 1, TLK_ADULT_HYENA_CULLING_AVAILABLE, "Simba's Return and Pride Rock: MD uses the live stage in ordinary hyena culling decisions; movement, combat, spawning, artwork and sound remain independent. Restarts the level"},
    {"gameplay.levels.simbas_return.doorway_hyenas", "Doorway hyena spawns", 33, 1, 1, TLK_RETURN_DOORWAY_HYENAS_AVAILABLE, "Original MD doorway-owned enemy lists, including the extra hyena in two rooms. Ordinary spawning and updates retained; lifetime, combat, terrain, art and sound remain independent. Restarts the level"},
    {"gameplay.levels.simbas_return.doorway_timing", "Doorway entry timing", 33, 1, 1, TLK_RETURN_DOOR_TIMING_AVAILABLE, "Original MD entry wait before ordinary fade, teleport and input resume. Spawns, combat, terrain, art and sound remain independent. Restarts the level"},
    {"gameplay.levels.simbas_return.ledge_wall_probes", "Ledge-jump wall probes", 33, 1, 1, TLK_RETURN_WALL_AVAILABLE, "Original MD ledge-jump flag selects lower, inward wall probes during Return jumps. Terrain, grip points, combat, artwork and sound stay independent. Restarts the level"},
    {"gameplay.levels.simbas_return.exit_timing", "Exit countdown", 33, 1, 1, TLK_RETURN_EXIT_AVAILABLE, "Original MD room-completion wait before the exit, translated into the ordinary native countdown. Combat, layout, art and sound remain independent. Restarts the level"},
    {"gameplay.levels.pride_rock.scar_activation", "Scar activation and reveal", 33, 1, 1, TLK_SCAR_ACTIVATION_AVAILABLE, "MD initializes later Scar controllers when spawned and uses its vertical reveal band. Normal callbacks, spawning and reveal retained; body bounds, contact response, artwork and sound remain independent. Restarts the level"},
    {"gameplay.levels.be_prepared.leaper_behavior", "Jumping enemy groups", 33, 1, 1, TLK_BE_PREPARED_BEHAVIOR_AVAILABLE, "MD linked following, group wake-up and movement speed. Contact boxes, artwork and sound remain independent. Restarts the level"},
    {"gameplay.levels.be_prepared.attack_events", "Enemy attack sequence", 33, 1, 1, TLK_BE_PREPARED_BEHAVIOR_AVAILABLE, "MD attack-animation progression through voice cues; ordinary enemy decisions retained. Audio selection remains independent. Restarts the level"},
    {"gameplay.levels.be_prepared.death_update_order", "Death update order", 33, 1, 1, TLK_BE_PREPARED_BEHAVIOR_AVAILABLE, "Finishes the ordinary actor update before a lava-death restart, preserving subsequent enemy behavior. Restarts the level"},
    {"gameplay.levels.be_prepared.leaper_bounds", "Jumping enemy contact boxes", 33, 1, 1, TLK_BE_PREPARED_AVAILABLE, "Installed MD rectangles for22 reviewed jumping enemy poses; ordinary and direct combat queries. Behavior, artwork and sound remain independent. Restarts the level"},
    {"gameplay.levels.be_prepared.rock_bounds", "Falling rock contact boxes", 33, 1, 1, TLK_BE_PREPARED_AVAILABLE, "Installed MD rectangles for13 falling rock phases, including impacts. Terrain, artwork and sound remain independent. Restarts the level"},
    {"gameplay.levels.be_prepared.geyser_projectile_bounds", "Geyser projectile contact box", 33, 1, 1, TLK_BE_PREPARED_AVAILABLE, "Installed MD projectile rectangle; normal overlap and damage decisions retained. Restarts the level"},
    {"gameplay.levels.be_prepared.lava_spread", "Lava scatter range", 33, 1, 1, TLK_BE_PREPARED_AVAILABLE, "MD horizontal lava-emitter scatter using the ordinary random result; preserves random consumption. Restarts the level"},
    {"gameplay.levels.be_prepared.emitter_positions", "Lava emitter placements", 33, 1, 1, TLK_BE_PREPARED_AVAILABLE, "Original MD marker relocation before normal or retry queue registration; rock placements remain independent. Restarts the level"},
    {"gameplay.levels.be_prepared.geyser_initialization", "Geyser initialization", 33, 1, 1, TLK_BE_PREPARED_AVAILABLE, "MD initializes the ordinary geyser controller during construction; normal timer, random result and updates retained. Restarts the level"},
    {"gameplay.levels.be_prepared.streaming_top", "Activation top margin", 33, 1, 1, TLK_STREAMING_TOP_AOT_AVAILABLE, "MD six-tile top margin when scanning queued enemies and hazards; normal initial scan, camera and culling retained. Restarts the level"},
#ifndef TLK_HAKUNA_LIFE_AVAILABLE
#define TLK_HAKUNA_LIFE_AVAILABLE 0
#endif
    {"gameplay.levels.hakuna_matata.pickup_positions", "Extra-life pickup placements", 33, 1, 1, TLK_HAKUNA_LIFE_AVAILABLE, "Original MD life-pickup homes and availability after death; normal contact awards the life. Other pickups, contact boxes, artwork and sound remain independent. Restarts the level"},
    {"gameplay.levels.be_prepared.ledge_wall_probes", "Ledge-jump wall probes", 33, 1, 1, TLK_EXILE_GRIP_AVAILABLE, "MD ledge-jump flag selects lower/inward wall probes; terrain and grip points remain independent. Restarts the level"},
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
    {"graphics.menus", "Menus", 1, 0, 0, 0, ""},
    {"graphics.menus.title", "Title menu artwork", 1, 1, 0, 1, "Original MD title opening and ready menu: two background planes, fourteen Simba poses, logo, labels, copyright and selector. Publisher cards, readiness/navigation, Options and sound selected separately"},
    {"graphics.menus.publisher_cards", "Startup publisher cards", 1, 1, 0, 1, "Original MD SEGA palette animation, Disney/Virgin and Westwood/Disney Animation cards prepared during installation. Adds the original189-field SEGA prefix; following card hold durations stay native. Title art, controls and music selected separately. Full startup sequence applies on next launch"},
    {"graphics.menus.options", "Options artwork", 1, 1, 0, 1, "Original MD setting-screen planes, logo, labels, font and selector. Button names reflect active port controls; input rules and sounds remain independent. Sound Test and level-select artwork have separate choices"},
    {"gameplay.menus.options_navigation", "Options navigation", 33, 1, 0, 1, "MD wraps six rows including Exit, supports left/right adjustments, two-state music and original preset order. Existing control bindings and independent artwork/sounds retained"},
    {"audio.effects.options_cursor", "Options cursor", 23, 1, 1, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Original MD FM100 on Options Up/Down, including wrap and Exit. Replaces only the matching native menu voice; setting changes, navigation and artwork remain independent"},
    {"audio.music.title", "Title / opening", 20, 1, 1, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Original MD program73 at the title's native music start; continues through opening, ready menu, ordinary Options and level selection without restarting. Music On/Off retained; effects, artwork, readiness and Sound Test independent"},
    {"audio.music.sound_test", "Sound Test catalogue and playback", 20, 1, 1, TLK_FINAL_MENU_ART_AVAILABLE && TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Original MD sixteen-song catalogue, circular selection and audition. Names and programs prepared during installation; Music Off respected. Sound Test artwork, title and Options sources independent. Restarts the current scene"},
    {"audio.effects.world.hakuna", "Hakuna Matata", 25, 0, 0, 0, ""},
    {"audio.effects.world.hakuna.gorilla_defeat", "Gorilla defeat sounds", 25, 1, 1, 1, "Original MD defeat impacts172/92/163 and gorilla voice14 with its original parameter128. Native animation/defeat timing and music retained; ordinary attack and coconut sounds remain separate pending source work"},
    {"audio.effects.world.hakuna.gorilla_jump", "Gorilla jump cue", 25, 1, 1, 1, "Original MD silence at the repeated native-only gorilla jump cue. Defeat, grab, coconut and Simba sounds stay separate; animation and movement retained"},
    {"audio.effects.world.hakuna.gorilla_attack", "Gorilla attack cue", 25, 1, 1, 1, "Original MD FM166 at the ordinary gorilla phase-three attack marker. Native duplicate suppressed; jump silence, defeat, grab, coconut and Simba sounds stay separate. Original movement and timing retained"},
    {"audio.effects.world.hakuna.gorilla_grab", "Gorilla grab response", 25, 1, 1, 1, "Original MD voice13 replaces the native gorilla grab-response cue. Native grab animation and timing retained; Simba hurt, attack, jump, defeat and coconuts stay independently selected"},
    {"graphics.sprites.enemies.gorilla.coconuts", "Coconuts", 184, 0, 0, 0, ""},
    {"graphics.sprites.enemies.gorilla.coconuts.frames", "Frame artwork", 184, 1, 0, 1, "Original MD static coconut body and six break drawings, only for Hakuna coconut actors. Timing and lifetime independent"},
    {"graphics.sprites.enemies.gorilla.coconuts.palette", "Palette", 184, 1, 0, 1, "Original MD body palette0 and break palette1, independent of artwork, scenery and lifetime"},
    {"audio.effects.world.hakuna.coconut_bounce", "Coconut bounce", 25, 1, 1, 1, "Original MD FM123 at the owned coconut bounce; matching native sound suppressed. Lifetime and artwork independent"},
    {"audio.effects.world.hakuna.coconut_break", "Coconut break", 25, 1, 1, 1, "Original MD FM103 at the owned coconut break; matching native sound suppressed. Lifetime and artwork independent"},
#endif
    {"gameplay.life_pickup_limit", "Extra-life limit", 27, 1, 0, TLK_LIFE_PICKUP_AVAILABLE, "Original MD nine-life limit for 1UP availability and ordinary life awards; SNES uses eight. Bonus reward schedules, artwork and sound are independent"},
    {"audio.effects.world.one_up", "1UP pickup", 25, 1, 1, 1, "Shared1UP program wherever it runs: original MD cub PCM15 / adult FM114. King retains its existing extra-life sound override. Independent of extra-life limits, graphics and other pickup sounds"},
    {"graphics.sprites.animals.flying_creatures", "Flying creatures", 2, 0, 0, 0, "All ten original drawings share their indexed artwork and anchors"},
    {"graphics.sprites.animals.flying_creatures.palette", "Palette", 2, 1, 0, 1, "Original MD colors for the shared flying-creature program; independent of Simba, other animals and take-off sound; exact owner, pose and native palette checks preserve flashes"},
    {"graphics.sprites.world_objects.ride_obstacles", "Ostrich ride obstacles", 2, 0, 0, 0, "Ground obstacle and compound tree branches"},
    {"graphics.sprites.world_objects.ride_obstacles.frames", "Frame artwork", 2, 1, 0, 1, "Original MD ground obstacle, lower/upper tree branches and collision drawings; exact parent/child ownership; independent of palette, script and collision behavior"},
    {"graphics.sprites.world_objects.ride_obstacles.palette", "Palette", 2, 1, 0, 1, "Original MD ride-obstacle palettes0/1/2; independent of artwork, Simba and scenery; native flashes and repurposed banks preserved"},
    {"graphics.sprites.animals.giraffes", "Giraffe platforms", 2, 0, 0, 0, "Head drawings; large bodies belong to scenery"},
    {"graphics.sprites.animals.giraffes.frames", "Frame artwork", 2, 1, 0, 1, "Original MD seven standing, bending and flat head drawings; native animation timing, collisions, placements and scenery remain independent"},
    {"graphics.sprites.animals.giraffes.palette", "Palette", 2, 1, 0, 1, "Original live MD giraffe palette1; exact native OBJ5 and captured owner checks preserve flashes; independent of artwork, scenery, rhinos and other animals"},
    {"graphics.menus.level_select", "Cheat / level-select artwork", 1, 1, 0, 1, "Original MD two-plane menu, labels, fourteen level names and selector. Native BARRY entry, navigation and three invulnerability states retained; both enabled states display Yes. Title, Options and sounds selected independently"},
    {"audio.effects.level_select", "Cheat / level-select effects", 23, 1, 0, TLK_MENU_AUDIO_OUTPUT_AVAILABLE, "Original MD cursor FM100 when changing rows; value changes and exit are silent. Only verified native debug-menu voices are replaced. Title music, artwork, settings and gameplay sounds remain independent"},
    {"graphics.menus.sound_test", "Sound Test artwork", 1, 1, 0, TLK_FINAL_MENU_ART_AVAILABLE, "Original selected-console background, font, selector and list layout. Catalogue names, order and playback follow the independent Sound Test catalogue/audio choice; changing artwork preserves the selected song"},
    {"audio.effects.world.hakuna.spider", "Hakuna spider voice", 25, 1, 1, 1, "Original MD voice6 at the spider's ordinary animation marker, replacing the native cue. Spider movement, artwork, positions, other enemies and music stay independent"},
    {"audio.effects.world.hakuna.spider_projectile", "Spider projectile", 25, 1, 1, 1, "Original MD FM167 when the spider launches its projectile; matching native cue suppressed. Voice, defeat sound, movement, artwork and music remain independent; changing audio restarts the level"},
    {"audio.effects.world.hakuna.frog_attack", "Frog attack cue", 25, 1, 1, 1, "Original MD silence at the native-only frog charge sound. Frog movement, animation, positions, defeat sounds and music stay independent"},
    {"audio.effects.world.rolling_stones", "Rolling stone rumble", 25, 1, 1, TLK_NATIVE_AUDIO_OWNER_AVAILABLE, "Original MD omits the SNES rolling-stone loop in Exile and Be Prepared. Replaces only verified native rolling voices at output; rock movement, timing, other impacts, artwork and music stay independent"},
    {"audio.effects.simba.hazard_death", "Water and lava splash", 24, 1, 1, 1, "Original MD FM103 at Simba's shared water/lava death action, for cub and adult. Movement, death timing, artwork and music stay independent; changing audio restarts the level"},
    {"audio.effects.simba.revival_roar", "Revival roar", 24, 1, 1, 1, "Original MD shared revival cue: cub PCM10, adult requests10 then11. Separate from ordinary roar, level/death music, artwork and retry timing; changing audio restarts the level"},
    {"graphics.sprites.cinematics.timon", "Opening Timon", 2, 0, 0, 0, "Scene-owned opening graphics; voice and placement have separate choices"},
    {"graphics.sprites.cinematics.timon.frames", "Frame artwork", 486, 1, 0, 1, "All22 original MD opening drawings, installed from the original scene bank; independent of bonus Timon, palette, timing and placement"},
    {"graphics.sprites.cinematics.timon.palette", "Palette", 486, 1, 0, 1, "Original MD opening palette; mixed artwork uses nearest original nontransparent colors; native fades retained"},
    {"graphics.sprites.cinematics.timon.animation", "Pose timing", 486, 1, 0, 1, "Original MD four-update pose cadence from native scene phases and counters; native startup, fade and overall scene lifetime retained; independent of artwork and voice"},
    {"graphics.titles.remaining", "Other levels and King instruction", 112, 0, 0, 0, ""},
    {"graphics.titles.remaining.frames", "Caption artwork", 0, 1, 0, 1, "Original MD artwork for the remaining level and bonus names and King instruction; native message order and lifetime retained; independent of palette and vertical position"},
    {"graphics.titles.remaining.palette", "Caption palette", 0, 1, 0, 1, "Original shared MD caption palette; independent of artwork, HUD and Simba; native flash palettes retained"},
    {"graphics.titles.remaining.position", "Caption height", 0, 1, 0, 1, "MD selects the original Y72 anchor; SNES keeps the native baseline. Both artwork modes stay horizontally centred; message order and lifetime remain native"},

    {"gameplay.levels.pride_rock.rain", "Ending rain movement and buildup", 33, 1, 1, 1, "Original MD rain buildup to29 drops and320-pixel horizontal wrapping. Rain artwork and palette remain independently selected under World objects; ending script, camera, music and speech remain separate. Restarts the level"},
    {"graphics.sprites.enemies.chameleons", "Chameleons", 10, 0, 0, 0, "Chameleons in The Pridelands and Simba's Exile"},
    {"graphics.sprites.enemies.chameleons.frames", "Frame artwork", 10, 1, 0, 1, "Choose the chameleon's drawings. Colors, movement, attacks and sounds are chosen separately."},
    {"graphics.sprites.enemies.chameleons.palette", "Palette", 10, 1, 0, 1, "Choose the chameleon's colors without changing its drawings."},
    {"graphics.sprites.enemies.porcupines", "Porcupines", 10, 0, 0, 0, "Porcupines in The Pridelands and Simba's Exile"},
    {"graphics.sprites.enemies.porcupines.frames", "Frame artwork", 10, 1, 0, 1, "Choose the porcupine's drawings. Colors, movement, attacks and sounds are chosen separately."},
    {"graphics.sprites.enemies.porcupines.palette", "Palette", 10, 1, 0, 1, "Choose the porcupine's colors without changing its drawings."},
};
enum { COUNT = sizeof nodes / sizeof nodes[0] };
static int parents_ready;
static void BindResourceParents(void) {
    if(parents_ready)return;
    for(int i=0;i<COUNT;i++)nodes[i].parent=TlkResourceParentById(nodes,COUNT,i);
    for(int i=0;i<COUNT;i++){const char *parent=TlkResourceSemanticParent(nodes[i].id);if(parent)for(int j=0;j<COUNT;j++)if(!strcmp(nodes[j].id,parent)){nodes[i].parent=j;break;}}
    parents_ready=1;
}
static unsigned char active[COUNT], draft[COUNT];
static uint16_t snes_cub[16], md_cub[16];
static int md_ready;
static TlkCheckpointArt *checkpoint_art;
static TlkRevivalArt *installed_revival_art;
static TlkNativeHud *installed_native_hud;
static const char *native_hud_asset_path;
void TlkResourcesSetNativeHudAssetsPath(const char *path) {native_hud_asset_path=path;}
int TlkResourcesNativeHudAssetsReady(void) {return installed_native_hud!=NULL;}
TlkNativeHud *TlkResourcesNativeHudCopy(void) {return TlkNativeHudClone(installed_native_hud);}
static const char *revival_asset_path;
void TlkResourcesSetRevivalAssetsPath(const char *path) {revival_asset_path=path;}
int TlkResourcesRevivalAssetsReady(void) {return installed_revival_art!=NULL;}
TlkRevivalArt *TlkResourcesRevivalArtCopy(void) {return TlkRevivalArtClone(installed_revival_art);}
static const char *checkpoint_asset_path;
void TlkResourcesSetCheckpointAssetsPath(const char *path) {checkpoint_asset_path=path;}
int TlkResourcesCheckpointAssetsReady(void) {return checkpoint_art!=NULL;}
static TlkTitleArt *title_art;
static const char *title_asset_path;
void TlkResourcesSetTitleAssetsPath(const char *path) {title_asset_path=path;}
int TlkResourcesTitleAssetsReady(void) {return title_art!=NULL;}
static char profile_path[2048], status[256], md_status[256];
static char asset_cache_path[2048];
static int prepare_cache,cache_prepared;
void TlkResourcesSetCachePath(const char *path,int prepare) {
    snprintf(asset_cache_path,sizeof asset_cache_path,"%s",path?path:"");
    prepare_cache=prepare;cache_prepared=0;
}
int TlkResourcesCachePrepared(void) { return cache_prepared; }

int TlkResourcesCount(void) { BindResourceParents();return COUNT; }
const TlkResourceNode *TlkResourcesNode(int i) { BindResourceParents();return i >= 0 && i < COUNT ? &nodes[i] : NULL; }
/* IDs and their catalogue order are immutable; active/draft sources are not.
 * Index the names once, while every resolution still reads the current choice.
 * Publish a complete table before audio/render callers may read it. */
static unsigned ResourceIdHash(const char *id) {
    unsigned hash=2166136261u;
    for(;*id;id++)hash=(hash^(unsigned char)*id)*16777619u;
    return hash;
}
int TlkResourcesFind(const char *id) {
    enum { CAPACITY=2048 };
    _Static_assert(COUNT<CAPACITY,"Resource name index needs more capacity");
    static unsigned short slots[CAPACITY];
    static atomic_uint ready;
    if(!id)return -1;
    if(atomic_load_explicit(&ready,memory_order_acquire)!=2) {
        unsigned expected=0;
        if(atomic_compare_exchange_strong_explicit(&ready,&expected,1,
                memory_order_acq_rel,memory_order_acquire)) {
            for(unsigned i=0;i<COUNT;i++) {
                unsigned at=ResourceIdHash(nodes[i].id)&(CAPACITY-1);
                while(slots[at])at=(at+1)&(CAPACITY-1);
                slots[at]=(unsigned short)(i+1);
            }
            atomic_store_explicit(&ready,2,memory_order_release);
        }else while(atomic_load_explicit(&ready,memory_order_acquire)!=2) {}
    }
    unsigned at=ResourceIdHash(id)&(CAPACITY-1);
    while(slots[at]) {
        unsigned i=slots[at]-1;
        if(!strcmp(id,nodes[i].id))return (int)i;
        at=(at+1)&(CAPACITY-1);
    }
    return -1;
}
int TlkResourcesChoice(int i, int pending) { return i >= 0 && i < COUNT ? (pending ? draft[i] : active[i]) : 0; }
static int graphics_preview_node=-1,graphics_preview_source;
void TlkResourcesPreviewBegin(int i,int source) {
    graphics_preview_node=i>=0 && i<COUNT && !strncmp(nodes[i].id,"graphics",8)?i:-1;
    graphics_preview_source=source;
}
void TlkResourcesPreviewEnd(void) { graphics_preview_node=-1; }
int TlkResourcesResolved(int i, int pending) {
    BindResourceParents();
    if (i < 0 || i >= COUNT) return TLK_SOURCE_SNES;
    if(TlkResourceSharedDeath(nodes[i].id))i=TlkResourcesFind("audio.music.pride_health_death");
    int preview=graphics_preview_node>=0 && !strncmp(nodes[i].id,"graphics",8);
    const unsigned char *choices = pending || preview ? draft : active;
    for (; i >= 0; i = nodes[i].parent) {
        int choice=preview && i==graphics_preview_node?graphics_preview_source:choices[i];
        if(choice)return choice;
    }
    return TLK_SOURCE_SNES;
}
int TlkResourcesSet(int i, int source) {
    if (i < 0 || i >= COUNT || source < 0 || source > TLK_SOURCE_MD || (!i && !source)) return 0;
    if(TlkResourceSharedDeath(nodes[i].id)) {
        for(int j=0;j<COUNT;j++)if(TlkResourceSharedDeath(nodes[j].id))draft[j]=(unsigned char)source;
    } else draft[i] = (unsigned char)source;
    return 1;
}
int TlkResourcesDirty(void) { return memcmp(active, draft, sizeof active) != 0; }
void TlkResourcesRevert(void) { memcpy(draft, active, sizeof draft); }
void TlkResourcesDefaults(void) { memset(draft, 0, sizeof draft); draft[0] = TLK_SOURCE_SNES; }
void TlkResourcesGraphicsPreset(void) {
    TlkResourcesDefaults();
    const char *ids[]={"display.viewport","graphics.scenery","graphics.sprites.simba.cub.palette","graphics.sprites.simba.adult.palette"};
    for (unsigned i=0;i<sizeof ids/sizeof ids[0];i++) TlkResourcesSet(TlkResourcesFind(ids[i]),TLK_SOURCE_MD);
}
void TlkResourcesMdPreset(void) {
    TlkResourcesDefaults();
    if(!md_ready)return;
    draft[0]=TLK_SOURCE_MD;
    /* Keep branch inheritance useful after choosing the preset. Only choices
     * that cannot use MD receive an explicit SNES override. */
    for(int i=1;i<COUNT;i++)if(nodes[i].leaf)draft[i]=TLK_SOURCE_SNES;
    for(int i=1;i<COUNT;i++) {
        if(!nodes[i].leaf || !nodes[i].md_supported)continue;
        draft[i]=TLK_SOURCE_INHERIT;
        /* Reuse the same package/backend checks as Apply. Do not advertise a
         * choice merely because its adapter was compiled into this player. */
        if(TlkResourcesValidate(NULL,0))draft[i]=TLK_SOURCE_SNES;
    }
}
const char *TlkResourcesStatus(void) { return status; }
const char *TlkResourcesMdStatus(void) { return md_status; }
int TlkResourcesMixed(void) {
    int i = TlkResourcesFind("graphics.sprites.simba.cub.palette");
    int adult = TlkResourcesFind("graphics.sprites.simba.adult.palette");
    return md_ready && (TlkResourcesResolved(i, 0) == TLK_SOURCE_MD || TlkResourcesResolved(adult, 0) == TLK_SOURCE_MD);
}
int TlkResourcesViewportWidth(void) {
    return TlkResourcesResolved(TlkResourcesFind("display.viewport"), 0) == TLK_SOURCE_MD ? 320 : 256;
}
int TlkResourcesViewportForScene(unsigned level) {
    int width=TlkResourcesViewportWidth();
    return width==320 && level==3 ? 256 : width;
}
int TlkResourcesUseMd(const char *id) { return md_ready && TlkResourcesResolved(TlkResourcesFind(id),0)==TLK_SOURCE_MD; }

int TlkResourcesHudFramesMd(unsigned kind) {
    static const char *ids[]={"graphics.hud.frames.roar","graphics.hud.frames.health","graphics.hud.frames.lives"};
    return kind<3 && TlkResourcesUseMd(ids[kind]);
}
int TlkResourcesHasMd(void) { return md_ready; }
int TlkResourcesPresentation(void) {
    /* Support independent/new graphics leaves in native width. The existing
     * expression below also owns stable game-patch anchors and viewport modes. */
    if(md_ready)for(int i=0;i<COUNT;i++)if(nodes[i].leaf && nodes[i].md_supported &&
       !strncmp(nodes[i].id,"graphics.",9) && TlkResourcesResolved(i,0)==TLK_SOURCE_MD)return 1;
    return TlkResourcesMixed() || TlkResourcesUseMd("graphics.sprites.simba.cub.frames") ||
           TlkResourcesUseMd("graphics.sprites.simba.adult.frames") || TlkResourcesViewportWidth() != 256 ||
           TlkResourcesUseMd("graphics.sprites.enemies.gorilla.frames") || TlkResourcesUseMd("graphics.sprites.enemies.gorilla.palette") ||
           TlkResourcesUseMd("graphics.sprites.world_objects.frames") || TlkResourcesUseMd("graphics.sprites.world_objects.palette") ||
           TlkResourcesUseMd("graphics.sprites.animals.monkeys.frames") ||
           TlkResourcesUseMd("graphics.sprites.enemies.hyenas.adult.frames") || TlkResourcesUseMd("graphics.sprites.enemies.hyenas.adult.palette") ||
           TlkResourcesUseMd("graphics.sprites.simba.cub.exile_death_motion") ||
           TlkResourcesUseMd("graphics.sprites.simba.cub.hakuna_death_motion") ||
           TlkResourcesUseMd("graphics.sprites.stampede.wildebeests.palette") ||
           TlkResourcesUseMd("graphics.sprites.stampede.rocks.frames") || TlkResourcesUseMd("graphics.sprites.stampede.rocks.palette") ||
           TlkResourcesUseMd("graphics.scenery.stampede_palette") ||
           TlkResourcesUseMd("graphics.sprites.simba.cub.graveyard_death_motion") ||
           TlkResourcesUseMd("graphics.sprites.animals.monkeys.palette") ||
           TlkResourcesUseMd("graphics.sprites.animals.ostriches.palette") ||
           TlkResourcesUseMd("graphics.sprites.animals.hippos.frames") || TlkResourcesUseMd("graphics.sprites.animals.hippos.palette") ||
           TlkResourcesUseMd("graphics.sprites.animals.rhinos.frames") || TlkResourcesUseMd("graphics.sprites.animals.rhinos.palette") ||
           TlkResourcesUseMd("graphics.sprites.animals.rhinos.tail.palette") ||
           TlkResourcesUseMd("graphics.hud.palette") ||
           TlkResourcesHudFramesMd(0) || TlkResourcesHudFramesMd(1) || TlkResourcesHudFramesMd(2) ||
           TlkResourcesUseMd("graphics.sprites.enemies.hyenas.frames") || TlkResourcesUseMd("graphics.sprites.enemies.hyenas.palette") ||
           TlkResourcesUseMd("graphics.sprites.enemies.vultures.frames") || TlkResourcesUseMd("graphics.sprites.enemies.vultures.palette") ||
           TlkResourcesUseMd("graphics.sprites.bones.frames") || TlkResourcesUseMd("graphics.sprites.bones.palette") ||
           TlkResourcesUseMd("graphics.sprites.mufasa.palette") ||
           TlkResourcesUseMd("graphics.sprites.enemies.other.frames") || TlkResourcesUseMd("graphics.sprites.enemies.other.palette") ||
           TlkResourcesUseMd("graphics.sprites.pickups.frames") || TlkResourcesUseMd("graphics.sprites.pickups.palette") ||
           TlkResourcesUseMd("graphics.sprites.leaves.frames") || TlkResourcesUseMd("graphics.sprites.leaves.palette") ||
           TlkResourcesUseMd("graphics.sprites.effects.defeat_puff.frames") || TlkResourcesUseMd("graphics.sprites.effects.defeat_puff.palette") ||
           TlkResourcesUseMd("graphics.sprites.effects.pickup_arrival.frames") || TlkResourcesUseMd("graphics.sprites.effects.pickup_arrival.palette") ||
           TlkResourcesUseMd("graphics.sprites.effects.pickup_arrival.position") ||
           TlkResourcesUseMd("graphics.titles.remaining.frames") || TlkResourcesUseMd("graphics.titles.remaining.palette") ||
           TlkResourcesUseMd("graphics.titles.remaining.position") ||
           TlkResourcesUseMd("graphics.titles.pride_lands.frames") || TlkResourcesUseMd("graphics.titles.pride_lands.palette") ||
           TlkResourcesUseMd("graphics.titles.pride_lands.position") || TlkResourcesUseMd("graphics.titles.pride_lands.duration") ||
           TlkResourcesUseMd("graphics.sprites.checkpoints.frames") || TlkResourcesUseMd("graphics.sprites.checkpoints.palette") ||
           TlkResourcesUseMd("graphics.scenery.foreground") || TlkResourcesUseMd("graphics.scenery.background") ||
           TlkResourcesUseMd("graphics.scenery.palettes");
}
int TlkResourcesValidate(char *reason, size_t size) {
    int blocked = 0;
    if (reason && size) *reason = 0;
    for (int i = 0; i < COUNT; i++) {
        if (!nodes[i].leaf || TlkResourcesResolved(i, 1) != TLK_SOURCE_MD) continue;
        if(!strcmp(nodes[i].id,"gameplay.continue_token_positions") &&
           (!TlkMdSceneMarkerDataReady(1) || !TlkMdSceneMarkerDataReady(6))) {
            if(!blocked && reason && size)snprintf(reason,size,"Prepared Continue-token placements unavailable; run Setup");blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.hyena_wall_probes") && !TlkGraveyardWallRules()){
            if(!blocked && reason && size)snprintf(reason,size,"Graveyard hyena wall data unavailable; run Setup");blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.upper_bone_position")){
            unsigned md;if(!TlkGraveyardUpperMarker(83,1268,0,0,&md)){
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard upper bone data unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.upper_vulture_positions")){
            unsigned md;if(!TlkGraveyardUpperMarker(118,2276,952,118,&md)){
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard upper patrol data unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.perched_vulture_positions")){
            unsigned md;if(!TlkGraveyardPerchedMarker(11103,26616,50,&md)){
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard perched vulture data unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.bug_positions")){
            unsigned md;if(!TlkGraveyardBugMarker(12010,21152,0,&md)){
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard random bug data unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.pickup_positions")){
            unsigned md;if(!TlkGraveyardPickupMarker(1981,696,17,&md)){
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard pickup data unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.falling_bone_shake") && !TlkGraveyardShakeRules()){
            if(!blocked && reason && size)snprintf(reason,size,"Falling bone data unavailable; run Setup");blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"audio.effects.world.be_prepared.group_call") && !TlkBePreparedGroupSoundRules()){
            if(!blocked&&reason&&size)snprintf(reason,size,"Be Prepared sound data unavailable; run Setup");blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.be_prepared.leaper_behavior") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.attack_events") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.death_update_order") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.leaper_bounds") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.rock_bounds") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.geyser_projectile_bounds") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.lava_spread") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.emitter_positions") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.geyser_initialization")) && !TlkBePreparedDataReady()){
            if(!blocked&&reason&&size)snprintf(reason,size,"Be Prepared data unavailable; run Setup");blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.simba.adult_ledge_reactions")&&!TlkLateSceneAdultLedgeRules()){
            if(!blocked&&reason&&size)snprintf(reason,size,"Adult ledge data unavailable; run Setup");blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.pride_rock.scar_activation") || !strcmp(nodes[i].id,"gameplay.levels.simbas_return.exit_timing") || !strcmp(nodes[i].id,"gameplay.levels.adult_hyenas.bounds") || !strcmp(nodes[i].id,"gameplay.levels.simbas_return.doorway_timing") ||
            !strcmp(nodes[i].id,"gameplay.levels.simbas_return.doorway_hyenas") ||
            !strcmp(nodes[i].id,"gameplay.levels.simbas_return.terrain") ||
            !strcmp(nodes[i].id,"gameplay.levels.simbas_return.pickup_positions") ||
            !strcmp(nodes[i].id,"gameplay.levels.pride_rock.terrain") ||
            !strcmp(nodes[i].id,"gameplay.levels.pride_rock.object_positions")) && !TlkLateSceneDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Late level layout data unavailable; run Setup");
            blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.be_prepared.rock_positions") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.terrain")) && !TlkNextSceneDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Be Prepared: prepared collision data unavailable; run Setup");
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.bonus.round_selection")){
            unsigned level;if(!TlkNextSceneBonusSelection(1,&level)){
                if(!blocked && reason && size)snprintf(reason,size,"Bonus selection: prepared table unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strncmp(nodes[i].id,"gameplay.bonus.bug_hunt.",sizeof("gameplay.bonus.bug_hunt.")-1) && !TlkHuntDataSize()) {
            if(!blocked && reason && size)snprintf(reason,size,"Bug Hunt: prepared terrain unavailable; run Setup");
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.rhino_bounds")) {
            unsigned native,external;
            if(!TlkHitboxDataGet(0xc3c991,6,0,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Rhino body: prepared bounds unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.hippo_height")) {
            unsigned native,external;
            if(!TlkCantWaitHippoOffset(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Hippo platforms: prepared height unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.exit_boundary")) {
            unsigned native,external;
            if(!TlkCantWaitExitBoundary(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"King completion: prepared boundary unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.terrain") && !TlkCwTerrainDataSize()) {
            if(!blocked && reason && size)snprintf(reason,size,"Terrain map: prepared collision data unavailable; run Setup");
            blocked++;continue;
        }
        if(TLK_CANT_WAIT_OSTRICH_AVAILABLE && !strcmp(nodes[i].id,"gameplay.camera")) {
            unsigned native,external;
            if(!TlkCantWaitRideValue(0,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"MD camera: prepared ride parameters unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.ostrich_obstacles")) {
            unsigned native,external;
            if(!TlkCantWaitOstrichDelay(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Ostrich obstacles: prepared timing unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.giraffe_platforms")) {
            unsigned native,external;
            if(!TlkCantWaitGiraffeOffset(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Giraffe platforms: prepared positions unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.exit_start_skip")) {
            unsigned native,md;if(!TlkNextSceneDestinyExitStart(&native,&md)){
                if(!blocked && reason && size)snprintf(reason,size,"Destiny exit: prepared button mask unavailable; run Setup.cmd");blocked++;continue;
            }
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.monkey_behavior") ||
            !strncmp(nodes[i].id,"audio.effects.world.simbas_destiny.monkey_",41)) && !TlkDestinyMonkeyDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: prepared monkey actions unavailable; run Setup.cmd",nodes[i].id);
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.monkey_grips")) {
            unsigned native,external;
            if(!TlkCantWaitMonkeyGrip(0xc43e0b,0,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"%s: prepared monkey points unavailable; run Setup.cmd",nodes[i].id);
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.monkey_roar_range")) {
            unsigned native,external;
            if(!TlkCantWaitRoarRange(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Monkey roar: prepared range unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.start")) {
            unsigned native,external;
            if(!TlkStartDataCantWaitValue(0,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Can't Wait: prepared entry position unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.cant_wait.rhino_tail_bounds")) {
            unsigned native,external;
            if(!TlkHitboxDataGet(0xc3cf4f,5,3,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Rhino tail: prepared catch regions unavailable; run Setup");
                blocked++;continue;
            }
        }
        if((!strncmp(nodes[i].id,"graphics.sprites.bonus.",22) ||
            !strncmp(nodes[i].id,"graphics.sprites.enemies.scar.",29)) && !TlkNextSceneDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: installed scene palettes unavailable; run Setup",nodes[i].id);
            blocked++;continue;
        }
        if(!strncmp(nodes[i].id,"graphics.sprites.enemies.gorilla.",33) && !TlkNextSceneDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"Gorilla: installed scene palettes unavailable; run Setup");
            blocked++;continue;
        }
        if(!strncmp(nodes[i].id,"graphics.sprites.enemies.hyenas.adult.",36) && !TlkNextSceneDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"Adult hyenas: installed scene palettes unavailable; run Setup");
            blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.stampede.exit_flow") || !strcmp(nodes[i].id,"graphics.interlevel.stampede") || !strcmp(nodes[i].id,"audio.effects.interlevel.stampede")) && (!TlkNextSceneDataReady() || !TlkInterlevelDataCliffReady())) {
            if(!blocked && reason && size)snprintf(reason,size,"Stampede: installed cliff scene unavailable; run Setup");
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"audio.effects.interlevel.stampede") && !TlkMdSoundReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Stampede: MD sound driver unavailable");blocked++;continue;
        }
        if((!strncmp(nodes[i].id,"graphics.sprites.stampede.",26) || !strcmp(nodes[i].id,"graphics.scenery.stampede_palette")) && !TlkNextSceneDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: installed scene data unavailable; run Setup",nodes[i].id);
            blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"graphics.sprites.simba.cub.graveyard_death_motion") ||
            !strcmp(nodes[i].id,"graphics.sprites.simba.cub.king_death_motion") ||
            !strcmp(nodes[i].id,"graphics.sprites.simba.cub.stampede_death_motion") ||
            !strcmp(nodes[i].id,"graphics.sprites.simba.adult.death_motion") ||
            !strcmp(nodes[i].id,"graphics.sprites.simba.cub.exile_death_motion") ||
            !strcmp(nodes[i].id,"graphics.sprites.simba.cub.hakuna_death_motion")) &&
           (!TlkGraveyardDataReady() || TlkMdSpritesCubDeathAssetCount()!=20)) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: installed death sequence unavailable; run Setup",nodes[i].id);
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.hyena_ground_tags") && !TlkGraveyardDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: installed hyena terrain data unavailable; run Setup",nodes[i].id);
            blocked++;continue;
        }
        if(!strncmp(nodes[i].id,"graphics.titles.remaining.",sizeof("graphics.titles.remaining.")-1) && !TlkTitleArtCaptionsReady(title_art)) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: remaining caption artwork unavailable; run Setup",nodes[i].id);
            blocked++;continue;
        }
        if (!strncmp(nodes[i].id,"graphics.titles.pride_lands.",28) && !title_art) {
            if (!blocked && reason && size) snprintf(reason,size,"%s: caption artwork unavailable",nodes[i].id);
            blocked++;continue;
        }
        if (!strncmp(nodes[i].id,"graphics.sprites.checkpoints.",29) && !checkpoint_art) {
            if (!blocked && reason && size) snprintf(reason,size,"%s: verified checkpoint artwork unavailable",nodes[i].id);
            blocked++;continue;
        }
        if (!strcmp(nodes[i].id,"gameplay.simba.roar") && !TlkRoarDataReady()) {
            if (!blocked && reason && size) snprintf(reason,size,"%s: verified roar sequence unavailable",nodes[i].id);
            blocked++;continue;
        }
        if (!strcmp(nodes[i].id,"gameplay.bonus.bug_toss.start") || !strcmp(nodes[i].id,"gameplay.bonus.bug_toss.arena") || !strcmp(nodes[i].id,"gameplay.bonus.bug_toss.culling_bounds")) {
            unsigned native,external;
            if(!TlkStartDataBonusValue(2,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"%s: prepared bonus entry/limits unavailable",nodes[i].id);
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.entry_input_delay") || !strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.control_handoff")) {
            unsigned native,external;if(!TlkStartDataGraveyardInputDelay(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared entry countdown unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.vulture_positions")) {
            unsigned md;if(!TlkGraveyardVultureMarker(10786,1776,0,&md)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared vulture homes unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.falling_bone_support")) {
            unsigned delay,height;if(!TlkGraveyardBoneContactDelay(&delay) || !TlkGraveyardHeadSurface(51,0,&height)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared falling-bone support retry unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.vulture_turn_point")) {
            unsigned native,external;if(!TlkGraveyardVultureTurn(0,&native,&external) || !TlkGraveyardVultureTurn(1,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared vulture turn operands unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.vulture_launch_timing")) {
            unsigned native,external;if(!TlkGraveyardVultureLaunch(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared vulture launch masks unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.mufasa_farewell")) {
            unsigned value;if(!TlkGraveyardFarewellValue(0xc2565b,1,&value)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared Scar farewell unavailable; run Setup");
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"graphics.sprites.mufasa.palette") && !TlkGraveyardDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared Scar farewell colors unavailable; run Setup");
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.bone_contact")) {
            unsigned native,external;
            if(!TlkGraveyardBoneContact(0xc3b437,2,0,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"%s: prepared platform contact unavailable; run Setup.cmd",nodes[i].id);
                blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.bone_bridge_positions")) {
            unsigned md;if(!TlkGraveyardBoneMarker(10248,0,0,&md)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared bone bridge positions unavailable; run Setup");blocked++;continue;
            }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.opening_skull_trigger")) {
            unsigned md;if(!TlkGraveyardRevealMarker(3443,0,0,&md)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared reveal marker unavailable; run Setup");blocked++;continue;
            }
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.ledge_wall_probes") || !strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.grip_points") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.ledge_wall_probes") || !strcmp(nodes[i].id,"gameplay.levels.simbas_return.ledge_wall_probes") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.ledge_wall_probes") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.grip_points") || !strcmp(nodes[i].id,"gameplay.levels.simbas_exile.grip_points") || !strcmp(nodes[i].id,"gameplay.levels.simbas_exile.ledge_wall_probes")) && !TlkNextSceneDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Exile: prepared grip points unavailable; run Setup");blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.simba.adult_ceiling_rows") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.bonus_bug_bounds") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.gorilla_bounds") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.poison_bug_bounds") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.ceiling_clearance") || !strcmp(nodes[i].id,"gameplay.levels.simbas_exile.ceiling_clearance")) && !TlkHitboxDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Exile: prepared pose clearance unavailable; run Setup");blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.levels.simbas_exile.terrain") || !strcmp(nodes[i].id,"gameplay.levels.simbas_exile.falling_rock_bounds") || !strcmp(nodes[i].id,"gameplay.levels.stampede.camera_shake")) && !TlkNextSceneDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Exile: prepared terrain unavailable; run Setup");blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.terrain") && !TlkNextSceneDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Hakuna: prepared terrain unavailable; run Setup");blocked++;continue;
        }
        if((!strcmp(nodes[i].id,"gameplay.simba.adult_roar") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.arena_barrier") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.boulder_surface") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.boulder_positions") || !strcmp(nodes[i].id,"gameplay.simba.adult_turn_motion") || !strcmp(nodes[i].id,"gameplay.hitboxes.adult_points") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.obstacle_positions") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.monkey_positions") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.terrain") || !strcmp(nodes[i].id,"gameplay.levels.simbas_destiny.boulder_contact") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.gorilla_defeat_pauses") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.bonus_bug_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.pickup_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.gorilla_arena_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.log_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.checkpoint_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.poison_bug_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.spider_positions") || !strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.frog_positions")) && !TlkNextSceneDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Hakuna: prepared spider placements unavailable; run Setup");blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.hakuna_matata.retry_controls") || !strcmp(nodes[i].id,"gameplay.levels.be_prepared.retry_controls")){
            unsigned native,external;
            if(!TlkStartDataRetryInputDelay(&native,&external)){
                if(!blocked && reason && size)snprintf(reason,size,"Hakuna: prepared retry controls unavailable; run Setup");blocked++;continue;
            }
        }
        { static const char *const entry_ids[]={"gameplay.levels.simbas_exile.start","gameplay.levels.hakuna_matata.start","gameplay.levels.simbas_destiny.start","gameplay.levels.be_prepared.start","gameplay.levels.simbas_return.start","gameplay.levels.pride_rock.start"};
          for(unsigned j=0;j<6;j++)if(!strcmp(nodes[i].id,entry_ids[j])){
            unsigned native,external;if(!TlkStartDataLaterValue(j+4,0,&native,&external)){
                if(!blocked && reason && size)snprintf(reason,size,"%s: prepared entry position unavailable; run Setup",nodes[i].id);blocked++;
            }
          }
        }
        if(!strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.start")) {
            unsigned native,external;if(!TlkStartDataGraveyardValue(0,&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"Graveyard: prepared entry unavailable; run Setup");blocked++;continue;
            }
        }
        if (!strcmp(nodes[i].id,"gameplay.levels.pride_lands.start")) {
            unsigned native,external;
            if (!TlkStartDataValue(0,&native,&external)) {
                if (!blocked && reason && size) snprintf(reason,size,"%s: verified default position unavailable",nodes[i].id);
                blocked++;continue;
            }
        }
        if (!strcmp(nodes[i].id,"gameplay.levels.pride_lands.lizard_reactivation")) {
            unsigned native,external;
            if(!TlkReactivationDataFlags(&native,&external)) {
                if(!blocked && reason && size)snprintf(reason,size,"%s: verified lizard descriptor unavailable",nodes[i].id);
                blocked++;continue;
            }
        }
        if ((!strcmp(nodes[i].id,"gameplay.bonus.bug_toss.result_flow") || !strcmp(nodes[i].id,"graphics.bonus_results") || !strcmp(nodes[i].id,"audio.effects.bonus.result_voice")) && !TlkBonusResultDataReady()){
            if(!blocked && reason && size)snprintf(reason,size,"%s: prepared bonus result unavailable",nodes[i].id);
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"audio.effects.bonus.result_voice") && !TlkMdSoundReady()){
            if(!blocked && reason && size)snprintf(reason,size,"%s: MD sound driver unavailable",nodes[i].id);
            blocked++;continue;
        }
        if ((!strcmp(nodes[i].id,"gameplay.levels.pride_lands.interlevel_scene") || !strcmp(nodes[i].id,"graphics.interlevel.pride_lands") || !strcmp(nodes[i].id,"graphics.ending_sunrise") || !strcmp(nodes[i].id,"audio.effects.interlevel.pride_lands") || !strcmp(nodes[i].id,"audio.voices.ending")) && !TlkInterlevelDataReady()) {
            if(!blocked && reason && size)snprintf(reason,size,"%s: prepared interlevel scene unavailable",nodes[i].id);
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"graphics.ending_title") && !TlkInterlevelDataEndingTitleReady()){
            if(!blocked && reason && size)snprintf(reason,size,"%s: prepared ending title unavailable; run Setup.cmd",nodes[i].id);
            blocked++;continue;
        }
        if(!strncmp(nodes[i].id,"graphics.sprites.cinematics.timon",sizeof("graphics.sprites.cinematics.timon")-1) && !TlkInterlevelDataTimonReady()){
            if(!blocked && reason && size)snprintf(reason,size,"%s: installed opening Timon graphics unavailable; run Setup.cmd",nodes[i].id);
            blocked++;continue;
        }
        if(!strcmp(nodes[i].id,"graphics.ending_credits") && !TlkInterlevelDataCreditsReady()){
            if(!blocked && reason && size)snprintf(reason,size,"%s: prepared credits unavailable; run Setup.cmd",nodes[i].id);
            blocked++;continue;
        }
        if (!strcmp(nodes[i].id,"audio.effects.world.simbas_exile.exit") && !TlkInterlevelDataCliffReady()){
            if(!blocked && reason && size)snprintf(reason,size,"Exile: installed outro samples unavailable; run Setup");blocked++;continue;
        }
        if ((!strcmp(nodes[i].id,"audio.effects.interlevel.pride_lands") || !strcmp(nodes[i].id,"audio.voices.ending") || !strcmp(nodes[i].id,"audio.voices.opening_timon") || !strcmp(nodes[i].id,"audio.music.ending_credits") || !strcmp(nodes[i].id,"audio.music.pride_rock.finale") || !strcmp(nodes[i].id,"audio.music.title") || !strcmp(nodes[i].id,"audio.music.sound_test") || !strcmp(nodes[i].id,"audio.effects.world.simbas_exile.exit") || !strcmp(nodes[i].id,"audio.effects.world.hakuna.gorilla_defeat") || !strcmp(nodes[i].id,"audio.effects.world.hakuna.gorilla_jump") || !strcmp(nodes[i].id,"audio.effects.world.hakuna.gorilla_attack") || !strcmp(nodes[i].id,"audio.effects.world.hakuna.gorilla_grab") || !strcmp(nodes[i].id,"audio.effects.world.hakuna.coconut_bounce") || !strcmp(nodes[i].id,"audio.effects.world.hakuna.coconut_break")) && !TlkMdSoundReady()){
            if(!blocked && reason && size)snprintf(reason,size,"%s: MD sound driver unavailable",nodes[i].id);
            blocked++;continue;
        }
        if ((!strncmp(nodes[i].id,"gameplay.hitboxes.",18) || !strcmp(nodes[i].id,"gameplay.levels.pride_lands.ceiling_clearance") ||
             !strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.hyena_bounds") ||
             !strcmp(nodes[i].id,"gameplay.levels.adult_hyenas.bounds") ||
             !strcmp(nodes[i].id,"gameplay.levels.pride_lands.bonus_bug_bounds") ||
             !strcmp(nodes[i].id,"gameplay.levels.elephant_graveyard.bonus_bug_bounds") ||
             !strcmp(nodes[i].id,"gameplay.levels.pride_rock.scar_bounds")) && !TlkHitboxDataReady()) {
            if (!blocked && reason && size)snprintf(reason,size,"%s: verified pose bounds unavailable",nodes[i].id);
            blocked++;continue;
        }
        if (!strcmp(nodes[i].id,"gameplay.levels.pride_lands.contacts") && !TlkContactMapReady()) {
            if (!blocked && reason && size) snprintf(reason,size,"%s: verified contact map unavailable",nodes[i].id);
            blocked++;continue;
        }
        if (nodes[i].md_supported && !strncmp(nodes[i].id,"audio.",6) && !TlkMdSoundReady()) {
            if (!blocked && reason && size) snprintf(reason,size,"%s: %s",nodes[i].id,TlkMdSoundStatus());
            blocked++;continue;
        }
        if (!md_ready || !nodes[i].md_supported) {
            if (!blocked && reason && size)
                snprintf(reason, size, "%s: %s", nodes[i].id,
                         !md_ready ? "verified Mega Drive ROM required" : "Mega Drive adapter not implemented");
            blocked++;
        }
    }
    return blocked;
}

static int ReadMd(const char *path,const uint8_t *snes,size_t snes_size) {
    static const uint8_t expected[32] = {
        0xe1,0x12,0xd1,0x81,0x18,0x93,0x04,0xb2,0xd2,0x90,0x0b,0xdc,0x0d,0x6d,0x61,0x52,
        0x11,0xd5,0x47,0xa5,0x44,0x12,0x19,0x21,0x87,0x8c,0x19,0x9e,0x41,0x21,0x70,0xf5};
    snprintf(md_status, sizeof md_status, "Mega Drive ROM unavailable");
    FILE *f = path && *path ? fopen(path, "rb") : NULL;
    if (!f) return 0;
    if (fseek(f, 0, SEEK_END) || ftell(f) != 0x300000 || fseek(f, 0, SEEK_SET)) {
        fclose(f); snprintf(md_status, sizeof md_status, "Mega Drive ROM: unsupported size"); return 0;
    }
    uint8_t *rom = (uint8_t *)malloc(0x300000);
    if (!rom) { fclose(f); return 0; }
    int ok = fread(rom, 1, 0x300000, f) == 0x300000;
    fclose(f);
    uint8_t hash[32]; sha256_compute(rom, ok ? 0x300000 : 0, hash);
    ok = ok && !memcmp(hash, expected, sizeof hash);
    if (ok) {
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
        if(prepare_cache || !TlkMdSpriteAssetsReady())
#endif
        {
        TlkStartDataInit(snes,snes_size,rom,0x300000);
        TlkReactivationDataInit(snes,snes_size,rom,0x300000);
        TlkHitboxDataInit(snes,snes_size,rom,0x300000);
        }
        uint8_t snes_hash[32];sha256_compute(snes,snes_size,snes_hash);
        int cached=!prepare_cache && TlkMdAssetsLoadCache(asset_cache_path,snes_hash,hash);
        if (!cached && (prepare_cache || !*asset_cache_path)) {
            TlkMdAssetsInit(rom,0x300000);TlkMdAssetsBindSnes(snes,snes_size);
            TlkContactMapInit(snes,snes_size,rom,0x300000);
        }
        if(!prepare_cache && *asset_cache_path && !cached) {
            fprintf(stderr,"Prepared scene data is missing or outdated. Run Setup.cmd again.\n");
            snprintf(md_status,sizeof md_status,"Prepared scene data unavailable; run Setup.cmd");free(rom);return 0;
        }
        cache_prepared=cached;
        if (prepare_cache) cache_prepared=TlkMdAssetsSaveCache(asset_cache_path,snes_hash,hash);
        if (*asset_cache_path) fprintf(stderr,"resource_cache=%s\n",prepare_cache?(cache_prepared?"prepared":"prepare_failed"):(cached?"loaded":"miss_decoded_from_rom"));
        TlkMdSpritesInit(rom,0x300000);
        checkpoint_art=TlkCheckpointArtReadFile(checkpoint_asset_path);
        installed_revival_art=TlkRevivalArtReadFile(revival_asset_path);
        installed_native_hud=TlkNativeHudReadFile(native_hud_asset_path);
        if(installed_native_hud)fprintf(stderr,"native_hud_assets=loaded\n");
        if(installed_revival_art)fprintf(stderr,"revival_assets=loaded\n");
        if(checkpoint_art)fprintf(stderr,"checkpoint_assets=loaded\n");
        title_art=TlkTitleArtReadFile(title_asset_path);
        if(title_art)fprintf(stderr,"caption_assets=loaded\n");
#if defined(TLK_PRIDE_FINAL_AVAILABLE) && TLK_PRIDE_FINAL_AVAILABLE
        if(prepare_cache || !TlkMdSpriteAssetsReady())
#endif
        TlkRoarDataInit(snes,snes_size,rom,0x300000);
        TlkMdHudInit(rom,0x300000);
        TlkMdSoundInit(rom,0x300000);
        /* Same reference-verified MD response for scenery and character colours. */
        for (unsigned i = 0; i < 16; i++) {
            unsigned off = 0x1d78aa + i * 2, c = rom[off] * 256u + rom[off+1];
            md_cub[i] = TlkMdColor555(c);
        }
        snprintf(md_status, sizeof md_status, "Mega Drive World ROM verified; Pride Lands graphics ready; %s",
                 TlkMdSoundReady()?"MD audio ready":"MD sound library unavailable");
    } else snprintf(md_status, sizeof md_status, "Mega Drive ROM: unsupported SHA-256");
    free(rom);
    return ok;
}

void TlkResourcesInit(const uint8_t *snes, size_t size, const char *md_path, const char *profile) {
    BindResourceParents();
    TlkCheckpointArtFree(checkpoint_art);checkpoint_art=NULL;
    TlkRevivalArtFree(installed_revival_art);installed_revival_art=NULL;
    TlkNativeHudFree(installed_native_hud);installed_native_hud=NULL;
    TlkTitleArtFree(title_art);title_art=NULL;
    TlkMdAssetsClear();
    TlkMdSpritesClear();
    TlkContactMapClear();
    TlkRoarDataClear();
    TlkStartDataClear();
    TlkReactivationDataClear();
    TlkHitboxDataClear();
    TlkInterlevelDataClear();TlkBonusResultDataClear();TlkCantWaitDataClear();TlkHuntDataClear();
    memset(active, 0, sizeof active); active[0] = TLK_SOURCE_SNES;
    memset(snes_cub, 0, sizeof snes_cub);
    if (snes && size >= 0x7bb3)
        for (unsigned i = 0; i < 16; i++) snes_cub[i] = snes[0x7b93+i*2] | snes[0x7b94+i*2] << 8;
    md_ready = snes && size >= 0x7bb3 && ReadMd(md_path,snes,size);
    if (md_ready) TlkMdSpritesBindSnes(snes,size);
    snprintf(profile_path, sizeof profile_path, "%s", profile ? profile : "resources.ini");
    snprintf(status, sizeof status, "SNES defaults active");
    TlkResourcesRevert();
    FILE *f = fopen(profile_path, "r");
    if (!f) return;
    char line[512], id[128], value[32];
    int schema = 0, invalid = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == ';' || line[0] == '#' || line[0] == '\n') continue;
        if (sscanf(line, "%127s = %31s", id, value) != 2) { invalid = 1; continue; }
        if (!strcmp(id, "schema")) { schema = !strcmp(value, "1"); continue; }
        int i = TlkResourcesFind(id);
        int source = !strcmp(value,"inherit") ? 0 : !strcmp(value,"snes") ? 1 : !strcmp(value,"md") ? 2 : -1;
        if (i < 0 || !TlkResourcesSet(i, source)) invalid = 1;
    }
    fclose(f);
    char reason[256];
    if (invalid || !schema || TlkResourcesValidate(reason, sizeof reason)) {
        TlkResourcesRevert();
        snprintf(status, sizeof status, "Profile rejected; SNES defaults active (file kept)");
    } else {
        memcpy(active, draft, sizeof active);
        snprintf(status, sizeof status, "Saved resource profile loaded");
    }
}

int TlkResourcesApply(void) {
    if (TlkResourcesValidate(status, sizeof status)) return 0;
    if (!TlkResourcesDirty()) { snprintf(status, sizeof status, "No pending changes"); return 1; }
    char temp[2100]; snprintf(temp, sizeof temp, "%s.tmp", profile_path);
    FILE *f = fopen(temp, "w");
    if (!f) { snprintf(status, sizeof status, "Cannot write resource profile"); return 0; }
    int ok = fprintf(f, "; Lion King resource choices\nschema = 1\n") >= 0;
    static const char *names[] = {"inherit", "snes", "md"};
    for (int i = 0; i < COUNT; i++)
        if (fprintf(f, "%s = %s\n", nodes[i].id, names[draft[i]]) < 0) ok = 0;
    if (fclose(f)) ok = 0;
#ifdef _WIN32
    if (ok) ok = MoveFileExA(temp, profile_path, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != 0;
#else
    if (ok) ok = rename(temp, profile_path) == 0;
#endif
    if (!ok) { remove(temp); snprintf(status, sizeof status, "Cannot save profile; active choices unchanged"); return 0; }
    memcpy(active, draft, sizeof active);
    snprintf(status, sizeof status, "Applied and saved");
    return 1;
}

int TlkResourcesSharedPaletteMatches(const uint16_t *cgram) {
    if (!cgram || !md_ready) return 0;
    for (unsigned i=1;i<16;i++) if (cgram[128+i]!=snes_cub[i]) return 0;
    return 1;
}
static uint16_t SharedColor(unsigned index,const uint16_t *cgram,uint16_t original) {
    if (index < 128 || index >= 144 || !TlkResourcesSharedPaletteMatches(cgram)) return original;
    /* Do not recolour transitions, flash palettes, or other users of the bank. */
    return md_cub[index - 128];
}
uint16_t TlkResourcesSharedObjColor(unsigned index,const uint16_t *cgram,uint16_t original) {
    return SharedColor(index,cgram,original);
}
uint16_t TlkResourcesCubColor(unsigned level, unsigned index, const uint16_t *cgram, uint16_t original) {
    const char *id=level>=6 && level<=9 ? "graphics.sprites.simba.adult.palette" : "graphics.sprites.simba.cub.palette";
    if(TlkFallbackEnabled() && TlkResourcesUseMd(id) && index>=128 && index<144 &&
       !TlkResourcesSharedPaletteMatches(cgram))
        TlkFallbackRecord("sampling_failure",id,"simba_palette_guard",0,0,index,1);
    return TlkResourcesUseMd(id)?SharedColor(index,cgram,original):original;
}
uint16_t TlkResourcesHudColor(unsigned index,const uint16_t *cgram,uint16_t original) {
    if(TlkFallbackEnabled() && TlkResourcesUseMd("graphics.hud.palette") && index>=128 && index<144 &&
       !TlkResourcesSharedPaletteMatches(cgram))
        TlkFallbackRecord("sampling_failure","graphics.hud.palette","hud_palette_guard",0,0,index,1);
    return TlkResourcesUseMd("graphics.hud.palette")?SharedColor(index,cgram,original):original;
}
int TlkResourcesCheckpointSample(uint32_t pose,int x,int y,unsigned frames,unsigned palette,const uint16_t *cgram,uint16_t *color) {
    int result=TlkCheckpointArtPoseSample(checkpoint_art,pose,x,y,frames,palette,cgram,color);
    if(result<0 && (frames || palette))
        TlkFallbackRecord("sampling_failure","graphics.sprites.checkpoints","checkpoint_sample_rejected",0,pose,0,1);
    return result;
}
int TlkResourcesTitleBounds(unsigned source,int *x,int *y,int *w,int *h) {
    int result=TlkTitleArtBounds(title_art,source,x,y,w,h);
    if(!result && source)TlkFallbackRecord("sampling_failure","graphics.titles","md_caption_bounds_unavailable",0,0,0,1);
    return result;
}
int TlkResourcesTitleSample(int x,int y,unsigned frames,unsigned palette,const uint16_t *cgram,uint16_t *color) {
    int result=TlkTitleArtSample(title_art,x,y,frames,palette,cgram,color);
    if(result<0 && (frames || palette))TlkFallbackRecord("sampling_failure","graphics.titles","caption_sample_rejected",0,0,0,1);
    return result;
}


unsigned TlkResourcesCaptionMatch(unsigned level,unsigned hint,const uint8_t *packet,size_t size) {
    return TlkTitleArtCaptionMatch(title_art,level,hint,packet,size);
}
int TlkResourcesCaptionBounds(unsigned slot,int *x,int *y,int *w,int *h) {
    return TlkTitleArtCaptionBounds(title_art,slot,x,y,w,h);
}
static const uint16_t *CaptionNativePalette(unsigned slot) {
    unsigned level=slot==15?1:slot?slot-1:0;
    return TlkNextSceneNativeObj(level,0);
}
int TlkResourcesCaptionSample(unsigned slot,int x,int y,unsigned palette,const uint16_t *cgram,uint16_t *color) {
    return TlkTitleArtCaptionSample(title_art,slot,x,y,palette,CaptionNativePalette(slot),cgram,color);
}
int TlkResourcesCaptionColor(unsigned slot,unsigned pixel,const uint16_t *cgram,uint16_t *color) {
    return TlkTitleArtCaptionColor(title_art,slot,pixel,CaptionNativePalette(slot),cgram,color);
}

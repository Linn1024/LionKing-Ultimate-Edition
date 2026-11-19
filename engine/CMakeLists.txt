cmake_minimum_required(VERSION 3.20)
project(TLKRecomp C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Cache repeated compiles, including regenerated sources whose contents did
# not change. Respect an explicitly configured launcher (including an empty
# one), and keep ccache optional for machines that do not have it.
option(TLK_USE_CCACHE "Use ccache when available" ON)
if(TLK_USE_CCACHE)
    find_program(TLK_CCACHE_PROGRAM ccache)
    if(TLK_CCACHE_PROGRAM)
        foreach(lang C CXX)
            if(NOT DEFINED CMAKE_${lang}_COMPILER_LAUNCHER AND
               NOT DEFINED ENV{CMAKE_${lang}_COMPILER_LAUNCHER})
                set(CMAKE_${lang}_COMPILER_LAUNCHER "${TLK_CCACHE_PROGRAM}")
            endif()
        endforeach()
    endif()
endif()

# Linux builds require _GNU_SOURCE for popen / readlink in strict C mode.
add_compile_definitions(_GNU_SOURCE)

set(SNESRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/snesrecomp" CACHE PATH
    "Path to snesrecomp framework submodule")
set(TLK_SNESRECOMP_GEN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/generated/snesrecomp" CACHE PATH
    "Directory containing generated snesrecomp C sources")

file(GLOB GENERATED_SOURCES CONFIGURE_DEPENDS
    "${TLK_SNESRECOMP_GEN_DIR}/*.c")

# Capabilities follow the emitted program, including reference --no-hle builds.
set(TLK_CAMERA_AOT_AVAILABLE OFF)
set(TLK_RNG_ENTRY_AOT_AVAILABLE OFF)
set(TLK_LAYOUT_AOT_AVAILABLE OFF)
set(TLK_START_LOADS "")
set(TLK_SPAWN_INIT_ENTRIES "")
set(TLK_STREAMING_WINDOW_AOT_AVAILABLE OFF)
set(TLK_HITBOX_ENTRIES "")
set(TLK_REACTIVATION_AOT_AVAILABLE OFF)
set(TLK_LEAF_EMITTER_AOT_AVAILABLE OFF)
set(TLK_LEAF_PARTICLE_AOT_AVAILABLE OFF)
set(TLK_TERRAIN_DISPATCHES "")
set(TLK_ROAR_AOT_AVAILABLE OFF)
set(TLK_HYENA_TAUNT_AOT_AVAILABLE OFF)
set(TLK_LIZARD_DEFEAT_AOT_AVAILABLE OFF)
set(TLK_LIZARD_LAUNCH_AOT_AVAILABLE OFF)
set(TLK_PICKUP_ARRIVAL_AOT_AVAILABLE OFF)
set(TLK_LEDGE_GRAB_AOT_AVAILABLE OFF)
set(TLK_LEDGE_AUDIO_ENTRIES "")
foreach(source IN LISTS GENERATED_SOURCES)
    if(source MATCHES "bankc5_part[0-9a-f]+_v2.c$")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${source}")
        file(READ "${source}" pickup_unit)
        if(pickup_unit MATCHES "TlkPickupArrivalDispatch\\(cpu\\)")
            set(TLK_PICKUP_ARRIVAL_AOT_AVAILABLE ON)
        endif()
    endif()
    if(source MATCHES "bankc0_part[0-9a-f]+_v2.c$")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${source}")
        file(READ "${source}" camera_unit)
        if(camera_unit MATCHES "TlkRngEntryDispatch\\(cpu\\)")
            set(TLK_RNG_ENTRY_AOT_AVAILABLE ON)
        endif()
        if(camera_unit MATCHES "TlkStreamingWindowDispatch\\(cpu\\)")
            set(TLK_STREAMING_WINDOW_AOT_AVAILABLE ON)
        endif()
        foreach(kind Body Player)
            if(camera_unit MATCHES "Tlk${kind}BoundsDispatch\\(cpu\\)")
                list(APPEND TLK_HITBOX_ENTRIES "${kind}")
            endif()
        endforeach()
        if(camera_unit MATCHES "aot_pace_point\\(cpu, _aot_cy, _aot_mc, 0xC0CC36u\\)")
            set(TLK_REACTIVATION_AOT_AVAILABLE ON)
        endif()
        if(camera_unit MATCHES "TlkCameraDispatch\\(cpu\\)")
            set(TLK_CAMERA_AOT_AVAILABLE ON)
        endif()
        if(camera_unit MATCHES "TlkMarkerDispatch\\(cpu\\)")
            set(TLK_LAYOUT_AOT_AVAILABLE ON)
        endif()
        foreach(kind Initial Stream CameraReturn Scan)
            if(camera_unit MATCHES "TlkSpawn${kind}Dispatch\\(cpu\\)")
                list(APPEND TLK_SPAWN_INIT_ENTRIES "${kind}")
            endif()
        endforeach()
          foreach(point C07763 C0867B C08687)
              if(camera_unit MATCHES "aot_pace_point\\(cpu, _aot_cy, _aot_mc, 0x${point}u\\)")
                  list(APPEND TLK_START_LOADS "${point}")
              endif()
          endforeach()
          foreach(kind Floor Right RightActor Left LeftActor Wall Ledge Ceiling)
            if(camera_unit MATCHES "TlkTerrain${kind}Dispatch\\(cpu\\)")
                list(APPEND TLK_TERRAIN_DISPATCHES "${kind}")
            endif()
        endforeach()
    endif()
    if(source MATCHES "bankc3_part[0-9a-f]+_v2.c$")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${source}")
        file(READ "${source}" roar_unit)
        if(roar_unit MATCHES "TlkRoarHandlerDispatch\\(cpu\\)")
            set(TLK_ROAR_AOT_AVAILABLE ON)
        endif()
        foreach(kind Left Right)
            if(roar_unit MATCHES "TlkLedge${kind}Dispatch\\(cpu\\)")
                list(APPEND TLK_LEDGE_AUDIO_ENTRIES "${kind}")
            endif()
        endforeach()
    endif()
    if(source MATCHES "bankc1_part[0-9a-f]+_v2.c$")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${source}")
        file(READ "${source}" leaf_unit)
        if(leaf_unit MATCHES "TlkLizardLaunchDispatch\\(cpu\\)")
            set(TLK_LIZARD_LAUNCH_AOT_AVAILABLE ON)
        endif()
        if(leaf_unit MATCHES "TlkLizardDefeatDispatch\\(cpu\\)")
            set(TLK_LIZARD_DEFEAT_AOT_AVAILABLE ON)
        endif()
        if(leaf_unit MATCHES "TlkHyenaTauntDispatch\\(cpu\\)")
            set(TLK_HYENA_TAUNT_AOT_AVAILABLE ON)
        endif()
        if(leaf_unit MATCHES "TlkLeafEmitterDispatch\\(cpu\\)")
            set(TLK_LEAF_EMITTER_AOT_AVAILABLE ON)
        endif()
        if(leaf_unit MATCHES "TlkLeafParticleDispatch\\(cpu\\)")
            set(TLK_LEAF_PARTICLE_AOT_AVAILABLE ON)
        endif()
    endif()
endforeach()
list(REMOVE_DUPLICATES TLK_LEDGE_AUDIO_ENTRIES)
list(LENGTH TLK_LEDGE_AUDIO_ENTRIES TLK_LEDGE_AUDIO_ENTRY_COUNT)
if(TLK_LEDGE_AUDIO_ENTRY_COUNT EQUAL 2)
    set(TLK_LEDGE_GRAB_AOT_AVAILABLE ON)
endif()
set(TLK_LEAVES_AOT_AVAILABLE OFF)
list(REMOVE_DUPLICATES TLK_HITBOX_ENTRIES)
list(LENGTH TLK_HITBOX_ENTRIES TLK_HITBOX_ENTRY_COUNT)
set(TLK_HITBOX_AOT_AVAILABLE OFF)
if(TLK_HITBOX_ENTRY_COUNT EQUAL 2)
    set(TLK_HITBOX_AOT_AVAILABLE ON)
endif()
list(REMOVE_DUPLICATES TLK_START_LOADS)
list(LENGTH TLK_START_LOADS TLK_START_LOAD_COUNT)
set(TLK_START_AOT_AVAILABLE OFF)
list(REMOVE_DUPLICATES TLK_SPAWN_INIT_ENTRIES)
list(LENGTH TLK_SPAWN_INIT_ENTRIES TLK_SPAWN_INIT_ENTRY_COUNT)
set(TLK_SPAWN_INIT_AOT_AVAILABLE OFF)
if(TLK_SPAWN_INIT_ENTRY_COUNT EQUAL 4)
    set(TLK_SPAWN_INIT_AOT_AVAILABLE ON)
endif()
set(TLK_STREAMING_TOP_AOT_AVAILABLE OFF)
if(TLK_STREAMING_WINDOW_AOT_AVAILABLE AND TLK_SPAWN_INIT_AOT_AVAILABLE)
    set(TLK_STREAMING_TOP_AOT_AVAILABLE ON)
endif()
if(TLK_START_LOAD_COUNT EQUAL 3)
    set(TLK_START_AOT_AVAILABLE ON)
endif()
list(REMOVE_DUPLICATES TLK_TERRAIN_DISPATCHES)
list(LENGTH TLK_TERRAIN_DISPATCHES TLK_TERRAIN_DISPATCH_COUNT)
set(TLK_TERRAIN_AOT_AVAILABLE OFF)
if(TLK_TERRAIN_DISPATCH_COUNT EQUAL 8)
    set(TLK_TERRAIN_AOT_AVAILABLE ON)
endif()
if(TLK_LEAF_EMITTER_AOT_AVAILABLE AND TLK_LEAF_PARTICLE_AOT_AVAILABLE)
    set(TLK_LEAVES_AOT_AVAILABLE ON)
endif()
configure_file(cmake/native_adapters.h.in "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources/native_adapters.h")

if(NOT GENERATED_SOURCES)
    message(WARNING
        "No generated sources found in ${TLK_SNESRECOMP_GEN_DIR}. "
        "Run `python3 scripts/generate_snesrecomp.py` to generate them.")
endif()

# Compile the game once for both hosts. An OBJECT library also retains the
# generated module-registration constructor, which a static archive linker
# could otherwise discard because no host references that object directly.
add_library(snesrecomp_game OBJECT)
target_include_directories(snesrecomp_game PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/recomp"
    "${CMAKE_CURRENT_SOURCE_DIR}/runner"
    "${SNESRECOMP_ROOT}/runner/src"
    "${SNESRECOMP_ROOT}/runner/src/snes")

if(NOT MSVC)
    target_compile_options(snesrecomp_game PRIVATE
        -w -Wno-implicit-function-declaration)
endif()

# ── Hosts ─────────────────────────────────────────────────────────────────
# tlk_headless: windowless validation host (runner/headless_main.c).
# tlk_sdl:      playable SDL3 host (runner/sdl_main.c) on the headless
#               emulation path: window, audio, pacing, input.
# Both compile the runner and TLK adapter, and share the generated objects;
# SNESRECOMP_ENABLE_MODS must precede the include (runner.cmake reads it).
option(TLK_BUILD_HOSTS "Build tlk_headless and tlk_sdl" ON)
# TLK_STATIC_SDL: ignore any installed SDL3 and link the pinned SDL3 release
# (snesrecomp's SNESRECOMP_SDL3_FETCH, 3.4.10, sha256-checked) statically, so
# the player tarball runs without SDL3 installed (scripts/package.sh). The
# video/audio/input backends are compiled in and dlopen their system libraries
# at run time. Default OFF: dev builds keep using the system SDL3.
option(TLK_STATIC_SDL "Build and statically link the pinned SDL3 release" OFF)
if(TLK_STATIC_SDL)
    set(CMAKE_DISABLE_FIND_PACKAGE_SDL3 ON)
    set(SNESRECOMP_SDL3_FETCH ON CACHE BOOL "" FORCE)
    set(SNESRECOMP_SDL_BACKEND "SDL3" CACHE STRING "" FORCE)
    set(_tlk_sdl_opts SDL_VIDEO SDL_AUDIO SDL_JOYSTICK SDL_HIDAPI SDL_HIDAPI_JOYSTICK SDL_OPENGL)
    # Windows (MinGW cross build, cmake/mingw-w64-x86_64.cmake) uses SDL's
    # own Win32 backends; the Linux ones below do not exist there.
    if(NOT WIN32)
        list(APPEND _tlk_sdl_opts
             SDL_WAYLAND SDL_WAYLAND_SHARED SDL_X11 SDL_X11_SHARED
             SDL_PIPEWIRE SDL_PIPEWIRE_SHARED SDL_PULSEAUDIO SDL_PULSEAUDIO_SHARED
             SDL_ALSA SDL_ALSA_SHARED SDL_LIBUDEV SDL_DBUS SDL_KMSDRM)
    endif()
    foreach(_opt IN LISTS _tlk_sdl_opts)
        set(${_opt} ON CACHE BOOL "" FORCE)
    endforeach()
endif()
if(TLK_BUILD_HOSTS)
    if(NOT EXISTS "${SNESRECOMP_ROOT}/runner/runner.cmake")
        message(FATAL_ERROR "snesrecomp submodule missing at ${SNESRECOMP_ROOT}")
    endif()
    set(SNESRECOMP_ENABLE_MODS ON CACHE BOOL
        "Mod package loader + trusted plugins (required by the desktop host)" FORCE)
    include("${SNESRECOMP_ROOT}/runner/runner.cmake")
    snesrecomp_target_generated_code(snesrecomp_game "${TLK_SNESRECOMP_GEN_DIR}")
    if(GENERATED_SOURCES)
        target_compile_definitions(snesrecomp_game INTERFACE SNESRECOMP_HAS_GENERATED_CODE=1)
    else()
        target_compile_definitions(snesrecomp_game INTERFACE SNESRECOMP_SETUP_HOST=1)
    endif()
    # Runtime adaptations: patched build-dir copies of pinned snesrecomp
    # sources (cmake/runtime-patches/*.hunks); the submodule stays untouched.
    include(cmake/TlkRuntimePatches.cmake)
    tlk_use_patched_runtime_sources(SNESRECOMP_RUNNER_SOURCES)

    set(TLK_RUNNER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/runner")
    set(TLK_COMMON_SOURCES
        ${SNESRECOMP_RUNNER_SOURCES}
        ${TLK_RUNNER_DIR}/tlk_game.c
        ${TLK_RUNNER_DIR}/tlk_decomp.c
        ${TLK_RUNNER_DIR}/aot_pace.c
        ${TLK_RUNNER_DIR}/tlk_fiber.c
        ${TLK_RUNNER_DIR}/tlk_savestate.c
        ${TLK_RUNNER_DIR}/tlk_wide.c
        ${TLK_RUNNER_DIR}/tlk_resources.c
        ${TLK_RUNNER_DIR}/tlk_fallback_log.c
        ${TLK_RUNNER_DIR}/tlk_md_assets.c
        ${TLK_RUNNER_DIR}/tlk_audio.c
        ${TLK_RUNNER_DIR}/tlk_hyena_audio.c
        ${TLK_RUNNER_DIR}/tlk_lizard_audio.c
        ${TLK_RUNNER_DIR}/tlk_pickup_audio.c
        ${TLK_RUNNER_DIR}/tlk_ledge_audio.c
        ${TLK_RUNNER_DIR}/tlk_md_sound.c
        ${TLK_RUNNER_DIR}/tlk_md_sprites.c
        ${TLK_RUNNER_DIR}/tlk_md_hud.c
        ${TLK_RUNNER_DIR}/tlk_md_camera.c
        ${TLK_RUNNER_DIR}/tlk_camera.c
        ${TLK_RUNNER_DIR}/tlk_guest.c
        ${TLK_RUNNER_DIR}/tlk_layout.c
        ${TLK_RUNNER_DIR}/tlk_start_data.c
        ${TLK_RUNNER_DIR}/tlk_pride_data.c
        ${TLK_RUNNER_DIR}/tlk_rng_entry.c
        ${TLK_RUNNER_DIR}/tlk_rng_runtime.c
        ${TLK_RUNNER_DIR}/tlk_temp_path.c
        ${TLK_RUNNER_DIR}/tlk_spawn_init.c
        ${TLK_RUNNER_DIR}/tlk_reactivation.c
        ${TLK_RUNNER_DIR}/tlk_reactivation_data.c
        ${TLK_RUNNER_DIR}/tlk_hitboxes.c
        ${TLK_RUNNER_DIR}/tlk_ceiling.c
        ${TLK_RUNNER_DIR}/tlk_streaming_top.c
        ${TLK_RUNNER_DIR}/tlk_hitbox_data.c
        ${TLK_RUNNER_DIR}/tlk_contact_map.c
        ${TLK_RUNNER_DIR}/tlk_terrain.c
        ${TLK_RUNNER_DIR}/tlk_roar_data.c
        ${TLK_RUNNER_DIR}/tlk_roar.c
        ${TLK_RUNNER_DIR}/tlk_leaves.c
        ${TLK_RUNNER_DIR}/host_contract.c)

    function(tlk_configure_target target)
        target_include_directories(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources")
        target_include_directories(${target} PRIVATE
            ${SNESRECOMP_RUNNER_INCLUDE_DIRS}
            ${SNESRECOMP_ROOT}/runner/src/desktop
            ${TLK_RUNNER_DIR}
            ${CMAKE_CURRENT_SOURCE_DIR}/recomp)
        target_link_libraries(${target} PRIVATE snesrecomp_game ${SNESRECOMP_RUNNER_LIBRARIES} ${CMAKE_DL_LIBS} tlk_checkpoint_art tlk_title_art)
        target_compile_definitions(${target} PRIVATE
            SNES_GAME_VERSION="dev"
            SNES_GAME_TITLE="The Lion King")
        snesrecomp_rom_identity(${target} "${CMAKE_CURRENT_SOURCE_DIR}/cmake/rom_identity.txt")
    endfunction()

    add_executable(tlk_headless ${TLK_COMMON_SOURCES}
        ${TLK_RUNNER_DIR}/headless_main.c
        ${TLK_RUNNER_DIR}/tlk_rommap.c
        ${TLK_RUNNER_DIR}/tlk_callpair.c
        ${TLK_RUNNER_DIR}/headless_host.c
        ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_headless)
    snesrecomp_target_mmx_config(tlk_headless)
    # common_rtl.c includes the SDL compat header; no window is ever opened.
    snesrecomp_target_sdl(tlk_headless)

    # Explicit research target only: observe end-of-field palettes without
    # adding diagnostics or changing code in either distributed host.
    add_executable(tlk_cant_wait_capture EXCLUDE_FROM_ALL ${TLK_COMMON_SOURCES}
        ${CMAKE_CURRENT_SOURCE_DIR}/../tools/cant_wait_native_capture.c
        ${TLK_RUNNER_DIR}/tlk_rommap.c ${TLK_RUNNER_DIR}/tlk_callpair.c
        ${TLK_RUNNER_DIR}/headless_host.c ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_cant_wait_capture)
    snesrecomp_target_mmx_config(tlk_cant_wait_capture)
    snesrecomp_target_sdl(tlk_cant_wait_capture)

    add_executable(tlk_pride_reload_probe EXCLUDE_FROM_ALL ${TLK_COMMON_SOURCES}
        ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_reload_probe.c
        ${TLK_RUNNER_DIR}/tlk_rommap.c ${TLK_RUNNER_DIR}/tlk_callpair.c
        ${TLK_RUNNER_DIR}/headless_host.c ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_pride_reload_probe)
    snesrecomp_target_mmx_config(tlk_pride_reload_probe)
    snesrecomp_target_sdl(tlk_pride_reload_probe)

    add_executable(tlk_native_bank_probe EXCLUDE_FROM_ALL ${TLK_COMMON_SOURCES}
        runner/tlk_native_bank.c ${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_native_bank_probe.c
        ${TLK_RUNNER_DIR}/tlk_rommap.c ${TLK_RUNNER_DIR}/tlk_callpair.c
        ${TLK_RUNNER_DIR}/headless_host.c ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_native_bank_probe)
    snesrecomp_target_mmx_config(tlk_native_bank_probe)
    snesrecomp_target_sdl(tlk_native_bank_probe)

    add_executable(tlk_scene_prepare_probe EXCLUDE_FROM_ALL ${TLK_COMMON_SOURCES}
        runner/tlk_native_bank.c "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_prepare_probe.c"
        ${TLK_RUNNER_DIR}/tlk_rommap.c ${TLK_RUNNER_DIR}/tlk_callpair.c
        ${TLK_RUNNER_DIR}/headless_host.c ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_scene_prepare_probe)
    snesrecomp_target_mmx_config(tlk_scene_prepare_probe)
    snesrecomp_target_sdl(tlk_scene_prepare_probe)

    add_executable(tlk_native_bank_test EXCLUDE_FROM_ALL ${TLK_COMMON_SOURCES}
        runner/tlk_native_bank.c tests/native_bank_test.c
        ${TLK_RUNNER_DIR}/tlk_rommap.c ${TLK_RUNNER_DIR}/tlk_callpair.c
        ${TLK_RUNNER_DIR}/headless_host.c ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_native_bank_test)
    snesrecomp_target_mmx_config(tlk_native_bank_test)
    snesrecomp_target_sdl(tlk_native_bank_test)

    add_executable(tlk_resources_test
        tests/resources_test.c runner/tlk_resources.c runner/tlk_md_assets.c runner/tlk_md_sound.c runner/tlk_md_sprites.c runner/tlk_md_hud.c runner/tlk_contact_map.c runner/tlk_roar_data.c runner/tlk_start_data.c runner/tlk_reactivation_data.c runner/tlk_hitbox_data.c
        "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_resources_test PRIVATE
        runner "${SNESRECOMP_ROOT}/runner/src" "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources")
    add_executable(tlk_md_assets_test tests/md_assets_test.c runner/tlk_md_assets.c runner/tlk_contact_map.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_md_assets_test PRIVATE runner "${SNESRECOMP_ROOT}/runner/src")
    add_executable(tlk_cant_wait_background_test tests/cant_wait_background_test.c runner/tlk_md_assets.c runner/tlk_contact_map.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_cant_wait_background_test PRIVATE runner "${SNESRECOMP_ROOT}/runner/src")
    foreach(_tlk_log_test tlk_resources_test tlk_md_assets_test tlk_cant_wait_background_test)
        target_sources(${_tlk_log_test} PRIVATE runner/tlk_fallback_log.c)
    endforeach()
    add_executable(tlk_fallback_log_test tests/fallback_log_test.c runner/tlk_fallback_log.c)
    target_include_directories(tlk_fallback_log_test PRIVATE runner)
    add_executable(tlk_md_sound_test tests/md_sound_test.c runner/tlk_md_sound.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    add_executable(tlk_md_sound_state_test tests/md_sound_state_test.c runner/tlk_md_sound.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    add_executable(tlk_health_death_audio_test tests/health_death_audio_test.c runner/tlk_audio.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_health_death_audio_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    add_library(tlk_death_scene STATIC runner/tlk_death_scene.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_death_scene PUBLIC runner PRIVATE "${SNESRECOMP_ROOT}/runner/src")
    add_executable(tlk_death_scene_test tests/death_scene_test.c)
    target_link_libraries(tlk_death_scene_test PRIVATE tlk_death_scene)
    add_executable(tlk_revival_scene_test tests/revival_scene_test.c)
    target_link_libraries(tlk_revival_scene_test PRIVATE tlk_death_scene)
    add_library(tlk_revival_art STATIC EXCLUDE_FROM_ALL runner/tlk_revival_art.c)
    target_include_directories(tlk_revival_art PRIVATE "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_revival_art PUBLIC tlk_death_scene)
    add_library(tlk_revival_art_prepare STATIC EXCLUDE_FROM_ALL runner/tlk_revival_art.c)
    target_compile_definitions(tlk_revival_art_prepare PRIVATE TLK_REVIVAL_ART_PREPARE=1)
    target_include_directories(tlk_revival_art_prepare PRIVATE "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_revival_art_prepare PUBLIC tlk_death_scene)
    add_library(tlk_checkpoint_art STATIC runner/tlk_checkpoint_art.c)
    target_include_directories(tlk_checkpoint_art PRIVATE "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_checkpoint_art PUBLIC tlk_revival_art)
    add_library(tlk_title_art STATIC runner/tlk_title_art.c)
    target_include_directories(tlk_title_art PRIVATE "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_title_art PUBLIC tlk_revival_art)
    target_link_libraries(tlk_resources_test PRIVATE tlk_checkpoint_art tlk_title_art)
    add_executable(tlk_revival_art_test EXCLUDE_FROM_ALL tests/revival_art_test.c)
    target_link_libraries(tlk_revival_art_test PRIVATE tlk_revival_art_prepare)
    target_include_directories(tlk_death_scene_test PRIVATE "${SNESRECOMP_ROOT}/runner/src")
    add_executable(tlk_death_art_test tests/death_art_test.c runner/tlk_md_sprites.c runner/tlk_md_assets.c runner/tlk_contact_map.c)
    target_include_directories(tlk_death_art_test PRIVATE runner "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources" "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_death_art_test PRIVATE tlk_death_scene)
    target_include_directories(tlk_md_sound_state_test PRIVATE runner "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_md_sound_state_test PRIVATE ${CMAKE_DL_LIBS})
    add_executable(tlk_md_hud_test tests/md_hud_test.c runner/tlk_md_hud.c)
    target_include_directories(tlk_md_hud_test PRIVATE runner)
    add_executable(tlk_md_camera_test tests/md_camera_test.c runner/tlk_md_camera.c)
    add_executable(tlk_contact_map_test tests/contact_map_test.c runner/tlk_contact_map.c runner/tlk_md_assets.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_contact_map_test PRIVATE runner "${SNESRECOMP_ROOT}/runner/src")
    add_executable(tlk_terrain_hook_test tests/terrain_hook_test.c runner/tlk_terrain.c runner/tlk_contact_map.c runner/tlk_md_assets.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_terrain_hook_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    add_executable(tlk_roar_test tests/roar_test.c runner/tlk_roar.c runner/tlk_roar_data.c runner/tlk_md_sprites.c runner/tlk_md_assets.c runner/tlk_contact_map.c "${SNESRECOMP_ROOT}/runner/src/sha256.c")
    target_include_directories(tlk_roar_test PRIVATE runner "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources" ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    add_executable(tlk_hyena_audio_test tests/hyena_audio_test.c runner/tlk_hyena_audio.c)
    target_include_directories(tlk_hyena_audio_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    add_executable(tlk_lizard_audio_test tests/lizard_audio_test.c runner/tlk_lizard_audio.c)
    add_executable(tlk_start_test tests/start_test.c runner/tlk_layout.c runner/tlk_start_data.c)
    target_include_directories(tlk_start_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    foreach(_tlk_log_test tlk_health_death_audio_test tlk_death_art_test tlk_contact_map_test tlk_terrain_hook_test tlk_roar_test)
        target_sources(${_tlk_log_test} PRIVATE runner/tlk_fallback_log.c)
    endforeach()
    add_executable(tlk_spawn_init_test tests/spawn_init_test.c runner/tlk_spawn_init.c)
    target_include_directories(tlk_spawn_init_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    add_executable(tlk_reactivation_test tests/reactivation_test.c runner/tlk_reactivation.c runner/tlk_reactivation_data.c)
    add_executable(tlk_hitboxes_test tests/hitboxes_test.c runner/tlk_hitboxes.c runner/tlk_hitbox_data.c)
    add_executable(tlk_ceiling_test tests/ceiling_test.c runner/tlk_ceiling.c runner/tlk_hitbox_data.c)
    add_executable(tlk_streaming_top_test tests/streaming_top_test.c runner/tlk_streaming_top.c)
    target_include_directories(tlk_streaming_top_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    target_include_directories(tlk_ceiling_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS} "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources")
    target_include_directories(tlk_hitboxes_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS} "${CMAKE_CURRENT_SOURCE_DIR}/generated/resources")
    target_include_directories(tlk_reactivation_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    target_include_directories(tlk_lizard_audio_test PRIVATE runner ${SNESRECOMP_RUNNER_INCLUDE_DIRS})
    target_include_directories(tlk_md_camera_test PRIVATE runner)
    target_include_directories(tlk_md_sound_test PRIVATE runner "${SNESRECOMP_ROOT}/runner/src")
    target_link_libraries(tlk_resources_test PRIVATE ${CMAKE_DL_LIBS})
    target_link_libraries(tlk_md_sound_test PRIVATE ${CMAKE_DL_LIBS})

    # tlk_sdl: same sources and host contract as tlk_headless (so the same
    # frame driver and APU timeline), plus a small SDL3 front end for window,
    # audio, pacing and input. Not the framework desktop host: that one turns
    # on extended frame timing, which bypasses TLK's NTSC SPC ratio.
    add_executable(tlk_sdl ${TLK_COMMON_SOURCES}
        ${TLK_RUNNER_DIR}/sdl_main.c
        ${TLK_RUNNER_DIR}/tlk_video.c
        ${TLK_RUNNER_DIR}/tlk_assets.c
        ${TLK_RUNNER_DIR}/headless_host.c
        ${TLK_RUNNER_DIR}/verified_rom.c)
    tlk_configure_target(tlk_sdl)
    # The vendored GL loader only detects MSVC's stdcall macros. MinGW x86
    # needs the same ABI explicitly; otherwise the first GL call corrupts ESP.
    if(WIN32 AND MINGW AND CMAKE_SIZEOF_VOID_P EQUAL 4)
        target_compile_definitions(tlk_sdl PRIVATE GL_APIENTRY=__stdcall)
    endif()
    snesrecomp_target_sdl(tlk_sdl)
    # OpenGL presenter + GLSL presets (CC0), staged to build/assets/shaders.
    snesrecomp_target_opengl(tlk_sdl)
    snesrecomp_target_shader_presets(tlk_sdl)
    tlk_use_patched_target_sources(tlk_sdl)
    # In-game settings menu: recomp-ui's runtime menu (MIT, submodule), drawn
    # with Dear ImGui over the OpenGL presenter (runner/tlk_menu_imgui.cpp).
    # Its fonts and images are staged to build/assets/fonts and assets/img.
    # FreeType/HarfBuzz would only colour netplay-chat emoji, and the release
    # binary must not need either installed: keep recomp-ui from finding them.
    set(CMAKE_DISABLE_FIND_PACKAGE_Freetype ON)
    set(RECOMP_UI_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/recomp-ui" CACHE PATH "" FORCE)
    include("${RECOMP_UI_ROOT}/recomp_ui.cmake")
    target_sources(tlk_sdl PRIVATE ${TLK_RUNNER_DIR}/tlk_menu_imgui.cpp)
    recomp_target_launcher_ui(tlk_sdl CONSOLE snes)
    # The font and shader presets, compiled in for the single Windows .exe
    # (runner/tlk_assets.c). The font comes first: it is the file probed.
    include(cmake/TlkEmbedAssets.cmake)
    set(tlk_shader_dir "${SNESRECOMP_ROOT}/runner/assets/shaders")
    file(GLOB_RECURSE tlk_shader_files RELATIVE "${tlk_shader_dir}" CONFIGURE_DEPENDS
         "${tlk_shader_dir}/*.glslp" "${tlk_shader_dir}/*.glsl")
    set(tlk_embedded
        "assets/fonts/LatoLatin-Regular.ttf=${RECOMP_UI_ROOT}/assets/common/fonts/LatoLatin-Regular.ttf")
    foreach(f IN LISTS tlk_shader_files)
        list(APPEND tlk_embedded "assets/shaders/${f}=${tlk_shader_dir}/${f}")
    endforeach()
    tlk_embed_assets(tlk_sdl "${CMAKE_CURRENT_BINARY_DIR}/tlk_assets_data.c" ${tlk_embedded})
    # Windows: the app icon (packaging/icon, tools/make_icon.py).
    if(WIN32)
        enable_language(RC)
        target_sources(tlk_sdl PRIVATE packaging/tlk_sdl.rc)
    endif()
    # Isolated SDL/PCM integration of the same prepared-bank boundary probe.
    # Reuse the actual player's presentation/UI configuration without changing
    # its sources or enabling the experiment in the distributed executable.
    get_target_property(tlk_bank_sdl_sources tlk_sdl SOURCES)
    list(FILTER tlk_bank_sdl_sources EXCLUDE REGEX "/sdl_main\\.c$")
    add_executable(tlk_native_bank_sdl EXCLUDE_FROM_ALL ${tlk_bank_sdl_sources}
        runner/tlk_native_bank.c "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_native_bank_probe.c")
    foreach(tlk_bank_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                              LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
        get_target_property(tlk_bank_value tlk_sdl ${tlk_bank_property})
        if(tlk_bank_value)
            set_property(TARGET tlk_native_bank_sdl PROPERTY ${tlk_bank_property} "${tlk_bank_value}")
        endif()
    endforeach()
    target_compile_definitions(tlk_native_bank_sdl PRIVATE TLK_NATIVE_BANK_SDL=1)
    get_target_property(tlk_scene_sdl_sources tlk_native_bank_sdl SOURCES)
    list(FILTER tlk_scene_sdl_sources EXCLUDE REGEX "/pride_native_bank_probe\\.c$")
    add_executable(tlk_scene_prepare_sdl EXCLUDE_FROM_ALL ${tlk_scene_sdl_sources}
        "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_prepare_probe.c")
    foreach(tlk_scene_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                               LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
        get_target_property(tlk_scene_value tlk_native_bank_sdl ${tlk_scene_property})
        if(tlk_scene_value)
            set_property(TARGET tlk_scene_prepare_sdl PROPERTY ${tlk_scene_property} "${tlk_scene_value}")
        endif()
    endforeach()
    # Native preparation/wait ownership under the standalone MD scene clock.
    foreach(tlk_owner_variant probe sdl)
        set(tlk_owner_base tlk_scene_prepare_${tlk_owner_variant})
        get_target_property(tlk_owner_sources ${tlk_owner_base} SOURCES)
        list(FILTER tlk_owner_sources EXCLUDE REGEX "/pride_scene_prepare_probe\\.c$")
        add_executable(tlk_scene_owner_${tlk_owner_variant} EXCLUDE_FROM_ALL ${tlk_owner_sources}
            runner/tlk_death_scene.c "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_owner_probe.c")
        foreach(tlk_owner_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                                   LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
            get_target_property(tlk_owner_value ${tlk_owner_base} ${tlk_owner_property})
            if(tlk_owner_value)
                set_property(TARGET tlk_scene_owner_${tlk_owner_variant} PROPERTY ${tlk_owner_property} "${tlk_owner_value}")
            endif()
        endforeach()
    endforeach()
    foreach(tlk_restore_variant probe sdl)
        set(tlk_restore_base tlk_scene_owner_${tlk_restore_variant})
        get_target_property(tlk_restore_sources ${tlk_restore_base} SOURCES)
        list(FILTER tlk_restore_sources EXCLUDE REGEX "/pride_scene_owner_probe\\.c$")
        add_executable(tlk_scene_restore_${tlk_restore_variant} EXCLUDE_FROM_ALL ${tlk_restore_sources}
            "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_restore_probe.c")
        foreach(tlk_restore_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                                     LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
            get_target_property(tlk_restore_value ${tlk_restore_base} ${tlk_restore_property})
            if(tlk_restore_value)
                set_property(TARGET tlk_scene_restore_${tlk_restore_variant} PROPERTY ${tlk_restore_property} "${tlk_restore_value}")
            endif()
        endforeach()
    endforeach()
    # Scene-owned presentation experiment; distributed compositor stays intact.
    foreach(tlk_render_variant probe sdl)
        set(tlk_render_base tlk_scene_restore_${tlk_render_variant})
        get_target_property(tlk_render_sources ${tlk_render_base} SOURCES)
        list(FILTER tlk_render_sources EXCLUDE REGEX "/pride_scene_restore_probe\\.c$")
        list(FILTER tlk_render_sources EXCLUDE REGEX "/tlk_wide\\.c$")
        add_executable(tlk_scene_render_${tlk_render_variant} EXCLUDE_FROM_ALL ${tlk_render_sources}
            runner/tlk_revival_art.c
            "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_render_probe.c"
            "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_render_wide.c")
        foreach(tlk_render_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                                    LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
            get_target_property(tlk_render_value ${tlk_render_base} ${tlk_render_property})
            if(tlk_render_value)
                set_property(TARGET tlk_scene_render_${tlk_render_variant} PROPERTY ${tlk_render_property} "${tlk_render_value}")
            endif()
        endforeach()
    endforeach()
    get_target_property(tlk_oam_sources tlk_scene_restore_probe SOURCES)
    list(FILTER tlk_oam_sources EXCLUDE REGEX "/pride_scene_restore_probe\\.c$")
    list(FILTER tlk_oam_sources EXCLUDE REGEX "/tlk_wide\\.c$")
    add_executable(tlk_scene_oam_probe EXCLUDE_FROM_ALL ${tlk_oam_sources}
        "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_render_probe.c"
        "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_oam_audit.c")
    foreach(tlk_oam_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                             LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
        get_target_property(tlk_oam_value tlk_scene_restore_probe ${tlk_oam_property})
        if(tlk_oam_value)
            set_property(TARGET tlk_scene_oam_probe PROPERTY ${tlk_oam_property} "${tlk_oam_value}")
        endif()
    endforeach()
    get_target_property(tlk_hud_oracle_sources tlk_headless SOURCES)
    list(FILTER tlk_hud_oracle_sources EXCLUDE REGEX "/headless_main\\.c$")
    add_executable(tlk_native_hud_oracle EXCLUDE_FROM_ALL ${tlk_hud_oracle_sources}
        runner/tlk_native_hud.c "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_native_hud_oracle.c")
    foreach(tlk_hud_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                             LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
        get_target_property(tlk_hud_value tlk_headless ${tlk_hud_property})
        if(tlk_hud_value)
            set_property(TARGET tlk_native_hud_oracle PROPERTY ${tlk_hud_property} "${tlk_hud_value}")
        endif()
    endforeach()
    target_compile_definitions(tlk_native_hud_oracle PRIVATE TLK_NATIVE_HUD_PREPARE=1)
    foreach(tlk_prepared_variant probe sdl)
        set(tlk_prepared_base tlk_scene_render_${tlk_prepared_variant})
        get_target_property(tlk_prepared_sources ${tlk_prepared_base} SOURCES)
        list(FILTER tlk_prepared_sources EXCLUDE REGEX "/pride_scene_render_wide\\.c$")
        add_executable(tlk_scene_prepared_${tlk_prepared_variant} EXCLUDE_FROM_ALL ${tlk_prepared_sources}
            runner/tlk_native_hud.c "${CMAKE_CURRENT_SOURCE_DIR}/../tools/pride_scene_prepared_objects.c")
        foreach(tlk_prepared_property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS
                                      LINK_LIBRARIES LINK_OPTIONS LINK_DIRECTORIES)
            get_target_property(tlk_prepared_value ${tlk_prepared_base} ${tlk_prepared_property})
            if(tlk_prepared_value)
                set_property(TARGET tlk_scene_prepared_${tlk_prepared_variant} PROPERTY ${tlk_prepared_property} "${tlk_prepared_value}")
            endif()
        endforeach()
        target_compile_definitions(tlk_scene_prepared_${tlk_prepared_variant} PRIVATE TLK_FORCE_SCENE_PRESENTATION=1 TLK_NATIVE_HUD_PREPARE=1)
    endforeach()
else()
    target_sources(snesrecomp_game PRIVATE ${GENERATED_SOURCES})
endif()

# ── Install / packaging ───────────────────────────────────────────────────
# `cmake --install build --prefix DIR` installs the player binary and the
# notes that go with it. scripts/package.sh turns that into a tarball. The
# ROM, extracted assets and the generated C are never installed.
if(TLK_BUILD_HOSTS)
    include(GNUInstallDirs)
    install(TARGETS tlk_sdl RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
    # Shader presets are looked up next to the binary (assets/shaders/...).
    install(DIRECTORY ${SNESRECOMP_ROOT}/runner/assets/shaders
            DESTINATION ${CMAKE_INSTALL_BINDIR}/assets)
    install(FILES packaging/README.txt packaging/LICENSE-NOTES.txt
            DESTINATION ${CMAKE_INSTALL_DOCDIR})
    install(FILES snesrecomp/LICENSE DESTINATION ${CMAKE_INSTALL_DOCDIR}
            RENAME LICENSE-snesrecomp.txt)
    # The settings menu: recomp-ui (MIT) with Dear ImGui (MIT), and the one
    # font it draws with (Lato, OFL 1.1), looked up in assets/fonts.
    install(FILES ${RECOMP_UI_ROOT}/assets/common/fonts/LatoLatin-Regular.ttf
            DESTINATION ${CMAKE_INSTALL_BINDIR}/assets/fonts)
    install(FILES ${RECOMP_UI_ROOT}/LICENSE DESTINATION ${CMAKE_INSTALL_DOCDIR}
            RENAME LICENSE-recomp-ui.txt)
    install(FILES packaging/LICENSE-imgui.txt packaging/LICENSE-Lato.txt
            DESTINATION ${CMAKE_INSTALL_DOCDIR})
    if(TLK_STATIC_SDL)
        include(FetchContent)
        FetchContent_GetProperties(SDL3)   # sdl3_SOURCE_DIR (set in a function)
        # SDL3 is zlib-licensed; its licence goes with the binary it is in.
        install(FILES "${sdl3_SOURCE_DIR}/LICENSE.txt" DESTINATION ${CMAKE_INSTALL_DOCDIR}
                RENAME LICENSE-SDL3.txt)
    endif()
endif()

include(cmake/TlkFinalAssets.cmake)
tlk_add_final_asset_preparer(tlk_prepare_final_assets)
include(cmake/TlkHudAssets.cmake)
tlk_add_hud_asset_preparer(tlk_prepare_hud_assets)
include(cmake/TlkSpriteAssets.cmake)
tlk_add_sprite_asset_preparer(tlk_prepare_sprite_assets)
include(cmake/TlkCaptionAssets.cmake)
tlk_add_caption_asset_preparer(tlk_prepare_caption_assets)
include(cmake/TlkCheckpointAssets.cmake)
tlk_add_checkpoint_asset_preparer(tlk_prepare_checkpoint_assets)
include(cmake/TlkRevivalAssets.cmake)
tlk_add_revival_asset_preparer(tlk_prepare_revival_assets)
include(cmake/TlkNativeHudAssets.cmake)
tlk_add_native_hud_asset_preparer(tlk_prepare_native_hud_assets)
include(cmake/TlkSceneAssets.cmake)
tlk_add_scene_asset_preparer(tlk_prepare_scene_assets)

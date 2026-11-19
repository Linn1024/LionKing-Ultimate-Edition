include_guard(GLOBAL)
function(tlk_add_sprite_asset_preparer target)
    get_filename_component(engine "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.." ABSOLUTE)
    add_executable(${target} "${engine}/tools/prepare_sprite_assets.c"
        "${engine}/runner/tlk_md_sprite_prepare.c" "${engine}/runner/tlk_md_assets.c"
        "${engine}/runner/tlk_contact_map.c" "${engine}/runner/tlk_fallback_log.c"
        "${engine}/runner/tlk_cant_wait_data.c" "${engine}/runner/tlk_pride_data.c" "${engine}/runner/tlk_start_data.c"
        "${engine}/runner/tlk_cw_terrain_data.c" "${engine}/runner/tlk_hunt_data.c"
        "${engine}/runner/tlk_reactivation_data.c" "${engine}/runner/tlk_hitbox_data.c"
        "${engine}/runner/tlk_roar_data.c" "${engine}/runner/tlk_destiny_monkey_data.c"
        "${engine}/runner/tlk_graveyard_data.c"
        "${engine}/runner/tlk_next_scene_data.c" "${engine}/runner/tlk_late_scene_data.c" "${engine}/runner/tlk_be_prepared_data.c"
        "${engine}/runner/tlk_interlevel_data.c" "${engine}/runner/tlk_interlevel_prepare.c"
        "${engine}/runner/tlk_bonus_result_data.c" "${engine}/runner/tlk_bonus_result_prepare.c"
        "${engine}/runner/tlk_temp_path.c" "${engine}/snesrecomp/runner/src/sha256.c")
    target_include_directories(${target} PRIVATE "${engine}/runner" "${engine}/generated/resources"
        "${engine}/snesrecomp/runner/src")
    set_property(TARGET ${target} PROPERTY C_STANDARD 11)
    target_compile_definitions(${target} PRIVATE TLK_INTERLEVEL_PREPARER=1)
    if(MINGW)
        target_link_options(${target} PRIVATE -static)
    endif()
endfunction()

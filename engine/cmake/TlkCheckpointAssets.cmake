include_guard(GLOBAL)
function(tlk_add_checkpoint_asset_preparer target)
    get_filename_component(engine "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.." ABSOLUTE)
    add_executable(${target} "${engine}/tools/prepare_checkpoint_assets.c"
        "${engine}/runner/tlk_checkpoint_art.c" "${engine}/runner/tlk_revival_art.c"
        "${engine}/runner/tlk_death_scene.c" "${engine}/runner/tlk_temp_path.c"
        "${engine}/snesrecomp/runner/src/sha256.c")
    target_include_directories(${target} PRIVATE "${engine}/runner" "${engine}/snesrecomp/runner/src")
    set_property(TARGET ${target} PROPERTY C_STANDARD 11)
    target_compile_definitions(${target} PRIVATE TLK_CHECKPOINT_ART_PREPARE=1)
    if(MINGW)
        target_link_options(${target} PRIVATE -static)
    endif()
endfunction()

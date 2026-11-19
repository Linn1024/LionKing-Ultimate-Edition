include_guard(GLOBAL)
function(tlk_add_hud_asset_preparer target)
    get_filename_component(engine "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.." ABSOLUTE)
    add_executable(${target} "${engine}/tools/prepare_hud_assets.c"
        "${engine}/runner/tlk_md_hud_prepare.c" "${engine}/runner/tlk_temp_path.c"
        "${engine}/snesrecomp/runner/src/sha256.c")
    target_include_directories(${target} PRIVATE "${engine}/runner" "${engine}/snesrecomp/runner/src")
    set_property(TARGET ${target} PROPERTY C_STANDARD 11)
    if(MINGW)
        target_link_options(${target} PRIVATE -static)
    endif()
endfunction()

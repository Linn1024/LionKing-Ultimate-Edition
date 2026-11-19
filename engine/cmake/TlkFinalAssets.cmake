# Shared by the full build and the small installer-tool build. No SDL/guest code.
include_guard(GLOBAL)
function(tlk_add_final_asset_preparer target)
    get_filename_component(engine "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/.." ABSOLUTE)
    add_executable(${target}
        "${engine}/tools/prepare_final_assets.c" "${engine}/runner/tlk_final_art.c"
        "${engine}/runner/tlk_final_art_prepare.c" "${engine}/runner/tlk_md_assets.c"
        "${engine}/runner/tlk_title_opening_art.c" "${engine}/runner/tlk_options_art.c" "${engine}/runner/tlk_options_art_prepare.c"
        "${engine}/runner/tlk_contact_map.c"
        "${engine}/runner/tlk_final_native.c" "${engine}/runner/tlk_final_native_prepare.c"
        "${engine}/runner/tlk_title_bank.c" "${engine}/runner/tlk_title_bank_prepare.c"
        "${engine}/runner/tlk_temp_path.c" "${engine}/snesrecomp/runner/src/sha256.c")
    target_include_directories(${target} PRIVATE "${engine}/runner" "${engine}/snesrecomp/runner/src")
    set_property(TARGET ${target} PROPERTY C_STANDARD 11)
    if(MINGW)
        target_link_options(${target} PRIVATE -static)
    endif()
endfunction()

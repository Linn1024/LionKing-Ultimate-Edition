# Fresh patched hardware/game runtime and owned presentation/helper objects.
# Generated guest programs are deliberately a separate build dependency.
include_guard(GLOBAL)
set(_TLK_PRIDE_CORE_ENGINE "${CMAKE_CURRENT_LIST_DIR}/..")

function(tlk_add_pride_core_objects target template)
    if(NOT TARGET "${template}")
        message(FATAL_ERROR "Pride core template target is missing: ${template}")
    endif()
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    get_filename_component(engine "${_TLK_PRIDE_CORE_ENGINE}" ABSOLUTE)
    set(stage "${CMAKE_CURRENT_BINARY_DIR}/${target}-sources")
    set(patcher "${engine}/scripts/apply_runtime_patches.py")
    foreach(layer runtime game)
        if(layer STREQUAL "runtime")
            set(root "${engine}/snesrecomp")
        else()
            set(root "${engine}")
        endif()
        set(patches "${engine}/cmake/${layer}-patches")
        file(GLOB hunks CONFIGURE_DEPENDS "${patches}/*.hunks")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${patcher}" ${hunks})
        execute_process(COMMAND "${Python3_EXECUTABLE}" "${patcher}" --patches "${patches}"
            --snesrecomp "${root}" --out "${stage}/${layer}" RESULT_VARIABLE result)
        if(NOT result EQUAL 0)
            message(FATAL_ERROR "Pride ${layer} patches failed: ${result}")
        endif()
        # Source changes, as well as patch changes, must refresh staged copies.
        foreach(hunk IN LISTS hunks)
            file(STRINGS "${hunk}" source_line REGEX "^file:")
            string(REGEX REPLACE "^file:[ ]*" "" source "${source_line}")
            set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${root}/${source}")
        endforeach()
    endforeach()
    add_library("${target}" OBJECT
        "${stage}/runtime/ppu.c" "${stage}/runtime/common_rtl.c" "${stage}/runtime/interp_bridge.c"
        "${stage}/game/tlk_game.c" "${stage}/game/tlk_savestate.c" "${stage}/game/tlk_resources.c"
        "${stage}/game/tlk_audio.c" "${engine}/runner/pride/wide/pride_launch_wide.c"
        "${engine}/runner/tlk_native_audio_owner.c" "${engine}/runner/tlk_reset.c" "${engine}/runner/tlk_pride_launch.c"
        "${engine}/runner/tlk_rng_entry.c" "${engine}/runner/tlk_rng_runtime.c" "${engine}/runner/tlk_temp_path.c")
    foreach(property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS)
        get_target_property(value "${template}" "${property}")
        if(value)
            set_property(TARGET "${target}" PROPERTY "${property}" "${value}")
        endif()
    endforeach()
    target_include_directories("${target}" PRIVATE "${engine}/runner")
    target_compile_definitions("${target}" PRIVATE TLK_PRIDE_DEATH_AOT_AVAILABLE=1 TLK_RNG_ENTRY_STAGED_AVAILABLE=1)
    # Preserve the separately reviewed host-I/O helper's compilation profile.
    set_source_files_properties("${engine}/runner/tlk_temp_path.c" PROPERTIES COMPILE_OPTIONS "-O2;-std=c11")
    set_property(TARGET "${target}" PROPERTY C_STANDARD 11)
    set_property(TARGET "${target}" PROPERTY C_STANDARD_REQUIRED TRUE)
endfunction()

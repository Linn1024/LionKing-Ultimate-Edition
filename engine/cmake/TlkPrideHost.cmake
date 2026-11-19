# Build only the reviewed host coordinator. Core/generated guest objects and
# the MD backend are separate dependencies; this does not enable their capability.
include_guard(GLOBAL)
set(_TLK_PRIDE_HOST_ENGINE "${CMAKE_CURRENT_LIST_DIR}/..")

function(tlk_add_pride_host_object target template compatibility_sha256)
    if(NOT TARGET "${template}")
        message(FATAL_ERROR "Pride host template target is missing: ${template}")
    endif()
    string(LENGTH "${compatibility_sha256}" identity_length)
    if(NOT identity_length EQUAL 64 OR NOT compatibility_sha256 MATCHES "^[0-9a-fA-F]+$")
        message(FATAL_ERROR "Pride host needs an explicit reviewed 32-byte save compatibility identity")
    endif()
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    get_filename_component(engine "${_TLK_PRIDE_HOST_ENGINE}" ABSOLUTE)
    set(stage "${CMAKE_CURRENT_BINARY_DIR}/${target}-frontend")
    set(patcher "${engine}/scripts/apply_runtime_patches.py")
    set(first "${stage}/shared")
    set(final "${stage}/host")
    foreach(layer frontend-patches pride-frontend-patches)
        file(GLOB patches CONFIGURE_DEPENDS "${engine}/cmake/${layer}/*.hunks")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${patches})
    endforeach()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
        "${patcher}" "${engine}/runner/sdl_main.c"
        "${engine}/runner/tlk_resource_editor_sdl.h" "${engine}/runner/tlk_resource_editor_selftest.h")
    execute_process(COMMAND "${Python3_EXECUTABLE}" "${patcher}"
        --patches "${engine}/cmake/frontend-patches" --snesrecomp "${engine}" --out "${first}"
        RESULT_VARIABLE result)
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Pride shared frontend patches failed: ${result}")
    endif()
    execute_process(COMMAND "${Python3_EXECUTABLE}" "${patcher}"
        --patches "${engine}/cmake/pride-frontend-patches" --snesrecomp "${first}" --out "${final}"
        RESULT_VARIABLE result)
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Pride host frontend patches failed: ${result}")
    endif()
    # Quoted includes must resolve the patched editors beside their frontend,
    # before the template target's ordinary runner include directory.
    configure_file("${first}/tlk_resource_editor_sdl.h" "${final}/tlk_resource_editor_sdl.h" COPYONLY)
    configure_file("${first}/tlk_resource_editor_selftest.h" "${final}/tlk_resource_editor_selftest.h" COPYONLY)
    set(bytes "")
    foreach(index RANGE 0 31)
        math(EXPR offset "${index} * 2")
        string(SUBSTRING "${compatibility_sha256}" ${offset} 2 byte)
        list(APPEND bytes "0x${byte}")
    endforeach()
    list(JOIN bytes "," bytes)
    file(WRITE "${stage}/tlk_pride_save_identity.h" "#define TLK_PRIDE_SAVE_COMPATIBILITY_BYTES ${bytes}\n")
    add_library("${target}" OBJECT "${engine}/runner/pride/tlk_pride_host.c")
    foreach(property INCLUDE_DIRECTORIES COMPILE_DEFINITIONS COMPILE_OPTIONS)
        get_target_property(value "${template}" "${property}")
        if(value)
            set_property(TARGET "${target}" PROPERTY "${property}" "${value}")
        endif()
    endforeach()
    target_include_directories("${target}" PRIVATE "${stage}" "${engine}/runner")
    target_compile_definitions("${target}" PRIVATE TLK_PRIVATE_COMPILED_HOOKS=1
        TLK_NATIVE_BANK_SDL=1 TLK_FORCE_SCENE_PRESENTATION=1
        "TLK_PRIDE_FRONTEND_SOURCE=\"${final}/sdl_main.c\"")
    set_property(TARGET "${target}" PROPERTY C_STANDARD 11)
    set_property(TARGET "${target}" PROPERTY C_STANDARD_REQUIRED TRUE)
endfunction()

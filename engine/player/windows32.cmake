# Reviewed Windows development profile. Supply MinGW compiler paths at configure.
set(TLK_STATIC_SDL ON CACHE BOOL "Static pinned SDL3")
set(TLK_USE_CCACHE OFF CACHE BOOL "Optional compiler cache")
set(SNESRECOMP_STATIC_RUNTIME ON CACHE BOOL "Static compiler runtime")
set(SNESRECOMP_EXECUTION_DEFAULT off CACHE STRING "Native execution selection")
set(SNESRECOMP_FRAME_IMPL LLE CACHE STRING "Reviewed frame implementation")
set(SNESRECOMP_AUDIO_TRACE_HISTORY SMALL CACHE STRING "Reviewed audio state")
foreach(feature BOOT_WATCHDOG_DIAGNOSTICS CPU_HW_DIAGNOSTICS DISPATCH_HISTORY
    FRAME_FINGERPRINTS FUNC_SNAPSHOT LUA NET PPU_DMA_HISTORY SPC_DIAGNOSTICS
    STACK_BALANCE_DIAGNOSTICS TRACE)
    set(SNESRECOMP_ENABLE_${feature} OFF CACHE BOOL "Reviewed development profile")
endforeach()
set(SNESRECOMP_EXPOSE_COVERAGE_MOD OFF CACHE BOOL "Reviewed coverage setting")
get_filename_component(workspace "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
if(EXISTS "${workspace}/.tools/SDL3-3.4.10/CMakeLists.txt")
    set(SNESRECOMP_SDL3_SOURCE_DIR "${workspace}/.tools/SDL3-3.4.10" CACHE PATH "Local pinned SDL source")
endif()

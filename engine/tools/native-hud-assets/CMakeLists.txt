cmake_minimum_required(VERSION 3.20)
project(LionKingNativeHudAssets LANGUAGES C)
include(../../cmake/TlkNativeHudAssets.cmake)
tlk_add_native_hud_asset_preparer(tlk_prepare_native_hud_assets)

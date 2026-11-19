cmake_minimum_required(VERSION 3.20)
project(LionKingHudAssets LANGUAGES C)
include(../../cmake/TlkHudAssets.cmake)
tlk_add_hud_asset_preparer(tlk_prepare_hud_assets)

cmake_minimum_required(VERSION 3.20)
project(LionKingSpriteAssets LANGUAGES C)
include(../../cmake/TlkSpriteAssets.cmake)
tlk_add_sprite_asset_preparer(tlk_prepare_sprite_assets)

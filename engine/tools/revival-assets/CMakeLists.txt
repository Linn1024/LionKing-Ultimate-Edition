cmake_minimum_required(VERSION 3.20)
project(LionKingRevivalAssets LANGUAGES C)
include(../../cmake/TlkRevivalAssets.cmake)
tlk_add_revival_asset_preparer(tlk_prepare_revival_assets)

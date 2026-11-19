cmake_minimum_required(VERSION 3.20)
project(LionKingCaptionAssets LANGUAGES C)
include(../../cmake/TlkCaptionAssets.cmake)
tlk_add_caption_asset_preparer(tlk_prepare_caption_assets)

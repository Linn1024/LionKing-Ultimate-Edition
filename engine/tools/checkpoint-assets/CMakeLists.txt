cmake_minimum_required(VERSION 3.20)
project(LionKingCheckpointAssets LANGUAGES C)
include(../../cmake/TlkCheckpointAssets.cmake)
tlk_add_checkpoint_asset_preparer(tlk_prepare_checkpoint_assets)

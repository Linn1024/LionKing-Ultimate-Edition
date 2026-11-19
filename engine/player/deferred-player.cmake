# Build in the engine directory where its non-global imported GL/SDL/UI targets
# are visible. Defer until all ordinary engine templates/libraries are defined.
include("${CMAKE_CURRENT_LIST_DIR}/../cmake/TlkPridePlayer.cmake")
cmake_language(DEFER CALL tlk_add_pride_player tlk_pride_player
    "${TLK_PRIDE_ROM}" "${TLK_PRIDE_GENERATION}" "${TLK_PRIDE_MD_BACKEND}")

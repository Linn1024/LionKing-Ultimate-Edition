include("${CMAKE_CURRENT_LIST_DIR}/../cmake/TlkPrideFinalPlayer.cmake")
cmake_language(DEFER CALL tlk_add_pride_final_player tlk_pride_final_player
    "${TLK_PRIDE_ROM}" "${TLK_PRIDE_GENERATION}" "${TLK_PRIDE_MD_BACKEND}")

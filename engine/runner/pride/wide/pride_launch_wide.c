/* Preserve the reviewed renderer while configuration replaces probe settings. */
#include <stdio.h>
#include <stdlib.h>
#ifdef _WIN32
#include <direct.h>
#endif
#include "../../tlk_pride_launch.h"
#define fopen TlkPrideFileOpen
#define getenv TlkPrideSetting
#define _mkdir TlkPrideMakeDirectory
#include "pride_machine_reset_wide.c"
#undef fopen
#undef getenv
#undef _mkdir

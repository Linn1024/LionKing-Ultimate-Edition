/* Reviewed single-translation-unit Pride runtime. Keeping the dependency
 * order explicit preserves callback/serializer ownership while components move
 * behind their own APIs. All game programs and assets remain ROM-derived. */
#include "tlk_resources.h"
#include "tlk_pride_launch.h"
#include "tlk_rng_runtime.h"
#include "tlk_temp_path.h"
#include "tlk_pride_save_context.h"
#include "common_rtl.h"
/* Bind the unwrapped frame before the coordinator's include-time aliases. */
static inline bool PrideNativeFrame(uint32 inputs) { return RtlRunFrame(inputs); }
static void PrideLaunchClearPrivate(void);
#include "pride_practice_probe.c"
#include "pride_machine_reset.inc"
#include "pride_present.inc"
#include "pride_launch_clear.inc"
#include "pride_save_dispatch.inc"
#include "tlk_pride_save_cold.inc"

#ifndef TLK_HUD_ROLE_H
#define TLK_HUD_ROLE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Native task allocation changes after reload. Follow the draw record's
 * position back to its task and identify the ROM callback, not its heap slot.
 * Unknown or stale ownership retains the native sprite. 0=roar, 1=health. */
static inline int TlkHudMeterRole(const uint8_t *ram, size_t ram_size,
                                const uint8_t *rom, size_t rom_size,
                                unsigned draw, bool fixed) {
    if (!fixed || !ram || ram_size < 0x10000 || !rom || draw > 0xfffa) return -1;
    unsigned position = ram[draw + 4] | (unsigned)ram[draw + 5] << 8;
    if (position < 0xa008 || position > 0xff88) return -1;
    unsigned task = position - 8;
    unsigned owner_draw = ram[task + 12] | (unsigned)ram[task + 13] << 8;
    if (owner_draw != draw) return -1;
    uint32_t descriptor = ram[task + 4] | (uint32_t)ram[task + 5] << 8 |
                          (uint32_t)ram[task + 6] << 16;
    if (descriptor < 0xc00000) return -1;
    size_t offset = descriptor & 0x3fffff;
    if (offset > rom_size || rom_size - offset < 3) return -1;
    uint32_t callback = rom[offset] | (uint32_t)rom[offset + 1] << 8 |
                        (uint32_t)rom[offset + 2] << 16;
    return callback == 0xc0d6a6 ? 0 : callback == 0xc00201 ? 1 : -1;
}

#endif

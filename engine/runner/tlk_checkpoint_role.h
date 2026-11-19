#ifndef TLK_CHECKPOINT_ROLE_H
#define TLK_CHECKPOINT_ROLE_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Semantic identity only, not visibility. The caller must still establish
 * ownership of the displayed OAM. The checkpoint head shares the hero's first
 * revival image, so pose alone cannot identify it. No task/draw heap slot is
 * assumed: validate the bidirectional task/draw link and original descriptor.
 * Only the three reviewed shared checkpoint images are supported on the
 * collectible task. Its static post-reload counterpart accepts the base only. */
static inline bool TlkCheckpointDrawRoleImpl(const uint8_t *ram, size_t ram_size,
                                        const uint8_t *rom, size_t rom_size,
                                        unsigned draw, uint32_t pose, bool fixed,
                                        uint32_t captured_descriptor) {
    if (fixed || !ram || ram_size < 0x20000 || !rom ||
        draw < 0x8000 || draw > 0xffe8 ||
        (pose != 0xc456de && pose != 0xc2fde1 && pose != 0xc2fe18)) return false;
    /* These descriptors run the common checkpoint program across worlds.
     * Identity comes from the reciprocal owner and original ROM below;
     * the caller separately validates visible OAM and the live palette. */
    unsigned position = ram[draw+4] | (unsigned)ram[draw+5] << 8;
    if (position < 0xa008 || position > 0xff88) return false;
    unsigned task = position-8;
    unsigned owner_draw = ram[task+12] | (unsigned)ram[task+13] << 8;
    uint32_t descriptor = ram[task+4] | (uint32_t)ram[task+5] << 8 |
                          (uint32_t)ram[task+6] << 16;
    uint32_t draw_pose = ram[draw+10] | (uint32_t)ram[draw+11] << 8 |
                        (uint32_t)ram[draw+12] << 16;
    if (owner_draw != draw || (descriptor != 0xc588a6 && descriptor != 0xc5889a)) return false;
    if (captured_descriptor && captured_descriptor != descriptor) return false;
    if (draw_pose != pose && (!captured_descriptor ||
        (draw_pose != 0xc456de && draw_pose != 0xc2fde1 && draw_pose != 0xc2fe18))) return false;
    if (descriptor == 0xc588a6 && pose != 0xc456de) return false;
    if (descriptor == 0xc588a6 && draw_pose != 0xc456de) return false;
    /* Object entries2/3 use static/collectible callbacks with the same image.
     * The collectible callback writes checkpoint coordinates and runs its
     * native interaction/blink state. Presentation must not replace that work. */
    if (rom_size < 0x588cb || rom[0x588ca] != 0x6b) return false;
    size_t at = descriptor & 0x3fffff;
    unsigned table_at = descriptor == 0xc588a6 ? 0xbe20 : 0xbe26;
    uint32_t callback = rom[at] | (uint32_t)rom[at+1] << 8 | (uint32_t)rom[at+2] << 16;
    uint32_t image = rom[at+6] | (uint32_t)rom[at+7] << 8 | (uint32_t)rom[at+8] << 16;
    uint32_t table = rom[table_at] | (uint32_t)rom[table_at+1] << 8 | (uint32_t)rom[table_at+2] << 16;
    if (descriptor == 0xc5889a && (rom[0x55725] != 0x08 || rom[0x557de] != 0x6b)) return false;
    return callback == (descriptor == 0xc588a6 ? 0xc588ca : 0xc55725) && image == 0xc456de && table == descriptor;
}

static inline bool TlkCheckpointDrawRole(const uint8_t *ram, size_t ram_size,
                                        const uint8_t *rom, size_t rom_size,
                                        unsigned draw, uint32_t pose, bool fixed) {
    return TlkCheckpointDrawRoleImpl(ram,ram_size,rom,rom_size,draw,pose,fixed,0);
}

/* Displayed OAM can still own the preceding verified pose after animation
 * advances in task RAM. Require the captured descriptor to remain the same
 * reciprocal live owner; the caller must also validate the actual OAM/palette. */
static inline bool TlkCheckpointCapturedDrawRole(const uint8_t *ram, size_t ram_size,
                                                const uint8_t *rom, size_t rom_size,
                                                unsigned draw, uint32_t pose, bool fixed,
                                                uint32_t captured_descriptor) {
    if (captured_descriptor != 0xc5889a && captured_descriptor != 0xc588a6) return false;
    return TlkCheckpointDrawRoleImpl(ram,ram_size,rom,rom_size,draw,pose,fixed,captured_descriptor);
}

#endif

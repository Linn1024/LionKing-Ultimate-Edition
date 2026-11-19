#ifndef TLK_WORLD_LIFE_SPRITE_H
#define TLK_WORLD_LIFE_SPRITE_H
/* Shared C58981/C23E5F life pickup, paired with MD09792C/17EBE2.
 * Includes every original stream drawing; bonus reward ownership is separate. */
static int TlkWorldLifeSpritePose(unsigned pose) {
    switch(pose&0x3fffff) {
    case 0x50216:case 0x50241:case 0x50270:
    case 0x5029f:case 0x502ce:case 0x502f9:return 1;
    default:return 0;
    }
}
#endif

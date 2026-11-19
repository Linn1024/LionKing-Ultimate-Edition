#ifndef TLK_ENEMY_ART_FAMILY_H
#define TLK_ENEMY_ART_FAMILY_H
/* Historical sprite-map role2 combines two actors. These nine reviewed
 * original porcupine drawings must not follow the chameleon's source. */
static int TlkEnemyArtPorcupine(unsigned pose) {
    switch(pose&0x3fffff) {
    case 0x12c31:case 0x12c64:case 0x12c9b:case 0x12cd2:case 0x12d0d:
    case 0x12d44:case 0x12d7b:case 0x12db6:case 0x12df1:return 1;
    default:return 0;
    }
}
#endif

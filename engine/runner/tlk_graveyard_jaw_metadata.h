/* Original C58820/MD D1854 and C5882C/MD D1862 share this jaw program.
 * Only these eleven jaw poses qualify; later Scar farewell art is separate. */
static inline int TlkGraveyardJawPose(unsigned pose) {
    switch(pose) {
    case 0xc39abb: case 0xc39b00: case 0xc39b77: case 0xc39bf2:
    case 0xc39c61: case 0xc39cc8: case 0xc39d47: case 0xc39dca:
    case 0xc39e49: case 0xc39eb0: case 0xc39f0b:return 1;
    default:return 0;
    }
}

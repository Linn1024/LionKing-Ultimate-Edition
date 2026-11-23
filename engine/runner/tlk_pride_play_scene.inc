/* Both reviewed Pride descriptors use the same cold decoder/native bank.
 * Readiness, live actor, task and pending-history checks stay with the caller. */
static int PrideOrdinaryPlayScene(unsigned level,unsigned descriptor) {
    return level==0 && (descriptor==0xc00387 || descriptor==0xc0080d);
}

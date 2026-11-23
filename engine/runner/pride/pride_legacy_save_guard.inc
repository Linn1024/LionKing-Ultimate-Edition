/* The private scene/cache envelopes cannot infer missing public-player
 * context. Recognize its native format without attempting guest publication. */
static int PrideLegacyNativeSave(const uint8_t *record,size_t size) {
    if(!record || size<32 || memcmp(record,"TLKSTAT1",8))return 0;
    uint32_t version=TlkGet32(record+8);if(version<1 || version>4)return 0;
    size_t header=version==1?32:36;if(size<header)return 0;
    uint64_t length=TlkGet64(record+24);
    if(!length || length>=(64u<<20) || length>size-header)return 0;
    pride_state_set_error("Native save format: use its original player or restart level");
    return 1;
}

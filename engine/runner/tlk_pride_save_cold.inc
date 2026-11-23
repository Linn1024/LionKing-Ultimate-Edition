/* Before the first Pride bank/decoder capture, native state contains the whole
 * live context. Once capture starts, only the private serializers may save it.
 * This deliberately does not treat an incomplete capture as an empty one. */
static int PridePracticeSave(const char *path,uint32_t field) {
    if(TlkPrideHealthDeathSelected() && field && !ow(0x1ff9e) &&
       ol(0xdf)!=0xc00387 && ol(0xdf)!=0xc0080d &&
       !have_return && !scene_calls && !scene_active && !active &&
       !owner_scene.started && !preparation_pending &&
       (!prepared || !program || !TlkNativeBankReady(prepared,program)))
        return __real_tlk_state_save(path,field);
    return PrideScenePracticeSave(path,field);
}

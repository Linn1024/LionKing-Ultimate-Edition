/* Installation supplies reviewed native payloads. Playback never prepares them. */
static int ContinueTitleBankAssetsLoad(const char *path) {
    size_t size=0;uint8_t *record=path?read_file(path,&size):NULL;
    title_bank_assets=record?TlkTitleBankLoad(record,size):NULL;
    if(!title_bank_assets) {
        free(record);fprintf(stderr,"Installed title sound data is missing or incompatible. Run Setup.\n");return 0;
    }
    sha256_compute(record,size,title_bank_asset_digest);free(record);return 1;
}
static int ContinueNativeAssetsLoad(const char *path) {
    size_t size=0;uint8_t *record=path?read_file(path,&size):NULL;
    final_native_assets=record?TlkFinalNativeLoad(record,size):NULL;
    if(!final_native_assets) {
        free(record);fprintf(stderr,"Installed final-life payloads are missing or incompatible. Run Setup.\n");return 0;
    }
    sha256_compute(record,size,final_native_asset_digest);free(record);return 1;
}

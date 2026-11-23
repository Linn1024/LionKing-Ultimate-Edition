/* Versioned native ownership wrapping the existing native/MD audio history. */
#undef TlkAudioHistorySize
#undef TlkAudioSaveHistory
#undef TlkAudioValidateHistory
#undef TlkAudioLoadHistory
extern size_t TlkNativeAudioOwnerStateSize(void);
extern int TlkNativeAudioOwnerSave(uint8_t *,size_t);
extern int TlkNativeAudioOwnerValidate(const uint8_t *,size_t);
extern int TlkNativeAudioOwnerLoad(const uint8_t *,size_t);
extern void TlkNativeAudioOwnerReset(void);
enum { SEM_AUDIO_HEADER=64 };
static int SemanticAudioHash(const uint8_t *data,size_t size,uint8_t hash[32]) {
    uint8_t *copy=malloc(size);if(!copy)return 0;
    memcpy(copy,data,size);memset(copy+32,0,32);sha256_compute(copy,size,hash);free(copy);return 1;
}
size_t TlkAudioHistorySize(void) {
    size_t base=TlkBaseAudioHistorySize();
    return base?SEM_AUDIO_HEADER+base+TlkNativeAudioOwnerStateSize():0;
}
int TlkAudioSaveHistory(uint8_t *out,size_t size) {
    size_t base=TlkBaseAudioHistorySize(),metadata=TlkNativeAudioOwnerStateSize();
    if(!out || !base || size!=SEM_AUDIO_HEADER+base+metadata || size>TLK_AUDIO_HISTORY_MAX)return 0;
    memset(out,0,SEM_AUDIO_HEADER);memcpy(out,"TLKSEM01",8);TlkPut32(out+8,1);
    TlkPut32(out+12,base);TlkPut32(out+16,metadata);
    if(!TlkBaseAudioSaveHistory(out+SEM_AUDIO_HEADER,base) ||
       !TlkNativeAudioOwnerSave(out+SEM_AUDIO_HEADER+base,metadata))return 0;
    uint8_t hash[32];if(!SemanticAudioHash(out,size,hash))return 0;
    memcpy(out+32,hash,32);return 1;
}
int TlkAudioValidateHistory(const uint8_t *data,size_t size) {
    if(!data || size<8 || memcmp(data,"TLKSEM01",8))return TlkBaseAudioValidateHistory(data,size);
    if(size<SEM_AUDIO_HEADER || size>TLK_AUDIO_HISTORY_MAX || TlkGet32(data+8)!=1)return 0;
    unsigned base=TlkGet32(data+12),metadata=TlkGet32(data+16);
    if(base>size-SEM_AUDIO_HEADER || metadata!=size-SEM_AUDIO_HEADER-base ||
       metadata!=TlkNativeAudioOwnerStateSize())return 0;
    for(unsigned i=20;i<32;i++)if(data[i])return 0;
    uint8_t hash[32];
    return TlkBaseAudioValidateHistory(data+SEM_AUDIO_HEADER,base) &&
        TlkNativeAudioOwnerValidate(data+SEM_AUDIO_HEADER+base,metadata) &&
        SemanticAudioHash(data,size,hash) && !memcmp(hash,data+32,32);
}
int TlkAudioLoadHistory(const uint8_t *data,size_t size) {
    if(!data || size<8 || memcmp(data,"TLKSEM01",8)) {
        if(!TlkBaseAudioLoadHistory(data,size))return 0;
        TlkNativeAudioOwnerReset();return 1;
    }
    if(!TlkAudioValidateHistory(data,size))return 0;
    unsigned base=TlkGet32(data+12),metadata=TlkGet32(data+16);
    const uint8_t *nested=data+SEM_AUDIO_HEADER;
    uint8_t fingerprint[32];if(audio_fingerprint(fingerprint)<0)return 0;
    int compatible=(!host_rate || TlkGet32(nested+28)==host_rate) &&
        !memcmp(fingerprint,nested+48,32);
    if(!TlkBaseAudioLoadHistory(nested,base))return 0;
    if(compatible)return TlkNativeAudioOwnerLoad(nested+base,metadata);
    /* A discarded foreign MD tail must not leave its native counterpart muted. */
    TlkNativeAudioOwnerReset();return 1;
}

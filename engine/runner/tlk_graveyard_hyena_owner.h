#ifndef TLK_GRAVEYARD_HYENA_OWNER_H
#define TLK_GRAVEYARD_HYENA_OWNER_H
/* Regular and scripted variants share the original walking/reaction actions.
 * Socket-head actors are a separate rendering-only family. */
static inline int TlkGraveyardHyenaDescriptor(unsigned descriptor) {
    return descriptor==0xc58c74 || descriptor==0xc58c80;
}
static inline int TlkGraveyardHyenaDrawDescriptor(unsigned descriptor) {
    return TlkGraveyardHyenaDescriptor(descriptor) || descriptor==0xc58c8c || descriptor==0xc58c98;
}
#endif

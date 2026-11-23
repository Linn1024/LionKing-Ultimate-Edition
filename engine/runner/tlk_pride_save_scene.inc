/* An idle, complete Pride cache can accompany both reviewed play scenes and
 * the native level card. The latter does not earn MD rendering capability.
 * The caller still rejects active/incomplete decoder or owned-scene state. */
static int PrideCompleteContextScene(unsigned level,unsigned descriptor) {
    return level==0 && (descriptor==0xc00387 || descriptor==0xc0080d || descriptor==0xc005ab);
}

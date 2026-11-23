/* The owned default scene replaces its actor at254 and restores health at274.
 * Native initialization can finish at different earlier fields depending on
 * the prior camera/map work. Ground the real initialized actor within that
 * preparation interval; do not require one predecessor route's age268. */
static int PrideDefaultGroundWindow(unsigned age,int initialized,int advancing) {
    return initialized && !advancing && age>=254 && age<274;
}

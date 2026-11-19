#ifndef TLK_TEMP_PATH_H
#define TLK_TEMP_PATH_H
#include <stddef.h>

/* Format a distinct name for this process and invocation. No file is created.
 * Failure clears out when capacity permits, so cleanup cannot use a truncated
 * destination. The name is host I/O state and is never serialized. */
int TlkTemporaryPath(char *out,size_t capacity,const char *path,const char *suffix);
#endif

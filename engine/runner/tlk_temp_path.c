#include "tlk_temp_path.h"
#include <limits.h>
#include <stdatomic.h>
#include <stdio.h>
#ifdef _WIN32
#include <process.h>
#else
#include <unistd.h>
#endif

static atomic_uint next_ticket;

int TlkTemporaryPath(char *out,size_t capacity,const char *path,const char *suffix) {
    if(!out || !capacity)return 0;
    out[0]=0;
    if(!path || !*path || !suffix)return 0;
    unsigned ticket=atomic_load_explicit(&next_ticket,memory_order_relaxed);
    do {
        if(ticket==UINT_MAX)return 0;
    } while(!atomic_compare_exchange_weak_explicit(&next_ticket,&ticket,ticket+1,
                                                  memory_order_relaxed,memory_order_relaxed));
#ifdef _WIN32
    unsigned long process=(unsigned long)_getpid();
#else
    unsigned long process=(unsigned long)getpid();
#endif
    int n=snprintf(out,capacity,"%s.%lu.%u%s",path,process,ticket,suffix);
    if(n<=0 || (size_t)n>=capacity) { out[0]=0;return 0; }
    return 1;
}

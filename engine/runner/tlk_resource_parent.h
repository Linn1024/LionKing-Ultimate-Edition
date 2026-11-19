#ifndef TLK_RESOURCE_PARENT_H
#define TLK_RESOURCE_PARENT_H
#include "tlk_resources.h"
#include <string.h>
/* Resource IDs survive appended/injected nodes. A dot or underscore separates
 * a group from descendants; ceiling_rows/ceiling_clearance retain their
 * existing ceiling group. A leaf can never become another resource's parent. */
static inline int TlkResourceParentById(const TlkResourceNode *nodes,int count,int index) {
    if(index<=0 || index>=count)return -1;
    const char *id=nodes[index].id;size_t length=strlen(id),best_length=0;int best=0;
    for(int i=1;i<count;i++) {
        if(i==index || nodes[i].leaf)continue;
        size_t n=strlen(nodes[i].id);
        if(n>best_length && n<length && (id[n]=='.' || id[n]=='_') && !memcmp(id,nodes[i].id,n)) {
            best=i;best_length=n;
        }
    }
    return best;
}
#endif

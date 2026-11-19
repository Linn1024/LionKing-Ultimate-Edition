#ifndef TLK_HYENA_CONTEXT_ART_H
#define TLK_HYENA_CONTEXT_ART_H
#include <stdint.h>
#include <stddef.h>
/* Original paired operands5722. Only installer decodes MD images; captured
 * animation context distinguishes the two MD counterparts of C633D8. */
static const struct { unsigned native_pose,cursor,alias; } tlk_hyena_context_art[]={
{0xc633d8,0xc24de0,0xfe1000},
{0xc633d8,0xc24eec,0xfe1001},
{0xc63417,0xc24ef0,0xfe1002},
{0xc6345e,0xc24ef4,0xfe1003},
{0xc634ad,0xc24ef8,0xfe1004},
{0xc634fc,0xc24efc,0xfe1005},
{0xc63543,0xc24f00,0xfe1006},
{0xc633d8,0xc2509f,0xfe1007},
};

static inline unsigned TlkHyenaContextAlias(unsigned context,unsigned pose) {
    if(!context || context>8 || tlk_hyena_context_art[context-1].native_pose!=pose)return 0;
    return tlk_hyena_context_art[context-1].alias;
}
static inline unsigned TlkHyenaContextCapture(const uint8_t *ram,size_t size,unsigned draw,
                                             unsigned pose,int fixed,unsigned descriptor) {
    if(!ram || size<0x20000 || fixed || descriptor!=0xc58ecc || draw<0x8000 || draw>0xffe8)return 0;
    unsigned pos=ram[draw+4]|(unsigned)ram[draw+5]<<8;if(pos<0xa008 || pos>0xff88)return 0;
    unsigned actor=pos-8;
#define HY_WORD(at) (ram[(at)]|(unsigned)ram[(at)+1]<<8)
#define HY_PTR(at) (HY_WORD(at)|(unsigned)ram[(at)+2]<<16)
    if(HY_WORD(actor+12)!=draw || HY_PTR(actor+4)!=descriptor || HY_PTR(draw+10)!=pose)return 0;
    unsigned cursor=HY_PTR(actor+0x12);
    for(unsigned i=0;i<8;i++)if(tlk_hyena_context_art[i].native_pose==pose &&
        tlk_hyena_context_art[i].cursor==cursor)return i+1;
#undef HY_PTR
#undef HY_WORD
    return 0;
}
#endif


/* Research-only prepared decoder bodies, observed during original cold loading.
 * Retain the real prologue and PLB/PLP/RTL epilogue. No CPU/DMA/audio clock copy. */
#include "tlk_md_assets.h"
typedef struct SceneTemplate {
    unsigned source,destination,expected;
    uint8_t *payload,*before;
    uint8_t input[10],scratch[10],stack[5],p;
    uint16_t a,x,y,sp;
    DmaChannel dma_input,dma_output;
    unsigned port,ready,capturing;
} SceneTemplate;
static SceneTemplate scene_templates[]={
    {.source=0xee6e03,.destination=0x7e4434,.expected=12316},
    {.source=0xc9f9e1,.destination=0x7e2434,.expected=5760},
    {.source=0xe20001,.destination=0x7f0000,.expected=16000},
    {.source=0xe7c514,.destination=0x7f8800,.expected=10112},
    {.source=0xe8c1a3,.destination=0x7fba00,.expected=7552},
    {.source=0xefe261,.destination=0x7fd780,.expected=2176},
    {.source=0xecf6c1,.destination=0x7fe000,.expected=3840}
};
static unsigned scene_apply_templates,scene_template_applies;
static SceneTemplate *scene_template(void) {
    for(unsigned i=0;i<sizeof scene_templates/sizeof *scene_templates;i++)
        if(scene_templates[i].source==scene_source && scene_templates[i].destination==scene_dest)return &scene_templates[i];
    return NULL;
}
static void scene_template_init(void) {
    for(unsigned i=0;i<sizeof scene_templates/sizeof *scene_templates;i++) {
        SceneTemplate *t=&scene_templates[i];size_t n=0;
        t->payload=malloc(t->expected);t->before=malloc(0x20000);
        if(!t->payload || !t->before || !TlkMdDecompress(g_rom,0x300000,t->source&0x3fffff,t->payload,t->expected,&n) || n!=t->expected)exit(42);
    }
    const char *value=TlkPrideSetting("TLK_SCENE_PREPARE_APPLY");scene_apply_templates=value && !strcmp(value,"1");
}
static int scene_template_quiet(CpuState *cpu) {
    if(cpu->D || cpu->m_flag!=1 || cpu->x_flag || cpu->DB!=(scene_dest>>16) || cpu->S<0x205 || cpu->S>=0x300 ||
       g_snes->nmiEnabled || g_snes->dma->dmaBusy || g_snes->dma->dmaTimer || g_snes->dma->channel[1].hdmaActive)return 0;
    for(unsigned i=0;i<8;i++)if(g_snes->dma->channel[i].dmaActive)return 0;
    return 1;
}
static void scene_template_dma(DmaChannel *out,const DmaChannel *terminal) {
    /* All other fields belong to the caller or to the retained prologue. */
    out->aAdr=terminal->aAdr;out->size=terminal->size;
    out->dmaActive=terminal->dmaActive;out->offIndex=terminal->offIndex;
}
static void scene_template_loop(CpuState *cpu) {
    SceneTemplate *t=scene_template();if(!t)return;
    /* A native fallback/reload may execute this recipe again after cold capture.
     * Keep its original decoder and the valid prepared capsule. Its caller ABI
     * need not satisfy the owned replacement's quiet/capture contract. */
    if(!scene_death && t->ready)return;
    if(!scene_template_quiet(cpu))exit(43);
    if(!scene_death) {
        if(t->ready || t->capturing)exit(43);
        memcpy(t->before,g_ram,0x20000);memcpy(t->input,g_ram+10,10);t->sp=cpu->S;
        t->dma_input=g_snes->dma->channel[1];t->capturing=1;return;
    }
    if(!scene_apply_templates)return;
    if(scene_word(0x1ffa2)!=1 || scene_word(0xa6ba) || scene_word(0x1ff90) || scene_long(0xb243)!=0xc35a82)exit(43);
    if(!t->ready || memcmp(t->input,g_ram+10,10) || (cpu->P&0x0c)!=(t->p&0x0c))exit(43);
    const DmaChannel *live=&g_snes->dma->channel[1];
    if(live->bAdr!=t->dma_input.bAdr || live->aBank!=t->dma_input.aBank || live->mode!=t->dma_input.mode ||
       live->fixed!=t->dma_input.fixed || live->decrement!=t->dma_input.decrement ||
       live->indirect!=t->dma_input.indirect || live->fromB!=t->dma_input.fromB || live->unusedBit!=t->dma_input.unusedBit)exit(43);
    /* Fixed, validated writes; no borrowed decoder state or live chip restore. */
    memcpy(g_ram+t->destination-0x7e0000,t->payload,t->expected);
    memcpy(g_ram+10,t->scratch,10);memcpy(g_ram+cpu->S-4,t->stack,5);
    scene_template_dma(&g_snes->dma->channel[1],&t->dma_output);g_snes->ramAdr=t->port;
    cpu->A=t->a;cpu->X=t->x;cpu->Y=t->y;cpu->P=t->p;cpu_p_to_mirrors(cpu);
    scene_template_applies++;
    scene_log(cpu,"prepared",0xc1cd75);scene_dump("prepared");
    interp_bridge_pre_opcode_redirect(0xc1cd83);
}
static void scene_template_exit(CpuState *cpu) {
    SceneTemplate *t=scene_template();if(!t || !t->capturing)return;
    unsigned at=t->destination-0x7e0000;
    if(!scene_template_quiet(cpu) || cpu->S!=t->sp || memcmp(g_ram+at,t->payload,t->expected) ||
       g_snes->ramAdr!=((at+t->expected)&0x1ffff))exit(44);
    for(unsigned i=0;i<0x20000;i++)if(g_ram[i]!=t->before[i] && !(i>=at && i<at+t->expected) &&
        !(i>=10 && i<20) && !(i>=(unsigned)t->sp-4 && i<=(unsigned)t->sp))exit(44);
    DmaChannel expected=t->dma_input;scene_template_dma(&expected,&g_snes->dma->channel[1]);
    if(memcmp(&expected,&g_snes->dma->channel[1],sizeof expected))exit(44);
    memcpy(t->scratch,g_ram+10,10);memcpy(t->stack,g_ram+cpu->S-4,5);
    t->a=cpu->A;t->x=cpu->X;t->y=cpu->Y;t->p=cpu->P;
    t->dma_output=g_snes->dma->channel[1];t->port=g_snes->ramAdr;t->ready=1;t->capturing=0;
    free(t->before);t->before=NULL;
}

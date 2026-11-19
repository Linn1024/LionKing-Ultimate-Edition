"""Private proof: installed MD Game Over drawing with unmodified SNES timing.

Not a public capability: Continue YES/NO, arbitrary mixtures and current-build
save/restart ownership must be completed before resource-tree activation.
"""
from pathlib import Path

builder = Path(__file__).with_name('build_pride_menu197_observer.py')
source = builder.read_text().replace("ROOT / 'build/pride-menu197-observer'",
                                   "ROOT / 'build/pride-menu200-native-art'")
anchor = "target = out / 'host.i'"
assert source.count(anchor)==1
injection = r'''
declarations = "static int NativeMenu200Enabled(void);\nstatic void NativeMenu200Event(const char *);\nstatic void NativeMenu200Paint(uint32_t *,int);\n"
anchor200 = 'static void FinalSceneBegin(CpuState *cpu,uint32_t pc) {'
assert s.count(anchor200)==1
s = s.replace(anchor200,declarations+anchor200)
anchor200 = 'if(!timing || strcmp(timing,"1")) {'
assert s.count(anchor200)==1
s = s.replace(anchor200,'if((!timing || strcmp(timing,"1")) && !NativeMenu200Enabled()) {')
for anchor200, call200 in [('ContinueMenuPaint(pixels,256);','NativeMenu200Paint(pixels,256);'),
                          ('ContinueMenuPaint(pixels,width);','NativeMenu200Paint(pixels,width);')]:
    assert s.count(anchor200)==1
    s = s.replace(anchor200,anchor200+call200)
anchor200 = 'static void MenuObserve197(const char *kind,CpuState *cpu,uint32_t pc){'
assert s.count(anchor200)==1
s = s.replace(anchor200,anchor200+'NativeMenu200Event(kind);')
s += r"""
static unsigned native_menu200_armed,native_menu200_active,native_menu200_exiting,native_menu200_updates;
static int NativeMenu200Enabled(void){
    const char *v=getenv("TLK_NATIVE_MENU200");
    return v && !strcmp(v,"1") && !TlkPrideFinalLifeSelected();
}
static void NativeMenu200Event(const char *kind){
    if(!NativeMenu200Enabled() || !final_menu_art_mode)return;
    unsigned scene=MenuPointer197(0xdf);
    if(!strcmp(kind,"FinalSceneBegin") && !MenuWord197(0x1ff9e) && !MenuWord197(0x2000) &&
       !MenuWord197(0x2004) && !MenuWord197(0x1ffaa) && !MenuWord197(0x1ffa8) &&
       (scene==0xc00387 || scene==0xc0080d) && MenuPointer197(0xb243)==0xc35a82){
        native_menu200_armed=1;native_menu200_active=native_menu200_exiting=native_menu200_updates=0;
    }
    if(!native_menu200_armed)return;
    if(!strcmp(kind,"FinalInputHold") && scene==0xc0057b && !MenuWord197(0x1ffa8)){
        if(native_menu200_active)native_menu200_updates++;
        else native_menu200_active=1;
    }
    if(!strcmp(kind,"ContinueTitleExit") && native_menu200_active)native_menu200_exiting=1;
    if(!strcmp(kind,"frame") && native_menu200_active &&
       (scene!=0xc0057b || (native_menu200_exiting && !(g_snes->ppu->inidisp&15)))){
        native_menu200_armed=native_menu200_active=native_menu200_exiting=0;
    }
}
static void NativeMenu200Paint(uint32_t *pixels,int width){
    if(!NativeMenu200Enabled() || !native_menu200_active || (width!=256 && width!=320))return;
    if(!TlkFinalArtDrawMenuViewport(final_menu_art,124+native_menu200_updates,0,0,(unsigned)width,final_menu_canvas))exit(120);
    unsigned brightness=g_snes->ppu->inidisp&0x80?0:g_snes->ppu->inidisp&15;
    unsigned start=(320-width)/2;
    for(unsigned y=0;y<224;y++)for(unsigned x=0;x<(unsigned)width;x++){
        uint32_t c=final_menu_canvas[y*320+x+start],rgb=0xff000000u;
        for(unsigned shift=0;shift<24;shift+=8){unsigned v=(c>>shift&255)>>3;v=v*brightness/15;rgb|=((v<<3)|(v>>2))<<shift;}
        pixels[y*width+x]=rgb;
    }
}
"""
'''
# The builder executes in this wrapper's namespace and records both sources.
source = source.replace(anchor,injection+'\n'+anchor)
source = source.replace('paths = [Path(__file__),bp,old,pre,target,rsp]',
                        'paths = [Path(__file__),builder,bp,old,pre,target,rsp]')
source = source.replace('Read-only pre-guard callbacks and native menu scalar fields. Needs current production neutrality qualification.',
                        'Private installed MD Game Over painter on native final timing. Read-only guest; output changed. No Continue support, public capability, save or source-switch qualification.')
exec(compile(source,str(builder),'exec'))

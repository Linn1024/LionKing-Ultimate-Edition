"""Build an excluded last-life scene/fade prototype with its own frontend copy."""
from pathlib import Path

original=Path(__file__).with_name('build_pride_final_display_probe.py')
source=original.read_text()
for before,after in [
    ("ROOT/'build/pride-final-display-probe2'","ROOT/'build/pride-final-scene-probe3'"),
    ('tools/pride_final_display_probe.c','tools/pride_final_scene_probe.c'),
    ('paths=[Path(__file__),source,','paths=[Path(__file__),original,fast_original,fast_source,frontend,source,')]:
    assert source.count(before)>=1,before
    source=source.replace(before,after)
needle="    command=argv(entry['command']);obj=out/'host.obj'"
replacement='''    fast_original=ROOT/'tools/pride_final_fast_assets_probe.c'
    fast_source=out/'fast.c';fast_text=fast_original.read_text()
    anchor='_Bool __wrap_RtlRunFrame(uint32 inputs)'
    assert fast_text.count(anchor)==1
    fast_source.write_text(fast_text.replace(anchor,'_Bool FinalSceneRunNative(uint32 inputs)'))
    source.write_text('#include <stdint.h>\\nvoid FinalSceneCaptureNative(const uint8_t*);\\nvoid FinalScenePaintNative(uint32_t*);\\n#define __wrap_RtlRunFrame PrideObservedRunFrame\\n#include "'+(ROOT/'engine/runner/pride/tlk_pride_host.c').as_posix()+'"\\n#undef __wrap_RtlRunFrame\\n#include "'+fast_source.as_posix()+'"\\n#include "'+(ROOT/'tools/pride_final_scene_probe.c').as_posix()+'"\\n')
    command=argv(entry['command']);obj=out/'host.obj'
    define=next(n for n,s in enumerate(command) if s.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='))
    frontend_original=Path(command[define].split('=',1)[1].strip('"'))
    shutil.copytree(frontend_original.parent,out/'frontend')
    frontend=out/'frontend'/frontend_original.name;text=frontend_original.read_text()
    anchor='TlkWideEndFrame(s_pixels);';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+' FinalSceneCaptureNative(s_pixels);')
    anchor='memcpy(s_screen, s_pixels, sizeof s_screen);';assert text.count(anchor)==1
    text=text.replace(anchor,anchor+' FinalScenePaintNative(s_screen);')
    anchor='    DrawFrontendOverlays();\\n    for (int y = 0; y < kHeight; y++) {';assert text.count(anchor)==1
    text=text.replace(anchor,'    FinalScenePaintNative(s_screen);\\n'+anchor)
    frontend.write_text(text)
    command[define]='-DTLK_PRIDE_FRONTEND_SOURCE="'+frontend.as_posix()+'"'
    command+=['-I'+str(ROOT/'tools')]
'''
assert source.count(needle)==1
source=source.replace(needle,replacement)
exec(compile(source,str(original),'exec'))

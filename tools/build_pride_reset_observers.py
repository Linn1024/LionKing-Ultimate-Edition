"""Build full-field observers for corrected reset and selected-audio lifecycles."""
import argparse
import json
from pathlib import Path
import shutil

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--audio-mixer',action='store_true')
args=parser.parse_args()
original_builder=ROOT/'tools/build_pride_reset_views.py'
output='audio3' if args.audio_mixer else 'views3'
source=original_builder.read_text()
source=source.replace('build/pride-reset/fixed','build/pride-reset/fixed3').replace('build/pride-reset/views','build/pride-reset/'+output)
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_builder,')
if args.audio_mixer:
    source=source.replace("for host in ('headless','sdl'):","for host in ('sdl',):")
    injection="""        source=source.replace('TlkCameraSetWidth(256);RtlRunFrame', 'TlkAudioFrame(i);TlkCameraSetWidth(256);RtlRunFrame')
        source=source.replace('RtlRenderAudio(samples,n,2);', 'RtlRenderAudio(samples,n,2);TlkAudioMix(samples,n,48000);')
        source=source.replace('    bridge_values(&pending_after', '    TlkAudioFrame(0);\\n    bridge_values(&pending_after')
"""
else:
    injection="        source=source.replace('reset_audio_fraction=0;', 'reset_audio_fraction=0; s_polls_frame=0;')\n"
source=source.replace('        generated=out/',injection+'        generated=out/')
exec(compile(source,str(original_builder),'exec'))
if args.audio_mixer:
    # Install before running: absence must never turn an MD test into native proof.
    backend_build=ROOT/'build/pride-reset/audio-views2/build-report.json'
    bound(backend_build)
    backend=backend_build.parent/'genesis_plus_gx_libretro.dll'
    out=ROOT/'build/pride-reset'/output
    shutil.copy2(backend,out/backend.name)
    report_path=out/'build-report.json';report=json.loads(report_path.read_text())
    for path in (backend_build,backend,out/backend.name):
        report['source_sha256'][str(path.relative_to(ROOT)).replace('\\','/')]=digest(path)
    report_path.write_text(json.dumps(report,indent=2)+'\n')

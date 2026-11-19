"""Observe selected MD audio with the real per-field scheduler during warm-up."""
from pathlib import Path

wrapped_builder = Path(__file__).with_name('build_pride_reset_views.py')
source = wrapped_builder.read_text().replace('build/pride-reset/fixed', 'build/pride-reset/fixed2').replace('build/pride-reset/views', 'build/pride-reset/audio-views')
source = source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),wrapped_builder,')
source = source.replace("for host in ('headless','sdl'):", "for host in ('sdl',):")
injection = '''        source=source.replace('TlkCameraSetWidth(256);RtlRunFrame', 'TlkAudioFrame(i);TlkCameraSetWidth(256);RtlRunFrame')
        source=source.replace('RtlRenderAudio(samples,n,2);', 'RtlRenderAudio(samples,n,2);TlkAudioMix(samples,n,48000);')
        source=source.replace('    bridge_values(&pending_after', '    TlkAudioFrame(0);\\n    bridge_values(&pending_after')
'''
source = source.replace('        generated=out/', injection + '        generated=out/')
exec(compile(source, str(wrapped_builder), 'exec'))

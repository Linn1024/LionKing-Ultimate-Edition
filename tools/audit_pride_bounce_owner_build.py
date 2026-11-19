"""Audit the fresh maintained ownership player and actual generated hook points."""
from pathlib import Path

original=Path(__file__).with_name('audit_pride_player_build.py')
source=original.read_text().replace("base = ROOT / 'build/pride-player'","base = ROOT / 'build/pride-bounce-owner-work/player'")
source=source.replace("assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base)), source",
    "assert not (source.is_relative_to(ROOT / 'build') and not source.is_relative_to(base) and not source.is_relative_to(ROOT/'build/pride-bounce-owner-work/game-program')), source")
source=source.replace("ROOT / 'build/pride-player-configure2.log', ROOT / 'build/pride-player-build.log'",
    "ROOT/'build/pride-bounce-owner-work/configure.log', ROOT/'build/pride-bounce-owner-work/build.log',original,ROOT/'build/pride-bounce-owner-work/game-program/generation-report.json',ROOT/'build/pride-bounce-owner-baseline/report.json',ROOT/'engine/runner/tlk_native_audio_owner.c',ROOT/'engine/runner/tlk_native_audio_owner.h',ROOT/'engine/runner/tlk_audio_owner_history.inc',ROOT/'engine/runner/tlk_audio.c',ROOT/'engine/runner/pride/pride_actor_handoff_compiled_hooks.h',ROOT/'engine/cmake/runtime-patches/native_audio_owner_dsp.hunks',ROOT/'engine/cmake/runtime-patches/native_audio_owner_spc.hunks'")
needle="    report = dict(result='BUILT',"
insert='''    required=(0xc21955,0xc21c90,0xc21e15,0xc21ebf,0xc2212e,0xc22349)
    generated=ROOT/'build/pride-bounce-owner-work/game-program/hooks'
    text=''.join((generated/name).read_text() for name in ('bankc2_part13_v2.c','bankc2_part14_v2.c'))
    for pc in required:
        assert f'PrideSceneCompiledPreOpcode(cpu,0x{pc:06X}u)' in text,hex(pc)
    assert text.count('PrideSceneCompiledPreOpcode(cpu,0xC21E15u)')==2
'''
source=source.replace(needle,insert+needle)
exec(compile(source,str(original),'exec'))

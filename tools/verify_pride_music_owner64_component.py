"""Verify music hardware lifetime across software-driver invalidation."""
from pathlib import Path

original_wrapper=Path(__file__).with_name('verify_pride_music_owner62_component.py')
script=original_wrapper.read_text().replace("ROOT/'build/pride-music-output62/component'", "ROOT/'build/pride-music-output65/component'")
script=script.replace('out.mkdir()', 'out.mkdir(parents=True)')
extra=r'''
    /* A verified KON can still be pending when the CPU starts a new driver.
     * Its owner follows the hardware commit, not the software reboot. */
    TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);ram[0x2e3+8]=0xe0;
    TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);TlkNativeAudioOwnerLatchKon(128);
    cpu.D=0x1f00;cpu.m_flag=1;cpu.x_flag=0;cpu.DB=0;
    lifecycle(&cpu,0xc21ebf,ram);CHECK(!s_sem_driver_valid);
    TlkNativeAudioOwnerCommit(7);CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);
    CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));
    TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);
    CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    ram[0x600]^=1;SemDriverValidate(ram);CHECK(!s_sem_driver_valid);
    CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);
    CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));ram[0x600]^=1;
    TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);
    CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));TlkNativeAudioOwnerReset();
    CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));
'''
anchor='anchor="    text=text.replace('
assert script.count(anchor)==1
script=script.replace(anchor,'extra += '+repr(extra)+'\n'+anchor)
script=script.replace("'paths=[Path(__file__),original,'", "'paths=[Path(__file__),original,Path(__file__).with_name(\"verify_pride_music_owner62_component.py\"),'")
exec(compile(script,str(original_wrapper),'exec'))

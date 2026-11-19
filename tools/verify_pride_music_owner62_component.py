"""Check current ownership lifetime, pending KON and fail-closed restoration."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_owned_audio_component.py')
source=original.read_text()
source=source.replace("ROOT/'build/pride-bounce-owner-work/component'", "ROOT/'build/pride-music-output62/component'")
source=source.replace('800','896')
anchor='int TlkResourcesUseMd(const char *id) { return 1; }'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\nstatic int music_selected=1;\nint TlkAudioNativeMusicSelected(void) { return music_selected; }')
extra=r'''
    /* A new software-slot assignment must not change the currently sounding
     * voice until its actual hardware keyon commits. */
    ram[0x2e3+8]=0xe0;
    TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);
    TlkNativeAudioOwnerLatchKon(128);TlkNativeAudioOwnerCommit(7);
    CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    CHECK(!TlkNativeAudioOwnerMusicMute(6,0,0));
    CHECK(!TlkNativeAudioOwnerMusicMute(7,1,0));
    CHECK(!TlkNativeAudioOwnerMusicMute(7,0,-1));
    music_selected=0;CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));music_selected=1;
    uint8_t music_wram[131072],music_aram[65536];
    memcpy(music_wram,g_ram,sizeof music_wram);memcpy(music_aram,ram,sizeof music_aram);
    for(unsigned ch=0;ch<8;ch++)TlkNativeAudioOwnerMusicMute(ch,0,0);
    CHECK(!memcmp(music_wram,g_ram,sizeof music_wram));CHECK(!memcmp(music_aram,ram,sizeof music_aram));
    ram[0x2e3+8]=0;TlkNativeAudioOwnerSpc(0xd34,8,7,0,ram);
    CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    TlkNativeAudioOwnerLatchKon(128);CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    CHECK(TlkNativeAudioOwnerSave(saved,896));TlkNativeAudioOwnerReset();
    CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));CHECK(TlkNativeAudioOwnerLoad(saved,896));
    CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    TlkNativeAudioOwnerCommit(7);CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));
    CHECK(TlkNativeAudioOwnerLoad(saved,896));CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    memcpy(invalid,saved,896);SemPut32(invalid+892,257);
    CHECK(!TlkNativeAudioOwnerLoad(invalid,896));CHECK(TlkNativeAudioOwnerMusicMute(7,0,0));
    ram[0x600]^=1;CHECK(TlkNativeAudioOwnerLoad(saved,896));
    CHECK(!TlkNativeAudioOwnerMusicMute(7,0,0));ram[0x600]^=1;
'''
anchor="    text=text.replace('    printf(\"PASS %u driver lifecycle checks'"
assert source.count(anchor)==1
source=source.replace(anchor,'    extra += '+repr(extra)+'\n'+anchor)
source=source.replace('paths=[Path(__file__),', 'paths=[Path(__file__),original,')
source=source.replace("scope='maintained code identity/queue/reset/serialization plus unknown-code restore'",
                      "scope='current music and bounce driver identity, pending KON, reused slots, output guards, read-only guest and current serialization'")
exec(compile(source,str(original),'exec'))

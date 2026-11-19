"""Verify independent cub death frames/palette through the Windows renderer.

Ordinary full routes prove coverage/isolation; loaded death intervals separately
compare the custom compositor with every PPU pixel and check palette colors.
Graphics do not select the differing MD death staging/timing behavior.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-death-art';out.mkdir(exist_ok=True)
    report_path=out/'report.json';report_path.write_text(json.dumps({'result':'RUNNING'})+'\n')
    catalog=json.loads((ROOT/'build/pride-sprites/catalog.json').read_text())
    death_poses={int(r['snes'],16) for r in catalog['cub_death_frames']};assert len(death_poses)==20
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    profiles={}
    for name,extra in {'native':'','frames':'graphics.sprites.simba.cub.frames = md\n',
                       'palette':'graphics.sprites.simba.cub.palette = md\n',
                       'both':'graphics.sprites.simba.cub = md\n'}.items():
        path=out/(name+'.ini');path.write_text('schema = 1\ngame = snes\ndisplay.viewport = md\n'+extra);profiles[name]=path
    tape=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape'
    neutral=out/'neutral.polled.tape';neutral.write_bytes(bytes(6000*2))
    common=['--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md']
    def run(name,profile,end,mode='aot',load=None,save=None,headless=False,width=320):
        folder=out/name;folder.mkdir(exist_ok=True)
        env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(folder/'coverage.json')
        cmd=[ROOT/('engine/build-win/tlk_headless.exe' if headless else 'dist/LionKing.exe'),*common,
             '--resource-profile',profiles[profile],'--frames',str(end),'--input-polled',neutral if load else tape]
        if headless:cmd+=['--wide',str(width),'--wide-png',folder/'picture.png']
        else:cmd+=['--config',config,'--no-pace','--no-audio','--no-record','--wav',folder/'route.wav',
                   '--wav-seconds','100','--dump-window',folder/'window.png','--dump-scene',folder/'scene.json']
        if mode=='lle':cmd.append('--lle')
        if load:cmd+=['--load',load]
        if save:cmd+=['--save-at',str(save[0]),save[1]]
        with (folder/'run.log').open('wb') as log:
            subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
        return folder
    runs={};all_guest=[];all_audio=[]
    state=out/'entry.state';playing=out/'playing.state'
    for profile in profiles:
        modes={}
        for mode in ('aot','lle'):
            saved=(4440,state) if profile=='native' else (4550,playing) if profile=='both' else None
            folder=run(profile+'-'+mode,profile,5400,mode,save=saved if mode=='aot' else None)
            guest=hashes(folder/'run.log');audio=wav_data(folder/'route.wav')
            all_guest.append(guest);all_audio.append(audio)
            coverage=json.loads((folder/'coverage.json').read_text())
            assert coverage['owned_native_death_frames']==20
            if profile in ('native','palette'):
                assert death_poses<=set(coverage['seen_owned_native_death_poses']),('Native owned death frames not rendered',profile,coverage)
            if profile in ('frames','both'):
                assert death_poses<={r['snes'] for r in coverage['seen_cub_poses']},('Unmapped death frames',profile,coverage)
            modes[mode]={'hashes':guest,'wav_sha256':digest(folder/'route.wav')}
        assert modes['aot']==modes['lle']
        runs[profile]=modes
        print(profile,'ordinary full death/revival, selected source frames and exact audio/guest isolation PASS',flush=True)
    assert all(g==all_guest[0] for g in all_guest) and all(a==all_audio[0] for a in all_audio)
    # Every new MD frame is anchored/indexed-identical to its native counterpart.
    # The independent native PPU is therefore an exact pixel oracle in this
    # loaded death interval, for both frame selections and widths/modes.
    oracles=[]
    for width in (256,320):
        for profile in ('native','frames'):
            for mode in ('aot','lle'):
                folder=run(f'oracle-{width}-{profile}-{mode}',profile,4773,mode,load=state,headless=True,width=width)
                text=(folder/'run.log').read_text()
                match=re.search(r'wide=\d+ frames=(\d+) stage_frames=(\d+) custom_lines=(\d+) native_mismatch=(\d+)',text)
                assert match and int(match[3])>70000 and match[4]=='0',(width,profile,mode,text[-1200:])
                oracles.append({'width':width,'profile':profile,'mode':mode,'frames':int(match[1]),
                                'custom_lines':int(match[3]),'native_pixel_mismatches':0})
    print('All20 death images:333 fields x8 compositor/PPU pixel oracles PASS',flush=True)
    # Color mapping is verified from original palette words, separately from
    # frame artwork. The death screen has no overlapping world graphics.
    md=(ROOT/'Lion King, The (World).md').read_bytes()
    def color555(raw):
        c=[((raw>>shift)&7)*4+(((raw>>shift)&7)>>2) for shift in (1,5,9)]
        return c[0]|c[1]<<5|c[2]<<10
    def rgb(c):return tuple((((c>>s)&31)<<3)|(((c>>s)&31)>>2) for s in (0,5,10))
    md_colors=[rgb(color555(int.from_bytes(md[0x1d78aa+i*2:0x1d78ac+i*2],'big'))) for i in range(16)]
    pictures=[]
    for frame in (4501,4570,4660,4735):
        images={};scenes={}
        for profile in profiles:
            folder=run(f'picture-{frame}-{profile}',profile,frame,load=state)
            images[profile]=pixels(folder/'window.png');scenes[profile]=json.loads((folder/'scene.json').read_text())
            assert scenes[profile]['cub_death_frame'] and not scenes[profile]['stage_detected']
        assert images['native']==images['frames'] and images['palette']==images['both']
        width,height,base=images['native'];assert (width,height)==(640,448)
        changed=images['palette'][2];palette=scenes['native']['obj_palette0']
        lookup={rgb(palette[i]):md_colors[i] for i in range(16)}
        pieces=[p for p in scenes['native']['pieces'] if p['position_pointer']==0xb21b and not p['fixed']]
        assert pieces
        left=(min(p['screen'][0] for p in pieces)+32)*2;right=(max(p['screen'][0]+p['size'] for p in pieces)+32)*2
        top=min(p['screen'][1] for p in pieces)*2;bottom=max(p['screen'][1]+p['size'] for p in pieces)*2
        differences=0
        for y in range(height):
            for x in range(width):
                at=y*width+x;original=base[at];actual=changed[at]
                inside=left<=x<right and top<=y<bottom
                # Transparent sprite pixels expose the black backdrop, whose
                # color is independent of OBJ palette entry zero.
                assert not inside or original==(0,0,0) or original in lookup
                expected_color=lookup[original] if inside and original!=(0,0,0) else original
                assert actual==expected_color,('Death palette pixel differs',frame,x,y,original,actual,expected_color)
                differences+=actual!=original
        assert differences>500,('MD palette not applied',frame,differences)
        pictures.append({'frame':frame,'changed_pixels':differences,'exact_palette_pixel_mapping':True})
    print('Four death phases: independent frames/palettes, exact colors and preserved HUD/background PASS',flush=True)
    # Graphics remain compatible while the native animation is already playing.
    continuation=[]
    for profile in profiles:
        folder=run('loaded-playing-'+profile,profile,4773,load=playing)
        reference=run('playing-control-'+profile,profile,4773,save=(4550,out/('control-'+profile+'.state')))
        audio=wav_data(folder/'route.wav');full=wav_data(reference/'route.wav')
        assert audio and audio==full[-len(audio):] and hashes(folder/'run.log')==hashes(reference/'run.log')
        assert pixels(folder/'window.png')==pixels(reference/'window.png')
        continuation.append({'profile':profile,'exact_audio_bytes':len(audio),'exact_picture_and_guest':True})
    result={'result':'PASS','scope':__doc__,'player_sha256':digest(ROOT/'dist/LionKing.exe'),
            'headless_sha256':digest(ROOT/'engine/build-win/tlk_headless.exe'),'unique_death_frames':20,
            'owned_native_frame_rendering_verified':True,
            'ordinary_power_on_runs':8,'ordinary_audio_and_guest_identical_across_sources':True,'runs':runs,
            'ppu_oracles':oracles,'palette_pictures':pictures,'graphics_changed_playing_continuation':continuation,
            'ordinary_input_sha256':digest(tape),'catalog_sha256':digest(ROOT/'build/pride-sprites/catalog.json'),
            'staging_or_timing_gameplay_changed':False}
    report_path.write_text(json.dumps(result,indent=2)+'\n')
    print('Pride cub death frame/palette coverage PASS; original staging/timing remains independently open',flush=True)


if __name__=='__main__':main()

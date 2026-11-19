"""Replay later levels with real MD audio mixing and scene-specific scenery."""
import argparse,csv,json,os,re,subprocess
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--frames',type=int,choices=(19400,40000,60648),default=19400)
    frames=parser.parse_args().frames
    out=ROOT/({19400:'build/next-level-mix',40000:'build/later-level-mix',60648:'build/final-level-mix'}[frames]);out.mkdir(parents=True,exist_ok=True)
    profile=out/'resources.ini';profile.write_text((ROOT/'profiles/next-levels.ini').read_text())
    if frames==60648:
        with profile.open('a') as f:
            f.write('audio.music.be_prepared = md\naudio.music.simbas_return = md\naudio.music.pride_rock = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    results={};intermediate={}
    for mode in ('aot','lle'):
        folder=out/mode;folder.mkdir(exist_ok=True);env=os.environ.copy();env['TLK_MD_SOUND_COMMANDS']=str(folder/'commands.csv');env['TLK_AUDIO_STEMS']=str(folder/'stems.csv')
        cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),'--config',str(config),
             '--frames',str(frames),'--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),'--no-pace','--no-audio','--no-record',
             '--hash-at',','.join(map(str,[*range(500,frames,500),frames])),'--dump-scene',str(folder/'scene.json'),
             '--wav',str(folder/'start.wav'),'--wav-seconds','1']
        # Keep the WAV handle open so every frame is mixed, while bounding the
        # file to one second. Later audio is verified through driver/stem logs.
        if mode=='lle':cmd.append('--lle')
        log=folder/'game.log'
        with log.open('wb') as f:subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=600)
        level=json.loads((folder/'scene.json').read_text())['level']
        assert level=={19400:3,40000:6,60648:9}[frames],(mode,'Later-level route stopped',level)
        commands=list(csv.DictReader((folder/'commands.csv').open()));tracks=[int(r['value']) for r in commands if r['selector']=='1']
        required={2,83} if frames==19400 else {2,83,145,258,40,281}
        if frames==60648:required|={327,311,432}
        assert required<=set(tracks),(mode,tracks)
        stems=list(csv.DictReader((folder/'stems.csv').open()))
        assert any(5000<int(r['frame'])<12000 and int(r['md_peak'])>500 for r in stems),'Second-level music not rendered'
        assert any(13500<int(r['frame'])<18500 and int(r['md_peak'])>500 for r in stems),'Third-level music not rendered'
        results[mode]=hashes(log);intermediate[mode]=re.findall(r'frame=\d+ frame_sha256=[0-9a-f]+ wram_sha256=[0-9a-f]+',log.read_text())
        print(mode,'ordinary power-on route reaches level',level,'with selected MD tracks',sorted(required),'PASS',flush=True)
    checks=(frames+499)//500
    assert len(intermediate['aot'])==checks and intermediate['aot']==intermediate['lle'] and results['aot']==results['lle'],'Mixed AOT/LLE differs'
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,'frames':frames,'intermediate_hash_checks':checks,'hashes':results,'audio_mixed_all_frames':True,'required_md_programs':sorted(required),'final_level':level},indent=2)+'\n')


if __name__=='__main__':main()

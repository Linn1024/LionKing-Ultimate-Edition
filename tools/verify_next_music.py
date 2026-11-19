"""Verify independent MD music for all nine later main levels."""
import csv,json,os,subprocess,wave
from audit_scenes import ROOT
from verify_windows import hashes


def main():
    out=ROOT/'build/next-level-music';out.mkdir(parents=True,exist_ok=True)
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),'--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),'--no-pace','--no-audio','--no-record']
    reports={}
    for level,leaf,track in [(1,'cant_wait_to_be_king',2),(2,'elephant_graveyard',83),
                             (3,'stampede',145),(4,'simbas_exile',258),
                             (5,'hakuna_matata',40),(6,'simbas_destiny',281),
                             (7,'be_prepared',327),(8,'simbas_return',311),
                             (9,'pride_rock',432)]:
        native=out/f'{level}-native.ini';native.write_text('schema = 1\ngame = snes\n');state=out/f'{level}.state'
        with (out/f'{level}-prepare.log').open('wb') as f:subprocess.run(base+['--resource-profile',str(native),'--practice-level',str(level),'--frames','2300','--save-at','2300',str(state)],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
        runs={}
        for mode in ('native','md-aot','md-lle','sibling'):
            stem=out/f'{level}-{mode}';profile=stem.with_suffix('.ini');choice=''
            if mode.startswith('md'):choice=f'audio.music.{leaf} = md\n'
            if mode=='sibling':choice='audio.music.'+('elephant_graveyard' if level==1 else 'cant_wait_to_be_king')+' = md\n'
            profile.write_text('schema = 1\ngame = snes\n'+choice)
            env=os.environ.copy();env['TLK_MD_SOUND_COMMANDS']=str(stem)+'-commands.csv';env['TLK_AUDIO_STEMS']=str(stem)+'-stems.csv'
            cmd=base+['--resource-profile',str(profile),'--load',str(state),'--frames','2600','--wav',str(stem)+'.wav','--wav-seconds','6']+(['--lle'] if mode=='md-lle' else [])
            log=stem.with_suffix('.log')
            with log.open('wb') as f:subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
            commands=list(csv.DictReader(open(str(stem)+'-commands.csv')));stems=list(csv.DictReader(open(str(stem)+'-stems.csv')))
            tracks=[int(r['value']) for r in commands if r['selector']=='1']
            if mode.startswith('md'):
                assert tracks and set(tracks)=={track},(level,mode,tracks)
                assert stems and max(int(r['md_peak']) for r in stems)>500,(level,mode,'silent MD track')
            else:assert not tracks,(level,mode,'sibling music leaked')
            with wave.open(str(stem)+'.wav','rb') as w:audio=w.readframes(w.getnframes());assert w.getnchannels()==2 and w.getframerate()==48000 and len(audio)>200000
            runs[mode]={'hashes':hashes(log),'audio':audio,'tracks':tracks,'md_peak':max((int(r['md_peak']) for r in stems),default=0),'native_tail_peak':max((int(r['native_peak']) for r in stems[-100:]),default=0)}
        assert runs['native']['hashes']==runs['sibling']['hashes'] and runs['native']['audio']==runs['sibling']['audio'],'sibling source changed sound'
        assert runs['md-aot']['hashes']==runs['md-lle']['hashes'] and runs['md-aot']['audio']==runs['md-lle']['audio'],'music AOT/LLE differs'
        assert runs['native']['audio']!=runs['md-aot']['audio'],'music choice invisible'
        reports[str(level)]={m:{k:v for k,v in row.items() if k!='audio'} for m,row in runs.items()}
        print('Level',level,'original MD music',track,'audible, independent, AOT/LLE-identical PASS',flush=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','levels':reports},indent=2)+'\n')


if __name__=='__main__':main()

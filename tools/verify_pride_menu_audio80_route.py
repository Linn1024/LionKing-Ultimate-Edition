"""Original native preservation, independent menu commands, actual PCM and full win."""
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-menu-audio80';bp=base/'build-report.json';bound(bp)
    reference=ROOT/'build/pride-audio-dispatch75/report.json';prior=bound(reference)
    assert prior['result']=='CURRENT_DISPATCH_INVENTORIED'
    out=base/'route';out.mkdir();checks={};commands={};observations={}
    keys=['title_cursor','title_selection','options_adjustment','options_exit']
    pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    hashes=lambda folder:re.findall(pattern,(folder/'run.log').read_text())
    for name in ('native','menus-aot','menus-lle'):
        folder=out/name;folder.mkdir();cmd=prior['command'].copy();cmd[0]=str(base/'player.exe')
        profile=Path(cmd[cmd.index('--resource-profile')+1]).read_text()
        if name!='native':profile+='\n'+'\n'.join('audio.effects.'+key+' = md' for key in keys)+'\n'
        (folder/'resources.ini').write_text(profile);(folder/'host.ini').write_bytes(Path(cmd[cmd.index('--config')+1]).read_bytes())
        for flag,file in [('--config','host.ini'),('--resource-profile','resources.ini'),('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')]:cmd[cmd.index(flag)+1]=str(folder/file)
        if name.endswith('lle'):cmd+=['--lle']
        env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
        env.update(SDL_VIDEODRIVER='dummy',TLK_AUDIO_EVENTS=str(folder/'events.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'driver.csv'))
        with (folder/'run.log').open('wb') as log:
            rc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW).returncode
        scene=json.loads((folder/'scene.json').read_text())
        checks[name+'_full_walkthrough_next_level']=rc==0 and len(hashes(folder))==6000 and scene['level']==1
        driver=list(csv.DictReader((folder/'driver.csv').open()))
        observations[name]=dict(driver=driver,gameplay=scene['latched_gameplay'])
        commands[name]=cmd;print(name,'exit',rc,'level',scene['level'],'driver commands',len(driver),flush=True)
    native=out/'native';a=out/'menus-aot';b=out/'menus-lle'
    checks['native_all6000_guest_fields_preserved']=hashes(native)==hashes(reference.parent)
    checks['native_whole_pcm_preserved']=digest(native/'audio.wav')==digest(reference.parent/'audio.wav')
    for name,folder in [('aot',a),('lle',b)]:
        checks[name+'_all6000_canonical_pictures_preserved']=[r[:2] for r in hashes(folder)]==[r[:2] for r in hashes(native)]
        checks[name+'_final_gameplay_preserved']=observations['menus-'+name]['gameplay']==observations['native']['gameplay']
        actual=[(r['selector'],r['value']) for r in observations['menus-'+name]['driver']]
        control=[(r['selector'],r['value']) for r in observations['native']['driver']]
        checks[name+'_five_menu_commands_then_original_gameplay']=actual==[('2','100'),('2','101'),('2','101'),('2','101'),('2','101')]+control
        stems=list(csv.DictReader((folder/'stems.csv').open()))
        checks[name+'_audible_menu_md_stem']=any(591<=int(r['frame'])<=800 and int(r['md_peak'])>0 for r in stems)
    for file in ('window.png','scene.json','audio.wav','driver.csv','events.csv'):
        checks[file+'_selected_mode_parity']=digest(a/file)==digest(b/file)
    checks['selected_all6000_guest_mode_parity']=hashes(a)==hashes(b)
    def pcm(folder):
        with wave.open(str(folder/'audio.wav'),'rb') as stream:
            assert stream.getframerate()==48000 and stream.getsampwidth()==2 and stream.getnchannels()==2
            return stream.readframes(stream.getnframes())
    actual=pcm(a);control=pcm(native);acc=0.;samples=0
    for _ in range(591):
        acc+=48000/(21477272/357366);n=int(acc);acc-=n;samples+=n
    checks['whole_pcm_identical_before_first_menu_cue']=actual[:samples*4]==control[:samples*4]
    checks['selected_menu_audio_changes_actual_output']=actual[samples*4:samples*4+300000]!=control[samples*4:samples*4+300000]
    paths=[Path(__file__),bp,reference]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                original_md_semantic_scope='title cursor, title Start/Options selection, sampled Options value adjustment and silent Start return; native menu timing retained',
                full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

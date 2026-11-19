"""Qualify live attack ordering, independent media and genuine cold continuations."""
import csv
import json
import os
from pathlib import Path
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-porcupine38';out=base/'runtime-verification';out.mkdir()
    tool=ROOT/'tools/capture_pride_porcupine2.py';reports={};checks={};commands={}
    def capture(label,source='md',frames=1530,extra=()):
        cmd=['python',str(tool),'--player','build/pride-porcupine38','--output',label,'--source',source,'--frames',str(frames),*map(str,extra)]
        commands[label]=cmd;subprocess.run(cmd,cwd=ROOT,check=True,timeout=240)
        reports[label]=bound(base/label/'report.json');checks[label+'_capture']=reports[label]['result']=='PASS'
    capture('attack-seed',frames=1460,extra=['--save-at',1460])
    capture('attack-warm')
    capture('attack-lle',extra=['--lle'])
    tree=[json.loads(line) for line in (base/'attack-seed/tree.jsonl').read_text().splitlines()]
    index=tree[-1]['poll_index'];assert tree[-1]['field']==1460
    for label,extra in [('attack-cold',[]),('attack-cold-lle',['--lle'])]:
        capture(label,extra=['--load','build/pride-porcupine38/attack-seed/saved.state','--poll-offset',index,*extra])
    capture('attack-native',source='snes')
    for label,lle in [('native-route',False),('native-route-lle',True)]:
        capture(label,source='snes',frames=4500,extra=['--lle'] if lle else [])
    media=out/'md-sound.ini';media.write_text('schema = 1\ngame = snes\naudio.effects.world.porcupine = md\n')
    art=out/'md-art.ini';art.write_text('schema = 1\ngame = snes\ngraphics.sprites.enemies.other = md\n')
    capture('attack-md-sound',extra=['--profile',media.relative_to(ROOT)])
    capture('native-md-sound',source='snes',extra=['--profile',media.relative_to(ROOT)])
    capture('attack-md-art',extra=['--profile',art.relative_to(ROOT)])
    def equal(label,left,right,names=('window.png','scene.json','audio.wav','attack.csv')):
        a=base/left;b=base/right;checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        for name in names:checks[label+'_'+name]=digest(a/name)==digest(b/name)
    equal('modes','attack-warm','attack-lle')
    equal('cold_modes','attack-cold','attack-cold-lle')
    equal('cold_warm','attack-cold','attack-warm',('window.png','scene.json'))
    equal('native_modes','native-route','native-route-lle',('window.png','scene.json','audio.wav'))
    equal('art_independent','attack-md-art','attack-warm',('scene.json','audio.wav','attack.csv'))
    checks['art_changes_actual_client']=pixels(base/'attack-md-art/window.png')!=pixels(base/'attack-warm/window.png')
    checks['cold_remaining_pcm']=pcm(base/'attack-cold/audio.wav')==pcm(base/'attack-warm/audio.wav')[len(pcm(base/'attack-seed/audio.wav')):]
    checks['cold_trace_is_exact_suffix']=(base/'attack-warm/attack.csv').read_text().endswith('\n'.join((base/'attack-cold/attack.csv').read_text().splitlines()[1:])+'\n')
    def cue_fields(label):
        rows=list(csv.DictReader((base/label/'events.csv').open()))
        return [int(r['frame']) for r in rows if r['event']=='0015']
    checks['md_cue1470']=cue_fields('attack-warm')==[1470]
    checks['native_cue1478']=cue_fields('attack-native')==[1478]
    checks['md_sound_keeps_md_timing']=cue_fields('attack-md-sound')==[1470]
    checks['md_sound_keeps_native_timing']=cue_fields('native-md-sound')==[1478]
    checks['sound_changes_pcm']=pcm(base/'attack-md-sound/audio.wav')!=pcm(base/'attack-warm/audio.wav')
    driver=list(csv.DictReader((base/'attack-md-sound/driver.csv').open()))
    checks['md_sound_driver105_once']=sum(r['selector']=='2' and r['value']=='105' for r in driver)==1
    previous=ROOT/'build/pride-pickup-flight35/porcupine-native-control'
    checks['native35_guest_preserved']=hashes(base/'attack-native/run.log')==hashes(previous/'run.log')
    for name in ('window.png','scene.json','audio.wav'):checks['native35_'+name]=digest(base/'attack-native'/name)==digest(previous/name)
    for label in ('complete-wide','complete-wide-lle'):
        reports[label]=bound(base/label/'report.json');checks[label+'_completed']=json.loads((base/label/'scene.json').read_text())['level']==1
    equal('full_modes','complete-wide','complete-wide-lle')
    checks['v4_source_bit22']=int.from_bytes((base/'attack-seed/saved.state').read_bytes()[8:12],'little')==4 and bool(int.from_bytes((base/'attack-seed/saved.state').read_bytes()[32:36],'little')&0x00400000)
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for label,seed,selected in [('md-to-native',base/'attack-seed/saved.state','snes'),('native-to-md',ROOT/'build/pride-porcupine37/native-save/saved.state','md')]:
        folder=out/label;folder.mkdir();profile=folder/'resources.ini'
        profile.write_text('schema = 1\ngame = snes\ngameplay.levels.pride_lands.porcupine_attack = '+selected+'\n')
        cmd=reports['attack-warm']['command'].copy()
        for flag,value in [('--resource-profile',profile),('--frames',1530),('--dump-window',folder/'window.png'),('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--load',str(seed)];commands[label]=cmd
        with (folder/'run.log').open('wb') as log:run=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        text=(folder/'run.log').read_text();checks[label+'_reject_before_guest']=run.returncode==8 and 'loaded_state=' not in text and not (folder/'window.png').exists()
        checks[label+'_specific_message']='porcupine-attack source' in text
    paths=[Path(__file__),tool,base/'build-report.json',previous/'report.json',*[base/label/'report.json' for label in reports]]
    build=bound(base/'build-report.json')
    checks['binary_and_all321_inputs_bound']=len(build['link_inputs_sha256'])==321 and digest(base/'player.exe')==build['binary_sha256'] and all(digest(ROOT/p)==sha for p,sha in build['link_inputs_sha256'].items())
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,cold_poll_offset=index,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

"""Flight source/viewport guards, current cold continuation and unchanged play."""
import json
import os
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels
from verify_pride_final_scene_runtime import pcm


def main():
    base=ROOT/'build/pride-pickup-flight35';prior=ROOT/'build/pride-pickup-flight34'
    out=base/'save-verification';out.mkdir();checks={};commands={}
    build=base/'build-report.json';current=bound(build)
    old_build=prior/'build-report.json';old=bound(old_build)
    failed=prior/'integration/report.json';old_checks=bound(failed)
    checks['retained_wrong_source_failure']=old_checks['result']=='FAIL' and [k for k,v in old_checks['checks'].items() if not v]==['moving_save_rejects_wrong_source']
    labels=['wide-flight-view','wide-warm','wide-cold','wide-cold-lle','native-flight-view','flight-ui','complete-wide']
    reports={label:bound(base/label/'report.json') for label in labels}
    def equal(label,a,b):
        checks[label+'_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[label+'_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[label+'_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
        checks[label+'_motion']=(a/'flight.csv').read_bytes()==(b/'flight.csv').read_bytes()
    equal('warm34_preserved',base/'wide-warm',prior/'wide-warm')
    equal('cold_lle',base/'wide-cold',base/'wide-cold-lle')
    equal('full34_preserved',base/'complete-wide',prior/'complete-wide')
    seed=base/'wide-flight-view';warm=base/'wide-warm';cold=base/'wide-cold'
    checks['cold_warm_guest']=hashes(cold/'run.log')==hashes(warm/'run.log')
    checks['cold_warm_client']=pixels(cold/'window.png')==pixels(warm/'window.png')
    checks['cold_remaining_pcm']=pcm(cold/'audio.wav')==pcm(warm/'audio.wav')[len(pcm(seed/'audio.wav')):]
    checks['current_full_completion']=json.loads((base/'complete-wide/scene.json').read_text())['level']==1
    a=current['link_inputs_sha256'];b=old['link_inputs_sha256']
    checks['only_backend_save_object_changed']=len(set(a)-set(b))==len(set(b)-set(a))==1 and all(a[p]==b[p] for p in set(a)&set(b))
    data=(seed/'saved.state').read_bytes();native=(base/'native-flight-view/saved.state').read_bytes()
    checks['raw_version4_layout']=data[:8]==native[:8]==b'TLKSTAT1' and int.from_bytes(data[8:12],'little')==int.from_bytes(native[8:12],'little')==4
    flags=int.from_bytes(data[32:36],'little');native_flags=int.from_bytes(native[32:36],'little')
    checks['new_source_bit_saved']=bool(flags&0x00800000) and not native_flags&0x00800000
    checks['native_camera_flight_width_saved']=(flags>>8)&32767==320
    ui=reports['flight-ui'];checks['current_real_f12_switches']=ui['result']=='PASS' and len(ui['checks'])==13 and all(ui['checks'].values())
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    cases=[('md-to-snes',seed,'snes','md',seed/'saved.state','pickup-flight source'),
           ('snes-to-md',base/'native-flight-view','md','md',base/'native-flight-view/saved.state','pickup-flight source'),
           ('wrong-width',seed,'md','snes',seed/'saved.state','viewport'),
           ('unsafe34',seed,'md','md',prior/'wide-flight-view/saved.state','pickup-flight source')]
    for label,origin,source,viewport,state,error in cases:
        folder=out/label;folder.mkdir();profile=folder/'resources.ini'
        text=(origin/'resources.ini').read_text()
        text=text.replace('pickup_flight = md','pickup_flight = '+source).replace('pickup_flight = snes','pickup_flight = '+source)
        text=text.replace('display.viewport = md','display.viewport = '+viewport)
        profile.write_text(text)
        template=reports[origin.name]['command'];cmd=template.copy()
        if '--save-at' in cmd:i=cmd.index('--save-at');del cmd[i:i+3]
        for flag,value in [('--resource-profile',profile),('--frames',1601),('--dump-window',folder/'window.png'),
                           ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
        cmd+=['--load',str(state)];commands[label]=cmd
        with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
        text=(folder/'run.log').read_text()
        checks[label+'_rejected_before_guest']=r.returncode==8 and 'loaded_state=' not in text and not (folder/'window.png').exists()
        checks[label+'_specific_reason']=error in text
        print(label,r.returncode,error in text,flush=True)
    paths=[Path(__file__),build,old_build,failed,*[base/label/'report.json' for label in labels]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

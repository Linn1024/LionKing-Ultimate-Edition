"""Prove automatic saves occur after audio and splice real F5/F9 PCM exactly."""
import argparse
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from verify_pride_audio_state import wav_data
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import hashes


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native-aot','md-lle'),default='native-aot')
    p.add_argument('--normal-route',action='store_true');args=p.parse_args()
    base=ROOT/'build/pride-practice';ui=base/('verified/normal-ui' if args.normal_route else 'verified/ui')/args.case;report_path=ui/'report.json'
    before=json.loads(report_path.read_text());assert before['result']=='PASS' and all(before['checks'].values())
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());binary=base/'practice-sdl.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==before['binary_sha256']==build['runs']['sdl']['binary_sha256']
    out=base/('verified/boundary-normal' if args.normal_route else 'verified/boundary')/args.case;out.mkdir(parents=True,exist_ok=True);assert not (out/'report.json').exists()
    profile=out/'resources.ini';profile.write_bytes((ui/'resources.ini').read_bytes())
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
    field=before['observations']['automatic_saved_field'];state=out/'explicit.state'
    command=list(before['command']);command[command.index('--resource-profile')+1]=str(profile)
    command[command.index('--config')+1]=str(config)
    for flag,name in (('--dump-window','window.png'),('--dump-png','guest.png'),('--wav','audio.wav')):
        command[command.index(flag)+1]=str(out/name)
    command+=['--no-pace','--save-at',str(field),str(state)]
    with (out/'run.log').open('wb') as log:
        r=subprocess.run(command,cwd=ROOT,env=environment(out),stdout=log,stderr=subprocess.STDOUT,timeout=180)
    assert not r.returncode,r.returncode
    automatic=(ui/'automatic-original.state').read_bytes()
    checks=dict(automatic_equals_explicit=automatic==state.read_bytes(),control_automatic_equal=automatic==(out/'tlk_practice_restart.state').read_bytes(),
        final_guest=hashes(out/'run.log')==before['guest'])
    control=read_rows(out/'practice-fields.csv');live=read_rows(ui/'practice-fields.csv')
    rewinds=[i for i in range(1,len(live)) if int(live[i]['field'])<int(live[i-1]['field'])]
    assert len(rewinds)==2,rewinds
    loads=before['loads'] if args.normal_route else before['loads'][1:];assert len(loads)==2
    for n,i in enumerate(rewinds):assert int(live[i]['field'])==int(loads[n]['loaded_field'])+1
    def boundary(field):
        rows=[r for r in control if int(r['field'])==field+1];assert len(rows)==1,(field,len(rows))
        return int(rows[0]['wav_frames_before_audio'])*4
    a,b=wav_data(out/'audio.wav'),wav_data(ui/'audio.wav')
    first,second=(int(live[i]['wav_frames_before_audio'])*4 for i in rewinds)
    cut1=boundary(int(loads[0]['attempt_field']));start1=boundary(int(loads[0]['loaded_field']))
    cut2=boundary(int(loads[1]['attempt_field']));start2=boundary(int(loads[1]['loaded_field']))
    checks['initial_pcm_prefix']=b[:first]==a[:cut1]
    checks['manual_replay_pcm']=b[first:second]==a[start1:cut2]
    checks['restart_replay_pcm']=b[second:]==a[start2:]
    # The snapshot bytes above include the actual native view/audio/guest and
    # complete preparation cache. No masked client region or guest fixture.
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,report_path,ROOT/'tools/verify_pride_audio_state.py',ROOT/'tools/verify_pride_live_error_ui.py')}
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,normal_route=args.normal_route,
        saved_field=field,pcm_splice_bytes=[first,second],control_cuts=[cut1,start1,cut2,start2],
        binary_sha256=digest(binary),source_sha256=sources,command=command,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(args.case,result['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

"""Retain strict owned-scene saves alongside the separate pristine boot format."""
import argparse
import json
from pathlib import Path
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_preparation_state import frame_records,glyph_records
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import hashes,pixels


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=int,choices=(0,1),default=0);args=p.parse_args()
    start,width,graphics,save,age,load=('snes',256,'native','aot',225,'lle') if args.case==0 else ('md',320,'all','lle',300,'aot')
    base=ROOT/'build/pride-restart';out=base/'final/owned-saves'/str(args.case);out.mkdir(parents=True,exist_ok=True)
    assert not (out/'report.json').exists(),'Use a fresh proof directory'
    build_path=base/'build-report.json';build=json.loads(build_path.read_text());binary=base/'restart-probe.exe'
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==build['runs']['probe']['binary_sha256']
    reference=ROOT/'build/pride-repeat/scoped-headless'/f'{start}-{width}-{graphics}-{save}'
    profile=out/'resources.ini';profile.write_bytes((reference/'resources.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';state=out/'owned.state'
    entry=2459 if start=='snes' else 2458;at=entry+age
    commands={}
    def run(name,mode,extra):
        folder=out/name;folder.mkdir(exist_ok=True)
        command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
            '--resource-profile',profile,'--input',tape,'--frames',3000,'--wide',width,'--wide-png',folder/'picture.png',
            '--ram-log',folder/'route.ram']+extra
        if mode=='lle':command+=['--lle']
        commands[name]=list(map(str,command))
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(commands[name],cwd=ROOT,env=environment(folder),stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert not r.returncode,(name,r.returncode)
        return folder
    before=run('baseline',save,['--save-at',at,state]);after=run('resumed',load,['--load',state])
    scene=before/f'scene-{entry}'
    checks=dict(owned_format=state.read_bytes()[:8]==b'PRHSAVE1',guest=hashes(before/'run.log')==hashes(after/'run.log'),
        previous_guest=hashes(before/'run.log')==hashes(reference/'run.log'),
        final_image=pixels(before/'picture.png')==pixels(after/'picture.png'))
    a=(before/'route.ram').read_bytes().splitlines(keepends=True);b=(after/'route.ram').read_bytes().splitlines(keepends=True)
    checks['tracked_ram']=len(b)==3000-at and b==a[-len(b):]
    for folder,prior in ((before,reference),(scene,reference/f'scene-{entry}')):
        checks['previous_scene/'+folder.name]=digest(folder/'render-owned.rgb')==digest(prior/'render-owned.rgb')
    checks['remaining_scene']=frame_records(after/'render-owned.rgb',width)=={t:r for t,r in frame_records(scene/'render-owned.rgb',width).items() if entry+t>at}
    checks['glyphs']=glyph_records(after)==[(field,r) for field,r in glyph_records(scene) if field>at]
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv'):
        checks[name]=read_rows(after/name)==[r for r in read_rows(before/name) if int(r['field'])>at]
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),build_path,reference/'report.json',tape,ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_pride_live_error_ui.py')}
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',case=args.case,checks=checks,
        save_age=age,save_mode=save,load_mode=load,source_sha256=sources,binary_sha256=digest(binary),commands=commands,
        artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(args.case,report['result'],[n for n,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

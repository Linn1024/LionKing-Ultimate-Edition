"""Resume the actual second revival, including bank application and normal publication."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_repeat import BASE
from probe_pride_preparation_state import frame_records,glyph_records
from verify_pride_live_error_ui import environment,read_rows
from verify_windows import hashes,pixels

CASES=(('snes',256,'native','aot',225,'lle'),('snes',256,'native','lle',301,'aot'),
       ('md',320,'all','aot',269,'lle'),('md',320,'all','lle',300,'aot'))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',type=int,choices=range(4),default=0);args=p.parse_args()
    start,width,graphics,save,age,load=CASES[args.case];out=BASE/'saves'/str(args.case);out.mkdir(parents=True,exist_ok=True)
    entry=2459 if start=='snes' else 2458;at=entry+age
    before,after=out/'baseline',out/'resumed';before.mkdir(exist_ok=True);after.mkdir(exist_ok=True)
    cmd=[sys.executable,str(ROOT/'tools/probe_pride_repeat.py'),'--start',start,'--width',str(width),'--graphics',graphics,
        '--mode',save,'--save-at',str(at),'--output-root',str(before)]
    with (out/'baseline-driver.log').open('wb') as log:subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
    r=json.loads((before/'report.json').read_text());assert r['result']=='PASS'
    actual_second=r['scenes'][1];assert actual_second['begin_field']==entry
    state=before/'second.private-state';binary=BASE/'repeat-probe.exe';build_path=BASE/'build-report.json';build=json.loads(build_path.read_text())
    assert digest(binary)==build['runs']['probe']['binary_sha256']
    command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--resource-profile',before/'resources.ini',
        '--input',ROOT/'build/pride-repeated-route/oscillate/ordinary.tape','--load',state,'--frames','3000',
        '--wide',str(width),'--ram-log',after/'route.ram','--wide-png',after/'picture.png']
    if load=='lle':command+=['--lle']
    with (after/'run.log').open('wb') as log:run=subprocess.run(list(map(str,command)),cwd=ROOT,env=environment(after),stdout=log,stderr=subprocess.STDOUT,timeout=180)
    checks=dict(exit=run.returncode==0,guest=hashes(after/'run.log')==r['guest'])
    a=(before/'route.ram').read_bytes().splitlines(keepends=True);b=(after/'route.ram').read_bytes().splitlines(keepends=True)
    checks['tracked_ram']=len(b)==3000-at and b==a[-len(b):]
    scene=before/actual_second['folder']
    expected={t:data for t,data in frame_records(scene/'render-owned.rgb',width).items() if entry+t>at}
    checks['scene_records']=frame_records(after/'render-owned.rgb',width)==expected
    checks['glyphs']=glyph_records(after)==[(field,data) for field,data in glyph_records(scene) if field>at]
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv'):
        checks[name]=read_rows(after/name)==[row for row in read_rows(before/name) if int(row['field'])>at]
    checks['final_image']=pixels(after/'picture.png')==pixels(before/'picture.png')
    sources={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in (
        Path(__file__),ROOT/'tools/probe_pride_repeat.py',build_path,ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_pride_live_error_ui.py')}
    result=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',case=args.case,checks=checks,save_field=at,save_age=age,
        save_mode=save,load_mode=load,second_entry=entry,source_sha256=sources,binary_sha256=digest(binary),baseline_report_sha256=digest(before/'report.json'),
        resumed_artifacts_sha256={p.name:digest(p) for p in after.iterdir() if p.is_file()},
        full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(args.case,result['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

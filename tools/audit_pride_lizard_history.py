"""Pair actual lizard births and resolve the valid random reaction on this build."""
import csv
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_rng_audit import snes_step
from summarize_pride_practice import bound


def main():
    out=ROOT/'build/pride-lizard-history';paths=[Path(__file__)];checks={}
    for name in ('md/report.json','native/report.json','md-seed/report.json','rng-clear3/report.json'):
        path=out/name;r=bound(path);paths.append(path);assert r['result'] in ('CAPTURED','PASS')
    md={r['field']:r for r in json.loads((out/'md/actors.json').read_text())}
    native={r['field']:r for r in json.loads((out/'native/actors.json').read_text())}
    original_path=ROOT/'build/md-next-levels-replay/frames.json';original=json.loads(original_path.read_text());paths.append(original_path)
    nr=[dict(field=int(s[0]),player=[int(s[4],16),int(s[5],16)]) for line in (out/'native/game.ram').read_text().splitlines()
        for s in [line.split()] if s[1]=='0' and int(s[0])>930]
    mr=[b for a,b in zip(original,original[1:]) if b['poll']>a['poll'] and b['level']==0 and b['player'] is not None]
    ni=next(i for i,r in enumerate(nr) if r['player'][0]>65);mi=next(i for i,r in enumerate(mr) if r['player'][0]>65)
    pairs=[(a['field'],b['frame']) for a,b in zip(nr[ni:],mr[mi:]) if 1438<=a['field']<=1575]
    def actor(rows,field,address):return next((a['words'] for a in rows[field]['actors'] if a['actor']==address),None)
    checks['paired_births']=(pairs[0]==(1438,1827) and actor(native,1437,0xb413) is None and actor(md,1826,0x9ace) is None)
    births=list(csv.DictReader((out/'md/spawns.csv').open()))
    checks['original_constructor_marker_position']=any(r['frame']=='1827' and r['pc']=='18d414' and r['marker']=='14' and r['argument_x']=='576' and r['argument_y']=='688' for r in births)
    states={0xc160d5:0x19c004,0xc16451:0x19c39e,0xc150d7:0x199ac8}
    def canonical(w,external):
        state=(w[24]<<16|w[25]) if external else states.get(w[24]|w[25]<<16,-1)
        vx=(w[28]<<16|w[29]) if external else w[28]|w[29]<<16
        vy=(w[30]<<16|w[31]) if external else w[30]|w[31]<<16
        return [w[4],w[5],w[26],w[27],vx,vy,w[22],w[23],w[16],state]
    checked=[];first=None
    for nf,mf in pairs:
        a=actor(native,nf,0xb413);b=actor(md,mf,0x9ace);assert a and b
        left,right=canonical(a,False),canonical(b,True)
        if left!=right:first=dict(native_field=nf,md_field=mf,native=left,md=right);break
        checked.append([nf,mf])
    checks['history_matches_until_random_reaction']=first is not None and (first['native_field'],first['md_field'])==(1575,1959) and len(checked)>100
    before=actor(native,1574,0xb413);other=actor(md,1958,0x9ace)
    checks['same_attribute_and_tile_column']=before[32]&255==other[32]>>8==0x51 and before[35]==other[35]==36
    checks['next_update_crosses_tile_boundary']=before[4]==575 and before[4]>>4==35 and before[35]==36
    sample=out/'native/hl_wram_1574.bin';seed=int.from_bytes(sample.read_bytes()[0x1e00:0x1e03],'little');md_seed=json.loads((out/'md-seed/report.json').read_text())['seed']
    checks['current_live_seeds']=seed==0x60f4a8 and md_seed==0xa6ba04
    a,b=snes_step(seed),snes_step(md_seed)
    checks['valid_opposite_probability1_decisions']=a==(0xc0e854,188) and b==(0x4c7582,247) and a[1]<=204<b[1]
    old_path=ROOT/'build/pride-reaction-probability/report.json';old=json.loads(old_path.read_text());cases=ROOT/'build/pride-reaction-probability/cases.json'
    checks['prior_original_cpu_matrix_retained']=old['result']=='PASS' and old['matrix_cases']==1596 and digest(cases)==old['source_sha256']['cases']
    checks['current_native_predecision_snapshot_identical']=digest(sample)==old['source_sha256']['native_snapshot']
    checks['current_original_predecision_snapshot_identical']=digest(out/'md-seed/wram-1958.bin')==old['source_sha256']['md_snapshot']
    clear=bound(out/'rng-clear3/report.json');checks['naive_seed_only_override_invalid']=clear['cases']==48 and any(r['seed']==0x9f285a and r['checkpoint']==0 and r['m8']==0 and r['after']==0x9f2800 for r in clear['fixtures'])
    paths.extend([old_path,cases,ROOT/'tools/pride_rng_audit.py',ROOT/'docs/pride-reaction-probability.md'])
    report=dict(result='PARTIAL' if all(checks.values()) else 'INCOMPLETE',checks=checks,matching_lizard_controller_updates=len(checked),paired_updates=checked,first_action_difference=first,
        lizard_spawn_motion_bug_established=False,valid_rng_reaction_explanation_confirmed=True if all(checks.values()) else False,
        new_original_native_clear_fixtures=48,production_rng_source_enabled=False,full_first_level_fidelity_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='audit.json'})
    (out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],len(checks),'checks',len(checked),'matching lizard updates',[k for k,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

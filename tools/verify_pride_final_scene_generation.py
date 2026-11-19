"""Check maintained opt-in generation and unchanged normal hook/RNG output."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound

def main():
    out=ROOT/'build/pride-final-maintained-generation2';out.mkdir()
    generated=ROOT/'build/pride-final-compiled-generated2';extension=bound(generated/'report.json')
    tool=ROOT/'engine/scripts/generate_pride_guest.py';backend=ROOT/'build/pride-bounce-owner-work/game-program/codegen'
    commands={};reports={};checks={}
    for name,enabled in [('normal',False),('final',True)]:
        cmd=[sys.executable,str(tool),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
            '--out',str(out/name),'--codegen',str(backend)]
        if enabled:cmd.append('--final-scenes')
        with (out/(name+'.log')).open('wb') as log:
            subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        commands[name]=cmd;reports[name]=bound(out/name/'generation-report.json')
        print(name,'maintained generation completed',flush=True)
    old=ROOT/'build/pride-bounce-owner-work/game-program/hooks'
    for name in reports['normal']['instrumented_units']:
        checks[name+'/normal_unchanged']=digest(out/'normal/hooks'/name)==digest(old/name)
        checks[name+'/final_matches_verified_extension']=digest(out/'final/hooks'/name)==extension['generated_sha256'][name]
    names=sorted(p.name for p in (out/'normal/rng').glob('bank*.c'))
    checks['all_rng_units_unchanged_between_modes']=len(names)==137 and all(digest(out/'normal/rng'/name)==digest(out/'final/rng'/name) for name in names)
    checks['extension_opt_in_only']=reports['normal']['final_scene_hooks'] is False and reports['final']['final_scene_hooks'] is True
    paths=[Path(__file__),tool,ROOT/'engine/recomp/pride_final_hooks.json',generated/'report.json',
        out/'normal/generation-report.json',out/'final/generation-report.json']
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],len(checks),'checks',flush=True);assert all(checks.values()),checks

if __name__=='__main__':main()

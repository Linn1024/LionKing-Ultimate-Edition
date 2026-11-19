"""Relink the installed player with reviewed Continue-token artwork selection."""
import json
from pathlib import Path
import shutil
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound


def main():
    prior=ROOT/'build/pride-sprite-fresh44';old_path=prior/'build-report.json';old=bound(old_path)
    out=ROOT/'build/pride-continue-token46';out.mkdir()
    subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/game-patches'),
                    '--snesrecomp',str(ROOT/'engine'),'--out',str(out/'game')],check=True)
    rows=json.loads(subprocess.check_output(['C:/mingw32/bin/ninja.exe','-t','compdb','-x'],cwd=prior))
    inputs=argv('link '+(prior/'link.rsp').read_text())[1:];compiles={}
    for label,suffix,source in [
        ('sprites','/game/tlk_md_sprites.c.obj',out/'game/tlk_md_sprites.c'),
        ('wide','/pride_final_wide.c.obj',ROOT/'engine/runner/pride/final/pride_final_wide.c'),
        ('resources','/game/tlk_resources.c.obj',out/'game/tlk_resources.c')]:
        found=[r for r in rows if r.get('output','').replace('\\','/').endswith(suffix)];assert len(found)==1,(label,found)
        row=found[0];cmd=argv(row['command']);obj=out/(label+'.obj')
        for flag,value in [('-c',source),('-o',obj),('-MT',obj),('-MF',out/(label+'.d'))]:cmd[cmd.index(flag)+1]=str(value)
        with (out/(label+'-compile.log')).open('wb') as log:
            subprocess.run(cmd,cwd=prior,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        previous=(prior/row['output']).resolve();indices=[i for i,p in enumerate(inputs) if not p.startswith('-') and (prior/p).resolve()==previous]
        assert len(indices)==1;inputs[indices[0]]=obj.as_posix();compiles[label]=cmd
    rsp=out/'link.rsp';rsp.write_text(subprocess.list2cmdline(inputs))
    with (out/'link.log').open('wb') as log:
        subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(rsp),'-o',str(out/'player.exe')],cwd=prior,
                       stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    for name in ('genesis_plus_gx_libretro.dll','save-contract.json'):shutil.copyfile(prior/name,out/name)
    linked={(prior/p).resolve().relative_to(ROOT).as_posix():digest(prior/p) for p in inputs if not p.startswith('-') and p.lower().endswith(('.obj','.a'))}
    unchanged=sum(old['link_inputs_sha256'].get(p)==sha for p,sha in linked.items());assert unchanged==319 and len(linked)==322
    paths=[Path(__file__),old_path,rsp,ROOT/'engine/runner/tlk_md_sprites.c',ROOT/'engine/runner/tlk_md_sprites.h',
           ROOT/'engine/runner/tlk_continue_token_role.h', ROOT/'engine/generated/resources/pride_sprite_map.h', ROOT/'tools/pride_sprite_catalog.py', ROOT/'tools/pride_npc_pairs.json',ROOT/'engine/runner/tlk_wide.c',
           ROOT/'engine/cmake/game-patches/z-continue-token-resource.hunks',out/'game/tlk_resources.c',out/'game/tlk_md_sprites.c']
    report=dict(result='BUILT',binary_sha256=digest(out/'player.exe'),compiles=compiles,
                link_inputs_sha256=linked,unchanged_prior_inputs=unchanged,fresh_standalone_graph_claimed=False,
                installed_sprite_package_format_changed=False, installed_sprite_policy_changed=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('BUILT',report['binary_sha256'],'unchanged',unchanged,flush=True)


if __name__=='__main__':main()

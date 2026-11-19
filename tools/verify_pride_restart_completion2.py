"""Replay the credited complete Pride route with both title navigation choices."""
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
    base=ROOT/'build/pride-restart-difficulty25';bound(base/'build-report.json')
    source=ROOT/'build/pride-arena-work/completion/report.json';old=bound(source)
    fixtures=ROOT/'build/pride-restart-difficulty-fixtures/report.json';prepared=bound(fixtures)
    prefix=ROOT/'build/pride-restart-prefix-spaced99/report.json';adapted=bound(prefix)
    out=base/'completion2';out.mkdir();checks={};commands={};observations={}
    (out/'host.ini').write_text('opengl = 0\nscale = 2\n')
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))}
    for width,nav in [(256,'snes'),(256,'md'),(320,'md')]:
        pair=[]
        for lle in (False,True):
            label=f'{width}-{nav}'+('-lle' if lle else '');folder=out/label;folder.mkdir();pair.append(folder)
            cmd=old['command'].copy();cmd[0]=str(base/'player.exe')
            if nav=='md':cmd[cmd.index('--input-polled')+1]=adapted['command'][adapted['command'].index('--input-polled')+1]
            profile=folder/'resources.ini';profile.write_text(Path(cmd[cmd.index('--resource-profile')+1]).read_text()+
                '\ngameplay.levels.pride_lands.final_life = md\ngameplay.menus.title_navigation = '+nav+'\ndisplay.viewport = '+('snes' if width==256 else 'md')+'\n')
            for flag,value in [('--config',out/'host.ini'),('--resource-profile',profile),('--dump-window',folder/'window.png'),
                               ('--dump-scene',folder/'scene.json'),('--wav',folder/'audio.wav')]:cmd[cmd.index(flag)+1]=str(value)
            template=prepared['commands']['md-normal']
            for flag in ('--final-menu-assets','--final-native-assets','--title-bank-assets'):cmd +=[flag,template[template.index(flag)+1]]
            if lle:cmd.append('--lle')
            with (folder/'run.log').open('wb') as log:r=subprocess.run(cmd,cwd=ROOT,env=dict(clean,TLK_FINAL_MD_ART='1',TLK_SOFT_TREE_LOG=str(folder/'tree.jsonl')),
                stdout=log,stderr=subprocess.STDOUT,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
            commands[label]=cmd;checks[label+'_exit']=r.returncode==0
            scene=json.loads((folder/'scene.json').read_text());checks[label+'_next_level']=scene['level']==1
            rows=[json.loads(line) for line in (folder/'tree.jsonl').read_text().splitlines()]
            first=next((row for row in rows if row['descriptor']==0xc00387 and row['level']==0),None)
            checks[label+'_easy_selected']=first is not None and first['difficulty']==0
            observations[label]=dict(final_level=scene['level'],first_pride=first)
            print(label,r.returncode,'final level',scene['level'],'difficulty',first['difficulty'] if first else None,flush=True)
        a,b=pair
        checks[f'{width}_{nav}_lle_guest']=hashes(a/'run.log')==hashes(b/'run.log')
        checks[f'{width}_{nav}_lle_client']=pixels(a/'window.png')==pixels(b/'window.png')
        checks[f'{width}_{nav}_lle_pcm']=pcm(a/'audio.wav')==pcm(b/'audio.wav')
        if nav=='snes':
            checks['native_nav_old_guest']=hashes(a/'run.log')==hashes(source.parent/'run.log')
            checks['native_nav_old_client']=pixels(a/'window.png')==pixels(source.parent/'window.png')
            checks['native_nav_old_pcm']=pcm(a/'audio.wav')==pcm(source.parent/'audio.wav')
    checks['ordinary_corrected_prefix']=adapted['ordinary_inputs'] and not adapted['guest_or_rom_edits']
    checks['gameplay_suffix_unchanged']=adapted['checks']['gameplay_suffix_unchanged']
    paths=[Path(__file__),base/'build-report.json',source,fixtures,prefix]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,observations=observations,
                ordinary_inputs=True,guest_or_rom_edits=False,all_first_level_fidelity_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
                artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

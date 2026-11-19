"""Add frontend registration to the compiled jump hooks after focused318."""
from pathlib import Path
template=Path(__file__).with_name('build_pride_battle317.py')
source=template.read_text().replace("out=ROOT/'build/pride-battle317'","out=ROOT/'build/pride-battle319'")
anchor="    compiles=dict(prior['compiles'])"
source=source.replace(anchor,"""    original=cwd/'native-engine/tlk_pride_final_player_host-frontend/host'
    with (out/'frontend-patch.log').open('wb') as log:subprocess.run(['python',str(ROOT/'engine/scripts/apply_runtime_patches.py'),'--patches',str(ROOT/'engine/cmake/final-frontend-patches'),'--snesrecomp',str(original),'--out',str(out/'frontend')],stdout=log,stderr=subprocess.STDOUT,check=True)
    for name in ('tlk_resource_editor_sdl.h','tlk_resource_editor_selftest.h'):shutil.copy2(original/name,out/'frontend'/name)
"""+anchor)
anchor="        ('unit',previous_unit,unit,ROOT/'build/pride-hyena-voice72/unit.obj')]:"
source=source.replace(anchor,"""        ('unit',previous_unit,unit,ROOT/'build/pride-hyena-voice72/unit.obj'),
        ('host',prior['compiles']['host'],ROOT/'engine/runner/pride/final/pride_final_host.c',Path(prior['compiles']['host'][prior['compiles']['host'].index('-o')+1]))]:""")
anchor="        if label=='audio':cmd+=['-DTLK_BATTLE_MUSIC_TRIGGER_AVAILABLE=1']"
source=source.replace(anchor,anchor+"""
        if label=='host':
            i=next(i for i,v in enumerate(cmd) if v.startswith('-DTLK_PRIDE_FRONTEND_SOURCE='));cmd[i]='-DTLK_PRIDE_FRONTEND_SOURCE="'+(out/'frontend/sdl_main.c').as_posix()+'"'
""")
source=source.replace('retained==322','retained==321').replace('paths=[Path(__file__),bp,','paths=[Path(__file__),Path(__file__).with_name(\'build_pride_battle317.py\'),out/\'game/tlk_audio.c\',out/\'frontend/sdl_main.c\',ROOT/\'engine/cmake/final-frontend-patches/battle-music-trigger.hunks\',bp,')
exec(compile(source,str(template),'exec'))

"""Publish scene-v2 preparation with native contact and immutable palettes."""
from pathlib import Path
template=Path(__file__).with_name('publish_cant_wait375.py')
source=template.read_text()
source=source.replace('build/cant-wait372/build-report.json','build/pride382/build-report.json')
source=source.replace('build/cant-wait373/report.json','build/pride380/report.json').replace('build/cant-wait374-window/report.json','build/pride384-qualification/report.json')
source=source.replace('build/cant-wait371-cmake/build-report.json','build/pride378-cmake/build-report.json')
source=source.replace('dist/installed-preview362','dist/installed-preview372').replace('dist/installed-preview372\'\nout.mkdir','dist/installed-preview382\'\nout.mkdir')
source=source.replace("out=ROOT/'dist/installed-preview372'","out=ROOT/'dist/installed-preview382'")
source=source.replace("after=before.replace('dist/installed-preview372','dist/installed-preview372')","after=before.replace('dist/installed-preview372','dist/installed-preview382').replace('Resolve-PreparedFile $manifest.scene_cache 1','Resolve-PreparedFile $manifest.scene_cache 2')")
source=source.replace("info['cant_wait_foreground_scope']=", "info['required_scene_cache_version']=2;info['prepared_contact_scope']='8000 Pride contact cells loaded from Setup data; immutable Cant Wait palette tables included; installed playback does not reconstruct these from ROM.';info['cant_wait_background_scope']='Prepared original MD Plane B with three scroll regions and live palette controller; static tables from scene-v2.';info['cant_wait_foreground_scope']=")
source=source.replace('Preview372 adds prepared MD foreground artwork for Cant Wait to Be King.','Preview382 loads terrain contact tables and fixed palette recipes from Setup scene-v2 data.')
source=source.replace('build/cant-wait375-publication','build/pride385-publication')
source=source.replace('build/cant-wait371-setup','build/pride380/data').replace('build/cant-wait371-cmake/build/PrepareSceneAssets.exe','build/pride378-cmake/build/PrepareSceneAssets.exe')
source=source.replace('paths=[Path(__file__),build,','paths=[Path(__file__),template,build,')
assert "after=before.replace('dist/installed-preview372','dist/installed-preview382').replace(" in source
exec(compile(source,str(template),'exec'))

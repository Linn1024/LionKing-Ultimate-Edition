"""Stage installed-caption player and a launcher using the new prepared entry."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-caption277-installed';bp=base/'build-report.json';b=bound(bp)
proofs=[ROOT/'build'/p/'report.json' for p in ('pride-caption278-assets','pride-caption279-runtime')]
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values())
previous=ROOT/'dist/installed-preview268';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview277';out.mkdir()
for p in previous.rglob('*'):
    if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(base/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256'];info['required_caption_assets_version']=1
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text().replace('preview268','preview277')+'\nSetup now prepares caption images/palettes. Playback requires caption_assets v1\nand does not decode these images from ROM. Other startup paths remain hybrid.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';s=launcher.read_text();assert s.count('dist/installed-preview268')==1
source=s.replace('dist/installed-preview268','dist/installed-preview277')
anchor='$sprites = Resolve-PreparedFile $manifest.sprite_assets 1';assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    $captions = Resolve-PreparedFile $manifest.caption_assets 1')
anchor="'--sprite-assets',$sprites,";assert source.count(anchor)==1
source=source.replace(anchor,anchor+"'--caption-assets',$captions,")
candidate=base/'RunInstalledPreviewCandidate.ps1';candidate.write_text(source.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
(base/'RunInstalledPreview.publish.ps1').write_text(source)
paths=[Path(__file__),bp,*proofs,old,launcher,candidate,base/'RunInstalledPreview.publish.ps1']
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PACKAGED',b['binary_sha256'],flush=True)

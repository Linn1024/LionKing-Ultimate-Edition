"""Stage installed revival images with the existing verified asset dependencies."""
import json
from pathlib import Path
import shutil
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
base=ROOT/'build/pride-revival297-installed';bp=base/'build-report.json';b=bound(bp)
proofs=[ROOT/'build'/p/'report.json' for p in ('pride-revival298-assets','pride-revival299-runtime')]
for p in proofs:
    r=bound(p);assert r['result']=='PASS' and all(r['checks'].values())
previous=ROOT/'dist/installed-preview287';old=previous/'package-report.json';bound(old)
out=ROOT/'dist/installed-preview297';out.mkdir()
for p in previous.rglob('*'):
    if not p.is_file() or p.name in ('package-report.json','package.json','README.txt','LionKing.exe'):continue
    q=out/p.relative_to(previous);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(base/'player.exe',out/'LionKing.exe')
info=json.loads((previous/'package.json').read_text());info['player_sha256']=b['binary_sha256'];info['required_revival_assets_version']=1
(out/'package.json').write_text(json.dumps(info,indent=2)+'\n')
(out/'README.txt').write_text((previous/'README.txt').read_text().replace('preview287','preview297')+'\nSetup prepares revival/idle images; first respawn and saved revival restoration\nuse owned copies of the installed package instead of decoding ROM artwork.\n')
launcher=ROOT/'scripts/RunInstalledPreview.ps1';s=launcher.read_text();assert s.count('dist/installed-preview287')==1
s=s.replace('dist/installed-preview287','dist/installed-preview297')
anchor='$checkpoints = Resolve-PreparedFile $manifest.checkpoint_assets 1';assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n    $revival = Resolve-PreparedFile $manifest.revival_assets 1')
anchor="'--checkpoint-assets',$checkpoints,";assert s.count(anchor)==1
s=s.replace(anchor,anchor+"'--revival-assets',$revival,")
candidate=base/'RunInstalledPreviewCandidate.ps1';candidate.write_text(s.replace('$projectRoot = Split-Path $PSScriptRoot -Parent',"$projectRoot = '"+str(ROOT)+"'"))
(base/'RunInstalledPreview.publish.ps1').write_text(s)
paths=[Path(__file__),bp,*proofs,old,launcher,candidate,base/'RunInstalledPreview.publish.ps1']
(out/'package-report.json').write_text(json.dumps(dict(result='PACKAGED_FOR_VERIFICATION',published=False,
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PACKAGED',b['binary_sha256'],flush=True)

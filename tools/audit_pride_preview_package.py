"""Bind packaged files against their actual dist directory; retain the raw manifest."""
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest


def main():
    base=ROOT/'build/pride-launch2';raw_path=base/'preview-package.json';raw=json.loads(raw_path.read_text());out=ROOT/'dist/development-preview'
    for name,sha in raw['source_sha256'].items():assert digest(ROOT/name)==sha,name
    for name,sha in raw['artifacts_sha256'].items():assert digest(out/name)==sha,name
    paths=[Path(__file__),raw_path,*[out/name for name in raw['artifacts_sha256']]]
    report=dict(result='PASS',checks=dict(all_packaged_bytes_match=True,raw_manifest_preserved=True),binary_sha256=raw['binary_sha256'],
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},experimental_preview=True,default_installed_player_replaced=False)
    (base/'preview-package-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS packaged preview bytes',flush=True)


if __name__=='__main__':main()

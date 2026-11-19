"""Resume maintained226 All Bugs validation after storage cleanup, in fresh output."""
from pathlib import Path
import gzip
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
observer = ROOT / 'build/pride-menu226-integrated/allbugs-observer'
metadata = json.loads((observer / 'binary-archive.json').read_text())
assert shutil.disk_usage(ROOT).free > 5 * 1024**3, 'Need 5 GiB writable headroom'
binary = observer / 'player.exe'
if not binary.exists():
    archive = observer / metadata['archive']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == metadata['archive_sha256']
    data = gzip.decompress(archive.read_bytes())
    assert len(data) == metadata['original_bytes']
    assert hashlib.sha256(data).hexdigest() == metadata['original_sha256']
    with binary.open('xb') as output:
        output.write(data)
assert hashlib.sha256(binary.read_bytes()).hexdigest() == metadata['original_sha256']

script = Path(__file__).with_name('verify_pride_checkpoint52_allbugs.py')
source = script.read_text().replace('pride-checkpoint-animation52', 'pride-menu226-integrated')
source = source.replace("out = base/'allbugs-verification'", "out = ROOT/'build/pride-menu245-allbugs'")
source = source.replace('paths = [Path(__file__), build_path,', 'paths = [Path(__file__), script, observer/\'binary-archive.json\', build_path,')
exec(compile(source, str(script), 'exec'))

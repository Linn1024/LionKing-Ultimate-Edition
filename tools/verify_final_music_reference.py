"""Verify final-level themes against the unmodified original MD movie."""
import csv
import hashlib
import json
import struct
from audit_scenes import ROOT, read_rom


def main():
    rom = read_rom('Lion King, The (World).md',
                   'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    folder = ROOT/'build/md-final-music-reference'
    evidence = folder/'commands.csv'
    reference = json.loads((folder/'report.json').read_text())
    assert reference['frames'] >= 55000 and reference['music_commands_observed']
    assert not (folder/'lua-error.txt').read_text()
    rows = list(csv.DictReader(evidence.open()))
    observed = {}
    for level, track in ((7, 327), (8, 311), (9, 432)):
        assert struct.unpack_from('>H', rom, 0x1d723c+level*2)[0] == track
        matches = [r for r in rows if int(r['level_register']) == level+1
                   and int(r['value']) == track and r['caller'].lower() == '1d7430']
        assert matches, (level, track, 'No original loader music call')
        observed[str(level)] = {'program': track,
                              'original_entry_frames': [int(r['frame']) for r in matches]}
    report = {'result': 'PASS', 'scope': __doc__, 'levels': observed,
              'rom_sha256': hashlib.sha256(rom).hexdigest(),
              'movie_sha256': reference['movie_sha256'],
              'commands_sha256': hashlib.sha256(evidence.read_bytes()).hexdigest(),
              'source': 'https://tasvideos.org/10612S', 'emulator': 'BizHawk 2.11 / movie core',
              'frames': reference['frames'], 'unmodified_original_movie': True,
              'full_movie_synchronization_verified': False}
    out = ROOT/'build/final-music-reference'
    out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Original MD Be Prepared / Return / Pride Rock level themes PASS', flush=True)


if __name__ == '__main__':
    main()

"""Verify later-level music against observed calls in the matching MD emulator."""
import csv
import hashlib
import json
import struct
from audit_scenes import ROOT, read_rom


def main():
    rom = read_rom('Lion King, The (World).md',
                   'e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    folder = ROOT/'build/md-later-music-reference'
    evidence = folder/'commands.csv'
    rows = list(csv.DictReader(evidence.open()))
    reference = json.loads((folder/'report.json').read_text())
    assert reference['frames'] >= 40000 and not (folder/'lua-error.txt').read_text()
    tracks = {3:145, 4:258, 5:40, 6:281}
    observed = {}
    for level, track in tracks.items():
        assert struct.unpack_from('>H', rom, 0x1d723c+level*2)[0] == track
        matches = [row for row in rows if int(row['level_register']) == level+1
                   and int(row['value']) == track and row['caller'].lower() == '1d7430']
        assert matches, (level, track, 'No original level-loader music call')
        observed[str(level)] = {'program': track, 'original_entry_frames': [int(row['frame']) for row in matches]}
    report = {'result':'PASS', 'scope':__doc__, 'rom_sha256':hashlib.sha256(rom).hexdigest(),
              'commands_sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),
              'source':'https://tasvideos.org/10612S', 'emulator':'BizHawk 2.11 / movie core',
              'unmodified_original_movie':True, 'levels':observed,
              'standalone_core_later_sync':False}
    out = ROOT/'build/later-music-reference'
    out.mkdir(exist_ok=True)
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Original MD music calls for Stampede, Exile, Hakuna and Destiny PASS', flush=True)


if __name__ == '__main__':
    main()

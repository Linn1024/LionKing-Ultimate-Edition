"""Measure the original FM123 tail without level music or gameplay edits."""
import array
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import MdLab,ROOT
from audit_scenes import read_rom


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-lizard-launch-tail';out.mkdir()
    rom=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    game=MdLab();peaks=[]
    try:
        for _ in range(180):game.step()
        game.samples.clear()
        for field in range(1,361):
            start=len(game.samples);game.driver_step(2 if field==1 else None,123)
            samples=array.array('h',game.samples[start:]);peaks.append(max(map(abs,samples),default=0))
    finally:game.close()
    assert max(peaks)>500
    assert max(peaks[120:])==0,'Existing120-field effect window would truncate original FM123'
    paths=[Path(__file__),ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
    report=dict(result='PASS',original_command=[2,123],fields=360,peaks=peaks,
        last_field_above_one=max(i+1 for i,v in enumerate(peaks) if v>1),peak_after_120=max(peaks[120:]),
        controlled_original_driver_not_gameplay=True,production_changed=False,
        rom_sha256=hashlib.sha256(rom).hexdigest(),source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Original FM123 tail PASS; last audible field',report['last_field_above_one'],flush=True)


if __name__=='__main__':main()

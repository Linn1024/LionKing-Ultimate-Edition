"""Replay the three original MD difficulty routes without the instruction hook."""
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from md_lab import MdLab,png
reference=ROOT/'build/md-porcupine178-difficulty/report.json';ref=bound(reference);assert ref['result']=='CAPTURED'
out=ROOT/'build/md-porcupine189-neutral';out.mkdir();checks={}
for difficulty in ('easy','normal','hard'):
    folder=out/difficulty;folder.mkdir();inputs_path=reference.parent/difficulty/'inputs.json';pads=json.loads(inputs_path.read_text());prefix=ref['cases'][difficulty]['prefix_fields']
    expected=json.loads((reference.parent/difficulty/'frames.json').read_text());game=MdLab();game.core.retro_set_controller_port_device.argtypes=[__import__('ctypes').c_uint,__import__('ctypes').c_uint]
    for port in (0,1):game.core.retro_set_controller_port_device(port,513)
    rows=[]
    try:
        for field,pad in enumerate(pads,1):
            game.step(pad);game.samples.clear()
            if field<prefix:continue
            word=lambda at:game.work_ram[at]|game.work_ram[at+1]<<8
            player=word(0xcd48);valid=0x8000<=player<0xff80
            rows.append(dict(field=field,health=word(0xccf6),lives=word(0xccee),player=[word(player+8),word(player+10)] if valid else None,immunity=word(player+0x46) if valid else None,action=(word(player+0x30)<<16|word(player+0x32))&0xffffff if valid else 0))
            if len(rows)>1 and rows[-1]['health']<rows[-2]['health']:png(folder/f'hit-{field}.png',*game.image)
        png(folder/'final.png',*game.image)
    finally:game.close()
    checks[difficulty+'_all_observed_fields_neutral']=rows==expected
    checks[difficulty+'_all_actual_images_neutral']=all(digest(folder/p.name)==digest(p) for p in (reference.parent/difficulty).glob('*.png'))
    (folder/'frames.json').write_text(json.dumps(rows,indent=2)+'\n');print(difficulty,checks[difficulty+'_all_observed_fields_neutral'],flush=True)
paths=[Path(__file__),reference,ROOT/'tools/md_lab.py',ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
    scope='Unhooked original MD repeats all three real Options/approach inputs. Every recorded player health/lives/position/action/immunity sample and actual image is unchanged. Reaction attribution remains separately observed in178; this is not an entire-work-RAM or PCM comparison.',
    source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()}),indent=2)+'\n')
print('PASS' if all(checks.values()) else 'FAIL',sum(checks.values()),'/',len(checks),flush=True)

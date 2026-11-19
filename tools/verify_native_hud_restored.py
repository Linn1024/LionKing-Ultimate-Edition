"""Verify restored native widgets against original CPU glyph-building code."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from analyze_pride_scene_oam import records


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'build/pride-native-hud-oracle';out.mkdir(exist_ok=True)
    report=out/'report.json';report.write_text('{"result":"RUNNING"}\n')
    sources=[Path(__file__),ROOT/'tools/pride_native_hud_oracle.c',ROOT/'engine/runner/tlk_native_hud.c',
             ROOT/'engine/runner/tlk_native_hud.h',ROOT/'Lion King, The (USA).sfc']
    identities={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in sources}
    with (out/'build.log').open('wb') as log:
        subprocess.run(['cmake','--build','engine/build-win','--target','tlk_native_hud_oracle','-j','4'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    binary=ROOT/'engine/build-win/tlk_native_hud_oracle.exe';identity=digest(binary)
    env=os.environ.copy();env['TLK_NATIVE_HUD_ORACLE']=str(out/'original-fonts.bin')
    cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--lle','--frames','1400','--input-polled',ROOT/'engine/tapes/allbugsF.read.tape']
    with (out/'run.log').open('wb') as log:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=180)
    raw=(out/'original-fonts.bin').read_bytes();assert raw[:8]==b'SNHUD001'
    assert len(raw)==8+66*1032
    fonts={}
    for at in range(8,len(raw),1032):
        kind,maximum=struct.unpack_from('<II',raw,at)
        assert (kind,maximum) not in fonts
        fonts[kind,maximum]=raw[at+520:at+1032]
    assert set(fonts)=={(1,n) for n in range(4,13)}|{(0,n) for n in range(8,65)}
    ordinary=next(r for r in records(ROOT/'build/pride-scene-oam-audit/native/native-oam.bin') if r['head'][1]==350)
    assert fonts[1,6]==ordinary['ram'][0x2230:0x2430]
    assert fonts[0,24]==ordinary['ram'][0x2030:0x2230]
    assert 'all33792 font bytes exact PASS' in (out/'run.log').read_text()
    assert digest(binary)==identity
    for file,sha in identities.items():assert digest(ROOT/file)==sha,file
    report.write_text(json.dumps(dict(result='PASS',scope=__doc__,health_cases=9,roar_cases=57,
        original_cpu_font_bytes=33792,ordinary_checkpoint_widget_targets_exact=True,
        source_detached=True,alias_safe=True,atomic_rejection_and_full_rom_identity_verified=True,
        oracle_guest_value_fixtures=True,ordinary_gameplay_proof=False,
        library_linked_to_distributed_hosts=False,probe_sha256=identity,source_sha256=identities,
        artifacts_sha256={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p!=report}),indent=2)+'\n')
    print('Native widgets health9/roar57 original-CPU font cases, ordinary restored targets and source/atomic guards PASS',flush=True)


if __name__=='__main__':main()

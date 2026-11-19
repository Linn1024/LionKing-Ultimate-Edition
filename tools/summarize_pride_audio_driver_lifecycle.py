"""Bind observed transport/reset seams to original instructions and driver identity."""
import collections
import csv
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player/audio-driver-lifecycle-audit'
    rp=base/'report.json';assert all(bound(rp)['checks'].values())
    fp=ROOT/'build/pride-lizard-launch-work/spc-driver-fingerprint-report.json';fingerprint=bound(fp)['masked_sha256']
    rom=read_rom('Lion King, The (USA).sfc',
        '457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    assert rom[0x21955:0x2195c]==bytes.fromhex('a2007400cad0fb')
    assert rom[0x21e15:0x21e17]==bytes.fromhex('646d')
    assert rom[0x21c79:0x21c7d]==bytes.fromhex('e6bfd045')
    assert rom[0x21c8b:0x21c90]==bytes.fromhex('e04c00b02a')
    result={}
    for profile in ('native','bounce'):
        with (base/profile/'lifecycle.csv').open() as stream:rows=list(csv.DictReader(stream))
        counts=dict(collections.Counter(r['pc'] for r in rows))
        boot=[r for r in rows if r['pc']=='c21955']
        drains=[r for r in rows if r['pc']=='c21e15']
        assert len(boot)==3 and len(drains)==141
        assert all((r['d'],r['m'],r['x'])==('1f00','1','1') for r in boot)
        assert all((r['d'],r['db'],r['m'],r['x'])==('1f00','00','1','0') for r in drains)
        assert not any(r['pc']=='c21cc2' for r in rows)
        snapshots=list((base/profile).glob('aram_*.bin'))
        for path in snapshots:
            code=bytearray(path.read_bytes()[0x600:0x1e00])
            for address in (0x1a76,0x1a77,0x1a7f,0x1a80):code[address-0x600]=0
            assert hashlib.sha256(code).hexdigest()==fingerprint
        assert len(snapshots)==counts['c22349']+counts['c21f44']+counts['c2195c']
        result[profile]=dict(pc_counts=counts,boot_fields=[int(r['field']) for r in boot],
            completed_queue_batches=len(drains),snapshots_with_known_driver=len(snapshots),
            full_guest_fields_observer_neutral=4500)
    sources=[Path(__file__),rp,fp]
    output=ROOT/'build/pride-lizard-launch-work/native-driver-lifecycle-report.json';assert not output.exists()
    report=dict(result='OBSERVED_NATIVE_DRIVER_LIFECYCLE_VERIFIED',observations=result,
        known_driver_masked_sha256=fingerprint,queue_full_or_lock_rejection_observed=False,
        all_computed_queue_writes_excluded=False,production_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources})
    output.write_text(json.dumps(report,indent=2)+'\n');print(report['result'],flush=True)


if __name__=='__main__':main()

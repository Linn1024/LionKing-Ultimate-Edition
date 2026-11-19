"""Bound observed sound-driver code identity without masking arbitrary changes."""
import hashlib
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    base=ROOT/'build/pride-lizard-launch-work/player/spc-voice-owner-audit'
    reference=base/'report.json';assert all(bound(reference)['checks'].values())
    start,end=0x600,0x1e00
    exemplar=(base/'native/aram_1400.bin').read_bytes()
    patches={0x1a76:0x1a5c,0x1a77:0x1a66,0x1a7f:0x1a5f,0x1a80:0x1a69}
    for target,writer in patches.items():
        assert exemplar[writer:writer+3]==bytes((0xc5,target&255,target>>8))
    def masked(ram):
        code=bytearray(ram[start:end])
        for target in patches:code[target-start]=0
        return hashlib.sha256(code).hexdigest()
    fingerprint=masked(exemplar);snapshots=[];all_changed=set()
    for profile in ('native','bounce'):
        for path in sorted((base/profile).glob('aram_*.bin')):
            ram=path.read_bytes();assert len(ram)==65536
            changed={i for i in range(start,end) if ram[i]!=exemplar[i]}
            assert changed<=patches.keys() and masked(ram)==fingerprint
            all_changed.update(changed)
            snapshots.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=digest(path),
                self_modified_values={f'{at:04x}':ram[at] for at in patches}))
    assert len(snapshots)==22 and all_changed==patches.keys()
    output=ROOT/'build/pride-lizard-launch-work/spc-driver-fingerprint-report.json';assert not output.exists()
    report=dict(result='OBSERVED_MASKED_DRIVER_IDENTITY_VERIFIED',code_start=start,code_end=end,
        masked_sha256=fingerprint,snapshots=snapshots,
        original_absolute_store_writers={f'{at:04x}':f'{pc:04x}' for at,pc in patches.items()},
        all_unobserved_driver_states_proven=False,maintained_validation_implemented=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),reference)})
    output.write_text(json.dumps(report,indent=2)+'\n');print(report['result'],len(snapshots),'snapshots',flush=True)


if __name__=='__main__':main()

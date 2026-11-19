"""Bound other cue17 callers against original Pride placement data."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_lizard_launch_preview_history import bound


def main():
    callers=ROOT/'build/pride-lizard-launch-work/bounce-native-callers-report.json'
    assert bound(callers)['result']=='ORIGINAL_PROGRAM17_CALLERS_BOUNDED'
    rom=read_rom('Lion King, The (USA).sfc','457abe634e0a8be03e29513a3dca8f3e9d0ddc6bf97d8931f2316094260f3712')
    decoder=ROOT/'engine/tools/re/decompress.py'
    spec=importlib.util.spec_from_file_location('tlk_lz',decoder)
    lz=importlib.util.module_from_spec(spec);spec.loader.exec_module(lz)
    u24=lambda at:int.from_bytes(rom[at:at+3],'little')&0x3fffff
    entry=0xbe11+0x1b*6
    assert u24(entry+3)==0x58c14 and u24(0x58c14)==0x2e754
    scenes={}
    for descriptor in (0x387,0x80d):
        collision,_=lz.decompress(rom,u24(descriptor));world,_=lz.decompress(rom,u24(descriptor+9))
        assert len(world)==16000 and len(collision)==12316
        markers=Counter()
        for at in range(0,len(world),2):
            offset=(int.from_bytes(world[at:at+2],'little')&0xfff8)//2
            assert offset+4<=len(collision)
            markers[collision[offset+3]]+=1
        assert markers[0x1b]==0
        scenes[f'c0{descriptor:04x}']=dict(cells=len(world)//2,marker_counts=dict(markers),
            other_caller_initial_placements=markers[0x1b])
    paths=[Path(__file__),callers,decoder,ROOT/'engine/runner/tlk_md_assets.c']
    report=dict(result='ORIGINAL_PRIDE_OTHER_CALLER_PLACEMENTS_ABSENT',
        marker=27,descriptor='c58c14',constructor='c2e754',audio_caller='c2e99f',scenes=scenes,
        dynamic_spawn_or_indirect_reachability_proven=False,
        global_program17_filter_safe_proven=False,production_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    destination=ROOT/'build/pride-lizard-launch-work/bounce-other-caller-scope-report.json';assert not destination.exists()
    destination.write_text(json.dumps(report,indent=2)+'\n');print(report['result'],'two complete 8000-cell placement maps',flush=True)


if __name__=='__main__':main()

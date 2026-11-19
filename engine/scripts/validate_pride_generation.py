"""Validate the actual sources and outputs bound by a Pride generation report."""
import argparse
import hashlib
import json
from pathlib import Path
import native_hook_generation as native_hooks


def main():
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generation', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    args = parser.parse_args()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    folder = args.generation.resolve()
    r = json.loads((folder / 'generation-report.json').read_text())
    assert r['result'] == 'GENERATED'
    for name, sha in r['source_sha256'].items():
        assert digest(root / name) == sha, name
    for name, sha in r['generated_sha256'].items():
        assert digest(folder / name) == sha, name
    manifest = json.loads((root / 'engine/recomp/pride_hooks.json').read_text())
    assert digest(args.rom) == manifest['rom_sha256']
    expected_units = set(manifest['instrumented_units'])
    if r.get('final_scene_hooks'):
        extension = json.loads((root/'engine/recomp/pride_final_hooks.json').read_text())
        expected_units.update(extension.get('instrumented_units', []))
        emitted = ''.join((folder/'hooks'/unit).read_text() for unit in r['instrumented_units'])
        for pc in extension['hook_pcs']:
            assert f'PrideSceneCompiledPreOpcode(cpu,0x{int(pc, 16):06X}u)' in emitted, pc
    assert sorted(r['instrumented_units']) == sorted(expected_units)
    if r.get('native_hooks'):
        expected_trees = ['native','hooks'] if (folder/'native').exists() else ['hooks']
        assert r['native_hooks']['trees'] == expected_trees
        native_hooks.verify_metadata(folder, native_hooks.load(root/'engine'), r['native_hooks'])
    # The standalone player enables native ownership only with both CPU paths.
    required=(0xc21955,0xc21c90,0xc21e15,0xc21ebf,0xc2212e,0xc22349)
    hooks=''.join((folder/'hooks'/unit).read_text() for unit in
                  ('bankc2_part13_v2.c','bankc2_part14_v2.c'))
    for pc in required:
        assert f'0x{pc:06x}' in manifest['hook_pcs'],hex(pc)
        assert f'PrideSceneCompiledPreOpcode(cpu,0x{pc:06X}u)' in hooks,hex(pc)
    assert hooks.count('PrideSceneCompiledPreOpcode(cpu,0xC21E15u)')==2
    print('Pride generation sources and',len(r['instrumented_units'])+1,'output units verified',flush=True)


if __name__ == '__main__':
    main()

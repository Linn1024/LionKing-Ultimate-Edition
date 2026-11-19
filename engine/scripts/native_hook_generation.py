"""Shared native callback generation and verification for ordinary player builds."""
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(engine):
    path = engine / 'recomp/pride_native_hooks.json'
    manifest = json.loads(path.read_text())
    if manifest['schema'] != 1 or manifest['feature'] != 'be_prepared_behavior':
        raise ValueError('unsupported native callback manifest')
    points = manifest['hook_pcs']
    if points != sorted(set(points)) or any(type(p) is not int or not 0 <= p <= 0xffffff for p in points):
        raise ValueError('invalid native callback points')
    for entries in manifest['continuations'].values():
        if any(pc not in points for pc, _, _ in entries):
            raise ValueError('continuation destination must be an explicit native callback point')
    return manifest


def environment(clean, manifest, enabled):
    env = {k: v for k, v in clean.items() if not k.startswith('TLK_COMPILED_')}
    env.update(TLK_COMPILED_NATIVE_HOOK_POINTS=json.dumps(manifest['hook_pcs'] if enabled else []),
               TLK_COMPILED_CONTINUATIONS=json.dumps(manifest['continuations'] if enabled else {}),
               TLK_COMPILED_TAIL_ENTRIES=json.dumps(manifest['tail_entries'] if enabled else {}))
    return env


def finish_tree(folder, manifest):
    # A shard may begin after its function's declaration prefix. Declare the
    # complete optional API before each translation unit, independently of how
    # the backend divided functions between shards.
    header = ('#ifndef TLK_NATIVE_HOOKS_API_H\n#define TLK_NATIVE_HOOKS_API_H\n'
              '#include "common_cpu_infra.h"\n#include "pride_scene_compiled_hooks_api.h"\n'
              'extern uint32_t interp_bridge_compiled_pre_opcode(CpuState *,uint32_t);\n')
    header += ''.join('RecompReturn '+name+'_continue(CpuState *,uint32_t,uint16,uint8);\n'
                      for name in sorted(manifest['continuations']))
    header += ''.join('RecompReturn '+name+'(CpuState *);\n' for name in sorted(manifest['tail_entries']))
    (folder/'tlk_native_hooks_api.h').write_text(header+'#endif\n')
    for path in folder.glob('bank*.c'):
        source = path.read_text()
        if '#include "tlk_native_hooks_api.h"' in source:
            raise ValueError('native callback generation requires a fresh output tree')
        path.write_text('#include "tlk_native_hooks_api.h"\n'+source)
    verify_tree(folder, manifest)


def verify_tree(folder, manifest):
    texts = {unit: (folder/unit).read_text() for unit in manifest['units']}
    all_text = '\n'.join(texts.values())
    for pc in manifest['hook_pcs']:
        if f'interp_bridge_compiled_pre_opcode(cpu,0x{pc:06X}u)' not in all_text:
            raise ValueError(('missing native callback', str(folder), hex(pc)))
    for name in manifest['continuations']:
        if f'RecompReturn {name}_continue(CpuState *cpu,uint32_t _resume_pc' not in all_text:
            raise ValueError(('missing native continuation body', name))
    for name, entries in manifest['tail_entries'].items():
        for pc, m, x in entries:
            key = pc | (m << 24) | (x << 25)
            fragment = (f'case 0x{key:08X}u: {{ cpu->host_return_valid=_hrv; '
                        'cpu_tailcall_inherit_return_context(_entry_s,_hrv); '
                        f'RecompReturn _tc={name}(cpu);')
            if fragment not in texts['bankc0_part05_v2.c']:
                raise ValueError(('missing normal actor-round restart tail', name))
    for unit, source in texts.items():
        prefix = '#include "tlk_native_hooks_api.h"\n'
        if not (source.startswith(prefix) or source.startswith('#include "pride_scene_compiled_hooks_api.h"\n'+prefix)):
            raise ValueError(('missing shard-wide native declarations', unit))


def metadata(folder, manifest, trees):
    files = {}
    for tree in trees:
        verify_tree(folder/tree, manifest)
        for name in [*manifest['units'], 'tlk_native_hooks_api.h']:
            files[tree+'/'+name] = digest(folder/tree/name)
    return dict(schema=1, feature=manifest['feature'], trees=list(trees), files=files)


def verify_metadata(folder, manifest, value):
    if value != metadata(folder, manifest, value['trees']):
        raise ValueError('native callback outputs differ from their generation record')

"""Optional compiled tail entries whose first instruction normalizes CPU width.

A REP/SEP immediate executes independently of incoming register width. A body
decoded for one entry width can therefore accept another only when that first
instruction makes both states identical before the next instruction. Validate
that premise against source bytes, then use the emitter's normal tail-call
return-context protocol. No guest instructions or return frames are fabricated.
"""
import re


def emit_tail_entries(source, entries, rom, rom_offset):
    if not entries:
        return source
    declarations = []
    cases = []
    for name, points in sorted(entries.items()):
        match = re.fullmatch(r'\w+_M([01])X([01])', name)
        if not match:
            raise ValueError(('invalid compiled target', name))
        base_m, base_x = map(int, match.groups())
        declarations.append('RecompReturn %s(CpuState *);' % name)
        for pc, m, x in points:
            if type(pc) is not int or not 0 <= pc <= 0xffffff or m not in (0, 1) or x not in (0, 1):
                raise ValueError(('invalid tail entry', name, pc, m, x))
            offset = rom_offset(pc >> 16, pc & 65535)
            opcode, mask = rom[offset:offset + 2]
            difference = ((base_m ^ m) << 5) | ((base_x ^ x) << 4)
            if opcode not in (0xc2, 0xe2) or not difference or difference & ~mask:
                raise ValueError(('entry does not normalize the differing width', name, pc))
            cases.append('case 0x%08Xu: { cpu->host_return_valid=_hrv; '
                         'cpu_tailcall_inherit_return_context(_entry_s,_hrv); '
                         'RecompReturn _tc=%s(cpu); RecompStackPop(); return _tc; }' %
                         (pc | (m << 24) | (x << 25), name))
    return '\n'.join(declarations) + '\n' + source.replace(
        'default: PrideSceneCompiledUnmapped(',
        '\n'.join(cases) + '\ndefault: PrideSceneCompiledUnmapped(')

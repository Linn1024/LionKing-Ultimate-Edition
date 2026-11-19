"""Codegen support for explicit, native continuations sharing a real return frame.

Copied into the patched emitter by 0015. No guest instructions are interpreted
by this adapter. The caller supplies its original stack watermark and return
kind; the destination skips its ordinary guest prologue and enters an emitted
instruction label. Empty configuration leaves generated bodies unchanged.
"""
import re


def emit_continuations(source, labels, entries):
    if not entries:
        return source
    signature = re.search(r'RecompReturn (\w+)\(CpuState \*cpu\) \{', source)
    if not signature:
        raise RuntimeError('continuation requires an ordinary compiled body')
    name = signature.group(1)
    local = {(pc, m, x) for pc, m, x in labels}
    declarations = []
    cases = []
    for destination, points in sorted(entries.items()):
        declarations.append('RecompReturn %s_continue(CpuState *,uint32_t,uint16,uint8);' % destination)
        for pc, m, x in points:
            if (pc, m, x) not in local:
                cases.append('case 0x%08Xu: { RecompStackPop(); return %s_continue(cpu,0x%06Xu,_entry_s,_hrv); }' %
                             (pc | (m << 24) | (x << 25), destination, pc))
    if cases:
        source = source.replace('default: PrideSceneCompiledUnmapped(', '\n'.join(cases) + '\ndefault: PrideSceneCompiledUnmapped(')
    if name in entries:
        for point in entries[name]:
            if tuple(point) not in local:
                raise RuntimeError(('continuation absent from compiled body', name, point))
        source = source.replace(signature.group(0),
                                'RecompReturn %s_continue(CpuState *cpu,uint32_t _resume_pc,uint16 _resume_s,uint8 _resume_hrv) {' % name, 1)
        # A resumed body must reach its destination instruction, not yield at
        # the unrelated ordinary function entry before reconstructing context.
        anchor = 'if (interp_bridge_lle_master_deadline_reached(cpu)'
        if anchor not in source:
            raise RuntimeError('missing compiled entry deadline')
        source = source.replace(anchor, 'if (!_resume_pc && interp_bridge_lle_master_deadline_reached(cpu)', 1)
        anchor = '  uint32 _host_return_pc24 = 0xFFFFFFFFu;'
        if source.count(anchor) != 1:
            raise RuntimeError('missing return-context cache')
        source = source.replace(anchor, '  if (_resume_pc) { _entry_s=_resume_s; _hrv=_resume_hrv; cpu->host_return_valid=_hrv; }\n' + anchor)
        anchor = '  if (g_recomp_stack_top >= 1) g_cpu_entry_s[g_recomp_stack_top - 1] = _entry_s;'
        if source.count(anchor) != 1:
            raise RuntimeError('missing stack watermark publication')
        dispatch = ['  if (_resume_pc) switch (_resume_pc | ((cpu->m_flag&1u)<<24) | ((cpu->x_flag&1u)<<25)) {']
        for pc, m, x in entries[name]:
            dispatch.append('  case 0x%08Xu: goto PRIDE_PC_%06X_M%dX%d;' % (pc | (m << 24) | (x << 25), pc, m, x))
        dispatch += ['  default: PrideSceneCompiledUnmapped(cpu,0,_resume_pc);', '  }']
        source = source.replace(anchor, anchor + '\n' + '\n'.join(dispatch))
        source += '\nRecompReturn %s(CpuState *cpu) { return %s_continue(cpu,0,0,0); }\n' % (name, name)
    return '\n'.join(declarations) + '\n' + source

"""Recover exact pre-edit bytes after a failed archive command; require bound hashes."""
import json
from pathlib import Path
import hashlib
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest

out=ROOT/'build/pride-hyena-probe103-baseline';out.mkdir()
bp=json.loads((ROOT/'build/pride-hyena-probe97/build-report.json').read_text())
component=json.loads((ROOT/'build/pride-hyena-probe97-component/report.json').read_text())
expected=bp['source_sha256']|component['source_sha256'];rows={}
for name in ['engine/runner/tlk_hyena_probe.c','engine/runner/tlk_hyena_probe.h','engine/tests/hyena_walking_probe_test.c','engine/cmake/final-frontend-patches/hyena-walking-probe.hunks','tools/pride_arena_history.py']:
    p=ROOT/name;data=p.read_bytes()
    if name.endswith('tlk_hyena_probe.c'):
        s=data.decode();start=s.index('static int source_known,previous_source;');end=s.index('void TlkHyenaWalkingProbe',start)
        s=s[:start]+s[end:];s=s.replace('sp<0x100 || sp>0x1fe6','sp<0x600 || sp>0x1fe6');data=s.encode()
    elif name.endswith('tlk_hyena_probe.h'):
        data=data.replace(b'void TlkHyenaProbePrepareSource(void);\nint TlkHyenaProbeProfileChanged(void);\n',b'')
    elif name.endswith('hyena_walking_probe_test.c'):
        s=data.decode().replace('case 15:cpu.S=0x80;','case 15:cpu.S=0x500;')
        s=s.replace('        cpu=setup(left,bank,339);memcpy(g_ram+0x2da,g_ram+cpu.S+1,10);cpu.S=0x2d9;call(&cpu,pc,1);\n','')
        start=s.index('    selected=0;TlkHyenaProbePrepareSource();');end=s.index('    printf(',start)
        data=(s[:start]+s[end:]).encode()
    elif name.endswith('hyena-walking-probe.hunks'):
        s=data.decode().replace('        TlkHyenaProbePrepareSource();\n','')
        data=s.split('\n@@ restart-after-hyena-walking-probe-source-change')[0].encode()
    sha=hashlib.sha256(data).hexdigest()
    if name!='tools/pride_arena_history.py':assert sha==expected[name],(name,sha,expected[name])
    q=out/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
    rows[name]=dict(sha256=sha,archive=q.relative_to(ROOT).as_posix())
(out/'report.json').write_text(json.dumps(dict(historical_sources=rows,recovery='Initial PowerShell archive command failed at Python parsing before any writes; exact inverse edits reconstructed original bytes and all four identities matched frozen97 proofs.'),indent=2)+'\n')
p=ROOT/'tools/pride_arena_history.py';s=p.read_text();anchor="    folders.append('pride-hyena-probe97-baseline')";assert s.count(anchor)==1
p.write_text(s.replace(anchor,anchor+"\n    folders.append('pride-hyena-probe103-baseline')"))
print('Recovered exact verified97 identities',len(rows),flush=True)

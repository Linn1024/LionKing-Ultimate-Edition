"""Reject damaged and semantically invalid ownership envelopes in the player."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_bounce_owner_history import bound
from verify_pride_audio_state import audio_offset


def main():
    public=ROOT/'build/pride-lizard-launch-work/player'
    base=ROOT/'build/pride-bounce-owner-work/player';bp=base/'build-report.json';bound(bp)
    state=base/'saves/bounce-aot-1399.state';original=state.read_bytes();at=audio_offset(original)
    assert original[at:at+8]==b'TLKSEM01'
    metadata=at+64+struct.unpack_from('<I',original,at+12)[0]
    out=base/'invalid-saves';out.mkdir();cases={};checks={};commands={}
    def sealed(raw):
        raw[at+32:at+64]=bytes(32)
        raw[at+32:at+64]=hashlib.sha256(raw[at:]).digest();return raw
    for name,offset,value in (
        ('envelope-version',at+8,2),('base-length',at+12,0xffffffff),
        ('metadata-length',at+16,799),('reserved',at+20,1),
        ('metadata-version',metadata+8,2),('metadata-size',metadata+12,796),
        ('impossible-token',metadata+24,struct.unpack_from('<I',original,metadata+16)[0]+1)):
        raw=bytearray(original);struct.pack_into('<I',raw,offset,value);cases[name]=sealed(raw)
    raw=bytearray(original);raw[-1]^=1;cases['checksum']=raw
    cases['truncated']=original[:-1];cases['trailing']=original+b'x'
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    clean['SDL_VIDEODRIVER']='dummy'
    for name,raw in cases.items():
        path=out/(name+'.state');path.write_bytes(raw)
        command=list(map(str,[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc',
            '--md-rom',ROOT/'Lion King, The (World).md','--config',public/'launch-audio/host.ini',
            '--resource-profile',public/'launch-audio/bounce.ini','--load',path,
            '--frames',1401,'--no-pace','--no-audio','--no-record']))
        commands[name]=command
        with (out/(name+'.log')).open('wb') as log:
            result=subprocess.run(command,cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=80)
        checks[name+'/rejected']=result.returncode==8
        checks[name+'/input_unchanged']=path.read_bytes()==raw
    assert state.read_bytes()==original
    sources=[Path(__file__),bp,state]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file()})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],len(checks),'damaged-save checks',flush=True)
    assert all(checks.values()),[k for k,v in checks.items() if not v]


if __name__=='__main__':main()

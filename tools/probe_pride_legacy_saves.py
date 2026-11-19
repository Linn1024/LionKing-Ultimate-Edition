"""Author genuine installed-player saves and inspect current loader behavior."""
import json
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment


def main():
    out=ROOT/'build/pride-legacy-save/probe';out.mkdir(parents=True)
    source=ROOT/'build/pride-tree-help2';build_path=source/'build-report.json';build=bound(build_path)
    native_path=source/'plain-native/build-report.json';native=bound(native_path)
    installed=ROOT/'dist/LionKing.exe';installed_sha=digest(installed)
    assert installed_sha==build['production_sha256']['dist/LionKing.exe']
    commands={};observations={}
    for name,choices in (('native',''),('md-media','display.viewport = md\ngraphics.sprites.simba.cub.palette = md\naudio.music.pride_lands = md\n')):
        folder=out/name;folder.mkdir();profile=folder/'resources.ini';profile.write_text('schema = 1\ngame = snes\n'+choices)
        config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n');state=folder/'installed.state'
        common=['--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md','--config',config,'--resource-profile',profile,'--no-audio','--no-record','--no-pace']
        cmd=[installed,*common,'--practice-level','0','--frames','1500','--save-at','1500',state]
        commands[name+'/author']=list(map(str,cmd))
        with (folder/'author.log').open('wb') as log:r=subprocess.run(commands[name+'/author'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        assert not r.returncode and state.exists(),(name,r.returncode)
        raw=state.read_bytes();assert raw[:8]==b'TLKSTAT1';version,field=struct.unpack_from('<II',raw,8);blob_len=struct.unpack_from('<Q',raw,24)[0]
        blob=raw[36:36+blob_len];markers=[(m.start(),struct.unpack_from('<I',blob,m.start()+4)[0]) for m in re.finditer(b'RBRS',blob) if m.start()+8<=len(blob)]
        observations[name]=dict(outer_version=version,saved_field=field,blob_len=blob_len,runtime_markers=markers,state_sha256=digest(state),loads={})
        for host,exe,identity in (('installed',installed,installed_sha),('native',source/'plain-native/native.exe',native['binary_sha256']),('mixed',source/'singlepass.exe',build['binary_sha256'])):
            assert digest(exe)==identity;case=folder/host;case.mkdir()
            cmd=[exe,*common,'--load',state,'--frames','1510'];commands[name+'/'+host]=list(map(str,cmd))
            with (case/'run.log').open('wb') as log:r=subprocess.run(commands[name+'/'+host],cwd=ROOT,env=environment(case),stdout=log,stderr=subprocess.STDOUT,timeout=180)
            text=(case/'run.log').read_text(errors='replace');observations[name]['loads'][host]=dict(exit=r.returncode,message=text.split('cannot load state ',1)[-1] if 'cannot load state ' in text else '')
            print(name,host,r.returncode,flush=True)
        assert digest(state)==observations[name]['state_sha256']
    paths=[Path(__file__),build_path,native_path,ROOT/'tools/verify_pride_live_error_ui.py']
    report=dict(result='OBSERVED',observations=observations,commands=commands,installed_binary_sha256=installed_sha,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},
                artifacts_sha256={str(p.relative_to(out)).replace('\\','/'):digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()

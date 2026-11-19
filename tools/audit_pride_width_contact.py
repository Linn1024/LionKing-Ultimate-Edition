"""Verify the live narrow-view contact and inspect actual Windows presentation."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT,read_rom
from build_pride_compiled_hooks import digest
from pride_actor_bounds_audit import bounds,overlap
from summarize_pride_practice import bound
from verify_windows import pixels


def main():
    base=ROOT/'build/pride-rng-player2';capture=base/'width-contact'
    cp=capture/'report.json';record=bound(cp);assert record['observer_full_frame_wram_neutral_every_field']
    md=read_rom('Lion King, The (World).md','e112d181189304b2d2900bdc0d6d615211d547a544121921878c199e412170f5')
    mapping_path=ROOT/'engine/generated/resources/pride_hitbox_map.h'
    mapping={int(a,16):int(b,16) for a,b in re.findall(r'\{0x([0-9a-f]+),0x([0-9a-f]+),[0-3]\}',mapping_path.read_text())}
    out=base/'width-contact-audit';out.mkdir();checks={};observations={};commands={}
    parents={320:base/'completion-reference-unpaused2/320',256:base/'completion-reference-unpaused256/256'}
    tape=base/'controller-unpaused2/route.polled.tape'
    paths=[Path(__file__),cp,mapping_path,tape,ROOT/'tools/pride_actor_bounds_audit.py',base/'build-report.json']
    clean={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_'))}
    for width,enemy in ((256,0xb613),(320,0xb693)):
        folder=out/str(width);folder.mkdir();config=folder/'host.ini';config.write_text('opengl = 0\nscale = 2\n')
        ram=(capture/str(width)/'wram-1402.bin').read_bytes();word=lambda at:struct.unpack_from('<H',ram,at)[0]
        actors=[];at=0xb213;previous=0
        while at:
            assert word(at)==previous and at not in actors
            actors.append(at);previous,at=at,word(at+2)
        assert enemy in actors
        bodies=[]
        for actor in (0xb213,enemy):
            draw=word(actor+12);pose=int.from_bytes(ram[draw+10:draw+13],'little')&0x3fffff
            flags=word(draw+8);external=mapping[pose]
            box=bounds(md,external,word(actor+8),word(actor+10),((flags&0x40)<<5)|((flags&0x80)<<5),True)
            bodies.append(dict(actor=actor,pose=pose,md_pose=external,xy=[word(actor+8),word(actor+10)],body=box))
        contact=word(0xb237)|(word(0xb239)<<16)
        hit=overlap(bodies[0]['body'],bodies[1]['body'])
        after=(capture/str(width)/'wram-1403.bin').read_bytes()
        checks[str(width)+'/contact_and_next_health']=((hit and contact==0x7eb613 and after[0x2004]==3) if width==256 else
                                                       (not hit and contact==0 and after[0x2004]==4))
        observations[str(width)]=dict(bodies=bodies,contact=contact,overlap=hit,camera=[word(0xb29b),word(0xb29d)])
        profile=parents[width]/'resources.ini';baseline=parents[width]/'aot/run.log';paths.extend([profile,baseline])
        cmd=[base/'player.exe','--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input-polled',tape,'--frames',1402,
             '--no-pace','--no-audio','--no-record','--hash-at',1402,'--dump-window',folder/'window.png']
        commands[str(width)]=list(map(str,cmd))
        with (folder/'run.log').open('wb') as log:
            result=subprocess.run(commands[str(width)],cwd=ROOT,env=clean,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        pattern=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
        expected=[r for r in re.findall(pattern,baseline.read_text()) if r[0]=='1402']
        checks[str(width)+'/actual_window_guest_exact']=result.returncode==0 and len(expected)==1 and re.findall(pattern,(folder/'run.log').read_text())==expected
        w,h,_=pixels(folder/'window.png');checks[str(width)+'/actual_window_dimensions']=(w,h)==(width*2,448)
    checks['player_body_equal']=observations['256']['bodies'][0]['body']==observations['320']['bodies'][0]['body']
    checks['inclusive_narrow_contact']=observations['256']['bodies'][0]['body'][0]==observations['256']['bodies'][1]['body'][2]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,observations=observations,commands=commands,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths},
        artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'},
        enemy_birth_pairing_proven=False,full_md_enemy_behavior_proven=False,
        full_first_level_fidelity_complete=False,public_player_enabled=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],[k for k,v in checks.items() if not v],flush=True)
    assert all(checks.values())


if __name__=='__main__':main()

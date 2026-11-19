"""Resume actual owned F1 saves across CPU modes with complete mixed audio."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from verify_pride_live_error_ui import environment,read_rows
from verify_pride_audio_state import wav_data
from verify_windows import hashes,pixels
from probe_pride_preparation_state import frame_records,glyph_records


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--case',choices=('native','md-media'),required=True);args=p.parse_args()
    base=ROOT/'build/pride-raster-state';author=base/'live/owned-ui-save'/args.case
    audit_path=base/'live/owned-ui-save-audit'/args.case/'report.json';audit=bound(audit_path);assert audit['result']=='PASS'
    author_path=author/'report.json';before=bound(author_path)
    assert all(v for k,v in before['checks'].items() if k!='whole_ui_free_record')
    source_path=base/'live'/args.case/'report.json';source=bound(source_path);assert source['result']=='PASS'
    build_path=base/'build-report.json';build=bound(build_path);binary=base/'live/runtime/practice-live.exe'
    assert digest(binary)==build['runs']['sdl']['binary_sha256']==audit['binary_sha256']
    state=author/'live/tlk_slot1.state';ordinary=base/'live'/args.case/'baseline/tlk_practice_restart.state'
    raw=state.read_bytes();saved=struct.unpack_from('<I',raw,20)[0];assert raw[:8]==b'PRHSAVE1'
    out=base/'verified/windows-owned'/args.case;out.mkdir(parents=True,exist_ok=True);assert not (out/'report.json').exists()
    profile=out/'resources.ini';profile.write_bytes((author/'resources.ini').read_bytes())
    tape=ROOT/'build/pride-repeated-route/oscillate/ordinary.tape';md=args.case=='md-media';commands={};folders=[]
    for name,mode,load in (('baseline','lle' if md else 'aot',ordinary),('resumed','aot' if md else 'lle',state)):
        folder=out/name;folder.mkdir();folders.append(folder);config=folder/'host.ini';config.write_text('opengl = 1\nscale = 2\n')
        cmd=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
             '--resource-profile',profile,'--config',config,'--input',tape,'--load',load,'--frames',3000,
             '--no-audio','--no-record','--no-pace','--dump-window',folder/'window.png','--dump-png',folder/'guest.png',
             '--wav',folder/'audio.wav','--wav-seconds',100,'--hash-at',','.join(map(str,range(1,3001)))]
        if mode=='lle':cmd+=['--lle']
        commands[name]=list(map(str,cmd));env=environment(folder)
        env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv');env['TLK_AUDIO_STEMS']=str(folder/'audio-stems.csv')
        with (folder/'run.log').open('wb') as log:
            r=subprocess.run(commands[name],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        assert r.returncode==0,(name,r.returncode)
    a,b=folders;width=320 if md else 256;entry,second=source['revival_begins']
    first=a/'restart-1';next_before=first/f'scene-{second}';next_after=b/f'scene-{second}'
    pat=r'frame=(\d+) frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)'
    rows=lambda folder:[(int(n),f,w) for n,f,w in re.findall(pat,(folder/'run.log').read_text())]
    checks=dict(endpoint_guest=hashes(a/'run.log')==hashes(b/'run.log'),
        all_native_fields=rows(b)==[r for r in rows(a) if r[0]>saved] and len(rows(b))==3000-saved,
        full_final_client=pixels(a/'window.png')==pixels(b/'window.png'),
        file_unchanged=state.read_bytes()==raw,
        remaining_scene=frame_records(b/'render-owned.rgb',width)=={age:data for age,data in frame_records(first/'render-owned.rgb',width).items() if entry+age>saved},
        remaining_glyphs=glyph_records(b)==[(f,data) for f,data in glyph_records(first) if f>saved])
    for name in ('render-owned.rgb','render-fields.csv','prepared-fonts.bin','prepared-objects.csv','ground-entry.bin','ground-return.bin','scenery-evidence.json'):
        checks['second/'+name]=digest(next_before/name)==digest(next_after/name)
    for name in ('owner-events.csv','owner-fields.csv','restore-events.csv','restore-fields.csv','post-ready.csv','spawn-policy.csv','bank-clock.csv'):
        checks[name]=read_rows(b/name)==[r for r in read_rows(a/name) if int(r['field'])>saved]
    boundary=[r for r in read_rows(a/'practice-fields.csv') if int(r['field'])==saved+1];assert len(boundary)==1
    cut=int(boundary[0]['wav_frames_before_audio'])*4
    checks['complete_pcm_tail']=wav_data(a/'audio.wav')[cut:]==wav_data(b/'audio.wav')
    stems=lambda folder:read_rows(folder/'audio-stems.csv')
    checks['remaining_audio_stems']=stems(b)==[r for r in stems(a) if int(r['frame'])>saved]
    if md:checks['md_stem_audible']=any(int(r['md_peak'])>0 for r in stems(b))
    paths=(Path(__file__),audit_path,author_path,source_path,build_path,state,ordinary,tape,ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_pride_live_error_ui.py',ROOT/'tools/verify_pride_audio_state.py')
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,case=args.case,saved_field=saved,
        native_fields_compared=3000-saved,complete_client_pixels=pixels(b/'window.png')[0]*pixels(b/'window.png')[1],
        binary_sha256=digest(binary),dll_sha256=audit['dll_sha256'],source_sha256={str(q.relative_to(ROOT)).replace('\\','/'):digest(q) for q in paths},commands=commands,
        artifacts_sha256={str(q.relative_to(out)).replace('\\','/'):digest(q) for q in out.rglob('*') if q.is_file() and q.name!='report.json'},
        public_player_enabled=False,full_first_level_fidelity_complete=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(args.case,report['result'],[n for n,v in checks.items() if not v],flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

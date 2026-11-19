"""Audit live rewinds with matched input epochs and independent full toast composition."""
import json
import os
from pathlib import Path
import re
import struct
import subprocess

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_handoff_state import BASE,rows
from probe_pride_preparation_state import frame_records,glyph_records
from verify_windows import hashes,pixels
from verify_pride_audio_state import wav_data

CASES=(('snes-default-256-native-0-aot-lle',2080),
       ('md-default-320-all-274-lle-aot',2083),
       ('md-default-320-all-300-lle-aot',2082),
       ('md-polled-320-native-301-aot-lle',2334),
       ('snes-checkpoint-256-native-346-lle-aot',4780))


def toast_client(reference,guest):
    width,height,base=pixels(reference);gw,gh,native=pixels(guest)
    assert (gw,gh)==(256,224) and height==448 and width in (512,640)
    font=(ROOT/'engine/runner/tlk_font8x8.h').read_text()
    glyphs=[[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',row)]
            for row in re.findall(r'\{([^{}]+)\}',font)]
    assert len(glyphs)==95 and all(len(glyph)==8 for glyph in glyphs)
    text='Loaded state';extra=(width//2-256)//2
    for y in range(4,20):
        for x in range(4,4+len(text)*8+8):
            p=native[y*256+x];o=tuple(c*25//255 for c in p)
            if 8<=y<16 and 8<=x<8+len(text)*8:
                char=text[(x-8)//8]
                if glyphs[ord(char)-32][y-8]&(1<<((x-8)%8)):o=(255,255,255)
            # ComposeWide copies overlay pixels only where the native overlay
            # differs from the native PPU. Its base may use different MD art.
            if o!=p:
                for dy in (0,1):
                    for dx in (0,1):base[(y*2+dy)*width+(extra+x)*2+dx]=o
    return width,height,base


def main():
    build_path=BASE/'build-report.json';build=json.loads(build_path.read_text());results={};sources={}
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    binary=BASE/'handoff-state-sdl.exe';assert digest(binary)==build['runs']['sdl']['binary_sha256']
    for case,load_at in CASES:
        reference=BASE/'windows'/case;r=json.loads((reference/'report.json').read_text());assert r['result']=='PASS'
        for name,sha in r['source_sha256'].items():assert digest(ROOT/name)==sha,name
        out=BASE/'live-rewind'/case;out.mkdir(parents=True,exist_ok=True)
        tape=None
        if case.startswith('md-polled-'):
            # Live loads retain the host replay cursor. Preserve the genuine
            # prefix, then hold Right across both epochs instead of feeding
            # different future words from the older changing recording.
            ref=ROOT/'build/pride-actor-handoff/active/md-polled-320-native-aot-owned'
            cut=sum(line.split()[1]=='0' for line in (ref/'route.ram').read_text().splitlines() if int(line.split()[0])<=r['save_at'])
            original=Path(r['commands']['baseline'][r['commands']['baseline'].index('--input-polled')+1])
            tape=out/'right-tail.polled.tape';tape.write_bytes(original.read_bytes()[:cut*2]+struct.pack('<H',256)*2000)
            sources[str(original.relative_to(ROOT)).replace('\\','/')]=digest(original)
            sources[str((ref/'route.ram').relative_to(ROOT)).replace('\\','/')]=digest(ref/'route.ram')
        runs={}
        for epoch in ('baseline','rewind'):
            folder=out/epoch;folder.mkdir(exist_ok=True);state=folder/'rewind.private-state'
            command=list(r['commands']['baseline']);command[command.index('--save-at')+2]=str(state)
            if epoch=='rewind':command+=['--load-at',str(load_at),str(state)]
            if tape:command[command.index('--input-polled')+1]=str(tape)
            for flag,file in (('--dump-window','window.png'),('--wav','audio.wav')):command[command.index(flag)+1]=str(folder/file)
            command+=['--dump-png',str(folder/'guest.png')]
            env=os.environ.copy()
            for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
            for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                        'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
            env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
            with (folder/'run.log').open('wb') as log:run=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
            assert run.returncode==0,(case,epoch,run.returncode)
            runs[epoch]=dict(exit_code=run.returncode,guest=hashes(folder/'run.log'),commands=command,
                artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
        a,b=out/'baseline',out/'rewind';checks={}
        checks['guest']=runs['baseline']['guest']==runs['rewind']['guest'] and len(runs['baseline']['guest'])==2
        checks['guest_image']=pixels(a/'guest.png')==pixels(b/'guest.png')
        checks['whole_client_with_toast']=pixels(b/'window.png')==toast_client(a/'window.png',b/'guest.png')
        checks['scene_records']=frame_records(a/'render-owned.rgb',r['width'])==frame_records(b/'render-owned.rgb',r['width'])
        actual,expected=wav_data(b/'audio.wav'),wav_data(a/'audio.wav')
        samples=lambda field:field*48000*357366//21477272*4
        prefix=samples(load_at);tail=expected[samples(r['save_at']):]
        checks['pcm_prefix']=actual[:prefix]==expected[:prefix];checks['pcm_tail']=actual[prefix:]==tail
        for name in ('owner-fields.csv','restore-fields.csv','post-ready.csv','prepared-objects.csv'):
            before=rows(a/name);wanted=[row for row in before if int(row['field'])<=load_at]+[row for row in before if int(row['field'])>r['save_at']]
            checks[name]=rows(b/name)==wanted
        glyphs=glyph_records(a)
        checks['glyphs']=glyph_records(b)==[(field,data) for field,data in glyphs if field<=load_at]+[(field,data) for field,data in glyphs if field>r['save_at']]
        before=rows(a/'render-fields.csv');expected_rows=[row for row in before if int(row['field'])<=load_at]+[row for row in before if int(row['field'])>r['save_at']]
        observed=rows(b/'render-fields.csv');assert len(expected_rows)==len(observed)
        differences=[dict(field=x['field'],values={k:[y[k],x[k]] for k in x if x[k]!=y[k]}) for x,y in zip(observed,expected_rows) if x!=y]
        top={p.name:digest(p) for p in out.iterdir() if p.is_file()}
        results[case]=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,load_at=load_at,save_at=r['save_at'],
            native_diagnostic_differences=differences,runs=runs,top_artifacts_sha256=top)
        sources[str((reference/'report.json').relative_to(ROOT)).replace('\\','/')]=digest(reference/'report.json')
        print(case,results[case]['result'],checks,'native diagnostic differences',len(differences),flush=True)
    for p in (Path(__file__),build_path,ROOT/'tools/probe_pride_preparation_state.py',ROOT/'tools/verify_windows.py',ROOT/'tools/verify_pride_audio_state.py',ROOT/'engine/runner/sdl_main.c',ROOT/'engine/runner/tlk_font8x8.h'):
        sources[str(p.relative_to(ROOT)).replace('\\','/')]=digest(p)
    report=dict(result='PASS' if all(r['result']=='PASS' for r in results.values()) else 'INCOMPLETE',cases=results,
        source_sha256=sources,binary_sha256=digest(binary),failed_load_rollback_verified=False,
        input_source_switching_verified=False,full_first_level_fidelity_complete=False)
    (BASE/'live-rewind.json').write_text(json.dumps(report,indent=2)+'\n')
    if report['result']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()

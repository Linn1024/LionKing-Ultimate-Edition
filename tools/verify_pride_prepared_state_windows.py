"""Audit prepared new-process first frames, complete presentation and native PCM.

Each load keeps its saved viewport/artwork profile. Cross-profile and general
lifecycle behavior remain separate requirements.
"""
import array
import json
import os
from pathlib import Path
import re
import subprocess
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from probe_pride_prepared_state import frame_records,glyph_records,rows
from verify_windows import hashes,pixels


def pcm(path):
    with wave.open(str(path),'rb') as wav:
        assert wav.getnchannels()==2 and wav.getframerate()==48000
        return wav.getnframes(),wav.readframes(wav.getnframes())


def main():
    base=ROOT/'build/pride-prepared-state';out=base/'windows';out.mkdir(exist_ok=True)
    binary=base/'prepared-state-sdl.exe';identity=digest(binary);build_path=base/'build-report.json'
    build=json.loads(build_path.read_text());assert identity==build['runs']['sdl']['binary_sha256']
    for name,sha in build['source_sha256'].items():assert digest(ROOT/name)==sha,name
    sources={str(Path(__file__).relative_to(ROOT)).replace('\\','/'):digest(Path(__file__)),
             str((ROOT/'tools/probe_pride_prepared_state.py').relative_to(ROOT)).replace('\\','/'):digest(ROOT/'tools/probe_pride_prepared_state.py'),
             str(build_path.relative_to(ROOT)).replace('\\','/'):digest(build_path)}
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 2\n');results={}
    for width,graphics in ((256,'native'),(320,'all')):
        for save_mode,load_mode in (('aot','lle'),('lle','aot')):
            case=f'{width}-{graphics}-{save_mode}-{load_mode}';parent=out/case;parent.mkdir(exist_ok=True)
            state=parent/'checkpoint.private-state';profile=parent/'resources.ini'
            settings='schema = 1\ngame = snes\ndisplay.viewport = '+('md' if width==320 else 'snes')+'\n'
            if graphics=='all':settings+='graphics.scenery = md\ngraphics.sprites.simba.cub = md\ngraphics.hud = md\ngraphics.sprites.enemies.hyenas = md\ngraphics.sprites.enemies.other = md\ngraphics.sprites.pickups = md\ngraphics.sprites.leaves = md\ngraphics.sprites.effects.defeat_puff = md\n'
            profile.write_text(settings+'graphics.sprites.checkpoints.frames = md\ngraphics.sprites.checkpoints.palette = md\n')
            runs={}
            for part in ('baseline','resumed','first'):
                folder=parent/part;folder.mkdir(exist_ok=True);env=os.environ.copy()
                for key in ('TLK_NATIVE_BANK_PROBE','TLK_SCENE_PREPARE_PROBE','TLK_SCENE_OWNER_PROBE','TLK_SCENE_RESTORE_PROBE','TLK_SCENE_RENDER_PROBE'):env[key]=str(folder)
                for key in ('TLK_NATIVE_BANK_APPLY','TLK_SCENE_PREPARE_APPLY','TLK_SCENE_OWNER_ENABLE',
                            'TLK_SCENE_RESTORE_ENABLE','TLK_SCENE_RESTORE_CANONICAL','TLK_SCENE_RESTORE_ROAR_ZERO','TLK_SCENE_RENDER_ENABLE'):env[key]='1'
                env['TLK_SCENE_OWNER_MD_ROM']=str(ROOT/'Lion King, The (World).md');env.pop('TLK_NATIVE_BANK_RECORD',None)
                inputs=ROOT/'build/pride-health-death-native/neutral-tail.polled.tape' if part=='baseline' else base/'neutral.polled.tape'
                end=4704 if part=='first' else 5400
                command=[binary,'--rom',ROOT/'Lion King, The (USA).sfc','--md-rom',ROOT/'Lion King, The (World).md',
                    '--config',config,'--resource-profile',profile,'--frames',end,'--no-pace','--no-audio','--no-record',
                    '--input-polled',inputs,'--dump-window',folder/'window.png','--wav',folder/'audio.wav','--wav-seconds','100']
                if (save_mode if part=='baseline' else load_mode)=='lle':command.append('--lle')
                if part=='baseline':command+=['--save-at','4703',state,'--hash-at','4704']
                else:command+=['--load',state]
                with (folder/'run.log').open('wb') as log:
                    result=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=240)
                runs[part]=dict(exit_code=result.returncode,guest=hashes(folder/'run.log'),
                    artifacts_sha256={p.name:digest(p) for p in folder.iterdir() if p.is_file()})
                assert result.returncode==0,(case,part,result.returncode)
            a=parent/'baseline';b=parent/'resumed';first=parent/'first'
            assert runs['baseline']['guest']==runs['resumed']['guest']
            assert pixels(a/'window.png')==pixels(b/'window.png')
            before=frame_records(a/'render-owned.rgb',width);after=frame_records(b/'render-owned.rgb',width)
            assert after=={age:record for age,record in before.items() if age>273}
            assert glyph_records(b)==[(field,raw) for field,raw in glyph_records(a) if field>4703]
            for name in ('render-fields.csv','prepared-objects.csv','owner-events.csv','restore-events.csv','owner-fields.csv','restore-fields.csv'):
                assert rows(b/name)==[r for r in rows(a/name) if int(r['field'])>4703],(case,name)
            expected=before[274];colors=array.array('I');colors.frombytes(expected[-width*224*4:])
            w,h,client=pixels(first/'window.png');assert (w,h)==(width*2,448)
            for y in range(h):
                for x in range(w):
                    c=colors[(y//2)*width+x//2];assert client[y*w+x]==(c>>16&255,c>>8&255,c&255)
            tag=re.search(r'^frame=4704 frame_sha256=([0-9a-f]+) wram_sha256=([0-9a-f]+)',(a/'run.log').read_text(),re.M)
            assert tag and runs['first']['guest']==dict(zip(('frame_sha256','wram_sha256'),tag.groups()))
            full_n,full=pcm(a/'audio.wav');tail_n,tail=pcm(b/'audio.wav')
            assert full_n==5400*48000*357366//21477272 and tail_n==697*48000*357366//21477272
            assert full[-len(tail):]==tail
            results[case]=dict(runs=runs,state_sha256=digest(state),first_client_pixels=w*h,
                final_client_pixels=w*h,remaining_render_and_glyph_traces_exact=True,
                continuation_pcm_bytes=len(tail),continuation_pcm_exact=True)
            print(case+' actual first/final windows, guest, owned traces, glyphs and PCM exact PASS',flush=True)
    for name,sha in sources.items():assert digest(ROOT/name)==sha,name
    assert digest(binary)==identity
    (out/'report.json').write_text(json.dumps(dict(result='PASS',scope=__doc__,runs=results,
        source_sha256=sources,binary_sha256=identity,cross_graphics_load_verified=False,
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()

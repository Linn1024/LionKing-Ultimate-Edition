"""Check taunt first-loaded artwork and entry counts across new-process saves.

This checks presentation and future cue dispatch. Exact playing-audio continuation
is checked separately by verify_pride_audio_state.py and its live F1/F5 test.
"""
import csv
import json
import os
import re
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels


def main():
    out=ROOT/'build/pride-hyena-taunt-state';out.mkdir(parents=True,exist_ok=True)
    source=ROOT/'build/pride-hyena-taunt'
    ready=source/'ready.state';tape=source/'after.polled.tape'
    profile=out/'resources.ini';profile.write_text('schema = 1\ngame = snes\ngraphics.sprites.enemies.hyenas = md\naudio.effects.world.hyena_taunt = md\n')
    config=out/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    base=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
          '--md-rom',str(ROOT/'Lion King, The (World).md'),'--resource-profile',str(profile),
          '--config',str(config),'--no-pace','--no-audio','--no-record']
    def run(name,frame,state,inputs,save=None,capture=True):
        env=os.environ.copy();env['TLK_HYENA_TAUNT_TRACE']=str(out/(name+'-entries.csv'))
        cmd=[*base,'--load',str(state),'--frames',str(frame),'--input-polled',str(inputs)]
        if save:cmd+=['--save-at',str(frame),str(save)]
        if capture:cmd+=['--dump-window',str(out/(name+'.png')),'--dump-scene',str(out/(name+'.json'))]
        log=out/(name+'.log')
        with log.open('wb') as stream:subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=180)
        return hashes(log)
    reference=run('full-reference',4350,ready,tape,capture=False)
    results=[]
    for frame in (4025,4027,4044,4058):
        name=str(frame);state=out/(name+'.state')
        run(name+'-save',frame,ready,tape,state,False)
        used=int(re.search(r'tape_words_used=(\d+)',(out/(name+'-save.log')).read_text()).group(1))
        suffix=out/(name+'.polled.tape');suffix.write_bytes(tape.read_bytes()[used*2:])
        expected=run(name+'-reference',frame+1,ready,tape)
        resumed=run(name+'-loaded',frame+1,state,suffix)
        assert expected==resumed,(frame,'First loaded guest state')
        assert json.loads((out/(name+'-reference.json')).read_text())==json.loads((out/(name+'-loaded.json')).read_text()),(frame,'Scene history')
        assert pixels(out/(name+'-reference.png'))==pixels(out/(name+'-loaded.png')),(frame,'First loaded window')
        assert run(name+'-continued',4350,state,suffix,capture=False)==reference,(frame,'Continuation')
        entries=list(csv.DictReader((out/(name+'-continued-entries.csv')).open()))
        assert len(entries)==(2 if frame==4025 else 1),(frame,'Duplicate/missed initialized entry',entries)
        assert all(row['emitted']=='1' for row in entries)
        results.append(frame);print(frame,'exact first field, continuation and future-entry count PASS',flush=True)
    (out/'report.json').write_text(json.dumps({'result':'PASS','scope':__doc__,
        'identical_first_fields':results,'no_duplicate_initialized_entry':True,
        'audio_continuation_checked_separately':True},indent=2)+'\n')


if __name__=='__main__':main()

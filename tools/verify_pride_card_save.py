"""Verify complete-cache saves on the native post-Pride level card."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_boss_save.py')
source=original_verifier.read_text().replace("base=ROOT/'build/pride-rng-player4'", "base=ROOT/'build/pride-rng-player5'")
source=source.replace("previous=ROOT/'build/pride-rng-player3'", "previous=ROOT/'build/pride-rng-player4'")
source=source.replace("out=base/'boss-saves'", "out=base/'card-saves'")
source=source.replace("tape=previous/'width-arena-input/route.polled.tape'", "tape=previous/'width-fight1/best.polled.tape'")
source=source.replace("previous/'width-arena-input/report.json'", "previous/'width-fight1/report.json'")
source=source.replace("'--frames',3000", "'--frames',4500")
source=source.replace('range(2801 if load else 1,3001)', 'range(3001 if load else 1,4501)')
source=source.replace("'--save-at',2800", "'--save-at',3000")
source=source.replace('len(rows(new))==3000', 'len(rows(new))==4500')
source=source.replace("int.from_bytes(record[20:24],'little')==2800", "int.from_bytes(record[20:24],'little')==3000")
source=source.replace('int(r[0])>2800', 'int(r[0])>3000').replace('len(rows(resumed))==200', 'len(rows(resumed))==1500')
source=source.replace('private_boss_envelope', 'private_card_envelope')
old="        checks[mode+'/wrong_source_rejected']=run('wrong-'+mode,base/'player.exe',mode,load=state,bad=True)==8 and 'State scene-random source differs' in (out/('wrong-'+mode)/'run.log').read_text()"
assert old in source
source=source.replace(old,"""        checks[mode+'/inactive_rng_choice_loads']=run('wrong-'+mode,base/'player.exe',mode,load=state,bad=True)==0
        changed=out/('wrong-'+mode)
        checks[mode+'/inactive_rng_every_field']=len(rows(changed))==1500 and rows(changed)==expected
        pcm=wav_data(changed/'audio.wav')
        checks[mode+'/inactive_rng_whole_pcm']=bool(pcm) and pcm==wav_data(new/'audio.wav')[-len(pcm):]
        checks[mode+'/inactive_rng_whole_client']=pixels(changed/'window.png')==pixels(new/'window.png')
        checks[mode+'/saved_card_scene_flag']=not (int.from_bytes(record[288:292],'little')&0x80000000)
        checks[mode+'/actual_card_boundary']=any(row[0]=='3000' and row[2]==digest(card_snapshot) for row in rows(new))""")
old="checks[mode+'/actual_boss_scene']=scene['level']==0 and scene['latched_gameplay']['descriptor']==0x80d"
assert old in source
source=source.replace(old,"checks[mode+'/next_main_level']=scene['level']==1")
source=source.replace('compared_fields=6800','compared_fields=18000')
source=source.replace('paths=[Path(__file__),bp,', 'paths=[Path(__file__),original_verifier,card_snapshot,bp,')
card_snapshot=Path(__file__).resolve().parents[1]/'build/pride-rng-player4/width-fight1/d5-p0-wait/wram-3000.bin'
assert int.from_bytes(card_snapshot.read_bytes()[0xdf:0xe2],'little')==0xc005ab
exec(compile(source,str(original_verifier),'exec'))

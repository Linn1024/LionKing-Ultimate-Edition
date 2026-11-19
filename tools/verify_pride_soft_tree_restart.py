"""Compare actual fallback-tree source restarts with cold selected-source boots."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_soft_tree.py')
source=original_verifier.read_text()
source=source.replace("choices=('native','md')","choices=('music','start')")
source=source.replace("out=base/'windows'/args.case","out=base/'restarts'/args.case")
source=source.replace("    initial=PRESET if args.case=='md' else 'schema = 1\\ngame = snes\\n'", """    source_id='audio.music.pride_lands' if args.case=='music' else 'gameplay.levels.pride_lands.start'
    initial='schema = 1\\ngame = snes\\n'""")
source=source.replace('profile.write_text(initial)', "profile.write_text(initial+(source_id+' = md\\n' if name=='control' else ''))")
source=source.replace("if args.case=='md':cmd+=['--lle']", "if args.case=='music':cmd+=['--lle']")
source=source.replace("commands[name]=list(map(str,cmd));env=environment(folder);", "commands[name]=list(map(str,cmd));env=environment(folder);env['TLK_START_TRACE']=str(folder/'start.csv');env['TLK_MD_SOUND_COMMANDS']=str(folder/'md-commands.csv');env['TLK_AUDIO_STEMS']=str(folder/'audio-stems.csv');")
begin=source.index("                baseline=profile.read_bytes()")
end=source.index("                proc.wait(timeout=180);",begin)
source=source[:begin]+'''                baseline=profile.read_bytes();row=setchoice(source_id,2)
                checks['draft_not_published']=profile.read_bytes()==baseline and row['dirty']==1 and row['field']==1500
                snap('pending-source')
                key(0x71)
                checks['requested_source_persisted']=source_id+' = md' in profile.read_text()
                # PrStartLevel closes the menu after loading the genuine startup boot.
                row=wait(lambda r:not r['menu'] and r['field']>=1450,120)
                checks['restart_closed_editor']=row['about']==0 and row['dirty']==0
''' + source[end:]
begin=source.index("    checks['all_guest_fields']")
end=source.index("    trace_rows=",begin)
source=source[:begin]+'''    from verify_pride_live_error_ui import read_rows
    cold,live=rows(a),rows(b)
    checks['all_restarted_guest_fields']=live[-1800:]==cold[-1800:] and len(live)==3301 and len(cold)==1801
    checks['final_guest_picture']=pixels(a/'guest.png')==pixels(b/'guest.png')
    fields_a=read_rows(a/'practice-fields.csv');fields_b=read_rows(b/'practice-fields.csv')
    cut_a=int(fields_a[-1800]['wav_frames_before_audio'])*4;cut_b=int(fields_b[-1800]['wav_frames_before_audio'])*4
    checks['complete_restarted_pcm']=wav_data(a/'audio.wav')[cut_a:]==wav_data(b/'audio.wav')[cut_b:]
    loads=read_rows(b/'live-load.csv')
    checks['genuine_boot_load']=len(loads)==2 and all(r['success']=='1' and r['loaded_field']=='0' for r in loads) and loads[-1]['attempt_field']=='1500'
    # The same native guest hashes do not establish the selected MD sound path.
    checks['all_restarted_audio_stems']=read_rows(a/'audio-stems.csv')[-1800:]==read_rows(b/'audio-stems.csv')[-1800:]
    if args.case=='start':
        starts=read_rows(b/'start.csv');positions=[int(r['selected']) for r in starts if r['pc'] in ('c0867d','c08689')]
        checks['original_md_start_constructor']=positions==[64,1248,65,1255]
    else:
        commands_md=read_rows(b/'md-commands.csv')
        checks['md_music_commands']=bool(commands_md) and any('137' in r.values() for r in commands_md)
''' + source[end:]
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))

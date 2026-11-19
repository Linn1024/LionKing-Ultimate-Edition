"""Retain the failed whole-record hypothesis and capture its original writer."""
from pathlib import Path

original=Path(__file__).with_name('capture_pride_fatal_entry.py')
source=original.read_text()
changes={
    "ROOT/'build/pride-fatal-entry'":"ROOT/'build/pride-fatal-entry-flags'",
    "ROOT/'tools/md_fatal_entry_trace.c'":"ROOT/'tools/md_fatal_entry_flags_trace.c'",
    "trace.md_fatal_entry_init.argtypes=[C.c_void_p,C.c_char_p]":
        "trace.md_fatal_entry_flags_init.argtypes=[C.c_void_p,C.c_char_p,C.c_char_p]",
    "trace.md_fatal_entry_init(game.core._handle,str(folder/'events.csv').encode())":
        "trace.md_fatal_entry_flags_init(game.core._handle,str(folder/'events.csv').encode(),str(folder/'writes.csv').encode())",
    'trace.md_fatal_entry_close()':'trace.md_fatal_entry_flags_close()',
    "checks[name+'/same_field_dispatch_retains_actor_state']=selected[2]['actor_words']==selected[3]['actor_words']":
        """before=[int(selected[2]['actor_words'][at:at+4],16) for at in range(0,256,4)]
        after=[int(selected[3]['actor_words'][at:at+4],16) for at in range(0,256,4)]
        differences=[dict(offset=i*2,before=a,after=b) for i,(a,b) in enumerate(zip(before,after)) if a!=b]
        writes=list(csv.DictReader((folder/'writes.csv').open()))
        flag_writes=[r for r in writes if int(r['field'])==death and int(r['address'],16)==0xff9411 and int(r['value'],16)==4]
        checks[name+'/only_original_post_actor_flag_differs']=differences==[dict(offset=0x42,before=0x400,after=0x404)]
        checks[name+'/original_post_actor_flag_write_observed']=len(flag_writes)==1
        checks[name+'/motion_timer_retained_until_same_field_dispatch']=all(selected[2][k]==selected[3][k] for k in ('action','x','y','vx','vy','timer'))""",
    "cases[name]=dict(prefix=prefix,death=death,events=selected,prefix_wram_controls=prefix_checks)":
        "cases[name]=dict(prefix=prefix,death=death,events=selected,prefix_wram_controls=prefix_checks,actor_word_differences=differences,post_actor_flag_writes=flag_writes)",
    'paths=[Path(__file__),source,tape,':
        "paths=[Path(__file__),original,ROOT/'tools/md_fatal_entry_trace.c',source,tape,",
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))

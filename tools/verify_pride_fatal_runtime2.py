"""Observe current death timing rather than assuming an older absolute field."""
from pathlib import Path

original=Path(__file__).with_name('verify_pride_fatal_runtime.py')
source=original.read_text()
changes={
    "ROOT/'build/pride-fatal-runtime'":"ROOT/'build/pride-fatal-runtime2'",
    "'--frames',4430,'--hash-at','4428,4429,4430'":
        "'--frames',5000,'--hash-at',','.join(map(str,range(4428,5001)))",
    "checks[label+'/three_guest_samples']=len(rows)==3":
        "checks[label+'/all_573_guest_samples']=len(rows)==573",
    "begin[0]['state']=='c35a82' and begin[0]['health']=='0' and begin[0]['field']=='4429'":
        "bool(begin) and begin[0]['state']=='c35a82' and begin[0]['health']=='0' and 4428<int(begin[0]['field'])<=5000",
    'paths=[Path(__file__),exe,tape,':'paths=[Path(__file__),original,exe,tape,',
    'sampled_fields=[4428,4429,4430]':'sampled_fields=dict(start=4428,end=5000,every=1)',
}
for before,after in changes.items():
    assert source.count(before)==1,before
    source=source.replace(before,after)
exec(compile(source,str(original),'exec'))

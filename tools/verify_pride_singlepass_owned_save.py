"""Check actual F1 with visible practice overlays against an explicit owned save."""
from pathlib import Path
import re

original_verifier=Path(__file__).with_name('verify_pride_overlay_owned_save.py')
source=original_verifier.read_text()
begin=source.index("    base=ROOT/'build/pride-practice-live';")
end=source.index('    def command(name):',begin)
initial='''    base=ROOT/'build/pride-singlepass';author=base/('md' if args.case=='md-media' else 'native')
    author_path=author/'report.json';prior=bound(author_path);assert prior['result']=='PASS' and all(prior['checks'].values())
    build_path=base/'build-report.json';build=bound(build_path)
    binary=base/'singlepass.exe';dll=base/'genesis_plus_gx_libretro.dll'
    assert digest(binary)==prior['binary_sha256']==build['binary_sha256']
    out=base/'owned-ui-save'/args.case;out.mkdir(parents=True);assert not (out/'report.json').exists()
    cold=author/('cold-lle' if args.case=='md-media' else 'cold-aot')
    state=cold/'tlk_practice_restart.state';profile=out/'resources.ini';profile.write_bytes((author/'resources.ini').read_bytes())
    begins=[r for r in read_rows(cold/'owner-events.csv') if r['event']=='begin'];assert len(begins)>=2
    commands={};target=int(begins[0]['field'])+225
'''
source=source[:begin]+initial+source[end:]
helper='''def singlepass_environment(folder):
    result=environment(folder);result['TLK_SINGLEPASS_LOG']=str(folder/'presents.csv');return result


'''
source=source.replace('def main():',helper+'def main():').replace('env=environment(live)','env=singlepass_environment(live)').replace('env=environment(control)','env=singlepass_environment(control)')
extra='''    for folder in (live,control):
        records=read_rows(folder/'presents.csv')
        checks[folder.name+'/one_overlay_pass']=bool(records) and all(r['toast_calls']=='1' for r in records)
        for record in folder.rglob('*.rgb'):
            subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(record)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
'''
source=source.replace('    paths=(Path(__file__),',extra+'    paths=(Path(__file__),original_verifier,build_path,')
exec(compile(source,str(original_verifier),'exec'))

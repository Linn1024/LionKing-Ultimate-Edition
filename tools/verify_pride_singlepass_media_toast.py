"""Check real F5 notifications with independently selected MD audio and graphics."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_overlay.py')
source=original_verifier.read_text().replace("base = ROOT/'build/pride-overlay'","base = ROOT/'build/pride-singlepass'").replace("out = base/'windows'","out = base/'audio-windows'").replace("binary = base/'overlay-sdl.exe'","binary = base/'singlepass.exe'")
source=source.replace("build['runs']['sdl']['binary_sha256']","build['binary_sha256']")
source=source.replace("profile.write_bytes((old/'resources.ini').read_bytes())","profile.write_bytes((ROOT/'build/pride-source-live/seeded/resources.ini').read_bytes());assert md")
helper='''def singlepass_environment(folder):
    result=environment(folder)
    result.update(TLK_SINGLEPASS_LOG=str(folder/'presents.csv'),TLK_AUDIO_STEMS=str(folder/'stems.csv'),TLK_MD_SOUND_COMMANDS=str(folder/'md-commands.csv'))
    return result


'''
source=source.replace('env=environment(folder)','env=singlepass_environment(folder)').replace('env=environment(candidate)','env=singlepass_environment(candidate)').replace('def main():',helper+'def main():')
extra='''    for folder in (author,control,candidate):
        records=read_rows(folder/'presents.csv')
        checks[folder.name+'/one_overlay_pass']=bool(records) and all(int(r['toast_calls'])==1 for r in records)
        checks[folder.name+'/audible_md']=any(int(r['md_peak'])>0 for r in read_rows(folder/'stems.csv'))
        for record in folder.rglob('*.rgb'):
            subprocess.run(['compact.exe','/C','/EXE:LZX','/F','/A',str(record)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True,timeout=60)
'''
source=source.replace('    paths=(Path(__file__),',extra+"    paths=(Path(__file__),original_verifier,ROOT/'build/pride-source-live/seeded/resources.ini',")
exec(compile(source,str(original_verifier),'exec'))

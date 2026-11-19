"""Verify one overlay pass through complete mixed-player reset replays."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_machine_player.py')
source=original_verifier.read_text().replace("base=ROOT/'build/pride-machine-player'","base=ROOT/'build/pride-singlepass'").replace("binary=base/'machine.exe'","binary=base/'singlepass.exe'")
source=source.replace("stems=read_rows(folder/'stems.csv');","stems=[r for r in read_rows(folder/'stems.csv') if r['frame'].isdigit()];")
source=source.replace('env=environment(folder);','env=environment(folder);env["TLK_SINGLEPASS_LOG"]=str(folder/"presents.csv");')
extra='''    present_calls=0
    for name in commands:
        records=read_rows(out/name/'presents.csv');present_calls+=len(records)
        checks[name+'/one_overlay_pass']=bool(records) and all(int(r['toast_calls'])==1 for r in records)
    for mode in ('aot','lle'):
        prior=ROOT/'build/pride-machine-player4'/args.case/('cold-'+mode)
        checks['cold-'+mode+'/prior_whole_client']=pixels(controls[mode]/'window.png')==pixels(prior/'window.png')
        checks['cold-'+mode+'/prior_all_fields']=rows(controls[mode])==rows(prior)
        checks['cold-'+mode+'/prior_pcm']=wav_data(controls[mode]/'audio.wav')==wav_data(prior/'audio.wav')
'''
source=source.replace('    paths=[Path(__file__),',extra+'    paths=[Path(__file__),original_verifier,')
source=source.replace("actual_user_reset_control_verified=False,", "single_overlay_pass_presentations=present_calls,actual_user_reset_control_verified=False,")
exec(compile(source,str(original_verifier),'exec'))

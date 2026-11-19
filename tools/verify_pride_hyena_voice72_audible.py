"""Qualify retained fight captures with the actual host sample timeline.

The first fight verifier incorrectly treated the MD-only stem log as a complete
native frame ledger. Its FAIL report and all captures remain unchanged.
"""
import csv
import json
from pathlib import Path
import wave
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    base=ROOT/'build/pride-hyena-voice72';source=base/'voice-fight/report.json';prior=bound(source)
    out=base/'voice-audible';out.mkdir();failed=[k for k,v in prior['checks'].items() if not v]
    assert prior['result']=='FAIL' and failed==['md_voice_audible_before_native_animation_cue']
    host=base/'frontend/sdl_main.c';text=host.read_text()
    assert '#define NTSC_FPS (21477272.0 / 357366.0)' in text
    assert 'audio_acc += want;' in text and 'audio_acc -= n;' in text
    rate=48000;acc=0.0;counts={};totals={0:0}
    for field in range(1,4601):
        acc+=rate/(21477272.0/357366.0);n=int(acc);acc-=n;counts[field]=n;totals[field]=totals[field-1]+n
    pcm={};checks={};root=source.parent
    for name in ('native','md-aot','md-lle'):
        cmd=prior['commands'][name];assert '--no-audio' in cmd
        config=(root/name/'host.ini').read_text();assert 'audio_rate' not in config and 'volume' not in config
        with wave.open(str(root/name/'audio.wav'),'rb') as stream:
            checks[name+'_exact_reconstructed_total_samples']=stream.getnframes()==totals[4600] and stream.getframerate()==48000 and stream.getnchannels()==2 and stream.getsampwidth()==2
            pcm[name]=stream.readframes(stream.getnframes())
        rows=list(csv.DictReader((root/name/'stems.csv').open()))
        checks[name+'_logged_active_sample_counts_match_host_timeline']=all(int(r['samples'])==counts[int(r['frame'])] for r in rows)
    entry=int(prior['observations']['md-aot']['entries'][0]['field'])
    events=list(csv.DictReader((root/'native/events.csv').open()))
    late=min(int(r['frame'])+1 for r in events if r['event']=='0020' and int(r['frame'])+1>=entry)
    begin=totals[entry-1]*4;end=totals[late-1]*4
    checks['nonempty_native_prefix_exact']=begin>0 and pcm['native'][:begin]==pcm['md-aot'][:begin]
    checks['md_voice_audible_before_first_native_cue']=end>begin and pcm['native'][begin:end]!=pcm['md-aot'][begin:end]
    checks['early_voice_pcm_exact_between_modes']=pcm['md-aot'][begin:end]==pcm['md-lle'][begin:end]
    checks['all_other_retained_fight_checks_pass']=all(v for k,v in prior['checks'].items() if k not in ('md_voice_audible_before_native_animation_cue','pcm_exact_before_first_entry'))
    paths=[Path(__file__),source,host,base/'build-report.json']
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                prior_failed_check=failed,prior_capture_runs_reused_without_modification=True,
                first_entry_completed_field=entry,first_native_cue_completed_field=late,begin_byte=begin,end_byte=end,
                total_samples=totals[4600],earlier_incorrect_empty_window=prior['observations']['early_audio_window'],
                original_fight_report_not_relabelled=True,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,entry,late,begin,end,flush=True)


if __name__=='__main__':main()

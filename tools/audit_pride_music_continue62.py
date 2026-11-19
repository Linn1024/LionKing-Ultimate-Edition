"""Localize the retained Continue PCM parity failures without changing their gate."""
import csv
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_pride_audio_state import wav_data


def main():
    source=ROOT/'build/pride-music-output62/lifecycle/report.json';prior=bound(source)
    out=source.parent/'continue-pcm-audit';out.mkdir();observations={};paths=[Path(__file__),source]
    for name in ('native','over','all'):
        a=source.parent/('continue-'+name+'-aot');b=source.parent/('continue-'+name+'-lle')
        pcm_a=wav_data(a/'audio.wav');pcm_b=wav_data(b/'audio.wav')
        assert len(pcm_a)==len(pcm_b)
        positions=[i for i in range(len(pcm_a)//4) if pcm_a[i*4:i*4+4]!=pcm_b[i*4:i*4+4]]
        ca=list(csv.DictReader((a/'driver.csv').open()));cb=list(csv.DictReader((b/'driver.csv').open()))
        observations[name]=dict(stereo_frames=len(pcm_a)//4,differing_stereo_frames=len(positions),
            first=positions[0] if positions else None,last=positions[-1] if positions else None,
            differing_frame_duration_microseconds=len(positions)*1e6/48000,
            commands_equal=ca==cb,
            samples=[dict(index=i,aot=struct.unpack_from('<hh',pcm_a,i*4),lle=struct.unpack_from('<hh',pcm_b,i*4)) for i in positions[:16]])
        paths.extend([a/'audio.wav',b/'audio.wav',a/'driver.csv',b/'driver.csv'])
    report=dict(result='OBSERVED',observations=observations,
                failed_lifecycle_checks=[k for k,v in prior['checks'].items() if not v],
                root_cause_not_established=True,original_failure_retained=True,runtime_or_source_changed=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(observations,indent=2),flush=True)


if __name__=='__main__':main()

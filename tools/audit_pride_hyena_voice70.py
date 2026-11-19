"""Bind the original entry-once versus native animation-cue voice difference."""
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-hyena-voice70-audit';out.mkdir()
    native_path=ROOT/'build/pride-hyena-voice70-snes/report.json'
    md_path=ROOT/'build/pride-hyena-voice70-md/report.json'
    native=bound(native_path);md=bound(md_path)
    assert native['result']==md['result']=='PASS'
    source=ROOT/'engine/runner/tlk_audio.c';text=source.read_text()
    frames_path=ROOT/'build/pride-hyena-recovery/snes/hard/frames.json';frames=json.loads(frames_path.read_text())
    by_field={r['field']:r for r in frames}
    phases=[]
    for first,last in ((4121,4178),(4361,4418)):
        assert by_field[first-1]['action']!=0xc14501
        assert all(by_field[f]['action']==0xc14501 for f in range(first,last+1))
        cues=[r for r in native['observations']['voices'] if first<=int(r['frame'])+1<=last]
        callers=[int.from_bytes(bytes.fromhex(r['stack'])[5:8],'little')+1 for r in cues]
        phases.append(dict(first_field=first,last_field=last,voice_fields=[int(r['frame'])+1 for r in cues],
            delays=[int(r['frame'])+1-first for r in cues],callers=callers))
    current=re.findall(r'\{"audio.effects.world.hyena_hurt",0x20,19,4,2,0xc1458d\}',text)
    checks=dict(native_observation_all4600_guest_hashes_and_pcm_neutral=all(native['checks'].values()),
                original_md_five_action_entries_with_one_entry_pcm4=len(md['observations']['entries'])==5 and all(md['checks'].values()),
                two_full_native_actions_have_two_late_voices=all(p['delays']==[11,39] and p['callers']==[0xc1458d]*2 for p in phases),
                current_source_maps_late_native_cue_to_pcm4=len(current)==1)
    paths=[Path(__file__),native_path,md_path,frames_path,source]
    report=dict(result='CONFIRMED_SOURCE_TIMING_GAP' if all(checks.values()) else 'INCOMPLETE',checks=checks,
                native_action='C14501',md_action='19B6D6',native_phases=phases,
                current_resource_id='audio.effects.world.hyena_hurt',
                required_behavior='For MD choice emit PCM4 once on the original first-entry branch; suppress both later native event20 occurrences. Preserve native choice, gameplay, other voices and current-build continuation.',
                public_runtime_fixed=False,full_first_level_complete=False,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,phases,flush=True)


if __name__=='__main__':main()

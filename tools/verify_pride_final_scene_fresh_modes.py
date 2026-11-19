"""Compare actual full-boot Continue behavior in normal and interpreter modes."""
import csv
import json
from pathlib import Path
import re
import sys
import wave
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
from verify_windows import hashes,pixels

def pcm(path):
    with wave.open(str(path),'rb') as f:return f.readframes(f.getnframes())

def main():
    base=ROOT/'build/pride-final-scene-compiled-probe';out=base/'fresh-modes';out.mkdir()
    normal=base/'fresh-compiled';interpreted=base/'fresh-interpreted'
    a=bound(normal/'report.json');b=bound(interpreted/'report.json')
    timeline=lambda p:list(csv.DictReader((p/'transition.csv').open()))
    rows=timeline(normal);stats=re.search(r'pride_compiled_hook_calls=(\d+) callbacks=(\d+) redirects=(\d+) paired_services=(\d+)',(normal/'run.log').read_text())
    assert stats
    scene=json.loads((normal/'scene.json').read_text())['latched_gameplay']
    checks=dict(both_completed=a['observations']['exit_code']==b['observations']['exit_code']==0,
        compiled_hooks_active=int(stats[1])>0 and int(stats[2])>0 and int(stats[3])>0,
        transition_confirmed_at_expected_field=len(rows)==477 and all(int(r['field'])-int(r['age'])==4018 for r in rows),
        actual_transition_timeline=rows==timeline(interpreted),
        returned_to_pride=scene['descriptor']==903 and scene['player']==[64,1255] and scene['health']==4 and scene['lives']==2,
        guest_endpoint=hashes(normal/'run.log')==hashes(interpreted/'run.log'),
        actual_window=pixels(normal/'window.png')==pixels(interpreted/'window.png'),
        full_boot_pcm=pcm(normal/'audio.wav')==pcm(interpreted/'audio.wav'))
    generation=ROOT/'build/pride-final-maintained-generation2/report.json';bound(generation)
    generated=generation.parent/'normal/rng';original=ROOT/'build/pride-bounce-owner-work/game-program/rng'
    names=sorted(p.name for p in generated.glob('bank*.c'))
    checks['all_137_normal_rng_units_match_retained']=len(names)==137 and all(digest(generated/n)==digest(original/n) for n in names)
    paths=[Path(__file__),normal/'report.json',interpreted/'report.json',generation]
    result=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
        compiled_statistics=dict(zip(('calls','callbacks','redirects','paired_services'),map(int,stats.groups()))),
        existing_tier_fallback_retained=True,full_aot_coverage_claimed=False,resource_capabilities_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['result'],checks,result['compiled_statistics'],flush=True);assert all(checks.values()),checks

if __name__=='__main__':main()

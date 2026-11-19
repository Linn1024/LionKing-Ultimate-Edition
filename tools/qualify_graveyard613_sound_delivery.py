"""Aggregate the actual route, separately exercised taunt and final equivalent sound boundaries."""
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound
names=['graveyard594-cues','graveyard597-opening','graveyard601-native-music','graveyard603-lifecycle','graveyard604-pillar-qualified','graveyard605-native-seams','graveyard606-route-audio','graveyard607-audio-ui','graveyard610-sound-seams','graveyard611-taunt','graveyard612-pillar-resume']
proofs=[ROOT/'build'/name/'report.json' for name in names];reports={name:bound(path) for name,path in zip(names,proofs)}
for name in ('graveyard597-opening','graveyard601-native-music','graveyard603-lifecycle','graveyard604-pillar-qualified','graveyard605-native-seams','graveyard607-audio-ui','graveyard612-pillar-resume'):assert reports[name]['result']=='PASS',name
route=reports['graveyard606-route-audio'];assert all(v for k,v in route['checks'].items() if k!='all_exercised_effect_families')
assert reports['graveyard611-taunt']['result']=='TAUNT_EXERCISED' and reports['graveyard611-taunt']['count']>0
trace=reports['graveyard610-sound-seams'];assert trace['checks']['corrected_one_per_event'] and trace['checks']['gameplay_preserved'] and trace['checks']['actual_picture_preserved'] and not trace['checks']['audio_changes']
key=lambda rows:[tuple(r[k] for k in ('frame','actor','pc','value')) for r in rows]
assert key(trace['records']['old'])==key(trace['records']['current'])
sounds={(int(x['selector']),int(x['value'])) for x in route['sounds']};required={(19,1),(19,2),(19,4),(19,7),(19,15),(2,94),(2,97),(2,98),(2,105),(2,112),(2,117),(2,123),(2,127),(2,171),(2,92)};assert required<=sounds
build=ROOT/'build/graveyard609/build-report.json';b=bound(build);out=ROOT/'build/graveyard613-sound-delivery';out.mkdir(exist_ok=True);paths=[Path(__file__),build,*proofs]
checks=dict(full_route_to_living_stampede=True,all_observed_sound_families=True,separate_natural_taunt=True,native_controls=True,independent_native_music=True,independent_bones_pillar=True,current_save_and_pause=True,actual_ui_persistence_restart=True,equivalent_final_boundaries=True,actual_windows=True)
(out/'report.json').write_text(json.dumps(dict(result='PASS',checks=checks,player_sha256=b['binary_sha256'],scope='Practical Graveyard sound/gameplay scope; native gameplay retained and every observed MD family mapped.606 expected taunt on a route which never performs it;611 exercises the real native taunt separately.610 disproves a suspected duplicate: old/new bone PCM/events/picture match. Final observer uses the same store before/after for the execution paths;612 preserves restored pillar sound peaks through one impact. No gameplay or audible duplicate-bug fix is claimed, and no unrelated whole-level repeat was made.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print('QUALIFIED',b['binary_sha256'],flush=True)

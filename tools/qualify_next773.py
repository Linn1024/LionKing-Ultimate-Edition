"""Bound practical delivery qualification; do not claim universal MD AI/canyon parity."""
import json,struct,re
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/next773-qualified';out.mkdir(exist_ok=True)
names=('next745-presentation','next749-background','next752-route','next755-exile','next757-death','next761-windows','next764-choices','next768-setup','next772-matte')
paths=[ROOT/'build'/n/'report.json' for n in names];r={n:bound(p) for n,p in zip(names,paths)}
build=ROOT/'build/next771/build-report.json';helper=ROOT/'build/next741-helper/build-report.json';bound(build);bound(helper)
def payload(path):
 data=path.read_bytes();count=struct.unpack_from('<I',data,20)[0];at=192+416+17792;images={}
 for _ in range(count):
  pose,a,b=struct.unpack_from('<III',data,at);at+=12;images[pose]=data[at:at+a+b];at+=a+b
 gameplay=data[at:];version=struct.unpack_from('<I',gameplay,8)[0];n=5 if version==2 else 6;sizes=struct.unpack_from('<'+'I'*n,gameplay,16);sections=[];offset=40
 for size in sizes:sections.append(gameplay[offset:offset+size]);offset+=size
 assert offset==len(gameplay)
 return images,sections,data[192:192+416+17792]
old,oldsections,oldpal=payload(ROOT/'build/graveyard707-helper/sprites.assets');new,newsections,newpal=payload(ROOT/'build/next741-helper/sprites.assets')
def hashes(folder):return re.findall(r'wram_sha256=([a-f0-9]+)',(ROOT/f'build/next764-choices/{folder}/run.log').read_text())
route=r['next752-route'];roles=json.loads((ROOT/'build/next752-route/sprites.json').read_text())['seen_by_role'];commands=json.loads((ROOT/'build/next755-exile/report.json').read_text())
checks=dict(original_c_background_pixels=r['next749-background']['result']=='PASS',graphics_guest_controls=r['next745-presentation']['result']=='PASS',both_levels_completed=route['last']['level']==5 and route['last']['health']>0,all_four_route_windows=len(route['captures'])==4,actor_sources_exercised=all(roles[k]>0 for k in ('stampede_cub','stampede_rock','lizard','porcupine','leaves')),final_exile_sound_and_progression=commands['result']=='PASS',death_sources_save_music_retry=r['next757-death']['result']=='PASS',actual_death_windows_current_save=r['next761-windows']['result']=='PASS',pickup_and_roar_sources=r['next764-choices']['result']=='PASS',pickups_guest_unchanged=hashes('pickups-snes')[0]==hashes('pickups-md')[0],all_existing_sprite_pixels_preserved=all(new[p]==v for p,v in old.items()),existing_palettes_death_bank_preserved=oldpal==newpal,all_five_previous_gameplay_sections_preserved=oldsections==newsections[:5],native_setup=r['next768-setup']['result']=='PASS',final_stampede_client_matte=r['next772-matte']['result']=='PASS')
paths += [Path(__file__),build,helper,ROOT/'engine/cmake/TlkPrideFinalPlayer.cmake',ROOT/'engine/runner/tlk_next_scene_data.c',ROOT/'Play Stampede MD.cmd',ROOT/'Play Simbas Exile MD.cmd',ROOT/'profiles/stampede-md.ini',ROOT/'profiles/exile-md.ini']
(out/'report.json').write_text(json.dumps(dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,scope='Practical Stampede/Exile delivery. Combined route and final Exile sound continuation reach healthy Hakuna. Later changes only observed-pickup presentation, source help/availability and Stampede matte; focused affected checks retained. Stampede uses native perspective geometry with MD colors. Native movement/AI remain; no universal MD behavior or every-pose claim. Native fall/final-life paths retained.',old_images=len(old),new_images=len(new),prepared_bytes=(ROOT/'build/next741-helper/sprites.assets').stat().st_size,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths}),indent=2)+'\n');print(checks)

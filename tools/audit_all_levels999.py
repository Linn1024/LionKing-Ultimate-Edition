"""Audit the practical playable-level milestone using retained focused evidence."""
import json
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/all-levels999-audit';out.mkdir(exist_ok=True)
names=['next752-route','next755-exile','hakuna856-selected','hakuna859-qualified','destiny818-route','destiny863-handoff','later902-selected','later913-selected','pride933-route','pride951-qualified','ending955-route','ending957-credits','bonus970-prepared','bonus995-qualified','bonus996-publication','bonus997-installed']
paths=[ROOT/'build'/n/'report.json' for n in names];reports={};identities={}
for n,p in zip(names,paths):
 try:reports[n]=bound(p);identities[n]=True
 except AssertionError as e:identities[n]=str(e)
checks={'retained_source_identities':all(x is True for x in identities.values())}
if checks['retained_source_identities']:
 r=reports
 checks.update(stampede_exile_reach_hakuna=r['next752-route']['last']['level']==5 and r['next752-route']['last']['health']>0 and r['next755-exile']['result']=='PASS',
  selected_hakuna_route_healthy=r['hakuna856-selected']['checks']['healthy_destiny'],
  separate_hakuna_seams_qualified=r['hakuna859-qualified']['result']=='PASS',
  destiny_reaches_be_prepared=r['destiny818-route']['result']=='PASS' and r['destiny863-handoff']['result']=='PASS',
  be_prepared_return_complete=r['later902-selected']['result']=='PASS',
  return_md_contact_tape_honestly_partial=r['later913-selected']['result']=='PARTIAL',
  scar_reaches_victory=r['pride933-route']['gameplay']['descriptor']==0x7a9 and r['pride933-route']['gameplay']['health']>0,
  main_resources_qualified=r['pride951-qualified']['result']=='PASS',
  credits_reached=r['ending955-route']['gameplay']['descriptor']==0x83f,
  actual_credits_visible=r['ending957-credits']['result']=='PASS',
  earlier_assets_preserved=r['bonus970-prepared']['result']=='PASS',
  final_bonus_qualified=r['bonus995-qualified']['result']=='PASS',
  coherent_install=r['bonus996-publication']['result']=='PASS',
  actual_bonus_launchers=r['bonus997-installed']['result']=='PASS')
manifest=json.loads((ROOT/'game-data/install.json').read_text(encoding='utf-8-sig'))
package=json.loads((ROOT/'dist/installed-preview989/package.json').read_text())
checks['published_player_identity']=digest(ROOT/'dist/installed-preview989/LionKing.exe')==package['player_sha256']
checks['current_prepared_package']=manifest['sprite_assets']['mapped_images']==1466 and manifest['scene_cache']['version']==3
checks['current_launcher']='dist/installed-preview989' in (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
limits=['Native Stampede perspective and256 viewport; no complete MD perspective adapter.', 'Native most enemy AI, Scar combat, bonus catches/timers/scoring/rewards/effects, intro/result/counter art and unreviewed/flashing bodies.', 'Native post-fight/rainy ending/credits presentation. Actual fight stays in normal9;07DB is post-fight.', 'Return8 completes with native contacts; full MD adult-hyena-contact8 tape is still partial. Ordinary MD-box combat works; no full-route claim.', 'Historical routes plus preservation/focused current checks, not a newly replayed whole-game matrix or universal MD parity certification.', 'Static native port retains allowed emulated subsystems and existing runtime data access; complete removal of every runtime ROM data dependency is not claimed.']
paths += [Path(__file__),ROOT/'game-data/install.json',ROOT/'scripts/RunInstalledPreview.ps1',ROOT/'dist/installed-preview989/package.json',ROOT/'docs/HANDOFF.md',ROOT/'docs/all-levels-progress.md',ROOT/'docs/bonus-delivery.md',ROOT/'README.md',ROOT/'docs/background-audit.md',ROOT/'engine/docs/devlog.md']
report=dict(result='DELIVERED' if all(checks.values()) else 'INCOMPLETE',milestone='All remaining main levels through native victory and scrolling credits, with practical independent resource choices and applicable bonus stages.',checks=checks,source_identity_checks=identities,retained_results={n:r.get('result') for n,r in reports.items()},limits=limits,published_player=989,source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
for n,x in identities.items():
 if x is not True:print('UNBOUND',n,x,flush=True)

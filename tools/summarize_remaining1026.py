"""Retain a valid negative Genesis replay and the separately qualified fixes."""
import json
from pathlib import Path
from audit_scenes import ROOT
from pride_arena_history import bound
from build_pride_compiled_hooks import digest
out=ROOT/'build/remaining1026-review';out.mkdir(exist_ok=True)
names=['remaining1004-bounds','remaining1008-data','remaining1010-combat','remaining1016-client','remaining1017-setup','remaining1019-qualified','remaining1020-publication','remaining1024-boot','remaining1025-genesis-tas']
paths=[ROOT/'build'/n/'report.json' for n in names];reports={n:bound(p) for n,p in zip(names,paths)}
checks={n:reports[n]['result']=='PASS' for n in names if n not in ('remaining1004-bounds','remaining1025-genesis-tas')}
tas=reports['remaining1025-genesis-tas'];checks['valid_negative_tas']=tas['result']=='FAIL' and all(tas['checks'][k] for k in ('confirmed_easy_boot','clean_exit','profile_loaded','exact_available_md_profile','all_recorded_inputs_consumed','actual_window_captured')) and not tas['checks']['all_main_levels'] and not tas['checks']['victory_or_credits']
s=(ROOT/'Lion King, The (USA).sfc').read_bytes();m=(ROOT/'Lion King, The (World).md').read_bytes()
constants=[('scar_first_health_parameter',0x65c31,'f46400',0x1b0e62,'3f3c0064'),('scar_second_health_parameter',0x65cf8,'f49600',0x1b0f36,'3f3c0096'),('scar_final_health_parameter',0x65e4f,'f4c800',0x1b107c,'3f3c00c8'),('scar_combo_end65',0x65fc2,'c94100',0x1b11aa,'0c690041002c'),('scar_combo_step20',0x65ffa,'c91400',0x1b11ee,'0c690014002c'),('scar_combo_step30',0x66017,'c91e00',0x1b1238,'0c69001e002c')]
constant_checks={n:s[np:np+len(bytes.fromhex(nb))]==bytes.fromhex(nb) and m[mp:mp+len(bytes.fromhex(mb))]==bytes.fromhex(mb) for n,np,nb,mp,mb in constants};checks['bounded_scar_ai_original_bytes']=all(constant_checks.values())
checks['scar_duel_distance_difference']=s[0x65d73:0x65d76]==bytes.fromhex('c91800') and m[0x1b0fb0:0x1b0fb4]==bytes.fromhex('0c400010')
checks['installed_binary']=digest(ROOT/'dist/installed-preview1014/LionKing.exe')==json.loads((ROOT/'dist/installed-preview1014/package.json').read_text())['player_sha256']
paths += [Path(__file__),ROOT/'docs/remaining-fidelity-audit.md',ROOT/'docs/HANDOFF.md',ROOT/'docs/all-levels-progress.md',ROOT/'README.md',ROOT/'engine/docs/devlog.md',ROOT/'engine/runner/tlk_hitboxes.c',ROOT/'engine/runner/tlk_hitbox_data.c',ROOT/'engine/runner/tlk_wide.c',ROOT/'tools/scar_bounds_pairs.json',ROOT/'profiles/available-md.ini',ROOT/'Play Available MD.cmd']
report=dict(result='REVIEWED_WITH_OPEN_MD_GAPS' if all(checks.values()) else 'INCOMPLETE',verification_checks=checks,published_player=1014,scar_original_constant_checks=constant_checks,genesis_tas_result=tas['result'],genesis_tas_checks=tas['checks'],genesis_tas_final=tas['final_gameplay'],genesis_tas_polls=[tas['tape_words_used'],tas['tape_words_total']],open_scope=['First-level Genesis TAS gameplay equivalence; replay never reaches next main stage.', 'Native Stampede perspective and ending presentation.', 'Most native adult/general enemy movement/combat, additional adult/Scar FX and bonus gameplay/counter/FX scope.', 'Full selected-MD-contact Return8 and full selected-Scar-box route remain unproved.', 'Unknown/flashing art retains deliberate native guards; not all fallback is a proven visible defect.'],source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)

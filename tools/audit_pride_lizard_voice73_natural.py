"""Bind ordinary active-list lizard owners and counter32/51 applicability."""
import csv
import json
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-lizard-voice73-natural';out.mkdir();checks={};observations={};paths=[Path(__file__)]
    md_by_field={}
    for kind,action,descriptor in (('native',0xc16451,0xc58ca4),('md',0x19c39e,0x9798e)):
        report_path=ROOT/f'build/pride-lizard-history/{kind}/report.json';bound(report_path)
        actors_path=report_path.parent/'actors.json';rows=json.loads(actors_path.read_text());paths.extend([report_path,actors_path])
        observed=[];links=True
        for row in rows:
            previous=0 if kind=='native' else 0x934e
            for actor in row['actors']:
                words=actor['words'];links&=words[0]==previous;previous=actor['actor']
                state=(words[24]|words[25]<<16) if kind=='native' else (words[24]<<16|words[25])&0xffffff
                if kind=='md':md_by_field[(row['field'],actor['actor'])]=(state,words[22])
                if state!=action:continue
                desc=(words[2]|(words[3]&255)<<16) if kind=='native' else (words[2]<<16|words[3])&0xffffff
                observed.append(dict(field=row['field'],actor=actor['actor'],descriptor=desc,counter=words[22],marker_word=words[34]))
        checks[kind+'_active_backward_links_valid']=links
        checks[kind+'_all288_attack_rows_have_reviewed_descriptor']=len(observed)==288 and all(r['descriptor']==descriptor for r in observed)
        boundaries=[r for r in observed if r['counter'] in (32,51)]
        checks[kind+'_four_natural_counter32_and51_states']=sum(r['counter']==32 for r in boundaries)==sum(r['counter']==51 for r in boundaries)==4
        checks[kind+'_observed_boundary_markers_enabled']=all(r['marker_word']!=0 for r in boundaries)
        observations[kind]=dict(attack_rows=len(observed),descriptor=descriptor,boundaries=boundaries)
    census=ROOT/'build/pride-audio-inventory/report.json';bound(census);commands=census.parent/'commands.csv';paths.extend([census,commands])
    matched=[]
    for row in csv.DictReader(commands.open()):
        if row['selector']!='2' or row['value']!='124' or row['outer_caller']!='19c462':continue
        key=(int(row['frame'])-1,int(row['actor'],16))
        if key in md_by_field:
            matched.append(dict(sound_field=int(row['frame']),actor=key[1],preceding_action=md_by_field[key][0],preceding_counter=md_by_field[key][1]))
    checks['four_original_md_sound_calls_follow_owned_counter32']=len(matched)==4 and all(r['preceding_action']==0x19c39e and r['preceding_counter']==32 for r in matched)
    gate=ROOT/'build/pride-lizard-voice73/report.json';bound(gate);paths.append(gate)
    report=dict(result='BOUNDED_NATURAL_LIZARD_VOICE_OWNERS_VERIFIED' if all(checks.values()) else 'INCOMPLETE',checks=checks,
                observations=observations,md_call_boundary_pairs=matched,
                runtime_changed=False,whole_actor_or_contact_equivalence_claimed=False,
                scope='Existing ordinary captures; original active ownership and timer stages. No absolute cross-version field alignment or full earlier-guard equivalence claim.',
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,matched,flush=True)


if __name__=='__main__':main()

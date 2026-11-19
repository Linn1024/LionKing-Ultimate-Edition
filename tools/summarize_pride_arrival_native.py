"""Extend the frozen arrival index with fresh full native regression evidence."""
from pathlib import Path

original=Path(__file__).with_name('summarize_pride_arrival_audio.py')
source=original.read_text().replace("base/'native-gates/play-report.json'","base/'native-gates2/play-report.json'")
needle="    paths+=[Path(__file__),ROOT/'tools/pride_arrival_history.py']"
assert source.count(needle)==1
source=source.replace(needle,"""    allbugs_path=base/'allbugs-arrival2/report.json'
    allbugs=bound(allbugs_path)
    assert allbugs['result']=='PASS' and len(allbugs['checks'])==10 and all(allbugs['checks'].values())
    checks+=10
    paths += [allbugs_path,base/'allbugs-observer/build-report.json',original]
    changed_path=base/'arrival-changed-source/report.json'
    changed=bound(changed_path)
    assert changed['result']=='PASS' and len(changed['checks'])==20 and all(changed['checks'].values())
    checks+=20
    paths += [changed_path]
    restart_path=base/'arrival-restart2/report.json'
    restart=bound(restart_path)
    assert restart['result']=='PASS' and len(restart['checks'])==12 and all(restart['checks'].values())
    checks+=12
    paths += [restart_path]
    route_path=base/'arrival-route/report.json'
    route=bound(route_path)
    assert route['result']=='PASS' and len(route['checks'])==19 and all(route['checks'].values())
    checks+=19
    paths += [route_path]
"""+needle)
source=source.replace('paired_picture_full_wram_fields=28500,','paired_picture_full_wram_fields=45100,\n        native_allbugs_tracked_fields_per_mode=60648,observer_neutrality_fields=3000,actual_restart_fields=3600,\n        audible_complete_route_fields=5000,audible_route_native_comparison_fields=5000,')
source=source.replace('cold_process_mode_combinations=20,','cold_process_mode_combinations=20,changed_audio_process_combinations=4,')
exec(compile(source,str(original),'exec'))

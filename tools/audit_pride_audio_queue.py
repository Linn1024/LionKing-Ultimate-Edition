"""Bind device priming, the live-load regression, full routes and unchanged game."""
import json
from pathlib import Path
import subprocess

from md_lab import ROOT
from build_pride_compiled_hooks import digest
from pride_arena_history import bound


def main():
    out=ROOT/'build/pride-audio-queue-bindings';out.mkdir();checks={};reports={}
    names=['pride-restart-difficulty25/build-report.json',
           'pride-audio-queue27/build-report.json','pride-audio-queue27/queue/report.json',
           'pride-audio-prime28/build-report.json','pride-audio-prime28/queue/report.json',
           'pride-audio-prime28/queue-lle/report.json','pride-audio-prime28/queue-ui/report.json',
           'pride-audio-prime29/failed-build.json','pride-audio-prime30/build-report.json',
           'pride-audio-prime30/queue-ui/report.json','pride-audio-prime30/queue-lle/report.json',
           'pride-audio-prime30/routes/report.json','pride-audio-prime30/routes-device/report.json']
    for name in names:reports[name]=bound(ROOT/'build'/name);checks[name+'_bound']=True
    for index,count in [(2,15),(4,39),(5,26),(9,9),(10,26),(11,30),(12,8)]:
        r=reports[names[index]];checks[names[index]+'_passes']=r['result']=='PASS' and len(r['checks'])==count and all(r['checks'].values())
    baseline=reports[names[2]]['observations']
    checks['baseline_empty_queue_observed']=all(r['underruns']>0 for r in baseline.values())
    checks['baseline_device_shortfall_observed']=any(r['last_row']['missing_calls']>0 for r in baseline.values())
    failed=reports[names[6]]
    checks['retained_live_load_failure']=failed['result']=='FAIL' and len(failed['checks'])==9 and sum(failed['checks'].values())==8 and failed['checks']['no_missing_requests'] is False
    checks['retained_early_hunk_abort']=reports[names[7]]['result']=='ABORTED' and not (ROOT/'build/pride-audio-prime29/player.exe').exists()
    previous=reports[names[0]]['link_inputs_sha256']
    checks['reference25_binary']=digest(ROOT/'build/pride-restart-difficulty25/player.exe')==reports[names[0]]['binary_sha256']
    for index in [1,3,8]:
        r=reports[names[index]];folder=(ROOT/'build'/names[index]).parent;inputs=r['link_inputs_sha256']
        checks[folder.name+'_binary']=digest(folder/'player.exe')==r['binary_sha256']
        checks[folder.name+'_md_component']=digest(folder/'genesis_plus_gx_libretro.dll')==digest(ROOT/'build/pride-restart-difficulty25/genesis_plus_gx_libretro.dll')
        checks[folder.name+'_317_inputs']=len(inputs)==317 and all(digest(ROOT/p)==sha for p,sha in inputs.items())
        removed=set(previous)-set(inputs);added=set(inputs)-set(previous)
        checks[folder.name+'_host_only']=len(removed)==len(added)==1 and all(Path(p).name=='host.obj' for p in removed|added) and all(previous[p]==inputs[p] for p in set(previous)&set(inputs))
    text=(ROOT/'build/pride-audio-prime30/frontend/sdl_main.c').read_text()
    checks['genuine_pcm_before_resume']='SDL_GetAudioStreamQueued(astream)>=target*4' in text and 'AudioDeviceQueue(abuf,c,audio_target);' in text
    checks['live_load_paused_before_io']='uint32_t hf = 0;\n    AudioDeviceReset();\n    if (!ContinueLifecycleLoad(path, &hf))' in text
    checks['menu_pause_reprime']='if(open)AudioDeviceReset();' in text
    checks['underruns_not_only_evidence']=all(r['last_row']['missing_calls']==0 for r in reports[names[10]]['observations'].values()) and reports[names[9]]['checks']['no_missing_requests']
    checks['public_player_unchanged']=digest(ROOT/'build/pride-cold-boot2/player.exe')=='dcd4130049e874f4657f3b313cbde198a41119b4d3bd82f95a3a07618c671a02'
    checks['public_launcher_unchanged']=digest(ROOT/'Play Standalone Preview.cmd')=='c9f0aa27fd1a36f9950501098743e3099a690fea62fc9e5436414e035f718d87'
    checks['helper_unchanged']=digest(ROOT/'dist/PrepareFinalAssets.exe')=='1b3adc42d9de92651a847d1b11d2083c66b552e387fc4c9119ed3545b88828b9'
    checks['frameworks_unmodified']=not subprocess.check_output(['git','status','--porcelain','--','snesrecomp','recomp-ui'],cwd=ROOT/'engine').strip()
    paths=[Path(__file__),*[ROOT/'build'/name for name in names]]
    report=dict(result='PASS' if all(checks.values()) else 'FAIL',checks=checks,
                source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in paths})
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],sum(checks.values()),'/',len(checks),[k for k,v in checks.items() if not v],flush=True)


if __name__=='__main__':main()

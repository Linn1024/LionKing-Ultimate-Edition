"""Measure batched blank-screen title transfers in an isolated LLE prototype."""
import json,os,re,shutil,subprocess
from pathlib import Path
from audit_scenes import ROOT
from build_pride_compiled_hooks import argv,digest
from pride_arena_history import bound
base=ROOT/'build/pride-porcupine327';bp=base/'build-report.json';b=bound(bp)
out=ROOT/'build/pride-title-dma333-probe';out.mkdir(exist_ok=True);cwd=ROOT/'build/pride-sprite-fresh44'
cmd=b['compiles']['host'].copy();cmd[cmd.index('-c')]='-E'
for flag,value in (('-o',out/'host-original.i'),('-MT',out/'host.obj'),('-MF',out/'host.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'preprocess.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
text=(out/'host-original.i').read_text();anchor='static void ContinueTitlePayload(CpuState *cpu,uint32_t pc) {';assert text.count(anchor)==1
extension='''
static void TitleBatchDma333(CpuState *cpu,uint32_t pc) {
    if(!getenv("TLK_TITLE_DMA333") || !continue_transition_mode || !final_scene_entry ||
       !continue_title_ready_field || continue_transition.confirmed_field || reload_fast_used ||
       FinalAddress(0xdf)!=0xc005ab || FinalWord(0x1ff9e)!=14)return;
    if(!(g_snes->ppu->inidisp&0x80) || g_snes->nmiEnabled || cpu->D ||
       cpu->DB!=0x80 || g_snes->dma->dmaBusy || g_snes->dma->dmaTimer)exit(123);
    unsigned mask=(pc==0xc09750 || pc==0xc0978a)?cpu->X&255:cpu->A&255;
    if(mask!=1)exit(123);
    for(unsigned n=0;n<8;n++)if(g_snes->dma->channel[n].dmaActive || g_snes->dma->channel[n].hdmaActive)exit(123);
    unsigned bytes=g_snes->dma->channel[0].size;
    cpu_write8(cpu,cpu->DB,0x420b,mask);
    unsigned cycles=0;
    while(g_snes->dma->dmaBusy) {if(++cycles>300000)exit(123);dma_doDma(g_snes->dma);}
    fprintf(stderr,"title_batch333 age=%u pc=%06x bytes=%u cycles=%u\\n",(unsigned)snes_frame_counter+1-final_scene_entry,pc,bytes,cycles);
    interp_bridge_pre_opcode_redirect(pc+3);
}
'''
# The preprocessed TU has already expanded the bridge macros. Register through
# the same table and redirect dispatcher as the maintained frontend.
extension=extension.replace('interp_bridge_pre_opcode_redirect','PrideRedirectOpcode')
extension=extension.replace('stderr','(__acrt_iob_func(2))')
registration='\n    PrideRegisterOpcodeHook(0xc07397,TitleBatchDma333);PrideRegisterOpcodeHook(0xc0734e,TitleBatchDma333);PrideRegisterOpcodeHook(0xc09750,TitleBatchDma333);PrideRegisterOpcodeHook(0xc0978a,TitleBatchDma333);\n'
text=text.replace(anchor,extension+'\n'+anchor+registration);(out/'host.i').write_text(text)
cmd=b['compiles']['host'].copy()
for flag,value in (('-c',out/'host.i'),('-o',out/'host.obj'),('-MT',out/'host.obj'),('-MF',out/'host.d')):cmd[cmd.index(flag)+1]=str(value)
with (out/'compile.log').open('wb') as log:subprocess.run(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
inputs=argv('link '+(base/'link.rsp').read_text())[1:];old=Path(b['compiles']['host'][b['compiles']['host'].index('-o')+1])
matches=[i for i,p in enumerate(inputs) if not p.startswith('-') and (cwd/p).resolve()==old];assert len(matches)==1;inputs[matches[0]]=(out/'host.obj').as_posix()
(out/'link.rsp').write_text(subprocess.list2cmdline(inputs))
with (out/'link.log').open('wb') as log:subprocess.run(['C:/mingw32/bin/g++.exe','@'+str(out/'link.rsp'),'-o',str(out/'player.exe')],cwd=cwd,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy2(base/'genesis_plus_gx_libretro.dll',out/'genesis_plus_gx_libretro.dll')
reference=ROOT/'build/pride-title-readiness-probe3/report.json';ref=bound(reference)
assets=json.loads((ROOT/'build/pride-battle320/report.json').read_text())['commands']['md-new']
commands={};exits={}
for label in ('control','batch'):
    folder=out/label;folder.mkdir(exist_ok=True);cmd=ref['commands']['256-neutral'].copy();cmd[0]=str(out/'player.exe')
    cmd+=['--lle'];cmd[cmd.index('--frames')+1]='4850'
    for flag in ('--asset-cache','--hud-assets','--sprite-assets','--caption-assets','--checkpoint-assets','--revival-assets','--native-hud-assets'):
        if flag not in cmd:cmd += [flag,assets[assets.index(flag)+1]]
    for flag,name in (('--config','host.ini'),('--resource-profile','resources.ini')):
        (folder/name).write_bytes(Path(cmd[cmd.index(flag)+1]).read_bytes());cmd[cmd.index(flag)+1]=str(folder/name)
    for flag,name in (('--dump-window','window.png'),('--dump-scene','scene.json'),('--wav','audio.wav')):
        if flag in cmd:cmd[cmd.index(flag)+1]=str(folder/name)
    env={k:v for k,v in os.environ.items() if not k.startswith(('TLK_','SDL_','SNESRECOMP_'))};env.update(SDL_VIDEODRIVER='dummy',TLK_CONTINUE_EXIT_LOG=str(folder/'exit.csv'))
    if label=='batch':env['TLK_TITLE_DMA333']='1'
    commands[label]=cmd
    with (folder/'run.log').open('wb') as log:exits[label]=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW).returncode
    print(label,exits[label],flush=True)
report=dict(result='OBSERVED',exits=exits,commands=commands,scope='Isolated interpreted prototype, genuine prefatal backend checkpoint; batching native DMA through existing byte engine only while title is forced blank and NMI disabled. No maintained code or public player changes.',source_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in (Path(__file__),bp,reference,out/'host.i',out/'host-original.i')},artifacts_sha256={p.relative_to(out).as_posix():digest(p) for p in out.rglob('*') if p.is_file() and p.name!='report.json'})
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('OBSERVED',flush=True)

"""Verify independent first-level NPC artwork/palettes through player windows."""
import json
import os
import subprocess
from audit_scenes import ROOT
from verify_windows import hashes,pixels

def main():
    dest=ROOT/'build/pride-npc-verification';dest.mkdir(parents=True,exist_ok=True)
    config=dest/'host.ini';config.write_text('opengl = 1\nscale = 3\n')
    results={}
    for actor,frame in [('lizard',985),('hyena',3890),('porcupine',3000),('pickup',1020),('hud',2200)]:
        branch='graphics.hud' if actor=='hud' else 'graphics.sprites.pickups' if actor=='pickup' else 'graphics.sprites.enemies.'+('hyenas' if actor=='hyena' else 'other')
        captures={};guest={}
        for source,choices in [('snes',''),('frames',branch+'.frames = md\n'),
                               ('palette',branch+'.palette = md\n'),('both',branch+' = md\n')]:
            name=actor+'-'+source;profile=dest/(name+'.ini');profile.write_text('schema = 1\ngame = snes\n'+choices)
            env=os.environ.copy();env['TLK_SPRITE_REPORT']=str(dest/(name+'-coverage.json'))
            cmd=[str(ROOT/'dist/LionKing.exe'),'--rom',str(ROOT/'Lion King, The (USA).sfc'),
                 '--md-rom',str(ROOT/'Lion King, The (World).md'),'--config',str(config),
                 '--resource-profile',str(profile),'--no-pace','--no-audio','--no-record','--frames',str(frame),
                 '--input-polled',str(ROOT/'engine/tapes/allbugsF.read.tape'),'--dump-window',str(dest/(name+'.png'))]
            log=dest/(name+'.log')
            with log.open('wb') as output:subprocess.run(cmd,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT,check=True,timeout=90)
            guest[source]=hashes(log);captures[source]=pixels(dest/(name+'.png'))
            assert guest[source] and guest[source]==guest['snes'],name+' changed the guest state'
        width,height,native=captures['snes'];difference={}
        for source in ['frames','palette','both']:
            w,h,picture=captures[source];assert (w,h)==(width,height)
            difference[source]=sum(a!=b for a,b in zip(native,picture))
        assert difference['both']>0,actor+' adaptation was invisible'
        assert captures['both']!=captures['frames'],actor+' palette was not independent'
        assert captures['both']!=captures['palette'],actor+' artwork was not independent'
        results[actor]={'guest_hashes_unchanged':True,'changed_pixels':difference}
        print(actor,results[actor],flush=True)
    (dest/'report.json').write_text(json.dumps({'result':'PASS','actors':results},indent=2)+'\n')
    print('NPC window source-independence PASS')

if __name__=='__main__':main()

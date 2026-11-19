"""Read-only native Continue cursor/clock observer from the current139 graph."""
from pathlib import Path
builder=Path(__file__).with_name('build_pride_menu197_observer.py')
source=builder.read_text().replace('pride-menu197-observer','pride-menu206-observer').replace('snes_frame_counter<4000','snes_frame_counter<3000')
anchor="target = out / 'host.i'"
assert source.count(anchor)==1
extra=r'''
anchor206=',age,stack\n",file);'
assert s.count(anchor206)==1
s=s.replace(anchor206,',age,stack,choice_x,choice_action\n",file);')
anchor206='final_scene_entry,final_scene_age,cpu?cpu->S:0);'
assert s.count(anchor206)==1
s=s.replace(anchor206,'final_scene_entry,final_scene_age,cpu?cpu->S:0,MenuWord197(0xa68e)>0x1000 && MenuWord197(0xa68e)<0xff80?MenuWord197(MenuWord197(0xa68e)+8):0,MenuWord197(0xa68e)>0x1000 && MenuWord197(0xa68e)<0xff80?MenuPointer197(MenuWord197(0xa68e)+0x30):0);')
anchor206='"%s,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u\\n"'
# Generated preprocessed C contains a single escaped newline.
anchor206=anchor206.replace('\\n','\n')
assert s.count(anchor206)==1
s=s.replace(anchor206,anchor206.replace('\\n','\\n')[:-3]+',%u,%u\\n"'.replace('\\n','\n'))
'''
source=source.replace(anchor,extra+'\n'+anchor)
source=source.replace('paths = [Path(__file__),bp,old,pre,target,rsp]',
                      'paths = [Path(__file__),builder,bp,old,pre,target,rsp]')
exec(compile(source,str(builder),'exec'))

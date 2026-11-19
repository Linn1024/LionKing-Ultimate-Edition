"""Compare Return's prepared-buffer C sampler with five actual original VDP states."""
from pathlib import Path
template=Path(__file__).with_name('check_be_prepared867_sampler.py');s=template.read_text().replace('build/be-prepared867-sampler','build/return890-sampler').replace('build/be-prepared866/build-report.json','build/return889/build-report.json').replace('build/be-prepared864-background/report.json','build/return888-background/report.json').replace('build/next824-reference/','build/later873-reference/')
s=s.replace('TlkMdSceneBackgroundReady(7)','TlkMdSceneBackgroundReady(8)').replace('TlkMdSceneBackgroundViewPixel(7,','TlkMdSceneBackgroundViewPixel(8,')
s=s.replace("wx=(x-row['background_scroll'])&511;", "scroll=struct.unpack_from('>H',v,0xfc02+y*4)[0]&1023;wx=(x-scroll)&511;")
exec(compile(s,str(template),'exec'))

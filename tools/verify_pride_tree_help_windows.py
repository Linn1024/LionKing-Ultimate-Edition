"""Check paged capability help through real Windows keys, captures and font math."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_soft_tree.py')
source=original_verifier.read_text()
source=source.replace("base=ROOT/'build/pride-soft-tree'","base=ROOT/'build/pride-tree-help2'")
source=source.replace("out=base/'windows'/args.case","out=base/'windows'/args.case")
source=source.replace('                assert USER32.PostMessageW(hwnd,0x201,1,x+(y<<16));',
                      '                assert USER32.PostMessageW(hwnd,0x200,0,x+(y<<16));\n                assert USER32.PostMessageW(hwnd,0x201,1,x+(y<<16));')
source=source.replace("time.sleep(.1)\n                row=latest(trace);checks['mouse_after_resize']", "wait(lambda r:choice(r,'display.viewport')[1]==0 and r['dirty']==1)\n                row=latest(trace);checks['mouse_after_resize']")
source=source.replace("                key(0x1b)  # leave Resources section\n                key(0x1b)  # close settings", """                key(0x0d)
                row=wait(lambda r:r['about']==2)
                checks['reopen_applied_choices']=row['dirty']==0 and profile.read_bytes()==saved and all(c[1]==c[2] for c in row['choices'])
                snap('reopened');key(0x7b)""")
needle="                # F6 stages the documented graphics mix; Apply uses the shared host resize."
assert source.count(needle)==1
source=source.replace(needle,'''                node_id='graphics.sprites.simba.cub.frames';select(node_id);key(0x48)
                row=wait(lambda r:r['modal']==1);selected=row['selected']
                scope=re.search(r'\\{"'+re.escape(node_id)+r'",[^\\n]*, "([^\\"]*)"\\}',(ROOT/'engine/runner/tlk_resources.c').read_text()).group(1)
                expected=node_id+'\\nPending choice: MD\\nApplied choice: MD\\n'+scope+'\\nUnsupported scenes use SNES.'
                checks['complete_scope_and_fallback']=row['help']==expected and row['pages']>1
                for page in range(row['pages']):
                    if page:key(0x22)
                    row=wait(lambda r:r['page']==page);snap('help-page-'+str(page))
                    checks['page-'+str(page)+'-independent-panel-pixels']=help_panel(folder/('help-page-'+str(page)+'.png'),expected,page)
                for _ in range(5):key(0x22)
                checks['last_page_clamp']=latest(trace)['page']==row['pages']-1
                for _ in range(5):key(0x21)
                row=latest(trace);checks['modal_navigation_keeps_tree']=row['page']==0 and row['selected']==selected and row['field']==1500 and row['help']==expected
                key(0x1b);key(0x48);row=wait(lambda r:r['modal']==1)
                checks['help_reopens_at_first_page']=row['page']==0 and row['help']==expected
                key(0x1b)
''' + needle)
helper='''def help_panel(path,text,page):
    # Independent 8x8 bitmap-font oracle for every pixel in the opaque modal.
    w,h,actual=pixels(path);assert h==448 and w in (512,640)
    font=(ROOT/'engine/runner/tlk_font8x8.h').read_text()
    glyphs=[[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',row)] for row in re.findall(r'\\{([^{}]+)\\}',font)]
    assert len(glyphs)==95
    lines=[]
    for paragraph in text.split('\\n'):
        if not paragraph:lines.append('')
        while paragraph:lines.append(paragraph[:30]);paragraph=paragraph[30:]
    expected=[(24,33,51)]*(248*122)
    def draw(x,y,label,color):
        for col,char in enumerate(label):
            for dy,bits in enumerate(glyphs[ord(char)-32]):
                for dx in range(8):
                    if bits & (1<<dx):expected[(y+dy)*248+x+col*8+dx]=color
    for i,label in enumerate(lines[page*9:(page+1)*9]):draw(4,6+i*10,label,(255,220,160))
    draw(4,100,'Up/Down: page '+str(page+1)+'/'+str((len(lines)+8)//9),(190,190,190))
    draw(4,110,'Enter/B: return',(190,190,190))
    offset=(w//2-256)//2
    return all(actual[(72*2+y*2+dy)*w+(offset+4+x)*2+dx]==expected[y*248+x]
               for y in range(122) for x in range(248) for dy in range(2) for dx in range(2))


'''
source=source.replace('def main():',helper+'def main():')
source=source.replace('paths=[Path(__file__),',"paths=[Path(__file__),original_verifier,ROOT/'engine/runner/tlk_resources.c',ROOT/'engine/runner/tlk_font8x8.h',")
exec(compile(source,str(original_verifier),'exec'))

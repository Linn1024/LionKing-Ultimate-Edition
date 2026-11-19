"""Compare unanchored vulture drawings; retain actual art/origin differences."""
from pathlib import Path
template=Path(__file__).with_name('audit_graveyard495_vultures.py')
s=template.read_text().replace('build/graveyard495-vultures','build/graveyard496-vultures')
s=s.replace('return {(x+i,y+j):data[j*w+i]', 'return {(i,j):data[j*w+i]')
exec(compile(s,str(template),'exec'))

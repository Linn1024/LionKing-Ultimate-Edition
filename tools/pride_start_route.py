"""Prepare a local controller route for the reviewed MD initial-position choice.

The MD default is one pixel farther right. Two brief releases in the first
walk, with three extra polls, put this route back on its intended terrain path.
Only controller words change; ROM, state and actor data are never modified.
The source recording remains local and retains its existing provenance.
"""
import struct


def prepare(source, destination):
    raw=source.read_bytes()
    assert len(raw)%2==0
    words=list(struct.unpack('<'+'H'*(len(raw)//2),raw))
    start=words.index(0x100)
    assert words[start:start+57]==[0x100]*57 and words[start+57]==0x8100,'Unexpected first-walk recording; provide an adapted route explicitly'
    replacement=[0x100,0,0x100,0x100,0]+[0x100]*55
    words[start:start+57]=replacement
    destination.write_bytes(struct.pack('<'+'H'*len(words),*words))
    return destination

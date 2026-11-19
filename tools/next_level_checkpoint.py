"""Use the native non-Pride checkpoint inside a research-only frontend wrapper.

This is fixture extraction, not a shipped development-save migration feature.
"""
import struct
def native_fixture(source,target,frame=24500):
    data=source.read_bytes()
    if data.startswith(b'TLKFSV01'):
        size=struct.unpack_from('<I',data,20)[0];data=data[96:96+size]
    assert data.startswith(b'TLKSTAT1')
    assert struct.unpack_from('<I',data,12)[0]==frame
    target.write_bytes(data);return target

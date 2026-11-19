"""Render installed menu assets for Windows-compositor comparison (32-bit)."""
import ctypes as C
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from md_lab import ROOT,png

package=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir()
dll=C.CDLL(str(ROOT/'build/pride-final-menu-scene/reader.dll'))
dll.TlkFinalArtLoad.argtypes=[C.c_void_p,C.c_size_t];dll.TlkFinalArtLoad.restype=C.c_void_p
dll.TlkFinalArtFree.argtypes=[C.c_void_p]
dll.TlkFinalArtDrawMenu.argtypes=[C.c_void_p,C.c_uint32,C.c_uint,C.c_uint,C.POINTER(C.c_uint32)]
raw=package.read_bytes();buffer=C.create_string_buffer(raw);art=dll.TlkFinalArtLoad(buffer,len(raw));assert art
pixels=(C.c_uint32*(320*224))()
try:
    for age in (118,140,160,220):
        assert dll.TlkFinalArtDrawMenu(art,age,1,0,pixels)
        png(out/(str(age)+'.png'),bytes(pixels),320,224,1280,1)
finally:dll.TlkFinalArtFree(art)

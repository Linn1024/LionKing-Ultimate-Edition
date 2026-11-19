"""Capture our Windows SDL client without moving the desktop mouse or focus."""
import ctypes as C
from ctypes import wintypes as W
from md_lab import png

USER=C.WinDLL('user32',use_last_error=True)
GDI=C.WinDLL('gdi32',use_last_error=True)
USER.GetClientRect.argtypes=[W.HWND,C.POINTER(W.RECT)]
USER.GetDC.argtypes=[W.HWND];USER.GetDC.restype=W.HDC
USER.PrintWindow.argtypes=[W.HWND,W.HDC,W.UINT]
USER.ReleaseDC.argtypes=[W.HWND,W.HDC]
GDI.CreateCompatibleDC.argtypes=[W.HDC];GDI.CreateCompatibleDC.restype=W.HDC
GDI.CreateCompatibleBitmap.argtypes=[W.HDC,C.c_int,C.c_int];GDI.CreateCompatibleBitmap.restype=W.HBITMAP
GDI.SelectObject.argtypes=[W.HDC,W.HGDIOBJ];GDI.SelectObject.restype=W.HGDIOBJ
GDI.GetDIBits.argtypes=[W.HDC,W.HBITMAP,W.UINT,W.UINT,C.c_void_p,C.c_void_p,W.UINT]
GDI.DeleteObject.argtypes=[W.HGDIOBJ];GDI.DeleteDC.argtypes=[W.HDC]


class Header(C.Structure):
    _fields_=[('size',W.DWORD),('width',W.LONG),('height',W.LONG),('planes',W.WORD),
              ('bits',W.WORD),('compression',W.DWORD),('bytes',W.DWORD),
              ('xppm',W.LONG),('yppm',W.LONG),('used',W.DWORD),('important',W.DWORD)]


def capture_client(hwnd,path):
    rectangle=W.RECT();assert USER.GetClientRect(hwnd,C.byref(rectangle))
    width,height=rectangle.right,rectangle.bottom
    dc=USER.GetDC(hwnd);assert dc
    memory=GDI.CreateCompatibleDC(dc);bitmap=GDI.CreateCompatibleBitmap(dc,width,height)
    assert memory and bitmap
    previous=GDI.SelectObject(memory,bitmap)
    try:
        # Client-only + full-content capture includes the real OpenGL presenter
        # even when another application covers this window.
        assert USER.PrintWindow(hwnd,memory,3),'PrintWindow failed'
        GDI.SelectObject(memory,previous)
        header=Header();header.size=C.sizeof(Header);header.width=width;header.height=-height
        header.planes=1;header.bits=32
        pixels=C.create_string_buffer(width*height*4)
        assert GDI.GetDIBits(memory,bitmap,0,height,pixels,C.byref(header),0)==height
        png(path,pixels.raw,width,height,width*4,1)
        return width,height
    finally:
        GDI.DeleteObject(bitmap);GDI.DeleteDC(memory);USER.ReleaseDC(hwnd,dc)

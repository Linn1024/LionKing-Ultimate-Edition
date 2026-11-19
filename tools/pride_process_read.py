"""Read-only observation of a child player's own exported/static data symbols."""
import ctypes as C
from ctypes import wintypes as W
import re
import struct
import subprocess
K=C.WinDLL('kernel32',use_last_error=True)
class Module(C.Structure):
    _fields_=[('size',W.DWORD),('id',W.DWORD),('pid',W.DWORD),('global_uses',W.DWORD),('process_uses',W.DWORD),
        ('base',C.c_void_p),('bytes',W.DWORD),('module',W.HMODULE),('name',W.WCHAR*256),('path',W.WCHAR*260)]
K.CreateToolhelp32Snapshot.argtypes=[W.DWORD,W.DWORD];K.CreateToolhelp32Snapshot.restype=W.HANDLE
K.Module32FirstW.argtypes=[W.HANDLE,C.POINTER(Module)];K.Module32FirstW.restype=W.BOOL
K.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];K.OpenProcess.restype=W.HANDLE
K.ReadProcessMemory.argtypes=[W.HANDLE,C.c_void_p,C.c_void_p,C.c_size_t,C.POINTER(C.c_size_t)];K.ReadProcessMemory.restype=W.BOOL
K.CloseHandle.argtypes=[W.HANDLE]
class PlayerRead:
    def __init__(self,binary,pid):
        raw=binary.read_bytes();pe=struct.unpack_from('<I',raw,60)[0];imagebase=struct.unpack_from('<I',raw,pe+24+28)[0]
        symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(binary)],creationflags=subprocess.CREATE_NO_WINDOW).decode()
        addresses={name:int(address,16)-imagebase for address,name in re.findall(r'^([0-9a-fA-F]+) [BbDd] (_\S+)\s*$',symbols,re.M)}
        snap=K.CreateToolhelp32Snapshot(0x18,pid);assert snap and snap!=C.c_void_p(-1).value
        try:
            module=Module();module.size=C.sizeof(module);assert K.Module32FirstW(snap,C.byref(module)),C.get_last_error()
            self.base=module.base
        finally:K.CloseHandle(snap)
        self.symbols=addresses;self.handle=K.OpenProcess(0x410,False,pid);assert self.handle,C.get_last_error()
    def read(self,address,size):
        data=C.create_string_buffer(size);used=C.c_size_t()
        assert K.ReadProcessMemory(self.handle,address,data,size,C.byref(used)) and used.value==size,C.get_last_error()
        return data.raw
    def value(self,name):return struct.unpack('<I',self.read(self.base+self.symbols['_'+name],4))[0]
    def snapshot(self):
        ram=self.base+self.symbols['_g_ram']
        word=lambda at:struct.unpack('<H',self.read(ram+at,2))[0]
        return dict(field=self.value('snes_frame_counter'),active=self.value('native_menu_active'),
            updates=self.value('native_menu_updates'),credits_art=self.value('native_menu_credits'),
            selected_no=self.value('native_menu_no'),confirmed=self.value('native_menu_confirmed'),
            art_mode=self.value('final_menu_art_mode'),transition_mode=self.value('continue_transition_mode'),
            credits_guest=word(0x1ffa8),health=word(0x2004),spares=word(0x1ffaa))
    def close(self):
        if self.handle:K.CloseHandle(self.handle);self.handle=None

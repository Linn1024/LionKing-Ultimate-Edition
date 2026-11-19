"""Read selected native guest words without suspending or writing the process."""
import ctypes as C,json,os,re,subprocess
from ctypes import wintypes as W
from pathlib import Path

def guest_words(exe,settings,addresses):
 ps=str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe')
 query="Get-Process LionKing | Where-Object { $_.Path -eq '"+str(exe)+"' } | Select-Object Id,@{n='Base';e={$_.MainModule.BaseAddress.ToInt64()}} | ConvertTo-Json -Compress"
 info=json.loads(subprocess.check_output([ps,'-NoProfile','-Command',query],text=True,creationflags=subprocess.CREATE_NO_WINDOW));assert isinstance(info,dict),'Expected one matching player'
 symbols=subprocess.check_output(['C:/mingw32/bin/nm.exe',str(exe)],text=True,creationflags=subprocess.CREATE_NO_WINDOW);symbol=re.search(r'^([0-9a-fA-F]+) B _g_ram$',symbols,re.M);assert symbol
 # PE32 optional header ImageBase, so ASLR and link layout are both respected.
 data=exe.read_bytes();pe=int.from_bytes(data[0x3c:0x40],'little');assert data[pe:pe+4]==b'PE\0\0' and data[pe+24:pe+26]==b'\x0b\x01';image_base=int.from_bytes(data[pe+52:pe+56],'little')
 k=C.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];k.OpenProcess.restype=W.HANDLE;k.ReadProcessMemory.argtypes=[W.HANDLE,C.c_void_p,C.c_void_p,C.c_size_t,C.POINTER(C.c_size_t)];k.CloseHandle.argtypes=[W.HANDLE]
 handle=k.OpenProcess(0x10,False,info['Id']);assert handle;buffer=C.create_string_buffer(0x20000);used=C.c_size_t()
 try:ok=k.ReadProcessMemory(handle,info['Base']+int(symbol[1],16)-image_base,buffer,len(buffer),C.byref(used))
 finally:k.CloseHandle(handle)
 assert ok and used.value==len(buffer),(C.get_last_error(),used.value)
 return {name:int.from_bytes(buffer.raw[p:p+2],'little') for name,p in addresses.items()}

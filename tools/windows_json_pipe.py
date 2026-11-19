"""Losslessly archive a child's JSONL diagnostic stream without a large raw file."""
import ctypes as C
from ctypes import wintypes as W
import gzip
import hashlib
import json
import os
import threading
import uuid

K=C.WinDLL('kernel32',use_last_error=True)
K.CreateNamedPipeW.argtypes=[W.LPCWSTR,W.DWORD,W.DWORD,W.DWORD,W.DWORD,W.DWORD,W.DWORD,C.c_void_p]
K.CreateNamedPipeW.restype=W.HANDLE
K.ConnectNamedPipe.argtypes=[W.HANDLE,C.c_void_p];K.ConnectNamedPipe.restype=W.BOOL
K.ReadFile.argtypes=[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p];K.ReadFile.restype=W.BOOL
K.CloseHandle.argtypes=[W.HANDLE]

class JsonPipe:
    def __init__(self,path):
        self.path=path;self.name='\\\\.\\pipe\\lionking-json-'+str(os.getpid())+'-'+uuid.uuid4().hex
        self.handle=K.CreateNamedPipeW(self.name,1,0,1,65536,65536,0,None)
        assert self.handle and self.handle!=C.c_void_p(-1).value,C.get_last_error()
        self.row=None;self.error=None;self.rows=0;self.bytes=0;self.sha=hashlib.sha256();self.lock=threading.Lock()
        self.thread=threading.Thread(target=self._run,daemon=True);self.thread.start()
    def _run(self):
        pending=b''
        try:
            connected=K.ConnectNamedPipe(self.handle,None)
            if not connected and C.get_last_error()!=535:raise OSError(C.get_last_error(),'ConnectNamedPipe')
            with gzip.open(self.path,'xb') as archive:
                buffer=C.create_string_buffer(65536)
                while True:
                    used=W.DWORD()
                    if not K.ReadFile(self.handle,buffer,len(buffer),C.byref(used),None):
                        if C.get_last_error()==109:break
                        raise OSError(C.get_last_error(),'ReadFile')
                    if not used.value:break
                    data=buffer.raw[:used.value];archive.write(data);self.sha.update(data);self.bytes+=len(data)
                    pending+=data
                    lines=pending.split(b'\n');pending=lines.pop()
                    for line in lines:
                        if not line:continue
                        row=json.loads(line)
                        with self.lock:self.row=row;self.rows+=1
                if pending:raise ValueError('Incomplete final JSONL record')
        except BaseException as error:self.error=repr(error)
        finally:K.CloseHandle(self.handle)
    def latest(self):
        if self.error:raise RuntimeError(self.error)
        with self.lock:return self.row
    def finish(self):
        self.thread.join(10)
        assert not self.thread.is_alive(),'Child diagnostic pipe did not close'
        assert self.error is None,self.error
        return dict(rows=self.rows,uncompressed_bytes=self.bytes,uncompressed_sha256=self.sha.hexdigest())

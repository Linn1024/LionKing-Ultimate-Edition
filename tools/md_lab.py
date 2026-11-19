"""Local ROM research with the pinned, locally-built 32-bit MD reference core.

Run using .tools/python32/python.exe. Captures are local build artifacts.
"""
from pathlib import Path
import argparse
import ctypes as C
import json
import struct
import wave
import zlib

ROOT = Path(__file__).resolve().parents[1]

def png(path, data, width, height, pitch, fmt):
    rgb=bytearray()
    for y in range(height):
        rgb.append(0)
        for x in range(width):
            n=4 if fmt==1 else 2
            v=int.from_bytes(data[y*pitch+x*n:y*pitch+(x+1)*n], 'little')
            if fmt==1: color=((v>>16)&255,(v>>8)&255,v&255)
            elif fmt==2: color=(((v>>11)&31)*255//31,((v>>5)&63)*255//63,(v&31)*255//31)
            else: color=(((v>>10)&31)*255//31,((v>>5)&31)*255//31,(v&31)*255//31)
            rgb.extend(color)
    def chunk(name,value):
        return struct.pack('>I',len(value))+name+value+struct.pack('>I',zlib.crc32(name+value))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+
                     chunk(b'IDAT',zlib.compress(rgb))+chunk(b'IEND',b''))

class GameInfo(C.Structure):
    _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
class Variable(C.Structure):
    _fields_=[('key',C.c_char_p),('value',C.c_char_p)]
class Timing(C.Structure):
    _fields_=[('fps',C.c_double),('sample_rate',C.c_double)]
class Geometry(C.Structure):
    _fields_=[('base_width',C.c_uint),('base_height',C.c_uint),('max_width',C.c_uint),('max_height',C.c_uint),('aspect_ratio',C.c_float)]
class AVInfo(C.Structure):
    _fields_=[('geometry',Geometry),('timing',Timing)]

class MdLab:
    def __init__(self):
        self.core=C.CDLL(str(ROOT/'.tools/genesis-plus-gx/genesis_plus_gx_libretro.dll'))
        self.frame=0; self.pad=0; self.fmt=0; self.image=None; self.samples=bytearray(); self.defaults={}
        self.directory=str(ROOT/'build/md-lab').encode(); self.refs=[]
        def env(cmd,p):
            if cmd==10: self.fmt=C.cast(p,C.POINTER(C.c_int))[0]; return True
            if cmd==16:
                v=C.cast(p,C.POINTER(Variable)); i=0
                while v[i].key:
                    self.defaults[v[i].key]=v[i].value.split(b'; ',1)[-1].split(b'|')[0]; i+=1
                return True
            if cmd==15:
                v=C.cast(p,C.POINTER(Variable))
                if v[0].key in self.defaults: v[0].value=self.defaults[v[0].key]; return True
                return False
            if cmd==17: C.cast(p,C.POINTER(C.c_bool))[0]=False; return True
            if cmd in (9,31): C.cast(p,C.POINTER(C.c_char_p))[0]=self.directory; return True
            if cmd in (3,18): C.cast(p,C.POINTER(C.c_bool))[0]=cmd==18; return True
            return False
        def video(p,w,h,pitch):
            if p and p!=C.c_void_p(-1).value: self.image=(C.string_at(p,pitch*h),w,h,pitch,self.fmt)
        def audio(p,n): self.samples.extend(C.string_at(p,n*4)); return n
        def input_state(port,device,index,button): return int(port==0 and bool(self.pad&(1<<button)))
        def bind(name,ret,args,fn):
            cb=C.CFUNCTYPE(ret,*args)(fn); self.refs.append(cb); getattr(self.core,'retro_set_'+name)(cb)
        bind('environment',C.c_bool,[C.c_uint,C.c_void_p],env)
        bind('video_refresh',None,[C.c_void_p,C.c_uint,C.c_uint,C.c_size_t],video)
        bind('audio_sample',None,[C.c_int16,C.c_int16],lambda l,r:None)
        bind('audio_sample_batch',C.c_size_t,[C.c_void_p,C.c_size_t],audio)
        bind('input_poll',None,[],lambda:None)
        bind('input_state',C.c_int16,[C.c_uint]*4,input_state)
        self.core.retro_init()
        self.rom=C.create_string_buffer((ROOT/'Lion King, The (World).md').read_bytes())
        info=GameInfo(b'Lion King, The (World).md',C.cast(self.rom,C.c_void_p),len(self.rom)-1,None)
        self.core.retro_load_game.argtypes=[C.POINTER(GameInfo)]; self.core.retro_load_game.restype=C.c_bool
        if not self.core.retro_load_game(C.byref(info)): raise RuntimeError('ROM rejected')
        self.av=AVInfo(); self.core.retro_get_system_av_info(C.byref(self.av))
        for name,n in [('work_ram',65536),('zram',8192),('vram',65536),('cram',128),('reg',32),('vsram',128)]:
            setattr(self,name,(C.c_ubyte*n).in_dll(self.core,name))
        self.core.m68k_get_reg.argtypes=[C.c_int]; self.core.m68k_get_reg.restype=C.c_uint
        self.core.m68k_set_reg.argtypes=[C.c_int,C.c_uint]
    def step(self,pad=0):
        self.pad=pad; self.core.retro_run(); self.frame+=1
    def write_code(self,address,code):
        assert len(code)%2==0
        for i in range(0,len(code),2):
            self.work_ram[address+i]=code[i+1]; self.work_ram[address+i+1]=code[i]
    def driver_step(self,command=None,value=0):
        code=bytearray()
        if command is not None:
            code.extend(bytes.fromhex('303c')+struct.pack('>H',value&65535)+bytes((0x7e,command))+bytes.fromhex('4eb9002d0000'))
        code.extend(bytes.fromhex('7e004eb9002d000060fe'))
        self.write_code(0xfe00,code)
        self.core.m68k_set_reg(17,0x2700)
        self.core.m68k_set_reg(15,0xfffd00)
        self.core.m68k_set_reg(16,0xfffe00)
        self.step()
    def dump(self,directory):
        directory.mkdir(parents=True,exist_ok=True)
        for name in ('work_ram','zram','vram','cram','reg','vsram'):
            (directory/(name+'.bin')).write_bytes(bytes(getattr(self,name)))
        if self.image: png(directory/'screen.png',*self.image)
        self.core.retro_serialize_size.restype=C.c_size_t
        size=self.core.retro_serialize_size(); state=C.create_string_buffer(size)
        self.core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]; self.core.retro_serialize.restype=C.c_bool
        if self.core.retro_serialize(state,size): (directory/'game.state').write_bytes(state.raw)
        with wave.open(str(directory/'audio.wav'),'wb') as wav:
            wav.setnchannels(2); wav.setsampwidth(2); wav.setframerate(round(self.av.timing.sample_rate)); wav.writeframes(self.samples)
        summary={'frame':self.frame,'width':self.image[1], 'height':self.image[2], 'vdp_register_12':self.reg[12],
                 'fps':self.av.timing.fps,'sample_rate':self.av.timing.sample_rate,'pc':hex(self.core.m68k_get_reg(16))}
        (directory/'info.json').write_text(json.dumps(summary,indent=2)); print(summary)
    def close(self): self.core.retro_unload_game(); self.core.retro_deinit()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--frames',type=int,default=1800)
    ap.add_argument('--out',type=Path,default=ROOT/'build/md-lab')
    ap.add_argument('--load',type=Path)
    ap.add_argument('--trace',action='store_true')
    ap.add_argument('--driver-pattern',type=lambda s:int(s,0))
    ap.add_argument('--driver-effect',type=lambda s:int(s,0),choices=range(128))
    args=ap.parse_args(); game=MdLab()
    trace=None
    if args.trace:
        args.out.mkdir(parents=True,exist_ok=True)
        trace=C.CDLL(str(ROOT/'build/md_trace.dll'))
        trace.md_trace_init.argtypes=[C.c_void_p,C.c_char_p]
        assert trace.md_trace_init(game.core._handle,str(args.out/'sound-writes.csv').encode())
    if args.load:
        buf=C.create_string_buffer(args.load.read_bytes())
        game.core.retro_unserialize.argtypes=[C.c_void_p,C.c_size_t]; game.core.retro_unserialize.restype=C.c_bool
        assert game.core.retro_unserialize(buf,len(buf)-1)
    standalone=args.driver_pattern is not None or args.driver_effect is not None
    if standalone:
        if not args.load:
            for n in range(180): game.step()
        game.driver_step(1,args.driver_pattern if args.driver_pattern is not None else 0)
        if args.driver_effect is not None: game.driver_step(2,args.driver_effect)
        game.samples.clear()
    for n in range(args.frames):
        if trace: trace.md_trace_frame(n)
        if standalone: game.driver_step()
        else: game.step((1<<3) if not args.load and 200<n<1500 and n%90<3 else 0)
    if trace: trace.md_trace_close()
    game.dump(args.out); game.close()

if __name__=='__main__': main()

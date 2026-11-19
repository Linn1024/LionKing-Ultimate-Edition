"""Capture a local Mega Drive reference with an installed libretro core.

This is a research tool, not the PC game's runtime. No core or ROM is bundled.
"""
from pathlib import Path
import ctypes as C
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--core',type=Path,required=True)
    ap.add_argument('--frames',type=int,default=1000)
    args=ap.parse_args()
    core=C.CDLL(str(args.core.resolve()))
    env_t=C.CFUNCTYPE(C.c_bool,C.c_uint,C.c_void_p)
    video_t=C.CFUNCTYPE(None,C.c_void_p,C.c_uint,C.c_uint,C.c_size_t)
    sample_t=C.CFUNCTYPE(None,C.c_int16,C.c_int16)
    batch_t=C.CFUNCTYPE(C.c_size_t,C.c_void_p,C.c_size_t)
    poll_t=C.CFUNCTYPE(None)
    input_t=C.CFUNCTYPE(C.c_int16,C.c_uint,C.c_uint,C.c_uint,C.c_uint)
    class Info(C.Structure):
        _fields_=[('path',C.c_char_p),('data',C.c_void_p),('size',C.c_size_t),('meta',C.c_char_p)]
    class Var(C.Structure):
        _fields_=[('key',C.c_char_p),('value',C.c_char_p)]
    variables={}; strings=[]; pixel_format=0; last=None; frame=0
    @env_t
    def env(cmd,data):
        nonlocal pixel_format
        if cmd==10:
            pixel_format=C.cast(data,C.POINTER(C.c_int))[0]; return True
        if cmd==16:
            p=C.cast(data,C.POINTER(Var)); n=0
            while p[n].key:
                default=p[n].value.split(b'; ',1)[-1].split(b'|')[0]
                variables[p[n].key]=default; n+=1
            return True
        if cmd==15:
            p=C.cast(data,C.POINTER(Var)); key=p[0].key
            if key in variables: p[0].value=variables[key]; return True
            return False
        if cmd==17: C.cast(data,C.POINTER(C.c_bool))[0]=False; return True
        if cmd in (9,31):
            b=str(ROOT / 'build/reference').encode(); strings.append(b)
            C.cast(data,C.POINTER(C.c_char_p))[0]=b; return True
        if cmd==3: C.cast(data,C.POINTER(C.c_bool))[0]=False; return True
        if cmd in (18,): C.cast(data,C.POINTER(C.c_bool))[0]=True; return True
        return False
    @video_t
    def video(data,w,h,pitch):
        nonlocal last
        if data and data != C.c_void_p(-1).value: last=(C.string_at(data,pitch*h),w,h,pitch,pixel_format)
    @sample_t
    def sample(l,r): pass
    @batch_t
    def batch(p,n): return n
    @poll_t
    def poll(): pass
    @input_t
    def inp(port,device,index,id):
        # Start taps through the logos, title, and game intro.
        return int(port==0 and id==3 and frame>200 and frame<1500 and frame%90<3)
    callbacks=[('environment',env),('video_refresh',video),('audio_sample',sample),
               ('audio_sample_batch',batch),('input_poll',poll),('input_state',inp)]
    for name,cb in callbacks: getattr(core,'retro_set_'+name)(cb)
    core.retro_init()
    path=ROOT/'Lion King, The (World).md'
    buf=C.create_string_buffer(path.read_bytes())
    info=Info(str(path).encode(),C.cast(buf,C.c_void_p),len(buf)-1,None)
    core.retro_load_game.argtypes=[C.POINTER(Info)]; core.retro_load_game.restype=C.c_bool
    if not core.retro_load_game(C.byref(info)): raise RuntimeError('core rejected ROM')
    dest=ROOT/'build/reference'; dest.mkdir(parents=True,exist_ok=True)
    from PIL import Image
    for frame in range(args.frames):
        core.retro_run()
        if last and (frame+1)%200==0:
            raw,w,h,pitch,fmt=last
            rgb=bytearray()
            for y in range(h):
                for x in range(w):
                    bpp=4 if fmt==1 else 2
                    v=int.from_bytes(raw[y*pitch+x*bpp:y*pitch+(x+1)*bpp],'little')
                    if fmt==1: c=((v>>16)&255,(v>>8)&255,v&255)
                    elif fmt==2: c=(((v>>11)&31)*255//31,((v>>5)&63)*255//63,(v&31)*255//31)
                    else: c=(((v>>10)&31)*255//31,((v>>5)&31)*255//31,(v&31)*255//31)
                    rgb.extend(c)
            Image.frombytes('RGB',(w,h),bytes(rgb)).save(dest/f'md-{frame+1}.png')
    core.retro_serialize_size.restype=C.c_size_t
    size=core.retro_serialize_size(); state=C.create_string_buffer(size)
    core.retro_serialize.argtypes=[C.c_void_p,C.c_size_t]; core.retro_serialize.restype=C.c_bool
    if core.retro_serialize(state,size):
        (dest/'md.state').write_bytes(state.raw)
        print('saved reference state',size)
    core.retro_unload_game(); core.retro_deinit()

if __name__=='__main__': main()

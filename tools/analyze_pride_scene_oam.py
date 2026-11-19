"""Compare native raster OAM/CHR data with recorded semantic pieces."""
import hashlib
import json
from pathlib import Path
import struct
from audit_scenes import ROOT
from verify_windows import hashes


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def records(path):
    with path.open('rb') as f:
        assert f.read(8)==b'PROAM001'
        version,heads,states,lines,ram_size,vram_size,piece_words=struct.unpack('<7I',f.read(28))
        assert (version,heads,states,lines,ram_size,vram_size,piece_words)==(1,32,8,224,131072,262144,14)
        while raw:=f.read(128):
            head=struct.unpack('<32I',raw);ram=f.read(ram_size);endram=f.read(ram_size);vram=f.read(vram_size)
            raster=[]
            for _ in range(lines):
                state=struct.unpack('<8I',f.read(32));oam=f.read(544);cgram=f.read(512)
                raster.append((state,oam,cgram))
            pieces=[struct.unpack('<14i',f.read(56)) for _ in range(head[4])]
            yield dict(head=head,ram=ram,endram=endram,vram=vram,raster=raster,pieces=pieces)


def slot_data(record):
    state,raw,_=record['raster'][0];oam=struct.unpack('<256H',raw[:512]);high=raw[512:]
    vr=record['vram'][state[7]*65536:(state[7]+1)*65536]
    result=[]
    sizes=((8,16),(8,32),(8,64),(16,32),(16,64),(32,64),(16,32),(16,32))
    for i in range(128):
        xy,attr=oam[i*2:i*2+2]
        x=(xy&255)|((high[i//4]>>((i%4)*2)&1)<<8);x=x-512 if x>=256 else x
        y=xy>>8;size=sizes[state[1]>>5][high[i//4]>>((i%4)*2+1)&1]
        base=(state[1]&7)<<13
        if attr&256:base+=((state[1]&0x18)+8)<<9
        shape=bytearray()
        for dy in range(0,size,8):
            for dx in range(0,size,8):
                tile=((((attr&255)>>4)+dy//8)<<4)|(((attr&15)+dx//8)&15)
                start=((base+tile*16)&32767)*2
                shape+=vr[start:start+32] if start+32<=65536 else vr[start:]+vr[:start+32-65536]
        intersects=x+size>0 and x<256 and any(((line-y)&255)<size for line in range(224))
        result.append(dict(slot=i,x=x,y=y,size=size,attr=attr,intersects_view=intersects,
            nonempty_tiles=any(shape),signature=hashlib.sha256(struct.pack('<iiII',x,y,size,attr)+shape).hexdigest()))
    return result


def main():
    folder=ROOT/'build/pride-scene-oam-audit/native'
    capture=json.loads((folder/'capture.json').read_text());assert capture['completed']
    assert capture['exe_sha256']==digest(ROOT/'engine/build-win/tlk_scene_oam_probe.exe')
    baseline=ROOT/'build/pride-scene-restore-headless/native-canonical'
    assert hashes(folder/'run.log')==hashes(baseline/'run.log')
    assert digest(folder/'route.ram')==digest(baseline/'route.ram')
    all_records={r['head'][1]:r for r in records(folder/'native-oam.bin')};assert set(all_records)==set(range(240,361))
    source=all_records[268];source_slots=slot_data(source);output=[]
    for age,r in all_records.items():
        h=r['head'];state,raw,_=r['raster'][0];slots=slot_data(r)
        matching=[];recoverable=[]
        for p in r['pieces']:
            s=slots[p[5]&127]
            if p[6] and (s['x'],s['y'],s['size'],s['attr'])==(p[0],p[1]&255,p[4],p[2]):matching.append(p[5]&127)
        for p in source['pieces']:
            slot=p[5]&127
            original=source_slots[slot]
            if p[6] and (original['x'],original['y'],original['size'],original['attr'])==(p[0],p[1]&255,p[4],p[2]) and slots[slot]['signature']==original['signature']:recoverable.append(slot)
        oam_uniform=all(x[1]==raw for x in r['raster'])
        row=dict(age=age,field=h[0],latch=h[3],recorded=h[4],hud_slots=h[5],health=h[9],roar=h[10],
            inidisp=state[0],raw_oam_sha256=hashlib.sha256(raw).hexdigest(),oam_same_all224_lines=oam_uniform,
            intersecting_nonempty_slots=[s['slot'] for s in slots if s['intersects_view'] and s['nonempty_tiles']],
            matching_recorded_slots=matching,recoverable268_slots=recoverable,
            slots=slots)
        output.append(row)
    (folder/'analysis.json').write_text(json.dumps(output,indent=2)+'\n')
    for age in (254,268,269,270,273,291,297,298,345,346):
        r=next(x for x in output if x['age']==age)
        print(age,'pieces',r['recorded'],'nonempty-intersect',len(r['intersecting_nonempty_slots']),
              'matching',len(r['matching_recorded_slots']),'recoverable268',len(r['recoverable268_slots']),r['raw_oam_sha256'][:12],flush=True)
    (ROOT/'build/pride-scene-oam-audit/report.json').write_text(json.dumps(dict(result='AUDITED',scope=__doc__,
        fields=len(output),read_only_guest_and_full_tracked_ram_exact=True,
        source_sha256={'script':digest(Path(__file__)),'probe':digest(ROOT/'tools/pride_scene_oam_audit.c'),
                       'binary':capture['exe_sha256']},
        artifacts_sha256={'raw':digest(folder/'native-oam.bin'),'analysis':digest(folder/'analysis.json')},
        full_first_level_fidelity_complete=False),indent=2)+'\n')


if __name__=='__main__':main()

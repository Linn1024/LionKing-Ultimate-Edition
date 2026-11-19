"""Verify115 reviewed late actor links from installed buffers, guards and prior-data preservation."""
from pathlib import Path
template=Path(__file__).with_name('check_hakuna825_prepared.py');s=template.read_text().replace('build/hakuna825-prepared','build/later884-prepared').replace('build/hakuna823/build-report.json','build/later883/build-report.json').replace('build/hakuna822-helper','build/later882-helper')
a=s.index(' /* Frog death');b=s.index(' FILE *ok=',a)
s=s[:a]+''' /* Unknown banks stay unavailable; normal adult colors are scene-owned. */
 TlkMdSpritesNextScene(7);if(TlkNextSceneNativeObj(7,1))return 6;
 if(!TlkNextSceneNativeObj(7,6)||!TlkNextSceneNativeObj(8,6))return 7;
 if(TlkNextSceneNativeObj(8,2)||TlkNextSceneMdPalette(9))return 8;
 memset(colors,0,sizeof colors);memcpy(colors+224,TlkNextSceneNativeObj(7,6),32);
 pose=0xc62e83;if(!TlkMdSpritesBounds(pose,&bx,&by,&w,&h))return 9;
 int found=0,sx=0,sy=0;unsigned short c=0;
 for(int y=by;y<by+h && !found;y++)for(int x=bx;x<bx+w;x++)if(TlkMdSpritesNpcSample(pose,x,y,0,1,1,colors,&c)==1){found=1;sx=x;sy=y;break;}
 if(!found)return 10;colors[225]^=1;
 if(TlkMdSpritesNpcSample(pose,sx,sy,0,1,1,colors,&c)!=-1)return 11;
'''+s[b:]
s=s.replace("ROOT/'tools/hakuna_destiny_actor_pairs.json'", "ROOT/'tools/later_actor_pairs.json'").replace("gorilla=json.loads((ROOT/'tools/hakuna_gorilla_pairs.json').read_text())['pairs']", "gorilla=[]")
s=s.replace("ROOT/'build/hakuna801-helper/sprites.assets'", "ROOT/'build/hakuna822-helper/sprites.assets'")
anchor="checks.update(unrelated_images_preserved=";a=s.index(anchor);b=s.index('\npaths=',a)
s=s[:a]+'''def sections(g):
 assert struct.unpack_from('<I',g,8)[0]==3;sizes=struct.unpack_from('<6I',g,16);at=40;result=[]
 for size in sizes:result.append(g[at:at+size]);at+=size
 assert at==len(g);return result
previous=sections(og);current=sections(ng)
checks.update(unrelated_images_preserved=all(ni[k]==v for k,v in oi.items() if k not in changed),first_five_gameplay_sections_preserved=previous[:5]==current[:5],previous896_scene_words_preserved=previous[5][16:]==current[5][16:16+896*2],new_scene_schema=current[5][:8]==b'TLKNXT03' and len(current[5])==2576,shared_palettes_and_death_bank_preserved=old[192:18400]==new[192:18400],images1253=len(ni)==1253)
'''+s[b:]
exec(compile(s,str(template),'exec'))

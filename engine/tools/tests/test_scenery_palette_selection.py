"""Compile the real editor/colour collector with deterministic host inputs.

No ROM, SDL, ImGui or generated game code is needed. Run with unittest or pytest.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


HARNESS = r'''
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
#define CHECK(x) do { if(!(x)) { fprintf(stderr,"line %d: %s\n",__LINE__,#x); return 1; } } while(0)
struct SDL_Texture {}; struct SDL_Renderer {};
using ImTextureID=uintptr_t;
struct ImVec2 { float x,y; ImVec2(float x=0,float y=0):x(x),y(y){} };
struct ImVec4 { float x,y,z,w; ImVec4(float x,float y,float z,float w):x(x),y(y),z(z),w(w){} };
enum { SDL_PIXELFORMAT_XRGB8888,SDL_TEXTUREACCESS_STATIC,SDL_SCALEMODE_NEAREST,
       ImGuiChildFlags_Borders,ImGuiColorEditFlags_NoTooltip,ImGuiColorEditFlags_NoInputs };
#define IM_COL32(...) 0
void SDL_DestroyTexture(SDL_Texture*) {}
SDL_Texture *SDL_CreateTexture(SDL_Renderer*,int,int,int,int) { return nullptr; }
void SDL_SetTextureScaleMode(SDL_Texture*,int) {}
void SDL_UpdateTexture(SDL_Texture*,void*,const void*,int) {}
static int click=-1,grid_index=0,next_target=-1,notices=0;
static bool edit=false,reset=false;
namespace ImGui {
struct DrawList { void AddRect(ImVec2,ImVec2,int,int,int,int) {} } draw;
bool CollapsingHeader(const char*) { grid_index=0; return true; }
void TextWrapped(const char *s) { if(strstr(s,"not in the current"))notices++; }
bool Combo(const char*,int *target,const char**,int) {
 if(next_target<0)return false; *target=next_target;next_target=-1;return true;
}
void BeginChild(const char*,ImVec2,int) {} void EndChild() {}
void PushID(int) {} void PopID() {} void SameLine() {}
bool ColorButton(const char *id,ImVec4,int,ImVec2) {
 if(strcmp(id,"##shade"))return false;
 return grid_index++==click;
}
DrawList *GetWindowDrawList(){return &draw;}
ImVec2 GetItemRectMin(){return {}; } ImVec2 GetItemRectMax(){return {}; }
bool IsItemHovered(){return false;} void SetTooltip(const char*){}
bool ColorEdit3(const char*,float *v,int){v[0]=1;v[1]=v[2]=0;return edit;}
bool Button(const char *s){return reset&&!strcmp(s,"Reset this shade");}
void TextUnformatted(const char*){} ImVec2 GetContentRegionAvail(){return {800,600};}
void Image(ImTextureID,ImVec2){}
}
struct TlkResourceNode { const char *id; } nodes[]={
 {"graphics.scenery.background.palette"},{"graphics.scenery.foreground.palette"},
 {"graphics.sprites.simba.cub.palette"}};
const TlkResourceNode *TlkResourcesNode(int n){return n>=0&&n<3?nodes+n:nullptr;}
int TlkResourcesFind(const char *s){for(int i=0;i<3;i++)if(!strcmp(s,nodes[i].id))return i;return -1;}
#include "tlk_palette_editor.inc"
// Only the host file/resource APIs are substituted; preset parsing is production code.
static std::map<std::string,std::string> files;
struct SDL_PathInfo { size_t size; };
const char *SDL_getenv(const char*){return nullptr;}
char *SDL_GetPrefPath(const char*,const char*){return nullptr;}
void SDL_free(void *p){free(p);}
bool SDL_GetPathInfo(const char *p,SDL_PathInfo *info){
 auto it=files.find(p);if(it==files.end())return false;info->size=it->second.size();return true;
}
void *SDL_LoadFile(const char *p,size_t *size){
 auto it=files.find(p);if(it==files.end())return nullptr;*size=it->second.size();
 void *result=malloc(*size);memcpy(result,it->second.data(),*size);return result;
}
bool SDL_SaveFile(const char *p,const void *v,size_t size){files[p]=std::string((const char*)v,size);return true;}
bool SDL_RenamePath(const char *a,const char *b){files[b]=files.at(a);files.erase(a);return true;}
bool SDL_RemovePath(const char *p){files.erase(p);return true;}
bool SDL_CreateDirectory(const char*){return true;}
uint64_t SDL_GetTicksNS(){return 1;}
char **SDL_GlobDirectory(const char*,const char*,int,int *count){*count=0;return nullptr;}
static int choices[3]={1,0,0};
int TlkResourcesCount(){return 3;}
int TlkResourcesChoice(int i,int){return choices[i];}
int TlkResourcesSet(int i,int v){choices[i]=v;return 1;}
int TlkResourcesValidate(char*,size_t){return 0;}
#include "tlk_browser_presets.h"
static unsigned frame_level=1;
unsigned TlkWideFrameLevel(){return frame_level;} bool TlkWideFrameStageActive(){return true;}
bool TlkWidePreview(uint32_t*,int){return false;}
struct Line { uint16_t cgram[256]={}; } line;
struct { bool stage=true; } s_frame;
static uint32_t s_sprite_colour_seen[1024]={};
static unsigned s_md_level=1;
static int s_cw_scene=0,s_scenery_palette[2]={},external_source=0;
static uint16_t s_cw_external[2][64]={},s_cw_native_mapped[2][128]={},md_colours[64]={};
const Line *WorldPresentationLine(int){return &line;}
int TlkResourcesUseMd(const char*){return external_source;}
int TlkMdScenePaletteColors(unsigned,uint16_t *out){std::copy(md_colours,md_colours+64,out);return 1;}
unsigned TlkMdSceneModeColor(unsigned,int,unsigned c,int){return c;}
// COLLECTOR
#include "tlk_browser_palette_editor.h"
void palette(std::initializer_list<uint16_t> shades) {
 std::fill(line.cgram,line.cgram+256,*shades.begin());
 std::copy(shades.begin(),shades.end(),line.cgram);
}
int main(int argc,char **argv) {
 if(argc!=2)return 2;std::string mode=argv[1];
 BrowserPaletteEditor e;palette({1,2,3});click=1;e.Draw(nullptr,0);click=-1;
 if(mode=="source") {
  std::fill(md_colours,md_colours+64,3);md_colours[1]=1;md_colours[2]=2;external_source=1;
 } else if(mode=="dedup")palette({2,2,3});
 else if(mode=="reorder")palette({3,1,2});
 else if(mode=="absent")palette({1,4,3});
 else if(mode=="shrink")palette({1});
 else if(mode=="animation") {
  s_cw_scene=1;std::fill(s_cw_native_mapped[1],s_cw_native_mapped[1]+128,4);
  s_cw_native_mapped[1][1]=5;
 } else if(mode=="empty") {
  s_frame.stage=false;e.Draw(nullptr,0);CHECK(palette_count[1]==0);s_frame.stage=true;palette({3,1,2});
 } else if(mode=="level") { frame_level=2;palette({7,8}); }
 else if(mode=="layer") { next_target=0;palette({7,8}); }
 else if(mode=="node") { palette({7,8}); }
 else if(mode!="presets"&&mode!="reset")return 2;
 if(mode=="reset") { TlkResourcesPaletteSet(1,1,2,17);palette({3,1,2});reset=true; }
 else edit=true;
 e.Draw(nullptr,mode=="node"?1:0);edit=reset=false;
 if(mode=="reset") {CHECK(palette_count[1]==0);return 0;}
 int entry[4];CHECK(TlkResourcesPaletteEntry(0,1,entry));
 CHECK(entry[0]==(mode=="level"?2:1));
 CHECK(entry[1]==(mode=="layer"||mode=="node"?0:1));
 CHECK(entry[2]==(mode=="level"||mode=="layer"||mode=="node"?7:2));
 CHECK(entry[3]==31);
 if(mode=="absent"||mode=="shrink"||mode=="animation")CHECK(notices>0);
 if(mode=="presets") {
  // Actual production codec and transaction code; both sprite sources remain independent.
  CHECK(TlkResourcesPaletteSet(14,5,2,12));CHECK(TlkResourcesPaletteSet(14,5,32770,13));
  FILE *f=tmpfile();CHECK(f);CHECK(PaletteWrite(f));rewind(f);
  char text[1024]={};size_t bytes=fread(text,1,sizeof text-1,f);fclose(f);CHECK(bytes>0);
  CHECK(strstr(text,"colour.1.1.0002 = 001f\n"));
  CHECK(strstr(text,"sprite_colour.graphics.sprites.simba.cub.palette.snes.0002 = 000c\n"));
  CHECK(strstr(text,"sprite_colour.graphics.sprites.simba.cub.palette.md.0002 = 000d\n"));
  TlkResourcesPaletteReset(-1,-1);
  char *row=strtok(text,"\n");while(row){char id[256],value[32];CHECK(sscanf(row,"%255s = %31s",id,value)==2);CHECK(PaletteParse(id,value)==1);row=strtok(nullptr,"\n");}
  CHECK(palette_count[1]==3);PaletteCommit();CHECK(!PaletteDirty());
  CHECK(TlkResourcesPaletteMap(1,1,2)==31);CHECK(TlkResourcesPaletteMap(1,1,3)==3);
  CHECK(TlkResourcesSpritePaletteMap(2,0,2)==12);CHECK(TlkResourcesSpritePaletteMap(2,1,2)==13);
  TlkResourcesPaletteSet(1,1,2,19);CHECK(PaletteDirty());PaletteRevert();CHECK(!PaletteDirty());
  TlkResourcesPalettePreview(1);CHECK(TlkResourcesPaletteMap(1,1,2)==31);TlkResourcesPalettePreview(0);
  std::string message;
  CHECK(BrowserPresets::Save("presets","Roundtrip",message));
  const auto saved=BrowserPresets::Choices();
  TlkResourcesPaletteReset(-1,-1);CHECK(BrowserPresets::Load("presets","Roundtrip",message));
  CHECK(BrowserPresets::Choices()==saved);
  // Literal schema-1 fixture from the pre-patch format, including both sprite sources.
  files["presets/Legacy.ini"]="schema = 1\n"
   "graphics.scenery.background.palette = snes\n"
   "graphics.scenery.foreground.palette = inherit\n"
   "graphics.sprites.simba.cub.palette = md\n"
   "colour.1.1.0002 = 001e\n"
   "sprite_colour.graphics.sprites.simba.cub.palette.snes.0002 = 000c\n"
   "sprite_colour.graphics.sprites.simba.cub.palette.md.0002 = 000d\n";
  CHECK(BrowserPresets::Load("presets","Legacy",message));
  CHECK(choices[2]==2);CHECK(palette_count[1]==3);
  TlkResourcesPalettePreview(1);
  CHECK(TlkResourcesPaletteMap(1,1,2)==30);
  CHECK(TlkResourcesSpritePaletteMap(2,0,2)==12);CHECK(TlkResourcesSpritePaletteMap(2,1,2)==13);
  TlkResourcesPalettePreview(0);
  // Loading a draft preset must not overwrite the active profile.
  CHECK(TlkResourcesPaletteMap(1,1,2)==31);CHECK(PaletteDirty());
  CHECK(BrowserPresets::Save("presets","Legacy copy",message));
  CHECK(files["presets/Legacy copy.ini"].find("colour.1.1.0002 = 001e\n")!=std::string::npos);
  PaletteRevert();CHECK(!PaletteDirty());
 }
 return 0;
}
'''


class SceneryPaletteSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("c++")
        if not compiler:
            raise unittest.SkipTest("C++ compiler required")
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        work = Path(cls.temp.name)
        runner = Path(__file__).resolve().parents[2] / "runner"
        # Copy the exact production editor; replace only its platform dependencies.
        shutil.copyfile(runner / "tlk_browser_palette_editor.h", work / "tlk_browser_palette_editor.h")
        shutil.copyfile(runner / "tlk_palette_editor.inc", work / "tlk_palette_editor.inc")
        shutil.copyfile(runner / "tlk_browser_presets.h", work / "tlk_browser_presets.h")
        (work / "tlk_wide.h").write_text("")
        (work / "tlk_browser_sprite_colours.h").write_text(
            "struct BrowserSpriteColours { int owner=-1; void Clear(){} "
            "void Draw(SDL_Renderer*,int){} };\n")
        source = (runner / "tlk_wide.c").read_text()
        collector = source[source.index("int TlkWidePaletteColors("):]
        # Isolate this function if more code is added below it later.
        depth = 0
        for i in range(collector.index("{"), len(collector)):
            depth += (collector[i] == "{") - (collector[i] == "}")
            if not depth:
                collector = collector[:i + 1]
                break
        (work / "test.cpp").write_text(HARNESS.replace("// COLLECTOR", collector))
        cls.binary = work / "test"
        subprocess.run([compiler, "-std=c++17", "-O0", "-g", str(work / "test.cpp"),
                        "-o", str(cls.binary)], check=True, capture_output=True, text=True)

    def test_selection_and_presets(self):
        for scenario in ("source", "dedup", "reorder", "absent", "shrink", "animation",
                         "empty", "level", "layer", "node", "reset", "presets"):
            with self.subTest(scenario=scenario):
                result = subprocess.run([str(self.binary), scenario], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

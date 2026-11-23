#pragma once
extern "C" {
#include "tlk_wide.h"
}
#include "tlk_browser_sprite_colours.h"
struct BrowserPaletteEditor {
 BrowserSpriteColours sprites;
 SDL_Texture *image[2]={};int owner=-1,target=1,selected=-1,selection_level=-1;bool refresh=true;uint64_t palette_stamp=~uint64_t(0);
 void Clear(){sprites.Clear();for(auto &t:image){SDL_DestroyTexture(t);t=nullptr;}}
 ~BrowserPaletteEditor(){Clear();}
 static ImVec4 RGB(unsigned c){return ImVec4((c&31)/31.f,(c>>5&31)/31.f,(c>>10&31)/31.f,1);}
 void Draw(SDL_Renderer *renderer,int node){
  const auto *n=TlkResourcesNode(node);
  if(!n||!strstr(n->id,"palette")||strncmp(n->id,"graphics.",9))return;
  if(TlkResourcesSpritePaletteNode(node)){sprites.Draw(renderer,node);return;}
  if(sprites.owner>=0)sprites.Clear();
  if(!ImGui::CollapsingHeader("Edit this level's colours"))return;
  uint64_t stamp=1469598103934665603ull;
  for(int i=0;i<TlkResourcesPaletteCount(1);i++){int e[4];TlkResourcesPaletteEntry(i,1,e);for(int v:e){stamp^=(unsigned)v;stamp*=1099511628211ull;}}
  if(stamp!=palette_stamp){palette_stamp=stamp;refresh=true;}
  unsigned level=TlkWideFrameLevel();
  if(level>=14||!TlkWideFrameStageActive()){ImGui::TextWrapped("Start a level to edit its colours. Your original artwork is always kept.");return;}
  if(owner!=node){owner=node;target=strstr(n->id,"foreground")?0:strstr(n->id,"sprites")?2:1;selected=-1;refresh=true;}
  const char *layers[]={"Foreground","Background","Sprites and HUD"};
  if(ImGui::Combo("What to recolour",&target,layers,3)){selected=-1;refresh=true;}
  ImGui::TextWrapped("Only this level and layer change. The same shade elsewhere in this layer changes together. Apply & save keeps your colours; no restart is needed.");
  if(selection_level!=(int)level){selection_level=(int)level;selected=-1;refresh=true;}
  uint16_t colors[128];int count=TlkWidePaletteColors((unsigned)target,colors,128);
  if(!count){ImGui::TextWrapped("No colours are available in this scene yet.");return;}
  // Like BrowserPaletteModel, keep the 15-bit colour, never its grid index.
  if(selected<0)selected=colors[0];
  ImGui::BeginChild("Original shades",ImVec2(0,150),ImGuiChildFlags_Borders);
  for(int i=0;i<count;i++){
   ImGui::PushID((int)colors[i]);if(i%12)ImGui::SameLine();ImVec4 c=RGB(colors[i]);
   if(ImGui::ColorButton("##shade",c,ImGuiColorEditFlags_NoTooltip,ImVec2(28,28)))selected=colors[i];
   if(colors[i]==selected)ImGui::GetWindowDrawList()->AddRect(ImGui::GetItemRectMin(),ImGui::GetItemRectMax(),IM_COL32(255,215,70,255),0,0,3);
   if(ImGui::IsItemHovered())ImGui::SetTooltip("Choose this original shade");ImGui::PopID();
  }
  ImGui::EndChild();
  bool visible=std::find(colors,colors+count,selected)!=colors+count;
  ImGui::ColorButton("Selected original shade",RGB((unsigned)selected),ImGuiColorEditFlags_NoTooltip,ImVec2(28,28));
  if(!visible)ImGui::TextWrapped("The selected shade is not in the current scene palette. Edits still apply to this original colour.");
  unsigned original=(unsigned)selected;TlkResourcesPalettePreview(1);unsigned edited=TlkResourcesPaletteMap(level,(unsigned)target,(uint16_t)original);TlkResourcesPalettePreview(0);
  ImVec4 c=RGB(edited);float values[]={c.x,c.y,c.z};
  if(ImGui::ColorEdit3("New colour",values,ImGuiColorEditFlags_NoInputs)){
   unsigned replacement=0;for(unsigned i=0;i<3;i++)replacement|=(unsigned)std::clamp((int)(values[i]*31.f+.5f),0,31)<<(i*5);
   if(TlkResourcesPaletteSet((int)level,target,(int)original,(int)replacement))refresh=true;
  }
  if(ImGui::Button("Reset this shade")){TlkResourcesPaletteSet((int)level,target,(int)original,(int)original);refresh=true;}
  ImGui::SameLine();if(ImGui::Button("Reset layer colours")){TlkResourcesPaletteReset((int)level,target);refresh=true;}
  if(refresh){
   std::vector<uint32_t> pixels(320*224);
   for(int d=0;d<2;d++){
    TlkResourcesPalettePreview(d);
    if(TlkWidePreview(pixels.data(),320)){
     if(!image[d])image[d]=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_XRGB8888,SDL_TEXTUREACCESS_STATIC,320,224);
     if(image[d]){SDL_SetTextureScaleMode(image[d],SDL_SCALEMODE_NEAREST);SDL_UpdateTexture(image[d],nullptr,pixels.data(),320*4);}
    }
   }TlkResourcesPalettePreview(0);refresh=false;
  }
  ImGui::TextUnformatted("Current game / your pending colours");
  float w=std::min(320.f,(ImGui::GetContentRegionAvail().x-12)/2);
  for(int i=0;i<2;i++){if(i)ImGui::SameLine();if(image[i])ImGui::Image((ImTextureID)(uintptr_t)image[i],ImVec2(w,w*224/320));}
  ImGui::TextWrapped("Colour edits are included when you save a custom preset. Undo changes restores your saved colours.");
 }
};

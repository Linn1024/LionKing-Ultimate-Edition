/* Project-owned desktop browser. The framework and its menu remain untouched.
 * A separate ImGui context/window works with both SDL and OpenGL game video. */
#include "tlk_visual_resources.h"
#include "tlk_resource_audio_preview.h"
#include "tlk_resources.h"
#include "tlk_fallback_log.h"
#include "tlk_resource_death_choice.h"
#include "tlk_browser_sounds.h"
#include "tlk_browser_descriptions.h"
#include "tlk_browser_comparisons.h"
#include "tlk_browser_gallery_routes.h"
#include "tlk_browser_scene_examples.h"
#include "imgui.h"
#include "imgui_impl_sdl3.h"
#include <algorithm>
#include <cctype>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>
#include <atomic>
#include <memory>
#include <mutex>
#include "tlk_browser_presets.h"
#include "tlk_browser_sprite_colours.h"
#include "tlk_browser_palette_editor.h"
#include "tlk_browser_preset_manager.h"
#include "tlk_browser_placement_diagram.h"
#include "tlk_browser_preset_manager.h"
#include "tlk_browser_genesis_theme.h"
#include "common/recomp_runtime_ui_internal.h"
static std::atomic<bool> preview_capture{false};
extern "C" int __real_TlkFallbackEnabled(void);
extern "C" void __real_TlkFallbackRecord(const char*,const char*,const char*,unsigned,unsigned,unsigned,uint64_t);
extern "C" void __real_TlkFallbackSpriteRecord(const char*,const char*,unsigned,unsigned,const TlkFallbackSpriteInfo*,uint64_t);
extern "C" int __wrap_TlkFallbackEnabled(void){return preview_capture?0:__real_TlkFallbackEnabled();}
extern "C" void __wrap_TlkFallbackRecord(const char*k,const char*r,const char*why,unsigned obj,unsigned pose,unsigned detail,uint64_t count){if(!preview_capture)__real_TlkFallbackRecord(k,r,why,obj,pose,detail,count);}
extern "C" void __wrap_TlkFallbackSpriteRecord(const char*k,const char*why,unsigned obj,unsigned pose,const TlkFallbackSpriteInfo*info,uint64_t count){if(!preview_capture)__real_TlkFallbackSpriteRecord(k,why,obj,pose,info,count);}
__attribute__((constructor)) static void RegisterVisualBrowser(void) {
    g_tlk_visual_resources_open=TlkVisualResourcesOpen;
    g_tlk_main_settings_open=TlkMainSettingsOpen;
}
extern "C" {
#include "tlk_wide.h"
#include "tlk_md_sound.h"
#include "tlk_be_prepared_data.h"
void RtlApuLock(void);
void RtlApuUnlock(void);
unsigned TlkResourcesHostLevel(void);
void TlkResourcesHostApplied(void);
bool __real_SDL_RenderPresent(SDL_Renderer *renderer);
}
namespace {
const ImVec4 gold(1.f,.84f,.35f,1),muted(.76f,.72f,.67f,1),teal(1.f,.84f,.35f,1);
bool Starts(const char *s,const char *p){return !strncmp(s,p,strlen(p));}
int Parent(int i) {
    const char *id=TlkResourcesNode(i)->id;
    if(!strcmp(id,"gameplay.levels.pride_lands.health_death"))return TlkResourcesFind("gameplay.simba");
    if(!strcmp(id,"gameplay.levels.pride_lands.final_life"))return TlkResourcesFind("gameplay.menus");
    if(Starts(id,"graphics.titles.pride_lands."))return TlkResourcesFind("graphics.titles");
    if(Starts(id,"audio.music.")&&(strstr(id,".track")||!strcmp(id,"audio.music.pride_rock.finale")))return TlkResourcesFind("audio.music");
    return TlkResourcesNode(i)->parent;
}
const char *Label(int i) {
    const char *id=TlkResourcesNode(i)->id;
    if(Starts(id,"audio.music.")&&strstr(id,".track")){std::string group(id,strlen(id)-6);int index=TlkResourcesFind(group.c_str());if(index>=0)return TlkResourcesNode(index)->label;}
    if(!strcmp(id,"audio.music.pride_rock.finale"))return "Scar defeat / ending";
    if(!strcmp(id,"audio.music.pride_health_death"))return "Health-death cue (all levels)";
    if(!strcmp(id,"graphics.pride_final_menu"))return "Continue / Game Over";
    if(!strcmp(id,"gameplay.levels"))return "Levels";
    if(!strcmp(id,"gameplay.levels.pride_lands.start"))return "Entry position";
    if(!strcmp(id,"gameplay.levels.pride_lands.contacts"))return "Terrain layout and floor shapes";
    if(!strcmp(id,"gameplay.levels.pride_lands.health_death"))return "Death movement";
    if(!strcmp(id,"gameplay.levels.pride_lands.final_life"))return "Last life / Continue (Pride Lands)";
    if(!strcmp(id,"graphics.titles"))return "Level names";
    if(!strcmp(id,"graphics.titles.pride_lands.position"))return "Caption height";
    if(!strcmp(id,"graphics.titles.pride_lands.duration"))return "Caption duration (Pride Lands)";
    return TlkResourcesNode(i)->label;
}
bool Hidden(int i) {
    const auto *n=TlkResourcesNode(i);const char *id=n->id;
    if(!strcmp(id,"graphics.scenery.palettes"))return true;
    if(n->leaf&&!n->md_supported)return true;
    if(!n->leaf&&Starts(id,"audio.music."))return true;
    if(!strcmp(id,"graphics.titles.pride_lands.duration")||!strcmp(id,"gameplay.levels.pride_lands.final_life"))return true;
    if(TlkResourceSharedDeath(id)&&strcmp(id,"audio.music.pride_health_death"))return true;
    return !strcmp(id,"graphics.titles.pride_lands")||Starts(id,"graphics.titles.remaining")||strstr(id,"death_motion");
}
void SetChoice(int selected,int source) {
    const char *id=TlkResourcesNode(selected)->id;TlkResourcesSet(selected,source);
    if(!strcmp(id,"gameplay.levels.pride_lands.health_death"))for(int i=0;i<TlkResourcesCount();i++)if(strstr(TlkResourcesNode(i)->id,"death_motion"))TlkResourcesSet(i,source);
    if(Starts(id,"graphics.titles.pride_lands.")) {
        std::string other="graphics.titles.remaining."+std::string(id+strlen("graphics.titles.pride_lands."));
        int index=TlkResourcesFind(other.c_str());if(index>=0)TlkResourcesSet(index,source);
    }
}
bool Advanced(int i) {
    const auto *n=TlkResourcesNode(i);if(!n->leaf)return false;
    const char *id=n->id;
    return !n->md_supported || strstr(id,"_bounds") || strstr(id,"hitboxes") ||
        strstr(id,"streaming") || strstr(id,"_markers") || strstr(id,"ceiling") ||
        strstr(id,"initialization") || strstr(id,"input_filter") || strstr(id,"reactivation");
}
std::string Path(int i) {
    std::string s;
    for(;i>0;i=Parent(i))s=std::string(Label(i))+(s.empty()?"":" / ")+s;
    return s;
}
std::string Lower(std::string s){for(char &c:s)c=(char)std::tolower((unsigned char)c);return s;}
const char *Source(int s){return s==TLK_SOURCE_MD?"Genesis":"SNES";}
int Category(int i){const char *id=TlkResourcesNode(i)->id;return Starts(id,"graphics")?0:Starts(id,"audio")?1:Starts(id,"gameplay")?2:3;}
void Tree(int i,int cat,const std::string &query,int &selected,int &visible) {
    if(Hidden(i))return;const auto *n=TlkResourcesNode(i);
    bool matches=n->leaf && (cat<0 || (cat==4?Advanced(i):Category(i)==cat && !Advanced(i))) &&
        (query.empty() || Lower(Path(i)).find(query)!=std::string::npos || Lower(n->scope).find(query)!=std::string::npos);
    bool descendants=false;
    if(!n->leaf)for(int j=1;j<TlkResourcesCount()&&!descendants;j++)if(TlkResourcesNode(j)->leaf&&!Hidden(j)) {
        if((cat<0 || (cat==4?Advanced(j):Category(j)==cat&&!Advanced(j))) &&
           (query.empty() || Lower(Path(j)).find(query)!=std::string::npos || Lower(TlkResourcesNode(j)->scope).find(query)!=std::string::npos))
            for(int p=Parent(j);p>0;p=Parent(p))if(p==i){descendants=true;break;}
    }
    if(!matches&&!descendants)return;
    ImGui::PushID(i);visible++;
    ImGuiTreeNodeFlags flags=ImGuiTreeNodeFlags_OpenOnArrow|ImGuiTreeNodeFlags_SpanAvailWidth;
    if(n->leaf)flags|=ImGuiTreeNodeFlags_Leaf|ImGuiTreeNodeFlags_NoTreePushOnOpen;
    if(i==selected)flags|=ImGuiTreeNodeFlags_Selected;
    if(!query.empty())ImGui::SetNextItemOpen(true,ImGuiCond_Always);
    else if(Parent(i)==0)flags|=ImGuiTreeNodeFlags_DefaultOpen;
    std::string text=Label(i);
    if(n->leaf&&TlkResourcesChoice(i,1)!=TLK_SOURCE_INHERIT)text+=" ["+std::string(Source(TlkResourcesChoice(i,1)))+"]";
    float spacing=ImGui::GetTreeNodeToLabelSpacing(),wrap=std::max(60.f,ImGui::GetContentRegionAvail().x-spacing-8);
    ImVec2 size=ImGui::CalcTextSize(text.c_str(),nullptr,false,wrap);
    ImGui::PushStyleVar(ImGuiStyleVar_FramePadding,ImVec2(4,std::max(3.f,(size.y-ImGui::GetFontSize())*.5f+3)));
    bool open=ImGui::TreeNodeEx("##entry",flags|ImGuiTreeNodeFlags_FramePadding);
    ImGui::PopStyleVar();
    auto a=ImGui::GetItemRectMin(),b=ImGui::GetItemRectMax();
    ImGui::GetWindowDrawList()->AddText(ImGui::GetFont(),ImGui::GetFontSize(),ImVec2(a.x+spacing,a.y+(b.y-a.y-size.y)*.5f),ImGui::GetColorU32(i==selected?gold:ImGui::GetStyleColorVec4(ImGuiCol_Text)),text.c_str(),nullptr,wrap);
    if(ImGui::IsItemClicked()&&!ImGui::IsItemToggledOpen())selected=i;
    if(open&&!n->leaf) {
        for(int j=1;j<TlkResourcesCount();j++)if(Parent(j)==i)Tree(j,cat,query,selected,visible);
        ImGui::TreePop();
    }
    ImGui::PopID();
}
void Theme() {
    ImGui::StyleColorsDark();auto &s=ImGui::GetStyle();
    s.WindowPadding=ImVec2(26,22);s.FramePadding=ImVec2(16,10);s.ItemSpacing=ImVec2(12,12);
    s.WindowRounding=0;s.ChildRounding=0;s.FrameRounding=0;s.GrabRounding=0;s.ScrollbarRounding=0;s.ScrollbarSize=14;
    s.ChildBorderSize=2;s.FrameBorderSize=1;s.AntiAliasedLines=false;
    s.Colors[ImGuiCol_WindowBg]=ImVec4(0,0,0,0);
    s.Colors[ImGuiCol_ChildBg]=ImVec4(.055f,.035f,.14f,.96f);
    s.Colors[ImGuiCol_PopupBg]=ImVec4(.07f,.04f,.16f,1);
    s.Colors[ImGuiCol_FrameBg]=ImVec4(.13f,.08f,.20f,1);
    s.Colors[ImGuiCol_FrameBgHovered]=ImVec4(.24f,.15f,.24f,1);
    s.Colors[ImGuiCol_FrameBgActive]=ImVec4(.30f,.19f,.19f,1);
    s.Colors[ImGuiCol_Button]=ImVec4(.16f,.09f,.16f,1);
    s.Colors[ImGuiCol_ButtonHovered]=ImVec4(.38f,.22f,.13f,1);
    s.Colors[ImGuiCol_ButtonActive]=ImVec4(.48f,.30f,.12f,1);
    s.Colors[ImGuiCol_Header]=ImVec4(.36f,.21f,.12f,1);
    s.Colors[ImGuiCol_HeaderHovered]=ImVec4(.44f,.28f,.14f,1);
    s.Colors[ImGuiCol_HeaderActive]=ImVec4(.48f,.30f,.12f,1);
    s.Colors[ImGuiCol_Border]=ImVec4(.61f,.43f,.21f,1);
    s.Colors[ImGuiCol_Separator]=s.Colors[ImGuiCol_Border];
    s.Colors[ImGuiCol_Text]=ImVec4(1.f,.96f,.85f,1);
    s.Colors[ImGuiCol_TextDisabled]=ImVec4(.54f,.48f,.48f,1);
    s.Colors[ImGuiCol_CheckMark]=gold;
    s.Colors[ImGuiCol_SliderGrab]=gold;
    s.Colors[ImGuiCol_SliderGrabActive]=ImVec4(1,1,.65f,1);
    s.Colors[ImGuiCol_ScrollbarBg]=ImVec4(.05f,.03f,.10f,1);
    s.Colors[ImGuiCol_ScrollbarGrab]=ImVec4(.45f,.29f,.15f,1);
    s.Colors[ImGuiCol_PlotHistogram]=gold;
}
void Render(SDL_Renderer *ren,ImDrawData *data) {
    SDL_SetRenderScale(ren,data->FramebufferScale.x,data->FramebufferScale.y);
    for(int i=0;i<data->CmdListsCount;i++) {
        auto *list=data->CmdLists[i];std::vector<SDL_Vertex> v(list->VtxBuffer.Size);
        for(int j=0;j<list->VtxBuffer.Size;j++) {
            auto &s=list->VtxBuffer[j];auto c=s.col;
            v[j]={{s.pos.x-data->DisplayPos.x,s.pos.y-data->DisplayPos.y},
                  {(c&255)/255.f,((c>>8)&255)/255.f,((c>>16)&255)/255.f,(c>>24)/255.f},{s.uv.x,s.uv.y}};
        }
        for(const auto &cmd:list->CmdBuffer) {
            if(cmd.UserCallback){if(cmd.UserCallback!=ImDrawCallback_ResetRenderState)cmd.UserCallback(list,&cmd);continue;}
            SDL_Rect clip={(int)(cmd.ClipRect.x-data->DisplayPos.x),(int)(cmd.ClipRect.y-data->DisplayPos.y),
                           (int)(cmd.ClipRect.z-cmd.ClipRect.x),(int)(cmd.ClipRect.w-cmd.ClipRect.y)};
            SDL_SetRenderClipRect(ren,&clip);
            std::vector<int> idx(cmd.ElemCount);
            for(unsigned j=0;j<cmd.ElemCount;j++)idx[j]=list->IdxBuffer[cmd.IdxOffset+j]+cmd.VtxOffset;
            SDL_RenderGeometry(ren,(SDL_Texture *)(uintptr_t)cmd.GetTexID(),v.data(),(int)v.size(),idx.data(),(int)idx.size());
        }
    }
    SDL_SetRenderClipRect(ren,nullptr);
}
struct Pictures {
    SDL_Texture *image[2]={};int node=-2,owner=-2,width=192,height=192,planes=4,frame=0,uploaded=-1;unsigned scene=0,frames=0;
    bool combined=false;
    bool valid[2]={},same=false,scene_available=false;int x0=0,y0=0,x1=192,y1=192;
    void *job=nullptr;Uint8 *data=nullptr;std::string message;
    ~Pictures(){Clear();}
    void Clear(){for(auto &p:image){if(p)SDL_DestroyTexture(p);p=nullptr;}if(job)TlkNativeAudioPreviewClose(job);job=nullptr;SDL_free(data);data=nullptr;node=owner=-2;combined=false;frames=0;uploaded=-1;frame=0;valid[0]=valid[1]=false;same=false;scene_available=false;message.clear();}
    void Update(SDL_Renderer *ren,int selected,int parent=-1,bool whole=false) {
        if(parent<0)parent=selected;
        if(selected!=node||parent!=owner||whole!=combined){Clear();node=selected;owner=parent;combined=whole;char reason[256]={};job=TlkSubjectPreviewStart(TlkResourcesNode(selected)->id,scene,reason,sizeof reason);message=job?"Preparing this resource...":reason;if(SDL_getenv("TLK_BROWSER_AUDIT")){std::fprintf(stderr,"browser_job owner=%d subject=%d combined=%d\n",owner,node,combined);std::fflush(stderr);}}
        if(job){Uint32 bytes=0;char reason[256]={};int r=TlkSubjectPreviewPoll(job,&data,&bytes,&frames,reason,sizeof reason);if(r){TlkNativeAudioPreviewClose(job);job=nullptr;message=r==1?"":*reason?reason:"This original resource could not be prepared.";if(r==1){uint32_t header[5];std::memcpy(header,data,20);width=header[1];height=header[2];planes=header[4];}}}
        if(!data||frame==uploaded)return;uploaded=frame;
        if(!frame&&SDL_getenv("TLK_BROWSER_AUDIT"))std::fprintf(stderr,"browser_subject id=%s frames=%u width=%d height=%d\n",TlkResourcesNode(selected)->id,frames,width,height);
        if(SDL_getenv("TLK_BROWSER_AUDIT"))std::fflush(stderr);
        const uint32_t *p=(const uint32_t*)(data+20)+(size_t)frame*width*height*planes;
        const char *id=TlkResourcesNode(selected)->id;
        std::string family=id;
        while(family.find('.')!=std::string::npos&&TlkResourcesFind((family+".frames").c_str())<0&&TlkResourcesFind((family+".palette").c_str())<0)family.resize(family.rfind('.'));
        int axes[2]={0,1};
        if(planes==4)for(int k=0;k<2;k++) {
            if(combined){axes[k]=k?3:0;continue;}
            TlkResourcesPreviewBegin(selected,k?TLK_SOURCE_MD:TLK_SOURCE_SNES);
            int drawing=TlkResourcesFind((family+".frames").c_str()),colors=TlkResourcesFind((family+".palette").c_str());
            if(Starts(id,"graphics.hud")) {
                static const char *meter[]={"graphics.hud.frames.roar","graphics.hud.frames.health","graphics.hud.frames.lives"};
                drawing=TlkResourcesFind(!strcmp(id,"graphics.hud.palette")?meter[frame%3]:id);
                colors=TlkResourcesFind("graphics.hud.palette");
            }
            axes[k]=(drawing>=0&&TlkResourcesResolved(drawing,1)==TLK_SOURCE_MD?2:0)+(colors>=0&&TlkResourcesResolved(colors,1)==TLK_SOURCE_MD?1:0);
            TlkResourcesPreviewEnd();
        }
        if(SDL_getenv("TLK_BROWSER_AUDIT")){std::fprintf(stderr,"browser_compare owner=%s subject=%s combined=%u axes=%d,%d\n",TlkResourcesNode(owner)->id,id,combined,axes[0],axes[1]);std::fflush(stderr);}
        x0=width;y0=height;x1=y1=0;
        for(int k=0;k<2;k++) {
            if(!TlkBrowserGallerySourceAvailable(id,k)){valid[k]=false;continue;}
            if(image[k])SDL_DestroyTexture(image[k]);std::vector<uint32_t> rgba(p+axes[k]*width*height,p+(axes[k]+1)*width*height);
            for(int y=0;y<height;y++)for(int x=0;x<width;x++)if(!(rgba[y*width+x]>>24))rgba[y*width+x]=((x/12+y/12)&1)?0xff1d3033:0xff17282b;
            else{x0=std::min(x0,x);y0=std::min(y0,y);x1=std::max(x1,x+1);y1=std::max(y1,y+1);}
            image[k]=SDL_CreateTexture(ren,SDL_PIXELFORMAT_XRGB8888,SDL_TEXTUREACCESS_STATIC,width,height);
            if(image[k]){SDL_UpdateTexture(image[k],nullptr,rgba.data(),width*4);SDL_SetTextureScaleMode(image[k],SDL_SCALEMODE_NEAREST);}valid[k]=image[k]!=nullptr;
        }
        if(x0>=x1){x0=y0=0;x1=width;y1=height;}else{x0=std::max(0,x0-10);y0=std::max(0,y0-10);x1=std::min(width,x1+10);y1=std::min(height,y1+10);}
        same=valid[0]&&valid[1]&&std::memcmp(p+axes[0]*width*height,p+axes[1]*width*height,width*height*4)==0;
    }
};
struct Music {const char *id;int program;};
const Music tracks[]={
    {"audio.music.pride_lands",137},{"audio.music.cant_wait_to_be_king",2},
    {"audio.music.elephant_graveyard.track",83},{"audio.music.stampede",145},
    {"audio.music.simbas_exile.track",258},{"audio.music.hakuna_matata.track",40},
    {"audio.music.simbas_destiny.track",281},{"audio.music.be_prepared.track",327},
    {"audio.music.simbas_return.track",311},{"audio.music.pride_rock.track",432},
    {"audio.music.pride_rock.finale",339},{"audio.music.ending_credits",61},{"audio.music.title",73},
    {"audio.music.pride_health_death",430},{"audio.music.pride_game_over",327},
    {"audio.music.pride_battle",134},{"audio.music.bug_toss",134},{"audio.music.bug_hunt",281}
};
int Track(int selected) {
    const char *id=TlkResourcesNode(selected)->id;int level=(int)TlkResourcesHostLevel();
    for(unsigned i=0;i<sizeof tracks/sizeof *tracks;i++)if(!strcmp(id,tracks[i].id))return (int)i;
    if((!strcmp(id,"audio")||!strcmp(id,"audio.music"))&&level>=0&&level<10)return level;
    return -1;
}
int SoundCue(int selected){for(unsigned i=0;i<sizeof browser_sounds/sizeof *browser_sounds;i++)if(!strcmp(TlkResourcesNode(selected)->id,browser_sounds[i].id))return (int)i;return -1;}
struct Audition {
    SDL_AudioStream *stream=nullptr;void *native_job=nullptr;std::string message;std::vector<float> waveform;bool own_audio=false;
    ~Audition(){Stop();if(own_audio)SDL_QuitSubSystem(SDL_INIT_AUDIO);}
    void Stop(){if(stream)SDL_DestroyAudioStream(stream);stream=nullptr;if(native_job)TlkNativeAudioPreviewClose(native_job);native_job=nullptr;}
    void Submit(const std::vector<int16_t>&pcm,int source,bool restored) {
        waveform.assign(500,0);
        for(unsigned i=0;i<500;i++)for(unsigned j=i*pcm.size()/500;j<(i+1)*pcm.size()/500;j++)waveform[i]=std::max(waveform[i],std::abs((float)pcm[j])/32768.f);
        if(SDL_getenv("TLK_BROWSER_AUDIT"))std::fprintf(stderr,"browser_sample source=%d peak=%.6f restored=%d\n",source,*std::max_element(waveform.begin(),waveform.end()),restored);
        if(SDL_getenv("TLK_BROWSER_AUDIT"))std::fflush(stderr);
        if(*std::max_element(waveform.begin(),waveform.end())==0){message="No audible sample was produced for this cue.";return;}
        if(!(SDL_WasInit(SDL_INIT_AUDIO)&SDL_INIT_AUDIO)){if(!SDL_InitSubSystem(SDL_INIT_AUDIO)){message="Could not initialize audio.";return;}own_audio=true;}
        SDL_AudioSpec spec={SDL_AUDIO_S16,2,32000};
        stream=SDL_OpenAudioDeviceStream(SDL_AUDIO_DEVICE_DEFAULT_PLAYBACK,&spec,nullptr,nullptr);
        if(stream){SDL_PutAudioStreamData(stream,pcm.data(),(int)(pcm.size()*2));SDL_FlushAudioStream(stream);SDL_ResumeAudioStreamDevice(stream);message="Playing a five-second sample.";}
        else message="Could not open the audio device.";
    }
    void Tick() {
        if(!native_job)return;SDL_AudioSpec spec;Uint8 *samples=nullptr;Uint32 bytes=0;char reason[256]={};
        int result=TlkNativeAudioPreviewPoll(native_job,&spec,&samples,&bytes,reason,sizeof reason);
        if(!result)return;TlkNativeAudioPreviewClose(native_job);native_job=nullptr;
        if(result<0){message=reason;return;}
        std::vector<int16_t> pcm(bytes/2);std::memcpy(pcm.data(),samples,bytes);SDL_free(samples);Submit(pcm,TLK_SOURCE_SNES,true);
    }
    void Play(int source,int track,int cue=-1) {
        Stop();waveform.clear();if(source==TLK_SOURCE_SNES&&track==13){message="SNES stops the level music during this death sequence; it has no separate death tune.";return;}std::vector<int16_t> pcm(32000*2*5);bool ok=false,restored=true;
        if(source==TLK_SOURCE_SNES) {
            char reason[256]={};int level=track>=0&&track<10?track:track==12?14:track==16?10:track==17?11:-1;
            if(cue>=0) {auto &sound=browser_sounds[cue];int event=sound.event;if(event==-3){const uint16_t *r=TlkBePreparedGroupSoundRules();event=r?r[TLK_BP_SOUND_NATIVE_EVENT]:-2;}if(event<0){message=sound.event==-1?"SNES has no separate cue at this action. Other scene audio may still play.":"This SNES preview is not available yet. That does not mean the original is silent.";return;}native_job=TlkNativeEffectPreviewStart(sound.level,(unsigned)event,reason,sizeof reason);}
            else if(level>=0)native_job=TlkNativeAudioPreviewStart((unsigned)level,reason,sizeof reason);
            else std::snprintf(reason,sizeof reason,"A native sample for this scene is not available yet.");
            message=reason;return;
        }
        if(source==TLK_SOURCE_MD && (track>=0 || cue>=0) && TlkMdSoundReady()) {
            if(cue>=0&&!browser_sounds[cue].selector){message="Genesis has no separate cue at this action. Other scene audio may still play.";return;}
            RtlApuLock();std::vector<uint8_t> state(TlkMdSoundStateSize());
            if(!state.empty()&&TlkMdSoundSaveState(state.data(),state.size())) {
                TlkMdSoundRestart();TlkMdSoundCommand(1,0);
                /* Let the original driver's stop/reset finish before posting
                 * an effect. Posting both in the same batch can swallow FM FX. */
                if(cue>=0){std::vector<int16_t> settle(8192);TlkMdSoundRender(settle.data(),4096,32000);TlkMdSoundClearOutput();}
                if(cue<0)TlkMdSoundCommand(1,tracks[track].program);
                else {const auto &sound=browser_sounds[cue];
                    if(sound.selector==2&&sound.value==92){
                        TlkMdSoundCommand(2,strstr(sound.id,"geysers")?171:172);
                        TlkMdSoundRender(pcm.data(),16000,32000);
                    }
                    switch(sound.selector){
                    case -1:TlkMdSoundOpeningTimonSample();break;
                    case -2:TlkMdSoundInterlevelSample(sound.value);break;
                    case -3:TlkMdSoundCliffSample();break;
                    case -4:TlkMdSoundExileExitSample(sound.value);break;
                    case -5:TlkMdSoundBonusResultSample();break;
                    case -6:{const uint16_t *r=TlkBePreparedGroupSoundRules();if(r)TlkMdSoundPcm(r[TLK_BP_SOUND_MD_SAMPLE],r[TLK_BP_SOUND_MD_PARAMETER]);break;}
                    case -7:TlkMdSoundDestinySpeechSample(0);break;
                    default:TlkMdSoundCommand(sound.selector,sound.value);break;
                }}ok=true;
                for(unsigned pos=cue>=0&&browser_sounds[cue].selector==2&&browser_sounds[cue].value==92?16000:0;pos<32000*5;pos+=512) {
                    if(cue>=0&&browser_sounds[cue].selector==-7&&pos>=32000*TLK_DESTINY_SPEECH_SECOND_DELAY/60&&pos-512<32000*TLK_DESTINY_SPEECH_SECOND_DELAY/60)TlkMdSoundDestinySpeechSample(1);
                    unsigned n=std::min(512u,32000*5-pos);
                    if(!TlkMdSoundRender(pcm.data()+pos*2,n,32000)){ok=false;break;}
                }
                if(!TlkMdSoundLoadState(state.data(),state.size()))ok=restored=false;
                std::vector<uint8_t> verify(state.size());
                if(!TlkMdSoundSaveState(verify.data(),verify.size()) || state!=verify)ok=restored=false;
            }
            RtlApuUnlock();
        }
        if(!ok){message="A sample is not available in this scene.";return;}
        Submit(pcm,source,restored);
        if(SDL_getenv("TLK_BROWSER_AUDIT"))std::fflush(stderr);
    }
};
const char *Explanation(const TlkResourceNode *n) {
    if(!strcmp(n->id,"audio.music.pride_rock.finale"))return "Choose the music after Scar is defeated, including when it begins. Genesis starts during Simba's victory walk; SNES keeps its original pause. Artwork and animation timing stay separate.";
    if(!strcmp(n->id,"audio.effects.interlevel.pride_lands")||!strcmp(n->id,"audio.effects.interlevel.stampede"))return "Choose the dialogue for this story scene. Genesis speech works with either the original SNES pictures or the Genesis scene. The picture and animation choices stay separate.";
    if(!strcmp(n->id,"graphics.titles.pride_lands.duration"))return "Choose how long the Pride Lands opening name stays visible.";
    if(!strcmp(n->id,"graphics.menus.publisher_cards"))return "Choose the opening publisher logos shown before the title menu.";
    if(const char *text=TlkBrowserPlacementDescription(n->id))return text;
    if(!strcmp(n->id,"graphics.scenery.foreground")||!strcmp(n->id,"graphics.scenery.background"))return "Choose this layer's artwork and colours together. Open Artwork or Palette below to mix them. Terrain and collision follow your gameplay choices.";
    if(Starts(n->id,"graphics.scenery.")&&strstr(n->id,".frames"))return "Choose this scenery layer's drawings. Colours have their own Palette choice; terrain and collision follow Gameplay.";
    if(!n->leaf)return "Set a source for this whole branch. Choose a character, object or setting below to explore it.";
    if(!strcmp(n->id,"graphics.interlevel.pride_lands"))return "Both versions have an illustrated scene after Pride Lands. This build pairs each illustration with its own scene timing, chosen under Gameplay / Levels / Pride Lands. Speech is chosen separately.";
    if(strstr(n->id,"death_motion"))return "Changes the movement of the death animation. Sprite artwork and colors are separate choices.";
    if(strstr(n->id,"snes_motion")||!strcmp(n->id,"graphics.scenery.firelight"))return n->scope;
    if(strstr(n->id,"palette"))return "Changes the colors. Animation drawings, gameplay and music stay independent.";
    if(strstr(n->id,"frames"))return "Changes the sprite drawings. Colors and gameplay timing are separate choices.";
    if(Starts(n->id,"audio.music"))return "Choose which version of this music plays. Artwork and gameplay stay independent.";
    if(Starts(n->id,"audio"))return "Choose this sound independently of the music and visual style.";
    if(Starts(n->id,"gameplay"))return GameplayExplanation(n->id);
    if(Starts(n->id,"graphics.scenery"))return "Choose the artwork used for the scenery. Terrain and collision follow your gameplay choices.";
    return "Choose which version to use for this part of the game.";
}
struct VersionComparison {std::string snes,genesis;};
VersionComparison Comparison(const TlkResourceNode *n) {
    const char *id=n->id;
    if(!n->leaf)return {"Child choices follow SNES unless you override them.","Child choices follow Genesis unless you override them."};
    if(!strcmp(id,"audio.music.pride_rock.finale"))return {"The SNES ending music, with the original pause before it begins.","The Genesis ending music starts when Simba begins his victory walk toward the edge."};
    if(Starts(id,"gameplay")) {
        if(const auto *h=TlkBrowserGameplayComparison(id))return {h->snes,h->genesis};
        if(strstr(id,"positions")||strstr(id,"placements")||strstr(id,"position")||strstr(id,".pickups"))
            return {"Uses the original SNES locations for these objects.","Uses the original Genesis locations, including any moved, added or omitted objects. Shared locations stay the same."};
        if(strstr(id,"bounds")||strstr(id,"hitboxes"))
            return {"Uses the SNES touch or landing area for each supported pose.","Uses the Genesis area for the matching pose. The size and direction of the difference vary by pose; drawings are separate."};
    }
    if(!strcmp(id,"display.viewport"))return {"Usually shows a 256-pixel-wide console view.","Usually shows a 320-pixel-wide console view. Special scenes such as the Stampede keep their own framing."};
    if(!strcmp(id,"graphics.titles.pride_lands.duration"))return {"The Pride Lands opening name stays visible for about two and a half seconds.","It stays visible for about one and two-thirds seconds. This choice affects Pride Lands only."};
    if(!strcmp(id,"graphics.sprites.effects.pickup_arrival.position"))return {"Pickups finish their flight at the SNES HUD sparkle positions.","They finish at the Genesis positions near the top corners. Their flight path is a separate choice."};
    if(!strcmp(id,"graphics.sprites.cinematics.timon.animation"))return {"The opening Timon scene uses the SNES pose timing.","Uses the Genesis four-update pace for pose changes. Overall scene length and speech are separate."};
    if(!strcmp(id,"graphics.bonus_results"))return {"Uses the SNES Bugs Caught lettering and number artwork.","Uses the Genesis Bugs Collected card and digits. Choose the score-counting sequence under Gameplay / Bonus stages."};
    if(!strcmp(id,"graphics.interlevel.pride_lands"))return {"The original SNES illustration is used with SNES scene timing. Combining it with Genesis timing is not implemented yet.","The original Genesis illustration is used with Genesis scene timing. The artwork currently follows that timing choice."};
    if(!strcmp(id,"graphics.interlevel.stampede"))return {"With SNES scene timing, keeps the SNES scene. With Genesis timing, a separate SNES illustration is unavailable, so the Genesis illustration is used.","Uses the Genesis illustration with Genesis scene timing. Scene timing is chosen under Gameplay / Levels / The Stampede."};
    if(!strcmp(id,"graphics.ending_title"))return {"Keeps the SNES presentation without the added Genesis title overlay.","The Genesis title appears over the sunrise during the Genesis ending waits. SNES ending timing has no matching interval."};
    if(!strcmp(id,"graphics.menus.publisher_cards"))return {"The original SNES publisher cards before the title menu.","Adds the animated SEGA logo before the Genesis publisher cards."};
    if(!strcmp(id,"graphics.ending_credits"))return {"The SNES credit lettering, names and layout.","The Genesis lettering, names, layout and scrolling pace. Ending speeches and music are chosen separately."};
    if(!strcmp(id,"graphics.scenery.timon_start_position"))return {"Timon stands at his original SNES opening-scene position.","He stands at his Genesis opening-scene position. This affects only the opening after Start."};
    if(!strcmp(id,"graphics.scenery.destiny_face_position"))return {"Mufasa's face appears at a fixed place in the sky.","Its position follows Simba's location at the end of Destiny."};
    if(strstr(id,".titles.")&&strstr(id,".position"))return {"Uses the SNES caption height, centred across the picture.","Uses the Genesis caption height, centred across the picture."};
    if(strstr(id,"snes_motion"))return {"Keeps this SNES background's original scrolling.","Adds the Genesis depth-scrolling effect to SNES artwork. Genesis artwork already uses its original motion."};
    if(!strcmp(id,"graphics.scenery.firelight"))return {"Keeps the SNES foreground's original static colours.","Makes the red SNES foreground highlights flicker using the Genesis fire cycle. Genesis colours already animate."};
    if(strstr(id,"palette"))return {"Uses the original SNES colours with your chosen drawings.","Uses the original Genesis colours with your chosen drawings. Mixed drawings use the closest available shades."};
    if(Starts(id,"audio"))return {"Uses this action's SNES sound or music. Listen below to compare it.","Uses this action's Genesis sound or music. A version with no separate cue stays silent; unavailable previews are labelled."};
    if(Starts(id,"graphics.menus")||!strcmp(id,"graphics.pride_final_menu"))return {"The SNES menu artwork, lettering and colours.","The Genesis menu artwork, lettering and colours. Button response and sounds are separate choices."};
    if(Starts(id,"graphics"))return {"Uses the original SNES artwork for this subject.","Uses the original Genesis artwork. Timing, sound and solid surfaces follow their own choices."};
    return {"Uses the original SNES rule for this choice.","Uses the original Genesis rule for this choice."};
}
int ChangeTiming(int index) {
    const auto *n=TlkResourcesNode(index);int change=n->change;
    if(!strcmp(n->id,"display.viewport")&&
       (TlkResourcesResolved(TlkResourcesFind("gameplay.camera"),0)==TLK_SOURCE_MD||
        TlkResourcesResolved(TlkResourcesFind("gameplay.camera"),1)==TLK_SOURCE_MD))change=TLK_CHANGE_LEVEL;
    if(!n->leaf)for(int i=1;i<TlkResourcesCount();i++) {
        const auto *child=TlkResourcesNode(i);if(!child->leaf||Hidden(i))continue;
        for(int p=Parent(i);p>=0;p=Parent(p))if(p==index){change=std::max(change,ChangeTiming(i));break;}
    }
    return change;
}
/* Apply commits every draft choice, including ones on other pages. Report
 * effective leaf changes so explicit overrides with the same result stay live. */
int PendingChangeTiming(std::string &reason) {
    int timing=TLK_CHANGE_LIVE;
    reason.clear();
    for(int i=1;i<TlkResourcesCount();i++) {
        const auto *n=TlkResourcesNode(i);
        if(!n->leaf || TlkResourcesResolved(i,0)==TlkResourcesResolved(i,1))continue;
        int change=ChangeTiming(i);
        if(change>timing){timing=change;reason=Path(i);}
    }
    return timing;
}
void DrawComparison(const TlkResourceNode *n) {
    VersionComparison c=Comparison(n);
    ImGui::TextUnformatted("SNES and Genesis compared");
    if(ImGui::BeginTable("version-comparison",2,ImGuiTableFlags_SizingStretchSame|ImGuiTableFlags_BordersInnerV)) {
        ImGui::TableNextRow();ImGui::TableNextColumn();ImGui::TextColored(gold,"SNES");ImGui::TextWrapped("%s",c.snes.c_str());
        ImGui::TableNextColumn();ImGui::TextColored(gold,"GENESIS");ImGui::TextWrapped("%s",c.genesis.c_str());
        ImGui::EndTable();
    }
}
std::vector<int> ArtworkExamples(int branch) {
    std::vector<int> examples;
    for(int i=1;i<TlkResourcesCount();i++) {
        const auto *n=TlkResourcesNode(i);if(Hidden(i)||!TlkSubjectPreviewSupported(n->id))continue;
        bool inside=false,redundant=false;
        for(int p=Parent(i);p>=0;p=Parent(p)) {
            if(p==branch){inside=true;break;}
            if(n->leaf&&TlkSubjectPreviewSupported(TlkResourcesNode(p)->id))redundant=true;
        }
        if(inside&&!redundant)examples.push_back(i);
    }
    return examples;
}
void ArtworkChildren(int branch,int &selected) {
    ImGui::Separator();ImGui::TextUnformatted("Choose an individual part");
    bool table=ImGui::BeginTable("artwork-children",2,ImGuiTableFlags_SizingStretchSame);
    for(int i=1;i<TlkResourcesCount();i++)if(Parent(i)==branch&&!Hidden(i)) {
        bool any=TlkResourcesNode(i)->leaf;
        for(int j=1;!any&&j<TlkResourcesCount();j++)if(TlkResourcesNode(j)->leaf&&!Hidden(j))
            for(int p=Parent(j);p>=0;p=Parent(p))if(p==i){any=true;break;}
        if(any){if(table)ImGui::TableNextColumn();ImGui::PushID(i);if(ImGui::Button(Label(i),ImVec2(-1,44)))selected=i;ImGui::PopID();}
    }
    if(table)ImGui::EndTable();
}

}
extern "C" int TlkVisualResourcesOpen(SDL_Window *parent) {
    if(SDL_getenv("TLK_RESOURCE_LEGACY"))return -1;
    ImGuiContext *previous=ImGui::GetCurrentContext();SDL_Window *glwin=SDL_GL_GetCurrentWindow();SDL_GLContext gl=SDL_GL_GetCurrentContext();
    SDL_Window *window=SDL_CreateWindow("The Lion King - Customize your game",1440,960,SDL_WINDOW_RESIZABLE|SDL_WINDOW_HIGH_PIXEL_DENSITY);
    if(!window)return -1;SDL_SetWindowMinimumSize(window,1120,780);
    SDL_Renderer *ren=SDL_CreateRenderer(window,nullptr);
    if(!ren){SDL_DestroyWindow(window);return -1;}
    SDL_SetRenderVSync(ren,1);ImGuiContext *context=ImGui::CreateContext();ImGui::SetCurrentContext(context);Theme();auto &io=ImGui::GetIO();
    io.IniFilename=nullptr;io.LogFilename=nullptr;io.ConfigFlags|=ImGuiConfigFlags_NavEnableKeyboard|ImGuiConfigFlags_NavEnableGamepad;
    GenesisBrowserArt menu_art;bool has_menu_art=menu_art.Load(ren);
    ImFontConfig font;font.SizePixels=20;font.OversampleH=1;font.OversampleV=1;font.PixelSnapH=true;
    ImFont *menu_font=io.Fonts->AddFontDefault(&font);menu_art.Font(io.Fonts,menu_font);
    if(!ImGui_ImplSDL3_InitForSDLRenderer(window,ren)){ImGui::DestroyContext();ImGui::SetCurrentContext(previous);SDL_DestroyRenderer(ren);SDL_DestroyWindow(window);return -1;}
    unsigned char *font_pixels;int fw,fh;io.Fonts->GetTexDataAsRGBA32(&font_pixels,&fw,&fh);
    SDL_Texture *font_texture=SDL_CreateTexture(ren,SDL_PIXELFORMAT_ABGR8888,SDL_TEXTUREACCESS_STATIC,fw,fh);
    SDL_UpdateTexture(font_texture,nullptr,font_pixels,fw*4);SDL_SetTextureBlendMode(font_texture,SDL_BLENDMODE_BLEND);SDL_SetTextureScaleMode(font_texture,SDL_SCALEMODE_NEAREST);
    io.Fonts->SetTexID((ImTextureID)(uintptr_t)font_texture);
    int selected=TlkResourcesFind("graphics"),title_node=-1,category=0,result=0;bool running=true,close_request=false,focus_changes=true;
    char search[160]={};int sound_variant=0;Pictures pictures;BrowserPaletteEditor palette_editor;Audition audio;std::string notice;
    const std::string preset_directory=BrowserPresets::Directory();
    BrowserPresetManager presets(preset_directory);
    char preset_name[65]={};std::string preset_error;bool create_preset=false;
    /* Developer capture shortcut: browse an item without applying any choice. */
    if(const char *start=SDL_getenv("TLK_BROWSER_START_AT")) {
        int index=TlkResourcesFind(start);
        if(index>0&&!Hidden(index)){selected=index;category=Advanced(index)?4:Category(index);std::snprintf(search,sizeof search,"%s",Path(index).c_str());}
    }
    if(const char *listen=SDL_getenv("TLK_BROWSER_AUDITION_SOURCE")) {
        int source=std::atoi(listen),cue=SoundCue(selected),track=Track(selected);
        if((source==TLK_SOURCE_SNES||source==TLK_SOURCE_MD)&&(cue>=0||track>=0))audio.Play(source,track,cue);
    }
    while(running) {
        audio.Tick();
        SDL_Event ev;
        while(SDL_PollEvent(&ev)) {
            ImGui_ImplSDL3_ProcessEvent(&ev);
            if(ev.type==SDL_EVENT_QUIT || (ev.type==SDL_EVENT_WINDOW_CLOSE_REQUESTED&&ev.window.windowID==SDL_GetWindowID(window)))close_request=true;
            if(ev.type==SDL_EVENT_KEY_DOWN&&(ev.key.key==SDLK_ESCAPE||ev.key.key==SDLK_F12)&&!ImGui::IsPopupOpen(nullptr,ImGuiPopupFlags_AnyPopupId))close_request=true;
            if(ev.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN&&ev.gbutton.button==SDL_GAMEPAD_BUTTON_EAST)close_request=true;
        }
        ImGui_ImplSDL3_NewFrame();ImGui::NewFrame();menu_art.Backdrop(io.DisplaySize);
        ImGui::SetNextWindowPos(ImVec2(0,0));ImGui::SetNextWindowSize(io.DisplaySize);
        ImGui::Begin("Customize",nullptr,ImGuiWindowFlags_NoDecoration|ImGuiWindowFlags_NoMove|ImGuiWindowFlags_NoSavedSettings);
        ImGui::BeginGroup();
        if(menu_art.logo)ImGui::Image((ImTextureID)(uintptr_t)menu_art.logo,ImVec2(326,62));
        else ImGui::TextColored(gold,"THE LION KING");
        ImGui::EndGroup();ImGui::SameLine(0,28);ImGui::BeginGroup();
        ImGui::TextColored(gold,"YOUR KINGDOM, YOUR RULES");
        ImGui::TextUnformatted("Choose your artwork, sound and gameplay.");
        ImGui::TextColored(muted,"The game is paused. Take your time.");
        ImGui::EndGroup();
        if(!has_menu_art)ImGui::TextWrapped("Menu artwork unavailable. Run Setup to restore it.");
        const char *tabs[]={"Artwork","Music & sound","Gameplay","Display","Advanced"};
        for(int i=0;i<5;i++){if(i)ImGui::SameLine();bool active=i==category;if(active)ImGui::PushStyleColor(ImGuiCol_Button,ImVec4(.38f,.23f,.10f,1));std::string tab=(active?"  ":"")+std::string(tabs[i]);if(ImGui::Button(tab.c_str())){category=i;selected=TlkResourcesFind(i==0?"graphics":i==1?"audio":i==2?"gameplay":i==3?"display":"game");}if(active){menu_art.MarkSelected();ImGui::PopStyleColor();}}
        ImGui::Spacing();float body=ImGui::GetContentRegionAvail().y-185;
        ImGui::BeginChild("Navigation",ImVec2(std::min(390.f,io.DisplaySize.x*.30f),body),ImGuiChildFlags_Borders);
        ImGui::SetWindowFontScale(.875f);
        ImGui::SetNextItemWidth(-1);ImGui::InputTextWithHint("##search","Find a choice...",search,sizeof search);
        ImGui::TextWrapped("%s",*search?"Search results":category==4?"Advanced choices":"Explore your kingdom");
        ImGui::Separator();int visible=0;std::string query=Lower(search);
        if(category==4 || !query.empty()){for(int i=1;i<TlkResourcesCount();i++)if(Parent(i)==0)Tree(i,query.empty()?category:-1,query,selected,visible);}
        else {int root=TlkResourcesFind(category==0?"graphics":category==1?"audio":category==2?"gameplay":"display");Tree(root,category,query,selected,visible);}
        if(!visible)ImGui::TextWrapped("No switchable choices match this search.");ImGui::EndChild();
        ImGui::SameLine();ImGui::BeginChild("Inspector",ImVec2(0,body),ImGuiChildFlags_Borders);
        if(selected!=title_node){std::string title="The Lion King - Customize your game - "+Path(selected);SDL_SetWindowTitle(window,title.c_str());title_node=selected;sound_variant=0;notice.clear();}
        const auto *node=TlkResourcesNode(selected);if(pictures.owner>=0&&pictures.owner!=selected)pictures.Clear();ImGui::PushTextWrapPos(0);
        ImGui::SetWindowFontScale(.75f);ImGui::TextWrapped("%s",Path(selected).c_str());ImGui::SetWindowFontScale(1.25f);ImGui::PushStyleColor(ImGuiCol_Text,gold);ImGui::TextWrapped("%s",Label(selected));ImGui::PopStyleColor();ImGui::SetWindowFontScale(1);
        ImGui::TextWrapped("%s",Explanation(node));ImGui::Spacing();
        int choice=TlkResourcesChoice(selected,1),resolved=TlkResourcesResolved(selected,1);
        bool pride_illustration=!strcmp(node->id,"graphics.interlevel.pride_lands");
        int pride_scene_source=TlkResourcesResolved(TlkResourcesFind("gameplay.levels.pride_lands.interlevel_scene"),1);
        for(int k=0;k<3;k++) {
            if(!selected&&!k)continue;if(k)ImGui::SameLine();
            const char *label=k==0?"Inherit":k==1?"SNES":"Genesis";bool active=choice==k;
            ImGui::PushStyleColor(ImGuiCol_Button,active?ImVec4(.38f,.23f,.10f,1):ImVec4(.13f,.07f,.17f,1));
            ImGui::BeginDisabled((k==2&&node->leaf&&!node->md_supported)||(pride_illustration&&k&&k!=pride_scene_source));
            if(ImGui::Button(label,ImVec2(174,44))){
                SetChoice(selected,k);pictures.Clear();notice.clear();int kept=0;
                if(k==TLK_SOURCE_MD&&!node->leaf)for(int i=1;i<TlkResourcesCount();i++) {
                    const auto *child=TlkResourcesNode(i);if(!child->leaf||child->md_supported||TlkResourcesResolved(i,1)!=TLK_SOURCE_MD)continue;
                    for(int p=child->parent;p>=0;p=TlkResourcesNode(p)->parent)if(p==selected){TlkResourcesSet(i,TLK_SOURCE_SNES);kept++;break;}
                }
                if(kept)notice=std::to_string(kept)+" SNES-only items were kept on SNES. Supported child overrides are preserved.";
            }
            if(active)menu_art.MarkSelected();ImGui::EndDisabled();ImGui::PopStyleColor();
        }
        if(pride_illustration)ImGui::TextColored(teal,"Scene artwork follows %s scene timing in this build.",Source(pride_scene_source));
        else ImGui::TextColored(teal,"Will use %s%s",Source(resolved),choice==0?" (inherited)":"");
        if(node->leaf&&!node->md_supported)ImGui::TextColored(gold,"This item currently supports SNES only.");
        palette_editor.Draw(ren,selected);
        int timing=ChangeTiming(selected);
        const char *when=timing==TLK_CHANGE_GAME?"This choice requires a game restart.":timing==TLK_CHANGE_LEVEL?"This choice restarts the current level.":"This choice takes effect when you resume.";
        if(!strcmp(node->id,"graphics.menus.publisher_cards"))when="After Apply & save: publisher cards change on the next launch. The current opening is not replayed.";
        ImGui::TextWrapped("%s",when);
        if(!node->leaf)ImGui::TextColored(muted,"Individual child overrides are kept. Restart depends on the children you change.");
        ImGui::Separator();
        if(!node->leaf||(Starts(node->id,"graphics")&&TlkSubjectPreviewSupported(node->id))) {
            if(ImGui::CollapsingHeader("About these choices"))DrawComparison(node);
        } else DrawComparison(node);
        ImGui::Separator();
        if(!notice.empty())ImGui::TextWrapped("%s",notice.c_str());
        bool visual_timing=!strcmp(node->id,"graphics.titles.pride_lands.duration")||!strcmp(node->id,"graphics.sprites.cinematics.timon.animation");
        bool artwork_branch=Starts(node->id,"graphics")&&!node->leaf;
        int picture_node=selected;
        if(artwork_branch&&!TlkSubjectPreviewSupported(node->id)) {
            static int example_branch=-1,example=-1;auto examples=ArtworkExamples(selected);
            if(example_branch!=selected||std::find(examples.begin(),examples.end(),example)==examples.end()){
                example_branch=selected;example=examples.empty()?-1:examples[0];pictures.Clear();
            }
            if(example>=0){ImGui::TextUnformatted("Example subject");ImGui::SetNextItemWidth(-1);}
            if(example>=0&&ImGui::BeginCombo("##example-subject",Path(example).c_str())) {
                for(int i:examples)if(ImGui::Selectable(Path(i).c_str(),i==example)){example=i;pictures.Clear();}
                ImGui::EndCombo();
            }
            picture_node=example;
        }
        const char *picture_id=picture_node>=0?TlkResourcesNode(picture_node)->id:"";
        if(!strcmp(node->id,"graphics.scenery.destiny_face_position")) {
            TlkBrowserDrawSkyPlacement();
        } else if(Starts(node->id,"graphics")&&!visual_timing&&picture_node>=0&&TlkSubjectPreviewSupported(picture_id)) {
            if(artwork_branch)ImGui::TextWrapped("Complete SNES and Genesis looks: drawings and colours together. Open an individual part below to compare it separately.");
            if(const char *note=TlkBrowserGalleryNote(picture_id))ImGui::TextWrapped("%s",note);
            if(TlkBrowserPlacementDescription(picture_id)&&!TlkSubjectPreviewSupported(picture_id)) {
                pictures.Clear();
                ImGui::TextColored(muted,"%s",TlkBrowserPlacementScene(picture_id));
                ImGui::TextWrapped("A comparison of this scene's placement is not available yet.");
            } else {
            ImGui::TextUnformatted("Compare this resource");
            if(TlkBrowserScenePicker(picture_id)) {
                static const char *levels[]={"Pride Lands","Can't Wait to Be King","Elephant Graveyard","The Stampede","Simba's Exile","Hakuna Matata","Simba's Destiny","Be Prepared","Simba's Return","Pride Rock"};
                int scene=(int)pictures.scene;if(ImGui::Combo("Example level",&scene,levels,10)){pictures.Clear();pictures.scene=(unsigned)scene;}
            }
            if(!strcmp(picture_id,"graphics.scenery.stampede_palette")) {
                pictures.scene=3;ImGui::TextColored(muted,"Scene: The Stampede");
            }
            if(Starts(picture_id,"graphics.sprites.animals.monkeys")) {
                const char *types[]={"King monkeys","Destiny monkeys"};int type=pictures.scene==6?1:0;
                if(ImGui::Combo("Example",&type,types,2)){pictures.Clear();pictures.scene=type?6:1;}
                if(!pictures.scene)pictures.scene=1;
            }
            pictures.Update(ren,picture_node,selected,artwork_branch);if(pictures.frames>1){ImGui::SetNextItemWidth(-1);int drawing=pictures.frame+1;ImGui::SliderInt("##drawing",&drawing,1,(int)pictures.frames,"Drawing %d");pictures.frame=drawing-1;}
            if(!pictures.data) {
                ImGui::TextWrapped("%s",pictures.message.c_str());
                if(!pictures.job&&ImGui::Button("Retry preview"))pictures.Clear();
            } else {
            bool placement=TlkBrowserSpecialGallery(picture_id)==17;
            if(placement)ImGui::TextUnformatted("Full scene canvas: compare Timon's placement.");
            else ImGui::Checkbox("Enlarge artwork",&focus_changes);
            float w=(ImGui::GetContentRegionAvail().x-12)/2;
            bool gallery_table=ImGui::BeginTable("artwork-images",2,ImGuiTableFlags_SizingStretchSame);
            for(int k=0;k<2;k++) {
                if(gallery_table)ImGui::TableNextColumn();else if(k)ImGui::SameLine();ImGui::BeginGroup();ImGui::TextColored(k?teal:gold,"%s",k?"GENESIS":"SNES");
                if(pictures.valid[k]&&pictures.image[k]) {
                    int x0=focus_changes&&!placement?pictures.x0:0,y0=focus_changes&&!placement?pictures.y0:0,x1=focus_changes&&!placement?pictures.x1:pictures.width,y1=focus_changes&&!placement?pictures.y1:pictures.height;
                    float h=std::min(230.f,w*(y1-y0)/(x1-x0)),iw=h*(x1-x0)/(y1-y0);
                    ImGui::Image((ImTextureID)(uintptr_t)pictures.image[k],ImVec2(iw,h),ImVec2(x0/(float)pictures.width,y0/(float)pictures.height),ImVec2(x1/(float)pictures.width,y1/(float)pictures.height));
                } else if(!TlkBrowserGallerySourceAvailable(picture_id,k))ImGui::TextWrapped("A picture preview for this version is not available yet. See the version explanation above.");
                else ImGui::TextWrapped("The image could not be displayed. Try preparing it again.");
                ImGui::EndGroup();
            }
            if(gallery_table)ImGui::EndTable();
            if(pictures.frames)ImGui::TextColored(muted,"Sample drawings. Drag the slider to inspect other poses.");
            if(pictures.same)ImGui::TextWrapped("This choice produces no visible change for this drawing with your other selections.");
            }
            }
        } else if(Starts(node->id,"audio")) {
            ImGui::TextUnformatted("Listen before choosing");int track=Track(selected);
            if(track>=0){
                if(!node->leaf)ImGui::TextColored(muted,"Example: %s",Path(TlkResourcesFind(tracks[track].id)).c_str());
                bool native=track<10||track==12||track==13||track==16||track==17;
                ImGui::BeginDisabled(!native);if(ImGui::Button("Listen to SNES"))audio.Play(TLK_SOURCE_SNES,track);ImGui::EndDisabled();
                ImGui::SameLine();if(ImGui::Button("Listen to Genesis"))audio.Play(TLK_SOURCE_MD,track);
                if(!native)ImGui::TextColored(muted,"SNES preview not available yet; this is not a silence notice.");
                ImGui::TextColored(muted,"Listen to the original soundtracks without changing your current game.");
            } else if(SoundCue(selected)>=0) {
                std::vector<int> variants;for(unsigned i=0;i<sizeof browser_sounds/sizeof *browser_sounds;i++)if(!strcmp(browser_sounds[i].id,node->id))variants.push_back((int)i);
                if(sound_variant>=(int)variants.size())sound_variant=0;
                if(variants.size()>1&&ImGui::BeginCombo("Sound",browser_sounds[variants[sound_variant]].name?browser_sounds[variants[sound_variant]].name:"Main cue")){
                    for(unsigned v=0;v<variants.size();v++)if(ImGui::Selectable(browser_sounds[variants[v]].name?browser_sounds[variants[v]].name:"Main cue",sound_variant==(int)v))sound_variant=(int)v;ImGui::EndCombo();
                }
                int cue=variants[sound_variant];const auto &sound=browser_sounds[cue];
                if(ImGui::Button("Listen to SNES"))audio.Play(TLK_SOURCE_SNES,-1,cue);
                ImGui::SameLine();if(ImGui::Button("Listen to Genesis"))audio.Play(TLK_SOURCE_MD,-1,cue);
                if(!sound.selector)ImGui::TextColored(muted,"Genesis: no separate cue for this action.");
                if(sound.event==-1)ImGui::TextColored(muted,"SNES: no separate cue for this action.");
                if(sound.event==-2)ImGui::TextColored(muted,"SNES: scene preview not available yet; this is not a silence notice.");
            } else ImGui::TextWrapped("Choose an individual sound below to listen. A few complete cinematic recordings still need their own samples.");
            if(ImGui::Button("Stop sample"))audio.Stop();ImGui::TextWrapped("%s",audio.message.c_str());
            if(!audio.waveform.empty())ImGui::PlotHistogram("##waveform",audio.waveform.data(),(int)audio.waveform.size(),0,"5 SECOND SAMPLE",0,1,ImVec2(-1,80));
        } else if(!strcmp(node->id,"display.viewport")) {
            float w=ImGui::GetContentRegionAvail().x;
            ImGui::TextUnformatted("SNES 256 columns / Genesis 320 columns");
            auto *d=ImGui::GetWindowDrawList();auto p=ImGui::GetCursorScreenPos();
            d->AddRectFilled(p,ImVec2(p.x+w,p.y+130),IM_COL32(32,75,70,255),8);
            d->AddRect(ImVec2(p.x+w*.1f,p.y),ImVec2(p.x+w*.9f,p.y+130),IM_COL32(240,184,87,255),8,0,3);
            ImGui::Dummy(ImVec2(w,140));ImGui::TextWrapped("Genesis scrolling scenes show more of the world. Stampede retains its reviewed 256-column view.");
        }
        if(artwork_branch)ArtworkChildren(selected,selected);
        ImGui::Spacing();if(category==4&&*node->scope&&ImGui::CollapsingHeader("Implementation details"))ImGui::TextWrapped("%s",node->scope);
        if(category==4&&ImGui::CollapsingHeader("Details")){ImGui::TextWrapped("Resource: %s",node->id);ImGui::Text("Applied: %s",Source(TlkResourcesResolved(selected,0)));ImGui::TextWrapped("Explicit child choices override their parent. Saving a branch preserves those child overrides.");}
        ImGui::PopTextWrapPos();ImGui::EndChild();ImGui::Spacing();
        char reason[256];int blocked=TlkResourcesValidate(reason,sizeof reason);
        ImGui::TextColored(muted,"Preset: %s",presets.Label().c_str());
        std::string restart_reason;int pending_timing=PendingChangeTiming(restart_reason);
        if(blocked)ImGui::TextColored(gold,"%s",reason);
        else if(!TlkResourcesDirty())ImGui::TextColored(muted,"Your saved choices are up to date.");
        else {
            ImGui::PushStyleColor(ImGuiCol_Text,pending_timing==TLK_CHANGE_LIVE?muted:gold);
            ImGui::TextWrapped("%s",pending_timing==TLK_CHANGE_GAME?"Your pending choices require a game restart.":pending_timing==TLK_CHANGE_LEVEL?"Apply will restart the current level, including your other pending choices.":"All pending choices take effect when you resume.");
            if(!restart_reason.empty()){ImGui::SetWindowFontScale(.75f);ImGui::TextWrapped("Restart required by: %s",restart_reason.c_str());ImGui::SetWindowFontScale(1);}
            ImGui::PopStyleColor();
        }
        ImGui::BeginDisabled(blocked||!TlkResourcesDirty());
        const char *apply_label=pending_timing==TLK_CHANGE_LEVEL?"Save & restart":"Apply & save";
        if(ImGui::Button(apply_label,ImVec2(260,40))&&TlkResourcesApply()){result=1;running=false;}
        ImGui::EndDisabled();ImGui::SameLine();if(ImGui::Button("Undo changes",ImVec2(240,40))){TlkResourcesRevert();presets.loaded=presets.Match(BrowserPresets::Choices(0));pictures.Clear();notice.clear();}
        ImGui::SameLine();if(ImGui::Button("Presets",ImVec2(180,40)))ImGui::OpenPopup("Choose a starting point");
        if(ImGui::BeginPopup("Choose a starting point")) {
            if(ImGui::MenuItem("Save current choices as new preset...")){preset_name[0]=0;preset_error.clear();create_preset=true;}
            if(ImGui::MenuItem("Manage presets...")){presets.open=true;presets.message.clear();}
            ImGui::Separator();ImGui::TextUnformatted("Your presets");
            auto custom_presets=BrowserPresets::List(preset_directory);
            if(custom_presets.empty())ImGui::TextDisabled("No custom presets yet");
            for(const auto &name:custom_presets) {
                ImGui::PushID(name.c_str());
                if(ImGui::MenuItem(name.c_str())){if(BrowserPresets::Load(preset_directory,name,notice)){presets.Refresh();presets.loaded=name;}pictures.Clear();}
                ImGui::PopID();
            }
            ImGui::Separator();ImGui::TextUnformatted("Built-in starting points");
            if(ImGui::MenuItem("All SNES")){TlkResourcesDefaults();presets.loaded.clear();pictures.Clear();}
            if(ImGui::MenuItem("Available Genesis")){TlkResourcesMdPreset();presets.loaded.clear();pictures.Clear();}
            if(ImGui::MenuItem("SNES artwork / Genesis gameplay & sound")) {
                presets.loaded.clear();
                TlkResourcesMdPreset();int gfx=TlkResourcesFind("graphics");TlkResourcesSet(gfx,TLK_SOURCE_SNES);
                for(int i=1;i<TlkResourcesCount();i++)if(Starts(TlkResourcesNode(i)->id,"graphics."))
                    TlkResourcesSet(i,strstr(TlkResourcesNode(i)->id,"death_motion")?TLK_SOURCE_MD:TLK_SOURCE_INHERIT);
                pictures.Clear();
            }
            ImGui::EndPopup();
        }
        if(create_preset){ImGui::OpenPopup("Save a custom preset");create_preset=false;}
        if(ImGui::BeginPopupModal("Save a custom preset",nullptr,ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::TextUnformatted("Keep all current resource choices, including unsaved changes.");
            ImGui::TextUnformatted("This saves a preset without applying changes to your game.");
            if(ImGui::IsWindowAppearing())ImGui::SetKeyboardFocusHere();
            ImGui::SetNextItemWidth(480);bool enter=ImGui::InputText("Name",preset_name,sizeof preset_name,ImGuiInputTextFlags_EnterReturnsTrue);
            ImGui::TextUnformatted("Letters, numbers, spaces, - and _ (up to 64 characters).");
            if(!preset_error.empty())ImGui::TextWrapped("%s",preset_error.c_str());
            if(ImGui::Button("Save preset")||enter){
                if(BrowserPresets::Save(preset_directory,preset_name,preset_error)){notice=preset_error;presets.loaded=preset_name;presets.Refresh();ImGui::CloseCurrentPopup();}
            }
            ImGui::SameLine();if(ImGui::Button("Cancel"))ImGui::CloseCurrentPopup();
            ImGui::EndPopup();
        }
        bool refresh_pictures=false;presets.Draw(window,refresh_pictures);if(refresh_pictures)pictures.Clear();
        ImGui::SameLine();if(ImGui::Button("Close",ImVec2(140,40)))close_request=true;
        if(close_request){if(TlkResourcesDirty())ImGui::OpenPopup("Discard unsaved choices?");else running=false;close_request=false;}
        if(ImGui::BeginPopupModal("Discard unsaved choices?",nullptr,ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::TextUnformatted("Your saved profile has not changed.");
            if(ImGui::Button("Keep editing"))ImGui::CloseCurrentPopup();ImGui::SameLine();
            if(ImGui::Button("Discard & close")){TlkResourcesRevert();running=false;}ImGui::EndPopup();
        }
        ImGui::End();ImGui::Render();SDL_SetRenderDrawColor(ren,13,8,30,255);SDL_RenderClear(ren);Render(ren,ImGui::GetDrawData());__real_SDL_RenderPresent(ren);
        SDL_Delay(8);
    }
    audio.Stop();pictures.Clear();palette_editor.Clear();TlkResourcesPreviewEnd();if(!result)TlkResourcesRevert();
    SDL_DestroyTexture(font_texture);ImGui_ImplSDL3_Shutdown();ImGui::DestroyContext();ImGui::SetCurrentContext(previous);
    SDL_DestroyTexture(menu_art.backdrop);menu_art.backdrop=nullptr;SDL_DestroyTexture(menu_art.logo);menu_art.logo=nullptr;SDL_DestroyTexture(menu_art.sun);menu_art.sun=nullptr;
    SDL_DestroyRenderer(ren);SDL_DestroyWindow(window);if(glwin&&gl)SDL_GL_MakeCurrent(glwin,gl);if(parent)SDL_RaiseWindow(parent);
    return result;
}
/* One desktop presentation for both game renderers. The ordinary host model
 * still owns settings, saving, binding capture, practice and quit confirmation. */
extern "C" int TlkMainSettingsOpen(SDL_Window *parent,RecompRuntimeUi *ui,void (*bind_event)(const SDL_Event *)) {
    ImGuiContext *previous=ImGui::GetCurrentContext();SDL_Window *glwin=SDL_GL_GetCurrentWindow();SDL_GLContext gl=SDL_GL_GetCurrentContext();
    SDL_Window *window=SDL_CreateWindow("The Lion King - Game settings",1280,900,SDL_WINDOW_RESIZABLE|SDL_WINDOW_HIGH_PIXEL_DENSITY);
    if(!window)return -1;SDL_SetWindowMinimumSize(window,1120,780);
    SDL_Renderer *ren=SDL_CreateRenderer(window,nullptr);if(!ren){SDL_DestroyWindow(window);return -1;}
    SDL_SetRenderVSync(ren,1);ImGuiContext *settings_context=ImGui::CreateContext();ImGui::SetCurrentContext(settings_context);Theme();auto &io=ImGui::GetIO();
    io.IniFilename=nullptr;io.LogFilename=nullptr;io.ConfigFlags|=ImGuiConfigFlags_NavEnableKeyboard|ImGuiConfigFlags_NavEnableGamepad;
    GenesisBrowserArt art;art.Load(ren);ImFontConfig fc;fc.SizePixels=20;fc.OversampleH=fc.OversampleV=1;fc.PixelSnapH=true;
    auto *font=io.Fonts->AddFontDefault(&fc);art.Font(io.Fonts,font);
    ImGui_ImplSDL3_InitForSDLRenderer(window,ren);
    unsigned char *pixels;int fw,fh;io.Fonts->GetTexDataAsRGBA32(&pixels,&fw,&fh);
    SDL_Texture *ft=SDL_CreateTexture(ren,SDL_PIXELFORMAT_ABGR8888,SDL_TEXTUREACCESS_STATIC,fw,fh);
    SDL_UpdateTexture(ft,nullptr,pixels,fw*4);SDL_SetTextureBlendMode(ft,SDL_BLENDMODE_BLEND);SDL_SetTextureScaleMode(ft,SDL_SCALEMODE_NEAREST);io.Fonts->SetTexID((ImTextureID)(uintptr_t)ft);
    int page=0,display_page=0;bool live=true,quit=false,binding=false;char resolution[128]={};std::string notice;
    const char *pages[]={"Display","Audio","Controls","Practice","About"};
    if(ui->in_section&&ui->section_index<ui->section_count){const char *s=ui->sections[ui->section_index];for(int i=0;i<5;i++)if(!strcmp(s,pages[i]))page=i;if(!strcmp(s,"Level select"))page=3;}
    auto &cb=ui->config.callbacks;
    auto save=[&](){if(cb.save)cb.save(cb.context);};
    while(live&&recomp_runtime_ui_is_open(ui)){
        SDL_Event ev;
        while(SDL_PollEvent(&ev)){
            if(binding&&(ev.type==SDL_EVENT_KEY_DOWN||ev.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN)){
                if(bind_event)bind_event(&ev);binding=false;continue;
            }
            if(ev.type==SDL_EVENT_KEY_DOWN&&(ev.key.key==SDLK_F11||(ev.key.key==SDLK_RETURN&&(ev.key.mod&SDL_KMOD_ALT)))){
                for(size_t i=0;i<ui->config.item_count;i++){const auto *item=ui->config.items+i;if(!strcmp(item->key,"tlk.fullscreen")){int on=0;if(cb.get_value&&cb.set_value&&cb.get_value(cb.context,item,&on)&&cb.set_value(cb.context,item,!on))save();}}
                continue;
            }
            ImGui_ImplSDL3_ProcessEvent(&ev);
            if(ev.type==SDL_EVENT_QUIT){quit=true;live=false;}
            if(ev.type==SDL_EVENT_WINDOW_CLOSE_REQUESTED&&ev.window.windowID==SDL_GetWindowID(window))live=false;
            if(ev.type==SDL_EVENT_KEY_DOWN&&(ev.key.key==SDLK_ESCAPE||ev.key.key==SDLK_F12||ev.key.key==SDLK_TAB)&&!io.WantTextInput)live=false;
            if(ev.type==SDL_EVENT_GAMEPAD_BUTTON_DOWN&&(ev.gbutton.button==SDL_GAMEPAD_BUTTON_EAST||ev.gbutton.button==SDL_GAMEPAD_BUTTON_START||ev.gbutton.button==SDL_GAMEPAD_BUTTON_GUIDE))live=false;
        }
        ImGui_ImplSDL3_NewFrame();ImGui::NewFrame();art.Backdrop(io.DisplaySize);
        ImGui::SetNextWindowPos(ImVec2(0,0));ImGui::SetNextWindowSize(io.DisplaySize);
        ImGui::Begin("Game settings",nullptr,ImGuiWindowFlags_NoDecoration|ImGuiWindowFlags_NoSavedSettings);
        if(art.logo)ImGui::Image((ImTextureID)(uintptr_t)art.logo,ImVec2(326,62));else ImGui::TextColored(gold,"THE LION KING");
        ImGui::SameLine(0,28);ImGui::BeginGroup();ImGui::TextColored(gold,"GAME SETTINGS");ImGui::TextUnformatted("Your adventure is paused.");ImGui::TextColored(muted,"Changes are saved as you make them.");ImGui::EndGroup();
        for(int i=0;i<5;i++){
            if(i)ImGui::SameLine();std::string label=(i==page?"  ":"")+std::string(pages[i]);
            if(ImGui::Button(label.c_str())){page=i;notice.clear();}
            if(page==i)art.MarkSelected();
        }
        if(page==0){const char *groups[]={"Window","Widescreen","Pixel style"};for(int i=0;i<3;i++){if(i)ImGui::SameLine();std::string group=(display_page==i?"  ":"")+std::string(groups[i]);if(ImGui::Button(group.c_str()))display_page=i;if(display_page==i)art.MarkSelected();}}
        ImGui::Spacing();float body=ImGui::GetContentRegionAvail().y-110;
        ImGui::BeginChild("Settings",ImVec2(0,body),ImGuiChildFlags_Borders);ImGui::PushTextWrapPos(0);
        if(page==0&&display_page==0){
            ImGui::TextColored(gold,"WINDOW AND PICTURE");
            ImGui::TextWrapped("Window size changes the size on your monitor. Widescreen reveals more of the level; it does not stretch the artwork.");
        }
        if(page==2)ImGui::TextWrapped(binding?"Press a key or controller button. Escape cancels.":"Choose a game button, then press its new key or controller button. The game menu determines each button's action.");
        std::vector<size_t> order;
        for(size_t i=0;i<ui->config.item_count;i++)if(!strcmp(ui->config.items[i].key,"tlk.window_size"))order.push_back(i);
        for(size_t i=0;i<ui->config.item_count;i++)if(!strcmp(ui->config.items[i].key,"tlk.screen_effects"))order.push_back(i);
        for(size_t i=0;i<ui->config.item_count;i++)if(strcmp(ui->config.items[i].key,"tlk.window_size")&&strcmp(ui->config.items[i].key,"tlk.screen_effects"))order.push_back(i);
        for(size_t i:order){
            const auto *item=ui->config.items+i;const char *key=item->key;
            if(!key||!item->section)continue;
            bool display=!strcmp(item->section,"Display")||!strcmp(item->section,"Graphics");
            bool show=page==0?display:page==1?!strcmp(item->section,"Audio"):page==2?!strcmp(item->section,"Controls"):page==3?(!strcmp(item->section,"Level select")||!strcmp(item->section,"Practice")):!strcmp(item->section,"About");
            if(page==0){bool layout=!strcmp(key,"tlk.widescreen")||!strcmp(key,"tlk.widescreen_hud")||!strcmp(key,"tlk.widescreen_enemies")||!strcmp(key,"tlk.aspect");bool pixels=!strcmp(key,"tlk.screen_effects")||!strcmp(key,"tlk.shader")||!strcmp(key,RECOMP_RUNTIME_UI_KEY_LINEAR_FILTER)||!strcmp(key,RECOMP_RUNTIME_UI_KEY_INTEGER_SCALE);if(display_page==0&&(layout||pixels))continue;if(display_page==1&&!layout)continue;if(display_page==2&&!pixels)continue;}
            if(!show||!strcmp(key,"tlk.hd_mode7")||!strcmp(key,RECOMP_RUNTIME_UI_KEY_MENU_DIM)||!strcmp(key,RECOMP_RUNTIME_UI_KEY_MENU_OPACITY))continue;
            if(page==4&&!strcmp(key,"tlk.about"))continue;
            ImGui::PushID((int)i);bool enabled=!binding&&(!cb.is_enabled||cb.is_enabled(cb.context,item));
            const char *label=item->label,*description=item->description;
            if(!strcmp(key,RECOMP_RUNTIME_UI_KEY_WINDOW_SCALE)){
                int mode=0;for(size_t j=0;j<ui->config.item_count;j++)if(!strcmp(ui->config.items[j].key,"tlk.widescreen")&&cb.get_value)cb.get_value(cb.context,ui->config.items+j,&mode);
                label=mode==3?"Pixel zoom":"Quick window size";
                description=mode==3?"Size of the game pixels. Smaller values show more level without resizing the window.":"Choose a multiple of the original height. This replaces the custom size above.";
            }
            if(!strcmp(key,"tlk.widescreen")){label="Level view";description="Original keeps the console view. 16:9 and 21:9 reveal more at the sides. Adaptive follows your window's shape. Some special scenes keep their original framing.";}
            if(!strcmp(key,"tlk.widescreen_hud")){label="Health and lives placement";description="Place the meters at the edges of the wider picture, or keep their original positions.";}
            if(!strcmp(key,"tlk.widescreen_enemies")){label="Widescreen gameplay";description="Original keeps the console camera and enemy timing while drawing a wider picture. Extended adjusts the camera and activation for the wider view, changing gameplay and recorded walkthroughs.";}
            if(!strcmp(key,"tlk.aspect")){label="Original picture shape";description="Used for the original console view. TV keeps the classic television shape; 8:7 uses square game pixels; 1:1 makes the whole frame square. Widescreen uses Level view instead.";}
            if(!strcmp(key,"tlk.vsync")){label="Match monitor refresh";description="Synchronizes presentation with your monitor. The game still uses its original update rate.";}
            char effects_state[32]={};
            const RecompRuntimeUiItem *effects_item=nullptr;
            if(!strcmp(key,"tlk.shader")||!strcmp(key,"tlk.screen_effects")){
                for(size_t j=0;j<ui->config.item_count;j++)if(!strcmp(ui->config.items[j].key,"tlk.screen_effects")){effects_item=ui->config.items+j;break;}
                if(effects_item&&cb.get_text)cb.get_text(cb.context,effects_item,effects_state,sizeof effects_state);
            }
            if(!strcmp(key,"tlk.screen_effects")){
                label="Enable screen effects";
                description=!strcmp(effects_state,"restart")?"Saved. Close and reopen the game to apply this change.":!strcmp(effects_state,"unavailable")?"Screen effects could not start on this computer. You can keep playing with this option off.":"Allows CRT, LCD and other picture effects. Close and reopen the game after changing this option.";
            }
            if(!strcmp(key,"tlk.shader")){
                label="Screen effect";enabled=!binding;
                description=!strcmp(effects_state,"active")?"Choose a look. Changes apply when you return to the game.":!strcmp(effects_state,"restart")?"Your choice is saved. Close and reopen the game to finish changing screen effects.":!strcmp(effects_state,"unavailable")?"Your choice is saved, but screen effects could not start on this computer.":"Choose a look, then enable screen effects above and close and reopen the game.";
            }
            if(!strcmp(key,RECOMP_RUNTIME_UI_KEY_LINEAR_FILTER)){label="Smooth pixels";description="Softens pixel edges. Turn off for crisp original artwork.";}
            if(!strcmp(key,RECOMP_RUNTIME_UI_KEY_INTEGER_SCALE))description="Keeps pixels at whole-number sizes. Borders may remain around the picture.";
            if(!strcmp(key,"tlk.window_size")){
                if(!*resolution&&cb.get_text)cb.get_text(cb.context,item,resolution,sizeof resolution);
                ImGui::TextColored(gold,"Custom window size");ImGui::SetNextItemWidth(300);
                bool enter=ImGui::InputText("##resolution",resolution,sizeof resolution,ImGuiInputTextFlags_EnterReturnsTrue);ImGui::SameLine();
                if((ImGui::Button("Apply size")||enter)&&cb.set_text){if(cb.set_text(cb.context,item,resolution)){save();notice="Window size saved. Fullscreen uses your monitor; this size is kept for windowed play.";}else notice="Enter width x height, between 320 x 224 and 7680 x 4320.";}
                ImGui::TextWrapped("%s",description);
                const RecompRuntimeUiItem *view=nullptr;
                for(size_t j=0;j<ui->config.item_count;j++)if(!strcmp(ui->config.items[j].key,"tlk.widescreen"))view=ui->config.items+j;
                int mode=0;if(view&&cb.get_value&&cb.get_value(cb.context,view,&mode)){
                    bool fit=mode==3;
                    if(ImGui::Checkbox("Widescreen: show more of the level",&fit)&&cb.set_value){
                        if(cb.set_value(cb.context,view,fit?3:0))save();
                        notice=fit?"Resize the window to reveal more level in both directions. Pixel zoom controls the drawing size; fixed scenes retain their framing.":"Original console framing selected. Fixed wide views are available under Widescreen.";
                    }
                }
                ImGui::TextWrapped("Resize width or height to reveal more level at the selected pixel zoom. Special scenes keep their original framing.");
                ImGui::Separator();ImGui::PopID();continue;
            }
            ImGui::BeginDisabled(!enabled);
            int value=0;bool changed=false;
            if(item->type==RECOMP_RUNTIME_UI_ACTION){
                if(ImGui::Button(label)&&cb.run_action){cb.run_action(cb.context,item);if(!strcmp(key,"tlk.bind"))binding=true;if(!strcmp(key,"tlk.start_level"))live=false;}
            }else if(cb.get_value&&cb.get_value(cb.context,item,&value)){
                ImGui::TextColored(gold,"%s",label);ImGui::SetNextItemWidth(std::min(450.f,ImGui::GetContentRegionAvail().x));
                if(item->type==RECOMP_RUNTIME_UI_BOOL){bool on=value!=0;changed=ImGui::Checkbox("Enabled",&on);value=on;}
                else if(item->type==RECOMP_RUNTIME_UI_CHOICE){
                    const bool wide_rules=!strcmp(key,"tlk.widescreen_enemies"),view_mode=!strcmp(key,"tlk.widescreen");
                    const char *view_names[]={"Original console view","16:9","21:9","Fit window (free size)"};
                    const char *shown=view_mode&&value>=0&&value<4?view_names[value]:wide_rules?(value?"Extended camera and enemies":"Original camera and enemies"):value>=item->minimum&&(size_t)(value-item->minimum)<item->choice_count?item->choices[value-item->minimum]:"Custom";
                    if(ImGui::BeginCombo("##value",shown)){for(size_t k=0;k<item->choice_count;k++)if(ImGui::Selectable(view_mode&&k<4?view_names[k]:wide_rules?(k?"Extended camera and enemies":"Original camera and enemies"):item->choices[k],value==item->minimum+(int)k)){value=item->minimum+(int)k;changed=true;}ImGui::EndCombo();}
                }else changed=ImGui::SliderInt("##value",&value,item->minimum,item->maximum);
                if(changed&&cb.set_value){int saved=cb.set_value(cb.context,item,value);if(saved)save();if(saved&&!strcmp(key,"tlk.screen_effects"))notice="Saved. Close and reopen the game to apply this change.";if(!strcmp(key,RECOMP_RUNTIME_UI_KEY_WINDOW_SCALE))*resolution=0;}
            }
            ImGui::EndDisabled();ImGui::TextWrapped("%s",description?description:"");ImGui::Separator();ImGui::PopID();
        }
        if(page==4){
            ImGui::TextWrapped("Ultimate Edition combines SNES and Genesis artwork, sound and gameplay choices.");
            ImGui::TextColored(gold,"Based on TLKRecomp by Alejandro AR (kinduff).");
            ImGui::TextLinkOpenURL("Upstream TLKRecomp", "https://github.com/kinduff/TLKRecomp");
            ImGui::SameLine();ImGui::TextLinkOpenURL("kinduff.com (upstream author)", "https://kinduff.com");
            ImGui::TextWrapped("Runtime components: snesrecomp and recomp-ui. Original game: Disney / Virgin Interactive and its original developers. Component copyright and license notices are included with the game.");
        }
        ImGui::PopTextWrapPos();ImGui::EndChild();
        if(!notice.empty())ImGui::TextWrapped("%s",notice.c_str());else if(ui->status_frames)ImGui::TextColored(gold,"%s",ui->status);else ImGui::TextColored(muted,"Esc: return to the game");
        if(ImGui::Button("Resume",ImVec2(180,40)))live=false;
        ImGui::SameLine();if(ImGui::Button("Customize game",ImVec2(280,40))){TlkResourcesRevert();if(TlkVisualResourcesOpen(window)==1)TlkResourcesHostApplied();}
        ImGui::SameLine();if(ImGui::Button("Quit",ImVec2(140,40))){
            for(size_t i=0;i<ui->config.item_count;i++)if(!strcmp(ui->config.items[i].key,RECOMP_RUNTIME_UI_KEY_QUIT)&&cb.run_action){if(cb.run_action(cb.context,ui->config.items+i)){quit=true;live=false;}}
        }
        ImGui::End();ImGui::Render();SDL_SetRenderDrawColor(ren,13,8,30,255);SDL_RenderClear(ren);Render(ren,ImGui::GetDrawData());__real_SDL_RenderPresent(ren);SDL_Delay(8);
        recomp_runtime_ui_advance_status(ui,io.DeltaTime*60);
    }
    if(binding&&bind_event){SDL_Event cancel={};cancel.type=SDL_EVENT_KEY_DOWN;cancel.key.down=true;cancel.key.key=SDLK_ESCAPE;bind_event(&cancel);}
    recomp_runtime_ui_close(ui);SDL_DestroyTexture(ft);ImGui_ImplSDL3_Shutdown();ImGui::DestroyContext();ImGui::SetCurrentContext(previous);
    SDL_DestroyTexture(art.backdrop);art.backdrop=nullptr;SDL_DestroyTexture(art.logo);art.logo=nullptr;SDL_DestroyTexture(art.sun);art.sun=nullptr;
    SDL_DestroyRenderer(ren);SDL_DestroyWindow(window);if(glwin&&gl)SDL_GL_MakeCurrent(glwin,gl);if(parent)SDL_RaiseWindow(parent);return quit?0:1;
}
/* Isolated diagnostics only; no media files or live-game mutation. Exercises
 * the exact audition path and its complete backend restore for every cue. */
extern "C" void TlkBrowserAuditEffects(const char *path) {
    FILE *f=std::fopen(path,"w");if(!f)return;Audition audio;
    for(unsigned i=0;i<sizeof browser_sounds/sizeof *browser_sounds;i++) {
        audio.Play(TLK_SOURCE_MD,-1,(int)i);float peak=audio.waveform.empty()?0:*std::max_element(audio.waveform.begin(),audio.waveform.end());
        std::fprintf(f,"%u\t%s\t%d\t%.6f\t%s\n",i,browser_sounds[i].id,browser_sounds[i].selector,peak,audio.message.c_str());std::fflush(f);audio.Stop();
    }
    std::fclose(f);
}

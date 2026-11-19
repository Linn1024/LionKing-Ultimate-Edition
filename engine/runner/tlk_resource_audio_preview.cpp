/* On-demand five-second native soundtrack previews. An isolated, hidden copy
 * of the installed player enters the level normally and clones its loaded SPC.
 * No state, source selection or audio device in the current game is changed.
 * Cache files are short media previews under the user's application data. */
#define NOMINMAX
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include "tlk_resource_audio_preview.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cctype>
#include <string>
#include <vector>
extern "C" {
#include "tlk_wide.h"
#include "snes/apu.h"
#include "snes/ppu.h"
extern Snes *g_snes;
extern uint8_t g_ram[0x20000];
void TlkBrowserAuditEffects(const char *path);
void RtlApuLock(void);
void RtlApuUnlock(void);
bool __real_TlkWideEndFrame(const uint8_t *stock);
}
#include "tlk_md_assets.h"
#include "tlk_resources.h"
#include "tlk_browser_gallery.h"
namespace {
std::wstring Wide(const std::string &s){int n=MultiByteToWideChar(CP_UTF8,0,s.c_str(),-1,nullptr,0);std::wstring w(n? n-1:0,0);if(n>1)MultiByteToWideChar(CP_UTF8,0,s.c_str(),-1,&w[0],n);return w;}
std::wstring Quote(const std::wstring &s){std::wstring out=L"\"";unsigned slash=0;for(wchar_t c:s){if(c==L'\\'){slash++;continue;}if(c==L'\"')out.append(slash*2+1,L'\\');else out.append(slash,L'\\');slash=0;out+=c;}out.append(slash*2,L'\\');return out+L'\"';}
struct Job {HANDLE process=nullptr;Uint64 began=0;std::string cache,temp,profile,config,workspace;};
void Remove(const std::string &path){if(!path.empty())SDL_RemovePath(path.c_str());}
void Reason(char *out,size_t size,const char *s){if(out&&size)std::snprintf(out,size,"%s",s);}
bool ValidWave(const char *path,SDL_AudioSpec *spec,Uint8 **samples,Uint32 *bytes) {
    if(!SDL_LoadWAV(path,spec,samples,bytes))return false;
    if(spec->freq==32000&&spec->channels==2&&spec->format==SDL_AUDIO_S16&&*bytes==32000*2*5*2)return true;
    SDL_free(*samples);*samples=nullptr;return false;
}
bool NativeSamples(std::vector<int16_t> &pcm) {
    if(!g_snes||!g_snes->apu)return false;Apu *copy=apu_init();if(!copy)return false;
    RtlApuLock();Spc *spc=copy->spc;Dsp *dsp=copy->dsp;void *shadow=dsp->shadow;
    *copy=*g_snes->apu;copy->spc=spc;copy->dsp=dsp;*spc=*g_snes->apu->spc;spc->apu=copy;
    *dsp=*g_snes->apu->dsp;dsp->apu_ram=copy->ram;dsp->shadow=shadow;RtlApuUnlock();
    /* Preserve queued CPU->SPC bus events in the clone: a just-submitted song
     * start can still be waiting for its original SPC timestamp. */
    copy->dsp->sampleRead=copy->dsp->sampleWrite;pcm.resize(32000*2*5);
    for(unsigned pos=0;pos<32000*5;pos+=256){for(unsigned n=0;n<256*32;n++)apu_cycle(copy);dsp_getSamples(copy->dsp,pcm.data()+pos*2,std::min(256u,32000*5-pos));}
    apu_free(copy);return true;
}
bool Wave(const char *path,const std::vector<int16_t>&pcm) {
    SDL_IOStream *f=SDL_IOFromFile(path,"wb");if(!f)return false;
    uint8_t h[44]={};std::memcpy(h,"RIFF",4);std::memcpy(h+8,"WAVEfmt ",8);std::memcpy(h+36,"data",4);
    auto put=[&](int at,unsigned v,int bytes){for(int i=0;i<bytes;i++)h[at+i]=(uint8_t)(v>>(i*8));};
    put(4,36+(unsigned)pcm.size()*2,4);put(16,16,4);put(20,1,2);put(22,2,2);put(24,32000,4);put(28,128000,4);put(32,4,2);put(34,16,2);put(40,(unsigned)pcm.size()*2,4);
    bool ok=SDL_WriteIO(f,h,sizeof h)==sizeof h&&SDL_WriteIO(f,pcm.data(),pcm.size()*2)==pcm.size()*2;SDL_CloseIO(f);return ok;
}
}
extern "C" bool __wrap_TlkWideEndFrame(const uint8_t *stock) {
    bool result=__real_TlkWideEndFrame(stock);
    static const char *target=SDL_getenv("TLK_BROWSER_NATIVE_LEVEL"),*path=SDL_getenv("TLK_BROWSER_NATIVE_OUT");
    static unsigned stable=0;
    static const char *gallery=SDL_getenv("TLK_BROWSER_GALLERY_ID"),*effect=SDL_getenv("TLK_BROWSER_NATIVE_EVENT");
    if(!target||!path)return result;
    int level=std::atoi(target);if((level<0||level>13)&&level!=14)std::exit(92);
    unsigned current=g_ram[0x1ff9e]|(unsigned)g_ram[0x1ff9f]<<8;
    unsigned descriptor=g_ram[0xdf]|(unsigned)g_ram[0xe0]<<8|(unsigned)g_ram[0xe1]<<16;
    bool lit=g_snes&&g_snes->ppu&&g_snes->ppu->inidisp==15;
    unsigned health=g_ram[0x2004]|(unsigned)g_ram[0x2005]<<8;
    unsigned root=g_ram[0x6e]|(unsigned)g_ram[0x6f]<<8;
    unsigned action=root<=0xffa0?g_ram[root+48]|(unsigned)g_ram[root+49]<<8|(unsigned)g_ram[root+50]<<16:0;
    int gallery_kind=gallery?TlkBrowserSpecialGallery(gallery):0;
    if(gallery_kind==5||gallery_kind==7||gallery_kind==8) {
        auto key=[](SDL_Keycode code,bool down){SDL_Event e={};e.type=down?SDL_EVENT_KEY_DOWN:SDL_EVENT_KEY_UP;
            e.key.type=(SDL_EventType)e.type;e.key.key=code;e.key.scancode=SDL_GetScancodeFromKey(code,nullptr);e.key.down=down;SDL_PushEvent(&e);};
        static unsigned title_age,options_age;
        if(descriptor==0xc005ab&&action==0xc465f0&&lit) {
            ++title_age;if(title_age==30)key(SDLK_DOWN,true);if(title_age==34)key(SDLK_DOWN,false);
            if(title_age==46)key(SDLK_RETURN,true);if(title_age==50)key(SDLK_RETURN,false);
        }
        if(action!=0xc465f0&&title_age>=46&&title_age<50){key(SDLK_RETURN,false);title_age=50;}
        if(gallery_kind==7&&descriptor==0xc005ab&&action==0xc4690e&&lit){
            ++options_age;for(unsigned n=0;n<3;n++){if(options_age==30+n*16)key(SDLK_DOWN,true);if(options_age==34+n*16)key(SDLK_DOWN,false);}
            if(options_age==78)key(SDLK_Z,true);if(options_age==82)key(SDLK_Z,false);
        }
        if(action!=0xc4690e&&options_age>=78&&options_age<82){key(SDLK_Z,false);options_age=82;}
        if(gallery_kind==8&&descriptor==0xc005ab&&action==0xc4690e&&lit){
            static const SDL_Keycode sequence[]={SDLK_Z,SDLK_A,SDLK_W,SDLK_W,SDLK_S};
            ++options_age;for(unsigned n=0;n<5;n++){if(options_age==30+n*30)key(sequence[n],true);if(options_age==34+n*30)key(sequence[n],false);}
        }
        if(gallery_kind==8&&action!=0xc4690e&&options_age>=150){key(SDLK_S,false);options_age=154;}
    }
    if((effect && std::atoi(effect)==256)||gallery_kind==9||gallery_kind==17) {
        /* Enter the actual opening by its ordinary Start input. The title
         * sound bank is not the loaded Timon speech bank. Child process only. */
        static unsigned start_input,speech_age,title_age;
        auto key=[](bool down){SDL_Event e={};e.type=down?SDL_EVENT_KEY_DOWN:SDL_EVENT_KEY_UP;
            e.key.type=(SDL_EventType)e.type;e.key.key=SDLK_RETURN;e.key.scancode=SDL_SCANCODE_RETURN;e.key.down=down;SDL_PushEvent(&e);};
        if(!start_input && descriptor==0xc005ab && action==0xc465f0 && lit && ++title_age>=120){key(true);start_input=1;}
        else if(start_input && start_input<8){if(++start_input==8)key(false);}
        unsigned actor_action=g_ram[0xb243]|(unsigned)g_ram[0xb244]<<8|(unsigned)g_ram[0xb245]<<16;
        if(SDL_getenv("TLK_BROWSER_AUDIT")) {static unsigned previous=~0u;
            if(previous!=actor_action){previous=actor_action;std::fprintf(stderr,"timon_preview_context scene=%06x root=%06x player=%06x phase=%u input=%u lit=%u\n",descriptor,action,actor_action,g_ram[0xb241],start_input,lit);std::fflush(stderr);}}
        if(descriptor==0xc005ab && actor_action==0xc47146 && g_ram[0xb241]==2 && ++speech_age>=2) {
            if(gallery_kind==9||gallery_kind==17){bool ok=BrowserGallery::Write(gallery,path);std::exit(ok?0:94);}
            std::vector<int16_t> pcm;bool ok=NativeSamples(pcm)&&Wave(path,pcm);
            std::fprintf(stderr,"native_preview scene=opening_timon loaded_voice=1 samples=%u\n",(unsigned)pcm.size()/2);std::exit(ok?0:93);
        }
        return result;
    }
    bool ready=result&&(current==(unsigned)level||(level==14&&current==0))&&(level==14?descriptor==0xc005ab&&lit&&action==0xc465f0:
        level==3?descriptor==0xc0041d&&lit&&health>0&&health<100:TlkWideFrameStageActive());
    if(gallery_kind==5||gallery_kind==7||gallery_kind==8)ready=result&&descriptor==0xc005ab&&lit&&action==(gallery_kind==5?0xc4690e:gallery_kind==7?0xc46b68:0xc46e59);
    if(gallery_kind==6)ready=result&&descriptor==0xc0057b&&lit&&action==0xc462f6&&g_ram[root+46]==0;
    stable=ready?stable+1:0;
    if(stable>=120&&SDL_getenv("TLK_BROWSER_AUDIT_MD")){TlkBrowserAuditEffects(SDL_getenv("TLK_BROWSER_AUDIT_MD"));std::exit(0);}
    if(effect && (stable==85 || stable==120)) {
        unsigned offset=g_ram[0x1f6d]|(unsigned)g_ram[0x1f6e]<<8;
        if(offset>0x40 || g_ram[0x1fbf]!=255 || g_ram[0x1fc0]!=255){stable--;return result;}
        unsigned at=0x1f6f+offset;
        if(stable==85){uint8_t packet[4]={1,0x82,0xe0,0};std::memcpy(g_ram+at,packet,4);offset+=4;}
        else {uint8_t packet[8]={2,(uint8_t)std::atoi(effect),0,0xe0,0,0x80,0x78,0};std::memcpy(g_ram+at,packet,8);offset+=8;}
        g_ram[0x1f6d]=(uint8_t)offset;g_ram[0x1f6e]=(uint8_t)(offset>>8);
    }
    if(gallery&&stable>=(gallery_kind==6?10:120)){bool ok=BrowserGallery::Write(gallery,path);std::exit(ok?0:94);}
    if(stable>=(effect?121u:120u)){std::vector<int16_t> pcm;bool ok=NativeSamples(pcm)&&Wave(path,pcm);std::fprintf(stderr,"native_preview level=%u descriptor=%06x stable=%u samples=%u\n",current,descriptor,stable,(unsigned)pcm.size()/2);std::exit(ok?0:93);}
    return result;
}
static void *Start(unsigned level,int event,const char *gallery,char *reason,size_t size) {
    if(level>13&&level!=14){Reason(reason,size,"A native sample for this scene is not available yet.");return nullptr;}
    const char *dir=SDL_GetPrefPath("LionKing","ResourcePreviews");
    if(!dir){Reason(reason,size,"Could not open the preview cache.");return nullptr;}
    Job *job=new Job;std::string root=dir;SDL_free((void*)dir);std::string key=gallery?std::string(gallery)+"-level"+std::to_string(level):"";for(char &c:key)if(!std::isalnum((unsigned char)c))c='-';
    if(gallery&&!std::strcmp(gallery,"graphics.ending_credits"))key+="-readable";
    job->cache=root+(gallery?"gallery-v7-"+key:"snes-457abe63-v4-level"+std::to_string(level)+(event>=0?"-cue"+std::to_string(event):""))+(gallery?".tlkg":".wav");
    SDL_AudioSpec spec;Uint8 *samples=nullptr;Uint32 bytes;
    SDL_PathInfo cached;if(gallery&&SDL_GetPathInfo(job->cache.c_str(),&cached)&&cached.size>20)return job;
    if(!gallery&&ValidWave(job->cache.c_str(),&spec,&samples,&bytes)){SDL_free(samples);return job;}
    job->workspace=root+"job-"+std::to_string(GetCurrentProcessId())+"-"+std::to_string(SDL_GetTicksNS());
    if(!SDL_CreateDirectory(job->workspace.c_str())){Reason(reason,size,"Could not create the preview workspace.");delete job;return nullptr;}
    job->temp=job->workspace+(gallery?"/sample.tlkg":"/sample.wav");job->profile=job->workspace+"/resources.ini";job->config=job->workspace+"/video.ini";
    auto file=[](const std::string&p,const char*text){SDL_IOStream*f=SDL_IOFromFile(p.c_str(),"wb");if(!f)return false;bool ok=SDL_WriteIO(f,text,std::strlen(text))==std::strlen(text);SDL_CloseIO(f);return ok;};
    if(!file(job->profile,"schema = 1\ngame = snes\n")||!file(job->config,"opengl = 0\nscale = 1\n")){Reason(reason,size,"Could not create the preview workspace.");TlkNativeAudioPreviewClose(job);return nullptr;}
    int argc=0;LPWSTR *argv=CommandLineToArgvW(GetCommandLineW(),&argc);wchar_t module[32768];GetModuleFileNameW(nullptr,module,32768);std::wstring command=Quote(module);
    const wchar_t *flags[]={L"--rom",L"--md-rom",L"--asset-cache",L"--final-menu-assets",L"--final-native-assets",L"--title-bank-assets",L"--hud-assets",L"--sprite-assets",L"--caption-assets",L"--checkpoint-assets",L"--revival-assets",L"--native-hud-assets"};
    for(int i=1;i+1<argc;i++)for(auto flag:flags)if(!wcscmp(argv[i],flag)){command+=L" "+std::wstring(flag)+L" "+Quote(argv[i+1]);break;}
    LocalFree(argv);command+=L" --config "+Quote(Wide(job->config))+L" --resource-profile "+Quote(Wide(job->profile))+L" --frames 12000 --no-pace --no-record --no-audio";
    if(level<14)command+=L" --practice-level "+std::to_wstring(level);
    std::vector<std::wstring> env;LPWCH block=GetEnvironmentStringsW();
    for(const wchar_t*p=block;*p;p+=wcslen(p)+1)if(_wcsnicmp(p,L"TLK_",4)&&_wcsnicmp(p,L"SDL_",4)&&_wcsnicmp(p,L"SNESRECOMP_",11))env.emplace_back(p);
    FreeEnvironmentStringsW(block);env.emplace_back(L"SDL_VIDEODRIVER=dummy");env.emplace_back(L"SDL_AUDIODRIVER=dummy");env.emplace_back(L"TLK_BROWSER_NATIVE_LEVEL="+std::to_wstring(level));env.emplace_back(L"TLK_BROWSER_NATIVE_OUT="+Wide(job->temp));
    if(event>=0)env.emplace_back(L"TLK_BROWSER_NATIVE_EVENT="+std::to_wstring(event));
    if(gallery)env.emplace_back(L"TLK_BROWSER_GALLERY_ID="+Wide(gallery));
    std::sort(env.begin(),env.end(),[](const auto&a,const auto&b){return _wcsicmp(a.c_str(),b.c_str())<0;});std::vector<wchar_t> environment;
    for(auto &line:env){environment.insert(environment.end(),line.begin(),line.end());environment.push_back(0);}environment.push_back(0);
    STARTUPINFOW startup={};startup.cb=sizeof startup;startup.dwFlags=STARTF_USESHOWWINDOW;startup.wShowWindow=SW_HIDE;PROCESS_INFORMATION process={};
    bool created=CreateProcessW(module,&command[0],nullptr,nullptr,FALSE,CREATE_NO_WINDOW|CREATE_UNICODE_ENVIRONMENT,environment.data(),nullptr,&startup,&process);
    if(!created){Reason(reason,size,"Could not start the isolated audio preview.");TlkNativeAudioPreviewClose(job);return nullptr;}
    CloseHandle(process.hThread);job->process=process.hProcess;job->began=SDL_GetTicks();Reason(reason,size,"Preparing the original SNES track...");return job;
}
extern "C" void *TlkNativeAudioPreviewStart(unsigned level,char *reason,size_t size){return Start(level,-1,nullptr,reason,size);}
extern "C" void *TlkNativeEffectPreviewStart(unsigned level,unsigned event,char *reason,size_t size){
    if(event==256)return Start(14,256,nullptr,reason,size);
    /* The idle Pride opening has not loaded the hyena voices used later in
     * the fight. Graveyard already has the same original30/31/32 cue bank.
     * Only the isolated audition's loading context changes, never its gain. */
    if(level==0 && event>=30 && event<=32)level=2;
    return event<256?Start(level,(int)event,nullptr,reason,size):nullptr;
}
extern "C" int TlkSubjectPreviewSupported(const char *id){return BrowserGallery::Find(id)||TlkBrowserSpecialGallery(id)||TlkBrowserSceneExample(id,0)>=0;}
extern "C" void *TlkSubjectPreviewStart(const char *id,unsigned scene,char *reason,size_t size){
    int special=TlkBrowserSpecialGallery(id);if(special)return Start((special>=4&&special<=9)||special==17?14:special==18?2:0,-1,special==9?"graphics.sprites.cinematics.timon":id,reason,size);
    auto *subject=BrowserGallery::Find(id);int example=TlkBrowserSceneExample(id,scene);
    if(!subject&&example>=0)return Start((unsigned)example,-1,id,reason,size);
    if(!subject){Reason(reason,size,"Choose an individual artwork item to compare.");return nullptr;}
    return Start(!strncmp(id,"graphics.sprites.animals.monkeys",31)&&scene==1?1:subject->level,-1,subject->prefix,reason,size);
}
static int Ready(Job *job,char *reason,size_t size) {
    if(!job)return -1;
    if(job->process) {
        if(WaitForSingleObject(job->process,0)==WAIT_TIMEOUT){if(SDL_GetTicks()-job->began<20000)return 0;Reason(reason,size,"The preview did not finish in time.");return -1;}
        DWORD code=1;GetExitCodeProcess(job->process,&code);CloseHandle(job->process);job->process=nullptr;
        if(code){Reason(reason,size,"The original resource could not be prepared.");return -1;}
        if(!SDL_RenamePath(job->temp.c_str(),job->cache.c_str())){Reason(reason,size,"Could not save the preview.");return -1;}
    }
    return 1;
}
extern "C" int TlkSubjectPreviewPoll(void *opaque,Uint8 **pixels,Uint32 *bytes,unsigned *frames,char *reason,size_t size){
    auto *job=(Job*)opaque;int r=Ready(job,reason,size);if(r!=1)return r;size_t length=0;auto *data=(Uint8*)SDL_LoadFile(job->cache.c_str(),&length);
    if(!data||length<20){SDL_free(data);Remove(job->cache);Reason(reason,size,"The saved preview was incomplete. Choose Retry preview to prepare it again.");return -1;}uint32_t header[5];std::memcpy(header,data,20);
    if(header[0]!=0x33474c54||!((header[1]==192&&header[2]==192)||(header[1]==320&&header[2]==224))||header[3]<1||header[3]>24||(header[4]!=2&&header[4]!=4)||length!=20+header[3]*header[4]*header[1]*header[2]*4){SDL_free(data);Remove(job->cache);Reason(reason,size,"The saved preview was incomplete. Choose Retry preview to prepare it again.");return -1;}
    *pixels=data;*bytes=(Uint32)length;*frames=header[3];return 1;
}
extern "C" int TlkNativeAudioPreviewPoll(void *opaque,SDL_AudioSpec *spec,Uint8 **samples,Uint32 *bytes,char *reason,size_t size) {
    Job *job=(Job*)opaque;if(!job)return -1;
    int ready=Ready(job,reason,size);if(ready!=1)return ready;
    if(!ValidWave(job->cache.c_str(),spec,samples,bytes)){Reason(reason,size,"The preview sample is invalid.");return -1;}
    return 1;
}
extern "C" void TlkNativeAudioPreviewClose(void *opaque) {
    Job *job=(Job*)opaque;if(!job)return;
    if(job->process){if(WaitForSingleObject(job->process,0)==WAIT_TIMEOUT)TerminateProcess(job->process,0);WaitForSingleObject(job->process,2000);CloseHandle(job->process);}
    Remove(job->temp);Remove(job->profile);Remove(job->config);
    if(!job->workspace.empty()){Remove(job->workspace+"/tlk_practice_boot.state");Remove(job->workspace);}
    delete job;
}

#pragma once
/* Browser-owned presentation of validated installer assets. No ROM access,
 * decoding, guest state or gameplay source changes. */
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <shellapi.h>
extern "C" {
#include "tlk_final_art_internal.h"
#include "tlk_options_art_internal.h"
}
struct GenesisBrowserArt {
    TlkFinalArt *art=nullptr;
    SDL_Texture *backdrop=nullptr,*logo=nullptr,*sun=nullptr;
    ~GenesisBrowserArt(){SDL_DestroyTexture(backdrop);SDL_DestroyTexture(logo);SDL_DestroyTexture(sun);TlkFinalArtFree(art);}
    static uint32_t Color(uint16_t c){
        unsigned r=c&31,g=(c>>5)&31,b=(c>>10)&31;
        return 0xff000000u|((r<<3)|(r>>2))|(((g<<3)|(g>>2))<<8)|(((b<<3)|(b>>2))<<16);
    }
    SDL_Texture *Texture(SDL_Renderer *ren,const uint8_t *pixels,int w,int h,const uint16_t *palette,bool transparent=false){
        std::vector<uint32_t> rgba(w*h);
        for(int i=0;i<w*h;i++)rgba[i]=transparent&&!pixels[i]?0:Color(palette[pixels[i]&63]);
        SDL_Texture *t=SDL_CreateTexture(ren,SDL_PIXELFORMAT_ABGR8888,SDL_TEXTUREACCESS_STATIC,w,h);
        if(t){SDL_UpdateTexture(t,nullptr,rgba.data(),w*4);SDL_SetTextureBlendMode(t,SDL_BLENDMODE_BLEND);SDL_SetTextureScaleMode(t,SDL_SCALEMODE_NEAREST);}return t;
    }
    bool Load(SDL_Renderer *ren){
        int argc=0;wchar_t **args=CommandLineToArgvW(GetCommandLineW(),&argc);FILE *f=nullptr;
        if(args){for(int i=1;i+1<argc;i++)if(!wcscmp(args[i],L"--final-menu-assets")){f=_wfopen(args[i+1],L"rb");break;}LocalFree(args);}
        if(!f)return false;
        std::fseek(f,0,SEEK_END);long bytes=std::ftell(f);std::rewind(f);
        if(bytes>0&&bytes<=64*1024*1024){std::vector<uint8_t> data(bytes);if(std::fread(data.data(),1,data.size(),f)==data.size())art=TlkFinalArtLoad(data.data(),data.size());}
        std::fclose(f);if(!art||!art->options||!art->sound_test)return false;
        auto *o=art->options;
        // The title's separately prepared scenery has no menu lettering.
        // Use the original opening API to separate logo pixels from that scenery.
        std::vector<uint32_t> scene(320*224),title(320*224),crop(272*52);
        if(!TlkTitleOpeningArtBackdrop(art->opening,scene.data())||!TlkTitleOpeningArtDraw(art->opening,0,title.data()))return false;
        auto swap=[](uint32_t c){return(c&0xff00ff00u)|((c&255)<<16)|((c>>16)&255);};
        backdrop=SDL_CreateTexture(ren,SDL_PIXELFORMAT_ABGR8888,SDL_TEXTUREACCESS_STATIC,320,224);
        for(int y=0;y<52;y++)for(int x=0;x<272;x++){int at=(y+14)*320+x+24;crop[y*272+x]=title[at]==scene[at]?0:swap(title[at]);}
        for(auto &c:scene)c=swap(c);
        if(backdrop){SDL_UpdateTexture(backdrop,nullptr,scene.data(),320*4);SDL_SetTextureScaleMode(backdrop,SDL_SCALEMODE_NEAREST);}
        logo=SDL_CreateTexture(ren,SDL_PIXELFORMAT_ABGR8888,SDL_TEXTUREACCESS_STATIC,272,52);
        if(logo){SDL_UpdateTexture(logo,nullptr,crop.data(),272*4);SDL_SetTextureBlendMode(logo,SDL_BLENDMODE_BLEND);SDL_SetTextureScaleMode(logo,SDL_SCALEMODE_NEAREST);}
        sun=Texture(ren,o->selector,24,24,o->palette+32,true);
        return backdrop&&logo&&sun;
    }
    void Font(ImFontAtlas *atlas,ImFont *font){
        if(!art||!art->options)return;
        for(int c=32;c<127;c++)atlas->AddCustomRectFontGlyph(font,(ImWchar)c,16,16,16,ImVec2(0,2));
        unsigned char *pixels;int w,h;atlas->GetTexDataAsRGBA32(&pixels,&w,&h);
        for(int i=0;i<atlas->CustomRects.Size;i++){
            auto &r=atlas->CustomRects[i];if(r.Font!=font||r.GlyphID<32||r.GlyphID>=127)continue;
            const uint8_t *glyph=art->options->font[r.GlyphID-32];
            for(int y=0;y<16;y++)for(int x=0;x<16;x++){
                unsigned v=glyph[(y/2)*8+x/2];uint32_t color=v?Color(art->options->palette[32+v]):0;
                std::memcpy(pixels+((r.Y+y)*w+r.X+x)*4,&color,4);
            }
        }
    }
    void Backdrop(ImVec2 size){
        if(!backdrop)return;
        auto *d=ImGui::GetBackgroundDrawList();
        d->AddImage((ImTextureID)(uintptr_t)backdrop,ImVec2(0,0),size);
        d->AddRectFilled(ImVec2(0,0),size,IM_COL32(9,7,36,150));
        // Stepped gold edges echo the original pixel outlines.
        d->AddRect(ImVec2(8,8),ImVec2(size.x-8,size.y-8),IM_COL32(220,174,65,255),0,0,2);
        d->AddRect(ImVec2(12,12),ImVec2(size.x-12,size.y-12),IM_COL32(73,45,24,255));
    }
    void MarkSelected(){
        auto a=ImGui::GetItemRectMin(),b=ImGui::GetItemRectMax();auto *d=ImGui::GetWindowDrawList();
        d->AddRect(a,b,IM_COL32(255,218,100,255),0,0,2);
        if(sun)d->AddImage((ImTextureID)(uintptr_t)sun,ImVec2(a.x+3,(a.y+b.y)*.5f-9),ImVec2(a.x+21,(a.y+b.y)*.5f+9));
    }
};

#pragma once
extern "C" {
#include "tlk_wide.h"
}
#include "tlk_browser_palette_model.h"

/* The preview pose never changes palette identity or the colour being edited. */
struct BrowserSpriteColours {
    void *job=nullptr;
    Uint8 *data=nullptr;
    unsigned frames=0,planes=0,w=0,h=0;
    int owner=-1,frame=0,last_source=-1,last_drawing=-1;
    int capture_source=-1,capture_drawing=-1;
    uint64_t stamp=0;
    unsigned texture_w=0,texture_h=0;
    SDL_Texture *textures[2]={};
    std::string message;
    BrowserPaletteModel palette;
    bool selected_by_user[2]={};

    ~BrowserSpriteColours(){Clear();}
    void Clear() {
        if(job)TlkNativeAudioPreviewClose(job);
        job=nullptr;SDL_free(data);data=nullptr;
        for(auto &t:textures){SDL_DestroyTexture(t);t=nullptr;}
        owner=-1;frames=planes=w=h=texture_w=texture_h=0;frame=0;
        last_source=last_drawing=capture_source=capture_drawing=-1;stamp=0;
        palette.Clear();selected_by_user[0]=selected_by_user[1]=false;message.clear();
    }
    static ImVec4 RGB(unsigned c) {
        return ImVec4((c&31)/31.f,(c>>5&31)/31.f,(c>>10&31)/31.f,1);
    }
    static uint32_t Pixel(unsigned c) {
        unsigned r=c&31,g=c>>5&31,b=c>>10&31;
        return 0xff000000u|((r*8+(r>>2))<<16)|((g*8+(g>>2))<<8)|(b*8+(b>>2));
    }
    void Poll() {
        if(!job)return;
        Uint32 bytes=0;char reason[256]={};
        int result=TlkSubjectPreviewPoll(job,&data,&bytes,&frames,reason,sizeof reason);
        if(!result)return;
        TlkNativeAudioPreviewClose(job);job=nullptr;
        message=result==1?"":reason;
        if(result==1&&data&&bytes>=20) {
            uint32_t header[5];memcpy(header,data,20);
            w=header[1];h=header[2];planes=header[4];
            uint64_t expected=20+uint64_t(w)*h*frames*planes*4;
            if(header[0]==0x33474c54&&header[3]==frames&&expected==bytes&&w&&h&&frames&&(planes==2||planes==4)) {
                palette.Build((const uint32_t*)(data+20),w,h,frames,planes);
                for(int source=0;source<2;source++)if(!selected_by_user[source]&&!palette.original_colours[source].empty())palette.selected[source]=palette.original_colours[source].front();
                stamp=0;return;
            }
        }
        SDL_free(data);data=nullptr;frames=planes=w=h=0;
        if(message.empty())message="The sample picture could not be loaded.";
    }
    void Draw(SDL_Renderer *renderer,int node) {
        if(!TlkResourcesSpritePaletteNode(node))return;
        if(!ImGui::CollapsingHeader("Custom colours for this sprite"))return;
        const char *id=TlkResourcesNode(node)->id;
        if(owner!=node) {
            Clear();owner=node;char reason[256]={};
            job=TlkSubjectPreviewStart(id,0,reason,sizeof reason);
            message=job?"Preparing the sprite preview...":reason;
        }
        Poll();
        int md=TlkResourcesResolved(node,1)==TLK_SOURCE_MD;
        std::string family=id;family.resize(family.size()-8);
        int drawing=TlkResourcesFind((family+".frames").c_str());
        if(drawing<0&&family=="graphics.hud")drawing=TlkResourcesFind("graphics.hud.frames.health");
        int drawing_md=drawing>=0&&TlkResourcesResolved(drawing,1)==TLK_SOURCE_MD;
        bool gallery=data&&w&&h&&frames&&(planes==2||planes==4);
        bool visible_subject=false;
        if(last_source!=md||last_drawing!=drawing_md) {
            last_source=md;last_drawing=drawing_md;stamp=0;
        }
        ImGui::TextWrapped("Colours apply to every pose and level of this sprite. SNES and Genesis keep separate custom colours.");
        ImGui::Text("Editing %s colours",md?"Genesis":"SNES");
        if(gallery) {
            int pose=frame+1;bool changed=false;
            ImGui::BeginDisabled(frames<2);
            if(ImGui::Button("Previous pose")){pose=pose>1?pose-1:(int)frames;changed=true;}
            ImGui::SameLine();
            float next_width=ImGui::CalcTextSize("Next pose").x+ImGui::GetStyle().FramePadding.x*2+ImGui::GetStyle().ItemSpacing.x;
            ImGui::SetNextItemWidth(std::max(100.f,ImGui::GetContentRegionAvail().x-next_width));
            changed|=ImGui::SliderInt("##sprite-pose",&pose,1,(int)frames,"Pose %d",ImGuiSliderFlags_AlwaysClamp);
            if(ImGui::IsItemHovered())ImGui::SetTooltip("Preview only. Your colour changes apply to all poses.");
            ImGui::SameLine();
            if(ImGui::Button("Next pose")){pose=pose<(int)frames?pose+1:1;changed=true;}
            ImGui::EndDisabled();
            if(changed){frame=pose-1;stamp=0;message.clear();}
        } else {
            if(capture_source!=md||capture_drawing!=drawing_md) {
                capture_source=md;capture_drawing=drawing_md;std::vector<uint32_t> live(320*224);
                TlkResourcesPreviewBegin(node,md?TLK_SOURCE_MD:TLK_SOURCE_SNES);
                TlkWidePreview(live.data(),320);TlkResourcesPreviewEnd();
            }
            uint16_t visible[128];int count=TlkWideSpritePaletteColors(node,md,visible,128);
            visible_subject=count>0;
            palette.Observe(md,std::vector<uint16_t>(visible,visible+count));
            if(palette.colours[md].empty()) {
                if(!message.empty())ImGui::TextWrapped("%s",message.c_str());
                ImGui::TextWrapped("Visit a scene where this sprite is visible to choose its colours here.");
            } else if(visible_subject)ImGui::TextWrapped("Showing this sprite's colours from the current scene.");
            else ImGui::TextWrapped("Your saved colours are available below.");
        }
        /* Keep saved shades available even when the samples use other lighting.
         * Merging never changes which colour is selected. */
        std::vector<uint16_t> saved[2];int edited_count=0;
        for(int draft=0;draft<2;draft++)for(int i=0;i<TlkResourcesPaletteCount(draft);i++) {
            int e[4];TlkResourcesPaletteEntry(i,draft,e);
            if(e[0]==14&&e[1]==node+3) {
                saved[!!(e[2]&32768)].push_back((uint16_t)(e[2]&32767));
                if(draft&&!!(e[2]&32768)==md)edited_count++;
            }
        }
        for(int source=0;source<2;source++)palette.Merge(source,saved[source]);
        const auto &colours=palette.colours[md];
        if(colours.empty())return;
        bool split=ImGui::GetContentRegionAvail().x>=820;
        if(split) {
            split=ImGui::BeginTable("Sprite colour editor",2,ImGuiTableFlags_SizingStretchProp|ImGuiTableFlags_NoSavedSettings);
            if(split){ImGui::TableSetupColumn("Colours",ImGuiTableColumnFlags_WidthStretch,.52f);ImGui::TableSetupColumn("Preview",ImGuiTableColumnFlags_WidthStretch,.48f);ImGui::TableNextRow();ImGui::TableSetColumnIndex(0);}
        }
        ImGui::Text("%u colours / %d edited",(unsigned)colours.size(),edited_count);
        float size=34,spacing=ImGui::GetStyle().ItemSpacing.x;
        int columns=std::clamp((int)((ImGui::GetContentRegionAvail().x-16)/(size+spacing)),1,16);
        int rows=((int)colours.size()+columns-1)/columns;
        float height=std::clamp(rows*(size+ImGui::GetStyle().ItemSpacing.y)+16,54.f,154.f);
        ImGui::BeginChild("Sprite palette",ImVec2(0,height),ImGuiChildFlags_Borders);
        TlkResourcesPalettePreview(1);
        for(unsigned i=0;i<colours.size();i++) {
            unsigned c=colours[i],edited=TlkResourcesSpritePaletteMap(node,md,(uint16_t)c);
            ImGui::PushID((int)c);if(i%(unsigned)columns)ImGui::SameLine();
            if(ImGui::ColorButton("##sprite-colour",RGB(edited),ImGuiColorEditFlags_NoTooltip,ImVec2(size,size))) {
                palette.selected[md]=(int)c;selected_by_user[md]=true;message.clear();
            }
            ImVec2 lo=ImGui::GetItemRectMin(),hi=ImGui::GetItemRectMax();
            if((int)c==palette.selected[md])ImGui::GetWindowDrawList()->AddRect(lo,hi,IM_COL32(255,215,70,255),0,0,3);
            if(edited!=c)ImGui::GetWindowDrawList()->AddCircleFilled(ImVec2(hi.x-6,lo.y+6),3,IM_COL32(255,215,70,255));
            if(ImGui::IsItemHovered()) {
                ImGui::BeginTooltip();ImGui::TextUnformatted(edited==c?"Original colour":"Custom colour");
                ImGui::ColorButton("Original",RGB(c),ImGuiColorEditFlags_NoTooltip,ImVec2(28,28));
                if(edited!=c){ImGui::SameLine();ImGui::ColorButton("New",RGB(edited),ImGuiColorEditFlags_NoTooltip,ImVec2(28,28));}
                ImGui::EndTooltip();
            }
            ImGui::PopID();
        }
        TlkResourcesPalettePreview(0);ImGui::EndChild();
        unsigned axis=planes==4?drawing_md*2+md:md;
        const uint32_t *pixels=gallery?(const uint32_t*)(data+20)+((size_t)frame*planes+axis)*w*h:nullptr;
        unsigned original=(unsigned)palette.selected[md];
        if(gallery&&!BrowserPaletteModel::Uses(pixels,(size_t)w*h,(uint16_t)original)) {
            ImGui::TextWrapped("This colour is not visible in this pose. It still applies wherever the sprite uses it.");
            if(ImGui::Button("Find a pose with this colour")) {
                int found=BrowserPaletteModel::FindPose((const uint32_t*)(data+20),w,h,frames,planes,axis,(uint16_t)original,(unsigned)frame);
                if(found>=0){frame=found;stamp=0;message.clear();pixels=(const uint32_t*)(data+20)+((size_t)frame*planes+axis)*w*h;}
                else message="This edited shade is not used in these sample poses. It may belong to another art style or lighting.";
            }
        }
        TlkResourcesPalettePreview(1);
        unsigned edited=TlkResourcesSpritePaletteMap(node,md,(uint16_t)original);
        TlkResourcesPalettePreview(0);
        ImGui::ColorButton("Original shade",RGB(original),ImGuiColorEditFlags_NoTooltip,ImVec2(30,30));
        if(ImGui::IsItemHovered())ImGui::SetTooltip("Original colour. Reset colour restores this shade.");
        ImGui::SameLine();float values[]={(edited&31)/31.f,(edited>>5&31)/31.f,(edited>>10&31)/31.f};
        if(ImGui::ColorEdit3("New colour",values,ImGuiColorEditFlags_NoInputs)) {
            unsigned replacement=0;
            for(int i=0;i<3;i++)replacement|=(unsigned)std::clamp((int)(values[i]*31.f+.5f),0,31)<<(i*5);
            if(TlkResourcesPaletteSet(14,node+3,(int)original|(md<<15),(int)replacement))message.clear();
            else message="The colour-edit limit has been reached. Reset unused colours before adding more.";
        }
        ImGui::BeginDisabled(edited==original);
        if(ImGui::Button("Reset colour")) {
            TlkResourcesPaletteSet(14,node+3,(int)original|(md<<15),(int)original);message.clear();
        }
        ImGui::EndDisabled();
        std::string reset=std::string("Reset ")+(md?"Genesis":"SNES")+" palette";
        if(ImGui::GetItemRectSize().x+ImGui::CalcTextSize(reset.c_str()).x+ImGui::GetStyle().FramePadding.x*2+ImGui::GetStyle().ItemSpacing.x<ImGui::GetContentRegionAvail().x)ImGui::SameLine();
        ImGui::BeginDisabled(!edited_count);
        if(ImGui::Button(reset.c_str())) {
            for(int i=TlkResourcesPaletteCount(1)-1;i>=0;i--) {
                int e[4];TlkResourcesPaletteEntry(i,1,e);
                if(e[0]==14&&e[1]==node+3&&!!(e[2]&32768)==md)TlkResourcesPaletteSet(14,node+3,e[2],e[2]&32767);
            }
            palette.ResetSource(md);message.clear();
        }
        ImGui::EndDisabled();
        if(ImGui::IsItemHovered(ImGuiHoveredFlags_AllowWhenDisabled))ImGui::SetTooltip("Resets only this sprite's selected console palette. Other sprites and the other version keep their colours.");
        if(split)ImGui::TableSetColumnIndex(1);
        if(!gallery&&!visible_subject) {
            if(!message.empty())ImGui::TextWrapped("%s",message.c_str());
            ImGui::TextWrapped("To preview these colours without a sample picture, open a scene containing this sprite.");
            if(split)ImGui::EndTable();
            ImGui::TextWrapped("Apply & save keeps your colours. No level restart is needed.");return;
        }
        uint64_t next=1469598103934665603ull;
        for(int i=0;i<TlkResourcesPaletteCount(1);i++) {
            int e[4];TlkResourcesPaletteEntry(i,1,e);
            for(int v:e){next^=(unsigned)v;next*=1099511628211ull;}
        }
        next^=(unsigned)(frame+1)*5+axis;
        unsigned display_w=gallery?w:320,display_h=gallery?h:224;
        if(texture_w!=display_w||texture_h!=display_h) {
            for(auto &t:textures){SDL_DestroyTexture(t);t=nullptr;}
            texture_w=display_w;texture_h=display_h;
        }
        if(!textures[0]||next!=stamp) {
            stamp=next;
            for(int side=0;side<2;side++) {
                std::vector<uint32_t> rgba((size_t)display_w*display_h);
                if(gallery) {
                    std::copy(pixels,pixels+rgba.size(),rgba.begin());TlkResourcesPalettePreview(1);
                    for(unsigned y=0;y<h;y++)for(unsigned x=0;x<w;x++) {
                        uint32_t &p=rgba[(size_t)y*w+x];
                        if(!(p>>24)){p=((x/12+y/12)&1)?0xff1d3033:0xff17282b;continue;}
                        if(side)p=Pixel(TlkResourcesSpritePaletteMap(node,md,BrowserPaletteModel::Colour(p)));
                    }
                } else {
                    TlkResourcesPreviewBegin(node,md?TLK_SOURCE_MD:TLK_SOURCE_SNES);
                    TlkResourcesPalettePreview(side);TlkWidePreview(rgba.data(),320);TlkResourcesPreviewEnd();
                }
                TlkResourcesPalettePreview(0);
                if(!textures[side])textures[side]=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_XRGB8888,SDL_TEXTUREACCESS_STATIC,display_w,display_h);
                if(textures[side]){SDL_SetTextureScaleMode(textures[side],SDL_SCALEMODE_NEAREST);SDL_UpdateTexture(textures[side],nullptr,rgba.data(),display_w*4);}
            }
        }
        ImGui::TextUnformatted(gallery?"Original / Your colours":"Before / Your colours");
        auto box=gallery?palette.bounds[md]:BrowserPaletteModel::Bounds{0,0,display_w,display_h};
        float bw=(float)(box.right-box.left),bh=(float)(box.bottom-box.top);
        float width=std::min(320.f,(ImGui::GetContentRegionAvail().x-12)/2);
        float scale=std::min(width/std::max(1.f,bw),240.f/std::max(1.f,bh));
        ImVec2 uv0((float)box.left/display_w,(float)box.top/display_h);
        ImVec2 uv1((float)box.right/display_w,(float)box.bottom/display_h);
        for(int side=0;side<2;side++) {
            if(side)ImGui::SameLine();
            if(textures[side])ImGui::Image((ImTextureID)(uintptr_t)textures[side],ImVec2(bw*scale,bh*scale),uv0,uv1);
        }
        if(split)ImGui::EndTable();
        if(!message.empty())ImGui::TextWrapped("%s",message.c_str());
        ImGui::TextWrapped("Apply & save changes the game when you resume. No level restart is needed. Custom presets include your colours.");
    }
};

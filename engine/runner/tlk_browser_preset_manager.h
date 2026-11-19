#pragma once
#include <memory>
#include <mutex>
/* File dialogs return through shared state; a late callback never owns the UI. */
struct BrowserPresetManager {
    struct Item {std::string name;std::vector<int> values;};
    struct Dialog {std::mutex mutex;bool done=false;std::string path,error;};
    std::string dir,selected,loaded,message,operation,import_path;
    std::vector<Item> items;char name[65]={};bool open=false,confirm=false,naming=false;
    std::shared_ptr<Dialog> dialog;bool exporting=false;
    std::vector<int> export_values;
    explicit BrowserPresetManager(const std::string &directory):dir(directory){Refresh();loaded=Match(BrowserPresets::Choices(0));selected=loaded;}
    void Refresh() {
        items.clear();for(auto &n:BrowserPresets::List(dir)){std::vector<int> v;std::string error;BrowserPresets::Read(BrowserPresets::Path(dir,n),v,error);items.push_back({n,v});}
    }
    std::string Match(const std::vector<int> &values)const {for(const auto &i:items)if(i.values==values)return i.name;return "";}
    std::string Label()const {
        auto values=BrowserPresets::Choices();
        for(const auto &i:items)if(i.name==loaded&&i.values==values)return loaded+(TlkResourcesDirty()?" (not applied)":"");
        std::string exact=Match(values);
        if(!exact.empty())return exact+(TlkResourcesDirty()?" (not applied)":"");
        return loaded.empty()?"Custom mix":loaded+" (modified)";
    }
    static void SDLCALL FileChosen(void *opaque,const char *const *files,int) {
        auto *owner=(std::shared_ptr<Dialog>*)opaque;auto state=*owner;delete owner;
        std::lock_guard<std::mutex> lock(state->mutex);
        if(!files)state->error=SDL_GetError();else if(files[0])state->path=files[0];state->done=true;
    }
    void ChooseFile(SDL_Window *window,bool save) {
        if(dialog)return;dialog=std::make_shared<Dialog>();exporting=save;
        if(save){std::string error;if(!BrowserPresets::Read(BrowserPresets::Path(dir,selected),export_values,error)){message=error;dialog.reset();return;}}
        static const SDL_DialogFileFilter filters[]={{"Lion King resource preset","ini"}};
        auto *owner=new std::shared_ptr<Dialog>(dialog);
        if(save)SDL_ShowSaveFileDialog(FileChosen,owner,window,filters,1,(dir+"/"+selected+".ini").c_str());
        else SDL_ShowOpenFileDialog(FileChosen,owner,window,filters,1,nullptr,false);
    }
    void Poll() {
        if(!dialog)return;std::string path,error;
        {std::lock_guard<std::mutex> lock(dialog->mutex);if(!dialog->done)return;path=dialog->path;error=dialog->error;}
        dialog.reset();if(!error.empty()){message="File dialog failed: "+error;return;}if(path.empty())return;
        if(exporting){if(BrowserPresets::Write(path,export_values,message))message="Exported preset. Your game choices have not changed.";return;}
        import_path=path;operation="Import";message.clear();std::string base=path.substr(path.find_last_of("/\\")+1);size_t dot=base.find_last_of('.');if(dot!=std::string::npos)base.resize(dot);
        if(!BrowserPresets::ValidName(base))base="Imported preset";std::snprintf(name,sizeof name,"%s",base.c_str());naming=true;
    }
    void Draw(SDL_Window *window, bool &refresh_pictures) {
        Poll();if(open){Refresh();ImGui::OpenPopup("Your custom presets");open=false;}
        ImGui::SetNextWindowSize(ImVec2(std::min(950.f,ImGui::GetIO().DisplaySize.x-40),0),ImGuiCond_Appearing);
        ImGui::SetNextWindowPos(ImGui::GetMainViewport()->GetCenter(),ImGuiCond_Appearing,ImVec2(.5f,.5f));
        if(ImGui::BeginPopupModal("Your custom presets",nullptr,ImGuiWindowFlags_AlwaysAutoResize)) {
            ImGui::TextWrapped("Load a preset to review its choices. Apply & save activates it in your game.");
            if(ImGui::BeginListBox("##preset-list",ImVec2(-1,180))) {
                for(auto &item:items)if(ImGui::Selectable(item.name.c_str(),selected==item.name))selected=item.name;
                if(items.empty())ImGui::TextUnformatted("No saved presets yet.");ImGui::EndListBox();
            }
            bool exists=std::any_of(items.begin(),items.end(),[&](const Item&i){return i.name==selected;});
            ImGui::BeginDisabled(!exists||dialog!=nullptr);
            if(ImGui::Button("Load")){if(BrowserPresets::Load(dir,selected,message)){loaded=selected;refresh_pictures=true;}}
            ImGui::SameLine();if(ImGui::Button("Update")){operation="Update";confirm=true;}
            ImGui::SameLine();if(ImGui::Button("Rename")){operation="Rename";message.clear();std::snprintf(name,sizeof name,"%s",selected.c_str());naming=true;}
            ImGui::SameLine();if(ImGui::Button("Delete")){operation="Delete";confirm=true;}
            ImGui::SameLine();if(ImGui::Button("Export"))ChooseFile(window,true);ImGui::EndDisabled();
            ImGui::BeginDisabled(dialog!=nullptr);if(ImGui::Button("Import preset..."))ChooseFile(window,false);ImGui::EndDisabled();
            if(dialog)ImGui::TextWrapped("Choose a file in the file dialog, or cancel it.");
            if(!message.empty())ImGui::TextWrapped("%s",message.c_str());
            ImGui::BeginDisabled(dialog!=nullptr);if(ImGui::Button("Done"))ImGui::CloseCurrentPopup();ImGui::EndDisabled();
            if(confirm){ImGui::OpenPopup("Confirm preset change");confirm=false;}
            ImGui::SetNextWindowSize(ImVec2(std::min(700.f,ImGui::GetIO().DisplaySize.x-40),0));
            ImGui::SetNextWindowPos(ImGui::GetMainViewport()->GetCenter(),ImGuiCond_Appearing,ImVec2(.5f,.5f));
            if(ImGui::BeginPopupModal("Confirm preset change",nullptr,ImGuiWindowFlags_AlwaysAutoResize)) {
                ImGui::TextWrapped("%s preset: %s?",operation.c_str(),selected.c_str());
                ImGui::TextWrapped("%s",operation=="Update"?"Replace its saved choices with your current choices, including unsaved edits. This does not apply them to the game.":"Remove this saved preset. Your active game choices remain in place.");
                if(ImGui::Button(operation.c_str())) {
                    if(operation=="Update") {if(BrowserPresets::Write(BrowserPresets::Path(dir,selected),BrowserPresets::Choices(),message))message="Updated "+selected+". Game choices are unchanged.";}
                    else if(SDL_RemovePath(BrowserPresets::Path(dir,selected).c_str())){message="Deleted "+selected+".";if(loaded==selected)loaded.clear();selected.clear();}else message="Could not delete the preset.";
                    Refresh();ImGui::CloseCurrentPopup();
                }
                ImGui::SameLine();if(ImGui::Button("Cancel"))ImGui::CloseCurrentPopup();ImGui::EndPopup();
            }
            if(naming){ImGui::OpenPopup("Name this preset");naming=false;}
            ImGui::SetNextWindowSize(ImVec2(std::min(700.f,ImGui::GetIO().DisplaySize.x-40),0));
            ImGui::SetNextWindowPos(ImGui::GetMainViewport()->GetCenter(),ImGuiCond_Appearing,ImVec2(.5f,.5f));
            if(ImGui::BeginPopupModal("Name this preset",nullptr,ImGuiWindowFlags_AlwaysAutoResize)) {
                ImGui::TextUnformatted(operation.c_str());if(ImGui::IsWindowAppearing())ImGui::SetKeyboardFocusHere();ImGui::SetNextItemWidth(-100);bool enter=ImGui::InputText("Name",name,sizeof name,ImGuiInputTextFlags_EnterReturnsTrue|ImGuiInputTextFlags_AutoSelectAll);
                if(!message.empty())ImGui::TextWrapped("%s",message.c_str());
                if(ImGui::Button("Save")||enter){
                    bool ok=operation=="Import"?BrowserPresets::Import(import_path,dir,name,message):BrowserPresets::Rename(dir,selected,name,message);
                    if(ok){if(loaded==selected&&operation=="Rename")loaded=name;selected=name;Refresh();ImGui::CloseCurrentPopup();}
                }
                ImGui::SameLine();if(ImGui::Button("Cancel"))ImGui::CloseCurrentPopup();ImGui::EndPopup();
            }
            ImGui::EndPopup();
        }
    }
};

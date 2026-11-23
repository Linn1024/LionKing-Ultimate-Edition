/* Named resource-choice snapshots. Loading edits the draft only. */
#ifndef TLK_BROWSER_PRESETS_H
#define TLK_BROWSER_PRESETS_H
namespace BrowserPresets {
static std::string Directory() {
    const char *test=SDL_getenv("TLK_BROWSER_PRESET_DIRECTORY");
    if(test&&*test)return test;
    const char *path=SDL_GetPrefPath("LionKing","CustomPresets");
    std::string result=path?path:"";SDL_free((void*)path);return result;
}
static bool ValidName(const std::string &name) {
    if(name.empty()||name.size()>64||name.front()==' '||name.back()==' ')return false;
    for(unsigned char c:name)if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c==' '||c=='-'||c=='_'))return false;
    return true;
}
static std::string Path(const std::string &dir,const std::string &name) {return dir+"/"+name+".ini";}
static std::vector<int> Choices(int draft=1) {
    std::vector<int> values(TlkResourcesCount());for(int i=0;i<(int)values.size();i++)values[i]=TlkResourcesChoice(i,draft);
    for(int n=0;n<TlkResourcesPaletteCount(draft);n++){int e[4];TlkResourcesPaletteEntry(n,draft,e);values.insert(values.end(),e,e+4);}return values;
}
static void Set(const std::vector<int> &values){int count=TlkResourcesCount();for(int i=0;i<count&&i<(int)values.size();i++)TlkResourcesSet(i,values[i]);TlkResourcesPaletteReset(-1,-1);for(size_t i=count;i+3<values.size();i+=4)TlkResourcesPaletteSet(values[i],values[i+1],values[i+2],values[i+3]);}
static bool Read(const std::string &path,std::vector<int> &values,std::string &message) {
    SDL_PathInfo info;if(!SDL_GetPathInfo(path.c_str(),&info)||info.size>1024*1024){message="Could not read this preset, or the file is too large.";return false;}
    size_t size=0;char *raw=(char*)SDL_LoadFile(path.c_str(),&size);
    if(!raw){message="Could not read that preset.";return false;}
    std::string text(raw,size);SDL_free(raw);values.assign(TlkResourcesCount(),-1);bool schema=false,valid=size>0&&text.find('\0')==std::string::npos;size_t pos=0;
    if(text.compare(0,3,"\xef\xbb\xbf")==0)pos=3;
    while(valid&&pos<text.size()) {
        size_t end=text.find('\n',pos);std::string line=text.substr(pos,end==std::string::npos?end:end-pos);pos=end==std::string::npos?text.size():end+1;
        size_t start=line.find_first_not_of(" \t\r");if(start==std::string::npos||line[start]==';'||line[start]=='#')continue;
        char id[160],value[32],extra;
        if(std::sscanf(line.c_str(),"%159s = %31s %c",id,value,&extra)!=2){valid=false;break;}
        if(!std::strcmp(id,"schema")){if(schema||std::strcmp(value,"1"))valid=false;schema=true;continue;}
        int entry[4],colour=TlkResourcesPaletteDecode(id,value,entry);
        if(colour>=0){
            if(!colour||values.size()>=(size_t)TlkResourcesCount()+16384){valid=false;break;}
            for(size_t i=TlkResourcesCount();i+3<values.size();i+=4)if(values[i]==entry[0]&&values[i+1]==entry[1]&&values[i+2]==entry[2])valid=false;
            values.insert(values.end(),entry,entry+4);continue;
        }
        int index=TlkResourcesFind(id),source=!std::strcmp(value,"inherit")?0:!std::strcmp(value,"snes")?1:!std::strcmp(value,"md")?2:-1;
        if(index<0||source<0||values[index]>=0||(!index&&!source)){valid=false;break;}values[index]=source;
    }
    for(int i=0;i<TlkResourcesCount();i++)if(values[i]<0){const char *id=TlkResourcesNode(i)->id;if(std::strstr(id,"graphics.scenery.snes_motion")==id||!std::strcmp(id,"graphics.scenery.firelight"))values[i]=0;}
    if(!valid||!schema||std::find(values.begin(),values.end(),-1)!=values.end()){message="This preset is incomplete or incompatible. Your choices have not changed.";return false;}
    return true;
}
static std::string Text(const std::vector<int> &values) {
    std::string text="; Lion King custom resource preset\nschema = 1\n";const char *sources[]={"inherit","snes","md"};
    for(int i=0;i<TlkResourcesCount();i++)text+=std::string(TlkResourcesNode(i)->id)+" = "+sources[values[i]]+"\n";
    for(size_t i=TlkResourcesCount();i+3<values.size();i+=4){char line[256];if(TlkResourcesPaletteEncode(values.data()+i,line,sizeof line))text+=line;}return text;
}
static bool Write(const std::string &path,const std::vector<int> &values,std::string &message) {
    std::string text=Text(values),temp=path+".tmp-"+std::to_string(SDL_GetTicksNS());
    if(!SDL_SaveFile(temp.c_str(),text.data(),text.size())||!SDL_RenamePath(temp.c_str(),path.c_str())){
        SDL_RemovePath(temp.c_str());message="Could not save the preset. Your game choices have not changed.";return false;
    }return true;
}
static std::vector<std::string> List(const std::string &dir) {
    std::vector<std::string> names;if(dir.empty())return names;
    int count=0;char **files=SDL_GlobDirectory(dir.c_str(),"*.ini",0,&count);
    if(files){for(int i=0;i<count;i++){std::string n=files[i];if(n.size()>4){n.resize(n.size()-4);if(ValidName(n))names.push_back(n);}}SDL_free(files);}
    std::sort(names.begin(),names.end());return names;
}
static bool Save(const std::string &dir,const std::string &name,std::string &message) {
    if(!ValidName(name)){message="Use 1-64 letters, numbers, spaces, - or _. No leading or trailing spaces.";return false;}
    if(dir.empty()||!SDL_CreateDirectory(dir.c_str())){message="Could not open the custom preset folder.";return false;}
    std::string path=Path(dir,name);SDL_PathInfo info;
    if(SDL_GetPathInfo(path.c_str(),&info)){message="That name already exists. Choose another name.";return false;}
    if(!Write(path,Choices(),message))return false;
    message="Saved custom preset: "+name+". Use Apply & save to apply any pending game choices.";return true;
}
static bool Load(const std::string &dir,const std::string &name,std::string &message) {
    if(!ValidName(name)){message="Invalid preset name.";return false;}
    std::vector<int> values;if(!Read(Path(dir,name),values,message))return false;
    auto before=Choices();Set(values);
    char reason[256]={};
    if(TlkResourcesValidate(reason,sizeof reason)) {
        Set(before);
        message=std::string("Cannot load this preset: ")+reason;return false;
    }
    message="Loaded "+name+". Review your choices, then Apply & save. Undo changes restores your active choices.";return true;
}
static bool Rename(const std::string &dir,const std::string &name,const std::string &next,std::string &message) {
    if(!ValidName(name)||!ValidName(next)){message="Use 1-64 letters, numbers, spaces, - or _. No leading or trailing spaces.";return false;}
    if(name==next)return true;SDL_PathInfo info;
    if(SDL_GetPathInfo(Path(dir,next).c_str(),&info)){message="That name already exists. Choose another name.";return false;}
    if(!SDL_RenamePath(Path(dir,name).c_str(),Path(dir,next).c_str())){message="Could not rename the preset.";return false;}
    message="Renamed preset to "+next+".";return true;
}
static bool Import(const std::string &path,const std::string &dir,const std::string &name,std::string &message) {
    std::vector<int> values;if(!Read(path,values,message))return false;
    auto before=Choices();Set(values);char reason[256]={};int blocked=TlkResourcesValidate(reason,sizeof reason);Set(before);
    if(blocked){message=std::string("Cannot import this preset: ")+reason;return false;}
    if(!ValidName(name)){message="Choose a name using letters, numbers, spaces, - or _.";return false;}
    SDL_PathInfo info;if(SDL_GetPathInfo(Path(dir,name).c_str(),&info)){message="That name already exists. Choose another name.";return false;}
    if(!SDL_CreateDirectory(dir.c_str())||!Write(Path(dir,name),values,message))return false;
    message="Imported "+name+". Choose Load when you want to use it.";return true;
}
}
#endif

/* Plain-SDL resource editor. Included after the native-size UI primitives.
 * Edits are drafts in the shared resource model; only Apply publishes them. */
#include "tlk_visual_resources.h"
static void CloseMenu(void);
void TlkResourcesHostApplied(void);
static unsigned char *s_resource_open;
static int *s_resource_visible;
static int s_resource_count,s_resource_rows,s_resource_selected,s_resource_top;
static int s_resource_action=-1;
static char s_resource_message[256];
static const char *const kResourceActions[]={"Apply","Undo","SNES","Mix","MD","Back"};
enum { RESOURCE_ACTION_COUNT=sizeof kResourceActions/sizeof kResourceActions[0] };
static const char *ResourceChoice(int source) {
    return source==TLK_SOURCE_MD?"MD":source==TLK_SOURCE_SNES?"SNES":"Inh";
}
static int ResourceEnsure(void) {
    int count=TlkResourcesCount();
    if(count==s_resource_count)return count>0;
    if(count<=0)return 0;
    unsigned char *open=calloc((size_t)count,1);int *visible=malloc((size_t)count*sizeof *visible);
    if(!open || !visible) { free(open);free(visible);return 0; }
    free(s_resource_open);free(s_resource_visible);s_resource_open=open;s_resource_visible=visible;s_resource_count=count;
    for(int i=0;i<count;i++)if(i<=4 || !strcmp(TlkResourcesNode(i)->id,"display"))open[i]=1;
    s_resource_selected=s_resource_top=0;return 1;
}
static void ResourceVisit(int index,int depth) {
    if(index<0 || index>=s_resource_count || depth>s_resource_count || s_resource_rows>=s_resource_count)return;
    s_resource_visible[s_resource_rows++]=index;
    if(!s_resource_open[index] || TlkResourcesNode(index)->leaf)return;
    int display=index==0?TlkResourcesFind("display"):-1;
    if(display>=0)ResourceVisit(display,depth+1);
    for(int i=1;i<s_resource_count;i++)if(i!=display && TlkResourcesNode(i)->parent==index)ResourceVisit(i,depth+1);
}
static int ResourcePosition(void) {
    s_resource_rows=0;if(!ResourceEnsure())return -1;ResourceVisit(0,0);
    for(int i=0;i<s_resource_rows;i++)if(s_resource_visible[i]==s_resource_selected)return i;
    s_resource_selected=0;return 0;
}
static int ResourceDepth(int index) {
    int depth=0;
    while(index>0 && depth<s_resource_count) { index=TlkResourcesNode(index)->parent;depth++; }
    return depth;
}
static void ResourceBegin(void) {
    int visual=g_tlk_visual_resources_open?g_tlk_visual_resources_open(win):-1;
    if(visual>=0){s_about=0;if(visual)TlkResourcesHostApplied();return;}
    ResourceEnsure();s_resource_selected=s_resource_top=0;s_resource_action=-1;s_resource_message[0]=0;
}
static void ResourceBox(int x,int y,int w,int h,uint32_t color) {
    for(int row=y;row<y+h && row<kHeight;row++)for(int col=x;col<x+w && col<kWidth;col++)
        if(row>=0 && col>=0)s_screen[row*kWidth+col]=color;
}
static void ResourceText(int x,int y,const char *text,int columns,int lines) {
    while(*text && lines-->0) {
        char line[33];int n=0;
        while(text[n] && text[n]!='\n' && n<columns && n<32) { line[n]=text[n];n++; }
        line[n]=0;DrawText(x,y,line);text+=n;if(*text=='\n')text++;y+=10;
    }
}
static void ResourceInfo(void) {
    const TlkResourceNode *node=TlkResourcesNode(s_resource_selected);if(!node)return;
    snprintf(s_resource_message,sizeof s_resource_message,"%s\nPending choice: %s\nApplied choice: %s\n%s\n%s",
        node->id,ResourceChoice(TlkResourcesResolved(s_resource_selected,1)),ResourceChoice(TlkResourcesResolved(s_resource_selected,0)),
        !node->leaf?"Children inherit this branch":!node->md_supported?"MD adapter unavailable":node->scope,
        "Unsupported scenes use SNES.");
}
static void ResourceClose(int whole) {
    TlkResourcesRevert();s_resource_message[0]=0;s_about=0;if(whole)CloseMenu();
}
static void ResourceAction(int action) {
    s_resource_message[0]=0;
    if(action==0) {
        if(!TlkResourcesDirty()) { snprintf(s_resource_message,sizeof s_resource_message,"No pending changes");return; }
        if(TlkResourcesApply())TlkResourcesHostApplied();
        snprintf(s_resource_message,sizeof s_resource_message,"%s",TlkResourcesStatus());
    } else if(action==1)TlkResourcesRevert();
    else if(action==2)TlkResourcesDefaults();
    else if(action==3)TlkResourcesGraphicsPreset();
    else if(action==4) {
        TlkResourcesMdPreset();
        snprintf(s_resource_message,sizeof s_resource_message,"Available MD choices selected.\nUnavailable choices stay SNES.\nApply to save and restart.\nIndividual choices can be edited.");
    }
    else if(action==5)ResourceClose(0);
}
static void ResourceMove(int delta) {
    int position=ResourcePosition();if(position<0)return;
    position+=delta;if(position<0)position=0;if(position>=s_resource_rows)position=s_resource_rows-1;
    s_resource_selected=s_resource_visible[position];s_resource_action=-1;
}
static void ResourceCycle(void) {
    int choice=TlkResourcesChoice(s_resource_selected,1)+1;
    if(choice>TLK_SOURCE_MD)choice=s_resource_selected?TLK_SOURCE_INHERIT:TLK_SOURCE_SNES;
    TlkResourcesSet(s_resource_selected,choice);
}
static void ResourceKey(SDL_Keycode key,int repeat) {
    if(s_resource_message[0]) { s_resource_message[0]=0;return; }
    if(!ResourceEnsure()) { if(key==SDLK_ESCAPE)ResourceClose(0);return; }
    if(key==SDLK_ESCAPE) { ResourceClose(0);return; }
    if(key==SDLK_F12) { ResourceClose(1);return; }
    if(key==SDLK_UP) { ResourceMove(-1);return; }
    if(key==SDLK_DOWN) { ResourceMove(1);return; }
    if(key==SDLK_PAGEUP) { ResourceMove(-10);return; }
    if(key==SDLK_PAGEDOWN) { ResourceMove(10);return; }
    if(key==SDLK_HOME) { s_resource_selected=0;s_resource_action=-1;return; }
    if(key==SDLK_END) { ResourcePosition();s_resource_selected=s_resource_visible[s_resource_rows-1];s_resource_action=-1;return; }
    if(key==SDLK_TAB) { s_resource_action=(s_resource_action+2)%(RESOURCE_ACTION_COUNT+1)-1;return; }
    if(key==SDLK_LEFT || key==SDLK_RIGHT) {
        if(s_resource_action>=0) { s_resource_action=(s_resource_action+(key==SDLK_RIGHT?1:RESOURCE_ACTION_COUNT-1))%RESOURCE_ACTION_COUNT;return; }
        const TlkResourceNode *node=TlkResourcesNode(s_resource_selected);
        if(key==SDLK_RIGHT && !node->leaf)s_resource_open[s_resource_selected]=1;
        else if(key==SDLK_LEFT) {
            if(!node->leaf && s_resource_open[s_resource_selected])s_resource_open[s_resource_selected]=0;
            else if(node->parent>=0)s_resource_selected=node->parent;
        }
        return;
    }
    if(repeat)return;
    if(key==SDLK_RETURN || key==SDLK_KP_ENTER || key==SDLK_SPACE) {
        if(s_resource_action>=0)ResourceAction(s_resource_action);else ResourceCycle();
    } else if(key==SDLK_H)ResourceInfo();
    else if(key==SDLK_F2)ResourceAction(0);
    else if(key==SDLK_F3)ResourceAction(1);
    else if(key==SDLK_F4)ResourceAction(2);
    else if(key==SDLK_F6)ResourceAction(3);
    else if(key==SDLK_F7)ResourceAction(4);
}
static void ResourcePad(SDL_GamepadButton button) {
    switch(button) {
    case SDL_GAMEPAD_BUTTON_DPAD_UP: ResourceKey(SDLK_UP,0);break;
    case SDL_GAMEPAD_BUTTON_DPAD_DOWN: ResourceKey(SDLK_DOWN,0);break;
    case SDL_GAMEPAD_BUTTON_DPAD_LEFT: ResourceKey(SDLK_LEFT,0);break;
    case SDL_GAMEPAD_BUTTON_DPAD_RIGHT: ResourceKey(SDLK_RIGHT,0);break;
    case SDL_GAMEPAD_BUTTON_SOUTH: ResourceKey(SDLK_RETURN,0);break;
    case SDL_GAMEPAD_BUTTON_EAST: ResourceKey(SDLK_ESCAPE,0);break;
    case SDL_GAMEPAD_BUTTON_WEST: ResourceKey(SDLK_F2,0);break;
    case SDL_GAMEPAD_BUTTON_NORTH: ResourceKey(SDLK_H,0);break;
    case SDL_GAMEPAD_BUTTON_LEFT_SHOULDER: ResourceKey(SDLK_F3,0);break;
    case SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER: ResourceKey(SDLK_TAB,0);break;
    case SDL_GAMEPAD_BUTTON_START: case SDL_GAMEPAD_BUTTON_GUIDE: ResourceClose(1);break;
    default:break;
    }
}
static void DrawResourceEditor(void) {
    Panel(0,0,kWidth,kHeight);Ink(255,255,255);DrawText(8,4,"VERSION RESOURCES");
    DrawText(232,4,TlkResourcesDirty()?"*":"");
    Ink(180,190,210);DrawText(4,16,"Arrows:move/fold Enter:source");DrawText(4,26,"Tab:actions F7:MD H:info");
    int position=ResourcePosition();if(position<0) { DrawText(8,60,"Editor unavailable");return; }
    if(position<s_resource_top)s_resource_top=position;
    if(position>=s_resource_top+10)s_resource_top=position-9;
    Ink(160,160,160);DrawText(8,40,"RESOURCE");DrawText(208,40,"CHOICE");
    for(int row=0;row<10 && s_resource_top+row<s_resource_rows;row++) {
        int index=s_resource_visible[s_resource_top+row],y=52+row*11;
        const TlkResourceNode *node=TlkResourcesNode(index);
        if(index==s_resource_selected && s_resource_action<0)ResourceBox(4,y-1,248,10,0x27334c);
        int indent=ResourceDepth(index)*6;if(indent>54)indent=54;
        Ink(220,220,220);DrawText(8+indent,y,node->leaf?" ":s_resource_open[index]?"-":"+");
        ResourceText(16+indent,y,node->label,(192-16-indent)/8,1);
        Ink(node->leaf && !node->md_supported?170:240,node->leaf && !node->md_supported?150:210,160);
        DrawText(208,y,ResourceChoice(TlkResourcesChoice(index,1)));
    }
    const TlkResourceNode *node=TlkResourcesNode(s_resource_selected);
    Ink(190,190,190);ResourceText(4,164,node->id,31,2);
    char support[80];snprintf(support,sizeof support,"%s",!node->leaf?"Children inherit branch choice":!node->md_supported?"MD: unavailable (SNES only)":
        node->change==TLK_CHANGE_LIVE?"MD: live; H shows supported scope":node->change==TLK_CHANGE_LEVEL?"MD: level restart; H shows scope":"MD: game restart; H shows scope");
    ResourceText(4,186,support,31,1);
    int x=4;
    for(int i=0;i<RESOURCE_ACTION_COUNT;i++) {
        int width=(int)strlen(kResourceActions[i])*8+8;
        if(s_resource_action==i)ResourceBox(x,201,width,12,0x42577b);
        Ink(240,240,240);DrawText(x+4,203,kResourceActions[i]);x+=width+2;
    }
    if(s_resource_message[0]) {
        ResourceBox(4,72,248,122,0x182133);Ink(255,220,160);ResourceText(8,78,s_resource_message,30,10);
        Ink(190,190,190);DrawText(8,182,"Press a key to return");
    }
}
static int ResourceMouse(const SDL_Event *event) {
    if(event->type==SDL_EVENT_MOUSE_WHEEL) { ResourceMove(event->wheel.y>0?-3:3);return 1; }
    if(event->type!=SDL_EVENT_MOUSE_BUTTON_DOWN || event->button.button!=SDL_BUTTON_LEFT)return 0;
    if(s_resource_message[0]) { s_resource_message[0]=0;return 1; }
    int dw=0,dh=0,window_w=0,window_h=0;SDL_GetCurrentRenderOutputSize(ren,&dw,&dh);SDL_GetWindowSize(win,&window_w,&window_h);
    int width=WideWidth();if(!width)width=kWidth;
    SnesDisplayViewport viewport;ComputeViewport(width,kHeight,dw,dh,&viewport);
    if(window_w<=0 || window_h<=0 || viewport.width<=0 || viewport.height<=0)return 1;
    int x=(int)((event->button.x*dw/window_w-viewport.x)*width/viewport.width)-(width-kWidth)/2;
    int y=(int)((event->button.y*dh/window_h-viewport.y)*kHeight/viewport.height);
    if(x<0 || x>=kWidth || y<0 || y>=kHeight)return 1;
    ResourcePosition();
    if(y>=52 && y<162) {
        int row=(y-52)/11+s_resource_top;
        if(row<s_resource_rows) {
            s_resource_selected=s_resource_visible[row];s_resource_action=-1;
            const TlkResourceNode *node=TlkResourcesNode(s_resource_selected);
            int indent=ResourceDepth(s_resource_selected)*6;if(indent>54)indent=54;
            if(x>=204)ResourceCycle();
            else if(!node->leaf && x<16+indent)s_resource_open[s_resource_selected]^=1;
        }
    } else if(y>=201 && y<216) {
        int left=4;
        for(int i=0;i<RESOURCE_ACTION_COUNT;i++) { int width=(int)strlen(kResourceActions[i])*8+8;if(x>=left && x<left+width) { s_resource_action=i;ResourceAction(i);break; }left+=width+2; }
    }
    return 1;
}

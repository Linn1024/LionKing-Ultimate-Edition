/* SDL virtual-device regression, called only by --selftest-remap. */
static void StResourceButton(SDL_Joystick *js,SDL_GamepadButton button) {
    SDL_SetJoystickVirtualButton(js,button,true);StPump();
    SDL_SetJoystickVirtualButton(js,button,false);StPump();
}
static int StResourceSelect(SDL_Joystick *js,const char *id) {
    StTap(SDLK_HOME);
    for(int tries=0;tries<TlkResourcesCount()*2;tries++) {
        const TlkResourceNode *node=TlkResourcesNode(s_resource_selected);
        if(!strcmp(node->id,id))return 1;
        size_t n=strlen(node->id);
        if(!s_resource_selected || (!strncmp(id,node->id,n) && id[n]=='.'))
            StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_RIGHT);
        int previous=s_resource_selected;StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_DOWN);
        if(previous==s_resource_selected)return 0;
    }
    return 0;
}
static void StResourceChoice(SDL_Joystick *js,int value) {
    for(int i=0;i<3 && TlkResourcesChoice(s_resource_selected,1)!=value;i++)
        StResourceButton(js,SDL_GAMEPAD_BUTTON_SOUTH);
}
static void StResourceSelfTest(SDL_Joystick *js) {
    int count=TlkResourcesCount();int *applied=malloc((size_t)count*sizeof *applied);
    StCheck(applied!=NULL,"tree active-choice snapshot allocated");if(!applied)return;
    for(int i=0;i<count;i++)applied[i]=TlkResourcesChoice(i,0);
    SDL_SetJoystickVirtualButton(js,SDL_GAMEPAD_BUTTON_BACK,false);
    SDL_SetJoystickVirtualButton(js,SDL_GAMEPAD_BUTTON_START,false);StPump();
    CloseMenu();StTap(SDLK_F12);
    StCheck(s_menu_open && s_about==2 && !s_menu_gl,"F12 opens the fallback editor");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_LEFT);
    StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_DOWN);
    StCheck(s_resource_selected==0 && !s_resource_open[0],"virtual d-pad folds root and stays on visible node");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_RIGHT);
    StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_DOWN);
    StCheck(!strcmp(TlkResourcesNode(s_resource_selected)->id,"display"),"virtual d-pad expands root and visits Display first");
    StCheck(StResourceSelect(js,"graphics.sprites.simba.cub"),"virtual d-pad reaches nested Cub branch");
    StResourceChoice(js,TLK_SOURCE_MD);
    StCheck(StResourceSelect(js,"graphics.sprites.simba.cub.palette"),"virtual d-pad reaches nested palette override");
    StResourceChoice(js,TLK_SOURCE_SNES);
    StCheck(TlkResourcesDirty() && TlkResourcesResolved(TlkResourcesFind("graphics.sprites.simba.cub.frames"),1)==TLK_SOURCE_MD &&
        TlkResourcesResolved(s_resource_selected,1)==TLK_SOURCE_SNES,"virtual A edits branch inheritance and contrary leaf override");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER);
    StCheck(s_resource_action==0,"virtual RB focuses Apply");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_RIGHT);
    StCheck(s_resource_action==1,"virtual d-pad selects Revert action");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_SOUTH);
    StCheck(!TlkResourcesDirty(),"virtual A invokes footer Revert");
    StCheck(StResourceSelect(js,"graphics.sprites.simba.adult.frames"),"virtual d-pad reaches unsupported adapter");
    StResourceChoice(js,TLK_SOURCE_MD);StResourceButton(js,SDL_GAMEPAD_BUTTON_WEST);
    StCheck(s_resource_message[0] && TlkResourcesDirty(),"virtual X Apply rejects unsupported draft");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_EAST);
    StCheck(!s_resource_message[0] && s_about==2,"virtual B dismisses validation and keeps editor open");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_LEFT_SHOULDER);
    StCheck(!TlkResourcesDirty(),"virtual LB reverts rejected draft");
    StCheck(StResourceSelect(js,"graphics.sprites.simba.cub.frames"),"virtual d-pad reaches long capability description");
    int selected=s_resource_selected;
    StResourceButton(js,SDL_GAMEPAD_BUTTON_NORTH);
    StCheck(s_resource_message[0] && ResourceMessagePages()>1 &&
        strstr(s_resource_message,TlkResourcesNode(selected)->scope) && strstr(s_resource_message,"Unsupported scenes use SNES."),
        "virtual Y opens complete paged scope and fallback text");
    StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_DOWN);
    StCheck(s_resource_page==1 && s_resource_selected==selected,"virtual d-pad pages help without moving tree");
    for(int i=0;i<10;i++)StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_DOWN);
    StCheck(s_resource_page==ResourceMessagePages()-1,"help navigation clamps at last page");
    for(int i=0;i<10;i++)StResourceButton(js,SDL_GAMEPAD_BUTTON_DPAD_UP);
    StCheck(s_resource_page==0,"help navigation clamps at first page");
    SDL_Event wheel;SDL_zero(wheel);wheel.type=SDL_EVENT_MOUSE_WHEEL;wheel.wheel.y=-1;
    SDL_PushEvent(&wheel);StPump();
    StCheck(s_resource_page==1 && s_resource_selected==selected,"SDL wheel pages modal without moving tree");
    wheel.wheel.y=0;SDL_PushEvent(&wheel);StPump();
    StCheck(s_resource_page==1 && s_resource_selected==selected,"horizontal or zero wheel leaves help page unchanged");
    Present();StResourceButton(js,SDL_GAMEPAD_BUTTON_EAST);
    StResourceChoice(js,TLK_SOURCE_MD);StResourceButton(js,SDL_GAMEPAD_BUTTON_EAST);
    StCheck(s_menu_open && s_about==0 && !TlkResourcesDirty(),"virtual B cancels nested edit and returns to Resources");
    StTap(SDLK_ESCAPE);StTap(SDLK_ESCAPE);StTap(SDLK_F12);
    StResourceButton(js,SDL_GAMEPAD_BUTTON_START);
    StCheck(!s_menu_open && !s_about,"virtual Start closes entire resource editor");
    StTap(SDLK_F12);StResourceButton(js,SDL_GAMEPAD_BUTTON_GUIDE);
    StCheck(!s_menu_open && !s_about,"virtual Guide closes entire resource editor");
    int same=1;for(int i=0;i<count;i++)if(TlkResourcesChoice(i,0)!=applied[i])same=0;
    StCheck(same && !TlkResourcesDirty(),"virtual editor test preserves every applied resource choice");
    free(applied);
}

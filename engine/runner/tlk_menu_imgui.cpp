/* tlk_menu_imgui.cpp -- Dear ImGui glue for tlk_sdl's in-game menu.
 *
 * The menu itself (rows, navigation, status line, look) is recomp-ui's
 * runtime menu (recomp-ui/src/recomp_runtime_ui.h); sdl_main.c owns its rows
 * and callbacks. This file only gives it an ImGui frame to draw in: one
 * context on the OpenGL presenter's window, fed SDL events, rendered from the
 * presenter's overlay hook between the game picture and the swap. ImGui's own
 * keyboard/gamepad navigation stays off; sdl_main.c drives the menu. */
#include "tlk_menu_imgui.h"
#include "tlk_resources.h"
#include "tlk_md_assets.h"
#include "tlk_visual_resources.h"

#include "imgui.h"
#include "launcher_theme.h"
#include "imgui_impl_opengl3.h"
#include "imgui_impl_sdl3.h"

#include <cstdio>
#include <cstring>
extern "C" { int (*g_tlk_visual_resources_open)(SDL_Window *)=nullptr; }

static bool s_ready;
static SDL_Window *s_win;

/* recomp-ui's desktop layout needs about 768x672 (the window at scale 3);
 * smaller, its footer runs into the Resume button. A smaller window gets the
 * menu laid out at that size and shrunk to fit: s_shrink < 1. */
enum { kLayoutW = 768, kLayoutH = 672 };
static float s_shrink = 1.0f;

static void UpdateShrink(void) {
    int w = 0, h = 0;
    SDL_GetWindowSize(s_win, &w, &h);
    float k = 1.0f;
    if (w > 0 && w < kLayoutW) k = (float)w / kLayoutW;
    if (h > 0 && (float)h / kLayoutH < k) k = (float)h / kLayoutH;
    s_shrink = k;
}

extern "C" int TlkMenuImguiInit(SDL_Window *win, const char *font_path, float font_px) {
    if (s_ready) return 1;
    SDL_GLContext ctx = SDL_GL_GetCurrentContext();
    if (!ctx) return 0;
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO &io = ImGui::GetIO();
    io.IniFilename = nullptr;   /* nothing to remember: the menu lays itself out */
    io.LogFilename = nullptr;
    io.ConfigFlags |= ImGuiConfigFlags_NoMouse;   /* until the mouse moves (UseMouse) */
    /* Sizes stay in window units; on a HiDPI display the glyphs are
     * rasterized at its pixel density so they are sharp, not magnified. */
    ImFontConfig cfg;
    float density = SDL_GetWindowPixelDensity(win);
    cfg.RasterizerDensity = density > 0.0f ? density : 1.0f;
    ImFont *font = nullptr;
    if (font_path) {
        if (FILE *f = std::fopen(font_path, "rb")) {
            std::fclose(f);
            font = io.Fonts->AddFontFromFileTTF(font_path, font_px, &cfg);
        }
    }
    if (!font) {
        cfg.SizePixels = font_px;
        io.Fonts->AddFontDefault(&cfg);
        std::fprintf(stderr, "menu: font %s not found, using ImGui's own\n", font_path ? font_path : "(none)");
    }
    if (!ImGui_ImplSDL3_InitForOpenGL(win, ctx) || !ImGui_ImplOpenGL3_Init("#version 330")) {
        ImGui::DestroyContext();
        return 0;
    }
    s_win = win;
    s_ready = true;
    return 1;
}

/* recomp-ui selects the row under the mouse pointer every frame, so a pointer
 * that merely rests over the window would undo every key press. The mouse
 * counts only from the moment it is moved or clicked, until the next key or
 * pad button. */
static void UseMouse(bool on) {
    ImGuiIO &io = ImGui::GetIO();
    if (on) io.ConfigFlags &= ~ImGuiConfigFlags_NoMouse;
    else io.ConfigFlags |= ImGuiConfigFlags_NoMouse;
}

extern "C" void TlkMenuImguiEvent(const SDL_Event *ev) {
    if (!s_ready) return;
    switch (ev->type) {
    case SDL_EVENT_MOUSE_MOTION:
    case SDL_EVENT_MOUSE_BUTTON_DOWN:
    case SDL_EVENT_MOUSE_WHEEL: UseMouse(true); break;
    case SDL_EVENT_KEY_DOWN:
    case SDL_EVENT_GAMEPAD_BUTTON_DOWN: UseMouse(false); break;
    default: break;
    }
    if (s_shrink < 1.0f && (ev->type == SDL_EVENT_MOUSE_MOTION || ev->type == SDL_EVENT_MOUSE_BUTTON_DOWN ||
                            ev->type == SDL_EVENT_MOUSE_BUTTON_UP)) {
        SDL_Event e = *ev;   /* window coordinates -> the shrunk layout's */
        if (e.type == SDL_EVENT_MOUSE_MOTION) { e.motion.x /= s_shrink; e.motion.y /= s_shrink; }
        else { e.button.x /= s_shrink; e.button.y /= s_shrink; }
        ImGui_ImplSDL3_ProcessEvent(&e);
        return;
    }
    ImGui_ImplSDL3_ProcessEvent(ev);
}

extern "C" void TlkMenuImguiOpened(void) {
    if (s_ready) UseMouse(false);
}

static ImVec4 Col(const LngColor &c) { return ImVec4(c.r, c.g, c.b, c.a); }

/* The About window: why this port exists, by whom, and where the source is.
 * Centred over the menu in the menu's own theme; the links open the browser
 * (mouse); the About section's rows do the same from the keyboard or a pad. */
static void DrawAbout(int *about) {
    static const LauncherTheme t = launcher_theme_by_name("snes");
    ImGuiIO &io = ImGui::GetIO();
    ImGui::SetNextWindowPos(ImVec2(io.DisplaySize.x * 0.5f, io.DisplaySize.y * 0.5f), ImGuiCond_Always,
                            ImVec2(0.5f, 0.5f));
    ImGui::SetNextWindowSize(ImVec2(520.0f, 0.0f), ImGuiCond_Always);
    ImGui::SetNextWindowFocus();
    ImGui::PushStyleVar(ImGuiStyleVar_WindowRounding, t.radius_lg);
    ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(t.spacing_lg * 1.5f, t.spacing_lg * 1.5f));
    ImGui::PushStyleVar(ImGuiStyleVar_ItemSpacing, ImVec2(t.spacing_sm, t.spacing_md));
    ImGui::PushStyleVar(ImGuiStyleVar_WindowBorderSize, 1.0f);
    ImGui::PushStyleColor(ImGuiCol_WindowBg, Col(t.panel));
    ImGui::PushStyleColor(ImGuiCol_Border, Col(t.accent2));
    ImGui::PushStyleColor(ImGuiCol_Separator, Col(t.border));
    ImGui::PushStyleColor(ImGuiCol_Text, Col(t.text));
    ImGui::PushStyleColor(ImGuiCol_TextDisabled, Col(t.text_muted));
    ImGui::PushStyleColor(ImGuiCol_TextLink, Col(t.accent2));
    ImGui::PushStyleColor(ImGuiCol_Button, Col(t.control));
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, Col(t.control_hovered));
    ImGui::PushStyleColor(ImGuiCol_ButtonActive, Col(t.accent_dim));
    const ImGuiWindowFlags flags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
                                   ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoNavInputs |
                                   ImGuiWindowFlags_AlwaysAutoResize;
    if (ImGui::Begin("##tlk-about", nullptr, flags)) {
        ImGui::PushStyleColor(ImGuiCol_Text, Col(t.accent2));
        ImGui::TextUnformatted("About");
        ImGui::PopStyleColor();
        ImGui::Separator();
        ImGui::TextWrapped("When I was around 8 years old, my family and I would gather around the kitchen TV to "
                           "try to beat this game. We still love it, and it's an important part of our family "
                           "lore.");
        ImGui::TextWrapped("This effort is a tribute: to my family, to my kid self, and to the community, which "
                           "I'm sure will enjoy it.");
        ImGui::TextUnformatted("Alejandro AR");
        ImGui::SameLine();
        ImGui::TextLinkOpenURL("kinduff.com", "https://kinduff.com");
        ImGui::TextDisabled("Source:");
        ImGui::SameLine();
        ImGui::TextLinkOpenURL("github.com/kinduff/TLKRecomp", "https://github.com/kinduff/TLKRecomp");
        ImGui::Separator();
        ImGui::AlignTextToFramePadding();
        ImGui::TextDisabled("Esc/B  Close");
        const char *close = "Close";
        const float close_w = ImGui::CalcTextSize(close).x + t.spacing_lg * 2.0f;
        ImGui::SameLine(ImGui::GetContentRegionMax().x - close_w);
        if (ImGui::Button(close, ImVec2(close_w, 0.0f))) *about = 0;
    }
    ImGui::End();
    ImGui::PopStyleColor(9);
    ImGui::PopStyleVar(4);
}

extern "C" void TlkResourcesHostApplied(void);
extern "C" unsigned TlkResourcesHostLevel(void);
extern "C" unsigned TlkResourcesHostDescriptor(void);
extern "C" int TlkAudioMusicAvailable(const char *id);
extern "C" int TlkMdSpritesCubScene(unsigned level,unsigned descriptor);

static void ResourceRow(int i) {
    const TlkResourceNode *node = TlkResourcesNode(i);
    ImGui::PushID(i);
    ImGui::TableNextRow();
    ImGui::TableSetColumnIndex(0);
    ImGuiTreeNodeFlags flags = ImGuiTreeNodeFlags_SpanAllColumns;
    if (node->leaf) flags |= ImGuiTreeNodeFlags_Leaf | ImGuiTreeNodeFlags_NoTreePushOnOpen;
    else if (i <= 4 || !strcmp(node->id,"display")) flags |= ImGuiTreeNodeFlags_DefaultOpen;
    /* Span only the label column; controls in adjacent columns stay clickable. */
    flags &= ~ImGuiTreeNodeFlags_SpanAllColumns;
    bool open = ImGui::TreeNodeEx(node->label, flags);
    if (ImGui::IsItemHovered()) ImGui::SetTooltip("%s", node->id);
    ImGui::TableSetColumnIndex(1);
    int choice = TlkResourcesChoice(i, 1);
    ImGui::SetNextItemWidth(-1);
    const char *choices = i ? "Inherit\0SNES\0Mega Drive\0" : "SNES\0Mega Drive\0";
    int shown = i ? choice : choice - 1;
    if (ImGui::Combo("##source", &shown, choices)) TlkResourcesSet(i, i ? shown : shown + 1);
    ImGui::TableSetColumnIndex(2);
    int source=TlkResourcesResolved(i,0);
    unsigned matched=0,total=0,level=TlkResourcesHostLevel();
    bool scene_leaf=node->leaf && !strncmp(node->id,"graphics.scenery.",17);
    bool background_leaf=!strcmp(node->id,"graphics.scenery.background");
    unsigned descriptor=TlkResourcesHostDescriptor();
    bool pride_scene=level==0 && (descriptor==0x387 || descriptor==0x80d);
    bool music_leaf=node->leaf && !strncmp(node->id,"audio.music.",12);
    if (source==TLK_SOURCE_MD && music_leaf && !TlkAudioMusicAvailable(node->id)) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && (!strcmp(node->id,"gameplay.levels.pride_lands.start") ||
             !strcmp(node->id,"gameplay.levels.pride_lands.activation")) &&
             (level!=0 || descriptor!=0x387)) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && !strncmp(node->id,"gameplay.hitboxes.",18) &&
             !pride_scene) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && (!strcmp(node->id,"gameplay.levels.pride_lands.ceiling_rows") ||
             !strcmp(node->id,"gameplay.levels.pride_lands.ceiling_clearance") ||
             !strcmp(node->id,"gameplay.levels.pride_lands.streaming_top")) &&
             !pride_scene) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && !strcmp(node->id,"gameplay.levels.pride_lands.lizard_reactivation") &&
             !pride_scene) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && !pride_scene && ((node->md_supported && !strncmp(node->id,"audio.effects.",14)) ||
        (!strcmp(node->id,"graphics.sprites.simba.cub.frames") && !TlkMdSpritesCubScene(level,descriptor)) ||
        !strcmp(node->id,"gameplay.camera") ||
        !strcmp(node->id,"gameplay.levels.pride_lands.pickups") ||
        !strcmp(node->id,"gameplay.levels.pride_lands.leaves") ||
        !strcmp(node->id,"gameplay.levels.pride_lands.contacts") ||
        !strcmp(node->id,"gameplay.simba.roar") ||
        !strcmp(node->id,"graphics.hud.frames") ||
        !strcmp(node->id,"graphics.sprites.leaves.frames") ||
        !strcmp(node->id,"graphics.sprites.leaves.palette") ||
        !strncmp(node->id,"graphics.sprites.effects.defeat_puff.",37) ||
        !strncmp(node->id,"graphics.sprites.enemies.",24) ||
        !strncmp(node->id,"graphics.sprites.checkpoints.",29) ||
        !strncmp(node->id,"graphics.sprites.pickups.",24))) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && scene_leaf &&
        !(background_leaf ? TlkMdSceneBackgroundReady(level) : TlkMdSceneReady(level))) ImGui::TextUnformatted("SNES fallback");
    else if (source==TLK_SOURCE_MD && !strcmp(node->id,"graphics.scenery.foreground") &&
             TlkMdSceneCoverage(level,&matched,&total) && matched<total) ImGui::TextUnformatted("MD + SNES");
    else ImGui::TextUnformatted(source==TLK_SOURCE_MD ? "Mega Drive" : "SNES");
    ImGui::TableSetColumnIndex(3);
    if (!node->leaf) ImGui::TextDisabled("Branch");
    else if (node->md_supported) {
        bool camera_viewport=!strcmp(node->id,"display.viewport") &&
            (TlkResourcesResolved(TlkResourcesFind("gameplay.camera"),0)==TLK_SOURCE_MD ||
             TlkResourcesResolved(TlkResourcesFind("gameplay.camera"),1)==TLK_SOURCE_MD);
        ImGui::TextColored(ImVec4(.6f,.85f,.55f,1), "%s",node->change==TLK_CHANGE_LEVEL || camera_viewport?"Level restart":node->change==TLK_CHANGE_GAME?"Game restart":"Live");
        if (*node->scope && ImGui::IsItemHovered()) {
            if (!strcmp(node->id,"graphics.scenery.foreground") && TlkMdSceneCoverage(level,&matched,&total))
                ImGui::SetTooltip("%u of %u terrain cells can use MD artwork. Other cells retain SNES artwork.\nThe selected layout and collision remain unchanged.",matched,total);
            else ImGui::SetTooltip("Mega Drive support: %s", node->scope);
        }
    } else ImGui::TextDisabled("SNES only");
    if (open && !node->leaf) {
        if (i==0) ResourceRow(TlkResourcesFind("display"));
        for (int child = i+1; child < TlkResourcesCount(); child++)
            if (TlkResourcesNode(child)->parent == i && (i!=0 || strcmp(TlkResourcesNode(child)->id,"display"))) ResourceRow(child);
        ImGui::TreePop();
    }
    ImGui::PopID();
}

static void DrawResources(int *about) {
    int visual=g_tlk_visual_resources_open?g_tlk_visual_resources_open(s_win):-1;
    if(visual>=0){*about=0;if(visual)TlkResourcesHostApplied();return;}
    ImGuiIO &io = ImGui::GetIO();
    ImGui::SetNextWindowPos(ImVec2(io.DisplaySize.x*.5f,io.DisplaySize.y*.5f),ImGuiCond_Always,ImVec2(.5f,.5f));
    ImGui::SetNextWindowSize(ImVec2(736,620),ImGuiCond_Always);
    const ImGuiWindowFlags flags = ImGuiWindowFlags_NoCollapse | ImGuiWindowFlags_NoSavedSettings |
                                   ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize;
    if (ImGui::Begin("Version resources", nullptr, flags)) {
        ImGui::TextWrapped("Choose a source for a branch. Children inherit it until you override them.");
        ImGui::TextDisabled("Source availability and native fallbacks are listed per resource.");
        ImGui::TextDisabled("Foreground preserves the selected layout; unsupported terrain and scenes retain SNES art.");
        ImGui::TextWrapped("%s", TlkResourcesMdStatus());
        ImGui::Separator();
        const ImGuiTableFlags tf = ImGuiTableFlags_BordersInnerH | ImGuiTableFlags_RowBg |
                                   ImGuiTableFlags_ScrollY | ImGuiTableFlags_SizingStretchProp;
        if (ImGui::BeginTable("resource-tree", 4, tf, ImVec2(0,385))) {
            ImGui::TableSetupColumn("Resource", ImGuiTableColumnFlags_WidthStretch, 3.4f);
            ImGui::TableSetupColumn("Choice", ImGuiTableColumnFlags_WidthStretch, 1.6f);
            ImGui::TableSetupColumn("Active", ImGuiTableColumnFlags_WidthStretch, 1.1f);
            ImGui::TableSetupColumn("MD support", ImGuiTableColumnFlags_WidthStretch, 1.3f);
            ImGui::TableSetupScrollFreeze(0,1);
            ImGui::TableHeadersRow();
            ResourceRow(0);
            ImGui::EndTable();
        }
        char reason[256];
        int blocked = TlkResourcesValidate(reason,sizeof reason);
        if (blocked) {
            ImGui::TextColored(ImVec4(1,.7f,.35f,1), "%d unavailable selection(s)",blocked);
            ImGui::TextWrapped("%s",reason);
        } else {
            ImGui::TextUnformatted(TlkResourcesStatus());
            if (TlkResourcesDirty()) ImGui::TextDisabled("Graphics apply live; gameplay/audio changes restart the current level.");
        }
        ImGui::BeginDisabled(blocked || !TlkResourcesDirty());
        if (ImGui::Button("Apply and save")) if (TlkResourcesApply()) TlkResourcesHostApplied();
        ImGui::EndDisabled();
        ImGui::SameLine();
        if (ImGui::Button("Revert")) TlkResourcesRevert();
        ImGui::SameLine();
        if (ImGui::Button("SNES defaults")) TlkResourcesDefaults();
        ImGui::SameLine();
        if (ImGui::Button("Mixed graphics")) TlkResourcesGraphicsPreset();
        ImGui::SameLine();
        if (ImGui::Button("Available MD")) TlkResourcesMdPreset();
        if (ImGui::IsItemHovered()) ImGui::SetTooltip("Select available MD choices; unavailable choices stay SNES. Apply saves the profile and restarts when needed.");
        ImGui::SameLine();
        if (ImGui::Button("Close")) { TlkResourcesRevert(); *about=0; }
        ImGui::TextDisabled("Tab: focus control   Arrows / Enter: edit   Esc: close   Apply commits the whole profile.");
    }
    ImGui::End();
}

extern "C" void TlkMenuImguiDraw(RecompRuntimeUi *ui, int *about) {
    if (!s_ready) return;
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplSDL3_NewFrame();
    UpdateShrink();
    if (s_shrink < 1.0f) {
        ImGuiIO &io = ImGui::GetIO();
        io.DisplaySize.x /= s_shrink;
        io.DisplaySize.y /= s_shrink;
        io.DisplayFramebufferScale.x *= s_shrink;
        io.DisplayFramebufferScale.y *= s_shrink;
    }
    ImGui::NewFrame();
    if (*about == 2) {
        ImGui::GetIO().ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard | ImGuiConfigFlags_NavEnableGamepad;
        DrawResources(about);
    } else {
        ImGui::GetIO().ConfigFlags &= ~(ImGuiConfigFlags_NavEnableKeyboard | ImGuiConfigFlags_NavEnableGamepad);
        recomp_runtime_ui_render_imgui(ui);
        if (*about == 1) DrawAbout(about);
    }
    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

extern "C" void TlkMenuImguiShutdown(void) {
    if (!s_ready) return;
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplSDL3_Shutdown();
    ImGui::DestroyContext();
    s_ready = false;
}

#pragma once
/* A labelled explanation of the actual anchoring rule, not a game screenshot. */
static void TlkBrowserDrawSkyPlacement() {
    ImGui::SeparatorText("Mufasa's face at the end of Destiny");
    ImGui::TextWrapped("SNES keeps the face in one place in the level. Genesis places it above and to the left of Simba, so its location depends on where he finishes.");
    static float player=.65f;ImGui::TextUnformatted("Move Simba in this example");ImGui::SetNextItemWidth(-1);ImGui::SliderFloat("##example-simba",&player,.4f,.9f,"",ImGuiSliderFlags_AlwaysClamp);
    if(ImGui::BeginTable("sky-placement",2,ImGuiTableFlags_SizingStretchSame)) {
        for(int source=0;source<2;source++) {
            ImGui::TableNextColumn();ImGui::TextUnformatted(source?"GENESIS":"SNES");
            auto p=ImGui::GetCursorScreenPos();float w=ImGui::GetContentRegionAvail().x,h=190;auto*d=ImGui::GetWindowDrawList();
            d->AddRectFilled(p,ImVec2(p.x+w,p.y+h),IM_COL32(15,18,58,255));
            float face=source?player-.3125f:.26f,fx=p.x+face*w,px=p.x+player*w;
            d->AddCircleFilled(ImVec2(fx,p.y+52),25,IM_COL32(174,139,71,255));
            ImVec2 label=ImGui::CalcTextSize("FACE");d->AddText(ImVec2(fx-label.x/2,p.y+86),IM_COL32(255,224,118,255),"FACE");
            ImVec2 simba=ImGui::CalcTextSize("SIMBA");d->AddText(ImVec2(px-simba.x/2,p.y+145),IM_COL32(255,224,118,255),"SIMBA");
            d->AddLine(ImVec2(p.x+8,p.y+174),ImVec2(p.x+w-8,p.y+174),IM_COL32(126,106,72,255),3);
            ImGui::Dummy(ImVec2(w,h));ImGui::TextWrapped("%s",source?"Follows Simba's finishing position.":"Stays at the same spot in the level.");
        }ImGui::EndTable();
    }ImGui::TextWrapped("Placement diagram only. Artwork, colours and animation are separate choices.");
}

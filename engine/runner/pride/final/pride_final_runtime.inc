/* Excluded next scene controller: allow initial drawing, suppress early UI
 * decisions, then hold before actor/menu updates until original input age124. */
#define __wrap_RtlRunFrame FinalSceneUnusedV3Frame
#define FinalSceneCaptureNative FinalSceneCaptureV3
#define FinalScenePaintNative ContinueTransitionInitialPaint
#include "pride_final_present.inc"
#undef FinalScenePaintNative
#undef FinalSceneCaptureNative
#undef __wrap_RtlRunFrame
#include "tlk_continue_menu.h"
#include "tlk_cant_wait_gameplay.h"
static int ContinueLifecycleEnabled(void);
static void ContinueLocalClear(void);
static uint32_t continue_menu_field,continue_title_fade_field;
static FILE *final_input_trace;
static unsigned final_input_reading;
static void FinalInputLog(const char *kind,CpuState *cpu) {
    if(!final_input_trace || !final_scene_entry)return;
    unsigned field=(unsigned)snes_frame_counter+(cpu?1u:0u);
    fprintf(final_input_trace,"%s,%u,%u,%04x,%02x,%02x,%04x,%04x,%04x,%u,%u,%u\n",kind,
        field,field-final_scene_entry,
        cpu?cpu->S:0,cpu?cpu->DB:0,cpu?cpu->P:0,FinalWord(0x5a),FinalWord(0x5c),FinalWord(0x5e),
        FinalWord(0xa68e),FinalWord(0xa6b4),FinalWord(0x1ffa8));fflush(final_input_trace);
}
static void FinalInputDecision(CpuState *cpu,uint32_t pc) {
    (void)pc;
    if(!final_scene_mode || !final_scene_entry)return;
    unsigned age=(unsigned)snes_frame_counter+1-final_scene_entry;
    if(FinalAddress(0xdf)!=0xc0057b || FinalWord(0x1ff9e))return;
    if(ContinueLifecycleEnabled() && !FinalWord(0x1ffa8) && age>=TLK_CONTINUE_MENU_FIRST_INPUT) {
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag ||
           cpu->S<0x200 || cpu->S>=0x300)exit(103);
        FinalInputLog("game_over",cpu);
        /* The MD Game Over loop has no selector/YES path. Preserve the real
         * pad service and actor updates, but use its200-field dismissal window
         * instead of the native500-update wait. Direction is not dismissal. */
        interp_bridge_pre_opcode_redirect(TlkGameOverMenuTimedOut(age) || (FinalWord(0x5a)&0xf0c0)?
            0xc08e2d:0xc08d77);return;
    }
    if(ContinueLifecycleEnabled() && TlkContinueMenuTimedOut(age)) {
        /* Use the original native timeout cleanup, preserving credits and
         * the real caller frame. Native code otherwise skips its timer while
         * a credit remains, unlike the selected MD menu behavior. */
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag ||
           cpu->S<0x200 || cpu->S>=0x300)exit(103);
        interp_bridge_pre_opcode_redirect(0xc08e2d);return;
    }
    FinalInputLog(age<124?"suppressed":"decision",cpu);
    if(age<TLK_CONTINUE_MENU_FIRST_INPUT) {
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag)exit(103);
        interp_bridge_pre_opcode_redirect(0xc08d77);
    }
}
static void FinalInputHold(CpuState *cpu,uint32_t pc) {
    NativeMenuEvent(NATIVE_MENU_LOOP);
    (void)pc;
    if(!final_scene_mode || !final_scene_entry)return;
    if(final_scene_waiting) {
        if(cpu->S!=final_scene_s)exit(103);
        if(!final_input_reading) {
            /* The original input service, with its hardware-page DB, refreshes
             * both held and edge words while the menu decision loop is held. */
            final_input_reading=1;cpu->DB=0;
            cpu_write8(cpu,0,cpu->S--,0x8c);cpu_write8(cpu,0,cpu->S--,0xcd);
            interp_bridge_pre_opcode_redirect(0xc0a073);return;
        }
        cpu->A=final_scene_a;cpu->X=final_scene_x;cpu->Y=final_scene_y;cpu->D=final_scene_d;
        cpu->DB=final_scene_db;cpu->P=final_scene_p;cpu_p_to_mirrors(cpu);
        final_scene_waiting=final_input_reading=0;
    }
    unsigned age=(unsigned)snes_frame_counter+1-final_scene_entry;
    if(age<90 || age>=124)return;
    if(FinalAddress(0xdf)!=0xc0057b || FinalWord(0x1ff9e) || cpu->D || cpu->DB!=0x7e ||
       cpu->m_flag || !cpu->x_flag || cpu->S<0x200 || cpu->S>=0x300)exit(103);
    final_scene_a=cpu->A;final_scene_x=cpu->X;final_scene_y=cpu->Y;final_scene_s=cpu->S;
    final_scene_d=cpu->D;final_scene_db=cpu->DB;cpu_mirrors_to_p(cpu);final_scene_p=cpu->P;
    final_scene_waiting=1;final_input_reading=0;
    cpu_write8(cpu,0,cpu->S--,0x8c);cpu_write8(cpu,0,cpu->S--,0xcd);
    interp_bridge_pre_opcode_redirect(0xc0983d);
}

static FILE *continue_exit_log;
static unsigned continue_exit_installed;
static void ContinueExitPoint(CpuState *cpu,uint32_t pc) {
    if(!continue_exit_log || !final_scene_entry)return;
    fprintf(continue_exit_log,"point,%u,%06x,%u,%u,%u,%u\n",
        (unsigned)snes_frame_counter+1-final_scene_entry,pc,FinalWord(0x2004),
        FinalWord(0x1ffaa),cpu->A,cpu->S);
    fflush(continue_exit_log);
}
static void ContinueExitCapture(const uint8_t *pixels) {
    if(!continue_exit_log || !final_scene_entry)return;
    const uint32_t *rgb=(const uint32_t *)pixels;
    unsigned lit=0,peak=0;
    for(unsigned i=0;i<256*224;i++) {
        unsigned p=rgb[i]&0xffffff;lit+=p!=0;
        for(unsigned shift=0;shift<24;shift+=8) {
            unsigned c=p>>shift&255;if(c>peak)peak=c;
        }
    }
    fprintf(continue_exit_log,"frame,%u,%06x,%u,%u,%u,%u\n",final_scene_age,
        FinalAddress(0xdf),FinalWord(0x2004),FinalWord(0x1ffaa),lit,peak);
}

static void ContinueTransitionPreviousCapture(const uint8_t *pixels) {
    FinalSceneCaptureV3(pixels);
    ContinueExitCapture(pixels);
    if(final_scene_entry && final_scene_age>=85 && final_scene_age<=130)FinalInputLog("frame",NULL);
}

/* Reviewed semantic reloads consume installer-prepared payloads. No APU snapshot. */
static unsigned reload_fast_mode,reload_fast_used;
static void ReloadFastWord(unsigned at,unsigned value) {g_ram[at]=value;g_ram[at+1]=value>>8;}
static void ReloadFastPoint(CpuState *cpu,uint32_t pc) {
    (void)pc;
    if(!reload_fast_mode || !final_scene_entry ||
       (unsigned)snes_frame_counter+1-final_scene_entry<200 || FinalWord(0x1ff9e))return;
    for(unsigned i=0;i<TLK_FINAL_NATIVE_RELOAD_COUNT;i++) {
        const TlkFinalNativeRecipe *recipe=TlkFinalNativeRecipeAt(i+1);
        if(reload_fast_used&(1u<<i))continue;
        if(FinalAddress(13)!=recipe->source || FinalAddress(10)!=recipe->destination)continue;
        if(cpu->D || g_snes->dma->dmaBusy || g_snes->dma->dmaTimer)exit(106);
        for(unsigned n=0;n<8;n++)if(g_snes->dma->channel[n].dmaActive)exit(106);
        size_t written=0;
        const uint8_t *payload=TlkFinalNativePayload(final_native_assets,i+1,&written);
        if(!payload || written!=recipe->size)exit(106);
        memcpy(g_ram+(recipe->destination&0x1ffff),payload,written);
        ReloadFastWord(10,recipe->destination_end);
        g_ram[12]=recipe->destination_end>>16;
        ReloadFastWord(13,recipe->source_end);g_ram[15]=recipe->source_end>>16;
        g_snes->ramAdr=recipe->destination_end&0x1ffff;
        reload_fast_used|=1u<<i;
        continue_menu_field=0;
        if(continue_exit_log) {fprintf(continue_exit_log,"fast,%u,%06x,%u,%u,%u,%u\n",
            (unsigned)snes_frame_counter+1-final_scene_entry,recipe->source,
            FinalWord(0x2004),FinalWord(0x1ffaa),i,(unsigned)written);fflush(continue_exit_log);}
        /* Entry prologue was not executed: retain real caller DB/P/stack and RTL. */
        interp_bridge_pre_opcode_redirect(0xc1cd85);return;
    }
}


/* Private Continue cache integration. Caller owns final-life/YES re-entry. */
static TlkNativeBankProgram *continue_bank_program;
static TlkNativeBank *continue_bank;
static const char *continue_bank_dir;
static FILE *continue_bank_log;
static unsigned continue_bank_apply;
static unsigned continue_transition_mode;
static void ContinueBankDump(const char *name) {
    if(!continue_bank_dir)return;
    char path[1024];snprintf(path,sizeof path,"%s/%s-apu.bin",continue_bank_dir,name);
    FILE *f=fopen(path,"wb");if(!f)exit(108);
    ProbeIo io={.base={.func=probe_write},.file=f};apu_saveload(g_snes->apu,&io.base);fclose(f);
    snprintf(path,sizeof path,"%s/%s-wram.bin",continue_bank_dir,name);f=fopen(path,"wb");
    if(!f || fwrite(g_ram,1,0x20000,f)!=0x20000)exit(108);fclose(f);
}
static void ContinueBankPoint(CpuState *cpu,uint32_t pc) {
    if(!continue_bank || !continue_bank_program)return;
    if(!continue_bank_apply && !continue_transition_mode && !continue_bank_dir)return;
    unsigned field=(unsigned)snes_frame_counter+1;
    tlk_bridge_apu_flush(cpu);
    if((pc==0xc082bb || pc==0xc082fa) && !TlkNativeBankReady(continue_bank,continue_bank_program)) {
        unsigned captured=TlkNativeBankCapture(continue_bank,continue_bank_program,g_snes->apu,g_ram,
            0x20000,pc,field);
        if(continue_bank_log) {fprintf(continue_bank_log,"capture,%u,%u,%u,%u\n",field,final_scene_entry,pc,captured);fflush(continue_bank_log);}
        if(captured && continue_bank_dir) {
            ContinueBankDump("captured");size_t n=TlkNativeBankRecordSize(continue_bank);
            uint8_t *bytes=malloc(n);if(!bytes || !TlkNativeBankSave(continue_bank,continue_bank_program,bytes,n))exit(108);
            char path[1024];snprintf(path,sizeof path,"%s/bank.record",continue_bank_dir);
            FILE *f=fopen(path,"wb");if(!f || fwrite(bytes,1,n,f)!=n)exit(108);fclose(f);free(bytes);
        }
    }
    if(pc!=0xc082a5 || !final_scene_entry)return;
    ContinueBankDump("before");
    if(!continue_bank_apply)return;
    if(cpu->D || cpu->DB || cpu->m_flag || cpu->x_flag || cpu->S!=0x2fc)exit(108);
    uint64_t clock=g_snes->apu->portClock;unsigned cycles=g_snes->apu->cycles;
    unsigned ok=TlkNativeBankApplyContinue(continue_bank,continue_bank_program,g_snes->apu,g_ram,
        0x20000,pc,0xc00387);
    if(continue_bank_log) {fprintf(continue_bank_log,"apply,%u,%u,%u,%u\n",field,final_scene_entry,pc,ok);fflush(continue_bank_log);}
    if(!ok)return; /* Cold/unsupported cache retains original native loader. */
    if(clock!=g_snes->apu->portClock || cycles!=g_snes->apu->cycles)exit(108);
    ContinueBankDump("applied");
    cpu->A=0;cpu->X=0;cpu->Y=16;
    interp_bridge_pre_opcode_redirect(0xc082b9);
}


#include "tlk_continue_scene.h"
static unsigned ContinueMenuComponent(const TlkContinueView *view,unsigned component) {
    if(!final_menu_art_mode)return TlkContinueSceneNativeComponent(view,component);
    static const unsigned levels[]={0,4,8,12,17,21,25,29};
    for(unsigned i=0;i<8;i++)if(component==levels[i]) {
        unsigned c=TlkContinueSceneMdComponent(view,i);return c*4+(c>>2);
    }
    exit(114);
}
extern int ContinueTransitionFullCanvas(uint32_t *out,int width,int hud);
extern int ContinueTransitionOriginCanvas(uint32_t *out,int width,int hud);
static TlkContinueScene continue_transition;
static unsigned continue_transition_level_ready;
static unsigned continue_title_pending;
static uint32_t continue_title_ready_field,continue_title_previous_pad;
static TlkTitleNavigation title_navigation;
/* Current external pad packet, republished before every fresh/resumed field.
 * The SNES backend neutralizes opposing directions before its hardware read. */
static uint16_t title_navigation_opposing_directions;
static int title_navigation_source_known,title_navigation_last_source;
static uint32_t continue_transition_menu[256*224],continue_transition_level[256*224];
/* Native menu artwork stays centred. Extra columns belong to each captured
 * canvas independently; they are not inferred from another platform's planes. */
enum { FINAL_SIDE_PIXELS=64*224, FINAL_SIDE_BYTES=4*FINAL_SIDE_PIXELS*4 };
static uint32_t continue_canvas_sides[4][FINAL_SIDE_PIXELS];
static void ContinueSplitCanvas(const uint32_t *full,int width,uint32_t *centre,uint32_t *sides) {
    unsigned extra=(width-256)/2;
    for(unsigned y=0;y<224;y++) {
        memcpy(centre+y*256,full+y*width+extra,256*sizeof *centre);
        if(extra) {
            memcpy(sides+y*64,full+y*width,32*sizeof *sides);
            memcpy(sides+y*64+32,full+y*width+288,32*sizeof *sides);
        }
    }
}
static FILE *continue_transition_log;
static unsigned continue_control_waiting;
static uint16_t continue_control_a,continue_control_x,continue_control_y,continue_control_s,continue_control_d;
static uint8_t continue_control_db,continue_control_p;
static void ContinueTitleExit(CpuState *cpu,uint32_t pc) {
    NativeMenuEvent(NATIVE_MENU_TITLE_EXIT);
    (void)cpu;(void)pc;
    if(!continue_transition_mode || !final_scene_entry || !final_scene_have_target ||
       FinalAddress(0xdf)!=0xc0057b || continue_transition.confirmed_field || reload_fast_used)return;
    continue_title_pending=1;
    {
        unsigned now=(unsigned)snes_frame_counter+1;
        if(cpu->D || cpu->DB!=0x7e || cpu->m_flag || !cpu->x_flag || cpu->S!=0x2ef)exit(113);
        continue_title_fade_field=now-((now-final_scene_entry)>=TLK_CONTINUE_MENU_TIMEOUT);
        if(continue_title_fade_field>0xffffffffu-191)exit(117);
        continue_title_ready_field=continue_title_fade_field+191;
        continue_title_previous_pad=FinalWord(0x5c);
        /* Native waits40 before fading. The selected MD menu leaves now;
         * keep the real cleanup/fade/reset services and caller frame. */
        interp_bridge_pre_opcode_redirect(0xc08e33);
    }
}
static void PublisherStartup(CpuState *);
static void ContinueTitleSelect(CpuState *cpu,uint32_t pc) {
    (void)pc;
    PublisherStartup(cpu);
    if(!continue_title_pending || !continue_transition_mode)return;
    /* Complete the original startup actor constructor, then enter its real
     * title phase3. Level15 is a separate interlude, not the title screen. */
    if(FinalWord(0x1ff9e)!=14 || FinalAddress(0xdf)!=0xc0057b)return;
    unsigned actor=FinalWord(0x68);
    if(cpu->DB!=0x7e || cpu->m_flag || cpu->x_flag || !cpu->D ||
       actor<0x2000 || actor>0xffc0 || FinalWord(cpu->D)!=actor ||
       FinalWord(actor+0x30)!=0x62f6 || g_ram[actor+0x32]!=0xc4)exit(112);
    ReloadFastWord(actor+0x2e,3);continue_title_pending=0;
    interp_bridge_pre_opcode_redirect(0xc463fc);
}
/* Installed startup/title payloads are scoped to an unconfirmed final exit.
 * Ordinary power-on, new-game loading and Continue YES retain their own owners.
 * No used-mask is needed: the original source/destination request is the cursor,
 * and its real caller still performs all DMA, palette and audio services. */
static void ContinueTitlePayload(CpuState *cpu,uint32_t pc) {
    (void)pc;
    if(!continue_transition_mode || !final_scene_entry || continue_transition.confirmed_field ||
       reload_fast_used || (!continue_title_pending && FinalAddress(0xdf)!=0xc005ab))return;
    for(unsigned i=TLK_FINAL_NATIVE_TITLE_FIRST;i<TLK_FINAL_NATIVE_COUNT;i++) {
        const TlkFinalNativeRecipe *r=TlkFinalNativeRecipeAt(i);
        if(FinalAddress(13)!=r->source || FinalAddress(10)!=r->destination)continue;
        if(cpu->D || g_snes->dma->dmaBusy || g_snes->dma->dmaTimer)exit(106);
        for(unsigned n=0;n<8;n++)if(g_snes->dma->channel[n].dmaActive)exit(106);
        size_t size=0;const uint8_t *payload=TlkFinalNativePayload(final_native_assets,i,&size);
        if(!payload || size!=r->size)exit(106);
        memcpy(g_ram+(r->destination&0x1ffff),payload,size);
        ReloadFastWord(10,r->destination_end);g_ram[12]=r->destination_end>>16;
        ReloadFastWord(13,r->source_end);g_ram[15]=r->source_end>>16;
        g_snes->ramAdr=r->destination_end&0x1ffff;
        if(continue_exit_log) {
            fprintf(continue_exit_log,"title_fast,%u,%06x,%u,%u,%u,%u\n",
                (unsigned)snes_frame_counter+1-final_scene_entry,r->source,
                FinalWord(0x2004),FinalWord(0x1ffaa),i,(unsigned)size);fflush(continue_exit_log);
        }
        interp_bridge_pre_opcode_redirect(0xc1cd85);return;
    }
}
#include "pride_final_title_bank.inc"
static void ContinueTransitionConfirm(CpuState *cpu,uint32_t pc) {
    NativeMenuEvent(NATIVE_MENU_CONFIRM);
    (void)cpu;(void)pc;
    if(!continue_transition_mode || !final_scene_entry || FinalAddress(0xdf)!=0xc0057b)return;
    if(!TlkNativeBankReady(continue_bank,continue_bank_program)) {
        if(final_menu_art_mode) {
            fprintf(stderr,"Development MD Continue requires its prepared native bank; no fallback is available\n");exit(114);
        }
        return;
    }
    if(TlkContinueSceneBegin(&continue_transition,0xc00387,(unsigned)snes_frame_counter+1)) {
        continue_menu_field=0;
        if(final_menu_art_mode) {
            final_menu_confirmed_credits=FinalWord(0x1ffa8);
            if(!final_menu_confirmed_credits || final_menu_confirmed_credits>9) {
                fprintf(stderr,"Invalid confirmed menu credits %u at age %u\n",final_menu_confirmed_credits,
                    (unsigned)snes_frame_counter+1-final_scene_entry);exit(114);
            }
        }
    }
}
static unsigned continue_transition_input_started;
static void TitleOpeningControl(CpuState *,uint32_t);
#include "pride_final_title_ready.inc"
static void ReadyTitleArtObserve(CpuState *);
#include "pride_final_title_navigation.inc"
static void ContinueTransitionInputBegin(CpuState *cpu,uint32_t pc) {
    ContinueTitleReadyInput(cpu,pc);
    (void)cpu;(void)pc;
    if(!continue_transition_mode || continue_transition_input_started || !continue_transition.confirmed_field)return;
    TlkContinueView v;
    if(!TlkContinueSceneView(&continue_transition,(unsigned)snes_frame_counter+1,&v) ||
       !v.controls_ready || FinalAddress(0xdf)!=0xc00387)return;
    /* Original MD begins gameplay with a fresh button history: a jump held
     * through the fade is accepted. Let the real native service read hardware
     * and produce this first edge; preserve the live suppression/mapping mask. */
    g_ram[0x5c]=g_ram[0x5d]=0;continue_transition_input_started=1;
}
static void ContinueTransitionControl(CpuState *cpu,uint32_t pc) {
    (void)cpu;(void)pc;
    if(!continue_transition_mode || !continue_transition.confirmed_field)return;
    TlkContinueView v;
    if(!TlkContinueSceneView(&continue_transition,(unsigned)snes_frame_counter+1,&v) || v.controls_ready)return;
    /* Real pad service/suppression latches continue to run. The owned player
     * update receives neutral controls while native spawn/physics/drawing
     * finish, until the original MD gameplay-input boundary. */
    if(FinalAddress(0xdf)!=0xc00387)return;
    g_ram[0x5a]=g_ram[0x5b]=0; /* Keep raw held state for the real edge filter. */
}
void FinalSceneCaptureNative(const uint8_t *pixels) {
    ContinueTitleNavigationCapture();
    /* Title rendering takes over before its later level/menu-ready flag.
     * Release the outgoing black canvas at that real renderer handoff. */
    if(continue_transition_mode && continue_title_fade_field && !continue_title_pending &&
       FinalAddress(0xdf)==0xc005ab) {
        continue_menu_field=continue_title_fade_field=0;
        /* The outgoing slot is now absent. Canonicalize both its centre and
         * wide margins before a save at this renderer handoff can observe it. */
        memset(continue_transition_menu,0,sizeof continue_transition_menu);
        memset(continue_canvas_sides[2],0,sizeof continue_canvas_sides[2]);
    }
    /* Native title construction has completed this unconfirmed NO/timeout
     * episode. Retire it before a later Start can borrow Continue reloads.
     * Also reconciles older private title saves on their first real frame. */
    if(continue_transition_mode && final_scene_entry && !continue_title_pending && !continue_title_ready_field &&
       !continue_transition.confirmed_field && !reload_fast_used &&
       !FinalWord(0x1ff9e) && FinalAddress(0xdf)==0xc005ab)ContinueLocalClear();
    ContinueTransitionPreviousCapture(pixels);
    if(final_menu_art_mode && final_scene_entry && final_scene_age==90 && final_scene_have_target)
        ContinueMenuCapture(pixels,final_scene_target,continue_canvas_sides[1]);
    /* Capture the selected picture before serialization and UI overlays. The
     * raw PPU picture omits independently selected art/palettes. Keep the
     * native picture if this scoped compositor cannot supply a complete one. */
    /* Arena display state has one final queued scroll update after the hit.
     * Keep the hit picture at age0, then freeze the completed selected age1
     * picture. Age/descriptor come from serialized state, including cold0→1. */
    int width=WideWidth();
    static uint32_t selected[320*224];
    if(final_scene_mode && final_scene_entry && final_scene_have_origin && (width==256 || width==320) &&
       (!final_scene_age || (final_scene_age==1 && FinalAddress(0xdf)==0xc0080d)) &&
       ContinueTransitionOriginCanvas(selected,width,s_wide_hud))
        ContinueSplitCanvas(selected,width,final_scene_origin,continue_canvas_sides[0]);
    if(!continue_transition_mode)return;
    if(final_scene_entry && final_scene_have_target && !continue_transition.confirmed_field && !reload_fast_used &&
       !FinalWord(0x1ff9e) && FinalAddress(0xdf)==0xc0057b && final_scene_age>=124) {
        unsigned now=(unsigned)snes_frame_counter;
        if(!continue_title_fade_field || now==continue_title_fade_field || !continue_menu_field) {
            ContinueMenuCapture(pixels,continue_transition_menu,continue_canvas_sides[2]);continue_menu_field=now;
        }
    }
    TlkContinueView v;
    if(!TlkContinueSceneView(&continue_transition,(unsigned)snes_frame_counter,&v))return;
    if(v.phase==TLK_CONTINUE_MENU) {
        if(final_menu_art_mode)ContinueMenuConfirmedCapture(continue_transition_menu,continue_canvas_sides[2]);
        else {
        memcpy(continue_transition_menu,pixels,sizeof continue_transition_menu);
        /* Verified native256 Continue layout only. UI remains during the exit;
         * Rafiki occupies the separate lower-left animation region. */
        for(unsigned y=0;y<224;y++)for(unsigned x=0;x<256;x++)
            if(y<96 || (x>=144 && y>=160))
                continue_transition_menu[y*256+x]=final_scene_target[y*256+x];
        }
    }
    if(FinalWord(0x2004) && FinalAddress(0xdf)==0xc00387 &&
       ContinueTransitionFullCanvas(selected,width,s_wide_hud)) {
        ContinueSplitCanvas(selected,width,continue_transition_level,continue_canvas_sides[3]);
        continue_transition_level_ready=1;
    }
    if(continue_transition_log) {
        fprintf(continue_transition_log,"%u,%u,%u,%u,%u,%u,%u,%u,%u\n",(unsigned)snes_frame_counter,
            (unsigned)((unsigned)snes_frame_counter-continue_transition.confirmed_field),v.phase,v.step,
            v.controls_ready,continue_transition_level_ready,FinalWord(0x2004),FinalWord(0xb21b),FinalWord(0xb21d));
        fflush(continue_transition_log);
    }
}
static void ContinuePaintPlane(uint32_t *pixels,unsigned count,const uint32_t *origin,
    const uint32_t *target,const uint32_t *menu,const uint32_t *level) {
    FinalScenePaintInitialPlane(pixels,count,origin,target);
    if(!continue_transition_mode)return;
    if(continue_title_fade_field && continue_menu_field) {
        uint32_t now=(uint32_t)snes_frame_counter;
        unsigned age=now>=continue_title_fade_field?now-continue_title_fade_field:0;
        TlkContinueView fade={.phase=TLK_CONTINUE_FADE_OUT,.step=age>=19?7:(age+2)/3};
        for(unsigned i=0;i<count;i++) {
            unsigned rgb=0;
            for(unsigned shift=0;shift<24;shift+=8) {
                unsigned c=ContinueMenuComponent(&fade,(menu[i]>>shift&255)>>3);
                rgb|=((c<<3)|(c>>2))<<shift;
            }
            pixels[i]=(menu[i]&0xff000000u)|rgb;
        }
        return;
    }
    TlkContinueView v;
    if(!TlkContinueSceneView(&continue_transition,(unsigned)snes_frame_counter,&v) || v.controls_ready)return;
    if(v.phase==TLK_CONTINUE_BLACK ||
       ((v.phase==TLK_CONTINUE_FADE_IN || v.phase==TLK_CONTINUE_LEVEL) && !continue_transition_level_ready)) {
        memset(pixels,0,count*sizeof *pixels);return;
    }
    const uint32_t *source=(v.phase==TLK_CONTINUE_MENU || v.phase==TLK_CONTINUE_FADE_OUT)?
        menu:level;
    for(unsigned i=0;i<count;i++) {
        unsigned rgb=0;
        for(unsigned shift=0;shift<24;shift+=8) {
            unsigned c=(v.phase==TLK_CONTINUE_MENU || v.phase==TLK_CONTINUE_FADE_OUT)?
                ContinueMenuComponent(&v,(source[i]>>shift&255)>>3):
                TlkContinueSceneNativeComponent(&v,(source[i]>>shift&255)>>3);
            rgb|=((c<<3)|(c>>2))<<shift;
        }
        pixels[i]=(source[i]&0xff000000)|rgb;
    }
}
void FinalScenePaintNative(uint32_t *pixels) {
    ContinuePaintPlane(pixels,256*224,final_scene_origin,final_scene_target,
        continue_transition_menu,continue_transition_level);
    ContinueMenuPaint(pixels,256);
    NativeMenuPaint(pixels,256);
    InterlevelPaint(pixels,256);
    BonusResultPaint(pixels,256);
    EndingSunrisePaint(pixels,256);
    ReadyTitleArtPaint(pixels,256);
    OptionsMenuPaint(pixels,256);
}
void FinalScenePaintWide(uint32_t *pixels,int width) {
    if(width!=320){InterlevelPaint(pixels,width);BonusResultPaint(pixels,width);EndingSunrisePaint(pixels,width);ReadyTitleArtPaint(pixels,width);OptionsMenuPaint(pixels,width);return;}
    static uint32_t sides[FINAL_SIDE_PIXELS];
    for(unsigned y=0;y<224;y++) {
        memcpy(sides+y*64,pixels+y*320,32*sizeof *sides);
        memcpy(sides+y*64+32,pixels+y*320+288,32*sizeof *sides);
    }
    ContinuePaintPlane(sides,FINAL_SIDE_PIXELS,continue_canvas_sides[0],continue_canvas_sides[1],
        continue_canvas_sides[2],continue_canvas_sides[3]);
    for(unsigned y=0;y<224;y++) {
        memcpy(pixels+y*320,sides+y*64,32*sizeof *sides);
        memcpy(pixels+y*320+288,sides+y*64+32,32*sizeof *sides);
    }
    ContinueMenuPaint(pixels,width);
    NativeMenuPaint(pixels,width);
    InterlevelPaint(pixels,width);
    BonusResultPaint(pixels,width);
    EndingSunrisePaint(pixels,width);
    ReadyTitleArtPaint(pixels,width);
    OptionsMenuPaint(pixels,width);
}

static void ContinueLifecycleEntry(CpuState *,uint32_t);
static void ContinueEnsureInstalled(void) {

    if(!continue_exit_installed) {
        OptionsMenuInstall();
        if(!interp_bridge_add_pre_opcode_hook(0xc089b9,ContinueLifecycleEntry))exit(110);
        if(!interp_bridge_add_pre_opcode_hook(0xc08e2d,ContinueTitleExit) ||
           !interp_bridge_add_pre_opcode_hook(0xc4636b,ContinueTitleSelect) ||
           !interp_bridge_add_pre_opcode_hook(0xc463fc,ContinueTitleReadySetup) ||
           !interp_bridge_add_pre_opcode_hook(0xc4677b,ContinueTitleNavigationInput))exit(112);
        const char *transition=ContinueModeSetting("TLK_CONTINUE_TRANSITION");continue_transition_mode=transition && !strcmp(transition,"1");
        const char *transition_log=getenv("TLK_CONTINUE_TRANSITION_LOG");if(transition_log) {
            continue_transition_log=fopen(transition_log,"w");if(!continue_transition_log)exit(109);
            fputs("field,age,phase,step,control,level_ready,health,x,y\n",continue_transition_log);
        }
        if(!interp_bridge_add_pre_opcode_hook(0xc08d9f,ContinueTransitionConfirm) ||
           !interp_bridge_add_pre_opcode_hook(0xc0a0ee,ContinueTransitionControl) ||
           !interp_bridge_add_pre_opcode_hook(0xc0a073,ContinueTransitionInputBegin))exit(109);

        const char *bank_mode=ContinueModeSetting("TLK_CONTINUE_BANK_APPLY");
        continue_bank_apply=bank_mode && !strcmp(bank_mode,"1");
        continue_bank_dir=getenv("TLK_CONTINUE_BANK_DIR");
        if(continue_bank_dir) {
            char path[1024];snprintf(path,sizeof path,"%s/bank.csv",continue_bank_dir);
            continue_bank_log=fopen(path,"w");if(!continue_bank_log)exit(108);
            fputs("event,field,entry,pc,ok\n",continue_bank_log);
        }
        /* Cache ownership is independent of diagnostic output. A normal boot
         * captures its own bank in memory; saves carry it without a sidecar. */
        {
            continue_bank_program=TlkNativeBankProgramCreate(g_rom,0x300000,build_digest);
            continue_bank=TlkNativeBankCreate();if(!continue_bank_program || !continue_bank)exit(108);
            const char *record=getenv("TLK_CONTINUE_BANK_RECORD");if(record) {
                FILE *f=fopen(record,"rb");if(!f)exit(108);fseek(f,0,SEEK_END);long n=ftell(f);rewind(f);
                if(n<1 || n>262144)exit(108);uint8_t *bytes=malloc(n);
                if(!bytes || fread(bytes,1,n,f)!=(size_t)n)exit(108);fclose(f);
                if(!TlkNativeBankLoad(continue_bank,continue_bank_program,bytes,n))exit(108);free(bytes);
            }
            if(!interp_bridge_add_pre_opcode_hook(0xc082a5,ContinueBankPoint) ||
               !interp_bridge_add_pre_opcode_hook(0xc082bb,ContinueBankPoint) ||
               !interp_bridge_add_pre_opcode_hook(0xc082fa,ContinueBankPoint))exit(108);
        }

        const char *mode=ContinueModeSetting("TLK_CONTINUE_FAST_RELOAD");reload_fast_mode=mode && !strcmp(mode,"1");
        if(!interp_bridge_add_pre_opcode_hook(0xc1ccfe,ReloadFastPoint) ||
           !interp_bridge_add_pre_opcode_hook(0xc1ccfe,ContinueTitlePayload))exit(106);
        if(!interp_bridge_add_pre_opcode_hook(0xc22036,ContinueTitleUpload))exit(115);

        const char *path=getenv("TLK_CONTINUE_EXIT_LOG");
        if(path) {
            continue_exit_log=fopen(path,"w");if(!continue_exit_log)exit(104);
            fputs("kind,age,pc_or_descriptor,health,lives,a_or_lit,stack_or_peak\n",continue_exit_log);
            static const uint32_t points[]={0xc08d88,0xc08d9f,0xc08da5,0xc08da9,0xc08dad,0xc08dc8};
            for(unsigned i=0;i<sizeof points/sizeof *points;i++)
                if(!interp_bridge_add_pre_opcode_hook(points[i],ContinueExitPoint))exit(104);
        }
        continue_exit_installed=1;
    }
    if(!final_scene_installed) {
        const char *mode=ContinueModeSetting("TLK_FINAL_SCENE_PRESENT");final_scene_mode=mode && !strcmp(mode,"1");
        const char *path=getenv("TLK_FINAL_INPUT_LOG");if(path) {
            final_input_trace=fopen(path,"w");if(!final_input_trace)exit(103);
            fputs("kind,field,age,stack,db,p,pad5a,pad5c,pad5e,choice,timer,credits\n",final_input_trace);
        }
        if(!interp_bridge_add_pre_opcode_hook(0xc089b9,FinalSceneBegin) ||
           !interp_bridge_add_pre_opcode_hook(0xc08cce,FinalInputHold) ||
           !interp_bridge_add_pre_opcode_hook(0xc08cd6,FinalInputDecision))exit(103);
        final_scene_installed=1;
    }
    /* Hook registration and immutable payload preparation happen once. Choices
     * are live configuration and must be refreshed after every source commit. */
    const char *names[]={"TLK_FINAL_SKIP","TLK_FINAL_LATE_SKIP","TLK_FINAL_FAST_ASSETS",
        "TLK_FINAL_SCENE_PRESENT","TLK_CONTINUE_FAST_RELOAD","TLK_CONTINUE_BANK_APPLY","TLK_CONTINUE_TRANSITION"};
    unsigned *modes[]={&final_mode,&final_fast_late_mode,&final_fast_mode,&final_scene_mode,
        &reload_fast_mode,&continue_bank_apply,&continue_transition_mode};
    for(unsigned i=0;i<7;i++) {const char *v=ContinueModeSetting(names[i]);*modes[i]=v && !strcmp(v,"1");}
    final_menu_art_mode=ContinueMenuSource();
}
static int ContinueResourcesApplied(void) {
    int selected=ContinueTitleNavigationSelected();
    int changed=title_navigation_source_known && selected!=title_navigation_last_source;
    title_navigation_source_known=1;title_navigation_last_source=selected;
    int art_changed=final_menu_art_mode!=ContinueMenuSource();
    final_menu_source_changed|=art_changed;
    int active=final_scene_entry!=0 || title_navigation.owner!=0 || changed || art_changed || NativeMenuOwned() || TlkInterlevelSceneActive() || TlkCliffSceneActive() || TlkBonusResultSceneActive();
    if(TlkInterlevelSceneActive() && FinalAddress(0xdf)==0xc005ab && FinalWord(0x1ff9e)==1){
        /* Applying resources restarts the outgoing level, preserving the
         * ordinary bonus award path rather than skipping into the next level. */
        g_ram[0x1ff9e]=g_ram[0x1ff9f]=0;
    }
    if(TlkCliffSceneActive() && FinalAddress(0xdf)==0xc0041d){
        /* An explicit resource Apply restarts the outgoing Stampede. */
        g_ram[0x1ff9e]=3;g_ram[0x1ff9f]=0;
    }
    TlkTitleNavigationClear(&title_navigation);
    if(active)ContinueLocalClear();
    ContinueEnsureInstalled();
    return active;
}
_Bool __wrap_RtlRunFrame(uint32 inputs) {
    ContinueEnsureInstalled();
    InterlevelEnsureInstalled();
    BonusResultEnsureInstalled();
    TlkCantWaitGameplayInstall();
    if(!title_navigation_source_known) {
        title_navigation_source_known=1;title_navigation_last_source=ContinueTitleNavigationSelected();
    }
    title_navigation_opposing_directions=(inputs&0x30)==0x30?0x0c00:0;
    /* Original arena foreground submissions finish once after the fatal hit;
     * the MD backdrop's preceding-camera phase is already frozen. Derive this
     * one-field hold from the serialized clock, including cold age0 loads. */
    if(final_scene_mode && final_scene_entry && (WideWidth()==256 || WideWidth()==320) &&
       (unsigned)snes_frame_counter+1-final_scene_entry==1 && FinalAddress(0xdf)==0xc0080d)
        TlkWideHoldBackgroundPhase();
    _Bool result=FinalSceneRunNative(inputs);
    NativeMenuEvent(NATIVE_MENU_FRAME);
    return result;
}
#include "pride_final_save.inc"

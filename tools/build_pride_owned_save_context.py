"""Move the reviewed idle-save predicate into an owned engine header."""
from pathlib import Path

builder = Path(__file__).with_name('build_pride_boss_save.py')
source = builder.read_text().replace("parent=ROOT/'build/pride-rng-player3'", "parent=ROOT/'build/pride-rng-player5'")
source = source.replace("out=ROOT/'build/pride-rng-player4'", "out=ROOT/'build/pride-rng-player7'")
source = source.replace("predicate=ROOT/'engine/runner/tlk_pride_play_scene.inc'", "predicate=ROOT/'engine/runner/tlk_pride_save_context.h'")
start = source.index("    anchor='static int practice_context_ready(void) {'")
end = source.index("    source=out/'host.i'", start)
source = source[:start] + '''    old_predicate=ROOT/'engine/runner/tlk_pride_save_scene.inc'
    assert text.count(old_predicate.read_text())==1
    owned=subprocess.check_output(['C:/mingw32/bin/gcc.exe','-E','-P','-x','c',str(predicate)],text=True)
    text=text.replace(old_predicate.read_text(),owned)
    start=text.index('static int practice_context_ready(void) {')
    end=text.index('static int practice_publish(',start)
    old=text[start:end]
    assert 'PrideCompleteContextScene(ow(0x1ff9e),ol(0xdf))' in old
    text=text[:start]+"""static int practice_context_ready(void) {
    const TlkPrideSaveContext context={
        .owner_installed=!!owner_installed, .restore_installed=!!restore_installed,
        .have_return=!!have_return, .owner_started=!!owner_scene.started,
        .preparation_pending=!!preparation_pending, .owner_waiting=!!owner_waiting,
        .grounded_waiting=!!grounded_waiting, .scene_active=!!scene_active, .active=!!active,
        .level=ow(0x1ff9e), .descriptor=ol(0xdf), .cub_age=ow(0x2000),
        .health=ow(0x2004), .word_1ff90=ow(0x1ff90), .phase=ow(8)
    };
    return TlkPrideIdleSaveEligible(&context);
}
"""+text[end:]
''' + source[end:]
source = source.replace('paths=[Path(__file__),bp,original,source,predicate,',
                        'paths=[Path(__file__),builder,bp,original,source,predicate,old_predicate,')
source = source.replace('Candidate4 boss-save eligibility built;', 'Candidate7 owned save eligibility built;')
exec(compile(source, str(builder), 'exec'))

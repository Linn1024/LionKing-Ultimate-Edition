"""Current title saves restore physical effect ownership, PCM and remaining inputs."""
from pathlib import Path
original=Path(__file__).with_name('verify_pride_menu_audio80_resume.py')
source=original.read_text().replace("ROOT/'build/pride-menu-audio80'","ROOT/'build/pride-menu-output83'")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original,')
exec(compile(source,str(original),'exec'))

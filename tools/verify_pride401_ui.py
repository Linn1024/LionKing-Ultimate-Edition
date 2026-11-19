"""Interactive399 check without the CLI's automatic menu screenshot exit."""
from pathlib import Path
template=Path(__file__).with_name('verify_pride399_ui.py')
source=template.read_text().replace('build/pride399-ui','build/pride401-ui')
source=source.replace('trace=JsonPipe(', "i=cmd.index('--dump-window');del cmd[i:i+2]\ntrace=JsonPipe(")
source=source.replace('paths=[Path(__file__),reference,build]','paths=[Path(__file__),template,reference,build]')
exec(compile(source,str(template),'exec'))

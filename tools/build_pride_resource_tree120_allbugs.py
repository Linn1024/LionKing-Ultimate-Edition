"""Current118 observer using its inherited103 host object's actual identity."""
from pathlib import Path
verifier_source=Path(__file__).with_name('build_pride_checkpoint52_allbugs.py')
source=verifier_source.read_text().replace('pride-checkpoint-animation52','pride-resource-tree118')
source=source.replace('unchanged == 321 and len(all_inputs) == 322','unchanged == 322 and len(all_inputs) == 323')
anchor="(cwd/p).resolve() == base/'host.obj'";assert source.count(anchor)==1
source=source.replace(anchor,"(cwd/p).resolve() == Path(previous['compiles']['host'][previous['compiles']['host'].index('-o')+1])")
source=source.replace('paths = [Path(__file__),','paths = [Path(__file__),verifier_source,')
exec(compile(source,str(verifier_source),'exec'))

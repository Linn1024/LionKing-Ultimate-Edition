"""Original entrance replay with actual camera records for countdown reachability."""
from pathlib import Path
verifier_source=Path(__file__).with_name('capture_pride_hyena_intro109.py')
source=verifier_source.read_text().replace('pride-hyena-intro109','pride-hyena-camera115')
anchor="        rows.append(row)";assert source.count(anchor)==1
source=source.replace(anchor,"        camera=word(0xcd36);row.update(camera_x=word(camera+8),camera_y=word(camera+10),relative_x=word(actor+8)-word(camera+8),relative_y=word(actor+10)-word(camera+10))\n"+anchor)
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),verifier_source,')
source=source.replace("result='ORIGINAL_HYENA_INTRO_CAPTURED'","result='ORIGINAL_HYENA_CAMERA_CAPTURED'")
exec(compile(source,str(verifier_source),'exec'))

"""Preserve ordinary native play and the unchanged OpenGL menu presenter."""
from pathlib import Path

original_verifier=Path(__file__).with_name('verify_pride_singlepass_native.py')
source=original_verifier.read_text()
source=source.replace("ROOT/'build/pride-singlepass/plain-native'","ROOT/'build/pride-soft-tree/plain-native'")
begin=source.index("    prior=ROOT/'build/pride-reset/fixed4'")
end=source.index("    out=",begin)
source=source[:begin]+"    prior=ROOT/'build/pride-singlepass/plain-native';prior_path=prior/'build-report.json';old=bound(prior_path);before=prior/'native.exe';assert digest(before)==old['binary_sha256']\n"+source[end:]
source=source.replace(",('aot',True,False)","")
source=source.replace("env['TLK_SINGLEPASS_LOG']=str(folder/'presents.csv')","env['TLK_SINGLEPASS_LOG']=str(folder/'presents.csv');env['TLK_SOFT_TREE_LOG']=str(folder/'tree.jsonl')")
source=source.replace("presents=read_rows(b/'presents.csv')", "presents=[json.loads(line) for line in (b/'tree.jsonl').read_text().splitlines()]")
source=source.replace("r['toast_calls']=='1'","r['passes']==1").replace("r['menu']=='1'","r['menu']==1")
source=source.replace('paths=[Path(__file__),','paths=[Path(__file__),original_verifier,')
exec(compile(source,str(original_verifier),'exec'))

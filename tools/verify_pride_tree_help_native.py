"""Compare ordinary native rendering with the preceding fallback-tree frontend."""
from pathlib import Path

first_verifier=Path(__file__).with_name('verify_pride_soft_tree_native.py')
source=first_verifier.read_text().replace("ROOT/'build/pride-soft-tree/plain-native'","ROOT/'build/pride-tree-help2/plain-native'")
source=source.replace("prior=ROOT/'build/pride-singlepass/plain-native'","prior=ROOT/'build/pride-soft-tree/plain-native'")
source=source.replace('paths=[Path(__file__),original_verifier,','paths=[Path(__file__),first_verifier,original_verifier,')
exec(compile(source,str(first_verifier),'exec'))

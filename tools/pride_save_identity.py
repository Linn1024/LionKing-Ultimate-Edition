"""Conservative compatibility identity for pointer-free private save envelopes.

The host executable, window UI and observers are excluded. Every other linked
object/library remains bound, so a backend/library update requires review even
when its bytes might be compatible. Paths are provenance, not identity inputs.
"""
import hashlib
import json


DOMAIN=b'TLK.PRIDE.SAVE-COMPATIBILITY\0'


def contract_identity(contract):
    return hashlib.sha256(DOMAIN+json.dumps(contract,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')).hexdigest()


def make_contract(link_inputs,host_key,private_sources,backend_sha,epoch=1):
    assert host_key in link_inputs and len(link_inputs)>200
    assert private_sources and all(name.startswith('tools/') for name in private_sources)
    return dict(format='TLK-Pride-Save-Compatibility',schema=1,compatibility_epoch=epoch,
                abi=dict(pointer_bits=32,byte_order='little',outer_native=4,rollback_residue=8,
                         private_owned=1,private_ordinary=1,private_boot=1,preparation_cache=1,native_bank=1),
                linked_components_sha256=sorted(sha for name,sha in link_inputs.items() if name!=host_key),
                private_context_sources_sha256=dict(sorted(private_sources.items())),md_backend_sha256=backend_sha)

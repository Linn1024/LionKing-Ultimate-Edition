"""Bind ordered link components as well as their bytes and context schemas."""
from pride_save_identity import contract_identity
from pride_save_identity import make_contract as unordered_contract


def make_contract(link_inputs,host_key,private_sources,backend_sha,epoch=1):
    value=unordered_contract(link_inputs,host_key,private_sources,backend_sha,epoch)
    value['schema']=2
    # Link order can affect symbol resolution. Paths remain provenance-only.
    value['linked_components_sha256']=[sha for name,sha in link_inputs.items() if name!=host_key]
    return value

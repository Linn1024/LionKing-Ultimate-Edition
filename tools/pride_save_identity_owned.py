"""Extend the ordered contract's source closure to owned runner modules."""
from pride_save_identity2 import contract_identity
from pride_save_identity2 import make_contract as research_contract


def make_contract(link_inputs,host_key,private_sources,backend_sha,epoch=1):
    assert private_sources and all(name.startswith(('tools/','engine/runner/')) for name in private_sources)
    research={name:sha for name,sha in private_sources.items() if name.startswith('tools/')}
    value=research_contract(link_inputs,host_key,research,backend_sha,epoch)
    value['private_context_sources_sha256']=dict(sorted(private_sources.items()))
    return value

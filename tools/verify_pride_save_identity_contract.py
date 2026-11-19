"""Verify compatibility boundaries, including link order and path independence."""
import copy
import json
from pathlib import Path

from audit_scenes import ROOT
from build_pride_compiled_hooks import digest
from summarize_pride_practice import bound
from pride_save_identity2 import make_contract,contract_identity


def main():
    base=ROOT/'build/pride-save-identity2';build_path=base/'build-report.json';build=bound(build_path)
    prior_path=ROOT/'build/pride-legacy-save/player/build-report.json';prior=bound(prior_path)
    closure_path=ROOT/'build/pride-tree-help2/build-report.json';closure=bound(closure_path)
    links=prior['runs']['mixed']['link_inputs_sha256'];host='build/pride-legacy-save/player/host.obj'
    private={name:sha for name,sha in closure['source_sha256'].items() if name.startswith('tools/') and name.endswith(('.c','.h')) and 'present_probe' not in name}
    backend=digest(base/'genesis_plus_gx_libretro.dll');expected=build['runs']['a']['save_compatibility_sha256']
    identity=lambda values=links,key=host,sources=private,md=backend,epoch=1:contract_identity(make_contract(values,key,sources,md,epoch))
    checks={'actual_inputs_reproduce_identity':identity()==expected,
            'visibly_different_executables_share_identity':build['runs']['a']['binary_sha256']!=build['runs']['b']['binary_sha256'] and expected==build['runs']['b']['save_compatibility_sha256'],
            'incompatible_epoch_rotates_identity':identity(epoch=2)==build['runs']['incompatible']['save_compatibility_sha256']!=expected}
    relink={('moved/'+name if name!=host else 'moved/host.obj'):sha for name,sha in links.items()}
    checks['component_path_changes_preserve_identity']=identity(values=relink,key='moved/host.obj')==expected
    newhost=dict(links);newhost[host]='0'*64;checks['frontend_object_change_preserves_identity']=identity(values=newhost)==expected
    changed=dict(links);key=next(k for k in links if k!=host);changed[key]='0'*64
    checks['component_bytes_change_rotates_identity']=identity(values=changed)!=expected
    checks['link_order_change_rotates_identity']=identity(values=dict(reversed(list(links.items()))))!=expected
    extra=dict(links);extra['new-component.obj']='1'*64;checks['unknown_component_rotates_identity']=identity(values=extra)!=expected
    changed=copy.deepcopy(private);changed[next(iter(changed))]='0'*64;checks['private_context_change_rotates_identity']=identity(sources=changed)!=expected
    checks['md_backend_change_rotates_identity']=identity(md='0'*64)!=expected
    a=(base/'a.i').read_text();b=(base/'b.i').read_text();checks['editor_title_is_only_code_difference']=a.replace('VERSION RESOURCES','RESOURCE SOURCES')==b
    checks['no_runtime_self_executable_fingerprint']='sha256_compute(bytes,(size_t)size,build_digest)' not in a
    paths=[Path(__file__),build_path,prior_path,closure_path,ROOT/'tools/pride_save_identity.py',ROOT/'tools/pride_save_identity2.py']
    report=dict(result='PASS' if all(checks.values()) else 'INCOMPLETE',checks=checks,
                source_sha256={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},save_compatibility_sha256=expected,public_player_enabled=False)
    (base/'contract-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['result'],checks,flush=True)
    if not all(checks.values()):raise SystemExit(1)


if __name__=='__main__':main()

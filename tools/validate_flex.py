#!/usr/bin/env python3
"""Validate a Miva flex component folder. Usage: python3 validate_flex.py <component-dir> [--managed]"""
import json, os, re, sys
KNOWN = {'text','textarea','texteditor','checkbox','radio','select','selector','color','date','datetime','slider',
 'distributedslider','image','imagetype','link','fragment','product','category','customlookup','productcustomfieldlookup',
 'categorycustomfieldlookup','merchandisingshowcase','merchandisingprompt','group','list','font','typography','button',
 'padding','lengthunit','cornerradius','borderthickness','dropshadow','breakpoint','breakpointgroup','page'}
GLOBAL_RES = {'mm-theme-styles', 'mmx-customizations'}
err, warn = [], []
def main(d, managed_ok):
    fj = os.path.join(d, 'flex.json')
    if not os.path.isfile(fj): return err.append('flex.json missing at component root')
    try: f = json.load(open(fj))
    except Exception as e: return err.append(f'flex.json is not valid JSON: {e}')
    for k in ('code', 'name', 'type', 'version'):
        if not f.get(k): err.append(f'flex.json missing "{k}"')
    code = f.get('code', '')
    if code and not re.fullmatch(r'[a-z][a-z0-9-]+', code): err.append(f'code "{code}" must be lowercase letters, digits, hyphens')
    if f.get('resourcegroup_code') != code: warn.append('resourcegroup_code usually equals code')
    if f.get('managed', True) and not managed_ok: err.append('custom components need "managed": false')
    deps = f.get('depends') or {}
    if not isinstance(deps, dict): err.append('depends must be an object {"code": ">=version"}'); deps = {}
    for p in ('initialization_template', 'instance_template', 'upgrade_template', 'preview', 'detailed_preview'):
        if f.get(p) and not os.path.isfile(os.path.join(d, f[p])): err.append(f'{p} file not found: {f[p]}')
    own = {}
    for kind in ('scripts', 'styles'):
        for r in f.get(kind, []):
            if not os.path.isfile(os.path.join(d, r.get('filepath', ''))): err.append(f'{kind} file not found: {r.get("filepath")}')
            own[('js' if kind == 'scripts' else 'css') + ':' + r.get('resource_code', '')] = r
            names = {a.get('name'): a.get('value') for a in r.get('attributes', [])}
            if 'integrity' in names and not managed_ok: err.append(f'remove "integrity" attribute from {r.get("filepath")}')
            if names.get('data-mmx-resource-type') == 'adoptable' and code != 'mmx-base' and not re.search(r'26\.0[2-9]|2[7-9]\.|[3-9]\d\.', str(deps.get('mmx-base', ''))):
                err.append(f'{r.get("filepath")} is adoptable: depends.mmx-base must be >=26.02.00')
    for im in f.get('images', []):
        if not os.path.isfile(os.path.join(d, im.get('source_filepath', ''))): err.append(f'images source not found: {im.get("source_filepath")}')
    init = read(d, f.get('initialization_template'))
    used = set(re.findall(r'param="((?:css|js):[\w-]+)"', init))
    for key in own:
        if key not in used and f.get('type') != 'library': err.append(f'init.mvt never outputs own resource "{key}"')
    for key in used - set(own):
        rc = key.split(':', 1)[1]
        if rc not in GLOBAL_RES and rc not in deps: warn.append(f'init.mvt loads "{key}" but "{rc}" is not in depends')
    walk(f.get('properties'), 'properties'); walk(f.get('advanced_properties') or [], 'advanced_properties')
    js = ''.join(read(d, r['filepath']) for r in f.get('scripts', []))
    inst = read(d, f.get('instance_template'))
    defined = set(re.findall(r"customElements\.define\(\s*['\"]([\w-]+)", js))
    if re.search(r'extends MMX_\w+', js):
        if 'mmx-base' not in deps: err.append('JS extends MMX_* but depends has no mmx-base')
        if 'makeShadow()' in js and 'makeComponent()' not in js: warn.append('use this.makeComponent() (26.02+) instead of makeShadow()')
        rcs = ''.join(re.findall(r'styleResourceCodes\s*=\s*\[([^\]]*)\]', js))
        for key in own:
            if key.startswith('css:') and rcs and key[4:] not in rcs: warn.append(f'styleResourceCodes lacks "{key[4:]}"; its CSS will not reach the shadow DOM')
    for tag in defined:
        if f"customElements.get('{tag}')" not in js and f'customElements.get("{tag}")' not in js: warn.append(f'guard define of <{tag}> with if (!customElements.get(...))')
        if tag.startswith('mmx-') and not code.startswith('mmx-'): err.append(f'custom component redefines Miva tag <{tag}>; rename the tag and class')
    tags = set(re.findall(r'<([a-z]\w*-[\w-]+)[\s>]', inst)) - {'mmx-text', 'mmx-button', 'mmx-icon'}
    if defined and tags and not tags & defined: warn.append(f'instance.mvt tags {sorted(tags)} not defined by this JS {sorted(defined)}')
def walk(props, path):
    seen = set()
    for p in props or []:
        c, t, here = p.get('code'), p.get('type'), f"{path}>{p.get('code')}"
        if not c or not t: err.append(f'{here}: property needs code and type'); continue
        if c in seen: warn.append(f'{here}: duplicate code among siblings')
        seen.add(c)
        if t not in KNOWN: warn.append(f'{here}: unknown type "{t}" (check MCP/schema)')
        if t in ('select', 'radio', 'selector') and not p.get('options'): err.append(f'{here}: {t} needs options')
        if t == 'list':
            if not p.get('list_type'): err.append(f'{here}: list needs list_type')
            ipp = p.get('item_prompt_property')
            if ipp and ':' not in ipp: err.append(f'{here}: item_prompt_property needs a member suffix, e.g. "{ipp}:value"')
        for tf in (p.get('textsettings') or {}).get('fields', []):
            if not tf.get('pseudoclasses'): warn.append(f'{here}: textsettings field {tf.get("code")} has no pseudoclasses')
        walk(p.get('properties'), here)
def read(d, rel):
    try: return open(os.path.join(d, rel)).read() if rel else ''
    except OSError: return ''
if __name__ == '__main__':
    main(sys.argv[1], '--managed' in sys.argv)
    for m in err: print('ERROR  ', m)
    for m in warn: print('WARN   ', m)
    print('PASS' if not err else f'FAIL ({len(err)} errors)'); sys.exit(1 if err else 0)

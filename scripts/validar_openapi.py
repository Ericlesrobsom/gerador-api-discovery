import yaml
d = yaml.safe_load(open('openapi.yaml', encoding='utf-8'))
refs = []

def walk(o):
    if isinstance(o, dict):
        if '$ref' in o:
            refs.append(o['$ref'])
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)

walk(d)
bad = []
for r in refs:
    if not r.startswith('#/'):
        bad.append(r)
        continue
    cur = d
    for p in r[2:].split('/'):
        if not isinstance(cur, dict) or p not in cur:
            bad.append(r)
            break
        cur = cur[p]
print('paths', len(d['paths']), 'refs', len(refs), 'invalid', len(bad))
for b in bad[:10]:
    print('bad', b)
for path, ops in d['paths'].items():
    for method, op in ops.items():
        if method in ('get', 'post', 'put', 'delete', 'patch') and 'responses' not in op:
            print('sem responses', method, path)

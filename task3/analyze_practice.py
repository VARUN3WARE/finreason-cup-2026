import json, sys, collections
sys.path.insert(0, 'task3')
from xbrl import *

rows = [json.loads(l) for l in open('toolkit/finreason_task3/data/public_dev.jsonl')]


def period_ok(c, t):
    if t.end:
        return c.start == t.start and c.end == t.end
    return c.instant == t.start


report = collections.Counter()
by_rule = collections.defaultdict(collections.Counter)
examples = collections.defaultdict(list)
for r in rows:
    q = r['query']; rule = r['dqc_id']; s = sections(q); t = target(q)
    inst = s.get('Instance document', ''); ctxs = contexts(inst); fs = facts(inst)
    gx, gc = num(r['answer']['extracted_value']), num(r['answer']['calculated_value'])
    tf = [f for f in fs if f.concept == t.concept and f.context in ctxs and period_ok(ctxs[f.context], t)]
    nodim = [f for f in tf if not ctxs[f.context].dims]
    ex = None
    for f in nodim or tf:
        v = num(f.raw)
        if f.sign_attr == '-' and v is not None: v = -v
        ex = v; break
    cat = []
    cat.append('ex_found' if ex is not None else 'ex_missing')
    cat.append('ex_match' if ex is not None and ex == gx else ('gold_ex_zero' if gx == 0 else 'ex_mismatch'))
    # calculated candidates
    arcs = calc_arcs(s.get('Calculation linkbase document', ''))
    kids = [(c, w, role) for (p, c, w, role) in arcs if p == t.concept]
    parents = [(p, w, role) for (p, c, w, role) in arcs if c == t.concept]
    cands = {}
    if gx is not None: cands['neg'] = -gx
    ctx_ids = {f.context for f in nodim} or {f.context for f in tf}
    def val(concept):
        for f in fs:
            if f.concept == concept and f.context in ctx_ids:
                v = num(f.raw)
                if v is not None:
                    return -v if f.sign_attr == '-' else v
        return None
    roles = collections.defaultdict(list)
    for c, w, role in kids: roles[role].append((c, w))
    for role, ks in roles.items():
        vals = [(val(c), w) for c, w in ks]
        if any(v is not None for v, _ in vals):
            cands[f'sum_children'] = sum((v or 0) * w for v, w in vals)
            if all(v is not None for v, _ in vals): cands['sum_children_complete'] = cands['sum_children']
    hit = [k for k, v in cands.items() if v is not None and gc is not None and v == gc]
    cat.append('kids' if kids else 'nokids'); cat.append('parents' if parents else 'noparents')
    key = (rule, tuple(cat), tuple(sorted(hit)) or ('nohit',))
    report[key] += 1
    if len(examples[key]) < 2: examples[key].append(r['id'])
for k, v in sorted(report.items()):
    print(v, k, examples[k])

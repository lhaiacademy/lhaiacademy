#!/usr/bin/env python3
"""Count lines of code vs tests in an exported repository tree (git archive of main).

Method (repeatable):
- Only files with a programming-language extension are counted (CODE_EXT).
  Not counted: .json, .md, .yml/.yaml, .svg, .txt, images, media, lockfiles.
- Excluded paths: any path segment in EXCL_SEG (node_modules, vendor, dist, build, .next,
  .open-next, coverage, generated); minified files (*.min.js, *.min.css); next-env.d.ts;
  the two built single-page studio apps that are copied into apps/web/public by a build step
  (BUILT_FILES); and documentation folders (DOC_TOP: docs/, reports/, research_notes/), whose
  mock pages are counted separately as "docs_mock".
- A file is a TEST when its name contains .test. or .spec. (incl. .vitest.test.), or a path
  segment is one of TEST_SEG (test, tests, __tests__, e2e, e2e-local, harness).
- "lines" = physical lines; "nonblank" = lines with any non-space character.
"""
import os, re, sys, json, collections

CODE_EXT = {'ts','tsx','js','jsx','mjs','cjs','mts','cts','css','scss','html','sql','prisma',
            'py','kt','kts','java','sh','ps1','go','rs'}
EXCL_SEG = {'node_modules','vendor','dist','build','.next','.open-next','coverage','generated'}
TEST_SEG = {'test','tests','__tests__','e2e','e2e-local','harness'}
DOC_TOP = {'docs','reports','research_notes'}
BUILT_FILES = {'apps/web/public/bank-studio/index.html','apps/web/public/rmg-studio/index.html'}

def classify(rel):
    parts = rel.split('/')
    name = parts[-1]
    ext = name.rsplit('.',1)[-1].lower() if '.' in name else ''
    if ext not in CODE_EXT: return None
    if any(p in EXCL_SEG for p in parts[:-1]): return None
    if name.endswith('.min.js') or name.endswith('.min.css') or name == 'next-env.d.ts': return None
    if rel in BUILT_FILES: return None
    if parts[0] in DOC_TOP: return 'docs_mock'
    if re.search(r'\.(test|spec)\.', name) or any(p in TEST_SEG for p in parts[:-1]): return 'test'
    return 'code'

def area(rel, repo):
    p = rel.split('/')
    if repo == 'lhai-tech':
        if p[0] == 'apps' and len(p) > 2: return 'apps/' + p[1]
        if p[0] in ('packages','tools','services','tooling','.github'): return p[0]
        return '(root)'
    return '(all)'

def main(root, repo):
    tot = collections.defaultdict(lambda: [0,0,0])   # kind -> files, lines, nonblank
    by_area = collections.defaultdict(lambda: [0,0])  # (area,kind) -> lines, nonblank
    by_ext = collections.defaultdict(lambda: [0,0])
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('node_modules','.git')]
        for f in fn:
            full = os.path.join(dp, f); rel = os.path.relpath(full, root).replace(os.sep,'/')
            k = classify(rel)
            if not k: continue
            try: txt = open(full, encoding='utf-8', errors='replace').read()
            except Exception: continue
            lines = txt.count('\n') + (0 if txt.endswith('\n') or not txt else 1)
            nb = sum(1 for l in txt.splitlines() if l.strip())
            t = tot[k]; t[0]+=1; t[1]+=lines; t[2]+=nb
            a = by_area[(area(rel,repo),k)]; a[0]+=lines; a[1]+=nb
            if k != 'docs_mock':
                e = by_ext[(rel.rsplit('.',1)[-1].lower(),k)]; e[0]+=lines; e[1]+=nb
    out = {'repo':repo,
           'totals':{k:{'files':v[0],'lines':v[1],'nonblank':v[2]} for k,v in tot.items()},
           'by_area':{f'{a}|{k}':{'lines':v[0],'nonblank':v[1]} for (a,k),v in sorted(by_area.items())},
           'by_ext':{f'{e}|{k}':{'lines':v[0],'nonblank':v[1]} for (e,k),v in sorted(by_ext.items(), key=lambda x:-x[1][0])}}
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

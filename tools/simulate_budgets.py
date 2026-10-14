# Estimates how many guesses a consistent solver needs per grid shape.
# Budgets in index.html (TPL[*].b) were set near the 90th percentile of this.
# Usage: python3 simulate_budgets.py ../words.js   (takes ~1 min)
import random, re, statistics, sys
_s = open(sys.argv[1] if len(sys.argv) > 1 else '../words.js').read()
A = re.search(r'CROSSLE_ANS="([^"]*)"', _s).group(1).split()
T = {
 'H': [('d',0,0),('d',0,4),('a',2,0)],
 'frame': [('a',0,0),('a',4,0),('d',0,0),('d',0,4)],
 'comb': [('a',0,0),('d',0,0),('d',0,2),('d',0,4)],
 'E': [('d',0,0),('a',0,0),('a',2,0),('a',4,0)],
 'waffle': [('a',0,0),('a',2,0),('a',4,0),('d',0,0),('d',0,2),('d',0,4)],
 'frame5': [('a',0,0),('a',2,0),('a',4,0),('d',0,0),('d',0,4)],
}
def cells(s):
    o, r, c = s; return [(r+i, c) if o == 'd' else (r, c+i) for i in range(5)]
def fill(t, rng):
    slots = [cells(s) for s in t]; grid = {}; words = [None]*len(slots)
    def ok(w, cs): return all(grid.get(c, w[k]) == w[k] for k, c in enumerate(cs))
    def bt(k, tries=[0]):
        if k == len(slots): return True
        tries[0] += 1
        if tries[0] > 20000: return False
        cs = slots[k]; cand = [w for w in A if ok(w, cs) and w not in words]
        rng.shuffle(cand)
        for w in cand[:40]:
            saved = {c: grid.get(c) for c in cs}
            for i, c in enumerate(cs): grid[c] = w[i]
            words[k] = w
            if bt(k+1): return True
            words[k] = None
            for c, v in saved.items():
                if v is None: grid.pop(c, None)
                else: grid[c] = v
        return False
    return (words, slots) if bt(0) else None
def score(g, a):
    r = ['b']*5; cnt = {}
    for i in range(5):
        if g[i] == a[i]: r[i] = 'g'
        else: cnt[a[i]] = cnt.get(a[i], 0) + 1
    for i in range(5):
        if r[i] != 'g' and cnt.get(g[i], 0) > 0: r[i] = 'y'; cnt[g[i]] -= 1
    return ''.join(r)
def play(words, slots, rng):
    known = {}; hist = [[] for _ in slots]; solved = [False]*len(slots); n = 0
    while not all(solved):
        def cands(k):
            cs = slots[k]
            return [w for w in A if all(known.get(c, w[i]) == w[i] for i, c in enumerate(cs)) and all(score(g, w) == f for g, f in hist[k])]
        _, k = min((len(cands(k)), k) for k in range(len(slots)) if not solved[k])
        g = rng.choice(cands(k)); n += 1
        f = score(g, words[k]); hist[k].append((g, f))
        for i, cc in enumerate(slots[k]):
            if f[i] == 'g': known[cc] = g[i]
        for j in range(len(slots)):
            if all(cc in known for cc in slots[j]): solved[j] = True
    return n
rng = random.Random(1)
for name, t in T.items():
    fails = 0; res = []
    for _ in range(40):
        p = fill(t, rng)
        if not p: fails += 1; continue
        res.append(play(*p, rng))
    res.sort()
    print(name, 'fillfail', fails, 'median', statistics.median(res), 'p90', res[int(.9*len(res))-1] if res else None, 'max', max(res) if res else None)

"""Rebuild words.js for Crossle.

Source: SCOWL word lists via the npm package `wordlist-english`
  (npm pack wordlist-english && tar xzf wordlist-english-*.tgz  ->  ./package/)
Answers = 5-letter words from SCOWL sizes 10+20+35 (english + american),
          minus simple inflections (plurals, -ed, -ing, -ies) and the blocklists.
Guesses = 5-letter words from sizes 10..55, minus BLOCK_ALL.
Words in DEMOTE are allowed as guesses but never chosen as answers.

Usage: python3 build_words.py path/to/package > ../words.js
Changing the answer list changes every daily and endless grid (grids are
seeded from the code, then drawn from this list in order).
"""
import json, re, sys
P = sys.argv[1].rstrip('/') + '/'
def load(n):
    s = set()
    for v in ['english', 'american']:
        s |= set(json.load(open(f'{P}{v}-words-{n}.json')))
    return s
five = lambda s: {w for w in s if re.fullmatch('[a-z]{5}', w)}
common = five(load(10) | load(20) | load(35))
valid = set()
for n in [10, 20, 35, 40, 50, 55]: valid |= five(load(n))
allw = set()
for n in [10, 20, 35, 40, 50, 55, 60]: allw |= load(n)
def inflected(w):
    if w.endswith('s') and not w.endswith('ss') and (w[:-1] in allw or (w.endswith('es') and w[:-2] in allw)): return True
    if w.endswith('ed') and (w[:-2] in allw or w[:-1] in allw or w[:-3] in allw): return True
    if w.endswith('ing') or (w.endswith('ies') and w[:-3] + 'y' in allw): return True
    return False
# Slurs and vulgarities: never answers, never accepted as guesses.
BLOCK_ALL = set("""kikes spics negro squaw gooks coons dykes nigga chink honky dagos micks pommy fagot
twats cunts fucks shits sluts whore bitch pussy dicks penis semen anals boner horny porno milfs wanks
titty clits vulva dildo arsed rapes raped pervs gypos pikey skank spade boobs cocks effed fanny farts
fecal frigs gypsy hymen labia nooky ponce poncy pubes pubic pubis turds kinky""".split())
# Fine to type, unpleasant as a daily answer.
DEMOTE = set("sperm feces enema urine vomit lynch queer".split())
ans = sorted(w for w in common if not inflected(w) and w not in BLOCK_ALL | DEMOTE)
val = sorted((valid | DEMOTE) - BLOCK_ALL - set(ans))
print('window.CROSSLE_ANS="' + ' '.join(ans) + '";')
print('window.CROSSLE_VAL="' + ' '.join(val) + '";')
print(f'// {len(ans)} answers, {len(val)} extra guesses', file=sys.stderr)

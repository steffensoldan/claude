import pandas as pd, re, numpy as np

df = pd.read_excel('safaitic_narrative_2.xlsx', sheet_name='All Narrative').copy()
df = df.drop_duplicates(subset=['Translation']).reset_index(drop=True)

t = df['Translation'].astype(str)
low = t.str.lower()

# --- core text: strip leading genealogy chain "By X son of Y son of ..."
def core(s):
    s2 = re.sub(r'^\s*by\s+', '', s, flags=re.I)
    s2 = re.sub(r'^[^,.]*?(son of [^,.]+?)+\s+(and|here|was|is|at|in)\b', r'\2', s2, flags=re.I)
    return s2
df['core'] = t.apply(core)
df['core_words'] = df['core'].str.split().str.len()
df['son_chain'] = low.str.count(r'son of')

# --- lexicons
emo = ['wept','weep','wail','grief','griev','mourn','distraught','distress','longed','longing',
       'anxious','afraid','fear','mercy','merci','beloved','loved one','love','in need','despair',
       'yearn','missed','wept while','sorrow','tears']
scene = ['lion','wolf','snow','rain','flood','drought','horse','camel','dog','ewe','lamb','goat',
         'sheep','star','scorpio','rising','pasture','pond','well','cairn','captive','raid','struck',
         'blood','migrat','watering','sky','wind','spring of','pleiades']
meta = ['efface','blind','destroy','intact','read this writing','long life','whoever leaves','left intact']
anchor = ['year','king','herod','agrippa','nabat','roman','rebel','revolt']

def hits(series, lex):
    return series.apply(lambda s: sum(s.count(w) for w in lex))

df['emo']    = np.minimum(hits(low, emo), 4)
df['scene']  = np.minimum(hits(low, scene), 4)
df['meta']   = np.minimum(hits(low, meta), 2)
df['anchor'] = np.minimum(hits(low, anchor), 2)

# rarity: inverse single-theme frequency
prim = df['Theme'].astype(str).str.split(';').str[0].str.strip()
freq = prim.map(prim.value_counts())
df['rarity'] = (1 - (freq / freq.max())).round(2)
df['multi_theme'] = df['Theme'].astype(str).str.contains(';').astype(int)

# integrity / clarity
df['lacuna'] = t.str.count('----')
words = t.str.split().str.len().replace(0,1)
df['integrity'] = (1 - np.minimum(df['lacuna']/4, 1)).round(2)
df['uncert'] = (t.str.count(r'\{') + t.str.count(r'\[')) / words
df['clarity'] = (1 - np.minimum(df['uncert']*3, 1)).round(2)

# brevity sweet spot on CORE words (6-22 best), penalize formula(<5) & sprawl(>40)
def brev(w):
    if w < 5: return 0.2
    if w <= 22: return 1.0
    if w <= 40: return 0.6
    return 0.3
df['brevity'] = df['core_words'].apply(brev)
df['geneal_pen'] = np.minimum(df['son_chain']*0.05, 0.4)

# --- LITERARY composite (weights tuned for: spürbar, klanghaft, verknappt, leicht verankert)
df['LiteraryScore'] = (
    df['emo']*3.0 + df['scene']*2.5 + df['rarity']*3.0 + df['meta']*1.5 +
    df['anchor']*1.0 + df['brevity']*2.5 + df['integrity']*2.0 + df['clarity']*1.5
    - df['geneal_pen']*2.0
).round(2)

df = df.sort_values('LiteraryScore', ascending=False).reset_index(drop=True)
print('Nach Dedup:', len(df), 'Inschriften')
print('\nTOP 20:')
for i,r in df.head(20).iterrows():
    print(f"[{r['LiteraryScore']:.1f}] ({r['Theme'][:22]}) {r['Translation'][:130]}")
df.to_pickle('scored.pkl')

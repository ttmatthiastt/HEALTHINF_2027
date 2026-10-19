import json
from pathlib import Path
from statistics import pstdev
goldfile = Path("thesis_gold_standard_final.json")
outfolder = Path("outputs")
def statdict():
    return {"EM": 0, "WS": 0, "FA": 0, "CA": 0, "HS": 0, "N": 0}

def check(gold, pred):
    if pred is None and gold is None:
        return "CA"# correct abstention
    if pred is not None and gold is None:
        return "HS"# hallucinated score
    if pred is None and gold is not None:
        return "FA"# false abstention
    if pred == gold:
        return "EM"# exact match
    return "WS"# wrong score



def calc(d):
    em = d["EM"]
    ws = d["WS"]
    fa = d["FA"]
    ca = d["CA"]
    hs = d["HS"]
    n = d["N"]
    ans = em + ws + fa
    unans = ca + hs
    eia = (em + ca) / n if n else 0
    aia = em / ans if ans else 0
    car = ca / unans if unans else 0
    hr = hs / unans if unans else 0
    return {
        "eia": eia,
        "aia": aia,
        "car": car,
        "hr": hr,
        "em": em,
        "ws": ws,
        "fa": fa,
        "ca": ca,
        "hs": hs,
        "n": n,
    }


f = open(goldfile, "r", encoding="utf-8")
golddata = json.load(f)
goldbyid = {}
for t in golddata["transcripts"]:
    goldbyid[t["transcript_id"]] = t
byprompt = {}
bytr = {}
byinf = {True: statdict(), False: statdict()}
skip = 0

for file in sorted(outfolder.glob("*.json")):
    f = open(file, "r", encoding="utf-8")
    pred = json.load(f)
    trid = pred.get("transcript_id")
    prompt = pred.get("prompt_type", "unknown")
    gold = goldbyid.get(trid)
    if gold is None:
        skip += 1
        continue

    if prompt not in byprompt:
        byprompt[prompt] = statdict()

    if (prompt, trid) not in bytr:
        bytr[(prompt, trid)] = statdict()
    for sec in ["barthel", "lawton"]:
        gsec = gold.get(sec, {})
        psec = pred.get(sec, {})
        for act in gsec:
            gscore = gsec[act].get("score")
            pscore = psec.get(act, {}).get("score")
            c = check(gscore, pscore)
            byprompt[prompt][c] += 1
            byprompt[prompt]["N"] += 1
            bytr[(prompt, trid)][c] += 1
            bytr[(prompt, trid)]["N"] += 1
            inf = bool(gsec[act].get("inferred", False))
            byinf[inf]["N"] += 1
            if c == "EM":
                byinf[inf]["EM"] += 1
            elif c == "WS":
                byinf[inf]["WS"] += 1
            elif c == "FA":
                byinf[inf]["FA"] += 1
            elif c == "CA":
                byinf[inf]["CA"] += 1
            elif c == "HS":
                byinf[inf]["HS"] += 1

metricsbyprompt = {}
for p in byprompt:
    metricsbyprompt[p] = calc(byprompt[p])

metricbytr = {}
for k in bytr:
    metricbytr[k] = calc(bytr[k])
sd = {}
for p in metricsbyprompt:
    vals = []
    for (pp, t) in metricbytr:
        if pp == p:
            vals.append(metricbytr[(pp, t)]["eia"])
    sd[p] = pstdev(vals) if len(vals) > 1 else 0

print("METRICS BY PROMPT")
for p in metricsbyprompt:
    m = metricsbyprompt[p]
    print(p, m["n"], round(m["eia"], 3), round(m["aia"], 3), round(m["car"], 3), round(m["hr"], 3))

print("METRICS BY TRANSCRIPT")

for (prompt, trid) in bytr:
    m = metricbytr[(prompt, trid)]
    print(
        prompt,
        trid,
        m["n"],
        round(m["eia"], 3),
        round(m["car"], 3),
        round(m["hr"], 3)
    )


print("SD PER PROMPT")
for p in sd:
    print(p, round(sd[p], 3))

print("INFERRED TAG")
for i in [True, False]:
    d = byinf[i]
    print(i, d["N"], d["EM"], d["WS"], d["FA"], d["CA"], d["HS"])
print("skipped", skip) #checking for any errors
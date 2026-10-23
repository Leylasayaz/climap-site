"""OSM ham verisinden Clim-Map sayfasına gömülecek kompakt veri üretir.
Gerçek (OSM): ilçe sınırları, okullar, pazar/çarşılar, inşaat alanları, Dicle, surlar, ana yollar, bina yoğunluğu.
Temsili (üretilmiş): yüzey sıcaklığı, risk puanı, sıcak noktalar, yaşlı yoğunluğu, Serin Durak noktaları."""
import json, math, random, sys, os

D = sys.argv[1]
OUT = sys.argv[2]
L = lambda f: json.load(open(os.path.join(D, f)))
random.seed(2027)

LAT0, LON0 = 37.92, 40.21
KX, KY = math.cos(math.radians(LAT0)) * 111320, 110540
def xy(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)
def ll(x, y): return (LAT0 + y / KY, LON0 + x / KX)

def rdp(pts, eps):
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    n = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        d = abs(dy * px - dx * py + bx * ay - by * ax) / n
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)
    return [a, b]

def rnd5(p): return [round(p[0], 5), round(p[1], 5)]

# ilçeler (lon,lat GeoJSON -> [lat,lon])
DN = [("Bağlar", "baglar"), ("Kayapınar", "kayapinar"), ("Sur", "sur"), ("Yenişehir", "yenisehir")]
districts = []
for name, f in DN:
    g = L(f + ".json")[0]["geojson"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = []
    for poly in polys:
        ring = [(c[1], c[0]) for c in poly[0]]
        h = len(ring) // 2
        simp = rdp(ring[:h + 1], 0.0006)[:-1] + rdp(ring[h:], 0.0006)
        rings.append([rnd5(p) for p in simp])
    districts.append({"n": name, "r": rings})

def pip(lat, lon, ring):
    ins = False; j = len(ring) - 1
    for i in range(len(ring)):
        yi, xi = ring[i]; yj, xj = ring[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-15) + xi): ins = not ins
        j = i
    return ins
def district_of(lat, lon):
    for i, d in enumerate(districts):
        if any(pip(lat, lon, r) for r in d["r"]): return i
    return -1

# Dicle ve surlar
lines = L("lines.json")["elements"]
dicle = []
for e in lines:
    t = e["tags"]
    if t.get("waterway") == "river" and "Dicle" in (t.get("name") or ""):
        dicle.append([rnd5(p) for p in rdp([(g["lat"], g["lon"]) for g in e["geometry"]], 0.00025)])
walls = []
for e in lines:
    t = e["tags"]
    if t.get("historic") == "citywalls" or t.get("barrier") == "city_wall":
        walls.append([rnd5(p) for p in rdp([(g["lat"], g["lon"]) for g in e["geometry"]], 0.00004)])
dicle_xy = [xy(*p) for line in dicle for p in line]
def dist_river(x, y): return min(math.hypot(x - a, y - b) for a, b in dicle_xy) if dicle_xy else 9e9

# yollar (yalnızca altlık yüklenemezse çizilir)
roads = []
for e in L("roads.json")["elements"]:
    if "geometry" not in e: continue
    pts = rdp([(g["lat"], g["lon"]) for g in e["geometry"]], 0.00018)
    if len(pts) >= 2: roads.append({"k": {"trunk": 0, "primary": 0, "secondary": 1, "tertiary": 2}[e["tags"]["highway"]], "p": [rnd5(p) for p in pts]})

# OSM noktaları
def center(e):
    if "center" in e: return e["center"]["lat"], e["center"]["lon"]
    return e["lat"], e["lon"]
schools = []
for e in L("schools.json")["elements"]:
    la, lo = center(e)
    schools.append([round(la, 5), round(lo, 5), e["tags"].get("name") or ""])
markets = []
for e in L("markets.json")["elements"]:
    la, lo = center(e)
    markets.append([round(la, 5), round(lo, 5), e["tags"].get("name") or ""])
sites = []
for e in L("construction.json")["elements"]:
    nm = e["tags"].get("name") or ""
    if "Yıkıl" in nm or "Deprem" in nm: continue  # enkaz alanları şantiye değildir
    la, lo = center(e)
    sites.append([round(la, 5), round(lo, 5), nm])

# altıgen hücreler: bina yoğunluğundan kentsel alan
R = 260.0
def hex_round(x, y):
    q = (math.sqrt(3) / 3 * x - y / 3) / R; r = (2 / 3 * y) / R
    s = -q - r; rq, rr_, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr_ - r), abs(rs - s)
    if dq > dr and dq > ds: rq = -rr_ - rs
    elif dr > ds: rr_ = -rq - rs
    return rq, rr_
def hex_center(q, r): return (R * math.sqrt(3) * (q + r / 2), R * 1.5 * r)
counts = {}
for e in L("buildings.json")["elements"]:
    c = e.get("center")
    if not c: continue
    k = hex_round(*xy(c["lat"], c["lon"]))
    counts[k] = counts.get(k, 0) + 1
vals = sorted(counts.values())
p90 = vals[int(len(vals) * 0.9)] if vals else 1

def noise(x, y, s):
    return (math.sin(x / s + 1.7) * math.cos(y / (s * 1.3) - 0.4) + math.sin((x + y) / (s * 0.7))) / 2
cells = []
for (q, r), n in counts.items():
    if n < 3: continue
    x, y = hex_center(q, r); la, lo = ll(x, y)
    di = district_of(la, lo)
    if di < 0: continue
    dens = min(1.0, n / p90)
    dr = dist_river(x, y) / 1000
    H = max(0.05, min(1, 0.45 + 0.4 * dens + 0.15 * noise(x, y, 900) - 0.35 * math.exp(-dr / 0.5)))
    E = max(0.05, min(1, 0.1 + 0.9 * dens))
    V = max(0.05, min(1, 0.5 + 0.25 * noise(x + 3000, y - 2000, 700) + (0.15 if districts[di]["n"] == "Sur" else 0) + (0.1 if districts[di]["n"] == "Bağlar" else 0) - (0.12 if districts[di]["n"] == "Kayapınar" else 0)))
    temp = 33 + 15 * H
    cells.append({"q": q, "r": r, "la": la, "lo": lo, "d": di, "H": H, "E": E, "V": V, "t": temp, "raw": (H * E * V) ** (1 / 3)})
order = sorted(range(len(cells)), key=lambda i: -cells[i]["raw"])
cuts = [0.08, 0.25, 0.5, 0.75]
for rank, i in enumerate(order):
    f = rank / len(order)
    cells[i]["s"] = 5 if f < cuts[0] else 4 if f < cuts[1] else 3 if f < cuts[2] else 2 if f < cuts[3] else 1

# sıcak noktalar (temsili)
TYPES = [
    ("okul", "Bağlar"), ("pazar", "Sur"), ("meydan", "Bağlar"), ("okul", "Yenişehir"), ("durak", "Kayapınar"),
    ("santiye", "Bağlar"), ("okul", "Kayapınar"), ("meydan", "Sur"), ("durak", "Yenişehir"), ("pazar", "Bağlar"),
]
chosen = []
for k_, (typ, dn) in enumerate(TYPES):
    di = [d["n"] for d in districts].index(dn)
    for i in order:
        c = cells[i]
        if c["d"] != di or c["s"] != (4 if k_ % 3 == 2 else 5): continue
        x, y = xy(c["la"], c["lo"])
        if any(math.hypot(x - a, y - b) < 900 for a, b, _ in chosen): continue
        chosen.append((x, y, i)); break
hot = []
for k, (x, y, i) in enumerate(chosen):
    ox, oy = random.uniform(-70, 70), random.uniform(-70, 70)
    la, lo = ll(x + ox, y + oy)
    hot.append({"la": round(la, 5), "lo": round(lo, 5), "type": TYPES[k][0], "d": TYPES[k][1], "s": cells[i]["s"], "t": round(cells[i]["t"], 1)})

# Serin Durak (temsili): pazar, durak ve şantiye sıcak noktalarının yakınında
durak = []
for h in hot:
    if h["type"] in ("pazar", "durak", "santiye"):
        x, y = xy(h["la"], h["lo"]); la, lo = ll(x + random.uniform(120, 220), y + random.uniform(-150, 150))
        durak.append([round(la, 5), round(lo, 5)])

# yaşlı nüfus yoğunluğu (temsili leke merkezleri)
el = sorted([c for c in cells if c["E"] > 0.45], key=lambda c: -(c["V"] + 0.3 * c["E"]))
elder = []
for c in el:
    x, y = xy(c["la"], c["lo"])
    if any(math.hypot(x - a, y - b) < 700 for a, b, *_ in [(xy(e[0], e[1])) for e in elder]): continue
    elder.append([round(c["la"], 5), round(c["lo"], 5), round(0.4 + 0.6 * c["V"], 2)])
    if len(elder) >= 14: break

data = {
    "districts": districts, "dicle": dicle, "walls": walls, "roads": roads,
    "schools": schools, "markets": markets, "sites": sites,
    "cells": [[c["q"], c["r"], c["d"], round(c["t"], 1), c["s"], round(c["E"], 2)] for c in cells],
    "hex": {"R": R, "lat0": LAT0, "lon0": LON0, "kx": KX, "ky": KY},
    "hot": hot, "durak": durak, "elder": elder,
}
s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
open(OUT, "w").write(s)
print("bytes", len(s), "cells", len(cells), "hot", len(hot), "schools", len(schools), "markets", len(markets), "sites", len(sites),
      "roads", len(roads), "dicle", sum(map(len, dicle)), "walls", sum(map(len, walls)), "durak", len(durak), "elder", len(elder))
print([(h["type"], h["d"], h["s"]) for h in hot])

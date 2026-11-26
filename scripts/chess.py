"""Generate assets/chess-blue.svg: an animated replay of Morphy's Opera Game (1858). Run: python3 scripts/chess.py"""
from pathlib import Path

# (from, to, SAN); castling is a list of two piece moves
MOVES = [
    ("e2e4", "1. e4"), ("e7e5", "1... e5"), ("g1f3", "2. Nf3"), ("d7d6", "2... d6"),
    ("d2d4", "3. d4"), ("c8g4", "3... Bg4"), ("d4e5", "4. dxe5"), ("g4f3", "4... Bxf3"),
    ("d1f3", "5. Qxf3"), ("d6e5", "5... dxe5"), ("f1c4", "6. Bc4"), ("g8f6", "6... Nf6"),
    ("f3b3", "7. Qb3"), ("d8e7", "7... Qe7"), ("b1c3", "8. Nc3"), ("c7c6", "8... c6"),
    ("c1g5", "9. Bg5"), ("b7b5", "9... b5"), ("c3b5", "10. Nxb5"), ("c6b5", "10... cxb5"),
    ("c4b5", "11. Bxb5+"), ("b8d7", "11... Nbd7"), (("e1c1", "a1d1"), "12. O-O-O"), ("a8d8", "12... Rd8"),
    ("d1d7", "13. Rxd7"), ("d8d7", "13... Rxd7"), ("h1d1", "14. Rd1"), ("e7e6", "14... Qe6"),
    ("b5d7", "15. Bxd7+"), ("f6d7", "15... Nxd7"), ("b3b8", "16. Qb8+"), ("d7b8", "16... Nxb8"),
    ("d1d8", "17. Rd8#"),
]
BACK = "RNBQKBNR"
GLYPH = {"K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟︎"}
SQ, BX, BY = 46, 40, 38          # square size, board origin
PLY, MOVE, HOLD = 0.8, 0.35, 4.0  # seconds per ply, slide time, pause on mate
TOTAL = len(MOVES) * PLY + HOLD


def xy(sq):
    f, r = ord(sq[0]) - 97, int(sq[1])
    return BX + f * SQ + SQ / 2, BY + (8 - r) * SQ + SQ / 2


# piece id -> dict(kind, white, start, track=[(t0, t1, from, to)], dies=t)
pieces, at = {}, {}
for f in range(8):
    for white, r, kind in ((True, 1, BACK[f]), (True, 2, "P"), (False, 8, BACK[f]), (False, 7, "P")):
        sq = f"{chr(97 + f)}{r}"
        pid = len(pieces)
        pieces[pid] = dict(kind=kind, white=white, start=sq, track=[], dies=None)
        at[sq] = pid

for i, (mv, _) in enumerate(MOVES):
    t0 = i * PLY
    for m in (mv if isinstance(mv, tuple) else (mv,)):
        a, b = m[:2], m[2:]
        if b in at:
            pieces[at[b]]["dies"] = t0 + MOVE
        pid = at.pop(a)
        pieces[pid]["track"].append((t0, t0 + MOVE, a, b))
        at[b] = pid
assert pieces[at["d8"]]["kind"] == "R" and pieces[at["e8"]]["kind"] == "K", "game replay broke"


def anim(attr, keys):
    """keys: [(t, value)] in seconds -> SMIL animate looping over TOTAL."""
    kt = ";".join(f"{t / TOTAL:.4f}" for t, _ in keys)
    vals = ";".join(str(v) for _, v in keys)
    return f'<animate attributeName="{attr}" dur="{TOTAL}s" repeatCount="indefinite" keyTimes="{kt}" values="{vals}"/>'


out = []
for p in pieces.values():
    x0, y0 = xy(p["start"])
    kx, ky = [(0, x0)], [(0, y0)]
    for t0, t1, a, b in p["track"]:
        (ax, ay), (bx, by) = xy(a), xy(b)
        kx += [(t0, ax), (t1, bx)]
        ky += [(t0, ay), (t1, by)]
    kx.append((TOTAL, kx[-1][1]))
    ky.append((TOTAL, ky[-1][1]))
    kids = (anim("x", kx) + anim("y", ky)) if p["track"] else ""
    if p["dies"]:
        kids += anim("opacity", [(0, 1), (p["dies"] - 0.05, 1), (p["dies"], 0), (TOTAL, 0)])
    cls = "w" if p["white"] else "b"
    out.append(f'<text class="pc {cls}" x="{x0}" y="{y0}">{GLYPH[p["kind"]]}{kids}</text>')

captions = []
for i, (_, san) in enumerate(MOVES):
    t0, t1 = i * PLY, (i + 1) * PLY if i < len(MOVES) - 1 else TOTAL
    captions.append(f'<text class="san" x="470" y="200" opacity="0">{san}'
                    + anim("opacity", [(0, 0), (t0, 0), (t0, 1), (t1, 1), (t1, 0), (TOTAL, 0)]) + "</text>")

squares = "".join(
    f'<rect x="{BX + f * SQ}" y="{BY + r * SQ}" width="{SQ}" height="{SQ}" fill="{"#13213B" if (f + r) % 2 else "#1E3A5F"}"/>'
    for f in range(8) for r in range(8))
files = "".join(f'<text class="co" x="{BX + f * SQ + SQ / 2}" y="{BY + 8 * SQ + 16}">{chr(97 + f)}</text>' for f in range(8))
ranks = "".join(f'<text class="co" x="{BX - 12}" y="{BY + r * SQ + SQ / 2 + 4}">{8 - r}</text>' for r in range(8))
bar = f'<rect x="470" y="300" width="0" height="6" rx="3" fill="#22D3EE">{anim("width", [(0, 0), (len(MOVES) * PLY, 480), (TOTAL, 480)])}</rect>'

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="440" viewBox="0 0 1000 440" role="img" aria-label="Animated replay of Morphy's Opera Game, 1858, ending in 17. Rd8 checkmate">
  <style>
    .pc{{font:38px "Segoe UI Symbol","Apple Symbols","DejaVu Sans",serif;text-anchor:middle;dominant-baseline:central}}
    .w{{fill:#F0F9FF;stroke:#0A1020;stroke-width:1}} .b{{fill:#020617;stroke:#7DD3FC;stroke-width:1}}
    .co{{font:600 11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#7DD3FC;opacity:.7;text-anchor:middle}}
    .k{{font:600 12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;letter-spacing:4px;fill:#7DD3FC}}
    .h{{font:700 30px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#F0F9FF}}
    .s{{font:400 15px -apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#94A3B8}}
    .san{{font:800 56px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:url(#g)}}
  </style>
  <defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#38BDF8"/><stop offset="1" stop-color="#818CF8"/></linearGradient></defs>
  <rect width="1000" height="440" rx="18" fill="#05070D"/>
  {squares}{files}{ranks}
  {"".join(out)}
  <text class="k" x="470" y="70">PLAY THE NEXT MOVE</text>
  <text class="h" x="470" y="110">The Opera Game</text>
  <text class="s" x="470" y="136">Paul Morphy vs. the Duke and the Count · Paris, 1858</text>
  {"".join(captions)}
  <rect x="470" y="300" width="480" height="6" rx="3" fill="#0A1020"/>{bar}
  <text class="s" x="470" y="336">17 moves · two sacrifices · one mate</text>
</svg>
'''
Path(__file__).resolve().parent.parent.joinpath("assets/chess-blue.svg").write_text(svg)
print("wrote assets/chess-blue.svg", f"{TOTAL:.1f}s loop")

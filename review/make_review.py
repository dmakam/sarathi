import sys; sys.path.insert(0, "/root/gita-app/build")
import graph_data as G, content as C
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule

F = "Arial"
HEAD = PatternFill("solid", fgColor="0F5257")
YEL = PatternFill("solid", fgColor="FFF4C2")
thin = Side(style="thin", color="D5DEDD")
B = Border(bottom=thin)
STATE = {s[0]: s for s in G.STATES}
SIT = {s[0]: s[1] for s in C.SITUATIONS}
CON = {c[0]: (c[1], c[3]) for c in C.CONCEPTS}
TH = {}
for i, (tid, name, vs) in enumerate(C.THEMES, 1):
    for v in vs: TH.setdefault(v, []).append(f"{i}. {name}")
def themes(v): return "; ".join(TH.get(v, [])) or "(outside the 20 themes)"
def vkey(v): a, b = v.split("."); return (int(a), int(b))
REL = {"leads": "leads to", "answers": "answers", "echoes": "echoes",
       "parallel": "runs parallel to", "culminates": "culminates in"}

wb = Workbook()
sheets = []
def sheet(title, cols, widths, rows, prefix):
    ws = wb.create_sheet(title)
    ws.append(cols + ["Decision", "Your note"])
    for c in ws[1]:
        c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HEAD
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    for i, r in enumerate(rows, 1):
        ws.append([f"{prefix}{i:03d}"] + r + ["", ""])
    n = len(rows) + 1
    for row in ws.iter_rows(min_row=2, max_row=n):
        for c in row:
            c.font = Font(name=F, size=10); c.alignment = Alignment(vertical="top", wrap_text=True); c.border = B
        row[-2].fill = YEL; row[-1].fill = YEL
    for i, w in enumerate(widths + [12, 34]):
        ws.column_dimensions[chr(65 + i)].width = w
    dc = chr(65 + len(cols)); 
    dv = DataValidation(type="list", formula1='"Accept,Reject,Change"', allow_blank=True,
                        errorTitle="Pick a decision", error="Choose Accept, Reject or Change.")
    ws.add_data_validation(dv); dv.add(f"{dc}2:{dc}{n}")
    rng = f"{dc}2:{dc}{n}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Accept"'], fill=PatternFill("solid", fgColor="CFEAD6")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Reject"'], fill=PatternFill("solid", fgColor="F6D2CC")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"Change"'], fill=PatternFill("solid", fgColor="D9DEF3")))
    ws.freeze_panes = "C2"; ws.auto_filter.ref = f"A1:{chr(65+len(cols)+1)}{n}"
    sheets.append((title, dc, n))
    return ws

# 1 verse-verse
rows = [[a, themes(a), REL.get(t, t), b, themes(b), note] for a, t, b, note in sorted(G.LINKS, key=lambda x: vkey(x[0]))]
sheet("Verse to verse", ["ID", "From verse", "From theme", "Relation", "To verse", "To theme", "Reason"],
      [7, 9, 26, 15, 9, 26, 46], rows, "VV")
# 2 verse-feeling
rows = []
for v in sorted(G.TAGS, key=vkey):
    for s in G.TAGS[v]["s"]:
        st = STATE[s]; rows.append([v, themes(v), st[1], st[3], st[4]])
sheet("Verse to feeling", ["ID", "Verse", "Theme", "Feeling or state", "Kind", "What the state means"],
      [7, 9, 30, 20, 11, 40], rows, "VF")
# 3 verse-situation
rows = []
for v in sorted(G.TAGS, key=vkey):
    for h in G.TAGS[v]["h"]: rows.append([v, themes(v), SIT.get(h, h)])
sheet("Verse to situation", ["ID", "Verse", "Theme", "Situation (What you're facing)"], [7, 9, 34, 44], rows, "VS")
# 4 verse-idea
rows = []
for v in sorted(G.TAGS, key=vkey):
    for c in G.TAGS[v]["c"]:
        nm, gl = CON.get(c, (c, "")); rows.append([v, themes(v), nm, gl])
sheet("Verse to idea", ["ID", "Verse", "Theme", "Idea", "Meaning"], [7, 9, 34, 14, 34], rows, "VI")
# 5 antidotes
rows = [[STATE[a][1], "is answered by", STATE[h][1], v, themes(v), note] for h, a, v, note in G.ANTIDOTES]
sheet("Feeling antidotes", ["ID", "Afflictive feeling", "Relation", "Healing state", "Evidence verse", "Theme", "Reason"],
      [7, 18, 14, 18, 10, 26, 42], rows, "FA")
# 6 chains
rows = []
for cid, name, gloss, val, steps in G.CHAINS:
    for i, (step, v) in enumerate(steps, 1): rows.append([name, i, step, v, themes(v)])
sheet("Chains", ["ID", "Chain", "Step", "Stage", "Verse", "Theme"], [7, 24, 6, 26, 9, 30], rows, "CH")

# Start sheet
ws = wb.active; ws.title = "Start here"
ws.column_dimensions["A"].width = 26; ws.column_dimensions["B"].width = 12
for c in "CDEF": ws.column_dimensions[c].width = 12
ws["A1"] = "Sarathi knowledge graph: link review"; ws["A1"].font = Font(name=F, size=16, bold=True, color="0F5257")
lines = [
 "Every link below is a draft I proposed for the 116 core shlokas (the 20 Heartfulness themes).",
 "Fill only the yellow Decision and Your note columns on each tab.",
 "Decision: Accept = keep as is.  Reject = remove.  Change = keep but fix (say how in Your note).",
 "Blank rows count as not reviewed. Rejected and changed rows are applied on the next build.",
 "Example: VV001  2.47 leads to 2.48 ... Decision: Change ... Your note: 'say \"grows into\" instead'.",
 "Each tab has filters on the header row, so you can review one theme or one verse at a time.",
]
for i, t in enumerate(lines, 3):
    ws[f"A{i}"] = t; ws[f"A{i}"].font = Font(name=F, size=10)
r0 = 10
for j, h in enumerate(["Tab", "Links", "Accepted", "Rejected", "Changed", "Left"]):
    c = ws.cell(r0, 1 + j, h); c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HEAD
for k, (t, dc, n) in enumerate(sheets, r0 + 1):
    q = f"'{t}'!{dc}2:{dc}{n}"
    vals = [t, f"=ROWS({q})", f'=COUNTIF({q},"Accept")', f'=COUNTIF({q},"Reject")', f'=COUNTIF({q},"Change")', f"=B{k}-C{k}-D{k}-E{k}"]
    for j, v in enumerate(vals): ws.cell(k, 1 + j, v).font = Font(name=F, size=10)
tot = r0 + len(sheets) + 1
ws.cell(tot, 1, "Total").font = Font(name=F, bold=True)
for j in range(2, 7):
    col = chr(64 + j)
    ws.cell(tot, j, f"=SUM({col}{r0+1}:{col}{tot-1})").font = Font(name=F, bold=True)
ws.cell(tot + 2, 1, "Source of the theme lists: Heartfulness Gitopadesh Vidyarthi course, learning.heartfulness.org/courses/GPDVY-EN. Links are drafts by Claude for your review.").font = Font(name=F, size=9, italic=True)
out = "/root/gita-app/review/Sarathi-graph-review.xlsx"
wb.save(out); print(out, [(s[0], s[2]-1) for s in sheets])

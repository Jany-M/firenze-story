"""docs/REFINEMENTS.md: the open points of every landmark model in one list, gathered from the "Review list" / "Known limits"
section of each docs/landmarks/*.md (the pages stay the reference). Run after editing a review list (prepare.py runs it)."""
import re, glob, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
out = ["# Refinement list", "",
       "Everything still to refine on the landmark models, gathered from the review lists of each technical page (the pages",
       "stay the reference; this list is regenerated from them by `pipeline/53_refinements.py`). Statues and fountains have their",
       "own list: [STATUES.md](STATUES.md). Landmarks not modelled yet are in the plan (`_dev/notes/PROJECT-DRAFT.md` §12).", ""]
for f in sorted(glob.glob(os.path.join(ROOT, "docs", "landmarks", "*.md"))):
    s = open(f, encoding="utf-8").read(); k = os.path.basename(f)
    title = s.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"^## (?:Review list|Known limits[^\n]*)\n(.*?)(?=^## |^\*\*|\Z)", s, re.S | re.M)
    if not m: continue
    items, cur = [], None
    for line in m.group(1).splitlines():
        if line.startswith("- "):
            if cur: items.append(cur)
            cur = line[2:].strip()
        elif line.startswith("  ") and cur: cur += " " + line.strip()
    if cur: items.append(cur)
    if not items: continue
    out += [f"## {title}", f"Technical page: [{k}](landmarks/{k})", ""]
    out += ["- [ ] " + re.sub(r"\]\((?!http|/|landmarks/)([A-Z-]+\.md)", r"](landmarks/\1", i) for i in items] + [""]
open(os.path.join(ROOT, "docs", "REFINEMENTS.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("refinements:", sum(1 for l in out if l.startswith("- [ ]")), "items")

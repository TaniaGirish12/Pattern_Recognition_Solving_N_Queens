"""Programmatic check that report.md satisfies the IEEE template rules:
- Abstract exactly 180 words.
- Conclusion 240–260 words.
- Each non-bulleted paragraph contains 7–10 sentences.
- 10–15 references, with at least 80% from 2020 or later.
"""

import re
import sys


def word_count(text):
    # Strip markdown formatting symbols
    text = re.sub(r"[\*\_`#]", "", text)
    return len(re.findall(r"\b[\w'\-]+\b", text))


def sentence_count(text):
    text = re.sub(r"\s+", " ", text).strip()
    # Sentences end with . ! ? but be careful about decimals like 0.995.
    # Replace common decimal patterns first.
    text = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", text)
    # Abbreviations like "i.e.", "e.g." -- not relevant here but safe to keep.
    parts = re.split(r"(?<=[.!?])\s+", text)
    sentences = [p for p in parts if re.search(r"\w", p)]
    return len(sentences)


with open("report.md") as f:
    text = f.read()

# --- Abstract ---
abstract_match = re.search(r"## Abstract\s+(.*?)\n\*\*Index Terms", text, re.S)
abstract = abstract_match.group(1).strip()
ab_words = word_count(abstract)
print(f"Abstract: {ab_words} words")
if ab_words == 180:
    print("  PASS (exactly 180)")
else:
    print(f"  FAIL (need exactly 180, got {ab_words}, diff={ab_words - 180})")

# --- Conclusion ---
conc_match = re.search(r"## V\. Conclusion\s+(.*?)\n---", text, re.S)
conclusion = conc_match.group(1).strip()
co_words = word_count(conclusion)
print(f"Conclusion: {co_words} words")
if 240 <= co_words <= 260:
    print("  PASS (within 240-260)")
else:
    print(f"  FAIL (need 240-260, got {co_words})")

# --- Section paragraphs (sentence counts) ---
# Find every "##" section, look at the prose paragraphs inside.
def collect_paragraphs(text):
    # Remove tables, image links, lists
    lines = text.splitlines()
    out_paragraphs = []
    current = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            in_table = True
            continue
        if in_table and (stripped == "" or not stripped.startswith("|")):
            in_table = False
        if stripped == "":
            if current:
                p = " ".join(current).strip()
                out_paragraphs.append(p)
                current = []
            continue
        # Skip headers
        if stripped.startswith("#"):
            if current:
                p = " ".join(current).strip()
                out_paragraphs.append(p)
                current = []
            continue
        # Skip horizontal rules, image links, bold-table-captions, list items
        if stripped.startswith("---"):
            continue
        if stripped.startswith("!["):
            continue
        if re.match(r"^\d+\.\s", stripped):
            continue
        if stripped.startswith("- "):
            continue
        if stripped.startswith("**Table"):
            continue
        if stripped.startswith("**Index Terms"):
            continue
        current.append(stripped)
    if current:
        out_paragraphs.append(" ".join(current).strip())
    return out_paragraphs


paragraphs = collect_paragraphs(text)
prose_paragraphs = [p for p in paragraphs if word_count(p) >= 40]

print(f"\nFound {len(prose_paragraphs)} prose paragraphs")
print("Sentence counts per paragraph (target 7-10):")
out_of_range = 0
for i, p in enumerate(prose_paragraphs, 1):
    sc = sentence_count(p)
    flag = "ok" if 7 <= sc <= 10 else "OUT OF RANGE"
    if not 7 <= sc <= 10:
        out_of_range += 1
    first_words = " ".join(p.split()[:8])
    print(f"  P{i:2d}: {sc} sentences ({flag}) -- {first_words}...")

# --- References ---
refs_match = re.search(r"## References\s+(.*)", text, re.S)
refs_block = refs_match.group(1)
refs = re.findall(r"\[\d+\]\s+(.*?)(?=\n\n\[\d+\]|\Z)", refs_block, re.S)
num_refs = len(refs)
print(f"\nReferences: {num_refs}")
if 10 <= num_refs <= 15:
    print(f"  PASS (10-15)")
else:
    print(f"  FAIL (need 10-15)")

# Years
years_found = []
for r in refs:
    years = re.findall(r"\b(19\d\d|20\d\d)\b", r)
    if years:
        # The year of publication is usually the LAST 4-digit year (after page numbers).
        years_found.append(int(years[-1]))
    else:
        years_found.append(None)

ge_2020 = sum(1 for y in years_found if y is not None and y >= 2020)
print(f"References from 2020 or later: {ge_2020}/{num_refs} = {ge_2020/num_refs*100:.1f}%")
if ge_2020 / num_refs >= 0.80:
    print(f"  PASS (>=80%)")
else:
    print(f"  FAIL (<80%)")

print("\nYear by ref:")
for i, (r, y) in enumerate(zip(refs, years_found), 1):
    snippet = r.replace("\n", " ")[:60]
    print(f"  [{i}] {y}: {snippet}")

print(f"\nSummary: {out_of_range} paragraphs out of range; "
      f"abstract {'ok' if ab_words == 180 else 'BAD'}; "
      f"conclusion {'ok' if 240 <= co_words <= 260 else 'BAD'}; "
      f"refs {'ok' if (10 <= num_refs <= 15 and ge_2020/num_refs >= 0.80) else 'BAD'}.")

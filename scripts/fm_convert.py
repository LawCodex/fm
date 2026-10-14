#!/usr/bin/env python3
"""Convert the FSM Code 2014 chapter files and the FSM Constitution (cached by fm_fetch.py) to Markdown.

Usage: fm_convert.py RAW_DIR OUT_DIR
"""
import datetime, os, re, sys, unicodedata
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from markdownify import markdownify

RAW, OUT = sys.argv[1], sys.argv[2]
BASE = "https://www.fsmlaw.org/fsm/"
TODAY = datetime.date.today().isoformat()


def yq(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def load(rel):
    p = os.path.join(RAW, "html", rel)
    return open(p, "rb").read().decode("cp1252", "replace") if os.path.exists(p) else None


def to_md(soup_body):
    for t in soup_body.find_all(["script", "style", "button"]):
        t.decompose()
    for a in soup_body.find_all("a"):
        if a.get("href", "").startswith("#") or not a.get_text(strip=True):
            a.unwrap()
    for img in soup_body.find_all("img"):
        img.decompose()
    md = markdownify(str(soup_body), heading_style="ATX", bullets="-")
    md = md.replace("\xa0", " ")
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


def chapter(rel):
    html = load(rel)
    if not html:
        return None
    soup = BeautifulSoup(html, "lxml")
    body = soup.body or soup
    # title line, e.g. "FSMC, TITLE 4. JUDICIARY OF THE FSM"
    tdiv = body.find(string=re.compile(r"TITLE\s+\d+", re.I))
    title_line = re.sub(r"\s+", " ", tdiv).strip() if tdiv else ""
    if tdiv is not None:
        par = tdiv.find_parent("div")
        if par is not None:
            par.decompose()
    # drop the table of sections (h4 SECTIONS + following paragraph)
    for h4 in body.find_all("h4"):
        if h4.get_text(strip=True).upper() in ("SECTIONS", "SECTION"):
            nxt = h4.find_next_sibling()
            if nxt is not None and nxt.name == "p":
                nxt.decompose()
            h4.decompose()
    h2 = body.find("h2")
    ch_title = re.sub(r"\s+", " ", h2.get_text(" ")).strip() if h2 else os.path.basename(rel)
    if h2 is not None:
        h2.decompose()
    for h in body.find_all("h2"):
        h.name = "h3"
    for h in body.find_all("h3"):
        txt = re.sub(r"\s+", " ", h.get_text(" ")).strip()
        h.clear()
        h.string = txt
        h.name = "h3"
    return title_line, ch_title, to_md(body)


def slug(s, n=80):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:n].rstrip("-")


def main():
    n = 0
    # constitution
    html = load("constitution/constitution.htm")
    if html:
        soup = BeautifulSoup(html, "lxml")
        body = soup.body or soup
        for t in body.find_all(["b", "i", "strong", "em", "u", "font", "span"]):
            t.unwrap()
        md = to_md(body)
        # headings: ARTICLE N + its title line; Section N.
        md = re.sub(r"(?m)^ARTICLE ([IVXLC]+)\s*\n\n([^\n]{1,120})\n", r"## ARTICLE \1 — \2\n", md)
        md = re.sub(r"(?m)^(Section \d+[A-Za-z]?)\.\s*", r"#### \1.\n\n", md)
        md = re.sub(r"(?m)^(PREAMBLE)$", r"## \1", md)
        md = re.sub(r"(?m)^(SCHEDULE ON TRANSITION|TRANSITION)$", r"## \1", md)
        fm = ["---", 'title: "Constitution of the Federated States of Micronesia"', 'identifier: "FSM Const."',
              "type: constitution", "jurisdiction: fm", "language: en", "date: 1979-05-10", "status: in_force",
              f"source: {yq(BASE + 'constitution/constitution.htm')}",
              'publisher: "FSM Legal Information System (fsmlaw.org)"', f"retrieved: {TODAY}", "---", ""]
        p = os.path.join(OUT, "constitution", "constitution-of-the-federated-states-of-micronesia.md")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write(
            "\n".join(fm) + "# Constitution of the Federated States of Micronesia\n\n" + md + "\n")
        n += 1
    idx = load("code/indexcode2014.html")
    links = []
    for h in re.findall(r'href="([^"]+)"', idx):
        if re.match(r"^title\d+/.*\.html?$", h, re.I) and h not in links:
            links.append(h)
    counts = {}
    for h in links:
        rel = "code/" + h
        r = chapter(rel)
        if not r:
            continue
        title_line, ch_title, md = r
        tnum = int(re.search(r"title(\d+)", h, re.I).group(1))
        name = slug(ch_title.replace("CHAPTER", "chapter")) or slug(os.path.basename(h))
        sub = os.path.splitext(os.path.basename(h))[0]
        fname = slug(sub) + ".md"
        title = f"FSM Code 2014, Title {tnum}, {ch_title}"
        fm = ["---", f"title: {yq(title)}", f"identifier: {yq(f'{tnum} F.S.M.C. ' + ch_title.split(' ')[1] if ch_title.upper().startswith('CHAPTER') and len(ch_title.split()) > 1 else sub)}",
              "type: code", "jurisdiction: fm", "language: en", "edition: \"FSM Code 2014 (annotated)\"",
              f"code_title: {yq(title_line)}", "status: " + ("repealed" if re.search(r"repealed", ch_title, re.I) else "in_force"),
              f"source: {yq(urljoin(BASE + 'code/', h))}", f"retrieved: {TODAY}", "---", ""]
        p = os.path.join(OUT, "code", f"title-{tnum:02d}", fname)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8", newline="\n").write("\n".join(fm) + f"# {title}\n\n" + md + "\n")
        counts[tnum] = counts.get(tnum, 0) + 1
        n += 1
    print(n, "files;", len(counts), "titles")


if __name__ == "__main__":
    main()

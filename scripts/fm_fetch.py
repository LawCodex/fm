#!/usr/bin/env python3
"""Fetch the Constitution and the Code of the Federated States of Micronesia (FSM Code 2014,
HTML chapter files) from the FSM Legal Information System (https://www.fsmlaw.org).

robots.txt sets Crawl-delay: 30 — every request waits 30 s. Responses are cached in RAW/html/.
Usage: fm_fetch.py RAW_DIR
"""
import os, re, sys, time
from urllib.parse import urljoin
import requests

BASE = "https://www.fsmlaw.org/fsm/"
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
DELAY = 30
RAW = sys.argv[1]
S = requests.Session()
S.headers["User-Agent"] = UA
_last = [0.0]


def get(url):
    rel = url.split("/fsm/", 1)[1]
    p = os.path.join(RAW, "html", rel)
    if os.path.exists(p):
        return open(p, "rb").read()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    for a in range(4):
        wait = _last[0] + DELAY - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            r = S.get(url, timeout=120)
            if r.status_code == 200:
                open(p, "wb").write(r.content)
                return r.content
            print("HTTP", r.status_code, url, file=sys.stderr, flush=True)
            if r.status_code == 404:
                return None
        except Exception as e:
            print("ERR", url, e, file=sys.stderr, flush=True)
    return None


def main():
    get(BASE + "constitution/constitution.htm")
    idx = get(BASE + "code/indexcode2014.html").decode("latin-1")
    links = []
    for h in re.findall(r'href="([^"]+)"', idx):
        if re.match(r"^title\d+/.*\.html?$", h, re.I) and h not in links:
            links.append(h)
    print(len(links), "chapter files", flush=True)
    for i, h in enumerate(links):
        get(urljoin(BASE + "code/", h))
        if i % 25 == 0:
            print(i, flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()

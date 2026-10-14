# LawCodex — Federated States of Micronesia (`fm`)

National legislation of the Federated States of Micronesia as plain Markdown: the **Constitution**
and the **Code of the Federated States of Micronesia, 2014 edition (annotated)**, from the FSM Legal
Information System (<https://www.fsmlaw.org>), a project run with the Supreme Court of the FSM.

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as Markdown in git.

Retrieved: **2026-10-13 – 2026-10-15**.

## Contents

| Category | Directory | Files |
|---|---|---:|
| Constitution of the Federated States of Micronesia | `constitution/` | 1 |
| FSM Code 2014 — one file per chapter (or schedule) | `code/title-NN/` | 386 (48 titles; 12 chapters marked repealed) |
| **Total** | | **387** |

The FSM Code files are the annotated edition: each section is followed by its **Source** note
(public law), **Cross-reference** and **Case annotations** as published by the LIS, all kept verbatim.

## What is NOT covered

- The **state codes** (Chuuk, Kosrae, Pohnpei, Yap), Supreme Court rules and decisions, national
  regulations and the Compact of Free Association documents also hosted on fsmlaw.org — not
  included (the 30-second crawl delay makes a full crawl of the site impractical; national
  primary legislation was prioritised).
- Public laws enacted after the FSM Code 2014 consolidation (they are published by the FSM Congress,
  <https://www.cfsm.gov.fm>, not consolidated here).
- One chapter file linked from the index returned HTTP 404 (`title06/T6_Ch16_SchI_2014.html`).
- Constitutional amendments are published on fsmlaw.org as separate pages
  (`fsm/constitution/amend*.htm`); the file here is the site's full-text `constitution.htm`.

## Structure

```
constitution/constitution-of-the-federated-states-of-micronesia.md   ## ARTICLE …, #### Section N.
code/title-04/t4-ch1-2014.md                                          # FSM Code 2014, Title 4, CHAPTER 1 …
                                                                      ### § 101. Short title.
```

File names follow the LIS source file names (e.g. `t4-ch1-2014` = Title 4, Chapter 1); `identifier`
gives the F.S.M.C. citation (e.g. `4 F.S.M.C. 1`), `code_title` the Title heading.

## Sources and licence

- Source: FSM Legal Information System, <https://www.fsmlaw.org/fsm/code/indexcode2014.html> and
  <https://www.fsmlaw.org/fsm/constitution/constitution.htm>. The LIS describes its texts as copies
  of official publications of the National Government and states that "these documents are within
  the public domain", while noting the copies are not an official publication.
- robots.txt sets `Crawl-delay: 30`; every request was spaced 30 seconds apart (≈390 requests,
  identifying User-Agent, cached).

## Regenerate

```sh
python3 scripts/fm_fetch.py   ../_raw/fm     # 30 s between requests (~3.5 h for a full run)
python3 scripts/fm_convert.py ../_raw/fm .
```

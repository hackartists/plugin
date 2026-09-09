#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""org 덱을 PowerPoint 로 옮기기 위한 모듈형 CLI.

커맨드는 JSON 스펙 파일에 요소를 하나씩 쌓고, 마지막에 build 가 pptx 를 만든다.
pptx 를 직접 열고 닫지 않기 때문에 순서를 바꾸거나 중간에 끼워 넣어도 결과가
흔들리지 않는다 -- 같은 커맨드 나열이면 같은 pptx 가 나온다.

  deck.py new spec.json --title "..." --subtitle "..." --date "2026년 8월"
  deck.py add-toc  spec.json --entry "1|개요|전략 전환;역할과 수익"
  deck.py add-chapter spec.json --no 1 --title 개요 --items "전략 전환;역할과 수익"
  deck.py add-page spec.json --title "3자 R&R — 리스크는 *해외 주관사*" \
                             --section "I. 개요" --sub "역할과 수익"
  deck.py add-table spec.json --header "구분|해외 SPV|DB증권" \
                              --row "법적 지위|*발행 주체*|공급자" --widths "1.5,4,4"
  deck.py add-callout spec.json --text "*설계 원칙*  리스크와 수익을 분리한다"
  deck.py build spec.json -o out.pptx

요소 커맨드(add-table / add-column / add-image / ...)는 직전에 추가한
add-page 에 붙는다.

인라인 마크업:  *굵게* -> 볼드+키컬러,  !강조! -> 볼드+레드,  \\n -> 줄바꿈
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


# ── 스펙 입출력 ──────────────────────────────────────────────────────────
def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, spec):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)


def last_page(spec, cmd):
    for sl in reversed(spec["slides"]):
        if sl["kind"] == "page":
            return sl
    sys.exit(f"{cmd}: 붙일 페이지가 없습니다. 먼저 add-page 를 실행하세요.")


def nl(v):
    return v.replace("\\n", "\n") if isinstance(v, str) else v


def split(v, sep):
    return [nl(x) for x in v.split(sep)] if v else []


def maybe_json(v):
    """--arch '{...}' 또는 --arch path/to.json 둘 다 받는다."""
    if v is None:
        return None
    if os.path.exists(v):
        with open(v, encoding="utf-8") as f:
            return json.load(f)
    return json.loads(v)


# ── 커맨드 ───────────────────────────────────────────────────────────────
def cmd_new(a):
    save(a.spec, {"meta": {"title": a.title, "subtitle": a.subtitle,
                           "author": a.author, "email": a.email, "date": a.date,
                           "institute": a.institute, "slidenote": a.slidenote,
                           "thanks": a.thanks, "thanksnote": a.thanksnote},
                  "slides": ([{"kind": "cover"}] if not a.no_cover else [])})


def cmd_add_toc(a):
    spec = load(a.spec)
    entries = []
    for e in a.entry:
        no, title, items = (e.split("|") + ["", ""])[:3]
        entries.append([int(no), title, [i for i in items.split(";") if i]])
    spec["slides"].append({"kind": "toc", "entries": entries})
    save(a.spec, spec)


def cmd_add_chapter(a):
    spec = load(a.spec)
    spec["slides"].append({"kind": "chapter", "no": a.no, "title": a.title,
                           "items": [i for i in (a.items or "").split(";") if i]})
    save(a.spec, spec)


def cmd_add_page(a):
    spec = load(a.spec)
    pg = {"kind": "page", "title": a.title, "section": a.section or "",
          "sub": a.sub or "", "elements": []}
    spec["slides"].append(pg)
    if a.note:
        pg["elements"].append({"type": "note", "text": nl(a.note)})
    if a.callout:
        pg["elements"].append({"type": "callout", "text": nl(a.callout)})
    save(a.spec, spec)


def cmd_add_table(a):
    spec = load(a.spec)
    pg = last_page(spec, "add-table")
    el = {"type": "table",
          "header": split(a.header, "|") if a.header else None,
          "rows": [split(r, "|") for r in a.row],
          "widths": [float(x) for x in a.widths.split(",")],
          "row_h": a.row_h, "size": a.size}
    pg["elements"].insert(_pos(pg), el)
    save(a.spec, spec)


def cmd_add_column(a):
    spec = load(a.spec)
    pg = last_page(spec, "add-column")
    cols = []
    for c in a.col:
        head, _, rest = c.partition("::")
        blocks = []
        for chunk in rest.split("::"):
            if not chunk:
                continue
            blocks.append([nl(b) for b in chunk.split(";;") if b])
        cols.append({"heading": nl(head), "bullets": blocks[0] if blocks else []})
    ratios = [float(x) for x in a.ratios.split(",")] if a.ratios else [1] * len(cols)
    pg["elements"].insert(_pos(pg), {"type": "columns", "ratios": ratios, "cols": cols})
    save(a.spec, spec)


def cmd_add_fnarch(a):
    spec = load(a.spec)
    pg = last_page(spec, "add-functional-architecture")
    pg["elements"].insert(_pos(pg), {"type": "fnarch", "arch": maybe_json(a.arch)})
    save(a.spec, spec)


def cmd_add_image(a):
    spec = load(a.spec)
    pg = last_page(spec, "add-image")
    pg["elements"].insert(_pos(pg), {"type": "image", "path": a.path,
                                     "w": a.width, "h": a.height})
    save(a.spec, spec)


def cmd_add_asistobe(a):
    spec = load(a.spec)
    pg = last_page(spec, "add-asis-tobe")
    rows = []
    for r in a.row:
        tag, lft, rgt = (r.split("|") + ["", ""])[:3]
        rows.append([nl(tag), nl(lft), nl(rgt)])
    pg["elements"].insert(_pos(pg), {"type": "asistobe", "asis": nl(a.asis),
                                     "tobe": nl(a.tobe), "rows": rows})
    save(a.spec, spec)


def cmd_add_note(a):
    spec = load(a.spec)
    last_page(spec, "add-note")["elements"].append({"type": "note", "text": nl(a.text)})
    save(a.spec, spec)


def cmd_add_callout(a):
    spec = load(a.spec)
    last_page(spec, "add-callout")["elements"].append(
        {"type": "callout", "text": nl(a.text)})
    save(a.spec, spec)


def cmd_add_thanks(a):
    spec = load(a.spec)
    spec["slides"].append({"kind": "thanks"})
    save(a.spec, spec)


def _pos(pg):
    """note/callout 은 항상 바닥에 붙으므로 그 앞에 끼워 넣는다."""
    for i, e in enumerate(pg["elements"]):
        if e["type"] in ("note", "callout"):
            return i
    return len(pg["elements"])


# ── 렌더 ─────────────────────────────────────────────────────────────────
def cmd_build(a):
    from biyard_pptx import Deck
    spec = load(a.spec)
    m = spec["meta"]
    d = Deck(**{k: (m.get(k) or "") for k in
                ("title", "subtitle", "author", "email", "date", "institute",
                 "slidenote", "thanks", "thanksnote")})
    for sl in spec["slides"]:
        k = sl["kind"]
        if k == "cover":
            d.cover()
        elif k == "toc":
            d.toc([(e[0], e[1], e[2]) for e in sl["entries"]])
        elif k == "chapter":
            d.chapter(sl["no"], sl["title"], sl.get("items", []))
        elif k == "thanks":
            d.thanks()
        elif k == "page":
            s = d.content(sl["title"], section=sl.get("section", ""),
                          sub=sl.get("sub", ""))
            for el in sl["elements"]:
                t = el["type"]
                if t == "table":
                    s.table(el.get("header"), el["rows"], el["widths"],
                            size=el.get("size") or 9,
                            row_h=el.get("row_h") or 0.30)
                elif t == "columns":
                    boxes = s.columns(el["ratios"])
                    for box, c in zip(boxes, el["cols"]):
                        if c.get("heading"):
                            box.heading(c["heading"])
                        if c.get("bullets"):
                            box.bullets(c["bullets"])
                elif t == "fnarch":
                    s.fnarch(el["arch"])
                elif t == "asistobe":
                    s.asistobe(el)
                elif t == "image":
                    s.image(el["path"], w=el.get("w"), h=el.get("h"))
                elif t == "note":
                    s.note(el["text"])
                elif t == "callout":
                    s.callout(el["text"])
    out = a.output or os.path.splitext(a.spec)[0] + ".pptx"
    d.save(out)
    print(out, len(d.prs.slides._sldIdLst), "slides")


# ── 파서 ─────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(prog="deck.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, help_):
        p = sub.add_parser(name, help=help_)
        p.add_argument("spec")
        p.set_defaults(func=fn)
        return p

    p = add("new", cmd_new, "덱 생성 (표지 포함)")
    for k in ("title", "subtitle", "author", "email", "date", "institute",
              "slidenote", "thanks", "thanksnote"):
        p.add_argument("--" + k, default={"institute": "㈜바이야드",
                                          "thanks": "Thank you"}.get(k, ""))
    p.add_argument("--no-cover", action="store_true")

    p = add("add-toc", cmd_add_toc, "목차 (--entry '1|개요|하위1;하위2')")
    p.add_argument("--entry", action="append", required=True)

    p = add("add-chapter", cmd_add_chapter, "챕터 간지")
    p.add_argument("--no", type=int, required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--items", default="")

    p = add("add-page", cmd_add_page, "본문 페이지 (이후 요소가 여기에 붙는다)")
    p.add_argument("--title", required=True)
    p.add_argument("--section", default="")
    p.add_argument("--sub", default="")
    p.add_argument("--note", default="")
    p.add_argument("--callout", default="")

    p = add("add-table", cmd_add_table, "표")
    p.add_argument("--header", default="")
    p.add_argument("--row", action="append", required=True)
    p.add_argument("--widths", required=True)
    p.add_argument("--row-h", dest="row_h", type=float, default=0.30)
    p.add_argument("--size", type=float, default=9)

    p = add("add-column", cmd_add_column, "다단 (--col '소제목::불릿1;;불릿2')")
    p.add_argument("--col", action="append", required=True)
    p.add_argument("--ratios", default="")

    p = add("add-functional-architecture", cmd_add_fnarch, "기능 아키텍처 도해")
    p.add_argument("--arch", required=True, help="JSON 문자열 또는 .json 경로")

    p = add("add-image", cmd_add_image, "이미지")
    p.add_argument("--path", required=True)
    p.add_argument("--width", type=float)
    p.add_argument("--height", type=float)

    p = add("add-asis-tobe", cmd_add_asistobe, "AS-IS / TO-BE")
    p.add_argument("--asis", required=True)
    p.add_argument("--tobe", required=True)
    p.add_argument("--row", action="append", default=[], help="'태그|AS-IS|TO-BE'")

    p = add("add-note", cmd_add_note, "하단 회색 한 줄")
    p.add_argument("--text", required=True)

    p = add("add-callout", cmd_add_callout, "하단 틴트 박스")
    p.add_argument("--text", required=True)

    add("add-thanks", cmd_add_thanks, "마무리 페이지")

    p = add("build", cmd_build, "pptx 출력")
    p.add_argument("-o", "--output", default="")

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""hackartist-new.sty 의 룩앤필을 PowerPoint 로 옮긴 빌더.

sty 가 beamer 템플릿으로 하는 일 -- 표지 · 챕터 간지 · 제목 밴드 · 헤더/푸터 ·
표 스타일 · 강조색 · 기능 아키텍처 도해 -- 를 python-pptx 네이티브 도형으로
다시 그린다. 이미지가 아니라 실제 도형/텍스트라 PowerPoint 에서 편집된다.

  from biyard_pptx import Deck
  d = Deck(title="...", subtitle="...", slidenote="...")
  d.cover()
  d.chapter(1, "개요", ["전략 전환", "역할과 수익"])
  s = d.content("3자 R&R — 리스크는 *해외 주관사*", section="I. 개요", sub="역할과 수익")
  s.table(["구분", "해외 SPV", "DB증권"], [[...], ...], [1.5, 4.2, 4.2])
  s.callout("*설계 원칙*  리스크와 수익을 법인격 단위로 분리한다")
  d.thanks()
  d.save("out.pptx")

인라인 마크업(표·본문 공통):
  *굵게*  -> 볼드 + 키컬러      !강조!  -> 볼드 + 레드
"""

import copy
import os
import re

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "assets", "biyard-logo.png")

# ── hackartist-new.sty 팔레트 그대로 ──────────────────────────────────────
C = {
    "key":       RGBColor(0x00, 0xDB, 0xBD),
    "key_deep":  RGBColor(0x00, 0x80, 0x6F),
    "key_dark":  RGBColor(0x00, 0x5C, 0x50),
    "ink":       RGBColor(0x06, 0x23, 0x1F),
    "red":       RGBColor(0xC0, 0x00, 0x00),
    "amber":     RGBColor(0xED, 0x7D, 0x31),
    "green":     RGBColor(0x00, 0x90, 0x51),
    "dark":      RGBColor(0x26, 0x26, 0x26),
    "gray":      RGBColor(0x6E, 0x6E, 0x6E),
    "rule":      RGBColor(0xAA, 0xE0, 0xD7),
    "tint":      RGBColor(0xE6, 0xFA, 0xF6),
    "white":     RGBColor(0xFF, 0xFF, 0xFF),
    "yellow":    RGBColor(0xFF, 0xE0, 0x66),
}

FONT = "Pretendard"
FONT_FALLBACK = "맑은 고딕"      # Pretendard 미설치 PC 대비

# ── 슬라이드 기하 (16:9, 13.333 x 7.5 in) ────────────────────────────────
SW, SH = 13.3333, 7.5
MARGIN = 0.50
HEAD_Y = 0.16
SUBHEAD_Y = 0.36
BAND_Y, BAND_H = 0.74, 0.62
BODY_TOP = 1.56
BODY_BOT = 6.82
FOOT_Y = 6.95
BODY_W = SW - 2 * MARGIN

_MARKUP = re.compile(r"(\*[^*]+\*|![^!]+!)")


def _runs(paragraph, text, size, color, bold=False, font=FONT):
    """*굵게* / !강조! 마크업을 run 으로 쪼갠다."""
    for piece in _MARKUP.split(text):
        if not piece:
            continue
        r = paragraph.add_run()
        if piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            r.text = piece[1:-1]
            r.font.bold = True
            r.font.color.rgb = C["key_deep"]
        elif piece.startswith("!") and piece.endswith("!") and len(piece) > 2:
            r.text = piece[1:-1]
            r.font.bold = True
            r.font.color.rgb = C["red"]
        else:
            r.text = piece
            r.font.bold = bold
            r.font.color.rgb = color
        r.font.size = Pt(size)
        r.font.name = font



def _wrapped_lines(text, width_in, size_pt):
    """줄 수 추정. 한글은 폭이 폰트 크기와 거의 같고 ASCII 는 절반쯤이므로
    글자마다 가중치를 달리 세어야 실제 줄바꿈과 맞는다."""
    import math
    weighted = sum(1.0 if ord(c) > 0x2000 else 0.5 for c in str(text))
    per_line = max(1.0, width_in / (size_pt / 72.0))
    return max(1, math.ceil(weighted / per_line))


def _textbox(slide, x, y, w, h, text, size=11, color=None, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, wrap=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, line in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.15
        _runs(p, line, size, color or C["dark"], bold)
    return tb



def _no_shadow(shape):
    """자동도형에 딸려오는 테마 그림자·스타일을 지운다."""
    from lxml import etree
    from pptx.oxml.ns import qn
    sp = shape._element
    style = sp.find(qn("p:style"))
    if style is not None:
        sp.remove(style)
    spPr = sp.find(qn("p:spPr"))
    if spPr is not None:
        for eff in spPr.findall(qn("a:effectLst")):
            spPr.remove(eff)
        spPr.append(etree.SubElement(spPr, qn("a:effectLst")))



def _drop_shadow(shape, blur=6.0, dist=3.0, direction=2700000, alpha=28000):
    from lxml import etree
    from pptx.oxml.ns import qn
    spPr = shape._element.find(qn("p:spPr"))
    for eff in spPr.findall(qn("a:effectLst")):
        spPr.remove(eff)
    lst = etree.SubElement(spPr, qn("a:effectLst"))
    outer = etree.SubElement(lst, qn("a:outerShdw"))
    outer.set("blurRad", str(int(blur * 12700)))
    outer.set("dist", str(int(dist * 12700)))
    outer.set("dir", str(direction))
    outer.set("rotWithShape", "0")
    c = etree.SubElement(outer, qn("a:srgbClr")); c.set("val", "6E6E6E")
    a = etree.SubElement(c, qn("a:alpha")); a.set("val", str(alpha))


def _rect(slide, x, y, w, h, fill=None, line=None, lw=0.75, radius=None):
    shape_t = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    sh = slide.shapes.add_shape(shape_t, Inches(x), Inches(y), Inches(w), Inches(h))
    if radius:
        sh.adjustments[0] = radius
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    _no_shadow(sh)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = Inches(0.03)
    tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    sh.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    return sh


def _label(shape, text, size, color, bold=True):
    tf = shape.text_frame
    for i, line in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.line_spacing = 1.0
        _runs(p, line, size, color, bold)



# ═══════════════════════════════════════════════════════════════ Canvas ══
def _arrow_ends(shape, head=True, tail=False, kind="triangle", size="med"):
    from lxml import etree
    from pptx.oxml.ns import qn
    ln = shape._element.find(qn("p:spPr")).find(qn("a:ln"))
    if ln is None:
        spPr = shape._element.find(qn("p:spPr"))
        ln = etree.SubElement(spPr, qn("a:ln"))
    for tag, on in (("a:headEnd", tail), ("a:tailEnd", head)):
        if not on:
            continue
        e = etree.SubElement(ln, qn(tag))
        e.set("type", kind); e.set("w", size); e.set("len", size)


class Canvas:
    """TikZ 좌표계를 그대로 쓰는 그리기 면.

    y 는 위로 증가(TikZ 관례). xmax/ymax 로 준 논리 크기를 슬라이드의
    (x, y, w, h) 안에 비율 유지로 맞춰 넣고 가운데 정렬한다. 덕분에 org 덱의
    tikzpicture 좌표를 손대지 않고 옮길 수 있다.
    """

    def __init__(self, slide, x, y, w, h, xmax, ymax, xmin=0.0, ymin=0.0):
        self.s = slide
        sx = min(w / (xmax - xmin), h / (ymax - ymin))
        self.k = sx
        self.ox = x + (w - (xmax - xmin) * sx) / 2 - xmin * sx
        self.oy = y + (h - (ymax - ymin) * sx) / 2 + ymax * sx

    def X(self, v):  return self.ox + v * self.k
    def Y(self, v):  return self.oy - v * self.k
    def S(self, v):  return v * self.k
    def pt(self, v): return max(5.0, v * self.k * 72.0)

    # ---- 도형 -----------------------------------------------------------
    def box(self, cx, cy, w, h, text="", fill=None, line=None, size=0.22,
            color=None, bold=False, lw=0.5, radius=0.06, dash=False):
        sh = _rect(self.s, self.X(cx - w / 2), self.Y(cy + h / 2),
                   self.S(w), self.S(h), fill=fill, line=line, lw=lw, radius=radius)
        if dash and line is not None:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            sh.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        if text:
            _label(sh, text, self.pt(size), color or C["dark"], bold=bold)
        return sh

    def text(self, cx, cy, text, size=0.20, color=None, align=PP_ALIGN.CENTER,
             w=3.0, bold=False, anchor="c"):
        h = 0.5 * max(1, str(text).count("\n") + 1)
        yy = self.Y(cy) - self.S(h) / 2
        xx = self.X(cx) - self.S(w) / 2 if anchor == "c" else self.X(cx)
        return _textbox(self.s, xx, yy, self.S(w), self.S(h), text,
                        size=self.pt(size), color=color or C["gray"],
                        align=align, bold=bold, anchor=MSO_ANCHOR.MIDDLE)

    def _seg(self, p1, p2, color, lw, dash, head, tail):
        from pptx.enum.shapes import MSO_CONNECTOR
        cn = self.s.shapes.add_connector(
            MSO_CONNECTOR.STRAIGHT, Inches(self.X(p1[0])), Inches(self.Y(p1[1])),
            Inches(self.X(p2[0])), Inches(self.Y(p2[1])))
        cn.line.color.rgb = color
        cn.line.width = Pt(lw)
        if dash:
            from pptx.enum.dml import MSO_LINE_DASH_STYLE
            cn.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        if head or tail:
            _arrow_ends(cn, head=head, tail=tail)
        return cn

    def arrow(self, p1, p2, color=None, lw=1.25, dash=False, both=False):
        return self._seg(p1, p2, color or C["key_deep"], lw, dash, True, both)

    def line(self, p1, p2, color=None, lw=1.0, dash=False):
        return self._seg(p1, p2, color or C["rule"], lw, dash, False, False)

    def path(self, pts, color=None, lw=1.25, dash=False, head=True, both=False):
        """꺾은선. 마지막 구간에만 화살촉을 붙인다."""
        color = color or C["key_deep"]
        for i in range(len(pts) - 1):
            last = (i == len(pts) - 2)
            self._seg(pts[i], pts[i + 1], color, lw, dash,
                      head and last, both and i == 0)

    def blockarrow(self, cx, cy, w, h, both=True, fill=None, line=None):
        shp = MSO_SHAPE.LEFT_RIGHT_ARROW if both else MSO_SHAPE.RIGHT_ARROW
        sh = self.s.shapes.add_shape(shp, Inches(self.X(cx - w / 2)),
                                     Inches(self.Y(cy + h / 2)),
                                     Inches(self.S(w)), Inches(self.S(h)))
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill or RGBColor(0xB3, 0xF2, 0xE9)
        sh.line.color.rgb = line or C["key_deep"]
        sh.line.width = Pt(0.5)
        _no_shadow(sh)
        return sh


# ══════════════════════════════════════════════════════════════ 슬라이드 ══
class Slide:
    """본문 슬라이드 -- 제목 밴드 아래 영역에 요소를 얹는다."""

    def __init__(self, deck, slide):
        self.deck, self.s = deck, slide
        self._y = BODY_TOP           # 세로 커서

    # ---- 배치 헬퍼 -------------------------------------------------------
    def columns(self, ratios, gap=0.30, y=None, h=None):
        """가로 분할. ratios 합이 1 이 아니어도 비율로 정규화한다."""
        y = BODY_TOP if y is None else y
        h = (BODY_BOT - y) if h is None else h
        tot = sum(ratios)
        usable = BODY_W - gap * (len(ratios) - 1)
        boxes, x = [], MARGIN
        for r in ratios:
            w = usable * r / tot
            boxes.append(_Box(self, x, y, w, h))
            x += w + gap
        return boxes

    # ---- 요소 -----------------------------------------------------------
    def heading(self, text, x=None, y=None, w=None, size=12):
        x = MARGIN if x is None else x
        y = self._y if y is None else y
        w = BODY_W if w is None else w
        _textbox(self.s, x, y, w, 0.26, text, size=size, color=C["key_dark"], bold=True)
        self._y = y + 0.32
        return self

    def bullets(self, items, x=None, y=None, w=None, size=11, gap=0.055):
        x = MARGIN if x is None else x
        y = self._y if y is None else y
        w = BODY_W if w is None else w
        cy = y
        for it in items:
            level, txt = (it if isinstance(it, tuple) else (0, it))
            ind = 0.16 * level
            bullet = _textbox(self.s, x + ind, cy, 0.14, 0.22, "▪",
                              size=size - 3, color=C["key_deep"])
            tw = w - ind - 0.17
            _textbox(self.s, x + ind + 0.17, cy - 0.015, tw, 0.22, txt, size=size)
            cy += _wrapped_lines(txt, tw, size) * (size * 1.25 / 72.0) + gap
        self._y = cy + 0.06
        return self

    def table(self, header, rows, widths, x=None, y=None, size=9,
              head_fill=None, label_col=True, row_h=0.30, w=None):
        x = MARGIN if x is None else x
        y = self._y if y is None else y
        head_fill = head_fill or C["ink"]
        total = sum(widths)
        w = (BODY_W if x == MARGIN else total) if w is None else w
        scale = w / total
        nrow, ncol = len(rows) + (1 if header else 0), len(widths)
        gt = self.s.shapes.add_table(nrow, ncol, Inches(x), Inches(y),
                                     Inches(w), Inches(row_h * nrow))
        tbl = gt.table
        tbl.first_row = bool(header)
        tbl.horz_banding = False
        for i, cw in enumerate(widths):
            tbl.columns[i].width = Emu(int(Inches(cw * scale)))

        def fill_cell(cell, text, bold, color, fill, plain=False):
            if plain:
                text = str(text).replace("*", "").replace("!", "")
            cell.fill.solid()
            cell.fill.fore_color.rgb = fill
            cell.margin_left = cell.margin_right = Inches(0.055)
            cell.margin_top = cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            for k, line in enumerate(str(text).split("\n")):
                p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
                p.line_spacing = 1.1
                _runs(p, line, size, color, bold)

        r0 = 0
        if header:
            for j, htxt in enumerate(header):
                fill_cell(tbl.cell(0, j), htxt, True, C["white"], head_fill, plain=True)
            r0 = 1
        for i, row in enumerate(rows):
            for j, cval in enumerate(row):
                is_label = label_col and j == 0
                fill_cell(tbl.cell(i + r0, j), cval, is_label,
                          C["white"] if is_label else C["dark"],
                          C["key_deep"] if is_label else C["white"],
                          plain=is_label)
        self._y = y + row_h * nrow + 0.12
        return self

    def note(self, text, size=8.5, y=None):
        y = BODY_BOT - 0.02 if y is None else y
        _textbox(self.s, MARGIN, y, BODY_W, 0.30, text, size=size,
                 color=C["gray"], align=PP_ALIGN.CENTER)
        return self

    def callout(self, text, size=10, y=None, h=0.34):
        y = (BODY_BOT - 0.42) if y is None else y
        box = _rect(self.s, MARGIN + 0.30, y, BODY_W - 0.60, h,
                    fill=C["tint"], line=None, radius=0.14)
        _label(box, text, size, C["dark"], bold=False)
        return self

    def image(self, path, x=None, y=None, w=None, h=None):
        kw = {}
        if w: kw["width"] = Inches(w)
        if h: kw["height"] = Inches(h)
        self.s.shapes.add_picture(path, Inches(x if x is not None else MARGIN),
                                  Inches(y if y is not None else BODY_TOP), **kw)
        return self

    def canvas(self, xmax, ymax, x=None, y=None, w=None, h=None, xmin=0.0, ymin=0.0):
        x = MARGIN if x is None else x
        y = self._y if y is None else y
        w = BODY_W if w is None else w
        h = (BODY_BOT - y - 0.10) if h is None else h
        return Canvas(self.s, x, y, w, h, xmax, ymax, xmin, ymin)


    # ---- AS-IS / TO-BE (sty 의 asistobe 이식) ------------------------------
    def asistobe(self, spec, y=None, h=None):
        y = BODY_TOP - 0.06 if y is None else y
        h = (BODY_BOT - y - 0.30) if h is None else h
        rows = spec.get("rows", [])
        H = 2.4 + 1.95 * max(1, len(rows))
        cv = Canvas(self.s, MARGIN, y, BODY_W, h, 16.0, H)
        _rect(self.s, cv.X(0.0), cv.Y(H), cv.S(6.6), cv.S(H),
              fill=RGBColor(0xF7, 0xF7, 0xF7), line=None, radius=0.02)
        _rect(self.s, cv.X(6.6), cv.Y(H), cv.S(9.4), cv.S(H),
              fill=C["tint"], line=None, radius=0.02)
        cv.text(3.3, H - 0.45, "AS-IS", size=0.34, color=C["dark"], bold=True, w=4)
        cv.text(11.3, H - 0.45, "TO-BE", size=0.34, color=C["key_deep"], bold=True, w=6)
        cv.text(3.3, H - 1.05, spec.get("asis", ""), size=0.21, color=C["red"],
                w=6.2, bold=True)
        cv.text(11.3, H - 1.05, spec.get("tobe", ""), size=0.21, color=C["key_deep"],
                w=8.8, bold=True)
        cv.blockarrow(6.6, H - 1.05, 1.0, 0.42, both=False,
                      fill=C["amber"], line=C["amber"])
        ry = H - 2.40
        for tag, lft, rgt in rows:
            cv.box(3.3, ry, 5.8, 1.30, lft, fill=C["white"],
                   line=RGBColor(0xD9, 0x8C, 0x8C), size=0.185, radius=0.03)
            cv.box(11.3, ry, 8.6, 1.30, rgt, fill=C["white"], line=C["key_deep"],
                   size=0.185, radius=0.03)
            cv.blockarrow(6.6, ry, 1.15, 0.62, both=False,
                          fill=RGBColor(0xB3, 0xF2, 0xE9), line=C["key_deep"])
            tb = _rect(self.s, cv.X(6.6) - cv.S(0.95), cv.Y(ry + 0.90),
                       cv.S(1.9), cv.S(0.34), fill=C["yellow"], line=C["amber"],
                       radius=0.14)
            _label(tb, tag, cv.pt(0.19), C["dark"], bold=True)
            ry -= 1.95
        return self

    # ---- 기능 아키텍처 (sty 의 fnarch 이식) --------------------------------
    def fnarch(self, spec, y=None, h=None):
        y = BODY_TOP + 0.05 if y is None else y
        h = (BODY_BOT - y - 0.30) if h is None else h
        _draw_fnarch(self.s, spec, y, h)
        return self


class _Box:
    """columns() 가 돌려주는 세로 영역. Slide 와 같은 요소 API 를 쓴다."""

    def __init__(self, slide, x, y, w, h):
        self.sl, self.x, self.y, self.w, self.h = slide, x, y, w, h
        self._y = y

    def heading(self, text, size=12):
        _textbox(self.sl.s, self.x, self._y, self.w, 0.26, text,
                 size=size, color=C["key_dark"], bold=True)
        self._y += 0.32
        return self

    def bullets(self, items, size=10.5, gap=0.05):
        cy = self._y
        for it in items:
            level, txt = (it if isinstance(it, tuple) else (0, it))
            ind = 0.16 * level
            _textbox(self.sl.s, self.x + ind, cy, 0.14, 0.22, "▪",
                     size=size - 3, color=C["key_deep"])
            tw = max(0.5, self.w - ind - 0.17)
            _textbox(self.sl.s, self.x + ind + 0.17, cy - 0.015, tw, 0.22,
                     txt, size=size)
            cy += _wrapped_lines(txt, tw, size) * (size * 1.25 / 72.0) + gap
        self._y = cy + 0.06
        return self

    def table(self, header, rows, widths, size=9, row_h=0.30):
        Slide.table(self.sl, header, rows, widths, x=self.x, y=self._y,
                    size=size, row_h=row_h, w=self.w)
        self._y = self.sl._y
        return self

    def image(self, path, w=None, h=None):
        self.sl.image(path, x=self.x, y=self._y, w=w or self.w, h=h)
        return self

    def canvas(self, xmax, ymax, h=None, xmin=0.0, ymin=0.0):
        hh = (self.y + self.h - self._y - 0.05) if h is None else h
        return Canvas(self.sl.s, self.x, self._y, self.w, hh, xmax, ymax, xmin, ymin)


# ══════════════════════════════════════════════════════ 기능 아키텍처 ══
def _draw_fnarch(slide, spec, oy, oh):
    """sty 의 fnarch 와 같은 산식으로 배치하고 네이티브 도형으로 그린다.

    내부 단위는 sty 와 동일(cm 계열)로 계산한 뒤 마지막에 슬라이드 인치로 스케일.
    """
    PW, LX, LXE, CX, CXE, LBX = 12.6, 0.25, 12.45, 1.95, 12.40, 1.10
    FH, FG, FGX = 0.62, 0.08, 0.14
    GT, GP, GGX, RG = 0.34, 0.10, 0.20, 0.18
    LP, LG, NH, TH, BP = 0.10, 0.22, 0.28, 0.66, 0.18
    EW, GAP = 2.55, 1.75

    layers = spec["layers"]
    band = spec.get("band")
    ext = spec.get("external")

    def layer_h(L):
        if "groups" in L:
            cols = L.get("cols") or len(L["groups"])
            rows = -(-len(L["groups"]) // cols)
            mf = max(len(g[1]) for g in L["groups"])
            gh = GT + mf * FH + (mf - 1) * FG + GP
            hh = rows * gh + (rows - 1) * RG + 2 * LP
        else:
            hh = FH + 2 * LP
        return hh + (NH if L.get("note") else 0)

    total = sum(layer_h(L) for L in layers) + (len(layers) - 1) * LG + TH + 2 * BP
    if band:
        total += FH + 2 * LP + LG

    TW = PW + GAP + EW
    sx = min(BODY_W / TW, oh / total)      # 인치 스케일
    ox = MARGIN + (BODY_W - TW * sx) / 2

    def X(v):  return ox + v * sx
    def Y(v):  return oy + (total - v) * sx      # tikz y(위쪽 증가) -> ppt y
    def S(v):  return v * sx
    def pt(v): return max(5.0, v * sx * 72.0)    # 1 unit = 1cm 기준 환산

    # 플랫폼 카드
    card = _rect(slide, X(0), Y(total), S(PW), S(total),
                 fill=C["white"], line=C["key_deep"], lw=0.75, radius=0.02)
    _drop_shadow(card)
    _textbox(slide, X(0), Y(total - BP - 0.42), S(PW), S(0.4),
             spec.get("name", ""), size=pt(0.30), color=C["key_dark"],
             bold=True, align=PP_ALIGN.CENTER)

    y = total - BP - TH
    for L in layers:
        lh = layer_h(L)
        yb = y - lh
        _rect(slide, X(LX), Y(y), S(LXE - LX), S(lh),
              fill=C["tint"], line=C["key_deep"], lw=0.5, radius=0.03)
        _textbox(slide, X(LX), Y((y + yb) / 2 + 0.20), S(LBX + 0.55 - LX), S(0.42),
                 L["label"], size=pt(0.26), color=C["key_dark"], bold=True,
                 align=PP_ALIGN.CENTER)
        ct = y
        if L.get("note"):
            _textbox(slide, X(CX), Y(y - 0.05), S(CXE - CX), S(NH),
                     L["note"], size=pt(0.19), color=C["gray"], align=PP_ALIGN.CENTER)
            ct = y - NH
        cw = CXE - CX
        if "groups" in L:
            cols = L.get("cols") or len(L["groups"])
            gw = (cw - (cols - 1) * GGX) / cols
            mf = max(len(g[1]) for g in L["groups"])
            gh = GT + mf * FH + (mf - 1) * FG + GP
            for k, (gname, funcs) in enumerate(L["groups"]):
                row, col = divmod(k, cols)
                gx = CX + col * (gw + GGX)
                gy1 = ct - LP - row * (gh + RG)
                _rect(slide, X(gx), Y(gy1), S(gw), S(gh),
                      fill=C["white"], line=C["key_deep"], lw=0.4, radius=0.03)
                _textbox(slide, X(gx + 0.10), Y(gy1 - 0.04), S(gw - 0.2), S(0.22),
                         gname, size=pt(0.19), color=C["key_dark"], bold=True)
                for j, f in enumerate(funcs):
                    by = gy1 - GT - j * (FH + FG)
                    b = _rect(slide, X(gx + 0.20), Y(by), S(gw - 0.40), S(FH),
                              fill=C["white"], line=C["key_deep"], lw=0.5, radius=0.06)
                    _label(b, f, pt(0.21), C["dark"], bold=False)
        else:
            fs = L["funcs"]
            bw = (cw - (len(fs) - 1) * FGX) / len(fs)
            for k, f in enumerate(fs):
                txt, filled = (f if isinstance(f, tuple) else (f, False))
                bx = CX + k * (bw + FGX)
                b = _rect(slide, X(bx), Y(ct - LP), S(bw), S(FH),
                          fill=C["key_deep"] if filled else C["white"],
                          line=C["key_dark"] if filled else C["key_deep"],
                          lw=0.5, radius=0.06)
                _label(b, txt, pt(0.21),
                       C["white"] if filled else C["dark"], bold=False)
        y = yb - LG

    if band:
        bname, bfuncs = band
        bh = FH + 2 * LP
        _rect(slide, X(LX), Y(y), S(LXE - LX), S(bh),
              fill=RGBColor(0xF4, 0xF4, 0xF4), line=C["gray"], lw=0.5, radius=0.03)
        _textbox(slide, X(LX), Y((y + y - bh) / 2 + 0.16), S(LBX + 0.55 - LX), S(0.36),
                 bname, size=pt(0.24), color=C["gray"], bold=True, align=PP_ALIGN.CENTER)
        cw = CXE - CX
        bw = (cw - (len(bfuncs) - 1) * FGX) / len(bfuncs)
        for k, f in enumerate(bfuncs):
            b = _rect(slide, X(CX + k * (bw + FGX)), Y(y - LP), S(bw), S(FH),
                      fill=C["white"], line=C["gray"], lw=0.5, radius=0.06)
            _label(b, f, pt(0.21), C["dark"], bold=False)

    if ext:
        ex, exe = PW + GAP, PW + GAP + EW
        ey0, ey1 = 0.85, total - 0.85
        _rect(slide, X(ex), Y(ey1), S(EW), S(ey1 - ey0),
              fill=C["white"], line=C["gray"], lw=0.5, radius=0.03)
        _textbox(slide, X(ex), Y(ey1 - 0.20), S(EW), S(0.34), ext["name"],
                 size=pt(0.26), color=C["gray"], bold=True, align=PP_ALIGN.CENTER)
        items = ext["items"]
        top, bot = ey1 - 1.05, ey0 + 0.35
        step = (top - bot) / (len(items) - 1) if len(items) > 1 else 0
        for k, it in enumerate(items):
            cy = top - k * step
            b = _rect(slide, X(ex + 0.20), Y(cy + FH / 2), S(EW - 0.40), S(FH),
                      fill=C["white"], line=C["gray"], lw=0.5, radius=0.06)
            _label(b, it, pt(0.21), C["dark"], bold=False)
        # 셰브론 하나
        ax, axe, ay = PW + 0.03, ex - 0.03, total / 2
        arrow = slide.shapes.add_shape(
            MSO_SHAPE.LEFT_RIGHT_ARROW, Inches(X(ax)), Inches(Y(ay + 0.55)),
            Inches(S(axe - ax)), Inches(S(1.10)))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = RGBColor(0xB3, 0xF2, 0xE9)
        arrow.line.color.rgb = C["key_deep"]
        arrow.line.width = Pt(0.5)
        _no_shadow(arrow)
        if ext.get("link"):
            _textbox(slide, X(ax), Y(ay - 0.75), S(axe - ax), S(0.6), ext["link"],
                     size=pt(0.19), color=C["gray"], align=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════════════ Deck ══
class Deck:
    def __init__(self, title, subtitle="", author="", email="", date="",
                 institute="㈜바이야드", slidenote="", thanks="Thank you",
                 thanksnote=""):
        self.meta = dict(title=title, subtitle=subtitle, author=author, email=email,
                         date=date, institute=institute, slidenote=slidenote,
                         thanks=thanks, thanksnote=thanksnote)
        self.prs = Presentation()
        self.prs.slide_width = Inches(SW)
        self.prs.slide_height = Inches(SH)
        self._blank = self.prs.slide_layouts[6]
        self._chrome = []          # (slide, is_dark) — 페이지 번호를 마지막에 채운다
        _apply_theme(self.prs)

    # ---- 내부 ----------------------------------------------------------
    def _new(self, dark=False):
        s = self.prs.slides.add_slide(self._blank)
        if dark:
            bg = _rect(s, 0, 0, SW, SH, fill=RGBColor(0x04, 0x3A, 0x33))
            bg.shadow.inherit = False
        return s

    def _footer(self, s, dark=False):
        if os.path.exists(LOGO):
            s.shapes.add_picture(LOGO, Inches(MARGIN - 0.06), Inches(FOOT_Y - 0.02),
                                 height=Inches(0.20))
        tb = _textbox(s, SW - MARGIN - 1.6, FOOT_Y, 1.6, 0.22, "",
                      size=8, color=C["gray"], align=PP_ALIGN.RIGHT)
        self._chrome.append((len(self.prs.slides._sldIdLst), tb))

    # ---- 슬라이드 ------------------------------------------------------
    def cover(self):
        s = self._new(dark=True)
        m = self.meta
        _rect(s, 0, SH - 0.09, SW, 0.09, fill=C["key"])
        if os.path.exists(LOGO):
            s.shapes.add_picture(LOGO, Inches(SW - MARGIN - 1.55), Inches(0.45),
                                 height=Inches(0.30))
        _rect(s, MARGIN + 0.30, 2.55, 0.055, 1.05, fill=C["key"])
        _textbox(s, MARGIN + 0.55, 2.52, 10.2, 0.75, m["title"],
                 size=30, color=C["white"], bold=True)
        if m["subtitle"]:
            _textbox(s, MARGIN + 0.55, 3.34, 10.2, 0.40, m["subtitle"],
                     size=13, color=C["rule"])
        _textbox(s, MARGIN + 0.55, 4.55, 4.0, 0.28, "Date", size=8.5, color=C["key"])
        _textbox(s, MARGIN + 0.55, 4.78, 4.0, 0.28, m["date"], size=12,
                 color=C["white"], bold=True)
        _textbox(s, MARGIN + 4.55, 4.55, 5.0, 0.28, "Presenter", size=8.5, color=C["key"])
        _textbox(s, MARGIN + 4.55, 4.78, 5.0, 0.28,
                 f"{m['author']}   {m['institute']}", size=12, color=C["white"], bold=True)
        return Slide(self, s)

    def chapter(self, no, title, items=()):
        s = self._new(dark=True)
        _rect(s, 0, SH - 0.09, SW, 0.09, fill=C["key"])
        if os.path.exists(LOGO):
            s.shapes.add_picture(LOGO, Inches(SW - MARGIN - 1.55), Inches(0.45),
                                 height=Inches(0.30))
        _textbox(s, MARGIN + 0.55, 1.55, 4.0, 2.6, f"{no:02d}", size=110,
                 color=RGBColor(0x0A, 0x50, 0x47), bold=True)
        _rect(s, 3.95, 1.72, 0.055, 0.42, fill=C["key"])
        _textbox(s, 4.20, 1.68, 7.5, 0.50, title, size=22, color=C["white"], bold=True)
        y = 2.30
        for it in items:
            _textbox(s, 4.32, y, 0.14, 0.22, "▪", size=8, color=C["key"])
            _textbox(s, 4.50, y - 0.015, 7.0, 0.24, it, size=11, color=C["rule"])
            y += 0.26
        return Slide(self, s)

    def content(self, title, section="", sub=""):
        s = self._new()
        m = self.meta
        if m["slidenote"]:
            _textbox(s, MARGIN, HEAD_Y, 8.5, 0.22, m["slidenote"], size=8.5,
                     color=C["gray"])
        if sub:
            _textbox(s, MARGIN, SUBHEAD_Y, 6.0, 0.24, sub, size=9.5,
                     color=C["dark"], bold=True)
        if section:
            _textbox(s, SW - MARGIN - 4.0, SUBHEAD_Y, 4.0, 0.24, section, size=9.5,
                     color=C["ink"], bold=True, align=PP_ALIGN.RIGHT)
        band = _rect(s, 0, BAND_Y, SW, BAND_H, fill=C["key_deep"])
        _label(band, title, 19, C["white"], bold=True)
        for p in band.text_frame.paragraphs:
            for r in p.runs:
                if r.font.color.rgb == C["key_deep"]:
                    r.font.color.rgb = C["yellow"]
        self._footer(s)
        return Slide(self, s)

    def toc(self, sections):
        """Table of Contents — 2단, 번호 배지 + 하위 항목."""
        s = self._new()
        band = _rect(s, 0, BAND_Y, SW, BAND_H, fill=C["key_deep"])
        _label(band, "Table of Contents", 19, C["white"], bold=True)
        self._footer(s)
        half = (len(sections) + 1) // 2
        for col, chunk in enumerate((sections[:half], sections[half:])):
            x = MARGIN + 0.30 + col * (BODY_W / 2)
            y = BODY_TOP + 0.25
            for no, title, items in chunk:
                badge = _rect(s, x, y, 0.26, 0.26, fill=C["key_deep"], radius=0.12)
                _label(badge, str(no), 10, C["white"], bold=True)
                _textbox(s, x + 0.38, y - 0.01, 5.0, 0.28, title, size=13,
                         color=C["ink"], bold=True)
                y += 0.36
                for it in items:
                    _textbox(s, x + 0.44, y, 0.12, 0.20, "\u25aa", size=7,
                             color=C["key_deep"])
                    _textbox(s, x + 0.60, y - 0.015, 5.0, 0.22, it, size=10.5,
                             color=C["dark"])
                    y += 0.25
                y += 0.16
        return Slide(self, s)

    def thanks(self):
        s = self._new(dark=True)
        m = self.meta
        _rect(s, 0, SH - 0.09, SW, 0.09, fill=C["key"])
        _rect(s, MARGIN + 0.30, 3.15, 0.055, 0.75, fill=C["key"])
        _textbox(s, MARGIN + 0.55, 3.10, 10.0, 0.85, m["thanks"], size=34,
                 color=C["white"], bold=True)
        if m["thanksnote"]:
            _textbox(s, MARGIN + 0.55, 4.05, 9.0, 0.40, m["thanksnote"],
                     size=11, color=C["rule"])
        return Slide(self, s)

    def save(self, path):
        total = len(self.prs.slides._sldIdLst)
        for idx, tb in self._chrome:
            p = tb.text_frame.paragraphs[0]
            r = p.add_run(); r.text = str(idx)
            r.font.size = Pt(8); r.font.bold = True
            r.font.color.rgb = C["key_deep"]; r.font.name = FONT
            r2 = p.add_run(); r2.text = f" / {total}"
            r2.font.size = Pt(8); r2.font.color.rgb = C["gray"]; r2.font.name = FONT
        self.prs.save(path)
        return path


# ══════════════════════════════════════════════════════════════ 테마 ══
_THEME_COLORS = [("dk1", "062321"), ("lt1", "FFFFFF"), ("dk2", "262626"),
                 ("lt2", "E6FAF6"), ("accent1", "00806F"), ("accent2", "00DBBD"),
                 ("accent3", "005C50"), ("accent4", "ED7D31"), ("accent5", "C00000"),
                 ("accent6", "6E6E6E"), ("hlink", "00806F"), ("folHlink", "005C50")]


def _apply_theme(prs):
    """테마 색상 · 글꼴을 sty 팔레트로 교체한다."""
    from pptx.oxml.ns import qn
    theme = prs.slide_masters[0].part.part_related_by(
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme")
    root = theme._element if hasattr(theme, "_element") else None
    if root is None:
        from lxml import etree
        root = etree.fromstring(theme.blob)
    scheme = root.find(qn("a:themeElements"))
    if scheme is None:
        return
    clr = scheme.find(qn("a:clrScheme"))
    for name, hexv in _THEME_COLORS:
        node = clr.find(qn(f"a:{name}"))
        if node is None:
            continue
        for child in list(node):
            node.remove(child)
        from lxml import etree
        srgb = etree.SubElement(node, qn("a:srgbClr"))
        srgb.set("val", hexv)
    fonts = scheme.find(qn("a:fontScheme"))
    for tag in ("a:majorFont", "a:minorFont"):
        f = fonts.find(qn(tag))
        for sub in ("a:latin", "a:ea", "a:cs"):
            n = f.find(qn(sub))
            if n is not None:
                n.set("typeface", FONT if sub != "a:cs" else FONT)
    theme._blob = None
    try:
        from lxml import etree
        theme._element = root
        theme.blob = etree.tostring(root, xml_declaration=True,
                                    encoding="UTF-8", standalone=True)
    except Exception:
        pass

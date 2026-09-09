---
name: ppt-creator
description: 주제만 있는 상태에서 리서치 → 목차 합의 → org-beamer 작성 → pptx 생성까지 끝내는 발표자료 제작 스킬. "발표자료 만들어줘", "이 주제로 덱 만들어", "PPT 만들어줘", "제안 발표자료", "org를 ppt로", "pptx로 변환" 요청 시 사용. 레퍼런스를 웹에서 모아 $REF_BASE_DIR 에 정리하고, 이미지·다이어그램·수식·표 우선으로 내용을 전달하는 org-beamer 를 쓴 뒤 편집 가능한 pptx 로 뽑는다.
---

# 발표자료 제작

주제 → 레퍼런스 → 목차 → org-beamer → pptx. 7 단계이며 **phase 5(목차 승인)는 건너뛸 수 없다.**

## 진입 모드

| 상황 | 시작 지점 |
|---|---|
| 주제만 있음 | phase 0 부터 전부 |
| org 파일이 이미 있음 (변환만 요청) | phase 0 → phase 7 |
| 기존 덱 수정 | phase 4 (기존 org 의 목차부터 재합의) |

---

## Phase 0 — 경로 확정

```bash
echo "REF=${REF_BASE_DIR:-<unset>} DECK=${DECK_BASE_DIR:-<unset>}"
```

- `$REF_BASE_DIR` 가 비어 있으면 **사용자에게 묻고**, 답을 `~/.claude/settings.json` 의
  `env.REF_BASE_DIR` 에 기록한다(다음 세션부터 진짜 환경변수로 잡힌다). 기록 방법은
  `references/research.md` 의 "환경변수 기억" 참고.
- `$DECK_BASE_DIR` 기본값은 `~/data/devel/github.com/hackartists/notes/presentations`.
- 슬러그는 영문 kebab-case (`db-sto-02-offshore-rwa`). 산출물 위치:
  - 레퍼런스 `$REF_BASE_DIR/<slug>/`
  - 덱 `$DECK_BASE_DIR/<slug>/<slug>.org`, `make_pptx.py`, `<slug>.pptx`

## Phase 1 — 주제 구체화

AskUserQuestion 으로 묻는다. 자유 대화로 흘리지 말고 선택지를 준다.

| 항목 | 왜 필요한가 |
|---|---|
| 청중 | 용어 수준과 근거의 깊이를 결정 |
| 목적 (설득 / 보고 / 교육) | 프레임 순서와 결론 위치를 결정 |
| 발표 시간 | 장수 예산 = 분 × 0.8 ~ 1.2 |
| 언어 | 국문 / 영문 / 혼용 |
| 반드시 들어갈 내용 | 리서치가 놓치면 안 되는 축 |
| 제약 | 공개 불가 정보, 기존 덱 재사용 여부 |

답을 슬러그 + 한 문단 브리프로 정리해 사용자에게 되읽어 확인받고, 브리프는 org 상단
`# ` 주석으로 남긴다.

## Phase 2 — 레퍼런스 수집

`references/research.md` 를 따른다. 요약:

1. WebSearch 로 후보를 찾고 WebFetch 로 본문을 확인한다.
2. 실제 파일(pdf · pptx · ppt · docx)은 `scripts/refs.sh fetch` 로 `$REF_BASE_DIR/<slug>/` 에 받는다.
3. `scripts/refs.sh extract` 로 `extracted/<파일명>/` 에 본문 텍스트와 그림을 뽑는다.
4. `$REF_BASE_DIR/<slug>/index.org` 에 파일마다 출처 URL · 접근일 · 한 줄 요지 · 사용 프레임을 적는다.

수집 대상은 두 종류를 섞는다 — **발표자료**(pdf · pptx: 구성과 도해를 빌려온다)와
**기술 문헌**(논문 · 리포트 · 백서: 수치와 주장을 빌려온다).

## Phase 3 — 정독

`extracted/` 의 텍스트를 읽고 두 목록을 만든다.

- **근거 목록**: 수치, 주장, 날짜. 각각 어느 파일의 몇 쪽에서 왔는지.
- **그림 인벤토리**: `extracted/<파일>/img-*.png` 중 쓸 만한 것의 경로와 "무엇을 보여주는
  그림인지" 한 줄. phase 6 의 1순위 전달 수단이 여기서 나온다. 이 목록이 비면 이미지
  우선 원칙은 실행 불가능해지므로, 비었다면 phase 2 로 되돌아간다.

## Phase 4 — 목차(TOC) 작성

`$DECK_BASE_DIR/<slug>/<slug>.org` 를 `templates/deck.org` 로 만들고 **뼈대만** 채운다.

```org
* 개요
#+BEAMER: \subsection{문제 정의}
*** 시장은 왜 지금 움직이는가                    [img:extracted/mckinsey-rwa/img-004.png]
*** 규제 타임라인                                [tikz]
#+BEAMER: \subsection{기존 접근의 한계}
*** 세 가지 구조의 비용 비교                     [table]
```

- 2 depth 고정: `* 섹션` / `\subsection{}` / `*** 프레임 제목`.
- 프레임 제목 뒤 대괄호에 **전달 수단 예고**를 적는다 (`img:경로` · `tikz` · `formula` · `table`).
  phase 6 에서 이 예고를 지킨다.
- 장수는 phase 1 의 예산 안에서.

## Phase 5 — 목차 승인 (필수 게이트)

목차를 사용자에게 보여주고 승인받는다. 승인 전에 본문을 쓰지 않는다.
수정 요청이 오면 목차만 고쳐 다시 보여준다.

## Phase 6 — 본문 작성

`references/org-authoring.md` 의 프레임 패턴을 따른다. 규칙:

**전달 수단 우선순위** — 위에서 되는 것을 쓴다.

1. 레퍼런스에서 뽑은 이미지 (`[[file:...]]`)
2. tikz 로 그린 도해
3. 수식
4. 표 또는 block

**문장 규칙**

- 키워드 단위로 쓴다. 완결된 문장이 아니라 명사구.
- 한 프레임 = 한 메시지. 불릿 5 개를 넘기지 않는다.
- **`\hanote` 금지.** 각주로 판단 근거나 부연을 다는 것은 이 스킬에서 금지한다. 근거는
  본문 요소(표의 열, 도해의 라벨)로 흡수하거나 버린다.
- 출처 표기 없음. `\src{}` 도 `\printbibliography` 도 쓰지 않는다. 출처는 `index.org` 에만 남는다.

## Phase 7 — pptx 변환

`references/org-to-pptx.md` 를 따라 `$DECK_BASE_DIR/<slug>/make_pptx.py` 를 쓰고 빌드한다.
커맨드 전체 인자는 `references/commands.md`.

```bash
python3 <플러그인>/skills/ppt-creator/scripts/deck.py new spec.json --title "..."
# ... add-* 나열 ...
python3 .../deck.py build spec.json -o <slug>.pptx
```

**확인은 생략하지 않는다.**

```bash
soffice --headless --convert-to pdf --outdir /tmp <slug>.pptx
pdftoppm -png -r 110 /tmp/<slug>.pdf /tmp/pg
```

생성된 png 를 실제로 읽어 본다. 넘침 · 겹침 · 잘린 글씨가 있으면 고치고 다시 빌드한다.

## 산출물

```
$REF_BASE_DIR/<slug>/          index.org, 원본 파일, extracted/
$DECK_BASE_DIR/<slug>/         <slug>.org, make_pptx.py, <slug>.pptx
```

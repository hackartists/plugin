# org → pptx 변환 (phase 7 상세)

`../scripts/deck.py` 커맨드를 나열해 JSON 스펙을 쌓고, `build` 로 pptx 를 만든다.
pptx 를 직접 열고 닫지 않으므로 **같은 커맨드 나열이면 항상 같은 pptx** 가 나온다.

## 워크플로

1. **org 를 읽고 프레임 단위로 쪼갠다.** `*` 섹션 → `add-chapter`, `***` 프레임 → `add-page`.
2. **프레임 안의 요소를 커맨드로 옮긴다.** 아래 매핑표를 따른다.
3. **빌드 스크립트를 한 파일(`make_pptx.sh`)로 저장한다.** 원본 org 가 바뀌면 해당 줄만 고치면 된다.
4. **`build` 후 반드시 눈으로 확인한다.** LibreOffice 로 pdf 변환 → `pdftoppm` → 이미지 확인.

## org 요소 → 커맨드 매핑

| org / LaTeX | 커맨드 |
|---|---|
| `* 섹션` | `add-chapter` |
| `*** 프레임 제목` | `add-page` |
| `#+ATTR_LATEX: :environment hatable` 표 | `add-table` |
| `:BMCOL:` 다단 | `add-column` |
| `\begin{fnarch}` | `add-functional-architecture` |
| `\begin{asistobe}` | `add-asis-tobe` |
| `\hanote{...}` | `add-note` 또는 `add-page --note` |
| `\hacallout{...}` | `add-callout` 또는 `add-page --callout` |
| `[[file:...]]` | `add-image` |
| 그 외 tikzpicture | 아래 "직접 그리는 도해" 참고 |

## 마크업 변환

| org | 커맨드 인자 |
|---|---|
| `*굵게*` | `*굵게*` (그대로) |
| `\haemph{...}` | `!강조!` |
| `\hakey{...}` | `*굵게*` |
| `\newline` | `\n` |

## 표 인자 형식

```
--header "구분|해외 SPV|DB증권"      # | 로 열 구분
--row "법적 지위|*발행 주체*|공급자"  # 행마다 --row 반복
--widths "1.5,4.0,4.0"              # 열 비율 (합이 12.33 에 맞춰 자동 스케일)
--row-h 0.60                         # 행 높이(인치). 줄바꿈 많으면 키운다
```

첫 열은 자동으로 라벨 스타일(키컬러 배경 + 흰 글씨)이 된다.

## 직접 그리는 도해

`add-*` 로 안 되는 일회성 tikz 도해는 `biyard_pptx.Canvas` 를 쓰는 파이썬을
따로 쓴다. **TikZ 좌표를 그대로 옮길 수 있다** — y 가 위로 증가하고, 논리 크기를
주면 슬라이드에 비율 유지로 맞춰 넣는다.

```python
cv = s.canvas(xmax=15.6, ymax=6.9, xmin=-1.2, ymin=-1.0)
cv.box(1.6, 6.35, 3.6, 0.95, "제주 우량 기초자산", fill=C["white"], line=C["gray"])
cv.arrow((1.6, 5.87), (1.6, 5.03))
cv.path([(1.6, 4.07), (1.6, 3.10), (7.7, 3.10), (7.7, 2.72)])   # 꺾은선
cv.text(4.5, 2.72, "원화 배당 → USD 송금", size=0.17, w=3.4)
cv.blockarrow(6.6, 3.0, 1.15, 0.62)                              # 셰브론
```

`size` 는 cm 단위 글자 높이로 준다(0.17~0.26 이 tiny~scriptsize 에 해당).

## 확인 (생략하지 말 것)

```bash
soffice --headless --convert-to pdf --outdir /tmp out.pptx
pdftoppm -png -r 110 /tmp/out.pdf /tmp/pg
```

자주 나오는 문제:
- **note 와 마지막 요소가 겹침** — note 는 바닥 고정이다. 위 요소 높이를 줄이거나 `--note` 대신 `add-note` 를 마지막에 붙인다.
- **표가 세로로 넘침** — `--row-h` 를 줄이거나 `--size` 를 낮춘다.
- **도해 글씨가 작음** — canvas 의 논리 크기(xmax/ymax)를 줄여 스케일을 키운다.

## 폰트

테마 글꼴은 Pretendard. 받는 쪽 PC 에 없으면 대체된다. 상대가 Windows 환경이면
`../scripts/biyard_pptx.py` 의 `FONT` 를 `"맑은 고딕"` 으로 바꾸거나 폰트 파일을
함께 전달한다.

## 참고

- 커맨드 전체 레퍼런스: `references/commands.md`
- 실제 사용 예: `$DECK_BASE_DIR/db-sto-02-offshore-rwa/make_pptx.py` (25장)

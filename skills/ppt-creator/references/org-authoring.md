# org-beamer 본문 작성

## 전달 수단 결정

프레임마다 이 순서로 내려가며 **처음 가능한 것**을 쓴다. 아래로 내려갈수록 정보 밀도가 떨어진다.

| 순위 | 수단 | 쓰는 경우 | 쓰지 않는 경우 |
|---|---|---|---|
| 1 | 레퍼런스 추출 이미지 | 그림 인벤토리에 이 프레임 메시지를 그대로 보여주는 그림이 있다 | 해상도 200px 미만, 다른 문서 로고가 박혀 있음 |
| 2 | tikz 도해 | 구조 · 흐름 · 비교처럼 **관계**가 메시지다 | 관계가 단순 나열이면 표가 낫다 |
| 3 | 수식 | 정량 관계 · 산정식 · 임계값이 메시지다 | 청중이 비전문가면 결과값만 |
| 4 | 표 / block | 항목 × 속성 격자다 | 열이 2 개 이하면 그냥 불릿 |

## 프레임 뼈대

```org
* I. 시장 진단
#+BEAMER: \subsection{규모와 속도}
*** 토큰화 채권, 3 년간 6 배
<본문 요소 하나>
```

`*` 섹션, `\subsection{}`, `***` 프레임. 프레임 제목은 **주장**을 담은 명사구로 쓴다 —
"시장 현황"이 아니라 "토큰화 채권, 3 년간 6 배".

## 1. 이미지

```org
#+ATTR_LATEX: :width 0.82\textwidth :center t
[[file:img/valuechain.png]]
```

레퍼런스에서 뽑은 파일은 `$DECK_BASE_DIR/<slug>/img/` 로 복사해 두고 상대경로로 건다.
`$REF_BASE_DIR` 를 직접 가리키면 덱만 옮겼을 때 깨진다.

## 2. tikz 도해

```org
#+BEGIN_EXPORT latex
\begin{center}
\begin{tikzpicture}[
  node distance=8mm,
  box/.style={draw=ha-rule, fill=white, rounded corners=1pt,
              minimum height=7mm, inner xsep=4pt, font=\scriptsize},
  fill/.style={box, fill=ha-fill, text=ha-onfill},
  arr/.style={-{Latex[length=1.6mm]}, draw=ha-key-deep}]
  \node[fill] (a) {기초자산};
  \node[box, right=of a] (b) {신탁 수익권};
  \node[box, right=of b] (c) {온체인 토큰};
  \draw[arr] (a) -- (b);
  \draw[arr] (b) -- (c);
\end{tikzpicture}
\end{center}
#+END_EXPORT
```

색은 스타일이 정의한 것만 쓴다: `ha-key`, `ha-key-deep`, `ha-fill`, `ha-onfill`,
`ha-rule`, `ha-tint`, `ha-gray`, `ha-green`, `ha-amber`, `ha-red`.
라이브러리는 템플릿이 `fit,arrows.meta,positioning,calc` 를 이미 로드한다.

전용 환경이 있는 두 도해는 tikz 를 직접 쓰지 말고 이것을 쓴다.

**AS-IS / TO-BE**

```org
#+BEGIN_EXPORT latex
\begin{asistobe}
\asis{직접 발행 리스크를 지는}{국내 하이브리드 구조}
\tobe{지분 0\%의 해외 주관사가 발행하는}{역외 언더라이터 구조}
\anchor{발행 리스크}
  {\habul Issuer 로 나서면 발행 · 유통 규제 전량 부담}
  {\habul 해외 SPV 가 독점 부담}
\end{asistobe}
#+END_EXPORT
```

**기능 아키텍처**

```org
#+BEGIN_EXPORT latex
\begin{fnarch}[0.70]
  \platform{
    \name{플랫폼}
    \layer{응용\\서비스}{\note{액터별 앱}\func*{투자자 앱}\func{어드민}}
    \layer[4]{코어 엔진}{\vgroup{컴플라이언스}{\func{KYC · AML}\func{룰 엔진}}}
    \band{보안 · 관리}{\func{권한 · 인증}\func{보안 · 감사}}
  }
  \external{\name{외부 연계}\link{REST · SDK}\ext{신탁사}\ext{Sumsub}}
\end{fnarch}
#+END_EXPORT
```

`\func*` = 채운 박스(남의 것), `\func` = 흰 박스(우리 것). `\layer[n]` 의 n 은 행당 그룹 수.

## 3. 수식

```org
#+BEGIN_EXPORT latex
\[ \text{연 수취액} = \underbrace{L \times 12}_{\text{라이선스}}
   + \underbrace{V \times r}_{\text{유통 수수료}} \qquad r = 0.15\% \]
#+END_EXPORT
```

`\underbrace` 로 항마다 이름을 붙이면 수식 자체가 설명이 된다 — 아래에 문장을 덧붙이지 않는다.

## 4. 표 · 다단 · block

**표**

```org
#+ATTR_LATEX: :environment hatable :align L{1.5cm} L{4.2cm} L{4.2cm} :center t
| \hahead{구분}       | \hahead{해외 SPV}          | \hahead{DB증권}              |
|---------------------+----------------------------+------------------------------|
| \halabel{법적 지위} | *정식 발행 주체*           | B2B 솔루션 공급자            |
| \halabel{온체인}    | 발행 · 배당 집행           | \haemph{접점 없음}           |
```

`L{}` 폭의 합이 `\textwidth`(약 16cm) 를 넘지 않게. 셀 줄바꿈은 `\newline`.

**다단**

```org
**** 좌                                                              :BMCOL:
:PROPERTIES:
:BEAMER_col: 0.32
:BEAMER_OPT: t
:END:
***** ① 국내 신탁사 — 리스크 0의 수수료원
+ 신규 수익원 가뭄 — PF 침체
+ \hakey{블록체인 리스크 0\%}
```

`:BEAMER_col:` 합이 0.98 을 넘으면 넘친다.

## 결론 상자 · 표제 프레임

스타일이 주는 환경이다. `#+LATEX:` 로 감싸지 말고 org 블록으로 쓴다 — 본문이 org 로
남아야 안의 마크업이 살아난다.

**callout** — 프레임의 결론 한 줄. 프레임당 최대 1 개, 설명 문단 금지.

```org
#+ATTR_LATEX: :options [-0.2em]
#+BEGIN_callout
네 칸 중 하나라도 못 채우면 *그 칸이 바로 오늘 물어야 할 질문* 입니다. \calloutnote
틀렸을 때 무너지는 것부터 검증합니다.
#+END_callout
```

`:options [...]` 는 상자 위 추가 여백(환경 자체 여백에 더해진다, 기본 `0em`). 둘째 줄은
`\calloutnote` 로 넘긴다 — org 본문에서 `\\[0.2em]` 는 `$\backslash$\[0.2em]` 로 깨진다.

**slogan** — 프레임 하나를 문장 하나로 채울 때. 세로 중앙 정렬, 기본 `\Large`.

```org
#+BEGIN_slogan
AI 가 *왜 필요* 한가?
#+END_slogan
```

크기는 `#+ATTR_LATEX: :options [\huge]` 로 바꾼다.

## 강조 · 마크업

org 마크업으로 쓴다. 템플릿의 `#+BIND: org-latex-text-markup-alist` 가 inline code 를
`\hakey{}` 로 내보내고, ox-beamer 가 굵게를 `\alert{}` 로 내보낸다. `\alert{}` 는
스타일에서 빨강 굵게이므로 `\haemph{}` 와 결과가 같고, 프레임 타이틀 · block 안에서는
바탕색에 맞춰 자동으로 색이 바뀐다.

| 표기 | 결과 | 쓰임 |
|---|---|---|
| `=핵심 개념=` | `\hakey{}` | 키컬러 — 이 프레임이 남길 한 단어 |
| `*강조*` | `\alert{}` | 빨강 굵게 — 경고 · 부정 · 대비 |
| `\haok` `\hacond` `\hatbd` | 배지 | 가능 / 조건부 / 미확정 |
| `\habul` | 불릿 | tikz · 환경 인자 안에서 |

`\hakey{}` `\haemph{}` 를 직접 쓰는 자리는 org 마크업이 파싱되지 않는 곳뿐이다 —
`#+LATEX:` 줄, `#+BEGIN_EXPORT latex` 블록, tikz 노드 라벨.

**중첩하지 않는다.** `=...=` 안은 verbatim 이라 다른 마크업이 안 먹는다. 매크로도
`\hakey{... \haemph{...} ...}` 처럼 겹치면 org 가 중첩 중괄호를 latex fragment 로
인식하지 못해 `\{` `\}` 로 이스케이프해 버린다. 겹치지 말고 나란히 쓴다.

`%` `&` `_` `#` 는 `\` 로 이스케이프한다. 특히 `0\%`. 단 org 본문에서는 org 가 알아서
이스케이프하므로 `76%` 로 쓴다 — `\%` 는 `#+LATEX:` 줄과 export 블록에서만.

`=...=` 는 앞뒤가 공백이거나 줄 시작/끝이어야 파싱된다. 줄표 바로 뒤(`—=핵심=`)는 안 먹는다.

## 금지

- **`\hanote{}` 금지.** 판단 근거 · 부연 · 단서를 각주로 다는 행위 전부. 근거는 표의 열이나
  도해 라벨로 흡수하고, 흡수되지 않으면 버린다.
- **출처 표기 금지.** `\src{}`, `\printbibliography`, "출처: ..." 모두 쓰지 않는다.
- **완결 문장 금지.** "~할 필요가 있다", "~로 판단된다" 대신 명사구로 끊는다.
- 프레임당 불릿 5 개 초과 금지. 넘으면 프레임을 쪼개거나 표로 바꾼다.
- 같은 수단을 3 프레임 연속 금지 — 표만 이어지면 덱이 읽히지 않는다.
- `\hacallout{}` `\footbox{}` 같은 덱 로컬 매크로 정의 금지. 상자는 `callout` 환경을 쓴다.

## 자체 점검

본문을 다 쓰면 확인한다.

```bash
grep -n 'hanote\|\\src{\|printbibliography' <slug>.org   # 아무것도 안 나와야 한다
grep -c '^\*\*\* ' <slug>.org                            # 프레임 수 = 장수 예산 안
grep -n '\\hakey{\|\\haemph{' <slug>.org | grep -v '#+LATEX:\|#+BIND:'   # 남으면 =...= / *...* 로
```

export 한 tex 도 본다. 중첩 중괄호가 깨졌으면 여기서 잡힌다.

```bash
grep -n '\\{\|[$]\\backslash[$]' <slug>.tex          # 아무것도 안 나와야 한다
```

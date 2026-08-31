# deck.py 커맨드 레퍼런스

모든 커맨드의 첫 인자는 스펙 파일 경로다. 요소 커맨드는 **직전 `add-page`** 에 붙는다.

## new
```
deck.py new spec.json --title T [--subtitle S] [--author A] [--email E]
                      [--date D] [--institute I] [--slidenote N]
                      [--thanks T] [--thanksnote TN] [--no-cover]
```
표지를 포함해 덱을 만든다. `--slidenote` 는 모든 본문 페이지 좌상단에 들어가는 한 줄.

## add-toc
```
deck.py add-toc spec.json --entry "1|개요|전략 전환;역할과 수익" --entry "2|..."
```
`번호|제목|하위항목;하위항목`. 2단으로 자동 분배된다.

## add-chapter
```
deck.py add-chapter spec.json --no 1 --title 개요 --items "전략 전환;역할과 수익"
```

## add-page
```
deck.py add-page spec.json --title T [--section "I. 개요"] [--sub "역할과 수익"]
                           [--note ...] [--callout ...]
```
`--section` 은 우상단, `--sub` 은 좌상단에 들어간다.

## add-table
```
deck.py add-table spec.json --header "A|B|C" --row "a|b|c" --row "d|e|f"
                            --widths "1.5,4,4" [--row-h 0.6] [--size 9]
```
`--header` 생략 가능. 첫 열은 라벨 스타일. 셀 안 줄바꿈은 `\n`.

## add-column
```
deck.py add-column spec.json --ratios "1,1,1" \
  --col "① 국내 신탁사::리스크 0;;신규 수수료원" \
  --col "② 해외 운용사::메인 수익 독식"
```
`소제목::불릿;;불릿`. `--ratios` 생략 시 균등 분할.

## add-functional-architecture
```
deck.py add-functional-architecture spec.json --arch arch.json
```
`--arch` 는 JSON 문자열 또는 파일 경로. 구조:
```json
{
  "name": "RWA/STO SaaS 플랫폼",
  "layers": [
    {"label": "응용\n서비스", "note": "액터별 앱",
     "funcs": [["투자자 앱", true], ["플랫폼 어드민", false]]},
    {"label": "코어 엔진", "cols": 4,
     "groups": [["컴플라이언스", ["KYC · AML", "관할 룰 엔진"]]]}
  ],
  "band": ["보안 · 관리", ["권한 · 인증", "보안 · 감사"]],
  "external": {"name": "외부 연계", "link": "REST · 벤더 SDK",
               "items": ["국내 신탁사", "Sumsub"]}
}
```
- `funcs` 의 `true` = 채운 박스(남의 것: 테넌트·체인), `false` = 흰 박스(우리 것)
- `cols` = 행당 그룹 수. 레이어 높이·그룹 폭·박스 등분은 모두 자동
- `band` = 전 계층을 가로지르는 관심사 한 줄
- `layers` 에 `groups` 대신 `funcs` 를 주면 가로 한 줄로 배치된다

## add-asis-tobe
```
deck.py add-asis-tobe spec.json \
  --asis "직접 발행 리스크를 지는\n국내 하이브리드 구조" \
  --tobe "지분 0% 해외 주관사가 발행하는\n역외 언더라이터 구조" \
  --row "발행 리스크 이전|Issuer 로 나서면 전량 부담|해외 SPV 가 독점 부담"
```

## add-image / add-note / add-callout / add-thanks
```
deck.py add-image   spec.json --path fig.png [--width 8] [--height 4]
deck.py add-note    spec.json --text "..."
deck.py add-callout spec.json --text "..."
deck.py add-thanks  spec.json
```

## build
```
deck.py build spec.json -o out.pptx
```
`-o` 생략 시 스펙 파일명 기준.

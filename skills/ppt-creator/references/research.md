# 레퍼런스 수집 · 정리

## 환경변수 기억

`$REF_BASE_DIR` 가 비어 있으면 사용자에게 한 번 묻고, 답을 `~/.claude/settings.json` 의
`env` 에 병합한다. 파일을 통째로 덮어쓰지 말 것 — 기존 키가 날아간다.

```bash
python3 - "$ANSWER" <<'EOF'
import json, os, sys, pathlib
p = pathlib.Path.home() / ".claude" / "settings.json"
cfg = json.loads(p.read_text()) if p.exists() else {}
cfg.setdefault("env", {})["REF_BASE_DIR"] = os.path.expanduser(sys.argv[1])
p.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")
EOF
```

기록해도 **현재 세션의 환경변수는 바뀌지 않는다.** 이번 실행에서는 사용자가 답한 경로를
그대로 쓰고, 다음 세션부터 `$REF_BASE_DIR` 로 잡힌다고 알려 준다.

`$DECK_BASE_DIR` 도 사용자가 기본값과 다른 곳을 원하면 같은 방식으로 기록한다.

## 무엇을 모으는가

| 종류 | 형식 | 무엇을 얻나 |
|---|---|---|
| 발표자료 | pdf · pptx · ppt | 구성 순서, 도해, 그림 |
| 기술 문헌 | 논문 · 리포트 · 백서 (pdf · docx) | 수치, 정의, 주장 |
| 웹 문서 | 공식 문서 · 블로그 | 최신 상태 확인 |

검색은 주제어 + `filetype:pdf`, `"deck"`, `"slides"`, `"white paper"`, `"annual report"`
같은 한정어를 섞어 **4~8 건**을 목표로 한다. 1 차 출처(기관 · 표준 · 원 논문)를 2 차 인용보다
우선한다.

## 받기

```bash
scripts/refs.sh fetch "$REF_BASE_DIR/<slug>" "<url>" [파일명]
```

- 파일명 생략 시 URL 에서 유추한다.
- 로그인·결제가 걸린 자료는 받지 않는다. 사용자에게 파일을 달라고 요청하거나 대체 자료를 찾는다.
- 받은 뒤 `file <경로>` 로 실제 형식을 확인한다. HTML 오류 페이지가 pdf 이름으로 저장되는 일이 잦다.

## 뽑기

```bash
scripts/refs.sh extract "$REF_BASE_DIR/<slug>/<파일>"
```

결과는 `extracted/<파일명(확장자 제외)>/` 아래에 놓인다.

| 입력 | 텍스트 | 그림 |
|---|---|---|
| pdf | `text.txt` (`pdftotext -layout`) | `img-*.png` (`pdfimages -png`), 페이지 통짜는 `page-*.png` (`pdftoppm`) |
| pptx · docx | `text.txt` (XML 에서 추출) | `img-*` (`unzip` 의 `ppt/media`, `word/media`) |

작은 아이콘·로고가 `img-*` 에 섞여 나온다. 200×200 px 미만은 후보에서 뺀다.
도해가 벡터라 `pdfimages` 로 안 나오면 `page-*.png` 에서 해당 쪽을 잘라 쓴다.

## 정리 — index.org

`$REF_BASE_DIR/<slug>/index.org` 는 이 스킬이 다음 실행에서 다시 읽는 유일한 요약이다.

```org
#+TITLE: <slug> 레퍼런스
#+DATE: 2026-09-10

| 파일 | 출처 | 접근일 | 요지 | 사용 |
|---+---+---+---+---|
| bis-rwa-2026.pdf | https://bis.org/publ/... | 2026-09-10 | 토큰화 채권 발행 규모 3 년 추이 | 2-1 시장 규모 |
| mckinsey-rwa.pdf | https://mckinsey.com/... | 2026-09-10 | 밸류체인 6 단계 도해 | 3-2 구조 |

* 그림 인벤토리
- extracted/mckinsey-rwa/img-004.png :: 발행-유통-수탁 밸류체인 (가로 6 단계)
- extracted/bis-rwa-2026/page-012.png :: 지역별 발행 규모 막대그래프

* 근거
- 토큰화 채권 발행액 2025 년 $18.3B :: bis-rwa-2026.pdf p.12
```

"사용" 열은 phase 6 을 마친 뒤 채운다. 비워 둔 항목은 다음 덱에서 재활용할 후보다.

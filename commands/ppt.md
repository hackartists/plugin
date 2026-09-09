---
description: 주제 리서치부터 org-beamer 작성, pptx 변환까지 발표자료를 만든다. org 파일이 이미 있으면 변환만 수행
argument-hint: "[발표 주제 — 또는 변환할 .org 경로. 생략 가능]"
---

Invoke the `ppt-creator` skill and follow it exactly.

목표: 곧바로 슬라이드를 쓰지 말고 skill 의 7 단계를 따른다 — (0) `$REF_BASE_DIR` · `$DECK_BASE_DIR` 확정 → (1) `AskUserQuestion` 으로 청중·목적·시간·언어 구체화 → (2) 웹에서 레퍼런스 수집 후 `$REF_BASE_DIR/<slug>/` 에 정리 → (3) 정독하고 근거 목록·그림 인벤토리 작성 → (4) 2 depth 목차 작성 → (5) **사용자 승인 게이트** → (6) 이미지 > tikz > 수식 > 표 우선순위로 본문 작성 → (7) pptx 변환 후 pdf 렌더로 눈으로 확인.

인자가 `.org` 파일 경로면 phase 0 → phase 7 만 수행한다.

사용자 요청: $ARGUMENTS

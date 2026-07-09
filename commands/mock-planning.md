---
description: mock 만들기 전 요구사항을 구체화한 뒤(페이지 추가/수정 분기, 근거 기반 선택지) 프로젝트 프레임워크로 mock 개발
argument-hint: "[무엇을 mock 할지 간단히 — 생략 가능]"
---

Invoke the `mock-planning` skill and follow it exactly.

목표: mock 을 곧바로 만들지 말고, skill 의 절차대로 (1) 코드베이스 탐색으로 후보 근거 확보 → (2) 페이지 추가/수정 분기 → (3) `AskUserQuestion` 으로 근거 기반 선택지를 제시하며 요구사항 구체화 → (4) 스펙 확정 → (5) 탐지된 프론트엔드 프레임워크로 mock 개발.

사용자 요청: $ARGUMENTS

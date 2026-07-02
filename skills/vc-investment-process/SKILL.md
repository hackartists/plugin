---
name: vc-investment-process
description: Use when planning (기획) or designing a feature for a VC/투자 도메인 제품, before writing the spec/requirements — or whenever a 기획 주제는 정해졌지만 실제 VC 업무의 어느 단계에 해당하고 어떤 전문지식이 필요한지 아직 불명확할 때. Also use when auditing VC terminology (용어 감수/체크) in specs, UI copy, or i18n files. Covers the full VC investment lifecycle: 펀드결성, LP모집, 딜소싱, 심사/DD, 투심위/텀시트, 계약, 사후관리/Exit. Triggers: 기능 도출, feature-discovery, 신규 기획 시작, "이 기능이 어떤 투자 프로세스랑 관련 있어?", "무슨 전문지식이 필요해?", "용어가 맞는지 체크해줘", 데이터룸/실사/DD/텀시트/투심위/IC/포트폴리오/사후관리/엑싯/펀드결성/LP 관련 기획.
---

# VC Investment Process

## Overview

VC(벤처캐피탈) 운용사의 실제 업무는 **7단계**로 나뉜다 — 펀드를 만드는 **펀드 레이어**(2단계)와 개별 딜을 굴리는 **딜 레이어**(5단계). 이 스킬은 기획 주제 하나를 받아서 (1) 그게 이 7단계 중 어디에 해당하는지 **관련 프로세스를 도출**하고, (2) 그 단계를 제대로 설계하는 데 필요한 용어·체크리스트·산출물·의사결정 포인트·규제 같은 **전문지식을 도출**한다.

**언제 쓰나**: 기획을 시작해서 스펙(Problem/Goal/요구사항)을 쓰기 **전에**. 기획 주제가 모호하거나 UI 아이디어부터 떠올랐을 때 특히 유용 — 실제 VC 워크플로우 어디에 꽂히는 기능인지 먼저 확인하고 설계한다.

## The 7-Stage Lifecycle

| # | Stage | Layer | 핵심 산출물 | Reference |
|---|-------|-------|------------|-----------|
| 1 | 펀드 결성 (Fund Formation) | 펀드 | 정관/LPA, 펀드 개요·투자전략, 보수구조 | `references/01-fund-formation-and-lp.md` |
| 2 | LP 모집 (LP Fundraising) | 펀드 | PPM, 약정서(Subscription), 결성 현황 | `references/01-fund-formation-and-lp.md` |
| 3 | 딜 소싱 (Deal Sourcing) | 딜 | 딜 파이프라인, IR덱/제안, 초기 핏 필터 | `references/02-deal-sourcing.md` |
| 4 | 심사 (Screening & Due Diligence) | 딜 | 데이터룸, DD 체크리스트, 밸류에이션 | `references/03-screening-and-due-diligence.md` |
| 5 | 투심위 → 의사결정 (IC & Decision) | 딜 | IC/딜퀄리피케이션 메모, 텀시트 | `references/04-ic-and-decision.md` |
| 6 | 계약 (Closing) | 딜 | 텀시트/SPA/SHA, 전자서명, 감사추적 | `references/05-closing-and-contract.md` |
| 7 | 사후관리 (Post-Investment) | 딜 | KPI 리포트, 후속투자, Exit | `references/06-post-investment-and-exit.md` |

전체 용어집(14개 카테고리, 한/영 대역·한국 규제 포함)은 `references/07-glossary-and-kr-regulatory.md`. **제품 내 용어 감수(spec/UI 카피/i18n 체크)** 는 혼동 쌍 표 + grep 스니펫이 있는 `references/08-terminology-audit-checklist.md`를 따른다.

## GP 업무의 중요도·시간 분포 (기획 우선순위 판단용)

GP 설문 연구(Gompers·Gornall·Kaplan·Strebulaev, ~900명)와 실무 통념 기준으로, **가장 중요한 파트와 가장 시간을 쓰는 파트가 서로 다르다**:

- **성과를 결정하는 것(중요)**: 딜 선별(소싱+picking, Stage 3~5). VC 수익은 멱법칙이라 한두 개 홈런 딜이 펀드 성과를 결정하고, GP들도 가치 창출 1순위로 deal selection을 꼽는다(사후 밸류애드보다 위). 존속 관점에선 펀드 결성(Stage 1~2)이 전제조건이나 2~4년 주기 이벤트.
- **시간을 잡아먹는 것**: 사후관리(Stage 7, 포트폴리오 개수 × 7~10년 누적)와 소싱 퍼널(Stage 3, 약 100:1 스크리닝). DD(Stage 4)는 건당 강도는 높지만 에피소드성.
- **기획 시사점**: 시간 소모 파트(스크리닝 triage·DD 자료 수집·KPI 리포팅)는 자동화 가치가, 판단 파트(선별·투심)는 의사결정 지원 가치가 크다. 기능이 어느 쪽을 치는지 먼저 분류하라.

## How to Use

1. **기획 주제를 한 문장으로 요약한다** (예: "동종업계 PER 비교 대시보드", "DD 체크리스트 자동 생성", "펀드별 포트폴리오 KPI 트래커").
2. **표에서 스테이지를 매칭한다.** 하나의 기능이 2개 스테이지에 걸칠 수 있다 — 예: "데이터룸 접근 제어"는 심사(4)와 계약(6) 양쪽에 영향을 준다. 애매하면 여러 개를 고른다.
3. **매칭된 `references/*.md`를 읽는다.** 스테이지 정의, 세부 단계, 산출물, 용어, **설계 체크포인트**를 확인한다.
4. **두 섹션으로 정리해 스펙(Problem/Goal/요구사항) 작성 근거로 쓴다:**
   - **관련 프로세스** — 어느 스테이지 + 세부 단계와 맞닿아 있는지
   - **필요 전문지식** — 그 단계의 용어/체크리스트/의사결정 포인트 중 이 기능 설계에 실제로 영향을 주는 것만
5. 작업 중인 제품에 그 스테이지를 다루는 기존 기능이 이미 있으면 **그 기능의 용어·산출물·분류 코드를 재사용**한다 — 새로 발명하지 않는다. 없으면(gap) 그 사실 자체가 기획 기회다.

## Common Mistakes

- 프로세스 단계를 확인하지 않고 UI부터 그리기 시작 → 실제 VC 워크플로우와 어긋난 기능이 나온다.
- 심사(DD)와 계약(Closing) 단계의 문서·공개 범위 요건을 혼동 — DD는 단계적 공개(staged disclosure)가 핵심, 계약은 서명 감사추적이 핵심.
- 용어 오용 — 텀시트(비구속)와 정의계약(SPA/SHA, 구속)을 같은 것처럼 씀, pre-money와 post-money를 혼동, 펀드의 GP 출자와 LP 출자를 혼동.
- 제품에 이미 있는 용어·분류 체계와 겹치는 것을 새로 발명함 — 기획 전에 제품의 기존 용어 체계를 먼저 훑는다.

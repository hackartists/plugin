# Stage 4: 심사 (Screening & Due Diligence)

**Layer**: 딜 — 데이터룸·실사 도구가 집중되는 스테이지.
**키워드**: 심사, 실사, DD, due diligence, 데이터룸, 데이터셋, 체크리스트, 밸류에이션, 가치평가, 팀평가, ESG, 리스크, 트랙션, 팩트체크, 폴더분류.

## 개요

한국 VC 실무에서 "심사"는 좁은 의미의 스크리닝(1차 필터)과 본실사(due diligence)를 함께 가리키는 경우가 많다. 이 레퍼런스는 그 전체 — 사업계획서 리뷰부터 팀 IR 미팅, 3단계 실사까지 — 를 다룬다.

### 스크리닝 (1차)

- 사업계획서/IR덱 리뷰, 심사역 대상 IR 미팅, 초기 팀·시장·핏 평가.
- 여기서 통과한 소수만 아래의 상세 실사(2·3단계)로 넘어간다.

### 3단계 실사 (Due Diligence)

1. **비즈니스 실사** — 팀, 시장, 제품/기술, 트랙션(고객/매출/리텐션), 경쟁 구도.
2. **재무 실사** — 재무제표, 세금 신고, 캡테이블, 현금흐름/번레이트, 매출 인식 방식.
3. **법률 실사** — 정관, 지분 구조, 주요 계약, IP(특허/상표), 소송/분쟁, 규제 컴플라이언스, 근로계약.

### 9개 실사 영역 체크리스트

Finance · Tax · Legal · HR · Assets · IT · Product/Services · Marketing & Sales · Founder background. 좋은 DD 체크리스트는 이 9개 영역을 빠짐없이 커버한다.

### 단계적 공개 (Staged Disclosure)

데이터룸은 실사 진행도에 따라 공개 범위를 넓힌다 — 이 제품의 접근 권한 모델과 직결되는 핵심 개념:

- **Level 1 (관심 단계)** — 피치덱, 요약 재무, 제품 개요.
- **Level 2 (본실사 단계)** — 전체 재무제표, 캡테이블, 주요 계약, IP 포트폴리오.
- **Level 3 (텀시트 이후)** — 근로계약, 세무 상세, 컴플라이언스 세부 문서.

### 밸류에이션 방법론

- **DCF(현금흐름할인)** — 미래 잉여현금흐름을 WACC로 할인해 현재가치 산출.
- **시장 비교(Market Comparable)** — 동종업계 배수(PER, EV/EBITDA, EV/Revenue)를 적용.
- **선행거래 비교(Precedent Transactions)** — 유사 M&A/투자 거래의 배수 참조.
- **VC Method** — 예상 Exit 가치를 목표 수익배수로 역산해 현재 밸류에이션 도출.
- 초기 단계 스타트업엔 SAFE/전환사채(CB)처럼 밸류에이션을 **유예**하는 구조도 흔하다(valuation cap + discount rate).

### 팀/조직 평가

창업자·핵심 인력의 과거 경력(스케일업/엑싯 경험 유무), 조직 안정성(이직률, 핵심인재 리스크), 지분 구조의 합리성(vesting/cliff 여부).

### 리스크·ESG·팩트체크

평판 리스크, 규제 리스크, 소송 이력, 환경/사회/지배구조(ESG) 요소, OSINT(공개정보) 기반 팩트체크 — 회사가 제출한 자료를 외부 공개정보로 교차검증.

## Design Checkpoints (설계 체크포인트)

- 이 기능은 9개 실사 영역 중 **어디에 속하는가**(재무/팀/시장/법무/기타)?
- 문서 분류 체계(폴더 택소노미)에서 어떤 분류가 이 기능의 입력/출력이 되는가 — **새 분류를 만들기 전에 제품의 기존 체계를 재사용할 수 있는지** 먼저 확인. 가치평가 관점의 분류 축은 통상 개요/재무/트랙션·제품/시장·경쟁/팀·조직/법무·IP.
- **단계적 공개**가 필요한 기능인가(즉 실사 진행도에 따라 노출 범위가 달라져야 하는가)?
- 결손 탐지(빠진 자료 감지) · 신뢰도 가중 · 동종업계 비교가 이 기능에 필요한가?
- 회사가 제출한 데이터를 **얼마나 신뢰할 것인가** — 자동 검증/외부 공개정보(OSINT) 대조가 필요한가?

## Sources

- [VC Due Diligence Checklist (Affinity)](https://www.affinity.co/guides/due-diligence-checklist-for-venture-capital) — 9개 영역 체계.
- [Due diligence data room checklist (EthosData)](https://www.ethosdata.com/blog/due-diligence-data-room-checklist/) — 단계적 공개(staged disclosure).
- [Venture Capital Due Diligence: Workflow and Key Stages](https://growthequityinterviewguide.com/venture-capital/venture-capital-industry/venture-capital-due-diligence) — 3단계 실사.

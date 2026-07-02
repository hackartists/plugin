# Stage 3: 딜 소싱 (Deal Sourcing)

**Layer**: 딜 (Deal layer) — 펀드가 결성된 후 실제로 투자 대상을 찾는 첫 단계.
**키워드**: 딜소싱, 파이프라인, 딜플로우, 인바운드, 아웃바운드, IR, 콜드아웃리치, 딜인박스, 프로프라이어터리딜, 중개딜, 투자단계(펀딩스테이지).

## 개요

VC는 좋은 딜이 저절로 굴러들어오길 기다리지 않는다 — 네트워킹, 추천, 피치 이벤트, 콜드 아웃리치, 이메일 인바운드 등 다양한 채널로 상시 소싱한다.

- **프로프라이어터리 딜(Proprietary deal)** — VC가 직접 발굴/소싱한 딜. 경쟁이 적어 조건이 유리한 경우가 많다.
- **중개 딜(Intermediated deal)** — IB/FA/브로커를 통해 들어온 딜. 통상 경쟁 입찰(auction) 구조라 조건이 불리할 수 있다.
- **채널**: 창업자 추천(warm intro), 다른 VC와의 코인베스트 네트워크, 액셀러레이터/데모데이, 이메일 인바운드(피치덱 직접 전송), 콜드 아웃리치.

## 초기 필터 (스크리닝 이전 단계)

딜 소싱 단계에서부터 이미 거친 1차 필터가 걸린다: 섹터 핏, 투자 단계(펀딩 스테이지) 핏, 체크사이즈(투자 규모) 핏, 지역/법인 핏. 이 필터를 통과한 딜만 "심사(Stage 4)" 단계로 넘어간다.

- **투자 단계 용어**: Pre-seed → Seed → Series A → B → C → (Growth/Pre-IPO). 각 단계는 통상 12~18개월 간격, 트랙션/PMF 수준으로 구분된다.

## 실무 감각 (통계)

- 100건의 딜을 검토하면 상세 실사(Stage 4의 비즈니스/재무/법률 실사)로 넘어가는 건 약 10건, 최종 투자 집행은 그중 1건 정도.
- 한국 실무: 상담·사업계획서 제출 단계에서 열 곳 중 여덟 곳이 탈락하고, 최종 투자를 받는 비율은 전체의 1~2%.
- 첫 미팅부터 실제 투자금 집행까지 최소 3개월 ~ 1년 이상 소요.

## Design Checkpoints (설계 체크포인트)

- 딜 유입 채널(이메일/추천/직접 제출)을 어떻게 캡처하고 딜 레코드로 정규화할 것인가?
- 초기 핏 필터(섹터/단계/체크사이즈)를 자동 판정할 것인가, 사람이 수동 분류할 것인가?
- 딜 상태(신규/관심/보류/거절) 전이 규칙과, 각 상태에서 노출되는 정보 범위는?
- 스팸/뉴스레터 등 딜이 아닌 인입을 어떻게 걸러낼 것인가(자동 분류 정확도 vs 오탈락 리스크)?
- 여러 펀드를 운용하는 GP라면, 소싱된 딜을 어느 펀드(또는 펀드 결정 이전 공통 풀)에 붙일 것인가?

## Sources

- [Deal Flow: Process & Deal Flow Management Best Practices (Carta)](https://carta.com/learn/private-funds/management/deal-flow/)
- [Venture Capital Investment Process: A Detailed Walkthrough](https://growthequityinterviewguide.com/venture-capital/venture-capital-industry/venture-capital-investment-process)
- [벤처투자조합 통합 매뉴얼 (KVCA)](https://www.kvca.or.kr/files/download.php?name=%EB%B2%A4%EC%B2%98%ED%88%AC%EC%9E%90%EC%A1%B0%ED%95%A9%ED%86%B5%ED%95%A9%EC%97%85%EB%AC%B4%EB%A7%A4%EB%89%B4%EC%96%BC.pdf) — 소요기간·통과율 통계.

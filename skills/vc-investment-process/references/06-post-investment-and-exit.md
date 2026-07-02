# Stage 7: 사후관리 (Post-Investment Monitoring) & Exit

**Layer**: 딜 — 계약 체결 이후 투자 자산이 살아있는 전체 기간을 다룬다. 이 스킬의 "full lifecycle" 범위상 Exit도 이 스테이지의 종결 이벤트로 함께 다룬다.
**키워드**: 사후관리, 포트폴리오모니터링, KPI리포트, 이사회, 보드덱, 후속투자, 팔로우온, 리저브, 엑싯, exit, M&A, IPO, 세컨더리, 청산우선권, 워터폴.

## 포트폴리오 모니터링 (Portfolio Monitoring)

- **정기 리포팅 캐던스** — 월간/분기 KPI 리포트(매출, 번레이트, 리텐션, 헤드카운트 등)를 포트폴리오사로부터 수취.
- **이사회 참여(Board seat/observer)** — VC가 이사회에 참여해 주요 의사결정에 관여, 보드덱 리뷰.
- **캐피탈콜 집행** — Stage 2에서 약정받은 LP 자금을 실제 투자 집행 시점에 콜(call)해서 납입.
- **포트폴리오 전체 뷰** — 펀드별/딜별로 투자 현황, 밸류에이션 변동, 리스크 신호를 한눈에 보는 대시보드가 핵심 산출물.

## 후속투자 (Follow-on Investment)

- **Pro-rata권** — 후속 라운드에서 기존 지분율을 유지할 권리(Stage 5 텀시트에서 확보).
- **리저브(Reserve) 전략** — 펀드 결성 시 초기 투자 외에 후속투자용으로 남겨두는 자금 배분 계획. 리저브 배분 판단(어느 포트폴리오사에 추가 투자할지)이 사후관리의 핵심 의사결정 중 하나.

## Exit

투자금 회수의 최종 이벤트. 대표적으로 세 경로:

- **M&A(인수합병)** — 전략적/재무적 인수자에게 매각.
- **IPO(기업공개)** — 상장을 통한 유동화.
- **세컨더리 매각(Secondary sale)** — 다른 투자자에게 지분을 직접 매각(상장/M&A 없이).

Exit 시 회수금은 **청산우선권(liquidation preference)** 순서를 따라 정산되고, 펀드 차원에서는 **워터폴(distribution waterfall)** — 원금 반환 → hurdle → GP catch-up → carry 분배 — 순서로 LP/GP에 배분된다.

## Design Checkpoints (설계 체크포인트)

- 이 기능은 **개별 딜 단위**인가, **펀드/포트폴리오 전체 뷰**인가?
- 어떤 KPI를 추적할 것인가 — 스타트업마다 KPI 정의가 다를 수 있다(SaaS의 MRR vs 커머스의 GMV 등).
- Exit 이벤트를 어떻게 트리거·기록할 것인가 — 딜/데이터룸의 최종 상태와 어떻게 연결되는가?
- 리저브/후속투자 판단을 지원하려면 기존 포트폴리오 데이터(밸류에이션 변동, 트랙션 추이)에 대한 시계열 뷰가 필요한가?
- 워터폴/carry 계산이 이 기능의 리포팅 범위에 포함되는가(Stage 1의 펀드 보수구조와 연결)?

> **Note**: 심사(Stage 4)에서 쓰는 리스크/ESG/외부 신호 분석은 사후관리 단계에서 **재확인/재평가** 용도로 재사용되는 경우가 많다 — 같은 분석 모듈을 두 스테이지가 공유하도록 설계할 수 있는지 검토할 것.

## Sources

- [Stages of venture capital (SVB)](https://www.svb.com/startup-insights/vc-relations/stages-of-venture-capital/)
- [Investment Memo & IC 관련: Bessemer Memos](https://www.bvp.com/memos) — Exit 이후 회고형 메모 사례 다수.

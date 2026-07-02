# Stage 5: 투심위 → 의사결정 (Investment Committee & Decision)

**Layer**: 딜 — 실사 결과를 놓고 실제 투자 여부를 결정하는 단계.
**키워드**: 투심위, IC, 투자심의위원회, 딜퀄리피케이션메모, IC메모, 텀시트, 밸류에이션 협상, 우선권.

## 개요

실사가 끝나면 심사역은 결과를 **딜퀄리피케이션 메모(IC 메모)** 로 요약해 **투자심의위원회(투심위, Investment Committee)** 에 상정한다. 위원회는 임원급 3~5명으로 구성되며, 이 자리에서 투자/보류/패스가 결정된다.

### IC 메모의 구조

- Executive Summary — 핵심 요약
- 팀/시장/제품 분석
- 재무 분석(밸류에이션, 유닛이코노믹스)
- 리스크와 그 완화 방안
- 추천(투자/보류/패스) + 조건

### 좋은 IC 메모의 원칙

- **투자 논지(Investment Thesis)를 3개 이내의 반박 가능한 명제로 좁힌다.** 각 명제는 위원이 "동의하지 않을 수 있을 만큼" 구체적이어야 한다.
- **관찰(Fact)과 해석(Interpretation)을 분리한다** — "무엇을 보고 들었는지"와 "그게 왜 투자와 관련 있는지"를 섞지 않는다. IC 이견의 대부분은 이 둘이 섞여서 생긴다.
- 메모는 읽는 사람을 더 똑똑하고 빠르게 만들어야 한다 — 전체 실사 과정을 재구성하지 않아도 회사/논지/근거/리스크/추천을 이해할 수 있어야 한다.

### 텀시트 (Term Sheet)

투심위에서 투자가 결정되면 VC는 텀시트를 스타트업에 전달한다.

- **비구속적(non-binding)** 문서 — 최종 구속력은 DD(특히 법률실사) 결과와 이후 정의계약(SPA/SHA)에 달려 있다.
- 표준 문서 참고: **NVCA Model Legal Documents**(미국 업계 표준 텀시트/투자계약서 템플릿).
- 주요 조건: 밸류에이션(pre-money/post-money), 지분율, **우선권(liquidation preference)**, 이사회 구성, **보호조항(protective provisions)**, **pro-rata권**(후속 라운드 지분 유지권), **ROFR**(우선매수권), **drag-along/tag-along**(동반매도청구/동반매도참여권), vesting(창업자 지분 베스팅).
- 텀시트 서명 후에도 실사는 끝나지 않는다 — 파이널 리걸 실사(Stage 6로 이어짐)가 남아있다.

## Design Checkpoints (설계 체크포인트)

- 투심위 발제 자료(IC 메모)를 이 기능에서 **어떻게 구조화**할 것인가 — Fact/Interpretation을 구분해서 보여줄 수 있는가?
- 의결 기록(찬성/반대/보류, 조건부 승인)을 남기고 추적할 필요가 있는가?
- 텀시트 조건(밸류에이션, 우선권 등)별 협상 이력을 버전 관리해야 하는가?
- 이 기능은 **펀드 단위**로 스코프되는가(어느 펀드의 투심위인지) — Stage 1의 펀드 구조와 연결이 필요한가?

## Sources

- [The Ultimate Guide To VC Investment Committee Memos](https://thevcfactory.com/investment-committee-memos/)
- [Bessemer Venture Partners — Memos](https://www.bvp.com/memos) — 실제 공개된 IC 메모 원본 사례.
- [NVCA Model Legal Documents](https://nvca.org/model-legal-documents/) — 텀시트 표준 템플릿.
- [Anatomy of a Term Sheet: Series A Financing](https://www.mccarter.com/wp-content/uploads/2020/12/AnatomyTermSheet_Q42020_FINAL.pdf)

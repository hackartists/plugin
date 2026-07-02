# Stage 6: 계약 (Closing / Contract Execution)

**Layer**: 딜 — 텀시트 합의 후 실제로 자금이 오가기 전 마지막 단계.
**키워드**: 계약, 클로징, closing, SPA, SHA, 정관, 전자서명, 서명감사추적, 파이널리걸실사.

## 개요

텀시트에 양측이 합의해도 실사는 끝나지 않는다 — **파이널 리걸 실사(external/final due diligence)** 가 텀시트 서명 이후에 진행되며, 이를 바탕으로 최종 구속력 있는 계약서(정의계약, definitive agreements)를 체결한다.

### 표준 문서 (NVCA Model Legal Documents 기준)

- **정관(Certificate of Incorporation)** — 우선주 종류·권리 정의.
- **우선주 인수계약(Preferred Stock Purchase Agreement)** — 실제 투자 실행 계약.
- **투자자 권리계약(Investors' Rights Agreement, IRA)** — 정보청구권, 등록청구권 등.
- **의결권계약(Voting Agreement)**, **ROFR/공동매도계약(Right of First Refusal and Co-Sale Agreement)**.
- 한국 실무에서는 **주식매매계약(SPA)** · **주주간계약(SHA)** 명칭이 널리 쓰인다. 텀시트는 10페이지 내외의 요약, 정의계약은 100페이지를 넘기기도 한다.

### 전자서명 & 감사추적

- **서명자 지정** — 자산보유사/투자사 측 담당자, 서명 순서·필수 여부.
- **서명 진행 상태** — 미요청 → 대기 → 완료 / 거절.
- **계약 상태** — 초안 → 서명중 → 체결완료 / 취소.
- **감사추적(audit trail)** — 누가·언제·무엇에 서명했는지, 문서 해시 값을 남겨 위변조를 검증 가능하게 한다.

## Design Checkpoints (설계 체크포인트)

- 이 기능은 어떤 계약 문서 유형(텀시트/SPA/SHA/기타)을 다루는가?
- 서명 상태와 계약 상태를 **분리해서** 추적하는가(서명 완료 ≠ 계약 발효인 경우가 있다)?
- 딜/DD 맥락(어느 데이터룸에서 나온 계약인지)과 계약 문서를 어떻게 연결할 것인가?
- 감사추적(서명자·시각·문서 해시)이 법적 효력 입증에 충분한가?
- 협상 중 레드라인/코멘트를 별도로 다룰 것인가, 기존 Q&A/메시지 흐름을 재사용할 것인가?

## Sources

- [NVCA Model Legal Documents](https://nvca.org/model-legal-documents/)
- [The Ultimate Guide to Venture Capital Term Sheets](https://www.goingvc.com/post/the-ultimate-guide-to-venture-capital-term-sheets)

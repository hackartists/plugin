# spec.json 스키마

`build_estimate.py` 와 `calc_fp.py` 가 읽는 입력. UTF-8 JSON.

```jsonc
{
  "project_title": "\"○○ 사업\" 소프트웨어 개발비 산정",  // 상세비용 B1 제목
  "output": "견적서.xlsx",                  // 출력 파일명(--output 으로 덮어쓰기 가능)
  "unit_price": 605784,                     // 기능점수당 단가(원). 생략 시 605784
  "correction": {                           // 보정계수 수준 1~5 (생략 시 각 2, 보안 2)
    "linkage": 2,        // 연계복잡성
    "performance": 2,    // 성능 요구수준
    "operation": 2,      // 운영환경 호환성
    "security": 5        // 보안성 요구수준 (금융/블록체인은 4~5 권장)
  },
  "profit_rate": 0.0,                        // 이윤율 (0.0 ~ 0.10). 생략 시 0.10
  "discount_rate": 0.0,                      // 할인율 (0.0 ~). 생략 시 0.0

  "direct_costs": [                          // 직접경비 (최대 4줄). 이윤 산정 제외, 개발비 가산.
    {"item": "UI 개발", "detail": "전체 개발 비용의 15%", "amount": "=K8*0.15"},
    {"item": "인프라 배포", "detail": "시니어 인프라 700만원 x 5M/M", "amount": "=7000000*5"}
  ],
  "expenses": [                              // 실비/Pass-through (최대 2줄). 할인 미적용.
    {"item": "클라우드 비용", "detail": "12개월 운영", "amount": 12000000}
  ],

  "applications": [                          // 기능 분해: 앱 → 세부업무 → 단위프로세스
    {
      "name": "STO 발행·기초자산 관리",
      "subs": [
        {
          "name": "기초자산 발굴·등록",
          "processes": [
            {"name": "기초자산 후보 등록", "desc": "STO 대상 후보 신규 등록", "type": "EI"},
            {"name": "기초자산 마스터 데이터", "desc": "메타·권리 저장소", "type": "ILF", "note": ""}
          ]
        }
      ]
    }
  ]
}
```

## 필드 규칙

- `type`: `EI` | `EO` | `EQ` | `ILF` | `EIF` (대문자). 그 외 값이면 빌드 에러.
- `amount`(직접비/실비): **숫자**(예: `12000000`) 또는 **엑셀 수식 문자열**.
  - 수식에서 `K8` 은 "보정 후 개발원가"를 가리킨다 → `"=K8*0.15"` = 개발원가의 15%.
  - 단순 산술만(예: `"=7000000*5"`). 복잡 수식은 숫자로 환산해 넣기.
- `direct_costs` ≤ 4줄, `expenses` ≤ 2줄 (템플릿 고정 영역). 초과 시 항목 통합.
- 빈 배열(`[]`)이면 해당 표는 비워둔다.

## 빌드 & 미리보기

```bash
python calc_fp.py spec.json                 # 엑셀 없이 금액 미리보기
python build_estimate.py spec.json --output 견적서.xlsx
```

`build_estimate.py` 는 `fullCalcOnLoad` 를 켜므로 Excel/Google Sheets에서 열면
모든 수식이 자동 재계산된다(LibreOffice 불필요).

# sw-estimate

KOSA **기능점수(FP) 간이법**으로 소프트웨어 개발비 견적서(.xlsx)를 생성하는 스킬.
제안서·요구사항을 받아 표준 4시트(최종견적·상세기능·상세비용·보정계수) 엑셀을 만든다.

## 빠른 사용

```bash
# 1) 금액 미리보기 (엑셀 불필요)
python scripts/calc_fp.py examples/sto_platform_spec.json

# 2) 목표 금액 → 필요 총FP 역산
python scripts/calc_fp.py --target 800000000 --security 5

# 3) 견적서 생성
python scripts/build_estimate.py examples/sto_platform_spec.json --output 견적서.xlsx
```

## 구성
- `SKILL.md` — 워크플로우(기능 분해 → 보정계수 → 빌드)
- `assets/kosa_fp_template.xlsx` — 빈 표준 템플릿(수식·서식 내장, 직접비 더블카운트 버그 수정본)
- `scripts/build_estimate.py` · `scripts/calc_fp.py`
- `references/kosa-fp-method.md` · `references/spec-schema.md`
- `examples/sto_platform_spec.json` — STO 플랫폼 예시(307 단위프로세스)

산식·FP유형·보정계수는 `references/kosa-fp-method.md` 참고. 단가(605,784원)는
KOSA 2024 고시값이며 갱신 시 spec 의 `unit_price` 로 교체.

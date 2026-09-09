#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOSA FP 간이법 금액 미리보기 / 목표금액 역산기.

엑셀을 열지 않고도(LibreOffice 불필요) spec.json 의 산식을 파이썬으로 재현해
견적 금액을 미리 계산한다. build_estimate.py 가 만드는 엑셀 수식과 동일한 산식.

사용법:
    python calc_fp.py spec.json                 # spec 기준 금액 미리보기
    python calc_fp.py --target 800000000 \
        --linkage 2 --performance 2 --operation 2 --security 5
                                                # 목표 개발원가를 맞추는 총FP 역산
"""
import argparse, json, math, sys

WEIGHT = {"EI":4, "EO":5.2, "EQ":3.9, "ILF":7.5, "EIF":5.4}
# 보정계수 표 (수준 -> 계수)
LINKAGE = {1:0.88, 2:0.94, 3:1.00, 4:1.06, 5:1.12}
PERF    = {1:0.91, 2:0.95, 3:1.00, 4:1.05, 5:1.09}
OPER    = {1:0.94, 2:1.00, 3:1.06, 4:1.13, 5:1.19}
SEC     = {1:0.97, 2:1.00, 3:1.03, 4:1.06, 5:1.08}
DEFAULT_UNIT = 605784  # KOSA 2024 기능점수당 단가(원)

def size_factor(fp):
    """규모 보정계수. 500FP 미만 1.28, 3,000FP 초과 1.153, 그 외 KOSA 산식."""
    if fp < 500: return 1.28
    if fp > 3000: return 1.153
    return 0.4057 * (math.log(fp) - 7.1978) ** 2 + 0.8878

def corr_product(cor):
    return (LINKAGE[int(cor.get("linkage",2))] * PERF[int(cor.get("performance",2))]
            * OPER[int(cor.get("operation",2))] * SEC[int(cor.get("security",2))])

def total_fp(spec):
    return sum(WEIGHT[p["type"].strip().upper()]
               for app in spec["applications"] for sub in app["subs"] for p in sub["processes"])

def count_funcs(spec):
    return sum(1 for app in spec["applications"] for sub in app["subs"] for p in sub["processes"])

def eval_direct(amount, dev_after):
    """직접비/실비 금액: 숫자거나, '=K8*0.15' / '=7000000*5' 형태의 단순 수식."""
    if isinstance(amount, (int, float)): return float(amount)
    s = str(amount).strip()
    if s.startswith("="): s = s[1:]
    s = s.replace("K8", repr(dev_after))  # K8 = 보정 후 개발원가
    return float(eval(s, {"__builtins__": {}}, {}))

def compute(spec):
    fp = total_fp(spec)
    unit = int(spec.get("unit_price", DEFAULT_UNIT))
    sf = size_factor(fp)
    cp = corr_product(spec.get("correction", {}))
    dev = fp * unit * sf * cp                       # 보정 후 개발원가 (상세비용 K8)
    profit = dev * float(spec.get("profit_rate", 0.10))   # 이윤 (K9)
    direct = sum(eval_direct(d["amount"], dev) for d in spec.get("direct_costs", []))  # 직접경비 (K19)
    expense = sum(eval_direct(e["amount"], dev) for e in spec.get("expenses", []))     # 실비 (K40)
    pre = dev + profit + direct                     # 최종견적 K7 (할인 전, 부가세 별도)
    disc = float(spec.get("discount_rate", 0.0))
    after = math.floor((pre - pre * disc) / 1_000_000) * 1_000_000  # K9 천만 절삭
    supply = after + expense                        # 부가세 별도 (실비는 할인 미적용)
    vat = round(supply * 0.1)
    return dict(funcs=count_funcs(spec), fp=fp, size_factor=sf, corr_product=cp,
                dev=dev, profit=profit, direct=direct, expense=expense,
                pre_discount=pre, discount_rate=disc, after_discount=after,
                supply=supply, vat=vat, total=supply+vat)

def required_fp(target_dev, cor, unit=DEFAULT_UNIT):
    """목표 '보정 후 개발원가'를 만드는 총FP를 반복 수렴으로 역산."""
    cp = corr_product(cor); fp = 1000.0
    for _ in range(200):
        fp = target_dev / (unit * size_factor(fp) * cp)
    return fp

def won(x): return f"{round(x):,}원"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--target", type=float, help="목표 보정후 개발원가(원)")
    ap.add_argument("--linkage", type=int, default=2)
    ap.add_argument("--performance", type=int, default=2)
    ap.add_argument("--operation", type=int, default=2)
    ap.add_argument("--security", type=int, default=2)
    ap.add_argument("--unit", type=int, default=DEFAULT_UNIT)
    a = ap.parse_args()

    if a.target:
        cor = dict(linkage=a.linkage, performance=a.performance, operation=a.operation, security=a.security)
        fp = required_fp(a.target, cor, a.unit)
        print(f"목표 개발원가 {won(a.target)} → 필요 총FP ≈ {fp:.0f}")
        print(f"  (보정계수곱 {corr_product(cor):.4f}, 규모계수 {size_factor(fp):.4f}, 단가 {a.unit:,})")
        print(f"  평균 가중치 5.0 가정 시 단위프로세스 ≈ {fp/5.0:.0f}개")
        return
    if not a.spec:
        ap.error("spec.json 경로 또는 --target 중 하나가 필요합니다.")
    with open(a.spec, encoding="utf-8") as f:
        spec = json.load(f)
    r = compute(spec)
    print(f"단위프로세스 {r['funcs']}개 / 총FP {r['fp']:.1f} "
          f"(규모 {r['size_factor']:.4f}, 보정곱 {r['corr_product']:.4f})")
    print(f"  보정 후 개발원가         {won(r['dev'])}")
    print(f"  이윤                     {won(r['profit'])}")
    print(f"  직접경비                 {won(r['direct'])}")
    print(f"  할인 전(부가세 별도)     {won(r['pre_discount'])}  (할인율 {r['discount_rate']*100:.1f}%)")
    print(f"  할인·절삭 후             {won(r['after_discount'])}")
    if r['expense']: print(f"  실비(할인 미적용)        {won(r['expense'])}")
    print(f"  ── 최종 견적(부가세 별도) {won(r['supply'])}")
    print(f"     부가세(10%)           {won(r['vat'])}")
    print(f"  ══ 최종 견적(부가세 포함) {won(r['total'])}")

if __name__ == "__main__":
    main()

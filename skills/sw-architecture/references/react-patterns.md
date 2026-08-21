# React/TypeScript Patterns — Lean 기준

전제: React 18 + TypeScript, Vite, react-router, TailwindCSS + 디자인 토큰,
shadcn/ui 계열 컴포넌트, i18n. monorepo의 `web/` 프론트엔드 기준이며, mobile/desktop
앱도 같은 배치 원칙(플랫폼 폴더 안 colocation, 조기 공용화 금지)을 따른다.

## 파일·폴더 배치

**Route-folder + colocation이 기본.**

```
src/pages/{route-path}/page.tsx      ← 페이지 (kebab-case, [param] 동적 세그먼트)
src/pages/{route-path}/layout.tsx    ← 해당 라우트 셸
src/pages/{route-path}/…             ← 그 페이지 전용 컴포넌트/훅은 여기 (colocation)
src/components/                      ← 2개 이상 페이지가 쓰는 것만 승격
src/components/ui/                   ← 디자인 시스템 primitive (shadcn) — 수정보다 variant 확장
src/lib/                             ← 순수 유틸 (React 무관 로직)
```

- 페이지 전용 컴포넌트를 `components/`에 만드는 것이 가장 흔한 배치 실수다.
  두 번째 사용처가 생길 때 승격한다 (rule of three의 완화형 — UI는 2회에 승격).
- 승격할 때는 페이지 특화 prop을 벗겨낸다. 페이지 사정이 담긴 prop이 남아 있으면
  아직 공용이 아니다.

## 컴포넌트 분리 기준

컴포넌트를 나누는 유효한 이유는 두 가지뿐이다:
1. **재사용** — 실제 두 번째 사용처가 있다.
2. **독립적 변경/이해 단위** — 파일이 커져서 (기준: ~300줄) 한 화면에서 추론이 어렵다.

다음은 분리 이유가 **아니다**: "깔끔해 보여서", "나중에 재사용할 것 같아서",
"컴포넌트는 작아야 하니까". JSX가 길다는 것만으로는 분리하지 않는다 — 렌더 함수
내부의 지역 변수로 조각을 나누는 것으로 충분한 경우가 많다.

새 UI가 필요할 때의 우선순위:
1. `components/ui/`의 기존 primitive 조합
2. 기존 컴포넌트에 prop/variant 추가
3. 기존 컴포넌트를 감싸는 페이지 로컬 컴포넌트
4. 신규 컴포넌트 (위 3개가 안 되는 이유를 말할 수 있을 때)

## 상태 관리 — 아래로, 더 아래로

상태는 가장 낮은 곳에 둔다. 에스컬레이션 순서:

1. **local `useState`** — 기본값. 폼 입력, 토글, 모달 오픈.
2. **lift up** — 실제로 형제가 공유할 때만 부모로 올린다.
3. **URL** — 필터·탭·페이지네이션처럼 새로고침/공유에 살아남아야 하는 상태는
   searchParams가 정답이다. state로 미러링하지 않는다.
4. **Context** — 진짜 앱 전역(auth, theme, i18n, workspace 셸)만. 기능 하나를 위한
   context 신설은 거의 항상 과잉이다. prop drilling 2–3단계는 정상이며 context보다
   추적하기 쉽다.
5. **서버 상태는 서버 상태 도구로** — 생성된 API 클라이언트(ts-bridges류) + fetch
   훅으로 다룬다. 서버 데이터를 `useState`+`useEffect`로 수동 복사·동기화하는 코드는
   버그 공장이다. 전역 스토어(redux/zustand)에 서버 데이터를 넣지 않는다.

## Custom Hook 기준

`useX`를 만드는 유효한 이유: **2개 이상의 컴포넌트가 같은 stateful 로직을 쓸 때**,
또는 컴포넌트에서 분리해야 테스트 가능한 도메인 로직일 때.

- 한 컴포넌트에서만 쓰는 `useX`는 인라인이 낫다 — 파일 하나, 간접화 한 층이 줄어든다.
- stateless 로직은 훅이 아니라 일반 함수로 (`lib/`) — 훅으로 만들면 테스트에 렌더러가
  필요해진다.

## 흔한 과잉과 처방

| 과잉 | 처방 |
|---|---|
| 측정 없는 `memo`/`useCallback`/`useMemo` | 제거. 실측된 리렌더 문제에만 도입 |
| props 인터페이스에 미사용 optional 필드 | 지금 쓰는 필드만 선언 |
| `useEffect`로 파생값 계산 | 렌더 중 계산하거나 `useMemo`. effect는 외부 동기화 전용 |
| 이벤트 핸들러마다 별도 함수 파일 | 컴포넌트 안 인라인 |
| 거대 `types.ts`에 모든 타입 집결 | 타입도 colocation — 쓰는 곳 옆에 |
| 조건부 렌더를 위한 wrapper 컴포넌트 | `{cond && <X/>}` 인라인 |
| API 응답 타입 수동 재정의 | 생성된 클라이언트 타입 import |

## 텍스트와 스타일

- 사용자 노출 문자열은 하드코딩하지 않는다 — 프로젝트 i18n 패턴(페이지 옆 `i18n.tsx`
  등)을 따른다. 기존 키를 검색해 재사용 우선.
- 색·간격은 디자인 토큰/Tailwind theme을 쓴다. hex 하드코딩은 토큰에 없는 값일
  때만이고, 그 경우 토큰 추가를 제안한다.

## 리팩토링 신호 (React 특화)

- 한 컴포넌트에 `useState` 6개 이상 → 관련 상태를 `useReducer` 또는 단일 객체로
  묶거나, 실제로 두 관심사면 그때 분리.
- prop이 10개 이상 → 컴포넌트가 두 가지 일을 하고 있을 확률이 높다. variant로
  갈라졌으면 children/composition으로 전환 검토.
- `useEffect` 안에서 `setState` 연쇄 → 데이터 흐름 재설계 (파생값/이벤트 핸들러로).
- 같은 fetch를 여러 컴포넌트가 각자 수행 → 상위에서 한 번 부르고 내려주거나 fetch
  캐시 계층으로.

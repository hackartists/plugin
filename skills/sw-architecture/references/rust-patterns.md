# Rust Patterns — Lean 기준

전제: Axum 기반 HTTP 서버(BFF/MSA 서비스), API 경로 기반 디렉토리, 매크로 기반
codegen(라우트 등록, DB 엔티티, TS 브리지), gRPC/Kafka 통신. (원칙은 일반이다.)

## 모듈 구조

**`src/api/{path}` — API 경로 미러링이 기본.** 기술 계층(handlers/, db/, dto/ 전역
폴더)도, 도메인 feature 폴더도 아니라 URL 경로를 그대로 디렉토리로 미러링한다:

```
src/
├── api/
│   └── v1/
│       └── deals/
│           ├── mod.rs        ← /v1/deals 핸들러 + 요청/응답 DTO colocate
│           └── memos/mod.rs  ← /v1/deals/:id/memos 핸들러 + DTO
├── models/                   ← 여러 경로가 공유하는 저장 모델 (공유가 생겼을 때)
├── grpc/  |  events/         ← gRPC 서버 구현 / Kafka producer·consumer
├── config/ · error.rs · main.rs
```

- 새 엔드포인트는 **기존 경로 디렉토리에 넣을 수 있는지 먼저** 본다. 하위 리소스면
  하위 디렉토리로 (`deals/memos/`). 경로에 없는 이름의 폴더를 만들지 않는다.
- 파일 하나로 시작한다. 핸들러 + DTO가 한 `mod.rs`에 있는 것이 기본이고, 파일이
  커졌을 때 나눈다 — 엔드포인트 하나에 handler/types/service 3분할 스캐폴딩 금지.
- 도메인 로직이 두 경로 이상에서 필요해지면 그때 `src/models/`·`src/domain/`으로
  승격한다.
- `mod.rs`의 `pub use` 남발 금지 — 공개 표면이 넓을수록 리팩토링이 어려워진다.
  `pub(crate)`가 기본값이라고 생각하라.
- gRPC 핸들러와 Kafka consumer도 같은 원칙 — proto/이벤트 계약은 packages의 생성
  스텁을 import하고, 서비스 안에서 계약 타입을 수동 재정의하지 않는다.

## Trait 규율

trait을 만드는 유효한 이유:
1. **실제 구현이 2개 이상** 존재한다 (지금, 로드맵이 아니라).
2. **외부 계약**이다 — 다른 crate/서비스가 구현해야 하는 인터페이스.
3. 표준 트레이트 구현 (`From`, `Display`, `Iterator`, serde 등).

"테스트를 위한 trait"은 마지막 수단이다 — 실제 Postgres/컨테이너 기반 테스트,
테스트용 생성자, 순수 함수 분리로 해결되는지 먼저 본다. mock을 위해 프로덕션 코드에
간접화를 넣는 것은 꼬리가 개를 흔드는 것이다.

제네릭도 같은 기준: 호출처가 한 타입뿐이면 concrete 타입으로 쓴다.
`impl Trait` 인자는 실제 다형성이 필요할 때만.

## 에러 처리

- 프로젝트의 기존 `Error` enum(`error.rs`)에 variant를 추가하는 것이 기본이다.
  feature마다 새 에러 타입을 만들지 않는다 — 에러 타입 수는 에러 처리 전략의 수를
  넘지 않아야 한다.
- `?`로 전파가 기본. `match`로 잡는 것은 그 자리에서 **다르게 행동**할 때만.
- `unwrap`/`expect`는 불변식이 보장된 곳 + 이유를 담은 `expect("...")` 메시지로.
  핸들러/서비스 경로에서는 금지.
- `let _ = fallible()` 로 에러를 버리지 않는다. 무시가 정말 맞으면 왜 무시해도
  되는지 주석 한 줄이 필요한 지점이다.

## 소유권 — 실용주의

- 우선순위: **컴파일되는 단순한 코드 > 영리한 zero-copy**. `clone()`은 죄가 아니다 —
  hot path에서 측정되기 전까지는.
- 다만 습관적 clone 3연쇄가 보이면 설계 신호다: 참조로 충분한지, 소유권을 넘기는 게
  맞는지 한 번 본다.
- 명시적 lifetime 파라미터가 3개 이상 필요해지면 구조를 의심한다 — 소유하는 타입으로
  바꾸는 것이 대부분 정답이다.
- `Arc<Mutex<T>>`는 공유 가변 상태가 정말 필요한지 자문한 후에. 메시지 전달이나
  DB가 정답인 경우가 많다.

## Codegen 존중

매크로/생성 코드가 있는 프로젝트에서 가장 비싼 실수는 **생성물을 수동으로 미러**하는
것이다:

- 라우트: 라우트 매크로(`#[get]`/`#[post]` + inventory 등록) 컨벤션을 따른다.
  수동 `Router::route()` 병기 금지.
- DB 엔티티: 엔티티 매크로(postgres-macros류)로 정의하고 additive 스키마 버전을
  따른다. 수동 DDL/수동 쿼리 매핑을 섞지 않는다.
- TS 타입: `make gen-ts` 류 codegen 커맨드가 진실이다. 프론트에 손으로 타입을 다시
  쓰지 않는다. **DTO를 바꿨으면 codegen 실행까지가 작업의 완료다.**

## 흔한 과잉과 처방

| 과잉 | 처방 |
|---|---|
| 필드 2개 struct에 builder 패턴 | struct literal 초기화 |
| newtype 남발 (`UserId(i64)`가 아무 불변식도 안 지킬 때) | 불변식·혼동 위험이 실재할 때만 |
| `impl Default` + `..Default::default()`로 필수값 우회 | 필수값은 생성자 인자로 강제 |
| 한 곳에서 쓰는 매크로 정의 | 함수/제네릭으로 |
| `async fn`인데 `.await` 없음 | 동기 함수로 |
| free function이면 될 것을 trait + 단일 impl | free function |
| `Box<dyn Trait>` 반환 (호출처가 한 타입만 씀) | concrete 타입 반환 |
| 모든 필드 `pub` | 접근이 필요한 필드만, 가급적 메서드 경유 |

## 리팩토링 신호 (Rust 특화)

- `mod.rs`가 로직을 갖기 시작 → 서브모듈로 내리고 mod.rs는 선언/재수출만.
- 함수 인자 5개 이상 → 의미 단위 struct로 묶는다 (Config/Params).
- 같은 `match self.kind {...}`가 3곳 이상 반복 → enum의 메서드로 이동. trait은
  variant가 아니라 **타입**이 갈릴 때.
- 서비스 함수가 DB 호출과 도메인 규칙을 섞어 200줄 → 순수 로직을 함수로 분리
  (인자로 데이터를 받는 형태) → 그 함수부터 단위 테스트.

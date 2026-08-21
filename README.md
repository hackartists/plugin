# hackartist-plugins

A curated skills library for Claude Code. Covers frontend design, visual art, Dioxus (Rust) development, Korean document processing, and skill discovery.

## Installation

### Install marketplace in Claude Code

```
/plugin marketplace add hackartists/plugin
```


## Skills

| Skill | 용도 |
|---|---|
| `sw-architecture` | React/Rust 개발·기획 시 lean 코드 원칙, 패턴 선택, MSA monorepo 배치, 점진적 리팩토링 가이드 |
| `sw-estimate` | KOSA 기능점수 간이법 개발비 견적서(.xlsx) 생성 |
| `dioxus`, `dioxus-translate`, `dioxus-knowledge-patch` | Dioxus(Rust) 앱 개발 |
| `frontend-design`, `canvas-design` | UI/시각 디자인 |
| `hwpxskill`, `hwpx-workflow` | 한글(HWPX) 문서 |
| `slack-tasks` | Biyard Slack Tasks 리스트/캔버스 |

## Commands

| Command | 용도 | 언제 |
|---|---|---|
| `/hackartist-plugins:minimize-changes` | 현재 diff가 목표 달성에 필요한 최소 변경인지 감사하고, 무관한 변경을 되돌리고 더 적은 코드로 축소 | 구현·리팩토링 직후, 커밋/PR 전 |
| `/hackartist-plugins:minimize-duplicates` | 변경 범위의 중복·유사 코드를 찾아 기존 코드를 **backward-compatible 하게 확장**해 재사용하도록 수정 | 새 코드 작성 전(탐색) + 작성 후(정리) |

`sw-architecture` 스킬은 개발 모드에서 `minimize-duplicates → 구현 → minimize-duplicates → minimize-changes` 순서를 루틴으로 실행하도록 지시한다.

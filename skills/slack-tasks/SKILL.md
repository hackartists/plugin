---
name: slack-tasks
description: Use when reading or appending the Biyard Slack "Tasks(Asset)" list, or creating/editing a Slack canvas, from any project. Triggers — "Tasks(Asset) 리스트 읽어/추가", "기능 도출한 거 Slack 리스트에 추가", "이 기능 Tasks에 올려줘", "slack canvas 업데이트/만들어줘", or when a feature-discovery / spec workflow needs to register a feature on the Slack list. Wraps the Slack Lists API (slackLists.items.*) and Canvas API (canvases.*) via a helper script with a bot token.
---

# Slack Tasks(Asset) & Canvas

Biyard workspace의 Slack **List "Tasks(Asset)"** 읽기·항목 추가와 **Slack canvas** 생성·편집을 헬퍼 스크립트로 처리한다. 기능 도출(feature-discovery) 워크플로우가 도출한 기능을 리스트에 등록할 때 주로 사용.

## Prerequisites

- 봇 토큰(`xoxb-…`)이 `~/.claude/.slack-canvas-token`에 저장돼 있어야 함 (한 줄, 개행 없이).
  - 필요한 scope: `lists:read`, `lists:write`, `canvases:read`, `canvases:write`.
  - 다른 경로를 쓰려면 `SLACK_CANVAS_TOKEN_FILE` 환경변수로 지정.
- `curl`, `jq` 필요 (macOS 기본 + Homebrew jq).

## Helper script

경로: `~/.claude/plugins/marketplaces/hackartists/skills/slack-tasks/slack-tasks.sh`
(권한 prompt 없이 자동 실행되도록 `~/.claude/settings.json`의 allow에 등록되어 있음.)

```bash
ST=~/.claude/plugins/marketplaces/hackartists/skills/slack-tasks/slack-tasks.sh

"$ST" auth                       # 토큰/봇 상태 확인 (auth.test)
"$ST" read                       # 리스트 항목을 [구분] 완료여부 이름 형태로 출력
"$ST" read --json                # 원본 JSON
"$ST" add 기획 "기능 이름"        # 항목 추가 — 이름 + 구분(기획)
"$ST" add 개발 "기능 이름"        # 구분=개발

# Canvas
"$ST" canvas-create "제목" "## 마크다운 본문"
"$ST" canvas-edit F0ABC123 insert_at_end "## 추가 섹션"   # op: insert_at_end(기본)|insert_at_start|replace
```

- 한글이 들어가는 인자는 스크립트가 `jq -n`으로 payload를 만들어 처리하므로 셸 인코딩 문제 없음.
- `add`는 **이름 + 구분만** 채운다(담당자/기한/참고자료는 사람이 Slack에서 채움).

## 기능 도출 워크플로우 연동

biyard/asset 의 `feature-discovery.md` (기획 P1)에서, `docs/{slug}/spec.md`를 만든 직후 한 줄로 호출:

```bash
~/.claude/plugins/marketplaces/hackartists/skills/slack-tasks/slack-tasks.sh add 기획 "<기능 이름>"
```

도출 단계 산출물은 항상 **구분=기획**으로 등록한다(개발 착수 시 사람이 개발로 변경).

## Workspace constants (참고)

| 항목 | 값 |
|---|---|
| Team ID | `T03H3B09USV` (Biyard) |
| List "Tasks(Asset)" | `F0B9C3J3J48` |
| 이름 컬럼 (text) | `Col0B8ED2JG3X` |
| 구분 컬럼 (select) | `Col0BBVG1TYSG` — 기획=`OptF7M55ONU`, 개발=`Opt34PZKJS4` |
| 기타 컬럼 | 담당자 `todo_assignee` · 기한 `todo_due_date` · 완료 `todo_completed` · 참고자료(link) `Col0B91JEQX4L` · 이유(canvas) `Col0B9A7QLQ03` |

> 상수는 스크립트 안에도 박혀 있다. 워크스페이스/리스트가 바뀌면 스크립트 상단을 수정한다.

## Rules

- **토큰은 절대 출력/커밋하지 않는다.** 항상 파일에서 읽고, curl 인자로 토큰을 노출하지 않는다(스크립트가 헤더로 처리).
- **추가는 이름+구분만.** 나머지 필드는 비워 두고 사람이 채운다.
- **검증용 임시 항목을 만들면 즉시 삭제한다** (`slackLists.items.delete`).
- 리스트/캔버스 ID가 바뀌면 이 문서의 상수 표와 스크립트 상단을 함께 갱신한다.

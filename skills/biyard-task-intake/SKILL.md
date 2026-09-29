---
name: biyard-task-intake
description: "\uc0ac\uc6a9\uc790(Miner)\uac00 \"\uc5c5\ubb34 \ucd94\uac00\ud574\ub193\uc544\", \"\uc774\uac70 \uc5c5\ubb34\ub85c \ub4f1\ub85d\ud574\ub193\uc544\", \"task \ub9cc\ub4e4\uc5b4\ub193\uc544\" \ub9d0\ud560 \ub54c \uc0ac\uc6a9. biyard/workflows \uc0ac\ub0b4 \uc5c5\ubb34 \uad00\ub9ac ERP(https://workflow.biyard.co)\uc758 API-key \uae30\ubc18 Task CRUD API(POST/GET/PATCH/DELETE /api/v1/tasks)\ub97c \ud1b5\ud574 \uc5c5\ubb34\ub97c \uc9c1\uc811 \ub4f1\ub85d\ud55c\ub2e4. \ucc98\uc74c \uc811\uc218\ud560 \ub54c\ub294 \uc81c\ubaa9/\uc124\uba85/Slack \ub300\ud654 \ub9c1\ud06c\ub9cc \ub123\uace0 \ub2f4\ub2f9\uc790\uc640 \uc77c\uc815\uc740 \ube44\uc6cc\ub454\ub2e4 \u2014 \ub098\uc911\uc5d0 PATCH\ub85c \ucc44\uc6b4\ub2e4."
---

# Biyard 업무 접수 (Task Intake)

Miner가 "업무 추가해놔"라고 하면 biyard/workflows의 `/api/v1/tasks` API로 **바로 접수**한다. 담당자·일정 없이 제목/설명/Slack 링크만으로 backlog에 넣는 것이 기본 동작이다.

## 하드 룰

1. **처음 접수할 때는 `assignee`와 `scheduled_at`을 절대 넣지 않는다.** 사용자가 "이거 누구한테 시켜" 등으로 명시적으로 담당자·일정을 지정하지 않는 한, 제목(title)·설명(content)·Slack 링크(slack_link)만 채운다.
2. 담당자/일정은 나중에 별도 요청이 있을 때 `PATCH /api/v1/tasks/{task_id}`로 채운다.
3. API 키는 대화에 노출하지 않는다 — `$WORKFLOWS_AGENT_API_KEY` 환경변수로만 다룬다.
4. `stage`는 `planning` 또는 `dev` 둘 중 하나만 유효하다. 애매하면 기본값 `dev`를 쓰고, 필요하면 사용자에게 확인한다.

## 준비물

- `~/.hermes/.env`에 다음 두 값이 있어야 한다 (없으면 사용자에게 물어서 `write_file`이 아니라 `terminal`로 append — `.env`는 직접 read_file 불가):
  - `WORKFLOWS_AGENT_API_KEY` — biyard/workflows GitHub repo secret `AGENT_API_KEY`와 동일한 값. 배포 파이프라인(`.github/workflows/prod-workflow.yml`)의 `workflows-secrets` k8s Secret에 배선되어 있어야 prod에서 동작한다.
  - `WORKFLOWS_API_BASE_URL` — 기본 `https://workflow.biyard.co`.
- 로컬 셸에서 값을 쓰려면 `terminal` 도구로 환경변수를 export한 뒤 사용한다 (Hermes의 `.env`는 `mcp__read_file`로 읽을 수 없음 — provider 채널을 거치지 않으므로 `terminal(command="grep ...")`으로 직접 읽어야 한다).

```bash
source <(grep -E '^WORKFLOWS_(AGENT_API_KEY|API_BASE_URL)=' ~/.hermes/.env)
```

## 접수 절차 (업무 추가해놔)

1. 사용자 메시지에서 **제목**, **설명**(맥락/배경), 그리고 있으면 **Slack 대화 링크**를 뽑아낸다. 부족하면 짧게 되묻는다 — 단, 담당자/일정은 절대 묻지 않는다.
2. `stage`를 정한다 — 특별한 언급 없으면 `dev` (바로 개발 착수 가정). 기획 단계로 명시되면 `planning`.
3. 아래처럼 생성한다:

```bash
source <(grep -E '^WORKFLOWS_(AGENT_API_KEY|API_BASE_URL)=' ~/.hermes/.env)

curl -s -X POST "${WORKFLOWS_API_BASE_URL}/api/v1/tasks" \
  -H "Authorization: Bearer ${WORKFLOWS_AGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<제목>",
    "content": "<설명>",
    "stage": "dev",
    "slack_link": "<슬랙 링크 있으면, 없으면 이 키 자체를 생략>"
  }'
```

4. 응답 예시: `{"idea_id":"...","task_id":"...","schedule_id":null}` (201). `schedule_id`가 `null`인 것이 정상 — 일정을 안 넣었으니 당연하다.
5. 사용자에게 `task_id`와 함께 접수 완료를 보고한다. "담당자·일정은 아직 비워뒀고, 필요하면 말씀해주시면 채우겠습니다" 같은 문구를 덧붙인다.

## 나중에 담당자/일정 채우기 (별도 요청 시에만)

```bash
curl -s -X PATCH "${WORKFLOWS_API_BASE_URL}/api/v1/tasks/${TASK_ID}" \
  -H "Authorization: Bearer ${WORKFLOWS_AGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"assignee": "U0123456", "status": "assigned"}'
```

일정(공유 날짜)까지 캘린더 등록·Slack 공지까지 원하면, 담당자가 있는 상태에서 새로 만드는 게 아니라 이 PATCH로 `scheduled_at`을 추가하는 것으로는 캘린더/공지가 되지 않는다 — 그 경로는 `POST /api/v1/tasks`에 `assignee` + `scheduled_at`을 **처음부터 같이** 줄 때만 탄다 (`services/workflows-service/src/routes/api.rs`의 `create_task_inner` 참고). 이미 만들어진 task에 나중에 일정을 걸고 싶으면 담당자를 PATCH로 먼저 채운 뒤, 팀에 공지가 필요하면 Slack `/biyard-assign-plan` 같은 기존 플로우를 안내하거나 사용자에게 확인한다.

## API 레퍼런스 요약

| 메서드 & 경로 | 용도 |
| --- | --- |
| `POST /api/v1/tasks` | 새 업무 생성. `title`,`content`,`stage` 필수; `assignee`,`scheduled_at`,`slack_link` 선택. `scheduled_at`은 `assignee` 없이는 400. |
| `GET /api/v1/tasks?status=backlog` | 목록 조회 (status: backlog/assigned/scheduled/done/closed) |
| `GET /api/v1/tasks/{task_id}` | 단건 조회 |
| `PATCH /api/v1/tasks/{task_id}` | `status`/`assignee`/`scheduled_at` 부분 수정 |
| `DELETE /api/v1/tasks/{task_id}` | 강제 종료 (idea도 rejected로 정리) |

인증 실패 시 401, `AGENT_API_KEY`가 배포에 미설정이면 전체 라우트가 404.

## 소스 / 배경

- 레포: `~/data/devel/github.com/biyard/workflows` (github.com/biyard/workflows)
- 구현: `services/workflows-service/src/routes/api.rs`
- 문서: 레포 `README.md`의 "API 키 기반 Task API" 섹션
- e2e 테스트: `e2e/tests/*.spec.ts` (Playwright, `request` 픽스처만 사용, 브라우저 없음)
- 배포: main 푸시 시 `.github/workflows/prod-workflow.yml`가 자동 배포 (k3s, `workflow.biyard.co`)

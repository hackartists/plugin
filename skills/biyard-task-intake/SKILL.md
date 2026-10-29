---
name: biyard-task-intake
description: "\uc0ac\uc6a9\uc790(Miner)\uac00 \"\uc5c5\ubb34 \ucd94\uac00\ud574\ub193\uc544\", \"\uc774\uac70 \uc5c5\ubb34\ub85c \ub4f1\ub85d\ud574\ub193\uc544\", \"task \ub9cc\ub4e4\uc5b4\ub193\uc544\" \ub9d0\ud560 \ub54c \uc0ac\uc6a9. biyard/workflows \uc0ac\ub0b4 \uc5c5\ubb34 \uad00\ub9ac ERP(https://workflow.biyard.co)\uc758 API-key \uae30\ubc18 Task CRUD API(POST/GET/PATCH/DELETE /api/v1/tasks)\ub97c \ud1b5\ud574 \uc5c5\ubb34\ub97c \uc9c1\uc811 \ub4f1\ub85d\ud55c\ub2e4. \ucc98\uc74c \uc811\uc218\ud560 \ub54c\ub294 \uc81c\ubaa9/\uc124\uba85/Slack \ub300\ud654 \ub9c1\ud06c\ub9cc \ub123\uace0 \ub2f4\ub2f9\uc790\uc640 \uc77c\uc815\uc740 \ube44\uc6cc\ub454\ub2e4 \u2014 \ub098\uc911\uc5d0 PATCH\ub85c \ucc44\uc6b4\ub2e4."
---

# Biyard 업무 접수 (Task Intake)

Miner가 "업무 추가해놔"라고 하면 biyard/workflows의 `/api/v1/tasks` API로 **바로 접수**한다. `assignee`는 기본적으로 Miner(Slack user id `U03QHDMCVB2`)로 채우고, 일정(`scheduled_at`)만 비운 채 backlog/assigned 상태로 넣는 것이 기본 동작이다.

## 하드 룰

1. **처음 접수할 때 `assignee`는 기본값으로 Miner(`U03QHDMCVB2`)를 넣는다.** 사용자가 "이거 누구한테 시켜"처럼 다른 담당자를 명시하면 그 사람의 Slack id로 바꾸고, `assignee`를 명시적으로 비우라고 하면 그때만 생략한다. `scheduled_at`은 별도 언급이 없는 한 넣지 않는다.
2. 일정(`scheduled_at`)은 나중에 별도 요청이 있을 때 `PATCH /api/v1/tasks/{task_id}`로 채운다. 담당자를 바꾸고 싶을 때도 같은 PATCH 경로를 쓴다.
3. API 키는 대화에 노출하지 않는다 — `$WORKFLOWS_AGENT_API_KEY` 환경변수로만 다룬다.
4. `stage`는 `planning` 또는 `dev` 둘 중 하나만 유효하다. 애매하면 기본값 `dev`를 쓰고, 필요하면 사용자에게 확인한다.
5. **Miner가 아닌 다른 사용자에게 업무를 등록할 때는 새 스레드로 분리한다** (Miner 지시, 2026-10-20). 같은 채널에 `~/.hermes/scripts/slack_thread_post.py --channel <CH> --text "*[업무] <제목>* <@담당자> 이 스레드가 이 업무의 소통 스레드야. (원 논의: <permalink>) • 범위/항목..."`로 루트 메시지를 올리고, 그 새 ts로 `pm_notes_register.py --assignee <담당자 Slack id> --channel <CH> --ts <새 ts>` 등록. 담당자 Slack id는 원 메시지 텍스트의 `<@U...>`에서 얻는다(conversations.replies). 원 스레드에는 새 스레드 링크 + task_id만 짧게 보고.
   - **예외**: 원 스레드 자체가 그 업무 할당용이면(Miner가 루트 메시지에서 담당자를 @멘션해 업무를 지시하고 같은 메시지/스레드에서 "업무등록해줘") 새 스레드를 만들지 말고 **원 스레드 ts로 바로 등록**한다 (Miner 지시, 2026-10-21).
   - 실수로 분리 스레드를 만들었다면: task PATCH `slack_link` + list Thread 컬럼을 원 permalink로 교체하고, 봇이 올린 분리 루트 메시지는 `chat.delete`로 지운다. PATCH는 `content`를 무시하므로 content 안의 옛 링크는 고칠 수 없다.
   - Due는 타인 할당 업무도 Miner가 따로 말하지 않으면 **내일**(`--due tomorrow`). 등록·Thread 수정 후 `slackLists.items.list`로 해당 row의 Due(`Col02`)가 실제로 채워져 있는지 확인하고, 비어 있으면 `slackLists.items.update`로 다시 채운다 (2026-10-21: 등록 시 OK였던 Due가 Thread 교체 후 비어 있던 사례 있음, 원인: Thread 셀을 update하면 같은 호출에 Due를 같이 넣어도 Due가 비워짐 — Thread 교체 후 Due만 담은 `slackLists.items.update`를 **별도 호출**로 한 번 더 보내고 확인).
   - 이미 기존 스레드로 등록해버린 경우 수정법: 새 루트 메시지를 올린 뒤 `PATCH /api/v1/tasks/{task_id}` `{"slack_link": <새 permalink>}` + `slackLists.items.update`로 해당 row의 Thread 컬럼(`THREAD_COLUMN`)을 새 permalink로 교체 (`pm_notes_register` 모듈의 `load_env`/`http_json`/상수 재사용).
6. task를 `done`으로 처리한 뒤(PATCH 또는 `pr_merge_finish.py`) `self-skilling` 스킬을 로드해 회고한다.
   - `pr_merge_finish.py`의 task 자동조회는 task 내용에 PR URL이 있어야 매칭된다. 슬랙 스레드로 등록하고 PR을 나중에 만든 업무는 `0 tasks match`로 FAIL 나므로 `--task-id`/`--row-id`(등록 출력의 `task_id`, `row_id`)를 넘긴다.
   - PR이 없는 업무 완료: workflows PATCH만으로는 Slack List 행이 Done이 안 된다. `~/.hermes/scripts`에서 `pr_merge_finish`를 import해 `Ctx(SimpleNamespace(repo=<아무 org/repo>, pr=0, task_id=..., row_id=..., list_id=pmn.DEFAULT_LIST_ID, clone=None, skip_merge=True, force=False, dry_run=False))`로 `step_task`, `step_list_row`만 호출하고, 끝나면 `ctx.state_path` 캐시 파일을 지운다. task_id/row_id는 `pm_notes_register.py` 출력에 있다. 출력이 없으면 `GET /api/v1/tasks?status=assigned` 결과에서 스레드 ts(`p<ts숫자>`)로 task_id를 찾고, `row_id=None`으로 두면 `find_row`가 task 제목/Thread로 행을 찾는다. status 목록 조회는 느리니(3개 루프가 180s 초과) status 하나씩 timeout을 넉넉히 잡는다.

## Due (Miner PM Notes 리스트 Due 컬럼 `Col02`)

`~/.hermes/scripts/pm_notes_register.py --due ...`로 지정 (KST 기준):
- 바로 작업 시작하는 업무 → 다음날 (`--due tomorrow`, 기본값)
- 장기 업무 → 한 달 뒤 (`--due month`)
- 백로그 → 비움 (`--due none`)
- 특정 날짜 → `--due YYYY-MM-DD`

## 준비물

- `~/.hermes/.env`에 다음 두 값이 있어야 한다 (없으면 사용자에게 물어서 `write_file`이 아니라 `terminal`로 append — `.env`는 직접 read_file 불가):
  - `WORKFLOWS_AGENT_API_KEY` — biyard/workflows GitHub repo secret `AGENT_API_KEY`와 동일한 값. 배포 파이프라인(`.github/workflows/prod-workflow.yml`)의 `workflows-secrets` k8s Secret에 배선되어 있어야 prod에서 동작한다.
  - `WORKFLOWS_API_BASE_URL` — 기본 `https://workflow.biyard.co`.
- 로컬 셸에서 값을 쓰려면 `terminal` 도구로 환경변수를 export한 뒤 사용한다 (Hermes의 `.env`는 `mcp__read_file`로 읽을 수 없음 — provider 채널을 거치지 않으므로 `terminal(command="grep ...")`으로 직접 읽어야 한다).

```bash
source <(grep -E '^WORKFLOWS_(AGENT_API_KEY|API_BASE_URL)=' ~/.hermes/.env)
```

## 접수 절차 (업무 추가해놔)

1. 사용자 메시지에서 **제목**, **설명**(맥락/배경), 그리고 있으면 **Slack 대화 링크**를 뽑아낸다. 부족하면 짧게 되묻는다 — 단, 담당자는 기본값(Miner)이 있으므로 묻지 않고, 일정도 절대 묻지 않는다.
2. `stage`를 정한다 — 특별한 언급 없으면 `dev` (바로 개발 착수 가정). 기획 단계로 명시되면 `planning`.
3. `assignee`는 기본값 `U03QHDMCVB2`(Miner)를 넣는다. 사용자가 다른 사람을 지정했으면 그 Slack id로 교체한다.
4. 아래처럼 생성한다:

```bash
source <(grep -E '^WORKFLOWS_(AGENT_API_KEY|API_BASE_URL)=' ~/.hermes/.env)

curl -s -X POST "${WORKFLOWS_API_BASE_URL}/api/v1/tasks" \
  -H "Authorization: Bearer ${WORKFLOWS_AGENT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<제목>",
    "content": "<설명>",
    "stage": "dev",
    "assignee": "U03QHDMCVB2",
    "slack_link": "<슬랙 링크 있으면, 없으면 이 키 자체를 생략>"
  }'
```

5. 응답 예시: `{"idea_id":"...","task_id":"...","schedule_id":null}` (201). `schedule_id`가 `null`인 것이 정상 — 일정을 안 넣었으니 당연하다.
6. 사용자에게 `task_id`와 함께 접수 완료를 보고한다. "담당자는 Miner로 등록했고, 일정은 아직 비워뒀습니다. 필요하면 말씀해주시면 채우겠습니다" 같은 문구를 덧붙인다.

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

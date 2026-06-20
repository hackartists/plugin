#!/usr/bin/env bash
# slack-tasks.sh — Biyard Slack "Tasks(Asset)" list + canvas helper.
#
# Auth: reads a Slack bot token (xoxb-…) from $SLACK_CANVAS_TOKEN_FILE
#       (default ~/.claude/.slack-canvas-token). Scopes needed: lists:read,
#       lists:write, canvases:read, canvases:write.
#
# Usage:
#   slack-tasks.sh read [--json]                 # read the Tasks(Asset) list
#   slack-tasks.sh add <기획|개발> <name...>      # add an item (이름 + 구분)
#   slack-tasks.sh auth                          # auth.test (sanity check)
#   slack-tasks.sh canvas-create <title> <md>    # create a canvas, prints id+url
#   slack-tasks.sh canvas-edit <canvasId> [op] <md>   # op: insert_at_end(default)|insert_at_start|replace
#
# All non-ASCII (Korean) payloads are built with jq -n to avoid shell quoting issues.
set -euo pipefail
export LC_ALL="${LC_ALL:-en_US.UTF-8}" LANG="${LANG:-en_US.UTF-8}"

TOKEN_FILE="${SLACK_CANVAS_TOKEN_FILE:-$HOME/.claude/.slack-canvas-token}"

# --- Biyard workspace constants -------------------------------------------
TEAM_ID="T03H3B09USV"
LIST_ID="F0B9C3J3J48"            # Tasks(Asset)
NAME_COL="Col0B8ED2JG3X"          # 이름 (text)
GUBUN_COL="Col0BBVG1TYSG"         # 구분 (select)
OPT_PLAN="OptF7M55ONU"            # 기획
OPT_DEV="Opt34PZKJS4"             # 개발
API="https://slack.com/api"

die() { echo "error: $*" >&2; exit 1; }
[ -f "$TOKEN_FILE" ] || die "token file not found: $TOKEN_FILE"
TOK="$(tr -d '\n' < "$TOKEN_FILE")"
[ -n "$TOK" ] || die "empty token in $TOKEN_FILE"
command -v jq >/dev/null || die "jq is required"

call() { # call <method> <json-payload-or-empty>
  local method="$1" payload="${2:-}"
  if [ -n "$payload" ]; then
    printf '%s' "$payload" | curl -s -X POST \
      -H "Authorization: Bearer $TOK" \
      -H "Content-Type: application/json; charset=utf-8" \
      --data @- "$API/$method"
  else
    curl -s -H "Authorization: Bearer $TOK" "$API/$method"
  fi
}

cmd="${1:-}"; shift || true
case "$cmd" in
  auth)
    call auth.test | jq '{ok, user, team, bot_id, error}'
    ;;

  read)
    raw="$(curl -s -G -H "Authorization: Bearer $TOK" \
            --data-urlencode "list_id=$LIST_ID" "$API/slackLists.items.list?limit=200")"
    [ "$(printf '%s' "$raw" | jq -r '.ok')" = "true" ] || { printf '%s' "$raw" | jq '{ok,error}'; exit 1; }
    if [ "${1:-}" = "--json" ]; then printf '%s\n' "$raw"; exit 0; fi
    printf '%s' "$raw" | jq -r '
      def g($v): if $v=="'"$OPT_PLAN"'" then "기획" elif $v=="'"$OPT_DEV"'" then "개발" else "미분류" end;
      .items[]
      | ([.fields[]|select(.key=="'"$NAME_COL"'" or .key=="name")|.text][0] // "") as $n
      | ([.fields[]|select(.key=="'"$GUBUN_COL"'" or .key=="Col0BBKGDG57D")|.select[0]][0]) as $g
      | ([.fields[]|select(.key=="todo_completed")|.checkbox][0]) as $done
      | "[\(g($g))] \(if $done==true then "✅" else "⬜" end) \($n)"'
    ;;

  add)
    gubun="${1:-}"; shift || true
    name="$*"
    [ -n "$gubun" ] && [ -n "$name" ] || die "usage: add <기획|개발> <name...>"
    case "$gubun" in
      기획|plan|PLAN) opt="$OPT_PLAN" ;;
      개발|dev|DEV)   opt="$OPT_DEV" ;;
      *) die "구분 must be 기획 or 개발 (got: $gubun)" ;;
    esac
    payload="$(jq -n --arg list "$LIST_ID" --arg ncol "$NAME_COL" --arg gcol "$GUBUN_COL" \
                     --arg name "$name" --arg opt "$opt" '{
      list_id: $list,
      initial_fields: [
        {column_id:$ncol, rich_text:[{type:"rich_text",elements:[{type:"rich_text_section",elements:[{type:"text",text:$name}]}]}]},
        {column_id:$gcol, select:[$opt]}
      ]}')"
    res="$(call slackLists.items.create "$payload")"
    ok="$(printf '%s' "$res" | jq -r '.ok')"
    if [ "$ok" = "true" ]; then
      id="$(printf '%s' "$res" | jq -r '(.item // .record).id')"
      echo "added: [$gubun] $name  (id: $id)"
    else
      printf '%s' "$res" | jq '{ok, error, needed, provided}'; exit 1
    fi
    ;;

  canvas-create)
    title="${1:-}"; md="${2:-}"
    [ -n "$title" ] || die "usage: canvas-create <title> <markdown>"
    [ -n "$md" ] || md="$(cat)"
    payload="$(jq -n --arg t "$title" --arg m "$md" \
      '{title:$t, document_content:{type:"markdown", markdown:$m}}')"
    res="$(call canvases.create "$payload")"
    ok="$(printf '%s' "$res" | jq -r '.ok')"
    if [ "$ok" = "true" ]; then
      cid="$(printf '%s' "$res" | jq -r '.canvas_id')"
      echo "canvas_id: $cid"
      echo "url: https://app.slack.com/client/$TEAM_ID/$cid"
    else
      printf '%s' "$res" | jq '{ok, error}'; exit 1
    fi
    ;;

  canvas-edit)
    cid="${1:-}"; shift || true
    op="insert_at_end"
    case "${1:-}" in insert_at_end|insert_at_start|replace) op="$1"; shift ;; esac
    md="${1:-}"; [ -n "$md" ] || md="$(cat)"
    [ -n "$cid" ] || die "usage: canvas-edit <canvasId> [op] <markdown>"
    payload="$(jq -n --arg id "$cid" --arg op "$op" --arg m "$md" \
      '{canvas_id:$id, changes:[{operation:$op, document_content:{type:"markdown", markdown:$m}}]}')"
    call canvases.edit "$payload" | jq '{ok, error}'
    ;;

  *)
    grep '^#' "$0" | sed 's/^# \{0,1\}//' | sed '/^!/d'
    exit 1
    ;;
esac

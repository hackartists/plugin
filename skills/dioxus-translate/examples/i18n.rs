//! Example i18n module — place one `i18n.rs` per page/feature directory.
//! Struct name convention: `<Component>Translate`.

use dioxus_translate::*;

translate! {
    NotificationsTranslate;
    // Simple static strings
    panel_title: { en: "Notifications", ko: "알림" },
    mark_all_read: { en: "Mark all as read", ko: "모두 읽음" },
    empty: { en: "No notifications yet", ko: "새 알림이 없습니다" },

    // Strings with placeholders — interpolate with `.replace()` at the call site
    reply_title: { en: "{name} replied to your comment", ko: "{name}님이 답글을 남겼습니다" },
    space_invite_title: { en: "{name} invited you to {space}", ko: "{name}님이 {space}에 초대했습니다" },

    // Multi-line entries for longer text
    action_ongoing_title: {
        en: "New action ongoing: {action_title}",
        ko: "새 활동 시작: {action_title}",
    },

    // Relative-time strings
    relative_now: { en: "just now", ko: "방금" },
    relative_minute: { en: "{n}m ago", ko: "{n}분 전" },
    relative_hour: { en: "{n}h ago", ko: "{n}시간 전" },
    relative_day: { en: "{n}d ago", ko: "{n}일 전" },
}

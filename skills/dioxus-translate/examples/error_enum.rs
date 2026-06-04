//! Example error enum combining `thiserror::Error` (log/debug messages) with
//! `#[derive(Translate)]` (user-facing localized messages).

use dioxus_translate::Translate;
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Error, Serialize, Deserialize, Translate, Clone)]
pub enum NotificationsError {
    #[error("inbox entry not found")]
    #[translate(en = "Notification not found", ko = "알림을 찾을 수 없습니다")]
    InboxEntryNotFound,

    #[error("mark-read failed")]
    #[translate(en = "Failed to mark as read", ko = "읽음 처리에 실패했습니다")]
    MarkReadFailed,

    // No #[translate] attribute: variant name "ListFailed" is used as the string.
    #[error("list failed")]
    ListFailed,

    // `#[translate(from)]` delegates to the inner type's Translate impl.
    // Requires a single-field tuple variant; pairs with thiserror's #[from].
    // #[error("{0}")]
    // #[translate(from)]
    // SpaceReward(#[from] SpaceRewardError),
}

pub fn show_error(err: &NotificationsError, lang: &dioxus_translate::Language) {
    // Localized user-facing message:
    let user_message: &'static str = err.translate(lang);
    // Developer/log message from thiserror:
    let log_message = err.to_string();
    tracing::warn!("{log_message}");
    let _ = user_message; // render in a toast / banner
}

// --- Option enums for dropdowns -------------------------------------------

#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize, Translate)]
pub enum TeamRole {
    #[default]
    #[translate(en = "Member", ko = "멤버")]
    Member,
    #[translate(en = "Admin", ko = "관리자")]
    Admin,
}

pub fn role_options(lang: &dioxus_translate::Language) -> Vec<(TeamRole, String)> {
    // The derive generates VARIANTS (unit variants) and variants(&lang).
    TeamRole::VARIANTS
        .iter()
        .copied()
        .zip(TeamRole::variants(lang))
        .collect()
}

//! Example component consuming translations via `use_translate()`.

use dioxus::prelude::*;
use dioxus_translate::{use_language, use_translate};

use super::i18n::NotificationsTranslate;

#[component]
pub fn NotificationItem(name: String, created_at: i64, now: i64) -> Element {
    // Reactive: re-renders when the global language changes.
    let tr: NotificationsTranslate = use_translate();
    // Raw language signal, when the Language value itself is needed.
    let lang = use_language();
    let _current = lang();

    let title = tr.reply_title.replace("{name}", &name);

    rsx! {
        div { class: "notification-item",
            h2 { "{tr.panel_title}" }
            div { class: "notification-item__title", "{title}" }
            button { "{tr.mark_all_read}" }
        }
    }
}

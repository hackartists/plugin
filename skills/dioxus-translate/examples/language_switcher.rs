//! Example language selector — explicit selection and toggle patterns.
//!
//! Assumes the consuming crate enables the `ko` feature of dioxus-translate
//! (`features = ["ko"]`). If the crate forwards the feature conditionally,
//! gate every `Language::Ko` reference with `#[cfg(feature = "ko")]` as shown
//! on the Korean button below.

use dioxus::prelude::*;
use dioxus_translate::{set_language, use_language, Language};

/// Settings-panel style: explicit per-language buttons.
#[component]
pub fn LanguageSettings() -> Element {
    let lang = use_language();
    let current = lang();

    rsx! {
        div { class: "language-settings",
            button {
                class: if current == Language::En { "active" } else { "" },
                onclick: move |_| set_language(Language::En),
                "English"
            }
            // Gate Korean-specific code when the `ko` feature is conditional.
            button {
                class: if current == Language::Ko { "active" } else { "" },
                onclick: move |_| set_language(Language::Ko),
                "한국어"
            }
        }
    }
}

/// Toggle style: `switch()` flips En<->Ko AND persists to
/// localStorage + the `language` cookie (web), keeping SSR in sync.
#[component]
pub fn LanguageToggle() -> Element {
    let lang = use_language();

    rsx! {
        button {
            onclick: move |_| {
                let _next = lang().switch();
            },
            "{lang()}"  // renders "en" or "ko"
        }
    }
}

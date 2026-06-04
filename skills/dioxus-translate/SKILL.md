---
name: dioxus-translate
description: This skill should be used when the user asks to "add i18n", "add translations", "create an i18n.rs file", "translate this component", "add Korean/English text", "use dioxus-translate", "add a translate! macro", "derive Translate", "switch language", or works with multi-language UI text in a Dioxus (Rust) application. Covers the translate! macro, Translate derive for enums, use_translate/use_language hooks, and language switching/persistence.
version: 0.1.0
---

# dioxus-translate: i18n for Dioxus

dioxus-translate is a Rust i18n library for the Dioxus framework. It generates type-safe
translation structs at compile time, so every UI string is a checked struct field rather
than a runtime string key. It supports English (`en`, always on) and Korean (`ko`, behind
the `ko` cargo feature), works on web (wasm), SSR/fullstack, and native (desktop/mobile)
targets, and persists the user's language choice via `localStorage` and a `language` cookie.

## Core Concepts

Three crates work together (typically only `dioxus-translate` is imported directly):

| Crate | Provides |
|-------|----------|
| `dioxus-translate` | `Language` enum, `use_translate()`, `use_language()`, `set_language()`, `translate::<T>()` |
| `dioxus-translate-macro` | `translate!` function-like macro, `#[derive(Translate)]` for enums |
| `dioxus-translate-types` | `Translator` trait (`fn en() -> Self`, `fn ko() -> Self`) |

Two distinct mechanisms:

1. **`translate!` macro** — generates a struct of `&'static str` fields for component UI text.
   Used in per-page/per-feature `i18n.rs` files. Consumed via `use_translate()`.
2. **`#[derive(Translate)]`** — implements `fn translate(&self, lang: &Language) -> &'static str`
   on an enum. Used for error enums and option/label enums (e.g. roles, statuses).

## Setup

Add to `Cargo.toml` (enable `ko` for Korean support):

```toml
[dependencies]
dioxus-translate = { version = "0.1", features = ["ko"] }
```

Without the `ko` feature, `Language::Ko` and all `ko:` translations are compiled out and
only English exists. Conditional code touching `Language::Ko` must be gated with
`#[cfg(feature = "ko")]` when the consuming crate forwards the feature.

## Workflow 1: Component Text via `translate!`

### Step 1 — Define translations in an `i18n.rs` next to the component

Convention: each page/feature directory owns an `i18n.rs` declaring one or more
`*Translate` structs named after the component (e.g. `HomeTranslate`, `NotificationsTranslate`).

```rust
use dioxus_translate::*;

translate! {
    NotificationsTranslate;
    panel_title: { en: "Notifications", ko: "알림" },
    mark_all_read: { en: "Mark all as read", ko: "모두 읽음" },
    empty: { en: "No notifications yet", ko: "새 알림이 없습니다" },
    reply_title: { en: "{name} replied to your comment", ko: "{name}님이 답글을 남겼습니다" },
}
```

Syntax rules:
- First token is the struct name, terminated by `;`.
- Each entry is `field_name: { en: "...", ko: "..." },` — trailing commas allowed.
- Values must be string literals. Each field becomes `pub field_name: &'static str`.
- `{placeholder}` tokens are plain text — interpolate at the call site with `.replace()`.

The macro expands to a `pub struct` with `#[derive(Debug, Clone, PartialEq)]`, a
`new(lang: &Language) -> Self` constructor, and a `Translator` impl (`en()`/`ko()`).

### Step 2 — Consume in the component with `use_translate()`

```rust
use dioxus_translate::*;

#[component]
pub fn NotificationPanel() -> Element {
    let tr: NotificationsTranslate = use_translate();

    rsx! {
        div { class: "panel",
            h2 { "{tr.panel_title}" }
            button { "{tr.mark_all_read}" }
        }
    }
}
```

`use_translate()` is reactive: it reads the global language signal, so components re-render
on language change. The local binding is conventionally named `tr`.

### Step 3 — Interpolate placeholders with `.replace()`

There is no built-in interpolation. Fields are `&'static str`; substitute manually:

```rust
let title = tr.reply_title.replace("{name}", &user_name);
```

## Workflow 2: Enum Labels via `#[derive(Translate)]`

For error enums and selectable-option enums, derive `Translate` and annotate variants:

```rust
use dioxus_translate::Translate;
use thiserror::Error;

#[derive(Debug, Error, Serialize, Deserialize, Translate, Clone)]
pub enum NotificationsError {
    #[error("inbox entry not found")]
    #[translate(en = "Notification not found", ko = "알림을 찾을 수 없습니다")]
    InboxEntryNotFound,

    #[error("mark-read failed")]
    #[translate(en = "Failed to mark as read", ko = "읽음 처리에 실패했습니다")]
    MarkReadFailed,
}
```

Usage: `err.translate(&lang)` returns the localized `&'static str`.

Key behaviors:
- Variants without `#[translate(...)]` fall back to the variant name as the English string.
- Works on unit, struct (`{ .. }`), and tuple (`(..)`) variants.
- `#[translate(from)]` on a single-field tuple variant delegates to the inner type's
  `Translate` impl — useful for nested error enums:
  ```rust
  #[error("{0}")]
  #[translate(from)]
  SpaceReward(#[from] SpaceRewardError),
  ```
- The derive also generates `EnumName::VARIANTS` (unit variants only) and
  `EnumName::variants(&lang) -> Vec<String>` — handy for populating `<select>` options.

## Language Access and Switching

```rust
use dioxus_translate::{use_language, set_language, Language};

let lang = use_language();          // Signal<Language>; read with lang()
let current: Language = lang();

set_language(Language::Ko);         // set explicitly (e.g. settings panel buttons)
let next = current.switch();        // toggle En <-> Ko; persists to localStorage + cookie
```

- `Language::switch()` flips the language, writes `localStorage["language"]`, and sets a
  `language=<code>; path=/` cookie (web only) so SSR renders the right language.
- `set_language()` only updates the signal; pair with persistence when needed.
- `set_initial_language(lang)` restores a saved preference at app startup (native/desktop
  targets hydrate from WebView localStorage before first render).
- `lang.to_string()` / `"ko".parse::<Language>()` convert to/from `"en"`/`"ko"` codes;
  unknown codes parse as `En`.

### SSR / fullstack behavior

On non-wasm targets, `use_language()` detects context at runtime: during an HTTP render it
reads the `language` cookie from the request (`language_from_cookie()`); on a native client
it uses the global signal. No app code changes are required — just be aware the cookie set
by `switch()` is what makes server-rendered HTML match the client language.

## Non-Component Contexts

Outside components (helpers, services), construct a translation struct directly:

```rust
let tr = NotificationsTranslate::new(&lang);       // from a Language value
let tr: NotificationsTranslate = translate(&lang); // equivalent free function
```

Pass `&tr` and/or `&lang` into plain helper functions rather than calling hooks there.

## Conventions (from the Ratel codebase)

- One `i18n.rs` per page/feature directory; struct named `<Component>Translate`.
- Bind as `let tr: XxxTranslate = use_translate();` at the top of the component.
- Snake_case field names describing the string's role (`panel_title`, `empty`, `save_button`).
- Placeholders in `{curly_braces}`, resolved with chained `.replace()` calls.
- Error enums live in `types/error.rs` combining `thiserror::Error` + `Translate` so the
  same enum yields log messages (`#[error]`) and user-facing localized text (`#[translate]`).

## Additional Resources

### Reference Files

- **`references/api-reference.md`** — complete API surface: `Language` methods, hook
  signatures, macro expansion details, feature flags, SSR/cookie internals.

### Example Files

- **`examples/i18n.rs`** — a complete `translate!` i18n module with placeholders.
- **`examples/component.rs`** — component consuming translations, interpolation helper.
- **`examples/error_enum.rs`** — `#[derive(Translate)]` error enum with `from` delegation.
- **`examples/language_switcher.rs`** — settings-panel language selector using `set_language`.

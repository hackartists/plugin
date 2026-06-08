# Dioxus Page Implementation

A **page** is a route target plus everything it owns: its component, translations, shared
state, layout, child components, and hooks. Everything page-related lives under one directory
so a page can be read, moved, or deleted as a unit.

## Directory Layout

```
src/pages/{path}/
├── mod.rs            # module wiring — declares submodules, re-exports the page component
├── page.rs           # MANDATORY — the page component (one `*Page` fn)
├── i18n.rs           # MANDATORY — dioxus-translate translations for this page
├── context.rs        # RECOMMENDED — page context shared with components/children
├── layout.rs         # OPTIONAL — layout wrapping this page or its child routes
├── components/       # components used by this page (or shared with children)
│   ├── mod.rs
│   └── *.rs          # one component per file
└── hooks/            # hooks used by this page (or shared with children)
    ├── mod.rs
    └── *.rs          # one hook per file
```

`{path}` mirrors the URL — e.g. `/console/settings` → `src/pages/console/settings/`.
Child pages nest as subdirectories so a parent `context.rs`/`layout.rs` is shared downward.

## File Responsibilities

| File | Required | Holds |
|------|----------|-------|
| `page.rs` | yes | The single `*Page` component — composes layout, context, child components |
| `i18n.rs` | yes | `translate! { … }` block for all of this page's UI text |
| `context.rs` | recommended | Page-scoped context: shared signals, loaders, and the API-calling methods |
| `layout.rs` | optional | Layout shell + `Outlet::<Route>` for child routes; auth guards |
| `components/*` | as needed | One component per file; split when `page.rs` grows |
| `hooks/*` | as needed | One hook per file; reusable logic for this page subtree |

## `page.rs` — the page component

```rust
use super::components::*;
use super::context::use_settings_context_provider;
use super::i18n::SettingsTranslate;
use dioxus::prelude::*;
use dioxus_translate::*;

#[component]
pub fn SettingsPage() -> Element {              // unique name, `Page` suffix
    let ctx = use_settings_context_provider();  // provide page context at the top
    let tr: SettingsTranslate = use_translate();

    rsx! {
        section { class: "settings",
            h1 { "{tr.title}" }
            SettingsProfileCard {}              // child components carry the detail
            SettingsNotificationList {}
        }
    }
}
```

- **Naming**: the component is a unique name ending in `Page` — `SettingsPage`, `SpaceAnalyzeDetailPage`.
  Never bare `Page` (collides across modules).
- **Keep `page.rs` thin**: it composes; the work lives in `components/*`. Any single `rsx!`
  block over ~300 lines must be split into a child component.
- **No direct API calls** — see below.

## `i18n.rs` — translations

```rust
use dioxus_translate::*;

translate! {
    SettingsTranslate;

    title: { en: "Settings", ko: "설정" },
    save:  { en: "Save",     ko: "저장" },
}
```

Consume in any component of the page subtree:

```rust
let tr: SettingsTranslate = use_translate();
rsx! { button { "{tr.save}" } }
```

See skill `hackartist-plugins:dioxus-translate` for the full `translate!` / `#[derive(Translate)]` API.

## `context.rs` — page state + the API boundary

The page context owns shared signals/loaders **and** the methods that mutate them. Components
call context methods; they never touch server functions directly. (Same four-function pattern as
app-wide context — see `references/context.md`.)

```rust
use by_macros::DioxusController;
use dioxus::prelude::*;

#[derive(Clone, Copy, DioxusController)]
pub struct UseSettingsContext {
    pub profile: Loader<Profile>,
    pub saving: Signal<bool>,
}

pub fn use_settings_context_provider() -> UseSettingsContext {
    let profile = use_loader(|| async move { get_profile_handler().await });
    use_context_provider(|| UseSettingsContext { profile, saving: Signal::new(false) })
}

pub fn use_settings_context() -> UseSettingsContext { use_context() }

impl UseSettingsContext {
    // The API call is wrapped here — components call `ctx.save(...)`, not the handler.
    pub async fn save(&self, req: UpdateProfileRequest) -> Result<()> {
        self.saving.set(true);
        let res = update_profile_handler(req).await;
        self.profile.restart();        // refresh the loader after mutation
        self.saving.set(false);
        res.map(|_| ())
    }
}
```

## `components/*` — sub-components

One component per file. A sub-component's own UI text does **not** have to live in the page's
`i18n.rs` — define a `translate!` block **inline in the component's own file** when the strings
are local to that component. Reserve the page `i18n.rs` for text shared across the page subtree.

**Recommended: put the component's `translate!` block at the end of the file**, below the
component, so the component reads first and its translations sit as an appendix.

```rust
use dioxus::prelude::*;
use dioxus_translate::*;

#[component]
fn SettingsProfileCard() -> Element {
    let ctx = use_settings_context();
    let tr: ProfileCardTranslate = use_translate();   // component-local translations
    rsx! {
        div { class: "card",
            label { "{tr.display_name}" }
            button { "{tr.save}" }
        }
    }
}

// ── i18n (component-local) — kept at the END of the file ──────────────────────
translate! {
    ProfileCardTranslate;

    display_name: { en: "Display name", ko: "표시 이름" },
    save:         { en: "Save",         ko: "저장" },
}
```

Use the page `i18n.rs` vs. an inline block by scope:

| Text scope | Where |
|------------|-------|
| Shared across the page + several components | page `i18n.rs` |
| Local to a single component | inline `translate!` at the end of that component's file |

## `layout.rs` — optional shell for child routes

```rust
#[component]
fn ConsoleLayout() -> Element {
    let auth = use_auth_context();
    if !auth.hydrated()      { return rsx! { LoadingSpinner {} }; }
    if !auth.is_signed_in()  { return rsx! { Navigate { to: Route::HomePage {} } }; }
    rsx! {
        div { class: "console-shell",
            ConsoleSidebar {}
            Outlet::<Route> {}     // child pages render here
        }
    }
}
```

Wire it in the `Route` enum with `#[layout(ConsoleLayout)]` — see `references/router.md`.

## `mod.rs` — wiring

```rust
mod page;
pub mod components;
pub mod context;
pub mod hooks;
pub mod i18n;
mod layout;

pub use page::*;          // re-export the page component for the Route enum
```

## The API Rule

**Components never call server functions directly.** Routing API access through the context (or a
`use_action`) keeps loading/error state and cache invalidation in one place.

```rust
// ❌ component reaches for the handler itself
let mut save = use_action(update_profile_handler);
save.call(req);

// ✅ go through the context method (which wraps the handler + refreshes the loader)
let ctx = use_settings_context();
rsx! { button { onclick: move |_| async move { ctx.save(req.clone()).await.ok(); }, "Save" } }
```

For reads, expose a `Loader`/`use_resource` on the context and let components read its value —
don't `use_resource` a handler inside a leaf component.

## Conventions Checklist

- Page component name is unique and ends in `Page`.
- `page.rs` and `i18n.rs` always present; `context.rs` present whenever state is shared.
- One component per file under `components/`; one hook per file under `hooks/`.
- Component-local text uses an inline `translate!` block at the **end** of the component's file; only shared text goes in the page `i18n.rs`.
- No single `rsx!` block exceeds ~300 lines — split into child components.
- No direct server-function calls in components — go through context methods or `use_action`.
- Child pages nest as subdirectories to inherit the parent `context.rs` / `layout.rs`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Component named `Page` (not unique) | Use a unique `*Page` name — `SettingsPage` |
| 400-line `rsx!` in `page.rs` | Extract child components into `components/*` |
| `update_x_handler().await` inside a component | Wrap the call in a context method or `use_action` |
| `use_resource(handler)` in a leaf component | Expose a `Loader` on the page context; read its value |
| Many components in one file | One component per file |
| Missing `i18n.rs`, hardcoded strings | Add `translate!` block; read via `use_translate()` |
| Page context provided in a child | Provide once in `page.rs` (or the layout above it) |

## Example File

See `examples/page.rs` for a complete page: `page.rs` + `i18n.rs` + `context.rs` + a child
component, all in one file for reference.

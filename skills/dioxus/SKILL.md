---
name: dioxus
description: Use when building any Dioxus (Rust) application — new project setup, context providers, routing, server functions, reactive state, signals, or any cross-cutting pattern. Load this skill for all Dioxus work.
---

# Dioxus

Dioxus is a Rust framework for fullstack web/desktop apps. All patterns live in this skill.

## Reference Files

| Topic | File |
|-------|------|
| Project setup, Cargo.toml, app entry point | `references/project-setup.md` |
| Tailwind CSS setup (dx-cli built-in, no npm) | `references/tailwind.md` |
| Context providers (`provide_context`, `consume_context`) | `references/context.md` |
| Routing, layouts, auth guards, navigation | `references/router.md` |
| Page implementation (dir layout, `*Page`, i18n, page context) | `references/page.md` |
| Server functions (`#[get]`/`#[post]`), extractors | `references/server.md` |
| Signals, `use_resource`, `use_action`, `use_effect`, `use_memo` | `references/state.md` |

## Quick Reference

### Imports

```rust
use dioxus::prelude::*;         // everything: signals, hooks, router, rsx, spawn, …
use by_macros::DioxusController; // context struct derive
```

### App Entry Point

```rust
#[component]
pub fn App() -> Element {
    use_auth_context_provider();        // context providers at root, deps-first order
    use_my_assets_context_provider();
    rsx! {
        document::Stylesheet { href: MAIN_CSS }
        Router::<Route> {}
    }
}
```

### Context (→ `references/context.md`)

```rust
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext { pub user: Signal<Option<User>> }  // None = not signed in

pub fn provide_auth_context()      -> UseAuthContext { provide_context(UseAuthContext { … }) }         // non-hook
pub fn use_auth_context_provider() -> UseAuthContext { let me = use_loader(|| async move { … }); use_context_provider(|| UseAuthContext { user: Signal::new(me.value()…) }) } // hook — App root
pub fn use_auth_context()          -> UseAuthContext { use_context::<UseAuthContext>() }                // hook — component body
pub fn consume_auth_context()      -> UseAuthContext { consume_context::<UseAuthContext>() }            // non-hook — spawn/closures
```

### Routing (→ `references/router.md`)

```rust
#[derive(Routable, Clone, Debug, PartialEq)]
#[rustfmt::skip]
enum Route {
    #[layout(NavLayout)]
        #[route("/")]           HomePage {},
        #[nest("/console")]
        #[layout(ConsoleLayout)]
            #[route("")]        ConsolePage {},
        #[end_layout]
        #[end_nest]
    #[end_layout]
}
```

### Page Implementation (→ `references/page.md`)

Everything a page owns lives under `src/pages/{path}/` ({path} mirrors the URL):

```
src/pages/settings/
├── mod.rs            # `mod page; pub use page::*;` + submodules
├── page.rs           # MANDATORY — the `*Page` component (thin; composes children)
├── i18n.rs           # MANDATORY — translate! { … } for this page's text
├── context.rs        # RECOMMENDED — shared signals/loaders + API-calling methods
├── layout.rs         # OPTIONAL — shell + Outlet::<Route> for child routes
├── components/*.rs    # one component per file (split when rsx! > ~300 lines)
└── hooks/*.rs         # one hook per file
```

Rules: page component has a unique name with `Page` suffix; one component/hook per file;
**components never call server functions directly** — go through a context method or `use_action`.
A sub-component's own text can be an inline `translate!` block at the **end** of its file; only
shared text goes in the page `i18n.rs`.

```rust
#[component]
pub fn SettingsPage() -> Element {
    use_settings_context_provider();        // provide page context at the top
    let tr: SettingsTranslate = use_translate();
    rsx! { h1 { "{tr.title}" } SettingsProfileCard {} }   // children carry the detail
}
```

### State (→ `references/state.md`)

```rust
let mut count = use_signal(|| 0);          // local state
let data  = use_resource(|| async move {}); // auto-runs, re-runs on dep change
let mut save = use_action(server_fn);      // runs on demand (mutations)
use_effect(move || { let _ = sig.read(); });// side effects, subscribes to signals
let memo  = use_memo(move || count() * 2); // derived; read as memo()
static N: GlobalSignal<i32> = Signal::global(|| 0); // app-level
```

### Server Functions (→ `references/server.md`)

```rust
#[get("/api/resource")]
pub async fn get_resource_handler() -> Result<Response> { … }

#[post("/api/resource", auth: AuthUser)]  // auth is a server-only extractor
pub async fn create_resource_handler(body: CreateRequest) -> Result<Response> { … }
```

## i18n

See skill `hackartist-plugins:dioxus-translate` for the `translate!` macro and `#[derive(Translate)]`.

## Dioxus 0.5+ Syntax

See skill `hackartist-plugins:dioxus-knowledge-patch` for signals replacing `use_state`, new RSX patterns, asset!(), stores.

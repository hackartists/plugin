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
| Context providers (`provide_context`, `consume_context`) | `references/context.md` |
| Routing, layouts, auth guards, navigation | `references/router.md` |
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

pub fn provide_auth_context()      -> UseAuthContext { provide_context(UseAuthContext { … }) }
pub fn use_auth_context_provider() -> UseAuthContext { use_context_provider(|| UseAuthContext { … }); /* + spawn */ }
pub fn consume_auth_context()      -> UseAuthContext { consume_context::<UseAuthContext>() }
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

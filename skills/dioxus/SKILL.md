---
name: dioxus
description: Use when starting a new Dioxus project, scaffolding a fullstack Rust web app, setting up Cargo.toml features, structuring app entry point, or needing an overview of which dioxus-* skills to invoke for specific patterns.
---

# Dioxus Hub

Dioxus is a Rust framework for fullstack web/desktop apps. This hub covers project setup and entry-point structure. For deep-dive patterns, invoke the satellite skills listed below.

## Satellite Skills

| Task | Skill |
|------|-------|
| Context providers / global services (use_*_context_provider, consume_*_context) | `hackartist-plugins:dioxus-context` |
| Routing, layouts, auth guards | `hackartist-plugins:dioxus-router` |
| Server functions (`#[get]`/`#[post]`) | `hackartist-plugins:dioxus-server` |
| Signals, state, effects, resources | `hackartist-plugins:dioxus-state` |
| i18n / translations | `hackartist-plugins:dioxus-translate` |
| Dioxus 0.5+ syntax changes | `hackartist-plugins:dioxus-knowledge-patch` |

When doing comprehensive planning (new project, multi-feature work), also invoke all satellite skills above for full pattern coverage.

## Cargo.toml Feature Flags

```toml
[dependencies]
dioxus         = { workspace = true }          # features enabled per-target
dioxus-translate = { workspace = true }
by-macros      = { workspace = true }          # #[get]/#[post] server fns
manganis       = { workspace = true }          # asset!() macro

[features]
default  = ["web", "server", "fullstack"]
web      = ["dioxus/web", ...]
server   = ["fullstack", "dioxus/server", "dep:tokio", "dep:axum", ...]
fullstack = ["dioxus/fullstack"]
desktop  = ["dioxus/desktop", "dep:reqwest", "dep:tokio", ...]
```

## App Entry Point Pattern

```rust
// src/app.rs
#[component]
pub fn App() -> Element {
    // 1. wire up context providers at root — order matters when one reads another
    ThemeService::init();
    use_auth_context_provider();           // UseAuthContext
    use_my_assets_context_provider();      // reads UseAuthContext, so comes after
    use_popup_context_provider();          // UsePopupContext

    rsx! {
        document::Stylesheet { href: MAIN_CSS }
        Router::<Route> {}
        PopupZone {}           // renders context-driven overlay
    }
}
```

```rust
// src/main.rs (web + server)
fn main() {
    dioxus::launch(App);
}
```

## Directory Convention

```
src/
  app.rs            App component — providers + Router
  route.rs          Route enum
  assets.rs         asset!() constants
  features/
    auth/
      mod.rs        pub use re-exports
      context.rs    UseAuthContext + use_init_auth/use_auth_context
      controllers/  #[get]/#[post] server functions
      types.rs      shared request/response/error types
      extractors.rs (server-only) axum FromRequestParts impls
      services.rs   (server-only) external API calls
      i18n.rs       translate! struct
  pages/
    home/
      mod.rs
      page.rs
      i18n.rs
  components/       shared UI primitives
  popup/            PopupService + PopupZone
  hooks/            use_loader, use_sleep, ...
  theme/            ThemeService
  config/           server config (env vars)
  types/            cross-cutting types (EntityType, Partition)
```

## Quick Reference

| Operation | Syntax |
|-----------|--------|
| Launch app | `dioxus::launch(App)` |
| Render assets | `asset!("/assets/logo.png")` |
| Document head | `document::Stylesheet`, `document::Script`, `document::Meta` |
| Conditional compile | `#[cfg(feature = "server")]` / `#[cfg(feature = "web")]` |
| Provider order | Init providers top-down; readers after writers |

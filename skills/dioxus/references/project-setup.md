# Dioxus Project Setup

## Cargo.toml Feature Flags

```toml
[dependencies]
dioxus          = { workspace = true }
dioxus-translate = { workspace = true }
by-macros       = { workspace = true }   # #[get]/#[post], DioxusController
manganis        = { workspace = true }   # asset!() macro
serde           = { workspace = true }
thiserror       = { workspace = true }

# Web-only
wasm-bindgen           = { workspace = true, optional = true }
gloo-net               = { version = "0.6", features = ["http"], optional = true }

# Server-only
tokio              = { workspace = true, optional = true }
axum               = { workspace = true, optional = true }
tower-sessions     = { workspace = true, optional = true }

[features]
default   = ["web", "server", "fullstack"]
web       = ["dioxus/web", "dep:wasm-bindgen", "dep:gloo-net"]
server    = ["fullstack", "dioxus/server", "dep:tokio", "dep:axum", "dep:tower-sessions"]
fullstack = ["dioxus/fullstack"]
desktop   = ["dioxus/desktop"]   # thin client: no server, talks to remote API
```

## Dioxus.toml

```toml
[application]
name = "my-app"
default_platform = "web"

[web.app]
title = "My App"
```

## Directory Convention

```
src/
  app.rs              App component — context providers + Router
  route.rs            Route enum
  assets.rs           asset!() constants
  features/
    auth/
      mod.rs          pub use re-exports
      context.rs      UseAuthContext + the three context fns
      controllers/    #[get]/#[post] server functions
      types.rs        shared request/response/error types (all targets)
      extractors.rs   (server-only) axum FromRequestParts impls
      services.rs     (server-only) external API calls
      i18n.rs         translate! struct
    asset/
      context.rs
      controllers/
      types.rs
  pages/
    home/
      mod.rs
      page.rs
      i18n.rs
  components/         shared UI primitives
  popup/              PopupService + PopupZone
  hooks/              use_loader, custom hooks
  theme/              ThemeService
  config/             server config (env vars)
  types/              cross-cutting types (EntityType, Partition)
```

## App Entry Point

```rust
// src/app.rs
#[component]
pub fn App() -> Element {
    // Context providers at root — order matters: consumers must come after providers
    use_auth_context_provider();
    use_my_assets_context_provider();  // reads auth ctx → must be after
    use_popup_context_provider();

    rsx! {
        document::Meta { name: "viewport", content: "width=device-width, initial-scale=1.0" }
        document::Stylesheet { href: MAIN_CSS }
        Router::<Route> {}
        PopupZone {}
    }
}

// src/main.rs
fn main() {
    dioxus::launch(App);
}
```

## Assets

```rust
// src/assets.rs
use dioxus::prelude::*;

pub const MAIN_CSS:   Asset = asset!("/assets/main.css");
pub const MAIN_JS:    Asset = asset!("/assets/main.js");
pub const LOGO:       Asset = asset!("/assets/logo.png");
```

## lib.rs re-exports

```rust
// src/lib.rs — wildcard re-export lets every module do `use crate::*;`
pub use dioxus::prelude::*;
pub use by_macros::*;
pub mod features;
pub mod pages;
pub mod components;
pub mod route;
pub use route::Route;
// … etc
```

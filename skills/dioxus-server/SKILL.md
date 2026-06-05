---
name: dioxus-server
description: Use when writing server functions in a Dioxus fullstack app with by-macros #[get]/#[post], adding axum extractors to server functions, gating server-only code with cfg(feature = "server"), or calling server functions from client components.
---

# dioxus-server: Server Functions in Dioxus (by-macros)

Server functions bridge client components and server logic. The `#[get]`/`#[post]` macros from `by-macros` emit a wasm client stub and a real axum handler from the same function signature.

## Basic Server Function

```rust
// features/auth/controllers/get_me.rs
use crate::features::auth::types::{AuthError, GetMeResponse};
use crate::*;

#[cfg(feature = "server")]
use crate::features::auth::extractors::OptionalUser;

#[get("/api/auth/me", user: OptionalUser)]
pub async fn get_me_handler() -> std::result::Result<GetMeResponse, AuthError> {
    Ok(GetMeResponse { user: user.0 })
}
```

- Route path → `#[get("/api/path")]` or `#[post("/api/path")]`
- Extractors → listed after the path as `name: Type` pairs
- Return type → `std::result::Result<Response, Error>` (use full path, not `crate::Result`)
- Extractor params are injected server-side only; the wasm stub signature omits them

## Calling from Client

```rust
// Client component — looks like a plain async call
use super::controllers::get_me_handler;

let resp = get_me_handler().await?;
```

The macro generates a matching client stub that serializes args, POSTs to the route, and deserializes the response. No `gloo_net`/`fetch` needed.

## Axum Extractors

Custom extractors implement `axum::extract::FromRequestParts` and are gated `#[cfg(feature = "server")]`:

```rust
// features/auth/extractors.rs
#![cfg(feature = "server")]

pub struct User(pub UserDto);
pub struct OptionalUser(pub Option<UserDto>);

impl<S: Send + Sync> FromRequestParts<S> for User { ... }
impl<S: Send + Sync> FromRequestParts<S> for OptionalUser { ... }
```

## Module Layout

```
features/auth/
  controllers/
    mod.rs           pub use re-exports; SESSION_USER_KEY const
    get_me.rs        #[get("/api/auth/me")]
    send_code.rs     #[post("/api/auth/send-code")]
    logout.rs        #[post("/api/auth/logout")]
  extractors.rs      #[cfg(feature = "server")] FromRequestParts impls
  services.rs        #[cfg(feature = "server")] external API calls (SES, Google)
  types.rs           request/response/error types (compiles on all targets)
```

## Feature Gating

```rust
// Always compiled — wasm bundle needs the client stub
pub mod controllers;

// Server-only
#[cfg(feature = "server")]
pub mod extractors;

#[cfg(feature = "server")]
pub mod services;
```

## Error Types

Errors must implement `serde::Serialize + Deserialize` so they round-trip through the server-fn wire format:

```rust
#[derive(Debug, thiserror::Error, serde::Serialize, serde::Deserialize)]
pub enum AuthError {
    #[error("not signed in")]
    NotSignedIn,
    #[error("server error: {0}")]
    Server(String),
}
```

## Quick Reference

| Pattern | Syntax |
|---------|--------|
| GET handler | `#[get("/api/path")]` |
| POST handler | `#[post("/api/path")]` |
| Required auth | `user: User` extractor param |
| Optional auth | `user: OptionalUser` extractor param |
| Server-only code | `#[cfg(feature = "server")]` |
| Web-only code | `#[cfg(feature = "web")]` |
| Call from client | `xxx_handler(args).await?` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `crate::Result<T>` as return type | Use `std::result::Result<T, E>` — `crate::Result` is a server-only alias |
| Importing extractors outside `#[cfg(feature = "server")]` | Gate extractor imports with `#[cfg(feature = "server")]` |
| Adding extractors to client call site | Extractor params are server-only — client stub has a different signature |
| Error type doesn't implement `Serialize` | Server-fn wire format requires `Serialize + Deserialize` on error |

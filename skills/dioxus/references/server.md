# Dioxus Server Functions

Server functions bridge client components and server logic. `#[get]`/`#[post]` from `by-macros` emit a wasm client stub and a real axum handler from the same function signature.

## Basic Server Function

```rust
// features/auth/controllers/get_me.rs
use crate::*;  // brings in #[get]/#[post] macros via by-macros

#[cfg(feature = "server")]
use crate::features::auth::extractors::OptionalUser;

#[get("/api/auth/me", user: OptionalUser)]
pub async fn get_me_handler() -> std::result::Result<GetMeResponse, AuthError> {
    Ok(GetMeResponse { user: user.0 })
}
```

- Route path → `#[get("/api/path")]` or `#[post("/api/path")]`
- Server-only extractors → listed after path as `name: Type` pairs (omitted from wasm stub)
- Return type → **`std::result::Result<T, E>`** — use full path, not `crate::Result`

## Calling from Client

```rust
// Component or context method — looks like a plain async call
let resp = get_me_handler().await?;
```

The macro generates a client stub that serializes args, POSTs to the route, and deserializes the response. No manual `gloo_net`/`fetch` needed.

## use_action — Preferred for Mutations

```rust
let mut save = use_action(create_resource_handler);

rsx! {
    button { onclick: move |_| save.call(form_data.clone()), "Save" }
    if save.pending() { p { "Saving..." } }
}
```

See `references/state.md` for full `use_action` API.

## use_loader — Preferred for Initial Data Load

```rust
let me = use_loader(|| async move { get_me_handler().await });
// me.value() → Some(T) on success
// me.pending() → true while in-flight
```

## Axum Extractors (Server-Only)

Extractors run server-side only and are gated `#[cfg(feature = "server")]`:

```rust
// features/auth/extractors.rs
#![cfg(feature = "server")]

use axum::extract::FromRequestParts;
use axum::http::request::Parts;

/// Signed-in user — rejects with 401 when session is missing.
pub struct AuthUser(pub UserDto);

/// Optional user — never rejects; `None` for anonymous callers.
pub struct OptionalUser(pub Option<UserDto>);

impl<S: Send + Sync> FromRequestParts<S> for AuthUser {
    type Rejection = AuthError;

    async fn from_request_parts(parts: &mut Parts, state: &S)
        -> Result<Self, Self::Rejection>
    {
        // read session cookie, look up user in DB
        todo!()
    }
}

impl<S: Send + Sync> FromRequestParts<S> for OptionalUser {
    type Rejection = AuthError;

    async fn from_request_parts(parts: &mut Parts, state: &S)
        -> Result<Self, Self::Rejection>
    {
        // try auth, return None on missing session (never reject)
        todo!()
    }
}
```

## Module Layout

```
features/auth/
  controllers/
    mod.rs           pub use re-exports; SESSION_USER_KEY const
    get_me.rs        #[get("/api/auth/me", user: OptionalUser)]
    send_code.rs     #[post("/api/auth/send-code")]
    logout.rs        #[post("/api/auth/logout")]
  extractors.rs      #[cfg(feature = "server")] FromRequestParts
  services.rs        #[cfg(feature = "server")] external API calls
  types.rs           shared request/response/error types (ALL targets)
```

## Feature Gating

```rust
pub mod controllers;    // compiled everywhere: wasm needs the client stubs

#[cfg(feature = "server")]
pub mod extractors;

#[cfg(feature = "server")]
pub mod services;
```

## Error Types

Errors must `Serialize + Deserialize` to round-trip the server-fn wire format:

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
| Required auth extractor | `auth: AuthUser` in attribute |
| Optional auth extractor | `user: OptionalUser` in attribute |
| Server-only code | `#[cfg(feature = "server")]` |
| Web-only code | `#[cfg(feature = "web")]` |
| Call from client | `handler_fn(args).await?` |
| Mutation in component | `use_action(handler_fn)` |
| Read on mount | `use_loader(\|\| async move { handler_fn().await })` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `crate::Result<T>` as return type | Use `std::result::Result<T, E>` — `crate::Result` is server-only |
| Extractor import outside `#[cfg(feature = "server")]` | Gate the import |
| Extractor param at call site | Extractor params are server-only; wasm stub omits them |
| Error type missing `Serialize` | Server-fn wire format requires `Serialize + Deserialize` |

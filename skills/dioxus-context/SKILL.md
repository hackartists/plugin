---
name: dioxus-context
description: Use when adding a global service or shared state to a Dioxus app, creating a feature context struct with DioxusController, writing use_{name}_context_provider / consume_{name}_context / provide_{name}_context hooks, or implementing reactive side effects tied to context signals.
---

# dioxus-context: Context Providers in Dioxus

Context provides app-wide state without prop-drilling. Provide once at root; read anywhere in the tree.

## Three Required Functions Per Context

Every context exposes exactly these three functions:

```rust
// 1. provide_{name}_context — wraps Dioxus provide_context() (non-hook)
//    Can be called during rendering without hook constraints.
pub fn provide_auth_context() -> UseAuthContext { ... }

// 2. use_{name}_context_provider — hook: calls provide_auth_context + reactive setup
//    Call once at App root (or layout root). Must be inside a component.
pub fn use_auth_context_provider() -> UseAuthContext { ... }

// 3. consume_{name}_context — wraps Dioxus consume_context() (non-hook)
//    Can be called anywhere the Dioxus runtime is active (components, spawn, event handlers).
pub fn consume_auth_context() -> UseAuthContext { ... }
```

## Core Pattern

```rust
use by_macros::DioxusController;
use dioxus::prelude::*;

// Always derive DioxusController — never manually derive Clone + Copy.
// DioxusController generates Clone + Copy and signal accessor boilerplate.
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    pub hydrated: Signal<bool>,
}

// 1. provide_{name}_context: wraps provide_context() (not a hook)
pub fn provide_auth_context() -> UseAuthContext {
    provide_context(UseAuthContext {
        user: Signal::new(None),
        hydrated: Signal::new(false),
    })
}

// 2. use_{name}_context_provider: provides + reactive setup
pub fn use_auth_context_provider() -> UseAuthContext {
    let ctx = provide_auth_context();

    // Spawn async work directly — no use_effect wrapper needed
    #[cfg(feature = "web")]
    spawn(async move {
        // let resp = get_me_handler().await;
        // if let Ok(r) = resp { ctx.user.set(r.user); }
    });

    ctx
}

// 3. consume_{name}_context: wraps consume_context() (not a hook)
pub fn consume_auth_context() -> UseAuthContext {
    consume_context::<UseAuthContext>()
}
```

## Adding Methods

Implement business logic on the context struct. Use `&self` — signals use interior mutability.

```rust
impl UseAuthContext {
    pub fn is_signed_in(&self) -> bool {
        self.user.read().is_some()
    }

    pub async fn sign_out(&self) -> Result<()> {
        logout_handler().await?;
        self.user.set(None);
        Ok(())
    }
}
```

## Naming Conventions

| Purpose | Name |
|---------|------|
| Context struct | `UseFooContext` |
| Hook provider (with reactive setup) | `use_foo_context_provider()` |
| Bare provider (wraps provide_context) | `provide_foo_context()` |
| Consumer (wraps consume_context) | `consume_foo_context()` |
| Context field | `pub bar: Signal<T>` |

## Usage in App Root

```rust
pub fn App() -> Element {
    use_auth_context_provider();        // UseAuthContext
    use_my_assets_context_provider();   // UseMyAssets — reads auth ctx, so after
    use_popup_context_provider();       // UsePopupContext
    rsx! { Router::<Route> {} }
}
```

## Reactive Effects on Context

Use `use_effect` to flush/reset derived state when a signal changes. Always read the signal inside the closure to subscribe:

```rust
let auth = consume_auth_context();
let mut assets_ctx = consume_my_assets_context();

use_effect(move || {
    let _ = auth.user.read();        // subscribe — re-runs when user changes
    assets_ctx.assets.set(None);     // flush derived cache
    assets_ctx.loaded.set(false);
});
```

## Dioxus Context API Reference

| Function | Hook? | Use when |
|----------|-------|----------|
| `provide_context(val)` | No | Provide during rendering, no hook caching needed |
| `use_context_provider(\|\| val)` | Yes | Equivalent to `use_hook(\|\| provide_context(...))` |
| `consume_context::<T>()` | No | Read from anywhere: components, spawn, event handlers |
| `use_context::<T>()` | Yes | Read at component top-level only |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `use_init_foo` naming | Use `use_foo_context_provider` / `consume_foo_context` |
| Manual `#[derive(Clone, Copy)]` | Always use `#[derive(DioxusController)]` instead |
| `sign_out(&mut self)` | Use `&self` — Signal fields have interior mutability |
| Calling `use_context_provider` twice | Use `provide_context` exactly once — second call overwrites |
| Provider order wrong | Providers that depend on others must come after them |
| `Signal::write()` during render | Use `Signal::set()` in effects/handlers, not during render |
| Missing signal read in `use_effect` | Effect won't subscribe — read the signal inside the closure |

## Example File

See `examples/context.rs` for a complete context with all three functions and methods.

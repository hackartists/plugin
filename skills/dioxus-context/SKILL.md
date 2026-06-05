---
name: dioxus-context
description: Use when adding a global service or shared state to a Dioxus app, creating a feature context struct with DioxusController, writing use_{name}_context_provider / consume_{name}_context / provide_{name}_context hooks, or implementing reactive side effects tied to context signals.
---

# dioxus-context: Context Providers in Dioxus

Context provides app-wide state without prop-drilling. Provide once at root; read anywhere in the tree.

## Three Required Functions Per Context

Every context exposes exactly these three functions:

```rust
// 1. use_{name}_context_provider — hook called at App root (or layout root)
//    Sets up the context AND any reactive effects/loaders. Must be inside a component.
pub fn use_auth_context_provider() -> UseAuthContext { ... }

// 2. provide_{name}_context — bare provider with no hooks
//    Use when you need to create the context without hook setup (e.g. tests, nested re-provides).
pub fn provide_auth_context() -> UseAuthContext { ... }

// 3. consume_{name}_context — read the context anywhere in the tree
pub fn consume_auth_context() -> UseAuthContext { ... }
```

## Core Pattern

```rust
use by_macros::DioxusController;
use dioxus::prelude::*;

// Always derive DioxusController — never manually derive Clone + Copy
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    pub hydrated: Signal<bool>,
}

// provide_{name}_context: pure provider, no hooks
pub fn provide_auth_context() -> UseAuthContext {
    use_context_provider(|| UseAuthContext {
        user: Signal::new(None),
        hydrated: Signal::new(false),
    })
}

// use_{name}_context_provider: provides + sets up reactive behavior
pub fn use_auth_context_provider() -> UseAuthContext {
    let ctx = provide_auth_context();

    #[cfg(feature = "web")]
    use_effect(move || {
        spawn(async move {
            // let resp = get_me_handler().await;
            // if let Ok(r) = resp { ctx.user.set(r.user); }
            ctx.hydrated.set(true);
        });
    });

    ctx
}

// consume_{name}_context: read from anywhere in the tree
pub fn consume_auth_context() -> UseAuthContext {
    use_context::<UseAuthContext>()
}
```

## Adding Methods

Implement business logic on the context struct so callers don't need to know about signals:

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
| Hook provider (with effects) | `use_foo_context_provider()` |
| Bare provider (no hooks) | `provide_foo_context()` |
| Consumer | `consume_foo_context()` |
| Context field | `pub bar: Signal<T>` |

## Usage in App Root

```rust
pub fn App() -> Element {
    use_auth_context_provider();        // UseAuthContext (provides + hydration effect)
    use_my_assets_context_provider();   // UseMyAssets — reads auth ctx, so after
    use_popup_context_provider();       // UsePopupContext
    rsx! { Router::<Route> {} }
}
```

## Reactive Effects on Context

Use `use_effect` to flush/reset derived state when a signal changes:

```rust
let auth = consume_auth_context();
use_effect(move || {
    let _ = auth.user.read();    // subscribe to user changes
    ctx.assets.set(None);        // reset cache when user changes
});
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `use_init_foo` naming | Use `use_foo_context_provider` / `consume_foo_context` |
| Manual `#[derive(Clone, Copy)]` | Always use `#[derive(DioxusController)]` instead |
| Calling `use_context_provider` in two places | Provide exactly once — subsequent calls overwrite |
| Provider order wrong (reader before writer) | Put providers top-down: deps after what they depend on |
| Using `Signal::write()` in render | Use `Signal::set()` in effects/handlers, not during render |

## Example File

See `examples/context.rs` for a complete context with all three functions and methods.

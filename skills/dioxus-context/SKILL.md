---
name: dioxus-context
description: Use when adding a global service or shared state to a Dioxus app via use_context_provider/use_context, creating a feature context struct, writing use_init_xxx or use_xxx_context hooks, or implementing reactive side effects tied to context signals.
---

# dioxus-context: Context Providers in Dioxus

Context provides app-wide state without prop-drilling. Provide once at root; read anywhere in the tree.

## Core Pattern

```rust
// 1. Define a Copy context struct — Signal fields make it reactive
#[derive(Clone, Copy)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    pub hydrated: Signal<bool>,
}

// 2. Provide at root with use_init_xxx()
pub fn use_init_auth() -> UseAuthContext {
    let ctx = use_context_provider(|| UseAuthContext {
        user: Signal::new(None),
        hydrated: Signal::new(false),
    });

    // Reactive side effect that runs when ctx.user changes
    use_effect(move || {
        if ctx.hydrated() { /* ... */ }
    });

    ctx
}

// 3. Read anywhere with use_xxx_context()
pub fn use_auth_context() -> UseAuthContext {
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
| Context struct | `UseFooContext` or `FooService` |
| Provider hook | `use_init_foo()` |
| Consumer hook | `use_foo()` or `use_foo_context()` |
| Context field | `pub bar: Signal<T>` |

## Reactive Effects on Context

Use `use_effect` to flush/reset derived state when a signal changes:

```rust
let auth = use_auth_context();
use_effect(move || {
    let _ = auth.user.read();    // subscribe to user changes
    let mut assets = ctx.assets;
    assets.set(None);            // reset when user changes
});
```

## `DioxusController` Derive (by-macros)

```rust
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    pub pending_email: Signal<Option<String>>,
}
```

`DioxusController` auto-derives `Clone + Copy` boilerplate and signal accessors. Equivalent to manually deriving `Clone + Copy` with `Signal` fields.

## Multiple Contexts

Call `use_context_provider` once per type at root. Child contexts (e.g., page-level) can use the same pattern at layout level instead of App root.

```rust
// App root
pub fn App() -> Element {
    use_init_auth();        // UseAuthContext
    use_init_my_assets();   // UseMyAssets — reads auth ctx, so after
    use_init_popup();       // PopupService
    rsx! { Router::<Route> {} }
}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Calling `use_context_provider` in two places | Provide exactly once at root — subsequent calls overwrite |
| Provider order wrong (reader before writer) | Put providers top-down: deps after what they depend on |
| Using `Signal::write()` in render | Use `Signal::set()` in effects/handlers, not during render |
| Forgetting `move` in `use_effect` closure | Closures must own their captures: `use_effect(move \|\| ...)` |

## Example File

See `examples/context.rs` for a complete feature context with init, consumer hook, and methods.

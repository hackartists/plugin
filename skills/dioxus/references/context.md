# Dioxus Context Providers

Context shares state app-wide without prop-drilling. Provide once at root; read anywhere.

## Three Required Functions Per Context

```rust
// 1. provide_{name}_context — wraps Dioxus provide_context() (not a hook)
//    Can be called during rendering without hook constraints.
pub fn provide_auth_context() -> UseAuthContext {
    provide_context(UseAuthContext {
        user: Signal::new(None),
    })
}

// 2. use_{name}_context_provider — hook: provide + spawn async init
//    Call ONCE at App root (or layout root). Must be inside a component.
pub fn use_auth_context_provider() -> UseAuthContext {
    let ctx = provide_auth_context();

    // Spawn one-time async init — no use_effect needed.
    #[cfg(feature = "web")]
    spawn(async move {
        // let resp = get_me_handler().await;
        // if let Ok(r) = resp { ctx.user.set(r.user); }
    });

    ctx
}

// 3. consume_{name}_context — wraps Dioxus consume_context() (not a hook)
//    Can be called anywhere the runtime is active: components, spawn, event handlers.
pub fn consume_auth_context() -> UseAuthContext {
    consume_context::<UseAuthContext>()
}
```

## Context Struct

Always derive `DioxusController` — never manually derive `Clone + Copy`.

```rust
use by_macros::DioxusController;
use dioxus::prelude::*;

#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    // user: None  →  not signed in
    // user: Some  →  signed in
}
```

## Methods on Context

Use `&self` — Signal fields have interior mutability, no `&mut self` needed.

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
| Bare provider | `provide_foo_context()` |
| Hook provider (with init) | `use_foo_context_provider()` |
| Consumer | `consume_foo_context()` |
| Fields | `pub bar: Signal<T>` |

## Reactive Effect Between Two Contexts

When one context must react to another's signal, use `use_effect` inside `use_{name}_context_provider`. Always read the signal inside the closure to subscribe.

```rust
pub fn use_my_assets_context_provider() -> UseMyAssetsContext {
    let ctx = provide_my_assets_context();
    let auth = consume_auth_context();  // reads another context

    // Flush cache whenever the signed-in user changes
    use_effect(move || {
        let _ = auth.user.read();    // subscribe — re-runs when user changes
        ctx.assets.set(None);
        ctx.loaded.set(false);
    });

    ctx
}
```

## Dioxus Context API: Hook vs Non-Hook

| Function | Hook? | Can call in |
|----------|-------|-------------|
| `provide_context(val)` | No | Component body, spawned tasks |
| `use_context_provider(\|\| val)` | Yes | Component top-level only |
| `consume_context::<T>()` | No | Anywhere runtime is active |
| `use_context::<T>()` | Yes | Component top-level only |

Prefer `provide_context` / `consume_context` — they're not constrained to hook call sites.

## Provider Order in App

```rust
pub fn App() -> Element {
    use_auth_context_provider();          // 1st — no deps
    use_my_assets_context_provider();     // 2nd — consumes auth
    use_popup_context_provider();         // 3rd — no deps on above
    rsx! { Router::<Route> {} }
}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `use_init_foo` naming | Use `use_foo_context_provider` |
| Manual `Clone + Copy` | Use `#[derive(DioxusController)]` |
| `&mut self` on methods | Use `&self` — Signal is interior mutable |
| Providing context twice | Second call overwrites — provide exactly once per type |
| Provider before its dependency | Deps must be provided first |
| Missing signal read in `use_effect` | Effect won't subscribe — read inside closure |

## Example File

See `examples/context.rs` for a complete two-context app with all three functions.

# Dioxus Context Providers

Context shares state app-wide without prop-drilling. Provide once at root; read anywhere.

## Four Functions Per Context

```rust
// 1. provide_{name}_context — provide_context() — NOT a hook
// NOTE: cannot construct Loader/Memo outside hook context; use use_auth_context_provider() instead.
pub fn provide_auth_context(ctx: UseAuthContext) -> UseAuthContext {
    provide_context(ctx)
}

// 2. use_{name}_context_provider — use_loader first, output into use_context_provider
pub fn use_auth_context_provider() -> UseAuthContext {
    let loader = use_loader(|| async move { get_me_handler().await });
    let user = use_memo(move || loader.value().and_then(|resp| resp.user));
    use_context_provider(|| UseAuthContext { loader, user })
}

// 3. use_{name}_context — use_context() hook — component top-level / inside hooks
pub fn use_auth_context() -> UseAuthContext {
    use_context::<UseAuthContext>()
}

// 4. consume_{name}_context — consume_context() — NOT a hook — spawn / event closures
pub fn consume_auth_context() -> UseAuthContext {
    consume_context::<UseAuthContext>()
}
```

## Hook Rules and When to Use Each

Dioxus hooks must be called **unconditionally at the top level** of a component or hook function. They cannot be called inside closures, `if` blocks, loops, `spawn`, or `#[cfg(...)]` attributes.

| Function | Hook? | Call site |
|----------|-------|-----------|
| `provide_{name}_context()` | No | During rendering (conditional provides, test setup) |
| `use_{name}_context_provider()` | **Yes** | Component top-level — App root or layout |
| `use_{name}_context()` | **Yes** | Component top-level or inside another hook |
| `consume_{name}_context()` | No | `spawn`, event handler closures, non-hook async |

### Component top-level → use hook

```rust
#[component]
fn UserMenu() -> Element {
    // ✅ Hook — unconditional, top-level
    let auth = use_auth_context();

    // Signal is Copy — capture once above, move into closures freely.
    // onclick returns async move directly — no spawn needed.
    rsx! {
        button {
            onclick: move |_| async move { auth.sign_out().await; },
            "Sign out"
        }
    }
}
```

### Inside another hook → use hook

```rust
pub fn use_my_assets_context_provider() -> UseMyAssetsContext {
    let ctx = use_context_provider(|| UseMyAssetsContext { /* … */ });
    let auth = use_auth_context(); // ✅ valid — this fn is itself called as a hook

    use_effect(move || {
        let _ = auth.user.read();
        ctx.assets.set(None);
    });
    ctx
}
```

### onclick / event handlers — `async move` directly, no spawn

```rust
// ✅ Dioxus event handlers accept async closures directly
rsx! {
    button {
        onclick: move |_| async move { auth.sign_out().await; },
        "Sign out"
    }
}

// ❌ spawn inside onclick is redundant
onclick: move |_| { spawn(async move { auth.sign_out().await; }); }
```

### Background task spawned outside a component → use consume

```rust
// ❌ Cannot call hooks inside spawn
spawn(async move {
    let auth = use_auth_context(); // PANIC — hook called outside component
});

// ✅ Use consume_context for explicitly spawned background tasks
pub async fn start_background_task() {
    let auth = consume_auth_context(); // non-hook, safe here
    if auth.is_signed_in() { /* … */ }
}
```

## Context Struct

```rust
use by_macros::DioxusController;
use dioxus::prelude::*;

// Always derive DioxusController — never manually derive Clone + Copy.
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub loader: Loader<GetMeResponse>,
    pub user: Memo<Option<User>>,
}
```

## Methods — use `&self`

Signal fields have interior mutability — `&mut self` is never needed.

```rust
impl UseAuthContext {
    pub fn is_signed_in(&self) -> bool {
        self.user.read().is_some()
    }

    pub async fn sign_out(&self) {
        logout_handler().await.ok();
        // user is a Memo — it recomputes from loader automatically on next poll
    }
}
```

## Naming Conventions

| Purpose | Name |
|---------|------|
| Context struct | `UseFooContext` |
| Non-hook provide | `provide_foo_context()` |
| Hook provider (root) | `use_foo_context_provider()` |
| Hook consumer (component) | `use_foo_context()` |
| Non-hook consumer (spawn/closures) | `consume_foo_context()` |

## Provider Order in App

```rust
pub fn App() -> Element {
    use_auth_context_provider();          // no deps
    use_my_assets_context_provider();     // consumes auth → must come after
    use_popup_context_provider();
    rsx! { Router::<Route> {} }
}
```

## Reactive Effect Between Contexts

```rust
pub fn use_my_assets_context_provider() -> UseMyAssetsContext {
    let ctx = use_context_provider(|| UseMyAssetsContext { assets: Signal::new(None) });
    let auth = use_auth_context(); // hook — valid inside a hook fn

    use_effect(move || {
        let _ = auth.user.read(); // must read inside closure to subscribe
        ctx.assets.set(None);
    });
    ctx
}
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `consume_auth_context()` in component body | Use `use_auth_context()` — hook version |
| `use_auth_context()` inside `spawn` | Use `consume_auth_context()` — non-hook |
| `use_auth_context()` inside a closure/if/loop | Move hook call to component top-level |
| Hook inside `#[cfg(feature = "web")]` | Remove cfg — hooks must run unconditionally on all targets |
| `&mut self` on methods | Use `&self` — Signal is interior mutable |
| Providing context twice | Second call overwrites — provide exactly once |
| Missing signal read in `use_effect` | Effect won't subscribe — read inside closure |

## Example File

See `examples/context.rs` for a complete example with all four functions and hook/non-hook usage.

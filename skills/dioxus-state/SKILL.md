---
name: dioxus-state
description: Use when managing reactive state in Dioxus with use_signal, use_resource, use_effect, use_memo, GlobalSignal, or implementing a custom use_loader hook for server data fetching.
---

# dioxus-state: Reactive State in Dioxus

All reactive state is `Signal<T>`. Signals are `Copy` — pass them into closures without cloning.

## Signals

```rust
let count = use_signal(|| 0_i32);

// Read (subscribes current scope)
let val: i32 = count();          // or count.read().clone()
// Read without subscribing
let val: i32 = *count.peek();
// Write
count.set(5);
count += 1;
*count.write() = 42;
```

## use_resource — Async Data Fetching

```rust
let data = use_resource(|| async move {
    fetch_user(id).await
});

// In render:
match data.read().as_ref() {
    None => rsx! { "Loading..." },
    Some(Err(e)) => rsx! { "Error: {e}" },
    Some(Ok(user)) => rsx! { "{user.name}" },
}

// Reload
data.restart();
```

## use_loader — Typed Wrapper (project pattern)

The `use_loader` hook wraps `use_resource` to provide a cleaner API:

```rust
let me = use_loader(|| async move { get_me_handler().await });

// In effect or render:
if let Some(result) = me.read() {
    if let Ok(resp) = result {
        user.set(resp.user);
    }
}
me.pending()   // true while in-flight
me.value()     // Some(T) on success, None otherwise
```

Use `use_loader` for read-side hydration (data on mount). Mutations stay as direct `handler().await` calls in event handlers.

## use_effect — Reactive Side Effects

Runs when any signal read inside the closure changes:

```rust
let auth = use_auth_context();

use_effect(move || {
    let _ = auth.user.read();    // subscribe — re-runs when user changes
    ctx.assets.set(None);        // flush derived cache
});
```

## use_memo — Derived Values

```rust
let doubled = use_memo(move || count() * 2);
// doubled() re-computes only when count changes
```

**Gotcha:** Don't use memo values in attributes — they don't subscribe properly:

```rust
// BAD
let style = use_memo(move || format!("color: {}", color()));
rsx! { div { style: style } }

// GOOD — read signal directly in RSX
rsx! { div { style: format!("color: {}", color()) } }
```

## GlobalSignal — App-Level State

```rust
static THEME: GlobalSignal<Theme> = GlobalSignal::new(|| Theme::Light);

// Read / write from anywhere (no hook required)
let t = THEME.read();
THEME.set(Theme::Dark);
```

## use_coroutine — Background Tasks

```rust
let tx = use_coroutine(|mut rx: UnboundedReceiver<Msg>| async move {
    while let Some(msg) = rx.next().await {
        match msg { Msg::Reload => { /* ... */ } }
    }
});

// Send from event handler
tx.send(Msg::Reload);
```

## Quick Reference

| Operation | Syntax |
|-----------|--------|
| Create signal | `use_signal(\|\| initial)` |
| Read (reactive) | `sig()` or `*sig.read()` |
| Read (no subscribe) | `*sig.peek()` |
| Write | `sig.set(v)` / `*sig.write() = v` / `sig += 1` |
| Async resource | `use_resource(\|\| async move { ... })` |
| Derived value | `use_memo(move \|\| expr)` |
| Side effect | `use_effect(move \|\| { ... })` |
| App-level | `static X: GlobalSignal<T> = GlobalSignal::new(\|\| ...)` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `sig.write()` during render | Causes infinite loop — use `.set()` in effects/handlers |
| Memo in attribute | Direct signal read in RSX instead |
| Missing `move` in closures | All reactive closures must own their captures |
| Calling `use_loader` in event handler | Only call hooks at component top-level; use `handler().await` in handlers |

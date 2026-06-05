---
name: dioxus-state
description: Use when managing reactive state in Dioxus with use_signal, use_resource, use_action, use_effect, use_memo, GlobalSignal, or implementing a custom use_loader hook for server data fetching.
---

# dioxus-state: Reactive State in Dioxus

All reactive state is `Signal<T>`. Signals are `Copy` — pass them into closures without cloning.

## Signals

```rust
let mut count = use_signal(|| 0_i32);

// Read (subscribes current scope)
let val: i32 = count();          // or *count.read()
// Read without subscribing
let val: i32 = *count.peek();
// Write
count.set(5);
count += 1;
*count.write() = 42;
```

## use_resource — Reactive Data Fetching (auto-runs)

Runs on mount and re-runs when any signal read inside the closure changes.

```rust
let mut revision = use_signal(|| "main");
let data = use_resource(move || async move {
    fetch_data(revision()).await  // re-runs when revision changes
});

// In render — match the full Option<Result<T, E>>:
match &*data.read_unchecked() {
    None             => rsx! { "Loading..." },
    Some(Err(e))     => rsx! { "Error: {e}" },
    Some(Ok(result)) => rsx! { "{result}" },
}

data.restart();   // force reload
data.value()      // ReadSignal<Option<T>>
data.pending()    // true while in-flight
```

**Use `use_resource` for**: loading data to display, reactive queries tied to signals.

## use_action — Mutations (triggered by user events)

Runs only when explicitly called (button clicks, form submits). Auto-cancels previous in-flight call.

```rust
let mut save = use_action(save_to_database);

rsx! {
    button { onclick: move |_| save.call(form_data.clone()), "Save" }

    if save.pending() { p { "Saving..." } }

    if let Some(result) = save.value() {
        match result {
            Ok(signal) => rsx! { p { "Saved: {signal}" } },
            Err(err)   => rsx! { p { "Error: {err}" } },
        }
    }
}

save.reset();   // cancel + clear
save.cancel();  // cancel without clearing
```

**Use `use_action` for**: mutations, form submits, any async work triggered by user events.

## use_loader — Typed Wrapper (project pattern)

Wraps `use_resource` with a cleaner API for one-shot server data:

```rust
let me = use_loader(|| async move { get_me_handler().await });

me.pending()          // true while in-flight
me.value()            // Some(T) on success, None otherwise
me.read()             // Option<Result<T, E>>
```

Use `use_loader` for read-side hydration. Mutations stay as direct `handler().await` in event handlers.

## use_effect — Reactive Side Effects

Runs after render when any signal read inside the closure changes:

```rust
let mut count = use_signal(|| 0);
let mut name = use_signal(|| "world".to_string());

// Re-runs whenever count OR name changes
use_effect(move || {
    println!("greeting: hello, {name} — count is {count}");
});
```

Correct subscription pattern — always read the signal inside the closure:
```rust
use_effect(move || {
    let _ = auth.user.read();    // MUST read here to subscribe
    assets_ctx.assets.set(None); // flush derived state
});
```

## use_memo — Derived Values

```rust
let doubled = use_memo(move || count() * 2);

// Call to read — doubled() in RSX
rsx! { p { "{doubled()}" } }
```

**Gotcha:** Passing a memo handle (not called) to an attribute breaks reactivity:

```rust
// BAD — passes the memo handle itself, not the value
let style = use_memo(move || format!("color: {}", color()));
rsx! { div { style: style } }

// GOOD — call the signal directly in RSX
rsx! { div { style: format!("color: {}", color()) } }
```

Memos compose: derive from other memos or signals freely.

## GlobalSignal — App-Level State

```rust
use dioxus::prelude::*;

static COUNT: GlobalSignal<i32> = Signal::global(|| 0);
static DOUBLED: GlobalMemo<i32> = Memo::global(|| COUNT() * 2);

// Read / write from anywhere (no hook required)
*COUNT.write() += 1;
let n = COUNT();
```

`Signal::global(|| initial)` — correct syntax (not `GlobalSignal::new`)

## use_future — Infinite Background Tasks

```rust
use_future(move || async move {
    loop {
        if running() { count += 1; }
        async_std::task::sleep(Duration::from_millis(400)).await;
    }
});
```

## Quick Reference

| Operation | Syntax |
|-----------|--------|
| Create signal | `use_signal(\|\| initial)` |
| Read (reactive) | `sig()` or `*sig.read()` |
| Read (no subscribe) | `*sig.peek()` |
| Write | `sig.set(v)` / `*sig.write() = v` / `sig += 1` |
| Async resource (auto) | `use_resource(move \|\| async move { ... })` |
| Mutation (on demand) | `use_action(server_fn)` then `action.call(args)` |
| Derived value | `use_memo(move \|\| expr)` then `memo()` |
| Side effect | `use_effect(move \|\| { ... })` |
| App-level signal | `static X: GlobalSignal<T> = Signal::global(\|\| ...)` |
| App-level memo | `static X: GlobalMemo<T> = Memo::global(\|\| ...)` |

## use_action vs use_resource

| | `use_action` | `use_resource` |
|---|---|---|
| **Runs** | When you call it | On mount + dependency change |
| **Good for** | Mutations, button clicks, form submits | Loading data to display |
| **Cancellation** | Auto-cancels previous call | Restarts on dependency change |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `sig.write()` during render | Causes infinite loop — use `.set()` in effects/handlers |
| Memo handle in attribute (not called) | Call the memo: `memo()` not `memo` |
| Missing signal read in `use_effect` | Effect won't subscribe — read inside the closure |
| `GlobalSignal::new(\|\| ...)` | Use `Signal::global(\|\| ...)` |
| `use_resource` for button click | Use `use_action` for user-triggered mutations |
| Calling hooks inside event handlers | Hooks at component top-level only; use `.await` in handlers |

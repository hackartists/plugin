# Dioxus Reactive State

All reactive state is `Signal<T>`. Signals are `Copy` — capture freely in closures.

## Signals

```rust
let mut count = use_signal(|| 0_i32);

count()              // read and subscribe
*count.peek()        // read without subscribing
count.set(5);        // write
count += 1;
*count.write() = 42;
```

## use_resource — Reactive Data Fetching (auto-runs)

Runs on mount and re-runs when any signal read inside the closure changes.

```rust
let mut revision = use_signal(|| "main");
let data = use_resource(move || async move {
    fetch_data(revision()).await   // re-runs when revision changes
});

// Render — match the full Option<T>:
match &*data.read_unchecked() {
    None          => rsx! { "Loading..." },
    Some(result)  => rsx! { "{result}" },
}

data.restart();           // force reload
data.value()              // ReadSignal<Option<T>>
data.pending()            // true while in-flight
```

**Use for**: loading data to display, reactive queries. Not for mutations.

## use_action — On-Demand Mutations

Runs only when explicitly called. Auto-cancels previous in-flight call.

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

save.reset();    // cancel + clear previous result
save.cancel();   // cancel without clearing
```

**Use for**: mutations, form submits, button-triggered async work.

## use_action vs use_resource

| | `use_action` | `use_resource` |
|---|---|---|
| **Runs** | When you call it | On mount + dep change |
| **Good for** | Mutations, button clicks | Loading data to display |
| **Cancellation** | Auto-cancels previous call | Restarts on dep change |

## use_loader — Typed One-Shot Wrapper (project pattern)

Project-level wrapper around `use_resource` with a cleaner read API:

```rust
let me = use_loader(|| async move { get_me_handler().await });

me.pending()    // true while in-flight
me.value()      // Some(T) on success, None otherwise
me.read()       // Option<Result<T, E>>
```

Use for read-side hydration on mount. Mutations use `use_action` or direct `.await` in handlers.

## use_effect — Reactive Side Effects

Runs after render when any signal read inside the closure changes.

```rust
// Subscribe by reading the signal inside the closure
use_effect(move || {
    println!("count changed to {count}");  // count() read → subscribed
});

// Flush derived state when auth changes
use_effect(move || {
    let _ = auth.user.read();   // subscribe — MUST be inside closure
    ctx.assets.set(None);
});
```

**For pure derivations use `use_memo`, not `use_effect`.**

## use_memo — Derived Values

```rust
let full_name = use_memo(move || format!("{first} {last}"));
// Recomputes only when first or last changes

// Read by calling: full_name()
rsx! { h1 { "{full_name()}" } }
```

**Attribute pitfall** — passing memo handle (not called) breaks reactivity:

```rust
// BAD: reactivity breaks, memo handle not called
let style = use_memo(move || format!("color: {}", color()));
rsx! { div { style: style } }

// GOOD: read signal directly in RSX expression
rsx! { div { style: format!("color: {}", color()) } }
```

## GlobalSignal — App-Level State

```rust
// Correct syntax — Signal::global(), NOT GlobalSignal::new()
static COUNT:   GlobalSignal<i32> = Signal::global(|| 0);
static DOUBLED: GlobalMemo<i32>   = Memo::global(|| COUNT() * 2);

// Read / write from anywhere (no hook)
*COUNT.write() += 1;
let n = COUNT();
```

## use_future — Infinite Background Tasks

```rust
use_future(move || async move {
    loop {
        if running() { count += 1; }
        sleep(Duration::from_millis(400)).await;
    }
});
```

## Quick Reference

| Operation | Syntax |
|-----------|--------|
| Local signal | `use_signal(\|\| initial)` |
| Read (reactive) | `sig()` or `*sig.read()` |
| Read (no subscribe) | `*sig.peek()` |
| Write | `sig.set(v)` / `*sig.write() = v` / `sig += 1` |
| Async resource (auto) | `use_resource(move \|\| async move { … })` |
| Mutation (on demand) | `use_action(fn)` → `action.call(args)` |
| Derived value | `use_memo(move \|\| expr)` → `memo()` |
| Side effect | `use_effect(move \|\| { read_sig_here; })` |
| App-level signal | `static X: GlobalSignal<T> = Signal::global(\|\| …)` |
| App-level memo | `static X: GlobalMemo<T> = Memo::global(\|\| …)` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `sig.write()` during render | Infinite loop — write in effects/handlers only |
| Memo handle in attribute (uncalled) | Use direct signal read in RSX |
| Missing signal read in `use_effect` | Effect doesn't subscribe — read inside closure |
| `GlobalSignal::new(\|\| …)` | Use `Signal::global(\|\| …)` |
| `use_resource` for button click | Use `use_action` for user-triggered mutations |
| Hook called inside event handler | Hooks at component top-level only |

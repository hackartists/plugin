// Example: signals, use_resource, use_action, use_effect, use_memo, GlobalSignal
use dioxus::prelude::*;

// ── use_signal: local component state ────────────────────────────────────
#[component]
pub fn Counter() -> Element {
    let mut count = use_signal(|| 0_i32);

    rsx! {
        button { onclick: move |_| count -= 1, "-" }
        span { "{count}" }
        button { onclick: move |_| count += 1, "+" }
    }
}

// ── use_resource: reactive async data fetching (auto-runs) ───────────────
// Runs on mount and whenever a signal read inside the closure changes.
#[derive(Clone, Debug, serde::Deserialize)]
pub struct Post { pub id: u32, pub title: String }

async fn fetch_post(id: u32) -> Result<Post, String> {
    Ok(Post { id, title: format!("Post {id}") })
}

#[component]
pub fn PostView(id: Signal<u32>) -> Element {
    // Reactive: re-fetches automatically when `id` signal changes
    let post = use_resource(move || async move { fetch_post(id()).await });

    match &*post.read_unchecked() {
        None          => rsx! { span { "Loading..." } },
        Some(Err(e))  => rsx! { span { "Error: {e}" } },
        Some(Ok(p))   => rsx! { h1 { "{p.title}" } },
    }
}

// ── use_action: mutation triggered by user event ──────────────────────────
// Only runs when you call it. Auto-cancels previous in-flight call.
async fn save_post(title: String) -> Result<u32, String> {
    Ok(42) // server-fn call here
}

#[component]
pub fn PostEditor() -> Element {
    let mut title = use_signal(|| String::new());
    let mut save = use_action(save_post);

    rsx! {
        input { value: "{title}", oninput: move |e| title.set(e.value()) }
        button {
            disabled: save.pending(),
            onclick: move |_| { save.call(title()); },
            if save.pending() { "Saving..." } else { "Save" }
        }
        if let Some(result) = save.value() {
            match result {
                Ok(id_signal) => rsx! { p { "Saved with id: {id_signal}" } },
                Err(e)        => rsx! { p { "Error: {e}" } },
            }
        }
    }
}

// ── use_effect: reactive side effect ─────────────────────────────────────
// Re-runs whenever a signal read inside the closure changes.
#[component]
pub fn LogOnChange() -> Element {
    let mut count = use_signal(|| 0_i32);

    use_effect(move || {
        // Reading count() inside the closure subscribes to it.
        println!("count changed to {count}");
    });

    rsx! { button { onclick: move |_| count += 1, "{count}" } }
}

// ── use_memo: derived, cached value ──────────────────────────────────────
#[component]
pub fn MemoExample() -> Element {
    let mut first = use_signal(|| "Ada".to_string());
    let mut last  = use_signal(|| "Lovelace".to_string());

    // Recomputes only when first or last change
    let full_name = use_memo(move || format!("{first} {last}"));
    let initials  = use_memo(move || {
        full_name()
            .split_whitespace()
            .filter_map(|w| w.chars().next())
            .collect::<String>()
    });

    rsx! {
        // Call the memo to read its value: full_name()
        h1 { "{full_name()}" }
        p { "Initials: {initials()}" }

        // GOOD: read signal directly in attribute
        // BAD:  pass memo handle (uncalled) to attribute — reactivity breaks
        p {
            font_weight: if full_name().len() > 10 { "bold" } else { "normal" },
            "Name: {full_name()}"
        }

        input { value: "{first}", oninput: move |e| first.set(e.value()) }
        input { value: "{last}",  oninput: move |e| last.set(e.value()) }
    }
}

// ── GlobalSignal: app-level state ─────────────────────────────────────────
// Signal::global(|| initial) — NOT GlobalSignal::new(|| ...)
static COUNT: GlobalSignal<i32> = Signal::global(|| 0);
static DOUBLED: GlobalMemo<i32> = Memo::global(|| COUNT() * 2);

#[component]
pub fn GlobalCounter() -> Element {
    rsx! {
        button { onclick: move |_| *COUNT.write() += 1, "+" }
        button { onclick: move |_| *COUNT.write() -= 1, "-" }
        p { "Count: {COUNT}" }
        p { "Doubled: {DOUBLED}" }
    }
}

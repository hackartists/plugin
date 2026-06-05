// Example: signals, use_resource, use_effect, use_loader, use_memo
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

// ── use_resource: async data fetching ────────────────────────────────────
#[derive(Clone)]
pub struct Post { pub id: u32, pub title: String }

async fn fetch_post(id: u32) -> Result<Post, String> {
    // replace with real server-fn call
    Ok(Post { id, title: format!("Post {id}") })
}

#[component]
pub fn PostView(id: u32) -> Element {
    let post = use_resource(move || async move { fetch_post(id).await });

    match post.read().as_ref() {
        None              => rsx! { span { "Loading..." } },
        Some(Err(e))      => rsx! { span { "Error: {e}" } },
        Some(Ok(p))       => rsx! { h1 { "{p.title}" } },
    }
}

// ── use_loader: typed read-side wrapper (project pattern) ─────────────────
pub struct Loader<T: 'static, E: 'static = String> {
    res: Resource<Result<T, E>>,
}
impl<T: 'static, E: 'static> Clone for Loader<T, E> { fn clone(&self) -> Self { *self } }
impl<T: 'static, E: 'static> Copy  for Loader<T, E> {}
impl<T: Clone + 'static, E: Clone + 'static> Loader<T, E> {
    pub fn read(&self)    -> Option<Result<T, E>> { self.res.read().clone() }
    pub fn pending(&self) -> bool                 { self.res.read().is_none() }
    pub fn value(&self)   -> Option<T>            { self.res.read().as_ref().and_then(|r| r.as_ref().ok().cloned()) }
}
pub fn use_loader<T, E, F, Fut>(future: F) -> Loader<T, E>
where T: 'static, E: 'static,
      F: 'static + FnMut() -> Fut,
      Fut: std::future::Future<Output = Result<T, E>> + 'static,
{ Loader { res: use_resource(future) } }

// Use for read-side hydration (mount data); NOT for mutations triggered by events.
#[component]
pub fn ProfileWithLoader(id: u32) -> Element {
    let post = use_loader(move || async move { fetch_post(id).await });

    if post.pending() { return rsx! { span { "Loading..." } }; }
    match post.value() {
        Some(p) => rsx! { h1 { "{p.title}" } },
        None    => rsx! { span { "Not found" } },
    }
}

// ── use_effect: reactive side effect ─────────────────────────────────────
#[component]
pub fn LogOnChange() -> Element {
    let count = use_signal(|| 0_i32);

    // Runs once on mount, then again each time `count` changes.
    use_effect(move || {
        let val = count(); // subscribes
        tracing::info!("count changed to {val}");
    });

    rsx! { button { onclick: move |_| *count.write() += 1, "{count}" } }
}

// ── use_memo: derived, cached value ──────────────────────────────────────
#[component]
pub fn MemoExample() -> Element {
    let items: Signal<Vec<u32>> = use_signal(|| (0..100).collect());
    // Recomputes only when `items` changes, not on every render.
    let total = use_memo(move || items.read().iter().sum::<u32>());

    rsx! {
        p { "Total: {total}" }
        // GOOD: read signal directly in attribute
        // BAD:  use_memo value in attribute — reactivity breaks
        p { style: format!("font-weight: {}", if total() > 50 { "bold" } else { "normal" }),
            "Items: {items.read().len()}"
        }
    }
}

// ── GlobalSignal: app-level state, no hook required ───────────────────────
static DARK_MODE: GlobalSignal<bool> = GlobalSignal::new(|| false);

#[component]
pub fn ThemeToggle() -> Element {
    rsx! {
        button {
            onclick: move |_| *DARK_MODE.write() ^= true,
            if DARK_MODE() { "Light mode" } else { "Dark mode" }
        }
    }
}

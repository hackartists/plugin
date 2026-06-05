// Example: feature context with init hook, consumer hook, and methods
// Pattern: Clone + Copy struct with Signal fields
use dioxus::prelude::*;

// ── Types ─────────────────────────────────────────────────────────────────
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct User {
    pub id: String,
    pub display_name: String,
}

// ── Context struct ────────────────────────────────────────────────────────
// Must be Clone + Copy so it can be captured by closures without cloning.
// Signal<T> is already Copy; add #[derive(DioxusController)] with by-macros
// or derive Clone + Copy manually.
#[derive(Clone, Copy)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    /// True once the first /api/auth/me call resolves (ok or err).
    /// Never treat user==None as "signed out" before this is true.
    pub hydrated: Signal<bool>,
}

// ── Provider ──────────────────────────────────────────────────────────────
/// Call once in App root. Returns the context so the caller can chain
/// use_effect / use_loader against it immediately.
pub fn use_init_auth() -> UseAuthContext {
    let ctx = use_context_provider(|| UseAuthContext {
        user: Signal::new(None),
        hydrated: Signal::new(false),
    });

    // Web-only hydration from session cookie on first mount.
    // use_effect subscribes to ctx.hydrated so it re-runs if hydrated flips.
    #[cfg(feature = "web")]
    {
        use_effect(move || {
            // spawn returns immediately; the async block runs in the background
            spawn(async move {
                // replace with real server-fn call
                // let resp = get_me_handler().await;
                // if let Ok(r) = resp { ctx.user.set(r.user); }
                ctx.hydrated.set(true);
            });
        });
    }

    ctx
}

// ── Consumer ──────────────────────────────────────────────────────────────
pub fn use_auth_context() -> UseAuthContext {
    use_context::<UseAuthContext>()
}

// ── Methods ───────────────────────────────────────────────────────────────
impl UseAuthContext {
    pub fn is_signed_in(&self) -> bool {
        self.user.read().is_some()
    }

    pub fn display_name(&self) -> Option<String> {
        self.user.read().as_ref().map(|u| u.display_name.clone())
    }

    pub async fn sign_out(&mut self) {
        // logout_handler().await.ok();
        self.user.set(None);
    }
}

// ── Usage in a component ───────────────────────────────────────────────────
#[component]
pub fn UserMenu() -> Element {
    let auth = use_auth_context();

    if !auth.hydrated() {
        return rsx! { span { "..." } };
    }

    rsx! {
        if auth.is_signed_in() {
            span { "{auth.display_name().unwrap_or_default()}" }
        } else {
            button { "Sign in" }
        }
    }
}

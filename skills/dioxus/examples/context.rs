// Example: feature context with the three required functions + methods
// Naming: use_{name}_context_provider / provide_{name}_context / consume_{name}_context
use by_macros::DioxusController;
use dioxus::prelude::*;

// ── Types ─────────────────────────────────────────────────────────────────
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct User {
    pub id: String,
    pub display_name: String,
}

// ── Context struct ────────────────────────────────────────────────────────
// Always use DioxusController — never manually derive Clone + Copy.
// user: None  →  not signed in (or initial state before first load)
// user: Some  →  signed in
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
}

// ── 1. provide_{name}_context ─────────────────────────────────────────────
// Wraps Dioxus provide_context() — not a hook.
pub fn provide_auth_context() -> UseAuthContext {
    provide_context(UseAuthContext {
        user: Signal::new(None),
    })
}

// ── 2. use_{name}_context_provider ────────────────────────────────────────
// Hook: uses use_context_provider (hook) + spawns async initialization.
// Call ONCE at App root (or layout root).
pub fn use_auth_context_provider() -> UseAuthContext {
    let ctx = use_context_provider(|| UseAuthContext {
        user: Signal::new(None),
    });

    // Spawn one-time async init — no use_effect needed.
    #[cfg(feature = "web")]
    spawn(async move {
        // let resp = get_me_handler().await;
        // if let Ok(r) = resp { ctx.user.set(r.user); }
    });

    ctx
}

// ── 3. consume_{name}_context ─────────────────────────────────────────────
// Wraps Dioxus consume_context() — not a hook.
// Can be called anywhere the runtime is active: components, spawn, event handlers.
pub fn consume_auth_context() -> UseAuthContext {
    consume_context::<UseAuthContext>()
}

// ── Methods ───────────────────────────────────────────────────────────────
// Use &self (not &mut self) — Signal fields use interior mutability.
impl UseAuthContext {
    pub fn is_signed_in(&self) -> bool {
        self.user.read().is_some()
    }

    pub fn display_name(&self) -> Option<String> {
        self.user.read().as_ref().map(|u| u.display_name.clone())
    }

    pub async fn sign_out(&self) {
        // logout_handler().await.ok();
        self.user.set(None);
    }
}

// ── App root ──────────────────────────────────────────────────────────────
#[component]
pub fn App() -> Element {
    use_auth_context_provider();
    use_my_assets_context_provider();
    rsx! { div { "app content" } }
}

// ── Consumer component ────────────────────────────────────────────────────
#[component]
pub fn UserMenu() -> Element {
    let auth = consume_auth_context();

    rsx! {
        if auth.is_signed_in() {
            span { "{auth.display_name().unwrap_or_default()}" }
        } else {
            button { "Sign in" }
        }
    }
}

// ── Second context: reactive on another context ───────────────────────────
#[derive(Clone, Copy, DioxusController)]
pub struct UseMyAssetsContext {
    pub assets: Signal<Option<Vec<String>>>,
}

pub fn provide_my_assets_context() -> UseMyAssetsContext {
    provide_context(UseMyAssetsContext {
        assets: Signal::new(None),
    })
}

pub fn use_my_assets_context_provider() -> UseMyAssetsContext {
    let ctx = use_context_provider(|| UseMyAssetsContext {
        assets: Signal::new(None),
    });
    let auth = consume_auth_context();

    // Flush cache whenever the signed-in user changes.
    // Read auth.user inside the closure to subscribe.
    use_effect(move || {
        let _ = auth.user.read();
        ctx.assets.set(None);
    });

    ctx
}

pub fn consume_my_assets_context() -> UseMyAssetsContext {
    consume_context::<UseMyAssetsContext>()
}

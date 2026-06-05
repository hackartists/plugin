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
// DioxusController generates Clone + Copy and signal accessor boilerplate.
// user==None before hydrated==true does NOT mean "signed out".
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
    pub hydrated: Signal<bool>,
}

// ── 1. provide_{name}_context ─────────────────────────────────────────────
// Wraps Dioxus provide_context() — not a hook.
// Can be called during rendering without hook constraints (e.g. conditional provides).
pub fn provide_auth_context() -> UseAuthContext {
    provide_context(UseAuthContext {
        user: Signal::new(None),
        hydrated: Signal::new(false),
    })
}

// ── 2. use_{name}_context_provider ────────────────────────────────────────
// Hook: provides the context AND spawns any async initialization work.
// Call ONCE at the component tree root (App or a top-level layout).
pub fn use_auth_context_provider() -> UseAuthContext {
    let ctx = provide_auth_context();

    // Spawn async work directly — no use_effect wrapper needed for one-time init.
    // Web-only: hydrate user from session cookie on first mount.
    #[cfg(feature = "web")]
    spawn(async move {
        // let resp = get_me_handler().await;
        // if let Ok(r) = resp { ctx.user.set(r.user); }
        ctx.hydrated.set(true);
    });

    ctx
}

// ── 3. consume_{name}_context ─────────────────────────────────────────────
// Wraps Dioxus consume_context() — not a hook.
// Can be called anywhere the Dioxus runtime is active: components, spawn, event handlers.
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

// ── App root wires up the provider ────────────────────────────────────────
#[component]
pub fn App() -> Element {
    use_auth_context_provider();
    use_my_assets_context_provider(); // depends on auth, so comes after
    rsx! { div { "app content" } }
}

// ── Child components consume ──────────────────────────────────────────────
#[component]
pub fn UserMenu() -> Element {
    let auth = consume_auth_context();

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

// ── Second context: shows reactive effect that depends on another context ──
#[derive(Clone, Copy, DioxusController)]
pub struct UseMyAssetsContext {
    pub assets: Signal<Option<Vec<String>>>,
    pub loaded: Signal<bool>,
}

pub fn provide_my_assets_context() -> UseMyAssetsContext {
    provide_context(UseMyAssetsContext {
        assets: Signal::new(None),
        loaded: Signal::new(false),
    })
}

pub fn use_my_assets_context_provider() -> UseMyAssetsContext {
    let ctx = provide_my_assets_context();
    let auth = consume_auth_context();

    // Flush cache when the signed-in user changes.
    // Must read auth.user inside the closure to subscribe to it.
    use_effect(move || {
        let _ = auth.user.read();    // subscribe
        ctx.assets.set(None);
        ctx.loaded.set(false);
    });

    ctx
}

pub fn consume_my_assets_context() -> UseMyAssetsContext {
    consume_context::<UseMyAssetsContext>()
}

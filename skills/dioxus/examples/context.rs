// Example: feature context — four public functions per context
// Naming convention:
//   provide_{name}_context      — non-hook, bare provide_context()
//   use_{name}_context_provider — hook, use_context_provider() + init at App root
//   use_{name}_context          — hook, use_context() — call at component top-level / inside hooks
//   consume_{name}_context      — non-hook, consume_context() — call inside spawn / event closures
use by_macros::DioxusController;
use dioxus::prelude::*;

// ── Types ─────────────────────────────────────────────────────────────────
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct User {
    pub id: String,
    pub display_name: String,
}

// ── Context struct ────────────────────────────────────────────────────────
// Always derive DioxusController — never manually derive Clone + Copy.
#[derive(Clone, Copy, DioxusController)]
pub struct UseAuthContext {
    pub user: Signal<Option<User>>,
}

// ── 1. provide_{name}_context ─────────────────────────────────────────────
// Not a hook. Use when providing outside the normal hook call-site
// (conditional provides, nested re-provides, testing).
pub fn provide_auth_context() -> UseAuthContext {
    provide_context(UseAuthContext {
        user: Signal::new(None),
    })
}

// ── 2. use_{name}_context_provider ────────────────────────────────────────
// Hook (use_context_provider). Call ONCE at App root or a top-level layout.
// Provides the context and spawns any one-time async initialization.
pub fn use_auth_context_provider() -> UseAuthContext {
    let ctx = use_context_provider(|| UseAuthContext {
        user: Signal::new(None),
    });

    #[cfg(feature = "web")]
    spawn(async move {
        // let resp = get_me_handler().await;
        // if let Ok(r) = resp { ctx.user.set(r.user); }
    });

    ctx
}

// ── 3. use_{name}_context ─────────────────────────────────────────────────
// Hook (use_context). Call at component top-level or inside other hooks.
// Follows hook rules: unconditional, top-level only.
pub fn use_auth_context() -> UseAuthContext {
    use_context::<UseAuthContext>()
}

// ── 4. consume_{name}_context ─────────────────────────────────────────────
// Not a hook (consume_context). Call from spawn, event handler closures,
// or any non-hook async context where hook rules don't apply.
pub fn consume_auth_context() -> UseAuthContext {
    consume_context::<UseAuthContext>()
}

// ── Methods ───────────────────────────────────────────────────────────────
// &self (not &mut self) — Signal uses interior mutability.
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

// ── App root — provides context ───────────────────────────────────────────
#[component]
pub fn App() -> Element {
    use_auth_context_provider();
    use_my_assets_context_provider(); // must come after auth
    rsx! { div { "app content" } }
}

// ── Component — use hook version at top-level ─────────────────────────────
#[component]
pub fn UserMenu() -> Element {
    let auth = use_auth_context(); // ← hook: unconditional, top-level

    rsx! {
        if auth.is_signed_in() {
            span { "{auth.display_name().unwrap_or_default()}" }
            button {
                onclick: move |_| async move { auth.sign_out().await; },
                "Sign out"
            }
        } else {
            button { "Sign in" }
        }
    }
}

// ── consume_* — for non-hook contexts ────────────────────────────────────
// Use consume_auth_context() when you can't call hooks:
// e.g. inside spawn where hook context is no longer active.
pub fn some_background_task() {
    spawn(async move {
        let auth = consume_auth_context(); // ← non-hook: safe inside spawn
        if auth.is_signed_in() { /* ... */ }
    });
}

// ── Second context: reacts to auth changes ───────────────────────────────
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
    let auth = use_auth_context(); // ← hook: this fn is itself a hook, so use_context is valid

    use_effect(move || {
        let _ = auth.user.read(); // subscribe — re-runs when user changes
        ctx.assets.set(None);
    });

    ctx
}

pub fn use_my_assets_context() -> UseMyAssetsContext {
    use_context::<UseMyAssetsContext>()
}

pub fn consume_my_assets_context() -> UseMyAssetsContext {
    consume_context::<UseMyAssetsContext>()
}

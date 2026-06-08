// Example: a complete page implementation.
//
// In a real project these are SEPARATE files under src/pages/settings/:
//   page.rs            — the *Page component (this file's `SettingsPage`)
//   i18n.rs            — the translate! block (this file's `SettingsTranslate`)
//   context.rs         — the page context (this file's `UseSettingsContext`)
//   components/*.rs     — one component per file (this file's `SettingsProfileCard`)
//   hooks/*.rs          — one hook per file
//   mod.rs             — `mod page; pub use page::*;` plus the other submodules
//
// They are collapsed here into one file only to read as a single example.
use by_macros::DioxusController;
use dioxus::prelude::*;
use dioxus_translate::*;

// ── i18n.rs ─────────────────────────────────────────────────────────────────
// Page-level text only (shared across the page). Component-local strings live
// inline in each component's own file — see SettingsProfileCard below.
translate! {
    SettingsTranslate;

    title: { en: "Settings", ko: "설정" },
}

// ── context.rs ────────────────────────────────────────────────────────────────
// Owns the page's shared state AND the API boundary. Components call these
// methods; they never call server-function handlers directly.
#[derive(Clone, Copy, DioxusController)]
pub struct UseSettingsContext {
    pub profile: Loader<Profile>,
    pub saving: Signal<bool>,
}

pub fn use_settings_context_provider() -> UseSettingsContext {
    // Read-side hydration via a loader; refreshed after mutations.
    let profile = use_loader(|| async move { get_profile_handler().await });
    use_context_provider(|| UseSettingsContext {
        profile,
        saving: Signal::new(false),
    })
}

pub fn use_settings_context() -> UseSettingsContext {
    use_context::<UseSettingsContext>()
}

impl UseSettingsContext {
    pub fn display_name(&self) -> String {
        self.profile
            .value()
            .map(|p| p.display_name)
            .unwrap_or_default()
    }

    // The only place the update handler is called — components call ctx.save().
    pub async fn save(&self, display_name: String) -> Result<(), ServerFnError> {
        self.saving.set(true);
        let res = update_profile_handler(UpdateProfileRequest { display_name }).await;
        self.profile.restart(); // re-fetch so the UI reflects the new value
        self.saving.set(false);
        res.map(|_| ())
    }
}

// ── page.rs ─────────────────────────────────────────────────────────────────
// Thin: provides context, then composes child components. No rsx! over ~300 lines.
#[component]
pub fn SettingsPage() -> Element {
    // Provide the page context once, at the top of the page component.
    use_settings_context_provider();
    let tr: SettingsTranslate = use_translate();

    rsx! {
        section { class: "settings",
            h1 { "{tr.title}" }
            SettingsProfileCard {}
        }
    }
}

// ── components/settings_profile_card.rs ───────────────────────────────────────
// A child component in its own file. Reads the page context; mutates via ctx.save().
// Its UI text is local, so its translate! block lives at the END of this file.
#[component]
fn SettingsProfileCard() -> Element {
    let ctx = use_settings_context();
    let tr: ProfileCardTranslate = use_translate();
    let mut name = use_signal(|| ctx.display_name());

    rsx! {
        div { class: "card",
            label { "{tr.display_name}" }
            input {
                value: "{name}",
                oninput: move |e| name.set(e.value()),
            }
            button {
                disabled: ctx.saving.read().clone(),
                // ✅ go through the context method, NOT the handler directly
                onclick: move |_| async move { ctx.save(name()).await.ok(); },
                if ctx.saving.read().clone() { "{tr.saving}" } else { "{tr.save}" }
            }
        }
    }
}

// ── i18n for this component — kept at the END of the component file ───────────
translate! {
    ProfileCardTranslate;

    display_name: { en: "Display name", ko: "표시 이름" },
    save:         { en: "Save",         ko: "저장" },
    saving:       { en: "Saving…",      ko: "저장 중…" },
}

// ── stand-ins so the example type-checks conceptually ─────────────────────────
// (In a real project these come from your DTO + server modules.)
#[derive(Clone, PartialEq)]
pub struct Profile {
    pub display_name: String,
}
pub struct UpdateProfileRequest {
    pub display_name: String,
}
async fn get_profile_handler() -> Result<Profile, ServerFnError> {
    unimplemented!()
}
async fn update_profile_handler(_req: UpdateProfileRequest) -> Result<(), ServerFnError> {
    unimplemented!()
}

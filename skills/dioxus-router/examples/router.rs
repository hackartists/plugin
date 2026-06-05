// Example: full Route enum with nested layouts and auth guard
use dioxus::prelude::*;
use dioxus_router::prelude::*;

// ── Route enum ────────────────────────────────────────────────────────────
#[derive(Debug, Clone, Routable, PartialEq)]
#[rustfmt::skip]   // prevents rustfmt from breaking nested macro attributes
pub enum Route {
    #[route("/")]
    HomePage {},

    #[route("/onboarding")]
    OnboardingPage {},

    // All /console/* routes share ConsoleLayout (auth guard lives there)
    #[nest("/console")]
        #[layout(ConsoleLayout)]
            #[route("")]
            ConsoleDashboardPage {},

            #[route("/settings")]
            ConsoleSettingsPage {},

            // Sub-layout within /console/investor
            #[nest("/investor")]
                #[layout(InvestorLayout)]
                    #[route("")]
                    ConsoleInvestorPage {},

                    #[route("/room/:room_id")]
                    ConsoleInvestorRoomPage { room_id: String },
                #[end_layout]
            #[end_nest]
        #[end_layout]
    #[end_nest]
}

// ── Layouts ───────────────────────────────────────────────────────────────
#[component]
pub fn ConsoleLayout() -> Element {
    // Auth guard pattern:
    // 1. Wait for hydration to avoid false "signed out" on first load
    // 2. Redirect if not signed in
    // 3. Render shell + Outlet for authenticated users

    // let auth = use_auth_context();
    // if !auth.hydrated() {
    //     return rsx! { LoadingSpinner {} };
    // }
    // if !auth.is_signed_in() {
    //     return rsx! { Navigate { to: Route::OnboardingPage {} } };
    // }

    rsx! {
        div { class: "console-shell",
            ConsoleSidebar {}
            main { class: "console-content",
                Outlet::<Route> {}   // renders matched child route
            }
        }
    }
}

#[component]
pub fn InvestorLayout() -> Element {
    rsx! {
        div { class: "investor-shell",
            InvestorNav {}
            Outlet::<Route> {}
        }
    }
}

// ── Pages (stub implementations) ─────────────────────────────────────────
#[component]
pub fn HomePage() -> Element {
    rsx! { h1 { "Home" } }
}

#[component]
pub fn OnboardingPage() -> Element {
    rsx! { h1 { "Onboarding" } }
}

#[component]
pub fn ConsoleDashboardPage() -> Element {
    rsx! { h1 { "Dashboard" } }
}

#[component]
pub fn ConsoleSettingsPage() -> Element {
    rsx! { h1 { "Settings" } }
}

#[component]
pub fn ConsoleInvestorPage() -> Element {
    rsx! { h1 { "Investor Console" } }
}

// Route param becomes a component prop — framework fills it from the URL
#[component]
pub fn ConsoleInvestorRoomPage(room_id: String) -> Element {
    rsx! { h1 { "Room: {room_id}" } }
}

// ── Navigation ────────────────────────────────────────────────────────────
#[component]
pub fn ConsoleSidebar() -> Element {
    let nav = use_navigator();

    rsx! {
        nav {
            Link { to: Route::ConsoleDashboardPage {}, "Dashboard" }
            Link { to: Route::ConsoleSettingsPage {}, "Settings" }
            button {
                onclick: move |_| nav.push(Route::HomePage {}),
                "Home"
            }
        }
    }
}

// Stub components referenced above
#[component] fn InvestorNav() -> Element { rsx! { nav { } } }
#[component] fn LoadingSpinner() -> Element { rsx! { span { "Loading..." } } }

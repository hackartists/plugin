# Dioxus Router

Routes are a `#[derive(Routable)]` enum. Each variant maps to a URL and a component.

## Route Enum

```rust
use dioxus::prelude::*;  // re-exports all router types

#[derive(Routable, Clone, Debug, PartialEq)]
#[rustfmt::skip]  // prevents rustfmt from breaking nested macro attributes
enum Route {
    #[route("/")]
    HomePage {},

    #[route("/user/:id")]
    UserPage { id: String },

    #[route("/docs/:..path")]    // catch-all
    DocsPage { path: Vec<String> },

    // Nested layout + nest
    #[nest("/console")]
    #[layout(ConsoleLayout)]        // auth guard lives in ConsoleLayout
        #[route("")]                // /console
        ConsoleDashboard {},

        #[route("/settings")]       // /console/settings
        ConsoleSettings {},

        #[nest("/investor")]
        #[layout(InvestorLayout)]
            #[route("")]            // /console/investor
            InvestorPage {},

            #[route("/room/:room_id")]
            InvestorRoomPage { room_id: String },
        #[end_layout]
        #[end_nest]
    #[end_layout]
    #[end_nest]

    // Redirects
    #[nest("/old")]
        #[redirect("/blog", || Route::HomePage {})]
        #[redirect("/blog/:name", |name: String| Route::UserPage { id: name })]
    #[end_nest]

    // 404 catch-all
    #[route("/:..route")]
    NotFound { route: Vec<String> },
}
```

## Layout Component (Auth Guard Pattern)

```rust
#[component]
fn ConsoleLayout() -> Element {
    let auth = use_auth_context();

    // 1. Wait for hydration — user==None before hydrated is NOT "signed out"
    if !auth.hydrated() {
        return rsx! { LoadingSpinner {} };
    }
    // 2. Redirect unsigned users
    if !auth.is_signed_in() {
        return rsx! { Navigate { to: Route::HomePage {} } };
    }
    // 3. Render shell + child route
    rsx! {
        div { class: "console-shell",
            ConsoleSidebar {}
            Outlet::<Route> {}    // renders the matched child route
        }
    }
}
```

## Mounting the Router

```rust
// In App component:
rsx! {
    Router::<Route> {}
}
```

## Navigation

```rust
// Declarative link
rsx! {
    Link { to: Route::UserPage { id: "42".to_string() }, "Go to user" }
}

// Programmatic
let nav = use_navigator();
nav.push(Route::ConsoleDashboard {});
nav.replace(Route::HomePage {});
nav.go_back();
```

## Route Parameters

Route params become component props — filled by the framework from the URL.

```rust
#[component]
fn UserPage(id: String) -> Element {
    rsx! { h1 { "User: {id}" } }
}

#[component]
fn DocsPage(path: Vec<String>) -> Element {
    rsx! { p { "Path: {path:?}" } }
}
```

## Quick Reference

| Pattern | Syntax |
|---------|--------|
| Static route | `#[route("/path")]` |
| Dynamic param | `#[route("/item/:id")]` + prop `id: String` |
| Catch-all | `#[route("/docs/:..path")]` + prop `path: Vec<String>` |
| 404 handler | `#[route("/:..route")]` at end of enum |
| Layout wrapper | `#[layout(Comp)]` … `#[end_layout]` |
| Nested URL prefix | `#[nest("/prefix")]` … `#[end_nest]` |
| Redirect | `#[redirect("/from", \|\| Route::To {})]` |
| Mount router | `Router::<Route> {}` |
| Render child | `Outlet::<Route> {}` inside layout |
| Navigate | `use_navigator()` then `.push()` / `.replace()` / `.go_back()` |
| Link | `Link { to: Route::Foo {} }` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `#[rustfmt::skip]` | Rustfmt breaks nested route macros |
| Auth check before hydration | Check `hydrated()` first — false negative before hydration resolves |
| `Outlet` missing in layout | Child route renders blank — add `Outlet::<Route> {}` |
| `#[end_layout]` / `#[end_nest]` missing | Every open must have a matching close |
| Using `dioxus_router::prelude::*` | Use `dioxus::prelude::*` — it re-exports everything |

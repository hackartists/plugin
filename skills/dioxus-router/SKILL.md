---
name: dioxus-router
description: Use when adding routes to a Dioxus app, creating a Route enum, nesting routes under a layout, adding route parameters, implementing auth guards, or navigating between pages programmatically.
---

# dioxus-router: Routing in Dioxus

Routes are defined as a `#[derive(Routable)]` enum. Each variant maps to a URL pattern and a component.

## Basic Route Enum

```rust
#[derive(Debug, Clone, Routable, PartialEq)]
#[rustfmt::skip]
pub enum Route {
    #[route("/")]
    HomePage {},

    #[route("/user/:id")]
    UserPage { id: String },

    #[route("/docs/:..path")]    // catch-all
    DocsPage { path: Vec<String> },
}
```

## Nested Routes with Layouts

```rust
#[derive(Debug, Clone, Routable, PartialEq)]
#[rustfmt::skip]
pub enum Route {
    #[route("/")]
    HomePage {},

    #[nest("/console")]
        #[layout(ConsoleLayout)]
            #[route("")]                        // /console
            ConsolePage {},

            #[route("/settings")]               // /console/settings
            ConsoleSettingsPage {},

            #[nest("/investor")]
                #[layout(InvestorLayout)]
                    #[route("")]                // /console/investor
                    ConsoleInvestorPage {},

                    #[route("/room/:id")]        // /console/investor/room/:id
                    ConsoleInvestorRoomPage { id: String },
                #[end_layout]
            #[end_nest]
        #[end_layout]
    #[end_nest]
}
```

## Layout Component

Layouts wrap nested routes. Use `Outlet::<Route>` to render child routes:

```rust
#[component]
pub fn ConsoleLayout() -> Element {
    let auth = use_auth_context();

    // Auth guard: redirect unsigned users
    if !auth.hydrated() {
        return rsx! { LoadingSpinner {} };
    }
    if !auth.is_signed_in() {
        return rsx! { Navigate { to: Route::HomePage {} } };
    }

    rsx! {
        div { class: "console-shell",
            ConsoleSidebar {}
            Outlet::<Route> {}    // renders matched child route
        }
    }
}
```

## Mounting the Router

```rust
// src/app.rs
rsx! {
    Router::<Route> {}
}
```

## Navigation

```rust
use dioxus::prelude::*;  // re-exports all router items

// Declarative link
rsx! {
    Link { to: Route::UserPage { id: "42".to_string() }, "Go to user" }
}

// Programmatic navigation
let nav = use_navigator();
nav.push(Route::ConsolePage {});
nav.replace(Route::HomePage {});
nav.go_back();
```

## Reading Route Params

Route parameters are component props — the framework fills them from the URL:

```rust
#[component]
pub fn UserPage(id: String) -> Element {
    rsx! { h1 { "User: {id}" } }
}
```

## Quick Reference

| Pattern | Syntax |
|---------|--------|
| Static route | `#[route("/path")]` |
| Dynamic param | `#[route("/item/:id")]` + prop `id: String` |
| Catch-all | `#[route("/docs/:..path")]` + prop `path: Vec<String>` |
| Nested layout | `#[nest] #[layout(Comp)] ... #[end_layout] #[end_nest]` |
| Mount router | `Router::<Route> {}` |
| Render children | `Outlet::<Route> {}` inside layout |
| Navigate | `use_navigator()` then `.push()` / `.replace()` / `.go_back()` |
| Link | `Link { to: Route::Foo {} }` |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing `#[end_layout]`/`#[end_nest]` | Every `#[layout]`/`#[nest]` must have a matching `#[end_*]` |
| Auth check before hydration | Check `hydrated()` first; `None` user before hydration ≠ signed out |
| Forgetting `#[rustfmt::skip]` | Rustfmt re-formats the enum body and breaks nested route macros |
| Outlet missing in layout | Layout renders but child route is blank — add `Outlet::<Route> {}` |

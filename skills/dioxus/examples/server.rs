// Example: server function module structure with by-macros
// controllers/get_user.rs

use crate::*;  // brings in #[get]/#[post] macros via by-macros

// Types that compile on both web (wasm32) and server targets
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct User {
    pub id: String,
    pub display_name: String,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct GetUserResponse {
    pub user: Option<User>,
}

#[derive(Debug, thiserror::Error, serde::Serialize, serde::Deserialize)]
pub enum UserError {
    #[error("not found")]
    NotFound,
    #[error("server error: {0}")]
    Server(String),
}

// ── Extractor (server-only) ───────────────────────────────────────────────
// Extracts the signed-in user from the session. Only compiled for server
// builds — the wasm bundle never sees this.
#[cfg(feature = "server")]
pub mod extractors {
    use axum::extract::FromRequestParts;
    use axum::http::request::Parts;
    use super::User;
    use super::UserError;

    pub struct AuthUser(pub User);

    impl<S: Send + Sync> FromRequestParts<S> for AuthUser {
        type Rejection = UserError;

        async fn from_request_parts(parts: &mut Parts, _state: &S)
            -> Result<Self, Self::Rejection>
        {
            // In practice: read session cookie, look up user in DB
            todo!("implement session lookup")
        }
    }
}

#[cfg(feature = "server")]
use extractors::AuthUser;

// ── Server function ───────────────────────────────────────────────────────
// #[get] generates:
//   - On server: axum GET handler at /api/user/:id (AuthUser extractor runs)
//   - On web:    async fn get_user_handler(id: String) that serializes/POSTs

#[get("/api/user/:id", auth: AuthUser)]
pub async fn get_user_handler(id: String) -> std::result::Result<GetUserResponse, UserError> {
    // `auth` is injected by the extractor — only exists on server
    // `id` comes from the route param and is part of the client call signature
    let _caller = auth.0;  // the signed-in user
    // let user = UserDb::get(&id).await.map_err(|e| UserError::Server(e.to_string()))?;
    Ok(GetUserResponse { user: None })
}

// ── POST example ─────────────────────────────────────────────────────────
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct UpdateDisplayNameRequest {
    pub display_name: String,
}

#[post("/api/user/display-name", auth: AuthUser)]
pub async fn update_display_name_handler(
    body: UpdateDisplayNameRequest,
) -> std::result::Result<User, UserError> {
    let _caller = auth.0;
    // persist body.display_name for caller.id ...
    todo!()
}

// ── Usage in a component (client side) ───────────────────────────────────
// use super::controllers::{get_user_handler, update_display_name_handler};
//
// #[component]
// pub fn UserProfile(id: String) -> Element {
//     let profile = use_loader(move || {
//         let id = id.clone();
//         async move { get_user_handler(id).await }
//     });
//
//     let mut name_input = use_signal(String::new);
//
//     rsx! {
//         if let Some(Ok(resp)) = profile.read().as_ref() {
//             if let Some(user) = &resp.user {
//                 p { "{user.display_name}" }
//             }
//         }
//         input { value: "{name_input}", oninput: move |e| name_input.set(e.value()) }
//         button {
//             onclick: move |_| async move {
//                 update_display_name_handler(UpdateDisplayNameRequest {
//                     display_name: name_input(),
//                 }).await.ok();
//             },
//             "Save"
//         }
//     }
// }

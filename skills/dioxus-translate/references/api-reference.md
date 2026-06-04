# dioxus-translate API Reference

Complete API surface of the `dioxus-translate` crate family.

## Crate Layout

| Crate | Role |
|-------|------|
| `dioxus-translate` | Runtime: `Language`, hooks, language persistence. Re-exports the macro crate and `Translator` trait, so `use dioxus_translate::*;` brings everything in. |
| `dioxus-translate-macro` | Proc macros: `translate!` (function-like) and `#[derive(Translate)]`. |
| `dioxus-translate-types` | The `Translator` trait only. |

## Feature Flags

```toml
[features]
ko = ["dioxus-translate-types/ko", "dioxus-translate-macro/ko"]
```

- Without `ko`: `Language` has only the `En` variant; `Translator` has only `fn en()`;
  `ko:` values in `translate!` are parsed but not emitted; `Language::switch()` always
  yields `En`.
- With `ko`: `Language::Ko` exists, `Translator::ko()` is required (the macro generates it),
  and `switch()` toggles between the two.
- When writing library code that must compile both ways, gate `Language::Ko` match arms with
  `#[cfg(feature = "ko")]`.

Target-specific dependencies (handled by the crate, no user action needed):
- wasm32: `dioxus/web` + `web-sys` (localStorage, cookie, navigator.language).
- non-wasm: `dioxus/server` + `dioxus/fullstack` (request-context cookie reading).

## `Language` Enum

```rust
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Copy, JsonSchema)]
pub enum Language {
    #[cfg(feature = "ko")]
    #[serde(rename = "ko")]
    Ko,
    #[serde(rename = "en")]
    En,
}
```

- `Default` is `En`.
- Serde serializes to `"ko"` / `"en"`.

### Methods

| Method | Behavior |
|--------|----------|
| `switch(&self) -> Self` | Computes the next language (Ko↔En), **sets the global signal**, and on wasm writes `localStorage["language"]` and the `language=<code>; path=/` cookie. Returns the new language. |
| `open_graph_locale(&self) -> String` | `"ko_KR"` / `"en_US"` for OpenGraph meta tags. |
| `to_string(&self) -> String` | `"ko"` / `"en"`. (Also implements `Display`.) |
| `all() -> Vec<Language>` | All compiled-in languages; `[Ko, En]` with the `ko` feature, otherwise `[En]`. |
| `FromStr` | `"ko"` → `Ko`, anything else → `En` (never errors). |

## Free Functions and Hooks

### `use_translate<T: Translator>() -> T`

Reactive hook. Reads the current language via `use_language()` and returns `T::en()` or
`T::ko()`. Call once at the top of a component; the component re-renders when the language
signal changes.

### `use_language() -> Signal<Language>`

- **wasm32**: returns the global `LANGUAGE` signal. Initialized lazily from
  `localStorage["language"]`, falling back to `navigator.language` (primary subtag),
  falling back to `Language::default()`.
- **non-wasm**: runtime dispatch via `dioxus::fullstack::FullstackContext::current()`:
  - During an SSR request: a fresh `use_signal` seeded from the request's `language` cookie.
  - Native client (desktop/mobile, no request context): the global `LANGUAGE` signal.

### `set_language(lang: Language)`

Sets the global language signal. Does **not** persist to localStorage/cookie — use
`Language::switch()` for persisted toggling, or persist manually alongside `set_language`.

### `set_initial_language(lang: Language)`

Identical to `set_language` but semantically intended for app startup: the app-level
persistence layer (e.g. restoring a saved preference from WebView localStorage on native
targets) calls this before any component reads the signal.

### `language_from_cookie() -> Language` (non-wasm only)

Parses the `language` cookie from the current fullstack request headers. Returns
`Language::default()` when there is no request context or no cookie. Normally called
indirectly via `use_language()`.

### `translate<T: Translator>(lang: &Language) -> T`

Non-reactive: returns `T::en()` / `T::ko()` for an explicit language. Use outside
components or when the language comes from a parameter.

### `STORAGE_KEY: &str = "language"`

The localStorage key (and cookie name) used for persistence. Import it when the app layer
reads/writes the saved preference itself.

## `Translator` Trait

```rust
pub trait Translator {
    fn en() -> Self;
    #[cfg(feature = "ko")]
    fn ko() -> Self;
}
```

Implemented automatically by the `translate!` macro. Rarely implemented by hand.

## `translate!` Macro Expansion

Input:

```rust
translate! {
    HomeTranslate;
    title: { en: "Home", ko: "홈" },
}
```

Generates:

```rust
#[derive(Debug, Clone, PartialEq)]
pub struct HomeTranslate {
    pub title: &'static str,
}

impl HomeTranslate {
    pub fn new(lang: &dioxus_translate::Language) -> Self {
        match lang {
            dioxus_translate::Language::En => Self::en(),
            dioxus_translate::Language::Ko => Self::ko(), // only with `ko` feature
        }
    }
}

impl dioxus_translate::Translator for HomeTranslate {
    fn en() -> Self { Self { title: "Home" } }
    fn ko() -> Self { Self { title: "홈" } }   // only with `ko` feature
}
```

Parsing notes:
- Struct name first, then `;`.
- Each field: `name: { lang: "literal", ... },` — only `en` and `ko` idents are recognized;
  others are silently ignored.
- Only string literals are accepted as values.
- Trailing commas are permitted everywhere.
- A field missing an `en:` value fails to compile (the generated struct field has no value).
- The struct and fields are always `pub`.

## `#[derive(Translate)]` Expansion

Applies to **enums only** (compile error otherwise). Generates:

```rust
impl dioxus_translate::Translate for MyEnum {
    fn translate(&self, lang: &dioxus_translate::Language) -> &'static str { ... }
}

impl MyEnum {
    pub const VARIANTS: &'static [Self] = &[ /* unit variants only */ ];
    pub fn variants(lang: &dioxus_translate::Language) -> Vec<String>;
}
```

The `Translate` trait it implements:

```rust
pub trait Translate {
    fn translate(&self, lang: &Language) -> &'static str;
}
```

Variant attribute forms:

| Attribute | Behavior |
|-----------|----------|
| *(none)* | Variant name used as both English and Korean string. |
| `#[translate(en = "...", ko = "...")]` | Explicit per-language strings. Either may be omitted (falls back to variant name). |
| `#[translate(from)]` | Single-field tuple variants only: delegates to `inner.translate(lang)`. Combine with `thiserror`'s `#[from]` for nested error enums. |

Match arms handle all variant shapes: unit (`Variant`), struct (`Variant { .. }`), tuple
(`Variant(..)`) — translations for non-unit variants are static per-variant strings (field
values are not interpolated).

`VARIANTS` / `variants(&lang)` only include **unit** variants — useful for rendering
dropdowns of translated options:

```rust
for (value, label) in TeamRole::VARIANTS.iter().zip(TeamRole::variants(&lang)) { ... }
```

## Persistence Model Summary

| Surface | Mechanism | Written by |
|---------|-----------|------------|
| Web client | `localStorage["language"]` | `Language::switch()` |
| SSR | `language` cookie (read from request) | `Language::switch()` (sets cookie on document) |
| Native client | Global signal, hydrated at startup | App layer via `set_initial_language()` |

Order of initial resolution on web: saved localStorage value → browser `navigator.language`
→ `Language::default()` (`En`).

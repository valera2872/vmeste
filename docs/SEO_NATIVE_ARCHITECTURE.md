# SEO-native architecture for «Вместе к цели»

## Purpose

Search traffic can land directly on an editorial Problem Page, receive a useful result without registration, and only then continue into the private workspace.

## Layers

1. **Problem Page** — static editorial page from `web/content/problem-pages.ts`.
2. **Micro Tool** — shared generator contract and rule-based implementation in `web/lib/micro-tool/engine.ts`.
3. **User Session** — private browser-only session in `sessionStorage`; never encoded into a public URL.
4. **SEO Layer** — static metadata, canonical, OpenGraph, sitemap and robots directives.
5. **Conversion Layer** — saves the current useful step into the existing workspace and opens `/cabinet`.

## Editorial registry

New public problems are added as data, not as a new React page. Each record contains:

- `title`
- `slug`
- `problemType`
- `intro`
- `examples`
- `prompts`
- `seoTitle`
- `seoDescription`
- `status`
- optional `relatedSlugs`

Only records with `status: "published"` are included in static generation and the sitemap.

## Privacy boundary

User-entered task text stays in client state/sessionStorage and the local workspace. It is never used to create a slug, route, canonical URL, sitemap entry or other indexable resource.

## Analytics funnel

Vendor-neutral events are dispatched through `window.dataLayer` (when present) and `vmeste:analytics` CustomEvent:

`problem_page_view → tool_started → task_entered → first_step_generated → smaller_step_requested / next_step_requested → app_continue_clicked`

The event vocabulary already reserves `signup_clicked`, `paywall_viewed` and `purchase_started` for later account/monetization stages.

# Claude Code — Jarvis Implementation Prompt

Copy the prompt below into Claude Code and provide `Jarvis-PRD.md`, `Jarvis-TRD.md`, `Jarvis-Configuration-Checklist.md` and `jarvis.env.example` as context. Google AI Pro gives the user expanded Antigravity development access and currently advertises a $10/month GenAI/Cloud credit; it does not itself provide a Gemini Developer API runtime key or unlimited API quota. The same implementation prompt can be used in Antigravity. Google AI Pro does not cover Claude Code; Claude Code access may require a separate paid Claude plan or usage-billed Console account. The application itself must still follow the $0/no-paid-fallback requirements.

---

```text
You are implementing Ahmad's Jarvis in the existing Windows project:
C:\Users\ahmad\.gemini\antigravity\scratch\jarvis-sales-hub

Read the supplied Jarvis-PRD.md, Jarvis-TRD.md, and
Jarvis-Configuration-Checklist.md first. Treat them as product and safety
requirements. The product starts with BOTH launch modules:
1) Personal Management: everyday tasks, user-controlled memory of planning,
   private files, voice/text, shared login and sync.
2) Sales: unified dental-practice prospecting/lead generation in the US and
   Canada (permitted public sources/CSV → evidence → dedupe → qualification /
   rank → CRM review), a Hostinger mailbox inbox scanner/reply-draft workflow,
   research-backed sales messaging, and approval-gated outreach.

Core offer: a WEBSITE plus a lead-qualification system integrated into the
website for dental practices. Paid performance marketing and local SEO lead
generation are optional add-ons. Do not describe the core offer as lead
qualification alone or as a lead-generation service. Example first-touch copy
must not invent performance claims or details:

Subject: A website with lead qualification for {{practice_name}}

Hi {{contact_name_or_team}},
{{verified_public_observation_if_available}}
We build websites for dental practices with a lead-qualification system
integrated into the website. Paid performance marketing and local SEO lead
generation are optional add-ons.
Would a short overview be useful?
Best, {{sender_name}}

The user requested 20–30 cold emails/day eventually, but the sender domain is
not warmed; this is a later cap, not launch volume. Start with conservative
monitored sending only after setup, compliance and provider checks. Content and
software-development modules are later, not this release.

Repository and secrets
- Inspect the repository structure and safe source files first. The current
  backend/frontend folders may be empty; create a coherent modular monolith,
  not microservices.
- IMPORTANT: a real `.env` exists in the project. Do NOT open, print, copy,
  parse, summarize, modify, overwrite, upload, or include it in prompts/logs.
  Do not echo secrets from any file or environment. Never ask the user to paste
  passwords, OAuth codes, API keys, bot tokens or project secrets into chat,
  voice, this prompt or Claude.
- Do not access files outside the project except the supplied docs. Do not run
  commands as administrator. Do not deploy, attach billing, enable paid
  services, send real email, create a live campaign, purchase a lead list or
  make a real payment.
- Keep a safe `.env.example` with placeholders only. Add `.env`, `.env.*` to
  `.gitignore`, with an explicit exception only for `.env.example`. Keep local
  secrets in Windows Credential Manager through an OS keyring integration.
  Do not put Supabase service_role/secret key in the browser or app config.

Free-first product constraints
- Target zero additional spend: React/TypeScript/Vite PWA, static Cloudflare
  Pages Free, Supabase Free Auth/Postgres/Storage with owner-scoped RLS, one
  Windows FastAPI worker and SQLite cache/outbox. Gemini Developer API is the
  only planned LLM; no local LLM or local speech model is a prerequisite.
  Evaluate `gemini-3.5-flash-lite` as the first free-tier candidate; use it
  only if eligible for this project. No billing account, paid fallback or paid enrichment. Quota
  exhaustion must stop/back off and queue work with an explanation.
- Google's current Gemini 3.5 Flash-Lite paid rates are $0.30 / 1M input
  tokens and $2.50 / 1M output tokens. Illustration only: 900 drafts at 2,000
  input + 500 output tokens each would be about $1.67 on paid rates; actual use
  varies. Eligible free-tier requests are $0 within quotas. Project/model
  quotas and eligibility vary; verify them in AI Studio. Do not link billing
  or switch to a paid model.
- The PWA is served from HTTPS and installable from Edge on Windows and Chrome
  on Android; no APK/store submission. Use foreground browser/device speech
  recognition and Edge/browser TTS where supported; disclose that browser
  recognition may send audio to its provider. Offer typing/dictation fallback.
  No local Whisper/TTS model installation, wake word or background listening.
- Ahmad has Google AI Pro. It expands development access and advertises $10/mo
  Google Cloud credit through Google Developer Program, subject to eligibility
  and activation. It does not itself provide Gemini API keys or unlimited
  runtime quota, and the credit is not a hard spend cap. Do not attach billing
  or consume it automatically; keep Antigravity `AI Credit Overages` at
  `Never`. Claude Code access remains separate from Google AI Pro.
- Google free-tier Gemini prompts/outputs may be used to improve products and
  human reviewers may process them; Google says not to submit sensitive,
  confidential or personal information to unpaid services. Public business research is approved, but send only public company-level facts
  to Gemini. Redact names, email addresses, phone numbers and other person-level
  identifiers before requests; merge recipient details locally after drafting.
  Never send private inbox bodies, private voice commands/transcripts, private
  plans/files, credentials, patient/health data or other personal/confidential
  content to free Gemini. The dental website qualifier must not solicit patient
  or health details in this release. Cloud sync to Supabase is separate from model processing.
  Private-email AI needs a separate informed consent and a service tier whose
  terms permit it; that choice is not granted here and paid inference is outside
  the $0 baseline. Until then, classify/draft private inbox replies with
  deterministic rules/templates; do not install a local model as fallback.
- Use the Windows PC worker for secure Hostinger credentials, bounded inbox
  polling, Gemini API calls that pass the privacy gate, durable task execution
  and approved outbound mail. It makes outbound HTTPS requests only; expose no
  public port. Mobile queues work; actions wait until the worker is online.

Security and email connection
- First mailbox target is Hostinger `harvey@zotterlabs.com` (exact spelling).
  Verify its plan supports secure IMAP read-only access and SMTP send/auth; it
  is not connected yet. Never enter a password in chat or voice. Use a masked
  Windows Settings form for a supported app password or provider OAuth; store
  the secret in Windows Credential Manager, not prompts, sync or logs.
- Launch inbox intake is read-only IMAP polling while the PC worker is awake,
  using peek/read-only semantics. It may scan, classify and draft replies in
  Jarvis, but must not mark read, delete, archive, move or send automatically.
  Do not upload full message bodies/attachments to Supabase by default. Since
  private email may contain personal/confidential data, do not pass it to free
  Gemini. Use deterministic classification/templates until Ahmad separately
  grants informed permission and chooses data terms that permit cloud inference.
  Public-business research consent does not cover mailbox-wide model processing.
- Start with mock connectors. Add the real Hostinger read-only connector only
  after auth, account isolation, no-write verification, polling caps, revocation
  and tests. Enable SMTP sending separately after deliverability/legal checks.
  Provider support is explicit, not “any email works.”
- Every external email requires fresh approval bound to exact mailbox,
  recipient, subject, body, links/attachments and payload hash. Any edit expires
  the approval. Recheck suppression/opt-out before send. Persist a unique
  idempotency action ID before the side effect and provider message ID after
  confirmed success. On ambiguous timeout, mark needs_reconciliation and NEVER
  blind-retry. SMTP cannot guarantee exactly-once after an unknown result.
- Account/mailbox data must be isolated. Do not use inbox rotation to bypass
  provider limits. Never automatically send campaigns or follow-ups.

Prospecting and lead generation (one Sales workflow)
- Start the ICP as dental practices in the US and Canada. Independent/small
  practices are a suggested segment only; leave practice size, buyer roles and
  final filters configurable because they are not confirmed.
- Configure the offer as a website plus an integrated lead-qualification
  system on that website. Paid performance marketing and local SEO lead
  generation are optional add-ons. Do not replace the core with a lead-gen-only
  service. Use only verified product facts; do not invent pricing, results,
  case studies or website features.
- Implement a source registry and pipeline: user-provided URLs/CSV or explicit
  allowlisted public sources → fetch under per-host rate budget → extract →
  evidence → normalize/dedupe → user-configured ICP filter/score → human CRM
  review → evidence-backed message draft.
- Respect the source's terms, robots/access rules, privacy and rate limits. Do
  not scrape behind login/paywall/CAPTCHA, bypass bot controls, rotate proxies
  to evade a block, or harvest private/personal-profile data. Start with
  fixtures and CSV/manual URL imports; enable live scraping only for configured
  allowed sources. Provide a crawl pause/kill switch and request budget.
- Every extracted fact used in ranking or personalization must store canonical
  source URL, captured-at timestamp, excerpt/field reference and a
  verified/inferred/unknown status. Never invent email addresses or contact
  facts; unknown stays blank. Never claim a lead is verified when only inferred.
- Exact normalized domain/email duplicates may be linked deterministically;
  ambiguous fuzzy matches require review. Explain score reasons and display
  evidence. Capture opt-outs/suppressions; no outbound draft should proceed
  when suppressed. Use a neutral draft if no relevant verified fact exists.
- Measure quality on a labeled test set as precision-at-K and source coverage;
  leave the target configurable until the user defines ICP and threshold.
  Do not promise paid-provider coverage or unlimited/free mass scraping.

Data, sync and modules
- Use Supabase Postgres as shared source of truth, with RLS on every table and
  private owner-scoped Storage paths. Use only publishable/anon browser key plus
  the authenticated user JWT. Do not introduce service_role in the client. Do
  not enable sign-up broadly; single-owner setup is the initial target.
- Use IndexedDB for an explicit offline outbox/cache. Each write has a stable
  client_event_id so replay is idempotent. Version task/plan/file edits; surface
  conflicting edits instead of silently overwriting files or plans.
- Keep distinct modules: shared voice/assistant/policy/tasks/memory/tools;
  Personal tasks/plans/files; Sales prospecting+leadgen/CRM/messaging/inbox/
  campaigns; connectors. Content/dev tools are not in scope.
- Avoid Redis/Kafka, vector DB, multi-agent framework and paid dependencies in
  the first slice. Start with typed deterministic workflow state machines,
  SQLite FTS5/Postgres text search and a single worker.
- Add task IDs, structured redacted logs, append-only audit events, visible
  worker/sync/connector status, export/deletion controls and pause-all-outbound.
  Do not store raw audio/full email bodies in logs by default.

Build and delivery sequence
1. Produce a short repo assessment and proposed file tree. Record unresolved
   choices in `docs/open-decisions.md`. Use the confirmed US/Canada dental ICP,
   Hostinger `harvey@zotterlabs.com`, website + integrated lead-qualification
   offer, optional paid-performance-marketing/local-SEO add-ons, and eventual
   20–30/day cap. Do not invent exact practice size, buyer role, source list,
   legal basis, physical mailing address, file-retention policy or proof/pricing.
2. Implement a safe mock-first foundation: PWA shell, auth/data adapters,
   migrations, RLS policies, task/event/approval schemas, offline outbox and
   dashboard/status screens. Add fake local data only in test fixtures.
3. Implement the first joint vertical demo for BOTH modules: voice/text creates
   a plan memory + task + private file metadata; a fixture lead is sourced from
   an allowed test page/CSV with evidence, deduped, ranked and reviewed; draft
   a personalized message from fixture evidence; request approval; fake-send;
   persist audit, task state and result. Restart the worker and prove no duplicate
   send. No real mailbox or real prospect in this phase.
4. Add personal live slice (tasks, user-confirmed plan memory, file upload,
   edit/export/delete, cross-device sync) and test on Windows and Pixel foreground
   PWA with text fallback.
5. Add permitted dental prospecting and the Hostinger `harvey@zotterlabs.com`
   read-only inbox connector, with deterministic private-mail triage/templates
   and Jarvis reply drafts. Do not send, delete, archive, mark-read or move mail.
   Do not send inbox content to free Gemini. Do not enable live SMTP send until
   secure provider auth, source allowlist/ICP, legal/contact/opt-out rules,
   domain authentication and exact-payload approval tests pass.
6. Add one approved live email action only after the user configures an account
   and supplies secrets through the app's secure flow. Keep exact-payload
   approval, durable dedupe and uncertain-send reconciliation.
7. Add more providers, inboxes, source adapters, campaigns, Telegram, booking,
   WhatsApp/payment links only as separate reviewed increments. Content/dev
   modules remain deferred.

Engineering rules
- Work in small changes, preserve existing user files and avoid speculative
  rewrites. Before any destructive file/database migration, describe the change
  and preserve a recoverable backup. Never print `.env`.
- Use typed Pydantic/TypeScript schemas; validate all external/model input.
  Prompt/model output is suggestion data, not authorization. Policy checks run
  in deterministic code on every tool/action.
- Create tests for RLS owner isolation, source allowlist/rate limits, provenance,
  no guessed email, suppression, send approval/hash, duplicate restart recovery,
  timeout reconciliation, offline replay and file privacy. Use a fake mail
  adapter; tests must assert that no real network send occurred.
- Keep docs up to date: setup without secrets, architecture, test commands,
  free-tier quota behavior, source policy, supported email providers, backup/
  restore, and open decisions. Do not claim a provider or feature is verified
  until tests or a safe read-back prove it.
- Do not deploy, attach a Google Cloud billing account, redeem/use cloud credits,
  change Antigravity overage settings, or change any billing setting. At each
  phase, summarize files changed, commands/tests run, failures, security
  decisions and what still needs Ahmad's explicit choice. If implementation
  would require entering a password, pause at the secure in-app settings flow
  and tell him to enter it there himself.

Do not invent the exact dental practice size, buyer role, source whitelist,
CASL/US lawful-contact basis, sender's physical mailing address, opt-out policy,
website features, pricing or case-study proof. The requested 20–30 cold emails
per day is an eventual cap only; because the domain is not warmed, start at a
small monitored pilot after authentication and legal/deliverability checks.
The PC is usually awake 15–16+ hours/day; work queues while it is off.

Before writing code, confirm the repository layout without reading `.env`, then
start with the mock-first joint demo. Do not implement the whole feature list in
one pass; make each phase testable and stop at the stated safety gates.
```

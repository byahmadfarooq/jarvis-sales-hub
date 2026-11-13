# Jarvis — Technical Requirements Document

**Version:** 1.0 draft · **Date:** 13 November 2026  
**Basis:** Implements the attached PRD with a zero-new-spend baseline. No live credentials or user passwords are included.

## 1. Technical direction

Use a cloud-synced **modular monolith**: one React/Vite PWA, one Supabase-hosted Postgres/Auth/Storage project for shared app state, Gemini Developer API for approved cloud inference, and one Windows FastAPI worker for secure mailbox access and durable actions. There is no local LLM prerequisite. Deploy only static PWA files to Cloudflare Pages Free. The worker makes outbound HTTPS requests only; expose no public port. It owns Hostinger credentials, performs bounded inbox polling while Windows is awake, and claims user-approved work. If the PC is asleep/offline, inbox and send actions wait in the durable queue. This avoids an always-on server and keeps mail credentials off the cloud DB.

This is a recommended target, not verified existing code. The repository's `backend` and `frontend` folders were empty at the last check; do not infer an implementation from the prior Antigravity plan or its `.env.example`.

## 2. Stack and free-cost boundary

| Layer | Recommended implementation | Cost boundary |
|---|---|---|
| Web/PWA | React, TypeScript, Vite, service worker, IndexedDB | OSS; static host only |
| PWA hosting | Cloudflare Pages Free | Static assets; no paid Functions required |
| Auth/data | Supabase Auth + Postgres + RLS + Storage | Free quotas; may pause after inactivity |
| Windows worker | Python, FastAPI, Pydantic, one DB-backed queue | Runs on user's PC; no cloud worker bill |
| Local persistence | SQLite WAL cache/outbox, SQLAlchemy/Alembic | Local disk; user-triggered export/backup |
| Voice | Foreground browser/device speech recognition; Edge/browser speech synthesis; typed fallback | Capability/privacy vary; no local speech model required |
| AI inference | Gemini Developer API, evaluate `gemini-3.5-flash-lite` first | $0 within eligible free quota; project limits/data terms apply |
| CI | Local pytest/npm checks first | No hosted CI dependency in MVP |

The baseline uses only eligible Gemini Developer API free-tier requests for approved public-business/synthetic inputs; no billing account, payment method, paid model, paid grounding/enrichment or automatic paid fallback. At API quota exhaustion, stop/back off and queue the affected operation with an explanation. Google AI Pro is separate from Gemini API keys/quotas; its advertised $10/month Cloud developer credit is optional, may require activation/eligibility, and is not a hard spending cap. Do not attach billing or consume credit automatically. No Ollama/local LLM is installed or required.

The currently published Supabase Free plan lists 500 MB database, 50,000 MAU, 5 GB egress and 1 GB Storage; projects with low activity may pause after a week, and automatic DB backups are not included. Export/restore is therefore a product feature. Cloudflare Pages Free currently lists up to 500 builds/month, one concurrent build, 20-minute build timeout and 25 MiB per asset. Firebase Spark needs no payment method and its Firestore free quota is 1 GiB, 50K reads/day, 20K writes/deletes/day and 10 GiB/month egress, but the relational sales/task model fits Postgres better; Cloud Functions are not in the Spark no-cost column. Recheck plan terms before any deploy or change of provider.

## 3. Topology and trust boundaries

```text
Edge/Chrome PWA (Windows + Pixel 9a)
  ├─ public Supabase URL + publishable key only
  ├─ Supabase Auth session; RLS-bound CRUD and realtime
  ├─ IndexedDB: offline drafts, sync outbox, cached non-secret data
  └─ no mailbox password, service key, or long-lived provider token
                         │ HTTPS + user JWT
                         ▼
Supabase Auth / Postgres / Storage (free tier)
  ├─ every row keyed by owner_id; RLS on every user table
  ├─ task/action queue, approvals, CRM/evidence, memory, file metadata
  ├─ private user-scoped object paths
  └─ no email OAuth refresh token or SMTP credential in a row
                         ▲ HTTPS using a scoped owner session
                         │ outbound polling only
Windows local agent (FastAPI + durable worker)
  ├─ Windows Credential Manager: email tokens/app passwords
  ├─ Gemini API calls only through a server-side privacy/allowlist gate
  ├─ Windows Credential Manager: Hostinger IMAP/SMTP credentials
  ├─ read-only inbox poller + deterministic private-mail triage/templates
  ├─ claims only the signed-in user's authorized jobs
  └─ sends only after exact fresh approval and policy checks
```

Gemini is an untrusted suggestion service. It returns typed proposals; deterministic Python code owns permissions, task transitions, source rules, approvals and external calls. A request firewall labels inputs and permits the free API only for public business research, approved public-source facts and synthetic fixtures. Private inbox bodies, planning memory, private files and credentials are blocked by default. Inbox contents and webpages are untrusted data, never tool instructions. API and mailbox secrets stay in Windows Credential Manager and never reach JavaScript, logs or prompts.

## 4. Repository layout

```text
backend/app/{api,auth,assistant,voice,policy,tasks,memory,files,tools}/
backend/app/modules/personal/{tasks,plans,file_vault}/
backend/app/modules/sales/{prospecting,crm,messaging,inbox,campaigns}/
backend/app/connectors/{supabase,google_mail,microsoft_mail,imap_smtp}/
backend/tests/{unit,integration,e2e,fixtures}/
frontend/src/{app,auth,voice,tasks,plans,files,sales,approvals,settings}/
frontend/public/{manifest.webmanifest,icons,service-worker.js}
supabase/migrations/
```

Keep shared capabilities separate from module workflow logic. Do not add a vector database, Redis, Kafka, multi-agent framework or paid UI kit for the first release. Use SQLite FTS5 for local note search; start with Postgres text search for cloud records. Add semantic embeddings only after user-approved memory search fails a defined evaluation.

## 5. Runtime and API behavior

**PWA:** Build responsive, keyboard-accessible screens for voice/text input, dashboard, tasks, plan memory, file vault, unified lead pipeline, inbox drafts, approvals, settings and activity. Use optimistic display only for reversible local edits. A service worker caches the app shell and explicitly safe static assets, never secrets or sensitive file contents by default. Install via the browser on Edge/Windows or Chrome/Android; no store submission or APK is needed. If the browser lacks a capability, show an ordinary input fallback.

**Auth:** Use Supabase Auth and protected routes. Disable public sign-up after the owner account is established unless a later product decision changes it. Enforce RLS even when the UI hides a record. Require TLS, secure session handling and logout/revocation. Auth uses an independent app login; mailbox connection is a separate provider-consent flow.

**API/data:** Prefer the Supabase client with a user's publishable key plus JWT and RLS for ordinary user data. Use narrowly scoped authenticated RPCs for task claims/lease transitions. The `service_role` key is not required by the MVP and must not appear in the frontend, local `.env`, Claude prompt or checked-in example. If a future server-only operation cannot be safely implemented with owner-scoped RLS, stop and design a separate secret boundary first.

**Windows worker:** FastAPI binds to loopback only and runs as the normal Windows user. Store Gemini API and Hostinger credentials in Windows Credential Manager. Use one lease at a time with heartbeat/checkpoints and authenticated-owner scoping. Worker functions are allowlisted; it cannot execute arbitrary shell commands or browse arbitrary accounts. It calls Gemini server-side only after input classification passes the privacy policy.

## 6. Data model and isolation

All shared rows include `id`, `owner_id`, `created_at`, `updated_at`, `version`, and where useful `deleted_at`. RLS tests must show cross-owner reads/writes fail.

- `tasks`: title, notes, due date, status, tags, optional `plan_note_id`, source turn, client event ID.
- `plan_notes` / `memory_items`: user-authored/confirmed text, kind, source, confidence, retention, version and explicit visibility.
- `files`: private object path, display name, MIME/size, checksum, tags, creation date and version; actual bytes in a private bucket.
- `companies`, `prospects`, `contacts`: normalized company domain, source/status, user-approved fields, no synthetic contact data.
- `evidence`: entity/field relation, source URL, capture time, excerpt/hash, extraction method, evidence classification (`verified`, `inferred`, `unknown`) and source status.
- `source_registry`: user-approved source domain/API, allowed fetch types, terms review date, rate budget, enabled flag.
- `suppression`: normalized contact/domain, reason, source and timestamp; checked at draft and send.
- `mailbox_connections`: provider/account label, granted scopes and connection status only; no raw password/token in this table.
- `message_drafts`: account ID, recipient, subject/body, source evidence IDs, content hash, status and approval linkage.
- `approvals`: actor, exact payload hash, account, recipient, created/expiry/consumed timestamps and decision.
- `send_actions`: unique idempotency/action key, attempt state, provider message ID, request/result digest and reconciliation status.
- `tasks`, `task_steps`, `outbox_events`, `audit_events`: durable orchestration and redacted event history.

Use migrations under version control. Add indexes for owner, normalized domain/email, task state/lease expiry, message status and evidence lookup. Do not store full audio or complete email bodies in logs/audit events. Define retention and user export before collecting personal files or raw message bodies.

## 7. Voice and AI boundaries

**Windows:** use foreground push-to-talk through browser/device speech recognition where supported, and Edge/browser speech synthesis for responses; disclose that browser speech recognition may send audio to its provider and test the actual Windows/Edge behavior. Offer typing and text responses as universal fallbacks. No local Whisper, TTS or LLM packages are required. Voice availability does not imply background wake-word support.

**Pixel PWA:** use foreground mic capture only with permission and an explicit recording indicator. Browser `SpeechRecognition` has limited cross-browser availability, and on some browsers audio is sent to a server; disclose it and do not claim offline/private recognition. Use the phone's speech facility only when supported and opted into; otherwise use Android keyboard dictation or typing. `speechSynthesis` uses available device voices and may vary by device. Background wake word/always-on listening is out of scope. Test actual Pixel behavior before calling mobile voice supported.

The model returns a Pydantic-validated object with intent, entities, confidence and proposed action. Reject unknown fields/tools. It cannot authorize a send, invent a fact, change scopes, select another account, or bypass the policy layer. Low-confidence names, dates, recipient, amount or evidence require clarification.

### Google AI Pro and Gemini API boundaries

Google AI Pro supports expanded development access in Antigravity/AI Studio and advertises US$10/month in Google Cloud credits through Google Developer Program; eligibility/activation must be checked. It does **not** itself create a Gemini Developer API key, guarantee free API quotas, or provide unlimited runtime. Gemini Developer API uses its own project and model-specific quotas. The included credit is optional and not a hard spend cap; do not attach billing or consume it automatically. Keep Antigravity AI Credit Overages at `Never`.

**Runtime choice:** Gemini Developer API is the only planned LLM; there is no local model prerequisite. Evaluate `gemini-3.5-flash-lite` as the first free-tier candidate; use it only if the model/project is eligible. Google's published free tier is $0 within its per-project/model limits; those limits vary and are visible in AI Studio. On limit errors, back off/queue; do not automatically attach billing or switch to a paid model. Public business research is approved, but send only company-level public facts to Gemini; redact contact names, emails, phone numbers and other person-level identifiers before each request, and merge them into drafts locally. The free-tier terms allow Google to use prompts/outputs to improve products and allow human review, and say not to submit sensitive, confidential or personal information. Therefore block private inbox bodies, private voice commands/transcripts, personal planning memory, private file contents, PHI and secrets, irrespective of this public-research approval. Private app sync to Supabase is a separate data flow and does not grant permission for Gemini processing. Use deterministic code for basic task CRUD/search and private inbox templates; no local LLM is installed as a fallback. The lead-qualification website must not solicit patient/health details in this release.

Google's current published paid rate for Gemini 3.5 Flash-Lite is $0.30 per 1M input tokens and $2.50 per 1M output tokens. For scale only, 900 requests with 2,000 input and 500 output tokens each would be about $1.67 at those rates, excluding any search/grounding tools, retries or larger context; actual usage is unknown. Eligible free-tier requests cost $0 within quota; paid rates are for comparison only. Paid service is outside the $0 baseline, requires billing, and is not an automatic fallback. Private-email cloud inference needs a separate informed choice and appropriate service terms; it is not enabled by this plan. Keep API keys only in Windows Credential Manager, never Vite variables, the synced DB, logs or `.env.example`.

## 8. Unified prospecting and lead generation

ICP: dental practices in the US and Canada. Independent/small practices are a recommended starting hypothesis, not a user-confirmed size rule. Core offer configuration is a website plus a lead-qualification system integrated into that website; paid performance marketing and local SEO lead generation are optional add-ons. Pipeline: `source selection → bounded fetch/import → extract → normalize → evidence record → exact dedupe → ICP filter/rank → human review/CRM import → evidence-backed draft`.

1. Start with user-entered URLs and CSV, plus a small allowlisted adapter for sources that permit automated access. Integrate an API only if its current free allowance, terms, data reuse rules and volume fit; do not ship paid enrichment by default.
2. Fetch only public, permitted pages. Respect site terms, robots/access directives, rate limits, privacy rules and source-specific exclusions. Use per-host budgets, timeouts, cache validators and a pause switch. No login, paywall, CAPTCHA, anti-bot or rate-limit bypass; no proxy rotation to evade a block.
3. Store provenance for each extracted fact: canonical URL, fetched time, excerpt or field reference, extractor/version and fact status. Distinguish verified evidence from model inference and unavailable fields. Do not infer or generate email addresses.
4. Normalize company names/domains and email addresses. Exact domain/contact matches can be linked automatically; fuzzy/conflicting duplicates wait for human review. Preserve source history when merging.
5. Score with explicit user-configured criteria. Every score has positive/negative reasons tied to evidence. The UI reports a labeled-sample precision-at-K and coverage, not a “good lead” claim without an agreed target and test set.
6. Before drafting, recheck source freshness, evidence and suppression. Use a verified company-level detail for personalization; no evidence means neutral copy. Do not infer sensitive personal attributes.

## 9. Email connection and send safety

**Connection:** first target is Hostinger `harvey@zotterlabs.com`. Verify the plan's documented secure IMAP/SMTP hosts, TLS and supported app-password/auth policy before claiming integration; the mailbox is not yet connected. Collect credentials only in a masked Windows Settings flow and store them in Windows Credential Manager, never chat/voice or synced configuration. Start with IMAP read-only/peek access; use SMTP for sending only after separate test and approval gates. Provider support is conditional on plan/auth policy; do not fall back to a normal account password.

**Inbox scan/draft:** while the Windows worker is awake, poll the Hostinger INBOX on a bounded, configurable cadence with read-only semantics (`EXAMINE`/peek); fetch only the messages needed, classify into a user-visible category, and store a reply draft in Jarvis. Do not mark messages read, delete, archive, move, or send. Keep raw bodies/attachments on the Windows worker by default; sync only the minimum metadata/draft fields explicitly needed. Private content cannot go to Gemini free tier, so use deterministic classification and templates until separate compliant consent is recorded. Do not treat mailbox access as permission to send all mail to a model.

**Scopes:** keep the initial inbox connector read-only; add SMTP/send only after provider support and approval tests. Never request delete/modify scopes for the initial slice. For later OAuth providers, request only necessary scopes, use PKCE where supported, and keep client secrets out of the PWA.

**Send protocol:**
1. Persist draft with selected `mailbox_connection_id`, recipient, body, evidence and opt-out checks.
2. On send request, re-evaluate source/recipient suppression and connector status.
3. Show exact account, recipient, subject, body and included links/files; obtain user confirmation.
4. Persist single-use approval bound to payload hash and idempotency key; any edit invalidates it.
5. Worker atomically claims the action, marks attempt started, sends once, and stores provider receipt/message ID.
6. On confirmed success, mark sent. On known pre-send failure, return a safe error. On ambiguous timeout, mark `needs_reconciliation`; never blindly repeat.

Exactly-once email delivery cannot be guaranteed by generic SMTP after an ambiguous network failure. The design guarantees no duplicate retry after confirmed receipt and makes uncertain outcomes visible for reconciliation. Tests must simulate crashes before/after provider acceptance.

## 10. Offline sync and file handling

Postgres is canonical for shared data; IndexedDB holds a bounded local cache and outbox. Each mutation has a stable `client_event_id` unique per user for replay safety. On reconnect, apply events in order and return canonical version/state. Scalar task edits can use optimistic version checks; conflicting plan notes/files are shown as conflicts, not overwritten by last-write-wins. File uploads are private and resumable only if supported; compare checksums, retain versions or require explicit replace confirmation. User-initiated export covers Postgres records and file manifest/contents; test restore to a clean project/local backup. Do not promise full local offline access to every cloud file.

Supabase Free inactivity pause can temporarily make cloud sync unavailable. The app must show this as a recoverable service pause, keep local outbox entries, and never suggest an automatic paid upgrade. There is no free-tier automatic DB backup in the published plan; schedule no paid backup product in the baseline—provide an explicit export workflow and a documented manual reminder.

## 11. Security, secrets and privacy

- Supabase publishable/anon key may be present in PWA config only with RLS, least privilege and no embedded sensitive data. It is not a substitute for RLS.
- Never ship Supabase `service_role`/secret key, database password, OAuth client secret, provider refresh token, SMTP/app password, Telegram bot token, Gemini key, Stripe secret or deployment token to frontend or repository.
- Local provider credentials are stored via Windows Credential Manager/OS credential vault. Cloud OAuth refresh tokens would require a server-side vault and encryption-key management; that is outside the $0 baseline and requires explicit approval/design.
- OAuth state/nonce and PKCE protect the login flow. Use exact redirect allowlists, same-origin protections and scoped tokens; support account disconnect/revocation.
- Email/web content is data, never instructions. Defend against prompt injection by keeping tool schemas/policy outside the prompt and redacting secrets before model calls.
- Keep files private with owner-scoped Storage policies, MIME/size limits, checksum and signed short-lived downloads; never public buckets by default.
- Logs use correlation IDs, redaction and bounded retention. Do not store password values, authorization headers, audio or whole customer emails by default.
- Site scraper must obey per-source budgets and a kill switch. Legal review/user source configuration is required before live crawl or outbound campaign.

## 12. Observability and acceptance tests

Every action has `task_id`, `owner_id`, module, correlation ID, policy result, source/approval reference, retry count and outcome; redact content. Dashboard shows worker last-seen, queue age, connector health, sync status, failure/unknown state and global outbound pause.

Test layers:
- Unit: schemas, capability matrix, evidence labels, ICP scoring reasons, suppression, dedupe, approval hashing, state transitions and output redaction; assert private data is blocked from Gemini free tier and paid fallback is impossible.
- Integration: Supabase RLS with two test owners; storage policies; OAuth callback/token storage using fake credentials; IMAP/SMTP/API mocks; migration and export/restore.
- Scraper safety: deny private/authenticated URLs, disallowed host, paywall/login/CAPTCHA pages, robots/terms-disabled source and over-budget request; enforce timeouts and backoff; no guessed email output.
- Durability: repeat event ID, duplicate approval, expired/edited approval, crash before send, crash after provider accepts, lost response, restart and reconciliation.
- PWA: installability, keyboard/accessibility, offline create/sync-once, version conflict, cross-device data isolation and file privacy.
- End-to-end: synthetic task+plan+file and fixture lead+evidence+draft+mock approval+fake mailbox; assert no real outbound request.
- Manual release gate: Pixel 9a foreground speech/text/TTS fallback; Windows loopback worker, Credential Manager, Hostinger read-only inbox, Gemini free-tier quota handling, no-paid-fallback and manual backup/restore.

## 13. Configuration and sources

Use the separate `Jarvis-Configuration-Checklist.md` and `jarvis.env.example`. The checked-in example contains only public identifiers and obvious placeholders; connection secrets are entered only through secure Settings/OAuth. Do not inspect, print or overwrite the existing project `.env`.

References: [Supabase pricing](https://supabase.com/pricing), [Supabase project pausing](https://supabase.com/docs/guides/platform/free-project-pausing), [Firebase pricing](https://firebase.google.com/pricing), [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/), [Web Speech API support](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition), [Gmail OAuth scopes](https://developers.google.com/workspace/gmail/api/auth/scopes), [Claude Code plans](https://claude.com/pricing?mode=code), [Google AI plans](https://one.google.com/about/google-ai-plans/), [Google Developer Program credits](https://developers.google.com/program/plans-and-pricing), [Antigravity plans](https://antigravity.google/docs/plans), [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), [Gemini API terms](https://aistudio.google.com/docs/terms), [Gemini API data retention](https://aistudio.google.com/docs/zdr), [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits). Terms/quotas checked 13 November 2026; verify again before a production rollout.

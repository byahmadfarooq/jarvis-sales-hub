# Jarvis Personal Assistant — Architecture Draft

**Status:** Proposed target architecture · **Date:** 13 November 2026  
**Scope:** A Windows-first personal assistant with the existing outreach/sales system retained as one bounded module. This is an architecture proposal, not a claim that the components are already implemented.

## Recommendation

Build a **cloud-synced modular monolith with a Windows worker**, not a collection of autonomous agents or microservices. Use one installable PWA, Supabase for app sync/state, Gemini Developer API for approved cloud AI, and a Windows worker for secure Hostinger access and durable actions. No local LLM is required. The worker is still needed while the PC is awake; when it is off, inbox and send jobs queue.

The Jarvis core owns voice/text, conversation, task planning, user-controlled memory, permissions and execution. Personal Management and Sales are both launch modules. Sales owns unified dental prospecting/lead generation, CRM, messaging, Hostinger inbox scan/reply drafts, and later booking/WhatsApp/payment routing. The core offer is a website plus an integrated lead-qualification system on that website; paid performance marketing and local SEO are optional add-ons. External actions pass through permissions and audit; Gemini never sees credentials, private voice commands, inbox bodies, plans or files by default.

## Current-state check

The screenshot and local project contents provide different levels of evidence. Treat the screenshot as the existing plan, not proof of a running system.

| Item | Evidence | Status |
|---|---|---|
| Project folders | `backend` and `frontend` exist but contain no files | Verified empty |
| Example configuration | `.env.example` names Gemini, Hostinger, optional Gmail/Brevo, booking, WhatsApp, payment and Telegram settings | Verified plan/config template |
| Welcome audio | `data/jarvis_welcome.mp3` exists | File verified; voice/model not verified |
| Edge Neural TTS | Screenshot says `en-GB-RyanNeural` was tested locally | Screenshot claim only |
| FastAPI/dashboard | Screenshot says to launch the backend and open dashboard | Planned; not verified running |
| Telegram approvals | Screenshot lists bot connection as a next step | Planned; not verified connected |
| Sales capabilities | User brief lists sourcing, multi-inbox email, classification, booking, WhatsApp, payment links and dashboard | Required scope; implementation not found |

I did not inspect `.env`; treat it as sensitive. No backend or frontend source files were present to verify behavior. The screenshot also mentions a Three.js/Canvas HUD; keep that as optional presentation, not a dependency of task correctness.

## System shape

```text
Edge / Chrome PWA (Windows + Pixel 9a)
     │ foreground voice/text; transcript/edit
     ▼
Assistant orchestrator + deterministic policy gate
     ├── Personal Management: tasks, plan memory, files
     ├── Sales: public dental leads, CRM, offer messages, inbox drafts
     ├── Gemini API broker: public/non-sensitive business inputs only
     └── approvals + durable queue + audit/status
             │ HTTPS + owner auth/RLS
     ┌───────┴───────────┐
  Supabase sync       Windows worker (while awake)
  tasks/files/CRM     Credential Manager + read-only Hostinger IMAP
                      Gemini relay + approved SMTP send
```

The model proposes a typed action; deterministic code validates it, checks policy and either queues it, asks for approval or refuses it. A task runner executes small steps and records outcomes. External content (email, web pages, Telegram messages) is untrusted data, never instructions that can override Jarvis policy.

## Module boundaries

| Module | Owns | Must not own |
|---|---|---|
| `voice` | Push-to-talk, audio capture, STT/TTS, transcript UI | Tool permissions |
| `assistant` | Turns, intent schemas, planning, response composition | Provider credentials |
| `policy` | Capability checks, risk tiers, approval rules | Business workflow state |
| `tasks` | Durable state machine, retries, cancellation, idempotency | Message content generation |
| `memory` | User-approved facts, preferences, searchable history | Hidden model-only memory |
| `tools` | Typed capability registry and common audit wrapper | Arbitrary agent-generated code |
| `sales` | Dental prospects, CRM, website + on-site qualifier offer, Hostinger inbox drafts | Core identity or global permissions |
| `connectors` | Provider-specific email, Telegram, calendar, payment APIs | Cross-account decisions |
| `dashboard` | Task/activity view, approvals, settings and health | Direct unguarded provider calls |

Keep each mailbox as a separate configured connector with its own identity, permissions, rate limits and health. The Sales module can select a sender only under explicit policy; do not use silent account rotation to evade provider limits. WhatsApp should initially create a user-reviewed click-to-chat route; use an official API only if later justified. Treat payment links as allowlisted, labelled destinations and show the recipient, amount/currency (when applicable) and exact URL before sharing.

A practical initial layout:

```text
backend/app/{api,assistant,voice,policy,tasks,memory,tools}/
backend/app/modules/sales/{leads,campaigns,inboxes,replies,booking,whatsapp,payments}/
backend/app/connectors/{email,telegram,calendar,payments}/
backend/tests/{unit,integration,e2e}/
frontend/src/{voice,dashboard,approvals,settings}/
```

## Windows implementation choices

- **API/runtime:** Python 3.12+, FastAPI, Pydantic models for every intent/tool input and output. Run locally as a normal user, bound to `127.0.0.1`; expose a health endpoint. Keep business logic out of route handlers.
- **UI:** TypeScript + React + Vite dashboard served locally. Start as a local web app; add a native wrapper only if Windows tray, startup or audio-device integration proves necessary. Use server-sent events for task/activity updates before adding WebSockets.
- **Persistence:** Supabase Postgres/Auth/Storage is the shared source of truth with per-user RLS. Keep a bounded IndexedDB/SQLite local cache and durable outbox on Windows for offline edits and worker jobs; export and restore are explicit user actions. Do not store connector secrets in Supabase.
- **Task execution:** A separate, single local worker reads a database-backed queue. Use leases/heartbeats, bounded retries with backoff, per-step checkpoints and idempotency keys. Do not start with Redis, Kafka or a distributed-agent framework. If the project later needs distributed workflows and multiple machines, evaluate a durable workflow engine then.
- **Voice:** Begin with foreground push-to-talk, not an always-listening wake word. Use browser/device speech recognition where supported, disclose that the browser may send audio to its own cloud service, and retain typed input as a fallback. Use Edge/browser speech synthesis for output when available; voice support depends on Edge/Pixel behavior. No local speech or language model installation is required. Read back critical entities (recipient, date, amount) for confirmation.
- **AI:** Gemini Developer API is the only planned LLM provider, using the eligible free tier only; no local LLM and no paid fallback. It may process public company-level business facts and synthetic/non-sensitive test data; redact personal contact names, emails and phone numbers before requests. The free tier can use prompts/outputs for product improvement and human review, so do not send private inbox bodies, voice commands, planning memory, files, credentials or patient/health data. The dental website qualifier must not solicit patient/health details initially. Keep private-mail triage/drafts deterministic unless separate informed consent and compatible service terms are later chosen. Record model/prompt version and redacted usage metrics, never secrets or full message bodies.
- **Antigravity:** Use it to build and test within the repository. Give the coding agent no production credentials and no blanket permission to send, pay, browse arbitrary accounts or run destructive commands. Check generated diffs and run the test suite before accepting changes.

## Voice, orchestration and memory

### Voice interaction

1. User presses and holds a microphone button; the UI shows recording state and a stop/cancel control.
2. Speech becomes a transcript. If transcription is ambiguous or a critical field is uncertain, Jarvis asks a short clarification instead of guessing.
3. Jarvis states its interpretation and next step. Read-only, low-risk questions can proceed; external side effects become a draft or approval request.
4. Jarvis speaks the result and shows the same result and task status on the dashboard. Provide a text-only path when mic, network or TTS is unavailable.

Add a wake word only after the push-to-talk flow is dependable, with a visible mute state and explicit audio-retention setting.

### Orchestration and durable tasks

Represent workflows as versioned deterministic state machines, not a free-running chain of agent prompts. Suggested task states: `queued`, `running`, `waiting_approval`, `retry_wait`, `succeeded`, `failed`, `cancelled`, and `needs_reconciliation`. A task record should include its ID, initiating user/turn, module, state, timestamps, retry count, idempotency key, approval reference and redacted result summary.

Commit task state and an outbox event in one database transaction before notifying Telegram or starting a side effect. On restart, reclaim expired worker leases and resume from the last completed step. If a network timeout leaves it unclear whether an email or payment-link message was sent, mark it `needs_reconciliation`; check provider state or ask the user before retrying. Never assume a timeout means “nothing happened.”

### Persistent memory

Start with explicit, inspectable memory: preferences and facts with source, timestamp and confidence; sales records in their own tables; and a task/event history. Keep transient conversation context separate and short-lived. Use Postgres text search for synced records and an optional local cache. Do not send private memory to Gemini free tier; exact search/filtering can work without cloud AI. Add embeddings only after a measured retrieval gap and separate data review.

Give the user controls to view, correct, forget and export stored memory. Set retention deliberately. Do not retain raw audio by default; store transcripts only when needed and disclose the setting. Do not treat an email or a model inference as a durable fact without recording provenance and allowing correction.

## Permissions and safety

Enforce permissions in code for every tool call, independent of the model prompt. Start with capability grants such as `sales.leads.read`, `sales.email.read`, `sales.email.draft`, `sales.email.send.approved`, `booking.link.share.approved`, and `payment_link.share.approved`. The first Hostinger inbox grant is read-only; do not mark read, delete, archive or move mail. Each connector receives only the credentials and operations it needs. An AI data-policy gate blocks private email, plans/files, credentials and health information from Gemini. Deny unknown tools and unexpected arguments by default.

| Risk tier | Examples | Default behavior |
|---|---|---|
| Read | Search a lead, classify a reply | Run within granted scope; log |
| Prepare | Draft an email, suggest a booking route | Save as draft; show user |
| External action | Send email, share WhatsApp/payment link, book | Fresh approval for exact action |
| Destructive or financial | Delete records, refund, charge, change access | Disabled initially; explicit user action |

A Telegram approval must be tied to the exact action: show recipient, account, channel, final text or link, and expiry; bind an opaque one-time approval ID to a hash of the payload; validate the allowlisted Telegram user/chat; consume it once; reject expired or changed payloads. Editing a draft invalidates its approval. Do not accept “approve all future messages.” Telegram approval is a control surface, not an authentication substitute for the bot token.

For outreach, keep suppression/unsubscribe checks, consent/source tracking, per-inbox rate limits and a global kill switch in deterministic code. Start with a small permitted test set and user approval for every outbound message. Do not use lead sourcing or sender rotation to bypass privacy law, site terms or mail-provider limits. Treat prompt injection in inbound messages as hostile; it cannot change policy, secrets or available tools.

Store provider secrets in Windows Credential Manager (through a maintained OS-keyring integration) rather than source, logs, prompts or dashboard responses. Keep `.env.example` to dummy values; do not commit a real `.env`. Protect the local UI with an app token or Windows-local authentication, strict CORS/CSRF checks and loopback-only binding. Encrypt backups and document how to revoke connector tokens.

## Observability and testing

Every task and external action gets a correlation ID. Emit structured, redacted logs and an append-only audit trail recording who/what initiated an action, policy decision, approval ID, connector result and retry. Show queued/running/waiting/failed tasks and connector health in the dashboard. Log counts, timings and error categories, not secrets or full customer messages. Include a pause-all-outbound control and a clear recovery path for stuck or uncertain tasks.

Test the safety boundary as well as the happy path:

- Unit-test intent schemas, permission decisions, state transitions, retries and redaction.
- Use fixture emails for classification, including ambiguous replies, unsubscribe requests and prompt-injection attempts.
- Contract-test each connector with mocked provider responses; test mailbox identity isolation.
- Test duplicate delivery, timeouts, worker crash/restart, stale leases, expired/used approvals and edited-after-approval payloads.
- Run end-to-end tests with a fake mailbox/payment service and a Telegram test bot; assert that no real message, booking or payment is made.
- Add a small manual Windows smoke test for microphone, TTS fallback, app restart, database backup/restore and kill switch.

## Phased delivery

1. **One dependable demo:** Use a synthetic dental practice and allowed fixture source; create a task/plan item; qualify a lead with evidence; draft the website + integrated lead-qualification offer; read a fixture inbox message; prepare a template reply; request exact approval and use a fake sender. Persist task/audit trail and prove restart-safe duplicate prevention. No real mailbox or prospect in this phase. This is the first definition of “working end to end.”
2. **Personal live slice:** Enable tasks, user-confirmed plans, private file library, export and Supabase sync; verify Windows and Pixel PWA.
3. **Public research + read-only inbox:** Use Gemini free tier only for approved public business data. Connect Hostinger `harvey@zotterlabs.com` via read-only IMAP after plan/auth verification; poll while the PC is awake, classify privately with deterministic rules/templates and save Jarvis reply drafts. Never send inbox content to free Gemini.
4. **Approval-gated outreach:** After legal/source review, domain SPF/DKIM/DMARC and a conservative monitored pilot, enable one SMTP send only with exact-payload approval and durable reconciliation. Treat 20–30/day as a later cap, not initial volume.
5. **Add-ons and later modules:** Add booking/WhatsApp/payment routing, additional inboxes, Telegram, content and development modules only in separate reviewed phases.

**Release gate for each phase:** tests pass; permission scopes are documented; recovery and audit behavior are demonstrated; an outbound kill switch works; no secret appears in logs or repository; and a human can explain what happened from the dashboard.

## First implementation tickets

1. Add repository README and threat-model notes; keep real credentials out of source and Antigravity context.
2. Create typed `Task`, `Approval`, `ToolRequest` and `ToolResult` schemas plus SQLite migrations.
3. Build the task state machine, durable worker, event log and local task dashboard with mock connectors.
4. Implement push-to-talk/transcript/TTS interfaces and a synthetic-lead fixture workflow.
5. Add Telegram approval bound to exact payload hash, then prove duplicate/stale approvals are rejected.
6. Connect Hostinger `harvey@zotterlabs.com` read-only only after the mock end-to-end demo passes and the mailbox plan/auth flow is verified.

**Decision:** keep the sales system intact as `modules.sales`; improve its safety and reliability at the shared tool/task boundary instead of letting its outreach logic become the Jarvis core.

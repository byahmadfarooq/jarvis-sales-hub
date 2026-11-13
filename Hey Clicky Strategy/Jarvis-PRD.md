# Jarvis — Product Requirements Document

**Version:** 1.0 draft · **Date:** 13 November 2026  
**Status:** Proposed; decisions still open are listed at the end.  
**Product:** Windows-first personal Jarvis, installable as a PWA on Windows and the user's Google Pixel 9a, with Personal Management and Sales both in the launch scope.

## 1. Product decision

Build one assistant with two launch modules: **Personal Management** (everyday tasks, user-controlled memory of plans, and private files) and **Sales** (prospecting/lead generation, CRM, research-backed sales messaging and a connected mailbox). The modules share voice, identity, sync, files where explicitly attached, task execution, permissions and audit history. Content creation and software-development helpers are later add-on modules, not launch scope.

The Sales workflow treats prospecting and lead generation as one capability: discover from allowed public sources or user imports, preserve evidence, deduplicate, qualify and rank, add approved prospects to CRM, then prepare personalized drafts. “Very good lead generation” means traceable, relevant, deduplicated and honest about gaps—not a promise of paid-database coverage or a fabricated email address.

## 2. Current-state evidence

The earlier project folder is `C:\Users\ahmad\.gemini\antigravity\scratch\jarvis-sales-hub`. Its `backend` and `frontend` folders were empty when checked. `.env.example` lists proposed Gemini, Hostinger, optional Gmail/Brevo, booking, WhatsApp, payment and Telegram settings; `data\jarvis_welcome.mp3` exists. The Antigravity screenshot claims Edge Neural TTS was tested and shows FastAPI/dashboard and Telegram connection as next steps; those claims were not independently verified. Do not treat existing plan text or environment-variable names as implemented integrations. The real `.env` was not inspected and must stay secret.

The earlier tool comparison informed the free-first choices here: React/Vite PWA, FastAPI, Supabase, Cloudflare Pages and Gemini Developer API. The target uses Gemini cloud inference without a local language-model prerequisite; the Windows worker remains local for secure mailbox access and durable queued actions. This is a proposed design, not evidence those integrations are implemented.

## 3. Goals and non-goals

### Goals
- Make voice or text a natural front door to tasks, planning notes, files and Sales workflows.
- Persist tasks, plans, prospects, evidence, approvals and outcomes across restarts and devices.
- Support installing the same responsive PWA on the Windows laptop and Pixel 9a without an app-store developer subscription or APK.
- Connect supported email accounts through an explicit, secure provider flow; never ask for the mailbox password in chat or voice.
- Provide careful, useful prospecting and sales drafts with source evidence, deduplication, suppression checks and approval before every send.
- Keep the prototype at $0 in new recurring software/hosting costs, subject to free-tier quotas and existing hardware/internet/email costs. Disable paid fallback paths.

### Non-goals for launch
- Content-production and software-development agents.
- Always-listening voice, reliable background voice on a phone, or guaranteed offline mobile speech recognition.
- Unbounded bulk scraping, private-profile harvesting, paywall/login/CAPTCHA bypass, or purchased enrichment.
- Autonomous email sending, automatic follow-ups, payments, refunds, bookings or destructive file actions.
- Guaranteed always-on cloud processing at $0, paid-data-provider completeness, or a claim that all email providers are compatible.

## 4. Users and core journeys

The first user is Ahmad, operating a personal Windows laptop and Pixel 9a. The user controls the connected mailbox, task data, memory, file retention, outreach audience and approvals. This is initially a single-user app; the data model must still enforce per-user ownership from day one.

### Personal journey
1. User presses the microphone button or types: “Remember my plan to finish the proposal, and make a task for Friday.”
2. Jarvis transcribes or reads the text, previews the proposed memory and task, and asks if a critical date/detail is unclear.
3. User confirms; Jarvis saves the plan with provenance and a linked task, then reads back the result.
4. User can later ask what was planned, edit/forget the memory, mark the task complete or export their data.

### File journey
1. User uploads a file or selects it using the device file picker; Jarvis records title, type, owner, date and optional tags.
2. File access is private to the signed-in user. Search shows relevant metadata; download/replacement/deletion is user-controlled and audited.
3. A file is never silently shared with a prospect or treated as a CRM attachment.

### Prospect-to-approved-outreach journey
1. User supplies a target profile and allowed public sources, or imports a CSV. Jarvis discovers candidates only within that scope.
2. Each candidate carries source URL, capture time, supporting excerpt/field evidence, field confidence and a clear verified/inferred/unknown label.
3. Jarvis normalizes and deduplicates candidates, applies user-configured exclusions and fit rules, and explains each score. Ambiguous matches go to review rather than an automatic merge.
4. User approves a lead into CRM. Jarvis uses verified company evidence to draft a first message or follow-up; it never invents an email, role, personal fact or reason for contact.
5. Jarvis shows the chosen sender account, recipient, subject, final body, evidence and opt-out status. The user approves that exact payload. Only then can the worker attempt one send and record the provider receipt.
6. If a timeout makes delivery uncertain, the task is marked for reconciliation and is not blindly resent. A reply or opt-out suppresses further campaign drafts/actions as configured.

### Secure email connection journey
The user can say “Connect my email.” Jarvis opens a dedicated connection flow. Prefer provider OAuth/consent with the narrowest scopes; tokens are stored encrypted by the Windows integration service, not in browser storage, synced rows, prompts or logs. For providers that only support IMAP/SMTP, ask the user to enter an app password in a masked Settings form only when the provider supports one, then store it in Windows Credential Manager. Passwords are never typed into chat, voice, model context, Claude Code, logs or shared files. A provider not explicitly supported is reported as unsupported until its authentication and sending behavior pass tests.

## 5. Launch module priorities

| Priority | Module/workflow | Launch slice |
|---|---|---|
| P0 | Shared assistant shell | PWA, login, voice/text, dashboard, approvals, activity and task status |
| P0 | Personal Management | Tasks, planning notes/memory, file library and sync/offline queue |
| P0 | Sales | Dental prospecting/lead generation, CRM, offer messaging, Hostinger inbox scan/reply drafts and approval-gated outreach |
| P1 | Sales expansion | Multiple inboxes, campaign/pitch management, more source adapters and bounded follow-up drafts |
| P1 | Optional connectors | Telegram approvals, booking links, WhatsApp handoff and payment-link sharing, each approved |
| Later | New modules | Content creation and software-development assistance |
| Later | Advanced voice | Wake word, native Windows wrapper, always-on or background mobile voice |

P0 means both personal and sales are represented in the first working release; it does not mean every provider or scale feature ships in the first demo. Start both modules with mocked, end-to-end vertical slices. Enable real connectors incrementally after their safety gates pass.

## 6. Functional requirements

**PR-01 Identity and sync.** The user signs into one account across Windows and Pixel. Every record is scoped to that user. The app clearly indicates online, offline, syncing, conflict and pending-worker states.

**PR-02 Voice and text.** Foreground push-to-talk works only with mic permission and a visible recording state; typed input is always available. Use browser/device speech recognition where supported, disclose that recognition may be cloud-processed by the browser provider, and fall back to typing rather than installing a local model. Use Edge/browser speech synthesis for spoken responses where available. Show the transcript and offer cancel/edit before any external action; no wake word or background listening.

**PR-03 Tasks.** Create, edit, complete, search and sort tasks; attach dates, status, tags and optional plan links; persist changes through restart. Voice parsing must not silently invent a due date. Reminders are in-app initially; background delivery is best-effort and disclosed.

**PR-04 Plan memory.** Save user-confirmed plans, decisions and preferences with source, timestamp, user scope and correction/deletion controls. Distinguish a quoted user fact from a model inference. Do not silently convert arbitrary private content into long-term memory.

**PR-05 Files.** Upload, list, search, download, tag, replace and delete user-owned files. Private by default; no public links, sharing or AI ingestion without a clear action. Preserve a version or ask before destructive replacement. Provide export/deletion controls.

**PR-06 Prospecting and lead generation.** Treat discovery, allowed-source extraction, user CSV import, normalization, deduplication, qualification/ranking and CRM import as a single workflow. Use only a source allowlist and documented provider/API terms, conservative per-host rate budgets and an auditable crawl history. Do not bypass login, paywall, CAPTCHA, robots/access restrictions or provider limits. Respect do-not-contact/suppression records.

**PR-07 Lead evidence and quality.** Each fact used for ranking or personalization must carry evidence URL, captured-at time and a verified/inferred/unknown label. Preserve a supporting excerpt or field-level source reference. Do not invent contact details. An email is sendable only when sourced and verified under the configured rule; otherwise leave it blank/unknown. Show why a lead matches or fails the user-defined ICP.

**PR-08 CRM.** Store prospects, companies, contact points, source evidence, qualification reasons, status, interactions and opt-out/suppression state. Dedupe exact normalized email/domain deterministically; put ambiguous fuzzy matches into a human review queue. Imported CSVs are previewed and deduplicated before commit.

**PR-09 Sales messaging.** The launch ICP is dental practices in the US and Canada; independent/small practices are a recommended starting hypothesis, not a confirmed size rule. The core offer is a **website plus a lead-qualification system integrated into that website**. Paid performance marketing and local-SEO lead generation are optional add-ons, not the core offer. Draft research-backed first emails and follow-ups using verified public company-level evidence; show evidence and label unknowns. Before a Gemini request, strip contact names, email addresses, phone numbers and other person-level details; merge the recipient locally after drafting. Never invent contact details, results, pricing, or claims. The website qualifier must not collect patient/health details in the initial release. Use neutral copy when evidence is absent. Every send needs fresh exact-payload approval; no bulk sending or automatic follow-up.

Sample first-touch copy (only personalize with verified public facts):

> Subject: A website with lead qualification for {{practice_name}}
>
> Hi {{contact_name_or_team}},
>
> {{verified_public_observation_if_available}}
>
> We build websites for dental practices with a lead-qualification system integrated into the website. Paid performance marketing and local SEO lead generation are optional add-ons.
>
> Would a short overview be useful?
>
> Best,
> {{sender_name}}

**PR-10 Mailboxes.** First target: Hostinger mailbox `harvey@zotterlabs.com` (exact spelling). Verify the mailbox plan and supported secure IMAP/SMTP authentication before claiming support; keep credentials in Windows Credential Manager entered only through a masked Settings flow. Launch inbox intake is read-only IMAP polling while the Windows worker is awake, using read-only/peek semantics; scan and classify incoming messages and save reply drafts in Jarvis. Never delete, archive, mark-read, or send automatically. Additional inboxes are later, separately scoped connectors.

**PR-11 Inbound and approvals.** Scan incoming messages read-only, classify with rationale/confidence, and draft a reply; do not delete, archive, mark-read, or send automatically. Private email bodies are not sent to Gemini's unpaid/free API. Until separate informed consent and compatible data terms are in place, use deterministic rules and reply templates for private mail; the model may draft only from public/synthetic or explicitly approved non-sensitive inputs. Every external send approval is fresh and bound to exact account, recipient, subject, body and attachments; edits invalidate approval. Recheck suppression/opt-out immediately before sending.

**PR-12 Durable actions.** Persist an idempotency key, approval reference, attempt state and result before/after the provider call. Record the provider message ID when available. Never blindly retry an ambiguous send. Surface a `needs_reconciliation` state after an uncertain timeout.

**PR-13 Safe connector setup.** Account linking begins from the in-app Settings/Connections page. OAuth uses provider sign-in/consent and revocation; SMTP-only credentials use a dedicated masked secure form. No credential entry via conversation.

**PR-14 Privacy and control.** The user can view, export, correct and delete their memory, tasks, files and CRM records. Deletion is confirmed in the app. The app provides pause-all-outbound and disconnect/revoke controls.

## 7. Measurable acceptance criteria

- A test journey in each module runs end-to-end with fixtures: create/retrieve a plan-linked task and file record; import a sourced lead, deduplicate it, draft an evidence-backed message, request approval and simulate the send.
- Every lead record created from discovery/import has source provenance; every used personalization fact points to evidence. Automated tests assert 100% provenance for the test corpus.
- The test suite rejects guessed email addresses, unsupported personal claims, missing evidence, suppressed contacts, disallowed sources and over-budget crawl attempts.
- The lead score includes a human-readable reason for each positive/negative criterion. Before live ranking starts, the user sets the ICP and acceptance target; report precision-at-K on a labeled evaluation sample rather than claiming quality from a model score alone.
- Duplicate domain/email imports are deterministic; ambiguous duplicates are queued for review. Tests prove an acknowledged send is not repeated after worker/app restart. Ambiguous provider outcomes stop for reconciliation, not retry.
- No external send occurs without a fresh exact-payload approval and a connected, visible sender account. Changed draft or recipient invalidates approval.
- Security tests prove one user cannot fetch another user’s records/files; no provider password/token exists in frontend bundle, logs, sync tables, prompt or tracked files.
- Offline edits queue locally with stable client IDs and sync once. Conflicting plan/file edits are visible and are not silently overwritten.
- The PWA installs from its HTTPS site on Edge/Windows and Chrome/Android; Pixel foreground voice is tested with a text fallback. No test assumes background wake-word operation.
- Evaluate Gemini Developer API `gemini-3.5-flash-lite` as the first free-tier model candidate; use it only if the user's project/model is eligible. Eligible API calls cost $0 within quota. Model and project limits vary and must be checked in Google AI Studio. At quota exhaustion, stop/queue with an explanation; never attach billing, use paid fallback, or silently consume Google AI Pro credits. Keep Antigravity AI Credit Overages at `Never`.
- Google's published paid rate for Gemini 3.5 Flash-Lite is $0.30 per 1M input tokens and $2.50 per 1M output tokens, subject to change. Illustratively, 900 requests at 2,000 input + 500 output tokens each would be about $1.67 on paid rates, excluding other tools/context; eligible free-tier calls remain $0 until quota is reached. This estimate is not a bill forecast, and the plan does not enable paid use.
- Google AI Pro provides development benefits but is separate from Gemini Developer API keys/quotas. Its advertised $10/month Google Cloud credit may require activation/eligibility and is not a hard spending cap; do not rely on it or enable billing in the $0 baseline.
- Free-tier prompts/outputs may be used to improve Google products and human reviewers may process them. Google says not to submit sensitive, confidential, or personal information to unpaid services. Public business research is approved; private inbox content, personal voice commands/transcripts, planning memory, private files, credentials, PHI and other sensitive or personal content remain blocked from Gemini's free tier. App sync to Supabase is a separate data flow from model processing. Basic task CRUD, exact/keyword search and private inbox templates can use deterministic code without a local model. Private-data cloud AI requires a separate informed choice and compatible service terms; paid-tier use requires billing and is outside the zero-additional-spend baseline. No local LLM is required or installed.

## 8. Free-first constraints

Checked on 13 November 2026 against current official plan pages; limits can change. Supabase Free is $0 and lists 500 MB database, 50,000 monthly active users, 5 GB egress and 1 GB file storage; low activity can pause a Free project after a week. Free does not include automatic database backups, so the product must offer user-triggered export and a restore test. Cloudflare Pages Free is adequate for static PWA assets (current limits include 500 builds/month, one concurrent build and 25 MiB per file); do not add paid Workers or a paid backend. Firebase Spark is also no-cost without a payment method, and Cloud Firestore lists 1 GiB, 50K reads/day, 20K writes/deletes per day and 10 GiB/month egress; however, relational CRM/workflow state and Postgres RLS make Supabase the better fit. Firebase Cloud Functions are not available on Spark according to the current pricing table, so do not add Blaze for this $0 plan.

No local language model or local speech-model installation is a prerequisite. Gemini API supplies cloud text reasoning for eligible, approved business inputs; the PWA uses browser/device speech recognition and Edge/browser speech synthesis where available, with typing as a fallback. Browser speech privacy and availability vary by device. The Windows worker is still required for secure Hostinger credentials, bounded inbox polling, durable queued tasks and approved outbound actions; when the PC sleeps, connector work waits.

The user already has Google AI Pro. Google currently lists expanded Google Antigravity access and an included $10/month GenAI/Cloud developer credit through Google Developer Program Premium. This is useful for development in Antigravity; it is not a Gemini Developer API key, unlimited API quota or automatic runtime allowance. Confirm regional eligibility, activation and credit balance in the Developer Program account before considering use. The credit is not a hard spending cap, so it is not assumed in the $0 additional-spend baseline. Keep Antigravity's AI Credit Overages set to **Never** unless the user deliberately chooses otherwise. Gemini Developer API has separate project/model quotas and billing. Google AI Pro also does not cover Claude Code; the same prompt may be used in Antigravity, while Claude Code access is separate.

The free Gemini tier may use prompts/outputs to improve Google products and human reviewers may process them; Google's terms say not to submit sensitive, confidential or personal information. Public business research is approved. Private inbox bodies, personal voice commands/transcripts, planning memory, private files, credentials and patient/health data are blocked from the free tier. App data sync to Supabase is separate from model processing. Basic task CRUD/search and private inbox reply templates can use deterministic code, with no local LLM. Any private-data cloud AI would need separate informed consent and compatible service terms; paid service requires billing and is outside the zero-spend baseline. No paid fallback is allowed.

## 9. Delivery phases

1. **Safe shared foundation:** PWA shell, user auth, RLS, offline queue, task/events schema, private file metadata, capability/policy layer and mock connectors. No secrets or live outbound.
2. **One joint demo:** voice/text creates a plan memory and task, attaches a synthetic file, runs a fixture prospect through provenance/dedupe/qualification, drafts a first email, shows exact approval, and simulates a send. Verify persistence and no duplicates after restart.
3. **Personal live slice:** tasks, plan search/edit/delete, private file upload/download, cross-device sync and export/restore; test on the Pixel and Windows browser.
4. **Sales read-only slice:** verify Hostinger support for `harvey@zotterlabs.com`, then add read-only IMAP inbox scanning/deterministic triage and reply templates, plus dental prospecting from reviewed public sources and CRM preview. Use Gemini free tier only for approved public-business research. No send until source/ICP, domain and contact rules are configured.
5. **Approved outreach:** exact-payload approval, suppression checks, one live send to a user-controlled test contact, provider receipt, restart recovery and reconciliation behavior; then small, user-approved batches with caps.
6. **Expand safely:** additional inboxes and source adapters, campaign/pitch management, Telegram, booking/WhatsApp/payment handoffs; only after connector-specific review and no-charge path is confirmed.
7. **Later modules:** content and development tools. Do not grant them broader permissions than the user chooses.

## 10. Decisions still needed

These are setup choices, not blockers for mock work:
- Verify Hostinger's current IMAP/SMTP support for `harvey@zotterlabs.com`, the mailbox plan, secure auth method and domain DNS ownership; no credentials have been supplied or connected.
- Confirm the recommended independent/small dental-practice segment, buyer roles, disqualifiers, source allowlist, and labeled-sample precision-at-K target. US and Canada are the chosen geographies.
- Finalize the website + integrated lead-qualification offer details, proof/results/pricing (if any), and when the optional paid-performance-marketing/local-SEO add-ons should be mentioned.
- Confirm jurisdiction-specific cold-email readiness, source/consent grounds (especially CASL in Canada), truthful sender identity, physical mailing address, opt-out/suppression process, and provider deliverability requirements. 20–30 cold emails/day is a later desired cap for an unwarmed domain, not a safe initial launch volume.
- Whether plan memory stores only explicit “remember this” items or also confirmed planning conversations; retention window and export frequency.
- Which file types/size limits may sync to cloud and what should remain local-only.
- Whether the proposed bounded inbox polling cadence and PC-worker availability window are acceptable. The user reports the PC is usually awake 15–16+ hours/day; work queues while it is off.
- Whether private business-email content may ever be sent to a paid/contractually suitable Gemini service; no such consent is granted here. Until then, private email classification/reply drafts use deterministic rules/templates, while public-business research may use the eligible free API tier.
- Confirm API project eligibility, actual model quotas/rates and region-specific terms before enabling runtime calls. Do not attach billing or rely on Google AI Pro's advertised developer credit.
- Whether Telegram is needed for launch approval or the dashboard is sufficient.

## References checked
- [Supabase pricing](https://supabase.com/pricing)
- [Supabase Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Firebase pricing](https://firebase.google.com/pricing)
- [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Claude plans and pricing](https://claude.com/pricing?mode=code)
- [Web Speech API support](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)
- [Chrome progressive web apps](https://developer.chrome.com/blog/getting-started-pwa)
- [Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Google AI plans](https://one.google.com/about/google-ai-plans/)
- [Google Developer Program plans and credits](https://developers.google.com/program/plans-and-pricing)
- [Antigravity plans and overages](https://antigravity.google/docs/plans)
- [Gemini API pricing and tiers](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API Additional Terms](https://aistudio.google.com/docs/terms)
- [Gemini API data retention](https://aistudio.google.com/docs/zdr)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)

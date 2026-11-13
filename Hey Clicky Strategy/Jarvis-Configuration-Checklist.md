# Jarvis — Configuration & Secrets Checklist

**Purpose:** A safe inventory of project settings, identifiers and secrets for the zero-spend prototype. This file contains no real passwords, API keys or tokens; it includes only the mailbox address the user supplied and non-secret configuration choices. **Never send passwords, OAuth codes, API keys, recovery codes or bot tokens in chat or voice.** Enter credentials only in the provider's own OAuth/consent page or Jarvis's masked Settings form. Claude Code must never receive them.

## 1. Minimum $0 setup

| Item | Needed when | Is it secret? | Where it belongs |
|---|---|---|---|
| Supabase project URL/ref | Cloud login/sync | No | PWA build config; URL/ref are identifiers |
| Supabase publishable/anon key | PWA database client | Public key, not authorization | PWA build config only with tested RLS |
| Owner app account | Sign in across devices | Password is secret | Supabase Auth/Jarvis login UI, never this file |
| Google AI Pro plan | Antigravity development | Account entitlement | Google account; not a Gemini API key/quota |
| Gemini AI Studio project | Cloud inference | Project ID is identifier; API key is secret | Free-tier-only project; do not attach billing |
| Cloudflare Pages account/site | Publish static PWA | Account ID is an identifier | Deployment dashboard; no token in app |
| Git repository | Git-based deploy/backup | Repo URL not secret | Project/docs; deploy access via provider consent |
| Windows worker + credential store | Hostinger inbox/read/send | Mailbox/API tokens are secret | Windows Credential Manager |
| First mailbox | Hostinger `harvey@zotterlabs.com` | Address is configured in app; password secret | Secure Windows Settings; not chat |
| Dental ICP and sources | Lead qualification | Business settings | US/Canada; independent/small practice is a hypothesis |

Gemini Developer API is the planned LLM and does require an API key, even when using its eligible free tier. No local LLM/STT/TTS package is required. The free Gemini tier is $0 within model/project quotas; exact limits vary and must be checked in AI Studio. Keep billing unattached and paid fallback disabled. At quota exhaustion, queue the AI-dependent action and explain the limit; tasks, files, deterministic inbox rules and templates must still work. Browser speech recognition/Edge speech synthesis are capability-dependent and may use provider cloud services; typing is always available.

## 2. Public identifiers versus secrets

| Name / value | Required? | How to obtain | Safe storage / notes |
|---|---|---|---|
| `SUPABASE_PROJECT_REF` | Yes | Supabase project settings/dashboard | Identifier; do not confuse with a password |
| `SUPABASE_URL` | Yes | Supabase API settings | Public URL; configure exact allowed redirect URLs |
| `SUPABASE_PUBLISHABLE_KEY` (legacy `anon`) | Yes | Supabase API settings | Public only with strict RLS and Auth; expose as Vite build config |
| `SUPABASE_SERVICE_ROLE_KEY` / secret key | **No** for MVP | Supabase API settings if ever needed later | Do not create, copy or add to PWA, `.env`, prompt or sync. Service role bypasses RLS |
| `SUPABASE_DB_PASSWORD` | No at runtime | Chosen when project is created | Keep in a password manager/OS vault if admin tooling needs it; never in app/browser |
| Firebase `projectId`, `authDomain`, `appId`, `messagingSenderId`, `storageBucket`, web `apiKey` | Only if choosing Firebase instead | Firebase Console → project/web app settings | Web config identifiers, not secrets; still require Security Rules/App Check. Do not set up in parallel with Supabase |
| Firebase Admin service-account JSON/private key | Not needed | Firebase Console/IAM only for a server-side Firebase backend | Highly sensitive; do not download for the Spark MVP or place in source/Claude |

**Database choice:** Supabase is the recommended project. Firebase is an alternative only if explicitly selected. Supabase fits relational CRM, tasks, audit/outbox and Row-Level Security; Firebase Spark has useful client sync and generous Firestore quota, but it changes the data model and Firebase Cloud Functions are not in the Spark no-cost column. Do not create both backends “just in case.”

## 3. Email connector credentials

### OAuth/API providers (preferred)

| Provider type | Settings/consent required | Secret handling |
|---|---|---|
| Gmail / Google Workspace | Google Cloud project, Gmail API enabled, OAuth consent/client, exact redirect URI, requested Gmail scopes, authorized test user if app is in testing | User signs in at Google; client secret remains in the Windows connector backend/provider settings if one is required. Access/refresh token stays encrypted in Windows Credential Manager; never stored in Postgres or browser storage |
| Microsoft / Outlook | Entra app registration/client ID, supported account/tenant setting, exact redirect URI, delegated Mail permissions, PKCE/native-public-client flow if supported | User signs in at Microsoft. Avoid client secrets in the PWA. Refresh token stays in Windows Credential Manager |
| Other provider | Provider's documented API/OAuth setup and allowed scopes | Do not claim support until consent, refresh, revocation, read and send paths pass tests |

Request only the scopes needed for the specific launch features (read mail, draft/compose, send only after approval). Gmail send scopes may be sensitive and can trigger OAuth testing/verification requirements. Do not request broad mailbox delete/modify permissions by default.

### IMAP/SMTP-only provider

First mailbox target: Hostinger `harvey@zotterlabs.com`. Verify the exact mailbox plan's current secure IMAP/SMTP host, ports, TLS mode and supported auth before connection; support is not yet verified. For read-only inbox intake, use IMAP read-only/peek semantics in a masked Windows Settings form and store any supported app password in Windows Credential Manager. Never enter it in chat/voice or place it in `.env`, sync, logs or model prompts. Do not fall back to a normal account password. Test connection without sending; verify no mark-read/delete/archive/move behavior.

### Send/approval rules

The mailbox label/address is visible in the UI so the user can choose the sender. Each send requires exact account, recipient, subject and body approval; draft edits invalidate approval. Suppression/opt-out is checked again immediately before the send attempt. Record provider receipt/message ID and a stable action key. If the result is uncertain, stop for reconciliation instead of retrying. Never rotate inboxes to evade provider limits.

## 4. Optional or later settings

| Setting | When | Secret? | Free-first rule |
|---|---|---|---|
| Gemini AI Studio project ID | Cloud LLM runtime | No | Create an API project; check free-tier eligibility/quotas; no billing in $0 baseline |
| Gemini Developer API key | Required for runtime calls | Yes | Create in Google AI Studio; store only in Windows Credential Manager; never Vite/sync/logs/docs |
| Gemini model/tier | Runtime selection | No | Evaluate `gemini-3.5-flash-lite` free tier first if eligible; no paid fallback |
| Browser speech/TTS capability | Foreground voice | No key in Jarvis | Verify Edge/Chrome and Pixel behavior; disclose browser recognition processing; typing fallback |
| Google OAuth `client_id` / `client_secret` for app login | If Google sign-in is selected | ID is public; secret is server-only | Optional; set redirect allowlist and test user rules |
| Custom SMTP for Supabase Auth emails | If email verification/recovery needs reliable delivery | SMTP password is secret | Existing mail plan may be required; store only in provider/server settings, not frontend |
| Cloudflare `account_id` | CLI/CI deploy only | No | Static Pages can be connected through dashboard/Git instead |
| Cloudflare API token | Automated deployment only | Yes | Least-privilege Pages deploy token in CI secret store; never browser or repo |
| Telegram bot token and allowed chat/user ID | Optional approval channel later | Token is secret; IDs are identifiers | Dashboard approvals are enough for first slice; bot token in Windows Credential Manager |
| Gemini API billing | Not needed in $0 baseline | Billing setting | Keep unlinked/disabled; paid usage requires a separate explicit decision |
| Google AI Pro developer credits | Optional, only if explicitly chosen | Credit benefit, not a key | Plan currently advertises $10/month GenAI/Cloud credit via Developer Program Premium; check claim/eligibility and usage before relying on it; not a hard spend cap |
| Alternate model API key | Not in launch | Yes; usage may cost money | Excluded; no alternate provider or automatic paid fallback |
| Stripe secret/webhook key | Only if programmatic payment integration is approved later | Yes | No payment API needed to share a user-created payment URL; transaction fees are separate |
| Booking URL / WhatsApp business number | Optional route links | Not authentication secrets | Configure as business data; show the destination before sharing |
| Paid lead-data/enrichment provider key | Not in MVP | Yes | Omit; use user-approved public sources/CSV and honest coverage limits |
| Custom domain | Optional branding | Not secret | Registration/renewal can cost money; use provider's free hostname for $0 |
| Claude Code account/API access | Needed only to run Claude Code | Account credential is private | Authenticate through Claude's official flow; do not paste API key into Jarvis. Current Claude Code access may require paid plan or API billing |

### Google AI Pro, Antigravity and Gemini API are separate

Google AI Pro is already part of the user's setup. Google advertises expanded Antigravity/AI Studio development access and US$10/month in Google Cloud credits through Google Developer Program, subject to eligibility and activation. Google AI Pro **does not provide a Gemini Developer API key, guarantee free API quotas, or make runtime unlimited**. Claude Code access remains separate. Do not rely on the developer credit for the $0 baseline; it is not a hard spending cap. Keep Antigravity `AI Credit Overages` at `Never`.

Gemini Developer API is a separate runtime service. Current official pricing lists `gemini-3.5-flash-lite` free of charge within its eligible free-tier quota. Published paid rates are $0.30 per 1M input tokens and $2.50 per 1M output tokens. For illustration, 900 requests at 2,000 input + 500 output tokens each would be about $1.67 at those paid rates, excluding other context/tools; actual use and prices can differ. Model availability and per-project quotas are not guaranteed; check AI Studio. Keep billing unattached, API project on free tier, and paid fallback disabled.

Google's Gemini unpaid-service terms permit prompts/outputs to be used to improve products and human reviewers may process them; Google says not to submit sensitive, confidential, or personal information. Public business research is approved, limited to company-level facts. Redact contact names, email addresses, phone numbers and other person-level identifiers before sending a Gemini request; merge recipient details locally. Do not send private inbox bodies, personal voice commands/transcripts, plans/memory, private files, credentials, patient/health data or other personal/confidential content to the free API. App data sync to Supabase is separate from AI processing. Inbox scanning can still be read-only via the Windows worker, but private-mail classification/reply drafts must use deterministic rules/templates unless the user separately consents and a service tier's terms allow the content. That consent is not granted by approval of public-business research.

Paid Gemini API has separate terms and requires a billing-enabled project. Paid-tier requests are not used for product improvement under Google's current terms, but limited abuse-monitoring processing/retention may still apply. Search grounding has separate retention/cost terms. Paid AI, credit-backed calls and private-email cloud inference are outside this zero-spend plan and require a separate deliberate choice; never enable a paid fallback. Google's API terms have additional region restrictions; verify the deployment/user region before enabling API access.

## 5. Provider/project setup notes

- **Supabase:** Create one Free project; record project ref and URL. Enable Auth, Postgres and private Storage only as needed. Turn on RLS before connecting the PWA. Disable public sign-up after setting up the owner account unless later decided otherwise. Supabase Free currently lists 500 MB database, 50K MAU, 5 GB egress and 1 GB Storage; low-activity projects may pause after a week and automatic DB backups are not included. Provide manual export/restore and recheck pricing before production.
- **Cloudflare Pages:** Deploy only static PWA assets on the Free plan. Current docs list 500 builds/month, one concurrent build and 25 MiB maximum per asset. Do not add Workers/functions or a billing plan for the baseline. Use HTTPS and exact Supabase redirect/CORS origins.
- **Firebase alternative:** Spark has no payment method requirement; Firestore currently lists 1 GiB, 50K reads/day, 20K writes/deletes per day and 10 GiB/month outbound. Cloud Functions are not available under Spark's no-cost column. If Firebase is later chosen, migrate intentionally and keep its Admin key server-only.
- **Gemini API:** Create a Google AI Studio project and an API key for the eligible free tier; do not link billing. Verify model availability, rate limits, region and actual project tier in AI Studio. Store the key in Windows Credential Manager only.
- **Hostinger:** Confirm `harvey@zotterlabs.com` is a mailbox on a plan that permits secure IMAP read and SMTP send; use least privilege and test read-only behavior first. Credentials remain on the Windows worker.
- **Google OAuth:** Only needed if a later provider/app-login flow uses it; configure exact redirect URIs and minimum scopes. Do not request Gmail scopes for the Hostinger mailbox.
- **No secrets in checklists:** Use placeholders for secrets and synthetic fixtures in tests. The only real account address recorded here is the Hostinger mailbox the user explicitly supplied; never add its password/token or unrelated personal account data.

## 6. Safe local configuration template

Use the companion `jarvis.env.example` as the tracked template. Copy it to a local ignored file only for non-secret development settings. Secrets are entered through Jarvis Connections or the OS credential manager, not copied into environment variables. With Vite, any `VITE_*` value is public in the compiled JavaScript.

Suggested `.gitignore` rules in the project:

```gitignore
.env
.env.*
!.env.example
!jarvis.env.example
secrets/
*.db
*.sqlite
*.sqlite3
uploads/
```

Keep the safe `jarvis.env.example` template tracked (or use `.env.example` and its exception if you rename it). Review `git status` before every commit; do not inspect or overwrite the already-existing project `.env` during initial setup.

## 7. User decisions before real connections

- Verify Hostinger plan/auth support for `harvey@zotterlabs.com`; connection and credentials are not yet configured.
- Confirm whether independent/small dental practices are the chosen size segment, plus buyer roles, source allowlist, qualification filters and precision-at-K target. Geography (US/Canada) is set.
- Confirm website/lead-qualification product details, proof, pricing, and conditions for mentioning optional paid-performance-marketing/local-SEO add-ons.
- Verify US/Canada cold-email legal readiness, documented CASL consent grounds, truthful sender identity, physical mailing address, opt-out/suppression procedure, SPF/DKIM/DMARC and provider limits. Desired 20–30/day is a later cap, not a safe initial volume.
- Memory retention and whether planning notes are saved only on explicit request or after confirmation.
- Which file types/size limits may sync to cloud; which remain local-only.
- Approve the bounded inbox polling cadence; tasks and inbox processing queue while the Windows PC is off (user reports 15–16+ hours awake most days).
- Whether private email bodies/plans/files may ever be sent to a paid/contractually suitable Gemini service. Public-business research is approved, but private-data cloud inference is not.
- Verify Gemini model/project free-tier eligibility and live quotas before runtime is enabled; no billing or paid fallback in this plan.
- Whether Telegram is needed in the first approval slice.

These choices can be made in app settings later. None requires sending secrets to HeyClicky, ChatGPT, Antigravity or Claude.

## References checked 13 November 2026
- [Google AI plans](https://one.google.com/about/google-ai-plans/)
- [Google Developer Program plans and credits](https://developers.google.com/program/plans-and-pricing)
- [Antigravity plans and overages](https://antigravity.google/docs/plans)
- [Gemini API pricing and rate limits](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API Additional Terms](https://aistudio.google.com/docs/terms)
- [Gemini API data retention](https://aistudio.google.com/docs/zdr)
- [Supabase pricing](https://supabase.com/pricing)
- [Supabase Free project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Firebase pricing](https://firebase.google.com/pricing)
- [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Claude pricing](https://claude.com/pricing?mode=code)
- [Web Speech API support](https://developer.mozilla.org/en-US/docs/Web/API/SpeechRecognition)

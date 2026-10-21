# NutriLens

NutriLens helps Indian consumers understand packaged food through product search, barcode lookup, ingredient explanations, nutrition insights and voice narration.

A responsive food-label education web app with barcode lookup, on-device English label OCR, explainable nutrition screening, allergy keyword alerts, portion conversion, device-local saved reports, comparison, JSON export and browser speech playback.

## Run

Requires Node.js 20+; no npm install or secret keys required.

```sh
npm run dev
# http://localhost:4173
npm test
npm run build
```

`npm run build` creates a self-contained Cloudflare-compatible Worker in `dist/server/index.js`, with the seven frontend assets embedded and a same-origin read-only product API. Deploy through Sites using the retained `.openai/hosting.json` identity. This version needs Worker/server hosting; uploading only the frontend to a static host will not provide search. `server.mjs` runs the equivalent local preview and API.

## October 2026 update: search, quantity and broader assessment

- Name/brand search uses the dedicated `search.openfoodfacts.org/search` full-text API (v3 product reads do not offer text search). The unavailable legacy endpoint was replaced after a live integration check. Suggestions appear as you type with mouse and keyboard selection. Requests are debounced, spaced by 7 seconds and cached in memory; 12 results per page. Search retrieves lightweight identity fields; selecting a match loads its full v3 product record. India is the default search market, with an explicit All countries option. Search targets product names and brands, prioritises exact-name matches on each page, and discloses the common “diary milk” spelling correction. Match market, barcode and exact recipe before selecting.
- Both barcode and search results go through an explicit confirmation step: net pack quantity, g/ml unit, food type and intended portion. Simple quantities such as `0.5 kg` normalise; ambiguous multipacks require manual entry. Per-100, per-portion and whole-pack nutrition views do not change grade.
- Open Food Facts Nutri-Score is shown with its supplied algorithm version (2021 or 2023), grade, score and component points when provided. Aggregate negative minus positive points is shown only when it matches the supplied raw score. Category-specific scoring is not reimplemented. Protein exclusion, estimated inputs and preparation basis are disclosed. Missing/inapplicable scores remain unavailable; manual nutrient edits discard the old score.
- Good factors, concerns, context and unknowns cover the original traffic lights plus fibre/protein, energy/portion, carbohydrate, added sugar, trans fat, caffeine, calcium, iron, potassium, vitamin D, NOVA processing, additive tags, ingredient explanations and selected allergies. Coverage is explicitly not a confidence score. We do not claim every health factor can be known from packaging or cancel allergy warnings with a nutrition grade.
- Voice automatically prefers recognised female English voice names, favouring Indian English, then offers a persistent device-voice picker and preview. Browsers provide no standard gender metadata. Fallback is disclosed. Hosted TTS with a documented female voice and a server-side secret would be needed for consistent cross-device speech; this build has no paid TTS integration. Long explanations play in short utterances; Stop cancels the queue.
- The automated tests cover source-score arithmetic and exclusions, missing data, unit normalisation, voice selection and previous safety-sensitive rules.

References: https://www.santepubliquefrance.fr/nutri-score and https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice

## What works

- Check-digit-validated EAN-8, UPC-A, EAN-13 and GTIN-14 entry, Open Food Facts v3 product fetch, timeout/error states, per-session lookup cache, 5-second lookup spacing.
- Live camera barcode recognition where the browser implements BarcodeDetector. HTTPS/localhost and permission are required; unsupported browsers use manual entry. UPC-E is not expanded in this version.
- English OCR through pinned Tesseract.js 5.1.1, loaded on demand from jsDelivr. Photo processing stays in the browser; the engine and language files require internet. Review OCR output before analysing; nutrition values are entered manually.
- Manual entry works without APIs. Missing numbers remain unknown. Drinks/specialised foods are shown without solid-food classifications. Food category from community data must be confirmed.
- Rules-based explanations (no AI API or invented numeric health score), seven optional English allergy keyword screens, and sources shown with reports.
- Voice uses an explicitly selected SpeechSynthesis voice and its language. Availability depends on the device. No Hindi translation is claimed.
- Up to 50 saved scans and preferences in localStorage; no accounts, cloud storage or analytics. Reports may contain allergy selections, so export deliberately.
- FSSAI licence entry links to the official verification service. It does not scrape FoSCoS, verify a licence automatically, or establish a product's safety.

## Server-side search

Direct browser searches failed in integration testing. `/api/search` now queries the dedicated search service server-side; `/api/product/:code` reads full records from the v3 endpoint. Only these fixed upstream hosts and read routes are allowed. The gateway supplies an identifying User-Agent with the app URL, bounds inputs, imposes an 18-second upstream timeout, caches searches for 5 minutes and product records for 1 hour, and applies a best-effort 9 uncached requests/minute quota per isolate. Production traffic needs a shared rate limiter and registration of the app/operator with Open Food Facts. No secrets are needed for these public reads.

`worker/api.js` is server source; `scripts/build.mjs` embeds `public/` into the deployment Worker. No personal preference or allergy data is sent to the server. Search terms are sent to the app and Open Food Facts, and public product data is cached; user scan history stays in localStorage.

## Architecture

`public/analysis.js`: pure versioned nutrition/ingredient rules, normalisation, demos.
`public/app.js`: views, browser integrations and local state.
`public/styles.css`: responsive visual system.
`tests/analysis.test.mjs`: safety-sensitive rule checks and data conversion checks.

## Nutrition methodology

Four nutrients use UK/NHS solid-food thresholds per 100 g. The UI explicitly identifies their jurisdiction and avoids calling these Indian statutory ratings. Lower classifications are inclusive at the low boundary; high classifications require exceeding the high boundary. Portion scaling changes displayed quantities, not classifications. Missing, negative and nonfinite inputs are unknown. Salt = sodium in grams × 2.5.

This is a limited educational screen, not a validated overall health score, medical assessment, allergy safety guarantee, contaminant analysis or freshness test. Ingredient keyword presence alone cannot determine dose, safety or risk. Allergen keyword matching can miss terms or over-flag negated claims. A dietitian should review the rules before a public health launch. Review source changes and version rule updates.

Sources:
- https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/how-to-read-food-labels/
- https://www.food.gov.uk/safety-hygiene/check-the-label
- https://fssai.gov.in/citizen/about-license-verification?dp=Citizen+Services
- https://openfoodfacts.github.io/openfoodfacts-server/api/

Open Food Facts attribution is visible in product reports and methodology. Database: ODbL; individual contents: Database Contents License. If redistributing a derived database, review the applicable share-alike terms. Demo labels are invented. They must never be presented as real verified products.

## Public-launch plan

1. Pilot with 20–30 students/shoppers using Indian packaged foods. Check exact variants, label accuracy, task completion and whether users understand the explanation. Record failures with consent, without collecting unnecessary personal health data.
2. Have a registered dietitian/food-science reviewer validate explanations, thresholds, special-category exclusions and allergen language for your target population. Add a reviewed multilingual glossary (Hindi plus local languages), with translated voice output and screen-reader tests.
3. Harden the included backend for a production Open Food Facts integration: identify the app with its requested User-Agent and a real operator contact, complete their API usage form, cache product reads, respect rate limits, log failures without health profiles, and provide a correction channel. The included gateway identifies the app by URL, but large-scale operation still needs a real operator contact, upstream registration and shared rate-limit enforcement.
4. Improve Indian product coverage through consented, reviewed label contributions and exact barcode/variant matching. Record provenance, label date and corrections. Never invent missing nutrition values. Offer a useful manual workflow when data is absent.
5. Seek an authorised FSSAI integration or partnership if automatic business verification is required. Until then preserve the official manual route. Never convert licence status into a health badge.
6. Add a maintained barcode-library fallback for browsers without native detection, validate camera/OCR on real Android and iOS devices, add image quality guidance and cancellation, and self-host reviewed OCR assets where practical. Existing web fallback is barcode entry.
7. Host on HTTPS with a custom domain, contact/help and privacy pages. Add a PWA manifest/service worker only with clear stale-data and offline handling. Do not cache a personalised allergy report into shared CDN responses. Avoid clinical claims or paid placement in verdicts.
8. Make it available first through a QR link in campus shops and supermarkets, not a mandatory app download. Track opt-in usability feedback rather than promising weight-loss or disease-prevention outcomes. Plan accessibility, ongoing data review, security headers and dependency maintenance before broader release.

## Verification limits

Unit tests and syntax checks cover deterministic rules. A mocked browser integration test cannot establish live database availability, physical camera recognition, real photo OCR quality or audible output on every device. Test those on target phones before a public launch. Sites publication starts owner-private; sharing publicly is a separate access decision.

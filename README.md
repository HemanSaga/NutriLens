# NutriLens

A responsive food-label education web app with barcode lookup, on-device English label OCR, explainable nutrition screening, allergy keyword alerts, portion conversion, device-local saved reports, comparison, JSON export and browser speech playback.

## Run

Requires Node.js 20+; no npm install or secret keys required.

```sh
npm run dev
# http://localhost:4173
npm test
npm run build
```

`dist/` is the deployable site. Upload that directory to any HTTPS static host. There is no compilation step; `npm run build` checks JavaScript syntax. `server.mjs` is for local preview, not a production server. Sites hosting identity is retained in `.openai/hosting.json`.

## What works

- Check-digit-validated EAN-8, UPC-A, EAN-13 and GTIN-14 entry, Open Food Facts v3 product fetch, timeout/error states, per-session lookup cache, 5-second lookup spacing.
- Live camera barcode recognition where the browser implements BarcodeDetector. HTTPS/localhost and permission are required; unsupported browsers use manual entry. UPC-E is not expanded in this version.
- English OCR through pinned Tesseract.js 5.1.1, loaded on demand from jsDelivr. Photo processing stays in the browser; the engine and language files require internet. Review OCR output before analysing; nutrition values are entered manually.
- Manual entry works without APIs. Missing numbers remain unknown. Drinks/specialised foods are shown without solid-food classifications. Food category from community data must be confirmed.
- Rules-based explanations (no AI API or invented numeric health score), seven optional English allergy keyword screens, and sources shown with reports.
- Voice uses SpeechSynthesis with en-IN. Availability and actual voice depend on the device. No Hindi translation is claimed.
- Up to 50 saved scans and preferences in localStorage; no accounts, cloud storage or analytics. Reports may contain allergy selections, so export deliberately.
- FSSAI licence entry links to the official verification service. It does not scrape FoSCoS, verify a licence automatically, or establish a product's safety.

## Architecture

`dist/analysis.js`: pure versioned nutrition/ingredient rules, normalisation, demos.
`dist/app.js`: views, browser integrations and local state.
`dist/styles.css`: responsive visual system.
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
3. Add a small backend for a production Open Food Facts integration: identify the app with its requested User-Agent and a real operator contact, complete their API usage form, cache product reads, respect rate limits, log failures without health profiles, and provide a correction channel. Browsers cannot reliably set the requested User-Agent; the current direct-fetch prototype should not be treated as a completed large-scale integration.
4. Improve Indian product coverage through consented, reviewed label contributions and exact barcode/variant matching. Record provenance, label date and corrections. Never invent missing nutrition values. Offer a useful manual workflow when data is absent.
5. Seek an authorised FSSAI integration or partnership if automatic business verification is required. Until then preserve the official manual route. Never convert licence status into a health badge.
6. Add a maintained barcode-library fallback for browsers without native detection, validate camera/OCR on real Android and iOS devices, add image quality guidance and cancellation, and self-host reviewed OCR assets where practical. Existing web fallback is barcode entry.
7. Host on HTTPS with a custom domain, contact/help and privacy pages. Add a PWA manifest/service worker only with clear stale-data and offline handling. Do not cache a personalised allergy report into shared CDN responses. Avoid clinical claims or paid placement in verdicts.
8. Make it available first through a QR link in campus shops and supermarkets, not a mandatory app download. Track opt-in usability feedback rather than promising weight-loss or disease-prevention outcomes. Plan accessibility, ongoing data review, security headers and dependency maintenance before broader release.

## Verification limits

Unit tests and syntax checks cover deterministic rules. A mocked browser integration test cannot establish live database availability, physical camera recognition, real photo OCR quality or audible output on every device. Test those on target phones before a public launch. Sites publication starts owner-private; sharing publicly is a separate access decision.

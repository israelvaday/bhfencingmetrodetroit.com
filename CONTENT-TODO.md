# Content & Setup TODO — before / soon after launch

The site is fully built and SEO-ready. A few values are **intentionally left as placeholders** so we never publish
fabricated business data. Fill these in (edit `scripts/build.py`, then run `python scripts/build.py` to rebuild),
or ask and we'll do it.

## 🔴 Do before / right after launch

1. **Contact form** — posts to a Cloudflare Worker (`bh-roofing-form`,
   `https://bh-roofing-form.oren-siyonov.workers.dev`) that emails the lead to **info@bhroofingmetrodetroit.com**
   via Resend (from `leads@gothamsitestudio.com`), then redirects to `/thank-you/`.
   - Worker source: `../bh-roofing-form-worker/` (deploy with `npx wrangler deploy`; set the Resend key with
     `npx wrangler secret put RESEND_API_KEY`).
   - **To change who receives leads:** edit `TO` in `bh-roofing-form-worker/src/index.js` and redeploy.
   - Confirm `info@bhroofingmetrodetroit.com` forwards to a real inbox (Namecheap email forwarding).

2. **DNS (Namecheap → GitHub Pages)** — point `bhroofingmetrodetroit.com` at GitHub Pages:
   - Four `A` records for the apex `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
     (and/or the four `AAAA` records if you want IPv6).
   - One `CNAME` record: `www` → `gothamsitestudio.github.io.`
   - Turn OFF any Namecheap parking / URL-redirect record on `@`. Then in the repo Settings → Pages, confirm the
     custom domain and enable **Enforce HTTPS** once the certificate is issued.

3. **Google Business Profile (GBP)** — set up GBP as a **service-area business** (hide address, list the service-area
   cities). This is the #1 local-ranking lever for an address-less business. Then set `BIZ["google"]` (and
   `facebook` / `instagram`) in `build.py` so the footer, reviews page, and schema `sameAs` link to real profiles.

4. **License number** — set `BIZ["license_no"]` in `build.py` (shows in the footer). **Confirm the "Licensed &
   Insured" claim is accurate.** If the business is not yet licensed/insured, remove those trust badges
   (`TRUST_ITEMS`, `HERO_CHIPS`, sidebar lists) — do not claim it otherwise.

5. **Submit sitemap** — after DNS is live and HTTPS works, submit `https://bhroofingmetrodetroit.com/sitemap.xml`
   to **Google Search Console** and **Bing Webmaster Tools**.

## 🟡 Verify / customize

6. **Reviews** — the site does **not** publish any fabricated reviews or star ratings (per Google's guidelines).
   Once you collect real Google reviews, we can add them plus `AggregateRating` schema for star rich-results.
7. **Brands installed** — `BRANDS` list is GAF, Owens Corning, CertainTeed, IKO, Malarkey, Velux. Adjust to the
   brands/shingles you actually install.
8. **Financing** — `/financing/` is written generically ("options on approved credit"). Confirm your real lender/terms.
9. **Business hours** — set to **Sun–Thu 9am–5pm · Fri 9am–12pm · Sat closed** (top bar, footer, contact page, and
    schema `openingHoursSpecification`). The site makes **no 24/7 or after-hours claims**. Confirm the hours are right.
10. **Cost guide** — `/services/roof-replacement-cost/` uses *typical* market price ranges for education, always
    pointing to a free exact estimate. Confirm the ranges are in line with your pricing.
11. **Storm / insurance page** — `/services/storm-damage-roof-repair/` states honestly that the homeowner is
    responsible for their own deductible and never promises "free" insurance roofs. Keep it that way.
12. **Gallery** — `/gallery/` uses representative imagery. Swap in real, geo-tagged project photos when available
    (great for local SEO).

## ✅ Already done
- **Phone (313) 236-4558** wired site-wide — tap-to-call in the header, footer, mobile bar,
  every CTA, and schema `telephone`.
- Matomo analytics installed on every page (site ID **22**, `matomo.gothamsitestudio.com`).
- 37 pages: home, 10 services, services hub, 18 city pages, areas hub, about, contact, reviews, financing, gallery, FAQ.
- Full technical SEO: unique titles/descriptions, canonicals, JSON-LD (RoofingContractor + Service + FAQPage
  + BreadcrumbList, no street address, GeoCircle service radius), Open Graph + Twitter cards, sitemap.xml, robots.txt,
  clean directory URLs, self-hosted fonts, WebP images, accessibility.

## How to rebuild after edits
```
cd "bh roofing metro detroit"
python scripts/build.py        # regenerates all HTML from _copy.json + build.py
```
To regenerate images: `python scripts/generate_images.py` (needs the Gemini API key; favicons need no key).

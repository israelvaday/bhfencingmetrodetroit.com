#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Static site generator for BH Roofing Metro Detroit.
Consumes scripts/_copy.json (produced by the copywriting workflow) + metadata below,
and emits a fully SEO-optimized static site (clean directory URLs, JSON-LD, sitemap,
robots, manifest, Matomo). Run:  python scripts/build.py

Phone-safe: every "call" affordance is driven by BIZ["tel"]. If it is ever blanked out, the
site automatically falls back to a free-estimate / email CTA instead of rendering a dead link.
"""
import json, os, html, datetime, re, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = json.load(open(os.path.join(ROOT, "scripts", "_copy.json"), encoding="utf-8"))
TODAY = datetime.date.today().isoformat()

def _asset_ver():
    """Content hash of CSS/JS so browsers refetch only when they actually change."""
    h = hashlib.md5()
    for f in ("assets/css/styles.css", "assets/css/fonts.css", "assets/js/main.js"):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()[:8]
ASSET_VER = _asset_ver()

# --------------------------------------------------------------------------- #
#  BUSINESS
# --------------------------------------------------------------------------- #
BIZ = dict(
    name="BH Roofing Metro Detroit",
    short="BH Roofing",
    phone="(313) 236-4558",
    tel="+13132364558",
    telplain="3132364558",
    email="info@bhroofingmetrodetroit.com",
    domain="bhroofingmetrodetroit.com",
    base="https://bhroofingmetrodetroit.com",
    area_line="Serving Metro Detroit & suburbs within 35 miles",
    counties=["Wayne County", "Oakland County", "Macomb County"],
    hours_short="Sun–Thu 9am–5pm · Fri 9am–12pm",
    hours_full="Sun–Thu 9am–5pm · Fri 9am–12pm · Sat closed",
    lat=42.45, lng=-83.15, radius=56327,
    facebook="", instagram="", google="",   # placeholders — set real profile URLs
    license_no="",                            # placeholder — client to confirm
    matomo_site_id="22",                      # Matomo site ID (matomo.alphalockandsafe.com)
)
HAS_PHONE = bool(BIZ["tel"])

# --------------------------------------------------------------------------- #
#  INLINE SVG ICONS  (stroke uses currentColor)
# --------------------------------------------------------------------------- #
def _svg(p, fill=False, vb="0 0 24 24"):
    a = ('fill="currentColor" stroke="none"' if fill else
         'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"')
    return f'<svg viewBox="{vb}" {a} aria-hidden="true">{p}</svg>'

ICONS = {
 "phone": _svg('<path d="M6.5 3.5h3l1.5 4-2 1.5a12 12 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2 2A16.5 16.5 0 0 1 4.5 5.5a2 2 0 0 1 2-2Z"/>'),
 "arrow": _svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
 "check": _svg('<path d="M20 6 9 17l-5-5"/>'),
 "star": _svg('<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 17l-5.2 2.7 1-5.8L3.5 9.7l5.9-.9z"/>', fill=True),
 "clock": _svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
 "shield": _svg('<path d="M12 3l7 3v5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>'),
 "wrench": _svg('<path d="M14.5 6a3.8 3.8 0 0 0 4.9 4.9l-8 8a2.6 2.6 0 0 1-3.7-3.7z"/><path d="M14.5 6l-2.2-2.2M6.5 14.5 4.3 12.3"/>'),
 "roof": _svg('<path d="M2.5 12.5 12 5l9.5 7.5"/><path d="M5.5 11v8.5h13V11"/><path d="M9.5 19.5V14h5v5.5"/>'),
 "mappin": _svg('<path d="M12 21s6.5-5.6 6.5-10.5A6.5 6.5 0 0 0 5.5 10.5C5.5 15.4 12 21 12 21Z"/><circle cx="12" cy="10.5" r="2.3"/>'),
 "mail": _svg('<rect x="3.5" y="5" width="17" height="14" rx="2"/><path d="m4 6.5 8 6 8-6"/>'),
 "chevron": _svg('<path d="m6 9 6 6 6-6"/>'),
 "bolt": _svg('<path d="M13 2 4.5 13.5H11l-1 8.5L19.5 10H13z"/>', fill=True),
 "building": _svg('<rect x="5" y="3.5" width="14" height="17" rx="1"/><path d="M9 8h2M13 8h2M9 12h2M13 12h2M9 16h2M13 16h2"/>'),
 "gutter": _svg('<path d="M3 10.5h18v3.2H3z"/><path d="M17.5 13.7v6"/><path d="M6.5 10.5V7.5M10.5 10.5V6.5M14.5 10.5V7.5"/>'),
 "wind": _svg('<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h9a2.5 2.5 0 1 1-2.5 2.5"/>'),
 "panels": _svg('<rect x="4" y="3.5" width="7" height="17" rx="1"/><rect x="13" y="3.5" width="7" height="17" rx="1"/>'),
 "clipboard": _svg('<rect x="6" y="4.5" width="12" height="16" rx="2"/><path d="M9.5 4.5a2.5 2 0 0 1 5 0"/><path d="m8.6 12 1.6 1.6 3.4-3.4"/><path d="M8.5 16.5h4"/>'),
 "home": _svg('<path d="M4 11 12 4l8 7"/><path d="M6 10v10h12V10"/><path d="M10 20v-6h4v6"/>'),
 "dollar": _svg('<path d="M12 3v18"/><path d="M16 7.5a3.5 3 0 0 0-4-2.5c-2 0-3.5 1-3.5 3s1.6 2.6 3.5 3 3.8 1 3.8 3.2S14 20 12 20a3.6 3 0 0 1-4-2.5"/>'),
 "truck": _svg('<path d="M3 6.5h11v9H3zM14 9.5h4l3 3v3h-7z"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17.5" cy="17.5" r="1.8"/>'),
 "badge": _svg('<circle cx="12" cy="10" r="6.5"/><path d="M8.5 15 7 21l5-2 5 2-1.5-6"/><path d="m9.5 10 1.7 1.7 3.3-3.3"/>'),
 "users": _svg('<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><path d="M16 5.2a3.2 3.2 0 0 1 0 6.1M17 20a5.5 5.5 0 0 0-2-4.3"/>'),
 "calendar": _svg('<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 9h16M8 3v4M16 3v4"/>'),
 "spark": _svg('<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>'),
 "leaf": _svg('<path d="M5 19c0-8 6-14 14-14 0 8-6 14-14 14Z"/><path d="M5 19c3-3 6-5 9-6"/>'),
 "hand": _svg('<path d="M9 11V5.5a1.5 1.5 0 0 1 3 0V11m0-1V4.5a1.5 1.5 0 0 1 3 0V11m0-.5a1.5 1.5 0 0 1 3 0V15a6 6 0 0 1-6 6h-1a6 6 0 0 1-5.2-3L4 13.5a1.6 1.6 0 0 1 2.7-1.7L8 13.5"/><path d="M6 8V5.5a1.5 1.5 0 0 1 3 0V11"/>'),
 "facebook": _svg('<path d="M14 8.5V6.8c0-.8.4-1.3 1.4-1.3H17V2.6h-2.4c-2.4 0-3.6 1.4-3.6 3.7v2.2H9v3h2v8h3v-8h2.2l.5-3z"/>', fill=True),
 "instagram": _svg('<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17" cy="7" r="1.1" fill="currentColor" stroke="none"/>'),
 "google": _svg('<path d="M21 12.2c0-.7-.1-1.4-.2-2H12v3.8h5.1a4.4 4.4 0 0 1-1.9 2.9v2.4h3.1c1.8-1.7 2.7-4.1 2.7-7.1z"/><path d="M12 21c2.4 0 4.5-.8 6-2.2l-3.1-2.4c-.8.6-1.9 1-2.9 1a5 5 0 0 1-4.7-3.5H4.1v2.4A9 9 0 0 0 12 21z"/><path d="M7.3 13.9a5.4 5.4 0 0 1 0-3.4V8.1H4.1a9 9 0 0 0 0 8.1z"/><path d="M12 6.6c1.3 0 2.5.5 3.4 1.4l2.6-2.6A9 9 0 0 0 4.1 8.1l3.2 2.4A5 5 0 0 1 12 6.6z"/>', fill=True),
}
def ico(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<span{c}>{ICONS.get(name, ICONS["check"])}</span>' if cls else ICONS.get(name, ICONS["check"])

# --------------------------------------------------------------------------- #
#  SERVICE + CITY METADATA  (merged with copy at build time)
# --------------------------------------------------------------------------- #
SVC_META = [
 ("roof-replacement", "Roof Replacement", "roof", "svc-replacement", "Roofing"),
 ("roof-repair", "Roof Repair", "wrench", "svc-repair", "Repair"),
 ("storm-damage-roof-repair", "Storm & Hail Damage", "bolt", "svc-storm", "Repair"),
 ("roof-inspection", "Roof Inspections", "clipboard", "svc-inspection", "Roofing"),
 ("flat-commercial-roofing", "Flat & Commercial", "building", "svc-commercial", "Commercial"),
 ("metal-roofing", "Metal Roofing", "panels", "svc-metal", "Roofing"),
 ("gutter-installation", "Gutters & Guards", "gutter", "svc-gutters", "Exterior"),
 ("siding-installation", "Siding", "home", "svc-siding", "Exterior"),
 ("attic-ventilation-skylights", "Ventilation & Skylights", "wind", "svc-ventilation", "Exterior"),
 ("roof-replacement-cost", "Cost Guide", "dollar", "svc-cost", "Planning"),
]
SVC_ORDER = [s[0] for s in SVC_META]
SVC_INFO = {s[0]: dict(nav=s[1], icon=s[2], img=s[3], group=s[4]) for s in SVC_META}
GROUP_ORDER = ["Roofing", "Repair", "Commercial", "Exterior", "Planning"]

RELATED = {
 "roof-replacement": ["roof-repair","metal-roofing","roof-inspection","roof-replacement-cost"],
 "roof-repair": ["storm-damage-roof-repair","roof-inspection","attic-ventilation-skylights","roof-replacement"],
 "storm-damage-roof-repair": ["roof-repair","roof-inspection","siding-installation","roof-replacement"],
 "roof-inspection": ["roof-repair","roof-replacement","flat-commercial-roofing","roof-replacement-cost"],
 "flat-commercial-roofing": ["roof-repair","roof-replacement","roof-inspection","roof-replacement-cost"],
 "metal-roofing": ["roof-replacement","roof-replacement-cost","flat-commercial-roofing","gutter-installation"],
 "gutter-installation": ["roof-replacement","siding-installation","attic-ventilation-skylights","roof-repair"],
 "siding-installation": ["roof-replacement","gutter-installation","storm-damage-roof-repair","roof-replacement-cost"],
 "attic-ventilation-skylights": ["roof-replacement","roof-repair","gutter-installation","roof-inspection"],
 "roof-replacement-cost": ["roof-replacement","roof-repair","metal-roofing","storm-damage-roof-repair"],
}

CITY_META = {
 "warren": ("Macomb", ["sterling-heights","clinton-township","royal-oak"], ["roof-repair","roof-replacement","storm-damage-roof-repair","gutter-installation"]),
 "sterling-heights": ("Macomb", ["warren","clinton-township","shelby-township"], ["roof-replacement","roof-repair","storm-damage-roof-repair","gutter-installation"]),
 "dearborn": ("Wayne", ["livonia","southfield","canton"], ["roof-repair","roof-replacement","storm-damage-roof-repair","siding-installation"]),
 "troy": ("Oakland", ["birmingham","rochester-hills","royal-oak"], ["roof-replacement","metal-roofing","roof-inspection","siding-installation"]),
 "livonia": ("Wayne", ["canton","farmington-hills","northville"], ["roof-replacement","roof-repair","gutter-installation","attic-ventilation-skylights"]),
 "canton": ("Wayne", ["livonia","northville","farmington-hills"], ["roof-replacement","roof-repair","siding-installation","roof-replacement-cost"]),
 "farmington-hills": ("Oakland", ["novi","southfield","livonia"], ["roof-replacement","metal-roofing","siding-installation","roof-inspection"]),
 "rochester-hills": ("Oakland", ["troy","shelby-township","birmingham"], ["roof-replacement","metal-roofing","roof-inspection","siding-installation"]),
 "novi": ("Oakland", ["farmington-hills","northville","troy"], ["roof-replacement","metal-roofing","siding-installation","roof-replacement-cost"]),
 "southfield": ("Oakland", ["farmington-hills","royal-oak","ferndale"], ["roof-repair","roof-replacement","flat-commercial-roofing","storm-damage-roof-repair"]),
 "royal-oak": ("Oakland", ["ferndale","birmingham","troy"], ["roof-replacement","roof-repair","gutter-installation","attic-ventilation-skylights"]),
 "st-clair-shores": ("Macomb", ["clinton-township","warren","grosse-pointe-woods"], ["roof-repair","roof-replacement","storm-damage-roof-repair","gutter-installation"]),
 "shelby-township": ("Macomb", ["sterling-heights","rochester-hills","clinton-township"], ["roof-replacement","metal-roofing","roof-inspection","siding-installation"]),
 "clinton-township": ("Macomb", ["sterling-heights","warren","shelby-township"], ["roof-repair","roof-replacement","storm-damage-roof-repair","gutter-installation"]),
 "birmingham": ("Oakland", ["royal-oak","troy","ferndale"], ["roof-replacement","metal-roofing","roof-inspection","siding-installation"]),
 "ferndale": ("Oakland", ["royal-oak","southfield","birmingham"], ["roof-repair","roof-replacement","gutter-installation","attic-ventilation-skylights"]),
 "grosse-pointe-woods": ("Wayne", ["st-clair-shores","warren","clinton-township"], ["roof-replacement","metal-roofing","roof-inspection","siding-installation"]),
 "northville": ("Wayne", ["novi","canton","livonia"], ["roof-replacement","metal-roofing","roof-inspection","roof-replacement-cost"]),
}
CITY_ORDER = [c["slug"] for c in COPY["cities"]] if COPY.get("cities") else list(CITY_META.keys())

# lookup dicts from copy
SVC_COPY = {s["slug"]: s for s in COPY["services"]}
CITY_COPY = {c["slug"]: c for c in COPY["cities"]}
CORE = COPY["core"]

# --------------------------------------------------------------------------- #
#  SHARED COPY
# --------------------------------------------------------------------------- #
VALUE_PROPS = [
 ("clock","Fast, Reliable Scheduling","A spreading leak or storm damage can't wait. We move quickly across metro Detroit and get a crew on your roof as soon as our schedule allows — no waiting weeks in the rain."),
 ("mappin","Local Metro Detroit Roofers","We know Michigan roofs and Michigan weather — freeze-thaw, ice dams, and spring wind storms. From Wayne to Oakland to Macomb County, we're right around the corner."),
 ("roof","Every Roofing Service, One Team","Replacement, repair, storm restoration, flat and commercial, metal, gutters, and siding — residential and commercial, all handled by one local crew."),
 ("hand","Honest, Upfront Pricing","Clear written quotes and free, no-obligation estimates. We'll tell you honestly whether you need a repair or a replacement — no scare tactics, no pressure, ever."),
 ("shield","Licensed, Insured & Guaranteed","A licensed and insured local crew that protects your property, sweeps up every stray nail, and stands behind the work with a workmanship guarantee."),
 ("spark","Curb Appeal & Home Value","A new roof doesn't just keep you dry — it transforms your home's look, energy efficiency, and resale value for years to come."),
]
PROCESS = [
 ("Request Your Free Estimate","Tell us what's going on — a leak, missing shingles, storm damage, or a roof that's just getting old. We'll answer your questions and schedule a visit that works for you."),
 ("Free Roof Inspection & Quote","We inspect the shingles, flashing, valleys, and ventilation, then give you a clear written quote in plain English — with honest repair-versus-replace advice. No obligation."),
 ("Expert Installation or Repair","We protect your landscaping and siding, then install or repair to code with quality materials and skilled crews who treat your home like their own."),
 ("Cleanup & Workmanship Guarantee","We haul away every scrap, run a magnetic sweep for stray nails, and back our work with a guarantee. Your roof is buttoned up tight against Michigan weather."),
]
TRUST_ITEMS = [
 ("shield","Licensed & Insured"),
 ("clock","Fast, Reliable Scheduling"),
 ("dollar","Free, No-Obligation Estimates"),
 ("badge","Workmanship Guarantee"),
 ("mappin","Local Metro Detroit Team"),
 ("hand","Financing Available"),
]
HERO_CHIPS = [("shield","Licensed & Insured"),("dollar","Free Estimates"),("badge","Workmanship Guarantee"),("bolt","Storm Damage Specialists")]
BRANDS = ["GAF","Owens Corning","CertainTeed","IKO","Malarkey","Velux"]

# --------------------------------------------------------------------------- #
#  HELPERS
# --------------------------------------------------------------------------- #
def esc(s): return html.escape(str(s), quote=True)
def U(path): return path if path.startswith("http") else BIZ["base"] + path

def svc_url(slug): return f"/services/{slug}/"
def city_url(slug): return f"/service-areas/{slug}/"
def city_name(slug): return CITY_COPY[slug]["city"]

# --------------------------------------------------------------------------- #
#  CONTEXTUAL INTERNAL LINKING
#  Auto-links the first mention of a topic in body prose to its money page.
#  Ordered most-specific-first so "roof replacement cost" wins over "roof replacement".
# --------------------------------------------------------------------------- #
LINK_PHRASES = [
 (r"roof replacement costs?|cost of a new roof|roofing costs?", "/services/roof-replacement-cost/"),
 (r"storm damage|hail damage|wind damage", "/services/storm-damage-roof-repair/"),
 (r"roof inspections?", "/services/roof-inspection/"),
 (r"standing[- ]seam|metal roofing|metal roofs?", "/services/metal-roofing/"),
 (r"commercial roofing|flat roofs?|low[- ]slope roofs?", "/services/flat-commercial-roofing/"),
 (r"gutter guards?|seamless gutters|gutters", "/services/gutter-installation/"),
 (r"attic ventilation|ice dams?|skylights?", "/services/attic-ventilation-skylights/"),
 (r"roof replacements?|re-roofing|re-roofs?|tear-offs?", "/services/roof-replacement/"),
 (r"roof leaks?|roof repairs?", "/services/roof-repair/"),
 (r"siding", "/services/siding-installation/"),
 (r"financing", "/financing/"),
]

class Linker:
    """Per-page contextual linker: at most one link per target, capped per page,
    never links a page to itself, and never matches inside markup it just inserted."""
    def __init__(self, current_url, budget=5):
        self.cur = current_url; self.budget = budget; self.used = set()

    def __call__(self, t):
        if self.budget <= 0:
            return t
        cands = []
        for pattern, url in LINK_PHRASES:
            if url == self.cur or url in self.used:
                continue
            m = re.search(r"\b(" + pattern + r")\b", t, re.I)
            if m:
                cands.append((m.start(1), m.end(1), url))
        cands.sort()
        picked, last = [], -1
        for s, e, u in cands:
            if s >= last and u not in self.used:
                picked.append((s, e, u)); self.used.add(u); last = e
                if len(picked) >= self.budget:
                    break
        self.budget -= len(picked)
        for s, e, u in reversed(picked):          # splice from the end so spans stay valid
            t = t[:s] + f'<a href="{u}">' + t[s:e] + "</a>" + t[e:]
        return t

def paras(lst, linker=None):
    return "".join(f"<p>{esc_inline(p, linker)}</p>" for p in lst)
def esc_inline(s, linker=None):
    t = esc(s)
    return linker(t) if linker else t

TOP_CITIES = ["warren","sterling-heights","troy","livonia","royal-oak","dearborn","canton","novi"]

def hero_secondary(size="btn-lg"):
    """Secondary hero CTA: tap-to-call when a phone is live, else an email fallback."""
    if HAS_PHONE:
        return f'<a class="btn btn-ghost {size}" href="tel:{BIZ["tel"]}">{ICONS["phone"]} {esc(BIZ["phone"])}</a>'
    return f'<a class="btn btn-ghost {size}" href="mailto:{BIZ["email"]}">{ICONS["mail"]} Email Us</a>'

# --------------------------------------------------------------------------- #
#  MATOMO  (exact snippet supplied by client — site ID 22)
# --------------------------------------------------------------------------- #
MATOMO = """<!-- Matomo -->
<script>
  var _paq = window._paq = window._paq || [];
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(["setDocumentTitle", document.domain + "/" + document.title]);
  _paq.push(["setCookieDomain", "*.bhroofingmetrodetroit.com"]);
  _paq.push(["setDomains", ["*.bhroofingmetrodetroit.com"]]);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="https://matomo.alphalockandsafe.com/matomo/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', '22']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
</script>
<noscript><p><img referrerpolicy="no-referrer-when-downgrade" src="https://matomo.alphalockandsafe.com/matomo/matomo.php?idsite=22&amp;rec=1" style="border:0;" alt="" /></p></noscript>
<!-- End Matomo Code -->"""

# --------------------------------------------------------------------------- #
#  JSON-LD
# --------------------------------------------------------------------------- #
def business_node():
    area = [{"@type":"City","name":city_name(s)+", MI"} for s in CITY_ORDER]
    area += [{"@type":"AdministrativeArea","name":c} for c in BIZ["counties"]]
    area += [{"@type":"AdministrativeArea","name":"Metropolitan Detroit"}]
    node = {
        "@type": ["RoofingContractor","HomeAndConstructionBusiness","GeneralContractor","LocalBusiness"],
        "@id": BIZ["base"] + "/#business",
        "name": BIZ["name"],
        "alternateName": BIZ["short"],
        "url": BIZ["base"] + "/",
        "email": BIZ["email"],
        "image": U("/assets/img/hero-home.jpg"),
        "logo": U("/assets/img/icon-512.png"),
        "description": "Residential and commercial roofing serving metro Detroit and suburbs within 35 miles — roof replacement, roof repair, storm and hail damage restoration, inspections, flat and commercial roofing, metal roofing, gutters, and siding.",
        "priceRange": "$$",
        "areaServed": area,
        "address": {"@type":"PostalAddress","addressLocality":"Detroit","addressRegion":"MI","addressCountry":"US"},
        "serviceArea": {"@type":"GeoCircle",
            "geoMidpoint":{"@type":"GeoCoordinates","latitude":BIZ["lat"],"longitude":BIZ["lng"]},
            "geoRadius": BIZ["radius"]},
        "openingHoursSpecification": [
            {"@type":"OpeningHoursSpecification","dayOfWeek":["Sunday","Monday","Tuesday","Wednesday","Thursday"],"opens":"09:00","closes":"17:00"},
            {"@type":"OpeningHoursSpecification","dayOfWeek":["Friday"],"opens":"09:00","closes":"12:00"}],
        "knowsAbout":["Roof replacement","Roof repair","Storm and hail damage","Roof inspection","Flat and commercial roofing","Metal roofing","Gutter installation","Siding","Attic ventilation","Ice dam prevention"],
    }
    if BIZ["tel"]:
        node["telephone"] = BIZ["tel"]
    same = [x for x in [BIZ["facebook"],BIZ["instagram"],BIZ["google"]] if x]
    if same: node["sameAs"] = same
    return node

def website_node():
    return {"@type":"WebSite","@id":BIZ["base"]+"/#website","url":BIZ["base"]+"/",
            "name":BIZ["name"],"publisher":{"@id":BIZ["base"]+"/#business"}}

def breadcrumb_node(items):
    return {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":U(u)} for i,(n,u) in enumerate(items)]}

def faq_node(faqs):
    return {"@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}

def service_node(name, slug, desc, areas=None, url_path=None, service_type=None):
    node = {"@type":"Service","name":name,"serviceType":service_type or name,
            "provider":{"@id":BIZ["base"]+"/#business"},
            "url":U(url_path or svc_url(slug)),"description":desc,
            "areaServed":[{"@type":"City","name":city_name(s)+", MI"} for s in (areas or TOP_CITIES)]}
    return node

# Clean schema.org service categories per page (no SEO-title/"near me" stuffing in structured data)
SERVICE_TYPE = {
 "roof-replacement": "Roof Replacement",
 "roof-repair": "Roof Repair",
 "storm-damage-roof-repair": "Storm and Hail Damage Roof Repair",
 "roof-inspection": "Roof Inspection",
 "flat-commercial-roofing": "Commercial and Flat Roofing",
 "metal-roofing": "Metal Roof Installation",
 "gutter-installation": "Gutter Installation and Repair",
 "siding-installation": "Siding Installation and Repair",
 "attic-ventilation-skylights": "Attic Ventilation and Skylight Installation",
 "roof-replacement-cost": "Roofing Cost Estimation",
}

def srcset(name, maxw):
    """Responsive srcset for /assets/img/{name}.webp with -480/-800/-1200 variants."""
    ws = [w for w in (480, 800, 1200) if w < maxw]
    parts = [f"/assets/img/{name}-{w}.webp {w}w" for w in ws]
    parts.append(f"/assets/img/{name}.webp {maxw}w")
    return ", ".join(parts)

SIZES_HERO = "(max-width: 900px) 100vw, 50vw"
SIZES_CARD = "(max-width: 700px) 100vw, (max-width: 1080px) 50vw, 33vw"

def jsonld(graph):
    return ('<script type="application/ld+json">' +
            json.dumps({"@context":"https://schema.org","@graph":graph}, ensure_ascii=False, separators=(",",":")) +
            "</script>")

# --------------------------------------------------------------------------- #
#  LAYOUT COMPONENTS
# --------------------------------------------------------------------------- #
def header(active=""):
    def dd_service(slug):
        i = SVC_INFO[slug]; c = SVC_COPY[slug]
        return (f'<a class="dd-item" href="{svc_url(slug)}"><span class="di-ic">{ICONS[i["icon"]]}</span>'
                f'<span><b>{esc(i["nav"])}</b><span>{esc(c["hero_tagline"][:64])}</span></span></a>')
    svc_items = "".join(dd_service(s) for s in SVC_ORDER)
    city_items = "".join(
        f'<a class="dd-item" href="{city_url(s)}"><span class="di-ic">{ICONS["mappin"]}</span>'
        f'<span><b>{esc(city_name(s))}</b><span>{esc(CITY_META[s][0])} County</span></span></a>'
        for s in CITY_ORDER)
    nav_call = ""
    if HAS_PHONE:
        nav_call = (f'<a class="nav-call" href="tel:{BIZ["tel"]}"><span class="ring">{ICONS["phone"]}</span>'
                    f'<span><small>Call for a free estimate</small><span class="ph">{esc(BIZ["phone"])}</span></span></a>')
    return f'''<div class="topbar"><div class="container">
    <div class="topbar-left">
      <span class="ico">{ICONS["mappin"]} {esc(BIZ["area_line"])}</span>
      <span class="ico">{ICONS["clock"]} {esc(BIZ["hours_short"])}</span>
    </div>
    <div class="topbar-right">
      <span class="badge-24"><span class="dot ok"></span>Free Estimates · Licensed &amp; Insured</span>
      <a href="mailto:{BIZ["email"]}">{ICONS["mail"]} {esc(BIZ["email"])}</a>
    </div></div></div>
  <header class="site-header" id="siteHeader">
    <div class="container"><nav class="nav" aria-label="Primary">
      <a class="brand" href="/" aria-label="{esc(BIZ["name"])} home">
        <img src="/assets/img/logo-mark.svg" width="48" height="48" alt="{esc(BIZ["short"])} logo">
        <span class="wm"><span class="name">BH Roofing</span><span class="tag">Metro Detroit</span></span>
      </a>
      <ul class="nav-menu">
        <li><a href="/"{' aria-current="page"' if active=="home" else ''}>Home</a></li>
        <li class="has-dd"><button aria-expanded="false" aria-haspopup="true" aria-controls="dd-services">Services <span class="caret">{ICONS["chevron"]}</span></button>
          <div class="dropdown" id="dd-services"><div class="dd-grid three">{svc_items}</div>
            <div class="dd-foot"><span>Residential &amp; commercial roofing — repair, replacement &amp; restoration.</span>
            <a class="sc-link" href="/services/">All services {ICONS["arrow"]}</a></div></div></li>
        <li class="has-dd"><button aria-expanded="false" aria-haspopup="true" aria-controls="dd-areas">Service Areas <span class="caret">{ICONS["chevron"]}</span></button>
          <div class="dropdown areas" id="dd-areas"><div class="dd-grid three">{city_items}</div>
            <div class="dd-foot"><span>18+ metro Detroit cities across 3 counties.</span>
            <a class="sc-link" href="/service-areas/">All areas {ICONS["arrow"]}</a></div></div></li>
        <li><a href="/services/roof-replacement-cost/"{' aria-current="page"' if active=="cost" else ''}>Pricing</a></li>
        <li><a href="/about/"{' aria-current="page"' if active=="about" else ''}>About</a></li>
        <li><a href="/reviews/"{' aria-current="page"' if active=="reviews" else ''}>Reviews</a></li>
        <li><a href="/contact/"{' aria-current="page"' if active=="contact" else ''}>Contact</a></li>
      </ul>
      <div class="nav-actions">
        {nav_call}
        <a class="btn btn-primary" href="/contact/">Free Estimate</a>
        <button class="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false"><span></span><span></span><span></span></button>
      </div>
    </nav></div>
  </header>'''

def mobile_cta():
    if HAS_PHONE:
        first = f'<a class="btn btn-navy" href="tel:{BIZ["tel"]}">{ICONS["phone"]} Call Now</a>'
    else:
        first = f'<a class="btn btn-navy" href="mailto:{BIZ["email"]}">{ICONS["mail"]} Email Us</a>'
    return (f'<div class="mobile-cta">{first}'
            f'<a class="btn btn-primary" href="/contact/">Free Estimate</a></div>')

def footer():
    svc_links = "".join(f'<li><a href="{svc_url(s)}">{esc(SVC_INFO[s]["nav"])}</a></li>' for s in SVC_ORDER)
    city_links = "".join(f'<li><a href="{city_url(s)}">{esc(city_name(s))}</a></li>' for s in CITY_ORDER)
    social = ""
    for key,url in [("google",BIZ["google"]),("facebook",BIZ["facebook"]),("instagram",BIZ["instagram"])]:
        if not url:
            continue  # never render dead "#" links — add real profile URLs in BIZ when live
        social += f'<a href="{url}" aria-label="{key.title()}" target="_blank" rel="noopener">{ICONS[key]}</a>'
    social_html = f'<div class="social">{social}</div>' if social else ''
    lic = f' · License #{esc(BIZ["license_no"])}' if BIZ["license_no"] else ""
    phone_li = (f'<li>{ICONS["phone"]}<span><a href="tel:{BIZ["tel"]}">{esc(BIZ["phone"])}</a><br><small>Free estimates · fast scheduling</small></span></li>'
                if HAS_PHONE else "")
    return f'''<footer class="site-footer">
    <div class="container"><div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="/"><img src="/assets/img/logo-mark.svg" width="46" height="46" alt="">
          <span class="wm"><span class="name">BH Roofing</span><span class="tag">Metro Detroit</span></span></a>
        <p>Residential &amp; commercial roofing across metro Detroit — roof replacement, repair, storm &amp; hail damage restoration, inspections, flat &amp; commercial, metal roofing, gutters &amp; siding. Licensed &amp; insured, honest pricing, free estimates.</p>
        {social_html}
      </div>
      <div class="footer-col"><h4>Services</h4><ul>{svc_links}
        <li><a href="/services/">All services →</a></li></ul></div>
      <div class="footer-col"><h4>Service Areas</h4><ul>{city_links}
        <li><a href="/service-areas/">All areas →</a></li></ul></div>
      <div class="footer-col"><h4>Get in Touch</h4>
        <ul class="footer-contact">
          {phone_li}
          <li>{ICONS["mail"]}<a href="mailto:{BIZ["email"]}">{esc(BIZ["email"])}</a></li>
          <li>{ICONS["mappin"]}<span>{esc(BIZ["area_line"])}</span></li>
          <li>{ICONS["clock"]}<span>{esc(BIZ["hours_full"])}</span></li>
        </ul>
        <a class="btn btn-primary btn-block" href="/contact/">Request Free Estimate</a>
      </div>
    </div></div>
    <div class="footer-bottom"><div class="container">
      <span>© {datetime.date.today().year} {esc(BIZ["name"])}. All rights reserved.{lic} · Built, designed &amp; promoted by <a href="https://www.gothamsitestudio.com/" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline;">Gotham Site Studio</a></span>
      <span><a href="/service-areas/">Service Areas</a> · <a href="/services/">Services</a> · <a href="/about/">About</a> · <a href="/reviews/">Reviews</a> · <a href="/faq/">FAQ</a> · <a href="/gallery/">Gallery</a> · <a href="/financing/">Financing</a> · <a href="/contact/">Contact</a> · <a href="/privacy-policy/">Privacy Policy</a> · <a href="/sitemap.xml">Sitemap</a></span>
    </div></div>
  </footer>'''

def breadcrumb(items):
    lis = ""
    for i,(n,u) in enumerate(items):
        last = i == len(items)-1
        if last: lis += f'<li><span aria-current="page">{esc(n)}</span></li>'
        else: lis += f'<li><a href="{u}">{esc(n)}</a></li>'
    return f'<nav class="breadcrumb" aria-label="Breadcrumb"><div class="container"><ol>{lis}</ol></div></nav>'

def cta_band(title="Ready for a roof you don't have to think about?", text="Get a free, no-obligation estimate today. Fast, reliable scheduling across metro Detroit whenever our schedule allows."):
    if HAS_PHONE:
        actions = (f'<a class="btn btn-primary btn-lg" href="tel:{BIZ["tel"]}">{ICONS["phone"]} {esc(BIZ["phone"])}</a>'
                   f'<a class="btn btn-white btn-lg" href="/contact/">Free Estimate</a>')
    else:
        actions = (f'<a class="btn btn-primary btn-lg" href="/contact/">{ICONS["calendar"]} Get My Free Estimate</a>'
                   f'<a class="btn btn-white btn-lg" href="mailto:{BIZ["email"]}">{ICONS["mail"]} Email Us</a>')
    return f'''<section class="section"><div class="container"><div class="cta-band"><div class="inner">
      <div><h2>{esc(title)}</h2><p>{esc(text)}</p></div>
      <div class="cta-actions">
        {actions}
      </div></div></div></div></section>'''

def faq_section(faqs, heading="Frequently Asked Questions", sub=None, more_link=None):
    items = ""
    for q,a in faqs:
        items += f'<details><summary>{esc(q)}</summary><div class="faq-a"><p>{esc(a)}</p></div></details>'
    subhtml = f'<p>{esc(sub)}</p>' if sub else ''
    more = (f'<p class="text-center mt-2"><a class="btn btn-ghost" href="{more_link}">See all roofing FAQs {ICONS["arrow"]}</a></p>'
            if more_link else '')
    return f'''<section class="section bg-cloud"><div class="container">
      <div class="section-head center"><span class="eyebrow">Answers</span><h2>{esc(heading)}</h2>{subhtml}</div>
      <div class="faq">{items}</div>{more}</div></section>'''

def trust_strip():
    items = ""
    for i,t in TRUST_ITEMS:
        if t == "Financing Available":
            items += f'<a class="trust-item" href="/financing/">{ICONS[i]} {esc(t)}</a>'
        else:
            items += f'<div class="trust-item">{ICONS[i]} {esc(t)}</div>'
    return f'<div class="truststrip"><div class="container">{items}</div></div>'

def brands_block():
    b = "".join(f'<span>{esc(x)}</span>' for x in BRANDS)
    return f'''<section class="section-sm"><div class="container">
      <p class="text-center" style="color:var(--steel);font-weight:600;margin-bottom:18px">Trusted roofing &amp; exterior brands we install</p>
      <div class="brands">{b}</div></div></section>'''

def resource_row(exclude=None, label="Helpful next steps"):
    """Contextual links to the support pages that would otherwise only be reachable
    from the nav/footer (about, gallery, reviews, faq, financing, cost guide)."""
    items = [
        ("/services/", "All roofing services"),
        ("/services/roof-replacement-cost/", "Roofing cost guide"),
        ("/service-areas/", "Areas we serve"),
        ("/gallery/", "See our work"),
        ("/reviews/", "Reviews &amp; our promise"),
        ("/faq/", "Roofing FAQs"),
        ("/financing/", "Financing options"),
        ("/about/", "About BH Roofing"),
    ]
    links = " · ".join(f'<a href="{u}">{t}</a>' for u, t in items if u != exclude)
    return (f'<p class="text-center" style="margin-top:1.4em;font-size:.95rem;color:var(--steel)">'
            f'<strong>{label}:</strong> {links}</p>')

def value_props_block(intro=None):
    cards = ""
    for i,t,d in VALUE_PROPS:
        img = (f'<div class="why-img"><img src="/assets/img/why-{i}.webp" '
               f'srcset="/assets/img/why-{i}-400.webp 400w, /assets/img/why-{i}.webp 800w" '
               f'sizes="(max-width: 700px) 100vw, 33vw" width="800" height="600" loading="lazy" alt=""></div>')
        cards += f'<div class="why-card">{img}<h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
    sub = f'<p>{esc(intro)}</p>' if intro else ''
    return f'''<section class="section bg-navy"><div class="container">
      <div class="section-head center"><span class="eyebrow">Why BH Roofing</span>
        <h2>Metro Detroit homeowners &amp; businesses trust us</h2>{sub}</div>
      <div class="grid grid-3">{cards}</div></div></section>'''

def process_block():
    steps = ""
    for t,d in PROCESS:
        steps += f'<div class="step"><h3>{esc(t)}</h3><p>{esc(d)}</p></div>'
    return f'''<section class="section"><div class="container">
      <div class="section-head center"><span class="eyebrow">How it works</span>
        <h2>Simple, honest, and done right the first time</h2>
        <p>From your first call to the final cleanup, we keep it clear and easy.</p></div>
      <div class="grid grid-4 steps">{steps}</div></div></section>'''

def reviews_invite(on_reviews_page=False):
    """Honest review section — invites Google reviews instead of fabricating testimonials."""
    if BIZ["google"]:
        btns = (f'<a class="btn btn-primary" href="{BIZ["google"]}" target="_blank" rel="noopener">{ICONS["google"]} Read Google Reviews</a>'
                f'<a class="btn btn-ghost" href="/reviews/">More about our promise {ICONS["arrow"]}</a>')
    elif on_reviews_page:
        btns = (f'<a class="btn btn-primary" href="/contact/">{ICONS["calendar"]} Get a free estimate</a>'
                f'<a class="btn btn-ghost" href="/gallery/">See our work {ICONS["arrow"]}</a>')
    else:
        btns = (f'<a class="btn btn-primary" href="/reviews/">{ICONS["badge"]} Our promise to every customer</a>'
                f'<a class="btn btn-ghost" href="/gallery/">See our work {ICONS["arrow"]}</a>')
    return f'''<section class="section"><div class="container">
      <div class="split">
        <div><span class="eyebrow">Reviews</span>
          <h2>Building a reputation, one roof at a time</h2>
          <p class="lead">We'd rather earn your trust than borrow someone else's words. Every job is done to the standard we'd want on our own home — clean, on time, and guaranteed.</p>
          <p>Worked with us? We'd love your feedback. Checking us out? See exactly what you can expect from our crew.</p>
          <div class="hero-cta">
            {btns}
          </div>
        </div>
        <div class="grid" style="gap:16px">
          <div class="feature"><div class="f-ic">{ICONS["badge"]}</div><h3>Workmanship guarantee</h3><p>We stand behind every roof we install and repair. If it isn't right, we make it right.</p></div>
          <div class="feature"><div class="f-ic">{ICONS["clock"]}</div><h3>On-time, tidy service</h3><p>We show up when we say, protect your property, and sweep every stray nail before we go.</p></div>
        </div>
      </div></div></section>'''

# --------------------------------------------------------------------------- #
#  PAGE SHELL
# --------------------------------------------------------------------------- #
def render(path, title, description, body, graph, active="", og_image="/assets/img/og-image.jpg", extra_head="", noindex=False):
    canonical = U(path)
    g = [business_node()] + graph
    robots_meta = "noindex,follow" if noindex else "index,follow,max-image-preview:large"
    canonical_tag = "" if noindex else f'<link rel="canonical" href="{canonical}">\n'
    og_url_tag = "" if noindex else f'<meta property="og:url" content="{canonical}">\n'
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{canonical_tag}<meta name="robots" content="{robots_meta}">
<meta name="theme-color" content="#0d2035">
<meta name="format-detection" content="telephone=yes">
<meta name="geo.region" content="US-MI"><meta name="geo.placename" content="Detroit, Michigan">
<link rel="preload" href="/assets/fonts/manrope-800.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/styles.css?v={ASSET_VER}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/assets/img/logo-mark.svg">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(BIZ["name"])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
{og_url_tag}<meta property="og:image" content="{U(og_image)}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{U(og_image)}">
{extra_head}
{jsonld(g)}
</head>
<body>
<a href="#main" class="skip-link btn btn-primary">Skip to main content</a>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
{mobile_cta()}
<script src="/assets/js/main.js?v={ASSET_VER}" defer></script>
{MATOMO}
</body>
</html>'''
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)
    return path

# --------------------------------------------------------------------------- #
#  PAGES
# --------------------------------------------------------------------------- #
def build_home():
    h = CORE["home"]
    h1 = esc(h["hero_h1"])
    hl = h.get("hero_hl","")
    if hl and hl in h["hero_h1"]:
        h1 = esc(h["hero_h1"]).replace(esc(hl), f'<span class="hl">{esc(hl)}</span>')
    chips = "".join(f'<span class="ht">{ICONS[i]} {esc(t)}</span>' for i,t in HERO_CHIPS)
    cards = ""
    for s in SVC_ORDER:
        i = SVC_INFO[s]; c = SVC_COPY[s]
        cards += f'''<a class="card svc-card" href="{svc_url(s)}">
          <div class="sc-media"><img src="/assets/img/{i["img"]}.webp" srcset="{srcset(i["img"],1200)}" sizes="{SIZES_CARD}" width="1200" height="800" loading="lazy" alt="{esc(c["h1"])}"><span class="sc-tag">{esc(i["group"])}</span></div>
          <div class="sc-body"><h3>{esc(i["nav"])}</h3><p>{esc(c["hero_tagline"])}</p>
          <span class="sc-link">Learn more {ICONS["arrow"]}</span></div></a>'''
    chips_city = "".join(
        f'<a class="city-chip" href="{city_url(s)}">{esc(city_name(s))} {ICONS["arrow"]}<span>{CITY_META[s][0]} Co.</span></a>'
        for s in CITY_ORDER)
    lk = Linker("/", budget=6)
    intro_body = paras(h["intro_body"], lk)
    faqs = [(f["q"],f["a"]) for f in h["faqs"]]
    graph = [website_node(), breadcrumb_node([("Home","/")]), faq_node(faqs),
             service_node("Roof Replacement and Repair","roof-repair",h["meta_description"],url_path="/")]
    body = f'''<section class="hero"><div class="container"><div class="hero-grid">
      <div class="hero-copy">
        <span class="eyebrow">Roofing · Metro Detroit</span>
        <h1>{h1}</h1>
        <p class="lead">{esc(h["hero_sub"])}</p>
        <div class="hero-cta">
          <a class="btn btn-primary btn-lg" href="/contact/">{ICONS["calendar"]} Get My Free Estimate</a>
          {hero_secondary("btn-lg")}
        </div>
        <div class="hero-trust">{chips}</div>
      </div>
      <div class="hero-media">
        <img src="/assets/img/hero-home.webp" srcset="{srcset("hero-home",1600)}" sizes="{SIZES_HERO}" width="1600" height="1000" fetchpriority="high" alt="Newly installed asphalt shingle roof on a metro Detroit home">
        <div class="hero-badge"><span class="hb-ic">{ICONS["shield"]}</span><span><b>Licensed &amp; Insured</b><span>free estimates across metro Detroit</span></span></div>
      </div>
    </div></div></section>
    {trust_strip()}
    <section class="section"><div class="container">
      <div class="split">
        <div><span class="eyebrow">Metro Detroit's roofing specialists</span>
          <h2>{esc(h["intro_h2"])}</h2>{intro_body}
          <div class="hero-cta"><a class="btn btn-navy" href="/services/">Explore our services {ICONS["arrow"]}</a>
          <a class="btn btn-ghost" href="/service-areas/">Areas we serve</a></div>
        </div>
        <div class="page-hero-media"><img src="/assets/img/process-install.webp" srcset="{srcset("process-install",1200)}" sizes="{SIZES_HERO}" width="1200" height="800" loading="lazy" alt="BH Roofing crew installing a new shingle roof in metro Detroit" style="border-radius:var(--r-xl);box-shadow:var(--sh-3)"></div>
      </div></div></section>
    <section class="section bg-cloud"><div class="container">
      <div class="section-head center"><span class="eyebrow">Our Services</span>
        <h2>Every roof, one trusted local team</h2><p>{esc(h["services_intro"])}</p></div>
      <div class="grid grid-3">{cards}</div>
    </div></section>
    {value_props_block(h.get("why_intro"))}
    {process_block()}
    <section class="section bg-cloud"><div class="container">
      <div class="section-head center"><span class="eyebrow">Service Areas</span>
        <h2>Proudly serving metro Detroit &amp; 18+ suburbs</h2><p>{esc(h["areas_intro"])}</p></div>
      <div class="city-grid">{chips_city}</div>
      <p class="text-center mt-2"><a class="btn btn-navy" href="/service-areas/">See all service areas {ICONS["arrow"]}</a></p>
      {resource_row(exclude="/", label="Explore")}
    </div></section>
    {reviews_invite()}
    {brands_block()}
    {faq_section(faqs, "Roofing FAQs", "Quick answers for metro Detroit homeowners and businesses.", more_link="/faq/")}
    {cta_band()}'''
    render("/", h["meta_title"], h["meta_description"], body, graph, active="home")

def build_services_hub():
    groups = {}
    for s in SVC_ORDER:
        groups.setdefault(SVC_INFO[s]["group"], []).append(s)
    sections = ""
    for grp in GROUP_ORDER:
        cards = ""
        for s in groups.get(grp,[]):
            i=SVC_INFO[s]; c=SVC_COPY[s]
            cards += f'''<a class="card svc-card" href="{svc_url(s)}">
              <div class="sc-media"><img src="/assets/img/{i["img"]}.webp" srcset="{srcset(i["img"],1200)}" sizes="{SIZES_CARD}" width="1200" height="800" loading="lazy" alt="{esc(c["h1"])}"><span class="sc-tag">{esc(grp)}</span></div>
              <div class="sc-body"><h3>{esc(c["h1"])}</h3><p>{esc(c["hero_tagline"])}</p><span class="sc-link">View service {ICONS["arrow"]}</span></div></a>'''
        sections += f'<div class="section-head" style="margin-top:12px"><h2>{esc(grp)}</h2></div><div class="grid grid-3">{cards}</div>'
    graph = [breadcrumb_node([("Home","/"),("Services","/services/")]),
             service_node("Roofing Services","roof-repair","Full-service residential and commercial roofing across metro Detroit.",
                           url_path="/services/",service_type="Roofing")]
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">Our Services</span><h1>Roofing Services in Metro Detroit</h1>
      <p>From a full tear-off and replacement to a stubborn leak, storm damage, or aging flat roof, BH Roofing installs and repairs every kind of residential and commercial roof across Wayne, Oakland, and Macomb counties — with honest advice and fast, reliable scheduling.</p>
      <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/contact/">Get a Free Estimate</a>
      {hero_secondary("btn-lg")}</div></div>
      <div class="page-hero-media"><img src="/assets/img/svc-replacement.webp" srcset="{srcset("svc-replacement",1200)}" sizes="{SIZES_HERO}" width="1200" height="800" fetchpriority="high" alt="Roofing services in metro Detroit"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Services","/services/")])}
    {trust_strip()}
    <section class="section"><div class="container">{sections}</div></section>
    {value_props_block()}
    {cta_band()}'''
    render("/services/", "Roofing Services Metro Detroit | BH Roofing",
           "Residential & commercial roofing in metro Detroit — roof replacement, repair, storm & hail damage, inspections, flat, metal, gutters & siding. Free estimates.",
           body, graph)

def build_service(slug):
    c = SVC_COPY[slug]; i = SVC_INFO[slug]
    lk = Linker(svc_url(slug), budget=6)
    secs = ""
    for s in c["sections"]:
        b = paras(s["body"], lk)
        bl = ""
        if s.get("bullets"):
            bl = "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in s["bullets"]) + "</ul>"
        secs += f'<h2>{esc(s["h2"])}</h2>{b}{bl}'
    incl = "".join(f"<li>{esc(x)}</li>" for x in c["whats_included"])
    why = ""
    for w in c["why_us"]:
        why += f'<div class="feature"><div class="f-ic">{ICONS[i["icon"]]}</div><h3>{esc(w["title"])}</h3><p>{esc(w["text"])}</p></div>'
    faqs = [(f["q"],f["a"]) for f in c["faqs"]]
    rel = ""
    for r in RELATED[slug]:
        ri=SVC_INFO[r]; rc=SVC_COPY[r]
        rel += f'''<a class="card svc-card" href="{svc_url(r)}">
          <div class="sc-media"><img src="/assets/img/{ri["img"]}.webp" srcset="{srcset(ri["img"],1200)}" sizes="{SIZES_CARD}" width="1200" height="800" loading="lazy" alt="{esc(rc["h1"])}"></div>
          <div class="sc-body"><h3>{esc(ri["nav"])}</h3><p>{esc(rc["hero_tagline"])}</p><span class="sc-link">Learn more {ICONS["arrow"]}</span></div></a>'''
    # Rotate the city list per service page (step coprime with 18) so link equity reaches
    # every city page instead of concentrating on the same 8 every time.
    _off = (SVC_ORDER.index(slug) * 7) % len(CITY_ORDER)
    _svc_cities = [CITY_ORDER[(_off + k) % len(CITY_ORDER)] for k in range(8)]
    city_links = " · ".join(f'<a href="{city_url(s)}">{esc(city_name(s))}</a>' for s in _svc_cities)
    graph = [breadcrumb_node([("Home","/"),("Services","/services/"),(SVC_INFO[slug]["nav"],svc_url(slug))]),
             service_node(SERVICE_TYPE[slug], slug, c["meta_description"]), faq_node(faqs)]
    active = "cost" if slug=="roof-replacement-cost" else ""
    cost_link = ("" if slug=="roof-replacement-cost" else
                 '<p style="margin-top:.9em;font-size:.92rem;text-align:center"><a href="/services/roof-replacement-cost/">See typical metro Detroit roofing prices →</a></p>')
    group_badge = f'<span class="pill">{esc(i["group"])}</span>'
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div>{group_badge}<h1 style="margin-top:.5em">{esc(c["h1"])}</h1>
      <p>{esc(c["hero_tagline"])}</p>
      <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/contact/">Get a Free Estimate</a>
      {hero_secondary("btn-lg")}</div></div>
      <div class="page-hero-media"><img src="/assets/img/{i["img"]}.webp" srcset="{srcset(i["img"],1200)}" sizes="{SIZES_HERO}" width="1200" height="800" fetchpriority="high" alt="{esc(c["h1"])} — BH Roofing"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Services","/services/"),(SVC_INFO[slug]["nav"],svc_url(slug))])}
    {trust_strip()}
    <section class="section"><div class="container"><div class="split" style="align-items:flex-start">
      <div class="prose">
        <p class="lead">{esc_inline(c["intro_lead"], lk)}</p>
        {secs}
        <h2>What's included</h2>
        <ul>{incl}</ul>
      </div>
      <aside class="sidebar-card">
        <h3>Request this service</h3>
        <p style="color:var(--slate);font-size:.95rem">Free, no-obligation estimate — usually same or next day across metro Detroit whenever our schedule allows.</p>
        <a class="btn btn-primary btn-block" href="/contact/">Get My Free Estimate</a>
        {('<p class="text-center" style="margin:.8em 0 .2em;color:var(--steel);font-size:.9rem">or call</p><a class="btn btn-navy btn-block" href="tel:'+BIZ["tel"]+'">'+ICONS["phone"]+' '+esc(BIZ["phone"])+'</a>') if HAS_PHONE else ('<p class="text-center" style="margin:.8em 0 .2em;color:var(--steel);font-size:.9rem">or email</p><a class="btn btn-navy btn-block" href="mailto:'+BIZ["email"]+'">'+ICONS["mail"]+' Email Us</a>')}
        {cost_link}
        <h3 style="margin-top:1.4em">Why choose BH Roofing</h3>
        <ul class="chk">
          <li>Licensed &amp; insured local crew</li>
          <li>Fast, reliable scheduling</li>
          <li>Upfront, written pricing</li>
          <li>Workmanship guarantee</li>
          <li>Full cleanup &amp; magnetic nail sweep</li>
        </ul>
      </aside>
    </div></div></section>
    <section class="section bg-cloud"><div class="container">
      <div class="section-head center"><span class="eyebrow">Why homeowners choose us</span><h2>The BH Roofing difference</h2></div>
      <div class="grid grid-3">{why}</div></div></section>
    {faq_section(faqs, SVC_INFO[slug]["nav"] + " — FAQs")}
    <section class="section"><div class="container">
      <div class="section-head"><span class="eyebrow">Serving metro Detroit</span><h2>Available across every suburb we serve</h2>
      <p>Including {city_links} and <a href="/service-areas/">18+ more cities</a>.</p></div>
      <div class="section-head" style="margin-top:8px"><h2 style="font-size:1.5rem">Related services</h2></div>
      <div class="grid grid-4">{rel}</div>
      {resource_row(exclude=svc_url(slug))}</div></section>
    {cta_band()}'''
    render(svc_url(slug), c["meta_title"], c["meta_description"], body, graph, active=active,
           og_image="/assets/img/og-image.jpg")

def build_areas_hub():
    by_county = {"Wayne":[],"Oakland":[],"Macomb":[]}
    for s in CITY_ORDER:
        by_county[CITY_META[s][0]].append(s)
    cols = ""
    for county in ["Wayne","Oakland","Macomb"]:
        chips = "".join(f'<a class="city-chip" href="{city_url(s)}">{esc(city_name(s))} {ICONS["arrow"]}</a>' for s in by_county[county])
        cols += f'<div><div class="section-head" style="margin-bottom:14px"><h2 style="font-size:1.4rem">{esc(county)} County</h2></div><div class="grid" style="gap:10px">{chips}</div></div>'
    graph = [breadcrumb_node([("Home","/"),("Service Areas","/service-areas/")])]
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">Service Areas</span><h1>Metro Detroit Service Areas for Roofing</h1>
      <p>No storefront, no showroom markup — just a local crew that comes to you. We serve metro Detroit and every suburb within 35 miles across Wayne, Oakland, and Macomb counties.</p>
      <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/contact/">Get a Free Estimate</a>
      {hero_secondary("btn-lg")}</div></div>
      <div class="page-hero-media"><img src="/assets/img/area-neighborhood.webp" srcset="{srcset("area-neighborhood",1600)}" sizes="{SIZES_HERO}" width="1600" height="900" fetchpriority="high" alt="Metro Detroit suburban neighborhood served by BH Roofing"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Service Areas","/service-areas/")])}
    {trust_strip()}
    <section class="section"><div class="container">
      <div class="section-head"><h2>Cities we serve</h2><p>Tap your city for local roofing details. Don't see yours? We likely still cover it — just <a href="/contact/">ask</a>.</p></div>
      <div class="grid grid-3">{cols}</div></div></section>
    {value_props_block()}
    {cta_band()}'''
    render("/service-areas/", "Service Areas — Roofing Metro Detroit | BH Roofing",
           "See the metro Detroit cities BH Roofing serves — 18+ suburbs across Wayne, Oakland & Macomb counties. Roof replacement, repair & storm damage. Free estimates.",
           body, graph)

def build_city(slug):
    c = CITY_COPY[slug]; county, neighbors, top = CITY_META[slug]
    lk = Linker(city_url(slug), budget=5)
    ctx = paras(c["local_context"], lk)
    why = "".join(f"<li>{esc(x)}</li>" for x in c["why_local"])
    faqs = [(f["q"],f["a"]) for f in c["faqs"]]
    top_cards = ""
    for s in top:
        si=SVC_INFO[s]; sc=SVC_COPY[s]
        top_cards += f'''<a class="card svc-card" href="{svc_url(s)}">
          <div class="sc-media"><img src="/assets/img/{si["img"]}.webp" srcset="{srcset(si["img"],1200)}" sizes="{SIZES_CARD}" width="1200" height="800" loading="lazy" alt="{esc(si["nav"])} in {esc(c["city"])}, MI"></div>
          <div class="sc-body"><h3>{esc(si["nav"])}</h3><p>{esc(sc["hero_tagline"])}</p><span class="sc-link">Learn more {ICONS["arrow"]}</span></div></a>'''
    neigh = "".join(f'<a class="city-chip" href="{city_url(n)}">{esc(city_name(n))} {ICONS["arrow"]}<span>{CITY_META[n][0]} Co.</span></a>' for n in neighbors)
    graph = [breadcrumb_node([("Home","/"),("Service Areas","/service-areas/"),(c["city"],city_url(slug))]),
             service_node(f"Roofing in {c['city']}, MI", "roof-repair", c["meta_description"], areas=[slug],
                          url_path=city_url(slug), service_type="Roofing"),
             faq_node(faqs)]
    img_name = "area-neighborhood" if CITY_ORDER.index(slug)%2==0 else "area-neighborhood2"
    img = img_name + ".webp"
    _svc1 = SVC_INFO[top[0]]["nav"]; _svc2 = SVC_INFO[top[1]]["nav"]
    _ri = CITY_ORDER.index(slug) % 4
    if _ri == 0:
        repl_p = (f"Not every roof can — or should — be torn off. When years of {county} County freeze-thaw, ice dams, and summer heat have "
                  f"worn out your shingles, we'll tell you straight and quote a full roof replacement in {c['city']} at an honest, written price. "
                  f"You'll get clear repair-versus-replace advice, plus options across {_svc1.lower()} and {_svc2.lower()} that fit your home and budget.")
    elif _ri == 1:
        repl_p = (f"If your roof is past patching, our {c['city']} roof replacement service handles everything in one project — we protect the property, "
                  f"tear off the old layers, install fresh underlayment, ice-and-water shield, and shingles, then sweep up every nail. "
                  f"From {_svc1.lower()} to {_svc2.lower()}, replacement quotes in {c['city']} are always free and no-obligation.")
    elif _ri == 2:
        repl_p = (f"Thinking about a roof replacement in {c['city']}? We'll walk you through shingle choices, ventilation, and real "
                  f"pricing before you commit — and if a repair will honestly do the job, we'll say so. Most {c['city']} re-roofs, "
                  f"including {_svc1.lower()} and {_svc2.lower()}, are completed fast so your home isn't exposed to Michigan weather.")
    else:
        repl_p = (f"When {c['city']} homeowners ask whether it's time to replace their roof, we look at the shingles, flashing, valleys, and ventilation "
                  f"— not just the surface. If replacement wins, you get an exact written quote covering materials, labor, and cleanup. "
                  f"We handle everything from {_svc1.lower()} to {_svc2.lower()} across {county} County.")
    replacement_sec = f'<h2>Roof replacement in {esc(c["city"])}, MI</h2><p>{esc(repl_p)}</p>'
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">{esc(county)} County · Metro Detroit</span><h1>{esc(c["h1"])}</h1>
      <p>{esc(c["hero_tagline"])}</p>
      <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/contact/">Free Estimate in {esc(c["city"])}</a>
      {hero_secondary("btn-lg")}</div></div>
      <div class="page-hero-media"><img src="/assets/img/{img}" srcset="{srcset(img_name,1600)}" sizes="{SIZES_HERO}" width="1600" height="900" fetchpriority="high" alt="Roofing in {esc(c["city"])}, Michigan"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Service Areas","/service-areas/"),(c["city"],city_url(slug))])}
    {trust_strip()}
    <section class="section"><div class="container"><div class="split" style="align-items:flex-start">
      <div class="prose">
        <p class="lead">{esc_inline(c["intro_lead"], lk)}</p>
        <h2>Roofing {esc(c["city"])} homeowners rely on</h2>
        {ctx}
        {replacement_sec}
        <h2>The roofing {esc(c["city"])} homes need most</h2>
        <p>{esc_inline(c["service_emphasis"], lk)}</p>
      </div>
      <aside class="sidebar-card">
        <h3>Free estimate in {esc(c["city"])}</h3>
        <p style="color:var(--slate);font-size:.95rem">Local, licensed &amp; insured. Fast, reliable scheduling across {esc(county)} County.</p>
        <a class="btn btn-primary btn-block" href="/contact/">Get My Free Estimate</a>
        {('<p class="text-center" style="margin:.8em 0 .2em;color:var(--steel);font-size:.9rem">or call</p><a class="btn btn-navy btn-block" href="tel:'+BIZ["tel"]+'">'+ICONS["phone"]+' '+esc(BIZ["phone"])+'</a>') if HAS_PHONE else ('<p class="text-center" style="margin:.8em 0 .2em;color:var(--steel);font-size:.9rem">or email</p><a class="btn btn-navy btn-block" href="mailto:'+BIZ["email"]+'">'+ICONS["mail"]+' Email Us</a>')}
        <h3 style="margin-top:1.4em">Why {esc(c["city"])} calls BH Roofing</h3>
        <ul class="chk">{why}</ul>
      </aside>
    </div></div></section>
    <section class="section bg-cloud"><div class="container">
      <div class="section-head center"><span class="eyebrow">Popular in {esc(c["city"])}</span><h2>Our most-requested {esc(c["city"])} roofing services</h2></div>
      <div class="grid grid-4">{top_cards}</div></div></section>
    {faq_section(faqs, f"Roofing in {c['city']} — FAQs")}
    <section class="section"><div class="container">
      <div class="section-head"><span class="eyebrow">Nearby</span><h2>We also serve neighboring communities</h2></div>
      <div class="city-grid">{neigh}</div>
      {resource_row(exclude=city_url(slug))}</div></section>
    {cta_band(f"Need a roof repaired or replaced in {c['city']}?", "Get a free, no-obligation estimate today. Fast, reliable scheduling across " + county + " County whenever our schedule allows.")}'''
    render(city_url(slug), c["meta_title"], c["meta_description"], body, graph)

def build_about():
    a = CORE["about"]
    lk = Linker("/about/", budget=6)
    secs = ""
    for idx,s in enumerate(a["body"]):
        secs += f'<h2>{esc(s["h2"])}</h2>{paras(s["paras"], lk)}'
    vals = ""
    ics = ["shield","clock","hand","badge","truck","spark"]
    for idx,v in enumerate(a["values"]):
        vals += f'<div class="feature"><div class="f-ic">{ICONS[ics[idx%len(ics)]]}</div><h3>{esc(v["title"])}</h3><p>{esc(v["text"])}</p></div>'
    graph = [breadcrumb_node([("Home","/"),("About","/about/")])]
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">About Us</span><h1>{esc(a["h1"])}</h1><p>{esc(a["lead"])}</p>
      <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/contact/">Work With Us</a>
      {hero_secondary("btn-lg")}</div></div>
      <div class="page-hero-media"><img src="/assets/img/about-team.webp" srcset="{srcset("about-team",1200)}" sizes="{SIZES_HERO}" width="1200" height="900" fetchpriority="high" alt="BH Roofing — metro Detroit roofing team"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("About","/about/")])}
    {trust_strip()}
    <section class="section"><div class="container"><div class="prose wide" style="margin-inline:auto">{secs}</div>
      {resource_row(exclude="/about/")}</div></section>
    <section class="section bg-cloud"><div class="container">
      <div class="section-head center"><span class="eyebrow">What we stand for</span><h2>Values behind every roof</h2></div>
      <div class="grid grid-3">{vals}</div></div></section>
    {process_block()}
    {cta_band()}'''
    render("/about/", a["meta_title"], a["meta_description"], body, graph, active="about")

def build_financing():
    f = CORE["financing"]
    lk = Linker("/financing/", budget=5)
    pts = "".join(f"<li>{esc(x)}</li>" for x in f["points"])
    fin_faqs = [
        ("Can I finance a roof replacement in metro Detroit?",
         "Yes. BH Roofing offers financing options through third-party lenders on approved credit, so you can replace or repair your roof now and spread the cost over comfortable monthly payments. Ask your estimator for current plans when you book your free estimate."),
        ("Does applying for roofing financing change the price of the job?",
         "No. Your written quote is the same whether you pay upfront or finance. We quote the roof, materials, and labor first — then you choose the payment option that works for you. There's never a penalty for paying the job off early with our typical lender programs."),
        ("What roofing projects can be financed?",
         "Most projects qualify — full roof replacement, larger repairs, metal and flat roofing, gutters, and siding. Bigger jobs like a complete tear-off and re-roof are where monthly payments help most, but many mid-size repairs can qualify too."),
        ("How do I get started with financing?",
         "Book your free estimate first. Once you have your written quote, we'll walk you through the current financing options and the lender's short application — most decisions come back quickly, and approved projects can usually be scheduled right away."),
    ]
    graph = [breadcrumb_node([("Home","/"),("Financing","/financing/")]), faq_node(fin_faqs)]
    steps = """<ol>
        <li><strong>Get your free estimate.</strong> We inspect the roof, walk you through options at every price point, and give you a clear written quote — no obligation.</li>
        <li><strong>Choose how to pay.</strong> Pay upfront, or ask about monthly payment plans through our third-party lending partners on approved credit.</li>
        <li><strong>Quick application.</strong> The lender's application takes minutes, and most credit decisions come back fast.</li>
        <li><strong>We get to work.</strong> Once approved, we schedule your roofing project — often within days.</li>
      </ol>"""
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">Financing</span><h1>{esc(f["h1"])}</h1><p>{esc(f["lead"])}</p>
      <div class="hero-cta"><a class="btn btn-primary btn-lg" href="/contact/">Ask About Financing</a>
      {hero_secondary("btn-lg")}</div></div>
      <div class="page-hero-media"><img src="/assets/img/svc-cost.webp" srcset="{srcset("svc-cost",1200)}" sizes="{SIZES_HERO}" width="1200" height="800" fetchpriority="high" alt="Roof replacement financing options in metro Detroit"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Financing","/financing/")])}
    {trust_strip()}
    <section class="section"><div class="container"><div class="prose wide" style="margin-inline:auto">
      {paras(f["body"], lk)}
      <h2>Flexible ways to pay</h2><ul>{pts}</ul>
      <h2>How financing a roofing project works</h2>
      {steps}
      <h2>Why metro Detroit homeowners finance their roofs</h2>
      <p>A new roof is one of the highest-return upgrades a Michigan home can get — better protection against ice dams and leaks, lower energy bills through the freeze-thaw months, and instant curb appeal. But roofs fail on their own schedule, not your budget's. Financing lets you fix a leaking, storm-damaged, or worn-out roof <em>now</em>, before a Michigan winter makes it worse, and pay over time instead of putting the project off another season.</p>
      <p>It also means you don't have to settle. Homeowners who planned on the most basic shingle often find that for a modest monthly difference they can get the architectural shingles, upgraded ventilation, or metal roof they actually wanted. Pair your quote with our <a href="/services/roof-replacement-cost/">roof replacement cost guide</a> to see typical metro Detroit price ranges before we arrive.</p>
      <div class="note">Ask your BH Roofing estimator about current financing options and promotions when you book your free estimate. Terms are provided by third-party lenders on approved credit.</div>
    </div></div></section>
    {faq_section(fin_faqs, "Roofing financing — FAQs")}
    {cta_band("Ready to protect your home without the wait?", "Get your free estimate and ask about monthly payment options — fast, reliable scheduling across metro Detroit whenever our schedule allows.")}'''
    render("/financing/", f["meta_title"], f["meta_description"], body, graph)

def build_reviews():
    graph = [breadcrumb_node([("Home","/"),("Reviews","/reviews/")])]
    if BIZ["google"]:
        hero_btns = (f'<a class="btn btn-primary btn-lg" href="{BIZ["google"]}" target="_blank" rel="noopener">{ICONS["google"]} Read Google Reviews</a>'
                     f'<a class="btn btn-ghost btn-lg" href="/contact/">Get a Free Estimate</a>')
    else:
        hero_btns = (f'<a class="btn btn-primary btn-lg" href="/contact/">Get a Free Estimate</a>'
                     f'{hero_secondary("btn-lg")}')
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">Reviews</span><h1>What Metro Detroit Says About Us</h1>
      <p>{esc(CORE["reviews_lead"])}</p>
      <div class="hero-cta">{hero_btns}</div></div>
      <div class="page-hero-media"><img src="/assets/img/svc-replacement.webp" srcset="{srcset("svc-replacement",1200)}" sizes="{SIZES_HERO}" width="1200" height="800" fetchpriority="high" alt="Happy metro Detroit homeowners and their new roofs"></div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Reviews","/reviews/")])}
    {trust_strip()}
    <section class="section"><div class="container"><div class="prose wide" style="margin-inline:auto">
      <h2>Our promise to every customer</h2>
      <p>Reviews are earned, not written. As we complete roofs across metro Detroit, verified customer reviews will appear here and on our Google Business Profile. In the meantime, here's exactly what you can expect when you call BH Roofing:</p>
      <ul>
        <li><strong>On-time arrival</strong> in the window we promise — with a heads-up when we're on the way.</li>
        <li><strong>A clear, written quote</strong> before any work starts. No surprises, no pressure.</li>
        <li><strong>Clean, careful work</strong> that protects your property, followed by a full cleanup and magnetic nail sweep.</li>
        <li><strong>A workmanship guarantee</strong> — if something isn't right, we come back and make it right.</li>
      </ul>
      <div class="note">Already worked with us? We'd be grateful for your feedback — it helps your neighbors find a roofer they can trust. Get in touch and we'll send you a review link.</div>
    </div></div></section>
    {reviews_invite(on_reviews_page=True)}
    {cta_band()}'''
    render("/reviews/", "Reviews — BH Roofing Metro Detroit",
           "See what to expect from BH Roofing — metro Detroit's local roofing team. Licensed, insured, guaranteed, with honest pricing and fast scheduling.",
           body, graph, active="reviews")

def build_contact():
    graph = [breadcrumb_node([("Home","/"),("Contact","/contact/")])]
    svc_opts = "".join(f'<option value="{esc(SVC_INFO[s]["nav"])}">{esc(SVC_INFO[s]["nav"])}</option>' for s in SVC_ORDER)
    if HAS_PHONE:
        hero_call = f'<div style="margin-top:1.4em"><a class="btn btn-primary btn-lg" href="tel:{BIZ["tel"]}">{ICONS["phone"]} Call {esc(BIZ["phone"])}</a></div>'
        contact_feature = f'<div class="feature"><div class="f-ic">{ICONS["phone"]}</div><h3>Call or email</h3><p><a href="tel:{BIZ["tel"]}">{esc(BIZ["phone"])}</a><br><a href="mailto:{BIZ["email"]}">{esc(BIZ["email"])}</a></p></div>'
    else:
        hero_call = f'<div style="margin-top:1.4em"><a class="btn btn-primary btn-lg" href="mailto:{BIZ["email"]}">{ICONS["mail"]} Email {esc(BIZ["email"])}</a></div>'
        contact_feature = f'<div class="feature"><div class="f-ic">{ICONS["mail"]}</div><h3>Email us</h3><p><a href="mailto:{BIZ["email"]}">{esc(BIZ["email"])}</a><br><small>We reply fast — usually the same day.</small></p></div>'
    body = f'''<section class="page-hero"><div class="container"><div class="page-hero-grid">
      <div><span class="eyebrow">Contact</span><h1>Get Your Free Roofing Estimate</h1>
      <p>{esc(CORE["contact_lead"])}</p>
      <ul class="chk" style="margin-top:1.2em;max-width:420px">
        <li>Free, no-obligation estimates &amp; roof inspections</li>
        <li>Fast, reliable scheduling</li>
        <li>Licensed, insured &amp; local to metro Detroit</li>
      </ul>
      {hero_call}
      </div>
      <div class="form-card">
        <h2 style="font-size:1.5rem;margin-bottom:.2em">Request a callback</h2>
        <p style="color:var(--steel);font-size:.92rem;margin-bottom:1em">We'll get back to you fast — usually the same day.</p>
        <div id="formErr" class="note" role="alert" style="display:none;border-color:var(--danger);background:var(--danger-050);margin-bottom:16px">Sorry — something went wrong sending your request. Please email us at <a href="mailto:{BIZ["email"]}">{esc(BIZ["email"])}</a> and we'll help right away.</div>
        <form action="https://bh-roofing-form.oren-siyonov.workers.dev" method="POST">
          <div class="form-row">
            <div class="field"><label for="name">Name <span class="req">*</span></label><input id="name" name="name" required autocomplete="name"></div>
            <div class="field"><label for="phone">Phone <span class="req">*</span></label><input id="phone" name="phone" type="tel" required autocomplete="tel"></div>
          </div>
          <div class="form-row">
            <div class="field"><label for="city">City / ZIP</label><input id="city" name="city" autocomplete="address-level2" placeholder="e.g. Royal Oak"></div>
            <div class="field"><label for="service">Service needed</label><select id="service" name="service"><option value="">Choose…</option>{svc_opts}<option>Not sure / other</option></select></div>
          </div>
          <div class="field"><label for="message">How can we help?</label><textarea id="message" name="message" placeholder="Tell us about your roof…"></textarea></div>
          <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
          <button class="btn btn-primary btn-lg btn-block" type="submit">{ICONS["calendar"]} Request My Free Estimate</button>
          <p class="form-note">By submitting you agree to be contacted about your request. We never share your information.</p>
        </form>
      </div>
    </div></div></section>
    {breadcrumb([("Home","/"),("Contact","/contact/")])}
    <section class="section bg-cloud"><div class="container"><div class="grid grid-3">
      {contact_feature}
      <div class="feature"><div class="f-ic">{ICONS["clock"]}</div><h3>Hours</h3><p>{esc(BIZ["hours_full"])}</p></div>
      <div class="feature"><div class="f-ic">{ICONS["mappin"]}</div><h3>Service area</h3><p>{esc(BIZ["area_line"])} across Wayne, Oakland &amp; Macomb counties.</p></div>
    </div></div></section>
    {cta_band("Let's get your roof sorted", "Tell us what's going on and we'll take care of it. Free estimates and fast, reliable scheduling across metro Detroit whenever our schedule allows.")}'''
    render("/contact/", "Contact — Free Roofing Estimate | BH Roofing Metro Detroit",
           "Contact BH Roofing for a free roof replacement or repair estimate in metro Detroit. Fast, reliable scheduling — request your free estimate today.",
           body, graph, active="contact")

def build_gallery():
    graph = [breadcrumb_node([("Home","/"),("Gallery","/gallery/")])]
    shots = [("svc-replacement","Full asphalt shingle roof replacement"),("svc-repair","Roof leak & shingle repair"),
             ("svc-storm","Storm & hail damage restoration"),("svc-metal","Standing-seam metal roof"),
             ("svc-commercial","Flat & commercial roofing"),("svc-gutters","Seamless gutters & guards"),
             ("svc-siding","Siding installation & repair"),("svc-ventilation","Attic ventilation & skylights"),
             ("cta-roof","New roof at dusk")]
    cards = "".join(
        f'<figure class="card"><div class="sc-media" style="aspect-ratio:3/2"><img src="/assets/img/{s}.webp" srcset="{srcset(s, 1600 if s=="cta-roof" else 1200)}" sizes="{SIZES_CARD}" width="1200" height="800" loading="lazy" alt="{esc(t)} — BH Roofing metro Detroit"></div>'
        f'<figcaption class="sc-body"><h3 style="font-size:1.05rem">{esc(t)}</h3></figcaption></figure>'
        for s,t in shots)
    body = f'''<section class="page-hero"><div class="container">
      <div style="max-width:760px"><span class="eyebrow">Gallery</span><h1>Our Roofing Work Across Metro Detroit</h1>
      <p>A look at the kind of roof replacements, repairs, and exterior work we do every week for homeowners and businesses around Wayne, Oakland, and Macomb counties.</p></div>
    </div></section>
    {breadcrumb([("Home","/"),("Gallery","/gallery/")])}
    <section class="section"><div class="container"><div class="grid grid-3">{cards}</div>
      <div class="note mt-3">Photos shown are representative of our work and product styles. Ask us for recent project examples in your neighborhood when you book a free estimate.</div>
    </div></section>
    {cta_band()}'''
    render("/gallery/", "Gallery — Roofing Work | BH Roofing Metro Detroit",
           "See examples of roofing work by BH Roofing across metro Detroit — roof replacement, repair, storm damage, metal, flat, gutters & siding.",
           body, graph)

def build_faq_hub():
    all_faqs = [(f["q"],f["a"]) for f in CORE["home"]["faqs"]]
    seen = set(q for q,_ in all_faqs)
    for s in SVC_ORDER:
        for f in SVC_COPY[s]["faqs"]:
            if f["q"] not in seen:
                all_faqs.append((f["q"],f["a"])); seen.add(f["q"])
    graph = [breadcrumb_node([("Home","/"),("FAQ","/faq/")])]
    items = "".join(f'<details><summary>{esc(q)}</summary><div class="faq-a"><p>{esc(a)}</p></div></details>' for q,a in all_faqs)
    svc_faq_links = " · ".join(f'<a href="{svc_url(s)}">{esc(SVC_INFO[s]["nav"])}</a>' for s in SVC_ORDER)
    body = f'''<section class="page-hero"><div class="container">
      <div style="max-width:760px"><span class="eyebrow">Answers</span><h1>Roofing FAQs</h1>
      <p>Everything metro Detroit homeowners and businesses ask us about roofing — costs, timelines, storm damage, warranties, and more.</p></div>
    </div></section>
    {breadcrumb([("Home","/"),("FAQ","/faq/")])}
    <section class="section"><div class="container">
      <div class="prose wide" style="margin-inline:auto;margin-bottom:1.6em">
        <p class="lead">This is the master list of every question we get asked across metro Detroit — pulled together in one place so you can compare answers across services. Deciding between repair and replacement? Start with the cost questions, then check the service-specific ones below.</p>
        <p>Prefer answers in context? Each service page covers its own FAQs alongside photos, what's included, and pricing guidance: {svc_faq_links}. Still stuck? <a href="/contact/">Send us the question</a> — a real person answers, usually the same day.</p>
      </div>
      <div class="faq">{items}</div></div></section>
    {cta_band()}'''
    render("/faq/", "Roofing FAQs | BH Roofing Metro Detroit",
           "Answers to common questions about roofing in metro Detroit — cost, timelines, storm damage, warranties, financing, and more.",
           body, graph)

def build_thanks():
    graph = [breadcrumb_node([("Home","/"),("Thank You","/thank-you/")])]
    if HAS_PHONE:
        sooner = f'<a class="btn btn-primary btn-lg" href="tel:{BIZ["tel"]}">{ICONS["phone"]} Call {esc(BIZ["phone"])}</a>'
    else:
        sooner = f'<a class="btn btn-primary btn-lg" href="mailto:{BIZ["email"]}">{ICONS["mail"]} Email Us</a>'
    body = f'''<section class="section" style="min-height:52vh;display:grid;place-items:center;text-align:center"><div class="container" style="max-width:640px">
      <div class="f-ic" style="margin:0 auto 18px;width:70px;height:70px;background:var(--success-050);color:var(--success);border-radius:18px;display:grid;place-items:center">{ICONS["check"]}</div>
      <h1>Thanks — we've got your request!</h1>
      <p class="lead">A member of the BH Roofing team will reach out shortly, usually the same day. Need us sooner?</p>
      <div class="hero-cta" style="justify-content:center">{sooner}
      <a class="btn btn-ghost btn-lg" href="/">Back to home</a></div>
    </div></section>'''
    render("/thank-you/", "Thank You | BH Roofing Metro Detroit",
           "Thanks for contacting BH Roofing. We'll be in touch shortly.", body, graph,
           noindex=True)

def build_privacy():
    body = f'''<section class="page-hero"><div class="container">
      <div style="max-width:760px"><span class="eyebrow">Legal</span><h1>Privacy Policy</h1>
      <p>How {esc(BIZ["name"])} collects, uses, and protects your personal information when you visit our website or contact us for service in Metro Detroit.</p></div>
    </div></section>
    {breadcrumb([("Home","/"),("Privacy Policy","/privacy-policy/")])}
    <section class="section"><div class="container"><div class="prose wide" style="margin-inline:auto">
      <p><strong>Effective Date:</strong> January 1, 2026</p>
      <p>{esc(BIZ["name"])} (&ldquo;we,&rdquo; &ldquo;our,&rdquo; or &ldquo;us&rdquo;) respects your privacy and is committed to protecting the personal information you share with us. This Privacy Policy explains what information we collect when you visit <strong>{esc(BIZ["domain"])}</strong>, call or text us, or submit a service request in Metro Detroit, Michigan, how we use and safeguard that information, and your choices regarding your data.</p>

      <h2>Information We Collect</h2>
      <p>We collect information in two main ways:</p>
      <ul>
        <li><strong>Information You Provide Directly:</strong> When you fill out our contact form, call us, send an SMS text message, or email us, we may collect your name, phone number, email address, property address or city/ZIP code, and details about your service or inspection request.</li>
        <li><strong>Information Collected Automatically:</strong> When you browse our website, we automatically collect standard technical and usage information such as your IP address, browser type, device type, operating system, referring URLs, pages viewed, and the dates and times of your visits through cookies and analytics tools, including Matomo analytics.</li>
      </ul>

      <h2>How We Use Your Information</h2>
      <p>We use the information we collect to operate our business and deliver local service across Wayne, Oakland, and Macomb counties, including:</p>
      <ul>
        <li>Scheduling on-site visits and technician dispatches</li>
        <li>Responding to your inquiries, providing estimates, evaluating your project or repair needs, and providing service recommendations</li>
        <li>Communicating with you by phone, SMS text, or email about appointments, arrival windows, and follow-up support</li>
        <li>Providing customer support and honoring our workmanship guarantee</li>
        <li>Monitoring website performance, diagnosing technical issues, improving user experience, and preventing spam or fraudulent submissions</li>
      </ul>

      <h2>SMS &amp; Phone Communications</h2>
      <p>If you call us, text us, or provide your phone number through our website contact form, you consent to receive phone calls and SMS text messages from {esc(BIZ["name"])} regarding your service inquiry, appointment scheduling, dispatch updates, and customer support.</p>
      <ul>
        <li><strong>Opt-Out:</strong> You may opt out of receiving SMS text messages at any time by replying <strong>STOP</strong> to any message we send, or by contacting us at <a href="tel:{BIZ["tel"]}">{esc(BIZ["phone"])}</a> or <a href="mailto:{BIZ["email"]}">{esc(BIZ["email"])}</a>. You may reply <strong>HELP</strong> for assistance.</li>
        <li><strong>Message &amp; Data Rates:</strong> Standard message and data rates from your wireless carrier may apply. Message frequency varies based on your active service request.</li>
        <li><strong>No Third-Party Marketing Sharing:</strong> We never sell, rent, or share your mobile phone number or SMS opt-in consent data with third parties or affiliates for marketing or promotional purposes.</li>
      </ul>

      <h2>Information Sharing &amp; Disclosure</h2>
      <p>We do not sell, rent, or trade your personal information to third parties. We share personal information only in the following limited situations:</p>
      <ul>
        <li><strong>Service Delivery &amp; Trusted Providers:</strong> With our field technicians, dispatch personnel, and trusted service providers (such as secure form routing, hosting, analytics, or communication tools) strictly as necessary to respond to and fulfill your service request.</li>
        <li><strong>Financing Partners (At Your Request):</strong> If you choose to apply for financing through a third-party lender, the information you submit on that application is handled in accordance with that lender&rsquo;s privacy policy.</li>
        <li><strong>Legal Obligations &amp; Protection:</strong> When required by law, subpoena, court order, or government regulation, or when necessary to protect the safety, rights, or property of {esc(BIZ["name"])}, our customers, or the public.</li>
      </ul>

      <h2>Cookies &amp; Analytics</h2>
      <p>Our website uses first-party cookies and Matomo analytics to measure site traffic, understand which services and Metro Detroit service areas visitors are researching, and record aggregate actions such as phone-link clicks or form submissions. We also use Cloudflare Turnstile on our contact form to protect against automated spam without tracking you across the web.</p>
      <p>You can configure your web browser to block or delete cookies at any time. Blocking cookies will not prevent you from reading our pages or calling us directly.</p>

      <h2>Data Security &amp; Retention</h2>
      <p>We maintain reasonable administrative, technical, and physical safeguards, including HTTPS encryption and restricted access to customer inquiries, to protect your personal information against unauthorized access, loss, misuse, or alteration. We retain personal information only for as long as needed to complete your service request, maintain warranty and service records, and comply with applicable legal, tax, and accounting requirements.</p>

      <h2>Your Privacy Rights &amp; Contact Information</h2>
      <p>You may request to access, update, correct, or delete the personal information we hold about you, or opt out of future communications at any time. To make a request or ask any questions about this Privacy Policy, please contact us:</p>
      <ul>
        <li><strong>Business Name:</strong> {esc(BIZ["name"])}</li>
        <li><strong>Service Area:</strong> Metro Detroit, MI (Wayne, Oakland &amp; Macomb Counties)</li>
        <li><strong>Phone:</strong> <a href="tel:{BIZ["tel"]}">{esc(BIZ["phone"])}</a></li>
        <li><strong>Email:</strong> <a href="mailto:{BIZ["email"]}">{esc(BIZ["email"])}</a></li>
      </ul>
    </div></div></section>
    {cta_band()}'''
    render("/privacy-policy/", f"Privacy Policy | {BIZ['name']}",
           f"Privacy Policy for {BIZ['name']}. Learn how we collect, use, and protect your personal information when you request service in Metro Detroit.",
           body, [breadcrumb_node([("Home","/"),("Privacy Policy","/privacy-policy/")])])

def build_404():
    body = f'''<section class="section" style="min-height:56vh;display:grid;place-items:center;text-align:center"><div class="container" style="max-width:640px">
      <span class="eyebrow" style="justify-content:center">Error 404</span>
      <h1>This page slipped through the shingles</h1>
      <p class="lead">The page you're looking for isn't here — but we can still help with your roof. Try one of these:</p>
      <div class="hero-cta" style="justify-content:center"><a class="btn btn-primary btn-lg" href="/">Home</a>
      <a class="btn btn-ghost btn-lg" href="/services/">Services</a>
      <a class="btn btn-ghost btn-lg" href="/contact/">Free Estimate</a></div>
    </div></section>'''
    doc = page_wrap("/404.html","Page Not Found | BH Roofing","Page not found.",body,[],robots="noindex,follow")
    open(os.path.join(ROOT,"404.html"),"w",encoding="utf-8").write(doc)

def page_wrap(path,title,desc,body,graph,robots="index,follow,max-image-preview:large"):
    g=[business_node()]+graph
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"><meta name="robots" content="{robots}">
<meta name="theme-color" content="#0d2035">
<link rel="stylesheet" href="/assets/css/styles.css?v={ASSET_VER}"><link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/assets/img/logo-mark.svg"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
{jsonld(g)}</head><body>{header()}<main id="main">{body}</main>{footer()}{mobile_cta()}
<script src="/assets/js/main.js?v={ASSET_VER}" defer></script>
{MATOMO}</body></html>'''

# --------------------------------------------------------------------------- #
#  SITEMAP / ROBOTS / MANIFEST / CNAME
# --------------------------------------------------------------------------- #
def build_meta_files():
    urls = ["/","/services/","/service-areas/","/about/","/reviews/","/financing/","/gallery/","/faq/","/contact/","/privacy-policy/"]
    urls += [svc_url(s) for s in SVC_ORDER]
    urls += [city_url(s) for s in CITY_ORDER]
    entries = ""
    for u in urls:
        pr = "1.0" if u=="/" else ("0.9" if u in ("/services/","/service-areas/") else "0.8")
        cf = "weekly" if u in ("/","/services/","/service-areas/") else "monthly"
        entries += f'  <url><loc>{U(u)}</loc><lastmod>{TODAY}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>\n'
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n'
    open(os.path.join(ROOT,"sitemap.xml"),"w",encoding="utf-8").write(sitemap)

    robots = f"""User-agent: *
Allow: /

Sitemap: {BIZ['base']}/sitemap.xml
"""
    open(os.path.join(ROOT,"robots.txt"),"w",encoding="utf-8").write(robots)

    manifest = {
        "name": BIZ["name"], "short_name": BIZ["short"],
        "description": "Roofing — replacement, repair & storm damage in metro Detroit.",
        "start_url": "/", "display": "standalone",
        "background_color": "#0d2035", "theme_color": "#0d2035",
        "icons": [
            {"src":"/assets/img/icon-192.png","sizes":"192x192","type":"image/png"},
            {"src":"/assets/img/icon-512.png","sizes":"512x512","type":"image/png"},
            {"src":"/assets/img/apple-touch-icon.png","sizes":"512x512","type":"image/png","purpose":"any maskable"},
        ],
    }
    open(os.path.join(ROOT,"site.webmanifest"),"w",encoding="utf-8").write(json.dumps(manifest,indent=2))
    open(os.path.join(ROOT,"CNAME"),"w",encoding="utf-8").write(BIZ["domain"]+"\n")
    open(os.path.join(ROOT,".nojekyll"),"w",encoding="utf-8").write("")

# --------------------------------------------------------------------------- #
def main():
    build_home()
    build_services_hub()
    for s in SVC_ORDER: build_service(s)
    build_areas_hub()
    for c in CITY_ORDER: build_city(c)
    build_about()
    build_financing()
    build_reviews()
    build_contact()
    build_gallery()
    build_faq_hub()
    build_privacy()
    build_thanks()
    build_404()
    build_meta_files()
    n = 10 + len(SVC_ORDER) + len(CITY_ORDER)
    print(f"Built {n} pages + sitemap/robots/manifest/CNAME.")

if __name__ == "__main__":
    main()

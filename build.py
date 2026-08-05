#!/usr/bin/env python3
"""
ProMan Painting & Wallpaper — static site generator.

Everything the site says lives in this file. Edit the data at the top,
run `python3 build.py`, and the whole site regenerates into docs/.

    python3 build.py                      # live build, served from the domain root
    python3 build.py --preview REPO-NAME  # preview build for a GitHub project page
    python3 build.py --preview            # preview build for opening files locally

GitHub Pages then serves docs/ directly — no build step on GitHub's side.

Preview mode exists because every internal link here is absolute (/about/,
/assets/...). That is correct at a domain root, but wrong at
account.github.io/repo-name/ and wrong again when a folder is opened straight
off disk. Preview mode rewrites those links, adds noindex so a preview can
never outrank the real site, and skips the CNAME file so GitHub does not
redirect the preview to a domain that is not live yet.
"""

import html
import os
import re
import shutil
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "docs")
TODAY = date.today().isoformat()

# Set by --preview. BASE_PATH is "/repo-name" for a project page, or "." for a
# folder opened directly from disk.
PREVIEW = False
BASE_PATH = ""

# ---------------------------------------------------------------------------
# 1. BUSINESS FACTS
#    ⚠️  Anything marked TODO is not confirmed yet. Fill it in before launch.
# ---------------------------------------------------------------------------

BIZ = {
    "name": "ProMan Painting & Wallpaper",
    "short": "ProMan",
    "owner": "Roman Ponomarenko",
    # Used for every tel: link, the header, the footer and the schema.
    "phone": "(864) 205-5618",
    # TODO: confirm the mailbox exists on the domain before launch.
    "email": "info@paintingwallpapers.com",
    "domain": "paintingwallpapers.com",          # confirmed by Roman, Aug 2026
    "street": "412 Thiago Ct",                   # not published — see SHOW_STREET
    "city": "Lyman",
    "state": "SC",
    "zip": "29365",
    "hours": "Open 24 hours",
    "gbp_url": "https://maps.app.goo.gl/",       # TODO: real Google Maps link
    "gbp_review_url": "https://g.page/r/",       # TODO: "leave a review" short link
    "thumbtack_url": "https://www.thumbtack.com/sc/lyman/",  # TODO: real profile URL
    "facebook_url": "https://www.facebook.com/profile.php?id=61561333509474",
    "instagram_url": "",                         # TODO
}

# Lyman is a home base, not a storefront. Service-area businesses should not
# publish a residential street address — Google recommends hiding it, and it
# keeps Roman's home off the open web. Flip to True only if a real office opens.
SHOW_STREET = False

# Verified social proof. These are the ONLY numbers the site is allowed to use.
PROOF = {
    "google_rating": "5.0",
    "google_count": 28,
    "thumbtack_rating": "4.9",
    "thumbtack_count": 83,
}
PROOF["total_reviews"] = PROOF["google_count"] + PROOF["thumbtack_count"]

# Claims that need paperwork behind them. Leave False/None until confirmed —
# flipping a flag adds the claim everywhere it belongs, and nowhere else.
CLAIMS = {
    "insured": False,     # general liability policy in hand?
    "licensed": False,    # SC license?
    "years": None,        # int — years in business
    "warranty": None,     # str — e.g. "2-year workmanship warranty"
    "projects": None,     # int — completed projects
}

# Contact form. Free Formspree account → paste the form ID here.
# Until then the form falls back to a plain mailto: so it still works.
FORM_ENDPOINT = ""  # e.g. "https://formspree.io/f/xyzabcde"

SITE_URL = "https://" + BIZ["domain"]

PHONE_HREF = "tel:+1" + re.sub(r"\D", "", BIZ["phone"])

# ---------------------------------------------------------------------------
# 2. SERVICES
# ---------------------------------------------------------------------------

SERVICES = [
    {
        "slug": "wallpaper-installation",
        "card": "Murals, designer paper, grasscloth and papered ceilings — planned, primed and hung with seams you cannot find.",
        "nav": "Wallpaper Installation",
        "h1": "Wallpaper Installation in Greenville & Spartanburg, SC",
        "title": "Wallpaper Installation Greenville SC | ProMan Painting & Wallpaper",
        "desc": "Professional wallpaper installation across Greenville, Spartanburg and the "
                "Upstate. Murals, designer paper, grasscloth and peel-and-stick. Free estimates.",
        "img": "dining-after.jpg",
        "alt": "Dark botanical wallpaper installed above white board-and-batten wainscoting in a dining room",
        "intro": "Wallpaper is what we are known for. Most painting companies in the Upstate "
                 "will quote you for paint and quietly pass on the paper — hanging it well is a "
                 "different trade, and a bad job shows from across the room.",
        "body": [
            ("What we hang",
             "Designer and boutique papers, hand-painted murals, grasscloth and natural "
             "fibres, textured and embossed paper, metallic and foil, traditional pre-pasted "
             "rolls, and peel-and-stick. Ceilings, accent walls, powder rooms, stair walls, "
             "closets and niches — including the awkward ones."),
            ("Pattern matching is the whole job",
             "A repeat that drifts a quarter inch per drop is invisible on roll two and "
             "obvious by roll six. We plan the layout before the first strip goes up: where "
             "the pattern breaks, which corner takes the mismatch, how the repeat lands at "
             "eye level and above the door. On a mural we dry-lay the panels first."),
            ("Prep decides whether it lasts",
             "Paper telegraphs everything underneath it. We skim and sand the wall flat, prime "
             "with the right sealer for the substrate and the paper, and let it cure. Skipping "
             "primer is the single most common reason paper bubbles, or takes the drywall face "
             "with it when it eventually comes off."),
        ],
        "bullets": [
            "Designer, mural and premium papers handled daily",
            "Pattern and repeat planned before the first drop",
            "Walls skimmed, sanded and primed properly first",
            "Tight seams, no bubbles, no lifted edges",
            "Outlets, vents and trim cut in clean",
            "Floors and furniture protected, full cleanup after",
        ],
    },
    {
        "slug": "wallpaper-removal",
        "card": "Old paper steamed off without wrecking the drywall, then patched and primed ready for whatever comes next.",
        "nav": "Wallpaper Removal",
        "h1": "Wallpaper Removal in Greenville & Spartanburg, SC",
        "title": "Wallpaper Removal Greenville SC | ProMan Painting & Wallpaper",
        "desc": "Old wallpaper removed without wrecking the drywall, walls repaired and left "
                "ready to paint or re-paper. Serving Greenville, Spartanburg and the Upstate.",
        "img": "bath-lemon.jpg",
        "alt": "Bathroom with botanical wallpaper on the upper wall above painted wainscoting",
        "intro": "Removal is the job people try themselves first and call us about second. "
                 "The paper comes off in postage stamps, the drywall face tears, and now there "
                 "is a skim-coat job on top of the original project.",
        "body": [
            ("Why it goes wrong",
             "Wallpaper hung straight onto unprimed drywall bonds to the paper face of the "
             "board. Pull hard and the face comes with it. Once that happens the wall needs "
             "skimming and sanding before anything can go back on it — which is a bigger job "
             "than the removal was."),
            ("How we do it",
             "We test a small area first to find out what we are dealing with: what the paper "
             "is, what is under it, and whether it was primed. Then we score, soak and steam "
             "to the paper's tolerance, take the backing off with it, and wash the adhesive "
             "residue off rather than leaving it to ghost through the next finish."),
            ("Left ready for the next thing",
             "Torn face paper and gouges get patched and skimmed, walls sanded flat and "
             "primed. You end up with a wall that is genuinely ready to paint or re-paper, "
             "not one that needs another trade to fix first."),
        ],
        "bullets": [
            "Test patch first — no guessing at the method",
            "Score, steam and soak matched to the paper",
            "Backing and adhesive residue both removed",
            "Torn drywall face patched and skimmed flat",
            "Walls primed and ready to paint or re-paper",
            "Contained mess, floors covered, full cleanup",
        ],
    },
    {
        "slug": "interior-painting",
        "card": "Walls, ceilings, trim and accent walls — prepped properly, cut by hand, cleaned up at the end of every day.",
        "card_pos": "50% 100%",
        "nav": "Interior Painting",
        "h1": "Interior Painting in Greenville & Spartanburg, SC",
        "title": "Interior Painting Greenville SC | ProMan Painting & Wallpaper",
        "desc": "Interior house painting across Greenville, Spartanburg and the Upstate — "
                "walls, ceilings, trim, doors and accent walls. Free estimates.",
        "img": "accent-wall.jpg",
        "alt": "Bedroom accent wall before and after, repainted in deep charcoal",
        "intro": "Walls, ceilings, trim, doors, closets and accent walls — a room at a time or "
                 "the whole house at once.",
        "body": [
            ("Prep, then paint",
             "Nail pops and cracks filled, caulk lines cut and replaced where they have split, "
             "glossy and patched areas spot-primed so they do not flash through the topcoat. "
             "The finish is only ever as good as the hour before it."),
            ("Your house stays livable",
             "Floors covered, furniture moved and wrapped, edges cut by hand. We clean up at "
             "the end of each day rather than leaving the room staged for tomorrow — which "
             "matters when the room is one you still have to live in."),
            ("Colour, if you want the help",
             "Bring your own colours or we will talk it through on site. North-facing rooms in "
             "the Upstate go cold with the wrong white, and a colour that reads warm on a chip "
             "in the store can read pink on a wall at four in the afternoon. Sample first."),
        ],
        "bullets": [
            "Walls, ceilings, trim, doors, baseboards",
            "Accent walls and feature colours",
            "Cracks, nail pops and caulk lines repaired first",
            "Spot-priming so patches do not flash",
            "Furniture and flooring covered and protected",
            "Cleaned up daily, not just at the end",
        ],
    },
    {
        "slug": "trim-and-molding",
        "card": "Crown molding, baseboards, casing and board-and-batten — installed, caulked and painted as one job.",
        "nav": "Trim & Molding",
        "h1": "Trim, Molding & Millwork in Greenville & Spartanburg, SC",
        "title": "Trim & Crown Molding Installation Greenville SC | ProMan",
        "desc": "Trim, crown molding, baseboards and board-and-batten installed and finished. "
                "Serving Greenville, Spartanburg and the Upstate. Free estimates.",
        "img": "rose-after.jpg",
        "alt": "Framed wall panel with a rose mural inside a painted molding surround",
        "intro": "Crown molding, baseboards, casing, chair rail, board-and-batten and picture "
                 "frame panelling — installed, caulked and finished, not just tacked up.",
        "body": [
            ("Installed and finished as one job",
             "Plenty of carpenters will hang trim and leave the filling, caulking and painting "
             "to someone else. We do the whole thing, which means the miters, the caulk lines "
             "and the paint are all one person's responsibility."),
            ("Where it earns its keep",
             "Panelling and board-and-batten under a papered wall is the detail that makes a "
             "dining room look designed rather than decorated. It is also the cheapest way to "
             "give a builder-grade room some architecture."),
            ("Old houses are not square",
             "Neither are plenty of new ones. Miters get cut to the angle the wall actually is, "
             "not the angle it should be, and the gap gets closed with caulk and filler rather "
             "than hidden behind a bead of silicone."),
        ],
        "bullets": [
            "Crown molding and ceiling trim",
            "Baseboards, casing and chair rail",
            "Board-and-batten and picture frame panelling",
            "Cut to the angles the room actually has",
            "Filled, caulked and painted as part of the job",
            "Coordinated with wallpaper and paint work",
        ],
    },
    {
        "slug": "commercial-painting",
        "card": "Offices, retail and professional spaces, scheduled around your hours so the business keeps running.",
        "nav": "Commercial Painting",
        "h1": "Commercial Painting & Wallpaper in Greenville & Spartanburg, SC",
        "title": "Commercial Painting Greenville SC | ProMan Painting & Wallpaper",
        "desc": "Commercial painting and wallcovering for offices, retail and small commercial "
                "spaces across Greenville, Spartanburg and the Upstate. Free estimates.",
        "img": "office-after.jpg",
        "alt": "Office feature wall finished in dark geometric wallpaper with a gold pattern",
        "intro": "Offices, retail units, real estate and professional spaces. Feature walls, "
                 "full repaints and commercial wallcovering — scheduled so your business keeps "
                 "running.",
        "body": [
            ("A Keller Williams office, done after hours",
             "The private office in the photograph above is at a Keller Williams real estate "
             "office here in the Upstate. The drywall had damage that had to be repaired and "
             "skimmed flat before anything could go on it, and the geometric paper had to be "
             "cut in around a window return and a wall-mounted TV. The work ran outside "
             "business hours, and the agent came back to a finished room."),
            ("Around your hours, not ours",
             "Evenings, weekends and phased room-by-room work so the space stays usable. For "
             "most offices the practical answer is one room at a time after close, and the team "
             "walks into a finished room on Monday."),
            ("A feature wall does a lot of work",
             "The wall behind reception or the conference camera is the one every client and "
             "every video call sees. It is a small area, a short job, and it changes the read "
             "of the whole space more than repainting everything beige again."),
            ("Finished properly around the details",
             "Commercial rooms are full of obstacles — mounted screens, cable runs, vents, "
             "window returns, signage. Those cut-ins are where a commercial job looks cheap or "
             "looks right."),
        ],
        "bullets": [
            "Offices, retail and professional spaces",
            "Feature walls and commercial wallcovering",
            "Evening, weekend and phased scheduling",
            "Clean cut-ins around screens, vents and cabling",
            "Low-odour and fast-dry products where needed",
            "Site left clean and usable each morning",
        ],
    },
    {
        "slug": "cabinet-painting",
        "card": "Kitchen and bathroom cabinets degreased, sanded, bonding-primed and finished in an enamel that cures hard.",
        "nav": "Cabinet Painting",
        "h1": "Cabinet Painting in Greenville & Spartanburg, SC",
        "title": "Cabinet Painting Greenville SC | ProMan Painting & Wallpaper",
        "desc": "Kitchen and bathroom cabinet painting across Greenville, Spartanburg and the "
                "Upstate — degreased, sanded, primed and finished properly. Free estimates.",
        "img": None,
        "alt": "",
        "intro": "Painting the cabinets is the cheapest change that makes a kitchen look like a "
                 "different kitchen. Done badly it is also the fastest thing to start peeling.",
        "body": [
            ("Degrease first, and properly",
             "Kitchen cabinet doors carry years of cooking grease, especially above the range. "
             "Paint does not stick to grease. Every door and frame gets cleaned and degreased "
             "before anything else happens — this is the step that gets skipped on cheap quotes "
             "and the reason the finish fails within a year."),
            ("Sand, prime, then finish",
             "Doors come off and get labelled, hardware bagged by location. Everything gets "
             "scuff-sanded, primed with a bonding primer suited to the substrate, and finished "
             "in a cabinet-grade enamel that cures hard enough to take daily use."),
            ("What to expect while it runs",
             "A typical kitchen is several days, most of which is drying and curing time rather "
             "than active work. Doors come back on at the end. The finish keeps hardening for a "
             "couple of weeks after we leave — go easy on it at first."),
        ],
        "bullets": [
            "Kitchen and bathroom cabinets, vanities, built-ins",
            "Doors removed, labelled, hardware bagged by location",
            "Degreased, scuff-sanded and bonding-primed",
            "Cabinet-grade enamel that cures hard",
            "Boxes and frames finished in place",
            "Kitchen left clean and usable each evening",
        ],
    },
    {
        "slug": "exterior-painting",
        "card": "Siding, trim, soffits and shutters, prepped for South Carolina humidity and hard afternoon sun.",
        "nav": "Exterior Painting",
        "h1": "Exterior Painting in Greenville & Spartanburg, SC",
        "title": "Exterior Painting Greenville SC | ProMan Painting & Wallpaper",
        "desc": "Exterior house painting for Greenville, Spartanburg and the Upstate — siding, "
                "trim, soffits, shutters and doors. Free estimates.",
        "img": None,
        "alt": "",
        "intro": "Siding, trim, soffits, fascia, shutters, doors and porches — prepped for "
                 "South Carolina weather rather than for the photograph.",
        "body": [
            ("Upstate weather is the real client",
             "Humidity, hard afternoon sun on the south and west elevations, and pollen for "
             "several weeks each spring. Paint fails here from the substrate outward — through "
             "chalked siding, unsealed end grain and failed caulk joints — long before the "
             "colour gives up."),
            ("Prep is most of the job",
             "Wash and let it dry properly. Scrape and sand failing areas back to sound edges. "
             "Re-caulk the joints that have opened. Spot-prime bare wood and every stain that "
             "would otherwise bleed through. Only then does colour go on."),
            ("Timing",
             "Late spring through early autumn is the window, avoiding the days when humidity "
             "or overnight temperatures stop the film from curing. We would rather move a day "
             "than put a coat on that will not cure — it costs a day now instead of the finish "
             "later."),
        ],
        "bullets": [
            "Siding, trim, soffits, fascia and shutters",
            "Front doors, porches, columns and railings",
            "Washed, scraped and sanded back to sound edges",
            "Joints re-caulked, bare wood spot-primed",
            "Exterior-grade products rated for SC humidity",
            "Landscaping and hardscape covered",
        ],
    },
    {
        "slug": "deck-and-fence-painting",
        "card": "Decks, fences and railings cleaned, dried through and sealed against the sun and the damp.",
        "nav": "Deck & Fence",
        "h1": "Deck & Fence Painting and Staining in Greenville & Spartanburg, SC",
        "title": "Deck Staining & Fence Painting Greenville SC | ProMan",
        "desc": "Deck and fence staining, sealing and painting across Greenville, Spartanburg "
                "and the Upstate. Free estimates.",
        "img": None,
        "alt": "",
        "intro": "Decks, fences, pergolas and railings — cleaned, prepped and sealed against "
                 "the sun and the humidity that take them apart.",
        "body": [
            ("Stain or paint",
             "Stain soaks in, shows the grain and wears thin gradually — easy to refresh, needs "
             "doing more often. Paint sits on top, covers tired wood and lasts longer, but when "
             "it does fail it peels and the next prep is a bigger job. On a deck underfoot, "
             "stain is usually the better answer."),
            ("Clean and dry before anything",
             "Wood cleaned of mildew, algae and grey weathered fibre, then given time to dry "
             "through. Sealing damp wood traps the moisture inside and the finish lifts within "
             "a season."),
            ("The details that fail first",
             "End grain, the tops of rails, and the gap where boards meet the joist — these go "
             "first because they hold water longest. They get the extra attention rather than "
             "the same single pass as the open boards."),
        ],
        "bullets": [
            "Decks, fences, pergolas, railings and gates",
            "Cleaned of mildew, algae and weathered fibre",
            "Dried through before any finish goes on",
            "Stain, semi-transparent or solid — your call",
            "End grain and rail tops given extra coverage",
            "Plants and siding protected during the work",
        ],
    },
]

SERVICE_BY_SLUG = {s["slug"]: s for s in SERVICES}

# Services shown in the header dropdown (all of them, in this order)
NAV_SERVICES = [
    "wallpaper-installation", "wallpaper-removal", "interior-painting",
    "trim-and-molding", "commercial-painting", "cabinet-painting",
    "exterior-painting", "deck-and-fence-painting",
]

# ---------------------------------------------------------------------------
# 3. SERVICE AREA
# ---------------------------------------------------------------------------

CITIES = [
    {"slug": "greenville-sc", "name": "Greenville", "county": "Greenville County", "tier": 1,
     "blurb": "Downtown, North Main, Augusta Road, Overbrook and the neighbourhoods around "
              "them — a mix of older homes that need careful prep and new builds that need "
              "character adding."},
    {"slug": "spartanburg-sc", "name": "Spartanburg", "county": "Spartanburg County", "tier": 1,
     "blurb": "Converse Heights, Hampton Heights, Duncan Park and out toward Westside. Plenty "
              "of older plaster and original trim that rewards doing the prep properly."},
    {"slug": "greer-sc", "name": "Greer", "county": "Greenville & Spartanburg Counties", "tier": 2,
     "blurb": "Between both our main markets and growing fast. A lot of newer construction "
              "where a papered feature wall is the quickest way out of builder beige."},
    {"slug": "simpsonville-sc", "name": "Simpsonville", "county": "Greenville County", "tier": 2,
     "blurb": "Family neighbourhoods and steady new construction. Nurseries, playrooms and "
              "dining rooms are most of what we are called for here."},
    {"slug": "five-forks-sc", "name": "Five Forks", "county": "Greenville County", "tier": 2,
     "blurb": "Larger homes and higher-end finishes, where designer paper and detailed "
              "millwork are worth the extra care."},
    {"slug": "taylors-sc", "name": "Taylors", "county": "Greenville County", "tier": 2,
     "blurb": "Established neighbourhoods with solid houses that mostly want refreshing "
              "rather than rebuilding."},
    {"slug": "mauldin-sc", "name": "Mauldin", "county": "Greenville County", "tier": 2,
     "blurb": "Convenient to both Greenville and Simpsonville. Interior repaints and accent "
              "walls make up most of our work here."},
    {"slug": "duncan-sc", "name": "Duncan", "county": "Spartanburg County", "tier": 3,
     "blurb": "Minutes from our base in Lyman, which usually means we can get out for an "
              "estimate quickly."},
    {"slug": "lyman-sc", "name": "Lyman", "county": "Spartanburg County", "tier": 3,
     "blurb": "Our home town. If you are in Lyman you are as local to us as it gets."},
    {"slug": "boiling-springs-sc", "name": "Boiling Springs", "county": "Spartanburg County", "tier": 3,
     "blurb": "A lot of newer family housing north of Spartanburg — kids' rooms and murals "
              "come up often."},
    {"slug": "travelers-rest-sc", "name": "Travelers Rest", "county": "Greenville County", "tier": 3,
     "blurb": "North of Greenville toward the mountains. Exterior work here takes real sun "
              "exposure into account."},
    {"slug": "inman-sc", "name": "Inman", "county": "Spartanburg County", "tier": 3,
     "blurb": "Northern Spartanburg County, comfortably inside our regular run."},
]

CITY_BY_SLUG = {c["slug"]: c for c in CITIES}

# ---------------------------------------------------------------------------
# 4. REVIEWS
#    ⚠️  DO NOT invent these. Paste real review text from Google or Thumbtack.
#    Until this list has entries, the reviews page shows verified ratings and
#    links out to the platforms instead of quoting anyone.
# ---------------------------------------------------------------------------

REVIEWS = [
    # {"text": "…", "who": "First name L.", "source": "Google", "stars": 5},
]

# ---------------------------------------------------------------------------
# 5. FAQ
# ---------------------------------------------------------------------------

FAQS = [
    ("Do you charge for an estimate?",
     "No. Estimates are free. We come out, look at the actual walls, and give you a written "
     "price. Measuring in person is the only way to quote paper honestly — repeat size and "
     "wall condition change the number more than square footage does."),
    ("How much does wallpaper installation cost?",
     "It depends on the paper and the wall. A large repeat wastes more material, a mural has "
     "to be laid out panel by panel, and a wall that needs skimming first adds a day. That is "
     "why we quote after seeing it rather than over the phone — but the estimate you get is "
     "the price you pay."),
    ("Can you remove wallpaper that was hung straight onto drywall?",
     "Yes, and it is the most common removal we do. If the wall was never primed, the paper "
     "is bonded to the drywall face and some tearing is unavoidable. We steam it off as "
     "cleanly as possible, then patch and skim the damaged areas so you end up with a flat "
     "wall ready for the next finish."),
    ("Do you supply the wallpaper or do I buy it?",
     "Either. Most clients order their own paper from a brand or designer they have chosen — "
     "tell us the product and we will tell you how many rolls to order for your walls, "
     "including the extra the repeat needs. Ordering short mid-job is the one delay that is "
     "genuinely hard to recover from."),
    ("How long will my project take?",
     "A single accent wall is usually a day. A powder room in paper is one to two. A whole "
     "interior repaint runs several days to a week depending on size and how much prep the "
     "walls need. You get a realistic schedule with the estimate, not an optimistic one."),
    ("What areas do you cover?",
     "Greenville, Spartanburg and the surrounding Upstate — including Greer, Simpsonville, "
     "Five Forks, Taylors, Mauldin, Duncan, Lyman, Boiling Springs, Travelers Rest and Inman. "
     "We are based in Lyman, between the two main markets."),
    ("Do you work with designers, builders and property managers?",
     "Yes. Designers are a good part of our wallpaper work, and we handle commercial and "
     "rental turnarounds on a schedule. If you need work done between tenants or before a "
     "listing photo shoot, say so up front and we will plan around the date."),
    ("What languages do you speak?",
     "English, Russian and Ukrainian."),  # TODO: confirm with Roman
]

# ---------------------------------------------------------------------------
# 6. GALLERY
# ---------------------------------------------------------------------------

GALLERY = [
    ("dining-after.jpg", "Dining room — botanical wallpaper over board-and-batten"),
    ("rose-after.jpg", "Bedroom — framed rose mural panel"),
    ("office-after.jpg", "Keller Williams office — geometric feature wall"),
    ("closet-watercolor.jpg", "Walk-in closet — watercolour and gold leaf, wall and ceiling"),
    ("powder-room.jpg", "Powder room — full wrap in patterned paper"),
    ("nursery-after.jpg", "Nursery — full-wall cloud mural"),
    ("dino-mural.jpg", "Kids' room — dinosaur photo mural"),
    ("bath-lemon.jpg", "Bathroom — botanical paper above painted wainscoting"),
    ("accent-wall.jpg", "Bedroom — charcoal accent wall"),
    ("bath-collage.jpg", "Bathrooms — papered ceiling and floral powder room"),
]

# Clean before/after pairs, used for the sliders.
PAIRS = [
    ("dining-before.jpg", "dining-after.jpg", "Dining room, Upstate SC",
     "Board-and-batten panelling installed, then dark botanical paper hung above it."),
    ("rose-before.jpg", "rose-after.jpg", "Bedroom feature panel",
     "An empty molding surround turned into a framed rose mural, seams cut tight to the frame."),
    ("office-before.jpg", "office-after.jpg", "Keller Williams office, Upstate SC",
     "Damaged drywall repaired and papered in a geometric print, cut in around the window and "
     "TV mount."),
    ("nursery-before.jpg", "nursery-after.jpg", "Nursery",
     "A plain wall replaced with a full-height cloud mural."),
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def e(s):
    return html.escape(str(s), quote=True)


def claim_list():
    """Promises we can make today. Verified ones only."""
    items = [
        "Free, written estimates",
        "The price we quote is the price you pay",
        "Floors, furniture and fixtures covered and protected",
        "Surfaces prepped properly before any finish goes on",
        "No bubbles, no lifted seams, no visible joins",
        "Full cleanup when we are done",
        "We turn up when we said we would",
        "Locally owned and operated, based in Lyman, SC",
    ]
    if CLAIMS["insured"]:
        items.insert(3, "Fully insured")
    if CLAIMS["licensed"]:
        items.insert(3, "Licensed in South Carolina")
    if CLAIMS["warranty"]:
        items.insert(2, CLAIMS["warranty"])
    return items


def stat_tiles():
    """Only numbers we can actually stand behind."""
    tiles = [
        (PROOF["google_rating"] + "★", "Google rating (%d reviews)" % PROOF["google_count"]),
        (PROOF["thumbtack_rating"] + "★", "Thumbtack rating (%d reviews)" % PROOF["thumbtack_count"]),
        (str(PROOF["total_reviews"]) + "+", "Five-star reviews in total"),
    ]
    if CLAIMS["years"]:
        tiles.append((str(CLAIMS["years"]) + "+", "Years in business"))
    else:
        tiles.append(("12", "Upstate towns covered"))
    return tiles


def nav_html(active):
    svc = "".join(
        '<a href="/%s/"%s>%s</a>' % (
            s, ' aria-current="page"' if active == s else "", e(SERVICE_BY_SLUG[s]["nav"]))
        for s in NAV_SERVICES
    )
    areas = "".join(
        '<a href="/%s/"%s>%s</a>' % (
            c["slug"], ' aria-current="page"' if active == c["slug"] else "", e(c["name"]))
        for c in CITIES
    )

    def link(href, slug, label):
        cur = ' aria-current="page"' if active == slug else ""
        return '<li><a href="%s"%s>%s</a></li>' % (href, cur, label)

    return """<nav class="nav" id="nav">
      <ul>
        %s
        <li class="nav__has" data-open="false">
          <button type="button" aria-haspopup="true">Services</button>
          <div class="nav__drop">%s</div>
        </li>
        <li class="nav__has" data-open="false">
          <button type="button" aria-haspopup="true">Areas</button>
          <div class="nav__drop">%s</div>
        </li>
        %s
        %s
        %s
      </ul>
    </nav>""" % (
        link("/", "home", "Home"), svc, areas,
        link("/gallery/", "gallery", "Gallery"),
        link("/reviews/", "reviews", "Reviews"),
        link("/about/", "about", "About"),
    )


def schema_localbusiness():
    addr = {
        "@type": "PostalAddress",
        "addressLocality": BIZ["city"],
        "addressRegion": BIZ["state"],
        "postalCode": BIZ["zip"],
        "addressCountry": "US",
    }
    if SHOW_STREET:
        addr["streetAddress"] = BIZ["street"]

    parts = [
        '"@context":"https://schema.org"',
        '"@type":"PaintingContractor"',
        '"@id":"%s#business"' % SITE_URL,
        '"name":"%s"' % BIZ["name"],
        '"url":"%s/"' % SITE_URL,
        '"telephone":"%s"' % BIZ["phone"],
        '"email":"%s"' % BIZ["email"],
        '"image":"%s/assets/img/logo.png"' % SITE_URL,
        '"logo":"%s/assets/img/logo.png"' % SITE_URL,
        '"priceRange":"$$"',
        '"founder":{"@type":"Person","name":"%s"}' % BIZ["owner"],
        '"address":%s' % _json(addr),
        '"areaServed":[%s]' % ",".join(
            '{"@type":"City","name":"%s, SC"}' % c["name"] for c in CITIES),
        '"aggregateRating":{"@type":"AggregateRating","ratingValue":"4.9",'
        '"reviewCount":"%d","bestRating":"5"}' % PROOF["total_reviews"],
        '"openingHoursSpecification":{"@type":"OpeningHoursSpecification",'
        '"dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],'
        '"opens":"00:00","closes":"23:59"}',
    ]
    sameas = [u for u in (BIZ["facebook_url"], BIZ["instagram_url"], BIZ["thumbtack_url"]) if u]
    if sameas:
        parts.append('"sameAs":[%s]' % ",".join('"%s"' % u for u in sameas))
    return "{" + ",".join(parts) + "}"


def _json(d):
    """Tiny JSON writer for the flat dicts used in schema."""
    inner = ",".join('"%s":"%s"' % (k, v) for k, v in d.items())
    return "{" + inner + "}"


def layout(*, slug, title, desc, body, path, extra_schema="", hero=None):
    """Wrap page body in the shared shell."""
    canonical = SITE_URL + path
    schema = schema_localbusiness()
    if extra_schema:
        schema = '[%s,%s]' % (schema, extra_schema)

    svc_links = "".join(
        '<li><a href="/%s/">%s</a></li>' % (s["slug"], e(s["nav"])) for s in SERVICES)
    city_links = "".join(
        '<li><a href="/%s/">%s, SC</a></li>' % (c["slug"], e(c["name"])) for c in CITIES[:8])

    social = []
    if BIZ["facebook_url"]:
        social.append('<a href="%s" rel="noopener">Facebook</a>' % BIZ["facebook_url"])
    if BIZ["instagram_url"]:
        social.append('<a href="%s" rel="noopener">Instagram</a>' % BIZ["instagram_url"])
    if BIZ["thumbtack_url"]:
        social.append('<a href="%s" rel="noopener">Thumbtack</a>' % BIZ["thumbtack_url"])

    addr_line = "%s, %s %s" % (BIZ["city"], BIZ["state"], BIZ["zip"])
    if SHOW_STREET:
        addr_line = BIZ["street"] + ", " + addr_line

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
%(robots)s<link rel="canonical" href="%(canonical)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(site)s/assets/img/dining-after.jpg">
<meta property="og:site_name" content="%(name)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2b2b2b">
<link rel="icon" href="/assets/img/logo.png">
<link rel="apple-touch-icon" href="/assets/img/logo.png">
<link rel="stylesheet" href="/assets/css/style.css">
<script type="application/ld+json">%(schema)s</script>
</head>
<body>

<div class="utilbar">
  <a class="utilbar__est" href="/contact/">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
    Free Estimate
  </a>
  <a class="utilbar__call" href="%(tel)s">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2 4.2 2 2 0 0 1 4 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.8 2z"/></svg>
    %(phone)s
  </a>
</div>

<header class="header">
  <div class="wrap header__inner">
    <a class="logo" href="/"><img src="/assets/img/logo.png" alt="%(name)s" width="210" height="54"></a>
    %(nav)s
    <div class="header__cta">
      <a class="header__phone" href="%(tel)s">%(phone)s</a>
      <a class="btn btn--primary" href="/contact/">Free Estimate</a>
      <button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="nav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>

%(hero)s
%(body)s

<section class="cta-band">
  <div class="wrap">
    <h2>Ready for a free estimate?</h2>
    <p>Tell us about the room. We will come out, look at the actual walls, and give you a
       written price — no charge and no pressure.</p>
    <div class="btn-row">
      <a class="btn btn--dark" href="%(tel)s">Call %(phone)s</a>
      <a class="btn btn--ghost" href="/contact/">Request an estimate</a>
    </div>
  </div>
</section>

<footer class="footer">
  <div class="wrap">
    <div class="footer__grid">
      <div>
        <img class="footer__logo" src="/assets/img/logo.png" alt="%(name)s" width="200" height="52">
        <p>Painting and wallpaper for Greenville, Spartanburg and the surrounding Upstate.
           Locally owned and operated.</p>
        <p><strong style="color:#fff">%(rating)s★</strong> average from %(total)d reviews
           across Google and Thumbtack.</p>
      </div>
      <div>
        <h4>Services</h4>
        <ul>%(svc_links)s</ul>
      </div>
      <div>
        <h4>Areas served</h4>
        <ul>%(city_links)s<li><a href="/#areas">All areas</a></li></ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="%(tel)s">%(phone)s</a></li>
          <li><a href="mailto:%(email)s">%(email)s</a></li>
          <li>%(addr)s</li>
          <li>%(hours)s</li>
          %(social)s
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <div>© %(year)s %(name)s. All rights reserved.</div>
      <div><a href="/privacy/">Privacy</a> &nbsp;·&nbsp; <a href="/contact/">Contact</a></div>
    </div>
  </div>
</footer>

<div class="mobile-bar">
  <a class="m-call" href="%(tel)s">Call now</a>
  <a class="m-quote" href="/contact/">Free estimate</a>
</div>

<script src="/assets/js/main.js" defer></script>
</body>
</html>
""" % {
        "title": e(title), "desc": e(desc), "canonical": canonical, "site": SITE_URL,
        "robots": '<meta name="robots" content="noindex,nofollow">\n' if PREVIEW else "",
        "name": e(BIZ["name"]), "schema": schema, "nav": nav_html(slug),
        "tel": PHONE_HREF, "phone": e(BIZ["phone"]), "email": e(BIZ["email"]),
        "addr": e(addr_line), "hours": e(BIZ["hours"]),
        "hero": hero or "", "body": body,
        "svc_links": svc_links, "city_links": city_links,
        "social": "".join("<li>%s</li>" % s for s in social),
        "rating": "4.9", "total": PROOF["total_reviews"],
        "year": date.today().year,
    }


def ba_block(before, after, label=""):
    return """<div class="ba">
      <img class="ba__before" src="/assets/img/%s" alt="Before — %s" loading="lazy" width="1200" height="900">
      <img class="ba__after" src="/assets/img/%s" alt="After — %s" loading="lazy" width="1200" height="900">
      <span class="ba__tag ba__tag--before">Before</span>
      <span class="ba__tag ba__tag--after">After</span>
      <span class="ba__handle" aria-hidden="true"></span>
      <input class="ba__range" type="range" min="0" max="100" value="50"
             aria-label="Drag to compare before and after">
    </div>""" % (before, e(label), after, e(label))


def rating_items():
    return """<ul class="hero__rating">
      <li><span class="stars">★★★★★</span> %s Google <span>(%d reviews)</span></li>
      <li><span class="stars">★★★★★</span> %s Thumbtack <span>(%d reviews)</span></li>
      <li>Locally owned <span>· Lyman, SC</span></li>
    </ul>""" % (PROOF["google_rating"], PROOF["google_count"],
                PROOF["thumbtack_rating"], PROOF["thumbtack_count"])


def trust_strip():
    tiles = "".join(
        '<div><div class="trust__n">%s</div><div class="trust__l">%s</div></div>' % (e(n), e(l))
        for n, l in stat_tiles())
    return '<section class="trust"><div class="wrap"><div class="trust__grid">%s</div></div></section>' % tiles


def faq_block(faqs):
    items = "".join(
        "<details><summary>%s</summary><div><p>%s</p></div></details>" % (e(q), e(a))
        for q, a in faqs)
    return '<div class="faq">%s</div>' % items


def faq_schema(faqs):
    qs = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (_jstr(q), _jstr(a)) for q, a in faqs)
    return '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}' % qs


def _jstr(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def areas_list(dark=False):
    links = "".join('<li><a href="/%s/">%s, SC</a></li>' % (c["slug"], e(c["name"]))
                    for c in CITIES)
    return '<ul class="areas">%s</ul>' % links


ROLLER_ICON = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<rect x="2" y="3" width="14" height="6" rx="1.5"/>'
    '<path d="M16 6h4a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-8"/>'
    '<rect x="9.5" y="14" width="5" height="7" rx="1.5"/>'
    '<path d="M12 11v3"/></svg>')


def service_card(s, city=None):
    """One service card. Services with no representative photo of their own get a
    graphite panel instead of somebody else's photo."""
    title = "%s in %s" % (s["nav"], city) if city else s["nav"]
    if s.get("img"):
        pos = s.get("card_pos")
        style = ' style="object-position:%s"' % pos if pos else ""
        media = ('<img src="/assets/img/%s" alt="%s" loading="lazy" '
                 'width="800" height="600"%s>' % (s["img"], e(s["alt"]), style))
    else:
        media = '<div class="card__block">%s</div>' % ROLLER_ICON
    return """<article class="card">%s
      <div class="card__body">
        <h3>%s</h3>
        <p>%s</p>
        <a class="card__link" href="/%s/">Learn more →</a>
      </div>
    </article>""" % (media, e(title), e(s["card"]), s["slug"])


def rebase(content, depth):
    """Rewrite absolute internal links for a preview build.

    depth is how many folders deep the page sits, so a page at /about/ can
    reach the stylesheet at ../assets/css/style.css when the site is opened
    straight off disk.
    """
    if not PREVIEW:
        return content
    prefix = ("../" * depth or "./") if BASE_PATH == "." else BASE_PATH + "/"

    def sub(m):
        attr, rest = m.group(1), m.group(2)
        # a bare href="/" is the home page
        if rest == "":
            return '%s="%s"' % (attr, prefix + ("index.html" if BASE_PATH == "." else ""))
        if BASE_PATH == "." and rest.endswith("/"):
            rest += "index.html"
        return '%s="%s"' % (attr, prefix + rest)

    return re.sub(r'\b(href|src)="/([^"]*)"', sub, content)


def write(path, content):
    full = os.path.join(OUT, path.lstrip("/"))
    depth = path.strip("/").count("/")
    content = rebase(content, depth)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------

def page_home():
    hero = """<section class="hero">
      <div class="wrap hero__grid">
        <div>
          <p class="eyebrow">Painting &amp; wallpaper · Greenville &amp; Spartanburg</p>
          <h1>House painting and wallpaper across Greenville &amp; Spartanburg</h1>
          <p class="hero__sub">Interiors, exteriors, cabinets and trim — and the wallpaper work
             most painting companies in the Upstate quietly pass on. Both trades, one crew.
             %d five-star reviews across Google and Thumbtack.</p>
          %s
          <div class="btn-row">
            <a class="btn btn--primary" href="/contact/">Get a free estimate</a>
            <a class="btn btn--ghost" href="%s">Call %s</a>
          </div>
        </div>
        <div>%s</div>
      </div>
    </section>""" % (PROOF["total_reviews"], rating_items(), PHONE_HREF, e(BIZ["phone"]),
                     ba_block("dining-before.jpg", "dining-after.jpg", "dining room wallpaper"))

    # Alternating so neither trade reads as the afterthought.
    lead_services = ["interior-painting", "wallpaper-installation", "exterior-painting",
                     "wallpaper-removal", "cabinet-painting", "commercial-painting"]
    cards = "".join(service_card(SERVICE_BY_SLUG[slug]) for slug in lead_services)

    promises = "".join("<li>%s</li>" % e(p) for p in claim_list())

    pairs = ""
    for before, after, title, note in PAIRS[1:4]:
        pairs += """<div>
          %s
          <h3 style="margin-top:16px">%s</h3>
          <p style="color:var(--muted);font-size:.96rem">%s</p>
        </div>""" % (ba_block(before, after, title), e(title), e(note))

    body = """
%(trust)s

<section class="section">
  <div class="wrap">
    <div class="feature feature--flip">
      <div class="feature__media">
        <img src="/assets/img/accent-wall.jpg" alt="Bedroom accent wall before and after, repainted in deep charcoal" loading="lazy" width="1000" height="750">
      </div>
      <div>
        <p class="eyebrow">Painting</p>
        <h2>The finish is decided in the hour before the paint</h2>
        <p>Nail pops and cracks filled, split caulk lines cut out and replaced, glossy and
           patched areas spot-primed so nothing flashes through the topcoat. Walls, ceilings,
           trim, doors, cabinets and exteriors — a room at a time or the whole house.</p>
        <p>Floors covered, furniture moved and wrapped, edges cut by hand, and the room
           cleaned up at the end of each day rather than staged for tomorrow. That matters
           when it is a room you still have to live in.</p>
        <div class="btn-row">
          <a class="btn btn--primary" href="/interior-painting/">Painting services</a>
          <a class="btn btn--outline" href="/contact/">Get a free estimate</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="feature">
      <div class="feature__media">
        <img src="/assets/img/closet-watercolor.jpg" alt="Watercolour and gold-leaf wallpaper on a closet wall and ceiling" loading="lazy" width="1000" height="750">
      </div>
      <div>
        <p class="eyebrow">Wallpaper</p>
        <h2>Wallpaper is a different trade — we treat it like one</h2>
        <p>Hanging paper well is not painting with extra steps. The repeat has to be planned
           before the first drop goes up, the wall has to be flat and primed, and every seam
           has to land tight enough that you cannot find it afterwards.</p>
        <p>It is the part of the job most painting companies in Greenville and Spartanburg
           quietly decline. It is the part we are known for — murals, designer paper,
           grasscloth, ceilings and the awkward little powder rooms nobody else wants.</p>
        <div class="btn-row">
          <a class="btn btn--primary" href="/wallpaper-installation/">Wallpaper services</a>
          <a class="btn btn--outline" href="/gallery/">See the work</a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--paper">
  <div class="wrap">
    <div class="center" style="margin-bottom:44px">
      <p class="eyebrow">Our services</p>
      <h2>Painting and wallpaper, done properly</h2>
      <p class="lead">Interiors, exteriors, commercial spaces and everything that gets
         prepped before the finish goes on.</p>
    </div>
    <div class="grid grid--3">%(cards)s</div>
    <div class="center" style="margin-top:36px">
      <a class="btn btn--outline" href="/gallery/">View the full gallery</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="center" style="margin-bottom:44px">
      <p class="eyebrow">Before &amp; after</p>
      <h2>Drag the slider</h2>
      <p class="lead">Real rooms in the Upstate. Drag each image to see what changed.</p>
    </div>
    <div class="grid grid--3">%(pairs)s</div>
  </div>
</section>

<section class="section section--ink">
  <div class="wrap">
    <div class="feature">
      <div>
        <p class="eyebrow">Why ProMan</p>
        <h2>Locally owned, and the reviews are the proof</h2>
        <p class="lead">%(total)d five-star reviews across Google and Thumbtack, with an
           %(gr)s on Google and %(tr)s on Thumbtack — earned one room at a time, in the
           Upstate, by the person who shows up to do the work.</p>
        <ul class="checks checks--2">%(promises)s</ul>
        <div class="btn-row">
          <a class="btn btn--primary" href="/contact/">Get a free estimate</a>
          <a class="btn btn--ghost" href="/reviews/">Read the reviews</a>
        </div>
      </div>
      <div class="feature__media">
        %(office)s
      </div>
    </div>
  </div>
</section>

<section class="section section--paper" id="areas">
  <div class="wrap">
    <div class="center" style="margin-bottom:36px">
      <p class="eyebrow">Service area</p>
      <h2>Serving Greenville, Spartanburg &amp; the Upstate</h2>
      <p class="lead">Based in Lyman, between both markets — which usually means we can get out
         to look at your walls quickly.</p>
    </div>
    %(areas)s
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="center" style="margin-bottom:30px">
      <p class="eyebrow">Questions</p>
      <h2>Frequently asked</h2>
    </div>
    <div style="max-width:820px;margin-inline:auto">%(faq)s</div>
  </div>
</section>
""" % {
        "trust": trust_strip(), "cards": cards, "pairs": pairs,
        "promises": promises, "areas": areas_list(dark=True), "faq": faq_block(FAQS),
        "total": PROOF["total_reviews"], "gr": PROOF["google_rating"],
        "tr": PROOF["thumbtack_rating"],
        "office": ba_block("office-before.jpg", "office-after.jpg", "commercial office"),
    }

    return layout(
        slug="home",
        title="Painters & Wallpaper Installers in Greenville, SC | %s" % BIZ["name"],
        desc="Wallpaper installation, removal and house painting across Greenville, Spartanburg "
             "and the Upstate. %d five-star reviews. Locally owned. Free estimates."
             % PROOF["total_reviews"],
        path="/", body=body, hero=hero, extra_schema=faq_schema(FAQS))


def page_service(s):
    hero_img = ('<div class="feature__media"><img src="/assets/img/%s" alt="%s" width="1000" height="750"></div>'
                % (s["img"], e(s["alt"]))) if s["img"] else ""

    sections = "".join(
        "<h2>%s</h2><p>%s</p>" % (e(h), e(p)) for h, p in s["body"])
    bullets = "".join("<li>%s</li>" % e(b) for b in s["bullets"])

    others = "".join(
        '<li><a href="/%s/">%s</a></li>' % (o["slug"], e(o["nav"]))
        for o in SERVICES if o["slug"] != s["slug"])

    head = """<section class="pagehead">
      <div class="wrap">
        <p class="crumbs"><a href="/">Home</a> › %s</p>
        <h1>%s</h1>
        <p>%s</p>
        <div class="btn-row" style="margin-top:26px">
          <a class="btn btn--primary" href="/contact/">Free estimate</a>
          <a class="btn btn--ghost" href="%s">Call %s</a>
        </div>
      </div>
    </section>""" % (e(s["nav"]), e(s["h1"]), e(s["intro"]), PHONE_HREF, e(BIZ["phone"]))

    body = """
%(trust)s
<section class="section">
  <div class="wrap">
    <div class="feature feature--top">
      <div class="prose">%(sections)s</div>
      %(img)s
    </div>
  </div>
</section>

<section class="section section--paper">
  <div class="wrap">
    <div class="feature">
      <div>
        <p class="eyebrow">What's included</p>
        <h2>Every %(nav)s job</h2>
        <ul class="checks">%(bullets)s</ul>
        <a class="btn btn--primary" href="/contact/">Get a free estimate</a>
      </div>
      <div>
        <h3>Other services</h3>
        <ul class="areas" style="margin-top:14px">%(others)s</ul>
        <h3 style="margin-top:32px">Where we work</h3>
        %(areas)s
      </div>
    </div>
  </div>
</section>
""" % {"trust": trust_strip(), "sections": sections, "img": hero_img,
       "nav": e(s["nav"].lower()), "bullets": bullets, "others": others,
       "areas": areas_list()}

    svc_schema = (
        '{"@context":"https://schema.org","@type":"Service","name":%s,'
        '"serviceType":%s,"provider":{"@id":"%s#business"},'
        '"areaServed":[%s],"description":%s}'
        % (_jstr(s["nav"]), _jstr(s["nav"]), SITE_URL,
           ",".join('{"@type":"City","name":"%s, SC"}' % c["name"] for c in CITIES),
           _jstr(s["desc"])))

    return layout(slug=s["slug"], title=s["title"], desc=s["desc"],
                  path="/%s/" % s["slug"], body=body, hero=head, extra_schema=svc_schema)


def page_city(c):
    top = ["wallpaper-installation", "interior-painting", "wallpaper-removal",
           "cabinet-painting", "exterior-painting", "commercial-painting"]
    cards = "".join(service_card(SERVICE_BY_SLUG[slug], city=c["name"]) for slug in top)

    near = [x for x in CITIES if x["slug"] != c["slug"]][:8]
    near_links = "".join('<li><a href="/%s/">%s, SC</a></li>' % (n["slug"], e(n["name"]))
                         for n in near)

    head = """<section class="pagehead">
      <div class="wrap">
        <p class="crumbs"><a href="/">Home</a> › %s, SC</p>
        <h1>Painters &amp; Wallpaper Installers in %s, SC</h1>
        <p>%s</p>
        <div class="btn-row" style="margin-top:26px">
          <a class="btn btn--primary" href="/contact/">Free estimate</a>
          <a class="btn btn--ghost" href="%s">Call %s</a>
        </div>
      </div>
    </section>""" % (e(c["name"]), e(c["name"]), e(c["blurb"]), PHONE_HREF, e(BIZ["phone"]))

    body = """
%(trust)s
<section class="section">
  <div class="wrap">
    <div class="feature">
      <div class="prose">
        <h2>Your local painting and wallpaper company in %(city)s</h2>
        <p>%(name)s is based in Lyman, %(county_note)s We cover %(city)s and the surrounding
           Upstate for wallpaper installation and removal, interior and exterior painting,
           cabinets, trim and commercial work.</p>
        <p>Wallpaper is the part we are best known for. If you have been told by another
           company in %(city)s that they only do paint, that is the gap we fill — murals,
           designer paper, grasscloth, papered ceilings and the small powder rooms that take
           more patience than square footage.</p>
        <p>%(blurb)s</p>
        <h2>Free estimates in %(city)s</h2>
        <p>We come out, look at the actual walls, and give you a written price. Wall condition
           and pattern repeat move the number more than square footage does, so quoting over
           the phone would mean guessing. The estimate is free and the price we quote is the
           price you pay.</p>
      </div>
      <div class="feature__media">%(ba)s</div>
    </div>
  </div>
</section>

<section class="section section--paper">
  <div class="wrap">
    <div class="center" style="margin-bottom:40px">
      <p class="eyebrow">%(city)s, SC</p>
      <h2>What we do here</h2>
    </div>
    <div class="grid grid--3">%(cards)s</div>
  </div>
</section>

<section class="section">
  <div class="wrap center">
    <h2>Nearby areas we serve</h2>
    <ul class="areas" style="justify-content:center;margin-top:22px">%(near)s</ul>
  </div>
</section>
""" % {"trust": trust_strip(), "city": e(c["name"]), "name": e(BIZ["name"]),
       "county_note": "which puts %s comfortably inside our regular run." % e(c["name"]),
       "blurb": e(c["blurb"]), "cards": cards, "near": near_links,
       "ba": ba_block("rose-before.jpg", "rose-after.jpg", "wallpaper feature panel")}

    return layout(
        slug=c["slug"],
        title="Painters in %s, SC | Wallpaper & Painting | %s" % (c["name"], BIZ["short"]),
        desc="Wallpaper installation, removal and house painting in %s, SC. %d five-star "
             "reviews, locally owned, free estimates." % (c["name"], PROOF["total_reviews"]),
        path="/%s/" % c["slug"], body=body, hero=head)


def page_gallery():
    figs = "".join(
        '<figure><img src="/assets/img/%s" alt="%s" loading="lazy" width="800" height="800">'
        '<figcaption>%s</figcaption></figure>' % (f, e(cap), e(cap))
        for f, cap in GALLERY)

    pairs = ""
    for before, after, title, note in PAIRS:
        pairs += """<div>
          %s
          <h3 style="margin-top:16px">%s</h3>
          <p style="color:var(--muted);font-size:.96rem">%s</p>
        </div>""" % (ba_block(before, after, title), e(title), e(note))

    head = """<section class="pagehead">
      <div class="wrap">
        <p class="crumbs"><a href="/">Home</a> › Gallery</p>
        <h1>Our work</h1>
        <p>Real rooms in Greenville, Spartanburg and the surrounding Upstate — photographed
           on the job, not staged.</p>
      </div>
    </section>"""

    body = """
<section class="section">
  <div class="wrap">
    <div class="center" style="margin-bottom:44px">
      <p class="eyebrow">Before &amp; after</p>
      <h2>Drag to compare</h2>
    </div>
    <div class="grid grid--2">%s</div>
  </div>
</section>

<section class="section section--paper">
  <div class="wrap">
    <div class="center" style="margin-bottom:40px">
      <p class="eyebrow">Portfolio</p>
      <h2>Recent projects</h2>
    </div>
    <div class="gallery">%s</div>
  </div>
</section>
""" % (pairs, figs)

    return layout(slug="gallery",
                  title="Gallery — Wallpaper & Painting Projects | %s" % BIZ["name"],
                  desc="Before and after photos of wallpaper installation, murals and painting "
                       "projects across Greenville, Spartanburg and the Upstate.",
                  path="/gallery/", body=body, hero=head)


def page_reviews():
    if REVIEWS:
        cards = "".join(
            '<div class="review"><div class="stars">%s</div><p>“%s”</p>'
            '<div class="review__who">%s</div>'
            '<div class="review__src">via %s</div></div>'
            % ("★" * r.get("stars", 5), e(r["text"]), e(r["who"]), e(r["source"]))
            for r in REVIEWS)
        quotes = '<div class="grid grid--3">%s</div>' % cards
    else:
        # No invented testimonials. Ratings are verified; the words are not ours to write.
        quotes = """<div class="review-cta">
          <div>
            <h3 style="margin-bottom:.3em">Read what customers actually wrote</h3>
            <p style="margin:0;color:var(--muted)">Every review lives on Google and Thumbtack,
               where you can read it in full and check it is real.</p>
          </div>
          <div class="btn-row" style="flex:0 0 auto">
            <a class="btn btn--primary" href="%s" rel="noopener">Google reviews</a>
            <a class="btn btn--outline" href="%s" rel="noopener">Thumbtack reviews</a>
          </div>
        </div>""" % (BIZ["gbp_url"], BIZ["thumbtack_url"])

    head = """<section class="pagehead">
      <div class="wrap">
        <p class="crumbs"><a href="/">Home</a> › Reviews</p>
        <h1>Reviews</h1>
        <p>%d five-star reviews across Google and Thumbtack — %s on Google, %s on Thumbtack.</p>
      </div>
    </section>""" % (PROOF["total_reviews"], PROOF["google_rating"], PROOF["thumbtack_rating"])

    body = """
%(trust)s
<section class="section">
  <div class="wrap">%(quotes)s</div>
</section>

<section class="section section--paper">
  <div class="wrap center">
    <p class="eyebrow">Worked with us?</p>
    <h2>A review helps more than you would think</h2>
    <p class="lead">We are a small local company. Reviews are how people in the Upstate find us
       — and how they decide whether to trust us with their walls.</p>
    <div class="btn-row" style="justify-content:center;margin-top:24px">
      <a class="btn btn--primary" href="%(review_url)s" rel="noopener">Leave a Google review</a>
    </div>
  </div>
</section>
""" % {"trust": trust_strip(), "quotes": quotes, "review_url": BIZ["gbp_review_url"]}

    return layout(slug="reviews",
                  title="Reviews | %s" % BIZ["name"],
                  desc="%d five-star reviews across Google and Thumbtack for wallpaper and "
                       "painting work in Greenville and Spartanburg, SC."
                       % PROOF["total_reviews"],
                  path="/reviews/", body=body, hero=head)


def page_about():
    head = """<section class="pagehead">
      <div class="wrap">
        <p class="crumbs"><a href="/">Home</a> › About</p>
        <h1>About %s</h1>
        <p>A locally owned painting and wallpaper company based in Lyman, South Carolina —
           between Greenville and Spartanburg.</p>
      </div>
    </section>""" % e(BIZ["name"])

    promises = "".join("<li>%s</li>" % e(p) for p in claim_list())

    body = """
%(trust)s
<section class="section">
  <div class="wrap">
    <div class="feature">
      <div class="prose">
        <h2>Who we are</h2>
        <p>%(name)s is run by %(owner)s out of Lyman, South Carolina. Lyman sits almost exactly
           between Greenville and Spartanburg, which is the practical reason we can serve both
           markets properly instead of treating one of them as the long drive.</p>
        <p>The work is split between wallpaper and painting, and wallpaper is where we have
           built the reputation. Murals, designer and boutique papers, grasscloth, papered
           ceilings, feature panels and the small awkward rooms — the jobs that need patience
           and a planned layout rather than speed.</p>

        <h2>How we work</h2>
        <p>We come out and look at the actual walls before quoting. We tell you what the prep
           actually requires, even when that makes the number bigger, because paper and paint
           both fail from the surface underneath rather than from the finish on top.</p>
        <p>Then we protect the floors and the furniture, do the prep properly, and clean up
           after ourselves. None of that is remarkable. It is just consistently doing the
           things that get skipped.</p>

        <h2>The reviews</h2>
        <p>%(total)d five-star reviews so far — %(gr)s on Google across %(gc)d reviews, and
           %(tr)s on Thumbtack across %(tc)d, where we hold their “Excellent” rating. Every one
           of them came from a room in the Upstate.</p>
      </div>
      <div class="feature__media">
        <img src="/assets/img/powder-room.jpg" alt="Powder room fully wrapped in patterned wallpaper" loading="lazy" width="1000" height="750">
      </div>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="wrap">
    <div class="center" style="margin-bottom:40px">
      <p class="eyebrow">What you get</p>
      <h2>Every job, every time</h2>
    </div>
    <ul class="checks checks--2" style="max-width:840px;margin-inline:auto">%(promises)s</ul>
  </div>
</section>
""" % {"trust": trust_strip(), "name": e(BIZ["name"]), "owner": e(BIZ["owner"]),
       "total": PROOF["total_reviews"], "gr": PROOF["google_rating"],
       "gc": PROOF["google_count"], "tr": PROOF["thumbtack_rating"],
       "tc": PROOF["thumbtack_count"], "promises": promises}

    return layout(slug="about", title="About | %s" % BIZ["name"],
                  desc="Locally owned painting and wallpaper company based in Lyman, SC, "
                       "serving Greenville, Spartanburg and the Upstate.",
                  path="/about/", body=body, hero=head)


def page_contact():
    svc_opts = "".join('<option>%s</option>' % e(s["nav"]) for s in SERVICES)
    city_opts = "".join('<option>%s</option>' % e(c["name"]) for c in CITIES)

    if FORM_ENDPOINT:
        form_attrs = 'action="%s" method="POST"' % FORM_ENDPOINT
        note = ("We usually reply the same day. If it is urgent, calling is faster.")
    else:
        # No form backend configured yet — fall back to the mail client so the
        # form still does something rather than silently failing.
        form_attrs = 'action="mailto:%s" method="POST" enctype="text/plain"' % BIZ["email"]
        note = ("This form currently opens your email app. Calling is faster — "
                "or email us directly at %s." % BIZ["email"])

    head = """<section class="pagehead">
      <div class="wrap">
        <p class="crumbs"><a href="/">Home</a> › Contact</p>
        <h1>Get a free estimate</h1>
        <p>Tell us about the room and we will come out, look at the walls, and give you a
           written price. No charge, no pressure.</p>
      </div>
    </section>"""

    body = """
<section class="section">
  <div class="wrap">
    <div class="feature">
      <div>
        <h2>Request an estimate</h2>
        <form class="form" %(attrs)s>
          <div class="form__row">
            <label>Name
              <input type="text" name="name" required autocomplete="name">
            </label>
            <label>Phone
              <input type="tel" name="phone" required autocomplete="tel">
            </label>
          </div>
          <label>Email
            <input type="email" name="email" autocomplete="email">
          </label>
          <div class="form__row">
            <label>Service
              <select name="service">%(svc)s<option>Something else</option></select>
            </label>
            <label>Town
              <select name="city">%(cities)s<option>Elsewhere in the Upstate</option></select>
            </label>
          </div>
          <label>Tell us about the project
            <textarea name="message" placeholder="Which rooms, roughly what size, and what you have in mind. If you already have a wallpaper picked out, tell us which one."></textarea>
          </label>
          <button class="btn btn--primary" type="submit">Request my free estimate</button>
          <p class="form__note">%(note)s</p>
        </form>
      </div>
      <div>
        <h2>Or just call</h2>
        <p class="lead">Fastest way to get on the schedule.</p>
        <p style="font-size:1.9rem;font-weight:900;margin:.2em 0">
          <a href="%(tel)s" style="color:var(--ink);text-decoration:none">%(phone)s</a>
        </p>
        <ul class="checks" style="margin-top:26px">
          <li>Free written estimates</li>
          <li>Serving Greenville, Spartanburg &amp; the Upstate</li>
          <li>%(hours)s</li>
          <li>Based in %(city)s, %(state)s %(zip)s</li>
        </ul>
        <h3 style="margin-top:32px">Find us online</h3>
        <ul class="areas" style="margin-top:14px">
          <li><a href="%(gbp)s" rel="noopener">Google</a></li>
          <li><a href="%(tt)s" rel="noopener">Thumbtack</a></li>
          <li><a href="%(fb)s" rel="noopener">Facebook</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>
""" % {"attrs": form_attrs, "svc": svc_opts, "cities": city_opts, "note": e(note),
       "tel": PHONE_HREF, "phone": e(BIZ["phone"]), "hours": e(BIZ["hours"]),
       "city": e(BIZ["city"]), "state": e(BIZ["state"]), "zip": e(BIZ["zip"]),
       "gbp": BIZ["gbp_url"], "tt": BIZ["thumbtack_url"], "fb": BIZ["facebook_url"]}

    return layout(slug="contact", title="Contact & Free Estimate | %s" % BIZ["name"],
                  desc="Request a free painting or wallpaper estimate in Greenville, "
                       "Spartanburg and the Upstate. Call %s." % BIZ["phone"],
                  path="/contact/", body=body, hero=head)


def page_privacy():
    head = """<section class="pagehead"><div class="wrap">
      <p class="crumbs"><a href="/">Home</a> › Privacy</p>
      <h1>Privacy policy</h1></div></section>"""
    body = """
<section class="section">
  <div class="wrap prose">
    <p><em>Last updated %(date)s</em></p>

    <h2>What we collect</h2>
    <p>If you fill in the estimate form we receive the name, phone number, email address, town
       and project details you enter. That is all we collect, and only because you sent it.</p>

    <h2>What we do with it</h2>
    <p>We use it to reply to you, quote your project and schedule the work. We do not sell it,
       rent it, or share it with anyone outside %(name)s except where we need a supplier to
       quote a material for your job.</p>

    <h2>How long we keep it</h2>
    <p>Enquiries that do not become jobs are deleted within two years. Records of completed
       work are kept for as long as we need them for warranty and accounting purposes.</p>

    <h2>Cookies and analytics</h2>
    <p>This site sets no advertising or tracking cookies and does not profile visitors.</p>

    <h2>Your choices</h2>
    <p>Email <a href="mailto:%(email)s">%(email)s</a> and we will tell you what we hold about
       you, correct it, or delete it.</p>

    <h2>Contact</h2>
    <p>%(name)s<br>%(city)s, %(state)s %(zip)s<br>
       <a href="%(tel)s">%(phone)s</a><br>
       <a href="mailto:%(email)s">%(email)s</a></p>
  </div>
</section>
""" % {"date": TODAY, "name": e(BIZ["name"]), "email": e(BIZ["email"]),
       "city": e(BIZ["city"]), "state": e(BIZ["state"]), "zip": e(BIZ["zip"]),
       "tel": PHONE_HREF, "phone": e(BIZ["phone"])}

    return layout(slug="privacy", title="Privacy Policy | %s" % BIZ["name"],
                  desc="How %s handles the information you send through this website."
                       % BIZ["name"],
                  path="/privacy/", body=body, hero=head)


def page_404():
    body = """
<section class="section center">
  <div class="wrap">
    <p class="eyebrow">404</p>
    <h1>That page is not here</h1>
    <p class="lead">The link may be old or mistyped. Try one of these instead.</p>
    <div class="btn-row" style="justify-content:center;margin-top:26px">
      <a class="btn btn--primary" href="/">Home</a>
      <a class="btn btn--outline" href="/gallery/">Gallery</a>
      <a class="btn btn--outline" href="/contact/">Free estimate</a>
    </div>
  </div>
</section>"""
    return layout(slug="404", title="Page not found | %s" % BIZ["name"],
                  desc="Page not found.", path="/404.html", body=body)


# ---------------------------------------------------------------------------
# NON-HTML FILES
# ---------------------------------------------------------------------------

def all_paths():
    paths = ["/", "/about/", "/contact/", "/gallery/", "/reviews/", "/privacy/"]
    paths += ["/%s/" % s["slug"] for s in SERVICES]
    paths += ["/%s/" % c["slug"] for c in CITIES]
    return paths


def sitemap():
    urls = ""
    for p in all_paths():
        pri = "1.0" if p == "/" else ("0.8" if p.count("/") == 2 else "0.6")
        urls += ("  <url><loc>%s%s</loc><lastmod>%s</lastmod>"
                 "<priority>%s</priority></url>\n" % (SITE_URL, p, TODAY, pri))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '%s</urlset>\n' % urls)


def robots():
    return "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL


def llms_txt():
    svc = "\n".join("- [%s](%s/%s/): %s" % (s["nav"], SITE_URL, s["slug"], s["desc"])
                    for s in SERVICES)
    cities = ", ".join("%s SC" % c["name"] for c in CITIES)
    return """# %(name)s

> Painting and wallpaper contractor based in %(city)s, South Carolina, serving Greenville,
> Spartanburg and the surrounding Upstate. Specialises in wallpaper installation and removal,
> including murals, designer papers and papered ceilings — a service most painting companies
> in the region do not offer.

- Owner: %(owner)s
- Phone: %(phone)s
- Email: %(email)s
- Base: %(city)s, %(state)s %(zip)s
- Hours: %(hours)s
- Ratings: %(gr)s on Google (%(gc)d reviews), %(tr)s on Thumbtack (%(tc)d reviews)

## Services
%(svc)s

## Service area
%(cities)s

## Key pages
- [Home](%(site)s/)
- [Gallery](%(site)s/gallery/)
- [Reviews](%(site)s/reviews/)
- [About](%(site)s/about/)
- [Contact and free estimate](%(site)s/contact/)
""" % {"name": BIZ["name"], "city": BIZ["city"], "state": BIZ["state"], "zip": BIZ["zip"],
       "owner": BIZ["owner"], "phone": BIZ["phone"], "email": BIZ["email"],
       "hours": BIZ["hours"], "gr": PROOF["google_rating"], "gc": PROOF["google_count"],
       "tr": PROOF["thumbtack_rating"], "tc": PROOF["thumbtack_count"],
       "svc": svc, "cities": cities, "site": SITE_URL}


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------

def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    write("index.html", page_home())
    write("about/index.html", page_about())
    write("contact/index.html", page_contact())
    write("gallery/index.html", page_gallery())
    write("reviews/index.html", page_reviews())
    write("privacy/index.html", page_privacy())
    write("404.html", page_404())

    for s in SERVICES:
        write("%s/index.html" % s["slug"], page_service(s))
    for c in CITIES:
        write("%s/index.html" % c["slug"], page_city(c))

    write("sitemap.xml", sitemap())
    write("llms.txt", llms_txt())
    write(".nojekyll", "")

    if PREVIEW:
        # keep a preview out of Google entirely, and do not let GitHub redirect
        # it to a domain that is not pointing anywhere yet
        write("robots.txt", "User-agent: *\nDisallow: /\n")
    else:
        write("robots.txt", robots())
        write("CNAME", BIZ["domain"] + "\n")

    shutil.copytree(os.path.join(ROOT, "assets", "css"),
                    os.path.join(OUT, "assets", "css"))
    shutil.copytree(os.path.join(ROOT, "assets", "js"),
                    os.path.join(OUT, "assets", "js"))
    shutil.copytree(os.path.join(ROOT, "photos"),
                    os.path.join(OUT, "assets", "img"))

    pages = 7 + len(SERVICES) + len(CITIES)
    print("Built %d pages into %s" % (pages, OUT))
    if PREVIEW:
        where = "opened directly from disk" if BASE_PATH == "." else BASE_PATH + "/"
        print("  → PREVIEW build for %s — noindex, no CNAME." % where)
        print("     Re-run plain `python3 build.py` before going live.")
    if BIZ["phone"].endswith("000-0000"):
        print("  ⚠️  Phone number is still a placeholder — set BIZ['phone'].")
    if not FORM_ENDPOINT:
        print("  ⚠️  No form endpoint — the contact form falls back to mailto:.")
    if not REVIEWS:
        print("  ⚠️  No review text yet — /reviews/ links out instead of quoting.")


def parse_args(argv):
    global PREVIEW, BASE_PATH
    if "--preview" in argv:
        PREVIEW = True
        i = argv.index("--preview")
        rest = argv[i + 1:]
        BASE_PATH = "/" + rest[0].strip("/") if rest else "."


if __name__ == "__main__":
    parse_args(sys.argv[1:])
    main()

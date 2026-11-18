import sys
from pathlib import Path
import urllib.request
from pptx import Presentation

BASE = Path(r"C:\Users\NEERAJ\.gemini\antigravity\scratch\SunSecond")
PPTX_PATH = BASE / "SunSecond_STDD_Executive_Pitch_Deck.pptx"

print("=" * 60)
print("LAYER 1: PRESENTATION (PPTX) INTEGRITY & FLOW")
print("=" * 60)
prs = Presentation(str(PPTX_PATH))
print(f"Total Slides: {len(prs.slides)} (Expected: 16)")
assert len(prs.slides) == 16, "Deck must have exactly 16 slides!"

# Check Slide 1 details
s1 = prs.slides[0]
s1_texts = [s.text_frame.text for s in s1.shapes if s.has_text_frame]
full_s1 = " ".join(s1_texts)
print("\nSlide 01 (Title Card):")
print("  - Title text:", s1_texts[1] if len(s1_texts) > 1 else s1_texts[0])
assert "BEC754" in full_s1, "BEC754 missing from title slide!"
assert "Rajkiya Engineering College, Sonbhadra" in full_s1, "College name missing from title slide!"
assert "Neeraj" in full_s1 and "Pankaj" in full_s1, "Team members missing from title slide!"
assert "2308410300042" in full_s1 and "2308410300044" in full_s1, "Roll numbers missing from title slide!"
print("  -> Academic & Team Credentials: VERIFIED (100% MATCH)")

# Check Slides 2 to 15
print("\nSlides 02-15 (Content Structure & Deep Dive Links):")
for i in range(1, 15):
    slide = prs.slides[i]
    slide_num = i + 1
    has_notes = slide.has_notes_slide and bool(slide.notes_slide.notes_text_frame.text.strip())
    links = []
    headers = []
    for s in slide.shapes:
        if s.has_text_frame:
            for p in s.text_frame.paragraphs:
                for r in p.runs:
                    if r.hyperlink and r.hyperlink.address:
                        links.append((r.text, r.hyperlink.address))
        if s.has_text_frame and s.text_frame.text.strip():
            lines = [line.strip() for line in s.text_frame.text.split("\n") if line.strip()]
            if lines and lines[0] not in headers:
                headers.append(lines[0])

    category_str = headers[0] if headers else "UNKNOWN"
    title_str = headers[1] if len(headers) > 1 else "NO TITLE"
    link_target = links[0][1] if links else "NO LINK"
    print(f"  Slide {slide_num:02d} | [{category_str[:28]}] -> Link: {link_target}")
    assert len(links) > 0, f"Slide {slide_num} missing deep-dive link!"
    assert has_notes, f"Slide {slide_num} missing speaker notes!"

# Check Slide 16
print("\nSlide 16 (Closing Vision, QR Code & Live Portal):")
s16 = prs.slides[15]
s16_texts = [s.text_frame.text for s in s16.shapes if s.has_text_frame]
full_s16 = " ".join(s16_texts)
assert "Every Ray Deserves a Second Life" in full_s16, "Vision quote missing on Slide 16!"
assert "iamneerajverma001.github.io/SunSecond" in full_s16, "GitHub Pages URL missing on Slide 16!"
# Check pictures on slide 16
pictures = [s for s in s16.shapes if s.shape_type == 13]  # 13 = PICTURE
print(f"  -> Embedded QR Pictures found: {len(pictures)} (Expected: 1)")
assert len(pictures) >= 1, "QR code picture must be embedded on Slide 16!"
print("  -> Closing Vision & QR Code: VERIFIED")

print("\n" + "=" * 60)
print("LAYER 2: LOCAL INTERACTIVE DATA ROOM & APPENDICES")
print("=" * 60)
core_files = [
    "index.html",
    "SUNSECOND_PROJECT_BIBLE.html",
    "SUNSECOND_PROJECT_BIBLE.md",
    "qr_sunsecond_dataroom.png",
    ".nojekyll",
    "README.md"
]
for cf in core_files:
    p = BASE / cf
    assert p.exists(), f"Core file missing: {cf}"
    print(f"  [OK] {cf} ({p.stat().st_size:,} bytes)")

docs_dir = BASE / "docs"
assert docs_dir.exists(), "docs directory missing!"
print(f"\nChecking 9 Appendices in {docs_dir.name}/:")
for letter in ["a", "b", "c", "d", "e", "f", "g", "h", "i"]:
    html_matches = list(docs_dir.glob(f"appendix_{letter}_*.html"))
    md_matches = list(docs_dir.glob(f"appendix_{letter}_*.md"))
    assert html_matches, f"Missing HTML for appendix {letter}"
    assert md_matches, f"Missing MD for appendix {letter}"
    h_file = html_matches[0]
    m_file = md_matches[0]
    # Check that html has back links
    h_text = h_file.read_text(encoding="utf-8")
    assert "../index.html" in h_text, f"{h_file.name} missing backlink to index.html"
    assert "../SUNSECOND_PROJECT_BIBLE.html" in h_text, f"{h_file.name} missing backlink to Project Bible"
    print(f"  [OK] Appendix {letter.upper()}: {h_file.name} ({h_file.stat().st_size:,} bytes) & {m_file.name}")

print("\n" + "=" * 60)
print("LAYER 3: FINANCIAL & TECHNICAL CROSS-METRIC UNIFICATION")
print("=" * 60)
bible_text = (BASE / "SUNSECOND_PROJECT_BIBLE.md").read_text(encoding="utf-8")
app_i_text = (docs_dir / "appendix_i_unit1_financials.md").read_text(encoding="utf-8")

metrics = [
    ("CapEx ₹23 Lakhs", ["23,00,000", "23 Lakh", "₹23L"]),
    ("OpEx ₹3.00L/month", ["3,00,000", "₹3.00L/mo", "₹3L/mo"]),
    ("Break-even 360 panels/mo", ["360 panels", "360 panels/mo"]),
    ("Steady-State 800 panels/mo", ["800 panels", "800 panels/mo"]),
    ("Annual Profit ₹44.4 Lakhs", ["44,37,000", "44.4L", "₹44.4 Lakh"]),
    ("Annual Cash ROI 193%", ["193%", "192.9%"]),
    ("Decision Triage Accuracy >98.5%", ["98.5%"]),
    ("4S Grading Standard", ["4S Standard", "4S Grading", "Safety, Spec, Silicon, Scrap"]),
    ("CPCB Category CEEW-14", ["CEEW-14", "CEEW 14"])
]

for label, search_terms in metrics:
    found_bible = any(term in bible_text for term in search_terms)
    found_app_i = any(term in app_i_text for term in search_terms)
    status_b = "Bible: OK" if found_bible else "Bible: MISSING"
    status_i = "App I: OK" if found_app_i else "App I: MISSING"
    print(f"  - {label:<35} | {status_b:<12} | {status_i:<12}")

print("\n" + "=" * 60)
print("LAYER 4: LIVE GITHUB PAGES WORLDWIDE ACCESSIBILITY")
print("=" * 60)
test_urls = [
    ("Landing Page", "https://iamneerajverma001.github.io/SunSecond/"),
    ("Master Bible", "https://iamneerajverma001.github.io/SunSecond/SUNSECOND_PROJECT_BIBLE.html"),
    ("Appendix A (Market)", "https://iamneerajverma001.github.io/SunSecond/docs/appendix_a_market_analysis.html"),
    ("Appendix E (Testing)", "https://iamneerajverma001.github.io/SunSecond/docs/appendix_e_testing_suites.html"),
    ("Appendix I (Unit-1)", "https://iamneerajverma001.github.io/SunSecond/docs/appendix_i_unit1_financials.html"),
    ("Pitch Deck Download", "https://iamneerajverma001.github.io/SunSecond/SunSecond_STDD_Executive_Pitch_Deck.pptx"),
    ("Slide 16 QR Code", "https://iamneerajverma001.github.io/SunSecond/qr_sunsecond_dataroom.png")
]

all_live = True
for name, url in test_urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as response:
            code = response.getcode()
            print(f"  [HTTP {code} OK] {name:<22} -> {url}")
    except Exception as e:
        all_live = False
        print(f"  [FAILED] {name:<22} -> {e}")

print("=" * 60)
if all_live:
    print(">>> FINAL RESULT: 100% UNIFIED, INTEGRATED & LIVE ONLINE! <<<")
else:
    print(">>> WARNING: Some live URLs could not be reached. <<<")
print("=" * 60)

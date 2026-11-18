"""
SunSecond (STDD) — Complete Interlinked Data Room & Executive Pitch Deck Builder
Builds:
  1. Portable Markdown + Styled Interactive HTML Data Room (index.html, SUNSECOND_PROJECT_BIBLE.html, docs/*.html)
  2. High-DPI Teal/Slate QR Code pointing to the Data Room URL
  3. 16-Slide Executive PowerPoint Pitch Deck with:
     - Clickable deep-dive links on every content slide (Slides 2-15)
     - Subtle institutional footer (BEC754 | Electronics Engineering, REC Sonbhadra)
     - Slide 16: Vision-linked Thank You note + clickable Data Room link + scannable QR code
"""

import argparse
import html
import json
import re
import shutil
import sys
from pathlib import Path

import markdown
import qrcode
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

sys.path.append(r"C:\Users\NEERAJ\.gemini\config\skills\presentation-designer\scripts")
from deck_engine import build_from_spec  # noqa: E402

BRAIN_DIR = Path(r"C:\Users\NEERAJ\.gemini\antigravity\brain\e8b5526c-d348-432a-91fc-7d0cdda26653")
OUT_DIR = Path(r"C:\Users\NEERAJ\.gemini\antigravity\scratch\SunSecond")
DOCS_DIR = OUT_DIR / "docs"
SPEC_PATH = BRAIN_DIR / "scratch" / "sunsecond_deck_spec.json"
PPTX_PATH = OUT_DIR / "SunSecond_STDD_Executive_Pitch_Deck.pptx"

# Mapping of source artifacts -> clean portable names in SunSecond/docs/
APPENDICES = [
    ("A", "solar_panel_afterlife_recycling_market_analysis.md", "appendix_a_market_analysis",
     "Market & Technical Analysis", "Global/India PV waste surge, panel mass-vs-value paradox & CPCB EPR"),
    ("B", "sunsecond_stdd_blueprint.md", "appendix_b_stdd_blueprint",
     "STDD Strategic Positioning", "Zero-bias HSM grading, on-site service UX & dual-stream cash flow"),
    ("C", "sunsecond_gia_roadmap_and_triage_science.md", "appendix_c_gia_triage_science",
     "GIA Roadmap & Triage Science", "5-step trust monopoly playbook, 14% wet-leakage trap & sensor physics"),
    ("D", "sunsecond_cascade_reuse_and_interview_guide.md", "appendix_d_cascade_reuse",
     "Cascade Reuse & Interview Kit", "Multi-tier reuse down to <60V SELV, Poka-Yoke & 5-stakeholder Mom-Test scripts"),
    ("E", "sunsecond_testing_suites_master_architecture.md", "appendix_e_testing_suites",
     "11-Method Testing Suites", "Dark I-V, AC-IS, UVF, NIR, SSTDR & Scout / Express-Van / Vault-Hub specs"),
    ("F", "sunsecond_monetization_and_marketplace_engine.md", "appendix_f_monetization_engine",
     "10-Stream Commercial Engine", "StockX Escrow Bazaar, Spinny Power Kits, GIA label licensing & Solar Blue Book"),
    ("G", "sunsecond_scrap_monetization_and_trust_architecture.md", "appendix_g_scrap_monetization",
     "SS-F Scrap Monetization", "Flipping CEEW's -₹10.2K/t loss to +₹98K/t via 7 levers & 5-rule governance"),
    ("H", "sunsecond_scrapping_suites_master_architecture.md", "appendix_h_scrapping_suites",
     "Toxin-Free Scrapping Suites", "Dual Hot-Knife/Roller delam, closed-loop MSA Electrowinning & 3 Extraction Suites"),
    ("I", "sunsecond_reality_financials_and_execution_plan.md", "appendix_i_unit1_financials",
     "Unit-1 Financials & Execution", "₹23L launch CapEx, ₹3L/mo OpEx, Month-4 break-even, 193% ROI & 6 risk defenses"),
]

# Slide (1-indexed) -> (Link Label, Relative Target HTML)
SLIDE_DEEP_DIVES = {
    2: ("Deep Dive: Appendix A — Market Analysis ->", "docs/appendix_a_market_analysis.html"),
    3: ("Deep Dive: Appendix B — STDD Blueprint ->", "docs/appendix_b_stdd_blueprint.html"),
    4: ("Deep Dive: Master Project Bible ->", "SUNSECOND_PROJECT_BIBLE.html"),
    5: ("Deep Dive: Appendix C — Triage Science ->", "docs/appendix_c_gia_triage_science.html"),
    6: ("Deep Dive: Appendix E — Testing Suites ->", "docs/appendix_e_testing_suites.html"),
    7: ("Deep Dive: Appendix D — Cascade Reuse ->", "docs/appendix_d_cascade_reuse.html"),
    8: ("Deep Dive: Appendix F — 10-Stream Engine ->", "docs/appendix_f_monetization_engine.html"),
    9: ("Deep Dive: Appendix H — Scrapping Suites ->", "docs/appendix_h_scrapping_suites.html"),
    10: ("Deep Dive: Appendix G — Scrap Economics ->", "docs/appendix_g_scrap_monetization.html"),
    11: ("Deep Dive: Appendix I — Unit-1 Model & ROI ->", "docs/appendix_i_unit1_financials.html"),
    12: ("Deep Dive: Master Project Bible ->", "SUNSECOND_PROJECT_BIBLE.html"),
    13: ("Deep Dive: Appendix I — Risk Matrix ->", "docs/appendix_i_unit1_financials.html"),
}

HTML_STYLE = """
:root {
  --bg: #f8fafc;
  --card: #ffffff;
  --slate: #1e293b;
  --muted: #475569;
  --teal: #0d9488;
  --teal-dark: #0f766e;
  --teal-soft: #ccfbf1;
  --amber: #f59e0b;
  --border: #cbd5e1;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--slate);
  line-height: 1.65;
}
.topbar {
  position: sticky; top: 0; z-index: 50;
  background: #0f172a; color: #f8fafc;
  padding: 12px 24px;
  display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
  border-bottom: 3px solid var(--teal);
  gap: 10px;
}
.topbar .brand { font-weight: 800; font-size: 16px; letter-spacing: 0.4px; }
.topbar .brand span { color: #2dd4bf; }
.topbar nav a {
  color: #e2e8f0; text-decoration: none; font-size: 13px; font-weight: 600;
  margin-left: 16px; padding: 6px 12px; border-radius: 6px;
  background: rgba(255,255,255,0.08);
}
.topbar nav a:hover { background: var(--teal); color: #fff; }
.container { max-width: 1080px; margin: 28px auto 60px; padding: 0 20px; }
.doc-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 14px; padding: 36px 42px;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05);
}
h1 { color: #0f172a; border-bottom: 3px solid var(--teal); padding-bottom: 10px; margin-top: 0; font-size: 28px; }
h2 { color: var(--teal-dark); margin-top: 32px; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; font-size: 21px; }
h3 { color: #1e293b; margin-top: 22px; font-size: 17px; }
a { color: var(--teal-dark); font-weight: 600; }
a:hover { color: var(--teal); }
table { width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px; display: block; overflow-x: auto; }
th { background: var(--teal); color: #fff; text-align: left; padding: 10px 12px; font-weight: 700; }
td { padding: 9px 12px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
blockquote {
  margin: 18px 0; padding: 14px 18px;
  background: #f0fdfa; border-left: 4px solid var(--teal);
  border-radius: 0 8px 8px 0; color: #134e4a;
}
code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 0.92em; color: #0f172a; }
pre { background: #0f172a; color: #e2e8f0; padding: 16px; border-radius: 8px; overflow-x: auto; }
pre code { background: none; color: inherit; padding: 0; }
.mermaid {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 16px; margin: 18px 0; text-align: center; overflow-x: auto;
}
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #134e4a 100%);
  color: #fff; border-radius: 16px; padding: 36px 40px; margin-bottom: 28px;
}
.hero h1 { color: #fff; border: none; margin: 0 0 8px; font-size: 32px; }
.hero .tag {
  display: inline-block; background: rgba(45,212,191,0.2); color: #5eead4;
  border: 1px solid #2dd4bf; padding: 4px 12px; border-radius: 999px;
  font-size: 12px; font-weight: 700; margin-bottom: 14px;
}
.hero p { color: #cbd5e1; margin: 6px 0; font-size: 15px; }
.cta-row { margin-top: 22px; display: flex; flex-wrap: wrap; gap: 12px; }
.btn {
  display: inline-block; padding: 12px 20px; border-radius: 8px;
  text-decoration: none; font-weight: 700; font-size: 14px;
}
.btn-primary { background: var(--teal); color: #fff !important; }
.btn-primary:hover { background: #14b8a6; }
.btn-amber { background: var(--amber); color: #0f172a !important; }
.grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 18px; margin-top: 18px;
}
.app-card {
  background: #fff; border: 1px solid var(--border); border-radius: 12px;
  padding: 20px 22px; display: flex; flex-direction: column; justify-content: space-between;
  transition: transform 0.15s, border-color 0.15s;
}
.app-card:hover { transform: translateY(-2px); border-color: var(--teal); }
.app-pill {
  display: inline-block; background: var(--teal-soft); color: var(--teal-dark);
  font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 6px; margin-bottom: 8px;
}
.app-card h3 { margin: 4px 0 8px; font-size: 16px; color: #0f172a; }
.app-card p { font-size: 13px; color: var(--muted); margin: 0 0 14px; }
.footer-bar {
  text-align: center; color: var(--muted); font-size: 12px; margin-top: 36px; padding-top: 18px;
  border-top: 1px solid var(--border);
}
@media print { .topbar { display: none; } .doc-card { border: none; box-shadow: none; padding: 0; } }
"""


def md_to_html_body(md_text: str) -> str:
    """Convert markdown to HTML while preserving Mermaid blocks and KaTeX math."""
    # Protect mermaid code fences before markdown conversion
    mermaid_blocks = []

    def _replace_mermaid(match):
        mermaid_blocks.append(match.group(1).strip())
        return f"@@MERMAID_BLOCK_{len(mermaid_blocks)-1}@@"

    cleaned = re.sub(r"```mermaid\s*\n(.*?)```", _replace_mermaid, md_text, flags=re.DOTALL)
    # Clean GitHub alert tags (> [!TIP], > [!IMPORTANT], > [!CAUTION])
    cleaned = re.sub(r"^>\s*\[!(TIP|IMPORTANT|CAUTION|NOTE|WARNING)\]\s*", r"> **\1:** ", cleaned, flags=re.MULTILINE)
    # Unescape escaped currency \$ for HTML display
    cleaned = cleaned.replace(r"\$", "$")

    html_out = markdown.markdown(
        cleaned,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )

    for idx, code in enumerate(mermaid_blocks):
        placeholder = f"<p>@@MERMAID_BLOCK_{idx}@@</p>"
        div = f'<div class="mermaid">\n{html.escape(code)}\n</div>'
        html_out = html_out.replace(placeholder, div).replace(f"@@MERMAID_BLOCK_{idx}@@", div)

    return html_out


def wrap_html_page(title: str, body_html: str, is_subdir: bool = False) -> str:
    prefix = "../" if is_subdir else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)} — SunSecond (STDD)</title>
  <style>{HTML_STYLE}</style>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'\\\\(',right:'\\\\)',display:false}}]}});"></script>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
  </script>
</head>
<body>
  <header class="topbar">
    <div class="brand">Sun<span>Second</span> (STDD) — Deep-Dive Data Room</div>
    <nav>
      <a href="{prefix}index.html">Data Room Home</a>
      <a href="{prefix}SUNSECOND_PROJECT_BIBLE.html">Master Project Bible</a>
      <a href="{prefix}SunSecond_STDD_Executive_Pitch_Deck.pptx">Download Pitch Deck (.pptx)</a>
    </nav>
  </header>
  <main class="container">
    <article class="doc-card">
      {body_html}
    </article>
    <div class="footer-bar">
      <strong>Project SunSecond</strong> &nbsp;|&nbsp; BEC754: Start-up and Entrepreneurial Activity Assessment &nbsp;|&nbsp;
      Department of Electronics Engineering, Rajkiya Engineering College, Sonbhadra &nbsp;|&nbsp;
      Team: Neeraj (2308410300042) &amp; Pankaj (2308410300044)
    </div>
  </main>
</body>
</html>
"""


def build_dataroom():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy & convert all 9 appendices into docs/
    link_map_md = {}
    link_map_html = {}
    for letter, src_name, dst_stem, short_title, desc in APPENDICES:
        src_path = BRAIN_DIR / src_name
        md_content = src_path.read_text(encoding="utf-8")
        # Save portable Markdown copy
        (DOCS_DIR / f"{dst_stem}.md").write_text(md_content, encoding="utf-8")
        # Render interactive HTML copy
        body = md_to_html_body(md_content)
        back_banner = (
            f'<p style="font-size:13px;margin-top:0;"><a href="../SUNSECOND_PROJECT_BIBLE.html">'
            f'&larr; Back to Master Project Bible</a> &nbsp;|&nbsp; '
            f'<a href="../index.html">All Deep-Dive Appendices</a></p>'
        )
        html_page = wrap_html_page(f"Appendix {letter}: {short_title}", back_banner + body, is_subdir=True)
        (DOCS_DIR / f"{dst_stem}.html").write_text(html_page, encoding="utf-8")

        file_url = f"file:///C:/Users/NEERAJ/.gemini/antigravity/brain/e8b5526c-d348-432a-91fc-7d0cdda26653/{src_name}"
        link_map_md[file_url] = f"docs/{dst_stem}.md"
        link_map_html[file_url] = f"docs/{dst_stem}.html"

    # 2. Rewrite Master Project Bible with portable relative links (both .md and .html)
    bible_raw = (BRAIN_DIR / "SUNSECOND_PROJECT_BIBLE.md").read_text(encoding="utf-8")
    bible_md_portable = bible_raw
    bible_html_source = bible_raw
    for old_url, rel_md in link_map_md.items():
        bible_md_portable = bible_md_portable.replace(old_url, rel_md)
    for old_url, rel_html in link_map_html.items():
        bible_html_source = bible_html_source.replace(old_url, rel_html)

    (OUT_DIR / "SUNSECOND_PROJECT_BIBLE.md").write_text(bible_md_portable, encoding="utf-8")
    bible_body = md_to_html_body(bible_html_source)
    (OUT_DIR / "SUNSECOND_PROJECT_BIBLE.html").write_text(
        wrap_html_page("Master Project Bible (v3.1)", bible_body, is_subdir=False),
        encoding="utf-8",
    )

    # 3. Build Flagship Data Room Landing Page (index.html)
    cards_html = []
    for letter, _, dst_stem, short_title, desc in APPENDICES:
        cards_html.append(f"""
        <div class="app-card">
          <div>
            <span class="app-pill">APPENDIX {letter}</span>
            <h3>{html.escape(short_title)}</h3>
            <p>{html.escape(desc)}</p>
          </div>
          <a href="docs/{dst_stem}.html">Open Deep Dive &rarr;</a>
        </div>
        """)

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>SunSecond (STDD) — Interactive Deep-Dive Data Room</title>
  <style>{HTML_STYLE}</style>
</head>
<body>
  <header class="topbar">
    <div class="brand">Sun<span>Second</span> (STDD) — The "GIA for Solar"</div>
    <nav>
      <a href="SUNSECOND_PROJECT_BIBLE.html">Master Project Bible</a>
      <a href="SunSecond_STDD_Executive_Pitch_Deck.pptx">Pitch Deck (.pptx)</a>
    </nav>
  </header>
  <main class="container">
    <section class="hero">
      <div class="tag">BEC754 &bull; START-UP &amp; ENTREPRENEURIAL ACTIVITY ASSESSMENT</div>
      <h1>SunSecond — Interactive Deep-Dive Data Room</h1>
      <p><strong>"Every Ray Deserves a Second Life. Every Gram Deserves a Clean Return."</strong></p>
      <p>Department of Electronics Engineering &nbsp;|&nbsp; Rajkiya Engineering College, Sonbhadra</p>
      <p>Team: <strong>Neeraj</strong> (Roll No. 2308410300042) &amp; <strong>Pankaj</strong> (Roll No. 2308410300044)</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="SUNSECOND_PROJECT_BIBLE.html">Read Master Project Bible (v3.1) &rarr;</a>
        <a class="btn btn-amber" href="SunSecond_STDD_Executive_Pitch_Deck.pptx">Download 16-Slide Pitch Deck (.pptx)</a>
      </div>
    </section>

    <h2 style="margin-top:10px;">9 Interlinked Deep-Dive Engineering &amp; Financial Appendices</h2>
    <section class="grid">
      {''.join(cards_html)}
    </section>

    <div class="footer-bar">
      All documents, diagrams, testing suite architectures, toxin-free extraction flows &amp; Unit-1 financials are cross-linked for instant faculty &amp; investor inspection.
    </div>
  </main>
</body>
</html>
"""
    (OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")


def generate_qr(url: str, qr_path: Path):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert("RGB")
    img.save(qr_path)


def enhance_pptx_with_links_and_thankyou(live_url: str):
    # 1. Build base 15 slides using presentation-designer engine
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    build_from_spec(spec, str(PPTX_PATH))

    # 2. Generate crisp scannable QR code
    qr_path = OUT_DIR / "qr_sunsecond_dataroom.png"
    generate_qr(live_url, qr_path)

    # 3. Post-process PPTX: add deep-dive links (Slides 2-15) + custom Slide 16 Thank You & QR
    prs = Presentation(str(PPTX_PATH))
    FONT = "Calibri"
    C_BG = RGBColor(255, 255, 255)
    C_CARD = RGBColor(241, 245, 249)
    C_PRIMARY = RGBColor(30, 41, 59)
    C_SECONDARY = RGBColor(71, 85, 105)
    C_TEAL = RGBColor(13, 148, 136)
    C_TEAL_BG = RGBColor(204, 251, 241)
    C_BORDER = RGBColor(203, 213, 225)
    C_MUTED = RGBColor(100, 116, 139)
    C_AMBER_DARK = RGBColor(180, 83, 9)

    # Add subtle footer + clickable Deep-Dive link pill to Slides 2..15
    for idx, slide in enumerate(prs.slides, start=1):
        if idx == 1:
            continue
        # Left institutional footer
        f_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.02), Inches(7.2), Inches(0.3))
        tf_f = f_box.text_frame
        tf_f.margin_left = tf_f.margin_right = tf_f.margin_top = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = f"SunSecond (STDD)  |  BEC754  |  Electronics Engineering, REC Sonbhadra  |  Slide {idx:02d}"
        p_f.font.name = FONT
        p_f.font.size = Pt(8.5)
        p_f.font.color.rgb = C_MUTED

        # Right clickable Deep-Dive Pill
        if idx in SLIDE_DEEP_DIVES:
            label, rel_target = SLIDE_DEEP_DIVES[idx]
            pill = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.05), Inches(6.97), Inches(3.48), Inches(0.34)
            )
            pill.fill.solid()
            pill.fill.fore_color.rgb = C_TEAL_BG
            pill.line.color.rgb = C_TEAL
            pill.line.width = Pt(0.75)
            tf_p = pill.text_frame
            tf_p.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf_p.margin_left = tf_p.margin_right = Inches(0.08)
            tf_p.margin_top = tf_p.margin_bottom = 0
            p = tf_p.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = label
            run.font.name = FONT
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = C_TEAL
            run.hyperlink.address = rel_target

    # ---------------------------------------------------------
    # SLIDE 16: CREATIVE VISION-LINKED THANK YOU + URL + QR CODE
    # ---------------------------------------------------------
    slide16 = prs.slides.add_slide(prs.slide_layouts[6])

    # White canvas background
    bg = slide16.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()

    # Left Teal Vertical Accent Spine
    bar = slide16.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.75), Inches(0.85), Inches(0.12), Inches(5.8))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_TEAL
    bar.line.fill.background()

    # Top Kicker Pill
    tag = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), Inches(0.85), Inches(3.3), Inches(0.38))
    tag.fill.solid()
    tag.fill.fore_color.rgb = C_TEAL_BG
    tag.line.color.rgb = C_TEAL
    tag.line.width = Pt(1)
    p_tag = tag.text_frame.paragraphs[0]
    p_tag.text = "BEC754  |  PROJECT SUNSECOND"
    p_tag.font.name = FONT
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_TEAL
    p_tag.alignment = PP_ALIGN.CENTER

    # Hero "Thank You." Display Title
    t_box = slide16.shapes.add_textbox(Inches(1.15), Inches(1.42), Inches(6.7), Inches(0.95))
    tf_t = t_box.text_frame
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = "Thank You."
    p_t.font.name = FONT
    p_t.font.size = Pt(44)
    p_t.font.bold = True
    p_t.font.color.rgb = C_PRIMARY

    # Creative Vision-Linked Quote Card
    q_card = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), Inches(2.5), Inches(6.65), Inches(1.75))
    q_card.fill.solid()
    q_card.fill.fore_color.rgb = C_TEAL_BG
    q_card.line.color.rgb = C_TEAL
    q_card.line.width = Pt(1.5)
    tf_q = q_card.text_frame
    tf_q.word_wrap = True
    tf_q.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_q.margin_left = Inches(0.3)
    tf_q.margin_right = Inches(0.3)

    pq1 = tf_q.paragraphs[0]
    pq1.text = "“Every Ray Deserves a Second Life."
    pq1.font.name = FONT
    pq1.font.size = Pt(18)
    pq1.font.bold = True
    pq1.font.color.rgb = C_TEAL

    pq2 = tf_q.add_paragraph()
    pq2.text = "Every Gram Deserves a Clean Return.”"
    pq2.font.name = FONT
    pq2.font.size = Pt(18)
    pq2.font.bold = True
    pq2.font.color.rgb = C_AMBER_DARK
    pq2.space_after = Pt(8)

    pq3 = tf_q.add_paragraph()
    pq3.text = "Grateful for your guidance as we engineer India's trusted, toxin-free circular solar standard."
    pq3.font.name = FONT
    pq3.font.size = Pt(11.5)
    pq3.font.italic = True
    pq3.font.color.rgb = C_PRIMARY

    # Team & College Credit Card
    m_card = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.15), Inches(4.5), Inches(6.65), Inches(2.15))
    m_card.fill.solid()
    m_card.fill.fore_color.rgb = C_CARD
    m_card.line.color.rgb = C_BORDER
    m_card.line.width = Pt(1)
    tf_m = m_card.text_frame
    tf_m.word_wrap = True
    tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_m.margin_left = Inches(0.3)
    tf_m.margin_right = Inches(0.3)

    pm0 = tf_m.paragraphs[0]
    pm0.text = "PRESENTED BY — SUNSECOND TEAM"
    pm0.font.name = FONT
    pm0.font.size = Pt(10)
    pm0.font.bold = True
    pm0.font.color.rgb = C_TEAL
    pm0.space_after = Pt(6)

    pm1 = tf_m.add_paragraph()
    pm1.text = "1. Neeraj   (Roll No. 2308410300042)      |      2. Pankaj   (Roll No. 2308410300044)"
    pm1.font.name = FONT
    pm1.font.size = Pt(13)
    pm1.font.bold = True
    pm1.font.color.rgb = C_PRIMARY
    pm1.space_after = Pt(6)

    pm2 = tf_m.add_paragraph()
    pm2.text = "Department of Electronics Engineering  •  Rajkiya Engineering College, Sonbhadra"
    pm2.font.name = FONT
    pm2.font.size = Pt(11.5)
    pm2.font.color.rgb = C_SECONDARY
    pm2.space_after = Pt(4)

    pm3 = tf_m.add_paragraph()
    pm3.text = "Subject: BEC754 — Start-up and Entrepreneurial Activity Assessment"
    pm3.font.name = FONT
    pm3.font.size = Pt(10.5)
    pm3.font.color.rgb = C_MUTED

    # Right Zone: Interactive Deep-Dive Data Room + Scannable QR Card
    r_x, r_y, r_w, r_h = Inches(8.15), Inches(0.85), Inches(4.4), Inches(5.8)
    r_card = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, r_x, r_y, r_w, r_h)
    r_card.fill.solid()
    r_card.fill.fore_color.rgb = C_CARD
    r_card.line.color.rgb = C_TEAL
    r_card.line.width = Pt(2)

    r_badge = slide16.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, r_x + Inches(0.45), r_y + Inches(0.28), Inches(3.5), Inches(0.38))
    r_badge.fill.solid()
    r_badge.fill.fore_color.rgb = C_TEAL
    r_badge.line.fill.background()
    p_rb = r_badge.text_frame.paragraphs[0]
    p_rb.text = "SCAN OR CLICK FOR DEEP DIVE"
    p_rb.font.name = FONT
    p_rb.font.size = Pt(10)
    p_rb.font.bold = True
    p_rb.font.color.rgb = RGBColor(255, 255, 255)
    p_rb.alignment = PP_ALIGN.CENTER

    r_title = slide16.shapes.add_textbox(r_x + Inches(0.25), r_y + Inches(0.78), r_w - Inches(0.5), Inches(0.55))
    tf_rt = r_title.text_frame
    tf_rt.word_wrap = True
    tf_rt.margin_left = tf_rt.margin_right = tf_rt.margin_top = tf_rt.margin_bottom = 0
    p_rt = tf_rt.paragraphs[0]
    p_rt.text = "Project Bible & 9 Technical Appendices"
    p_rt.font.name = FONT
    p_rt.font.size = Pt(14)
    p_rt.font.bold = True
    p_rt.font.color.rgb = C_PRIMARY
    p_rt.alignment = PP_ALIGN.CENTER

    # Crisp White Frame behind QR Code
    qr_frame = slide16.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, r_x + Inches(0.95), r_y + Inches(1.4), Inches(2.5), Inches(2.5)
    )
    qr_frame.fill.solid()
    qr_frame.fill.fore_color.rgb = RGBColor(255, 255, 255)
    qr_frame.line.color.rgb = C_BORDER
    qr_frame.line.width = Pt(1)

    # Embedded High-Res Scannable QR Code
    slide16.shapes.add_picture(str(qr_path), r_x + Inches(1.05), r_y + Inches(1.5), Inches(2.3), Inches(2.3))

    # Clickable Direct Link Box (opens local index.html offline on laptop!)
    url_box = slide16.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, r_x + Inches(0.3), r_y + Inches(4.12), r_w - Inches(0.6), Inches(0.52)
    )
    url_box.fill.solid()
    url_box.fill.fore_color.rgb = RGBColor(255, 255, 255)
    url_box.line.color.rgb = C_TEAL
    url_box.line.width = Pt(1)
    tf_u = url_box.text_frame
    tf_u.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_u = tf_u.paragraphs[0]
    p_u.alignment = PP_ALIGN.CENTER
    u_run = p_u.add_run()
    u_run.text = "Open Interactive Project Bible (Local) ->"
    u_run.font.name = FONT
    u_run.font.size = Pt(10.5)
    u_run.font.bold = True
    u_run.font.color.rgb = C_TEAL
    u_run.hyperlink.address = "index.html"

    # Displayed Web URL (Matches QR Code)
    web_box = slide16.shapes.add_textbox(r_x + Inches(0.25), r_y + Inches(4.74), r_w - Inches(0.5), Inches(0.95))
    tf_w = web_box.text_frame
    tf_w.word_wrap = True
    tf_w.margin_left = tf_w.margin_right = tf_w.margin_top = tf_w.margin_bottom = 0
    pw1 = tf_w.paragraphs[0]
    pw1.alignment = PP_ALIGN.CENTER
    w_run = pw1.add_run()
    w_run.text = live_url
    w_run.font.name = FONT
    w_run.font.size = Pt(10)
    w_run.font.bold = True
    w_run.font.color.rgb = C_PRIMARY
    w_run.hyperlink.address = live_url

    pw2 = tf_w.add_paragraph()
    pw2.alignment = PP_ALIGN.CENTER
    pw2.space_before = Pt(4)
    pw2.text = "Includes Master Project Bible (v3.1), 11 NDE Testing Suites, Toxin-Free Extraction & Unit-1 Financial Model"
    pw2.font.name = FONT
    pw2.font.size = Pt(9)
    pw2.font.color.rgb = C_MUTED

    # Speaker Notes for Slide 16
    notes_tf = slide16.notes_slide.notes_text_frame
    notes_tf.text = (
        "Thank the BEC754 faculty evaluators at Rajkiya Engineering College, Sonbhadra. "
        "Close with our vision: Every ray deserves a second life, and every gram deserves a clean return. "
        "Invite the jury to scan the QR code or click the live Data Room link to inspect the full Master Project Bible and all 9 deep-dive technical and financial appendices. Open the floor for Q&A."
    )

    prs.save(str(PPTX_PATH))
    print(f"Built 14-slide unified linked PPTX + QR + HTML Data Room at: {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build SunSecond Interlinked Data Room & 16-Slide PPTX")
    parser.add_argument(
        "--url",
        default="https://sunsecond-rec-sonbhadra.netlify.app",
        help="Public HTTPS URL encoded into the Slide 16 QR code (default placeholder ready for Netlify Drop / GitHub Pages)",
    )
    args = parser.parse_args()
    build_dataroom()
    enhance_pptx_with_links_and_thankyou(args.url)

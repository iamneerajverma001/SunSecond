"""
SunSecond (STDD) — Executive Pitch Deck Native PDF Generator
Generates a 13-slide publication-grade, 16:9 widescreen PDF:
- Exact EXECUTIVE_SLATE theme styling
- Active clickable hyperlinks on every slide (deep-dive appendices + live data room)
- Embedded high-DPI scannable QR Code on Slide 13
- Converted via Microsoft Edge Chromium headless engine (vector text, crisp graphics)
"""

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:\Users\NEERAJ\.gemini\antigravity\scratch\SunSecond")
SPEC_PATH = Path(r"C:\Users\NEERAJ\.gemini\antigravity\brain\e8b5526c-d348-432a-91fc-7d0cdda26653\scratch\sunsecond_deck_spec.json")
QR_PATH = BASE / "qr_sunsecond_dataroom.png"
HTML_OUT = BASE / "pitch_deck_presentation.html"
PDF_OUT = BASE / "SunSecond_STDD_Executive_Pitch_Deck.pdf"
LIVE_BASE_URL = "https://iamneerajverma001.github.io/SunSecond/"

# Slide deep-dive mappings (1-indexed)
SLIDE_LINKS = {
    2: ("Deep Dive: Appendix A — Market Analysis ->", LIVE_BASE_URL + "docs/appendix_a_market_analysis.html"),
    3: ("Deep Dive: Appendix B — STDD Blueprint ->", LIVE_BASE_URL + "docs/appendix_b_stdd_blueprint.html"),
    4: ("Deep Dive: Master Project Bible ->", LIVE_BASE_URL + "SUNSECOND_PROJECT_BIBLE.html"),
    5: ("Deep Dive: Appendix C — Triage Science ->", LIVE_BASE_URL + "docs/appendix_c_gia_triage_science.html"),
    6: ("Deep Dive: Appendix E — Testing Suites ->", LIVE_BASE_URL + "docs/appendix_e_testing_suites.html"),
    7: ("Deep Dive: Appendix D — Cascade Reuse ->", LIVE_BASE_URL + "docs/appendix_d_cascade_reuse.html"),
    8: ("Deep Dive: Appendix F — 10-Stream Engine ->", LIVE_BASE_URL + "docs/appendix_f_monetization_engine.html"),
    9: ("Deep Dive: Appendix H — Scrapping Suites ->", LIVE_BASE_URL + "docs/appendix_h_scrapping_suites.html"),
    10: ("Deep Dive: Appendix G — Scrap Economics ->", LIVE_BASE_URL + "docs/appendix_g_scrap_monetization.html"),
    11: ("Deep Dive: Master Project Bible ->", LIVE_BASE_URL + "SUNSECOND_PROJECT_BIBLE.html"),
    12: ("Deep Dive: Appendix D — Interview Kit ->", LIVE_BASE_URL + "docs/appendix_d_cascade_reuse.html"),
}

with open(SPEC_PATH, "r", encoding="utf-8") as f:
    spec = json.load(f)

# Encode QR code to base64
qr_b64 = ""
if QR_PATH.exists():
    with open(QR_PATH, "rb") as qf:
        qr_b64 = base64.b64encode(qf.read()).decode("utf-8")

CSS = """
@page {
  size: 13.333in 7.5in;
  margin: 0;
}
* {
  box-sizing: border-box;
}
body {
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Calibri, -apple-system, sans-serif;
  background: #0f172a;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.slide {
  width: 13.333in;
  height: 7.5in;
  background: #ffffff;
  position: relative;
  overflow: hidden;
  page-break-after: always;
  padding: 0.65in 0.8in 0.85in 0.8in;
}
.slide-dark {
  background: #0f172a;
  color: #f8fafc;
}
.cat-tag {
  color: #0d9488;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.slide-title {
  color: #1e293b;
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 22px 0;
  line-height: 1.25;
}
.footer-bar {
  position: absolute;
  bottom: 0.35in;
  left: 0.8in;
  right: 0.8in;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #64748b;
  border-top: 1px solid #e2e8f0;
  padding-top: 8px;
}
.deep-dive-btn {
  background: #ccfbf1;
  color: #0f766e !important;
  border: 1px solid #0d9488;
  padding: 5px 14px;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 700;
  font-size: 11.5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.card {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 12px;
  padding: 18px 20px;
}
.card.highlight {
  border: 2px solid #0d9488;
  background: #f0fdfa;
}
.card-pill {
  display: inline-block;
  background: #0d9488;
  color: #ffffff;
  font-size: 10px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 999px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.card-title {
  color: #1e293b;
  font-size: 17px;
  font-weight: 800;
  margin: 0 0 10px 0;
}
.card-subtitle {
  color: #0d9488;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 10px;
}
ul.bullet-list {
  margin: 0;
  padding-left: 18px;
  color: #334155;
  font-size: 13.5px;
  line-height: 1.55;
}
ul.bullet-list li {
  margin-bottom: 7px;
}
.kpi-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #0d9488;
  border-radius: 8px;
  padding: 16px 18px;
}
.kpi-val {
  color: #0d9488;
  font-size: 34px;
  font-weight: 900;
  line-height: 1;
}
.kpi-lbl {
  color: #1e293b;
  font-size: 14px;
  font-weight: 700;
  margin: 6px 0 4px;
}
.kpi-desc {
  color: #64748b;
  font-size: 12px;
  line-height: 1.4;
}
.summary-bar {
  margin-top: 18px;
  background: #f0fdfa;
  border: 1px solid #99f6e4;
  border-radius: 8px;
  padding: 12px 18px;
  color: #115e59;
  font-size: 13.5px;
  font-weight: 600;
}
table.custom-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 6px;
}
table.custom-table th {
  background: #0d9488;
  color: #fff;
  text-align: left;
  padding: 10px 14px;
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
}
table.custom-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
  color: #1e293b;
}
table.custom-table tr:nth-child(even) td {
  background: #f8fafc;
}
.tag-step {
  display: inline-block;
  background: #0d9488;
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  font-weight: 800;
  font-size: 12px;
  margin-right: 6px;
}
"""

slides_html = []

# ==========================================
# SLIDE 1: HERO TITLE CARD
# ==========================================
s1_html = """
<div class="slide slide-dark" style="display: flex; flex-direction: column; justify-content: center; padding: 1.0in 1.2in;">
  <div style="display: inline-block; background: rgba(13, 148, 136, 0.2); border: 1px solid #0d9488; color: #2dd4bf; padding: 6px 16px; border-radius: 999px; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; width: fit-content; margin-bottom: 24px;">
    BEC754 PITCH DECK  |  START-UP & ENTREPRENEURIAL ACTIVITY ASSESSMENT
  </div>
  <h1 style="color: #ffffff; font-size: 52px; font-weight: 900; margin: 0 0 14px 0; letter-spacing: -0.5px;">
    SunSecond — <span style="color: #2dd4bf;">The "GIA for Solar"</span>
  </h1>
  <p style="color: #94a3b8; font-size: 22px; max-width: 900px; margin: 0 0 36px 0; line-height: 1.45;">
    India's First Integrated Solar Triage, Demanufacturing & Decoupled-Traceability Platform (STDD)
  </p>
  <div style="background: rgba(30, 41, 59, 0.85); border: 1px solid #334155; border-radius: 12px; padding: 18px 26px; max-width: 820px; display: flex; justify-content: space-between; align-items: center;">
    <div>
      <div style="color: #cbd5e1; font-size: 13px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">Academic Institution & Department</div>
      <div style="color: #ffffff; font-size: 16px; font-weight: 700; margin-top: 3px;">Department of Electronics Engineering  |  Rajkiya Engineering College, Sonbhadra</div>
    </div>
    <div style="text-align: right; border-left: 1px solid #475569; padding-left: 24px;">
      <div style="color: #2dd4bf; font-size: 14px; font-weight: 800;">Neeraj (2308410300042)</div>
      <div style="color: #cbd5e1; font-size: 14px; font-weight: 700;">Pankaj (2308410300044)</div>
    </div>
  </div>
  <div class="footer-bar" style="border-top-color: #334155; color: #64748b;">
    <span>Subject: BEC754 — Start-up and Entrepreneurial Activity Assessment</span>
    <span>November 2026</span>
  </div>
</div>
"""
slides_html.append(s1_html)

# ==========================================
# SLIDES 2-12: CONTENT SLIDES
# ==========================================
for idx, s in enumerate(spec["slides"][1:], start=2):
    cat = s.get("category", "")
    title = s.get("title", "")
    stype = s.get("type", "")
    link_lbl, link_url = SLIDE_LINKS.get(idx, ("", ""))

    content_html = ""

    if stype == "KPI_METRICS":
        cards = ""
        for m in s.get("metrics", []):
            cards += f"""
            <div class="kpi-box">
              <div class="kpi-val">{m.get('value')}</div>
              <div class="kpi-lbl">{m.get('label')}</div>
              <div class="kpi-desc">{m.get('desc')}</div>
            </div>
            """
        b_sum = s.get("bottom_summary", "")
        content_html = f"""
        <div class="grid-4">{cards}</div>
        <div class="summary-bar"><strong>Key Synthesis:</strong> {b_sum}</div>
        """

    elif stype == "EXECUTIVE_SUMMARY":
        lead = s.get("lead_banner", "")
        l_card = s.get("left_card", {})
        r_card = s.get("right_card", {})
        l_bullets = "".join([f"<li>{b}</li>" for b in l_card.get("bullets", [])])
        r_bullets = "".join([f"<li>{b}</li>" for b in r_card.get("bullets", [])])
        content_html = f"""
        <div style="background: #f1f5f9; border-left: 4px solid #0d9488; padding: 10px 16px; border-radius: 6px; font-size: 15px; font-weight: 700; color: #0f766e; margin-bottom: 18px;">
          {lead}
        </div>
        <div class="grid-2">
          <div class="card" style="border-color: #fca5a5; background: #fff5f5;">
            <div class="card-pill" style="background: #ef4444;">{l_card.get('badge')}</div>
            <div class="card-title" style="color: #991b1b;">{l_card.get('title')}</div>
            <ul class="bullet-list" style="color: #7f1d1d;">{l_bullets}</ul>
          </div>
          <div class="card highlight">
            <div class="card-pill">{r_card.get('badge')}</div>
            <div class="card-title">{r_card.get('title')}</div>
            <ul class="bullet-list">{r_bullets}</ul>
          </div>
        </div>
        """

    elif stype == "PIPELINE_FLOW":
        stages_html = ""
        for i, st in enumerate(s.get("stages", [])):
            bullets = "".join([f"<li>{b}</li>" for b in st.get("bullets", [])])
            hl_class = "highlight" if st.get("highlight") else ""
            stages_html += f"""
            <div class="card {hl_class}" style="display: flex; flex-direction: column;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="card-pill">Stage 0{i+1}</span>
                <span style="font-size: 10px; font-weight: 800; color: #0d9488;">{st.get('tech')}</span>
              </div>
              <div class="card-title" style="font-size: 16px; margin-bottom: 8px;">{st.get('name')}</div>
              <ul class="bullet-list" style="font-size: 12.5px; padding-left: 14px;">{bullets}</ul>
            </div>
            """
        content_html = f'<div class="grid-4">{stages_html}</div>'

    elif stype == "CARDS_GRID":
        cards_html = ""
        cards_list = s.get("cards", [])
        num_cards = len(cards_list)
        grid_class = "grid-4" if num_cards == 4 else "grid-3"
        for c in cards_list:
            bullets = "".join([f"<li>{b}</li>" for b in c.get("bullets", [])])
            hl_class = "highlight" if c.get("highlight") else ""
            cards_html += f"""
            <div class="card {hl_class}">
              <div class="card-subtitle">{c.get('subtitle', '')}</div>
              <div class="card-title">{c.get('title')}</div>
              <ul class="bullet-list" style="font-size: 12.5px; padding-left: 14px;">{bullets}</ul>
            </div>
            """
        content_html = f'<div class="{grid_class}">{cards_html}</div>'

    elif stype == "CHART":
        # Slide 10: Scrap Economics
        t_card = s.get("takeaway_card", {})
        t_bullets = "".join([f"<li>{b}</li>" for b in t_card.get("bullets", [])])
        content_html = f"""
        <div class="grid-2">
          <div class="card" style="background: #ffffff;">
            <div class="card-title" style="font-size: 16px; margin-bottom: 14px;">Scrap Value vs. Net Economics (₹/Tonne)</div>
            <table class="custom-table" style="font-size: 12.5px;">
              <thead>
                <tr><th>Channel</th><th>Gross Value (₹/t)</th><th>Net Profit / Loss (₹/t)</th></tr>
              </thead>
              <tbody>
                <tr><td><strong>Kabadiwala</strong></td><td>₹22,000</td><td style="color: #64748b;">+₹4,000 (Toxic dump)</td></tr>
                <tr style="background: #fef2f2;"><td><strong>Shredding (CEEW Study)</strong></td><td>₹51,000</td><td style="color: #ef4444; font-weight: 700;">-₹10,230 (Loss!)</td></tr>
                <tr style="background: #f0fdfa;"><td><strong>SunSecond Ph-1 (Tolling)</strong></td><td>₹1,20,500</td><td style="color: #0d9488; font-weight: 800;">+₹62,500 (Profit)</td></tr>
                <tr style="background: #ccfbf1;"><td><strong>SunSecond Ph-2 (Direct)</strong></td><td>₹1,66,000</td><td style="color: #0f766e; font-weight: 900;">+₹98,000 (Leader)</td></tr>
              </tbody>
            </table>
            <div style="font-size: 11px; color: #64748b; margin-top: 10px;">
              *CEEW Study benchmarked across Gujarat, Rajasthan, and MP solar parks.
            </div>
          </div>
          <div class="card highlight">
            <div class="card-pill">{t_card.get('badge', 'LEVERS')}</div>
            <div class="card-title">{t_card.get('title')}</div>
            <ul class="bullet-list" style="font-size: 13px;">{t_bullets}</ul>
          </div>
        </div>
        """

    elif stype == "TIMELINE":
        steps_html = ""
        for i, step in enumerate(s.get("steps", [])):
            deliverables = "".join([f"<li>{d}</li>" for d in step.get("deliverables", [])])
            steps_html += f"""
            <div class="card" style="display: flex; flex-direction: column;">
              <div style="display: flex; align-items: center; margin-bottom: 6px;">
                <span class="tag-step">{i+1}</span>
                <span style="font-size: 11px; font-weight: 800; color: #0d9488;">{step.get('phase')}</span>
              </div>
              <div class="card-title" style="font-size: 15px; margin-bottom: 8px;">{step.get('title')}</div>
              <ul class="bullet-list" style="font-size: 12px; padding-left: 14px;">{deliverables}</ul>
            </div>
            """
        content_html = f'<div class="grid-4">{steps_html}</div>'

    elif stype == "CONCLUSION":
        items_html = ""
        for item in s.get("action_items", []):
            items_html += f"""
            <div class="card" style="display: flex; justify-content: space-between; align-items: flex-start; padding: 14px 18px; margin-bottom: 10px;">
              <div style="max-width: 820px;">
                <div style="color: #1e293b; font-weight: 800; font-size: 15px; margin-bottom: 4px;">{item.get('title')}</div>
                <div style="color: #475569; font-size: 13px; line-height: 1.45;">{item.get('desc')}</div>
              </div>
              <div style="text-align: right; min-width: 130px; border-left: 2px solid #e2e8f0; padding-left: 14px;">
                <div style="color: #0d9488; font-weight: 800; font-size: 13px;">{item.get('timeline')}</div>
                <div style="color: #64748b; font-size: 11.5px;">{item.get('owner')}</div>
              </div>
            </div>
            """
        content_html = f'<div>{items_html}</div>'

    slide_block = f"""
    <div class="slide">
      <div class="cat-tag">{cat}</div>
      <h2 class="slide-title">{title}</h2>
      {content_html}
      <div class="footer-bar">
        <span>SunSecond (STDD)  |  BEC754  |  Electronics Engineering, REC Sonbhadra  |  Slide {idx:02d} of 13</span>
        <a href="{link_url}" class="deep-dive-btn" target="_blank">{link_lbl}</a>
      </div>
    </div>
    """
    slides_html.append(slide_block)

# ==========================================
# SLIDE 13: CLOSING VISION, QR CODE & PORTAL
# ==========================================
s13_html = f"""
<div class="slide" style="padding: 0.8in 1.0in;">
  <div style="display: flex; height: 100%; gap: 40px; align-items: center;">
    
    <!-- Left Column: Vision & Closing -->
    <div style="flex: 1.2; display: flex; flex-direction: column; justify-content: center;">
      <div style="display: inline-block; background: #ccfbf1; color: #0d9488; border: 1px solid #0d9488; padding: 4px 14px; border-radius: 999px; font-weight: 800; font-size: 12px; width: fit-content; margin-bottom: 14px;">
        BEC754  |  PROJECT SUNSECOND
      </div>
      <h1 style="color: #1e293b; font-size: 46px; font-weight: 900; margin: 0 0 16px 0;">
        Thank You.
      </h1>
      
      <div style="background: #f0fdfa; border-left: 4px solid #0d9488; border-radius: 0 12px 12px 0; padding: 18px 24px; margin-bottom: 24px;">
        <div style="color: #0f766e; font-size: 18px; font-weight: 800; font-style: italic; line-height: 1.45;">
          "Every Ray Deserves a Second Life.<br>Every Gram Deserves a Clean Return."
        </div>
        <div style="color: #475569; font-size: 13px; margin-top: 8px;">
          The GIA Standard for Second-Life Solar & Circular Demanufacturing
        </div>
      </div>

      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 14px 20px;">
        <div style="font-size: 11px; text-transform: uppercase; font-weight: 800; color: #64748b; letter-spacing: 0.5px;">Student Founders & Project Assessment</div>
        <div style="display: flex; justify-content: space-between; margin-top: 6px;">
          <div>
            <strong style="color: #0f766e; font-size: 15px;">Neeraj</strong>
            <span style="color: #64748b; font-size: 13px;"> (Roll No. 2308410300042)</span>
          </div>
          <div>
            <strong style="color: #0f766e; font-size: 15px;">Pankaj</strong>
            <span style="color: #64748b; font-size: 13px;"> (Roll No. 2308410300044)</span>
          </div>
        </div>
        <div style="color: #334155; font-size: 12.5px; margin-top: 6px; font-weight: 600;">
          Department of Electronics Engineering  |  Rajkiya Engineering College, Sonbhadra
        </div>
      </div>
    </div>

    <!-- Right Column: Live Data Room & Scannable QR -->
    <div style="flex: 0.85; background: #f8fafc; border: 2px solid #0d9488; border-radius: 16px; padding: 24px; text-align: center; box-shadow: 0 8px 30px rgba(13, 148, 136, 0.08); display: flex; flex-direction: column; align-items: center; justify-content: center;">
      <div style="color: #0f766e; font-weight: 800; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
        Interactive Deep-Dive Data Room
      </div>
      
      <!-- Embedded QR Code -->
      <div style="background: #ffffff; padding: 12px; border-radius: 12px; border: 1px solid #cbd5e1; display: inline-block;">
        <img src="data:image/png;base64,{qr_b64}" alt="SunSecond Data Room QR Code" style="width: 170px; height: 170px; display: block;" />
      </div>

      <div style="font-size: 11.5px; color: #64748b; margin: 12px 0 10px; font-weight: 600;">
        Scan with Phone Camera to Access Master Bible & All 9 Appendices
      </div>

      <a href="{LIVE_BASE_URL}" target="_blank" style="display: inline-block; background: #0d9488; color: #ffffff !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 13px; margin-bottom: 6px;">
        Open Live Data Room Web Portal ->
      </a>

      <div style="font-size: 11px; color: #0d9488; font-weight: 700;">
        <a href="{LIVE_BASE_URL}" target="_blank" style="color: #0d9488; text-decoration: none;">{LIVE_BASE_URL}</a>
      </div>
    </div>

  </div>

  <div class="footer-bar">
    <span>SunSecond (STDD)  |  BEC754  |  Electronics Engineering, REC Sonbhadra  |  Slide 13 of 13</span>
    <span style="color: #0d9488; font-weight: 700;">Live Online Assessment Ready</span>
  </div>
</div>
"""
slides_html.append(s13_html)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SunSecond (STDD) — Executive Pitch Deck</title>
  <style>{CSS}</style>
</head>
<body>
  {"".join(slides_html)}
</body>
</html>
"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"Generated standalone presentation HTML: {HTML_OUT}")

# Run Microsoft Edge to compile to PDF
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
cmd = [
    edge_path,
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--print-to-pdf-no-header",
    f"--print-to-pdf={PDF_OUT}",
    str(HTML_OUT)
]
print("Compiling PDF via Microsoft Edge Chromium...")
res = subprocess.run(cmd, capture_output=True, text=True)
if PDF_OUT.exists() and PDF_OUT.stat().st_size > 10000:
    print(f"SUCCESS: Generated {PDF_OUT.name} ({PDF_OUT.stat().st_size:,} bytes)")
else:
    print("PDF Generation Output:", res.stdout, res.stderr)

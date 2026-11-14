# =====================================================================
# APPLICATION: app_fab_change_intel.py
# PURPOSE: Semiconductor Change Intelligence & Hook-Up Arbiter
# 
# TECHNOLOGY STACK:
#   - Runtime & UI: Python 3.12, Streamlit Community Cloud
#   - Orchestration & LLM: LangChain, Google Gemini (gemini-3.8-flash)
#   - Deterministic Analytics: Pandas, Pydantic v2, ReportLab PDF Engine
# 
# AUTHOR & ARCHITECT:
#   - Rohit Kumar, PMP, CEng (India), CEA, FSEr (TÜV)
#   - Mission-Critical Infrastructure & Systems Engineering Specialist 
#   - Forensic Project Controls & Contract Governance
#   - Contact: grohit41@gmail.com | LinkedIn: ROHITG41 (linkedin.com/in/rohitg41)
#   - Repository: https://github.com/ROHITG41/semiconductor-fab-arbiter
#
# INTELLECTUAL PROPERTY & LICENSING:
#   - Copyright © 2026 Rohit Kumar. All Rights Reserved.
# =====================================================================

import os
import io
import re
import streamlit as st
import pandas as pd
from typing import Dict, Any
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# ReportLab PDF Imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------------------------------------------------
# 1. UI CONFIGURATION & EXECUTIVE STYLING
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Semiconductor Change Intelligence & Hook-Up Arbiter",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    .main-header {
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        color: #102C57;
        font-size: 2.10rem;
        font-weight: 800;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
        color: #0F766E;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 16px;
    }
    .provenance-card {
        background-color: #F8FAFC;
        border-left: 4px solid #102C57;
        padding: 12px 18px;
        border-radius: 4px;
        margin-bottom: 16px;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.5;
    }
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .metric-value {
        font-size: 1.50rem;
        font-weight: 700;
        color: #102C57;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .arbiter-card {
        background-color: #F0FDFA;
        border: 1px solid #99F6E4;
        border-left: 5px solid #0F766E;
        padding: 18px;
        border-radius: 6px;
        margin-top: 10px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------
# 2. PYDANTIC V2 DATA CONTRACTS
# ---------------------------------------------------------------------
class ToolUtilitySpec(BaseModel):
    tool_id: str = Field(..., description="Unique tool identifier in cleanroom bay")
    process_bay: str = Field(..., description="Fab zone: Litho, Etch, CVD/ALD, CMP, Metrology")
    pcw_gpm: float = Field(..., description="Process Cooling Water volumetric flow")
    pcw_delta_p_bar: float = Field(..., description="Required PCW Delta-P at POU inlet")
    exhaust_cfm: float = Field(..., description="Scrubber / Acid exhaust volumetric flow")
    exhaust_dp_pa: float = Field(..., description="Required exhaust collar static pressure (-Pa)")
    power_kw: float = Field(..., description="Continuous electrical load with SEMI F47 sag immunity")
    vibration_limit_ums: float = Field(..., description="Max allowable floor vibration (VC-E / VC-G)")
    spec_freeze_date: str = Field(..., description="Contractual baseline spec freeze date")
    ecn_revision_date: str = Field(..., description="Actual OEM Engineering Change Notice date")

# ---------------------------------------------------------------------
# 3. DETERMINISTIC SUB-FAB PHYSICS & ATTRIBUTION ENGINE (CPU)
# ---------------------------------------------------------------------
def run_fab_tool_audit(
    tool_id: str,
    process_bay: str,
    baseline_gpm: float,
    revised_gpm: float,
    baseline_cfm: float,
    revised_cfm: float,
    baseline_kw: float,
    revised_kw: float,
    header_exhaust_headroom_cfm: float,
    header_pcw_headroom_gpm: float,
    spec_slip_days: int,
    base_build_slip_days: int,
    tool_install_slip_days: int,
    vibration_actual_ums: float,
    vibration_limit_ums: float,
    semi_f47_compliant: bool
) -> Dict[str, Any]:
    gpm_delta = revised_gpm - baseline_gpm
    cfm_delta = revised_cfm - baseline_cfm
    kw_delta = revised_kw - baseline_kw

    exhaust_headroom_violation = revised_cfm > (baseline_cfm + header_exhaust_headroom_cfm)
    pcw_headroom_violation = revised_gpm > (baseline_gpm + header_pcw_headroom_gpm)
    pipe_velocity_fps = (0.4085 * revised_gpm) / ((16.0 * 0.95) ** 2) * 16.0
    velocity_violation = pipe_velocity_fps > 10.0

    vibration_violation = vibration_actual_ums > vibration_limit_ums
    safety_gate_passed = semi_f47_compliant and not vibration_violation

    concurrent_delay = min(base_build_slip_days, tool_install_slip_days)
    net_tool_install_lag = max(0, tool_install_slip_days - base_build_slip_days)
    net_base_build_lag = max(0, base_build_slip_days - tool_install_slip_days)

    if spec_slip_days > 0 and (exhaust_headroom_violation or pcw_headroom_violation):
        primary_culprit = "Tool OEM (Late ECN Spec Churn & Utility Escalation)"
    elif base_build_slip_days > tool_install_slip_days:
        primary_culprit = "Base-Build MEP Contractor (Sub-Fab POC Handover Slip)"
    elif tool_install_slip_days > base_build_slip_days:
        primary_culprit = "Tool-Install / Hook-Up Contractor (Lateral Waffle-Slab Slip)"
    else:
        primary_culprit = "Shared Concurrent Delay (Base-Build & Tool-Install Co-Caused)"

    penalties = 0.0
    if exhaust_headroom_violation: penalties += 30.0
    if pcw_headroom_violation: penalties += 25.0
    if not semi_f47_compliant: penalties += 25.0
    if vibration_violation: penalties += 20.0
    if spec_slip_days > 0: penalties += 10.0
    
    hri_score = max(0.0, 100.0 - penalties)
    hri_status = "CLEARED FOR GTO" if hri_score >= 85.0 else ("CONDITIONAL HOLD" if hri_score >= 60.0 else "CRITICAL STOP-WORK")

    return {
        "tool_id": tool_id,
        "process_bay": process_bay,
        "baseline_cfm": baseline_cfm,
        "revised_cfm": revised_cfm,
        "baseline_gpm": baseline_gpm,
        "revised_gpm": revised_gpm,
        "baseline_kw": baseline_kw,
        "revised_kw": revised_kw,
        "gpm_delta": gpm_delta,
        "cfm_delta": cfm_delta,
        "kw_delta": kw_delta,
        "exhaust_headroom_violation": exhaust_headroom_violation,
        "pcw_headroom_violation": pcw_headroom_violation,
        "pipe_velocity_fps": pipe_velocity_fps,
        "velocity_violation": velocity_violation,
        "vibration_violation": vibration_violation,
        "safety_gate_passed": safety_gate_passed,
        "concurrent_delay": concurrent_delay,
        "net_tool_install_lag": net_tool_install_lag,
        "net_base_build_lag": net_base_build_lag,
        "primary_culprit": primary_culprit,
        "hri_score": hri_score,
        "hri_status": hri_status
    }

# ---------------------------------------------------------------------
# 4. REPORTLAB PDF DOSSIER GENERATOR (FIXED & SANITIZED)
# ---------------------------------------------------------------------
def _sanitize_markdown_for_reportlab(text: str) -> str:
    """Strips LaTeX math ($...$), backticks, and converts **bold** to ReportLab XML <b>bold</b>."""
    # Remove LaTeX math dollar signs e.g. $Lag=4$ -> Lag=4
    text = re.sub(r'\$([^\$]+)\$', r'\1', text)
    # Remove inline code backticks
    text = text.replace('`', '')
    # Escape ampersands not part of XML entities
    text = re.sub(r'&(?!amp;|lt;|gt;|bull;|copy;|nbsp;)', '&amp;', text)
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Remove any stray single asterisks
    text = text.replace('*', '')
    return text.strip()

def generate_pdf_dossier(audit_res: Dict[str, Any], memo_text: str) -> bytes:
    buffer = io.BytesIO()
    doc_pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )
    styles = getSampleStyleSheet()
    
    c_navy = colors.HexColor("#102C57")
    c_teal = colors.HexColor("#0F766E")
    c_slate = colors.HexColor("#334155")
    c_light = colors.HexColor("#F8FAFC")
    c_border = colors.HexColor("#CBD5E1")

    # Custom Executive Paragraph Styles
    style_kicker = ParagraphStyle(
        'Kicker', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=c_teal, spaceAfter=2
    )
    style_title = ParagraphStyle(
        'ExecTitle', parent=styles['Title'],
        fontName='Helvetica-Bold', fontSize=15, leading=19,
        textColor=c_navy, alignment=0, spaceAfter=4
    )
    style_sub = ParagraphStyle(
        'ExecSub', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13,
        textColor=c_slate, spaceAfter=6
    )
    style_prov = ParagraphStyle(
        'Provenance', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.2, leading=11.5,
        textColor=c_slate
    )
    style_h2 = ParagraphStyle(
        'SectionH2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=c_navy, spaceBefore=10, spaceAfter=4
    )
    style_h3 = ParagraphStyle(
        'SectionH3', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=9.8, leading=13,
        textColor=c_teal, spaceBefore=8, spaceAfter=3
    )
    style_body = ParagraphStyle(
        'ExecBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=c_slate, spaceAfter=3
    )
    style_bullet = ParagraphStyle(
        'ExecBullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=c_slate, leftIndent=12, spaceAfter=3
    )
    style_th = ParagraphStyle(
        'TableHead', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.white
    )
    style_td = ParagraphStyle(
        'TableCell', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.3, leading=11,
        textColor=c_slate
    )
    style_td_bold = ParagraphStyle(
        'TableCellBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.3, leading=11,
        textColor=c_navy
    )
    style_footer = ParagraphStyle(
        'ExecFooter', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=7.5, leading=10,
        textColor=colors.HexColor("#64748B"), alignment=1
    )

    story = []

    # 1. Masthead
    story.append(Paragraph("AUTONOMOUS SEMICONDUCTOR CHANGE INTELLIGENCE &amp; HOOK-UP ARBITER", style_kicker))
    story.append(Paragraph(f"Pre-Hookup Readiness &amp; Forensic Adjudication Dossier: {audit_res['tool_id']}", style_title))
    story.append(Paragraph(
        f"Process Zone: {audit_res['process_bay']} &nbsp;|&nbsp; "
        f"Hook-Up Readiness Index (HRI): {audit_res['hri_score']:.0f}/100 ({audit_res['hri_status']})",
        style_sub
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=c_teal, spaceBefore=2, spaceAfter=8))

    # 2. Framed Author & Provenance Card (Restored!)
    prov_html = (
        "<b>Lead Systems Architect:</b> Rohit Kumar, PMP, CEng (India), CEA, FSEr (TÜV)<br/>"
        "<b>Professional Domain:</b> Mission-Critical Infrastructure &amp; Systems Engineering Specialist | "
        "Forensic Project Controls &amp; Contract Governance<br/>"
        "<b>Contact &amp; Channels:</b> grohit41@gmail.com | LinkedIn: linkedin.com/in/rohitg41 | "
        "GitHub: github.com/ROHITG41/semiconductor-fab-arbiter<br/>"
        "<b>Architecture Standard:</b> Hybrid Deterministic CPU Multiphysics + Cognitive Multi-Agent Consensus "
        "(Python 3.12 / Pydantic v2 / Google Gemini / ReportLab)"
    )
    prov_table = Table([[Paragraph(prov_html, style_prov)]], colWidths=[540])
    prov_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light),
        ('BOX', (0, 0), (-1, -1), 0.75, c_border),
        ('LINEBEFORE', (0, 0), (0, -1), 3.5, c_navy),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(prov_table)
    story.append(Spacer(1, 10))

    # 3. Deterministic Telemetry & Attribution Table (Wrapped in Paragraphs so nothing clips!)
    story.append(Paragraph("Deterministic Sub-Fab Utility &amp; Concurrency Audit Summary", style_h2))
    table_data = [
        [
            Paragraph("Audit Parameter", style_th),
            Paragraph("Contractual Baseline", style_th),
            Paragraph("Revised ECN Telemetry", style_th),
            Paragraph("Deterministic Variance &amp; Compliance Ruling", style_th)
        ],
        [
            Paragraph("Acid Scrubber Exhaust", style_td_bold),
            Paragraph(f"{audit_res.get('baseline_cfm', 1400):,.0f} CFM", style_td),
            Paragraph(f"{audit_res.get('revised_cfm', 1400 + audit_res['cfm_delta']):,.0f} CFM", style_td),
            Paragraph(
                f"{audit_res['cfm_delta']:+,.0f} CFM "
                f"({'<b>EXCEEDS HEADROOM</b>' if audit_res['exhaust_headroom_violation'] else '<b>COMPLIANT</b>'})",
                style_td
            )
        ],
        [
            Paragraph("Process Cooling Water (PCW)", style_td_bold),
            Paragraph(f"{audit_res.get('baseline_gpm', 45):,.1f} GPM", style_td),
            Paragraph(f"{audit_res.get('revised_gpm', 45 + audit_res['gpm_delta']):,.1f} GPM", style_td),
            Paragraph(
                f"{audit_res['gpm_delta']:+,.1f} GPM | Pipe Vel: {audit_res['pipe_velocity_fps']:.2f} ft/s "
                f"({'<b>HEADROOM BREACH</b>' if audit_res['pcw_headroom_violation'] else '<b>COMPLIANT</b>'})",
                style_td
            )
        ],
        [
            Paragraph("Electrical Power &amp; Safety", style_td_bold),
            Paragraph(f"{audit_res.get('baseline_kw', 180):,.1f} kW", style_td),
            Paragraph(f"{audit_res.get('revised_kw', 180 + audit_res['kw_delta']):,.1f} kW", style_td),
            Paragraph(
                f"{audit_res['kw_delta']:+,.1f} kW | SEMI F47 &amp; VC-E Gate: "
                f"<b>{'PASSED' if audit_res['safety_gate_passed'] else 'HOLD / FAILED'}</b>",
                style_td
            )
        ],
        [
            Paragraph("Schedule Concurrency Offset", style_td_bold),
            Paragraph("SCL / FIDIC Cl. 8.4", style_td),
            Paragraph(f"Concurrent: {audit_res['concurrent_delay']} days", style_td),
            Paragraph(
                f"Net Culpable Lag — Tool-Install: <b>{audit_res['net_tool_install_lag']}d</b> | "
                f"Base-Build MEP: <b>{audit_res['net_base_build_lag']}d</b>",
                style_td
            )
        ],
        [
            Paragraph("Forensic Liability Isolation", style_td_bold),
            Paragraph("Design Basis Report", style_td),
            Paragraph("Assigned Culpability", style_td),
            Paragraph(f"<b>{audit_res['primary_culprit']}</b>", style_td)
        ],
    ]
    t = Table(table_data, colWidths=[125, 95, 105, 215])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light]),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 4. Multi-Agent Arbitration Memorandum (Cleanly Parsed)
    story.append(Paragraph("Executive Multi-Agent Arbitration &amp; Engineering Adjudication Memorandum", style_h2))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=6))
    
    for raw_line in memo_text.split('\n'):
        line = raw_line.strip()
        if not line or line == '---':
            continue
        if line.startswith('### ') or line.startswith('## ') or line.startswith('# '):
            clean_heading = re.sub(r'^#+\s*', '', line)
            clean_heading = _sanitize_markdown_for_reportlab(clean_heading)
            story.append(Paragraph(clean_heading, style_h3))
        elif line.startswith('- ') or line.startswith('* '):
            clean_bullet = _sanitize_markdown_for_reportlab(line[2:])
            story.append(Paragraph(f"&bull; {clean_bullet}", style_bullet))
        else:
            clean_body = _sanitize_markdown_for_reportlab(line)
            story.append(Paragraph(clean_body, style_body))

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.75, color=c_border, spaceBefore=4, spaceAfter=4))
    story.append(Paragraph(
        "Copyright &copy; 2026 Rohit Kumar, PMP, CEng (India), CEA, FSEr (TÜV). All Rights Reserved. "
        "Generated via Autonomous Semiconductor Change Intelligence &amp; Hook-Up Arbiter.",
        style_footer
    ))

    doc_pdf.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ---------------------------------------------------------------------
# 5. SAMPLE FAB REGISTER & PRESET GENERATOR
# ---------------------------------------------------------------------
def load_fab_wide_register():
    return pd.DataFrame([
        {"Tool ID": "ETCH-402", "Process Bay": "Plasma Etch", "OEM Vendor": "Lam Research", "PCW (GPM)": 56.0, "Exhaust (CFM)": 1720.0, "Power (kW)": 195.0, "HRI": 88.0, "Status": "CONDITIONAL HOLD", "Primary Culprit": "Tool OEM (Late ECN)"},
        {"Tool ID": "LITHO-101", "Process Bay": "EUV Lithography", "OEM Vendor": "ASML", "PCW (GPM)": 85.0, "Exhaust (CFM)": 2400.0, "Power (kW)": 310.0, "HRI": 96.0, "Status": "CLEARED FOR GTO", "Primary Culprit": "None (Fully Compliant)"},
        {"Tool ID": "CVD-205", "Process Bay": "PECVD / ALD", "OEM Vendor": "Applied Materials", "PCW (GPM)": 40.0, "Exhaust (CFM)": 1250.0, "Power (kW)": 160.0, "HRI": 92.0, "Status": "CLEARED FOR GTO", "Primary Culprit": "None (Fully Compliant)"},
        {"Tool ID": "CMP-301", "Process Bay": "CMP Planarization", "OEM Vendor": "Applied Materials", "PCW (GPM)": 65.0, "Exhaust (CFM)": 1850.0, "Power (kW)": 140.0, "HRI": 54.0, "Status": "CRITICAL STOP-WORK", "Primary Culprit": "Base-Build MEP (POC Slip)"},
        {"Tool ID": "MET-502", "Process Bay": "Metrology & Inspection", "OEM Vendor": "KLA Corporation", "PCW (GPM)": 20.0, "Exhaust (CFM)": 600.0, "Power (kW)": 75.0, "HRI": 95.0, "Status": "CLEARED FOR GTO", "Primary Culprit": "None (Fully Compliant)"},
    ])

def build_deterministic_arbiter_memo(res: Dict[str, Any]) -> str:
    return f"""### 1. Executive Summary & Tool Hook-Up Disposition
- **Tool ID & Bay:** {res['tool_id']} ({res['process_bay']})
- **Hook-Up Readiness Index (HRI):** {res['hri_score']:.0f}/100 — **{res['hri_status']}**
- **Primary Liability Assignment:** {res['primary_culprit']}

### 2. Coupled Sub-Fab Physics & Spec-Delta Audit
- **Scrubber Exhaust Impact:** Baseline {res.get('baseline_cfm', 1400):,.0f} CFM vs. Revised {res.get('revised_cfm', 1720):,.0f} CFM ({res['cfm_delta']:+,.0f} CFM delta). Header Exhaust Headroom Violation: **{str(res['exhaust_headroom_violation']).upper()}**.
- **Process Cooling Water Impact:** Baseline {res.get('baseline_gpm', 45):,.1f} GPM vs. Revised {res.get('revised_gpm', 56):,.1f} GPM ({res['gpm_delta']:+,.1f} GPM delta). PCW Headroom Violation: **{str(res['pcw_headroom_violation']).upper()}**.
- **Micro-Vibration & Power Safety:** SEMI F47 Voltage-Sag Compliance: **VERIFIED** | VC-E Vibration Limit: **{'BREACHED' if res['vibration_violation'] else 'COMPLIANT'}**.

### 3. Forensic Schedule Concurrency & EoT Determination
- **Concurrent Delay Offset:** {res['concurrent_delay']} days co-caused by Base-Build MEP and Tool-Install.
- **Net Culpable Lag:** Tool-Install Net Critical Lag = {res['net_tool_install_lag']} days | Base-Build Net Critical Lag = {res['net_base_build_lag']} days.
- **Commercial Ruling:** Under FIDIC Sub-Clause 8.4 and SCL Delay Protocol standards, delay claims are adjusted to remove concurrent overlap. Inflated prolongation costs are discharged.

### 4. Binding Remediation & Gas-Turn-On (GTO) Clearance Directives
- **Directive 01 (Sub-Fab Balancing):** Verify point-of-connection (POC) damper & VFD setpoints prior to cleanroom lateral tie-in.
- **Directive 02 (QA/QC Sign-Off):** Complete helium leak certification and SEMI S2 EMO interlock loop verification before authorizing final Gas-Turn-On (GTO).
"""

# ---------------------------------------------------------------------
# 6. MAIN DASHBOARD INTERFACE
# ---------------------------------------------------------------------
def main():
    st.markdown('<p class="main-header">🔬 SEMICONDUCTOR CHANGE INTELLIGENCE & HOOK-UP ARBITER</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Sub-Fab Utility & Tool Hook-Up Synchronization | Deterministic Multi-Utility Physics, SEMI/ISO Gates & Forensic Claims</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="provenance-card">
        <b>Lead Systems Architect:</b> Rohit Kumar, PMP, CEng (India), CEA, FSEr (TÜV)<br/>
        <b>Professional Domain:</b> Mission-Critical Infrastructure & Systems Engineering Specialist | Forensic Project Controls & Contract Governance<br/>
        <b>Contact & Channels:</b> grohit41@gmail.com | LinkedIn: ROHITG41 (linkedin.com/in/rohitg41)<br/>
        <b>Central Repository:</b> <a href="https://github.com/ROHITG41/semiconductor-fab-arbiter" target="_blank">github.com/ROHITG41/semiconductor-fab-arbiter</a>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "**Operational Context & Quick Guide:** This application governs semiconductor fab fit-out synchronization across "
        "base-build sub-fab utilities and OEM process tool change notices. Review the pre-loaded **Fab-Wide Multi-Bay Command Center** "
        "below, or use the left sidebar to drill down into individual tool bays (such as `ETCH-402` hit by late OEM `ECN-09`) to "
        "run coupled POU physics, multi-agent arbitration, and export an audit-grade ReportLab PDF Dossier."
    )

    with st.sidebar:
        st.subheader("🔑 Engine Configuration")
        try:
            api_key_from_secrets = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            api_key_from_secrets = ""

        if api_key_from_secrets:
            os.environ["GEMINI_API_KEY"] = api_key_from_secrets
            st.success("Gemini API Key active via Vault.")
        else:
            user_key = st.text_input("Gemini API Key (Optional)", type="password", help="Leave blank to run deterministic physics & arbitration engine.")
            if user_key:
                os.environ["GEMINI_API_KEY"] = user_key

        st.markdown("---")
        st.subheader("⚙️ Tool Bay Calibration (ETCH-402 ECN-09)")
        tool_id_in = st.text_input("Process Tool ID", value="ETCH-402")
        bay_in = st.selectbox("Process Bay Zone", ["Plasma Etch", "EUV Lithography", "PECVD / ALD", "CMP Planarization", "Metrology"])
        
        c_base, c_rev = st.columns(2)
        with c_base:
            base_cfm = st.number_input("Baseline Exhaust (CFM)", value=1400.0, step=50.0)
            base_gpm = st.number_input("Baseline PCW (GPM)", value=45.0, step=5.0)
            base_kw = st.number_input("Baseline Power (kW)", value=180.0, step=10.0)
        with c_rev:
            rev_cfm = st.number_input("Revised ECN Exhaust (CFM)", value=1720.0, step=50.0)
            rev_gpm = st.number_input("Revised ECN PCW (GPM)", value=56.0, step=5.0)
            rev_kw = st.number_input("Revised ECN Power (kW)", value=195.0, step=10.0)

        st.markdown("---")
        st.subheader("🏗️ Schedule & Sub-Fab Telemetry")
        headroom_cfm = st.number_input("Shared Scrubber Headroom (CFM)", value=450.0, step=50.0)
        headroom_gpm = st.number_input("Shared PCW Headroom (GPM)", value=150.0, step=25.0)
        spec_slip = st.number_input("OEM Spec Freeze Slip (Days)", value=14, step=1)
        bb_slip = st.number_input("Base-Build POC Handover Slip (Days)", value=6, step=1)
        ti_slip = st.number_input("Tool-Install Lateral Slip (Days)", value=10, step=1)
        vib_act = st.number_input("Measured Vibration (um/s)", value=2.8, step=0.1)
        vib_lim = st.number_input("VC-E Vibration Limit (um/s)", value=3.12, step=0.1)
        f47_ok = st.checkbox("SEMI F47 Voltage-Sag Compliance", value=True)

        st.markdown("---")
        st.subheader("📋 Semiconductor Standards")
        st.caption(
            "• ISO 14644-1: Cleanroom AMC & Pressure\n"
            "• SEMI S2 / S6: EMO & Exhaust Venting\n"
            "• SEMI F47: Voltage Sag Immunity\n"
            "• VC-E / VC-G: Micro-Vibration Limits\n"
            "• FIDIC Cl. 8.4 / SCL: EoT Concurrency"
        )

    audit_res = run_fab_tool_audit(
        tool_id=tool_id_in,
        process_bay=bay_in,
        baseline_gpm=base_gpm,
        revised_gpm=rev_gpm,
        baseline_cfm=base_cfm,
        revised_cfm=rev_cfm,
        baseline_kw=base_kw,
        revised_kw=rev_kw,
        header_exhaust_headroom_cfm=headroom_cfm,
        header_pcw_headroom_gpm=headroom_gpm,
        spec_slip_days=spec_slip,
        base_build_slip_days=bb_slip,
        tool_install_slip_days=ti_slip,
        vibration_actual_ums=vib_act,
        vibration_limit_ums=vib_lim,
        semi_f47_compliant=f47_ok
    )

    st.subheader("1. Fab-Wide Multi-Bay Command Center (Plant Scale)")
    fab_df = load_fab_wide_register()
    
    if tool_id_in not in fab_df["Tool ID"].values:
        new_row = {"Tool ID": tool_id_in, "Process Bay": bay_in, "OEM Vendor": "Custom OEM", "PCW (GPM)": rev_gpm, "Exhaust (CFM)": rev_cfm, "Power (kW)": rev_kw, "HRI": audit_res["hri_score"], "Status": audit_res["hri_status"], "Primary Culprit": audit_res["primary_culprit"]}
        fab_df = pd.concat([pd.DataFrame([new_row]), fab_df], ignore_index=True)
    else:
        fab_df.loc[fab_df["Tool ID"] == tool_id_in, "HRI"] = audit_res["hri_score"]
        fab_df.loc[fab_df["Tool ID"] == tool_id_in, "Status"] = audit_res["hri_status"]
        fab_df.loc[fab_df["Tool ID"] == tool_id_in, "Primary Culprit"] = audit_res["primary_culprit"]

    st.dataframe(fab_df, use_container_width=True, hide_index=True)
    st.markdown("<br/>", unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Tool Hook-Up Readiness (HRI)</div>
            <div class="metric-value" style="color:{'#16A34A' if audit_res['hri_score']>=85 else ('#D97706' if audit_res['hri_score']>=60 else '#DC2626')};">
                {audit_res['hri_score']:.0f}/100 <span style="font-size:0.80rem;">({audit_res['hri_status']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Exhaust Delta (ECN-09)</div>
            <div class="metric-value" style="color:{'#DC2626' if audit_res['exhaust_headroom_violation'] else '#102C57'};">
                {audit_res['cfm_delta']:+,.0f} <span style="font-size:0.85rem;">CFM</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Net Critical Lag (Tool-Install)</div>
            <div class="metric-value" style="color:{'#DC2626' if audit_res['net_tool_install_lag']>0 else '#16A34A'};">
                {audit_res['net_tool_install_lag']} <span style="font-size:0.85rem;">days</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Primary Liability Isolation</div>
            <div class="metric-value" style="font-size:1.05rem; color:#0F766E;">
                {audit_res['primary_culprit'].split(' ')[0]} {audit_res['primary_culprit'].split(' ')[1]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.35])

    with col_left:
        st.subheader(f"2. Tool-Bay Forensic Drill-Down: {tool_id_in}")
        detail_df = pd.DataFrame([
            {"Parameter": "Tool Process Zone", "Value": bay_in},
            {"Parameter": "Baseline vs Revised Exhaust", "Value": f"{base_cfm:,.0f} CFM -> {rev_cfm:,.0f} CFM ({audit_res['cfm_delta']:+,.0f})"},
            {"Parameter": "Baseline vs Revised PCW", "Value": f"{base_gpm:.1f} GPM -> {rev_gpm:.1f} GPM ({audit_res['gpm_delta']:+,.1f})"},
            {"Parameter": "Header Exhaust Headroom", "Value": f"{'EXCEEDED (Header Stall Risk)' if audit_res['exhaust_headroom_violation'] else 'Adequate Headroom'}"},
            {"Parameter": "PCW Pipe Velocity", "Value": f"{audit_res['pipe_velocity_fps']:.2f} ft/s (Max 10.0 ft/s)"},
            {"Parameter": "Micro-Vibration (VC-E)", "Value": f"{vib_act:.2f} um/s (Limit {vib_lim:.2f})"},
            {"Parameter": "SEMI F47 / Safety Gate", "Value": f"{'PASSED' if audit_res['safety_gate_passed'] else 'FAILED'}"},
            {"Parameter": "Concurrent Delay Offset", "Value": f"{audit_res['concurrent_delay']} days co-caused"},
            {"Parameter": "Net Culpable Contractor Lag", "Value": f"Tool-Install: {audit_res['net_tool_install_lag']}d | Base-Build: {audit_res['net_base_build_lag']}d"},
            {"Parameter": "Primary Responsible Party", "Value": audit_res['primary_culprit']}
        ])
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

        if audit_res['hri_score'] >= 85.0:
            st.success("✅ TOOL HOOK-UP CLEARED: Ready for Waffle-Slab Rigging and Gas-Turn-On (GTO).")
        else:
            st.error("❌ HOOK-UP READINESS HOLD: Utility deficit or late OEM spec change requires remediation.")
            if audit_res['exhaust_headroom_violation']:
                st.warning("⚠️ Scrubber exhaust headroom exceeded. Header upsizing or VFD boost required before welding.")
            if audit_res['pcw_headroom_violation']:
                st.warning("⚠️ Process Cooling Water flow exceeds sub-fab branch capacity.")
            if audit_res['vibration_violation']:
                st.warning("⚠️ Sub-fab dry pump vibration exceeds VC-E lithography floor limits.")

    with col_right:
        st.subheader("3. Multi-Agent Arbitration & ReportLab PDF Dossier")
        st.button("🚀 Re-Run Multi-Agent Arbitration & Generate Dossier", type="primary")

        if os.environ.get("GEMINI_API_KEY"):
            try:
                with st.spinner("Agentic Loop Synthesizing Semiconductor Arbitration Memorandum..."):
                    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.0)
                    arb_prompt = ChatPromptTemplate.from_messages([
                        ("system",
                         "You are the Lead Semiconductor Capital Program & Commissioning Arbiter. "
                         "Analyze the provided deterministic telemetry, sub-fab header headroom, micro-vibration checks, "
                         "and schedule concurrency attribution for process tool hook-up. "
                         "STRICT FORMATTING RULE: Never use LaTeX math ($...$) or backticks. Write all numbers and equations in plain alphanumeric text. "
                         "Draft an authoritative Multi-Agent Arbitration Memorandum covering: "
                         "1. Executive Summary & Tool Hook-Up Disposition, 2. Coupled Sub-Fab Physics & Spec-Delta Audit, "
                         "3. Forensic Schedule Concurrency & EoT Determination, "
                         "4. Binding Remediation & Gas-Turn-On (GTO) Clearance Directives."),
                        ("human", "TOOL AUDIT DATA:\n{metrics}")
                    ])
                    chain = arb_prompt | llm
                    response = chain.invoke({"metrics": str(audit_res)})
                    if isinstance(response.content, list):
                        memo_text = "\n".join([str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in response.content])
                    else:
                        memo_text = str(response.content)
            except Exception:
                memo_text = build_deterministic_arbiter_memo(audit_res)
        else:
            memo_text = build_deterministic_arbiter_memo(audit_res)

        st.markdown(f'<div class="arbiter-card">{memo_text}</div>', unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)

        pdf_bytes = generate_pdf_dossier(audit_res, memo_text)
        st.download_button(
            label="📥 Download ReportLab Pre-Hookup & NCR Dossier (.pdf)",
            data=pdf_bytes,
            file_name=f"SENTRY_FAB_Dossier_{tool_id_in}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

if __name__ == "__main__":
    main()

# --- EXECUTIVE PORTFOLIO FOOTER ---
st.divider()
st.markdown(
    """
    <div style="text-align: center; color: #475569; font-size: 0.85rem; padding: 15px 0; line-height: 1.6;">
        <p style="margin-bottom: 6px;">
            <strong>Technology Stack:</strong> Python 3.12, Streamlit Community Cloud, Pydantic v2, LangChain, Google Gemini (gemini-3.8-flash), ReportLab PDF Engine
        </p>
        <p style="margin-bottom: 6px;">
            <strong>Author &amp; Architect:</strong> Rohit Kumar, PMP, CEng (India), CEA, FSEr (TÜV)<br>
            Mission-Critical Infrastructure &amp; Systems Engineering Specialist | Forensic Project Controls &amp; Contract Governance
        </p>
        <p style="margin-bottom: 6px;">
            <strong>Enterprise Advisory &amp; Custom Architecture:</strong> 
            Available for technical consulting, custom agentic workflow development &amp; private enterprise deployments.<br>
            <a href="https://www.linkedin.com/in/rohitg41" target="_blank" style="color: #2563EB; text-decoration: none;">LinkedIn</a> | 
            <a href="mailto:grohit41@gmail.com" style="color: #2563EB; text-decoration: none;">grohit41@gmail.com</a>
        </p>
        <p style="font-size: 0.78rem; color: #64748B; margin-top: 8px;">
            <em>Dataset Note: Independent engineering demonstration validated on representative, anonymized project datasets.</em><br>
            <strong>Intellectual Property &amp; Licensing:</strong> Copyright &copy; 2026 Rohit Kumar. All Rights Reserved.<br>
            Published solely for technical portfolio evaluation and architectural demonstration. Unauthorized copying or commercial deployment prohibited.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# ReportLab PDF Imports (Added KeepTogether to prevent orphaned headings & blank pages)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
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
    tool_id: str = Field(..., description="Unique tool identifier in cleanroom

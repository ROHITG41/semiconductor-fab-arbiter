# 🔬 Semiconductor Change Intelligence & Hook-Up Arbiter

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Cloud-red.svg)](https://share.streamlit.io/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-green.svg)](https://pydantic.dev/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF-orange.svg)](https://www.reportlab.com/)

Autonomous engineering and commercial arbitration agent engineered for advanced semiconductor wafer fabrication facilities ($3B–$28B CapEx). During Phase 3/4 cleanroom fit-out, tool move-in, and testing & commissioning (T&C), late OEM process tool changes frequently collide with fixed base-build sub-fab headers and overlapping contractor schedules. This application automates synchronization across **8 coupled Point-of-Use (POU) utility services** to protect first-wafer revenue and capital budgets.

---

## 🏗️ System Architecture & Hybrid Data Flow

The application enforces a strict **Deterministic CPU + Cognitive Multi-Agent** separation of labor, utilizing **Model Context Protocol (MCP)** client-server patterns to ensure zero AI math hallucinations in hydraulic, exhaust, vibration, and contractual schedule calculations.

```mermaid
graph TD
    A["Raw OEM Engineering Change Notice (ECN) & DBR Baseline"] --> B["Step 1: Pydantic v2 Spec Ingestion & Data Contracts"]
    B --> C["Step 2: MCP Python Calculation Server (Deterministic CPU Physics)"]
    
    subgraph "Deterministic Sub-Fab Physics & SEMI Gates"
        C1["Darcy-Weisbach Hydronic & PCW Delta-P"]
        C2["SEMI S6 Scrubber Exhaust & Fan Affinity"]
        C3["SEMI F47 Voltage-Sag & VC-E Micro-Vibration"]
        C4["SCL Delay Protocol & Concurrency Math"]
    end
    
    C --> C1 & C2 & C3 & C4
    C1 & C2 & C3 & C4 --> D["Step 3: Multi-Agent Scope & Readiness Arbitration"]
    
    subgraph "Cognitive Multi-Agent Consensus"
        D1["Process Yield & OEM Compliance Sentinel"]
        D2["Base-Build & CapEx Commercial Auditor"]
        D3["Fab T&C & Commercial Arbiter"]
    end
    
    D --> D1 & D2 & D3
    D1 & D2 & D3 --> E["Binding Gas-Turn-On (GTO) Verdict & ReportLab PDF Dossier"]
